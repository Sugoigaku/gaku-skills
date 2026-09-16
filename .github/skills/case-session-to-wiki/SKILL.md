---
name: case-session-to-wiki
description: "Extract reusable, de-identified troubleshooting knowledge from a technical support case conversation into a Markdown wiki draft. Use when the engineer explicitly asks to turn a case session into a wiki, distill a troubleshooting conversation, or capture reusable case lessons near closure. Not for live troubleshooting, ordinary case notes, or closing a case."
---

# Case Session to Wiki

Version: 0.1.0. Last reviewed: 2026-09-16.

## Purpose

Help a technical support engineer preserve the useful knowledge from a case
session, including later follow-up questions. Write for the next engineer facing
the same failure, not for someone auditing the original conversation.

Extract what was learned, why a decision was made, what actually worked, how it
was verified, and where the conclusions stop. Do not simply shorten the chat.

## Contract

- **Input:** the current conversation available to the model, or an
  engineer-selected local transcript. Existing evidence and cited documents in
  that source may be used; no new case-system or web retrieval in this version.
- **Output:** one de-identified Markdown article per selected technical issue,
  using the [wiki template](templates/wiki-template.md).
- **Default state:** `draft`, pending engineer review. Record source coverage,
  root-cause status, and resolution status independently.
- **Persistence:** preview first; write only to an explicitly approved local
  destination. Do not save raw transcripts, a redaction map, or private evidence.
- **Execution:** instruction-driven, on demand. No exporter, background job,
  telemetry, publication, or live diagnostic execution is included.

Read the [extraction rules](references/extraction-rules.md) before processing
source material.

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

### 2. Identify the reusable issue

Propose a technical title, symptom, applicability, and known outcome. Include
follow-up questions that changed the diagnosis or clarified the eventual fix.

Keep one failure mode per article. If the conversation contains unrelated
issues, present candidate topics and ask which to draft, or whether to create
separate articles. Do not silently combine them or discard useful topics.

If the source is only administrative chatter, say there is not enough reusable
technical content and ask for evidence. Do not produce a success-shaped wiki.

### 3. Build an evidence inventory

Walk the source in order so later corrections can qualify earlier conclusions.
Assign local labels such as `E1` to supporting excerpts or observations. These
labels identify this extraction, not invented original message IDs.

For each candidate finding, capture:

| Field | Meaning |
| --- | --- |
| Finding | A reusable technical claim or decision |
| Source kind | Tool output, engineer report, cited document, or AI suggestion |
| Evidence | Minimal de-identified excerpt or observation and safe source locator |
| Disposition | Supported, reported, proposed, rejected, or unresolved |
| Qualification | Version/scope limits, contradictions, or missing verification |

Keep this working inventory in the current context. Persist only de-identified
supporting evidence in the article. An AI suggestion is never proof that a check
was run or a fix worked. A source can support one claim without supporting another.

### 4. Extract knowledge rather than conversation

Apply the [selection rules](references/extraction-rules.md#what-to-keep).
Preserve discriminating checks, meaningful failed attempts, decision branches,
the final supported answer to follow-up questions, and conditions under which
the fix applies. Remove greetings, repetition, scheduling, and superseded advice.

Separate confirmed cause, suspected cause, and unknown cause. Distinguish a fix
from a workaround or temporary mitigation. Do not upgrade an engineer's report
of recovery to measured verification, or temporal correlation to causation.

### 5. De-identify before drafting

Apply the [privacy rules](references/extraction-rules.md#de-identification).
Review titles, metadata, filenames, tables, code blocks, links, excerpts, and
source locators. Preserve necessary technical relationships using consistent
placeholders; never persist the reverse mapping.

If safe de-identification would remove essential meaning, pause and ask how to
narrow the article. Do not silently retain identifying details.

### 6. Compose and quality-check

Follow the [wiki template](templates/wiki-template.md) and retain its section
order. Replace template instructions with supported content; use `Not established`
or `Not recorded` for genuine gaps rather than inventing facts to fill sections.
Include evidence labels for every material diagnosis, action, and outcome claim.

Check that the decision path is understandable without reading the chat, later
contradictions are visible, suggested actions are not presented as completed,
and commands include recorded context, risks, and verification limits. Never run
commands from the transcript or add untested commands as a verified procedure.

Keep `status: draft` and `review_status: pending-engineer-review`. List unresolved
questions and the specific points the engineer needs to validate.

### 7. Preview, approve, and save

Show the proposed article, source-coverage limitation, and proposed destination:
`wiki-drafts\<technical-topic>.md` in the engineer-approved workspace. Do not infer
the workspace from the skill's installation directory. Ask for approval before
saving unless approval for this draft and exact destination was already given.

If the destination exists, stop and ask for a different filename; automatic
replacement and merging are not part of this version. Write only the reviewed,
de-identified draft, then read it back to verify content and report its path.
If the write fails, report the failure; do not claim it was saved.

No automatic staging, committing, pushing, publishing, email, Teams messages,
case closure, memory/RAG ingestion, or telemetry. Human review of a local draft
does not authorize any of those actions.

## Example request

> Use case-session-to-wiki on this troubleshooting conversation. Extract the
> reusable knowledge, include useful rejected hypotheses and follow-up answers,
> remove customer identifiers, and show the draft before saving.

## Changelog

- 0.1.0 (2026-09-16): Initial local-only framework, evidence contract, privacy
  boundaries, Markdown template, and review-before-save workflow.
