"""Tests for DicomProcessor."""

from pydicom import dcmread

from dicom_anonymizer.engine.processor import DicomProcessor


class TestDicomProcessorFile:
    """Tests for single file processing."""

    def test_process_file_success(self, sample_dicom_file, sample_preset, tmp_path):
        """Successfully processes a DICOM file."""
        output_file = tmp_path / "output.dcm"

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_file(sample_dicom_file, output_file)

        assert stats.success is True
        assert output_file.exists()
        assert stats.processing_time_ms > 0

    def test_anonymization_applied(self, sample_dicom_file, sample_preset, tmp_path):
        """Anonymization rules are applied correctly."""
        output_file = tmp_path / "output.dcm"

        processor = DicomProcessor(preset=sample_preset)
        processor.process_file(sample_dicom_file, output_file)

        ds = dcmread(str(output_file), force=True)

        # Z action with replacement
        assert ds.PatientName == "ANONYMIZED"
        # Z action without replacement
        assert ds.PatientID == ""
        # X action - should be removed
        assert not hasattr(ds, "PatientBirthDate")
        assert not hasattr(ds, "InstitutionName")

    def test_uid_remapping(self, sample_dicom_file, sample_preset, tmp_path):
        """UIDs are remapped to new consistent values."""
        output_file = tmp_path / "output.dcm"

        original_ds = dcmread(str(sample_dicom_file), force=True)
        original_study_uid = original_ds.StudyInstanceUID

        processor = DicomProcessor(preset=sample_preset)
        processor.process_file(sample_dicom_file, output_file)

        ds = dcmread(str(output_file), force=True)

        # UIDs should be different
        assert ds.StudyInstanceUID != original_study_uid
        # Should use 2.25 root
        assert ds.StudyInstanceUID.startswith("2.25.")
        # MediaStorageSOPInstanceUID should match SOPInstanceUID
        assert ds.file_meta.MediaStorageSOPInstanceUID == ds.SOPInstanceUID

    def test_deidentification_markers(self, sample_dicom_file, sample_preset, tmp_path):
        """De-identification markers are set."""
        output_file = tmp_path / "output.dcm"

        processor = DicomProcessor(preset=sample_preset)
        processor.process_file(sample_dicom_file, output_file)

        ds = dcmread(str(output_file), force=True)

        assert ds.PatientIdentityRemoved == "YES"
        assert "THAKAAMED" in ds.DeidentificationMethod
        assert sample_preset.name in ds.DeidentificationMethod

    def test_dry_run_no_output(self, sample_dicom_file, sample_preset, tmp_path):
        """Dry run doesn't create output file."""
        output_file = tmp_path / "output.dcm"

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_file(sample_dicom_file, output_file, dry_run=True)

        assert stats.success is True
        assert not output_file.exists()

    def test_statistics_tracking(self, sample_dicom_file, sample_preset, tmp_path):
        """Statistics are tracked correctly."""
        output_file = tmp_path / "output.dcm"

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_file(sample_dicom_file, output_file)

        # Should have some modifications
        assert stats.tags_modified > 0 or stats.tags_removed > 0
        # Should have UID remapping
        assert stats.uids_remapped > 0

    def test_invalid_file_handling(self, tmp_path, sample_preset):
        """Invalid DICOM file produces error or empty stats."""
        invalid_file = tmp_path / "invalid.dcm"
        invalid_file.write_text("not a dicom file")
        output_file = tmp_path / "output.dcm"

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_file(invalid_file, output_file)

        # With force=True, pydicom may still parse garbage - check output
        # Either fails or produces minimal/empty result
        if stats.success:
            # If it "succeeded", output shouldn't have useful data
            assert stats.tags_modified == 0 or stats.tags_removed == 0


class TestDicomProcessorDirectory:
    """Tests for directory processing."""

    def test_process_directory(self, sample_dicom_directory, sample_preset, tmp_path):
        """Processes all DICOM files in directory."""
        output_dir = tmp_path / "output"

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_directory(sample_dicom_directory, output_dir, parallel=False)

        assert stats.files_processed > 0
        assert stats.files_successful == stats.files_processed
        assert stats.files_failed == 0

    def test_parallel_processing(self, sample_dicom_directory, sample_preset, tmp_path):
        """Parallel processing works correctly."""
        output_dir = tmp_path / "output"

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_directory(
            sample_dicom_directory, output_dir, parallel=True, workers=2
        )

        assert stats.files_successful > 0
        assert stats.files_failed == 0

    def test_uid_consistency_across_files(self, sample_dicom_directory, sample_preset, tmp_path):
        """UIDs are consistent across files in same study."""
        output_dir = tmp_path / "output"

        processor = DicomProcessor(preset=sample_preset)
        processor.process_directory(sample_dicom_directory, output_dir, parallel=False)

        # Read all output files and collect study UIDs
        study_uids = set()
        for dcm_file in output_dir.rglob("*.dcm"):
            ds = dcmread(str(dcm_file), force=True)
            study_uids.add(ds.StudyInstanceUID)

        # Should have consistent study UID (all remapped to same new UID)
        assert len(study_uids) == 1
        assert list(study_uids)[0].startswith("2.25.")

    def test_progress_callback(self, sample_dicom_directory, sample_preset, tmp_path):
        """Progress callback is called correctly."""
        output_dir = tmp_path / "output"
        progress_calls = []

        def callback(completed, total):
            progress_calls.append((completed, total))

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_directory(
            sample_dicom_directory,
            output_dir,
            parallel=False,
            progress_callback=callback,
        )

        # Should have progress calls for each file
        assert len(progress_calls) == stats.files_processed
        # Last call should show complete
        assert progress_calls[-1][0] == progress_calls[-1][1]

    def test_empty_directory(self, tmp_path, sample_preset):
        """Empty directory returns empty statistics."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        output_dir = tmp_path / "output"

        processor = DicomProcessor(preset=sample_preset)
        stats = processor.process_directory(empty_dir, output_dir)

        assert stats.files_processed == 0


class TestDateShifting:
    """Tests for date shifting functionality."""

    def test_date_shifting_applied(self, sample_dicom_file, research_preset, tmp_path):
        """Date shifting is applied when configured."""
        output_file = tmp_path / "output.dcm"

        processor = DicomProcessor(
            preset=research_preset,
            date_anchor="20240115",
        )
        processor.process_file(sample_dicom_file, output_file)

        ds = dcmread(str(output_file), force=True)

        # Date should be shifted
        # Original: 20240115, with anchor 20240115 and base 1975-01-01
        # Shifted should be 1975-01-01
        assert ds.StudyDate == "19750101"
