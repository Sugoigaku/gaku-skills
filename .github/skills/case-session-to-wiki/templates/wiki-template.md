---
title: "<Technical symptom and distinguishing condition>"
status: draft
review_status: pending-engineer-review
product: "<Product and relevant version, or Not recorded>"
source_kind: "<current-session or provided-transcript>"
source_coverage: partial
root_cause_status: unknown
resolution_status: unverified
tags: []
---

# <Technical title without customer or case identifiers>

## Problem and applicability

Describe the observable problem, relevant environment constraints, prerequisites,
and when this article does not apply. Include only supported scope.

## Key findings

| Reusable finding | Evidence | Qualification |
| --- | --- | --- |
| <Finding> | E1 | <Supported scope or uncertainty> |

## Troubleshooting decision path

Keep meaningful diagnostic forks and useful failed attempts, not every chat turn.

| Question or hypothesis | Check or action | Observed result | Interpretation and next decision | Evidence |
| --- | --- | --- | --- | --- |
| <Question> | <Recorded check> | <Observed or reported result> | <What this supports or rules out> | E1 |

## Cause and confidence

State whether the cause is confirmed, suspected, or unknown, with evidence.
Explain relevant contradictions and why recovery does or does not establish cause.

## Resolution or workaround

Identify the action as a fix, workaround, or mitigation. Describe only recorded
steps and supported conditions. For commands, identify placeholders, execution
status, read/write impact, and recorded safety/rollback information. Label gaps.
Do not promote a proposal to a proven procedure.

## Verification

| Validation check | Recorded success criterion | Actual result and scope | Evidence |
| --- | --- | --- | --- |
| <Check> | <Criterion, or Not recorded> | <Observed, reported, or unverified> | E2 |

## Reusable lessons and follow-up answers

Capture transferable decisions, pitfalls, and supported answers to later
technical questions. Keep their applicability and limitations explicit.

## Open questions and limitations

List missing source history, untested assumptions, conflicting results, unknown
cause, missing safety details, and anything the engineer must still confirm.
Do not imply that closing the case answers every technical question.

## Evidence and references

Source coverage: <What was actually read and what is unavailable>.
Local E-labels refer to this extraction, not original message identifiers.

| Evidence | Source kind and safe locator | Minimal de-identified excerpt or observation |
| --- | --- | --- |
| E1 | <Tool output, report, or document; safe locator> | <Supporting content> |
| E2 | <Source kind; safe locator> | <Supporting content> |

List supplied, non-identifying documentation links if useful. Distinguish
session-cited links from documentation actually read and validated.

## Review checklist

- [ ] Every material claim has support, or is explicitly marked uncertain.
- [ ] Proposed and rejected actions are not presented as completed fixes.
- [ ] Cause, resolution, and verification statuses match the evidence.
- [ ] Coverage gaps and relevant later corrections are visible.
- [ ] Customer/case identifiers, private links, and credentials are absent.
- [ ] Commands have appropriate context, safety qualifications, and placeholders.
- [ ] The article remains a draft pending engineer review.
