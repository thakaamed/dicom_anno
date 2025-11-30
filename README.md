<div align="center">

# THAKAAMED DICOM Anonymizer

**Professional DICOM de-identification for Saudi healthcare**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: Non-Commercial](https://img.shields.io/badge/License-Non--Commercial-red.svg)](LICENSE)
[![DICOM PS3.15](https://img.shields.io/badge/DICOM-PS3.15-orange.svg)](https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_e.html)

*Supporting Saudi Vision 2030 Healthcare Transformation*

**THAKAAMED AI** | Enterprise Healthcare Solutions

</div>

---

## Overview

THAKAAMED DICOM Anonymizer is a professional-grade, cross-platform tool for de-identifying DICOM medical imaging files. Built specifically for Saudi healthcare institutions, it provides:

- **Three Built-in Presets**: SFDA Safe Harbor, Research, and Full Anonymization
- **DICOM PS3.15 Compliance**: Implements the DICOM de-identification standard
- **HIPAA Safe Harbor**: Compliant with US healthcare privacy regulations
- **Saudi PDPL Ready**: Designed for Saudi Personal Data Protection Law compliance
- **Comprehensive Reporting**: PDF, JSON, and CSV audit reports
- **Branded Output**: Professional THAKAAMED-branded console and reports

## Features

- **Privacy Protection**: Removes or replaces patient identifying information
- **Audit Trails**: Complete documentation for compliance review
- **Parallel Processing**: Fast batch processing with multi-threading
- **Flexible Presets**: Choose from built-in presets or create custom rules
- **Professional Reports**: Branded PDF reports for stakeholders
- **UID Consistency**: Maintains referential integrity across studies

## Quick Start

### Installation (Online)

```bash
# Clone/navigate to the project
cd DICOM-ANNO

# Create virtual environment and install (using uv - recommended)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

---

## 🔒 Offline Installation (Air-Gapped / No Internet)

For healthcare environments without internet access, follow these steps:

### Step 1: Prepare the Offline Package (On a machine WITH internet)

```bash
# Navigate to project directory
cd DICOM-ANNO

# Create a directory to store all dependencies
mkdir -p offline_packages

# Download all dependencies as wheel files
pip download -d ./offline_packages -r requirements.txt

# Also download the package build tools
pip download -d ./offline_packages pip setuptools wheel build

# Create a distributable archive (optional)
tar -czvf thakaamed-dicom-offline.tar.gz \
    offline_packages/ \
    src/ \
    pyproject.toml \
    requirements.txt \
    README.md \
    LICENSE
```

### Step 2: Transfer to Offline Machine

Transfer the following to the air-gapped machine via USB/secure transfer:
- `thakaamed-dicom-offline.tar.gz` (or the entire `DICOM-ANNO` folder with `offline_packages/`)

### Step 3: Install on Offline Machine

```bash
# Extract if using archive
tar -xzvf thakaamed-dicom-offline.tar.gz
cd DICOM-ANNO

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Linux/macOS:
source .venv/bin/activate
# Windows:
.venv\Scripts\activate

# Install pip/setuptools from offline packages first
pip install --no-index --find-links=./offline_packages pip setuptools wheel

# Install all dependencies from offline packages
pip install --no-index --find-links=./offline_packages -r requirements.txt

# Install the THAKAAMED DICOM Anonymizer
pip install --no-index --find-links=./offline_packages -e .

# Verify installation
thakaamed-dicom version
```

### Alternative: Single Wheel Distribution

#### On machine WITH internet:
```bash
cd DICOM-ANNO

# Build the wheel
pip install build
python -m build

# The wheel will be in dist/
# e.g., dist/thakaamed_dicom-1.0.0-py3-none-any.whl

# Download dependencies
mkdir -p dist/deps
pip download -d ./dist/deps pydicom pyyaml click rich reportlab pillow
```

#### On OFFLINE machine:
```bash
# Install dependencies first
pip install --no-index --find-links=./dist/deps pydicom pyyaml click rich reportlab pillow

# Install the wheel
pip install --no-index ./dist/thakaamed_dicom-1.0.0-py3-none-any.whl
```

### Windows Offline Installation

```powershell
# Extract archive
Expand-Archive -Path thakaamed-dicom-offline.zip -DestinationPath C:\thakaamed

# Navigate to directory
cd C:\thakaamed\DICOM-ANNO

# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install from offline packages
pip install --no-index --find-links=.\offline_packages pip setuptools wheel
pip install --no-index --find-links=.\offline_packages -r requirements.txt
pip install --no-index --find-links=.\offline_packages -e .

# Verify
thakaamed-dicom version
```

### Verify Offline Installation

```bash
# Check version
thakaamed-dicom version

# List presets (no internet required)
thakaamed-dicom presets

# Validate a preset
thakaamed-dicom validate --preset sfda_safe_harbor

# Test anonymization
thakaamed-dicom anonymize \
    -i ./test_dicom/ \
    -o ./test_output/ \
    -p sfda_safe_harbor \
    --dry-run
```

### Required Dependencies for Offline Package

| Package | Version | Purpose |
|---------|---------|---------|
| `pydicom` | >=2.4.0 | DICOM file handling |
| `pyyaml` | >=6.0 | YAML configuration |
| `click` | >=8.0 | CLI framework |
| `rich` | >=13.0 | Console output |
| `reportlab` | >=4.0 | PDF report generation |
| `pillow` | >=10.0 | Image handling for reports |
| `pydantic` | >=2.0 | Configuration validation |

---

### Basic Usage

```bash
# Anonymize a directory of DICOM files
thakaamed-dicom anonymize --input /path/to/dicom --output /path/to/output --preset sfda_safe_harbor

# List available presets
thakaamed-dicom presets

# Validate a preset configuration
thakaamed-dicom validate --preset research

# Show version
thakaamed-dicom version
```

---

## 📚 Complete Examples

### Single File Anonymization

#### SFDA Safe Harbor (Maximum Privacy)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/patient_scan.dcm \
    -o ./anonymized_output/anon_scan.dcm \
    -p sfda_safe_harbor
```

#### Research Preset (Keeps Dates Shifted)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/patient_scan.dcm \
    -o ./anonymized_output/research_scan.dcm \
    -p research \
    --date-anchor 20200101
```

#### Full Anonymization (Maximum Removal)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/patient_scan.dcm \
    -o ./anonymized_output/full_anon_scan.dcm \
    -p full_anonymization
```

### Batch Processing (Entire Directory)

#### Process All DICOM Files in a Folder
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor
```

#### With More Workers (Faster Processing)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --workers 8
```

#### Sequential Processing (No Parallel)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --no-parallel
```

### Report Options

#### Generate All Reports (PDF + JSON + CSV)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-format all
```

#### Generate Only PDF Report
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-format pdf
```

#### Generate Only JSON Report
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-format json
```

#### No Reports (Fast Processing)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --no-reports
```

#### Custom Report Directory
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-dir ./my_reports/
```

### Preview & Testing

#### Dry Run (Preview Without Writing Files)
```bash
thakaamed-dicom anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --dry-run
```

### Utility Commands

#### List All Available Presets
```bash
thakaamed-dicom presets
```

#### Validate a Built-in Preset
```bash
thakaamed-dicom validate --preset sfda_safe_harbor
thakaamed-dicom validate --preset research
thakaamed-dicom validate --preset full_anonymization
```

#### Validate a Custom YAML Config
```bash
thakaamed-dicom validate --config ./my_custom_preset.yaml
```

#### Generate Report from Existing JSON Audit
```bash
thakaamed-dicom report \
    --from-json ./reports/anonymization_report_20240115.json \
    --format pdf
```

#### Show Version
```bash
thakaamed-dicom version
```

#### Show Help
```bash
thakaamed-dicom --help
thakaamed-dicom anonymize --help
```

---

### Example Output

```
---------------------------------------------
  THAKAAMED DICOM Anonymizer
---------------------------------------------

Input: /path/to/dicom
Output: /path/to/output
Preset: SFDA Safe Harbor

Processing files...
[################################] 100% | 150/150

Processing Summary
+----------------------+--------+
| Files Processed      |    150 |
| Files Successful     |    150 |
| Tags Modified        |  4,250 |
| Tags Removed         |  1,890 |
| UIDs Remapped        |    165 |
+----------------------+--------+

Reports generated:
  ./output/reports/anonymization_report_20240115_143022.pdf
  ./output/reports/anonymization_report_20240115_143022.json
  ./output/reports/anonymization_report_20240115_143022.csv

Anonymization complete! Files saved to /path/to/output
```

## Built-in Presets

| Preset | Description | Use Case |
|--------|-------------|----------|
| `sfda_safe_harbor` | Maximum privacy protection | Data export, public sharing |
| `research` | Retains longitudinal data | Research studies with date shifting |
| `full_anonymization` | Complete de-identification | Maximum anonymization |

## CLI Reference

### anonymize

```bash
thakaamed-dicom anonymize [OPTIONS]

Options:
  -i, --input PATH          Input DICOM file or directory (required)
  -o, --output PATH         Output file or directory (required)
  -p, --preset NAME         Preset name or path to YAML (required)
  --date-anchor DATE        Anchor date for shifting (YYYYMMDD)
  -n, --dry-run            Preview without writing files
  --parallel/--no-parallel  Enable/disable parallel processing
  -w, --workers N           Number of parallel workers (default: 4)
  --report-format FORMAT    Report format: pdf, json, csv, all, none
  --no-reports             Disable report generation
  --report-dir PATH        Directory for reports
```

### validate

```bash
thakaamed-dicom validate --preset NAME
thakaamed-dicom validate --config PATH
```

### presets

```bash
thakaamed-dicom presets  # List all available presets
```

### report

```bash
thakaamed-dicom report --from-json audit.json --format pdf
```

## Documentation

- [Installation Guide](docs/installation.md)
- [CLI Reference](docs/cli-reference.md)
- [Configuration Guide](docs/configuration.md)
- [Compliance Documentation](docs/compliance.md)
- [API Reference](docs/api-reference.md)

## Python API

```python
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor

# Load preset
preset = load_preset("sfda_safe_harbor")

# Create processor
processor = DicomProcessor(preset=preset)

# Process single file
stats = processor.process_file("input.dcm", "output.dcm")
print(f"Success: {stats.success}")

# Process directory
stats = processor.process_directory(
    input_dir="./input",
    output_dir="./output",
    parallel=True,
    workers=4,
)
print(f"Processed: {stats.files_processed}")
```

## Compliance

THAKAAMED DICOM Anonymizer implements:

- **DICOM PS3.15**: Basic Application Level Confidentiality Profile
- **HIPAA Safe Harbor**: 45 CFR 164.514(b)(2) de-identification method
- **Saudi PDPL**: Personal Data Protection Law requirements

### De-identification Markers

All processed files include:
- PatientIdentityRemoved (0012,0062) = "YES"
- DeidentificationMethod (0012,0063) = "THAKAAMED - [Preset Name]"

### UID Remapping

UIDs are consistently remapped using:
- SHA-256 hash-based deterministic mapping
- 2.25 (UUID) root format
- Cross-file consistency for referential integrity

## License

**Non-Commercial Research License** (CC BY-NC-ND 4.0 with Additional Restrictions)

This software is provided for **RESEARCH AND EDUCATIONAL PURPOSES ONLY**.

### You MAY:
- Use for academic research and publications
- Use for educational purposes and learning
- Study and learn from the source code

### You MAY NOT:
- Use for commercial purposes
- Use in production healthcare environments
- Sell, sublicense, or redistribute
- Create derivative works

### Commercial Licensing

For commercial use, production deployment, or healthcare facility integration, please contact:

**Email:** licensing@thakaamed.com | **Web:** https://thakaamed.ai/licensing

See [LICENSE](LICENSE) for full terms.

## Acknowledgments

- Built with [pydicom](https://pydicom.github.io/)
- Reports generated with [ReportLab](https://www.reportlab.com/)
- CLI powered by [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)

---

<div align="center">

**THAKAAMED AI** | Enterprise Healthcare Solutions

*Vision 2030 Healthcare Transformation*

https://thakaamed.ai | contact@thakaamed.com

---

*Made with love in Riyadh, KSA*

*Good vibes only. 1337*

</div>
