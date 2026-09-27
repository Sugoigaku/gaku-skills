# Gaku Skills

Reusable skills for technical support work.

## customer-reply

Draft or refine considerate, technically precise customer support replies,
with particular guidance for Japanese business correspondence.

Version: 0.3.0. Last reviewed: 2026-09-27.

- Acknowledge the customer's specific effort, then lead with the answer.
- Separate verified facts, interpretation, uncertainty, impact, and next steps.
- Explain requests, recognize completed checks, and correct unclear wording.
- Deliver verified partial answers in the customer's question order.
- Explain mechanisms and support boundaries, scope negative findings, and
  distinguish later findings from information available at the time.
- Compare remedy prerequisites and side effects before recommending action.
- Cover technical answers, progress updates, information requests, corrections,
  follow-ups, and closure or agreed-pause drafts.
- Keep customer-facing language separate from English engineer review notes.
  Confirm the customer language before drafting when needed.
- Draft only: no automatic sending, deletion, diagnostic actions, or case closure.

The complete document-only bundle is three flat files:

| File | Contents |
| --- | --- |
| [SKILL.md](.github/skills/customer-reply/SKILL.md) | Focused trigger, conditional reference routing, completion criteria, and draft boundaries |
| [voice-and-wording.md](.github/skills/customer-reply/voice-and-wording.md) | Tone, Japanese wording cues, confidence levels, and editing rules |
| [reply-patterns.md](.github/skills/customer-reply/reply-patterns.md) | Scenario structures and synthetic English examples |

Use: "Use customer-reply to refine this support response without changing its
technical meaning," or "Use customer-reply to draft a progress update from
this thread." Technical claims still require evidence; wording guidance is not
a product reference. No mailbox access is required for supplied-text drafting.

Simple wording edits can use the entry point alone. Load only relevant voice
or scenario sections for more involved replies; templates and editing sequences
are not mandatory. Finish the supported draft without routine approval stops,
while retaining language confirmation, evidence limits, and draft-only controls.
This follows the [OpenAI skills and prompts guide](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra)
without depending on a particular model's judgment to enforce safety.

The project copy is under [.github/skills](.github/skills). For an optional
personal installation, specify **both** paths to the existing installer:

```text
python -B scripts\install_skill.py --source .github\skills\customer-reply --destination "%USERPROFILE%\.copilot\skills\customer-reply"
```

The example above uses Command Prompt variable syntax. In PowerShell, replace
the destination argument with `"$env:USERPROFILE\.copilot\skills\customer-reply"`.
The installer's default still selects `case-session-to-wiki`; it has not changed.
Start a fresh host session to check discovery. No personal installation or
platform upload is implied by adding the project files.

For platform upload, select the main skill and its two supporting files only.
The same repository packaging budgets described below apply. Local tests
verify document contracts, links, privacy patterns, and temporary installation,
not model compliance or platform acceptance. Use the
[customer-reply scenarios](tests/customer-reply-scenarios.md) for behavioral
acceptance. They are not an executed model-evaluation record.

## case-session-to-wiki

Turn selected troubleshooting conversations into de-identified technical Wiki
drafts. This is not a transcript dump, chronological case summary, live
troubleshooting agent, or case-closing tool.

Version: 0.8.0. Last reviewed: 2026-09-16.

The skill is now **document-only**: one SKILL.md and six supporting Markdown
files. No Python runtime, executable attachment, archive, or downloaded helper
is required by the skill. Native host tools handle supported input and local
files; an explicit agent checklist replaces deterministic validation.

## Upload to the company skill platform

The platform permits at most 10 supporting files, accepts documentation/image
extensions but not scripts or archives, and shares one 120KB budget among
SKILL.md, platform-extracted details, and attachments.

Upload [SKILL.md](.github/skills/case-session-to-wiki/SKILL.md) as the main skill.
Attach exactly these six files from the
[skill folder](.github/skills/case-session-to-wiki):

| Supporting file | Contents |
| --- | --- |
| [session-workflow.md](.github/skills/case-session-to-wiki/session-workflow.md) | Native session/transcript input, coverage, fresh session-local saving, and readback |
| [authoring.md](.github/skills/case-session-to-wiki/authoring.md) | Topic/type planning, extraction, outcomes, and detailed UI/command instructions |
| [sources.md](.github/skills/case-session-to-wiki/sources.md) | Original excerpts, precise locators, enrichment, and de-identification |
| [evidence-review.md](.github/skills/case-session-to-wiki/evidence-review.md) | Evidence schema v1, metadata, agent checklist, and independent-review boundary |
| [templates.md](.github/skills/case-session-to-wiki/templates.md) | QA, How-to, Break-fix, and compact source-entry templates |
| [diagrams.md](.github/skills/case-session-to-wiki/diagrams.md) | Optional source-backed Mermaid diagrams and text fallback |

All seven files are in one flat directory; no directory-preserving upload or
zip is needed. Keep these filenames so relative references resolve. Do not
attach this repository's README, scripts, tests, generated articles, transcripts,
session data, or credentials. Do not rename a script to an accepted extension.

The automated packaging tests enforce:

- At most 10 supporting files, accepted types, flat unique names, and valid links.
- A stricter project budget of **64,000 raw bytes** for the complete skill bundle.
- A conservative estimate of raw bundle bytes plus **two additional copies of
  SKILL.md and 16,384 bytes** for extracted details/overhead, under **120,000 bytes**.

This estimate deliberately uses decimal bytes, below 120 KiB, but it is not a
claim about the platform's unpublished extraction/accounting formula. Check the
platform's actual total after extraction. Upload acceptance and runtime tool
availability still require testing in that platform. No successful upload is
implied by local tests.

