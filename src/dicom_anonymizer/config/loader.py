# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""YAML configuration loader with validation."""

from importlib.resources import files
from pathlib import Path

import yaml

from dicom_anonymizer.config.models import AppConfig, PresetConfig


def get_user_presets_path() -> Path:
    """Get path to user preset files (in home directory)."""
    return Path.home() / ".dicom_anonymizer" / "presets"


def _load_bundled_preset(name: str) -> PresetConfig | None:
    """Load a bundled preset by name using importlib.resources.

    This properly handles packaged resources whether installed as a wheel,
    in a zip archive, or in development mode.

    Args:
        name: Preset name (without .yaml extension)

    Returns:
        PresetConfig if found, None otherwise
    """
    try:
        presets_package = files("dicom_anonymizer.presets")
        preset_file = presets_package.joinpath(f"{name}.yaml")

        # Use read_text() which works for both filesystem and zip resources
        if hasattr(preset_file, "read_text"):
            try:
                content = preset_file.read_text(encoding="utf-8")
                data = yaml.safe_load(content)
                if data:
                    return PresetConfig(**data)
            except FileNotFoundError:
                pass
    except Exception:
        pass
    return None


def _list_bundled_preset_names() -> list[str]:
    """List names of bundled presets using importlib.resources.

    Returns:
        List of preset names (without .yaml extension)
    """
    try:
        presets_package = files("dicom_anonymizer.presets")
        # iterdir() works on Traversable objects
        return [
            f.name.removesuffix(".yaml")
            for f in presets_package.iterdir()
            if f.name.endswith(".yaml")
        ]
    except Exception:
        return []


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
        # Try bundled presets first (using importlib.resources)
        preset = _load_bundled_preset(str(name_or_path))
        if preset is not None:
            return preset

        # Try user presets (filesystem)
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

    # Load YAML from filesystem (secure loading)
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
    return _list_bundled_preset_names()


def list_available_presets() -> list[dict]:
    """List all available presets (bundled + user) with details."""
    presets = []

    # Bundled presets (using importlib.resources)
    for preset_name in _list_bundled_preset_names():
        try:
            config = _load_bundled_preset(preset_name)
            if config:
                presets.append(
                    {
                        "name": config.name,
                        "filename": preset_name,
                        "description": config.description,
                        "location": "bundled",
                        "path": f"<bundled>/{preset_name}.yaml",
                        "compliance": config.compliance,
                    }
                )
        except Exception:
            pass  # Skip invalid presets

    # User presets (filesystem)
    user_dir = get_user_presets_path()
    if user_dir.exists():
        for yaml_file in user_dir.glob("*.yaml"):
            try:
                config = load_preset(yaml_file)
                presets.append(
                    {
                        "name": config.name,
                        "filename": yaml_file.stem,
                        "description": config.description,
                        "location": "user",
                        "path": str(yaml_file),
                        "compliance": config.compliance,
                    }
                )
            except Exception:
                pass

    return presets
