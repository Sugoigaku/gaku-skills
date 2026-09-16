# Local evidence validator: schema and mechanical contract

`tools/validate_wiki.py` is a Python 3.10+ standard-library-only, read-only,
offline validator. It reads only the files explicitly passed to it. It does not
generate articles, evidence, review attestations, redaction maps, or transcripts;
fetch links; inspect historical sessions; execute example commands; authenticate
reviewers; or publish anything.

The engineer must approve the sanitized evidence contents and destination
**before** creating the bundle. Approval cannot be established by this helper.
Do not give it raw transcripts or credential/customer identity maps. There is
no automatic redactor.

## CLI and exit contract

From the skill directory, using already-approved absolute input paths:

```text
python tools\validate_wiki.py --article C:\approved\qa-toggle.md --article C:\approved\how-to-toggle.md --evidence C:\approved\evidence.json
python tools\validate_wiki.py --article C:\approved\qa-toggle.md --evidence C:\approved\evidence.json --deny-term PRIVATE-LABEL --review C:\approved\review.json --require-semantic-review
```

Repeat `--article` and `--deny-term` as needed. There are no implicit input paths,
directory discovery, recursive reads, glob expansion, writes, or network calls.
Omitting `--review` reports semantic review as `pending`. Supplying
`--require-semantic-review`, or setting **any** declared article's
`reference_status: complete`, requires an acceptable attestation for the
**entire declared bundle**.

Normal validation, including invalid CLI arguments, emits one JSON object to
stdout and returns exit code **0** for `passed`, **1** for `failed`.
`--help` is the normal argparse text-help exception. Diagnostics report only
static categories and positional locations, not matching text, JSON values,
filenames, absolute paths, or exception details. Reader-provided deny terms are
never printed by the helper; be aware that shells may retain CLI arguments in
their own command histories.

The report shape is:

```json
{
  "schema_version": 1,
  "status": "passed",
  "mechanical_status": "passed",
  "semantic_review": "pending",
  "publication_status": "not-authorized",
  "issues": [],
  "hashes": {
    "evidence_sha256": "<lowercase SHA-256 of exact evidence bytes>",
    "articles": [{"index": 0, "sha256": "<lowercase SHA-256 of exact article bytes>"}]
  },
  "limitations": [
    "source-authenticity-not-verified",
    "regex-redaction-not-proof",
    "claim-map-completeness-not-verified",
    "semantic-support-not-independently-verified",
    "reviewer-identity-not-authenticated",
    "no-execution-or-publication-authorization"
  ]
}
```

An issue is exactly
`{"code":"<static-code>","location":"<positional-location>","domain":"mechanical|semantic","severity":"error"}`.
Locations use CLI article order (`article[0]`), zero-based JSON/block indexes,
and one-based line numbers. Parsed-JSON privacy locations deliberately identify
key/value **positions**, not user-controlled key names. Early failures can
return `"hashes": {}`. Issues are deduplicated and sorted deterministically.
`mechanical_status` excludes semantic-domain review failures; `status` includes
all failures. Semantic states are `pending`, `rejected`, `reported-supported`,
and `reported-qualified`. `reported-*` means only that a matching attestation
**reports** those verdicts; it is not an authenticated approval.

### Stable Python entry points

```python
validate_bundle(
    article_paths, evidence_path, *,
    deny_terms=(), review_path=None, require_semantic_review=False
) -> dict
strict_json_loads(text) -> object
normalize_excerpt(text) -> str
sha256_bytes(data) -> str
safe_https_url(value) -> bool
scan_sensitive(text, location, deny_terms=()) -> list[Issue]
main(argv=None) -> int
```

`article_paths` is an iterable of absolute `str`/`pathlib.Path` paths, not a
single string; the evidence/review arguments each identify one absolute file.
`strict_json_loads` raises `ValidationError` with a static code for malformed
JSON, duplicate keys at any level, and nonfinite constants.
`Issue.as_dict()` produces the issue shape above. Names beginning with `_`
are implementation details. Importing the module performs no validation.

## File and directory boundary

- The explicitly selected evidence file's resolved parent is the approved
  directory. All articles, evidence, and optional review must have that same
  parent. Their resolved file targets must also remain directly in it.
