import re
import subprocess
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".github" / "skills" / "case-session-to-wiki"
SKILL = SKILL_DIR / "SKILL.md"
TEMPLATE = SKILL_DIR / "templates" / "wiki-template.md"
HEADINGS = (
    "Problem and applicability",
    "Key findings",
    "Troubleshooting decision path",
    "Cause and confidence",
    "Resolution or workaround",
    "Verification",
    "Reusable lessons and follow-up answers",
    "Open questions and limitations",
    "Evidence and references",
    "Review checklist",
)


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

    def test_template_has_all_sections_in_order(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        headings = re.findall(r"(?m)^## (.+)$", text)
        self.assertEqual(headings, list(HEADINGS))

    def test_template_defaults_do_not_claim_verified_results(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        for field in (
            "status: draft",
            "review_status: pending-engineer-review",
            "source_coverage: partial",
            "root_cause_status: unknown",
            "resolution_status: unverified",
        ):
            with self.subTest(field=field):
                self.assertRegex(text, rf"(?m)^{re.escape(field)}$")

    def test_skill_resources_are_linked_and_portable(self):
        text = SKILL.read_text(encoding="utf-8")
        for target in (
            "references/extraction-rules.md",
            "templates/wiki-template.md",
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
                target = (document.parent / unquote(parsed.path)).resolve()
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
