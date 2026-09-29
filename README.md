# Gaku Skills

Two reusable skills for technical support work.

## customer-reply

Draft or improve customer support replies, including technical answers,
progress updates, follow-ups, and closure messages. Emphasizes clear,
evidence-based wording and Japanese business correspondence. Drafts only;
does not send messages.

Customer drafts use plain text, with simple bullets only when useful, and a
straightforward Japanese self-introduction rather than an overly formal one.

[Skill files](.github/skills/customer-reply)

## case-session-to-wiki

Turn troubleshooting conversations into reusable QA, How-to, or Break-fix
Wiki drafts. Organizes topics, removes identifying details, and preserves
actionable steps and source references. Does not publish automatically.

[Skill files](.github/skills/case-session-to-wiki)

Version 0.10.0 keeps sources inside each article: official documentation gets
descriptive links and relevant passages; session evidence gets short attributed
quotes without links or artificial line numbers. No separate `evidence.json`,
claim map, or evidence sidecar is generated. Answers focus on the technical task,
not an evidence audit. The three article types, de-identification, and draft-only
review status are retained.

Delivery shows full Windows paths in inline code with separate clickable links
derived from the same verified paths, preserving the separator before `.copilot`.
Existing generated articles and sidecars remain untouched.

The package remains seven Markdown files, with no bundled executable helpers.
Native tools are preferred; ordinary approved host commands may perform scoped
local file creation, metadata inspection, and readback. This does
not authorize troubleshooting execution, raw archive parsing, or reconstructed
validators. Missing preferred tools alone do not end the task; unsafe access,
missing essential evidence, or an unverified output destination still block it.

This revision follows the short descriptions, progressive disclosure, and
outcome-based completion principles in
[Rethinking skills and prompts for GPT-6 Astra](https://developers.openai.com/blog/rethinking-skills-and-prompts-for-gpt-6-astra).
The skill remains model-neutral; no model selection or stronger factual guarantee
is implied. Changes to the skill do not alter repository-wide contributor rules.

## Download

On [GitHub](https://github.com/Sugoigaku/gaku-skills), select **Code > Download ZIP**
and extract it, or clone the repository:

```text
git clone https://github.com/Sugoigaku/gaku-skills.git
```

Each skill is in `.github\skills`. Keep its entire folder, including all
supporting Markdown files, not just `SKILL.md`.

## Install for GitHub Copilot CLI

With Python 3.10+ installed, open **Command Prompt** in the downloaded repository
and run the command for the skill you want (or both):

```text
python -B scripts\install_skill.py --source .github\skills\customer-reply --destination "%USERPROFILE%\.copilot\skills\customer-reply"
python -B scripts\install_skill.py --source .github\skills\case-session-to-wiki --destination "%USERPROFILE%\.copilot\skills\case-session-to-wiki"
```

The installer will not overwrite an existing copy with different contents.
Start a fresh Copilot CLI session, then ask it to use `customer-reply` or
`case-session-to-wiki`. The skills themselves do not require Python.
