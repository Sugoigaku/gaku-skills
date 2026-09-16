"""Synthetic, offline tests; scratch bundles stay underneath this project's fixtures."""

from __future__ import annotations

import contextlib
import copy
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / ".github" / "skills" / "case-session-to-wiki" / "tools" / "validate_wiki.py"
SPEC = importlib.util.spec_from_file_location("wiki_validator", MODULE)
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)

CLAIM = "The synthetic toggle enables the sample feature."
UNRELATED = "The synthetic toggle repairs every storage failure."
PASSAGE = "The synthetic toggle enables the sample feature."


def source(sanitized: bool = False) -> dict:
    return {
        "id": "S1",
        "kind": "sanitized-evidence" if sanitized else "public-document",
        "title": "Approved synthetic observation" if sanitized else "Synthetic feature reference",
        "publisher": "Engineer report" if sanitized else "Example publisher",
        "origin": "approved-evidence:sample-toggle" if sanitized else "https://docs.example.org/features/toggle",
        "locator": "Lines 1" if sanitized else "Section: Sample toggle",
        "version": "v1.2.3",
        "inspection_status": "supplied-excerpt-only" if sanitized else "original-inspected",
        "text": PASSAGE,
        "excerpt_handling": "redacted" if sanitized else "verbatim",
    }


def reference(record: dict, evidence_name: str = "evidence.json") -> str:
    pairs = [
        ("Source type", record["kind"]),
        ("Evidence record", f'{record["id"]} in [{evidence_name}]({evidence_name})'),
        ("Title", record["title"]),
        ("Publisher or source role", record["publisher"]),
        ("Origin", record["origin"]),
        ("Exact location", record["locator"]),
        ("Version or revision", record["version"]),
        ("Access", "Public" if record["kind"] == "public-document" else "engineer-provided"),
        ("Verification", record["inspection_status"]),
        ("Inspected on", "2026-09-16"),
        ("Supports", "The selected claim in the answer or procedure."),
        ("Excerpt handling", record["excerpt_handling"]),
    ]
    result = f'\n### {record["id"]}\n\n'
    result += "\n\n".join(f"**{key}:** {value}" for key, value in pairs)
    quoted = "\n".join("> " + line if line else ">" for line in record["text"].replace("\r\n", "\n").split("\n"))
    return result + f"\n\n**Original excerpt:**\n\n{quoted}\n\n**Interpretation and limits:** This is synthetic and limited to the sample feature.\n"


def render(kind: str, record: dict, claim: str = CLAIM, extraction: bool = False, provenance: str | None = None) -> str:
    outcome = {
        "qa": "",
        "how-to": "procedure_status: unverified\n",
        "break-fix": "root_cause_status: unknown\nresolution_status: unverified\n",
    }[kind]
    result = (
        "---\ntitle: Synthetic sample\n"
        f"wiki_type: {kind}\nstatus: draft\nreview_status: pending-engineer-review\n"
        "product: Sample version 1.2.3\nsource_kind: current-session\nsource_coverage: partial\n"
        f"content_mode: {'extraction-only' if extraction else 'documentation-enriched'}\n"
        f"reference_status: incomplete\n{outcome}tags: []\n---\n\n# Synthetic sample\n"
    )
    provenance = provenance or ("observed-in-session" if extraction else "documentation-enriched")
    for heading in validator.HEADINGS[kind]:
        result += f"\n## {heading}\n\n"
        if heading == "Questions and answers":
            result += f"### Q1. What does the toggle do?\n\n**Answer:** {claim} [S1](#s1)\n\n"
            result += "**Conditions and exceptions:** Limited to the sample feature.\n\n**Sources:** [S1](#s1)\n"
        elif heading in {"Step-by-step procedure", "Resolution or workaround"}:
            result += f"### Step 1 - Enable the synthetic toggle\n\n**Provenance:** {provenance}\n\n**Execution validation:** not-run\n\n"
            fields = (
                ["Where", "Inputs", "Action", "Why", "Expected result", "If the result differs", "Safety and rollback"]
                if kind == "how-to" else ["Prerequisites and impact", "Action", "Expected result", "If it fails", "Rollback"]
            )
            for field in fields:
                result += f"**{field}:** {claim if field == 'Action' else 'Not established.'}\n\n"
            result += "**Sources:** [S1](#s1)\n"
        elif heading == "References and original excerpts":
            result += reference(record)
        elif heading == "Review checklist":
            result += "- [ ] Pending engineer review.\n"
        else:
            result += "Not established.\n"
    return result


class WikiValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture_root = ROOT / "tests" / "fixtures" / "wiki-validation"
        cls.fixture_root.mkdir(parents=True, exist_ok=True)

    def setUp(self):
        self.scratch = tempfile.TemporaryDirectory(prefix="synthetic-", dir=self.fixture_root)
        self.addCleanup(self.scratch.cleanup)
        self.directory = Path(self.scratch.name).resolve()
        self.evidence_path = self.directory / "evidence.json"
        self.review_path = self.directory / "review.json"
        self.paths: list[Path] = []
        self.evidence: dict = {}
        self.make_bundle()

    def write_json(self, path, value):
        path.write_text(json.dumps(value, ensure_ascii=True, indent=2) + "\n", encoding="utf-8")

    def make_bundle(self, kinds=("qa",), sanitized=False, extraction=False):
        src = source(sanitized)
        self.paths = []
        records = []
        for kind in kinds:
            path = self.directory / (kind + ".md")
            path.write_text(render(kind, src, extraction=extraction), encoding="utf-8")
            self.paths.append(path)
            enrichment = [] if kind == "qa" or extraction else [{
                "section": "Step 1 - Enable the synthetic toggle",
                "source_ids": ["S1"], "change": "Add the documented action and checkpoint.",
                "validation": "not-run",
            }]
            records.append({
                "file": path.name,
                "claims": [{"id": "C1", "text": CLAIM, "source_ids": ["S1"], "basis": "reported" if sanitized else "documented"}],
                "enrichments": enrichment,
            })
        self.evidence = {"schema_version": 1, "sources": [src], "articles": records}
        self.save_evidence()

    def save_evidence(self):
        self.write_json(self.evidence_path, self.evidence)

    def edit_article(self, old, new, index=0):
        path = self.paths[index]
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def check(self, **kwargs):
        return validator.validate_bundle(self.paths, self.evidence_path, **kwargs)

    def assert_pass(self, result=None):
        result = self.check() if result is None else result
        self.assertEqual("passed", result["status"], json.dumps(result, indent=2))
        return result

    def assert_fail(self, code=None, result=None):
        result = self.check() if result is None else result
        self.assertEqual("failed", result["status"], json.dumps(result, indent=2))
        if code:
            self.assertIn(code, {i["code"] for i in result["issues"]}, json.dumps(result, indent=2))
        return result

    def make_review(self, verdict="supported", kind="human"):
        result = {
            "schema_version": 1, "reviewer_kind": kind,
            "evidence_sha256": validator.sha256_bytes(self.evidence_path.read_bytes()),
            "articles": [
                {
                    "file": path.name, "sha256": validator.sha256_bytes(path.read_bytes()),
                    "coverage": "all-substantive-claims-reviewed",
                    "claims": [{"id": c["id"], "verdict": verdict, "reason": "A separate synthetic review reports this verdict."} for c in rec["claims"]],
                }
                for path, rec in zip(self.paths, self.evidence["articles"])
            ],
        }
        self.write_json(self.review_path, result)
        return result

    def test_good_all_types_share_bundle_source(self):
        self.make_bundle(("qa", "how-to", "break-fix"))
        result = self.assert_pass()
        self.assertEqual("pending", result["semantic_review"])
        self.assertEqual(3, len(result["hashes"]["articles"]))
        self.assertEqual("not-authorized", result["publication_status"])

    def test_good_sanitized_extraction_all_types(self):
        self.make_bundle(("qa", "how-to", "break-fix"), sanitized=True, extraction=True)
        self.assert_pass()

    def test_good_supplied_public_excerpt_and_crlf(self):
        src = self.evidence["sources"][0]
        src["inspection_status"] = "supplied-excerpt-only"
        self.edit_article("**Verification:** original-inspected", "**Verification:** supplied-excerpt-only")
        self.paths[0].write_bytes(self.paths[0].read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        self.save_evidence()
        self.assert_pass()

    def test_exact_multi_paragraph_quote(self):
        passage = "A short synthetic sentence.\n\nA second exact paragraph."
        self.evidence["sources"][0]["text"] = passage
        self.edit_article("> " + PASSAGE, "> A short synthetic sentence.\n>\n> A second exact paragraph.")
        self.save_evidence()
        self.assert_pass()

    def test_quote_changed_or_paraphrased(self):
        self.edit_article("> " + PASSAGE, "> The feature can be turned on by the toggle.")
        self.assert_fail("source-excerpt-mismatch")

    def test_quote_spaces_not_fuzzy_normalized(self):
        self.edit_article("> " + PASSAGE, ">  " + PASSAGE)
        self.assert_fail("source-excerpt-mismatch")

    def test_quote_must_be_blockquote(self):
        self.edit_article("> " + PASSAGE, PASSAGE)
        self.assert_fail("source-excerpt-format-invalid")

    def test_quote_interpretation_must_be_outside(self):
        self.edit_article("> " + PASSAGE, "> " + PASSAGE + "\n> An added interpretation.")
        self.assert_fail("source-excerpt-mismatch")

    def test_wrong_title_locator_origin_handling_and_publisher(self):
        for field, original, replacement in [
            ("Title", "Synthetic feature reference", "Different reference"),
            ("Exact location", "Section: Sample toggle", "Section: Different section"),
            ("Origin", "https://docs.example.org/features/toggle", "https://docs.example.org/other"),
            ("Excerpt handling", "verbatim", "redacted"),
            ("Publisher or source role", "Example publisher", "Different publisher"),
            ("Version or revision", "v1.2.3", "v1.2.4"),
        ]:
            with self.subTest(field=field):
                self.make_bundle()
                self.edit_article(f"**{field}:** {original}", f"**{field}:** {replacement}")
                self.assert_fail("source-entry-evidence-mismatch")

    def test_evidence_record_link_must_match(self):
        self.edit_article("S1 in [evidence.json](evidence.json)", "S2 in [evidence.json](evidence.json)")
        self.assert_fail("source-entry-evidence-link-mismatch")

    def test_missing_source_field(self):
        self.edit_article("**Supports:** The selected claim in the answer or procedure.\n\n", "")
        self.assert_fail("source-entry-fields-invalid")

    def test_duplicate_source_entry(self):
        self.edit_article("## Review checklist", reference(source()) + "\n## Review checklist")
        self.assert_fail("source-entry-unresolved-or-duplicate")

    def test_missing_citations(self):
        self.edit_article("[S1](#s1)", "Source not linked")
        self.assert_fail("claim-nearby-citation-missing")

    def test_wrong_citation_fragment(self):
        self.edit_article("[S1](#s1)", "[S1](#s2)")
        self.assert_fail("citation-unresolved-or-mismatched")

    def test_excess_citation(self):
        self.edit_article("**Answer:**", "[S9](#s9)\n\n**Answer:**")
        self.assert_fail("citation-unresolved-or-mismatched")

    def test_citation_in_code_does_not_support_answer(self):
        self.edit_article("[S1](#s1)", "\n\n```\n[S1](#s1)\n```\n")
        self.assert_fail("claim-nearby-citation-missing")

    def test_citation_in_inline_code_does_not_support_answer(self):
        self.edit_article("[S1](#s1)", "`[S1](#s1)`")
        self.assert_fail("claim-nearby-citation-missing")

    def test_rich_source_entry_cannot_replace_claim_map(self):
        self.evidence["articles"][0]["claims"] = []
        self.save_evidence()
        self.assert_fail("schema-list-invalid")

    def test_claim_must_occur_in_body_not_just_excerpt(self):
        self.edit_article("**Answer:** " + CLAIM, "**Answer:** A different claim.")
        self.assert_fail("claim-text-absent")

    def test_claim_citation_neighborhood_does_not_span_headings(self):
        self.edit_article("**Answer:** " + CLAIM + " [S1](#s1)", "**Answer:** " + CLAIM)
        self.edit_article("**Sources:** [S1](#s1)", "**Sources:** Not recorded.")
        self.edit_article("## Topic and scope\n\nNot established.", "## Topic and scope\n\n[S1](#s1)")
        self.assert_fail("claim-nearby-citation-missing")

    def test_each_answer_requires_own_claim(self):
        self.edit_article("## Open questions and limitations", "### Q2. Is another feature enabled?\n\n**Answer:** A separate statement. [S1](#s1)\n\n**Conditions and exceptions:** None.\n\n**Sources:** [S1](#s1)\n\n## Open questions and limitations")
        self.assert_fail("answer-or-step-claim-citation-missing")

    def test_every_bundle_source_used(self):
        unused = source()
        unused["id"] = "S2"
        self.evidence["sources"].append(unused)
        self.save_evidence()
        self.assert_fail("evidence-source-unused-in-bundle")

    def test_unused_embedded_source(self):
        extra = source()
        extra["id"] = "S2"
        self.evidence["sources"].append(extra)
        self.save_evidence()
        self.edit_article("## Review checklist", reference(extra) + "\n## Review checklist")
        self.assert_fail("source-entry-unused-or-missing")

    def test_malformed_json_duplicate_keys_and_nonfinite(self):
        for text, code in [
            ("{", "json-malformed"),
            ('{"schema_version":1,"schema_version":1,"sources":[],"articles":[]}', "json-duplicate-key"),
            ('{"x":{"y":1,"y":2}}', "json-duplicate-key"),
            ('{"x": NaN}', "json-nonfinite-number"),
            ('{"x": 1e99999}', "json-nonfinite-number"),
            (r'{"x": "\ud800"}', "json-malformed"),
        ]:
            with self.subTest(code=code):
                self.evidence_path.write_text(text, encoding="utf-8")
                self.assert_fail(code)

    def test_wrong_schema_versions(self):
        for value in [2, "1", True, None, [], {}]:
            with self.subTest(value=value):
                self.evidence["schema_version"] = value
                self.save_evidence()
                self.assert_fail("schema-version-unsupported")

    def test_unknown_fields_forbidden_at_each_level(self):
        for target in ["top", "source", "article", "claim", "enrichment"]:
            with self.subTest(target=target):
                self.make_bundle(("how-to",))
                obj = {
                    "top": self.evidence, "source": self.evidence["sources"][0],
                    "article": self.evidence["articles"][0],
                    "claim": self.evidence["articles"][0]["claims"][0],
                    "enrichment": self.evidence["articles"][0]["enrichments"][0],
                }[target]
                obj["raw_archive_path"] = "forbidden-field"
                self.save_evidence()
                self.assert_fail("schema-fields-mismatch")

    def test_invalid_source_field_types(self):
        for key in validator.SOURCE_FIELDS:
            for bad in [None, [], {}, 1, True]:
                with self.subTest(key=key, bad=bad):
                    self.make_bundle()
                    self.evidence["sources"][0][key] = bad
                    self.save_evidence()
                    self.assert_fail("schema-text-invalid")

    def test_invalid_claim_types(self):
        for key, bad in [("id", {}), ("text", 4), ("source_ids", "S1"), ("source_ids", [{}]), ("basis", [])]:
            with self.subTest(key=key, bad=bad):
                self.make_bundle()
                self.evidence["articles"][0]["claims"][0][key] = bad
                self.save_evidence()
                self.assert_fail()

    def test_invalid_container_types(self):
        for key in ["sources", "articles"]:
            for bad in [None, "value", {}, 4]:
                with self.subTest(key=key, bad=bad):
                    self.make_bundle()
                    self.evidence[key] = bad
                    self.save_evidence()
                    self.assert_fail("schema-list-invalid")

    def test_duplicate_ids_and_names(self):
        for target in ["sources", "articles", "claims"]:
            with self.subTest(target=target):
                self.make_bundle()
                obj = self.evidence["articles"][0]["claims"] if target == "claims" else self.evidence[target]
                obj.append(copy.deepcopy(obj[0]))
                self.save_evidence()
                self.assert_fail()

    def test_missing_or_private_provenance(self):
        bad_origins = ["", "archive record 4", "file:///archive.txt", "https://icm.ad.msft.net/incident", "https://intranet.example.org/page"]
        for origin in bad_origins:
            with self.subTest(origin=origin):
                self.make_bundle()
                self.evidence["sources"][0]["origin"] = origin
                self.save_evidence()
                self.assert_fail()

    def test_bad_public_urls(self):
        for url in [
            "http://docs.example.org/page", "ftp://docs.example.org/page",
            "https://name:secret@docs.example.org/page",
            "https://name@docs.example.org/page",
            "https://docs.example.org/page?sig=secret",
            "https://docs.example.org/page?token=secret",
            "https://docs.example.org/page?language=en",
            "https://docs.example.org/page?x-amz-signature=secret",
            "https://docs.example.org/page?%73ig=secret",
            "https://127.0.0.1/page", "https://[::1]/page",
            "https://localhost/page", "https://docs.example.org:444/page",
            "https://docs.example.org/%0asecret",
            "https://docs.example.org\\@evil.example.org/page",
        ]:
            with self.subTest(url=url):
                self.make_bundle()
                self.evidence["sources"][0]["origin"] = url
                self.save_evidence()
                self.assert_fail("public-origin-invalid")

    def test_good_https_anchor_and_markdown_origin(self):
        self.edit_article("**Origin:** https://docs.example.org/features/toggle", "**Origin:** [Reference](https://docs.example.org/features/toggle)")
        self.assert_pass()
        self.assertTrue(validator.safe_https_url("https://docs.example.org/page#section"))

    def test_safe_documentation_query_selectors_are_preserved(self):
        original = "https://docs.example.org/features/toggle"
        for query in [
            "view=windowsserver2025-ps",
            "preserve-view=true",
            "tabs=powershell",
            "view=sample-1.2_preview&preserve-view=true&tabs=PowerShell",
            "tabs=cli&view=sample-1.2",
            "view=windowsserver2025-ps#syntax",
        ]:
            for markdown_link in (False, True):
                with self.subTest(query=query, markdown_link=markdown_link):
                    self.make_bundle()
                    origin = original + "?" + query
                    self.assertTrue(validator.safe_https_url(origin))
                    self.evidence["sources"][0]["origin"] = origin
                    self.save_evidence()
                    value = f"[Reference]({origin})" if markdown_link else origin
                    self.edit_article("**Origin:** " + original, "**Origin:** " + value)
                    before = (self.paths[0].read_bytes(), self.evidence_path.read_bytes())
                    result = self.assert_pass()
                    self.assertEqual("pending", result["semantic_review"])
                    self.assertEqual(before, (self.paths[0].read_bytes(), self.evidence_path.read_bytes()))
                    self.assertEqual(validator.sha256_bytes(before[0]), result["hashes"]["articles"][0]["sha256"])

    def test_documentation_query_rejects_other_duplicate_empty_or_encoded_selectors(self):
        for query in [
            "", "view", "view=", "view=x&view=x", "view=x&view=y",
            "preserve-view=true&preserve-view=false", "tabs=cli&tabs=ps",
            "VIEW=x", "View=x", "view=x&View=y", "language=en",
            "view=x&language=en", "view=x&sig=synthetic", "view=x&token=synthetic",
            "view=x&", "&view=x", "view=x&&tabs=cli", "view=x;tabs=cli",
            "view=a+b", "view=a/b", "view=a:b", "view=a,b", "view=a=b",
            "view=a%20b", "view=%78", "%76iew=x", "view=%2578", "view=é",
        ]:
            with self.subTest(query=query):
                self.assertFalse(validator.safe_https_url("https://docs.example.org/page?" + query))
        self.evidence["sources"][0]["origin"] += "?view=x&tabs="
        self.save_evidence()
        self.assert_fail("public-origin-invalid")

    def test_safe_query_values_still_run_identifier_and_secret_scans(self):
        for value in [
            "00000000-1111-2222-3333-444444444444",
            "2601010000001234",
            "192.0.2.15",
            "eyJabcdefghijk.abcdefghijk.abcdefghijk",
        ]:
            with self.subTest(value=value):
                self.assertFalse(validator.safe_https_url("https://docs.example.org/page?view=" + value))

    def test_query_selector_remains_part_of_exact_origin_binding(self):
        self.edit_article(
            "**Origin:** https://docs.example.org/features/toggle",
            "**Origin:** [Reference](https://docs.example.org/features/toggle?view=windowsserver2025-ps)",
        )
        self.assert_fail("source-entry-evidence-mismatch")

    def test_allowed_query_still_honors_reader_deny_terms(self):
        original = self.evidence["sources"][0]["origin"]
        origin = original + "?tabs=SyntheticPrivateLabel"
        self.evidence["sources"][0]["origin"] = origin
        self.save_evidence()
        self.edit_article("**Origin:** " + original, "**Origin:** " + origin)
        result = self.assert_fail("sensitive-deny-term", self.check(deny_terms=["syntheticprivatelabel"]))
        self.assertNotIn("syntheticprivatelabel", json.dumps(result).casefold())

    def test_sanitized_record_locator_bound_to_included_text(self):
        self.make_bundle(sanitized=True)
        self.evidence["sources"][0]["locator"] = "Lines 200-201"
        self.save_evidence()
        self.assert_fail("sanitized-locator-invalid")

    def test_sanitized_origin_cannot_be_anonymous_archive_id(self):
        self.make_bundle(sanitized=True)
        self.evidence["sources"][0]["origin"] = "archive-record:42"
        self.save_evidence()
        self.assert_fail("sanitized-origin-invalid")

    def test_known_leaks_in_frontmatter_code_links_and_text(self):
        leaks = [
            ("00000000-1111-2222-3333-444444444444", "sensitive-guid"),
            ("2601010000001234", "sensitive-case-shaped-id"),
            ("192.0.2.15", "sensitive-ip-address"),
            ("2001:db8::1", "sensitive-ip-address"),
            ("person@example.org", "sensitive-email"),
            ("C:\\Users\\Synthetic\\archive.txt", "sensitive-user-path"),
            ("/home/synthetic/archive.txt", "sensitive-user-path"),
            ("-----BEGIN RSA PRIVATE KEY-----", "sensitive-private-key"),
            ("Bearer synthetic-secret", "sensitive-bearer"),
            ("api_key=synthetic-secret", "sensitive-credential"),
            ("https://docs.example.org/a?sig=synthetic-secret", "sensitive-signed-url"),
        ]
        for leak, code in leaks:
            for placement in ["frontmatter", "code", "link", "body"]:
                with self.subTest(code=code, placement=placement):
                    self.make_bundle()
                    if placement == "frontmatter":
                        self.edit_article("title: Synthetic sample", "title: " + json.dumps(leak))
                    elif placement == "code":
                        self.edit_article("## Topic and scope", "```\n" + leak + "\n```\n\n## Topic and scope")
                    elif placement == "link":
                        self.edit_article("## Topic and scope", "[" + leak + "](https://docs.example.org/page)\n\n## Topic and scope")
                    else:
                        self.edit_article("## Topic and scope", leak + "\n\n## Topic and scope")
                    result = self.assert_fail(code)
                    self.assertNotIn(leak, json.dumps(result))

    def test_json_escaped_leak_detected_after_decode(self):
        self.evidence["sources"][0]["publisher"] = "person@example.org"
        self.save_evidence()
        text = self.evidence_path.read_text(encoding="utf-8").replace("@", r"\u0040")
        self.evidence_path.write_text(text, encoding="utf-8")
        self.assert_fail("sensitive-email")

    def test_frontmatter_escaped_leak_detected_after_decode(self):
        self.edit_article("title: Synthetic sample", r'title: "person\u0040example.org"')
        self.assert_fail("sensitive-email")

    def test_deny_terms_case_insensitive_and_not_echoed(self):
        self.edit_article("## Topic and scope", "Project AcMeInternalOnly\n\n## Topic and scope")
        result = self.assert_fail("sensitive-deny-term", self.check(deny_terms=["acmeinternalonly"]))
        self.assertNotIn("acmeinternalonly", json.dumps(result).casefold())

    def test_versions_and_oids_not_ips(self):
        for value in ["v1.2.3.4", "version 1.2.3.4", "OID 1.3.6.1", "1.3.6.1.4.1.999"]:
            with self.subTest(value=value):
                self.assertEqual([], validator.scan_sensitive(value, "test"))
        self.assertEqual([], validator.scan_sensitive("a1234567890123456fedcba", "test"))

    def test_missing_enrichment_label(self):
        self.make_bundle(("how-to",))
        self.edit_article("**Provenance:** documentation-enriched\n\n", "")
        self.assert_fail("provenance-or-execution-label-missing-or-invalid")

    def test_missing_execution_label(self):
        self.make_bundle(("break-fix",))
        self.edit_article("**Execution validation:** not-run\n\n", "")
        self.assert_fail("provenance-or-execution-label-missing-or-invalid")

    def test_enrichment_manifest_missing(self):
        self.make_bundle(("how-to",))
        self.evidence["articles"][0]["enrichments"] = []
        self.save_evidence()
        self.assert_fail("enrichment-label-manifest-mismatch")

    def test_enrichment_heading_or_validation_mismatch(self):
        for key, value, expected in [
            ("section", "Nonexistent heading", "enrichment-heading-unresolved"),
            ("validation", "lab-tested", "enrichment-validation-or-citations-mismatch"),
        ]:
            with self.subTest(key=key):
                self.make_bundle(("how-to",))
                self.evidence["articles"][0]["enrichments"][0][key] = value
                self.save_evidence()
                self.assert_fail(expected)

    def test_qa_enriched_answer_can_be_explicitly_labeled(self):
        self.edit_article("**Answer:**", "**Provenance:** documentation-enriched\n\n**Execution validation:** not-run\n\n**Answer:**")
        self.evidence["articles"][0]["enrichments"] = [{
            "section": "Q1. What does the toggle do?", "source_ids": ["S1"],
            "change": "Clarify the documented condition.", "validation": "not-run",
        }]
        self.save_evidence()
        self.assert_pass()

    def test_extraction_only_rejects_documented_new_steps(self):
        self.make_bundle(("how-to",))
        self.edit_article("content_mode: documentation-enriched", "content_mode: extraction-only")
        self.assert_fail("extraction-only-enrichments-prohibited")

    def test_extraction_only_cannot_hide_documented_step_under_observed_label(self):
        self.make_bundle(("how-to",), extraction=True)
        self.assert_fail("extraction-only-step-needs-observed-or-reported-claim")

    def test_observation_requires_sanitized_source(self):
        self.evidence["articles"][0]["claims"][0]["basis"] = "observed"
        self.save_evidence()
        self.assert_fail("claim-observation-needs-sanitized-evidence")

    def test_required_metadata_and_type_outcomes(self):
        for change in [
            ("status: draft", "status: published"),
            ("review_status: pending-engineer-review", "review_status: approved"),
            ("source_coverage: partial", "source_coverage: whole-case"),
            ("source_coverage: partial", "source_coverage: complete-for-selected-visible-events"),
            ("source_kind: current-session\n", ""),
            ("wiki_type: qa", "wiki_type: faq"),
            ("reference_status: incomplete", "reference_status: finished"),
            ("content_mode: documentation-enriched", "content_mode: unrestricted"),
        ]:
            with self.subTest(change=change):
                self.make_bundle()
                self.edit_article(*change)
                self.assert_fail()

    def test_qa_rejects_root_cause_metadata(self):
        self.edit_article("tags: []", "root_cause_status: confirmed\ntags: []")
        self.assert_fail("frontmatter-field-not-allowed")

    def test_break_fix_resolution_status_tracks_recovery_evidence(self):
        for status in ["unverified", "reported", "verified"]:
            with self.subTest(status=status):
                self.make_bundle(("break-fix",))
                self.edit_article("resolution_status: unverified", "resolution_status: " + status)
                self.edit_article(
                    "## Resolution or workaround\n\n",
                    "## Resolution or workaround\n\nRemedy kind: fix, workaround, or mitigation remains a prose distinction.\n\n",
                )
                result = self.assert_pass()
                self.assertEqual("pending", result["semantic_review"])
                self.assertEqual("not-authorized", result["publication_status"])

    def test_break_fix_resolution_status_rejects_remedy_kinds(self):
        for status in ["fix", "workaround", "mitigation"]:
            with self.subTest(status=status):
                self.make_bundle(("break-fix",))
                self.edit_article("resolution_status: unverified", "resolution_status: " + status)
                self.assert_fail("schema-enum-invalid")

    def test_verified_resolution_does_not_waive_complete_reference_review(self):
        self.make_bundle(("break-fix",))
        self.edit_article("resolution_status: unverified", "resolution_status: verified")
        self.edit_article("reference_status: incomplete", "reference_status: complete")
        result = self.assert_fail("semantic-review-required")
        self.assertEqual("passed", result["mechanical_status"])
        self.assertEqual("pending", result["semantic_review"])
        self.make_review()
        result = self.assert_pass(self.check(review_path=self.review_path))
        self.assertEqual("reported-supported", result["semantic_review"])
        self.assertEqual("not-authorized", result["publication_status"])

    def test_frontmatter_duplicate_key_and_invalid_tags(self):
        self.edit_article("wiki_type: qa", "wiki_type: qa\nwiki_type: qa")
        self.assert_fail("frontmatter-key-invalid-or-duplicate")
        self.make_bundle()
        self.edit_article("tags: []", "tags: {}")
        self.assert_fail("frontmatter-tags-invalid")

    def test_heading_order_required(self):
        self.edit_article("## Topic and scope", "## Incorrect heading")
        self.assert_fail("article-headings-mismatch")

    def test_step_must_be_inside_procedure(self):
        self.make_bundle(("how-to",))
        self.edit_article("## Troubleshooting and rollback\n\nNot established.", "## Troubleshooting and rollback\n\n### Step 2 - Hidden new action\n\nDo an unsupported action.")
        self.assert_fail("step-heading-outside-procedure")

    def test_real_inspection_date_required(self):
        for value in ["2026-02-30", "2026-99-99", "Not independently inspected"]:
            with self.subTest(value=value):
                self.make_bundle()
                self.edit_article("**Inspected on:** 2026-09-16", "**Inspected on:** " + value)
                self.assert_fail("source-inspection-date-invalid")

    def test_code_action_with_external_citation_is_allowed(self):
        self.make_bundle(("how-to",))
        self.edit_article("**Action:** " + CLAIM, "**Action:**\n\n```\n" + CLAIM + "\n```")
        self.assert_pass()

    def test_review_pending_and_required_review_fails(self):
        self.assertEqual("pending", self.assert_pass()["semantic_review"])
        result = self.assert_fail("semantic-review-required", self.check(require_semantic_review=True))
        self.assertEqual("passed", result["mechanical_status"])

    def test_review_accepted_reports_review_not_authentication(self):
        self.make_bundle(("qa", "how-to", "break-fix"))
        self.make_review(kind="separate-agent")
        result = self.assert_pass(self.check(review_path=self.review_path, require_semantic_review=True))
        self.assertEqual("reported-supported", result["semantic_review"])
        self.assertIn("source-authenticity-not-verified", result["limitations"])
        self.assertIn("reviewer-identity-not-authenticated", result["limitations"])

    def test_qualified_review_accepted_with_reason(self):
        self.make_review(verdict="qualified")
        result = self.assert_pass(self.check(review_path=self.review_path, require_semantic_review=True))
        self.assertEqual("reported-qualified", result["semantic_review"])

    def test_generator_attestation_rejected(self):
        self.make_review(kind="generator")
        self.assert_fail("schema-enum-invalid", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_unsupported_and_unreviewed_claims_rejected(self):
        self.make_review(verdict="unsupported")
        self.assert_fail("review-claim-unsupported", self.check(review_path=self.review_path, require_semantic_review=True))
        review = self.make_review()
        review["articles"][0]["claims"] = []
        self.write_json(self.review_path, review)
        self.assert_fail("review-claim-coverage-incomplete", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_conflicting_duplicate_verdict_rejected(self):
        review = self.make_review()
        review["articles"][0]["claims"].append({"id": "C1", "verdict": "qualified", "reason": "Conflicting second verdict."})
        self.write_json(self.review_path, review)
        self.assert_fail("review-claim-unresolved-or-duplicate", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_review_coverage_and_extra_claims_rejected(self):
        for change in ["coverage", "extra"]:
            with self.subTest(change=change):
                review = self.make_review()
                if change == "coverage":
                    review["articles"][0]["coverage"] = "sample-reviewed"
                else:
                    review["articles"][0]["claims"].append({"id": "C2", "verdict": "supported", "reason": "Undeclared claim."})
                self.write_json(self.review_path, review)
                self.assert_fail(result=self.check(review_path=self.review_path, require_semantic_review=True))

    def test_stale_article_hash(self):
        self.make_review()
        self.edit_article("# Synthetic sample", "# Synthetic sample revised")
        self.assert_fail("review-article-hash-mismatch", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_stale_evidence_bytes_even_whitespace(self):
        self.make_review()
        with self.evidence_path.open("ab") as stream:
            stream.write(b"\n")
        self.assert_fail("review-evidence-hash-mismatch", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_reference_complete_requires_review_and_rebind_after_status_edit(self):
        self.make_review()
        self.edit_article("reference_status: incomplete", "reference_status: complete")
        self.assert_fail("semantic-review-required")
        self.assert_fail("review-article-hash-mismatch", self.check(review_path=self.review_path))
        self.make_review()
        self.assert_pass(self.check(review_path=self.review_path))

    def test_true_quote_with_unrelated_claim_remains_pending_or_fails_review_gate(self):
        self.edit_article("**Answer:** " + CLAIM, "**Answer:** " + UNRELATED)
        self.evidence["articles"][0]["claims"][0]["text"] = UNRELATED
        self.save_evidence()
        self.assertEqual("pending", self.assert_pass()["semantic_review"])
        self.assert_fail("semantic-review-required", self.check(require_semantic_review=True))
        self.make_review(verdict="unsupported")
        self.assert_fail("review-claim-unsupported", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_review_invalid_schema_types_never_raise(self):
        for key, value in [("articles", {}), ("reviewer_kind", []), ("evidence_sha256", []), ("schema_version", True)]:
            with self.subTest(key=key):
                review = self.make_review()
                review[key] = value
                self.write_json(self.review_path, review)
                self.assert_fail(result=self.check(review_path=self.review_path, require_semantic_review=True))

    def test_review_missing_sibling_article_rejected(self):
        self.make_bundle(("qa", "how-to"))
        review = self.make_review()
        review["articles"].pop()
        self.write_json(self.review_path, review)
        self.assert_fail("review-article-coverage-incomplete", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_review_duplicate_json_keys_fail(self):
        self.review_path.write_text('{"schema_version":1,"schema_version":1}', encoding="utf-8")
        self.assert_fail("json-duplicate-key", self.check(review_path=self.review_path, require_semantic_review=True))

    def test_missing_file(self):
        self.paths = [self.directory / "missing.md"]
        self.assert_fail("file-missing")

    def test_file_limit_and_empty_file(self):
        self.paths[0].write_bytes(b"x" * (validator.MAX_FILE_BYTES + 1))
        self.assert_fail("file-too-large")
        self.paths[0].write_bytes(b"")
        self.assert_fail("file-empty")

    def test_source_text_and_structure_limits(self):
        self.evidence["sources"][0]["text"] = "x" * (validator.MAX_TEXT_CHARS + 1)
        self.save_evidence()
        self.assert_fail("schema-text-invalid")
        self.make_bundle()
        self.edit_article("## Topic and scope", "\n".join("### More" for _ in range(validator.MAX_HEADINGS + 1)) + "\n\n## Topic and scope")
        self.assert_fail("article-structure-limit-exceeded")

    def test_claim_occurrence_limit(self):
        self.edit_article("## Topic and scope", (CLAIM + "\n") * (validator.MAX_CLAIM_OCCURRENCES + 1) + "\n## Topic and scope")
        self.assert_fail("claim-occurrence-limit-exceeded")

    def test_malformed_encoding_bom_and_nul(self):
        for raw in [b"\xff", b"\xef\xbb\xbf{}", b"\x00", b"one\rtwo"]:
            with self.subTest(raw=raw):
                self.evidence_path.write_bytes(raw)
                self.assert_fail("file-encoding-invalid")

    def test_explicit_absolute_paths_and_unique_names(self):
        self.assert_fail("file-path-invalid", validator.validate_bundle([Path("qa.md")], self.evidence_path))
        self.assert_fail("file-name-collision", validator.validate_bundle([self.paths[0], self.paths[0]], self.evidence_path))

    def test_declared_file_outside_approved_directory(self):
        nested = self.directory / "nested"
        nested.mkdir()
        other = nested / "qa.md"
        other.write_bytes(self.paths[0].read_bytes())
        self.assert_fail("file-directory-mismatch", validator.validate_bundle([other], self.evidence_path))

    def test_local_traversal_and_undeclared_links(self):
        for target, expected in [
            ("../secret.md", "local-link-outside-approved-directory"),
            ("%2e%2e%2fsecret.md", "local-link-outside-approved-directory"),
            ("%252e%252e%252fsecret.md", "local-link-outside-approved-directory"),
            ("sub/../qa.md", "local-link-outside-approved-directory"),
            ("C:\\secret.md", "local-link-outside-approved-directory"),
            ("//host/share.md", "local-link-outside-approved-directory"),
            ("private.md", "local-link-undeclared-target"),
        ]:
            with self.subTest(target=target):
                self.make_bundle()
                self.edit_article("## Topic and scope", f"[Navigation]({target})\n\n## Topic and scope")
                self.assert_fail(expected)

    def test_sibling_link_declared_target_is_allowed(self):
        self.make_bundle(("qa", "how-to"))
        self.edit_article("## Topic and scope", "[Procedure](how-to.md)\n\n## Topic and scope")
        self.assert_pass()

    def test_reference_style_html_image_and_unparsed_links_rejected(self):
        for content, code in [
            ("[Link][hidden]\n\n[hidden]: ../private.md", "markdown-reference-links-not-supported"),
            ('<a href="../private.md">Link</a>', "markdown-html-or-autolink-not-supported"),
            ("![Image](qa.md)", "markdown-link-syntax-not-supported"),
            ("[Link](../private(foo).md)", "markdown-link-syntax-not-supported"),
            ("[Outer [nested]](../private.md)", "markdown-link-syntax-not-supported"),
            ("[Link][hidden]\n\n> [hidden]: ../private.md", "markdown-reference-links-not-supported"),
        ]:
            with self.subTest(content=content):
                self.make_bundle()
                self.edit_article("## Topic and scope", content + "\n\n## Topic and scope")
                self.assert_fail(code)

    def test_manifest_cannot_make_validator_read_additional_articles(self):
        self.evidence["articles"][0]["file"] = "undeclared.md"
        self.save_evidence()
        self.assert_fail("declared-article-manifest-mismatch")

    def test_outside_symlink_file_is_rejected(self):
        outside = self.directory / "outside"
        outside.mkdir()
        target = outside / "qa.md"
        target.write_bytes(self.paths[0].read_bytes())
        link = self.directory / "linked.md"
        try:
            os.symlink(target, link)
        except OSError as error:
            self.skipTest("Host does not permit unprivileged symlink creation: " + type(error).__name__)
        self.assert_fail("file-outside-approved-directory-or-not-regular", validator.validate_bundle([link], self.evidence_path))

    def test_resolved_outside_target_rejected_without_read_even_without_symlink_privilege(self):
        original_resolve = Path.resolve
        original_open = Path.open
        outside = self.directory / "outside" / "qa.md"
        reads = []

        def resolve(path, *args, **kwargs):
            if path == self.paths[0]:
                return outside
            return original_resolve(path, *args, **kwargs)

        def open_path(path, *args, **kwargs):
            reads.append(path)
            return original_open(path, *args, **kwargs)

        with mock.patch.object(Path, "resolve", resolve), mock.patch.object(Path, "open", open_path):
            self.assert_fail("file-outside-approved-directory-or-not-regular")
        self.assertNotIn(outside, reads)

    def test_no_network_no_mutations_only_declared_reads(self):
        undeclared = self.directory / "unapproved.txt"
        undeclared.write_text("Synthetic data deliberately not declared.", encoding="utf-8")
        before = {p.name: p.read_bytes() for p in self.directory.iterdir()}
        reads = []
        original_open = Path.open

        def open_path(path, mode="r", *args, **kwargs):
            self.assertEqual("rb", mode)
            reads.append(path)
            return original_open(path, mode, *args, **kwargs)

        with mock.patch.object(Path, "open", open_path), mock.patch.object(socket, "socket", side_effect=AssertionError("network forbidden")), mock.patch.object(socket, "create_connection", side_effect=AssertionError("network forbidden")):
            self.assert_pass()
        self.assertEqual({*self.paths, self.evidence_path}, set(reads))
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.directory.iterdir()})

    def test_cli_json_success_failure_and_no_sensitive_errors(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = validator.main(["--article", str(self.paths[0]), "--evidence", str(self.evidence_path)])
        self.assertEqual(0, code)
        self.assertEqual("passed", json.loads(output.getvalue())["status"])
        output = io.StringIO()
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
            code = validator.main(["--unknown", "DO-NOT-ECHO-THIS"])
        self.assertEqual(1, code)
        self.assertNotIn("DO-NOT-ECHO-THIS", output.getvalue())
        self.assertEqual("failed", json.loads(output.getvalue())["status"])

    def test_public_json_parser_never_echoes_input(self):
        with self.assertRaises(validator.ValidationError) as error:
            validator.strict_json_loads('{"private":"DO-NOT-ECHO","private":1}')
        self.assertEqual("json-duplicate-key", str(error.exception))

    def test_invalid_api_arguments_report_static_failure(self):
        for article_paths, evidence_path, kwargs in [
            (self.paths[0], self.evidence_path, {}),
            (self.paths, self.evidence_path, {"deny_terms": None}),
            (self.paths, self.evidence_path, {"deny_terms": "not-an-array"}),
            (self.paths, self.evidence_path, {"require_semantic_review": 1}),
            (self.paths, self.directory / "\x00" / "evidence.json", {}),
        ]:
            with self.subTest(kwargs=kwargs):
                self.assert_fail(result=validator.validate_bundle(article_paths, evidence_path, **kwargs))


if __name__ == "__main__":
    unittest.main()
