"""Tests for configuration loader."""

import pytest

from dicom_anonymizer.config.loader import (
    get_bundled_presets_path,
    get_user_presets_path,
    list_available_presets,
    list_preset_names,
    load_preset,
)
from dicom_anonymizer.config.models import PresetConfig


class TestLoadPreset:
    """Tests for load_preset function."""

    def test_load_bundled_preset_sfda(self):
        """Load bundled sfda_safe_harbor preset."""
        config = load_preset("sfda_safe_harbor")
        assert isinstance(config, PresetConfig)
        assert config.name == "SFDA Safe Harbor"
        assert "HIPAA Safe Harbor" in " ".join(config.compliance)

    def test_load_bundled_preset_research(self):
        """Load bundled research preset."""
        config = load_preset("research")
        assert isinstance(config, PresetConfig)
        assert config.name == "Research"
        assert config.retain_longitudinal is True

    def test_load_bundled_preset_full(self):
        """Load bundled full_anonymization preset."""
        config = load_preset("full_anonymization")
        assert isinstance(config, PresetConfig)
        assert config.name == "Full Anonymization"

    def test_load_by_path(self, sample_config_file):
        """Load preset by file path."""
        config = load_preset(sample_config_file)
        assert isinstance(config, PresetConfig)
        assert config.name == "Test YAML Preset"

    def test_nonexistent_preset_raises(self):
        """Non-existent preset raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            load_preset("nonexistent_preset")

    def test_invalid_yaml_raises(self, tmp_path):
        """Invalid YAML raises ValueError."""
        invalid_file = tmp_path / "invalid.yaml"
        invalid_file.write_text("name: [\ninvalid yaml")

        with pytest.raises(ValueError):
            load_preset(invalid_file)

    def test_empty_file_raises(self, tmp_path):
        """Empty file raises ValueError."""
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("")

        with pytest.raises(ValueError):
            load_preset(empty_file)

    def test_validation_error_for_invalid_config(self, tmp_path):
        """Invalid configuration raises ValueError."""
        invalid_config = tmp_path / "invalid_config.yaml"
        # Missing required fields
        invalid_config.write_text("name: 'Test'\n# missing description")

        with pytest.raises(ValueError):
            load_preset(invalid_config)


class TestListPresets:
    """Tests for preset listing functions."""

    def test_list_preset_names(self):
        """list_preset_names returns bundled preset names."""
        names = list_preset_names()
        assert "sfda_safe_harbor" in names
        assert "research" in names
        assert "full_anonymization" in names

    def test_list_available_presets(self):
        """list_available_presets returns preset details."""
        presets = list_available_presets()
        assert len(presets) >= 3

        # Check structure
        for preset in presets:
            assert "name" in preset
            assert "description" in preset
            assert "location" in preset
            assert "compliance" in preset

    def test_bundled_presets_location(self):
        """Bundled presets have location 'bundled'."""
        presets = list_available_presets()
        bundled = [p for p in presets if p["location"] == "bundled"]
        assert len(bundled) >= 3


class TestPresetPaths:
    """Tests for preset path functions."""

    def test_bundled_presets_path_exists(self):
        """Bundled presets directory exists."""
        path = get_bundled_presets_path()
        assert path.exists()
        assert path.is_dir()

    def test_user_presets_path(self):
        """User presets path is in home directory."""
        path = get_user_presets_path()
        assert ".dicom_anonymizer" in str(path)
        assert "presets" in str(path)
