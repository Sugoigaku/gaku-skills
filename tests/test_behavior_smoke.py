import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "behavior_smoke", ROOT / "scripts" / "behavior_smoke.py"
)
SMOKE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SMOKE)


class BehaviorSmokeTests(unittest.TestCase):
    def test_all_registered_fixtures_exist_and_use_synthetic_inputs(self):
        self.assertIn("document-only", SMOKE.NAMES)
        self.assertIn("embedded-sources", SMOKE.NAMES)
        for name in SMOKE.NAMES:
            with self.subTest(name=name):
                text = (SMOKE.FIXTURES / f"{name}.txt").read_text(encoding="utf-8")
                self.assertIn("synthetic", text.lower())
                self.assertIn("case-session-to-wiki", text)

    def test_bundle_digest_changes_with_content_but_ignores_bytecode(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "SKILL.md"
            source.write_text("First", encoding="utf-8")
            before = SMOKE.bundle_digest(root)
            cache = root / "__pycache__"
            cache.mkdir()
            (cache / "helper.pyc").write_bytes(b"ignored")
            self.assertEqual(SMOKE.bundle_digest(root), before)
            source.write_text("Changed", encoding="utf-8")
            self.assertNotEqual(SMOKE.bundle_digest(root), before)

    def test_windows_shim_uses_direct_node_not_command_shell(self):
        def resolve(name):
            return r"C:\npm\copilot.cmd" if name == "copilot" else r"C:\node\node.exe"
        with patch.object(SMOKE.shutil, "which", side_effect=resolve):
            with patch.object(Path, "is_file", side_effect=lambda: True):
                command = SMOKE.cli_command()
        self.assertEqual(Path(command[1]).name, "npm-loader.js")
        self.assertTrue(command[0].endswith("node.exe"))
        self.assertFalse(any(value.lower().endswith(".cmd") for value in command))

    def events(self, success=True):
        return [
            {"type": "tool.execution_start", "data": {
                "toolName": "skill", "toolCallId": "synthetic-call",
                "arguments": {"skill": "case-session-to-wiki"},
            }},
            {"type": "tool.execution_complete", "data": {
                "toolCallId": "synthetic-call", "success": success,
            }},
            {"type": "assistant.message", "data": {
                "content": "Synthetic visible answer",
                "reasoningText": "SYNTHETIC_HIDDEN",
            }},
        ]

    def summarize(self, events, return_code=0):
        return SMOKE.summarize_events(
            "\n".join(json.dumps(event) for event in events), "topic-plan", return_code
        )

    def test_success_requires_actual_skill_execution_not_a_claim(self):
        result = self.summarize(self.events())
        self.assertTrue(result["native_skill_invoked"])
        self.assertEqual(result["transport_status"], "passed")
        self.assertEqual(result["semantic_result"], "not-reviewed")
        self.assertFalse(self.summarize(self.events()[2:])["native_skill_invoked"])

    def test_failed_invocation_or_cli_fails_transport(self):
        self.assertEqual(self.summarize(self.events(False))["transport_status"], "failed")
        self.assertEqual(self.summarize(self.events(), 1)["transport_status"], "failed")

    def test_unexpected_tool_is_not_silent(self):
        events = self.events() + [{
            "type": "tool.execution_start", "data": {"toolName": "powershell"}
        }]
        result = self.summarize(events)
        self.assertEqual(result["unexpected_tools"], ["powershell"])
        self.assertEqual(result["transport_status"], "failed")

    def test_hidden_fields_system_events_and_tool_results_are_not_exported(self):
        events = self.events() + [
            {"type": "system.message", "data": {"content": "SYNTHETIC_SYSTEM"}},
            {"type": "model.messages_snapshot", "data": {"messages": "SYNTHETIC_SNAPSHOT"}},
            {"type": "tool.execution_complete", "data": {
                "toolCallId": "extra", "result": {"content": "SYNTHETIC_RAW_RESULT"}
            }},
        ]
        text = json.dumps(self.summarize(events))
        for marker in (
            "SYNTHETIC_HIDDEN", "SYNTHETIC_SYSTEM",
            "SYNTHETIC_SNAPSHOT", "SYNTHETIC_RAW_RESULT",
        ):
            self.assertNotIn(marker, text)

    def test_malformed_output_cannot_pass(self):
        result = SMOKE.summarize_events("not-json\n[]\n", "topic-plan", 0)
        self.assertEqual(result["malformed_output_lines"], 2)
        self.assertEqual(result["transport_status"], "failed")

    def test_failed_reference_read_cannot_pass(self):
        result = self.summarize(self.events() + [{
            "type": "tool.execution_complete",
            "data": {"toolCallId": "reference-read", "success": False},
        }])
        self.assertEqual(result["failed_tool_calls"], 1)
        self.assertEqual(result["transport_status"], "failed")

    def test_native_final_result_is_supported_without_exporting_session_ids(self):
        events = self.events() + [{
            "type": "result", "exitCode": 0, "sessionId": "SYNTHETIC_SESSION"
        }]
        result = self.summarize(events)
        self.assertEqual(result["transport_status"], "passed")
        self.assertNotIn("SYNTHETIC_SESSION", json.dumps(result))
        events[-1]["exitCode"] = 1
        self.assertEqual(self.summarize(events)["transport_status"], "failed")


if __name__ == "__main__":
    unittest.main()
