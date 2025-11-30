"""End-to-end integration tests."""

import json

from click.testing import CliRunner
from pydicom import dcmread

from tests.fixtures.dicom_factory import DicomFactory
from thakaamed_dicom.cli.main import main


class TestFullWorkflow:
    """Tests for complete anonymization workflow."""

    def test_single_file_workflow(self, tmp_path):
        """Process single file end-to-end."""
        # Setup
        input_dir = tmp_path / "input"
        input_dir.mkdir()
        output_dir = tmp_path / "output"

        # Create test file
        ds = DicomFactory.create_minimal()
        input_file = input_dir / "test.dcm"
        ds.save_as(str(input_file))

        # Run CLI
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_file),
                "-o",
                str(output_dir / "output.dcm"),
                "-p",
                "sfda_safe_harbor",
            ],
        )

        assert result.exit_code == 0
        assert (output_dir / "output.dcm").exists()

    def test_directory_workflow(self, tmp_path):
        """Process directory end-to-end."""
        # Setup
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        # Create test files
        DicomFactory.create_study_series(
            input_dir,
            num_series=2,
            files_per_series=2,
        )

        # Run CLI
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
            ],
        )

        assert result.exit_code == 0

        # Verify output files exist
        output_files = list(output_dir.rglob("*.dcm"))
        assert len(output_files) == 4  # 2 series x 2 files

    def test_workflow_with_reports(self, tmp_path):
        """Process with report generation."""
        # Setup
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        # Create test files
        DicomFactory.create_study_series(
            input_dir,
            num_series=1,
            files_per_series=2,
        )

        # Run CLI with reports
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
                "all",
                "--no-parallel",
            ],
        )

        assert result.exit_code == 0

        # Verify reports exist
        report_dir = output_dir / "reports"
        assert report_dir.exists()

        json_files = list(report_dir.glob("*.json"))
        pdf_files = list(report_dir.glob("*.pdf"))
        csv_files = list(report_dir.glob("*.csv"))

        assert len(json_files) == 1
        assert len(pdf_files) == 1
        assert len(csv_files) == 1

    def test_workflow_no_reports(self, tmp_path):
        """Process with reports disabled."""
        # Setup
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        # Create test files
        DicomFactory.create_study_series(
            input_dir,
            num_series=1,
            files_per_series=2,
        )

        # Run CLI with no reports
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
                "--no-reports",
                "--no-parallel",
            ],
        )

        assert result.exit_code == 0

        # Reports directory should not exist or be empty
        report_dir = output_dir / "reports"
        if report_dir.exists():
            assert len(list(report_dir.iterdir())) == 0

    def test_dry_run_workflow(self, tmp_path):
        """Dry run doesn't create output."""
        # Setup
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        # Create test files
        ds = DicomFactory.create_minimal()
        input_file = input_dir / "test.dcm"
        input_dir.mkdir()
        ds.save_as(str(input_file))

        # Run CLI with dry-run
        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "anonymize",
                "-i",
                str(input_file),
                "-o",
                str(output_dir / "output.dcm"),
                "-p",
                "sfda_safe_harbor",
                "--dry-run",
            ],
        )

        assert result.exit_code == 0
        assert not output_dir.exists() or not (output_dir / "output.dcm").exists()

    def test_uid_consistency_across_study(self, tmp_path):
        """UIDs are consistent across files in same study."""
        # Setup
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        # Create study with multiple files
        DicomFactory.create_study_series(
            input_dir,
            num_series=2,
            files_per_series=2,
        )

        # Run CLI
        runner = CliRunner()
        runner.invoke(
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

        # All files should have same study UID
        study_uids = set()
        for dcm_file in output_dir.rglob("*.dcm"):
            ds = dcmread(str(dcm_file), force=True)
            study_uids.add(ds.StudyInstanceUID)

        assert len(study_uids) == 1
        assert list(study_uids)[0].startswith("2.25.")

    def test_json_report_valid_content(self, tmp_path):
        """JSON report contains valid audit data."""
        # Setup
        input_dir = tmp_path / "input"
        output_dir = tmp_path / "output"

        # Create test files
        DicomFactory.create_study_series(
            input_dir,
            num_series=1,
            files_per_series=2,
        )

        # Run CLI
        runner = CliRunner()
        runner.invoke(
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

        # Read and validate JSON
        json_files = list((output_dir / "reports").glob("*.json"))
        assert len(json_files) == 1

        with open(json_files[0]) as f:
            data = json.load(f)

        assert data["summary"]["files_processed"] == 2
        assert data["summary"]["files_successful"] == 2
        assert "SFDA Safe Harbor" in data["anonymization"]["preset_name"]
