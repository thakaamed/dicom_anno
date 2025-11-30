#!/usr/bin/env python3
"""
Basic DICOM Anonymization Example

This script demonstrates the simplest way to anonymize DICOM files
using DICOM Anonymizer.

Usage:
    python basic_anonymization.py
"""

from pathlib import Path

from dicom_anonymizer.config.loader import load_preset
from dicom_anonymizer.engine.processor import DicomProcessor


def main():
    """Demonstrate basic DICOM anonymization."""
    # Define paths
    input_file = Path("./sample.dcm")
    output_file = Path("./anonymized_sample.dcm")

    # Check if input exists (for demo purposes)
    if not input_file.exists():
        print(f"Note: Create a sample DICOM file at {input_file} to test")
        print("Demonstrating API usage...")

    # Step 1: Load a preset
    # Available presets: sfda_safe_harbor, research, full_anonymization
    preset = load_preset("sfda_safe_harbor")
    print(f"Loaded preset: {preset.name}")
    print(f"Description: {preset.description}")

    # Step 2: Create processor
    processor = DicomProcessor(preset=preset)

    # Step 3: Process file (only if it exists)
    if input_file.exists():
        stats = processor.process_file(input_file, output_file)

        # Step 4: Check results
        if stats.success:
            print(f"\nAnonymization successful!")
            print(f"  Tags modified: {stats.tags_modified}")
            print(f"  Tags removed: {stats.tags_removed}")
            print(f"  Private tags removed: {stats.private_tags_removed}")
            print(f"\nUID Remapping:")
            print(f"  Study UID: {stats.study_uid_original} -> {stats.study_uid_new}")
            print(f"  Series UID: {stats.series_uid_original} -> {stats.series_uid_new}")
            print(f"  SOP UID: {stats.sop_uid_original} -> {stats.sop_uid_new}")
            print(f"\nOutput saved to: {output_file}")
        else:
            print(f"Error: {stats.error_message}")
    else:
        print("\nAPI demonstration complete. Provide a DICOM file to test actual processing.")


if __name__ == "__main__":
    main()
