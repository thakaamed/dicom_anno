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
"""Anonymize command for THAKAAMED DICOM Anonymizer."""

from pathlib import Path

import click
from rich import box
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)
from rich.table import Table

from thakaamed_dicom.cli.console import (
    BRAND_GOLD,
    console,
    print_error,
    print_info,
    print_success,
    print_warning,
)
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor
from thakaamed_dicom.reports.generator import ReportGenerator
from thakaamed_dicom.reports.models import ReportFormat


@click.command()
@click.option(
    "--input",
    "-i",
    "input_path",
    type=click.Path(exists=True, path_type=Path),
    required=True,
    help="Input DICOM file or directory",
)
@click.option(
    "--output",
    "-o",
    "output_path",
    type=click.Path(path_type=Path),
    required=True,
    help="Output file or directory for anonymized files",
)
@click.option(
    "--preset",
    "-p",
    type=str,
    required=True,
    help="Preset name (sfda_safe_harbor, research, full_anonymization) or path to YAML",
)
@click.option(
    "--date-anchor",
    type=str,
    help="Anchor date for date shifting (YYYYMMDD format)",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Preview changes without writing files",
)
@click.option(
    "--parallel/--no-parallel",
    default=True,
    help="Enable/disable parallel processing",
)
@click.option(
    "--workers",
    "-w",
    type=int,
    default=4,
    help="Number of parallel workers",
)
@click.option(
    "--report-format",
    type=click.Choice(["pdf", "json", "csv", "all", "none"], case_sensitive=False),
    default="all",
    help="Report format(s) to generate",
)
@click.option(
    "--no-reports",
    is_flag=True,
    help="Disable report generation",
)
@click.option(
    "--report-dir",
    type=click.Path(path_type=Path),
    help="Directory for reports (default: output/reports)",
)
def anonymize(
    input_path: Path,
    output_path: Path,
    preset: str,
    date_anchor: str | None,
    dry_run: bool,
    parallel: bool,
    workers: int,
    report_format: str,
    no_reports: bool,
    report_dir: Path | None,
) -> None:
    """Anonymize DICOM files or directories.

    Process DICOM files according to the specified anonymization preset
    and generate audit reports.

    Examples:

        \b
        # Basic anonymization with SFDA preset
        thakaamed-dicom anonymize -i ./dicom -o ./output -p sfda_safe_harbor

        \b
        # Research preset with date shifting
        thakaamed-dicom anonymize -i ./study -o ./anon -p research --date-anchor 20180315

        \b
        # Dry run to preview changes
        thakaamed-dicom anonymize -i ./dicom -o ./output -p sfda_safe_harbor --dry-run

        \b
        # Single worker processing (no parallelism)
        thakaamed-dicom anonymize -i ./dicom -o ./output -p sfda_safe_harbor --no-parallel

        \b
        # Generate only PDF report
        thakaamed-dicom anonymize -i ./dicom -o ./output -p sfda_safe_harbor --report-format pdf

        \b
        # Disable report generation
        thakaamed-dicom anonymize -i ./dicom -o ./output -p sfda_safe_harbor --no-reports
    """
    # Load preset
    try:
        preset_config = load_preset(preset)
    except FileNotFoundError as e:
        print_error(f"Preset not found: {e}")
        raise click.Abort() from e
    except ValueError as e:
        print_error(f"Invalid preset configuration: {e}")
        raise click.Abort() from e

    # Display processing info
    console.print()
    console.rule(f"[bold {BRAND_GOLD}]THAKAAMED DICOM Anonymizer[/bold {BRAND_GOLD}]")
    console.print()
    print_info(f"Input: {input_path}")
    print_info(f"Output: {output_path}")
    print_info(f"Preset: {preset_config.name}")
    if dry_run:
        print_warning("DRY RUN MODE - No files will be written")
    console.print()

    # Create processor
    processor = DicomProcessor(
        preset=preset_config,
        date_anchor=date_anchor,
    )

    # Process based on input type
    if input_path.is_file():
        # Single file
        with console.status("Processing file..."):
            stats = processor.process_file(input_path, output_path, dry_run=dry_run)

        if stats.success:
            print_success("File processed successfully")
            _print_file_summary(stats)
        else:
            print_error(f"Processing failed: {stats.error_message}")

        # For single files, no batch reports
        return

    # Directory processing
    print_info("Scanning for DICOM files...")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Processing files...", total=None)

        def update_progress(completed: int, total: int) -> None:
            progress.update(task, completed=completed, total=total)

        stats = processor.process_directory(
            input_path,
            output_path,
            parallel=parallel,
            workers=workers,
            dry_run=dry_run,
            progress_callback=update_progress,
        )

    console.print()
    _print_batch_summary(stats)

    if stats.files_failed > 0:
        console.print()
        print_warning("Errors encountered:")
        for error in stats.errors[:10]:  # Show first 10 errors
            console.print(f"  [dim]{error}[/dim]")
        if len(stats.errors) > 10:
            console.print(f"  [dim]... and {len(stats.errors) - 10} more[/dim]")

    # Generate reports
    should_generate_reports = (
        not dry_run
        and not no_reports
        and report_format.lower() != "none"
        and stats.files_successful > 0
    )

    if should_generate_reports:
        console.print()
        _generate_reports(
            stats=stats,
            preset_config=preset_config,
            input_path=input_path,
            output_path=output_path,
            report_format=report_format,
            report_dir=report_dir,
            uid_mapping=processor.uid_mapper.export_mapping(),
        )

    if not dry_run and stats.files_successful > 0:
        console.print()
        print_success(f"Anonymization complete! Files saved to {output_path}")


