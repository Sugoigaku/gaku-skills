import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
READER_PATH = ROOT / ".github" / "skills" / "case-session-to-wiki" / "tools" / "session_reader.py"
SPEC = importlib.util.spec_from_file_location("session_reader", READER_PATH)
reader = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(reader)
SESSION_ID = "11111111-1111-4111-8111-111111111111"
OTHER_ID = "22222222-2222-4222-8222-222222222222"


def event(kind, **data):
    return {"type": kind, "data": data}


def encoded(records):
    return b"".join((json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8") for record in records)


class SessionReaderTests(unittest.TestCase):
    def setUp(self):
        # Synthetic fixtures stay under this repository, never OS temp or HOME.
        self.fixture = tempfile.TemporaryDirectory(prefix="reader-fixture-", dir=ROOT / "tests")
        self.addCleanup(self.fixture.cleanup)
        self.root = Path(self.fixture.name)
        self.sessions = self.root / "sessions"
        self.session = self.sessions / SESSION_ID
        self.session.mkdir(parents=True)
        self.log = self.session / "events.jsonl"
        self.log.write_bytes(b"")
        self.transcript = self.root / "provided.txt"

    def write(self, *records):
        self.log.write_bytes(encoded(records))

    def read(self, **kwargs):
        return reader.read_page(session_id=SESSION_ID, session_root=self.sessions, **kwargs)

    def gaps(self, page):
        return {gap["reason"]: gap["count"] for gap in page["coverage"]["gaps"]}

    def collect(self, read, budget):
        pages = []
        cursor = None
        for _ in range(10000):
            page = read(cursor=cursor, max_text_chars=budget)
            self.assertLessEqual(sum(len(entry["text"]) for entry in page["entries"]), budget)
            self.assertLessEqual(len(page["entries"]), reader.MAX_ENTRIES)
            pages.append(page)
            cursor = page["next_cursor"]
            if cursor is None:
                return pages
        self.fail("Pagination did not terminate")

    def assert_error(self, code, function, **kwargs):
        with self.assertRaises(reader.ReaderError) as caught:
            function(**kwargs)
        self.assertEqual(code, caught.exception.code)
        output = json.dumps(caught.exception.as_dict())
        self.assertNotIn(SESSION_ID, output)
        self.assertNotIn(str(self.root), output)
        self.assertEqual([], caught.exception.as_dict()["entries"])
        return caught.exception

    def test_hidden_system_context_arguments_and_unknown_events_are_excluded(self):
        hidden = "HIDDEN-SYNTHETIC-SENTINEL"
        self.write(
            event("system.message", content=hidden),
            event("developer.message", content=hidden),
            event("session.start", context=hidden),
            event("session.model_change", model=hidden),
            event("hook.end", content=hidden),
            event("tool.execution_start", arguments={"value": hidden}),
            event("session.assignment", content=hidden),
            event("user.message", content="question", context=hidden, attachments=[{"path": hidden}]),
            event("assistant.message", content="suggestion", reasoningText=hidden,
                  reasoningBlocks=[hidden], reasoningOpaque=hidden, toolRequests=[{"arguments": hidden}]),
            event("tool.execution_complete", success=True, result={"content": "visible"},
                  arguments={"value": hidden}, error=hidden, toolCallId=SESSION_ID),
        )
        page = self.read()
        serialized = json.dumps(page)
        self.assertNotIn(hidden, serialized)
        self.assertNotIn(SESSION_ID, serialized)
        self.assertNotIn(str(self.root), serialized)
        self.assertEqual(["question", "suggestion", "visible"], [e["text"] for e in page["entries"]])
        self.assertEqual(7, self.gaps(page)["excluded_events"])
        self.assertEqual(1, self.gaps(page)["attachment_omissions"])

    def test_successful_tool_allowlist_and_unknown_fields(self):
        secret = "DO-NOT-EMIT-SYNTHETIC"
        self.write(
            event("tool.execution_complete", success=True, result="direct"),
            event("tool.execution_complete", success=True, result={"content": "content", "error": secret}),
            event("tool.execution_complete", success=True, result={
                "content": [{"type": "text", "text": "block", "reasoningText": secret},
                            {"type": "image", "data": secret},
                            {"type": "resource", "resource": {"text": secret}},
                            {"type": "text", "text": {"nested": secret}},
                            {"unknown": secret}],
                "details": secret,
            }),
            event("tool.execution_complete", success=True,
                  result={"type": "text", "text": "typed", "unknown": secret}),
            event("tool.execution_complete", success=True, result={"stdout": secret, "nested": {"text": secret}}),
        )
        page = self.read()
        self.assertEqual(["direct", "content", "block", "typed", ""], [e["text"] for e in page["entries"]])
        self.assertNotIn(secret, json.dumps(page))
        self.assertEqual(2, self.gaps(page)["attachment_omissions"])
        self.assertEqual(4, self.gaps(page)["unsupported_tool_result_block"])
        self.assertEqual(4, self.gaps(page)["unrecognized_tool_result_fields"])
        self.assertEqual(1, self.gaps(page)["unsupported_tool_result"])
        self.assertTrue(all(e["tool_success"] is True for e in page["entries"]))

    def test_assistant_claim_is_not_tool_status_and_failures_have_no_bodies(self):
        self.write(
            event("assistant.message", content="I fixed it successfully.", success=True),
            event("tool.execution_complete", success=False,
                  result="Exception: fake-password", error={"credentials": "fake-password"}),
            event("tool.execution_complete", result="fake-password"),
            event("tool.execution_complete", success="true", result="fake-password"),
            event("tool.execution_complete", success=1, result="fake-password"),
        )
        page = self.read()
        self.assertNotIn("tool_success", page["entries"][0])
        self.assertEqual([False, None, None, None], [e["tool_success"] for e in page["entries"][1:]])
        self.assertNotIn("fake-password", json.dumps(page))
        self.assertEqual(1, self.gaps(page)["failed_tool_body_omitted"])
        self.assertEqual(3, self.gaps(page)["unknown_tool_status"])

    def test_strict_content_types_and_empty_results(self):
        self.write(
            *[event("user.message", content=value) for value in (None, 4, True, [], {"text": "not exposed"})],
            *[event("tool.execution_complete", success=True, result=value)
              for value in (None, 4, True, [], {"content": 1}, {"content": []})],
        )
        page = self.read()
        self.assertEqual(6, len(page["entries"]))
        self.assertTrue(all(e["text"] == "" for e in page["entries"]))
        self.assertEqual(5, self.gaps(page)["unsupported_message_content"])
        self.assertEqual(6, self.gaps(page)["tool_result_without_visible_text"])

    def test_tool_block_locators_do_not_lose_original_indices(self):
        self.write(event("tool.execution_complete", success=True, result={"content": [
            {"type": "text", "text": "a"}, {"type": "image", "data": "omitted"},
            {"type": "text", "text": "b"},
        ]}))
        entries = self.read()["entries"]
        self.assertEqual(["E1.0", "E1.2"], [e["id"] for e in entries])
        self.assertEqual([0, 2], [e["locator"]["part"] for e in entries])

    def test_exact_uuid_validation(self):
        for value in (
            "", "..", "../" + SESSION_ID, SESSION_ID + "/events.jsonl",
            "{" + SESSION_ID + "}", SESSION_ID.replace("-", ""), SESSION_ID + " ",
            "AAAAAAAA-AAAA-4AAA-8AAA-AAAAAAAAAAAA", 1,
        ):
            with self.subTest(value=value):
                self.assert_error("invalid_arguments", reader.read_page,
                                  session_id=value, session_root=self.sessions)

    def test_selection_arguments_and_limits(self):
        invalid = [
            {}, {"session_id": SESSION_ID, "transcript": self.transcript},
            {"transcript": self.transcript, "session_root": self.sessions},
        ]
        for arguments in invalid:
            self.assert_error("invalid_arguments", reader.read_page, **arguments)
        for value in (0, -1, True, 2.0, "5", reader.MAX_TEXT_CHARS + 1):
            self.assert_error("invalid_arguments", self.read, max_text_chars=value)

    def test_paths_reject_traversal_aliases_and_expansion(self):
        for value in (
            self.root / ".." / "provided.txt", ".", "", "NUL", "file.txt:stream",
            r"\\server\share\source", r"\\?\C:\source", "trailing.", "trailing ",
            "*.txt", "C:relative.txt", "file\0name",
        ):
            with self.subTest(value=str(value)):
                self.assert_error("unsafe_path", reader.read_page, transcript=value)
        self.assert_error("unsafe_path", reader.read_page, session_id=SESSION_ID,
                          session_root=str(self.sessions) + "\\..\\sessions")

    def test_missing_source_and_directory_are_sanitized(self):
        self.assert_error("source_unavailable", reader.read_page, transcript=self.transcript)
        self.assert_error("unsupported_source", reader.read_page, transcript=self.root)

    def test_default_root_resolves_only_selected_synthetic_session(self):
        home = self.root / "home"
        selected = home / ".copilot" / "session-state" / SESSION_ID
        selected.mkdir(parents=True)
        (selected / "events.jsonl").write_bytes(encoded([event("user.message", content="selected")]))
        other = selected.parent / OTHER_ID
        other.mkdir()
        (other / "events.jsonl").write_bytes(b"invalid-other-session\n")
        with mock.patch.object(Path, "home", return_value=home):
            self.assertEqual("selected", reader.read_page(session_id=SESSION_ID)["entries"][0]["text"])

    def test_session_file_and_directory_symlinks_are_refused(self):
        target = self.root / "outside.txt"
        target.write_text("synthetic outside text", encoding="utf-8")
        self.log.unlink()
        try:
            self.log.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("This account/platform cannot create symlinks")
        self.assert_error("unsafe_path", self.read)
        self.log.unlink()
        self.session.rmdir()
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "events.jsonl").write_bytes(b"")
        self.session.symlink_to(outside, target_is_directory=True)
        self.addCleanup(self.session.unlink)
        self.assert_error("unsafe_path", self.read)

    def test_transcript_and_selected_root_symlinks_are_refused(self):
        target = self.root / "target.txt"
        target.write_text("text", encoding="utf-8")
        try:
            self.transcript.symlink_to(target)
        except (OSError, NotImplementedError):
            self.skipTest("This account/platform cannot create symlinks")
        self.assert_error("unsafe_path", reader.read_page, transcript=self.transcript)
        root_link = self.root / "root-link"
        root_link.symlink_to(self.sessions, target_is_directory=True)
        self.addCleanup(root_link.unlink)
        self.assert_error("unsafe_path", reader.read_page, session_id=SESSION_ID, session_root=root_link)

    def test_reparse_flag_is_refused_even_without_link_creation_privilege(self):
        original = Path.lstat
        for reparse_path in (self.sessions, self.session, self.log):
            with self.subTest(component=reparse_path.name):
                def reparse_stat(path, *args, **kwargs):
                    actual = original(path, *args, **kwargs)
                    if path == reparse_path:
                        return SimpleNamespace(st_mode=actual.st_mode, st_file_attributes=0x400)
                    return actual

                with mock.patch.object(Path, "lstat", reparse_stat):
                    self.assert_error("unsafe_path", self.read)

    @unittest.skipUnless(os.name == "nt", "Windows junction test")
    def test_windows_junction_to_outside_root_is_refused(self):
        outside = self.root / "junction-target"
        outside.mkdir()
        (outside / "events.jsonl").write_bytes(b"")
        self.log.unlink()
        self.session.rmdir()
        command = f'mklink /J "{self.session}" "{outside}"'
        made = subprocess.run([os.environ.get("COMSPEC", "cmd.exe"), "/c", command],
                              capture_output=True, check=False)
        if made.returncode:
            self.skipTest("Junction creation is not supported here")
        self.addCleanup(os.rmdir, self.session)
        self.assert_error("unsafe_path", self.read)

    def test_malformed_complete_records_fail_before_any_page_is_returned(self):
        invalids = [
            b"{broken}\n", b"\n", b"[]\n", b'{"type": 1}\n',
            b'{"type":"user.message","data":[]}\n',
            b'{"type":"user.message","content":"wrong envelope"}\n',
            b'{"type":"user.message","data":{"content":"x","content":"y"}}\n',
            b'{"type":"ignored","data":{"value":NaN}}\n',
        ]
        for raw in invalids:
            with self.subTest(raw=raw):
                self.log.write_bytes(encoded([event("user.message", content="already fills budget")]) + raw)
                failure = self.assert_error("malformed_record", self.read, max_text_chars=1)
                self.assertEqual(2, failure.record)

    def test_empty_source_has_no_invented_case_coverage(self):
        for kind in ("events", "transcript"):
            self.transcript.write_bytes(b"")
            page = self.read() if kind == "events" else reader.read_page(transcript=self.transcript)
            self.assertEqual([], page["entries"])
            self.assertIsNone(page["next_cursor"])
            self.assertEqual(0, page["coverage"]["snapshot_text_chars"])
            self.assertTrue(page["coverage"]["visible_snapshot_complete"])
            self.assertEqual("not-asserted", page["coverage"]["case_coverage"])

    def test_utf8_and_transcript_crlf_bom_are_preserved(self):
        text = "\ufeffSynthetic café 日本語 😀\r\nsecond line\r\n"
        self.transcript.write_bytes(text.encode("utf-8"))
        pages = self.collect(lambda **kwargs: reader.read_page(transcript=self.transcript, **kwargs), 3)
        self.assertEqual(text, "".join(e["text"] for p in pages for e in p["entries"]))
        self.write(event("user.message", content=text))
        self.assertEqual(text, self.read()["entries"][0]["text"])

    def test_utf8_invalid_complete_evidence_fails_closed(self):
        self.log.write_bytes(b'{"type":"user.message","data":{"content":"\xff"}}\n')
        self.assert_error("invalid_utf8", self.read)
        self.log.write_bytes(b'{"type":"user.message","data":{"content":"\\ud800"}}\n')
        self.assert_error("invalid_utf8", self.read)
        self.transcript.write_bytes(b"start\xff")
        self.assert_error("invalid_utf8", reader.read_page, transcript=self.transcript)
        self.transcript.write_bytes(b"start\xf0\x9f")
        self.assert_error("invalid_utf8", reader.read_page, transcript=self.transcript)

    def test_pagination_is_deterministic_lossless_and_located(self):
        originals = ["alpha😀\n" * 15, "", "beta" * 20, "final"]
        self.write(
            event("user.message", content=originals[0]),
            event("assistant.message", content=originals[1]),
            event("tool.execution_complete", success=True, result=originals[2]),
            event("user.message", content=originals[3]),
        )
        self.assertEqual(self.read(max_text_chars=7), self.read(max_text_chars=7))
        for budget in (1, 7, 1000):
            with self.subTest(budget=budget):
                pages = self.collect(self.read, budget)
                extracted = {}
                offsets = {}
                returned = 0
                for page in pages:
                    for entry in page["entries"]:
                        key = entry["id"]
                        self.assertEqual(offsets.get(key, 0), entry["locator"]["char_start"])
                        offsets[key] = entry["locator"]["char_end"]
                        extracted[key] = extracted.get(key, "") + entry["text"]
                        returned += len(entry["text"])
                    self.assertEqual(sum(map(len, originals)) - returned,
                                     page["coverage"]["unread_segments"]["text_chars"])
                self.assertEqual(originals, list(extracted.values()))
                self.assertTrue(pages[-1]["coverage"]["visible_snapshot_complete"])

    def test_transcript_spans_buffers_and_unicode_boundaries_without_loss(self):
        text = "a" * (reader.READ_BYTES - 1) + "😀\r\n" + "é" * reader.READ_BYTES
        self.transcript.write_bytes(text.encode("utf-8"))
        pages = self.collect(lambda **kwargs: reader.read_page(transcript=self.transcript, **kwargs), 1234)
        rebuilt = ""
        for page in pages:
            for entry in page["entries"]:
                self.assertEqual(len(rebuilt), entry["locator"]["char_start"])
                rebuilt += entry["text"]
                self.assertEqual(len(rebuilt), entry["locator"]["char_end"])
        self.assertEqual(text, rebuilt)

    def test_empty_statuses_are_entry_bounded_and_paginate(self):
        self.write(*[event("tool.execution_complete", success=False, result="private") for _ in range(205)])
        pages = self.collect(self.read, 1)
        self.assertEqual([100, 100, 5], [len(p["entries"]) for p in pages])
        self.assertEqual(205, len({e["id"] for p in pages for e in p["entries"]}))
        self.assertEqual(105, pages[0]["coverage"]["unread_segments"]["text_units"])
        self.assertEqual(0, pages[0]["coverage"]["unread_segments"]["text_chars"])

    def test_cursor_roundtrip_binding_validation_and_budget_change(self):
        self.write(event("user.message", content="abcdef"))
        token = self.read(max_text_chars=1)["next_cursor"]
        self.assertIsInstance(token, str)
        self.assertNotIn(SESSION_ID, token)
        self.assertEqual("bcdef", self.read(cursor=token, max_text_chars=10)["entries"][0]["text"])
        for bad in ("", token + "=", "!", "a" * 3000, "A" + token[1:], 4):
            if bad == token:
                continue
            self.assert_error("invalid_cursor", self.read, cursor=bad)
        self.transcript.write_text("abcdef", encoding="utf-8")
        self.assert_error("invalid_cursor", reader.read_page, transcript=self.transcript, cursor=token)
        other = self.sessions / OTHER_ID
        other.mkdir()
        (other / "events.jsonl").write_bytes(self.log.read_bytes())
        self.assert_error("invalid_cursor", reader.read_page, session_id=OTHER_ID,
                          session_root=self.sessions, cursor=token)

    def test_cursor_strict_types_unknown_fields_and_invalid_positions(self):
        self.write(event("user.message", content="abcdef"))
        original = reader._cursor_decode(self.read(max_text_chars=1)["next_cursor"])
        for field, value in (("unit", True), ("offset", -1), ("unit", 100),
                             ("offset", 6), ("identity", "invalid"), ("v", True),
                             ("size", "100"), ("digest", "bad"), ("unknown", "ignored")):
            modified = {**original, field: value}
            self.assert_error("invalid_cursor", self.read, cursor=reader._cursor_encode(modified))

    def test_append_is_unread_and_original_snapshot_stays_stable(self):
        self.write(event("user.message", content="abcdef"))
        first = self.read(max_text_chars=2)
        appended = encoded([event("assistant.message", content="new turn")])
        with self.log.open("ab") as stream:
            stream.write(appended)
        resumed = self.read(cursor=first["next_cursor"])
        self.assertEqual("cdef", resumed["entries"][0]["text"])
        self.assertEqual(len(appended), resumed["coverage"]["unread_segments"]["appended_bytes"])
        self.assertEqual(first["coverage"]["snapshot_bytes"], resumed["coverage"]["snapshot_bytes"])
        self.assertEqual(["abcdef", "new turn"], [e["text"] for e in self.read()["entries"]])

    def test_prefix_mutation_even_after_append_is_rejected(self):
        self.write(event("user.message", content="abcdef"))
        first = self.read(max_text_chars=1)
        original_time = self.log.stat().st_mtime_ns
        original_bytes = self.log.read_bytes()
        self.log.write_bytes(original_bytes.replace(b"abcdef", b"zbcdef") + encoded([
            event("assistant.message", content="append")
        ]))
        os.utime(self.log, ns=(original_time, original_time))
        self.assert_error("source_changed", self.read, cursor=first["next_cursor"])

    def test_truncation_and_replacement_are_rejected(self):
        self.write(event("user.message", content="abcdef"))
        first = self.read(max_text_chars=1)
        original = self.log.read_bytes()
        self.log.write_bytes(original[:-3])
        self.assert_error("source_changed", self.read, cursor=first["next_cursor"])
        self.log.write_bytes(original)
        first = self.read(max_text_chars=1)
        replacement = self.session / "replacement.jsonl"
        replacement.write_bytes(original)
        replacement.replace(self.log)
        self.assert_error("source_changed", self.read, cursor=first["next_cursor"])

    def test_same_size_touch_is_rejected(self):
        self.write(event("user.message", content="abcdef"))
        first = self.read(max_text_chars=1)
        original = self.log.stat()
        os.utime(self.log, ns=(original.st_atime_ns, original.st_mtime_ns + 1_000_000_000))
        self.assert_error("source_changed", self.read, cursor=first["next_cursor"])

    def test_transcript_append_and_mutation_obey_snapshot(self):
        self.transcript.write_bytes(b"abcdef")
        first = reader.read_page(transcript=self.transcript, max_text_chars=2)
        with self.transcript.open("ab") as stream:
            stream.write(b"new")
        page = reader.read_page(transcript=self.transcript, cursor=first["next_cursor"])
        self.assertEqual("cdef", page["entries"][0]["text"])
        self.assertEqual(3, page["coverage"]["unread_segments"]["appended_bytes"])
        self.transcript.write_bytes(b"zbcdefnew")
        self.assert_error("source_changed", reader.read_page, transcript=self.transcript,
                          cursor=first["next_cursor"])

    def test_trailing_partial_attachment_omissions_and_later_completion(self):
        self.write(event("user.message", content="abcdef", attachments=[{"path": "never-open"}]))
        fragment = b'{"type":"user.message","data":{"content":"new'
        with self.log.open("ab") as stream:
            stream.write(fragment)
        first = self.read(max_text_chars=2)
        self.assertEqual(len(fragment), first["coverage"]["unread_segments"]["trailing_partial_bytes"])
        self.assertEqual(2, first["coverage"]["trailing_partial_record"])
        self.assertEqual(1, self.gaps(first)["attachment_omissions"])
        with self.log.open("ab") as stream:
            stream.write(b'"}}\n')
        page = self.read(cursor=first["next_cursor"])
        self.assertEqual("cdef", page["entries"][0]["text"])
        self.assertFalse(page["coverage"]["visible_snapshot_complete"])
        self.assertEqual(4, page["coverage"]["unread_segments"]["appended_bytes"])
        self.assertEqual(["abcdef", "new"], [e["text"] for e in self.read()["entries"]])

    def test_uncommitted_valid_json_or_invalid_utf8_is_not_emitted(self):
        for raw in (encoded([event("user.message", content="not committed")])[:-1], b"\xff\xf0"):
            self.log.write_bytes(raw)
            page = self.read()
            self.assertEqual([], page["entries"])
            self.assertEqual(len(raw), page["coverage"]["unread_segments"]["trailing_partial_bytes"])
            self.assertFalse(page["coverage"]["visible_snapshot_complete"])

    def test_oversized_record_is_a_bounded_failure(self):
        self.log.write_bytes(b" " * (reader.MAX_RECORD_BYTES + 1) + b"\n")
        self.assert_error("record_too_large", self.read)

    def test_mutation_during_final_verification_is_rejected(self):
        self.write(event("user.message", content="abcdef"))
        actual = reader._Snapshot.read
        calls = 0

        def changing_read(snapshot, size, *, line=False):
            nonlocal calls
            data = actual(snapshot, size, line=line)
            calls += 1
            if calls == 2:
                before = self.log.stat()
                os.utime(self.log, ns=(before.st_atime_ns, before.st_mtime_ns + 1_000_000_000))
            return data

        with mock.patch.object(reader._Snapshot, "read", changing_read):
            self.assert_error("source_changed", self.read)

    def test_verification_rereads_bytes_not_buffered_scan_content(self):
        self.write(event("user.message", content="abcdef"))
        original_bytes = self.log.read_bytes()
        original_time = self.log.stat()
        actual = reader._Snapshot.read
        calls = 0

        def changing_read(snapshot, size, *, line=False):
            nonlocal calls
            data = actual(snapshot, size, line=line)
            calls += 1
            if calls == 1:
                self.log.write_bytes(original_bytes.replace(b"abcdef", b"zbcdef"))
                os.utime(self.log, ns=(original_time.st_atime_ns, original_time.st_mtime_ns))
            return data

        with mock.patch.object(reader._Snapshot, "read", changing_read):
            self.assert_error("source_changed", self.read)

    def test_invalid_utf8_beyond_transcript_page_budget_discards_page(self):
        self.transcript.write_bytes(b"a" * (reader.READ_BYTES + 10) + b"\xff")
        self.assert_error("invalid_utf8", reader.read_page, transcript=self.transcript,
                          max_text_chars=1)

    def test_reader_opens_only_selected_source_and_never_writes(self):
        self.write(event("user.message", content="safe", attachments=[{"path": str(self.transcript)}]))
        real_open = os.open
        opened = []

        def checked_open(path, flags, *args, **kwargs):
            opened.append(Path(path))
            self.assertEqual(self.log, Path(path))
            self.assertFalse(flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC))
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(reader.os, "open", checked_open):
            page = self.read()
        self.assertEqual([self.log], opened)
        self.assertEqual("safe", page["entries"][0]["text"])
        self.assertFalse(self.transcript.exists())

    def test_cli_argument_errors_are_nonzero_json_without_raw_arguments(self):
        bad_args = [
            [], ["--session-id", "../private-value"],
            ["--transcript", "private-value", "--session-id", SESSION_ID],
            ["--transcript", "private-value", "--max-text-chars", "fake-password"],
            ["--transcript", "private-value", "--session-root", "private-root"],
            ["--unknown-secret", "fake-password"], ["--session-id"],
            ["--transcript", str(self.transcript)],
        ]
        for arguments in bad_args:
            with self.subTest(arguments=arguments):
                result = subprocess.run([sys.executable, "-B", str(READER_PATH), *arguments],
                                        cwd=ROOT, capture_output=True, text=True, check=False)
                self.assertNotEqual(0, result.returncode)
                self.assertEqual("", result.stderr)
                body = json.loads(result.stdout)
                self.assertIn("error", body)
                for hidden in ("fake-password", "private-value", SESSION_ID, str(self.root)):
                    self.assertNotIn(hidden, result.stdout)

    def test_cli_success_and_help_are_json(self):
        self.transcript.write_bytes("visible 😀".encode("utf-8"))
        result = subprocess.run(
            [sys.executable, "-B", str(READER_PATH), "--transcript", str(self.transcript)],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)
        self.assertEqual("visible 😀", json.loads(result.stdout)["entries"][0]["text"])
        with contextlib.redirect_stdout(io.StringIO()) as output:
            self.assertEqual(0, reader.main(["--help"]))
        self.assertIn("usage", json.loads(output.getvalue()))


if __name__ == "__main__":
    unittest.main()
