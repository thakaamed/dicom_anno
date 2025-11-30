"""Tests for Pydantic configuration models."""

import pytest
from pydantic import ValidationError

from dicom_anonymizer.config.models import (
    ActionCode,
    AppConfig,
    DateHandling,
    PresetConfig,
    TagRule,
)


class TestActionCode:
    """Tests for ActionCode enum."""

    def test_all_action_codes_exist(self):
        """All DICOM PS3.15 action codes are defined."""
        assert ActionCode.D.value == "D"
        assert ActionCode.Z.value == "Z"
        assert ActionCode.X.value == "X"
        assert ActionCode.K.value == "K"
        assert ActionCode.C.value == "C"
        assert ActionCode.U.value == "U"

    def test_action_code_from_string(self):
        """Action codes can be created from strings."""
        assert ActionCode("D") == ActionCode.D
        assert ActionCode("X") == ActionCode.X


class TestDateHandling:
    """Tests for DateHandling enum."""

    def test_all_date_handling_options(self):
        """All date handling options are defined."""
        assert DateHandling.REMOVE.value == "remove"
        assert DateHandling.SHIFT.value == "shift"
        assert DateHandling.KEEP_YEAR.value == "keep_year"


class TestTagRule:
    """Tests for TagRule model."""

    def test_valid_tag_rule(self):
        """Valid tag rule is accepted."""
        rule = TagRule(
            tag="(0010,0010)",
            action=ActionCode.Z,
            description="Patient Name",
        )
        assert rule.tag == "(0010,0010)"
        assert rule.action == ActionCode.Z

    def test_invalid_tag_format_rejected(self):
        """Invalid tag format is rejected."""
        with pytest.raises(ValidationError):
            TagRule(tag="invalid", action=ActionCode.Z)

    def test_tag_format_uppercase(self):
        """Tag format accepts uppercase hex."""
        rule = TagRule(tag="(0010,00FF)", action=ActionCode.X)
        assert rule.tag == "(0010,00FF)"

    def test_tag_format_lowercase(self):
        """Tag format accepts lowercase hex."""
        rule = TagRule(tag="(0010,00ff)", action=ActionCode.X)
        assert rule.tag == "(0010,00ff)"

    def test_optional_replacement(self):
        """Replacement field is optional."""
        rule = TagRule(tag="(0010,0010)", action=ActionCode.Z)
        assert rule.replacement is None

    def test_replacement_value(self):
        """Replacement value is stored."""
        rule = TagRule(
            tag="(0010,0010)",
            action=ActionCode.Z,
            replacement="ANONYMOUS",
        )
        assert rule.replacement == "ANONYMOUS"


class TestPresetConfig:
    """Tests for PresetConfig model."""

    def test_minimal_valid_config(self):
        """Minimal valid configuration is accepted."""
        config = PresetConfig(
            name="Test",
            description="Test preset",
        )
        assert config.name == "Test"
        assert config.date_handling == DateHandling.REMOVE  # Default

    def test_complete_config(self, sample_preset):
        """Complete configuration is accepted."""
        assert sample_preset.name == "Test Preset"
        assert len(sample_preset.tag_rules) == 4
        assert sample_preset.remove_private_tags is True

    def test_invalid_date_shift_base_rejected(self):
        """Invalid date_shift_base format is rejected."""
        with pytest.raises(ValidationError):
            PresetConfig(
                name="Test",
                description="Test",
                date_shift_base="not-a-date",
            )

    def test_valid_date_shift_base_accepted(self):
        """Valid date_shift_base format is accepted."""
        config = PresetConfig(
            name="Test",
            description="Test",
            date_handling=DateHandling.SHIFT,
            date_shift_base="20240115",
        )
        assert config.date_shift_base == "20240115"

    def test_longitudinal_with_remove_rejected(self):
        """retain_longitudinal with date_handling=remove is rejected."""
        with pytest.raises(ValidationError):
            PresetConfig(
                name="Test",
                description="Test",
                retain_longitudinal=True,
                date_handling=DateHandling.REMOVE,
            )

    def test_longitudinal_with_shift_accepted(self):
        """retain_longitudinal with date_handling=shift is accepted."""
        config = PresetConfig(
            name="Test",
            description="Test",
            retain_longitudinal=True,
            date_handling=DateHandling.SHIFT,
        )
        assert config.retain_longitudinal is True

    def test_age_threshold_bounds(self):
        """Age threshold must be between 0 and 120."""
        # Valid threshold
        config = PresetConfig(name="Test", description="Test", age_threshold=89)
        assert config.age_threshold == 89

        # Invalid threshold - too high
        with pytest.raises(ValidationError):
            PresetConfig(name="Test", description="Test", age_threshold=150)

        # Invalid threshold - negative
        with pytest.raises(ValidationError):
            PresetConfig(name="Test", description="Test", age_threshold=-1)

    def test_default_version(self):
        """Default version is 1.0.0."""
        config = PresetConfig(name="Test", description="Test")
        assert config.version == "1.0.0"

    def test_invalid_version_format_rejected(self):
        """Invalid version format is rejected."""
        with pytest.raises(ValidationError):
            PresetConfig(name="Test", description="Test", version="invalid")


class TestAppConfig:
    """Tests for AppConfig model."""

    def test_default_values(self):
        """Default values are set correctly."""
        config = AppConfig()
        assert config.default_preset == "sfda_safe_harbor"
        assert config.output_format == "pdf"
        assert config.log_level == "INFO"
        assert config.parallel_workers == 4

    def test_custom_values(self):
        """Custom values are accepted."""
        config = AppConfig(
            default_preset="research",
            output_format="json",
            log_level="DEBUG",
            parallel_workers=8,
        )
        assert config.default_preset == "research"
        assert config.output_format == "json"
        assert config.parallel_workers == 8

    def test_invalid_output_format_rejected(self):
        """Invalid output format is rejected."""
        with pytest.raises(ValidationError):
            AppConfig(output_format="invalid")

    def test_workers_bounds(self):
        """Workers must be between 1 and 32."""
        # Valid workers
        config = AppConfig(parallel_workers=16)
        assert config.parallel_workers == 16

        # Too many workers
        with pytest.raises(ValidationError):
            AppConfig(parallel_workers=100)

        # Too few workers
        with pytest.raises(ValidationError):
            AppConfig(parallel_workers=0)
