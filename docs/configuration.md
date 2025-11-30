# Configuration Guide

Complete guide to configuring DICOM Anonymizer presets.

## Overview

THAKAAMED uses YAML-based configuration files called "presets" to define de-identification rules. Each preset specifies:

- Metadata (name, description, compliance standards)
- Tag handling rules (which DICOM tags to modify and how)
- Date handling strategy
- Private tag treatment

## Built-in Presets

### sfda_safe_harbor

Maximum privacy protection following HIPAA Safe Harbor guidelines.

| Setting | Value |
|---------|-------|
| Compliance | HIPAA Safe Harbor, Saudi PDPL |
| Date Handling | Remove |
| Private Tags | Remove all |
| Use Case | Data export, public sharing |

### research

Balanced privacy with longitudinal data retention.

| Setting | Value |
|---------|-------|
| Compliance | HIPAA Safe Harbor (modified) |
| Date Handling | Shift (configurable offset) |
| Private Tags | Remove all |
| Use Case | Research studies, clinical trials |

### full_anonymization

Complete de-identification with maximum tag removal.

| Setting | Value |
|---------|-------|
| Compliance | HIPAA Safe Harbor, DICOM PS3.15 |
| Date Handling | Remove |
| Private Tags | Remove all |
| Use Case | Maximum anonymization requirements |

## Preset File Structure

```yaml
# Preset metadata
name: "Custom Preset"
description: "Description of what this preset does"
version: "1.0.0"

# Compliance information
compliance:
  standards:
    - "HIPAA Safe Harbor"
    - "Saudi PDPL"

# Date handling configuration
date_handling:
  method: "shift"  # Options: remove, shift, keep
  shift_days: 365  # Only used if method is "shift"

# Private tag handling
private_tags:
  action: "remove"  # Options: remove, keep

# Tag rules - list of rules for specific DICOM tags
tag_rules:
  - tag: "(0010,0010)"  # Patient Name
    action: "replace"
    value: "ANONYMIZED"

  - tag: "(0010,0020)"  # Patient ID
    action: "hash"

  - tag: "(0010,0030)"  # Patient Birth Date
    action: "remove"
```

## Configuration Options

### Metadata Section

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Human-readable preset name |
| `description` | Yes | Detailed description |
| `version` | No | Preset version string |

### Compliance Section

| Field | Required | Description |
|-------|----------|-------------|
| `standards` | No | List of compliance standards |

### Date Handling Section

| Field | Required | Options | Description |
|-------|----------|---------|-------------|
| `method` | Yes | remove, shift, keep | How to handle dates |
| `shift_days` | If shift | Integer | Days to shift (positive or negative) |

**Date handling methods:**

- **remove**: Delete all date values (maximum privacy)
- **shift**: Shift dates by fixed offset (preserves intervals)
- **keep**: Retain original dates (minimum privacy, not recommended)

### Private Tags Section

| Field | Required | Options | Description |
|-------|----------|---------|-------------|
| `action` | Yes | remove, keep | How to handle private tags |

**Private tag handling:**

- **remove**: Delete all private (odd group) tags
- **keep**: Retain private tags (not recommended for de-identification)

### Tag Rules Section

Each rule specifies how to handle a specific DICOM tag.

| Field | Required | Description |
|-------|----------|-------------|
| `tag` | Yes | DICOM tag in (GGGG,EEEE) format |
| `action` | Yes | Action to perform |
| `value` | Conditional | Replacement value (for replace action) |

#### Action Types

| Action | Code | Description | Requires Value |
|--------|------|-------------|----------------|
| `remove` | X | Delete the tag entirely | No |
| `empty` | Z | Set to empty/zero-length | No |
| `replace` | D | Replace with specified value | Yes |
| `hash` | U | Replace with deterministic hash | No |
| `keep` | K | Keep original value | No |
| `clean` | C | Clean identifying info from text | No |

#### DICOM PS3.15 Action Codes

The action types map to DICOM PS3.15 Basic Application Level Confidentiality Profile:

- **D** (Replace): Replace with a non-zero length dummy value
- **Z** (Zero): Replace with zero length or dummy value
- **X** (Remove): Remove the attribute
- **K** (Keep): Keep the original value (use with caution)
- **C** (Clean): Clean identifying information from value
- **U** (UID): Replace UID with new generated UID

## Common Tag References

### Patient Identification Tags

