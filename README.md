# Gaku Skills

Reusable GitHub Copilot skills for technical support work.

## First skill: case-session-to-wiki

Turn a troubleshooting conversation into reusable technical knowledge at case
closure. This is **not a transcript dump, a chronological case summary, or an
automatic case-closing tool**.

This is an instruction-driven framework. It chooses an article format based on
what the reader needs, then extracts the supported knowledge from the session.

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

The initial plan lists each topic, reader task, chosen type, proposed title,
source coverage/gaps, and filename. You approve or adjust the set before drafting.

- Different topics can produce separate articles of the same type.
- One topic can produce several types when each serves a distinct task.
- A simple topic is not expanded into QA, How-to, and Break-fix automatically.
- Short follow-up answers stay with their topic; repeated attempts are consolidated.
- Each article keeps its own sources, uncertainty, validation gates, and save result.
- Blocked topics remain visible. A ready subset is saved only with your approval;
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
requests it; it does not invent a citation or save a reference-complete wiki.
Case observations may cite primary session evidence, but must not masquerade as
published documentation or establish an unsupported general product guarantee.

### Workflow

```text
Explicit request near case closure
    -> Inventory topics and propose topic-by-type articles
    -> Confirm article scope and source coverage
    -> Build a source catalog and inspect cited originals
    -> Extract reusable findings and decisions
    -> De-identify the content
    -> Compose with the selected template and inline citations
    -> Check format quality, reference completeness, and engineer approval
    -> Save approved articles and report each result separately
```

### Files

| File | Responsibility |
| --- | --- |
| [SKILL.md](.github/skills/case-session-to-wiki/SKILL.md) | Trigger, workflow, input/output contract, and safety boundaries |
| [Extraction rules](.github/skills/case-session-to-wiki/references/extraction-rules.md) | Knowledge selection, evidence classification, and de-identification |
| [Article planning](.github/skills/case-session-to-wiki/references/article-planning.md) | Topic inventory, type selection, scope approval, and multi-article delivery |
| [Template selector](.github/skills/case-session-to-wiki/templates/wiki-template.md) | Format selection and shared requirements |
| [QA template](.github/skills/case-session-to-wiki/templates/qa-template.md) | Topic-focused questions and answers |
| [How-to template](.github/skills/case-session-to-wiki/templates/how-to-template.md) | Detailed procedure with checkpoints and failure branches |
| [Break-fix template](.github/skills/case-session-to-wiki/templates/break-fix-template.md) | Issue identification, repair, and verification |
| [Source attribution](.github/skills/case-session-to-wiki/references/source-attribution.md) | Mandatory citation, original-excerpt, and exact-location rules |
| [Source entry template](.github/skills/case-session-to-wiki/templates/source-entry-template.md) | Shared reference record embedded in every article |
| [Evaluation scenarios](tests/scenarios.md) | Synthetic behavioral cases and acceptance criteria |
| [Framework tests](tests/test_skill_framework.py) | Dependency-free structural checks |

### Try it

Open this repository in a new Copilot session and explicitly request the skill:

> Use case-session-to-wiki to extract reusable troubleshooting knowledge from
> this conversation. Propose separate articles by topic and QA, How-to, or
> Break-fix type. Include original supporting excerpts and exact sources.
> Show me the article plan before drafting and saving.

Or choose a format explicitly:

> Use case-session-to-wiki to create a How-to for the goal discussed here.
> Make every step followable by someone unfamiliar with the product.

For an existing case session, the skill must also be available there. A project
skill in this repository is not automatically available in unrelated workspaces.
For reuse across projects, the whole `case-session-to-wiki` directory can later
be installed under `%USERPROFILE%\.copilot\skills`. This scaffold does **not**
install anything globally or change other repositories.

The skill uses the conversation actually available to Copilot, or a local
transcript explicitly supplied by the engineer. It cannot recover missing turns,
hidden reasoning, or omitted tool output. Current-context input is marked
`partial`; a fully read supplied transcript is only
`complete-for-provided-transcript`, not proof of complete case history.

### Output and privacy

- One coherent topic per article; one failure mode per Break-fix article.
- Drafts retain uncertainty: recovery does not prove a root cause.
- Source completeness and source coverage are separate. A partial conversation
  can support a narrowly scoped, fully attributed draft, not a complete case history.
- The skill may read already-cited originals using available, authorized tools.
  It does not send case details to search services or launch a new investigation.
- Customer/case identifiers and credentials must be removed before persistence.
- The skill proposes `wiki-drafts\<wiki-type>-<technical-topic>.md` in an approved
  workspace. It previews the article, passes the reference gate, and obtains
  approval for the local destination.
- `wiki-drafts` and `private-inputs` are ignored **in this repository only**.
  Git ignore is not a privacy guarantee or permission to store real transcripts.
- No automatic publishing, Git commits of generated wikis, uploads, case-system
  changes, email, Teams messages, telemetry, or memory/RAG writes.

### Validation

From this repository:

```text
python -B -m unittest discover -s tests -p "test_*.py" -v
```

Structural tests verify packaging and template contracts, not the factual
accuracy of an AI-generated article. Use the [synthetic scenarios](tests/scenarios.md)
for behavioral evaluation before trying an approved, de-identified real case.
No real case data is included in this repository.

### Deliberately deferred

Automatic session export/import, broad literature searches, live case evidence
retrieval, merging into an existing wiki, wiki publication, and closure automation
are not part of v0.3.0. Targeted read-only inspection of already-cited original
documents is included; inaccessible sources remain explicit gaps.

### Packaging references

- [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Adding skills to Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)

Version: 0.3.0. Last reviewed: 2026-09-16.
