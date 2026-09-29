# Sources, Enrichment, and Privacy

Read the sections applicable to the sources actually used. Enrichment is
available for a named gap, not mandatory research for every article. Before any
output, apply de-identification to all included content.

## Inspect originals first

Collect references actually supporting the selected topics: documents, primary
observations, supplied originals, and visible tool results. Prefer original
publisher documentation over summaries. Use only authorized access.

1. Read the relevant original passage or explicitly supplied excerpt.
2. For official documentation, retain its actual title, safe canonical URL,
   relevant section, applicable version, and a short supporting passage.
3. For session evidence, select the relevant original words and actual visible
   role. Include them directly in the article, without links or invented locators.
4. Check each answer, condition, action, check, diagnosis, outcome, and diagram
   against its supporting passage. A symptom quotation is not proof of cause.
5. Preserve version differences, corrections, and contradictory evidence.

A URL, search snippet, login page, title, AI paraphrase, or repeated assistant
claim is not an inspected original. Do not invent URLs, quotations, revisions,
dates, sections, anchors, or line numbers. Never fetch additional customer/case
systems as part of this skill. On access failure, report the limitation and
request an accessible original/excerpt. A missing official document location
must not be replaced by an invented one.

## Exact locations and excerpts

| Source | Required safe locator |
| --- | --- |
| Public documentation/KB | Actual canonical URL and section/subheading or verified anchor; revision when exposed |
| Supplied document | Safe title/version plus page and section/paragraph |
| Source code | Safe repository identity, actual revision, relative file, and exact line range |
| Selected session conversation/report/tool result | Actual visible role plus the relevant excerpt embedded beside the claim; no link or artificial line locator |

For session evidence, the included attributed excerpt supplies context; an
anonymous archive line, session ID, or "earlier in chat" does not. No line
numbering or reverse map to the private archive is needed or permitted.
If only a compacted summary is visible, identify it as a summary; never fabricate
an original dialogue quote from it. Narrow the claim or request the original
when that distinction materially changes the answer.

Quote only a short permitted original passage necessary for the claim. Do not
copy whole documents or substantial passages. Keep interpretation outside the
quotation. Preserve the original language; an English explanation is separate,
not a replacement quotation. Show omissions as `[...]` and label visibly
redacted or shortened text "Excerpt redacted"; never call edited text verbatim.

Compare embedded quotes directly to the actual inspected passage.
Apart from line endings and Markdown blockquote markers, do not normalize away
differences in wording, spaces, punctuation, or meaning. Fuzzy agreement and
translation are not exact quotation. Do not generate supporting text from the
article and call it evidence.

Say an original was inspected only when it was actually read. Label an engineer's
supplied document excerpt "original not independently inspected" when appropriate.
Missing originals remain unavailable. A supplied excerpt can support a limited
claim without implying publisher authenticity. Mention a missing version only
when it affects applicability; never invent one or add "Not provided" padding.

## Compact inline attribution

Every substantive claim has a nearby descriptive documentation link or attributed
session excerpt outside code. Different claims in a step may need different
passages. Support actual Double-check assertions too; include only used sources.

Use the two [source formats](templates.md#source-entry):

- Official documentation: link the exact title/section to its safe canonical
  URL and give a short relevant passage in References. Preserve conditions,
  values, and scope needed to support the answer; a two-word fragment is not
  enough for a detailed numerical or procedural claim.
- Session evidence: quote the actual relevant dialogue or visible tool result
  beside the claim, with a plain-text role and reported/proposed/observed label.
  No session/message links, local-file links, or same-page source anchors.
- Supplied document without an inspected official origin: use a plain-text
  title/section and the supplied excerpt, with its inspection limitation.

No `evidence.json`, replacement sidecar, numbered source register, or persisted
claim map. Keep the supporting passage in each article; a sibling Wiki is not
original evidence. A bibliography with only URLs is incomplete. Do not replace
technical answers with repetitive evidence audits or commentary on earlier AI errors.

## Documentation enrichment

`documentation-enriched` is the default. For a specific missing prerequisite,
UI action, API signature, expected behavior, or explanation, inspect narrowly
relevant official documentation through available authorized tools. Use generic
technical terms only. Never send customer names, case numbers, private logs,
resource identifiers, or secret-bearing URLs to a search service.

When explicitly requested, `extraction-only` limits technical content to the
selected source and its already-cited originals. Do not add new procedures or
technical enrichment. Missing details remain gaps rather than invented steps.

Enrichment may add a supported explanation, complete a documented action,
replace environment-specific values with placeholders, or propose a safer
documented alternative. Broad research, uncertain versions, missing access,
and material scope expansion require clarification.

Distinguish observed, reported, documented, and inferred statements in ordinary
prose where it matters. A documented fact can remain documented in extraction-only mode
when it comes from an already-cited original; that mode forbids new additions,
not truthful documentation labels.

For added/adapted procedures, cite the inspected supporting documentation and
state once that the new sequence has not been run, unless the selected source
actually demonstrates that exact validation. Repeat the limitation only for
steps whose status differs. Syntax success is not end-to-end execution.
Do not add a separate enrichment ledger or repetitive per-step status forms.

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
  URL paths/queries/fragments, source locations, and embedded excerpts.
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

Use a de-identified inline excerpt for private observations and supplied excerpts
without an inspected safe public origin. Its role/title is plain text, not a
synthetic origin URI or a lookup back to the case. Local saving is not independent
factual or publication approval.

If safe de-identification destroys essential meaning or a required document location, stop
and ask for a shareable source or narrower claim. Do not retain identities for
traceability or substitute an unresolvable placeholder and call it complete.
If even a short sanitized supporting excerpt cannot be included safely, narrow
or block the affected claim. The absence of an evidence sidecar is not a blocker.

## Reference gate

Before saving, check every claim's support, actual source inspection, relevant
document location or session role, exact or explicitly redacted quotation,
applicability, citation links, and all output privacy surfaces. Missing critical references block
the affected article until evidence is supplied or unsupported scope removed.

Keep `reference_status: incomplete` while any required support is unresolved.
Only the completed [agent checklist](evidence-review.md#agent-checklist) permits
`checklist-checked`; it does not establish deterministic validation, source
authenticity, complete case history, successful execution, or engineer approval.
