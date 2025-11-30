# CLI Reference

Complete command-line interface documentation for DICOM Anonymizer.

## Global Options

All commands support these global options:

```bash
dicom-anonym [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
|--------|-------------|
| `--help` | Show help message and exit |
| `--version` | Show version and exit |

## Commands

### anonymize

De-identify DICOM files using a specified preset.

```bash
dicom-anonym anonymize [OPTIONS]
```

#### Required Options

| Option | Short | Description |
|--------|-------|-------------|
| `--input PATH` | `-i` | Input DICOM file or directory |
| `--output PATH` | `-o` | Output file or directory |
| `--preset NAME` | `-p` | Preset name or path to YAML config |

#### Optional Options

| Option | Default | Description |
|--------|---------|-------------|
| `--date-anchor DATE` | None | Anchor date for shifting (YYYYMMDD format) |
| `--dry-run` / `-n` | False | Preview changes without writing files |
| `--parallel` / `--no-parallel` | True | Enable/disable parallel processing |
| `--workers N` / `-w` | 4 | Number of parallel workers |
| `--report-format FORMAT` | all | Report format: pdf, json, csv, all, none |
| `--no-reports` | False | Disable report generation entirely |
| `--report-dir PATH` | output/reports | Directory for generated reports |

#### Examples

**Basic anonymization:**

```bash
dicom-anonym anonymize \
    --input /path/to/dicom/study \
    --output /path/to/anonymized \
    --preset sfda_safe_harbor
```

**Single file:**

```bash
dicom-anonym anonymize \
    -i ./scan.dcm \
    -o ./anonymized_scan.dcm \
    -p sfda_safe_harbor
```

**With date shifting:**

```bash
dicom-anonym anonymize \
    -i /data/study \
    -o /data/output \
    -p research \
    --date-anchor 20200101
```

**Dry run (preview):**

```bash
dicom-anonym anonymize \
    -i /data/study \
    -o /data/output \
    -p sfda_safe_harbor \
    --dry-run
```

**Custom worker count:**

```bash
dicom-anonym anonymize \
    -i /data/large_study \
    -o /data/output \
    -p sfda_safe_harbor \
    --workers 8
```

**JSON reports only:**

```bash
dicom-anonym anonymize \
    -i /data/study \
    -o /data/output \
    -p sfda_safe_harbor \
    --report-format json
```

**No reports:**

```bash
dicom-anonym anonymize \
    -i /data/study \
    -o /data/output \
    -p sfda_safe_harbor \
    --no-reports
```

**Custom preset file:**

```bash
dicom-anonym anonymize \
    -i /data/study \
    -o /data/output \
    -p ./my_custom_preset.yaml
```

---

### presets

List all available built-in presets.

```bash
dicom-anonym presets
```

#### Output

```
Available Presets
+-----------------------+------------------------------------------+
| Name                  | Description                              |
+-----------------------+------------------------------------------+
| sfda_safe_harbor      | SFDA Safe Harbor - Maximum privacy       |
| research              | Research - Retains longitudinal data     |
| full_anonymization    | Full Anonymization - Complete removal    |
+-----------------------+------------------------------------------+
```

---

### validate

Validate a preset configuration file.

```bash
dicom-anonym validate [OPTIONS]
```

#### Options

| Option | Description |
|--------|-------------|
| `--preset NAME` | Built-in preset name to validate |
| `--config PATH` | Path to custom YAML config to validate |

#### Examples

**Validate built-in preset:**

```bash
dicom-anonym validate --preset sfda_safe_harbor
```

**Validate custom config:**

```bash
dicom-anonym validate --config ./custom_preset.yaml
```

#### Output

```
Validation Results
+-----------------+--------+
| Check           | Status |
+-----------------+--------+
| YAML Syntax     | PASS   |
| Schema Valid    | PASS   |
| Tags Valid      | PASS   |
| Actions Valid   | PASS   |
+-----------------+--------+

Configuration is valid!
```

---

### report

Generate reports from existing JSON audit data.

```bash
dicom-anonym report [OPTIONS]
```

#### Required Options

| Option | Description |
|--------|-------------|
| `--from-json PATH` | Path to JSON audit file from previous run |

#### Optional Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--output PATH` | `-o` | Same as input | Output directory for reports |
| `--format FORMAT` | | pdf | Output format: pdf, json, csv, all |

#### Examples

**Generate PDF from JSON audit:**

```bash
dicom-anonym report \
    --from-json ./reports/audit_20240115.json \
    --format pdf
```

**Generate all formats:**

```bash
dicom-anonym report \
    --from-json ./reports/audit_20240115.json \
    --format all \
    -o ./new_reports
```

---

### version

Display version information.

```bash
dicom-anonym version
```

#### Output

```
DICOM Anonymizer v1.0.1
```

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Invalid arguments |
| 3 | File not found |
| 4 | Invalid configuration |
| 5 | Processing error |

## Environment Variables

| Variable | Description |
|----------|-------------|
| `THAKAAMED_CONFIG_DIR` | Custom directory for preset configurations |
| `THAKAAMED_LOG_LEVEL` | Logging level: DEBUG, INFO, WARNING, ERROR |

## Report Formats

### PDF

Professional branded reports suitable for stakeholders and compliance review.

- THAKAAMED branding with logo colors
- Executive summary with key metrics
- Detailed file-by-file breakdown
- Compliance attestation section

### JSON

Machine-readable format for integration with other systems.

```json
{
  "report_id": "abc123",
  "generated_at": "2024-01-15T14:30:00Z",
  "preset_name": "SFDA Safe Harbor",
  "files_processed": 150,
  "files_successful": 150,
  "total_tags_modified": 4250,
  "file_records": [...]
}
```

### CSV

Spreadsheet-compatible format for data analysis.

- UTF-8 with BOM for Excel compatibility
- One row per processed file
- Includes all metrics and UID mappings

---

## Shell Completion

### Bash

Add to `~/.bashrc`:

```bash
eval "$(_DICOM_ANONYM_COMPLETE=bash_source dicom-anonym)"
```

### Zsh

Add to `~/.zshrc`:

```bash
eval "$(_DICOM_ANONYM_COMPLETE=zsh_source dicom-anonym)"
```

### Fish

Add to `~/.config/fish/completions/dicom-anonym.fish`:

```fish
eval (env _DICOM_ANONYM_COMPLETE=fish_source dicom-anonym)
```

---

Next: [Configuration Guide](configuration.md) | [Compliance Documentation](compliance.md)
