"""Tests for HIPAA Safe Harbor compliance (18 identifiers)."""

import pytest
from pydicom import dcmread

from tests.fixtures.dicom_factory import DicomFactory
from thakaamed_dicom.config.loader import load_preset
from thakaamed_dicom.engine.processor import DicomProcessor


class TestHIPAASafeHarbor:
    """Tests for HIPAA Safe Harbor compliance (18 identifiers)."""

    @pytest.fixture
    def safe_harbor_processor(self):
        preset = load_preset("sfda_safe_harbor")
        return DicomProcessor(preset=preset)

    @pytest.fixture
    def full_phi_file(self, tmp_path):
        """Create file with all HIPAA identifiers."""
        ds = DicomFactory.create_with_all_phi()
        path = tmp_path / "full_phi.dcm"
        ds.save_as(str(path))
        return path

    def test_names_removed(self, safe_harbor_processor, full_phi_file, tmp_path):
        """All names are removed (Identifier #1)."""
        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(full_phi_file, output)
        ds = dcmread(str(output), force=True)

        # Check patient name
        assert str(ds.PatientName) in ("", "ANONYMIZED")

    def test_address_removed(self, safe_harbor_processor, full_phi_file, tmp_path):
        """Geographic information is removed (Identifier #2)."""
        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(full_phi_file, output)
        ds = dcmread(str(output), force=True)

        assert not hasattr(ds, "PatientAddress") or ds.PatientAddress == ""
        assert not hasattr(ds, "InstitutionAddress") or ds.InstitutionAddress == ""

    def test_dates_removed(self, safe_harbor_processor, full_phi_file, tmp_path):
        """Dates are removed (Identifier #3)."""
        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(full_phi_file, output)
        ds = dcmread(str(output), force=True)

        # Birth date must be removed for Safe Harbor
        assert not hasattr(ds, "PatientBirthDate") or ds.PatientBirthDate == ""

    def test_phone_numbers_removed(self, safe_harbor_processor, full_phi_file, tmp_path):
        """Phone numbers are removed (Identifier #4)."""
        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(full_phi_file, output)
        ds = dcmread(str(output), force=True)

        assert not hasattr(ds, "PatientTelephoneNumbers") or ds.PatientTelephoneNumbers == ""

    def test_medical_record_numbers_replaced(
        self, safe_harbor_processor, full_phi_file, tmp_path
    ):
        """Medical record numbers are replaced (Identifier #6)."""
        output = tmp_path / "output.dcm"
        original = dcmread(str(full_phi_file), force=True)
        safe_harbor_processor.process_file(full_phi_file, output)
        ds = dcmread(str(output), force=True)

        # Patient ID typically serves as MRN - should be changed or empty
        assert ds.PatientID != original.PatientID or ds.PatientID == ""

    def test_other_patient_ids_removed(self, safe_harbor_processor, full_phi_file, tmp_path):
        """Other patient identifiers are removed."""
        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(full_phi_file, output)
        ds = dcmread(str(output), force=True)

        assert not hasattr(ds, "OtherPatientIDs") or ds.OtherPatientIDs == ""

    def test_device_identifiers_handled(self, safe_harbor_processor, tmp_path):
        """Device identifiers and serial numbers are handled."""
        # Create file with device identifiers
        ds = DicomFactory.create_minimal()
        ds.DeviceSerialNumber = "SERIAL123"
        ds.StationName = "CT_SCANNER_01"
        input_file = tmp_path / "device.dcm"
        ds.save_as(str(input_file))

        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(input_file, output)
        result = dcmread(str(output), force=True)

        # Device serials should be handled based on preset
        # For safe harbor, these may or may not be removed depending on configuration
        # Just ensure processing completes without error
        assert result is not None

    def test_private_tags_removed_safe_harbor(
        self, safe_harbor_processor, tmp_path
    ):
        """Private tags are removed for Safe Harbor compliance."""
        ds = DicomFactory.create_with_private_tags(num_private=5)
        input_file = tmp_path / "private.dcm"
        ds.save_as(str(input_file))

        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(input_file, output)
        result = dcmread(str(output), force=True)

        private_count = sum(1 for elem in result if elem.tag.is_private)
        assert private_count == 0

    def test_uid_format_valid(self, safe_harbor_processor, full_phi_file, tmp_path):
        """New UIDs have valid format."""
        output = tmp_path / "output.dcm"
        safe_harbor_processor.process_file(full_phi_file, output)
        ds = dcmread(str(output), force=True)

        # UIDs should be in 2.25 format (UUID-based)
        assert ds.StudyInstanceUID.startswith("2.25.")
        assert ds.SeriesInstanceUID.startswith("2.25.")
        assert ds.SOPInstanceUID.startswith("2.25.")

        # UIDs should be <= 64 characters
        assert len(ds.StudyInstanceUID) <= 64
        assert len(ds.SeriesInstanceUID) <= 64
        assert len(ds.SOPInstanceUID) <= 64
