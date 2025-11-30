"""Tests for JSON report builder."""

import json

from thakaamed_dicom.reports.json_report import JSONReportBuilder


class TestJSONReportBuilder:
    """Tests for JSONReportBuilder."""

    def test_build_creates_file(self, sample_report_data, tmp_report_dir):
        """JSON report file is created."""
        builder = JSONReportBuilder()
        output_path = tmp_report_dir / "test_report.json"

        result = builder.build(sample_report_data, output_path)

        assert result.exists()
        assert result == output_path

    def test_build_valid_json(self, sample_report_data, tmp_report_dir):
        """Generated file is valid JSON."""
        builder = JSONReportBuilder()
        output_path = tmp_report_dir / "test_report.json"

        builder.build(sample_report_data, output_path)

        # Should not raise
        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        assert isinstance(data, dict)

    def test_build_contains_required_fields(self, sample_report_data, tmp_report_dir):
        """JSON contains all required fields."""
        builder = JSONReportBuilder()
        output_path = tmp_report_dir / "test_report.json"

        builder.build(sample_report_data, output_path)

        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        assert "report_id" in data
        assert "generated_at" in data
        assert "anonymization" in data
        assert "summary" in data
        assert "file_records" in data

    def test_build_summary_values(self, sample_report_data, tmp_report_dir):
        """Summary statistics are correct."""
        builder = JSONReportBuilder()
        output_path = tmp_report_dir / "test_report.json"

        builder.build(sample_report_data, output_path)

        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        summary = data["summary"]
        assert summary["files_processed"] == 3
        assert summary["files_successful"] == 2
        assert summary["files_failed"] == 1
        assert summary["total_tags_modified"] == 30

    def test_build_creates_parent_dirs(self, sample_report_data, tmp_path):
        """Parent directories are created if missing."""
        builder = JSONReportBuilder()
        output_path = tmp_path / "nested" / "dir" / "report.json"

        builder.build(sample_report_data, output_path)

        assert output_path.exists()

    def test_build_utf8_encoding(self, sample_report_data, tmp_report_dir):
        """JSON file uses UTF-8 encoding."""
        builder = JSONReportBuilder()
        output_path = tmp_report_dir / "test_report.json"

        builder.build(sample_report_data, output_path)

        # Read raw bytes and verify encoding
        with open(output_path, "rb") as f:
            content = f.read()
            # Should decode as UTF-8 without errors
            content.decode("utf-8")

    def test_build_file_records_structure(self, sample_report_data, tmp_report_dir):
        """File records have correct structure."""
        builder = JSONReportBuilder()
        output_path = tmp_report_dir / "test_report.json"

        builder.build(sample_report_data, output_path)

        with open(output_path, encoding="utf-8") as f:
            data = json.load(f)

        records = data["file_records"]
        assert len(records) == 3

        first_record = records[0]
        assert "original_path" in first_record
        assert "success" in first_record
        assert "study_uid" in first_record
        assert "original" in first_record["study_uid"]
        assert "new" in first_record["study_uid"]
