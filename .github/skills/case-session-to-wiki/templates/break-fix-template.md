---
title: "<Failure and distinguishing condition>"
wiki_type: break-fix
article_format: concise
status: draft
review_status: pending-engineer-review
product: "<Product/version if relevant>"
source_kind: "<current-session, provided-transcript, or local-session>"
source_coverage: partial
content_mode: documentation-enriched
reference_status: incomplete
root_cause_status: unknown
resolution_status: unverified
tags: []
---

# <Failure and distinguishing condition>

## Problem

<Describe the symptom clearly. Include a supported cause only if useful; do not
turn an evidence gap into a confirmed cause or an outage.>

## Before you start

<Important impact and essential prerequisites only, stated once.
Omit this section if there is nothing material to warn about.>

## Identify the issue

<A few decisive checks showing whether this is the same problem. Explain how
to open the relevant log/page or run the full diagnostic command, what to look
for, and what matching/non-matching results mean. No mandatory multi-column table.>

A small sourced decision diagram may help here; follow the
[diagram rules](../references/diagrams.md). Do not repeat every step as a diagram.

## Steps

### Step 1 - <Action>

<Give detailed, executable instructions, with numbered substeps if needed:
the target host/page, exact UI navigation and options, entered values, and
apply/save actions. For a practical documented PowerShell/CLI route, include
the full command block and explanatory comments or Notes. Explain placeholders,
required setup, expected output, and relevant failure handling.
Call a workaround a workaround; use inline citations, not repeated
Impact/Why/Rollback/Provenance forms. Keep review metadata in the companion.>

Follow the [detailed-action contract](../references/procedural-detail.md).
Do not stop at "import the certificate" or "restart the service" without saying how.

## Check the result

<Give the full check command or exact UI actions and explain what confirms
recovery. Distinguish recorded results from checks the reader must still perform.>

## References

Include compact [source entries](source-entry-template.md), original excerpts,
precise locations, and one link to the evidence companion.

## Double-check

<Only unresolved points, with the relevant step or conclusion. Omit if none.
Do not hide an important safety restriction here instead of stating it up front.>
