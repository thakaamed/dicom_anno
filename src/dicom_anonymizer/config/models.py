# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Pydantic models for configuration validation."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator


class ActionCode(str, Enum):
    """DICOM PS3.15 de-identification action codes."""

    D = "D"  # Dummy - replace with non-zero dummy value
    Z = "Z"  # Zero/Dummy - replace with zero length or dummy
    X = "X"  # Remove - completely remove attribute
    K = "K"  # Keep - keep unchanged
    C = "C"  # Clean - replace with similar non-identifying value
    U = "U"  # UID Replace - replace with new consistent UID


class DateHandling(str, Enum):
    """Date handling strategy."""

    REMOVE = "remove"  # Remove all dates (Safe Harbor)
    SHIFT = "shift"  # Shift dates by offset
    KEEP_YEAR = "keep_year"  # Keep year only


class TagRule(BaseModel):
    """Rule for handling a specific DICOM tag."""

    tag: str = Field(..., pattern=r"^\([0-9A-Fa-f]{4},[0-9A-Fa-f]{4}\)$")
    action: ActionCode
    replacement: str | None = None
    description: str | None = None


class PresetConfig(BaseModel):
    """Complete anonymization preset configuration."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str
    version: str = Field(default="1.0.0", pattern=r"^\d+\.\d+\.\d+$")

    # Compliance info
    compliance: list[str] = Field(default_factory=list)

    # Profile options (from DICOM PS3.15)
    clean_pixel_data: bool = Field(default=False)
    clean_visual_features: bool = Field(default=False)
    retain_longitudinal: bool = Field(default=False)
    retain_patient_characteristics: bool = Field(default=False)
    retain_device_identity: bool = Field(default=False)
    retain_institution_identity: bool = Field(default=False)
    retain_safe_private: bool = Field(default=False)

    # Date handling
    date_handling: DateHandling = DateHandling.REMOVE
    date_shift_base: str | None = None  # Format: YYYYMMDD

    # Age handling
    age_threshold: int = Field(default=89, ge=0, le=120)

    # Tag-specific rules
    tag_rules: list[TagRule] = Field(default_factory=list)

    # Private tag handling
    remove_private_tags: bool = Field(default=True)
    safe_private_tags: list[str] = Field(default_factory=list)

    @field_validator("date_shift_base")
    @classmethod
    def validate_date_format(cls, v: str | None) -> str | None:
        """Validate date_shift_base is in YYYYMMDD format."""
        if v is not None:
            try:
                datetime.strptime(v, "%Y%m%d")
            except ValueError as err:
                raise ValueError("date_shift_base must be in YYYYMMDD format") from err
        return v

    @model_validator(mode="after")
    def validate_longitudinal_date(self) -> "PresetConfig":
        """Validate that longitudinal data retention is compatible with date handling."""
        if self.retain_longitudinal and self.date_handling == DateHandling.REMOVE:
            raise ValueError("Cannot retain longitudinal data when dates are removed")
        return self


class AppConfig(BaseModel):
    """Application-level configuration."""

    default_preset: str = Field(default="sfda_safe_harbor")
    output_format: Literal["pdf", "json", "csv", "all"] = Field(default="pdf")
    output_directory: str = Field(default="./output")
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(default="INFO")
    parallel_workers: int = Field(default=4, ge=1, le=32)