The platform does not scan attachments for personal information. Review the
seven upload files yourself; do not substitute generated case examples. The
bundle contains generic instructions/placeholders and a labeled synthetic
evidence example, not real case artifacts.

## Preserved behavior

| Type | Reader task | Essential content |
| --- | --- | --- |
| QA | Understand a topic or answer a question | Direct answers, important qualifications, inline references |
| How-to | Achieve a goal | Essential impact/roles up front, detailed steps, actionable result check |
| Break-fix | Identify and restore a failed operation | Decisive matching checks, clear repair/workaround, recovery verification |

- Rich sessions become a topic-by-type article set, not one giant page or
  automatically three formats per topic. Explicit scope/type choices win.
- Concise structure does not mean short instructions: exact UI navigation,
  controls, input values, apply/save choices, complete documented commands,
  placeholder explanations, useful notes, and interpretable checks remain.
- Every substantive answer, step, check, cause, and outcome needs a relevant
  inline citation, short actual original excerpt, and precise safe locator.
- Portable `evidence.json` keeps source, claim, and enrichment records out of
  repetitive visible forms. The generation request authorizes its sanitized
  local save, not raw transcript or reverse-map persistence.
- Documentation enrichment is the default; `extraction-only` forbids new
  procedures. Added steps never inherit a historical experiment's success.
- Current-context coverage stays partial. Reported recovery is not measured
  verification, and a restart is not proof of cause.
- Fresh session-local folders, no routine preview/save prompts, no overwrite,
  internal readback, visible absolute paths and links, and honest partial-failure
  reporting remain required.
- No automatic publication, messages, live diagnostics, case closure, Git
  changes for generated drafts, memory/RAG ingestion, or telemetry.

## Replacements and deliberate limitations

| Removed bundled component | Document-only replacement | Limitation |
| --- | --- | --- |
| Python session reader | Exact-session native API or explicit visible transcript/current context | No raw event parsing, custom snapshot/cursor integrity, hidden-field filtering, or complete local-session certification |
| Python output-directory helper | Native metadata and create-only filesystem operations | Host must expose the correct session directory and safe creation/readback; missing capability is a reported blocker |
| Python Wiki validator | Agent-applied source/privacy/structure checklist and native inspection where available | No deterministic schema/quote/privacy pass, hash binding, or generated independent attestation |
| SVG fallback and validator | Mermaid or plain text/Markdown table | No external image assets or guaranteed rendering |

All new drafts carry `validation_method: agent-checklist`. References start
`incomplete` and may become `checklist-checked` only after the actual checklist
and saved-file readback. This edition never assigns `mechanically-checked` or
`complete`. Independent engineer review and publication authorization are still
separate requirements.

Missing session tools mean requesting an explicitly supplied visible transcript,
not scraping archives or other sessions. Missing safe local-write capability
means reporting that files could not be saved, not dumping a preview or inventing
paths. A chat-only platform can host the skill but cannot perform the full save
workflow without the necessary host tools.

Existing pre-0.8 drafts, attestations, and installed personal copies are not
silently migrated. The evidence record shape remains v1; new article metadata
is not claimed to pass the removed validator.

## Local use and optional installation

The project skill is discoverable from
[.github/skills](.github/skills). A personal installation is optional:

```text
python -B scripts\install_skill.py
```

The repository-only [installer](scripts/install_skill.py) verifies copied file
hashes, treats identical installs as a no-op, and refuses to overwrite a
different or locally edited destination. For a staged upgrade, supply a new
explicit destination and review it before replacement. It does not merge or
delete an older installed copy. Start a fresh host process to check discovery;
discovery is not proof of invocation.

Python 3.10+ is needed only for repository development utilities/tests, not the
uploaded skill. Nothing under [scripts](scripts) or [tests](tests) is an upload
attachment or a runtime dependency of the skill.

## Validation

From this repository:

```text
python -B -m unittest discover -s tests -p "test_*.py" -v
```

Tests cover actual upload file count/types/size, metadata, local links, template
shape, evidence examples, explicit behavioral safeguards, installer integration,
and the synthetic smoke runner. Tests of the removed Python helper APIs were
retired with those APIs, not replaced by claims of equivalent deterministic
validation. Document-contract tests cannot prove a model follows the workflow.

Use the [synthetic scenarios](tests/scenarios.md) for model behavior. The
repository-only [smoke runner](scripts/behavior_smoke.py) supports `topic-plan`,
`false-quote`, `enrichment`, `session-delivery`, and `document-only`:

```text
python -B scripts\behavior_smoke.py --fixture document-only --output <NEW_APPROVED_OUTPUT_PATH>
```

The runner permits only skill/view tools, checks actual native invocation,
fingerprints the bundle, and leaves semantic grading separate. It is not a
write-path integration test, company-platform upload test, or factual approval.
Only synthetic inputs are used. Existing
[v0.4.0](tests/behavior-evaluation-0.4.0.json) and
[v0.5.0](tests/behavior-evaluation-0.5.0.json) records are historical, not approval
of this release.

The [v0.8.0 evaluation](tests/behavior-evaluation-0.8.0.json) records 45 passing
local tests and two failed native-invocation smoke gates. The CLI runs read the
new project documents, but no native skill invocation was recorded; one also
had an initial failed path lookup. Do not treat their plausible answers as
passing native integration or platform acceptance.

The repository ignores local Wiki drafts, private inputs, and bytecode. Git
ignore is not a privacy guarantee or permission to store real case transcripts.
