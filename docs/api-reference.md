# API Reference

Python API documentation for THAKAAMED DICOM Anonymizer.

## Overview

THAKAAMED provides a Python API for programmatic DICOM de-identification. This enables integration with custom workflows, research pipelines, and healthcare applications.

## Quick Start

```python
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor

# Load preset
preset = load_preset("sfda_safe_harbor")

# Create processor
processor = DicomProcessor(preset=preset)

# Process single file
stats = processor.process_file("input.dcm", "output.dcm")
print(f"Success: {stats.success}")
```

## Module Reference

### thakaamed_dicom.config

Configuration loading and validation.

#### load_preset

```python
from thakaamed_dicom.config.loader import load_preset

def load_preset(name_or_path: str) -> AnonymizationPreset:
    """
    Load an anonymization preset by name or file path.

    Args:
        name_or_path: Built-in preset name or path to YAML file

    Returns:
        AnonymizationPreset: Validated preset configuration

    Raises:
        PresetNotFoundError: If preset name not found
        PresetValidationError: If preset configuration invalid

    Examples:
        >>> preset = load_preset("sfda_safe_harbor")
        >>> preset = load_preset("./custom_preset.yaml")
    """
```

#### list_presets

```python
from thakaamed_dicom.config.loader import list_presets

def list_presets() -> list[PresetInfo]:
    """
    List all available built-in presets.

    Returns:
        List of PresetInfo objects with name and description

    Examples:
        >>> for preset in list_presets():
        ...     print(f"{preset.name}: {preset.description}")
    """
```

#### AnonymizationPreset

```python
from thakaamed_dicom.config.models import AnonymizationPreset

class AnonymizationPreset(BaseModel):
    """
    Anonymization preset configuration.

    Attributes:
        name: Human-readable preset name
        description: Detailed description
        version: Preset version string
        compliance: ComplianceConfig with standards list
        date_handling: DateHandlingConfig
        private_tags: PrivateTagConfig
        tag_rules: List of TagRule objects
    """

    name: str
    description: str
    version: str = "1.0.0"
    compliance: ComplianceConfig
    date_handling: DateHandlingConfig
    private_tags: PrivateTagConfig
    tag_rules: list[TagRule]
```

#### TagRule

```python
from thakaamed_dicom.config.models import TagRule, ActionType

class TagRule(BaseModel):
    """
    Rule for handling a specific DICOM tag.

    Attributes:
        tag: DICOM tag in (GGGG,EEEE) format
        action: Action to perform (ActionType enum)
        value: Replacement value (required for REPLACE action)
    """

    tag: str
    action: ActionType
    value: str | None = None

class ActionType(str, Enum):
    """De-identification action types."""
    REMOVE = "remove"      # X: Delete tag
    EMPTY = "empty"        # Z: Set to empty
    REPLACE = "replace"    # D: Replace with value
    HASH = "hash"          # U: Hash-based replacement
    KEEP = "keep"          # K: Keep original
    CLEAN = "clean"        # C: Clean identifying info
```

---

### thakaamed_dicom.engine

Core processing engine.

#### DicomProcessor

```python
from thakaamed_dicom.engine.processor import DicomProcessor

class DicomProcessor:
    """
    Main DICOM de-identification processor.

    Args:
        preset: AnonymizationPreset configuration
        uid_mapper: Optional custom UIDMapper instance
        date_anchor: Optional anchor date for date shifting
    """

    def __init__(
        self,
        preset: AnonymizationPreset,
        uid_mapper: UIDMapper | None = None,
        date_anchor: date | None = None
    ):
        ...

    def process_file(
        self,
        input_path: str | Path,
        output_path: str | Path,
        dry_run: bool = False
    ) -> FileStatistics:
        """
        Process a single DICOM file.

        Args:
            input_path: Path to input DICOM file
            output_path: Path for output file
            dry_run: If True, don't write output file

        Returns:
            FileStatistics with processing results

        Raises:
            DicomProcessingError: If processing fails
        """
        ...

    def process_directory(
        self,
        input_dir: str | Path,
        output_dir: str | Path,
        parallel: bool = True,
        workers: int = 4,
        dry_run: bool = False,
        progress_callback: Callable[[int, int], None] | None = None
    ) -> ProcessingStatistics:
        """
        Process all DICOM files in a directory.

        Args:
            input_dir: Input directory path
            output_dir: Output directory path
            parallel: Enable parallel processing
            workers: Number of parallel workers
            dry_run: If True, don't write output files
            progress_callback: Optional callback(current, total)

        Returns:
            ProcessingStatistics with aggregate results
        """
        ...
```

