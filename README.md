# Gaku Skills

Reusable GitHub Copilot skills for technical support work.

## First skill: case-session-to-wiki

Turn a troubleshooting conversation into reusable technical knowledge at case
closure. This is **not a transcript dump, a chronological case summary, or an
automatic case-closing tool**.

The first version is an instruction-driven framework. It extracts the problem,
decisive evidence, useful rejected hypotheses, the resolution, verification,
follow-up answers, and lessons that will help another engineer.

### Workflow

```text
Explicit request near case closure
    -> Confirm source coverage and issue scope
    -> Separate evidence from suggestions
    -> Extract reusable findings and decisions
    -> De-identify the content
    -> Compose a Markdown draft
    -> Check quality and request engineer review
    -> Save to an approved local path
```

### Files

| File | Responsibility |
| --- | --- |
| [SKILL.md](.github/skills/case-session-to-wiki/SKILL.md) | Trigger, workflow, input/output contract, and safety boundaries |
| [Extraction rules](.github/skills/case-session-to-wiki/references/extraction-rules.md) | Knowledge selection, evidence classification, and de-identification |
| [Wiki template](.github/skills/case-session-to-wiki/templates/wiki-template.md) | Consistent structure for each generated article |
| [Evaluation scenarios](tests/scenarios.md) | Synthetic behavioral cases and acceptance criteria |
| [Framework tests](tests/test_skill_framework.py) | Dependency-free structural checks |

### Try it

Open this repository in a new Copilot session and explicitly request the skill:

> Use case-session-to-wiki to extract reusable troubleshooting knowledge from
> this conversation. Keep it de-identified and show me the draft before saving.

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

- One technical issue per article; unrelated issues require a scope decision.
- Drafts retain uncertainty: recovery does not prove a root cause.
- Customer/case identifiers and credentials must be removed before persistence.
- The skill proposes `wiki-drafts\<technical-topic>.md` in an approved workspace.
  It previews the article and obtains approval for the local destination.
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

Automatic session export/import, live evidence retrieval, public-document
revalidation, merging into an existing wiki, wiki publication, and closure
automation are not part of v0.1.0. Refine the article shape on a sample case first.

### Packaging references

- [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Adding skills to Copilot CLI](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)

Version: 0.1.0. Last reviewed: 2026-09-16.
