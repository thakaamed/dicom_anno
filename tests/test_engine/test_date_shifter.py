"""Tests for DateShifter."""

from datetime import datetime

from dicom_anonymizer.engine.date_shifter import DateShifter


class TestDateShifter:
    """Tests for DateShifter class."""

    def test_shift_date_basic(self):
        """Basic date shifting works correctly."""
        # Anchor date: 2024-01-15
        # Base date: 1975-01-01 (default)
        # Offset: -17916 days (approximately 49 years)
        shifter = DateShifter(anchor_date=datetime(2024, 1, 15))

        result = shifter.shift_date("20240115")
        assert result == "19750101"

    def test_shift_date_preserves_interval(self):
        """Date intervals are preserved after shifting."""
        shifter = DateShifter(anchor_date=datetime(2024, 1, 15))

        date1 = shifter.shift_date("20240115")
        date2 = shifter.shift_date("20240215")

        # Both should be shifted by same offset
        # Original interval: 31 days
        # Shifted interval should also be 31 days
        d1 = datetime.strptime(date1, "%Y%m%d")
        d2 = datetime.strptime(date2, "%Y%m%d")

        assert (d2 - d1).days == 31

    def test_shift_date_empty_returns_empty(self):
        """Empty date string returns empty."""
        shifter = DateShifter(anchor_date=datetime(2024, 1, 15))
        assert shifter.shift_date("") == ""

    def test_shift_date_no_offset_returns_original(self):
        """Without anchor date, original is returned."""
        shifter = DateShifter()
        assert shifter.shift_date("20240115") == "20240115"

    def test_shift_datetime(self):
        """DateTime shifting works correctly."""
        shifter = DateShifter(anchor_date=datetime(2024, 1, 15))

        result = shifter.shift_datetime("20240115143022")
        assert result.startswith("1975010")  # Year changed

    def test_shift_datetime_with_fraction(self):
        """DateTime with fractional seconds is handled."""
        shifter = DateShifter(anchor_date=datetime(2024, 1, 15))

        result = shifter.shift_datetime("20240115143022.123456")
        assert ".123456" in result  # Fraction preserved

    def test_set_anchor(self):
        """set_anchor updates the offset."""
        shifter = DateShifter()

        # Initially no offset
        assert shifter.shift_date("20240115") == "20240115"

        # Set anchor
        shifter.set_anchor(datetime(2024, 1, 15))

        # Now should shift
        assert shifter.shift_date("20240115") == "19750101"

    def test_custom_base_date(self):
        """Custom base date is used."""
        shifter = DateShifter(
            base_date=datetime(2000, 1, 1),
            anchor_date=datetime(2024, 1, 15),
        )

        result = shifter.shift_date("20240115")
        assert result == "20000101"

    def test_invalid_date_returns_original(self):
        """Invalid date format returns original."""
        shifter = DateShifter(anchor_date=datetime(2024, 1, 15))

        assert shifter.shift_date("invalid") == "invalid"
        assert shifter.shift_date("2024/01/15") == "2024/01/15"

    def test_safe_harbor_age_young(self):
        """Safe harbor age calculation for young patient."""
        birth = datetime(1980, 5, 15)
        ref = datetime(2024, 1, 15)

        age = DateShifter.calculate_safe_harbor_age(birth, ref)

        assert age == "043Y"

    def test_safe_harbor_age_over_89(self):
        """Safe harbor age calculation for patient over 89."""
        birth = datetime(1930, 1, 1)
        ref = datetime(2024, 1, 15)

        age = DateShifter.calculate_safe_harbor_age(birth, ref)

        assert age == "90+"

    def test_safe_harbor_age_exactly_89(self):
        """Safe harbor age calculation for patient exactly 89."""
        birth = datetime(1934, 1, 15)  # 90 years exactly
        ref = datetime(2024, 1, 15)

        age = DateShifter.calculate_safe_harbor_age(birth, ref)

        # 90 years exactly should trigger 90+
        assert age == "90+"