#### FileStatistics

```python
from thakaamed_dicom.engine.processor import FileStatistics

@dataclass
class FileStatistics:
    """Statistics for a single file processing."""

    success: bool
    input_path: Path
    output_path: Path
    tags_modified: int
    tags_removed: int
    private_tags_removed: int
    study_uid_original: str
    study_uid_new: str
    series_uid_original: str
    series_uid_new: str
    sop_uid_original: str
    sop_uid_new: str
    error_message: str = ""
```

#### ProcessingStatistics

```python
from thakaamed_dicom.engine.processor import ProcessingStatistics

@dataclass
class ProcessingStatistics:
    """Aggregate statistics for batch processing."""

    files_processed: int
    files_successful: int
    files_failed: int
    studies_processed: int
    series_processed: int
    total_tags_modified: int
    total_tags_removed: int
    total_uids_remapped: int
    total_private_tags_removed: int
    processing_time_seconds: float
    file_statistics: list[FileStatistics]
    errors: list[str]
```

---

### thakaamed_dicom.engine.uid_mapper

UID remapping utilities.

#### UIDMapper

```python
from thakaamed_dicom.engine.uid_mapper import UIDMapper

class UIDMapper:
    """
    Thread-safe UID remapping using deterministic hashing.

    UIDs are remapped using SHA-256 hash to ensure:
    - Deterministic: Same input always gives same output
    - Consistent: Cross-file relationships preserved
    - Valid: Output UIDs comply with DICOM format
    """

    def __init__(self, prefix: str = "2.25"):
        """
        Initialize mapper with UID prefix.

        Args:
            prefix: UID root prefix (default: 2.25 for UUID-based)
        """
        ...

    def map_uid(self, original_uid: str) -> str:
        """
        Map original UID to anonymized UID.

        Args:
            original_uid: Original DICOM UID

        Returns:
            Remapped UID with configured prefix
        """
        ...

    def get_mapping(self) -> dict[str, str]:
        """
        Get complete UID mapping dictionary.

        Returns:
            Dict mapping original UIDs to remapped UIDs
        """
        ...

    def clear(self) -> None:
        """Clear all stored mappings."""
        ...
```

---

### thakaamed_dicom.engine.actions

Tag action implementations.

#### ActionExecutor

```python
from thakaamed_dicom.engine.actions import ActionExecutor

class ActionExecutor:
    """
    Executes de-identification actions on DICOM datasets.

    Args:
        uid_mapper: UIDMapper instance for UID actions
        date_handler: DateHandler for date actions
    """

    def execute(
        self,
        dataset: Dataset,
        tag: BaseTag,
        action: ActionType,
        value: str | None = None
    ) -> ActionResult:
        """
        Execute action on a specific tag.

        Args:
            dataset: pydicom Dataset
            tag: DICOM tag to process
            action: Action to perform
            value: Replacement value (for REPLACE action)

        Returns:
            ActionResult with execution details
        """
        ...
```

---

### thakaamed_dicom.reports

Report generation.

#### ReportGenerator

```python
from thakaamed_dicom.reports.generator import ReportGenerator

class ReportGenerator:
    """
    Generate anonymization reports in multiple formats.

    Args:
        output_dir: Directory for generated reports
    """

    def __init__(self, output_dir: str | Path):
        ...

    def generate(
        self,
        statistics: ProcessingStatistics,
        preset: AnonymizationPreset,
        input_path: str | Path,
        output_path: str | Path,
        formats: list[ReportFormat] | None = None
    ) -> list[Path]:
        """
        Generate reports from processing statistics.

        Args:
            statistics: ProcessingStatistics from processor
            preset: AnonymizationPreset used
            input_path: Original input path
            output_path: Output path
            formats: List of formats (default: all)

        Returns:
            List of generated report file paths
        """
        ...

    @classmethod
    def from_json(cls, json_path: str | Path) -> ReportData:
        """
        Load report data from JSON file.

        Args:
            json_path: Path to JSON audit file

        Returns:
            ReportData object
        """
        ...
```

#### ReportFormat

```python
from thakaamed_dicom.reports.models import ReportFormat

class ReportFormat(str, Enum):
    """Available report formats."""
    PDF = "pdf"
    JSON = "json"
    CSV = "csv"
    ALL = "all"
```

---

## Usage Examples

### Basic File Processing