| Tag | Name | Recommended Action |
|-----|------|-------------------|
| (0010,0010) | Patient Name | replace or empty |
| (0010,0020) | Patient ID | hash or replace |
| (0010,0030) | Patient Birth Date | remove |
| (0010,0040) | Patient Sex | keep or remove |
| (0010,1000) | Other Patient IDs | remove |
| (0010,1001) | Other Patient Names | remove |

### Study/Series Tags

| Tag | Name | Recommended Action |
|-----|------|-------------------|
| (0008,0020) | Study Date | remove or shift |
| (0008,0021) | Series Date | remove or shift |
| (0008,0030) | Study Time | remove or shift |
| (0008,0050) | Accession Number | hash or remove |
| (0008,0090) | Referring Physician | remove or replace |

### Institution Tags

| Tag | Name | Recommended Action |
|-----|------|-------------------|
| (0008,0080) | Institution Name | remove |
| (0008,0081) | Institution Address | remove |
| (0008,1010) | Station Name | remove or hash |
| (0008,1040) | Institutional Department | remove |

### UID Tags (Always Remapped)

| Tag | Name | Action |
|-----|------|--------|
| (0020,000D) | Study Instance UID | hash (automatic) |
| (0020,000E) | Series Instance UID | hash (automatic) |
| (0008,0018) | SOP Instance UID | hash (automatic) |

## Custom Preset Example

Create a custom preset for your organization:

```yaml
# hospital_research.yaml
name: "Hospital Research Preset"
description: "Custom preset for internal research studies"
version: "1.0.0"

compliance:
  standards:
    - "HIPAA Safe Harbor"
    - "IRB Protocol #12345"

date_handling:
  method: "shift"
  shift_days: 180

private_tags:
  action: "remove"

tag_rules:
  # Patient identification
  - tag: "(0010,0010)"
    action: "replace"
    value: "RESEARCH_SUBJECT"

  - tag: "(0010,0020)"
    action: "hash"

  - tag: "(0010,0030)"
    action: "remove"

  - tag: "(0010,0040)"
    action: "keep"  # Keep sex for research

  # Remove contact information
  - tag: "(0010,2154)"  # Patient Telephone
    action: "remove"

  - tag: "(0010,2160)"  # Ethnic Group
    action: "remove"

  # Institution - keep department for study tracking
  - tag: "(0008,0080)"
    action: "replace"
    value: "RESEARCH_INSTITUTION"

  - tag: "(0008,1040)"
    action: "keep"  # Keep department

  # Remove physician names
  - tag: "(0008,0090)"
    action: "remove"

  - tag: "(0008,1050)"
    action: "remove"
```

## Using Custom Presets

```bash
# Use custom preset file
dicom-anonym anonymize \
    -i /data/input \
    -o /data/output \
    -p ./hospital_research.yaml

# Validate before use
dicom-anonym validate --config ./hospital_research.yaml
```

## Best Practices

### 1. Start with Built-in Presets

Use built-in presets as templates:

```bash
# View a preset
cat $(python -c "import dicom_anonymizer; print(dicom_anonymizer.__path__[0])")/presets/sfda_safe_harbor.yaml
```

### 2. Validate Before Production

Always validate custom presets:

```bash
dicom-anonym validate --config ./my_preset.yaml
```

### 3. Test with Dry Run

Preview changes before actual processing:

```bash
dicom-anonym anonymize \
    -i ./test_file.dcm \
    -o ./output \
    -p ./my_preset.yaml \
    --dry-run
```

### 4. Document Your Presets

Include comments in YAML:

```yaml
# Approved by IRB on 2024-01-15
# Contact: privacy@hospital.org
name: "IRB Approved Research"
# ...
```

### 5. Version Control Presets

Store presets in version control for audit trail.

## Troubleshooting

### Invalid Tag Format

```
Error: Invalid tag format "(0010, 0010)"
```

Fix: Remove spaces in tag: `(0010,0010)`

### Unknown Action

```
Error: Unknown action "delete"
```

Fix: Use valid action: `remove`, `empty`, `replace`, `hash`, `keep`, `clean`

### Missing Required Value

```
Error: Action "replace" requires "value" field
```

Fix: Add value field for replace actions:

```yaml
- tag: "(0010,0010)"
  action: "replace"
  value: "ANONYMIZED"  # Add this
```

---

Next: [Compliance Documentation](compliance.md) | [API Reference](api-reference.md)
