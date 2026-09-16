# Gaku Skills

Reusable GitHub Copilot skills for technical support work.

## First skill: case-session-to-wiki

Turn a troubleshooting conversation into reusable technical knowledge at case
closure. This is **not a transcript dump, a chronological case summary, or an
automatic case-closing tool**.

The skill combines instructions with read-only Python helpers for session input
and evidence validation. It chooses article formats by reader task and separates
observed findings from documentation-based additions.

Requires Python 3.10+ for the helpers. No Python packages, credentials, or network
services are needed by those helpers themselves.

### Three wiki formats

| Format | Use when the reader needs to... | Required content |
| --- | --- | --- |
| QA | Understand a topic or get specific answers | Clear questions, direct answers, conditions/exceptions, and sources for each answer |
| How-to | Achieve a goal or perform a task | Goal, prerequisites, beginner-followable steps, expected results, failure branches, and final validation |
| Break-fix | Recognize and resolve a failure | Symptoms, same-issue checks and exclusions, cause/uncertainty, fix or workaround, and recovery verification |

An explicit scope/format request takes priority. For a rich session, the skill
first proposes an **article set organized by topic and type**, rather than
compressing everything into one page or asking you to discover the topics.
There is no catch-all fourth format.

### Rich sessions become an article set

The skill plans each topic, reader task, type, source gap, and filename internally.
It does not print a preview or ask you to approve the article list or local save.

- Different topics can produce separate articles of the same type.
- One topic can produce several types when each serves a distinct task.
- A simple topic is not expanded into QA, How-to, and Break-fix automatically.
- Short follow-up answers stay with their topic; repeated attempts are consolidated.
- Each article keeps its own sources, uncertainty, validation gates, and save result.
- Blocked topics are reported briefly. The ready subset is saved automatically;
  missing siblings never become broken links.

See the [article planning contract](.github/skills/case-session-to-wiki/references/article-planning.md).

### References are mandatory

A bibliography containing only URLs is not enough. Every substantive answer,
instruction, matching criterion, diagnosis, and outcome must link to a source
entry containing:

- The document/evidence title and publisher or source role.
- The precise origin and location: canonical link plus heading/page/lines, or
  explicitly identified positions in the supplied transcript or tool result.
- A short, permitted original excerpt, separate from the skill's interpretation.
- Version/revision when available, access/inspection status, and applicability.

The same contract applies to all three formats. A quote must actually appear in
the inspected source; an AI paraphrase is not an original excerpt. Redactions and
omissions must be marked. Non-English originals remain in their original language.

If a required original or exact locator is missing, the skill shows the gap and
requests it. Private observations use approved, de-identified records in a
portable `evidence.json` companion, not anonymous archive-line references.
The generation request authorizes its de-identified local save in the session folder.

### Default enrichment, explicit provenance

Documentation-based enrichment is enabled by default, as selected by the
engineer. The skill may inspect relevant official documentation to fill a named
gap, using generic technical terms rather than private case data. Request
`extraction-only` to disallow new technical procedures.

Each procedural step identifies observed, documentation-enriched, or adapted
provenance and whether execution was not run, syntax-only, or lab-tested.
New commands do not inherit a historical experiment's success.

### Mechanical checks are not semantic approval

- `incomplete`: required evidence is still missing.
- `mechanically-checked`: the supplied articles/companion pass local consistency
  checks; semantic review remains pending.
- `complete`: a separate reviewer checked all substantive claims and supplied an
  attestation bound to the final content hashes.

The validator compares quotations against the supplied passages, rejects stale
review hashes, and flags known identifier patterns. It does not authenticate the
reviewer, fetch originals, judge entailment, detect every private name, or
authorize publication. A true quote attached to an unrelated claim can pass
mechanical matching and still fail semantic review.

Public reference URLs retain version selectors. The validator allows the safe
query keys `view`, `preserve-view`, and `tabs`; other query forms need a safe
canonical source rather than silently dropping identity-bearing parameters.

### Workflow

```text
Explicit request near case closure
    -> Read only the exact selected session/transcript through the bounded reader
    -> Inventory topics and propose topic-by-type articles
    -> Resolve the selected session and determine source coverage
    -> Inspect originals and label documentation-based enrichment
    -> Extract reusable findings and decisions
    -> De-identify the articles and portable evidence companion
    -> Compose with the selected template and inline citations
    -> Save in a fresh session-local folder, validate, and return file links
    -> Obtain separate semantic review before any publication-ready claim
```

### Files

| File | Responsibility |
| --- | --- |
| [SKILL.md](.github/skills/case-session-to-wiki/SKILL.md) | Trigger, workflow, input/output contract, and safety boundaries |
| [Extraction rules](.github/skills/case-session-to-wiki/references/extraction-rules.md) | Knowledge selection, evidence classification, and de-identification |
| [Article planning](.github/skills/case-session-to-wiki/references/article-planning.md) | Topic inventory, type selection, scope approval, and multi-article delivery |
| [Session input](.github/skills/case-session-to-wiki/references/session-input.md) | Exact-ID/transcript reader CLI, schema, pagination, and coverage |
| [Session output](.github/skills/case-session-to-wiki/references/session-output.md) | Automatic session-local folders, no console previews, and collision-safe delivery |
| [Enrichment](.github/skills/case-session-to-wiki/references/enrichment.md) | Default documentation enrichment and execution/provenance labels |
| [Template selector](.github/skills/case-session-to-wiki/templates/wiki-template.md) | Format selection and shared requirements |
| [QA template](.github/skills/case-session-to-wiki/templates/qa-template.md) | Topic-focused questions and answers |
| [How-to template](.github/skills/case-session-to-wiki/templates/how-to-template.md) | Detailed procedure with checkpoints and failure branches |
| [Break-fix template](.github/skills/case-session-to-wiki/templates/break-fix-template.md) | Issue identification, repair, and verification |
| [Source attribution](.github/skills/case-session-to-wiki/references/source-attribution.md) | Mandatory citation, original-excerpt, and exact-location rules |
| [Source entry template](.github/skills/case-session-to-wiki/templates/source-entry-template.md) | Shared reference record embedded in every article |
| [Evidence validation](.github/skills/case-session-to-wiki/references/evidence-validation.md) | Companion schema, claim mappings, mechanical checks, and review attestations |
| [Semantic review](.github/skills/case-session-to-wiki/references/semantic-review.md) | Independent claim-level review and final-hash approval requirements |
| [Evaluation scenarios](tests/scenarios.md) | Synthetic behavioral cases and acceptance criteria |
| [Framework tests](tests/test_skill_framework.py) | Dependency-free structural checks |

