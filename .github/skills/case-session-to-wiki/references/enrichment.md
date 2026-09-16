# Extraction and Documentation Enrichment

## Default and override

The engineer selected `documentation-enriched` as the default content mode.
This permits targeted documentation lookup and explanatory additions without
another mode-selection prompt. It does not authorize live diagnostics, policy
changes, new infrastructure, or executing a published procedure.

When explicitly requested, `extraction-only` limits technical content to the
selected source and its already-cited originals. Do not add new procedures in
that mode. Mark a missing step as a gap and ask for evidence.

## What enrichment permits

- Look up an official API signature, prerequisite, UI operation, or expected
  behavior necessary for the selected topic.
- Explain a term or add a documented step that makes a How-to followable.
- Replace environment-specific values with placeholders.
- Propose a safer documented alternative to a historical shortcut, while keeping
  its different validation status explicit.

Use only generic technical query terms. Do not transmit customer names, case
numbers, private logs, identifiers, or secret-bearing URLs to search services.
Inspect original passages rather than treating snippets or model memory as proof.
Broader research, missing access, ambiguous product versions, and changes to the
approved article scope remain human decision points.

## Required labels

Every How-to and Break-fix action step includes:

```text
**Provenance:** observed-in-session | documentation-enriched | adapted-from-documentation
**Execution validation:** not-run | syntax-only | lab-tested
```

Choose one value per field. For a mixed step, split it or use the more
conservative adapted/not-run classification. The claim map separately records
whether an assertion is observed, reported, documented, or inferred.

For every documentation-enriched/adapted procedural section, include a companion
`enrichments` entry with its exact heading, source IDs, a description of what was
added/changed, and the execution-validation state. QA additions still require
claim mappings and citations; they must not acquire invented experiment results.
Even a single sample step retains the chosen template's fields. Required roles
and prerequisites in the quoted source must appear in the article or step;
do not drop them when expanding the action into novice-friendly instructions.

## No inherited success

An API exists does not mean the composed script works end to end. A syntactically
valid command is not a completed lab test. Changing certificate parameters,
permissions, ordering, tools, rollback, or network settings invalidates any
claim that the exact new procedure was already executed.

Keep a documentation-supported How-to `documented-not-tested` until that exact
procedure has relevant execution evidence. If critical instructions or their
support are missing, keep it `unverified` and do not present it as runnable.
For Break-fix, a proposed repair cannot upgrade resolution from unverified.

Never reproduce accept-all certificate checks, swallowed diagnostic errors, or
unscoped deletion as recommended steps. Explain why historical observations from
such checks are limited; use a sourced alternative and label it as a new step.

## Review and verification

The generator may check signatures, syntax, and documentation, but must not
approve its own semantic review. A separate reviewer checks every added step's
inputs, prerequisites, applicability, expected output, safety, and rollback.
For high-impact procedural changes, obtain explicit lab validation approval;
otherwise the document stays a clearly marked, unexecuted review draft.

This file defines an authoring mode, not a production-execution capability.
