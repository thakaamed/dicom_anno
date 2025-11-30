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
"""YAML configuration loader with validation."""

from pathlib import Path

import yaml

from thakaamed_dicom.config.models import AppConfig, PresetConfig


def get_bundled_presets_path() -> Path:
    """Get path to bundled preset files."""
    return Path(__file__).parent.parent / "presets"


def get_user_presets_path() -> Path:
    """Get path to user preset files (in home directory)."""
    return Path.home() / ".thakaamed" / "presets"


def load_preset(name_or_path: str | Path) -> PresetConfig:
    """Load and validate a preset configuration.

    Args:
        name_or_path: Either a preset name (e.g., 'sfda_safe_harbor') or path to YAML file

    Returns:
        Validated PresetConfig instance

    Raises:
        FileNotFoundError: If preset file not found
        ValueError: If YAML parsing or validation fails
    """
    path = Path(name_or_path)

    # If it's a name (not a path), search for it
    if not path.suffix:
        # Try bundled presets first
        bundled = get_bundled_presets_path()
        bundled_file = bundled / f"{name_or_path}.yaml"

        if bundled_file.exists():
            path = bundled_file
        else:
            # Try user presets
            user_file = get_user_presets_path() / f"{name_or_path}.yaml"
            if user_file.exists():
                path = user_file
            else:
                raise FileNotFoundError(
                    f"Preset '{name_or_path}' not found in bundled or user presets. "
                    f"Available bundled presets: {list_preset_names()}"
                )

    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found: {path}")

    # Load YAML (secure loading)
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML syntax in {path}: {e}") from e

    if not data:
        raise ValueError(f"Empty configuration file: {path}")

    # Validate with Pydantic
    try:
        return PresetConfig(**data)
    except Exception as e:
        raise ValueError(f"Configuration validation failed for {path}: {e}") from e


def load_app_config(path: str | Path) -> AppConfig:
    """Load and validate application configuration.

    Args:
        path: Path to YAML configuration file

    Returns:
        Validated AppConfig instance
    """
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Application config not found: {config_path}")

    with open(config_path) as f:
        data = yaml.safe_load(f)

    if not data:
        raise ValueError(f"Empty configuration file: {config_path}")

    return AppConfig(**data)


def list_preset_names() -> list[str]:
    """List names of all available bundled presets."""
    bundled = get_bundled_presets_path()
    if not bundled.exists():
        return []
    return [p.stem for p in bundled.glob("*.yaml")]


def list_available_presets() -> list[dict]:
    """List all available presets (bundled + user) with details."""
    presets = []

    # Bundled presets
    bundled = get_bundled_presets_path()
    if bundled.exists():
        for yaml_file in bundled.glob("*.yaml"):
            try:
                config = load_preset(yaml_file)
                presets.append({
                    "name": config.name,
                    "filename": yaml_file.stem,
                    "description": config.description,
                    "location": "bundled",
                    "path": str(yaml_file),
                    "compliance": config.compliance,
                })
            except Exception:
                pass  # Skip invalid presets

    # User presets
    user_dir = get_user_presets_path()
    if user_dir.exists():
        for yaml_file in user_dir.glob("*.yaml"):
            try:
                config = load_preset(yaml_file)
                presets.append({
                    "name": config.name,
                    "filename": yaml_file.stem,
                    "description": config.description,
                    "location": "user",
                    "path": str(yaml_file),
                    "compliance": config.compliance,
                })
            except Exception:
                pass

    return presets