def _generate_reports(
    stats,
    preset_config,
    input_path: Path,
    output_path: Path,
    report_format: str,
    report_dir: Path | None,
    uid_mapping: dict,
) -> None:
    """Generate audit reports."""
    # Determine report directory
    if report_dir is None:
        report_dir = output_path / "reports"

    # Parse format
    format_map = {
        "pdf": [ReportFormat.PDF],
        "json": [ReportFormat.JSON],
        "csv": [ReportFormat.CSV],
        "all": [ReportFormat.ALL],
    }
    formats = format_map.get(report_format.lower(), [ReportFormat.ALL])

    with console.status("Generating reports..."):
        generator = ReportGenerator()
        generated_files = generator.generate(
            stats=stats,
            preset=preset_config,
            input_path=str(input_path),
            output_path=str(output_path),
            uid_mapping=uid_mapping,
            report_dir=report_dir,
            formats=formats,
        )

    if generated_files:
        print_success("Reports generated:")
        for report_path in generated_files:
            console.print(f"  [dim]{report_path}[/dim]")


def _print_file_summary(stats) -> None:
    """Print summary for single file processing."""
    table = Table(title="Processing Summary", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="magenta", justify="right")

    table.add_row("Tags Modified", str(stats.tags_modified))
    table.add_row("Tags Removed", str(stats.tags_removed))
    table.add_row("UIDs Remapped", str(stats.uids_remapped))
    table.add_row("Private Tags Removed", str(stats.private_tags_removed))
    table.add_row("Processing Time", f"{stats.processing_time_ms:.1f}ms")

    console.print(table)


def _print_batch_summary(stats) -> None:
    """Print summary for batch processing."""
    table = Table(title="Processing Summary", box=box.DOUBLE)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta", justify="right")

    table.add_row("Files Processed", str(stats.files_processed))
    table.add_row("Files Successful", f"[green]{stats.files_successful}[/green]")
    if stats.files_failed > 0:
        table.add_row("Files Failed", f"[red]{stats.files_failed}[/red]")
    table.add_row("Studies Processed", str(stats.num_studies))
    table.add_row("Series Processed", str(stats.num_series))
    table.add_row("-" * 20, "-" * 10)
    table.add_row("Tags Modified", f"{stats.total_tags_modified:,}")
    table.add_row("Tags Removed", f"{stats.total_tags_removed:,}")
    table.add_row("UIDs Remapped", f"{stats.total_uids_remapped:,}")
    table.add_row("Private Tags Removed", f"{stats.total_private_tags_removed:,}")
    table.add_row("-" * 20, "-" * 10)
    table.add_row("Processing Time", f"{stats.processing_time.total_seconds():.1f}s")

    console.print(table)
