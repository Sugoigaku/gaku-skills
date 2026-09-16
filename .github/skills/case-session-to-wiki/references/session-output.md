# Session-local Output

## Default delivery

A request to generate wikis authorizes local creation of de-identified articles
and their sanitized evidence companion inside the selected session. Do not print
previews or ask the user to approve the article list, evidence file, save path,
or folder creation. Plan, sanitize, write, validate, and return concise file links.

Explicit read-only, no-write, or plan-only requests still prevent saving.
Missing source material, unsafe disclosures, and unresolved session identity
are real blockers, not reasons to guess or silently weaken checks.

## Resolve the correct session

- Exact source session ID: use that source session's directory and the same root
  used by the reader, even if this skill was invoked from a different session.
- Current conversation or standalone transcript: use the invoking session's
  directory explicitly supplied by the host runtime.
- An explicit runtime directory must already exist and have a canonical UUID
  basename. An ID-selected session must also have its existing `events.jsonl`.
- Do not use the transcript's parent, current working directory, repository, or
  personal skill directory. Do not search for the latest session as a fallback.
- If runtime/session identity is unavailable, report that missing input. Ask for
  the exact session only if needed; never ask for routine save permission.

## Create a fresh run directory

Use the bundled helper from the skill's directory:

```text
python -B tools\create_output_directory.py --session-id <exact-lowercase-uuid>
python -B tools\create_output_directory.py --session-id <exact-lowercase-uuid> --session-root <same-root-used-by-reader>
python -B tools\create_output_directory.py --session-dir <runtime-provided-session-directory>
```

Do not combine `--session-dir` with ID/root options. These are placeholders, not
literal values to execute. The helper reuses the reader's strict path/reparse
checks and creates only one empty directory:

```text
<selected-session>\wiki-output-<UTC timestamp>-<unique suffix>\
```

The unique suffix is created atomically, so another run does not overwrite an
earlier one. Success returns only `status` and `output_directory` as JSON.
Errors return a fixed diagnostic and a nonzero exit code; never fall back to
another directory after an error. The helper does not read the archive body,
write articles, execute procedures, or certify de-identification.

## Write and validate

1. Finish source selection and de-identification internally; no console preview.
2. Create the new run directory without a confirmation prompt.
3. Save `evidence.json` and the selected `<wiki-type>-<technical-topic>.md` files
   in that directory. Do not persist raw inputs or reverse identity mappings.
4. Resolve duplicate generated names with distinct technical slugs or numeric
   suffixes. Always use create-only writes; if an unexpected file already exists,
   use an unused name and record the actual destination rather than overwrite it.
5. Validate the same-directory bundle, read back internally, and add only links
   whose targets exist. Revalidate after content changes.
6. For oversized sets, create separately numbered batch subfolders in this run
   directory with one companion per batch. No routine batch-approval question.
7. Report saved, blocked, failed, or deferred articles concisely. A failed or
   incomplete file is not a successful/validated output. Partial source coverage
   alone does not prevent a narrowly supported local draft.

Review happens on the saved files. Local save authorization is not independent
semantic review, approval to share restricted sources, or publication consent.
Never auto-commit, push, send messages, or change live systems as part of generation.
