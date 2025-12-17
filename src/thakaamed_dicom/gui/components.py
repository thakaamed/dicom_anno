# ============================================================================
#  THAKAAMED DICOM Anonymizer
#  Copyright (c) 2024 THAKAAMED AI. All rights reserved.
#
#  https://thakaamed.com | Enterprise Healthcare Solutions
#
#  LICENSE: CC BY-NC-ND 4.0 (Non-Commercial)
#  This software is for RESEARCH AND EDUCATIONAL PURPOSES ONLY.
#  For commercial licensing: licensing@thakaamed.com
#
#  See LICENSE file for full terms. | Built for Saudi Vision 2030
# ============================================================================
"""Reusable UI components for the THAKAAMED DICOM GUI."""

from dataclasses import dataclass


@dataclass
class PresetInfo:
    """Information about an anonymization preset."""
    
    id: str
    name: str
    description: str
    icon: str


# Available presets with descriptions
PRESETS = [
    PresetInfo(
        id="sfda_safe_harbor",
        name="SFDA Safe Harbor",
        description="Maximum privacy - removes all identifying information (HIPAA compliant)",
        icon="🔒",
    ),
    PresetInfo(
        id="research",
        name="Research Mode",
        description="Balanced for research - keeps dates shifted, removes direct identifiers",
        icon="🔬",
    ),
    PresetInfo(
        id="full_anonymization",
        name="Full Anonymization",
        description="Complete de-identification - removes all optional metadata",
        icon="🛡️",
    ),
]


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


def is_dicom_file(filename: str) -> bool:
    """Check if a file appears to be a DICOM file."""
    # Common DICOM extensions
    dicom_extensions = {".dcm", ".dicom", ".dic", ".ima"}
    lower_name = filename.lower()
    
    # Check extension
    for ext in dicom_extensions:
        if lower_name.endswith(ext):
            return True
    
    # DICOM files often have no extension or numeric names
    # We'll accept files without extensions for now
    if "." not in filename:
        return True
    
    return False

