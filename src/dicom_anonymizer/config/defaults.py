# SPDX-License-Identifier: MIT
# Copyright (c) 2024 THAKAAMED AI
"""Default configuration values."""

# Default output directory
DEFAULT_OUTPUT_DIR = "./output"

# Default report formats
DEFAULT_REPORT_FORMAT = "pdf"

# Default preset
DEFAULT_PRESET = "sfda_safe_harbor"

# Default parallel workers
DEFAULT_WORKERS = 4

# DICOM PS3.15 Basic Profile tags that should always be handled
BASIC_PROFILE_TAGS = [
    # Patient Module
    "(0010,0010)",  # Patient's Name
    "(0010,0020)",  # Patient ID
    "(0010,0030)",  # Patient's Birth Date
    "(0010,0032)",  # Patient's Birth Time
    "(0010,0040)",  # Patient's Sex
    "(0010,1000)",  # Other Patient IDs
    "(0010,1001)",  # Other Patient Names
    "(0010,1010)",  # Patient's Age
    "(0010,1040)",  # Patient's Address
    "(0010,2154)",  # Patient's Telephone Numbers
    # Study Module
    "(0008,0020)",  # Study Date
    "(0008,0021)",  # Series Date
    "(0008,0030)",  # Study Time
    "(0008,0050)",  # Accession Number
    "(0008,0080)",  # Institution Name
    "(0008,0081)",  # Institution Address
    "(0008,0090)",  # Referring Physician's Name
    "(0008,1048)",  # Physician(s) of Record
    "(0008,1050)",  # Performing Physician's Name
    "(0008,1070)",  # Operators' Name
    # Instance UIDs
    "(0020,000D)",  # Study Instance UID
    "(0020,000E)",  # Series Instance UID
    "(0008,0018)",  # SOP Instance UID
    # Descriptive Fields
    "(0008,103E)",  # Series Description
    "(0008,1030)",  # Study Description
]

# HIPAA Safe Harbor identifiers (18 categories)
HIPAA_IDENTIFIERS = [
    "Names",
    "Geographic subdivisions smaller than state",
    "Dates (except year)",
    "Telephone numbers",
    "Fax numbers",
    "Email addresses",
    "Social Security numbers",
    "Medical record numbers",
    "Health plan beneficiary numbers",
    "Account numbers",
    "Certificate/license numbers",
    "Vehicle identifiers",
    "Device identifiers",
    "Web URLs",
    "IP addresses",
    "Biometric identifiers",
    "Full-face photographs",
    "Unique identifying characteristics",
]
