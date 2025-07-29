import os
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union

from beets.plugins import BeetsPlugin
from beets.ui import Subcommand, decargs
from beets import config
from beets.library import Item, Album
from beets.util import displayable_path
from beets.dbcore import types

try:
    from deeprhythm import DeepRhythmPredictor
except ImportError:
    DeepRhythmPredictor = None


class BeetRhythmPlugin(BeetsPlugin):
    # Define flexible field types for BPM data
    item_types = {
        'bpm': types.FLOAT,
        'bpm_confidence': types.FLOAT,
    }
    
    def __init__(self):
        super().__init__(name='beetrhythm')
        
        # Configuration options
        self.config.add({
            'auto': True,  # Whether to automatically predict tempo on import
            'write': True,  # Whether to write tempo to file tags
            'force': False,  # Whether to overwrite existing tempo values
            'device': 'auto',  # Device to use for prediction (auto, cpu, cuda, mps)
            'batch_size': 128,  # Batch size for processing
            'workers': 8,  # Number of workers for batch processing
            'confidence_threshold': 0.0,  # Minimum confidence threshold
            'disable_batch': False,  # Disable batch processing (use individual processing)
            'write_confidence': False,  # Whether to always calculate and store confidence scores
        })
        
        # Initialize predictor lazily
        self._predictor = None
        
        # Register event listeners for auto mode
        if self.config['auto'].get():
            self.register_listener('album_imported', self.album_imported)
            self.register_listener('item_imported', self.item_imported)
    
    @property
    def predictor(self) -> Optional[DeepRhythmPredictor]:
        """Lazy initialization of the DeepRhythmPredictor."""
        if self._predictor is None:
            if DeepRhythmPredictor is None:
                self._log.error("DeepRhythm not installed. Please install with: pip install deeprhythm")
                return None
            
            device = self.config['device'].get()
            if device == 'auto':
                device = None
            
            try:
                self._predictor = DeepRhythmPredictor(device=device, quiet=True)
                self._log.info(f"DeepRhythm predictor initialized on device: {self._predictor.device}")
            except Exception as e:
                self._log.error(f"Failed to initialize DeepRhythm predictor: {e}")
                return None
        
        return self._predictor
    
    def commands(self):
        """Add the beetrhythm command to beets CLI."""
        beetrhythm_cmd = Subcommand(
            'br',
            help='predict tempo using DeepRhythm model'
        )
        beetrhythm_cmd.parser.add_option(
            '-f', '--force',
            action='store_true',
            help='overwrite existing tempo values'
        )
        beetrhythm_cmd.parser.add_option(
            '-w', '--write',
            action='store_true', default=None,
            help='write tempo to file tags'
        )
        beetrhythm_cmd.parser.add_option(
            '--no-write',
            action='store_false', dest='write',
            help='do not write tempo to file tags'
        )
        beetrhythm_cmd.parser.add_option(
            '-c', '--confidence',
            action='store_true',
            help='show confidence scores'
        )
        beetrhythm_cmd.parser.add_option(
            '-d', '--device',
            help='device for prediction (auto, cpu, cuda, mps)'
        )
        beetrhythm_cmd.func = self.beetrhythm_command
        
        return [beetrhythm_cmd]
    
    def beetrhythm_command(self, lib, opts, args):
        """Handle the beetrhythm command."""
        # Handle device option - reinitialize predictor if needed
        requested_device = opts.device if opts.device else self.config['device'].get()
        if requested_device == 'auto':
            requested_device = None
            
        # Check if we need to reinitialize the predictor with a different device
        if self._predictor is not None:
            current_device = str(self._predictor.device)
            # Handle device comparison (DeepRhythm device might be 'cpu', 'cuda:0', 'mps', etc.)
            if requested_device is None:
                # 'auto' was requested, check if current device is what auto would choose
                needs_reinit = False
            elif requested_device == 'cpu' and current_device != 'cpu':
                needs_reinit = True
            elif requested_device == 'cuda' and not current_device.startswith('cuda'):
                needs_reinit = True
            elif requested_device == 'mps' and current_device != 'mps':
                needs_reinit = True
            else:
                needs_reinit = False
                
            if needs_reinit:
                self._log.info(f"Reinitializing predictor: {current_device} -> {requested_device or 'auto'}")
                self._predictor = None
                # Temporarily override config for initialization
                original_device = self.config['device'].get()
                self.config['device'] = requested_device or 'auto'
                predictor = self.predictor  # This will reinitialize
                self.config['device'] = original_device
                if not predictor:
                    return
        else:
            # First time initialization with requested device
            if requested_device:
                original_device = self.config['device'].get()
                self.config['device'] = requested_device
                predictor = self.predictor
                self.config['device'] = original_device
                if not predictor:
                    return
            else:
                if not self.predictor:
                    return
        
        # Parse arguments
        if args:
            # Process specific paths
            paths = args
        else:
            # Process all items in library
            paths = None
        
        # Override config with command-line options
        force = opts.force or self.config['force'].get()
        write = opts.write if opts.write is not None else self.config['write'].get()
        show_confidence = opts.confidence
        
        if paths:
            # Process specific paths/folders
            self._process_paths(paths, force=force, write=write, show_confidence=show_confidence)
        else:
            # Process all items in library
            self._process_library(lib, force=force, write=write, show_confidence=show_confidence)
    
    def _process_paths(self, paths: List[str], force: bool = False, write: bool = True, show_confidence: bool = False):
        """Process specific paths or folders."""
        # Separate files and directories
        files = []
        directories = []
        
        for path_str in paths:
            path = Path(path_str)
            if path.is_file():
                if self._is_audio_file(path):
                    files.append(str(path))
            elif path.is_dir():
                directories.append(str(path))
            else:
                self._log.warning(f"Path not found: {path}")
        
        # Process directories
        for directory in directories:
            self._log.info(f"Processing directory: {directory}")
            
            # Check if we should use batch processing
            use_batch = (
                not self.config['disable_batch'].get() and
                self.config['workers'].get() > 1 and
                self.config['batch_size'].get() > 1
            )
            
            if use_batch:
                try:
                    results = self.predictor.predict_batch(
                        dirname=directory,
                        include_confidence=show_confidence,
                        workers=self.config['workers'].get(),
                        batch=self.config['batch_size'].get(),
                        quiet=True
                    )
                    
                    # Display results
                    for file_path, result in results.items():
                        if show_confidence:
                            tempo, confidence = result
                            self._log.info(f"{displayable_path(file_path)}: {tempo:.1f} BPM (confidence: {confidence:.3f})")
                        else:
                            tempo = result
                            self._log.info(f"{displayable_path(file_path)}: {tempo:.1f} BPM")
                    continue  # Successfully processed with batch, move to next directory
                        
                except Exception as e:
                    self._log.warning(f"Batch processing failed for {directory}, falling back to individual processing: {e}")
                    use_batch = False
            
            # Process directory files individually (either by choice or as fallback)
            if not use_batch:
                self._process_directory_individual(directory, show_confidence)
        
        # Process individual files
        if files:
            self._log.info(f"Processing {len(files)} individual files...")
            for file_path in files:
                self._process_single_file(file_path, show_confidence)
        
        if not files and not directories:
            self._log.info("No audio files or directories found to process")
    
    def _process_directory_individual(self, directory: str, show_confidence: bool = False):
        """Process all audio files in a directory individually."""
        import os
        audio_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                if self._is_audio_file(Path(file_path)):
                    audio_files.append(file_path)
        
        if audio_files:
            self._log.info(f"Found {len(audio_files)} audio files, processing individually...")
            for file_path in audio_files:
                self._process_single_file(file_path, show_confidence)
        else:
            self._log.info(f"No audio files found in {directory}")
    
    def _process_single_file(self, file_path: str, show_confidence: bool = False):
        """Process a single audio file."""
        try:
            if show_confidence:
                tempo, confidence = self.predictor.predict(file_path, include_confidence=True)
                self._log.info(f"{displayable_path(file_path)}: {tempo:.1f} BPM (confidence: {confidence:.3f})")
            else:
                tempo = self.predictor.predict(file_path)
                self._log.info(f"{displayable_path(file_path)}: {tempo:.1f} BPM")
                
        except Exception as e:
            self._log.error(f"Failed to predict tempo for {displayable_path(file_path)}: {e}")
    
    def _process_library(self, lib, force: bool = False, write: bool = True, show_confidence: bool = False):
        """Process all items in the beets library."""
        query = []
        if not force:
            # Only process items without tempo
            query.append('bpm:^$')
        
        items = lib.items(query)
        item_count = len(items)
        
        if item_count == 0:
            self._log.info("No items to process")
            return
        
        self._log.info(f"Processing {item_count} items from library...")
        
        # Group items by directory for batch processing
        dir_groups = {}
        for item in items:
            item_dir = os.path.dirname(item.path)
            if item_dir not in dir_groups:
                dir_groups[item_dir] = []
            dir_groups[item_dir].append(item)
        
        # Process each directory group
        for directory, dir_items in dir_groups.items():
            # Check if we should avoid batch processing for reliability
            if (self.config['disable_batch'].get() or 
                self.config['workers'].get() <= 1 or 
                self.config['batch_size'].get() <= 1):
                # Process items individually for better reliability
                self._process_items_individual(dir_items, write=write, show_confidence=show_confidence)
            else:
                self._process_items_batch(dir_items, write=write, show_confidence=show_confidence)
    
    def _process_items_individual(self, items: List[Item], write: bool = True, show_confidence: bool = False):
        """Process items individually without batch processing."""
        if not items:
            return
        
        self._log.info(f"Processing {len(items)} items individually...")
        
        # Determine if we should calculate confidence
        calculate_confidence = show_confidence or self.config['write_confidence'].get()
        
        for item in items:
            try:
                if calculate_confidence:
                    tempo, confidence = self.predictor.predict(item.path, include_confidence=True)
                    if confidence >= self.config['confidence_threshold'].get():
                        self._update_item_tempo(item, tempo, confidence, write=write)
                        if show_confidence:
                            self._log.info(f"{item.artist} - {item.title}: {tempo:.1f} BPM (confidence: {confidence:.3f})")
                        else:
                            self._log.info(f"{item.artist} - {item.title}: {tempo:.1f} BPM")
                    else:
                        self._log.warning(f"{item.artist} - {item.title}: Low confidence ({confidence:.3f}), skipping")
                else:
                    tempo = self.predictor.predict(item.path)
                    self._update_item_tempo(item, tempo, write=write)
                    self._log.info(f"{item.artist} - {item.title}: {tempo:.1f} BPM")
                    
            except Exception as e:
                self._log.error(f"Failed to predict tempo for {item.artist} - {item.title}: {e}")
    
    def _process_items_batch(self, items: List[Item], write: bool = True, show_confidence: bool = False):
        """Process a batch of items efficiently."""
        if not items:
            return
        
        # Create a mapping of file paths to items
        path_to_item = {item.path: item for item in items}
        file_paths = list(path_to_item.keys())
        
        # Determine if we should calculate confidence
        calculate_confidence = show_confidence or self.config['write_confidence'].get()
        
        try:
            # Process files individually but efficiently
            for file_path in file_paths:
                item = path_to_item[file_path]
                try:
                    if calculate_confidence:
                        tempo, confidence = self.predictor.predict(file_path, include_confidence=True)
                        if confidence >= self.config['confidence_threshold'].get():
                            self._update_item_tempo(item, tempo, confidence, write=write)
                            if show_confidence:
                                self._log.info(f"{item.artist} - {item.title}: {tempo:.1f} BPM (confidence: {confidence:.3f})")
                            else:
                                self._log.info(f"{item.artist} - {item.title}: {tempo:.1f} BPM")
                        else:
                            self._log.warning(f"{item.artist} - {item.title}: Low confidence ({confidence:.3f}), skipping")
                    else:
                        tempo = self.predictor.predict(file_path)
                        self._update_item_tempo(item, tempo, write=write)
                        self._log.info(f"{item.artist} - {item.title}: {tempo:.1f} BPM")
                        
                except Exception as e:
                    self._log.error(f"Failed to predict tempo for {item.artist} - {item.title}: {e}")
                    
        except Exception as e:
            self._log.error(f"Batch processing failed: {e}")
    
    def _update_item_tempo(self, item: Item, tempo: float, confidence: Optional[float] = None, write: bool = True):
        """Update an item's tempo in the database and optionally in file tags."""
        # Update database
        item.bpm = round(tempo, 1)
        if confidence is not None:
            item.bpm_confidence = round(confidence, 3)
        
        # Store changes
        item.store()
        
        # Write to file tags if requested
        if write:
            try:
                item.write()
            except Exception as e:
                self._log.warning(f"Failed to write tempo to file tags for {item.artist} - {item.title}: {e}")
    
    def album_imported(self, lib, album: Album):
        """Handle album import events."""
        if not self.config['auto'].get() or not self.predictor:
            return
        
        self._log.debug(f"Processing imported album: {album.albumartist} - {album.album}")
        
        # Get items that don't have tempo yet (unless force is enabled)
        items = album.items()
        if not self.config['force'].get():
            items = [item for item in items if not item.get('bpm')]
        
        if items:
            # Use individual processing if batch is disabled, otherwise use batch
            if (self.config['disable_batch'].get() or 
                self.config['workers'].get() <= 1 or 
                self.config['batch_size'].get() <= 1):
                self._process_items_individual(
                    items,
                    write=self.config['write'].get(),
                    show_confidence=False
                )
            else:
                self._process_items_batch(
                    items,
                    write=self.config['write'].get(),
                    show_confidence=False
                )
    
    def item_imported(self, lib, item: Item):
        """Handle singleton item import events."""
        if not self.config['auto'].get() or not self.predictor:
            return
        
        # Skip if item already has tempo (unless force is enabled)
        if item.get('bpm') and not self.config['force'].get():
            return
        
        self._log.debug(f"Processing imported item: {item.artist} - {item.title}")
        
        try:
            # Calculate confidence if configured to do so
            if self.config['write_confidence'].get():
                tempo, confidence = self.predictor.predict(item.path, include_confidence=True)
                if confidence >= self.config['confidence_threshold'].get():
                    self._update_item_tempo(item, tempo, confidence, write=self.config['write'].get())
                    self._log.info(f"Predicted tempo for {item.artist} - {item.title}: {tempo:.1f} BPM")
                else:
                    self._log.warning(f"Low confidence for {item.artist} - {item.title}: {confidence:.3f}, skipping")
            else:
                tempo = self.predictor.predict(item.path)
                self._update_item_tempo(item, tempo, write=self.config['write'].get())
                self._log.info(f"Predicted tempo for {item.artist} - {item.title}: {tempo:.1f} BPM")
        except Exception as e:
            self._log.error(f"Failed to predict tempo for {item.artist} - {item.title}: {e}")
    
    def _is_audio_file(self, path: Path) -> bool:
        """Check if a file is an audio file based on its extension."""
        audio_extensions = {'.mp3', '.flac', '.wav', '.m4a', '.ogg', '.wma', '.aac', '.mp4'}
        return path.suffix.lower() in audio_extensions
    