import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_concise_wiki import concise_article
from test_wiki_validation import CLAIM, source, validator, MODULE


SVG = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 90">
<title>Toggle enables the sample feature</title>
<rect x="5" y="15" width="130" height="50" fill="white" stroke="black"/>
<text x="25" y="45">Toggle</text>
<line x1="135" y1="40" x2="215" y2="40" stroke="black"/>
<rect x="215" y="15" width="135" height="50" fill="white" stroke="black"/>
<text x="235" y="45">Feature</text>
</svg>
'''
MERMAID = '```mermaid\nflowchart LR\n    A["Toggle"] --> B["Feature"]\n```\n'


class WikiDiagramTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.article = self.root / "qa-toggle.md"
        self.evidence = self.root / "evidence.json"
        self.svg = self.root / "concept.svg"
        self.review = self.root / "review.json"
        self.src = source()
        self.record = {
            "file": self.article.name,
            "claims": [{"id": "C1", "text": CLAIM, "source_ids": ["S1"], "basis": "documented"}],
            "enrichments": [],
        }
        self.evidence.write_text(json.dumps({
            "schema_version": 1, "sources": [self.src], "articles": [self.record],
        }), encoding="utf-8")
        self.article.write_text(concise_article("qa", self.src), encoding="utf-8")

    def diagram(self, text=MERMAID, caption=None):
        caption = f"Diagram: {CLAIM} [S1](#s1)" if caption is None else caption
        body = concise_article("qa", self.src)
        self.article.write_text(
            body.replace("\n## References", f"\n{text}\n{caption}\n\n## References"),
            encoding="utf-8",
        )

    def svg_diagram(self, text=SVG):
        self.svg.write_text(text, encoding="utf-8")
        self.diagram("![Toggle enables the sample feature](concept.svg)\n")

    def check(self, code=None, assets=(), **kwargs):
        result = validator.validate_bundle(
            [self.article], self.evidence, svg_paths=assets, **kwargs
        )
        if code:
            self.assertEqual(result["status"], "failed")
            self.assertIn(code, {i["code"] for i in result["issues"]}, result)
        else:
            self.assertEqual(result["status"], "passed", result)
        return result

    def attestation(self):
        record = {
            "schema_version": 1, "reviewer_kind": "human",
            "evidence_sha256": validator.sha256_bytes(self.evidence.read_bytes()),
            "articles": [{
                "file": self.article.name,
                "sha256": validator.sha256_bytes(self.article.read_bytes()),
                "coverage": "all-substantive-claims-reviewed",
                "claims": [{"id": "C1", "verdict": "supported", "reason": "Synthetic review only."}],
            }],
            "assets": [{"file": self.svg.name, "sha256": validator.sha256_bytes(self.svg.read_bytes())}],
        }
        self.review.write_text(json.dumps(record), encoding="utf-8")

    def test_diagram_is_optional(self):
        self.check()

    def test_mermaid_with_supported_caption(self):
        self.diagram()
        self.check()

    def test_sequence_diagram(self):
        self.diagram("```mermaid\nsequenceDiagram\n    A->>B: Enable the feature\n```\n")
        self.check()

    def test_svg_with_supported_caption_and_declared_local_file(self):
        self.svg_diagram()
        result = self.check(assets=[self.svg])
        self.assertEqual(len(result["hashes"]["assets"]), 1)

    def test_missing_caption_and_missing_caption_claim_are_rejected(self):
        self.diagram(caption="")
        self.check("diagram-caption-or-citation-missing")
        self.diagram(caption="Diagram: An unsupported explanation. [S1](#s1)")
        self.check("diagram-caption-claim-missing")

    def test_unclosed_mermaid_is_rejected(self):
        self.diagram("```mermaid\nflowchart LR\nA --> B\n")
        self.check("mermaid-fence-unclosed")

    def test_unsupported_mermaid_type_is_rejected(self):
        self.diagram("```mermaid\nunknownDiagram\nA --> B\n```\n")
        self.check("mermaid-type-or-size-invalid")

    def test_interactive_or_external_mermaid_is_rejected(self):
        for extra in (
            'click A "https://example.org"',
            '%%{init: {"securityLevel":"loose"}}%%',
            'A["<script>bad</script>"]',
            'style A fill:url(https://example.org/image)',
        ):
            with self.subTest(extra=extra):
                self.diagram(MERMAID.replace("\n```", f"\n{extra}\n```"))
                self.check("mermaid-interactive-or-external-content")

    def test_svg_script_event_foreign_object_and_external_reference_are_rejected(self):
        for content, code in (
            (SVG.replace("</svg>", "<script>alert(1)</script></svg>"), "svg-element-not-allowed"),
            (SVG.replace('viewBox=', 'onload="alert(1)" viewBox='), "svg-attribute-not-allowed"),
            (SVG.replace("</svg>", "<foreignObject>HTML</foreignObject></svg>"), "svg-element-not-allowed"),
            (SVG.replace('fill="white"', 'fill="url(https://example.org/image)"'), "svg-external-reference"),
        ):
            with self.subTest(code=code):
                self.svg_diagram(content)
                self.check(code, assets=[self.svg])

    def test_svg_entities_and_invalid_xml_are_rejected(self):
        self.svg_diagram('<!DOCTYPE svg [<!ENTITY x "data">]>' + SVG)
        self.check("svg-declaration-or-size-invalid", assets=[self.svg])
        self.svg_diagram("<svg>")
        self.check("svg-xml-invalid", assets=[self.svg])

    def test_svg_accessible_title_is_required(self):
        self.svg_diagram(SVG.replace("<title>Toggle enables the sample feature</title>", ""))
        self.check("svg-title-missing", assets=[self.svg])

    def test_remote_or_undeclared_images_are_rejected(self):
        self.diagram("![Concept](https://example.org/concept.svg)\n")
        self.check("markdown-link-syntax-not-supported")
        self.svg_diagram()
        self.check("markdown-link-syntax-not-supported")

    def test_unused_assets_are_rejected(self):
        self.svg.write_text(SVG, encoding="utf-8")
        self.check("svg-asset-unused", assets=[self.svg])

    def test_outside_assets_are_rejected(self):
        outside = self.root / "other"
        outside.mkdir()
        target = outside / "concept.svg"
        target.write_text(SVG, encoding="utf-8")
        self.diagram("![Concept](concept.svg)\n")
        self.check("file-directory-mismatch", assets=[target])

    def test_decoded_svg_labels_are_privacy_checked(self):
        self.svg_diagram(SVG.replace(">Toggle<", ">engineer&#64;example.invalid<"))
        result = validator.validate_bundle([self.article], self.evidence, svg_paths=[self.svg])
        self.assertEqual(result["status"], "failed")
        self.assertTrue(any("email" in i["code"] for i in result["issues"]), result)
        self.assertNotIn("engineer@", json.dumps(result))

    def test_svg_hash_is_bound_to_separate_review(self):
        self.svg_diagram()
        self.attestation()
        self.check(assets=[self.svg], review_path=self.review, require_semantic_review=True)
        self.svg.write_text(SVG.replace('width="130"', 'width="131"'), encoding="utf-8")
        self.check("review-asset-hash-mismatch", assets=[self.svg], review_path=self.review, require_semantic_review=True)

    def test_svg_cannot_be_omitted_from_review(self):
        self.svg_diagram()
        self.attestation()
        record = json.loads(self.review.read_text(encoding="utf-8"))
        del record["assets"]
        self.review.write_text(json.dumps(record), encoding="utf-8")
        result = validator.validate_bundle(
            [self.article], self.evidence, svg_paths=[self.svg],
            review_path=self.review, require_semantic_review=True,
        )
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["semantic_review"], "rejected")

    def test_cli_accepts_explicit_svg_and_does_not_change_files(self):
        self.svg_diagram()
        before = {p.name: p.read_bytes() for p in (self.article, self.evidence, self.svg)}
        result = subprocess.run([
            sys.executable, "-B", str(MODULE), "--article", str(self.article),
            "--evidence", str(self.evidence), "--svg", str(self.svg),
        ], capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)["status"], "passed")
        self.assertEqual(before, {p.name: p.read_bytes() for p in (self.article, self.evidence, self.svg)})


if __name__ == "__main__":
    unittest.main()
