"""Tests for CSV report builder."""

import csv

from thakaamed_dicom.reports.csv_report import CSVReportBuilder


class TestCSVReportBuilder:
    """Tests for CSVReportBuilder."""

    def test_build_creates_file(self, sample_report_data, tmp_report_dir):
        """CSV report file is created."""
        builder = CSVReportBuilder()
        output_path = tmp_report_dir / "test_report.csv"

        result = builder.build(sample_report_data, output_path)

        assert result.exists()
        assert result == output_path

    def test_build_valid_csv(self, sample_report_data, tmp_report_dir):
        """Generated file is valid CSV."""
        builder = CSVReportBuilder()
        output_path = tmp_report_dir / "test_report.csv"

        builder.build(sample_report_data, output_path)

        # Should parse without errors
        with open(output_path, encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            rows = list(reader)

        assert len(rows) > 0

    def test_build_contains_header(self, sample_report_data, tmp_report_dir):
        """CSV contains report header."""
        builder = CSVReportBuilder()
        output_path = tmp_report_dir / "test_report.csv"

        builder.build(sample_report_data, output_path)

        with open(output_path, encoding="utf-8-sig") as f:
            content = f.read()

        assert "DICOM ANONYMIZATION REPORT" in content
        assert "SUMMARY STATISTICS" in content
        assert "FILE DETAILS" in content

    def test_build_summary_statistics(self, sample_report_data, tmp_report_dir):
        """CSV contains summary statistics."""
        builder = CSVReportBuilder()
        output_path = tmp_report_dir / "test_report.csv"

        builder.build(sample_report_data, output_path)

        with open(output_path, encoding="utf-8-sig") as f:
            content = f.read()

        assert "Files Processed" in content
        assert "3" in content  # files_processed value
        assert "Tags Modified" in content
        assert "30" in content  # total_tags_modified value

    def test_build_file_records(self, sample_report_data, tmp_report_dir):
        """CSV contains file records."""
        builder = CSVReportBuilder()
        output_path = tmp_report_dir / "test_report.csv"

        builder.build(sample_report_data, output_path)

        with open(output_path, encoding="utf-8-sig") as f:
            content = f.read()

        # Should have file paths
        assert "/input/study1/CT001.dcm" in content
        assert "/input/study1/CT002.dcm" in content
        assert "/input/study1/CT003.dcm" in content

    def test_build_creates_parent_dirs(self, sample_report_data, tmp_path):
        """Parent directories are created if missing."""
        builder = CSVReportBuilder()
        output_path = tmp_path / "nested" / "dir" / "report.csv"

        builder.build(sample_report_data, output_path)

        assert output_path.exists()

    def test_build_excel_compatible_encoding(self, sample_report_data, tmp_report_dir):
        """CSV uses BOM for Excel compatibility."""
        builder = CSVReportBuilder()
        output_path = tmp_report_dir / "test_report.csv"

        builder.build(sample_report_data, output_path)

        # Check for UTF-8 BOM
        with open(output_path, "rb") as f:
            first_bytes = f.read(3)

        # UTF-8 BOM is EF BB BF
        assert first_bytes == b"\xef\xbb\xbf"

    def test_build_status_column(self, sample_report_data, tmp_report_dir):
        """CSV shows success/failed status correctly."""
        builder = CSVReportBuilder()
        output_path = tmp_report_dir / "test_report.csv"

        builder.build(sample_report_data, output_path)

        with open(output_path, encoding="utf-8-sig") as f:
            content = f.read()

        assert "Success" in content
        assert "Failed" in content
