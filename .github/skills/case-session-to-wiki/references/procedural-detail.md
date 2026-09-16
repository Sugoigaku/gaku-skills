# Detailed Actions, Simple Structure

This applies to How-to and Break-fix. Keep QA as direct questions and answers.
Concise means removing repetitive forms, not omitting the instructions a reader
needs. A step can contain several numbered substeps, a complete code block,
and useful notes. Do not impose a sentence, line, or word-count target.

## UI actions

For a UI operation, specify the target machine/service, how to open the console
or page, the navigation path, the exact option/control, what to enter or select,
and how to apply the change. Include the relevant wizard choices in order.
Use the labels supported by the source and applicable product version.

Do not stop at "import the certificate," "restart the service," "configure the
policy," or "verify connectivity." Explain how the reader performs that action.
Use numbered substeps under the existing Step heading, not a new checklist
of Where/Why/Impact fields.

## Complete commands

When PowerShell or another CLI is an appropriate documented way to do the task,
include the full command or script in a fenced block with its language.

- State where to run it, required elevation, and relevant shell/module version.
- Initialize required variables or point to an explicitly defined earlier setup.
  Explain every placeholder and how the reader obtains its value.
- Include the required parameters, setup, and continuation syntax. Do not use
  ellipses, "same as above," or pseudocode in a runnable block.
- Do not embed credentials or invent flags. Verify Microsoft-related commands
  against official documentation/code references when enriching the source.
- Use short code comments for non-obvious substitutions or important behavior.
  Put longer explanations in a short Notes paragraph or bullets after the block.
- State the observable result and how to interpret it. Include a failure branch
  only when it changes what the reader should do next.

A complete command is not automatically tested. Keep execution status and
provenance in the companion, and do not upgrade an adapted command to lab-tested.
The extraction workflow never runs the command against the reader's environment.

## Choosing UI or CLI

Use the practical, source-supported route. Include a CLI alternative when it
materially helps, especially for repetitive or precise operations; label it
as an alternative so the reader does not perform both routes unintentionally.
Do not assume a registry write and a Group Policy change are equivalent.
If equivalence is not established, describe the supported difference or keep
only the documented route.

## Impact and verification

Keep shared prerequisites and significant impact at the beginning. Add a local
warning near an action only when it prevents a real mistake. Do not repeat
"no impact," "no rollback required," or a full review form under every step.

For verification, include the actual query, command, or UI navigation and what
success looks like. In Break-fix, make matching checks executable too, rather
than merely naming an event ID or certificate property.

## Completeness check before saving

Read the procedure as someone unfamiliar with the product:

1. Can they find the correct screen and option without guessing?
2. Can they run each command after replacing the explained inputs?
3. Can they recognize success or know when to stop?
4. Is each important detail supported by inspected evidence/documentation?

If a required detail is missing, use the allowed documentation enrichment or
report the gap; do not shorten it into a vague instruction. Preserve short
references and final Double-check items without hiding critical safety limits.
