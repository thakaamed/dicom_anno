"""Tests for UIDMapper."""

from concurrent.futures import ThreadPoolExecutor

from thakaamed_dicom.engine.uid_mapper import UIDMapper


class TestUIDMapper:
    """Tests for UIDMapper class."""

    def test_consistent_mapping(self):
        """Same input produces same output."""
        mapper = UIDMapper(salt="test_salt")
        uid1 = "1.2.3.4.5"

        result1 = mapper.get_or_create(uid1)
        result2 = mapper.get_or_create(uid1)

        assert result1 == result2

    def test_different_inputs_produce_different_outputs(self):
        """Different inputs produce different outputs."""
        mapper = UIDMapper(salt="test_salt")

        result1 = mapper.get_or_create("1.2.3.4.5")
        result2 = mapper.get_or_create("1.2.3.4.6")

        assert result1 != result2

    def test_different_salts_produce_different_outputs(self):
        """Different salts produce different outputs for same input."""
        mapper1 = UIDMapper(salt="salt1")
        mapper2 = UIDMapper(salt="salt2")
        uid = "1.2.3.4.5"

        result1 = mapper1.get_or_create(uid)
        result2 = mapper2.get_or_create(uid)

        assert result1 != result2

    def test_uid_format_valid(self):
        """Generated UIDs have valid format."""
        mapper = UIDMapper()
        result = mapper.get_or_create("1.2.3.4.5")

        # Should start with 2.25 root
        assert result.startswith("2.25.")
        # Should be valid UID format (only digits and dots)
        assert all(c.isdigit() or c == "." for c in result)
        # Should not exceed 64 characters
        assert len(result) <= 64

    def test_clear_mappings(self):
        """Clear removes all mappings."""
        mapper = UIDMapper(salt="test_salt")

        mapper.get_or_create("1.2.3.4.5")
        mapper.get_or_create("1.2.3.4.6")
        assert len(mapper) == 2

        mapper.clear()
        assert len(mapper) == 0

    def test_export_mapping(self):
        """Export returns all mappings."""
        mapper = UIDMapper(salt="test_salt")
        uid1 = "1.2.3.4.5"
        uid2 = "1.2.3.4.6"

        new1 = mapper.get_or_create(uid1)
        new2 = mapper.get_or_create(uid2)

        exported = mapper.export_mapping()

        assert uid1 in exported
        assert uid2 in exported
        assert exported[uid1] == new1
        assert exported[uid2] == new2

    def test_thread_safety(self):
        """Concurrent access is thread-safe."""
        mapper = UIDMapper(salt="test_salt")
        uids = [f"1.2.3.4.{i}" for i in range(100)]

        def map_uid(uid):
            return uid, mapper.get_or_create(uid)

        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(map_uid, uids))

        # Verify all UIDs were mapped consistently
        for uid, new_uid in results:
            assert mapper.get_or_create(uid) == new_uid

        # Verify all UIDs are unique
        new_uids = [r[1] for r in results]
        assert len(set(new_uids)) == len(uids)

    def test_random_salt_when_not_provided(self):
        """Random salt is used when not provided."""
        mapper1 = UIDMapper()
        mapper2 = UIDMapper()
        uid = "1.2.3.4.5"

        # With different random salts, outputs should differ
        result1 = mapper1.get_or_create(uid)
        result2 = mapper2.get_or_create(uid)

        # Very unlikely to match with random salts
        assert result1 != result2
