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
"""Action handlers for DICOM PS3.15 de-identification action codes."""

from abc import ABC, abstractmethod

from pydicom import Dataset

from thakaamed_dicom.config.models import ActionCode, TagRule
from thakaamed_dicom.engine.uid_mapper import UIDMapper


class ActionHandler(ABC):
    """Abstract base class for action handlers."""

    @abstractmethod
    def apply(self, ds: Dataset, tag: str, rule: TagRule) -> bool:
        """
        Apply action to dataset.

        Args:
            ds: DICOM dataset
            tag: Tag string e.g., "(0010,0010)"
            rule: TagRule with action and replacement

        Returns:
            True if tag was modified/removed, False otherwise
        """

    @staticmethod
    def parse_tag(tag_str: str) -> tuple[int, int]:
        """Parse tag string to pydicom-compatible format."""
        # "(0010,0010)" -> (0x0010, 0x0010)
        clean = tag_str.strip("()")
        group, elem = clean.split(",")
        return (int(group, 16), int(elem, 16))


class DummyAction(ActionHandler):
    """D - Replace with non-zero length dummy value."""

    DUMMY_VALUES = {
        "PN": "ANONYMIZED",  # Person Name
        "LO": "ANONYMIZED",  # Long String
        "SH": "ANON",  # Short String
        "DA": "19000101",  # Date
        "TM": "000000",  # Time
        "DT": "19000101000000",  # DateTime
        "AS": "000Y",  # Age String
        "DS": "0",  # Decimal String
        "IS": "0",  # Integer String
        "UI": "0.0.0.0",  # UID (placeholder)
    }

    def apply(self, ds: Dataset, tag: str, rule: TagRule) -> bool:
        """Apply dummy value replacement."""
        tag_tuple = self.parse_tag(tag)

        if tag_tuple not in ds:
            return False

        elem = ds[tag_tuple]
        vr = elem.VR

        # Use rule replacement if provided, else default dummy
        if rule.replacement:
            elem.value = rule.replacement
        else:
            elem.value = self.DUMMY_VALUES.get(vr, "ANONYMIZED")

        return True


class ZeroAction(ActionHandler):
    """Z - Replace with zero length or dummy value."""

    def apply(self, ds: Dataset, tag: str, rule: TagRule) -> bool:
        """Apply zero/empty value replacement."""
        tag_tuple = self.parse_tag(tag)

        if tag_tuple not in ds:
            return False

        elem = ds[tag_tuple]

        # Use rule replacement if provided, else empty
        if rule.replacement:
            elem.value = rule.replacement
        else:
            elem.value = ""

        return True


class RemoveAction(ActionHandler):
    """X - Remove attribute completely."""

    def apply(self, ds: Dataset, tag: str, rule: TagRule) -> bool:
        """Remove the tag from dataset."""
        tag_tuple = self.parse_tag(tag)

        if tag_tuple not in ds:
            return False

        del ds[tag_tuple]
        return True


class KeepAction(ActionHandler):
    """K - Keep unchanged (recursive for sequences)."""

    def apply(self, ds: Dataset, tag: str, rule: TagRule) -> bool:
        """Keep action - no modification needed."""
        # K action means keep - no modification needed
        return False


class CleanAction(ActionHandler):
    """C - Replace with similar but non-identifying value."""

    def apply(self, ds: Dataset, tag: str, rule: TagRule) -> bool:
        """Clean and replace with non-identifying value."""
        tag_tuple = self.parse_tag(tag)

        if tag_tuple not in ds:
            return False

        # Use replacement if provided
        if rule.replacement:
            ds[tag_tuple].value = rule.replacement
            return True

        # Default: keep structure but replace identifying parts
        elem = ds[tag_tuple]
        if elem.VR == "PN":
            elem.value = "ANONYMIZED"
        elif elem.VR in ("LO", "SH", "LT", "ST", "UT"):
            # Keep generic description, remove specifics
            elem.value = "Cleaned"

        return True


class UIDReplaceAction(ActionHandler):
    """U - Replace with new consistent UID."""

    def __init__(self, uid_mapper: UIDMapper):
        """
        Initialize with UID mapper.

        Args:
            uid_mapper: UIDMapper instance for consistent mapping
        """
        self.uid_mapper = uid_mapper

    def apply(self, ds: Dataset, tag: str, rule: TagRule) -> bool:
        """Replace UID with consistently mapped new UID."""
        tag_tuple = self.parse_tag(tag)

        if tag_tuple not in ds:
            return False

        original_uid = str(ds[tag_tuple].value)
        new_uid = self.uid_mapper.get_or_create(original_uid)
        ds[tag_tuple].value = new_uid

        return True


class ActionFactory:
    """Factory for creating action handlers."""

    def __init__(self, uid_mapper: UIDMapper):
        """
        Initialize factory with UID mapper.

        Args:
            uid_mapper: UIDMapper instance for UID replacement actions
        """
        self.uid_mapper = uid_mapper
        self._handlers: dict[ActionCode, ActionHandler] = {
            ActionCode.D: DummyAction(),
            ActionCode.Z: ZeroAction(),
            ActionCode.X: RemoveAction(),
            ActionCode.K: KeepAction(),
            ActionCode.C: CleanAction(),
            ActionCode.U: UIDReplaceAction(uid_mapper),
        }

    def get_handler(self, action: ActionCode) -> ActionHandler:
        """Get handler for action code."""
        return self._handlers[action]
