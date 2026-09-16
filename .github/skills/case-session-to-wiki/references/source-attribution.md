# Source Attribution Contract

This contract is mandatory for QA, How-to, and Break-fix. References identify
what supports the article; they are not decorative further-reading links.
Default concise articles show only a linked title, precise locator, and short
original excerpt. The companion retains the full source, claim, and review
records. Do not duplicate those records as a long metadata form in the Wiki.

## Building the source catalog

1. Collect the references actually used in the selected conversation: document
   links, supplied originals, source-code locations, reports, and tool output.
   Prefer original publisher documentation over summaries when available.
2. Inspect the relevant original passage through an authorized tool, or read the
   engineer-supplied source. Default documentation enrichment allows targeted
   official-source lookup for a specific gap using generic technical terms.
   In extraction-only mode, limit retrieval to already-cited originals.
   Follow the [enrichment boundaries](enrichment.md); do not silently expand scope.
3. Record a unique ID such as `S1` using the
   [source entry template](../templates/source-entry-template.md). Distinguish
   documentation, transcript, and tool-output sources.
4. Map each supported answer, instruction, matching check, diagnosis, and outcome
   to the precise passage that substantiates it. Reuse an ID only for the same
   entry and location; use another entry when a different passage is needed.
   IDs are unique across the evidence companion and retain the same meaning in
   every article that uses them.
5. Preserve corrections, contradictory sources, version differences, and limits.
   Do not resolve conflicts by choosing whichever source makes the story simpler.

AI responses are extraction candidates, not authoritative references. An AI
claim must be traced to inspected documentation or primary evidence before it
becomes an asserted technical answer. A suggestion may be described as proposed
with a transcript citation, never as a verified procedure.

If no external document was provided or verified, say so. Cite primary evidence
for narrowly scoped case observations instead of inventing a publication.
General product limits, guarantees, and support policies require applicable
authoritative documentation, not a generalization from one case.

## Exact locations and original excerpts

Record both the origin and a precise location within it:

| Source | Required locator |
| --- | --- |
| Web documentation or KB | Actual title, canonical non-identifying URL, section/subheading or a verified anchor; revision when available |
| PDF or supplied document | Identifiable safe title/version and page plus section/paragraph |
| Source code | Safe repository identity, actual commit/revision, relative file, and line range |
| Supplied transcript | Approved sanitized companion record and exact positions within that record; the source role stays explicit |
| Tool result or log excerpt | Approved sanitized companion record and line positions, with minimal supporting output and tool-success qualifications |

If positions were not supplied, number them explicitly within the approved
sanitized record. Never pretend they are original archive message IDs. A source
ID alone, a home page, anonymous archive record number, or "earlier in the chat"
is not portable provenance.

Quote only the short original passage necessary to support the claim, where
quotation is permitted. Do not reproduce whole documents or substantial passages.
Do not turn paraphrases, recollections, translations, or search snippets into
purported original text. Keep interpretation outside the quotation.

Retain the source's original language. An English explanation can follow, but
does not replace the original. Mark omissions explicitly and label redacted
excerpts as redacted, using visible placeholders; never call edited text verbatim.
If quoting safely is not possible, request a shareable source or remove the
unsupported claim. A link without an available supporting excerpt is not complete.

For mutable pages, record the inspected version/update date when exposed and
the actual inspection date. Do not invent version numbers, dates, anchors, or
line ranges. If no revision exists, say `Not provided by source`.

## Access and verification

- `original-inspected`: the relevant original source was actually read.
- `supplied-excerpt-only`: the engineer supplied an excerpt and locator, but the
  publisher's original was not independently inspected. State that limitation.
- `unavailable`: the relevant original/excerpt could not be read. This cannot be
  used as verified support for a substantive claim.

A fetch that returns an access-denied page or a login form is not a successful
inspection. Report the limitation and request an accessible original or excerpt.
Never bypass access controls or send case/customer identifiers to search tools.

Public links must not contain credentials or customer-specific identifiers.
Access-controlled documentation links need explicit approval for the intended
audience before persistence. Do not include private case links or signed URLs.
If a precise locator cannot survive de-identification, do not replace it with an
unresolvable placeholder and claim completeness; ask for a safe alternative.

