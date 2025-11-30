"""Test fixtures for report tests."""

from datetime import datetime

import pytest

from thakaamed_dicom.reports.models import FileRecord, ReportData


@pytest.fixture
def sample_file_records():
    """Sample file records for testing."""
    return [
        FileRecord(
            original_path="/input/study1/CT001.dcm",
            output_path="/output/study1/CT001.dcm",
            success=True,
            study_uid_original="1.2.3.4.5.6.7.8.9.0",
            study_uid_new="2.25.123456789012345678901234567890",
            series_uid_original="1.2.3.4.5.6.7.8.9.1",
            series_uid_new="2.25.234567890123456789012345678901",
            sop_uid_original="1.2.3.4.5.6.7.8.9.2",
            sop_uid_new="2.25.345678901234567890123456789012",
            tags_modified=15,
            tags_removed=8,
            private_tags_removed=3,
            error_message="",
        ),
        FileRecord(
            original_path="/input/study1/CT002.dcm",
            output_path="/output/study1/CT002.dcm",
            success=True,
            study_uid_original="1.2.3.4.5.6.7.8.9.0",
            study_uid_new="2.25.123456789012345678901234567890",
            series_uid_original="1.2.3.4.5.6.7.8.9.1",
            series_uid_new="2.25.234567890123456789012345678901",
            sop_uid_original="1.2.3.4.5.6.7.8.9.3",
            sop_uid_new="2.25.456789012345678901234567890123",
            tags_modified=15,
            tags_removed=8,
            private_tags_removed=3,
            error_message="",
        ),
        FileRecord(
            original_path="/input/study1/CT003.dcm",
            output_path="/output/study1/CT003.dcm",
            success=False,
            study_uid_original="",
            study_uid_new="",
            series_uid_original="",
            series_uid_new="",
            sop_uid_original="",
            sop_uid_new="",
            tags_modified=0,
            tags_removed=0,
            private_tags_removed=0,
            error_message="Invalid DICOM format",
        ),
    ]


@pytest.fixture
def sample_report_data(sample_file_records):
    """Sample report data for testing."""
    return ReportData(
        report_id="test-report-123",
        generated_at=datetime(2024, 1, 15, 14, 30, 22),
        generator_version="1.0.0",
        report_hash="",
        preset_name="SFDA Safe Harbor",
        preset_description="Safe harbor de-identification for Saudi FDA compliance",
        compliance_standards=["DICOM PS3.15", "HIPAA Safe Harbor", "Saudi PDPL"],
        date_handling="remove",
        input_path="/input/study1",
        output_path="/output/study1",
        files_processed=3,
        files_successful=2,
        files_failed=1,
        studies_processed=1,
        series_processed=1,
        total_tags_modified=30,
        total_tags_removed=16,
        total_uids_remapped=6,
        total_private_tags_removed=6,
        processing_time_seconds=1.234,
        file_records=sample_file_records,
        tag_rules_applied=[
            {"tag": "(0010,0010)", "action": "Z", "description": "Patient's Name"},
            {"tag": "(0010,0020)", "action": "Z", "description": "Patient ID"},
            {"tag": "(0010,0030)", "action": "X", "description": "Patient's Birth Date"},
        ],
        errors=["/input/study1/CT003.dcm: Invalid DICOM format"],
        uid_mapping={
            "1.2.3.4.5.6.7.8.9.0": "2.25.123456789012345678901234567890",
            "1.2.3.4.5.6.7.8.9.1": "2.25.234567890123456789012345678901",
        },
    )


@pytest.fixture
def tmp_report_dir(tmp_path):
    """Temporary directory for report output."""
    report_dir = tmp_path / "reports"
    report_dir.mkdir()
    return report_dir
