"""Tests for main CLI group."""

from dicom_anonymizer.cli.main import main


class TestMainCLI:
    """Tests for the main CLI command group."""

    def test_help_shows_commands(self, cli_runner):
        """--help shows available commands."""
        result = cli_runner.invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "DICOM Anonymizer" in result.output
        assert "anonymize" in result.output
        assert "validate" in result.output
        assert "presets" in result.output
        assert "version" in result.output

    def test_no_command_shows_banner(self, cli_runner):
        """Running without command shows banner and help."""
        result = cli_runner.invoke(main, [])
        assert result.exit_code == 0
        # Check for banner elements
        assert "THAKAA" in result.output or "DICOM Anonymizer" in result.output
        # Check for help text
        assert "Usage:" in result.output

    def test_verbose_flag_accepted(self, cli_runner):
        """--verbose flag is accepted."""
        result = cli_runner.invoke(main, ["--verbose", "--help"])
        assert result.exit_code == 0

    def test_unknown_command_fails(self, cli_runner):
        """Unknown command produces error."""
        result = cli_runner.invoke(main, ["unknown_command"])
        assert result.exit_code != 0
