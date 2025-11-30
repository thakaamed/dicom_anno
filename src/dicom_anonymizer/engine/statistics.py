# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Processing statistics for DICOM anonymization."""

import threading
from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class FileStatistics:
    """Statistics for a single file."""

    file_path: str
    success: bool
    tags_modified: int = 0
    tags_removed: int = 0
    uids_remapped: int = 0
    private_tags_removed: int = 0
    error_message: str = ""
    processing_time_ms: float = 0.0


@dataclass
class ProcessingStatistics:
    """Aggregate statistics for batch processing."""

    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None

    files_processed: int = 0
    files_successful: int = 0
    files_failed: int = 0

    studies_processed: set = field(default_factory=set)
    series_processed: set = field(default_factory=set)

    total_tags_modified: int = 0
    total_tags_removed: int = 0
    total_uids_remapped: int = 0
    total_private_tags_removed: int = 0

    errors: list[str] = field(default_factory=list)
    file_stats: list[FileStatistics] = field(default_factory=list)

    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def add_file_result(self, stats: FileStatistics) -> None:
        """Thread-safe addition of file statistics."""
        with self._lock:
            self.file_stats.append(stats)
            self.files_processed += 1
            if stats.success:
                self.files_successful += 1
                self.total_tags_modified += stats.tags_modified
                self.total_tags_removed += stats.tags_removed
                self.total_uids_remapped += stats.uids_remapped
                self.total_private_tags_removed += stats.private_tags_removed
            else:
                self.files_failed += 1
                self.errors.append(f"{stats.file_path}: {stats.error_message}")

    def add_study(self, study_uid: str) -> None:
        """Thread-safe addition of study UID."""
        with self._lock:
            self.studies_processed.add(study_uid)

    def add_series(self, series_uid: str) -> None:
        """Thread-safe addition of series UID."""
        with self._lock:
            self.series_processed.add(series_uid)

    def finalize(self) -> None:
        """Mark processing complete."""
        self.end_time = datetime.now()

    @property
    def processing_time(self) -> timedelta:
        """Total processing time."""
        end = self.end_time or datetime.now()
        return end - self.start_time

    @property
    def num_studies(self) -> int:
        """Number of unique studies processed."""
        return len(self.studies_processed)

    @property
    def num_series(self) -> int:
        """Number of unique series processed."""
        return len(self.series_processed)
