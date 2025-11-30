# DICOM Anonymizer Examples

This directory contains example scripts and configurations for using DICOM Anonymizer.

## Examples

### basic_anonymization.py

Simple single-file anonymization demonstrating the basic API:

```bash
python basic_anonymization.py
```

Demonstrates:
- Loading a preset
- Creating a processor
- Processing a single file
- Checking results

### batch_processing.py

Batch processing with progress tracking and report generation:

```bash
python batch_processing.py ./input_directory ./output_directory
python batch_processing.py ./input_directory ./output_directory --preset research
python batch_processing.py ./input_directory ./output_directory --workers 8
```

Demonstrates:
- Command-line argument parsing
- Directory processing
- Progress callbacks
- Parallel processing
- Report generation

### custom_preset.yaml

Example custom preset configuration with detailed comments:

```bash
# Validate the preset
dicom-anonym validate --config ./custom_preset.yaml

# Use the preset
dicom-anonym anonymize -i ./input -o ./output -p ./custom_preset.yaml
```

Demonstrates:
- Preset structure
- All action types
- Common tag configurations
- Compliance settings

## Getting Started

1. Install DICOM Anonymizer:

```bash
pip install dicom-anonym
```

2. Run an example:

```bash
cd examples
python basic_anonymization.py
```

3. For batch processing, provide a directory with DICOM files:

```bash
python batch_processing.py /path/to/dicom/study /path/to/output
```

## Creating Your Own Scripts

Use these examples as templates for your own workflows:

```python
from dicom_anonymizer.config.loader import load_preset
from dicom_anonymizer.engine.processor import DicomProcessor

# Your custom code here
preset = load_preset("sfda_safe_harbor")
processor = DicomProcessor(preset=preset)
stats = processor.process_file("input.dcm", "output.dcm")
```

## Additional Resources

- [Installation Guide](../installation.md)
- [CLI Reference](../cli-reference.md)
- [Configuration Guide](../configuration.md)
- [API Reference](../api-reference.md)
- [Compliance Documentation](../compliance.md)
