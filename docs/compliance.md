# Compliance Documentation

Detailed compliance information for THAKAAMED DICOM Anonymizer.

## Overview

THAKAAMED DICOM Anonymizer is designed to meet the requirements of multiple healthcare data protection standards:

- **DICOM PS3.15**: Basic Application Level Confidentiality Profile
- **HIPAA Safe Harbor**: US healthcare privacy de-identification method
- **Saudi PDPL**: Saudi Arabia Personal Data Protection Law

## DICOM PS3.15 Compliance

### Basic Application Level Confidentiality Profile

THAKAAMED implements the Basic Profile from DICOM Part 15, Appendix E.

#### Profile Requirements

| Requirement | Implementation |
|-------------|----------------|
| De-identification markers | PatientIdentityRemoved = "YES" |
| Method documentation | DeidentificationMethod populated |
| UID replacement | Deterministic SHA-256 based remapping |
| Private tag removal | All private tags removed by default |

#### Attribute Actions

The Basic Profile defines actions for each attribute:

| Code | Name | THAKAAMED Implementation |
|------|------|--------------------------|
| D | Replace | Replace with configured dummy value |
| Z | Zero | Set to empty/zero-length value |
| X | Remove | Delete attribute from dataset |
| K | Keep | Retain original value |
| C | Clean | Remove identifying substrings |
| U | UID | Generate new UID with 2.25 root |

#### Required De-identification Markers

After processing, all files include:

```
(0012,0062) PatientIdentityRemoved: YES
(0012,0063) DeidentificationMethod: THAKAAMED - [Preset Name]
```

### UID Generation

THAKAAMED generates replacement UIDs using:

1. **Root**: `2.25` (UUID-derived OID arc)
2. **Algorithm**: SHA-256 hash of original UID
3. **Format**: Deterministic mapping for consistency
4. **Length**: Maximum 64 characters per DICOM standard

Example:
```
Original:  1.2.840.113619.2.278.3.123456
Remapped:  2.25.123456789012345678901234567890123456
```

### Cross-File Consistency

UIDs are remapped consistently across files:
- Same original UID always maps to same new UID
- Referential integrity maintained within studies
- Series relationships preserved

## HIPAA Safe Harbor Compliance

### 45 CFR 164.514(b)(2) - Safe Harbor Method

HIPAA Safe Harbor requires removal of 18 categories of identifiers.

#### 18 Identifier Categories

| # | Identifier | THAKAAMED Handling |
|---|------------|-------------------|
| 1 | Names | Removed or replaced with "ANONYMIZED" |
| 2 | Geographic data | All addresses removed |
| 3 | Dates (except year) | Removed or shifted |
| 4 | Phone numbers | Removed |
| 5 | Fax numbers | Removed |
| 6 | Email addresses | Removed |
| 7 | Social Security numbers | Removed |
| 8 | Medical record numbers | Hashed or replaced |
| 9 | Health plan beneficiary numbers | Removed |
| 10 | Account numbers | Removed |
| 11 | Certificate/license numbers | Removed |
| 12 | Vehicle identifiers | Removed |
| 13 | Device identifiers | Removed or kept per config |
| 14 | Web URLs | Removed |
| 15 | IP addresses | Removed |
| 16 | Biometric identifiers | N/A for DICOM |
| 17 | Full-face photographs | Handled in pixel data |
| 18 | Unique identifying numbers | Hashed |

#### DICOM Tag Mapping

| HIPAA Identifier | DICOM Tags |
|-----------------|------------|
| Names | (0010,0010), (0008,0090), (0008,1050) |
| Dates | (0010,0030), (0008,0020), (0008,0021) |
| Phone numbers | (0010,2154) |
| Medical record # | (0010,0020) |
| Device identifiers | (0018,1000), (0018,1002) |

### Safe Harbor Attestation

When using `sfda_safe_harbor` preset, the system:

1. Removes all 18 identifier categories from DICOM tags
2. Removes all private tags (may contain PHI)
3. Sets de-identification markers
4. Generates audit report for compliance review

## Saudi PDPL Compliance

### Personal Data Protection Law Requirements

The Saudi PDPL (Royal Decree M/19, 2021) establishes requirements for personal data processing.

#### Key Requirements

| Requirement | THAKAAMED Implementation |
|-------------|--------------------------|
| Data minimization | Removes unnecessary identifiers |
| Purpose limitation | Preset-based processing for specific uses |
| Accuracy | Deterministic, reproducible processing |
| Security | SHA-256 hashing for UIDs |
| Accountability | Comprehensive audit reports |

