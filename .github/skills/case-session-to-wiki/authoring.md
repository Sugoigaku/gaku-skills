# Knowledge Extraction and Article Authoring

Use topic selection for mixed material, outcome definitions when making a status
claim, and detailed-action guidance for How-to/Break-fix. A simple QA does not
need a procedural checklist or a formal planning table.

## Topic and type selection

Inventory the technical topics throughout the available source, including later
questions and corrections. Group by reader task, not chat length, date, every
message, or every failed attempt. Honor the engineer's explicit scope first.

| Reader task | Type | Keep foregrounded |
| --- | --- | --- |
| Understand a behavior, limit, or answer | `qa` | Direct supported questions and answers |
| Configure something or achieve a goal | `how-to` | A beginner-followable procedure |
| Recognize and restore a failed operation | `break-fix` | Discriminating checks, repair, and recovery verification |

A repair is not How-to merely because it has steps. A setup goal is not
Break-fix merely because something failed during the discussion. If an explicit
type would hide essential safety or diagnostic content, explain the mismatch
and ask one focused question before changing it.

- Independent subjects may produce separate articles of the same type.
- One topic may support multiple types only for distinct, independently useful
  reader tasks. Do not produce a three-format cross product.
- Consolidate retries about the same failure into one decision path. Short
  explanatory follow-ups can stay with their owning procedural article.
- Keep one coherent topic per article and one failure mode per Break-fix.
- Do not merge unrelated issues or let a brief follow-up disappear.
- Honor single-topic/type/page requests; do not silently expand them.
- Missing sources or critical steps block that candidate, not automatically
  every supported sibling. No sibling lends another its verification status.

For a complex set, this optional internal table can help track coverage. For one
clear task, select its type directly. Print a plan only when requested:

| ID | Topic | Wiki type | Reader task and scope | Title | Sources and coverage | Readiness and gaps | Filename |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | <Technical topic> | <Type> | <Distinct task> | <Safe title> | <Source IDs and limits> | <Ready or blocked, with reason> | <type-topic.md> |

Use de-identified labels even in the plan. Select the useful set without routine
article-list approval. Report blocked, excluded, or deferred topics briefly.
Batch oversized sets explicitly without omitting later corrections, silently
capping article count, or delegating raw case content. No index page is needed
unless requested.

## What to extract

Keep recognizable symptoms and safe error codes, applicable product versions,
essential topology relationships, checks distinguishing competing explanations,
meaningful failed attempts, the supported reason for an action, actual outcomes,
follow-up answers, scope limits, contradictions, and unresolved assumptions.

Drop greetings, scheduling, repetition, irrelevant outputs, generic tutorials,
and wrong advice that taught nothing. Write for the next engineer rather than
an auditor reconstructing the original conversation. A short article is fine;
there is no target length and no mandatory confidence essay.

Process corrections by evidence, scope, and sequence. Later text does not
automatically win, and repeated AI assertions do not strengthen a claim.
Retain unexplained contradictory observations. A log proves what it recorded,
not necessarily the cause of what happened.

| Disposition | Meaning |
| --- | --- |
| Supported | The inspected evidence substantiates this specific scoped claim |
| Reported | A participant reports the result; independent observation is absent |
| Proposed | Suggested, without established execution or outcome |
| Rejected | Later evidence explicitly rules out or corrects the claim |
| Unresolved | Missing, insufficient, or contradictory evidence |

## Outcome metadata

Keep source coverage, reference review, and technical outcomes separate.

For How-to, use `procedure_status`:

- `verified-in-source`: the exact complete sequence and relevant results were
  demonstrated within the recorded scope.
- `documented-not-tested`: inspected documentation supports the sequence, but
  it was not verified end to end in the selected evidence.
- `unverified`: critical steps, inputs, prerequisites, or results are missing
  or contradictory. Do not present it as a runnable production procedure.

For Break-fix:

- `root_cause_status: confirmed` requires evidence establishing causality
  within the recorded scope; `suspected` means a supported but unproven
  hypothesis; `unknown` means no supported causal conclusion.
- `resolution_status: verified` requires relevant observed post-change recovery
  without an unexplained contrary result; `reported` means a report without
  supporting checks; `unverified` covers proposed, missing, failed, or
  contradicted outcomes.
- Name a fix, workaround, or mitigation honestly in the prose. Recovery after
  a restart is not proof of a root cause or permanent repair.

QA has no mandatory cause, resolution, or procedure metadata. General limits,
guarantees, and support policies need applicable authoritative documentation;
one case observation cannot establish them. Never invent numerical confidence,
verification duration, success thresholds, or test output.

## Detailed actions, simple structure

Use [the templates](templates.md). Concise means no repetitive forms, not short
or vague instructions. QA remains direct question-and-answer text. How-to and
Break-fix may need numbered substeps, complete commands, and explanatory notes.
Never reduce an action to "import the certificate," "restart the service,"
"configure the policy," or "verify connectivity" without saying how.

### UI instructions

Specify the target machine/service and how to open the console/page, navigation
path, exact option/control, what to enter or select, wizard choices in order,
and how to apply/save. Use labels supported by the applicable product version.
Describe the observable result and a failure branch when it changes the next
action. Do not guess a missing UI detail to make a procedure appear complete.

### Complete commands

When a documented CLI route is practical, include a complete fenced command
block with the appropriate language in the generated article:

- State execution context, elevation, shell/module version, and prerequisites.
- Initialize required variables or reference explicit earlier setup. Explain
  each placeholder and where the reader gets its value.
- Include required parameters, setup, and correct continuation syntax. No
  ellipses, "same as above," or pseudocode inside a runnable block.
- Verify relevant APIs/commands in inspected official documentation when
  enriching. Do not invent flags, credentials, or silently substitute defaults.
- Use short comments only for non-obvious behavior; longer input explanations
  belong in a short Notes paragraph or bullets.
- Explain expected results and meaningful stop/failure conditions.

These are source-backed instructions for the reader, never commands executed
by the extraction workflow or a way to smuggle runtime helper scripts into the
upload. A complete command is not automatically tested.

Choose the practical supported UI or CLI route. Add an alternative only when
it helps and label it clearly so the reader does not run both unintentionally.
Do not assume a registry edit and Group Policy operation are equivalent.

### Impact, identification, and recovery

State essential roles, prerequisites, significant impact, and supported rollback
requirements once before actions. Keep a local warning when needed to prevent
a real mistake, but omit routine "no impact" or "no rollback needed" filler.
Missing critical safety information blocks an actionable guide until resolved
or its scope is narrowed; do not bury it in Double-check.

For Break-fix, explain how to perform each decisive matching check: exact UI/log
navigation or full command, expected value, and the meaning of non-matching
results. A matching error alone does not prove the same failure. Retain useful
exclusions and stop branches.

Verification needs the actual query, command, or UI action, recognizable result,
and recorded scope. Distinguish historical observations from checks still to be
performed. Do not claim measured recovery from a participant's report.

## Per-article and set gates

Each article must be self-contained, with its own source entries, coverage,
claim map, and outcome classifications. Sibling links are optional navigation.
Keep uncertainties in the affected answer/action and collect actual remaining
questions in a final optional Double-check. Omit empty sections and repeated
"Not recorded" padding; do not omit material limitations.

Use [evidence review](evidence-review.md#agent-checklist) for the final content
checks and [local delivery](session-workflow.md#verify-and-finish) for
`saved`, `blocked`, `failed`, or `deferred` outcomes. Do not duplicate a full
review itinerary here or make a ready sibling wait for an unrelated blocked topic.
