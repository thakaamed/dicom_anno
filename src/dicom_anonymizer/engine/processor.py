# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""DICOM anonymization processor."""

import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

from pydicom import dcmread
from pydicom.errors import InvalidDicomError

from dicom_anonymizer.config.models import ActionCode, DateHandling, PresetConfig
from dicom_anonymizer.engine.actions import ActionFactory
from dicom_anonymizer.engine.date_shifter import DateShifter
from dicom_anonymizer.engine.statistics import FileStatistics, ProcessingStatistics
from dicom_anonymizer.engine.uid_mapper import UIDMapper


class DicomProcessor:
    """Main DICOM anonymization processor."""

    def __init__(
        self,
        preset: PresetConfig,
        uid_salt: str | None = None,
        date_anchor: str | None = None,
    ):
        """
        Initialize processor.

        Args:
            preset: Anonymization preset configuration
            uid_salt: Salt for UID hashing (random if not provided)
            date_anchor: Anchor date for date shifting (YYYYMMDD)
        """
        self.preset = preset
        self.uid_mapper = UIDMapper(salt=uid_salt)
        self.action_factory = ActionFactory(self.uid_mapper)

        # Initialize date shifter if needed
        self.date_shifter: DateShifter | None = None
        if preset.date_handling == DateHandling.SHIFT and date_anchor:
            anchor = datetime.strptime(date_anchor, "%Y%m%d")
            self.date_shifter = DateShifter(anchor_date=anchor)

    def process_file(
        self,
        input_path: Path,
        output_path: Path,
        dry_run: bool = False,
    ) -> FileStatistics:
        """
        Process single DICOM file.

        Args:
            input_path: Path to input DICOM file
            output_path: Path for output file
            dry_run: If True, don't write output file

        Returns:
            FileStatistics with processing results
        """
        start_time = time.time()
        stats = FileStatistics(file_path=str(input_path), success=False)

        try:
            # Read DICOM file
            ds = dcmread(str(input_path), force=True)

            # Apply tag rules
            for rule in self.preset.tag_rules:
                handler = self.action_factory.get_handler(rule.action)
                if handler.apply(ds, rule.tag, rule):
                    if rule.action == ActionCode.X:
                        stats.tags_removed += 1
                    else:
                        stats.tags_modified += 1

            # Handle UIDs (always remap Study, Series, SOP Instance UIDs)
            stats.uids_remapped += self._handle_standard_uids(ds)

            # Handle dates based on preset configuration
            self._handle_dates(ds)

            # Handle private tags
            if self.preset.remove_private_tags:
                # Count private tags before removal
                private_count = sum(1 for elem in ds if elem.tag.is_private)
                ds.remove_private_tags()
                stats.private_tags_removed = private_count

            # Set de-identification markers
            self._set_deidentification_markers(ds)

            # Write output file
            if not dry_run:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                ds.save_as(str(output_path))

            stats.success = True

        except InvalidDicomError as e:
            stats.error_message = f"Invalid DICOM file: {e}"
        except Exception as e:
            stats.error_message = str(e)

        stats.processing_time_ms = (time.time() - start_time) * 1000
        return stats

    def _handle_standard_uids(self, ds) -> int:
        """Remap standard UIDs and return count."""
        count = 0
        uid_tags = [
            "StudyInstanceUID",
            "SeriesInstanceUID",
            "SOPInstanceUID",
            "FrameOfReferenceUID",
        ]

        for tag_name in uid_tags:
            if hasattr(ds, tag_name):
                original = getattr(ds, tag_name)
                if original:
                    new_uid = self.uid_mapper.get_or_create(str(original))
                    setattr(ds, tag_name, new_uid)
                    count += 1

        # Update MediaStorageSOPInstanceUID to match SOPInstanceUID
        if (
            hasattr(ds, "file_meta")
            and hasattr(ds.file_meta, "MediaStorageSOPInstanceUID")
            and hasattr(ds, "SOPInstanceUID")
        ):
            ds.file_meta.MediaStorageSOPInstanceUID = ds.SOPInstanceUID

        return count

    def _handle_dates(self, ds) -> None:
        """Handle date fields based on preset configuration."""
        date_tags = ["StudyDate", "SeriesDate", "AcquisitionDate", "ContentDate"]
        time_tags = ["StudyTime", "SeriesTime", "AcquisitionTime", "ContentTime"]

        if self.preset.date_handling == DateHandling.REMOVE:
            # Remove all dates
            for tag in date_tags + time_tags:
                if hasattr(ds, tag):
                    setattr(ds, tag, "")

        elif self.preset.date_handling == DateHandling.SHIFT and self.date_shifter:
            # Shift dates
            for tag in date_tags:
                if hasattr(ds, tag) and getattr(ds, tag):
                    original = getattr(ds, tag)
                    shifted = self.date_shifter.shift_date(str(original))
                    setattr(ds, tag, shifted)

        elif self.preset.date_handling == DateHandling.KEEP_YEAR:
            # Keep only year
            for tag in date_tags:
                if hasattr(ds, tag) and getattr(ds, tag):
                    original = str(getattr(ds, tag))
                    if len(original) >= 4:
                        setattr(ds, tag, f"{original[:4]}0101")

    def _set_deidentification_markers(self, ds) -> None:
        """Set required de-identification marker attributes."""
        ds.PatientIdentityRemoved = "YES"
        ds.DeidentificationMethod = f"THAKAAMED - {self.preset.name}"

    def process_directory(
        self,
        input_dir: Path,
        output_dir: Path,
        parallel: bool = True,
        workers: int = 4,
        dry_run: bool = False,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> ProcessingStatistics:
        """
        Process all DICOM files in directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            parallel: Enable parallel processing
            workers: Number of parallel workers
            dry_run: If True, don't write output files
            progress_callback: Called with (completed, total) for progress updates

        Returns:
            ProcessingStatistics with aggregate results
        """
        stats = ProcessingStatistics()

        # Find all DICOM files
        dicom_files = self._find_dicom_files(input_dir)
        total_files = len(dicom_files)

        if total_files == 0:
            return stats

        def process_one(input_path: Path) -> FileStatistics:
            # Calculate relative path for output
            rel_path = input_path.relative_to(input_dir)
            output_path = output_dir / rel_path
            return self.process_file(input_path, output_path, dry_run)

        if parallel and workers > 1:
            # Parallel processing
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(process_one, f): f for f in dicom_files}

                for i, future in enumerate(as_completed(futures)):
                    file_stats = future.result()
                    stats.add_file_result(file_stats)

                    if progress_callback:
                        progress_callback(i + 1, total_files)
        else:
            # Sequential processing
            for i, input_path in enumerate(dicom_files):
                file_stats = process_one(input_path)
                stats.add_file_result(file_stats)

                if progress_callback:
                    progress_callback(i + 1, total_files)

        stats.finalize()
        return stats

    def _find_dicom_files(self, directory: Path) -> list[Path]:
        """Find all DICOM files in directory recursively."""
        dicom_files = []

        for path in directory.rglob("*"):
            if path.is_file():
                # Check common DICOM extensions
                if path.suffix.lower() in (".dcm", ".dicom"):
                    dicom_files.append(path)
                elif path.suffix == "":
                    # Try to read as DICOM (no extension)
                    try:
                        dcmread(str(path), stop_before_pixels=True, force=True)
                        dicom_files.append(path)
                    except Exception:
                        pass

        return sorted(dicom_files)
