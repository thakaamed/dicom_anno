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
"""DICOM anonymization processor."""

import hashlib
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from pydicom import dcmread
from pydicom.errors import InvalidDicomError

from thakaamed_dicom.config.models import ActionCode, DateHandling, PresetConfig
from thakaamed_dicom.engine.actions import ActionFactory
from thakaamed_dicom.engine.date_shifter import DateShifter
from thakaamed_dicom.engine.statistics import FileStatistics, ProcessingStatistics
from thakaamed_dicom.engine.uid_mapper import UIDMapper


@dataclass
class AnonymizedFileInfo:
    """Information about anonymized file for path generation."""
    
    study_uid_hash: str
    series_uid_hash: str
    sop_uid_hash: str
    
    # Counter for files without UIDs
    _unknown_counter: int = 0
    
    @staticmethod
    def generate_hash(uid: str, length: int = 12, fallback_random: bool = True) -> str:
        """Generate a short hash from a UID.
        
        Args:
            uid: The UID to hash
            length: Length of the hash output
            fallback_random: If True, generate random hash for empty UIDs
        """
        if not uid:
            if fallback_random:
                # Generate random hash for files without UIDs
                import uuid
                random_id = str(uuid.uuid4())
                hash_bytes = hashlib.sha256(random_id.encode()).hexdigest()
                return hash_bytes[:length]
            return "unknown"
        hash_bytes = hashlib.sha256(uid.encode()).hexdigest()
        return hash_bytes[:length]


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
        output_path: Path | None = None,
        output_dir: Path | None = None,
        dry_run: bool = False,
    ) -> FileStatistics:
        """
        Process single DICOM file.

        Args:
            input_path: Path to input DICOM file
            output_path: Explicit path for output file (if None, uses anonymous naming)
            output_dir: Base output directory for anonymous naming
            dry_run: If True, don't write output file

        Returns:
            FileStatistics with processing results
        """
        start_time = time.time()
        stats = FileStatistics(file_path=str(input_path), success=False)

        try:
            # Read DICOM file
            ds = dcmread(str(input_path), force=True)

            # Capture study/series UIDs before modification for tracking
            if hasattr(ds, "StudyInstanceUID") and ds.StudyInstanceUID:
                stats.study_uid = str(ds.StudyInstanceUID)
            if hasattr(ds, "SeriesInstanceUID") and ds.SeriesInstanceUID:
                stats.series_uid = str(ds.SeriesInstanceUID)
            
            # Capture original SOPInstanceUID for anonymous filename generation
            original_sop_uid = ""
            if hasattr(ds, "SOPInstanceUID") and ds.SOPInstanceUID:
                original_sop_uid = str(ds.SOPInstanceUID)

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

            # Determine output path
            if output_path is None and output_dir is not None:
                # Generate anonymous path using Study/Series/SOP structure
                output_path = self._generate_anonymous_path(
                    output_dir,
                    stats.study_uid,
                    stats.series_uid,
                    original_sop_uid,
                )

            # Write output file
            if not dry_run and output_path is not None:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                ds.save_as(str(output_path))

            stats.success = True

        except InvalidDicomError as e:
            stats.error_message = f"Invalid DICOM file: {e}"
        except Exception as e:
            stats.error_message = str(e)

        stats.processing_time_ms = (time.time() - start_time) * 1000
        return stats
    
    def _generate_anonymous_path(
        self,
        output_dir: Path,
        study_uid: str,
        series_uid: str,
        sop_uid: str,
    ) -> Path:
        """
        Generate anonymous file path using hash-based naming.
        
        Structure: output_dir/Study_<hash>/Series_<hash>/<hash>.dcm
        
        Args:
            output_dir: Base output directory
            study_uid: Original StudyInstanceUID
            series_uid: Original SeriesInstanceUID  
            sop_uid: Original SOPInstanceUID
            
        Returns:
            Anonymous output path
        """
        study_hash = AnonymizedFileInfo.generate_hash(study_uid, 8)
        series_hash = AnonymizedFileInfo.generate_hash(series_uid, 8)
        sop_hash = AnonymizedFileInfo.generate_hash(sop_uid, 12)
        
        return output_dir / f"Study_{study_hash}" / f"Series_{series_hash}" / f"{sop_hash}.dcm"

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
        anonymous_filenames: bool = True,
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
            anonymous_filenames: If True, use hash-based anonymous filenames
                                organized by Study/Series folders

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
            if anonymous_filenames:
                # Use anonymous hash-based naming with Study/Series folders
                return self.process_file(
                    input_path, 
                    output_path=None, 
                    output_dir=output_dir, 
                    dry_run=dry_run
                )
            else:
                # Legacy: preserve original relative path structure
                rel_path = input_path.relative_to(input_dir)
                output_path = output_dir / rel_path
                return self.process_file(input_path, output_path=output_path, dry_run=dry_run)

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
