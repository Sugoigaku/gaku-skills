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