- Filenames are ASCII safe basenames: 1–100 stem characters, first
  alphanumeric, remaining alphanumeric/underscore/hyphen; exact lowercase
  `.md` for articles and `.json` for evidence/review. Windows reserved device
  stems, case-insensitive name collisions, and resolved-target collisions fail.
  `evidence.json` is the convention, not a hardcoded filename.
- Relative input paths, `..` input components, missing/empty/unreadable files,
  nonregular files, and symlinks resolving outside the directory fail. Links to
  undeclared files fail without reading the target. Internal same-directory
  symlinks are allowed only without target collisions.
- Each file has a fixed **2 MiB (2,097,152 bytes)** maximum, including review.
  Reads are bounded even if a file grows. Files must be UTF-8 without BOM, NUL,
  or lone CR. LF and CRLF are accepted. Article/evidence hashes always bind
  **original bytes**, not normalized text.
- Maximums: 32 articles; 256 evidence sources; 512 claims and 512 enrichments
  per article; 4,096 characters per nonempty evidence/review text field.
  Each article allows at most 2,048 headings and 4,096 visible source citations;
  each selected claim allows at most 64 exact occurrences before references.
  These bounds prevent ambiguous/repetitive input from creating unbounded work.
  An empty enrichment array is allowed; empty sources/articles/claims are not.
  JSON is strict: unknown/missing keys, duplicate keys, unknown schema
  versions, wrong types, nonfinite numbers, invalid controls, and malformed
  strings fail. Boolean `true` is not accepted as integer schema version `1`.
- Validation is a local snapshot, not an adversarial filesystem transaction.
  Do not run it in a directory subject to concurrent/untrusted replacement.
  It does not authenticate human approval of the directory or its contents.

## Evidence companion schema v1

These are the exact allowed keys. All are required; no arbitrary extensions,
raw/archive paths, credential maps, customer identity fields, or source-session
IDs are accepted.

```json
{
  "schema_version": 1,
  "sources": [{
    "id": "S1",
    "kind": "public-document",
    "title": "Synthetic feature reference",
    "publisher": "Example publisher",
    "origin": "https://docs.example.org/features/toggle",
    "locator": "Section: Sample toggle",
    "version": "v1.2.3",
    "inspection_status": "original-inspected",
    "text": "The synthetic toggle enables the sample feature.",
    "excerpt_handling": "verbatim"
  }],
  "articles": [{
    "file": "how-to-toggle.md",
    "claims": [{
      "id": "C1",
      "text": "The synthetic toggle enables the sample feature.",
      "source_ids": ["S1"],
      "basis": "documented"
    }],
    "enrichments": [{
      "section": "Step 1 - Enable the synthetic toggle",
      "source_ids": ["S1"],
      "change": "Add the documented action and checkpoint.",
      "validation": "not-run"
    }]
  }]
}
```

Source IDs match `S[1-9][0-9]{0,5}` and are unique across the bundle. Claim IDs
match `C[1-9][0-9]{0,5}` and are unique **within their article**. Source-ID arrays
are nonempty, unique, and resolve to declared sources. Article filenames must
exactly match the full explicitly declared article set. Every source must be
used by a claim somewhere in that set, but need not appear in every sibling.

### Provenance and locator rules

`kind` is `public-document` or `sanitized-evidence`.
`inspection_status` is `original-inspected` or `supplied-excerpt-only`;
`unavailable` cannot support a selected claim. `excerpt_handling` is `verbatim`
or `redacted`. Fields except `text` must be single-line.

For **public-document**, `origin` must be lexical HTTPS with:

- a DNS-shaped dotted host; no userinfo, IP literal, alternate port except
  443, whitespace, backslash, unsafe delimiters, or double encoding;
- optional query selectors using only the exact case-sensitive keys `view`,
  `preserve-view`, and `tabs`, each at most once. Each value must be nonempty
  ASCII letters/digits/`.`/`_`/`-`, with `&` separating selectors. Empty queries
  or values, repeated keys, unknown keys, percent encoding, and all other value
  characters are rejected. For example, `?view=windowsserver2025-ps` and
  `?view=windowsserver2025-ps&preserve-view=true&tabs=powershell` are allowed
  only if all existing identifier/secret checks also pass;
