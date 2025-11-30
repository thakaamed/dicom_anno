# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Report generation command for THAKAAMED DICOM Anonymizer."""

from pathlib import Path

import click

from dicom_anonymizer.cli.console import (
    console,
    print_error,
    print_info,
    print_success,
)
from dicom_anonymizer.reports.generator import ReportGenerator
from dicom_anonymizer.reports.models import ReportFormat


@click.command()
@click.option(
    "--from-json",
    "json_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Path to existing JSON audit report",
)
@click.option(
    "--format",
    "-f",
    "report_format",
    type=click.Choice(["pdf", "json", "csv", "all"], case_sensitive=False),
    default="all",
    help="Report format(s) to generate",
)
@click.option(
    "--output",
    "-o",
    "output_dir",
    type=click.Path(path_type=Path),
    help="Output directory for reports (default: same as input)",
)
def report(
    json_path: Path,
    report_format: str,
    output_dir: Path | None,
) -> None:
    """Generate reports from existing JSON audit data.

    Regenerate PDF, CSV, or other report formats from a previously
    generated JSON audit report.

    Examples:

        \b
        # Generate PDF from existing JSON audit
        thakaamed-dicom report --from-json ./reports/audit.json --format pdf

        \b
        # Generate all formats to specific directory
        thakaamed-dicom report --from-json ./audit.json -o ./new_reports

        \b
        # Generate CSV only
        thakaamed-dicom report --from-json ./audit.json --format csv
    """
    # Determine output directory
    if output_dir is None:
        output_dir = json_path.parent

    print_info(f"Loading JSON audit from: {json_path}")

    # Load report data from JSON
    try:
        report_data = ReportGenerator.from_json(json_path)
    except Exception as e:
        print_error(f"Failed to load JSON audit: {e}")
        raise click.Abort() from e

    # Parse format
    format_map = {
        "pdf": [ReportFormat.PDF],
        "json": [ReportFormat.JSON],
        "csv": [ReportFormat.CSV],
        "all": [ReportFormat.ALL],
    }
    formats = format_map.get(report_format.lower(), [ReportFormat.ALL])

    # Generate reports
    with console.status("Generating reports..."):
        generator = ReportGenerator()
        generated_files = generator.generate_from_data(
            report_data=report_data,
            report_dir=output_dir,
            formats=formats,
        )

    if generated_files:
        print_success("Reports generated:")
        for report_path in generated_files:
            console.print(f"  [dim]{report_path}[/dim]")
    else:
        print_error("No reports were generated")
