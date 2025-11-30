"""Tests for DICOM PS3.15 Basic Profile compliance."""

import pytest
from pydicom import dcmread

from dicom_anonymizer.config.loader import load_preset
from dicom_anonymizer.engine.processor import DicomProcessor
from tests.fixtures.dicom_factory import DicomFactory


class TestDicomPS315Compliance:
    """Tests for DICOM PS3.15 Basic Profile compliance."""

    @pytest.fixture
    def sfda_processor(self):
        preset = load_preset("sfda_safe_harbor")
        return DicomProcessor(preset=preset)

    @pytest.fixture
    def sample_phi_dicom(self, tmp_path):
        """Create DICOM with PHI fields."""
        ds = DicomFactory.create_with_all_phi()
        path = tmp_path / "phi_test.dcm"
        ds.save_as(str(path))
        return path

    @pytest.fixture
    def sample_dicom_with_private(self, tmp_path):
        """Create DICOM with private tags."""
        ds = DicomFactory.create_with_private_tags(num_private=10)
        path = tmp_path / "private.dcm"
        ds.save_as(str(path))
        return path

    def test_patient_name_handled(self, sfda_processor, sample_phi_dicom, tmp_path):
        """Patient's Name (0010,0010) is handled per Basic Profile."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        # Should be empty or dummy (Z action)
        assert str(ds.PatientName) in ("", "ANONYMIZED")

    def test_patient_id_handled(self, sfda_processor, sample_phi_dicom, tmp_path):
        """Patient ID (0010,0020) is handled per Basic Profile."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        # Should be empty or different from original
        original_ds = dcmread(str(sample_phi_dicom), force=True)
        assert ds.PatientID != original_ds.PatientID or ds.PatientID == ""

    def test_birth_date_removed(self, sfda_processor, sample_phi_dicom, tmp_path):
        """Patient's Birth Date (0010,0030) is removed."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        # Should be removed or empty (X action)
        assert not hasattr(ds, "PatientBirthDate") or ds.PatientBirthDate == ""

    def test_uids_remapped(self, sfda_processor, sample_phi_dicom, tmp_path):
        """Study/Series/SOP Instance UIDs are remapped (U action)."""
        output = tmp_path / "output.dcm"
        original_ds = dcmread(str(sample_phi_dicom), force=True)

        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        # All UIDs should be different and in 2.25 format
        assert ds.StudyInstanceUID != original_ds.StudyInstanceUID
        assert ds.SeriesInstanceUID != original_ds.SeriesInstanceUID
        assert ds.SOPInstanceUID != original_ds.SOPInstanceUID

        assert ds.StudyInstanceUID.startswith("2.25.")
        assert ds.SeriesInstanceUID.startswith("2.25.")
        assert ds.SOPInstanceUID.startswith("2.25.")

    def test_media_storage_uid_matches_sop(self, sfda_processor, sample_phi_dicom, tmp_path):
        """MediaStorageSOPInstanceUID matches SOPInstanceUID."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        assert ds.file_meta.MediaStorageSOPInstanceUID == ds.SOPInstanceUID

    def test_deidentification_markers_present(self, sfda_processor, sample_phi_dicom, tmp_path):
        """Required de-identification markers are present."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        # (0012,0062) Patient Identity Removed must be "YES"
        assert hasattr(ds, "PatientIdentityRemoved")
        assert ds.PatientIdentityRemoved == "YES"

        # (0012,0063) De-identification Method should be populated
        assert hasattr(ds, "DeidentificationMethod")
        assert ds.DeidentificationMethod != ""

    def test_private_tags_removed(self, sfda_processor, sample_dicom_with_private, tmp_path):
        """All private tags are removed."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_dicom_with_private, output)
        ds = dcmread(str(output), force=True)

        private_count = sum(1 for elem in ds if elem.tag.is_private)
        assert private_count == 0

    def test_institution_name_removed(self, sfda_processor, sample_phi_dicom, tmp_path):
        """Institution Name is handled appropriately."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        # Should be removed or anonymized
        assert not hasattr(ds, "InstitutionName") or ds.InstitutionName == ""

    def test_referring_physician_handled(self, sfda_processor, sample_phi_dicom, tmp_path):
        """Referring Physician Name is handled."""
        output = tmp_path / "output.dcm"
        sfda_processor.process_file(sample_phi_dicom, output)
        ds = dcmread(str(output), force=True)

        # Should be empty or anonymized
        if hasattr(ds, "ReferringPhysicianName"):
            value = str(ds.ReferringPhysicianName)
            assert value in ("", "ANONYMIZED", "Dr^Anonymized")
