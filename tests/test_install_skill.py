import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "skill_installer", ROOT / "scripts" / "install_skill.py"
)
INSTALLER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALLER)


class InstallSkillTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "SKILL.md").write_text("Synthetic skill\n", encoding="utf-8")
        (self.source / "tools").mkdir()
        (self.source / "tools" / "example.py").write_text(
            "print('synthetic')\n", encoding="utf-8"
        )
        self.destination = self.root / "personal" / "case-session-to-wiki"

    def test_install_verifies_files_and_keeps_source_unchanged(self):
        before = INSTALLER.manifest(self.source)
        self.assertEqual(
            INSTALLER.install(self.source, self.destination),
            {"status": "installed", "files_verified": 2},
        )
        self.assertEqual(INSTALLER.manifest(self.destination), before)
        self.assertEqual(INSTALLER.manifest(self.source), before)

    def test_actual_document_only_bundle_installs_with_all_references(self):
        destination = self.root / "actual-bundle"
        result = INSTALLER.install(INSTALLER.DEFAULT_SOURCE, destination)
        self.assertEqual(result, {"status": "installed", "files_verified": 7})
        self.assertEqual(
            INSTALLER.manifest(destination), INSTALLER.manifest(INSTALLER.DEFAULT_SOURCE)
        )
        self.assertTrue(all(path.suffix == ".md" for path in destination.rglob("*") if path.is_file()))

    def test_identical_install_is_idempotent(self):
        INSTALLER.install(self.source, self.destination)
        before = (self.destination / "SKILL.md").stat().st_mtime_ns
        self.assertEqual(
            INSTALLER.install(self.source, self.destination)["status"], "unchanged"
        )
        self.assertEqual((self.destination / "SKILL.md").stat().st_mtime_ns, before)

    def test_local_edit_is_not_overwritten(self):
        INSTALLER.install(self.source, self.destination)
        target = self.destination / "SKILL.md"
        target.write_text("User edit\n", encoding="utf-8")
        with self.assertRaisesRegex(INSTALLER.InstallError, "refusing to overwrite"):
            INSTALLER.install(self.source, self.destination)
        self.assertEqual(target.read_text(encoding="utf-8"), "User edit\n")

    def test_unknown_destination_file_blocks_replacement(self):
        INSTALLER.install(self.source, self.destination)
        (self.destination / "user-notes.txt").write_text("Keep me", encoding="utf-8")
        with self.assertRaises(INSTALLER.InstallError):
            INSTALLER.install(self.source, self.destination)

    def test_missing_skill_and_nested_destination_are_rejected(self):
        empty = self.root / "empty"
        empty.mkdir()
        with self.assertRaises(INSTALLER.InstallError):
            INSTALLER.install(empty, self.destination)
        with self.assertRaises(INSTALLER.InstallError):
            INSTALLER.install(self.source, self.source / "nested")
        self.assertFalse((self.source / "nested").exists())

    def test_bytecode_is_not_installed(self):
        cache = self.source / "__pycache__"
        cache.mkdir()
        (cache / "example.pyc").write_bytes(b"synthetic")
        result = INSTALLER.install(self.source, self.destination)
        self.assertEqual(result["files_verified"], 2)
        self.assertFalse((self.destination / "__pycache__").exists())

    def test_copy_failure_is_explicit(self):
        with patch.object(INSTALLER.shutil, "copytree", side_effect=OSError("synthetic")):
            with self.assertRaisesRegex(INSTALLER.InstallError, "partial destination"):
                INSTALLER.install(self.source, self.destination)

    def test_reparse_path_is_rejected_before_copying(self):
        with patch.object(INSTALLER, "is_link", return_value=True):
            with self.assertRaisesRegex(INSTALLER.InstallError, "reparse"):
                INSTALLER.install(self.source, self.destination)
        self.assertFalse(self.destination.exists())


if __name__ == "__main__":
    unittest.main()
