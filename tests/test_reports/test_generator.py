"""Tests for ReportGenerator."""

import json

from thakaamed_dicom.config.models import ActionCode, DateHandling, PresetConfig, TagRule
from thakaamed_dicom.engine.statistics import FileStatistics, ProcessingStatistics
from thakaamed_dicom.reports.generator import ReportGenerator
from thakaamed_dicom.reports.models import ReportFormat


class TestReportGenerator:
    """Tests for ReportGenerator."""

    def test_generate_all_formats(self, tmp_report_dir):
        """Generates all report formats."""
        # Setup
        stats = ProcessingStatistics()
        stats.files_processed = 2
        stats.files_successful = 2
        stats.files_failed = 0
        stats.finalize()

        preset = PresetConfig(
            name="Test Preset",
            description="Test description",
            version="1.0.0",
            compliance=["HIPAA"],
            date_handling=DateHandling.REMOVE,
            remove_private_tags=True,
            tag_rules=[],
        )

        generator = ReportGenerator()
        results = generator.generate(
            stats=stats,
            preset=preset,
            input_path="/input",
            output_path="/output",
            uid_mapping={},
            report_dir=tmp_report_dir,
            formats=[ReportFormat.ALL],
        )

        # Should have 3 files (JSON, CSV, PDF)
        assert len(results) == 3

        extensions = {p.suffix for p in results}
        assert ".json" in extensions
        assert ".csv" in extensions
        assert ".pdf" in extensions

    def test_generate_single_format(self, tmp_report_dir):
        """Generates single format when specified."""
        stats = ProcessingStatistics()
        stats.files_processed = 1
        stats.files_successful = 1
        stats.finalize()

        preset = PresetConfig(
            name="Test",
            description="Test",
            version="1.0.0",
            compliance=[],
            date_handling=DateHandling.REMOVE,
            remove_private_tags=False,
            tag_rules=[],
        )

        generator = ReportGenerator()
        results = generator.generate(
            stats=stats,
            preset=preset,
            input_path="/input",
            output_path="/output",
            uid_mapping={},
            report_dir=tmp_report_dir,
            formats=[ReportFormat.JSON],
        )

        assert len(results) == 1
        assert results[0].suffix == ".json"

    def test_generate_pdf_only(self, tmp_report_dir):
        """Generates PDF only when specified."""
        stats = ProcessingStatistics()
        stats.files_processed = 1
        stats.files_successful = 1
        stats.finalize()

        preset = PresetConfig(
            name="Test",
            description="Test",
            version="1.0.0",
            compliance=[],
            date_handling=DateHandling.REMOVE,
            remove_private_tags=False,
            tag_rules=[],
        )

        generator = ReportGenerator()
        results = generator.generate(
            stats=stats,
            preset=preset,
            input_path="/input",
            output_path="/output",
            uid_mapping={},
            report_dir=tmp_report_dir,
            formats=[ReportFormat.PDF],
        )

        assert len(results) == 1
        assert results[0].suffix == ".pdf"

    def test_generate_includes_tag_rules(self, tmp_report_dir):
        """Generated report includes tag rules from preset."""
        stats = ProcessingStatistics()
        stats.files_processed = 1
        stats.files_successful = 1
        stats.finalize()

        preset = PresetConfig(
            name="Test",
            description="Test",
            version="1.0.0",
            compliance=["HIPAA"],
            date_handling=DateHandling.REMOVE,
            remove_private_tags=True,
            tag_rules=[
                TagRule(tag="(0010,0010)", action=ActionCode.Z, description="Patient Name"),
                TagRule(tag="(0010,0020)", action=ActionCode.Z, description="Patient ID"),
            ],
        )

        generator = ReportGenerator()
        results = generator.generate(
            stats=stats,
            preset=preset,
            input_path="/input",
            output_path="/output",
            uid_mapping={},
            report_dir=tmp_report_dir,
            formats=[ReportFormat.JSON],
        )

        # Read JSON and verify
        with open(results[0], encoding="utf-8") as f:
            data = json.load(f)

        assert len(data["tag_rules_applied"]) == 2
        assert data["tag_rules_applied"][0]["tag"] == "(0010,0010)"

    def test_generate_includes_file_stats(self, tmp_report_dir):
        """Generated report includes file statistics."""
        stats = ProcessingStatistics()

        # Add file stats
        file_stat = FileStatistics(
            file_path="/input/test.dcm",
            success=True,
            tags_modified=10,
            tags_removed=5,
            uids_remapped=3,
            private_tags_removed=2,
            processing_time_ms=50.5,
        )
        stats.add_file_result(file_stat)
        stats.finalize()

        preset = PresetConfig(
            name="Test",
            description="Test",
            version="1.0.0",
            compliance=[],
            date_handling=DateHandling.REMOVE,
            remove_private_tags=False,
            tag_rules=[],
        )

        generator = ReportGenerator()
        results = generator.generate(
            stats=stats,
            preset=preset,
            input_path="/input",
            output_path="/output",
            uid_mapping={},
            report_dir=tmp_report_dir,
            formats=[ReportFormat.JSON],
        )

        with open(results[0], encoding="utf-8") as f:
            data = json.load(f)

        assert data["summary"]["files_processed"] == 1
        assert data["summary"]["total_tags_modified"] == 10

    def test_report_hash_calculated(self, tmp_report_dir):
        """Report hash is calculated and included."""
        stats = ProcessingStatistics()
        stats.finalize()

        preset = PresetConfig(
            name="Test",
            description="Test",
            version="1.0.0",
            compliance=[],
            date_handling=DateHandling.REMOVE,
            remove_private_tags=False,
            tag_rules=[],
        )

        generator = ReportGenerator()
        results = generator.generate(
            stats=stats,
            preset=preset,
            input_path="/input",
            output_path="/output",
            uid_mapping={},
            report_dir=tmp_report_dir,
            formats=[ReportFormat.JSON],
        )

        with open(results[0], encoding="utf-8") as f:
            data = json.load(f)

        assert "report_hash" in data
        assert len(data["report_hash"]) == 64  # SHA-256 hex

    def test_from_json_loads_data(self, sample_report_data, tmp_report_dir):
        """from_json correctly loads report data."""
        # First, generate a JSON report
        from thakaamed_dicom.reports.json_report import JSONReportBuilder

        builder = JSONReportBuilder()
        json_path = tmp_report_dir / "test.json"
        builder.build(sample_report_data, json_path)

        # Now load it back
        loaded = ReportGenerator.from_json(json_path)

        assert loaded.report_id == sample_report_data.report_id
        assert loaded.preset_name == sample_report_data.preset_name
        assert loaded.files_processed == sample_report_data.files_processed
        assert len(loaded.file_records) == len(sample_report_data.file_records)

    def test_generate_from_data(self, sample_report_data, tmp_report_dir):
        """generate_from_data creates reports from ReportData."""
        generator = ReportGenerator()
        results = generator.generate_from_data(
            report_data=sample_report_data,
            report_dir=tmp_report_dir,
            formats=[ReportFormat.ALL],
        )

        assert len(results) == 3

        extensions = {p.suffix for p in results}
        assert ".json" in extensions
        assert ".csv" in extensions
        assert ".pdf" in extensions

    def test_generate_creates_report_dir(self, tmp_path):
        """Report directory is created if missing."""
        stats = ProcessingStatistics()
        stats.finalize()

        preset = PresetConfig(
            name="Test",
            description="Test",
            version="1.0.0",
            compliance=[],
            date_handling=DateHandling.REMOVE,
            remove_private_tags=False,
            tag_rules=[],
        )

        report_dir = tmp_path / "new_reports"
        assert not report_dir.exists()

        generator = ReportGenerator()
        generator.generate(
            stats=stats,
            preset=preset,
            input_path="/input",
            output_path="/output",
            uid_mapping={},
            report_dir=report_dir,
            formats=[ReportFormat.JSON],
        )

        assert report_dir.exists()
