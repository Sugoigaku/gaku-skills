---
name: case-session-to-wiki
description: "Extract reusable, de-identified knowledge from a technical support case conversation into a QA, How-to, or Break-fix Markdown wiki, with original supporting excerpts and exact source attribution. Use when the engineer explicitly asks to turn a case session into a wiki, distill a troubleshooting conversation, or capture reusable case lessons near closure. Not for live troubleshooting, ordinary case notes, or closing a case."
---

# Case Session to Wiki

Version: 0.2.0. Last reviewed: 2026-09-16.

## Purpose

Help a technical support engineer preserve the useful knowledge from a case
session, including later follow-up questions. Write for the next engineer facing
the same failure, not for someone auditing the original conversation.

Extract what was learned, why a decision was made, what actually worked, how it
was verified, and where the conclusions stop. Do not simply shorten the chat.

## Contract

- **Input:** the available current conversation or an engineer-selected local
  transcript. Inspect existing evidence and the originals of cited documents;
  no broad searches, other-session discovery, or new case-system investigation.
- **Output:** one de-identified Markdown article per selected topic, using the
  [template selector](templates/wiki-template.md): QA, How-to, or Break-fix.
- **Attribution:** every article must contain inline source citations, original
  supporting excerpts, and exact safe locations. A URL-only bibliography fails.
- **Default state:** `draft`, pending engineer review. Record source coverage
  and reference completeness separately, plus relevant type-specific statuses.
- **Persistence:** preview first; write only to an explicitly approved local
  destination. Do not save raw transcripts, a redaction map, or private evidence.
- **Execution:** instruction-driven, on demand. No exporter, background job,
  telemetry, publication, or live diagnostic execution is included.

Read the [extraction rules](references/extraction-rules.md) and
[source attribution contract](references/source-attribution.md) before processing
source material. Neither format selection nor privacy review waives attribution.

## Workflow

### 1. Establish the source boundary

Use the selected source only. Do not search other sessions, browse internal
session databases, or assume access to a complete conversation archive.

For current-context input, record `source_kind: current-session` and
`source_coverage: partial`. For an explicitly supplied transcript, read all
accessible parts in order; record `complete-for-provided-transcript` only if none
were skipped or truncated. Otherwise record `partial` and describe the gaps.
Never request hidden reasoning, system instructions, or credential stores.

If the engineer requests the entire history but it is unavailable, ask for an
exported transcript or permission to make a partial draft. Do not fabricate an
export command, tool, old turn, attachment, or missing command output. If sources
are combined, retain the more conservative coverage and explain each source.

### 2. Select the topic and wiki type

