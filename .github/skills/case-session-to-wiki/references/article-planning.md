# Topic and Article Planning

## Topic inventory

Partition by technical subject and reader task, not by chat length, date, or
every new user message. Follow-up questions can belong to an earlier topic.
Later corrections qualify the earlier material even when separated by many turns.

For the available source:

1. Identify all substantive topics within the engineer's requested scope.
2. Group related observations, questions, procedures, and corrections.
3. Identify the distinct reader tasks supported by each topic's evidence.
4. Propose only articles with useful independent content. For partial sources,
   list known gaps without claiming that unseen history contains no other topics.

If the engineer requests one topic or one type, honor that boundary. Mention
other useful material as out of scope; do not expand the deliverable by default.

## Topic-by-type decisions

| Situation | Decision |
| --- | --- |
| Independent subjects use the same format | Propose separate articles of that type. |
| One subject has conceptual answers, a setup goal, and a distinct repair | Propose QA, How-to, and Break-fix only when each has its own supported task. |
| A failure discussion includes a few short explanatory questions | Keep them in the Break-fix unless a separate QA would add independent value. |
| Several retries diagnose the same failure | Consolidate into one decision path, not one article per attempt. |
| A topic lacks original sources or necessary steps | Mark its candidate blocked; do not fill the gap from another topic's success. |
| Administrative chatter or repetitive advice | Exclude it with a brief reason, without echoing identifying details. |

Do not automatically generate three formats for every topic. A useful article
set is not the Cartesian product of all topics and all available templates.
Split on a distinct reader task; consolidate duplicate explanations and repeated
questions. Retain one failure mode per Break-fix article.

## Proposed article table

Use this table as an internal working structure, not console output. Replace
the example row; the IDs are local plan labels, not case or session identifiers.

| ID | Topic | Wiki type | Reader task and scope | Proposed title | Sources and coverage | Readiness and gaps | Proposed filename |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | <Technical topic> | <qa, how-to, or break-fix> | <Distinct task and exclusions> | <De-identified title> | <Source labels; full/partial within the available input> | <Candidate or blocked; reason> | <type>-<technical-topic>.md |

Also list excluded or deferred topics and the reason for each. Use only
de-identified titles and filenames, even in the plan.

Select the supported set automatically within the requested scope. Do not ask for
routine article-list approval. An explicit plan-only or no-write request still
limits execution. Local saving does not authorize publication or procedure execution.

If the source or output is too large to handle reliably, propose explicit batches
from this inventory. Do not silently cap the article count,
omit later corrections, or delegate raw case content to make the problem disappear.
Keep the plan internal; do not print it or create a raw-source manifest.
The sanitized evidence companion is authorized for session-local saving; never
fill it with the reader's raw output.
Respect the documented validator limits when proposing each batch: at most
32 articles, 256 sources, and 512 claims/enrichments per article; files are limited
to 2 MiB and individual text fields to 4,096 characters. Keep original excerpts
short. Larger sets need separate batch directories/companions under the run folder, not
silent omission of the remaining topics or unannounced weakening of validation.

## Per-article validation

Apply the selected template, source-attribution gate, privacy review, and outcome
classification to each article independently. Keep coverage scoped to the
material that article actually uses. A blocked How-to must not inherit a sibling
QA's complete references or a Break-fix's verification status.

Embed the necessary source entries in each article. Shared references can be
reused from the approved companion with consistent IDs, but each quote must
support that article's own claim. A sibling article is not an original reference.
Avoid redundant main-body retelling; use optional related-article links for navigation.

## Set delivery

1. Keep drafts and article plans off the console. Apply each article's gates internally.
2. Follow [session-local delivery](session-output.md): create a fresh run directory
   under the selected session without asking for scope, folder, or save approval.
   Save the ready subset and report blocked/deferred articles with reasons.
3. Check every destination before writing. Resolve duplicate generated filenames
   with distinct technical slugs or numeric suffixes inside the new run folder;
   never overwrite an existing file or reuse an earlier run directory.
4. Write the sanitized companion first, then the ready review articles.
   Mechanical validation and independent semantic review remain distinct.
   Read back each file and run the documented validator.
   If a write fails, stop further writes and report the saved and unsaved subset.
   Do not delete earlier successful files or claim an atomic all-or-nothing save.
5. Add sibling links only after the target files exist, within the saved set.
   Recheck the links and the files changed by that navigation pass.
6. Return one result per planned article, using `saved`, `blocked`, `failed`, or
   `deferred`, with its full absolute file path visibly written out or a specific
   reason. Include the full output-directory path and clickable links; a hidden
   hyperlink target or filename alone is insufficient. Do not paste article bodies,
   evidence excerpts, or full planning tables into the final response.

No index page or other extra file is created unless the engineer asks for it.
The de-identified evidence companion is included in the local-save authorization.
Existing prohibitions on Git staging, publication, messages, and memory writes
still apply to the entire set.
