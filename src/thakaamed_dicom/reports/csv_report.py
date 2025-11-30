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
"""CSV report builder."""

import csv
from pathlib import Path

from thakaamed_dicom.reports.models import ReportData


class CSVReportBuilder:
    """Build CSV report for spreadsheet analysis."""

    def build(self, report_data: ReportData, output_path: Path) -> Path:
        """
        Generate CSV report file.

        Args:
            report_data: Complete report data
            output_path: Path for output file

        Returns:
            Path to generated file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use utf-8-sig for Excel compatibility (includes BOM)
        with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)

            # Summary section
            writer.writerow(["DICOM ANONYMIZATION REPORT"])
            writer.writerow([])
            writer.writerow(["Report ID", report_data.report_id])
            writer.writerow(["Generated At", report_data.generated_at.isoformat()])
            writer.writerow(["Preset", report_data.preset_name])
            writer.writerow(["Compliance", ", ".join(report_data.compliance_standards)])
            writer.writerow([])
            writer.writerow(["SUMMARY STATISTICS"])
            writer.writerow(["Metric", "Value"])
            writer.writerow(["Files Processed", report_data.files_processed])
            writer.writerow(["Files Successful", report_data.files_successful])
            writer.writerow(["Files Failed", report_data.files_failed])
            writer.writerow(["Studies Processed", report_data.studies_processed])
            writer.writerow(["Series Processed", report_data.series_processed])
            writer.writerow(["Tags Modified", report_data.total_tags_modified])
            writer.writerow(["Tags Removed", report_data.total_tags_removed])
            writer.writerow(["UIDs Remapped", report_data.total_uids_remapped])
            writer.writerow(["Private Tags Removed", report_data.total_private_tags_removed])
            writer.writerow(
                ["Processing Time (s)", f"{report_data.processing_time_seconds:.2f}"]
            )
            writer.writerow([])

            # File details section
            writer.writerow(["FILE DETAILS"])
            writer.writerow(
                [
                    "Original Path",
                    "Output Path",
                    "Status",
                    "Study UID (Original)",
                    "Study UID (New)",
                    "Tags Modified",
                    "Tags Removed",
                    "Error",
                ]
            )

            for record in report_data.file_records:
                writer.writerow(
                    [
                        record.original_path,
                        record.output_path,
                        "Success" if record.success else "Failed",
                        record.study_uid_original,
                        record.study_uid_new,
                        record.tags_modified,
                        record.tags_removed,
                        record.error_message,
                    ]
                )

        return output_path
