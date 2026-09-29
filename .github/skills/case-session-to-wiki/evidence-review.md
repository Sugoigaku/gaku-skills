# Embedded Sources and Honest Review

This edition has no executable validator. The rules below are an agent-applied
checklist, not automated schema enforcement, a privacy scanner, cryptographic
attestation, or proof that claims are true. Inspect the source and saved article
directly; do not generate a replacement validation script.

## Self-contained supporting material

Save Markdown articles only. Do not create `evidence.json`, another evidence
sidecar, a source register, or a claim/enrichment ledger. Supporting material
belongs in the article using the [source formats](templates.md#source-entry):

- Official documentation: descriptive title/section link to the inspected safe
  canonical URL, with a short relevant original passage under References.
- Session dialogue or visible tool result: short de-identified excerpt adjacent
  to the supported answer/action, attributed to the actual role, without a link
  or artificial line locator.
- Supplied document excerpt without an inspected official origin: plain-text
  title/section, the excerpt, and a brief inspection limitation.

Check support for each material statement internally, but do not persist or print
the working claim map. Keep observed, reported, documented, and inferred results
distinct in ordinary prose. Documentation does not prove a procedure ran, and
an assistant suggestion does not establish a diagnosis. Include only sources
actually used, preserving scope and later corrections without an audit narrative.

## Article metadata

Use simple YAML front matter with one scalar per key and no duplicate keys,
aliases, nested structures, or hidden instructions. Optional `title` and
`product` are safe strings; `tags` is an array of safe strings.

| Field | Values in this edition |
| --- | --- |
| `wiki_type` | `qa`, `how-to`, `break-fix` |
| `article_format` | `concise` |
| `status` | `draft` |
| `review_status` | `pending-engineer-review` |
| `validation_method` | `agent-checklist` |
| `source_kind` | `current-session`, `provided-transcript`, `local-session` |
| `source_coverage` | `partial`; `complete-for-provided-transcript` only under the input contract |
| `content_mode` | `documentation-enriched`, `extraction-only` |
| `reference_status` | `incomplete`, `checklist-checked` |

How-to additionally requires `procedure_status`: `unverified`,
`documented-not-tested`, or `verified-in-source`.
Break-fix requires `root_cause_status`: `unknown`, `suspected`, or `confirmed`,
and `resolution_status`: `unverified`, `reported`, or `verified`.
QA must not inherit these type-specific outcome fields.

Default all templates to partial coverage, incomplete references, and unverified/
unknown outcomes. Upgrade only when actual evidence satisfies the relevant
contract. This edition never assigns `mechanically-checked` or `complete`,
nor `complete-for-selected-visible-events`.

Existing drafts and evidence sidecars are not silently rewritten, deleted,
upgraded, or certified. New generation uses embedded sources only; revising an
older output requires an explicit request.

## Agent checklist

Use these as acceptance criteria, not a mandatory sequence of tool calls.
Check source support and privacy before persistence; confirm the saved result
through full readback. Reuse checks on unchanged content. After a correction,
recheck affected claims/files and cross-file dependencies instead of replaying
the entire checklist. Do not substitute field presence for actual inspection.
Keep detailed working review out of the article body.

| Check | Required inspection | Failure response |
| --- | --- | --- |
| Input and coverage | Exact selected source, all available requested pages, explicit gaps, honest source kind/coverage | Request supported input or narrow scope; never infer unseen turns |
| Structure | One selected template, one H1, ordered H2 sections, sequential Q/Step headings, no instructional leftovers | Correct draft; omit empty optional sections including References for session-only material |
| Readability | Direct technical answers; exact UI actions or full commands; important impact up front; no repetitive evidence audit | Fill from permitted originals or block an unsafe/incomplete procedure |
| Embedded sources | Markdown-only output; documentation references and session excerpts are inside each article, with no sidecar dependency | Embed permitted supporting material and remove sidecar links before saving |
| Claim coverage | Every material answer, condition, command, check, cause, outcome, and diagram relation has nearby support | Add inspected documentation or an attributed excerpt; remove/block unsupported claims |
| Original quotation | Compare each embedded excerpt directly with its inspected original; identify redactions and summary-only input | Correct misquotes; never reconstruct dialogue or mistake an assistant assertion for proof |
| Locator and origin | Actual document title/section/version and safe URL, or actual session role plus the included passage | Request missing documentation location; do not invent session links or line numbers |
| Entailment and scope | The passage supports this exact claim and its conditions, values, and version | Qualify, remove, or block; isolated words and true but irrelevant quotes do not support a claim |
| Chronology | Later corrections, meaningful failed checks, and contrary results are retained | Resolve by evidence or leave uncertainty explicit |
| Enrichment and outcomes | Added actions sourced, no inherited success, reported vs observed distinguished, mode honored | Correct labels; missing evidence cannot be fixed by stronger wording |
| Privacy | Inspect all text, metadata, filenames, URLs including decoded forms, code, captions, labels, and excerpts | Remove or visibly redact before persistence; stop if meaning is lost |
| Links and diagrams | Safe documentation links; no links on session excerpts; sibling files exist in this batch; no active Mermaid | Fix links, simplify/omit diagram; do not fetch undeclared files |
| Delivery | Correct existing session parent, fresh create-only folder/files, full readback, visible Windows paths and link targets agree with actual paths | Repair formatting, including the separator before `.copilot`; on write/access/integrity failure stop further writes and report exact subsets |

In articles use simple visible documentation links and same-directory sibling
basenames; no traversal, device/absolute local source links, hidden HTML, or
undeclared file reads. Final delivery links are separate: they point to the
verified absolute output paths as described in [local delivery](session-workflow.md#verify-and-finish).
Check sibling fragments if used, or link to the file without a fragment.
Code blocks cannot supply visible source citations.

Human/agent checks can miss misquotes, private names, or omitted claims.
Never report guaranteed redaction or deterministic validation from this workflow.
Only after every applicable checklist item is checked, no required reference
gap remains, and saved content is read back may a delivered draft be described
as `checklist-checked`. If that metadata was updated, read back and recheck the
edited file too. Any unchecked item keeps references incomplete; material source
or privacy gaps block delivery of the affected article as a ready review draft.

## Independent review and publication

Generator self-review is not independent review. The engineer or a genuinely
separate reviewer must inspect every substantive claim before relying on or
distributing the draft. Provide only de-identified files to an authorized
reviewer, never raw sessions or credentials. Do not launch paid review agents
or a factory automatically.

The reviewer checks original authenticity, entailment, document location/version,
applicability, chronology, exact procedure inputs, execution evidence,
significant impact/rollback, privacy, diagram meaning, and delivery accuracy.
Qualified claims must carry their limitation in the article; unsupported claims,
unknown origins, misquotes, missing safety steps, and omitted claims require changes.

This skill does not generate review attestations, authenticate reviewers, bind
reviews to cryptographic hashes, or automatically promote references to complete.
Any article/evidence edit invalidates prior review of that content; request
fresh review rather than reusing a stale approval. Keep final drafts pending
engineer review, even after the generator's checklist.

Independent review is distinct from explicit authorization to publish to a
defined audience. Neither local saving nor any checklist pass authorizes
publication, messaging, live-system changes, or executing the article's commands.
