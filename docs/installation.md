# Installation Guide

Complete installation instructions for THAKAAMED DICOM Anonymizer.

## Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: ~50MB for installation

## Installation Methods

### Installation from Source (Current Method)

> **Note:** This package is not yet published to PyPI. Install from source using the steps below.

```bash
# Navigate to the project directory
cd dicom_anno

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Install in editable mode
pip install -e .

# For development (includes pytest, ruff, mypy)
pip install -e ".[dev]"
```

This installs the package in "editable" mode, meaning changes to the source code are immediately reflected without reinstalling.

### Quick Install (Copy-Paste)

**Linux/macOS:**
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Windows:**
```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### From PyPI (Coming Soon)

Once the package is published to PyPI, installation will be simpler:

```bash
pip install thakaamed-dicom
```

## Verifying Installation

After installation, verify everything works:

```bash
# Check version
thakaamed-dicom version

# List available presets
thakaamed-dicom presets

# Get help
thakaamed-dicom --help
```

Expected output:

```
THAKAAMED DICOM Anonymizer v1.0.0
```

## Dependencies

The package automatically installs the following dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| pydicom | >=2.4.0 | DICOM file processing |
| click | >=8.0.0 | Command-line interface |
| rich | >=13.0.0 | Console formatting |
| pyyaml | >=6.0.0 | YAML configuration |
| pydantic | >=2.0.0 | Data validation |
| reportlab | >=4.0.0 | PDF report generation |

### Development Dependencies

When installing with `[dev]`, additional packages are included:

| Package | Purpose |
|---------|---------|
| pytest | Testing framework |
| pytest-cov | Coverage reporting |
| ruff | Linting and formatting |
| mypy | Type checking |

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt
- Python must be in your PATH
- Some terminals may not render Unicode correctly; use Windows Terminal for best results

```powershell
# Windows installation
cd dicom_anno
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### macOS

- Use Terminal or iTerm2
- Install Python via Homebrew if needed: `brew install python@3.11`

```bash
# macOS installation
cd dicom_anno
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### Linux

- Most distributions include Python 3.10+
- May need to install pip separately: `sudo apt install python3-pip`

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Installation
cd dicom_anno
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## Virtual Environment Setup

We recommend using a virtual environment to avoid dependency conflicts:

```bash
# Create virtual environment
python -m venv thakaamed-env

# Activate (Linux/macOS)
source thakaamed-env/bin/activate

# Activate (Windows)
thakaamed-env\Scripts\activate

# Install from local source
cd dicom_anno
pip install -r requirements.txt
pip install -e .

# When done, deactivate
deactivate
```

## Docker Installation (Local Build)

For containerized environments, build from local source:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt && pip install -e .

ENTRYPOINT ["thakaamed-dicom"]
```

Build and run:

```bash
# From the dicom_anno directory
docker build -t thakaamed-dicom .
docker run -v /path/to/dicom:/data thakaamed-dicom anonymize \
    -i /data/input -o /data/output -p sfda_safe_harbor
```

## Troubleshooting

### Common Issues

**Permission denied during installation**

```bash
# Use a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

**Command not found after installation**

```bash
# Ensure virtual environment is activated
source .venv/bin/activate

# Check installation
pip show thakaamed-dicom

# Verify CLI is available
which thakaamed-dicom
```

**Import errors with pydicom**

```bash
# Reinstall pydicom
pip uninstall pydicom
pip install pydicom>=2.4.0
```

### Getting Help

If you encounter issues:

1. Ensure you're using Python 3.10+: `python --version`
2. Ensure virtual environment is activated
3. Try reinstalling: `pip install -r requirements.txt && pip install -e . --force-reinstall`

## Upgrading (Local Development)

To get the latest changes when developing locally:

```bash
# Pull latest code
git pull

# Reinstall if dependencies changed
pip install -r requirements.txt
pip install -e .
```

## Uninstalling

To remove the package:

```bash
pip uninstall thakaamed-dicom

# Or simply deactivate and remove the virtual environment
deactivate
rm -rf .venv
```

---

Next: [CLI Reference](cli-reference.md) | [Configuration Guide](configuration.md)
