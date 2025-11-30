# Installation Guide

Complete installation instructions for THAKAAMED DICOM Anonymizer.

## Requirements

- **Python**: 3.10 or higher
- **Operating System**: Windows, macOS, or Linux
- **Disk Space**: ~50MB for installation

## Installation Methods

### Local Installation (Development/Testing)

For testing before publishing, install from the local source:

```bash
# Navigate to the project directory
cd DICOM-ANNO

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install in editable mode with dev dependencies (using uv - recommended)
uv pip install -e ".[dev]"

# Or using pip
pip install -e ".[dev]"
```

This installs the package in "editable" mode, meaning changes to the source code are immediately reflected without reinstalling.

### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create venv and install from local source
uv venv
source .venv/bin/activate
uv pip install -e ".[dev]"
```

### From PyPI (After Publishing)

Once the package is published to PyPI:

```bash
pip install thakaamed-dicom

# Or with uv
uv pip install thakaamed-dicom
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
# Windows local installation
cd DICOM-ANNO
py -m venv .venv
.venv\Scripts\activate
py -m pip install -e ".[dev]"
```

### macOS

- Use Terminal or iTerm2
- Install Python via Homebrew if needed: `brew install python@3.11`

```bash
# macOS local installation
cd DICOM-ANNO
python3 -m venv .venv
source .venv/bin/activate
pip3 install -e ".[dev]"
```

### Linux

- Most distributions include Python 3.10+
- May need to install pip separately: `sudo apt install python3-pip`

```bash
# Debian/Ubuntu
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Local installation
cd DICOM-ANNO
python3 -m venv .venv
source .venv/bin/activate
pip3 install -e ".[dev]"
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
cd DICOM-ANNO
pip install -e ".[dev]"

# When done, deactivate
deactivate
```

## Docker Installation (Local Build)

For containerized environments, build from local source:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -e .

ENTRYPOINT ["thakaamed-dicom"]
```

Build and run:

```bash
# From the DICOM-ANNO directory
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
pip install -e ".[dev]"
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
3. Try reinstalling: `pip install -e ".[dev]" --force-reinstall`

## Upgrading (Local Development)

To get the latest changes when developing locally:

```bash
# Pull latest code
git pull

# Reinstall if dependencies changed
pip install -e ".[dev]"
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
