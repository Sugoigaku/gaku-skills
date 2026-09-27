# Voice and Wording

Consult the sections relevant to the wording problem; this is not a required
reading list or a sequence of editing passes. For a simple polish, retain the
supplied structure unless it obscures the answer or an important qualification.

## The voice in one sentence

Respect the customer's effort, answer directly, explain carefully, and make the
next step feel justified rather than imposed.

## Tone rules

| Dimension | Do | Avoid |
| --- | --- | --- |
| Courtesy | Use a stable professional greeting and one context-specific thank-you | A stack of interchangeable greetings and apologies |
| Attention | Acknowledge the exact result, question, or coordination just supplied | A generic acknowledgment followed by the same checklist |
| Certainty | Be firm about verified facts and conditional about untested applicability | Hedging every fact, or disguising a hypothesis as cause |
| Ownership | Say what you have done, will do, or are waiting to confirm, accurately | Claiming escalation or progress that has not occurred |
| Accountability | Admit an omitted answer or unclear explanation briefly and correct it | Blaming the customer for misunderstanding or inventing fault |
| Reassurance | State the verified scope of no impact and its prerequisites | "Everything is fine" based on an alert interpretation alone |
| Requests | Explain why, ask politely, and specify the expected artifact | Unexplained imperatives or "please check everything" |
| Closure | Respect actual agreement and preserve a supported continuity path | Equating a pause, no reply, or deprioritization with resolution |

Politeness should soften the interpersonal burden, not the technical meaning.
Avoid exaggerated deference, repeated gratitude in every paragraph, promotional
language, emojis, and dramatic urgency.

## Japanese wording cues

The short conventional expressions below are verbatim quotations. They are
language cues, not complete templates. Explanations and skill instructions are
in English. Use Japanese cues only within authorized Japanese customer-facing
text; never insert them into English correspondence.

| Communicative job | Short phrase cue | When and how to use it |
| --- | --- | --- |
| Standard greeting | "いつもお世話になっております。" | A brief business opening; do not repeat it within the body |
| Thank a reply | "ご連絡いただきまして誠にありがとうございます。" | Replace generic gratitude with a reference to the actual contribution when useful |
| Thank investigation patience | "調査にお時間をいただきまして誠にありがとうございます。" | Use when investigation time actually elapsed, not as a universal opening |
| Recognize receipt or agreement | "承知いたしました。" | Name the particular result or decision being acknowledged |
| Introduce a substantive answer | "結論から申し上げますと、" | Follow immediately with the answer, not another preamble |
| Confirm a correct interpretation | "ご認識の通り、" | Confirm only the part that is correct; add the exact qualification beside it |
| Add clarification | "以下の通り補足いたします。" | Expand an earlier answer without pretending it never existed |
| Mark an observation | "お見受けしております。" | Describe what the available evidence appears to show, not a universal fact |
| Mark a limitation | "現時点から確認可能な情報のみでは原因を断定することは叶いませんでした。" | Say what cannot be concluded before offering general mechanisms |
| Connect reasoning | "そのため、" / "一方で、" / "なお、" | Separate consequence, contrast, and caveat; use only real logical connections |
| Request an action | "実施いただけますでしょうか。" | Pair with exact scope, reason, and relevant impact precautions |
| Request a result | "結果をご共有いただけますでしょうか。" | Specify which result and how it helps the next decision |
| Prefer existing evidence | "もし差し支えなければ、" | Offer a genuinely optional, lower-burden route, not a disguised mandatory action |
| Acknowledge burden | "お手数をおかけいたしますが、" | Use once around a necessary ask, not before every sentence |
| Stronger courtesy | "ご確認いただけますと幸甚でございます。" | Reserve for unusually burdensome requests; ordinary replies need less ceremony |
| Polite closing | "どうぞよろしくお願いいたします。" | A short closing where the delivery channel does not supply one |

Preserve product names, UI labels, error strings, and documented terms exactly.
Explain ambiguous terms in plain language on first use. Keep professional
Japanese sentence endings consistent; do not alternate casually with a highly
formal register. Avoid literal translation of English idioms.

Useful substantive transitions in Japanese include the short quoted cues
"今回確認できた内容としては、" (introduce newly confirmed findings),
"つまり" (explain the practical implication), and "一方で、" (introduce a
different condition or remaining limitation). The phrase "結果論としては"
signals hindsight, not an excuse or a substitute for accountability.
Use these only when they reflect the real logical relationship.

## Confidence ladder

Choose the level per claim, not per email:

1. **Verified observation:** "The supplied result confirms [narrow fact]."
2. **Confirmed interpretation:** "[Responsible team] confirmed [conclusion]
   for [scope]." Use only with an actual attributable finding.
3. **Evidence-supported inference:** "This is consistent with [mechanism];
   [remaining check] is needed to confirm it."
4. **General behavior:** "In general, [documented behavior]. This alone does
   not establish the cause in your environment."
5. **Unknown:** "The available information does not establish [cause/impact].
   The next step is [authorized action]."

Do not promote a quoted general statement to a case-specific confirmation.
Keep a dependency next to reassurance: "No change is required for [scope],
provided [verified prerequisite]," not an unconditional promise.

## Distinctions that improve explanation

- **Label versus object:** Define each, explain their relationship, then answer
  which one the customer actually needs to locate or change.
- **Signal versus impact:** An alert explains an observation; separate that
  observation from evidence of functional impact and action requirements.
- **General mechanism versus this occurrence:** Explain what can happen without
  pretending it proves what happened here.
- **Similar operations versus the exact operation:** If a retry is proposed,
  identify the precise difference rather than saying the previous attempt was
  wrong.
- **Administrative closure versus technical recovery:** Say whether work is
  complete, deferred, or still unverified. Do not let courtesy erase that status.

## Editing cues

- Replace ambiguous pronouns with the relevant object.
- Remove duplicate explanation and decorative policy footers, not supporting
  evidence or qualifications. Each technical paragraph should help the customer
  understand, decide, or act.
- Make vague asks specific: artifact + scope + purpose.
- Briefly acknowledge a missed answer or unclear wording, then correct it;
  do not invent responsibility for the underlying incident.
- A no-action conclusion needs no artificial ask.

For a substantive explanation rather than a wording edit, consult the relevant
[technical answer structure](reply-patterns.md#technical-answer-structures).

## Guardrails over stylistic habits

These requirements take precedence over fluent or courteous phrasing:

- No indefinite "please wait" when an agreed update checkpoint is available.
  If no time is authorized, flag that gap to the engineer rather than making
  up a promise.
- Do not repeat a disruptive action simply to obtain cleaner evidence.
  Prefer existing results; any repeat needs necessity, impact review, and
  authorization.
- Paraphrase specialist findings into customer-safe language. Do not forward
  internal deliberations or speculative blame as an explanation.
- Do not add "please disregard" or equivalent reassurance without the evidence
  and conditions that make it safe.
- Never copy a complete historical reply or distinctive personal sign-off.
  Adapt the communication function, not somebody else's identity.
