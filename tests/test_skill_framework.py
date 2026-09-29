import re
import subprocess
import unittest
from pathlib import Path, PureWindowsPath
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".github" / "skills" / "case-session-to-wiki"
SUPPORTING = {
    "session-workflow.md", "authoring.md", "sources.md",
    "evidence-review.md", "templates.md", "diagrams.md",
}
VERSION = "Version: 0.10.0. Last reviewed: 2026-09-29."
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
        self.assertLessEqual(len(description.group(1)), 300)

    def test_root_is_a_bounded_router_with_conditional_references(self):
        text = read("SKILL.md")
        self.assertLessEqual(len(text.encode("utf-8")), 6000)
        self.assertIn("do not preload every file", text)
        self.assertIn("Planning-only work need not load save/review instructions", text)
        self.assertIn("selected type and Source entry only", text)
        self.assertNotIn("| Always", text)
        self.assertNotIn("### 1.", text)

    def test_reference_loading_does_not_skip_delivery_safeguards(self):
        self.assertIn("Before delivering actual articles", read("SKILL.md"))
        self.assertIn("Check source support and privacy before persistence", read("evidence-review.md"))
        self.assertIn("recheck affected content", read("session-workflow.md"))

    def test_sample_scope_does_not_force_full_article_template(self):
        self.assertIn("return only that requested", read("SKILL.md"))
        self.assertIn("not a full article or extra template", read("SKILL.md"))
        self.assertIn("not the\nwhole template, front matter", read("templates.md"))

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
                self.assertNotIn("evidence.json", text)
                self.assertIn("omit this section for session-only sources", text)
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
        text = " ".join(read("session-workflow.md").split())
        for term in (
            "Never list or search other", "raw archive", "Do not improvise structural event filtering.",
            "On access denial, stop access attempts",
            "Do not silently switch sessions", "linked files",
        ):
            self.assertIn(term.lower(), text.lower())
        self.assertIn("reconstruct the removed helpers", read("SKILL.md"))

    def test_coverage_cannot_be_promoted_from_pasted_or_summarized_input(self):
        text = read("session-workflow.md")
        for term in (
            "partial` for all current-context and local-session reads",
            "complete-for-provided-transcript", "confirmed EOF",
            "did not change", "Pasted text is `current-session` and partial",
        ):
            self.assertIn(term, text)

    def test_save_requires_correct_session_create_only_and_full_readback(self):
        text = read("session-workflow.md")
        for term in (
            "that source session's directory", "not the invoking session",
            "create-only", "not an atomic no-overwrite guarantee",
            "stop and report that limitation", "Read each saved file back internally",
            "stop further writes", "Do not delete partial output",
            "each saved Wiki's", "full absolute file path", "separate descriptive",
            "same verified filesystem path", "path-aware joining",
        ):
            self.assertIn(term, text)

    def test_scoped_host_fallback_is_allowed_without_restoring_helpers(self):
        text = read("session-workflow.md")
        for term in (
            "ordinary approved host", "exclusive files/directories",
            "read back generated files", "Respect the host's approval policy",
            "not authorize a general script", "replacement\nvalidator",
            "Lack of one preferred tool alone is not a blocker",
        ):
            self.assertIn(term, text)

    def test_completion_handles_partial_sources_and_explicit_chat_delivery(self):
        text = read("session-workflow.md")
        for term in (
            "unchanged provider/ID", "explicitly requested\ncomplete-history",
            "continue with a narrowly", "same selected identity",
            "omit links to nonexistent files", "`reference_status: incomplete`",
            "never silently substitute",
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
            "`extraction-only`", "new sequence has not been run", "cannot inherit",
            "accept-all certificate", "preserve-view", "access-controlled",
            "Keep interpretation outside", "original language",
        ):
            self.assertIn(term, text)

    def test_source_formats_separate_document_links_from_unlinked_session_quotes(self):
        text = read("templates.md").split("## Source entry\n", 1)[1]
        official, session = text.split("### Session conversation or visible tool result\n", 1)
        self.assertIn("safe-canonical-HTTPS-URL", official)
        self.assertIn("Relevant section; applicable version", official)
        self.assertIn("not a few isolated", official)
        self.assertIn("**Session excerpt (Engineer; reported):**", session)
        self.assertIn("Do not link the excerpt", session)
        self.assertIn("Assistant; proposed", session)
        self.assertIn("Tool result; observed", session)
        self.assertIn("original not independently inspected", session)
        self.assertIn("Excerpt redacted", session)
        quote_template = re.search(r"(?ms)^```markdown\n(.*?)^```", session).group(1)
        self.assertEqual(markdown_links(quote_template), [])
        self.assertNotIn("Location:", quote_template)
        self.assertRegex(text, r"(?m)^> <.+>$")

    def test_windows_delivery_examples_preserve_separators_and_link_identity(self):
        text = read("session-workflow.md")
        examples = re.findall(
            r"(?m)^(?:Output directory|Article): `([^`]+)` - \[[^\]]+\]\(([^)]+)\)$",
            text,
        )
        self.assertEqual(len(examples), 2)
        for visible, target in examples:
            with self.subTest(visible=visible):
                self.assertIn("\\.copilot\\", visible)
                self.assertTrue(PureWindowsPath(visible).is_absolute())
                self.assertEqual(target, PureWindowsPath(visible).as_posix())
                self.assertEqual(PureWindowsPath(visible), PureWindowsPath(target))
        self.assertEqual(PureWindowsPath(examples[1][0]).parent, PureWindowsPath(examples[0][0]))
        for term in (
            "Never use a raw Windows path as Markdown link",
            "angle\nbrackets if it contains spaces", "file's actual absolute path",
            "not merely described", "not a lookalike path with a missing separator",
        ):
            self.assertIn(term, text)

    def test_embedded_sources_replace_sidecar_schema_across_the_bundle(self):
        text = read("evidence-review.md")
        self.assertIn("Save Markdown articles only", text)
        self.assertIn("Do not create `evidence.json`", text)
        self.assertIn("| Embedded sources |", text)
        self.assertNotIn("```json", text)
        self.assertNotIn("schema_version", text)
        self.assertIn("No `evidence.json`, replacement sidecar", read("sources.md"))
        self.assertIn("Do not generate `evidence.json`", read("SKILL.md"))
        self.assertIn("The absence of an evidence sidecar is not a blocker", read("sources.md"))
        for name in SUPPORTING | {"SKILL.md"}:
            document = read(name)
            with self.subTest(name=name):
                self.assertNotRegex(document, r"\]\((?:evidence\.json|#s\d+)\)")
                self.assertNotIn("approved-evidence:", document)
                self.assertNotIn("in the companion", document)
        self.assertIn(
            "not an original dialogue excerpt", " ".join(read("templates.md").split())
        )
        self.assertIn("not silently rewritten, deleted", text)
        self.assertIn("No line\nnumbering or reverse map", read("sources.md"))

    def test_mermaid_only_has_sourced_caption_and_text_fallback(self):
        text = read("diagrams.md")
        for term in (
            "`Diagram:`", "article itself", "No click handlers", "plain-text explanation",
            "does not generate SVG", "rendering as unverified", "Never upload",
        ):
            self.assertIn(term, text)

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
