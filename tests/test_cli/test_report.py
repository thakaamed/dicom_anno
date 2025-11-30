"""Tests for report command."""

from datetime import datetime

from click.testing import CliRunner

from dicom_anonymizer.cli.main import main
from dicom_anonymizer.reports.json_report import JSONReportBuilder
from dicom_anonymizer.reports.models import FileRecord, ReportData


class TestReportCommand:
    """Tests for report CLI command."""

    def _create_sample_json_report(self, path):
        """Create sample JSON report for testing."""
        report_data = ReportData(
            report_id="test-123",
            generated_at=datetime.now(),
            generator_version="1.0.0",
            preset_name="Test Preset",
            preset_description="Test description",
            compliance_standards=["HIPAA"],
            date_handling="remove",
            input_path="/input",
            output_path="/output",
            files_processed=2,
            files_successful=2,
            files_failed=0,
            studies_processed=1,
            series_processed=1,
            total_tags_modified=20,
            total_tags_removed=10,
            total_uids_remapped=4,
            total_private_tags_removed=5,
            processing_time_seconds=1.5,
            file_records=[
                FileRecord(
                    original_path="/input/file1.dcm",
                    output_path="/output/file1.dcm",
                    success=True,
                    study_uid_original="1.2.3",
                    study_uid_new="2.25.999",
                    series_uid_original="1.2.4",
                    series_uid_new="2.25.888",
                    sop_uid_original="1.2.5",
                    sop_uid_new="2.25.777",
                    tags_modified=10,
                    tags_removed=5,
                    private_tags_removed=2,
                    error_message="",
                ),
            ],
            tag_rules_applied=[],
            errors=[],
            uid_mapping={},
        )
        builder = JSONReportBuilder()
        builder.build(report_data, path)

    def test_report_requires_from_json(self):
        """Report requires --from-json option."""
        runner = CliRunner()
        result = runner.invoke(main, ["report"])

        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()

    def test_report_invalid_json_path(self):
        """Report with nonexistent JSON shows error."""
        runner = CliRunner()
        result = runner.invoke(main, ["report", "--from-json", "/nonexistent/path.json"])

        assert result.exit_code != 0

    def test_report_from_json_success(self, tmp_path):
        """Generate report from JSON successfully."""
        # Create sample JSON
        json_path = tmp_path / "test_audit.json"
        self._create_sample_json_report(json_path)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "report",
                "--from-json",
                str(json_path),
                "-o",
                str(output_dir),
                "--format",
                "pdf",
            ],
        )

        assert result.exit_code == 0

    def test_report_generates_pdf(self, tmp_path):
        """Report generates PDF file."""
        json_path = tmp_path / "test_audit.json"
        self._create_sample_json_report(json_path)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        runner = CliRunner()
        runner.invoke(
            main,
            [
                "report",
                "--from-json",
                str(json_path),
                "-o",
                str(output_dir),
                "--format",
                "pdf",
            ],
        )

        pdf_files = list(output_dir.glob("*.pdf"))
        assert len(pdf_files) >= 1

    def test_report_generates_all_formats(self, tmp_path):
        """Report generates all formats when requested."""
        json_path = tmp_path / "test_audit.json"
        self._create_sample_json_report(json_path)

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "report",
                "--from-json",
                str(json_path),
                "-o",
                str(output_dir),
                "--format",
                "all",
            ],
        )

        assert result.exit_code == 0

        pdf_files = list(output_dir.glob("*.pdf"))
        json_files = list(output_dir.glob("*.json"))
        csv_files = list(output_dir.glob("*.csv"))

        assert len(pdf_files) >= 1
        assert len(json_files) >= 1
        assert len(csv_files) >= 1

    def test_report_default_output(self, tmp_path):
        """Report defaults to same directory as input."""
        json_path = tmp_path / "test_audit.json"
        self._create_sample_json_report(json_path)

        runner = CliRunner()
        result = runner.invoke(
            main,
            [
                "report",
                "--from-json",
                str(json_path),
                "--format",
                "csv",
            ],
        )

        assert result.exit_code == 0

        # Should create in same directory as input
        csv_files = list(tmp_path.glob("*.csv"))
        assert len(csv_files) >= 1

    def test_report_format_choices(self, tmp_path):
        """Report format option accepts valid choices."""
        json_path = tmp_path / "test_audit.json"
        self._create_sample_json_report(json_path)

        runner = CliRunner()

        # Test each format
        for fmt in ["pdf", "json", "csv", "all"]:
            output_dir = tmp_path / f"output_{fmt}"
            output_dir.mkdir()

            result = runner.invoke(
                main,
                [
                    "report",
                    "--from-json",
                    str(json_path),
                    "-o",
                    str(output_dir),
                    "--format",
                    fmt,
                ],
            )

            assert result.exit_code == 0, f"Failed for format: {fmt}"
