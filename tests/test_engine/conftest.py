"""Test fixtures for engine tests."""

import pytest
from pydicom import Dataset
from pydicom.uid import ImplicitVRLittleEndian, generate_uid

from dicom_anonymizer.config.models import (
    ActionCode,
    DateHandling,
    PresetConfig,
    TagRule,
)


@pytest.fixture
def sample_dataset():
    """Create a sample DICOM dataset for testing."""
    ds = Dataset()

    # File meta
    ds.file_meta = Dataset()
    ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
    ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
    ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

    # Patient Module
    ds.PatientName = "Test^Patient"
    ds.PatientID = "12345"
    ds.PatientBirthDate = "19800115"
    ds.PatientSex = "M"

    # Study Module
    ds.StudyInstanceUID = generate_uid()
    ds.StudyDate = "20240115"
    ds.StudyTime = "143022"
    ds.StudyDescription = "Test Study"
    ds.AccessionNumber = "ACC001"

    # Series Module
    ds.SeriesInstanceUID = generate_uid()
    ds.SeriesDate = "20240115"
    ds.SeriesDescription = "Test Series"
    ds.Modality = "CT"

    # Instance Module
    ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
    ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID
    ds.InstanceNumber = 1

    # Equipment
    ds.Manufacturer = "Test Manufacturer"
    ds.InstitutionName = "Test Hospital"
    ds.StationName = "SCANNER01"

    # Add some pixel data placeholder
    ds.Rows = 512
    ds.Columns = 512
    ds.BitsAllocated = 16
    ds.BitsStored = 12
    ds.HighBit = 11
    ds.PixelRepresentation = 0

    return ds


@pytest.fixture
def sample_dicom_file(tmp_path, sample_dataset):
    """Create a sample DICOM file for testing."""
    dicom_file = tmp_path / "test.dcm"
    sample_dataset.save_as(str(dicom_file))
    return dicom_file


@pytest.fixture
def sample_dicom_directory(tmp_path, sample_dataset):
    """Create a directory with sample DICOM files."""
    dicom_dir = tmp_path / "dicom"
    dicom_dir.mkdir()

    # Create multiple files with same study but different series
    study_uid = sample_dataset.StudyInstanceUID

    for i in range(3):
        series_uid = generate_uid()
        for j in range(2):
            ds = Dataset()
            ds.file_meta = Dataset()
            ds.file_meta.MediaStorageSOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
            ds.file_meta.MediaStorageSOPInstanceUID = generate_uid()
            ds.file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

            ds.PatientName = "Test^Patient"
            ds.PatientID = "12345"
            ds.StudyInstanceUID = study_uid
            ds.SeriesInstanceUID = series_uid
            ds.SOPInstanceUID = ds.file_meta.MediaStorageSOPInstanceUID
            ds.SOPClassUID = "1.2.840.10008.5.1.4.1.1.2"
            ds.StudyDate = "20240115"
            ds.Modality = "CT"
            ds.InstanceNumber = j + 1

            file_path = dicom_dir / f"series{i}_instance{j}.dcm"
            ds.save_as(str(file_path))

    return dicom_dir


@pytest.fixture
def sample_preset():
    """Create a sample preset configuration for testing."""
    return PresetConfig(
        name="Test Preset",
        description="Test preset for unit tests",
        compliance=["Test Compliance"],
        date_handling=DateHandling.REMOVE,
        remove_private_tags=True,
        tag_rules=[
            TagRule(
                tag="(0010,0010)",
                action=ActionCode.Z,
                replacement="ANONYMIZED",
                description="Patient Name",
            ),
            TagRule(
                tag="(0010,0020)",
                action=ActionCode.Z,
                description="Patient ID",
            ),
            TagRule(
                tag="(0010,0030)",
                action=ActionCode.X,
                description="Birth Date",
            ),
            TagRule(
                tag="(0008,0080)",
                action=ActionCode.X,
                description="Institution Name",
            ),
        ],
    )


@pytest.fixture
def research_preset():
    """Create a research preset with date shifting."""
    return PresetConfig(
        name="Research Test",
        description="Research preset for testing date shifting",
        compliance=["Test Compliance"],
        date_handling=DateHandling.SHIFT,
        retain_longitudinal=True,
        remove_private_tags=True,
        tag_rules=[
            TagRule(
                tag="(0010,0010)",
                action=ActionCode.Z,
                replacement="ANONYMIZED",
                description="Patient Name",
            ),
        ],
    )
