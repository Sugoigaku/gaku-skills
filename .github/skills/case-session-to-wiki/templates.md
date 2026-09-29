# Wiki Templates

Read only the selected type and Source entry sections. Consult
[authoring](authoring.md#topic-and-type-selection) when the reader task is unclear.
These are full-article templates. A requested sample step or excerpt uses only
the relevant portion with its necessary citation and qualifications, not the
whole template, front matter, or unrelated sections.
The fenced blocks below are authoring templates, not articles to save unchanged.
Replace placeholders and remove instructional text. Keep the selected H2 order,
one H1, and sequential H3 Q/Step headings. Omit References when no documentation
is used; session excerpts belong beside the answers/actions they support.
Omit Before you start only if there
are no essential prerequisites or significant impact. Omit Double-check when
there are no actual open items; otherwise it must be last.

Use direct answers/actions, not repeated validation forms. For procedures,
apply [detailed-action guidance](authoring.md#detailed-actions-simple-structure);
the templates organize the article, not limit its necessary detail.

Default statuses are conservative. Follow [metadata and evidence rules](evidence-review.md#article-metadata)
before changing them. Source kind must reflect actual input, not the request's
wording. Every substantive claim needs a nearby documentation citation or
attributed session excerpt. Do not create source IDs, claim maps, or sidecars.

## QA template

```markdown
---
title: "<Topic>"
wiki_type: qa
article_format: concise
status: draft
review_status: pending-engineer-review
validation_method: agent-checklist
product: "<Product/version if relevant>"
source_kind: current-session
source_coverage: partial
content_mode: documentation-enriched
reference_status: incomplete
tags: []
---

# <Topic>

## Questions and answers

### Q1. <Question>

<Direct answer with essential version/scope limits and a descriptive documentation
link or an adjacent attributed session excerpt.
Repeat Q headings only for distinct questions. Do not force a case timeline,
cause, or repair section into QA.>

## References

<Insert compact documentation entries; omit this section for session-only sources.>

## Double-check

<Actual unresolved questions identifying the affected answer; omit if none.>
```

## How-to template

```markdown
---
title: "<Achieve a specific goal>"
wiki_type: how-to
article_format: concise
status: draft
review_status: pending-engineer-review
validation_method: agent-checklist
product: "<Product/version if relevant>"
source_kind: current-session
source_coverage: partial
content_mode: documentation-enriched
reference_status: incomplete
procedure_status: unverified
tags: []
---

# How to <achieve the goal>

## Goal

<What the reader will achieve and its essential scope.>

## Before you start

<Essential role, prerequisites, important impact, and supported rollback needs.
Omit only if unnecessary. Do not bury critical safety blockers at the end.>

## Steps

### Step 1 - <Action>

<Detailed numbered substeps: where to begin, how to open the interface, exact
navigation/options, values to enter, and apply/save actions. For a practical
documented CLI route, include the full command block, variables, placeholders,
execution context, and Notes explaining inputs and results. No ellipses or
hidden setup. Explain meaningful failures/stops. Cite supporting sources.>

## Check the result

<Full check command or exact UI actions, what to look for, and how to interpret
it. Distinguish observed results from checks that have not been executed.>

## References

<Insert compact documentation entries; omit this section for session-only sources.>

## Double-check

<Actual uncertainties with affected step; omit if none.>
```

## Break-fix template

```markdown
---
title: "<Failure and distinguishing condition>"
wiki_type: break-fix
article_format: concise
status: draft
review_status: pending-engineer-review
validation_method: agent-checklist
product: "<Product/version if relevant>"
source_kind: current-session
source_coverage: partial
content_mode: documentation-enriched
reference_status: incomplete
root_cause_status: unknown
resolution_status: unverified
tags: []
---

# <Failure and distinguishing condition>

## Problem

<Recognizable symptom, scope, and a supported cause only when established.
Do not turn a hypothesis into a confirmed cause or invent an outage.>

## Before you start

<Important impact, required roles/prerequisites, and supported rollback needs,
stated once. Omit only if nothing material applies.>

## Identify the issue

<Decisive same-issue checks with exact log/page navigation or full diagnostic
commands, what to look for, and what matching/non-matching results mean.
A matching error alone is insufficient. Include useful exclusions and stops.>

## Steps

### Step 1 - <Action>

<Detailed numbered substeps, exact UI navigation/options/values and apply/save
choices, or a complete documented command block with explained inputs and Notes.
State required setup, observable results, and meaningful failure handling.
Call a workaround a workaround. Cite the actual supporting passages.>

## Check the result

<Full check command or exact UI actions and what confirms recovery. Keep actual
recorded results separate from proposed checks or reported success.>

## References

<Insert compact documentation entries; omit this section for session-only sources.>

## Double-check

<Only unresolved points with the relevant step or conclusion; omit if none.>
```

## Source entry

Choose the source format below. No `S1`/`C1` identifiers, artificial `Lines 1-N`
locators, provenance forms, or evidence-file links. The article must be usable
without another file. Keep qualifications relevant to the technical answer.

### Official documentation

Use a descriptive document/section link near the supported claim. In References,
include the exact title, relevant section, applicable version if needed, and a
short inspected passage that actually supports the answer, not a few isolated
words. A verified section anchor is useful but not required. Group references
to the same document rather than repeating metadata for every sentence.

```markdown
- [<Exact official document title>](<safe-canonical-HTTPS-URL>) - <Relevant section; applicable version if needed>.
  > <Short exact supporting passage, preserving essential conditions and values.>
```

### Session conversation or visible tool result

Place the relevant excerpt directly after the answer/action it supports. Attribute
the actual visible role and distinguish a report, proposal, or observed result.
Do not link the excerpt to a session, message, file, or same-page source anchor.
Do not invent a message number, timestamp, source ID, or line locator.

```markdown
**Session excerpt (Engineer; reported):**
> <Relevant original words with only necessary visible redactions.>
```

Use `Assistant; proposed` or `Tool result; observed` only when that matches the
source. If an engineer supplied a document excerpt without an inspected official
origin, use a plain-text label with its supplied title/section and say "supplied
excerpt; original not independently inspected"; do not invent a link.

Mark edited quotations "Excerpt redacted" and show omissions with `[...]`.
Keep original wording distinct from interpretation. A compacted summary is not
an original dialogue excerpt; disclose that limit rather than reconstruct speech.

## Optional diagram placement

Follow [diagram rules](diagrams.md). Put a small Mermaid concept diagram inside
an existing relevant section before References, immediately followed by a
cited `Diagram:` caption. Do not add a mandatory diagram section or asset file.
Do not leave links to these skill instructions in the generated article.