#### PDPL Article Compliance

| Article | Requirement | Implementation |
|---------|-------------|----------------|
| Art. 10 | Consent for processing | Tool enables anonymization for lawful processing |
| Art. 12 | Data minimization | Presets remove non-essential data |
| Art. 14 | Security measures | Cryptographic hashing, audit trails |
| Art. 22 | Cross-border transfer | Anonymization enables compliant transfer |

### Saudi Healthcare Context

THAKAAMED is designed for Saudi Vision 2030 healthcare transformation:

- **Ministry of Health (MOH)** data sharing requirements
- **Saudi FDA (SFDA)** medical device data regulations
- **National Health Information Center** interoperability standards

## Audit Trail

### Report Contents

Every anonymization run generates comprehensive audit reports:

#### JSON Report

```json
{
  "report_id": "unique-identifier",
  "generated_at": "2024-01-15T14:30:00Z",
  "generator_version": "1.0.0",
  "preset_name": "SFDA Safe Harbor",
  "compliance_standards": ["HIPAA Safe Harbor", "Saudi PDPL"],
  "files_processed": 150,
  "files_successful": 150,
  "files_failed": 0,
  "total_tags_modified": 4250,
  "total_tags_removed": 1890,
  "total_uids_remapped": 165,
  "uid_mapping": {
    "1.2.3.original": "2.25.remapped"
  },
  "file_records": [...]
}
```

#### PDF Report

Professional formatted report including:

- Executive summary
- Processing statistics
- Compliance attestation
- File-by-file details
- UID mapping reference

#### CSV Report

Spreadsheet format for data analysis:

| Column | Description |
|--------|-------------|
| original_path | Source file path |
| output_path | Anonymized file path |
| success | Processing success status |
| tags_modified | Number of tags changed |
| tags_removed | Number of tags deleted |
| study_uid_original | Original Study UID |
| study_uid_new | Remapped Study UID |

### Retention Recommendations

| Report Type | Retention Period | Purpose |
|------------|------------------|---------|
| PDF | 7 years | Regulatory compliance |
| JSON | 7 years | Audit trail |
| CSV | As needed | Analysis |

## Compliance Checklist

### Pre-Processing

- [ ] Select appropriate preset for use case
- [ ] Validate preset configuration
- [ ] Verify input data inventory
- [ ] Document processing purpose

### Processing

- [ ] Use dry-run to preview changes
- [ ] Process with selected preset
- [ ] Verify no errors in output

### Post-Processing

- [ ] Review audit reports
- [ ] Verify de-identification markers present
- [ ] Archive reports per retention policy
- [ ] Document data disposition

## Compliance Validation

### Automated Validation

THAKAAMED includes built-in compliance tests:

```bash
# Run compliance test suite
pytest tests/test_compliance/ -v
```

Tests verify:
- All HIPAA identifiers removed
- DICOM PS3.15 markers present
- UID format compliance
- Private tag removal

### Manual Verification

For regulatory audits, verify using DICOM viewer:

1. Open anonymized file in viewer
2. Check Patient Name = "ANONYMIZED" or empty
3. Check PatientIdentityRemoved = "YES"
4. Verify UIDs start with "2.25."
5. Confirm no private tags present

## Limitations

### What THAKAAMED Does NOT Handle

| Item | Reason |
|------|--------|
| Burned-in pixel annotations | Requires specialized de-facing |
| Secondary capture screenshots | May contain visible PHI |
| Structured reports with text | May require manual review |
| Custom private tag semantics | Cannot interpret vendor data |

### Recommendations

For complete de-identification:

1. Use THAKAAMED for DICOM tag anonymization
2. Review images for burned-in PHI
3. Apply pixel de-identification tools if needed
4. Conduct final quality review

## References

### Standards Documents

- [DICOM PS3.15 Security Profiles](https://dicom.nema.org/medical/dicom/current/output/chtml/part15/chapter_E.html)
- [HIPAA De-identification Guidance](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)
- [Saudi PDPL Official Text](https://sdaia.gov.sa/en/PDPL)

### Regulatory Bodies

- **DICOM Standards Committee**: Standards development
- **US HHS OCR**: HIPAA enforcement
- **Saudi NDMO**: PDPL oversight
- **Saudi FDA (SFDA)**: Medical device regulation

---

Next: [API Reference](api-reference.md) | [Examples](examples/)
