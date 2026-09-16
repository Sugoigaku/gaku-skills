# Sources, Enrichment, and Privacy

## Inspect originals first

Collect references actually supporting the selected topics: documents, primary
observations, supplied originals, and visible tool results. Prefer original
publisher documentation over summaries. Use only authorized access.

1. Read the relevant original passage or explicitly supplied excerpt.
2. Assign an extraction-local unique source ID such as `S1`. Reuse it only for
   the same passage and locator; keep its meaning consistent across the batch.
3. Record the actual title, publisher/source role, safe origin, exact locator,
   version when exposed, inspection state, short passage, and excerpt handling.
4. Map each answer, condition, action, check, diagnosis, outcome, and diagram
   claim to its supporting passage. A symptom quotation is not proof of cause.
5. Preserve version differences, corrections, and contradictory evidence.

A URL, search snippet, login page, title, AI paraphrase, or repeated assistant
claim is not an inspected original. Do not invent URLs, quotations, revisions,
dates, sections, anchors, or line numbers. Never fetch additional customer/case
systems as part of this skill. On access failure, report the limitation and
request an accessible original/excerpt with a precise safe locator.

## Exact locations and excerpts

| Source | Required safe locator |
| --- | --- |
| Public documentation/KB | Actual canonical URL and section/subheading or verified anchor; revision when exposed |
| Supplied document | Safe title/version plus page and section/paragraph |
| Source code | Safe repository identity, actual revision, relative file, and exact line range |
| Private transcript/report/tool result | Portable sanitized companion source ID and exact lines within its included passage |

An anonymous archive line, session ID, "earlier in chat," or source ID without
an included record is not portable provenance. Number sanitized record lines
explicitly and say they are local to that included passage, not original event
or tool-call IDs. Do not persist a reverse map to the private archive.

Quote only a short permitted original passage necessary for the claim. Do not
copy whole documents or substantial passages. Keep interpretation outside the
quotation. Preserve the original language; an English explanation is separate,
not a replacement quotation. Mark omissions and use `excerpt_handling: redacted`
for visibly redacted or shortened text; never call edited text verbatim.

Compare quotes to the actual inspected passage, then to the sanitized companion.
Apart from line endings and Markdown blockquote markers, do not normalize away
differences in wording, spaces, punctuation, or meaning. Fuzzy agreement and
translation are not exact quotation. Do not generate companion text from the
article and call it evidence.

Use `original-inspected` only when the relevant original was actually read.
Use `supplied-excerpt-only` when an engineer supplied a passage but the publisher's
original was not independently inspected. Missing originals remain unavailable,
not selected supporting records. A supplied excerpt can support a limited claim
without implying publisher authenticity. Where no revision is exposed, record
`Not provided by source`, never an invented version.

## Compact inline attribution

Every substantive claim has a nearby `[S1](#s1)`-style citation outside code,
resolving to exactly one `### S1` entry in that article's References. Different
claims in a step may need different sources. Cite actual Double-check assertions
too. Include only used sources and keep identifiers unique.

