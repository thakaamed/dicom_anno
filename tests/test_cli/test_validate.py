"""Tests for validate command."""


from thakaamed_dicom.cli.main import main


class TestValidateCommand:
    """Tests for the validate command."""

    def test_validate_requires_option(self, cli_runner):
        """Validate command requires --preset or --config."""
        result = cli_runner.invoke(main, ["validate"])
        assert result.exit_code != 0
        assert "preset" in result.output.lower() or "config" in result.output.lower()

    def test_validate_bundled_preset_sfda(self, cli_runner):
        """Validate command accepts bundled sfda_safe_harbor preset."""
        result = cli_runner.invoke(main, ["validate", "--preset", "sfda_safe_harbor"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()
        assert "SFDA Safe Harbor" in result.output

    def test_validate_bundled_preset_research(self, cli_runner):
        """Validate command accepts bundled research preset."""
        result = cli_runner.invoke(main, ["validate", "--preset", "research"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()
        assert "Research" in result.output

    def test_validate_bundled_preset_full(self, cli_runner):
        """Validate command accepts bundled full_anonymization preset."""
        result = cli_runner.invoke(main, ["validate", "--preset", "full_anonymization"])
        assert result.exit_code == 0
        assert "valid" in result.output.lower()
        assert "Full Anonymization" in result.output

    def test_validate_invalid_preset_name(self, cli_runner):
        """Validate command fails for non-existent preset."""
        result = cli_runner.invoke(main, ["validate", "--preset", "nonexistent_preset"])
        assert result.exit_code != 0
        assert "not found" in result.output.lower()

    def test_validate_custom_config(self, cli_runner, sample_config_file):
        """Validate command accepts custom config file."""
        result = cli_runner.invoke(
            main, ["validate", "--config", str(sample_config_file)]
        )
        assert result.exit_code == 0
        assert "valid" in result.output.lower()

    def test_validate_shows_details(self, cli_runner):
        """Validate command shows preset details."""
        result = cli_runner.invoke(main, ["validate", "--preset", "sfda_safe_harbor"])
        assert result.exit_code == 0
        # Should show details about the preset
        assert "Tag Rules" in result.output or "tag_rules" in result.output.lower()
        assert "Date Handling" in result.output or "date_handling" in result.output.lower()
