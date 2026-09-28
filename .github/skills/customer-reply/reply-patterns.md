# Reply Patterns

All examples are synthetic English writing examples with placeholders. They
are not ready-to-send messages, product facts, service policies, or evidence.
Resolve every placeholder from the selected context before presenting a
complete draft. Apply the language confirmation rule in [SKILL.md](SKILL.md).

Read only the matching scenario or technical subsection. The suggested shapes
are optional scaffolding: adapt them to the question, combine only useful
elements, and skip templates entirely for a simple wording edit. Evidence and
authorization boundaries still apply when a pattern is used.

Formatting here organizes the reference, not the customer draft. Convert
examples to plain-text paragraphs; omit quote markers, bold, Markdown headings,
tables, and code fences. Simple bullets or numbering are allowed when useful.
Use bare reference URLs and a plain-text signature.

## Direct answer

Use: a technical question or a request to validate an interpretation.

Suggested shape:
1. Thank the specific contribution.
2. Give the direct answer, with the important condition beside it.
3. Explain the decisive distinction or mechanism.
4. Connect inspected evidence to the customer's situation.
5. Separate impact from action; add only necessary follow-up.

Synthetic example:

> Thank you for sharing the result.
>
> Your understanding of [specific point] is correct, with one distinction:
> [display label] and [actual object] are not the same item.
>
> [Verified explanation and relevant reference.] The supplied result confirms
> [narrow observation]. It does not by itself establish [broader conclusion].
>
> For [verified scope], [action required or evidence-supported no-action
> conclusion]. [Any necessary remaining check.]

If the customer asked several questions, preserve their numbering and answer
each once. Never begin an available answer with a request to reconfirm context.
Use separate plain-text cause/interpretation, impact, and action labels for complex
reassurance, but not for a two-sentence clarification.

## Technical answer structures

Use a relevant structure when the reply needs substantial reasoning; a primary
pattern is not a prerequisite. Do not pad the email to meet a length target.
The examples below are synthetic and are not operational instructions.

### Conditional multi-question answer

Start with a short status sentence when part of the answer is pending. Then
preserve the customer's numbering. For each question, provide:
**direct answer -> applicable condition -> explanation/source -> implication**.

> We can answer questions [answered items] now. [Remaining item] is still
> being checked by [confirmed owner].
>
> [Original question number]. [Direct answer]. Under [condition A],
> [supported outcome]; under [condition B], [different supported outcome].
> [Relevant evidence.] Your supplied information establishes [known condition],
> while [missing condition] remains unconfirmed.

Separate infrastructure capability from entitlement, support, or commercial
terms. Keep a shared scope limitation short; do not repeat it under every
question. Do not insert current product limits or historical license rules
from memory. Do not present an unsupported configuration as an equal
recommended alternative to a supported one.
Answer the technical part that can be supported; do not replace it with a
generic referral for commercial advice.

### Mechanism and responsibility boundary

Briefly restate the symptom only if needed to remove ambiguity. Explain
**preserved state -> changed dependency -> mismatch -> observed effect**.
Separate the documented mechanism from the conclusion about this occurrence.

> [Source] establishes that [state] is retained by [operation]. If [dependency]
> changes, the retained state may no longer match, which could explain
> [symptom]. [Case-specific evidence or the check still needed.]
>
> [Team] owns [scope]; [other owner] manages [different scope]. [Verified
> recovery guidance, or a clear statement that a validated procedure is
> not yet available.]

Do not turn a plausible mechanism into a confirmed defect or universal
by-design behavior. A boundary explains ownership, not blame. Suggesting that
an operator validate a recovery procedure is not proof that it is a safe,
supported workaround. Recovery after a change alone does not prove cause.

### Scoped investigation handoff

Use **checked scope -> result -> remaining uncertainty -> next owner ->
minimum required input**.

> We checked [specific layer/path] using [evidence]. Those checks did not find
> [particular failure] within [scope]. They do not yet establish why
> [customer symptom] persists.
>
> The next step is [authorized investigation with responsible team]. To
> identify the affected component, could you provide [minimum identifiers
> or artifact] through [approved channel]?

Report observed exclusions, not a global clean bill of health. Distinguish
"we will request investigation" from "investigation has started".

### Retrospective explanation

Use **what is confirmed now -> what was known then -> why the decision was
made -> confirmed shortcoming -> authorized improvement or remaining question**.

> We have now confirmed [finding] under [specific prerequisite]. At the time
> of the decision, [documented uncertainty] had not been resolved, so
> [recorded precaution] was taken.
>
> [Verified delay or error, if any, with appropriate accountability.]
> [Actual or authorized improvement action.] [Precisely unresolved point.]