## Inline citations

Place a Markdown link to the source entry beside the supported content, not just
at the bottom of the page. The [source entry template](../templates/source-entry-template.md)
demonstrates the link and entry shape.

- QA: cite each substantive answer and any material condition or exception.
- How-to: cite each step's action, required inputs, expected output, and safety
  guidance; different claims in a step may need different references.
- Break-fix: cite matching and non-matching criteria, cause, repair steps, and
  validation results. Do not cite a symptom-only passage as proof of the cause.

Every citation must resolve to exactly one compact embedded source entry. Include only
sources actually used. A title or citation ID without a supporting original
excerpt does not satisfy the contract.
Link the companion once in References. Keep any Double-check items after
References, at the end of the article; cite their supporting sources if needed.

## Approved evidence companion

The generation request authorizes a de-identified evidence companion beside the
articles in the selected session's new run folder. No separate local-save prompt
is required. Follow [session-local delivery](session-output.md), perform privacy
checks internally, and use the [validator's schema](evidence-validation.md).

- Public documentation records contain their canonical safe URL, exact locator,
  version, inspection state, and a short permitted supporting passage.
- `public-document` requires an actual safe HTTPS origin. A supplied excerpt
  without a canonical public URL is `sanitized-evidence`, even when it appears
  to quote a document. Do not invent a URL or label it public just from its title.
- Private observations become `sanitized-evidence` records with a stable
  `approved-evidence:<safe-id>` origin and exact lines within the included
  sanitized text. Article source entries point to the companion and source ID.
- Do not retain source session IDs, archive paths, identity maps, full logs,
  secrets, or a recoverable reverse map. The source's historical private
  authenticity remains a reviewer responsibility; do not imply public verification.
- Redacted text is compared against the approved sanitized passage, never labeled
  as untouched verbatim text. Keep redaction decisions explicit.
- The companion includes a claim map for each article and records material
  procedural enrichment. A claim map is itself reviewable and may be incomplete.
- A supplied excerpt can be valid supporting evidence with
  `supplied-excerpt-only`; lack of independent publisher inspection alone does
  not make its text unavailable. Semantic review remains a separate pending gate.
- Do not generate companion text from the article and call that independent
  evidence. First inspect the original, select the minimal passage, sanitize it,
  and perform the privacy checks before session-local saving.

If the engineer explicitly prohibits storing sanitized evidence, honor that
restriction and report the dependent articles as blocked. Do not replace it
with unresolvable private archive citations or print private evidence to the console.

## Reference completeness gate

Before saving a review draft, inspect all of the following:

- Every substantive assertion and instruction has appropriate inline support.
- Each cited entry includes its identifiable origin, exact location, short
  original excerpt, and verification/access status.
- The excerpt matches what was read or explicitly supplied; redactions and
  omissions are marked, and interpretation is not disguised as quotation.
- The source supports this claim within the stated product/version/scope.
- Citation links resolve, IDs are unique, and no invented or unused sources remain.
- No required original or locator is unavailable, and no identifying information
  or secret is introduced by references or quotes.

An explicitly supplied excerpt may support a limited claim with its provenance
clearly labeled; do not describe it as independently checked publisher guidance.
Reference completeness is not proof of full session coverage, source infallibility,
successful execution, or engineer approval.

On missing source material, keep `reference_status: incomplete`, list the exact
gaps, and ask for originals/locations only when necessary. Automatic local-save
authorization does not create missing evidence.

Run the [mechanical validator](../tools/validate_wiki.py) on approved local review
files and their companion. A pass can support `reference_status:
mechanically-checked`; rerun after changing that metadata. Quote matching proves
consistency with the supplied passage, not its authenticity or entailment.

Only a separate [semantic review](semantic-review.md), covering all substantive
claims and bound to final article/evidence hashes, permits reference status
`complete`. Use `--require-semantic-review` for that gate. The validator checks
an attestation, not the reviewer's identity or correctness. Any changed bytes
invalidate prior review; no automatic result ever authorizes publication.
