"""Tests for version command."""

from dicom_anonymizer import __version__
from dicom_anonymizer.cli.main import main


class TestVersionCommand:
    """Tests for the version command."""

    def test_version_displays_version_number(self, cli_runner):
        """Version command shows version number."""
        result = cli_runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_version_shows_branding(self, cli_runner):
        """Version command shows THAKAAMED branding."""
        result = cli_runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "THAKAAMED" in result.output
        assert "Vision 2030" in result.output

    def test_version_shows_python_version(self, cli_runner):
        """Version command shows Python version."""
        result = cli_runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "Python" in result.output

    def test_version_shows_dependencies(self, cli_runner):
        """Version command shows dependency versions."""
        result = cli_runner.invoke(main, ["version"])
        assert result.exit_code == 0
        assert "pydicom" in result.output
        assert "Rich" in result.output
        assert "Pydantic" in result.output
