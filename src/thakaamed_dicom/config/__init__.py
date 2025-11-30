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
"""Configuration module for THAKAAMED DICOM Anonymizer."""

from thakaamed_dicom.config.loader import (
    get_bundled_presets_path,
    get_user_presets_path,
    list_available_presets,
    load_preset,
)
from thakaamed_dicom.config.models import (
    ActionCode,
    AppConfig,
    DateHandling,
    PresetConfig,
    TagRule,
)

__all__ = [
    "ActionCode",
    "DateHandling",
    "TagRule",
    "PresetConfig",
    "AppConfig",
    "load_preset",
    "list_available_presets",
    "get_bundled_presets_path",
    "get_user_presets_path",
]