Do not use hindsight to claim an unvalidated action was obviously safe, nor
use uncertainty as a blanket defense of poor handling. "No prior failures
found" is not proof of zero risk. New findings must not silently become a
guarantee for all similar cases.

### Remedy comparison

Use paired plain-text paragraphs or simple bullets, not a table:

- [Option A]: [Verified precondition]; [what stops or changes]; [what is
  retained or deleted]; [verified support and availability].
- [Option B]: [Verified precondition]; [what stops or changes]; [what is
  retained or deleted]; [verified support and availability].

> Both options [shared outcome], but [option B] additionally [material side
> effect]. They are not equivalent. [Recommendation tied to the customer's
> stated goal and verified prerequisites.]

Put irreversible consequences before any executable steps. If retaining the
affected data is a requirement, reject or withhold a destructive recommendation
unless that requirement changes with explicit authorization. If a capability
became available later, distinguish the current option from historical
availability. Never perform the operation through this drafting skill.

## Investigation update

Use: investigation is ongoing, including no new result.

Suggested shape: acknowledge time or effort, state current status honestly, distinguish
what is known from what is pending, identify next owner and checkpoint.

Synthetic example:

> Thank you for the additional checks and for your patience.
>
> [Confirmed investigation state]. We do not yet have a confirmed answer to
> [remaining question].
>
> [Actual completed action or authorized next action]. [Approved next-update
> time and time zone, if available]. [Customer input needed, or an explicit
> statement that none is needed for the current step.]

Do not manufacture activity to make a no-update message sound substantive.
Do not promise a fix date when only a progress-update time is known. If no
checkpoint has been agreed, note this in engineer-only review notes.

## Information request

Use: a particular result is needed to decide the next step.

Suggested shape: recognize completed work, explain the remaining uncertainty, ask for
the minimum artifact, explain how it will be used.

Synthetic example:

> Thank you for confirming that [earlier check] has already been completed.
>
> To distinguish [possibility A] from [possibility B], could you share
> [specific existing result, scope, and relevant time range] through
> [approved channel]?
>
> This will let us verify [decision]. There is no need to repeat [earlier
> operation] solely to obtain a new result if the existing evidence is
> available and sufficient.

For a necessary new operation, use only verified instructions and explain
access requirements, impact, approval, expected result, and what to return.
If those are missing, ask the engineer, not the customer, to approve a guessed
procedure. Never request credentials or an unrestricted log dump.

## Correction or missed answer

Use: the earlier response was ambiguous, incorrect, or incomplete.

Suggested shape: answer the actual question, identify the exact correction, take brief
accountability, explain what is and is not established, give the next step.

Synthetic example:

> Thank you for pointing out the distinction.
>
> The correct interpretation is [corrected statement]. In the earlier reply,
> [term] referred to [intended object], not [different object]. I apologize
> that the wording did not make this clear.
>
> [What the evidence establishes]. The available information does not
> establish [remaining issue], so [authorized next step].

If the earlier answer was wrong, say it was incorrect rather than disguising
it as a clarification. If an answer was omitted, acknowledge the specific
omission and name who will confirm it. Never fill that gap with speculation.

## Follow-up

Use: the customer owns the next input or has not confirmed remaining concerns.

Suggested shape: briefly reference the previous answer, ask about the remaining blocker,
offer a low-burden path. Do not repeat the whole investigation.

Synthetic example:

> I am following up on [previous answer or agreed action].
>
> Are there any remaining questions about [scope], or is [specific input]
> still being coordinated? If more time is needed, please let us know
> [minimum scheduling information genuinely required].

A closure proposal is conditional and distinct from a closure announcement.
Do not invent a no-response deadline or claim that silence grants consent.
If a verified service policy governs follow-up, apply its actual terms rather
than making the template a policy.

## Closure or agreed pause

Use: closure or deferral has actually been agreed.

Suggested shape: acknowledge the precise agreement, state the real technical status,
describe the authorized administrative next step, provide a supported path
for later contact, and thank the customer's specific effort.

Synthetic example:

> Thank you for confirming that [actual closure or pause decision].
>
> [Accurate current status]. [If deferred: the remaining verification has not
> been completed.] [Approved wording for the intended closure process.]
>
> If further assistance is needed, [verified contact/continuity instructions].
> Thank you for your help with [specific effort].

Do not describe deprioritized work as resolved. Do not invent a reopen period,
promise preservation of records, or announce a completed closure that has not
occurred. Drafting this message never authorizes a case-state change.

## Optional short receipt acknowledgment

Use: supplied material has actually been received and checked for accessibility.
Thank the customer, state exactly what was verified, and give the next owner.
Receiving a file does not mean its technical contents have been analyzed.

## Final shape

The customer body should read as one coherent email, not a filled internal
form. Omit empty headings and unnecessary templates. Keep review notes,
evidence gaps, draft status, and tool failures outside the customer body.
