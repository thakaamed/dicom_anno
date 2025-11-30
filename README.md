<div align="center">

# 🏥 DICOM Anonymizer

### مُجهِّز بيانات DICOM الطبية

**Empowering Healthcare Research with Privacy-First Medical Imaging**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyPI version](https://img.shields.io/badge/pypi-v1.0.1-blue.svg)](https://pypi.org/project/dicom_anonymizer/)
[![SFDA Compliant](https://img.shields.io/badge/SFDA-Compliant-006C35.svg)](https://www.sfda.gov.sa/)
[![SDAIA Ready](https://img.shields.io/badge/SDAIA-PDPL_Ready-006C35.svg)](https://sdaia.gov.sa/)
[![DICOM PS3.15](https://img.shields.io/badge/DICOM-PS3.15-orange.svg)](https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_e.html)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

🇸🇦 **Built in Saudi Arabia for Global Healthcare** 🇸🇦

*Accelerating Vision 2030 Healthcare & AI Transformation*

**THAKAAMED AI** | https://thakaamed.ai

</div>

---

## 🌟 For Researchers & Healthcare Innovators

DICOM Anonymizer is purpose-built to help **researchers, hospitals, and AI teams** unlock the power of medical imaging data while maintaining the highest standards of patient privacy and regulatory compliance.

> **"Enabling world-class medical AI research, ethically and compliantly."**

### 🏛️ Saudi Regulatory Compliance First

| 🇸🇦 Saudi Standards | Status | Description |
|---------------------|--------|-------------|
| **SFDA** (Saudi FDA) | ✅ Compliant | Medical device software compliance ready |
| **SDAIA PDPL** | ✅ Compliant | Saudi Personal Data Protection Law (نظام حماية البيانات الشخصية) |
| **NDMO** | ✅ Ready | National Data Management Office guidelines |
| **MOH Guidelines** | ✅ Aligned | Ministry of Health data sharing standards |

### 🌍 International Standards

| Standard | Status | Description |
|----------|--------|-------------|
| **DICOM PS3.15** | ✅ Compliant | International medical imaging de-identification standard |
| **HIPAA Safe Harbor** | ✅ Compliant | US healthcare privacy (for international collaboration) |
| **GDPR** | ✅ Ready | EU data protection (for European partnerships) |

---

## Overview

DICOM Anonymizer is a professional-grade, cross-platform tool for de-identifying DICOM medical imaging files. Built specifically for healthcare institutions, it enables:

- **🔬 Research Excellence**: Safely share medical imaging data for AI/ML research
- **🏥 Hospital Data Export**: Export anonymized studies for multi-center collaborations
- **🎓 Academic Publications**: Prepare datasets for peer-reviewed research
- **🤖 AI Model Training**: Create privacy-safe datasets for medical AI development

### Key Features

| Feature | Description |
|---------|-------------|
| **SFDA Safe Harbor Preset** | Maximum privacy protection for regulatory compliance |
| **Research Preset** | Balanced anonymization with date shifting for longitudinal studies |
| **Full Anonymization** | Complete de-identification for public dataset sharing |
| **Branded PDF Reports** | Audit-ready documentation for ethics committees |
| **Parallel Processing** | Process thousands of DICOM files in minutes |
| **Offline Capable** | Works in air-gapped hospital networks |

### Why DICOM Anonymizer?

- 🇸🇦 **Saudi-First Design**: Built with SFDA/SDAIA/PDPL compliance as the foundation
- 🔒 **Privacy by Design**: No cloud uploads, 100% local processing
- 📋 **Audit Ready**: Generate compliance reports for IRB and ethics committees
- ⚡ **Fast & Efficient**: Multi-threaded processing for large datasets
- 🎨 **Professional Output**: Branded reports worthy of stakeholder presentations

## Quick Start

### Installation from PyPI

```bash
pip install dicom_anonymizer
```

### Installation from Source

```bash
# Clone/navigate to the project
cd dicom_anno

# Create virtual environment and install (using uv - recommended)
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"

# Or using pip
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### Check Version

```bash
dicom-anonym --version
```

---

## 🔒 Offline Installation (Air-Gapped / No Internet)

For healthcare environments without internet access, follow these steps:

### Step 1: Prepare the Offline Package (On a machine WITH internet)

```bash
# Navigate to project directory
cd dicom_anno

# Create a directory to store all dependencies
mkdir -p offline_packages

# Download all dependencies as wheel files
pip download -d ./offline_packages -r requirements.txt

# Also download the package build tools
pip download -d ./offline_packages pip setuptools wheel build

# Create a distributable archive (optional)
tar -czvf dicom-anonymizer-offline.tar.gz \
    offline_packages/ \
    src/ \
    pyproject.toml \
    requirements.txt \
    README.md \
    LICENSE
```

### Step 2: Transfer to Offline Machine

Transfer the following to the air-gapped machine via USB/secure transfer:
- `dicom-anonymizer-offline.tar.gz` (or the entire folder with `offline_packages/`)

### Step 3: Install on Offline Machine

```bash
# Extract if using archive
tar -xzvf dicom-anonymizer-offline.tar.gz
cd dicom_anno

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

# Install the DICOM Anonymizer
pip install --no-index --find-links=./offline_packages -e .

# Verify installation
dicom-anonym --version
```

### Alternative: Single Wheel Distribution

#### On machine WITH internet:
```bash
cd dicom_anno

# Build the wheel
pip install build
python -m build

# The wheel will be in dist/
# e.g., dist/dicom_anonymizer-1.0.1-py3-none-any.whl

# Download dependencies
mkdir -p dist/deps
pip download -d ./dist/deps pydicom pyyaml click rich reportlab pillow
```

#### On OFFLINE machine:
```bash
# Install dependencies first
pip install --no-index --find-links=./dist/deps pydicom pyyaml click rich reportlab pillow

# Install the wheel
pip install --no-index ./dist/dicom_anonymizer-1.0.1-py3-none-any.whl
```

### Windows Offline Installation

```powershell
# Extract archive
Expand-Archive -Path dicom-anonymizer-offline.zip -DestinationPath C:\dicom_anon

# Navigate to directory
cd C:\dicom_anon

# Create virtual environment
python -m venv .venv

# Activate
.venv\Scripts\activate

# Install from offline packages
pip install --no-index --find-links=.\offline_packages pip setuptools wheel
pip install --no-index --find-links=.\offline_packages -r requirements.txt
pip install --no-index --find-links=.\offline_packages -e .

# Verify
dicom-anonym --version
```

### Verify Offline Installation

```bash
# Check version
dicom-anonym --version

# List presets (no internet required)
dicom-anonym presets

# Validate a preset
dicom-anonym validate --preset sfda_safe_harbor

# Test anonymization
dicom-anonym anonymize \
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
dicom-anonym anonymize --input /path/to/dicom --output /path/to/output --preset sfda_safe_harbor

# List available presets
dicom-anonym presets

# Validate a preset configuration
dicom-anonym validate --preset research

# Show version
dicom-anonym --version
dicom-anonym version
```

---

## 📚 Complete Examples

### Single File Anonymization

#### SFDA Safe Harbor (Maximum Privacy)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/patient_scan.dcm \
    -o ./anonymized_output/anon_scan.dcm \
    -p sfda_safe_harbor
```

#### Research Preset (Keeps Dates Shifted)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/patient_scan.dcm \
    -o ./anonymized_output/research_scan.dcm \
    -p research \
    --date-anchor 20200101
```

#### Full Anonymization (Maximum Removal)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/patient_scan.dcm \
    -o ./anonymized_output/full_anon_scan.dcm \
    -p full_anonymization
```

### Batch Processing (Entire Directory)

#### Process All DICOM Files in a Folder
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor
```

#### With More Workers (Faster Processing)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --workers 8
```

#### Sequential Processing (No Parallel)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --no-parallel
```

### Report Options

#### Generate All Reports (PDF + JSON + CSV)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-format all
```

#### Generate Only PDF Report
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-format pdf
```

#### Generate Only JSON Report
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-format json
```

#### No Reports (Fast Processing)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --no-reports
```

#### Custom Report Directory
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --report-dir ./my_reports/
```

### Preview & Testing

#### Dry Run (Preview Without Writing Files)
```bash
dicom-anonym anonymize \
    -i ./dicom_files/ \
    -o ./anonymized_output/ \
    -p sfda_safe_harbor \
    --dry-run
```

### Utility Commands

#### List All Available Presets
```bash
dicom-anonym presets
```

#### Validate a Built-in Preset
```bash
dicom-anonym validate --preset sfda_safe_harbor
dicom-anonym validate --preset research
dicom-anonym validate --preset full_anonymization
```

#### Validate a Custom YAML Config
```bash
dicom-anonym validate --config ./my_custom_preset.yaml
```

#### Generate Report from Existing JSON Audit
```bash
dicom-anonym report \
    --from-json ./reports/anonymization_report_20240115.json \
    --format pdf
```

#### Show Version
```bash
dicom-anonym --version
dicom-anonym version
```

#### Show Help
```bash
dicom-anonym --help
dicom-anonym anonymize --help
```

---

### Example Output

```
---------------------------------------------
  DICOM Anonymizer
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
dicom-anonym anonymize [OPTIONS]

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
dicom-anonym validate --preset NAME
dicom-anonym validate --config PATH
```

### presets

```bash
dicom-anonym presets  # List all available presets
```

### report

```bash
dicom-anonym report --from-json audit.json --format pdf
```

## Documentation

- [Installation Guide](docs/installation.md)
- [CLI Reference](docs/cli-reference.md)
- [Configuration Guide](docs/configuration.md)
- [Compliance Documentation](docs/compliance.md)
- [API Reference](docs/api-reference.md)

## Python API

```python
from dicom_anonymizer.config.loader import load_preset
from dicom_anonymizer.engine.processor import DicomProcessor

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

## 🏛️ Compliance & Regulatory Standards

### 🇸🇦 Saudi Arabia (Primary)

DICOM Anonymizer is designed with **Saudi regulatory compliance as the foundation**:

| Authority | Regulation | Status |
|-----------|------------|--------|
| **SFDA** | Medical Device Software Guidelines | ✅ Compliant |
| **SDAIA** | Personal Data Protection Law (PDPL) نظام حماية البيانات الشخصية | ✅ Compliant |
| **NDMO** | National Data Management Office Standards | ✅ Ready |
| **MOH** | Ministry of Health Data Sharing Guidelines | ✅ Aligned |

### 🌍 International Standards

| Standard | Description | Status |
|----------|-------------|--------|
| **DICOM PS3.15** | Basic Application Level Confidentiality Profile | ✅ Implemented |
| **HIPAA Safe Harbor** | 45 CFR 164.514(b)(2) de-identification method | ✅ Compliant |
| **GDPR Art. 89** | Research exemption requirements | ✅ Ready |

### De-identification Markers

All processed files include DICOM compliance markers:
```
PatientIdentityRemoved (0012,0062) = "YES"
DeidentificationMethod (0012,0063) = "DICOM Anonymizer - SFDA Safe Harbor"
```

### UID Remapping

UIDs are consistently remapped using:
- SHA-256 hash-based deterministic mapping
- 2.25 (UUID) root format for new UIDs
- Cross-file consistency for referential integrity (multi-study support)

## License

MIT License

Copyright (c) 2024 THAKAAMED AI

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

See [LICENSE](LICENSE) for full terms.

## Acknowledgments

- Built with [pydicom](https://pydicom.github.io/)
- Reports generated with [ReportLab](https://www.reportlab.com/)
- CLI powered by [Click](https://click.palletsprojects.com/) and [Rich](https://rich.readthedocs.io/)

---

<div align="center">

## 🇸🇦 Saudi Made - صُنع في السعودية

### Made with ♥ in Riyadh

---

**THAKAAMED AI** | Enterprise Healthcare Solutions

*Accelerating Saudi Vision 2030 Healthcare & AI Transformation*

رؤية السعودية 2030 - تحويل الرعاية الصحية

---

📧 **contact@thakaamed.com** | 🌐 **https://thakaamed.ai**

---

*Empowering researchers to lead the future of medical AI*

*تمكين الباحثين لقيادة مستقبل الذكاء الاصطناعي الطبي*

</div>