- no obvious private host labels (`localhost`, `intranet`, `internal`,
  `private`), private suffixes (`.local`, `.internal`, `.localhost`, `.corp`,
  `.msft.net`), or case-service suffixes (`.microsofticm.com`,
  `.microsoftcrmapps.com`, `.dynamics.com`);
- no `cases` or `incidents` path segments and no scanner-detected identifiers
  or credentials, including after percent decoding.

Fragments are permitted. This is a conservative lexical allow policy, **not**
proof that a hostname/document is public, authoritative, accessible, or genuine.
It intentionally rejects some legitimate links. Use canonical safe URLs or an
approved sanitized evidence record; never bypass the check by inventing a URL.
Query selectors are never silently removed or normalized: the complete origin,
including its query and fragment, must match the article's source-entry origin.
Reader-specific deny terms continue to apply to the complete stored URL.

Public locators must be one of `Section: <nonempty exact section>`,
`Anchor: #safe-anchor`, `Page N` (optionally `, <exact detail>`), or
`Lines N` / `Lines N-M`. Positions must start at positive integers. The helper
does not fetch or confirm those locations in the publisher's original.

For **sanitized-evidence**, `origin` is
`approved-evidence:<safe-id>`, where `<safe-id>` matches
`[a-z][a-z0-9-]{2,63}`. It is a portable label for this included approved
sanitized text, **not** an anonymous private archive record. Locator is exactly
`Lines 1` for a one-line record or `Lines 1-N` for all N lines in `text`
(including blank lines after CRLF normalization). Thus line positions are
explicitly relative to the included approved record, not invented historical
transcript offsets. Do not encode real session/case IDs in safe labels.

`basis` is `observed`, `reported`, `documented`, or `inferred`. Observed/reported
claims need at least one `sanitized-evidence` source. This classification is a
declaration, not independent verification of execution.

## Article Markdown contract

This validator intentionally supports a **restricted Markdown/front-matter
contract**, not arbitrary YAML or a complete CommonMark parser.

### Metadata and headings

Required metadata and exact values:

| Field | Allowed values |
| --- | --- |
| `wiki_type` | `qa`, `how-to`, `break-fix` |
| `status` | `draft` only |
| `review_status` | `pending-engineer-review` only |
| `source_kind` | `current-session`, `provided-transcript`, `local-session` |
| `source_coverage` | `partial`, `complete-for-provided-transcript`, `complete-for-selected-visible-events` |
| `content_mode` | `documentation-enriched`, `extraction-only` |
| `reference_status` | `incomplete`, `mechanically-checked`, `complete` |

Documentation-enriched is the authoring default, but must be recorded
explicitly; the validator does not silently default missing metadata.
Current-session coverage must remain `partial`. The two `complete-for-*`
values require the matching `provided-transcript` and `local-session` kinds,
respectively. None means whole-case coverage.

Optional `title` and `product` are nonempty scalar strings; `tags` is a JSON
array of nonempty strings. All other keys are rejected except these
**required type-specific outcomes**:

- QA: no outcome/root-cause fields.
- How-to: `procedure_status` = `unverified`, `documented-not-tested`, or
  `verified-in-source`.
- Break-fix: `root_cause_status` = `unknown`, `suspected`, or `confirmed`;
  `resolution_status` = `unverified`, `reported`, or `verified`, describing
  recovery evidence. Remedy kind (`fix`, `workaround`, or `mitigation`) belongs
  in the article prose, not this metadata field. A `verified` resolution does
  not establish reference completeness or waive the separate semantic-review
  requirement for `reference_status: complete`.

Use `---` delimiters at the start; one `key: scalar` per line; bare safe
strings, JSON double-quoted strings, or single-quoted strings. YAML aliases,
multiline values, duplicate keys, arbitrary maps, and comments are unsupported.
Keep the exact ordered H2 headings from the corresponding existing template
and exactly one H1. QA answer blocks are sequential H3
`Q1. <question>`, `Q2. <question>`, etc. Procedure/repair blocks are sequential
H3 `Step 1 - <action>`, etc., inside the template's procedure/repair section.
At least one block is required. Step headings elsewhere fail.

