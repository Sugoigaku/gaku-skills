import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".github" / "skills" / "case-session-to-wiki"
SKILL = SKILL_DIR / "SKILL.md"
SELECTOR = SKILL_DIR / "templates" / "wiki-template.md"
SOURCE_ENTRY = SKILL_DIR / "templates" / "source-entry-template.md"
ARTICLE_PLANNING = SKILL_DIR / "references" / "article-planning.md"
TEMPLATES = {
    wiki_type: SKILL_DIR / "templates" / f"{wiki_type}-template.md"
    for wiki_type in ("qa", "how-to", "break-fix")
}
COMMON_ENDINGS = (
    "References",
    "Double-check",
)
HEADINGS = {
    "qa": ("Questions and answers",) + COMMON_ENDINGS,
    "how-to": (
        "Goal", "Before you start", "Steps", "Check the result",
    ) + COMMON_ENDINGS,
    "break-fix": (
        "Problem", "Before you start", "Identify the issue", "Steps", "Check the result",
    ) + COMMON_ENDINGS,
}


def markdown_links(text):
    prose = re.sub(r"(?ms)^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*(?=\n|$)", "", text)
    prose = re.sub(r"(`+).*?\1", "", prose, flags=re.DOTALL)
    return re.findall(r"\[[^\]]+\]\(([^)]+)\)", prose)


