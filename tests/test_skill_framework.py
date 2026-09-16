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
    "Open questions and limitations",
    "References and original excerpts",
    "Review checklist",
)
HEADINGS = {
    "qa": ("Topic and scope", "Questions and answers") + COMMON_ENDINGS,
    "how-to": (
        "Goal and success criteria",
        "Prerequisites and concepts",
        "Step-by-step procedure",
        "End-to-end verification",
        "Troubleshooting and rollback",
    ) + COMMON_ENDINGS,
    "break-fix": (
        "Problem and applicability",
        "Confirm this is the same issue",
        "Cause and confidence",
        "Resolution or workaround",
        "Verification",
        "Escalation and prevention",
    ) + COMMON_ENDINGS,
}


class SkillFrameworkTests(unittest.TestCase):
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
                "status: draft",
                "review_status: pending-engineer-review",
                "source_coverage: partial",
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

    def test_every_type_uses_the_shared_source_entry(self):
        for wiki_type, template in TEMPLATES.items():
            with self.subTest(wiki_type=wiki_type):
                text = template.read_text(encoding="utf-8")
                self.assertIn("](source-entry-template.md)", text)
                self.assertIn("**Sources:**", text)

    def test_source_entry_requires_original_text_and_precise_attribution(self):
        text = SOURCE_ENTRY.read_text(encoding="utf-8")
        fields = (
            "Source type",
            "Title",
            "Publisher or source role",
            "Origin",
            "Exact location",
            "Version or revision",
            "Access",
            "Verification",
            "Inspected on",
            "Supports",
            "Excerpt handling",
            "Original excerpt",
            "Interpretation and limits",
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(f"**{field}:**", text)
        self.assertRegex(text, r"(?m)^### S1$")
        self.assertRegex(text, r"(?m)^> <.+>$")

    def test_qa_answers_have_conditions_and_inline_source_fields(self):
        text = TEMPLATES["qa"].read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^### Q1\.")
        for field in ("Answer", "Conditions and exceptions", "Sources"):
            with self.subTest(field=field):
                self.assertIn(f"**{field}:**", text)

    def test_how_to_steps_have_actions_and_checkpoints(self):
        text = TEMPLATES["how-to"].read_text(encoding="utf-8")
        self.assertRegex(text, r"(?m)^### Step 1 - ")
        fields = (
            "Where",
            "Inputs",
            "Action",
            "Why",
            "Expected result",
            "If the result differs",
            "Safety and rollback",
            "Sources",
        )
        for field in fields:
            with self.subTest(field=field):
                self.assertIn(f"**{field}:**", text)

    def test_break_fix_has_match_and_non_match_paths_before_repair(self):
        text = TEMPLATES["break-fix"].read_text(encoding="utf-8")
        self.assertIn(
            "| Check and how to perform it | Matches when | Does not match when | Next action | Sources |",
            text,
        )
        for field in (
            "Prerequisites and impact",
            "Action",
            "Expected result",
            "If it fails",
            "Rollback",
            "Sources",
        ):
            with self.subTest(field=field):
                self.assertIn(f"**{field}:**", text)

    def test_skill_resources_are_linked_and_portable(self):
        text = SKILL.read_text(encoding="utf-8")
        for target in (
            "references/extraction-rules.md",
            "references/source-attribution.md",
            "references/article-planning.md",
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
            for link in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
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
                    "Version: 0.3.0. Last reviewed: 2026-09-16.",
                    document.read_text(encoding="utf-8"),
                )

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