The QA block requires nonempty `Answer`, `Conditions and exceptions`, and
`Sources` fields. How-to requires `Where`, `Inputs`, `Action`, `Why`,
`Expected result`, `If the result differs`, `Safety and rollback`, and `Sources`.
Break-fix repair requires `Prerequisites and impact`, `Action`,
`Expected result`, `If it fails`, `Rollback`, and `Sources`.
Use the template's `**Field name:**` notation, with each field on its own line.

### Source entries and exact quotations

Under `## References and original excerpts`, include `### S1`, etc., once per
cited source. Use **all** fields in `source-entry-template.md` in their exact
order. Values for source type, title, publisher, origin, exact location,
version, verification, and excerpt handling must equal the companion record,
not merely be present. Origin can be a bare URL or a single Markdown link with
that exact URL. Other matched values are plain single-line text.

Evidence linkage is exactly:

```markdown
**Evidence record:** S1 in [evidence.json](evidence.json)
```

When an alternate companion filename is explicitly supplied, use it in both
the link label and destination. Public source access is `Public`; sanitized
source access is `engineer-provided` or `approved restricted documentation`.
`Inspected on` is a real ISO date, or `Not independently inspected` only for
`supplied-excerpt-only`. These are reported states, not authenticated fetch logs.
`Supports` and `Interpretation and limits` must be nonempty.

Put the exact passage between `**Original excerpt:**` and
`**Interpretation and limits:**`, with every line—including paragraph
separators—explicitly quoted:

```markdown
**Original excerpt:**

> First paragraph copied from the approved record.
>
> Second paragraph copied from the approved record.

**Interpretation and limits:** Scope and connection to the claim, outside the quote.
```

Only CRLF→LF and blockquote formatting are normalized: up to three spaces of
indentation, one `>` marker, and at most one following space. No whitespace
collapse, punctuation changes, translation, fuzzy matching, or paraphrase
equivalence is accepted. Internal paragraph breaks and remaining leading or
trailing spaces matter. Surrounding empty separator lines outside the quote
are ignored. Redacted passages are compared to the already-approved sanitized
record; the helper neither edits originals nor proves the redaction truthful.

### Claims, citations, and enrichment

- Inline source citations use exactly `[S1](#s1)`. Source anchors are unique;
  wrong IDs/fragments, missing entries, and uncited embedded sources fail.
- Every selected claim's exact `text` must occur in the article **before**
  the references section. It may omit the attached citation. No semantic
  equivalence search or article-to-evidence generation takes place.
- All claim source IDs need a visible matching citation in the same nearest
  heading-delimited neighborhood, within 1,200 characters of the claim.
  A source entry's quote is not a body claim or a substitute for a body citation.
- Every QA answer and procedure/repair block needs both a visible citation and
  a mapped claim within that block. All cited IDs in each block must be covered
  by its mapped claims; the body-wide cited ID set must equal the claim-map
  source-ID set. This **does not** discover every uncited substantive sentence,
  prove relevance, or establish that a claim map is complete.
- Fenced/indented code and inline code cannot supply visible citations or
  headings. Claim text can include an exact code example, but must have a
  visible nearby citation outside code.
- Each procedure/repair step must have exactly one
  `**Provenance:** observed-in-session|documentation-enriched|adapted-from-documentation`
  and `**Execution validation:** not-run|syntax-only|lab-tested` label.
- Any section explicitly labeled enriched/adapted needs exactly one enrichment
  record naming its exact existing heading, supporting source IDs,
  nonempty `change`, and matching `validation`. The section's own direct
  content—not merely a child section—must cite those IDs. Records pointing
  to absent/ambiguous headings fail. An observed label cannot have an enrichment
  record. Nonprocedural sections, including QA answers, can also carry these
  paired labels and records.
- Extraction-only prohibits every enrichment record and every enriched/adapted
  label. Its procedure steps must be labeled observed-in-session and contain
  an observed/reported mapped claim backed by sanitized evidence. Relabeling a
  documented claim as an observed step is not enough. A dishonest replacement
  of **both** the evidence declarations and claim map cannot be detected
  semantically by this helper.

### Links

Use simple inline `[label](destination)` links with no nested brackets/parentheses,
whitespace/title attribute, or images. Reference-style links, raw HTML/comments,
HTML/angle autolinks, and images fail. A local destination must be a bare
declared filename (optionally with a fragment) or an existing same-article
`#anchor`; no scheme, drive, network path, slash, backslash, query, `..`,
or residual percent encoding after decoding is accepted. Local targets must
resolve directly inside the approved directory. Only same-article fragments
are resolved; sibling-file fragments are not verified. External links must
pass the same conservative HTTPS policy as public origins, but are never
fetched. Raw text URLs are leak-scanned, not followed.

