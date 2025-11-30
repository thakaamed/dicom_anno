"""Tests for action handlers."""

from pydicom import Dataset

from dicom_anonymizer.config.models import ActionCode, TagRule
from dicom_anonymizer.engine.actions import (
    ActionFactory,
    CleanAction,
    DummyAction,
    KeepAction,
    RemoveAction,
    UIDReplaceAction,
    ZeroAction,
)
from dicom_anonymizer.engine.uid_mapper import UIDMapper


class TestDummyAction:
    """Tests for DummyAction (D)."""

    def test_replace_with_dummy(self):
        """Replaces value with dummy."""
        ds = Dataset()
        ds.PatientName = "Original Name"

        action = DummyAction()
        rule = TagRule(tag="(0010,0010)", action=ActionCode.D)

        result = action.apply(ds, "(0010,0010)", rule)

        assert result is True
        assert ds.PatientName == "ANONYMIZED"

    def test_replace_with_custom_value(self):
        """Uses custom replacement if provided."""
        ds = Dataset()
        ds.PatientName = "Original Name"

        action = DummyAction()
        rule = TagRule(tag="(0010,0010)", action=ActionCode.D, replacement="CUSTOM")

        action.apply(ds, "(0010,0010)", rule)

        assert ds.PatientName == "CUSTOM"

    def test_missing_tag_returns_false(self):
        """Returns False if tag doesn't exist."""
        ds = Dataset()

        action = DummyAction()
        rule = TagRule(tag="(0010,0010)", action=ActionCode.D)

        result = action.apply(ds, "(0010,0010)", rule)

        assert result is False


class TestZeroAction:
    """Tests for ZeroAction (Z)."""

    def test_replace_with_empty(self):
        """Replaces value with empty string."""
        ds = Dataset()
        ds.PatientID = "12345"

        action = ZeroAction()
        rule = TagRule(tag="(0010,0020)", action=ActionCode.Z)

        result = action.apply(ds, "(0010,0020)", rule)

        assert result is True
        assert ds.PatientID == ""

    def test_replace_with_custom_value(self):
        """Uses custom replacement if provided."""
        ds = Dataset()
        ds.PatientID = "12345"

        action = ZeroAction()
        rule = TagRule(tag="(0010,0020)", action=ActionCode.Z, replacement="ANON")

        action.apply(ds, "(0010,0020)", rule)

        assert ds.PatientID == "ANON"


class TestRemoveAction:
    """Tests for RemoveAction (X)."""

    def test_remove_tag(self):
        """Removes tag from dataset."""
        ds = Dataset()
        ds.PatientBirthDate = "19800115"

        action = RemoveAction()
        rule = TagRule(tag="(0010,0030)", action=ActionCode.X)

        result = action.apply(ds, "(0010,0030)", rule)

        assert result is True
        assert not hasattr(ds, "PatientBirthDate")
        assert (0x0010, 0x0030) not in ds

    def test_remove_missing_tag(self):
        """Returns False if tag doesn't exist."""
        ds = Dataset()

        action = RemoveAction()
        rule = TagRule(tag="(0010,0030)", action=ActionCode.X)

        result = action.apply(ds, "(0010,0030)", rule)

        assert result is False


class TestKeepAction:
    """Tests for KeepAction (K)."""

    def test_keep_unchanged(self):
        """Keep action returns False (no modification)."""
        ds = Dataset()
        ds.PatientSex = "M"

        action = KeepAction()
        rule = TagRule(tag="(0010,0040)", action=ActionCode.K)

        result = action.apply(ds, "(0010,0040)", rule)

        assert result is False
        assert ds.PatientSex == "M"


class TestCleanAction:
    """Tests for CleanAction (C)."""

    def test_clean_with_replacement(self):
        """Uses custom replacement if provided."""
        ds = Dataset()
        ds.PatientName = "Original Name"

        action = CleanAction()
        rule = TagRule(tag="(0010,0010)", action=ActionCode.C, replacement="CLEANED")

        result = action.apply(ds, "(0010,0010)", rule)

        assert result is True
        assert ds.PatientName == "CLEANED"


class TestUIDReplaceAction:
    """Tests for UIDReplaceAction (U)."""

    def test_replace_uid(self):
        """Replaces UID with new consistent UID."""
        ds = Dataset()
        ds.StudyInstanceUID = "1.2.3.4.5"

        mapper = UIDMapper(salt="test")
        action = UIDReplaceAction(mapper)
        rule = TagRule(tag="(0020,000D)", action=ActionCode.U)

        result = action.apply(ds, "(0020,000D)", rule)

        assert result is True
        assert ds.StudyInstanceUID != "1.2.3.4.5"
        assert ds.StudyInstanceUID.startswith("2.25.")

    def test_consistent_uid_mapping(self):
        """Same original UID maps to same new UID."""
        mapper = UIDMapper(salt="test")
        action = UIDReplaceAction(mapper)
        rule = TagRule(tag="(0020,000D)", action=ActionCode.U)

        ds1 = Dataset()
        ds1.StudyInstanceUID = "1.2.3.4.5"
        action.apply(ds1, "(0020,000D)", rule)

        ds2 = Dataset()
        ds2.StudyInstanceUID = "1.2.3.4.5"
        action.apply(ds2, "(0020,000D)", rule)

        assert ds1.StudyInstanceUID == ds2.StudyInstanceUID


class TestActionFactory:
    """Tests for ActionFactory."""

    def test_all_action_codes_available(self):
        """Factory returns handler for all action codes."""
        mapper = UIDMapper()
        factory = ActionFactory(mapper)

        for code in ActionCode:
            handler = factory.get_handler(code)
            assert handler is not None

    def test_uid_action_uses_shared_mapper(self):
        """UID action uses the shared mapper."""
        mapper = UIDMapper(salt="test")
        factory = ActionFactory(mapper)

        handler = factory.get_handler(ActionCode.U)

        # Process a UID
        ds = Dataset()
        ds.StudyInstanceUID = "1.2.3.4.5"
        rule = TagRule(tag="(0020,000D)", action=ActionCode.U)
        handler.apply(ds, "(0020,000D)", rule)

        # Mapper should have the mapping
        assert len(mapper) == 1
