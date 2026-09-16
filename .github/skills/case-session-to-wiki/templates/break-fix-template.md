---
title: "<Failure and distinguishing condition>"
wiki_type: break-fix
status: draft
review_status: pending-engineer-review
product: "<Product and relevant version, or Not recorded>"
source_kind: "<current-session, provided-transcript, or local-session>"
source_coverage: partial
content_mode: documentation-enriched
reference_status: incomplete
root_cause_status: unknown
resolution_status: unverified
tags: []
---

# <Failure and distinguishing condition>

## Problem and applicability

Describe the observable failure, exact non-identifying error, impact, affected
versions, and triggering conditions. State when this guide does not apply.
Cite the evidence instead of assuming that a common error proves the same cause.

## Confirm this is the same issue

Give the reader specific checks before applying the fix. Include prerequisites
and how to interpret both matching and non-matching results.

| Check and how to perform it | Matches when | Does not match when | Next action | Sources |
| --- | --- | --- | --- | --- |
| <Source-supported check> | <Distinctive evidence> | <Lookalike or exclusion> | <Proceed, branch, or stop> | <Inline citations> |

Retain useful rejected hypotheses and failed attempts here when they help
discriminate this failure. An unexplained mismatch means investigate further,
not apply the repair anyway. Do not invent negative criteria to complete a table.

## Cause and confidence

State confirmed, suspected, or unknown cause, with its supporting original
evidence and limitations. Keep later contradictions visible. A symptom match or
successful restart alone does not establish a root cause.

## Resolution or workaround

Identify whether this is a fix, workaround, or mitigation. Use ordered steps
supported by the source, with explicit conditions for applying them.

### Step 1 - <Repair action>

**Provenance:** <observed-in-session, documentation-enriched, or adapted-from-documentation>

**Execution validation:** <not-run, syntax-only, or lab-tested>

**Prerequisites and impact:** <Required access, applicability, and read/write risks.>

**Action:** <Recorded or documented action, with clearly identified placeholders.>

**Expected result:** <Sourced checkpoint after this action.>

**If it fails:** <Supported branch or explicit stop condition.>

**Rollback:** <Sourced recovery action or an explicit limitation needing review.>

**Sources:** <Inline links supporting the action, its conditions, and expected result.>

Do not describe proposed actions as completed or a temporary mitigation as a
permanent fix. Do not run these instructions during knowledge extraction.
Record material additions/adaptations in the approved companion with this
section heading, source IDs, and separate execution-validation status.

## Verification

| Check | Recorded success criterion | Actual result and scope | Sources |
| --- | --- | --- | --- |
| <Post-fix check> | <Expected result, or Not recorded> | <Observed, reported, or unverified> | <Inline citations> |

Identify recurrence and the tested scope/duration. Do not invent thresholds or
claim permanent recovery from a single successful attempt.

## Escalation and prevention

Explain when to stop and what additional evidence is needed if matching or
verification fails. Include sourced preventive lessons and relevant follow-up
answers, without inventing support ownership or escalation destinations.

## Open questions and limitations

List source-coverage gaps, unknown cause, contradictory results, missing safety
information, and the specific points requiring engineer confirmation.

## References and original excerpts

State source coverage and verification limitations. Embed one full
[source entry](source-entry-template.md) per cited passage, with original text
and an exact safe locator. Replace the template link with actual source entries.
Each source entry links to its record in the approved evidence companion.

## Review checklist

- [ ] Symptoms and applicability are recognizable without reading the case chat.
- [ ] Matching checks, lookalike exclusions, and stop conditions precede repair.
- [ ] Cause, fix/workaround, and verification status match the evidence.
- [ ] Repair steps have sourced conditions, checkpoints, and risk qualifications.
- [ ] Every material claim links to an original excerpt with an exact location.
- [ ] No customer identifiers, private case links, or credentials remain.
- [ ] The article remains a draft pending engineer review.
