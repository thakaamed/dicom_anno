# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Date/time shifting for DICOM de-identification."""

from datetime import datetime, timedelta


class DateShifter:
    """Date/time shifting for longitudinal data de-identification."""

    # DICOM date/time formats
    DATE_FORMAT = "%Y%m%d"
    TIME_FORMAT = "%H%M%S"
    DATETIME_FORMAT = "%Y%m%d%H%M%S"

    def __init__(
        self,
        base_date: datetime | None = None,
        anchor_date: datetime | None = None,
    ):
        """
        Initialize date shifter.

        Args:
            base_date: Target base date (default: 1975-01-01)
            anchor_date: Original anchor date for offset calculation
        """
        self.base_date = base_date or datetime(1975, 1, 1)
        self.anchor_date = anchor_date
        self._offset: timedelta | None = None

        if anchor_date:
            self._offset = self.base_date - anchor_date

    def set_anchor(self, anchor_date: datetime) -> None:
        """Set anchor date and calculate offset."""
        self.anchor_date = anchor_date
        self._offset = self.base_date - anchor_date

    def shift_date(self, date_str: str) -> str:
        """
        Shift DICOM date string.

        Args:
            date_str: DICOM date (YYYYMMDD)

        Returns:
            Shifted date string
        """
        if not date_str or not self._offset:
            return date_str

        try:
            original = datetime.strptime(date_str[:8], self.DATE_FORMAT)
            shifted = original + self._offset
            return shifted.strftime(self.DATE_FORMAT)
        except ValueError:
            return date_str  # Return original if parsing fails

    def shift_time(
        self,
        time_str: str,
        date_str: str | None = None,
        shifted_date_str: str | None = None,
    ) -> str:
        """
        Shift DICOM time string (needed for midnight-spanning shifts).

        Args:
            time_str: DICOM time (HHMMSS or HHMMSS.ffffff)
            date_str: Original date (for midnight calculation)
            shifted_date_str: Shifted date

        Returns:
            Shifted time string
        """
        if not time_str:
            return time_str

        # For simple cases, time doesn't change (same-day offset)
        # Complex midnight handling would need datetime parsing
        return time_str

    def shift_datetime(self, datetime_str: str) -> str:
        """
        Shift DICOM datetime string.

        Args:
            datetime_str: DICOM datetime (YYYYMMDDHHMMSS.ffffff)

        Returns:
            Shifted datetime string
        """
        if not datetime_str or not self._offset:
            return datetime_str

        try:
            # Handle fractional seconds
            if "." in datetime_str:
                dt_part, frac = datetime_str.split(".")
            else:
                dt_part, frac = datetime_str, None

            original = datetime.strptime(dt_part[:14], self.DATETIME_FORMAT)
            shifted = original + self._offset

            result = shifted.strftime(self.DATETIME_FORMAT)
            if frac:
                result += f".{frac}"
            return result
        except ValueError:
            return datetime_str

    @staticmethod
    def calculate_safe_harbor_age(
        birth_date: datetime,
        reference_date: datetime,
    ) -> str:
        """
        Calculate age with HIPAA Safe Harbor constraints (>89 becomes 90+).

        Args:
            birth_date: Patient birth date
            reference_date: Study/reference date

        Returns:
            Age string (e.g., "045Y" or "90+")
        """
        age_days = (reference_date - birth_date).days
        age_years = age_days / 365.25

        if age_years > 89:
            return "90+"
        else:
            return f"{int(age_years):03d}Y"
