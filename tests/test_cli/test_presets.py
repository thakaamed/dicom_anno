"""Tests for presets command."""


from thakaamed_dicom.cli.main import main


class TestPresetsCommand:
    """Tests for the presets command."""

    def test_presets_lists_available(self, cli_runner):
        """Presets command lists available presets."""
        result = cli_runner.invoke(main, ["presets"])
        assert result.exit_code == 0
        # Should list the three bundled presets
        assert "SFDA Safe Harbor" in result.output or "sfda_safe_harbor" in result.output
        assert "Research" in result.output or "research" in result.output
        assert "Full Anonymization" in result.output or "full_anonymization" in result.output

    def test_presets_shows_descriptions(self, cli_runner):
        """Presets command shows preset descriptions."""
        result = cli_runner.invoke(main, ["presets"])
        assert result.exit_code == 0
        # Should include some description text
        assert "privacy" in result.output.lower() or "anonymization" in result.output.lower()

    def test_presets_shows_table(self, cli_runner):
        """Presets command shows formatted table."""
        result = cli_runner.invoke(main, ["presets"])
        assert result.exit_code == 0
        # Table should have column headers
        assert "Name" in result.output or "Preset" in result.output

    def test_presets_shows_usage_hint(self, cli_runner):
        """Presets command shows usage hints."""
        result = cli_runner.invoke(main, ["presets"])
        assert result.exit_code == 0
        # Should show how to use presets
        assert "validate" in result.output.lower() or "anonymize" in result.output.lower()
