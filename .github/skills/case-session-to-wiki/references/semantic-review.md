# Semantic Review and Release Gate

## Three different claims

1. **Mechanical consistency:** structure, source records, quote matching against
   supplied evidence, citation links, and known identifier patterns pass.
2. **Semantic review:** a human or separate agent has checked what the sources
   actually support, source authenticity/applicability, and the completeness of
   the claim map.
3. **Publication approval:** the engineer authorizes distribution to an identified
   audience. This skill never performs publication.

None implies the next. A passing validator is not a security certification,
proof of de-identification, live source-authenticity check, or factual approval.

## Reviewer inputs

Provide the saved de-identified article set and evidence companion. Do not
send raw sessions or credentials to another agent. Use a human if the remaining
evidence cannot be safely shared.

The reviewer must be separate from the generator. Do not invent a reviewer,
relabel the generator as independent, or create a passing review record from
the generator's own assessment. A separate model is preferred if the engineer
selects one, but do not silently change model configuration or spend on a factory.

Review final content hashes. If any article, reference, claim map, or evidence
text changes, the prior attestation is stale. Rerun mechanical checks and obtain
a new review for the changed final bytes.

## Required checks

| Check | What the reviewer actually verifies |
| --- | --- |
| Claim coverage | Every substantive answer, assumption, action, match/exclusion criterion, and outcome appears in the claim map. A generator-created map may omit claims. |
| Entailment | Each cited passage supports the specific claim, not merely its subject area. A true quote beside a false claim fails. |
| Original and locator | Reopen public originals when possible; distinguish supplied excerpts from independently inspected publisher text. A private observation points to an approved sanitized record, not an anonymous archive line. |
| Applicability | Product/version/environment and the reader's intended task match the source. Conflicting revisions remain explicit. |
| Chronology | Later corrections, failed validations, and meaningful contradictory evidence were not omitted. |
| Execution | Proposals, documented steps, syntax checks, and observed runs have distinct labels. New procedures do not inherit old experiment success. |
| Safety | Prerequisites, failure paths, impact, and rollback are sufficient for the claimed audience. No dangerous historical shortcut becomes a recommendation. |
| Privacy | Review natural language, filenames, identifiers, quotations, URLs, code, and the companion; regex checks do not recognize all names or private context. |
| Delivery | Article-level gates, approved paths, companion references, partial failures, and local-only scope are accurately reported. |
| Diagrams | Captions, labels, arrows, and ordering match sources; hypotheses are marked; no private identifiers are exposed. Mermaid source is covered by the article hash, and SVG assets by explicit asset hashes. |

For every mapped claim, record supported, qualified, or unsupported with a reason.
A qualified claim must be explicitly limited in the article. Unknown origins,
misquotes, missing critical steps, and omitted substantive claims require changes.

## Attestation

Use the exact schema in [evidence validation](evidence-validation.md).
The validator checks the submitted reviewer kind, claim coverage identifiers,
and final hashes. It does not authenticate the reviewer or prove the review
actually happened; retain that human responsibility explicitly.

The generator keeps reference status at most `mechanically-checked`.
If final metadata is later changed to `complete`, get a new attestation bound
to those exact final bytes. Never modify content after review and reuse an old
passing record.

## Acceptance evidence

Before sharing a release, execute the synthetic negative/edge cases, retain
their non-sensitive results, and verify native skill discovery/invocation in a
fresh process. Distinguish tests of Python code, prompt behavior under constrained
tools, and full host integration. Do not present one as proof of the others.

This review never authorizes sending, publishing, closing cases, changing live
systems, or executing untested commands.
Routine session-local saving already follows the generation request; review
happens on the saved files, without a console preview or another save prompt.
