# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Report data models."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReportFormat(str, Enum):
    """Supported report output formats."""

    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    ALL = "all"


@dataclass
class FileRecord:
    """Record of single file processing."""

    original_path: str
    output_path: str
    success: bool
    study_uid_original: str
    study_uid_new: str
    series_uid_original: str
    series_uid_new: str
    sop_uid_original: str
    sop_uid_new: str
    tags_modified: int
    tags_removed: int
    private_tags_removed: int
    error_message: str = ""


@dataclass
class ReportData:
    """Complete report data structure."""

    # Metadata
    report_id: str
    generated_at: datetime
    generator_version: str
    report_hash: str = ""

    # Anonymization context
    preset_name: str = ""
    preset_description: str = ""
    compliance_standards: list[str] = field(default_factory=list)
    date_handling: str = ""
    input_path: str = ""
    output_path: str = ""

    # Summary statistics
    files_processed: int = 0
    files_successful: int = 0
    files_failed: int = 0
    studies_processed: int = 0
    series_processed: int = 0
    total_tags_modified: int = 0
    total_tags_removed: int = 0
    total_uids_remapped: int = 0
    total_private_tags_removed: int = 0
    processing_time_seconds: float = 0.0

    # Detailed records
    file_records: list[FileRecord] = field(default_factory=list)
    tag_rules_applied: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    # UID mapping (for audit)
    uid_mapping: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "generator_version": self.generator_version,
            "report_hash": self.report_hash,
            "anonymization": {
                "preset_name": self.preset_name,
                "preset_description": self.preset_description,
                "compliance_standards": self.compliance_standards,
                "date_handling": self.date_handling,
                "input_path": self.input_path,
                "output_path": self.output_path,
            },
            "summary": {
                "files_processed": self.files_processed,
                "files_successful": self.files_successful,
                "files_failed": self.files_failed,
                "studies_processed": self.studies_processed,
                "series_processed": self.series_processed,
                "total_tags_modified": self.total_tags_modified,
                "total_tags_removed": self.total_tags_removed,
                "total_uids_remapped": self.total_uids_remapped,
                "total_private_tags_removed": self.total_private_tags_removed,
                "processing_time_seconds": self.processing_time_seconds,
            },
            "file_records": [self._file_record_to_dict(r) for r in self.file_records],
            "tag_rules_applied": self.tag_rules_applied,
            "errors": self.errors,
            "uid_mapping": self.uid_mapping,
        }

    @staticmethod
    def _file_record_to_dict(record: FileRecord) -> dict:
        return {
            "original_path": record.original_path,
            "output_path": record.output_path,
            "success": record.success,
            "study_uid": {
                "original": record.study_uid_original,
                "new": record.study_uid_new,
            },
            "series_uid": {
                "original": record.series_uid_original,
                "new": record.series_uid_new,
            },
            "sop_uid": {
                "original": record.sop_uid_original,
                "new": record.sop_uid_new,
            },
            "tags_modified": record.tags_modified,
            "tags_removed": record.tags_removed,
            "private_tags_removed": record.private_tags_removed,
            "error_message": record.error_message,
        }
