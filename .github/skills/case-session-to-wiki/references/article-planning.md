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

Show this table in the conversation before drafting a multi-article set. Replace
the example row; the IDs are local plan labels, not case or session identifiers.

| ID | Topic | Wiki type | Reader task and scope | Proposed title | Sources and coverage | Readiness and gaps | Proposed filename |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A1 | <Technical topic> | <qa, how-to, or break-fix> | <Distinct task and exclusions> | <De-identified title> | <Source labels; full/partial within the available input> | <Candidate or blocked; reason> | <type>-<technical-topic>.md |

Also list excluded or deferred topics and the reason for each. Use only
de-identified titles and filenames, even in the plan.

Ask one focused question to approve or adjust the proposed set. If the exact set
was already approved, proceed without asking again. Approval to draft a set is
not approval to save it, publish it, or execute its procedures.

If the source or output is too large to handle reliably, propose explicit batches
from this inventory and obtain agreement. Do not silently cap the article count,
omit later corrections, or delegate raw case content to make the problem disappear.
Keep the plan in the conversation; do not create a persistent raw-source manifest.

## Per-article validation

Apply the selected template, source-attribution gate, privacy review, and outcome
classification to each article independently. Keep coverage scoped to the
material that article actually uses. A blocked How-to must not inherit a sibling
QA's complete references or a Break-fix's verification status.

Embed the necessary source entries in each article. Shared references can be
reused, but each quote must support that article's own claim. A sibling article
is not an original reference. Avoid redundant main-body retelling; use optional
related-article links for navigation.

## Set delivery

1. Show the drafts and one row per article with its gates and exact proposed path.
2. Ask for approval for the files to save. If some articles are blocked, offer
   the ready subset and explicitly identify what remains; do not silently choose.
3. Check every destination before writing. If two topics yield the same filename
   or a destination already exists, ask for distinct approved paths. Do not
   overwrite, auto-merge, or silently invent a suffix.
4. Write only approved articles whose individual gates pass. Read back each file.
   If a write fails, stop further writes and report the saved and unsaved subset.
   Do not delete earlier successful files or claim an atomic all-or-nothing save.
5. Add sibling links only after the target files exist, within the approved set.
   Recheck the links and the files changed by that navigation pass.
6. Return one result per planned article, using `saved`, `blocked`, `failed`, or
   `deferred`, with its path or specific reason. A discussed preview is not saved.

No index page or other extra file is created unless the engineer asks for it.
Existing prohibitions on Git staging, publication, messages, and memory writes
still apply to the entire set.
