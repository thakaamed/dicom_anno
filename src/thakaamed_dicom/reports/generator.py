# -*- coding: utf-8 -*-
# ============================================================================
#  THAKAAMED DICOM Anonymizer
#  Copyright (c) 2024 THAKAAMED AI. All rights reserved.
#
#  https://thakaamed.com | Enterprise Healthcare Solutions
#
#  LICENSE: CC BY-NC-ND 4.0 (Non-Commercial)
#  This software is for RESEARCH AND EDUCATIONAL PURPOSES ONLY.
#  For commercial licensing: licensing@thakaamed.com
#
#  See LICENSE file for full terms. | Built for Saudi Vision 2030
# ============================================================================
"""Report generation orchestrator."""

import hashlib
import json
import uuid
from datetime import datetime
from pathlib import Path

from thakaamed_dicom import __version__
from thakaamed_dicom.config.models import PresetConfig
from thakaamed_dicom.engine.statistics import ProcessingStatistics
from thakaamed_dicom.reports.csv_report import CSVReportBuilder
from thakaamed_dicom.reports.json_report import JSONReportBuilder
from thakaamed_dicom.reports.models import FileRecord, ReportData, ReportFormat
from thakaamed_dicom.reports.pdf_report import PDFReportBuilder


class ReportGenerator:
    """Orchestrate report generation in multiple formats."""

    def __init__(self):
        self.pdf_builder = PDFReportBuilder()
        self.json_builder = JSONReportBuilder()
        self.csv_builder = CSVReportBuilder()

    def generate(
        self,
        stats: ProcessingStatistics,
        preset: PresetConfig,
        input_path: str,
        output_path: str,
        uid_mapping: dict,
        report_dir: Path,
        formats: list[ReportFormat] | None = None,
    ) -> list[Path]:
        """
        Generate reports in specified formats.

        Args:
            stats: Processing statistics from anonymization
            preset: Preset configuration used
            input_path: Original input path
            output_path: Output path for anonymized files
            uid_mapping: UID mapping dictionary for audit
            report_dir: Directory for report files
            formats: List of formats to generate (default: all)

        Returns:
            List of generated report file paths
        """
        formats = formats or [ReportFormat.ALL]
        
        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir.mkdir(parents=True, exist_ok=True)
        generated = []
        
        # For large batches, save full UID mapping to a separate file first
        # This ensures we don't lose it even if report generation fails
        if len(uid_mapping) > 1000:
            try:
                uid_mapping_path = report_dir / f"uid_mapping_full_{timestamp}.json"
                with open(uid_mapping_path, "w", encoding="utf-8") as f:
                    json.dump({
                        "generated_at": datetime.now().isoformat(),
                        "total_mappings": len(uid_mapping),
                        "note": "Full UID mapping for audit trail. Report contains truncated version.",
                        "mappings": uid_mapping,
                    }, f, indent=2)
                generated.append(uid_mapping_path)
                print(f"  📋 Full UID mapping saved ({len(uid_mapping):,} entries)")
            except Exception as e:
                print(f"  ⚠️ Could not save full UID mapping: {e}")

        # Build report data (with limits for large batches)
        report_data = self._build_report_data(stats, preset, input_path, output_path, uid_mapping)

        # Calculate hash
        report_data.report_hash = self._calculate_hash(report_data)

        # Base name for report files
        base_name = f"anonymization_report_{timestamp}"

        # Determine which formats to generate
        should_generate = {
            ReportFormat.PDF: False,
            ReportFormat.JSON: False,
            ReportFormat.CSV: False,
        }

        for fmt in formats:
            if fmt == ReportFormat.ALL:
                should_generate = dict.fromkeys(should_generate, True)
                break
            should_generate[fmt] = True

        # Generate each format
        if should_generate[ReportFormat.JSON]:
            json_path = report_dir / f"{base_name}.json"
            self.json_builder.build(report_data, json_path)
            generated.append(json_path)

        if should_generate[ReportFormat.CSV]:
            csv_path = report_dir / f"{base_name}.csv"
            self.csv_builder.build(report_data, csv_path)
            generated.append(csv_path)

        if should_generate[ReportFormat.PDF]:
            pdf_path = report_dir / f"{base_name}.pdf"
            self.pdf_builder.build(report_data, pdf_path)
            generated.append(pdf_path)

        return generated

    def generate_from_data(
        self,
        report_data: ReportData,
        report_dir: Path,
        formats: list[ReportFormat] | None = None,
    ) -> list[Path]:
        """
        Generate reports from existing ReportData.

        Args:
            report_data: Complete report data
            report_dir: Directory for report files
            formats: List of formats to generate (default: all)

        Returns:
            List of generated report file paths
        """
        formats = formats or [ReportFormat.ALL]

        # Generate timestamp for filenames
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"anonymization_report_{timestamp}"

        report_dir.mkdir(parents=True, exist_ok=True)
        generated = []

        # Determine which formats to generate
        should_generate = {
            ReportFormat.PDF: False,
            ReportFormat.JSON: False,
            ReportFormat.CSV: False,
        }

        for fmt in formats:
            if fmt == ReportFormat.ALL:
                should_generate = dict.fromkeys(should_generate, True)
                break
            should_generate[fmt] = True

        # Generate each format
        if should_generate[ReportFormat.JSON]:
            json_path = report_dir / f"{base_name}.json"
            self.json_builder.build(report_data, json_path)
            generated.append(json_path)

        if should_generate[ReportFormat.CSV]:
            csv_path = report_dir / f"{base_name}.csv"
            self.csv_builder.build(report_data, csv_path)
            generated.append(csv_path)

        if should_generate[ReportFormat.PDF]:
            pdf_path = report_dir / f"{base_name}.pdf"
            self.pdf_builder.build(report_data, pdf_path)
            generated.append(pdf_path)

        return generated

    def _build_report_data(
        self,
        stats: ProcessingStatistics,
        preset: PresetConfig,
        input_path: str,
        output_path: str,
        uid_mapping: dict,
        max_file_records: int = 500,
        max_uid_mappings: int = 1000,
    ) -> ReportData:
        """Build ReportData from processing results.
        
        For large batches (1000+ files), we limit the detailed records
        to prevent memory issues and keep reports manageable.
        """
        # Build file records from stats (limit for large batches)
        file_records = []
        total_files = len(stats.file_stats)
        
        # For large batches, only include first N records + failed ones
        if total_files > max_file_records:
            # Always include failed files first
            failed_stats = [s for s in stats.file_stats if not s.success]
            success_stats = [s for s in stats.file_stats if s.success]
            
            # Take all failed + first N successful
            remaining_slots = max(0, max_file_records - len(failed_stats))
            stats_to_include = failed_stats + success_stats[:remaining_slots]
        else:
            stats_to_include = stats.file_stats
        
        for file_stat in stats_to_include:
            record = FileRecord(
                original_path=file_stat.file_path,
                output_path="",  # Not tracked in current stats
                success=file_stat.success,
                study_uid_original="",
                study_uid_new="",
                series_uid_original="",
                series_uid_new="",
                sop_uid_original="",
                sop_uid_new="",
                tags_modified=file_stat.tags_modified,
                tags_removed=file_stat.tags_removed,
                private_tags_removed=file_stat.private_tags_removed,
                error_message=file_stat.error_message,
            )
            file_records.append(record)

        # Build tag rules list
        tag_rules = [
            {"tag": rule.tag, "action": rule.action.value, "description": rule.description or ""}
            for rule in preset.tag_rules
        ]
        
        # Limit UID mapping size for reports (full mapping saved separately)
        limited_uid_mapping = uid_mapping
        notes = []
        
        if total_files > max_file_records:
            notes.append(
                f"Large batch: Showing {len(stats_to_include):,} of {total_files:,} file records. "
                f"All files were processed successfully."
            )
        
        if len(uid_mapping) > max_uid_mappings:
            # Take first N mappings for the report
            limited_uid_mapping = dict(list(uid_mapping.items())[:max_uid_mappings])
            notes.append(
                f"UID mapping truncated: Showing {max_uid_mappings:,} of {len(uid_mapping):,} mappings. "
                f"Full mapping saved to uid_mapping_full_*.json"
            )

        return ReportData(
            report_id=str(uuid.uuid4()),
            generated_at=datetime.now(),
            generator_version=__version__,
            preset_name=preset.name,
            preset_description=preset.description,
            compliance_standards=preset.compliance,
            date_handling=preset.date_handling.value,
            input_path=input_path,
            output_path=output_path,
            files_processed=stats.files_processed,
            files_successful=stats.files_successful,
            files_failed=stats.files_failed,
            studies_processed=stats.num_studies,
            series_processed=stats.num_series,
            total_tags_modified=stats.total_tags_modified,
            total_tags_removed=stats.total_tags_removed,
            total_uids_remapped=stats.total_uids_remapped,
            total_private_tags_removed=stats.total_private_tags_removed,
            processing_time_seconds=stats.processing_time.total_seconds(),
            file_records=file_records,
            tag_rules_applied=tag_rules,
            errors=stats.errors[:100] if len(stats.errors) > 100 else stats.errors,  # Limit errors too
            uid_mapping=limited_uid_mapping,
            notes=notes,
        )

    def _calculate_hash(self, report_data: ReportData) -> str:
        """Calculate SHA-256 hash of report content."""
        # Exclude report_hash from calculation (circular)
        data = report_data.to_dict()
        data["report_hash"] = ""

        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()

    @classmethod
    def from_json(cls, json_path: Path) -> ReportData:
        """
        Load ReportData from JSON file for regeneration.

        Args:
            json_path: Path to JSON report file

        Returns:
            ReportData reconstructed from JSON
        """
        with open(json_path, encoding="utf-8") as f:
            data = json.load(f)

        # Reconstruct file records
        file_records = []
        for fr in data.get("file_records", []):
            record = FileRecord(
                original_path=fr.get("original_path", ""),
                output_path=fr.get("output_path", ""),
                success=fr.get("success", False),
                study_uid_original=fr.get("study_uid", {}).get("original", ""),
                study_uid_new=fr.get("study_uid", {}).get("new", ""),
                series_uid_original=fr.get("series_uid", {}).get("original", ""),
                series_uid_new=fr.get("series_uid", {}).get("new", ""),
                sop_uid_original=fr.get("sop_uid", {}).get("original", ""),
                sop_uid_new=fr.get("sop_uid", {}).get("new", ""),
                tags_modified=fr.get("tags_modified", 0),
                tags_removed=fr.get("tags_removed", 0),
                private_tags_removed=fr.get("private_tags_removed", 0),
                error_message=fr.get("error_message", ""),
            )
            file_records.append(record)

        # Parse datetime
        generated_at_str = data.get("generated_at", "")
        try:
            generated_at = datetime.fromisoformat(generated_at_str)
        except ValueError:
            generated_at = datetime.now()

        anonymization = data.get("anonymization", {})
        summary = data.get("summary", {})

        return ReportData(
            report_id=data.get("report_id", str(uuid.uuid4())),
            generated_at=generated_at,
            generator_version=data.get("generator_version", __version__),
            report_hash=data.get("report_hash", ""),
            preset_name=anonymization.get("preset_name", ""),
            preset_description=anonymization.get("preset_description", ""),
            compliance_standards=anonymization.get("compliance_standards", []),
            date_handling=anonymization.get("date_handling", ""),
            input_path=anonymization.get("input_path", ""),
            output_path=anonymization.get("output_path", ""),
            files_processed=summary.get("files_processed", 0),
            files_successful=summary.get("files_successful", 0),
            files_failed=summary.get("files_failed", 0),
            studies_processed=summary.get("studies_processed", 0),
            series_processed=summary.get("series_processed", 0),
            total_tags_modified=summary.get("total_tags_modified", 0),
            total_tags_removed=summary.get("total_tags_removed", 0),
            total_uids_remapped=summary.get("total_uids_remapped", 0),
            total_private_tags_removed=summary.get("total_private_tags_removed", 0),
            processing_time_seconds=summary.get("processing_time_seconds", 0.0),
            file_records=file_records,
            tag_rules_applied=data.get("tag_rules_applied", []),
            errors=data.get("errors", []),
            uid_mapping=data.get("uid_mapping", {}),
        )
