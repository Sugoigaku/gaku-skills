import json
import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".github" / "skills" / "case-session-to-wiki"
SUPPORTING = {
    "session-workflow.md", "authoring.md", "sources.md",
    "evidence-review.md", "templates.md", "diagrams.md",
}
VERSION = "Version: 0.8.0. Last reviewed: 2026-09-16."
HEADINGS = {
    "qa": ["Questions and answers", "References", "Double-check"],
    "how-to": [
        "Goal", "Before you start", "Steps", "Check the result",
        "References", "Double-check",
    ],
    "break-fix": [
        "Problem", "Before you start", "Identify the issue", "Steps",
        "Check the result", "References", "Double-check",
    ],
}


def read(name):
    return (SKILL_DIR / name).read_text(encoding="utf-8")


def markdown_links(text):
    prose = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*(?=\n|$)", "", text)
    prose = re.sub(r"(`+).*?\1", "", prose, flags=re.DOTALL)
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", prose)


def templates():
    blocks = re.findall(r"(?ms)^```markdown\n(---\n.*?)^```\s*$", read("templates.md"))
    return {
        re.search(r"(?m)^wiki_type: (.+)$", block).group(1): block
        for block in blocks
    }


class BundleContractTests(unittest.TestCase):
    def test_actual_bundle_contains_expected_markdown_documents(self):
        files = {
            path.relative_to(SKILL_DIR).as_posix(): path.read_bytes()
            for path in SKILL_DIR.rglob("*") if path.is_file()
        }
        self.assertEqual(set(files), SUPPORTING | {"SKILL.md"})
        for name, content in files.items():
            with self.subTest(name=name):
                self.assertEqual(Path(name).suffix, ".md")
                self.assertFalse(content.startswith(b"\xef\xbb\xbf"))
                self.assertNotIn("\x00", content.decode("utf-8"))

    def test_bundle_contains_no_runtime_helper_code_or_personal_identifiers(self):
        for path in SKILL_DIR.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                self.assertNotRegex(text, r"(?mi)^```(?:python|powershell|bash|javascript)\s*$")
                self.assertNotRegex(text, r"(?i)\b(?:session_reader|validate_wiki|create_output_directory)\.py\b")
                self.assertNotRegex(text, r"(?i)\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b")
                self.assertNotRegex(text, r"(?i)\b[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}\b")
                self.assertNotRegex(text, r"(?i)[a-z]:\\Users\\")
                self.assertNotRegex(text, r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")


class SkillFrameworkTests(unittest.TestCase):
    def test_discoverable_skill_has_required_front_matter(self):
        match = re.match(r"\A---\n(.*?)\n---\n", read("SKILL.md"), re.DOTALL)
        self.assertIsNotNone(match)
        self.assertRegex(match.group(1), rf"(?m)^name: {SKILL_DIR.name}$")
        description = re.search(r'(?m)^description: "(.+)"$', match.group(1))
        self.assertIsNotNone(description)
        self.assertLessEqual(len(description.group(1)), 1024)

    def test_all_supporting_documents_are_wired_from_skill(self):
        self.assertEqual(set(markdown_links(read("SKILL.md"))) & SUPPORTING, SUPPORTING)

    def test_examples_are_not_treated_as_live_links(self):
        text = (
            "[real](README.md)\n`[inline](missing.json)`\n"
            "```markdown\n[example](missing.md)\n```\n"
            "````markdown\n```text\n[nested](missing.md)\n```\n````\n"
            "[other](tests/scenarios.md)\n"
        )
        self.assertEqual(markdown_links(text), ["README.md", "tests/scenarios.md"])

    def test_local_links_and_heading_anchors_resolve(self):
        documents = [ROOT / "README.md", ROOT / "tests" / "scenarios.md"]
        documents.extend(SKILL_DIR.glob("*.md"))
        for document in documents:
            for link in markdown_links(document.read_text(encoding="utf-8")):
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc:
                    continue
                target = (document.parent / unquote(parsed.path)).resolve() if parsed.path else document
                with self.subTest(document=document.name, link=link):
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.exists(), f"Missing target: {target}")
                    if parsed.fragment:
                        self.assertTrue(target.is_file())
                        headings = re.findall(r"(?m)^#+ (.+)$", target.read_text(encoding="utf-8"))
                        anchors = {
                            re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                            for heading in headings
                        }
                        self.assertIn(unquote(parsed.fragment), anchors)

    def test_skill_declares_release(self):
        self.assertIn(VERSION, read("SKILL.md"))

    def test_readme_documents_wiki_purpose_and_install(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        section = text.split("## case-session-to-wiki\n", 1)[1].split(
            "## Download\n", 1
        )[0]
        self.assertIn("QA, How-to, or Break-fix", section)
        self.assertIn("Does not publish automatically", section)
        self.assertIn(".github/skills/case-session-to-wiki", section)
        self.assertIn("--source .github\\skills\\case-session-to-wiki", text)
        self.assertIn(
            '--destination "%USERPROFILE%\\.copilot\\skills\\case-session-to-wiki"',
            text,
        )

    def test_three_templates_keep_order_and_conservative_metadata(self):
        self.assertEqual(set(templates()), set(HEADINGS))
        for kind, text in templates().items():
            with self.subTest(kind=kind):
                self.assertEqual(re.findall(r"(?m)^## (.+)$", text), HEADINGS[kind])
                self.assertEqual(len(re.findall(r"(?m)^# ", text)), 1)
                for field in (
                    f"wiki_type: {kind}", "article_format: concise", "status: draft",
                    "review_status: pending-engineer-review", "validation_method: agent-checklist",
                    "source_kind: current-session", "source_coverage: partial",
                    "content_mode: documentation-enriched", "reference_status: incomplete",
                ):
                    self.assertRegex(text, rf"(?m)^{re.escape(field)}$")
                self.assertIn("[Evidence details](evidence.json)", text)
                self.assertNotIn("**Provenance:**", text)
                self.assertNotIn("**Conditions and exceptions:**", text)

    def test_outcomes_are_type_specific(self):
        for kind, text in templates().items():
            for field, expected in {
                "procedure_status": "unverified" if kind == "how-to" else None,
                "root_cause_status": "unknown" if kind == "break-fix" else None,
                "resolution_status": "unverified" if kind == "break-fix" else None,
            }.items():
                with self.subTest(kind=kind, field=field):
                    if expected:
                        self.assertRegex(text, rf"(?m)^{field}: {expected}$")
                    else:
                        self.assertNotRegex(text, rf"(?m)^{field}:")

    def test_qa_and_steps_remain_detailed_without_repeated_forms(self):
        self.assertRegex(templates()["qa"], r"(?m)^### Q1\.")
        for kind in ("how-to", "break-fix"):
            text = templates()[kind]
            self.assertRegex(text, r"(?m)^### Step 1 - ")
            for term in ("numbered substeps", "command block", "Notes"):
                self.assertIn(term, text)
            self.assertLess(text.index("## Before you start"), text.index("## Steps"))
            self.assertNotRegex(text, r"(?m)^\*\*(?:Where|Why|Impact|Rollback):")
        detail = read("authoring.md")
        for term in ("how to apply/save", "Initialize required variables", "No\n  ellipses"):
            self.assertIn(term, detail)

    def test_internal_topic_plan_and_partial_set_delivery_are_preserved(self):
        text = read("authoring.md")
        self.assertIn("| ID | Topic | Wiki type | Reader task and scope |", text)
        self.assertIn("three-format cross product", text)
        self.assertIn("later\nquestions and corrections", text)
        for outcome in ("saved", "blocked", "failed", "deferred"):
            self.assertIn(f"`{outcome}`", text)

    def test_native_input_does_not_recreate_raw_archive_reader(self):
        text = read("session-workflow.md")
        for term in (
            "Never list or search other", "raw archive", "Do not improvise structural event filtering.",
            "Do not use alternate tools to bypass access denial or content exclusion.",
            "Do not silently switch sessions", "linked files",
        ):
            self.assertIn(term.lower(), text.lower())
        self.assertIn("reconstruct the removed helpers", read("SKILL.md"))

    def test_coverage_cannot_be_promoted_from_pasted_or_summarized_input(self):
        text = read("session-workflow.md")
        for term in (
            "partial` for all current-context and local-session reads",
            "complete-for-provided-transcript", "confirmed EOF",
            "file did not change", "Pasted text is `current-session` and partial",
        ):
            self.assertIn(term, text)

    def test_save_requires_correct_session_create_only_and_full_readback(self):
        text = read("session-workflow.md")
        for term in (
            "that source session's directory", "not the invoking session",
            "create-only", "not\nan atomic no-overwrite guarantee",
            "stop and report that limitation", "Read each saved file back internally",
            "stop further writes", "Do not\n   delete partial output",
            "each saved Wiki's", "full absolute file path", "List the evidence companion separately",
        ):
            self.assertIn(term, text)

    def test_checklist_does_not_claim_machine_or_independent_approval(self):
        text = read("evidence-review.md")
        for term in (
            "no executable validator", "agent-applied", "checklist-checked",
            "never assigns `mechanically-checked` or `complete`",
            "Generator self-review is not independent review",
            "Any article/evidence edit invalidates prior review",
        ):
            self.assertIn(term.lower(), text.lower())
        for check in (
            "Claim coverage", "Original quotation", "Entailment and scope", "Privacy",
            "Chronology", "Delivery", "Enrichment and outcomes",
        ):
            self.assertIn(f"| {check} |", text)

    def test_privacy_and_enrichment_rules_remain_explicit(self):
        text = read("sources.md")
        for term in (
            "exact", "private archive", "reverse map", "Never send customer names",
            "`extraction-only`", "`not-run`", "cannot inherit",
            "accept-all certificate", "preserve-view", "access-controlled",
            "Keep interpretation outside", "original language",
        ):
            self.assertIn(term, text)

    def test_source_entry_keeps_short_original_and_locator(self):
        text = read("templates.md").split("## Source entry\n", 1)[1]
        for field in ("Source", "Location", "Original excerpt"):
            self.assertIn(f"**{field}:**", text)
        self.assertIn("**Excerpt handling:** redacted", text)
        self.assertRegex(text, r"(?m)^> <.+>$")

    def test_mermaid_only_has_sourced_caption_and_text_fallback(self):
        text = read("diagrams.md")
        for term in (
            "`Diagram:`", "companion", "No click handlers", "plain-text explanation",
            "does not generate SVG", "rendering as unverified", "Never upload",
        ):
            self.assertIn(term, text)

    def test_evidence_example_preserves_v1_schema_and_consistent_ids(self):
        blocks = re.findall(r"(?ms)^```json\n(.*?)^```", read("evidence-review.md"))
        self.assertEqual(len(blocks), 1)

        def unique_object(pairs):
            result = {}
            for key, value in pairs:
                self.assertNotIn(key, result, f"Duplicate example key: {key}")
                result[key] = value
            return result

        evidence = json.loads(blocks[0], object_pairs_hook=unique_object)
        self.assertEqual(set(evidence), {"schema_version", "sources", "articles"})
        self.assertIs(type(evidence["schema_version"]), int)
        self.assertEqual(evidence["schema_version"], 1)
        source = evidence["sources"][0]
        self.assertEqual(set(source), {
            "id", "kind", "title", "publisher", "origin", "locator", "version",
            "inspection_status", "text", "excerpt_handling",
        })
        self.assertEqual(source["kind"], "sanitized-evidence")
        self.assertEqual(source["locator"], "Lines 1")
        self.assertEqual(len(source["text"].splitlines()), 1)
        article = evidence["articles"][0]
        self.assertEqual(set(article), {"file", "claims", "enrichments"})
        self.assertEqual(article["enrichments"], [])
        self.assertEqual(set(article["claims"][0]), {"id", "text", "source_ids", "basis"})
        self.assertEqual(article["claims"][0]["source_ids"], [source["id"]])
        self.assertEqual(article["claims"][0]["basis"], "reported")

    def test_case_artifact_paths_are_ignored_but_skill_is_not(self):
        paths = (
            "wiki-drafts/topic.md", "private-inputs/transcript.md",
            "tests/__pycache__/test_skill_framework.cpython-313.pyc",
            ".github/skills/case-session-to-wiki/SKILL.md",
        )
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "--no-index", "--stdin", "-z"],
            input="\0".join(paths) + "\0", text=True, capture_output=True, check=True,
        )
        self.assertEqual(set(result.stdout.split("\0")[:-1]), set(paths[:3]))


if __name__ == "__main__":
    unittest.main()
