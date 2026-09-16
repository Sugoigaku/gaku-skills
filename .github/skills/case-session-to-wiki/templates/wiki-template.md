# Wiki Template Selector

This index replaces the v0.1 generic article template. Do not render this file
as a wiki or fall back to a catch-all structure. Select one template per article,
not necessarily one template for the entire session.

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
4. For a rich session, apply the
   [article planning contract](../references/article-planning.md). Inventory the
   topics and select a topic-by-type set internally without routine scope approval.
   Multiple topics can use the same type; one topic can use multiple types if
   each addresses a distinct reader task. Do not produce a three-format cross
   product or pad a single-issue session into three articles.
5. If a candidate's intent is genuinely ambiguous, ask a focused scope question.
   A brief relevant Q&A can stay in a procedural article, but must not hide a
   second independent topic or replace required sections. An explicit single-page
   request limits the set; ask before expanding it.

## Shared contract

- Generate `article_format: concise`: clear answers/actions, not validation forms.
- QA has no repeated Conditions and exceptions blocks. Actual uncertainties go
  into an optional final Double-check section.
- Procedural impact and essential prerequisites appear once up front. Steps
  contain actions and inline citations, not repeated Where/Why/Rollback labels.
- Set `wiki_type` to exactly `qa`, `how-to`, or `break-fix`.
- Keep source coverage separate from reference completeness and outcome confidence.
- Default to `content_mode: documentation-enriched`, labeling added procedures;
  honor extraction-only requests. Apply the [enrichment rules](../references/enrichment.md).
- All three templates include **References** with short original excerpts and use the
  same [source entry template](source-entry-template.md).
- Cite sources beside the answers, steps, checks, and conclusions they support.
  A bibliography without inline attribution or original excerpts is incomplete.
- Apply the [attribution rules](../references/source-attribution.md) before saving.
  Use compact source entries and link the full evidence companion once.
  Do not leave template links or use private archive positions as portable sources.
- Keep QA concise, How-to novice-followable, and Break-fix diagnostic and actionable.
  Do not add irrelevant sections solely to make the types look alike.
- Missing evidence stays explicit. Reference or critical procedural gaps block
  saving until resolved or the unsupported scope is removed.
- For a set, every article passes its own gates. Return a delivery table with
  saved, blocked, failed, or deferred results instead of one shared success flag.
- A mechanically checked review draft can await semantic review. Only an
  independent, final-hash-bound review supports `reference_status: complete`;
  a script pass is not that review and never authorizes publication.
