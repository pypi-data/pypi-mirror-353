# BeetRhythm - Beets Plugin for DeepRhythm Tempo Prediction

A [beets](https://beets.io/) plugin that uses [DeepRhythm](https://github.com/bleugreen/deeprhythm) to predict tempo (BPM) for your music library with high accuracy and speed.

## Features

- **Automatic tempo prediction** during music import
- **Batch processing** for efficient analysis of large collections
- **High accuracy** using the DeepRhythm CNN model (95.91% accuracy)
- **Fast processing** with GPU acceleration support
- **Flexible configuration** with confidence thresholds and device selection
- **CLI command** for manual processing of specific files or folders

## Installation

1. Install the plugin:
```bash
poetry install
```

2. Install DeepRhythm:
```bash
pip install deeprhythm
```

3. Add the plugin to your beets configuration:
```yaml
plugins:
  - beetrhythm

beetrhythm:
  auto: true              # Automatically predict tempo on import
  write: true             # Write tempo to file tags
  force: false            # Overwrite existing tempo values
  device: auto            # Device for prediction (auto, cpu, cuda, mps)
  batch_size: 128         # Batch size for processing
  workers: 8              # Number of workers for batch processing
  confidence_threshold: 0.0  # Minimum confidence threshold (0.0-1.0)
```

## Usage

### Automatic Mode

When `auto: true` is set in configuration, the plugin will automatically predict tempo for:
- Albums imported with `beet import`
- Individual tracks imported as singletons

### Manual CLI Command

Use the `beet beetrhythm` command to manually process files or folders:

```bash
# Process all items in library without tempo
beet beetrhythm

# Process specific folder
beet beetrhythm /path/to/music/folder

# Process specific files
beet beetrhythm /path/to/song1.mp3 /path/to/song2.flac

# Show confidence scores
beet beetrhythm -c /path/to/music

# Force overwrite existing tempo values
beet beetrhythm -f /path/to/music

# Use specific device
beet beetrhythm -d cuda /path/to/music

# Don't write to file tags (database only)
beet beetrhythm --no-write /path/to/music
```

### Command Options

- `-f, --force`: Overwrite existing tempo values
- `-w, --write`: Write tempo to file tags (default: true)
- `--no-write`: Don't write tempo to file tags
- `-c, --confidence`: Show confidence scores
- `-d, --device`: Device for prediction (auto, cpu, cuda, mps)

## Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `auto` | `true` | Automatically predict tempo during import |
| `write` | `true` | Write tempo values to file tags |
| `force` | `false` | Overwrite existing tempo values |
| `device` | `auto` | Device for prediction (auto, cpu, cuda, mps) |
| `batch_size` | `128` | Batch size for processing |
| `workers` | `8` | Number of workers for batch processing |
| `confidence_threshold` | `0.0` | Minimum confidence threshold (0.0-1.0) |

## Database Fields

The plugin adds the following flexible fields to your beets database:

- `bpm`: The predicted tempo in beats per minute (float)
- `bpm_confidence`: The confidence score of the prediction (float, 0.0-1.0)

You can query these fields like any other beets field:

```bash
# Find songs with tempo between 120-140 BPM
beet list bpm:120..140

# Find songs with high confidence predictions
beet list bpm_confidence:0.9..

# Find songs without tempo predictions
beet list bpm:^$
```

## Performance

The plugin uses batch processing when possible to greatly reduce processing time, especially when processing entire directories.

## Requirements

- Python 3.8+
- beets
- deeprhythm
- PyTorch (installed automatically with deeprhythm)

## Troubleshooting

### DeepRhythm not found
If you get an error about DeepRhythm not being installed:
```bash
pip install deeprhythm
```

### GPU not detected
If you have a CUDA-capable GPU but it's not being used:
- Ensure you have the CUDA version of PyTorch installed
- Set `device: cuda` in your configuration
- Check that your GPU drivers are up to date

### Memory issues
If you encounter memory issues with large batches:
- Reduce `batch_size` in configuration
- Reduce `workers` count
- Use `device: cpu` instead of GPU

## License

This project is licensed under the same terms as the beets project.

## Credits

- [DeepRhythm](https://github.com/bleugreen/deeprhythm) by bleugreen
- [beets](https://beets.io/) music library manager 