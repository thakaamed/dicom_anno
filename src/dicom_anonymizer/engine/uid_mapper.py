# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Consistent UID remapping for DICOM anonymization."""

import hashlib
import threading
import uuid


class UIDMapper:
    """Consistent UID remapping using deterministic hashing."""

    UID_ROOT = "2.25"  # Standard UUID-based UID root

    def __init__(self, salt: str | None = None):
        """
        Initialize UID mapper with optional salt.

        Args:
            salt: Secret salt for hash generation. If None, uses random UUID.
        """
        self.salt = salt or str(uuid.uuid4())
        self._mapping: dict[str, str] = {}
        self._lock = threading.Lock()

    def get_or_create(self, original_uid: str) -> str:
        """
        Get existing mapping or create new one.

        Args:
            original_uid: Original DICOM UID

        Returns:
            Consistently mapped new UID
        """
        with self._lock:
            if original_uid not in self._mapping:
                self._mapping[original_uid] = self._generate_uid(original_uid)
            return self._mapping[original_uid]

    def _generate_uid(self, original_uid: str) -> str:
        """Generate deterministic UID from original."""
        hash_input = f"{original_uid}{self.salt}".encode()
        hash_bytes = hashlib.sha256(hash_input).digest()

        # Use first 16 bytes as UUID integer
        uid_int = int.from_bytes(hash_bytes[:16], "big")

        # Format as DICOM UID with 2.25 root
        new_uid = f"{self.UID_ROOT}.{uid_int}"

        # DICOM UIDs max 64 chars
        if len(new_uid) > 64:
            new_uid = new_uid[:64]

        return new_uid

    def clear(self) -> None:
        """Clear all mappings (for new batch)."""
        with self._lock:
            self._mapping.clear()

    def export_mapping(self) -> dict[str, str]:
        """Export current mappings for audit trail."""
        with self._lock:
            return dict(self._mapping)

    def __len__(self) -> int:
        """Return number of mapped UIDs."""
        return len(self._mapping)
