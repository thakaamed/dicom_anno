"""Factory for creating test DICOM files."""

from pathlib import Path

from pydicom import Dataset, FileDataset
from pydicom.uid import ImplicitVRLittleEndian, generate_uid


class DicomFactory:
    """Factory for creating test DICOM files."""

    CT_SOP_CLASS = "1.2.840.10008.5.1.4.1.1.2"

    @classmethod
    def create_minimal(cls, **overrides) -> FileDataset:
        """Create minimal valid DICOM dataset."""
        # File meta
        file_meta = Dataset()
        file_meta.MediaStorageSOPClassUID = cls.CT_SOP_CLASS
        file_meta.MediaStorageSOPInstanceUID = generate_uid()
        file_meta.TransferSyntaxUID = ImplicitVRLittleEndian

        ds = FileDataset(None, {}, file_meta=file_meta, preamble=b"\0" * 128)

        # Patient module
        ds.PatientName = "Test^Patient^M"
        ds.PatientID = "TEST001"
        ds.PatientBirthDate = "19800515"
        ds.PatientSex = "M"

        # Study module
        ds.StudyInstanceUID = generate_uid()
        ds.StudyDate = "20240115"
        ds.StudyTime = "143022"
        ds.AccessionNumber = "ACC001"
        ds.StudyDescription = "Test Study"

        # Series module
        ds.SeriesInstanceUID = generate_uid()
        ds.Modality = "CT"
        ds.SeriesNumber = "1"
        ds.SeriesDescription = "Test Series"

        # Instance module
        ds.SOPInstanceUID = file_meta.MediaStorageSOPInstanceUID
        ds.SOPClassUID = file_meta.MediaStorageSOPClassUID
        ds.InstanceNumber = "1"

        # Apply overrides
        for key, value in overrides.items():
            setattr(ds, key, value)

        return ds

    @classmethod
    def create_with_private_tags(cls, num_private: int = 5) -> FileDataset:
        """Create DICOM with private tags."""
        ds = cls.create_minimal()

        # Add private tags
        for i in range(num_private):
            block = ds.private_block(0x0009, f"TestCreator{i}", create=True)
            block.add_new(0x01, "LO", f"Private Value {i}")

        return ds

    @classmethod
    def create_study_series(
        cls,
        output_dir: Path,
        num_series: int = 2,
        files_per_series: int = 3,
    ) -> Path:
        """Create directory with study containing multiple series."""
        output_dir.mkdir(parents=True, exist_ok=True)

        study_uid = generate_uid()

        for series_idx in range(num_series):
            series_uid = generate_uid()
            series_dir = output_dir / f"series_{series_idx + 1}"
            series_dir.mkdir()

            for file_idx in range(files_per_series):
                ds = cls.create_minimal(
                    StudyInstanceUID=study_uid,
                    SeriesInstanceUID=series_uid,
                    InstanceNumber=str(file_idx + 1),
                )

                file_path = series_dir / f"img_{file_idx + 1:04d}.dcm"
                ds.save_as(str(file_path))

        return output_dir

    @classmethod
    def create_with_all_phi(cls) -> FileDataset:
        """Create DICOM with all PHI fields populated for compliance testing."""
        ds = cls.create_minimal()

        # Additional PHI fields
        ds.PatientAddress = "123 Main St, Riyadh"
        ds.PatientTelephoneNumbers = "966123456789"
        ds.OtherPatientIDs = "OTHER001"
        ds.OtherPatientNames = "OtherName"
        ds.InstitutionName = "Test Hospital"
        ds.InstitutionAddress = "Hospital Address"
        ds.ReferringPhysicianName = "Dr^Referring"
        ds.PerformingPhysicianName = "Dr^Performing"
        ds.OperatorsName = "Operator^Name"
        ds.PhysiciansOfRecord = "Dr^Record"

        return ds
