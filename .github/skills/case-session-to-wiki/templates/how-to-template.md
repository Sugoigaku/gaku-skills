---
title: "<Achieve a specific goal>"
wiki_type: how-to
status: draft
review_status: pending-engineer-review
product: "<Product and relevant version, or Not recorded>"
source_kind: "<current-session, provided-transcript, or local-session>"
source_coverage: partial
content_mode: documentation-enriched
reference_status: incomplete
procedure_status: unverified
tags: []
---

# How to <achieve the goal>

## Goal and success criteria

State the starting point, intended end state, and how the reader will recognize
success. Define what is out of scope and cite the applicable source.

## Prerequisites and concepts

List required permissions, supported versions, tools, configuration inputs, and
safety conditions. Explain unfamiliar terms before using them. Distinguish
literal values from reader-supplied placeholders. Cite the source for each
material prerequisite; do not assume unmentioned product knowledge.

## Step-by-step procedure

Use numbered, ordered steps without unexplained jumps. Repeat this block for
each step; split compound actions when a novice would need an intermediate check.
Use actual UI labels or source-supported command syntax, not vague instructions
such as "configure it normally." Never invent missing clicks, flags, or outputs.

### Step 1 - <Verb and intended result>

**Provenance:** <observed-in-session, documentation-enriched, or adapted-from-documentation>

**Execution validation:** <not-run, syntax-only, or lab-tested>

**Where:** <Application, page, shell, working context, or execution target.>

**Inputs:** <Values to prepare, their meaning, and which placeholders to replace.>

**Action:** <Exact supported actions in order, with commands or UI navigation when available.>

**Why:** <Brief explanation of why this step is necessary.>

**Expected result:** <Observable checkpoint and how to check it.>

**If the result differs:** <Supported branch or explicit stop/escalation condition.>

**Safety and rollback:** <Read/write impact, approval needs, and sourced recovery action.>

**Sources:** <Inline links for actions, inputs, expected results, and safety statements.>

Separate documented guidance from actions actually executed in the case.
Record material additions/adaptations in the approved companion's enrichment
entries, with this exact section heading and supporting source IDs.
Missing critical inputs, steps, or checkpoints block a runnable guide; request
the original instructions instead of filling gaps with plausible behavior.

## End-to-end verification

| Check | Supported success criterion | Recorded result or not tested | Sources |
| --- | --- | --- | --- |
| <Check against the goal> | <Expected end state> | <Actual scope/result, or Not tested in source> | <Inline citations> |

Distinguish `documented-not-tested` from `verified-in-source`. Never imply that
writing this article executed the procedure or verified a customer's environment.

## Troubleshooting and rollback

List sourced common mistakes, recovery options, and stop conditions. Explain how
to undo changes when the source establishes that it is safe. Label missing
nonessential details; do not invent a rollback command or a safe default.

## Open questions and limitations

Record version constraints, source gaps, unsupported assumptions, and any parts
that still need validation. Do not call an incomplete procedure beginner-ready.

## References and original excerpts

State source coverage and verification limitations. Embed one full
[source entry](source-entry-template.md) per cited passage, including original
text and exact location. Replace the template link with the actual entries.
Each source entry links to the matching record in the approved evidence companion.

## Review checklist

- [ ] The goal, starting point, prerequisites, and success criteria are explicit.
- [ ] Each step specifies where, inputs, action, expected result, and failure path.
- [ ] Necessary concepts and placeholders are explained for an unfamiliar reader.
- [ ] Safety and rollback information is sourced, not invented.
- [ ] Each material instruction has a supporting original excerpt and exact source.
- [ ] Documented steps and observed execution are distinguished.
- [ ] No identifying information or credentials remain; engineer review is pending.
