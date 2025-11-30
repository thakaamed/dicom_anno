"""Pytest configuration and fixtures."""


import pytest
from click.testing import CliRunner

from thakaamed_dicom.config.models import (
    ActionCode,
    DateHandling,
    PresetConfig,
    TagRule,
)


@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_preset():
    """Sample preset configuration for testing."""
    return PresetConfig(
        name="Test Preset",
        description="Test preset for unit tests",
        compliance=["Test Compliance"],
        date_handling=DateHandling.REMOVE,
        remove_private_tags=True,
        tag_rules=[
            TagRule(
                tag="(0010,0010)",
                action=ActionCode.Z,
                description="Patient Name",
            ),
            TagRule(
                tag="(0010,0020)",
                action=ActionCode.Z,
                description="Patient ID",
            ),
            TagRule(
                tag="(0010,0030)",
                action=ActionCode.X,
                description="Birth Date",
            ),
            TagRule(
                tag="(0020,000D)",
                action=ActionCode.U,
                description="Study UID",
            ),
        ],
    )


@pytest.fixture
def sample_yaml_content():
    """Sample YAML configuration content."""
    return """
name: "Test YAML Preset"
description: "Test preset from YAML"
version: "1.0.0"

compliance:
  - "Test Compliance"

date_handling: "remove"
remove_private_tags: true
age_threshold: 89

tag_rules:
  - tag: "(0010,0010)"
    action: "Z"
    description: "Patient Name"
"""


@pytest.fixture
def invalid_yaml_content():
    """Invalid YAML content for testing error handling."""
    return """
name: "Invalid"
description: "Missing required fields
  - broken yaml
"""


@pytest.fixture
def sample_config_file(tmp_path, sample_yaml_content):
    """Create a sample YAML config file."""
    config_file = tmp_path / "test_preset.yaml"
    config_file.write_text(sample_yaml_content)
    return config_file