Use the [selection rules](templates/wiki-template.md#selection-rules).
Honor an explicit format request; otherwise select the dominant reader intent
and briefly explain it. Ask if multiple formats are equally plausible or the
requested type would hide necessary safety or diagnostic information.

- **QA:** clarify a topic through direct questions and supported answers.
- **How-to:** achieve a defined goal through a beginner-followable procedure.
- **Break-fix:** identify the same failure and restore the affected operation.

Keep one coherent topic per article, and one failure mode per Break-fix.
Include useful follow-up questions. For unrelated topics, ask which to draft
or whether to split them. Do not silently combine or discard useful topics.

If the source is only administrative chatter, say there is not enough reusable
technical content and ask for evidence. Do not produce a success-shaped wiki.

### 3. Build the source catalog and evidence inventory

Walk the source in order so later corrections can qualify earlier conclusions.
Assign local source IDs such as `S1`; these are extraction labels, not invented
original message IDs. Create a [source entry](templates/source-entry-template.md)
for every reference used, and connect each claim to the supporting passage.

Read already-cited originals through available authorized tools when needed.
Do not treat search snippets, a login page, a title, or an AI paraphrase as the
original. If access fails, state the failure and request an accessible excerpt
with its exact location. Do not bypass access controls, transmit case details to
search services, or infer missing text from memory.

For each candidate finding, capture:

| Field | Meaning |
| --- | --- |
| Finding | A reusable technical claim or decision |
| Source kind | Tool output, engineer report, cited document, or AI suggestion |
| Evidence | Source ID, original supporting excerpt, and exact safe location |
| Disposition | Supported, reported, proposed, rejected, or unresolved |
| Qualification | Version/scope limits, contradictions, or missing verification |

Keep this working inventory in the current context. Persist only the minimal
de-identified source entries in the article. AI suggestions are not authoritative
documentation or proof of execution. A source may support one claim but not another.

### 4. Extract knowledge rather than conversation

Apply the [selection rules](references/extraction-rules.md#what-to-keep).
Preserve discriminating checks, meaningful failed attempts, decision branches,
the final supported answer to follow-up questions, and conditions under which
the fix applies. Remove greetings, repetition, scheduling, and superseded advice.

For QA, consolidate repeated questions and put the direct answer first. Preserve
conditions and exceptions; do not force a case timeline into the answer.

For How-to, state the goal and define necessary terms and prerequisites. Expand
each step into where to act, exact inputs/actions, expected results, and what to
do if the result differs. Cite documented details rather than inventing missing
steps. Identify documentation-derived steps that were not tested in the case.

For Break-fix, provide both same-issue checks and lookalike exclusions before
repair instructions. Separate confirmed/suspected/unknown cause and distinguish
a fix from a workaround or mitigation. Reported recovery is not measured
verification, and temporal correlation alone is not causation.

### 5. De-identify before drafting

Apply the [privacy rules](references/extraction-rules.md#de-identification).
Review titles, metadata, filenames, tables, code blocks, links, excerpts, and
source locators. Preserve necessary technical relationships using consistent
placeholders; never persist the reverse mapping.

If safe de-identification would remove essential meaning, pause and ask how to
narrow the article. Do not silently retain identifying details.

### 6. Compose and pass the format and reference gates

Use exactly one selected type template and retain its section order. Replace
template instructions with supported content. Use `Not established` or
`Not recorded` for genuine gaps, not for hiding a missing critical prerequisite.
Remove instructional links to the skill bundle from the rendered article.

Every substantive QA answer, How-to step, Break-fix matching check, diagnosis,
repair, and verification claim must link to its source entry in the same article.
Embed full entries from the [shared source template](templates/source-entry-template.md);
do not merely link to that template or append unrelated reading material.

Apply the [reference gate](references/source-attribution.md#reference-completeness-gate).
Set `reference_status: complete` only when it passes. If not, present the gaps
and request the missing original/location or narrow the unsupported claims.
An incomplete preview may be discussed, but must not be saved as a finished wiki.

QA must remain concise and question-led. How-to must have sufficient sourced
detail for each prerequisite, action, and checkpoint; stop at missing critical
steps rather than claiming the guide is runnable. Break-fix must explain when
not to apply the fix and how to verify recovery. Keep contradictions visible.
Never execute transcript or documentation commands during extraction.

Keep `status: draft` and `review_status: pending-engineer-review`. List unresolved
questions and the specific points the engineer needs to validate.

### 7. Preview, approve, and save

Show the selected type, article, coverage limitations, reference status, and
proposed destination: `wiki-drafts\<wiki-type>-<technical-topic>.md` in the
engineer-approved workspace. Do not infer the workspace from the installation
directory. Saving requires the format and reference gates to pass, followed by
approval for this draft and exact destination. Approval is not evidence that a
missing source exists.

If the destination exists, stop and ask for a different filename; automatic
replacement and merging are not part of this version. Write only the reviewed,
de-identified draft, then read it back to verify content and report its path.
If the write fails, report the failure; do not claim it was saved.

No automatic staging, committing, pushing, publishing, email, Teams messages,
case closure, memory/RAG ingestion, or telemetry. Human review of a local draft
does not authorize any of those actions.

## Example request

> Use case-session-to-wiki on this troubleshooting conversation. Extract the
> reusable knowledge, choose QA, How-to, or Break-fix, and include original
> supporting excerpts with exact sources. Remove customer identifiers and show
> the draft before saving.

## Changelog

- 0.2.0 (2026-09-16): Added QA, How-to, and Break-fix routing and templates;
  mandatory claim-level attribution, original excerpts, exact locations,
  targeted inspection of cited originals, and pre-save reference completeness.
- 0.1.0 (2026-09-16): Initial local-only framework, evidence contract, privacy
  boundaries, Markdown template, and review-before-save workflow.