class SkillFrameworkTests(unittest.TestCase):
    def test_markdown_examples_are_not_treated_as_live_links(self):
        text = (
            "[real](README.md)\n"
            "`[inline example](missing.json)`\n"
            "```markdown\n[example](missing.md)\n```\n"
            "~~~text\n[example](#missing)\n~~~\n"
            "[other](tests/scenarios.md)\n"
        )
        self.assertEqual(markdown_links(text), ["README.md", "tests/scenarios.md"])

    def test_discoverable_skill_has_required_front_matter(self):
        text = SKILL.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(?P<fields>.*?)\n---\n", text, re.DOTALL)
        self.assertIsNotNone(match, "SKILL.md must start with YAML front matter")
        fields = match.group("fields")
        self.assertRegex(fields, rf"(?m)^name: {re.escape(SKILL_DIR.name)}$")
        description = re.search(r'(?m)^description: "(.+)"$', fields)
        self.assertIsNotNone(description, "A quoted, single-line description is required")
        self.assertLessEqual(len(description.group(1)), 1024)
        self.assertRegex(SKILL_DIR.name, r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

    def test_each_type_has_its_own_sections_in_order(self):
        for wiki_type, template in TEMPLATES.items():
            with self.subTest(wiki_type=wiki_type):
                text = template.read_text(encoding="utf-8")
                headings = re.findall(r"(?m)^## (.+)$", text)
                self.assertEqual(headings, list(HEADINGS[wiki_type]))

    def test_templates_default_to_drafts_with_incomplete_references(self):
        for wiki_type, template in TEMPLATES.items():
            text = template.read_text(encoding="utf-8")
            for field in (
                f"wiki_type: {wiki_type}",
                "article_format: concise",
                "status: draft",
                "review_status: pending-engineer-review",
                "source_coverage: partial",
                "content_mode: documentation-enriched",
                "reference_status: incomplete",
            ):
                with self.subTest(wiki_type=wiki_type, field=field):
                    self.assertRegex(text, rf"(?m)^{re.escape(field)}$")

    def test_outcome_metadata_is_specific_to_the_wiki_type(self):
        for wiki_type, template in TEMPLATES.items():
            text = template.read_text(encoding="utf-8")
            expected = {
                "root_cause_status": "unknown" if wiki_type == "break-fix" else None,
                "resolution_status": "unverified" if wiki_type == "break-fix" else None,
                "procedure_status": "unverified" if wiki_type == "how-to" else None,
            }
            for field, value in expected.items():
                with self.subTest(wiki_type=wiki_type, field=field):
                    if value is None:
                        self.assertNotRegex(text, rf"(?m)^{field}:")
                    else:
                        self.assertRegex(text, rf"(?m)^{field}: {value}$")

    def test_selector_links_all_types_and_is_not_an_article_template(self):
        text = SELECTOR.read_text(encoding="utf-8")
        self.assertFalse(text.startswith("---"))
        for template in TEMPLATES.values():
            with self.subTest(template=template.name):
                self.assertIn(f"]({template.name})", text)

    def test_article_planning_is_wired_into_selection_and_delivery(self):
        skill = SKILL.read_text(encoding="utf-8")
        selector = SELECTOR.read_text(encoding="utf-8")
        self.assertIn("](references/article-planning.md)", skill)
        self.assertIn("](references/article-planning.md#set-delivery)", skill)
        self.assertIn("](../references/article-planning.md)", selector)

    def test_article_plan_has_scope_evidence_and_filename_fields(self):
        text = ARTICLE_PLANNING.read_text(encoding="utf-8")
        self.assertIn(
            "| ID | Topic | Wiki type | Reader task and scope | Proposed title | "
            "Sources and coverage | Readiness and gaps | Proposed filename |",
            text,
        )
        self.assertEqual(
            re.findall(r"(?m)^## (.+)$", text),
            [
                "Topic inventory",
                "Topic-by-type decisions",
                "Proposed article table",
                "Per-article validation",
                "Set delivery",
            ],
        )

    def test_article_set_delivery_names_all_terminal_outcomes(self):
        text = ARTICLE_PLANNING.read_text(encoding="utf-8")
        delivery = text.split("## Set delivery\n", 1)[1]
        for outcome in ("saved", "blocked", "failed", "deferred"):
            with self.subTest(outcome=outcome):
                self.assertIn(f"`{outcome}`", delivery)
        self.assertIn("Check every destination before writing.", delivery)
        self.assertIn("Add sibling links only after the target files exist", delivery)

    def test_delivery_is_session_local_without_preview_or_routine_confirmation(self):
        text = SKILL.read_text(encoding="utf-8")
        contract = (SKILL_DIR / "references" / "session-output.md").read_text(encoding="utf-8")
        for target in ("references/session-output.md", "tools/create_output_directory.py"):
            self.assertIn(f"]({target})", text)
            self.assertTrue((SKILL_DIR / target).is_file())
        self.assertIn("No preview, destination question,", text)
        self.assertIn("source session, not the invoking session", text)
        self.assertIn("Explicit read-only, no-write, or plan-only requests still prevent saving.", contract)
        self.assertNotIn("### 7. Preview, approve, and save", text)

    def test_final_delivery_requires_visible_absolute_paths(self):
        text = SKILL.read_text(encoding="utf-8")
        contract = (SKILL_DIR / "references" / "session-output.md").read_text(encoding="utf-8")
        self.assertIn("each saved Wiki's full absolute file path", text)
        self.assertIn("Paths must be visibly written out", text)
        self.assertIn("full absolute output-directory path", contract)
        self.assertIn("Verify each saved path exists", contract)

    def test_every_type_uses_the_shared_source_entry(self):
        for wiki_type, template in TEMPLATES.items():
            with self.subTest(wiki_type=wiki_type):
                text = template.read_text(encoding="utf-8")
                self.assertIn("](source-entry-template.md)", text)
                self.assertIn("## References", text)
                self.assertNotIn("## Review checklist", text)

    def test_source_entry_requires_original_text_and_precise_attribution(self):
        text = SOURCE_ENTRY.read_text(encoding="utf-8")
        fields = ("Source", "Location", "Original excerpt")
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(f"**{field}:**", text)
        self.assertRegex(text, r"(?m)^### S1$")
        self.assertRegex(text, r"(?m)^> <.+>$")

    def test_qa_is_direct_answers_with_final_double_check(self):
        text = TEMPLATES["qa"].read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^### Q1\.")
        self.assertNotIn("**Conditions and exceptions:**", text)
        self.assertNotIn("**Sources:**", text)
        self.assertEqual(re.findall(r"(?m)^## (.+)$", text)[-1], "Double-check")

    def test_how_to_steps_have_no_repeated_forms(self):
        text = TEMPLATES["how-to"].read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^### Step 1 - ")
        self.assertIn("## Check the result", text)
        self.assertIn("## Before you start", text)
        self.assertEqual(re.findall(r"(?m)^\*\*([^*]+):\*\*", text), [])

    def test_break_fix_retains_identification_and_important_impact_up_front(self):
        text = TEMPLATES["break-fix"].read_text(encoding="utf-8")
        self.assertLess(text.index("## Before you start"), text.index("## Steps"))
        self.assertLess(text.index("## Identify the issue"), text.index("## Steps"))
        self.assertEqual(re.findall(r"(?m)^\*\*([^*]+):\*\*", text), [])

    def test_skill_resources_are_linked_and_portable(self):
        text = SKILL.read_text(encoding="utf-8")
        for target in (
            "references/extraction-rules.md",
            "references/source-attribution.md",
            "references/article-planning.md",
            "references/session-input.md",
            "references/enrichment.md",
            "references/evidence-validation.md",
            "references/semantic-review.md",
            "references/diagrams.md",
            "tools/session_reader.py",
            "tools/validate_wiki.py",
            "templates/wiki-template.md",
            "templates/source-entry-template.md",
        ):
            with self.subTest(target=target):
                self.assertIn(f"]({target})", text)
                self.assertTrue((SKILL_DIR / target).is_file())

    def test_local_markdown_links_and_heading_anchors_resolve(self):
        documents = [ROOT / "README.md", ROOT / "tests" / "scenarios.md"]
        documents.extend(SKILL_DIR.rglob("*.md"))
        for document in documents:
            text = document.read_text(encoding="utf-8")
            for link in markdown_links(text):
                parsed = urlsplit(link)
                if parsed.scheme or parsed.netloc:
                    continue
                target = (
                    (document.parent / unquote(parsed.path)).resolve()
                    if parsed.path
                    else document
                )
                with self.subTest(document=document, link=link):
                    self.assertTrue(target.is_relative_to(ROOT))
                    self.assertTrue(target.is_file(), f"Missing target: {target}")
                    if parsed.fragment:
                        headings = re.findall(
                            r"(?m)^#+ (.+)$", target.read_text(encoding="utf-8")
                        )
                        anchors = {
                            re.sub(r"[^\w -]", "", heading.lower()).replace(" ", "-")
                            for heading in headings
                        }
                        self.assertIn(unquote(parsed.fragment), anchors)

    def test_readme_and_skill_agree_on_release_version(self):
        for document in (ROOT / "README.md", SKILL):
            with self.subTest(document=document):
                self.assertIn(
                    "Version: 0.7.0. Last reviewed: 2026-09-16.",
                    document.read_text(encoding="utf-8"),
                )

    def test_independent_semantic_review_is_wired_before_complete_status(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("--require-semantic-review", text)
        self.assertIn("mechanically-checked", text)
        review = (SKILL_DIR / "references" / "semantic-review.md").read_text(encoding="utf-8")
        self.assertIn("reviewer must be separate from the generator", review)
        self.assertIn("prior attestation is stale", review)

    def test_reader_coverage_is_mapped_not_treated_as_case_completeness(self):
        text = SKILL.read_text(encoding="utf-8")
        for requirement in (
            "source_kind: session-events",
            "coverage.visible_snapshot_complete: true",
            "coverage.gaps",
            "coverage.unread_segments",
            "Current-context-only input is always partial.",
            'even when called a "supplied transcript,"',
        ):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, text)

    def test_case_artifact_paths_are_ignored_but_skill_is_not(self):
        paths = (
            "wiki-drafts/topic.md",
            "private-inputs/transcript.md",
            "tests/__pycache__/test_skill_framework.cpython-313.pyc",
            ".github/skills/case-session-to-wiki/SKILL.md",
        )
        result = subprocess.run(
            ["git", "-C", str(ROOT), "check-ignore", "--no-index", "--stdin", "-z"],
            input="\0".join(paths) + "\0",
            text=True,
            capture_output=True,
            check=True,
        )
        self.assertTrue(result.stdout.endswith("\0"))
        self.assertEqual(set(result.stdout.split("\0")[:-1]), set(paths[:3]))


if __name__ == "__main__":
    unittest.main()