### Try it

Open this repository in a new Copilot session and explicitly request the skill:

> Use case-session-to-wiki to extract reusable troubleshooting knowledge from
> this conversation. Propose separate articles by topic and QA, How-to, or
> Break-fix type. Include original supporting excerpts and exact sources.
> Save the files under that session and return only the file links.

Or choose a format explicitly:

> Use case-session-to-wiki to create a How-to for the goal discussed here.
> Make every step followable by someone unfamiliar with the product.

For an existing case session, the skill must also be available there. A project
skill in this repository is not automatically available in unrelated workspaces.
Install a new personal copy from this repository:

```text
python -B scripts\install_skill.py
```

The [installer](scripts/install_skill.py) verifies file hashes. Identical installs
are a no-op. Different or locally edited destinations are refused, not overwritten;
use a new explicitly selected destination for staged upgrade review. It does not
change other repositories. The already-installed pre-v0.4 personal copy requires
a separately reviewed migration, not a force overwrite.

Start a fresh Copilot process after installation and use `copilot skill list`
to check discovery. Discovery is not proof that a skill has been invoked.

### Supported session input

> Use case-session-to-wiki on the exact local session ID I provide. Propose an
> article set internally and label documentation-based additions. Save the
> de-identified files under that session; do not execute the procedures.

The bundled [session reader](.github/skills/case-session-to-wiki/tools/session_reader.py)
accepts an exact local ID or explicit UTF-8 transcript path. It pages supported
visible messages and tool-result text without loading hidden reasoning, system
events, attachments, or other sessions. See the input contract for exact options
and supported archive shape.

This is not an automatic redactor or permission bypass. Stop on access denial,
unsupported records, or missing input; request a supported transcript rather
than inventing an archive parser. A completed visible-source snapshot is still
not complete case history. Current-context-only extraction remains partial.

### Output and privacy

- One coherent topic per article; one failure mode per Break-fix article.
- Drafts retain uncertainty: recovery does not prove a root cause.
- Source completeness and source coverage are separate. A partial conversation
  can support a narrowly scoped, fully attributed draft, not a complete case history.
- Default enrichment may inspect targeted official originals through authorized
  tools. It never sends case details to search services or runs a new investigation.
- Customer/case identifiers and credentials must be removed before persistence.
- Default output is
  `<selected-session>\wiki-output-<UTC timestamp>-<unique suffix>\`.
  For a named session, this is the source session, not the invoking chat.
  For current-context/transcript-only input, the host supplies the invoking
  session directory. The skill never guesses from the working directory.
- The request authorizes a new folder and de-identified files without another
  confirmation. Plans, article bodies, and evidence previews stay off the console.
  The final response contains only file links and material validation issues.
- Repeated runs create new folders. Existing drafts are never overwritten or
  automatically moved. Explicit no-write requests still prevent saving.
- Local drafts may be mechanically checked while semantic review remains pending.
- `wiki-drafts` and `private-inputs` are ignored **in this repository only**.
  Git ignore is not a privacy guarantee or permission to store real transcripts.
- No automatic publishing, Git commits of generated wikis, uploads, case-system
  changes, email, Teams messages, telemetry, or memory/RAG writes.

### Validation

From this repository:

```text
python -B -m unittest discover -s tests -p "test_*.py" -v
```

Tests cover packaging, installation, reader pagination/exclusions, evidence
matching, invalid inputs, negative cases, and stale semantic-review attestations.
They do not establish the factual accuracy of arbitrary generated articles.
Use the [synthetic scenarios](tests/scenarios.md) for model-behavior evaluation;
record actual outcomes separately from unit-test results. No real case data is
included in tracked tests or fixtures.

For repeatable native prompt tests, run the [smoke runner](scripts/behavior_smoke.py)
with `--fixture topic-plan`, `false-quote`, or `enrichment` and a new approved
`--output` path. It uses only skill/view tools, checks actual native invocation,
and fingerprints the bundle; semantic grading remains explicitly separate.
The [v0.4.0 evaluation record](tests/behavior-evaluation-0.4.0.json) is historical:
its preview/save-approval expectations do not describe v0.5.0 delivery.
It remains an author assessment, not independent release approval.

Existing v0.3 trial articles are not silently migrated to the new evidence schema
or retroactively marked independently reviewed.

### Deliberately deferred

Cross-account/cloud session retrieval, attachment extraction, broad literature
searches, live case evidence retrieval, automated redaction, merging into existing
wikis, publication, and closure automation are not part of v0.5.0.

### Packaging references

- [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Adding skills to Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)

Version: 0.5.0. Last reviewed: 2026-09-16.
