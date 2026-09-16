# Wiki Template Selector

This index replaces the v0.1 generic article template. Do not render this file
as a wiki or fall back to a catch-all structure. Select one template below.

## Selection rules

1. Honor the engineer's explicit type. If it would omit essential safety or
   diagnostic content, explain the mismatch and ask before changing the type.
2. Otherwise identify the dominant reader intent:

   | Intent | Type | Template |
   | --- | --- | --- |
   | Understand a topic, behavior, limitation, or answer | `qa` | [QA](qa-template.md) |
   | Achieve a goal, configure something, or perform a task | `how-to` | [How-to](how-to-template.md) |
   | Recognize and restore a failed operation | `break-fix` | [Break-fix](break-fix-template.md) |

3. A repair does not become How-to merely because it has numbered steps.
   A configuration goal does not become Break-fix merely because questions arose.
   The current requested reader task wins over incidental conversation content.
4. If the intent is genuinely mixed or ambiguous, ask a focused scope question.
   Propose separate, related articles when useful; do not create extra files
   without agreement. A brief relevant Q&A can live inside a procedural article,
   but must not hide a second independent topic or replace its required sections.

## Shared contract

- Set `wiki_type` to exactly `qa`, `how-to`, or `break-fix`.
- Keep source coverage separate from reference completeness and outcome confidence.
- All three templates include **References and original excerpts** and use the
  same [source entry template](source-entry-template.md).
- Cite sources beside the answers, steps, checks, and conclusions they support.
  A bibliography without inline attribution or original excerpts is incomplete.
- Apply the [attribution rules](../references/source-attribution.md) before saving.
  Expand source entries inside the generated article; do not leave template links.
- Keep QA concise, How-to novice-followable, and Break-fix diagnostic and actionable.
  Do not add irrelevant sections solely to make the types look alike.
- Missing evidence stays explicit. Reference or critical procedural gaps block
  saving until resolved or the unsupported scope is removed.
