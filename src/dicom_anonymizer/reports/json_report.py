# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""JSON report builder."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from dicom_anonymizer.reports.models import ReportData


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder for datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class JSONReportBuilder:
    """Build JSON audit report."""

    def build(self, report_data: ReportData, output_path: Path) -> Path:
        """
        Generate JSON report file.

        Args:
            report_data: Complete report data
            output_path: Path for output file

        Returns:
            Path to generated file
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        data = report_data.to_dict()

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, cls=DateTimeEncoder, ensure_ascii=False)

        return output_path