Use the [compact source entry](templates.md#source-entry): linked exact title,
precise location, short original excerpt, and a redaction label when needed.
Public records link to their actual safe origin; private observations link to
the same-directory companion. Link `evidence.json` once at the top of References;
private source entries may also target it. Detailed provenance and claim/
enrichment records stay in the companion rather than cluttering the Wiki.

The source title, origin, locator, and excerpt must agree with the companion.
Keep the supporting source in each article; a sibling Wiki is not original
evidence. A bibliography with only URLs or an uncited source list is incomplete.

## Documentation enrichment

`documentation-enriched` is the default. For a specific missing prerequisite,
UI action, API signature, expected behavior, or explanation, inspect narrowly
relevant official documentation through available authorized tools. Use generic
technical terms only. Never send customer names, case numbers, private logs,
resource identifiers, or secret-bearing URLs to a search service.

When explicitly requested, `extraction-only` limits technical content to the
selected source and its already-cited originals. Do not add new procedures or
enrichment records. Missing details remain gaps rather than invented steps.

Enrichment may add a supported explanation, complete a documented action,
replace environment-specific values with placeholders, or propose a safer
documented alternative. Broad research, uncertain versions, missing access,
and material scope expansion require clarification.

Record claim basis in the companion as `observed`, `reported`, `documented`,
or `inferred`. A documented fact can remain documented in extraction-only mode
when it comes from an already-cited original; that mode forbids new additions,
not truthful documentation labels.

For every added/adapted procedural section, record its exact heading, source
IDs, what changed, and execution-validation state in `enrichments`. Keep that
metadata out of repetitive visible forms. Default new steps to `not-run`.
Use `syntax-only` or `lab-tested` only with evidence of that exact validation;
syntax success is not end-to-end execution.

New commands, changed parameters, permissions, sequencing, network/certificate
settings, or rollback instructions cannot inherit an earlier experiment's
success. Keep a documentation-supported procedure `documented-not-tested` until
the exact sequence has relevant execution evidence. Proposed repairs cannot
upgrade resolution status.

Never recommend historical accept-all certificate checks, swallowed errors, or
unscoped deletion. Explain the limitation of such observations and use a sourced
safe alternative if available, labeled as a new untested step. The extraction
workflow never runs transcript or documentation commands. High-impact lab work
requires separate explicit authorization outside generation.

## De-identification before persistence

Review the whole output, not just the prose:

- Titles, metadata, filenames, tables, code/comments, diagram labels, quotations,
  URL paths/queries/fragments, source locators, claim maps, and every JSON field.
- Remove customer/person names, emails, case/incident numbers, subscription/
  tenant/resource IDs, hostnames, IP addresses, environment-specific paths,
  customer-private links, exact case timestamps, tokens, passwords, private
  keys, bearer strings, signed URLs, and all other credentials.
- Use consistent placeholders such as `<CLIENT_HOST>`, `<SERVICE_HOST>`,
  `<RESOURCE_ID>`, or `<LOCAL_PATH>` only where needed. Remove irrelevant
  identifiers. Preserve relations such as "same subnet," order of events,
  public product names/versions, ports, protocols, configuration keys, and
  useful non-identifying error codes.
- Never save raw logs, transcripts, source screenshots, reader output, attachment
  dumps, original session IDs/paths, cursors, or a reversible identity map.
- Do not retain an access-controlled documentation link without explicit
  approval for its intended audience. That disclosure approval is separate
  from the routine local save.

Use public HTTPS source URLs without userinfo, signed tokens, private hostnames,
case-service links, identifiers, or credential queries. Preserve applicable
version selectors (`view`, `preserve-view`, `tabs`) only after inspecting their
values for identifying content. For other queries, obtain a verified safe
canonical source; never silently strip a required selector or invent an origin.
Check decoded URL forms as well as the visible text.

Use a `sanitized-evidence` record for private observations and supplied excerpts
without a verified safe public origin. Its origin is `approved-evidence:<safe-id>`,
a label for included de-identified text, not an external document or a lookup
back to the case. The word "approved" describes the locally authorized sanitized
record; it is not independent factual or publication approval.

If safe de-identification destroys essential meaning or a usable locator, stop
and ask for a shareable source or narrower claim. Do not retain identities for
traceability or substitute an unresolvable placeholder and call it complete.
If the engineer prohibits companion storage, block dependent articles instead
of printing evidence to the console or using anonymous archive citations.

## Reference gate

Before saving, check every claim's support, actual source inspection, precise
locator, exact or explicitly redacted quotation, applicability, citation links,
unique IDs, and all output privacy surfaces. Missing critical references block
the affected article until evidence is supplied or unsupported scope removed.

Keep `reference_status: incomplete` while any required support is unresolved.
Only the completed [agent checklist](evidence-review.md#agent-checklist) permits
`checklist-checked`; it does not establish deterministic validation, source
authenticity, complete case history, successful execution, or engineer approval.