```python
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor

# Load preset
preset = load_preset("sfda_safe_harbor")

# Create processor
processor = DicomProcessor(preset=preset)

# Process file
stats = processor.process_file(
    input_path="./patient_scan.dcm",
    output_path="./anonymized_scan.dcm"
)

print(f"Tags modified: {stats.tags_modified}")
print(f"Tags removed: {stats.tags_removed}")
print(f"New Study UID: {stats.study_uid_new}")
```

### Batch Processing with Progress

```python
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor

def progress_callback(current: int, total: int):
    print(f"Processing: {current}/{total}")

preset = load_preset("research")
processor = DicomProcessor(preset=preset)

stats = processor.process_directory(
    input_dir="./dicom_study",
    output_dir="./anonymized_study",
    parallel=True,
    workers=8,
    progress_callback=progress_callback
)

print(f"Processed: {stats.files_processed}")
print(f"Successful: {stats.files_successful}")
print(f"Failed: {stats.files_failed}")
```

### Custom Preset Configuration

```python
from thakaamed_dicom.config.models import (
    AnonymizationPreset,
    ComplianceConfig,
    DateHandlingConfig,
    DateHandling,
    PrivateTagConfig,
    TagRule,
    ActionType
)
from thakaamed_dicom.engine.processor import DicomProcessor

# Create preset programmatically
preset = AnonymizationPreset(
    name="Custom Research",
    description="Custom preset for research study",
    compliance=ComplianceConfig(standards=["IRB Protocol #123"]),
    date_handling=DateHandlingConfig(
        method=DateHandling.SHIFT,
        shift_days=90
    ),
    private_tags=PrivateTagConfig(action="remove"),
    tag_rules=[
        TagRule(tag="(0010,0010)", action=ActionType.REPLACE, value="SUBJECT"),
        TagRule(tag="(0010,0020)", action=ActionType.HASH),
        TagRule(tag="(0010,0030)", action=ActionType.REMOVE),
    ]
)

processor = DicomProcessor(preset=preset)
stats = processor.process_file("input.dcm", "output.dcm")
```

### Report Generation

```python
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor
from thakaamed_dicom.reports.generator import ReportGenerator
from thakaamed_dicom.reports.models import ReportFormat

# Process files
preset = load_preset("sfda_safe_harbor")
processor = DicomProcessor(preset=preset)
stats = processor.process_directory("./input", "./output")

# Generate reports
generator = ReportGenerator(output_dir="./reports")
report_paths = generator.generate(
    statistics=stats,
    preset=preset,
    input_path="./input",
    output_path="./output",
    formats=[ReportFormat.PDF, ReportFormat.JSON]
)

for path in report_paths:
    print(f"Generated: {path}")
```

### Regenerate Reports from JSON

```python
from thakaamed_dicom.reports.generator import ReportGenerator
from thakaamed_dicom.reports.pdf_report import PDFReportBuilder

# Load existing audit data
report_data = ReportGenerator.from_json("./audit_20240115.json")

# Generate PDF
pdf_builder = PDFReportBuilder()
pdf_builder.build(report_data, "./new_report.pdf")
```

### Custom UID Mapper

```python
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor
from thakaamed_dicom.engine.uid_mapper import UIDMapper

# Create custom mapper with specific prefix
mapper = UIDMapper(prefix="1.2.826.0.1.3680043.8.498")

# Use with processor
preset = load_preset("sfda_safe_harbor")
processor = DicomProcessor(preset=preset, uid_mapper=mapper)

# Process files
stats = processor.process_directory("./input", "./output")

# Get UID mapping for reference
uid_mapping = mapper.get_mapping()
for original, remapped in uid_mapping.items():
    print(f"{original} -> {remapped}")
```

### Date Shifting with Anchor

```python
from datetime import date
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor

# Use anchor date for consistent shifting
preset = load_preset("research")
processor = DicomProcessor(
    preset=preset,
    date_anchor=date(2020, 1, 1)
)

# All dates will be shifted relative to anchor
stats = processor.process_directory("./study", "./anonymized")
```

---

## Exceptions

```python
from thakaamed_dicom.exceptions import (
    ThakaamedError,          # Base exception
    PresetNotFoundError,     # Preset name not found
    PresetValidationError,   # Invalid preset configuration
    DicomProcessingError,    # Error during file processing
    ReportGenerationError,   # Error generating reports
)
```

---

## Type Hints

Full type hints are provided for IDE support:

```python
from thakaamed_dicom.config.models import AnonymizationPreset
from thakaamed_dicom.engine.processor import (
    DicomProcessor,
    FileStatistics,
    ProcessingStatistics
)
from thakaamed_dicom.reports.models import ReportData, ReportFormat
```

---

Next: [Examples](examples/) | [Configuration Guide](configuration.md)
