# DICOM Files Directory

**Place your DICOM files here for anonymization.**

## Quick Start

1. Copy/move your DICOM files (`.dcm`) into this folder
2. Run the anonymization command:

```bash
# SFDA Safe Harbor (Maximum Privacy)
thakaamed-dicom anonymize -i ./dicom_files/ -o ./anonymized_output/ -p sfda_safe_harbor

# Research (Date Shifting)
thakaamed-dicom anonymize -i ./dicom_files/ -o ./anonymized_output/ -p research --date-anchor 20200101

# Full Anonymization
thakaamed-dicom anonymize -i ./dicom_files/ -o ./anonymized_output/ -p full_anonymization
```

3. Find your anonymized files in `./anonymized_output/`
4. Reports will be in `./anonymized_output/reports/`

## Notes

- This directory is git-ignored (your DICOM files won't be committed)
- Subdirectories are supported (recursive scanning)
- Supports `.dcm` and `.dicom` file extensions

---

**THAKAAMED AI** | https://thakaamed.ai

