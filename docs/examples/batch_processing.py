#!/usr/bin/env python3
"""
Batch DICOM Processing Example

This script demonstrates how to process multiple DICOM files
in a directory with progress tracking and report generation.

Usage:
    python batch_processing.py ./input_directory ./output_directory
"""

import argparse
import sys
from pathlib import Path

from dicom_anonymizer.config.loader import load_preset
from dicom_anonymizer.engine.processor import DicomProcessor
from dicom_anonymizer.reports.generator import ReportGenerator
from dicom_anonymizer.reports.models import ReportFormat


def progress_callback(current: int, total: int) -> None:
    """Display progress bar."""
    bar_width = 40
    progress = current / total if total > 0 else 1
    filled = int(bar_width * progress)
    bar = "=" * filled + "-" * (bar_width - filled)
    percent = int(progress * 100)
    print(f"\r[{bar}] {percent}% ({current}/{total})", end="", flush=True)


def main():
    """Run batch DICOM anonymization with reports."""
    parser = argparse.ArgumentParser(
        description="Batch DICOM anonymization example"
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Input directory containing DICOM files"
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Output directory for anonymized files"
    )
    parser.add_argument(
        "--preset",
        "-p",
        default="sfda_safe_harbor",
        help="Preset name (default: sfda_safe_harbor)"
    )
    parser.add_argument(
        "--workers",
        "-w",
        type=int,
        default=4,
        help="Number of parallel workers (default: 4)"
    )
    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel processing"
    )

    args = parser.parse_args()

    # Validate input
    if not args.input_dir.exists():
        print(f"Error: Input directory does not exist: {args.input_dir}")
        sys.exit(1)

    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 50)
    print("  DICOM Batch Anonymization")
    print("=" * 50)
    print(f"\nInput:   {args.input_dir}")
    print(f"Output:  {args.output_dir}")
    print(f"Preset:  {args.preset}")
    print(f"Workers: {args.workers}")
    print()

    # Load preset
    try:
        preset = load_preset(args.preset)
        print(f"Loaded preset: {preset.name}")
    except Exception as e:
        print(f"Error loading preset: {e}")
        sys.exit(1)

    # Create processor
    processor = DicomProcessor(preset=preset)

    # Process directory
    print("\nProcessing files...")
    stats = processor.process_directory(
        input_dir=args.input_dir,
        output_dir=args.output_dir,
        parallel=not args.no_parallel,
        workers=args.workers,
        progress_callback=progress_callback
    )
    print()  # New line after progress bar

    # Display results
    print("\n" + "=" * 50)
    print("  Processing Summary")
    print("=" * 50)
    print(f"  Files processed:      {stats.files_processed:,}")
    print(f"  Files successful:     {stats.files_successful:,}")
    print(f"  Files failed:         {stats.files_failed:,}")
    print(f"  Studies processed:    {stats.studies_processed:,}")
    print(f"  Series processed:     {stats.series_processed:,}")
    print(f"  Tags modified:        {stats.total_tags_modified:,}")
    print(f"  Tags removed:         {stats.total_tags_removed:,}")
    print(f"  UIDs remapped:        {stats.total_uids_remapped:,}")
    print(f"  Private tags removed: {stats.total_private_tags_removed:,}")
    print(f"  Processing time:      {stats.processing_time_seconds:.2f}s")
    print("=" * 50)

    # Show errors if any
    if stats.errors:
        print("\nErrors encountered:")
        for error in stats.errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(stats.errors) > 10:
            print(f"  ... and {len(stats.errors) - 10} more errors")

    # Generate reports
    if stats.files_successful > 0:
        print("\nGenerating reports...")
        report_dir = args.output_dir / "reports"
        report_dir.mkdir(exist_ok=True)

        generator = ReportGenerator(output_dir=report_dir)
        report_paths = generator.generate(
            statistics=stats,
            preset=preset,
            input_path=args.input_dir,
            output_path=args.output_dir,
            formats=[ReportFormat.PDF, ReportFormat.JSON, ReportFormat.CSV]
        )

        print("\nReports generated:")
        for path in report_paths:
            print(f"  {path}")

    print(f"\nAnonymized files saved to: {args.output_dir}")


if __name__ == "__main__":
    main()
