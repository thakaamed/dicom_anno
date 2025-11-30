"""Tests for anonymize command."""

from click.testing import CliRunner

from dicom_anonymizer.cli.main import main
from tests.fixtures.dicom_factory import DicomFactory


class TestAnonymizeCommand:
    """Tests for anonymize CLI command."""

    def test_anonymize_requires_input(self):
        """Anonymize requires --input option."""
        runner = CliRunner()
        result = runner.invoke(main, ["anonymize", "-o", "/tmp/output", "-p", "sfda_safe_harbor"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_anonymize_requires_output(self, tmp_path):
        """Anonymize requires --output option."""
        # Create input file
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        ds = DicomFactory.create_minimal()
        (input_dir / "test.dcm").write_bytes(b"")  # Dummy file
        ds.save_as(str(input_dir / "test.dcm"))

        runner = CliRunner()
        result = runner.invoke(
            main, ["anonymize", "-i", str(input_dir / "test.dcm"), "-p", "sfda_safe_harbor"]
        )

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_anonymize_requires_preset(self, tmp_path):
        """Anonymize requires --preset option."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        ds = DicomFactory.create_minimal()
        ds.save_as(str(input_dir / "test.dcm"))

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_dir / "test.dcm"),
                "-o",
                str(tmp_path / "output.dcm"),
            ],
        )

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_anonymize_invalid_preset(self, tmp_path):
        """Anonymize with invalid preset shows error."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        ds = DicomFactory.create_minimal()
        ds.save_as(str(input_dir / "test.dcm"))

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_dir / "test.dcm"),
                "-o",
                str(tmp_path / "output.dcm"),
                "-p",
                "nonexistent_preset",
            ],
        )

        assert result.exit_code != 0

    def test_anonymize_single_file_success(self, tmp_path):
        """Anonymize single file successfully."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        ds = DicomFactory.create_minimal()
        input_file = input_dir / "test.dcm"
        ds.save_as(str(input_file))

        output_file = tmp_path / "output.dcm"

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_file),
                "-o",
                str(output_file),
                "-p",
                "sfda_safe_harbor",
            ],
        )

        assert result.exit_code == 0
        assert output_file.exists()

    def test_anonymize_directory_success(self, tmp_path):
        """Anonymize directory successfully."""
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        DicomFactory.create_study_series(
            input_dir,
            num_series=1,
            files_per_series=2,
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_dir),
                "-o",
                str(output_dir),
                "-p",
                "sfda_safe_harbor",
                "--no-parallel",
                "--no-reports",
            ],
        )

        assert result.exit_code == 0

    def test_anonymize_dry_run(self, tmp_path):
        """Dry run doesn't write output."""
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        ds = DicomFactory.create_minimal()
        input_file = input_dir / "test.dcm"
        ds.save_as(str(input_file))

        output_file = tmp_path / "output.dcm"

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_file),
                "-o",
                str(output_file),
                "-p",
                "sfda_safe_harbor",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert not output_file.exists()
        assert "DRY RUN" in result.output

    def test_anonymize_report_format_choice(self, tmp_path):
        """Report format option accepts valid choices."""
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        DicomFactory.create_study_series(
            input_dir,
            num_series=1,
            files_per_series=1,
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_dir),
                "-o",
                str(output_dir),
                "-p",
                "sfda_safe_harbor",
                "--report-format",
                "json",
                "--no-parallel",
            ],
        )

        assert result.exit_code == 0

    def test_anonymize_shows_progress(self, tmp_path):
        """Anonymize shows progress output."""
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        DicomFactory.create_study_series(
            input_dir,
            num_series=1,
            files_per_series=2,
        )

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_dir),
                "-o",
                str(output_dir),
                "-p",
                "sfda_safe_harbor",
                "--no-parallel",
                "--no-reports",
            ],
        )

        assert result.exit_code == 0
        # Should show some progress/summary info
        assert "Processing" in result.output or "Files" in result.output

    def test_anonymize_nonexistent_input(self, tmp_path):
        """Anonymize with nonexistent input shows error."""
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                "/nonexistent/path",
                "-o",
                str(tmp_path / "output"),
                "-p",
                "sfda_safe_harbor",
            ],
        )

        assert result.exit_code != 0
