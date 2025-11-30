"""Tests for PDF report builder."""

from thakaamed_dicom.reports.pdf_report import PDFReportBuilder


class TestPDFReportBuilder:
    """Tests for PDFReportBuilder."""

    def test_build_creates_file(self, sample_report_data, tmp_report_dir):
        """PDF report file is created."""
        builder = PDFReportBuilder()
        output_path = tmp_report_dir / "test_report.pdf"

        result = builder.build(sample_report_data, output_path)

        assert result.exists()
        assert result == output_path

    def test_build_valid_pdf(self, sample_report_data, tmp_report_dir):
        """Generated file is valid PDF."""
        builder = PDFReportBuilder()
        output_path = tmp_report_dir / "test_report.pdf"

        builder.build(sample_report_data, output_path)

        # Check PDF magic bytes
        with open(output_path, "rb") as f:
            header = f.read(5)

        assert header == b"%PDF-"

    def test_build_creates_parent_dirs(self, sample_report_data, tmp_path):
        """Parent directories are created if missing."""
        builder = PDFReportBuilder()
        output_path = tmp_path / "nested" / "dir" / "report.pdf"

        builder.build(sample_report_data, output_path)

        assert output_path.exists()

    def test_build_file_size_reasonable(self, sample_report_data, tmp_report_dir):
        """PDF file size is reasonable (not empty, not too large)."""
        builder = PDFReportBuilder()
        output_path = tmp_report_dir / "test_report.pdf"

        builder.build(sample_report_data, output_path)

        file_size = output_path.stat().st_size
        # Should be at least a few KB
        assert file_size > 1000
        # Should be less than 10MB (reasonable for a report)
        assert file_size < 10 * 1024 * 1024

    def test_build_handles_empty_file_records(self, sample_report_data, tmp_report_dir):
        """PDF generation handles empty file records."""
        sample_report_data.file_records = []
        builder = PDFReportBuilder()
        output_path = tmp_report_dir / "test_report.pdf"

        # Should not raise
        builder.build(sample_report_data, output_path)

        assert output_path.exists()

    def test_build_handles_many_file_records(self, sample_report_data, tmp_report_dir):
        """PDF generation handles many file records."""
        from thakaamed_dicom.reports.models import FileRecord

        # Add 100 file records
        for i in range(100):
            sample_report_data.file_records.append(
                FileRecord(
                    original_path=f"/input/study/file{i:03d}.dcm",
                    output_path=f"/output/study/file{i:03d}.dcm",
                    success=True,
                    study_uid_original="1.2.3.4.5",
                    study_uid_new="2.25.999",
                    series_uid_original="1.2.3.4.6",
                    series_uid_new="2.25.888",
                    sop_uid_original=f"1.2.3.4.{i}",
                    sop_uid_new=f"2.25.{i}",
                    tags_modified=10,
                    tags_removed=5,
                    private_tags_removed=2,
                    error_message="",
                )
            )

        builder = PDFReportBuilder()
        output_path = tmp_report_dir / "test_report.pdf"

        # Should not raise
        builder.build(sample_report_data, output_path)

        assert output_path.exists()

    def test_styles_created(self):
        """Custom paragraph styles are created."""
        builder = PDFReportBuilder()

        assert "ReportTitle" in builder.styles.byName
        assert "SectionHeader" in builder.styles.byName
        assert "Subtitle" in builder.styles.byName
        assert "TableCell" in builder.styles.byName

    def test_build_with_errors(self, sample_report_data, tmp_report_dir):
        """PDF generation handles reports with errors."""
        sample_report_data.files_failed = 5
        sample_report_data.errors = ["Error 1", "Error 2", "Error 3"]

        builder = PDFReportBuilder()
        output_path = tmp_report_dir / "test_report.pdf"

        # Should not raise
        builder.build(sample_report_data, output_path)

        assert output_path.exists()
