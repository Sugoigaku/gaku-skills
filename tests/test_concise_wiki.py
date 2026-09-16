import json
from pathlib import Path
import tempfile
import unittest

from test_wiki_validation import CLAIM, PASSAGE, render, source, validator


def concise_reference(src):
    target = src["origin"] if src["kind"] == "public-document" else "evidence.json"
    handling = "**Excerpt handling:** redacted\n\n" if src["excerpt_handling"] == "redacted" else ""
    quote = "\n".join("> " + line for line in src["text"].split("\n"))
    return (
        f'\n### {src["id"]}\n\n**Source:** [{src["title"]}]({target})\n\n'
        f'**Location:** {src["locator"]}\n\n{handling}**Original excerpt:**\n\n{quote}\n'
    )


def concise_article(kind, src, *, double_check=False):
    header = render(kind, src).split("\n# Synthetic sample", 1)[0]
    header = header.replace("wiki_type:", "article_format: concise\nwiki_type:", 1)
    text = header + "\n# Synthetic sample\n"
    for heading in validator.CONCISE_HEADINGS[kind]:
        text += f"\n## {heading}\n\n"
        if heading in ("Questions and answers", "Steps"):
            block = "Q1. What does the toggle do?" if kind == "qa" else "Step 1 - Enable the synthetic toggle"
            text += f"### {block}\n\n{CLAIM} [S1](#s1)\n"
        elif heading == "References":
            text += "[Evidence details](evidence.json)\n" + concise_reference(src)
        else:
            text += "Synthetic context.\n"
    if double_check:
        text += "\n## Double-check\n\n- Confirm applicability to the next release.\n"
    return text


class ConciseWikiTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.evidence_path = self.root / "evidence.json"
        self.make_bundle()

    def make_bundle(self, kinds=("qa",), sanitized=False, extraction=False, double_check=False):
        src = source(sanitized)
        self.paths = []
        articles = []
        for kind in kinds:
            path = self.root / f"{kind}.md"
            text = concise_article(kind, src, double_check=double_check)
            if extraction:
                text = text.replace("documentation-enriched", "extraction-only")
            path.write_text(text, encoding="utf-8")
            self.paths.append(path)
            articles.append({
                "file": path.name,
                "claims": [{"id": "C1", "text": CLAIM, "source_ids": ["S1"],
                            "basis": "reported" if extraction else "documented"}],
                "enrichments": [] if kind == "qa" or extraction else [{
                    "section": "Step 1 - Enable the synthetic toggle",
                    "source_ids": ["S1"], "change": "Use the documented toggle action.",
                    "validation": "not-run",
                }],
            })
        self.evidence = {"schema_version": 1, "sources": [src], "articles": articles}
        self.save_evidence()

    def save_evidence(self):
        self.evidence_path.write_text(json.dumps(self.evidence), encoding="utf-8")

    def edit(self, old, new):
        text = self.paths[0].read_text(encoding="utf-8")
        self.assertIn(old, text)
        self.paths[0].write_text(text.replace(old, new), encoding="utf-8")

    def check(self, code=None):
        result = validator.validate_bundle(self.paths, self.evidence_path)
        if code:
            self.assertEqual(result["status"], "failed")
            self.assertIn(code, {issue["code"] for issue in result["issues"]}, result)
        else:
            self.assertEqual(result["status"], "passed", result)
        return result

    def test_all_types_are_valid_without_legacy_forms(self):
        self.make_bundle(("qa", "how-to", "break-fix"))
        self.assertEqual(self.check()["semantic_review"], "pending")

    def test_sanitized_extraction_preserves_evidence_gate(self):
        self.make_bundle(("qa", "how-to", "break-fix"), sanitized=True, extraction=True)
        self.check()

    def test_optional_double_check_is_last(self):
        self.make_bundle(double_check=True)
        self.check()
        self.edit("\n## Double-check\n\n- Confirm applicability to the next release.\n",
                  "\n## Double-check\n\n- Confirm applicability.\n\n## More detail\n\nExtra.\n")
        self.check("article-headings-mismatch")

    def test_empty_double_check_is_not_padding(self):
        self.make_bundle(double_check=True)
        self.edit("- Confirm applicability to the next release.", "")
        self.check("double-check-empty")

    def test_double_check_claim_citations_are_validated(self):
        self.make_bundle(double_check=True)
        claim = "The next release needs a separate check."
        self.edit("- Confirm applicability to the next release.", f"- {claim} [S1](#s1)")
        self.evidence["articles"][0]["claims"].append({
            "id": "C2", "text": claim, "source_ids": ["S1"], "basis": "inferred",
        })
        self.save_evidence()
        self.check()

    def test_before_you_start_may_be_omitted(self):
        self.make_bundle(("how-to",))
        self.edit("\n## Before you start\n\nSynthetic context.\n", "")
        self.check()

    def test_qa_repeated_conditions_are_rejected(self):
        self.edit(CLAIM, "**Conditions and exceptions:** " + CLAIM)
        self.check("concise-block-boilerplate")

    def test_procedure_repeated_impact_forms_are_rejected(self):
        self.make_bundle(("break-fix",))
        self.edit(CLAIM, "**Prerequisites and impact:** " + CLAIM)
        self.check("concise-block-boilerplate")

    def test_quote_mismatch_still_fails(self):
        self.edit("> " + PASSAGE, "> A fabricated quotation.")
        self.check("source-excerpt-mismatch")

    def test_wrong_locator_or_title_still_fails(self):
        self.edit("**Location:** Section: Sample toggle", "**Location:** Section: Other")
        self.check("source-entry-evidence-mismatch")
        self.make_bundle()
        self.edit("[Synthetic feature reference]", "[Wrong title]")
        self.check("source-entry-evidence-mismatch")

    def test_companion_link_is_required(self):
        self.edit("[Evidence details](evidence.json)", "Evidence is unavailable.")
        self.check("source-entry-evidence-link-mismatch")

    def test_missing_enrichment_record_still_fails(self):
        self.make_bundle(("how-to",))
        self.evidence["articles"][0]["enrichments"] = []
        self.save_evidence()
        self.check("enrichment-label-manifest-mismatch")

    def test_unbacked_new_step_in_extraction_mode_still_fails(self):
        self.make_bundle(("how-to",))
        self.edit("content_mode: documentation-enriched", "content_mode: extraction-only")
        self.check("extraction-only-enrichments-prohibited")

    def test_complete_references_still_need_independent_review(self):
        self.edit("reference_status: incomplete", "reference_status: complete")
        self.check("semantic-review-required")

    def test_redacted_quotes_must_be_labeled(self):
        self.make_bundle(sanitized=True)
        self.edit("**Excerpt handling:** redacted\n\n", "")
        self.check("source-entry-fields-invalid")

    def test_unknown_profile_does_not_bypass_validation(self):
        self.edit("article_format: concise", "article_format: unchecked")
        self.check("schema-enum-invalid")

    def test_concise_samples_are_materially_shorter(self):
        for kind in validator.HEADINGS:
            with self.subTest(kind=kind):
                compact = concise_article(kind, source())
                legacy = render(kind, source())
                self.assertLess(len(compact.splitlines()), len(legacy.splitlines()) * 0.7)
                self.assertNotIn("**Conditions and exceptions:**", compact)
                self.assertNotIn("**Provenance:**", compact)


if __name__ == "__main__":
    unittest.main()
