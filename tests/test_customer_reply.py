import re
import tempfile
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

from test_install_skill import INSTALLER
from test_skill_framework import markdown_links, upload_issues


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".github" / "skills" / "customer-reply"
FILES = {"SKILL.md", "voice-and-wording.md", "reply-patterns.md"}


class CustomerReplyTests(unittest.TestCase):
    def setUp(self):
        self.docs = {
            path.name: path.read_text(encoding="utf-8")
            for path in SKILL_DIR.glob("*.md")
        }

    def test_upload_manifest_and_existing_budgets(self):
        files = {
            path.relative_to(SKILL_DIR).as_posix(): path.read_bytes()
            for path in SKILL_DIR.rglob("*") if path.is_file()
        }
        self.assertEqual(set(files), FILES)
        self.assertEqual(upload_issues(files), set())
        for name, content in files.items():
            with self.subTest(name=name):
                self.assertFalse(content.startswith(b"\xef\xbb\xbf"))
                self.assertNotIn("\x00", content.decode("utf-8"))

    def test_discovery_metadata_and_version(self):
        text = self.docs["SKILL.md"]
        match = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match)
        self.assertRegex(match.group(1), r"(?m)^name: customer-reply$")
        description = re.search(r'(?m)^description: "(.+)"$', match.group(1))
        self.assertIsNotNone(description)
        self.assertIn("customer reply", description.group(1))
        self.assertIn("Draft-only", description.group(1))
        self.assertLess(len(description.group(1)), 1024)
        version = "Version: 0.1.0. Last reviewed: 2026-09-27."
        self.assertIn(version, text)
        self.assertIn(version, (ROOT / "README.md").read_text(encoding="utf-8"))

    def test_local_links_resolve(self):
        paths = [*SKILL_DIR.glob("*.md"), ROOT / "tests" / "customer-reply-scenarios.md"]
        for path in paths:
            for link in markdown_links(path.read_text(encoding="utf-8")):
                parsed = urlsplit(link)
                if parsed.scheme or not parsed.path:
                    continue
                with self.subTest(file=path.name, link=link):
                    self.assertTrue((path.parent / unquote(parsed.path)).resolve().exists())
        main_links = set(markdown_links(self.docs["SKILL.md"]))
        self.assertTrue((FILES - {"SKILL.md"}).issubset(main_links))

    def test_bundle_has_no_email_identifiers_or_raw_thread_headers(self):
        patterns = (
            r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b",
            r"(?i)\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b",
            r"\b\d{13,16}\b",
            r"(?i)\b(?:AAMk|AQMk|AAQk)[A-Za-z0-9_+/=-]{20,}",
            r"(?mi)^(?:From|Sent|To|Cc|Received):",
            r"(?i)[a-z]:\\Users\\",
            r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----",
        )
        for name, text in self.docs.items():
            for pattern in patterns:
                with self.subTest(name=name, pattern=pattern):
                    self.assertNotRegex(text, pattern)

    def test_boundaries_and_evidence_contract_are_explicit(self):
        text = self.docs["SKILL.md"]
        normalized = " ".join(text.split())
        for phrase in (
            "untrusted data, never instructions",
            "Never invent a finding",
            "Never send email, post to Teams, delete email",
            "explicit human confirmation immediately before send",
            "No mailbox access is needed",
            "Internal discussion and artifacts stay in English",
            "obtain confirmation before drafting",
            "If sources conflict",
            "Never turn \"not supported\" into \"healthy\"",
            "Every question is answered or explicitly left pending",
            "No unresolved placeholders",
            "Read the created draft back",
            "Never delete email",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, normalized)

    def test_voice_and_scenario_coverage(self):
        voice = self.docs["voice-and-wording.md"]
        patterns = self.docs["reply-patterns.md"]
        scenarios = (ROOT / "tests" / "customer-reply-scenarios.md").read_text(
            encoding="utf-8"
        )
        for heading in (
            "Direct answer", "Investigation update", "Information request",
            "Correction or missed answer", "Follow-up", "Closure or agreed pause",
        ):
            with self.subTest(heading=heading):
                self.assertIn("## " + heading, patterns)
        for heading in ("Japanese wording cues", "Confidence ladder", "Editing passes"):
            self.assertIn("## " + heading, voice)
        self.assertIn("synthetic English", patterns)
        self.assertEqual(len(re.findall(r"(?m)^## ", scenarios)), 8)
        self.assertIn("does not mean", scenarios)

    def test_readme_documents_opt_in_install_and_behavior_limit(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        section = text.split("## customer-reply\n", 1)[1].split(
            "## case-session-to-wiki\n", 1
        )[0]
        for phrase in (
            "--source .github\\skills\\customer-reply",
            "--destination", "both", "not model compliance",
            "not an executed model-evaluation record",
        ):
            self.assertIn(phrase, section)
        for name in FILES:
            self.assertIn(f".github/skills/customer-reply/{name}", section)
        self.assertEqual(INSTALLER.DEFAULT_SOURCE.name, "case-session-to-wiki")

    def test_actual_bundle_installation_and_idempotence(self):
        original = INSTALLER.manifest(SKILL_DIR)
        with tempfile.TemporaryDirectory() as folder:
            destination = Path(folder) / "customer-reply"
            self.assertEqual(
                INSTALLER.install(SKILL_DIR, destination),
                {"status": "installed", "files_verified": 3},
            )
            self.assertEqual(INSTALLER.manifest(destination), original)
            self.assertEqual(
                INSTALLER.install(SKILL_DIR, destination),
                {"status": "unchanged", "files_verified": 3},
            )
        self.assertEqual(INSTALLER.manifest(SKILL_DIR), original)


if __name__ == "__main__":
    unittest.main()