## Hash-bound separate review schema v1

The full exact schema is:

```json
{
  "schema_version": 1,
  "reviewer_kind": "human",
  "evidence_sha256": "<SHA-256 of exact evidence file bytes>",
  "articles": [{
    "file": "how-to-toggle.md",
    "sha256": "<SHA-256 of exact article file bytes>",
    "coverage": "all-substantive-claims-reviewed",
    "claims": [{
      "id": "C1",
      "verdict": "supported",
      "reason": "The original passage supports this scoped claim."
    }]
  }]
}
```

`reviewer_kind` is `human` or `separate-agent`; `generator` and every other
value fail. Each declared article and selected claim must appear exactly once.
Unknown/missing articles/claims, duplicate or conflicting verdicts, missing
reasons, stale hashes, partial coverage, unknown values, and unsupported claims
fail. Verdicts are `supported`, `qualified`, or `unsupported`; `qualified`
requires a nonempty reason, but the helper cannot judge whether it is adequate.
An invalid supplied review fails even without `--require-semantic-review`.

This file reports another reviewer's judgment. It has no identity/signature
authentication; a generator falsely asserting `separate-agent` cannot be
distinguished mechanically. A matching hash proves only byte binding.

The helper never changes `reference_status`, outcomes, semantic status fields,
or publication state in input files. Default drafts stay `incomplete`.
If a gate chooses `mechanically-checked`, persist that change through the
separate approved authoring workflow. A `complete` reference label must be
present in the exact bytes a separate reviewer attests: **changing the label
after a review invalidates its hash**, just like editing a quote or claim.
Re-review and rebind after every article/evidence edit, including whitespace,
CRLF changes, and front-matter-only edits. Do not automatically relabel a stale
attestation or regenerate its hashes on the reviewer's behalf.

## Privacy flags and limitations

Suspicious content is a **blocking error**, including in filenames,
front matter, Markdown/code/link labels, excerpts, decoded JSON strings, and
review reasons. Checks include GUIDs, 13–20 digit case-shaped decimal IDs,
IPv4/IPv6 literals, email addresses, common user/UNC/file paths, private-key
headers, bearer credentials, credential assignments, JWT-shaped tokens, signed
URL/query patterns, and case-insensitive reader-supplied deny terms. Version
prefixes (`v1.2.3.4`, `version 1.2.3.4`, `revision 1.2.3.4`), explicit `OID`
prefixes, and dotted OIDs longer than four components are not treated as IPv4.
SHA hashes are not mistaken for standalone decimal case IDs.

False positives are intentional; narrow/rewrite the approved draft or choose
a safe original rather than bypassing the check. False negatives are possible:
regexes cannot identify all customer names, encodings, obfuscated credentials,
private URLs, paraphrased source text, or factual misattribution. This is not a
security sanitizer, complete Markdown interpreter, copyright-permission check,
claim-entailment engine, or proof of de-identification.

**A true quote can accompany an unrelated claim and pass mechanically.** Without
attestation it remains semantic-review `pending` and fails required semantic
review. A separate review reporting `unsupported` fails. A dishonest attestation
reporting `supported` is not detected; honesty, independence, source inspection,
claim coverage, contradictions, and qualification quality remain reviewer duties.

## Synthetic verification

From the repository root:

```text
python -m unittest discover -s tests -p test_wiki_validation.py -q
```

Tests generate only synthetic bundles using `TemporaryDirectory` explicitly
rooted under `tests/fixtures/wiki-validation`, never the operating system temp
directory. They clean their generated files. No stored real drafts, cases,
transcripts, or network resources are used. Tests cover all three formats,
quote/locator/claim/enrichment tampering, strict JSON, privacy flags, unsupported
or stale reviews, reference-status hash binding, traversal, declared-only reads,
and no network/file mutations by the validator. A real symlink test skips on
Windows hosts lacking symlink privilege; a deterministic resolved-target test
still exercises the outside-directory rejection without reading the target.
