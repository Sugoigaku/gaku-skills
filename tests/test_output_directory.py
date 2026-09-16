import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


TOOLS = (
    Path(__file__).resolve().parents[1] / ".github" / "skills"
    / "case-session-to-wiki" / "tools"
)
with patch.object(sys, "path", [str(TOOLS), *sys.path]):
    SPEC = importlib.util.spec_from_file_location(
        "output_directory", TOOLS / "create_output_directory.py"
    )
    OUTPUT = importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(OUTPUT)


class OutputDirectoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.session_id = "11111111-1111-4111-8111-111111111111"
        self.session = self.root / self.session_id
        self.session.mkdir()
        self.events = self.session / "events.jsonl"
        self.events.write_text('{"type":"user.message","data":{"content":"Synthetic"}}\n')

    def test_selected_source_session_owns_the_output(self):
        before = self.events.read_bytes()
        result = OUTPUT.create_output_directory(
            session_id=self.session_id, session_root=self.root,
        )
        path = Path(result["output_directory"])
        self.assertEqual(result["status"], "created")
        self.assertEqual(path.parent, self.session)
        self.assertTrue(path.name.startswith("wiki-output-"))
        self.assertTrue(path.is_dir())
        self.assertEqual(list(path.iterdir()), [])
        self.assertEqual(self.events.read_bytes(), before)

    def test_repeat_runs_never_replace_existing_outputs(self):
        first = Path(OUTPUT.create_output_directory(session_dir=self.session)["output_directory"])
        article = first / "qa-synthetic.md"
        article.write_text("Keep the earlier draft", encoding="utf-8")
        second = Path(OUTPUT.create_output_directory(session_dir=self.session)["output_directory"])
        self.assertNotEqual(first, second)
        self.assertEqual(second.parent, first.parent)
        self.assertEqual(article.read_text(encoding="utf-8"), "Keep the earlier draft")

    def test_runtime_session_directory_need_not_have_an_archive_file(self):
        self.events.unlink()
        result = OUTPUT.create_output_directory(session_dir=self.session)
        self.assertEqual(Path(result["output_directory"]).parent, self.session)

    def test_missing_selected_session_is_not_created(self):
        missing = "22222222-2222-4222-8222-222222222222"
        with self.assertRaises(OUTPUT.ReaderError):
            OUTPUT.create_output_directory(session_id=missing, session_root=self.root)
        self.assertFalse((self.root / missing).exists())

    def test_missing_archive_for_id_selection_is_rejected(self):
        self.events.unlink()
        with self.assertRaises(OUTPUT.ReaderError):
            OUTPUT.create_output_directory(session_id=self.session_id, session_root=self.root)

    def test_unknown_mixed_and_non_session_destinations_fail(self):
        cases = [
            {},
            {"session_dir": self.root},
            {"session_id": "../elsewhere", "session_root": self.root},
            {"session_dir": self.session, "session_id": self.session_id},
            {"session_dir": self.session, "session_root": self.root},
        ]
        for kwargs in cases:
            with self.subTest(kwargs=kwargs), self.assertRaises(OUTPUT.ReaderError):
                OUTPUT.create_output_directory(**kwargs)
        self.assertEqual(list(self.session.iterdir()), [self.events])

    def test_reparse_validation_is_reused_before_creation(self):
        with patch.object(
            OUTPUT, "resolve_session_directory",
            side_effect=OUTPUT.ReaderError("unsafe_path"),
        ):
            with self.assertRaises(OUTPUT.ReaderError):
                OUTPUT.create_output_directory(session_dir=self.session)
        self.assertEqual(list(self.session.iterdir()), [self.events])

    def test_cli_creates_only_a_path_report_without_article_text(self):
        result = subprocess.run(
            [sys.executable, "-B", str(TOOLS / "create_output_directory.py"),
             "--session-id", self.session_id, "--session-root", str(self.root)],
            capture_output=True, text=True, check=True,
        )
        report = json.loads(result.stdout)
        self.assertEqual(set(report), {"status", "output_directory"})
        self.assertEqual(Path(report["output_directory"]).parent, self.session)
        self.assertNotIn("Synthetic", result.stdout)

    def test_cli_bad_arguments_do_not_echo_source_values(self):
        result = subprocess.run(
            [sys.executable, "-B", str(TOOLS / "create_output_directory.py"),
             "--session-id", "SENSITIVE_INVALID_INPUT"],
            capture_output=True, text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["status"], "failed")
        self.assertNotIn("SENSITIVE_INVALID_INPUT", result.stdout + result.stderr)

    def test_creation_failure_is_reported_not_success(self):
        with patch.object(OUTPUT.tempfile, "mkdtemp", side_effect=OSError("private detail")):
            with patch("sys.stdout") as stdout:
                code = OUTPUT.main(["--session-dir", str(self.session)])
        self.assertEqual(code, 1)
        rendered = "".join(call.args[0] for call in stdout.write.call_args_list)
        self.assertEqual(json.loads(rendered)["error"], "output_directory_unavailable")
        self.assertNotIn("private detail", rendered)


if __name__ == "__main__":
    unittest.main()
