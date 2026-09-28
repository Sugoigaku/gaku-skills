# Wiki Templates

Read only the selected type and Source entry sections. Consult
[authoring](authoring.md#topic-and-type-selection) when the reader task is unclear.
These are full-article templates. A requested sample step or excerpt uses only
the relevant portion with its necessary citation and qualifications, not the
whole template, front matter, or unrelated sections.
The fenced blocks below are authoring templates, not articles to save unchanged.
Replace placeholders and remove instructional text. Keep the selected H2 order,
one H1, and sequential H3 Q/Step headings. Omit Before you start only if there
are no essential prerequisites or significant impact. Omit Double-check when
there are no actual open items; otherwise it must be last.

Use direct answers/actions, not repeated validation forms. For procedures,
apply [detailed-action guidance](authoring.md#detailed-actions-simple-structure);
the templates organize the article, not limit its necessary detail.

Default statuses are conservative. Follow [metadata and evidence rules](evidence-review.md#article-metadata)
before changing them. Source kind must reflect actual input, not the request's
wording. Every substantive claim needs a nearby source citation and a companion
mapping. Do not copy example IDs as evidence without actual supporting records.

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

<Direct answer with essential version/scope limits and an inline citation.
Repeat Q headings only for distinct questions. Do not force a case timeline,
cause, or repair section into QA.>

## References

[Evidence details](evidence.json)

<Insert a compact source entry for each used source.>

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

[Evidence details](evidence.json)

<Insert compact source entries.>

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

[Evidence details](evidence.json)

<Insert compact source entries.>

## Double-check

<Only unresolved points with the relevant step or conclusion; omit if none.>
```

## Source entry

Under References, repeat this block per used passage. Use nearby `[S1](#s1)`
citations in the article body. Public source links target the actual safe
canonical URL; sanitized private sources target `evidence.json`. That file is
in the same directory as the article. For explicit chat-only delivery, use
inline source records instead of nonexistent file links, following
[the chat-only contract](session-workflow.md#explicit-chat-only-delivery).

```markdown
### S1

**Source:** [<Exact source title>](<safe-public-origin-or-evidence.json>)

**Location:** <Exact locator matching the companion>

**Original excerpt:**

> <Short exact supporting passage matching the companion text.>
```

For a visibly redacted/shortened passage, insert
`**Excerpt handling:** redacted` immediately before Original excerpt.
Keep the exact quote separate from interpretation. Do not paraphrase quoted
words or invent locators. Publisher, inspection, claim basis, enrichment,
execution state, and other provenance stay in the companion.

## Optional diagram placement

Follow [diagram rules](diagrams.md). Put a small Mermaid concept diagram inside
an existing relevant section before References, immediately followed by a
cited `Diagram:` caption. Do not add a mandatory diagram section or asset file.
Do not leave links to these skill instructions in the generated article.
