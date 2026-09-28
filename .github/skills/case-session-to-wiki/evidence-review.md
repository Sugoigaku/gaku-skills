# Evidence Companion and Honest Review

This edition has no executable validator. The rules below are an agent-applied
checklist, not automated schema enforcement, a privacy scanner, cryptographic
attestation, or proof that claims are true. Use native JSON/file inspection when
available, but do not generate a replacement validation script. Report missing
inspection capabilities explicitly.

## Evidence companion

Keep the existing evidence schema v1 for portable source and claim records.
The companion is selected de-identified supporting material, not an export of
the session. Author records from originals before drafting their claims.

The following example is entirely synthetic and is a data-shape illustration,
not factual evidence to copy into a real article:

```json
{
  "schema_version": 1,
  "sources": [
    {
      "id": "S1",
      "kind": "sanitized-evidence",
      "title": "Synthetic operator report",
      "publisher": "Engineer",
      "origin": "approved-evidence:operator-report",
      "locator": "Lines 1",
      "version": "Not provided by source",
      "inspection_status": "supplied-excerpt-only",
      "text": "The operator reported that the sample export completed.",
      "excerpt_handling": "verbatim"
    }
  ],
  "articles": [
    {
      "file": "qa-sample-export.md",
      "claims": [
        {
          "id": "C1",
          "text": "The operator reported completion; independent verification is unavailable.",
          "source_ids": ["S1"],
          "basis": "reported"
        }
      ],
      "enrichments": []
    }
  ]
}
```

Use exactly these keys and types; no customer identity, private archive path,
cursor, session ID, reverse map, or raw-log extensions.

### Source records

- `id`: `S` followed by a positive integer, unique across the batch.
- `kind`: `public-document` or `sanitized-evidence`.
- `title`, `publisher`, `origin`, `locator`, `version`: nonempty strings
  describing the actual safe source, not invented publication metadata.
- `inspection_status`: `original-inspected` or `supplied-excerpt-only`.
  An unavailable source cannot support a selected claim.
- `text`: the minimal permitted supporting passage, with necessary visible
  redactions. No full raw records, logs, or documents.
- `excerpt_handling`: `verbatim` or `redacted`. Edited/shortened passages must
  not be called verbatim.

For public documentation, use the actual safe HTTPS origin and exact section,
anchor, page, or lines within it. Inspect the relevant source version. Follow
[source privacy](sources.md#de-identification-before-persistence).

For sanitized evidence, use `approved-evidence:<technical-slug>` as origin and
`Lines 1` for a one-line passage or `Lines 1-N` covering all N included lines.
Count blank lines; normalize CRLF to LF only for counting. These positions are
relative to the included sanitized passage, not historical archive positions.
Retain the actual role and inspection limitation; supplied publisher excerpts
without a verified public origin remain sanitized evidence.

### Article, claim, and enrichment records

Each article record has exactly `file`, `claims`, and `enrichments`.
`file` is its actual safe same-directory `.md` basename. List only articles
intended for that batch; after a partial write failure, explicitly report that
the saved companion may mention files that were not successfully written.

Each claim has exactly `id`, `text`, `source_ids`, and `basis`:

- `id`: `C` followed by a positive integer, unique within that article.
- `text`: the actual substantive statement as written in the article, outside
  References. Include all material assertions, not just convenient examples.
- `source_ids`: a nonempty, duplicate-free array of existing source IDs.
- `basis`: `observed`, `reported`, `documented`, or `inferred`.
  Observed/reported claims need corresponding sanitized primary evidence;
  inferred claims must remain explicitly qualified. Documentation is not
  evidence that the procedure ran.

Each enrichment has exactly `section`, `source_ids`, `change`, and `validation`:

- `section`: the exact, unambiguous heading of the added/adapted procedural step.
- `source_ids`: the relevant sources actually cited in that section.
- `change`: what was added or changed, with its scope.
- `validation`: `not-run`, `syntax-only`, or `lab-tested`, supported by evidence.
  Never promote a new procedure based on an old reported success.

Use an empty enrichment array for no new procedural additions; extraction-only
must have no enrichments. QA additions still need claim maps and citations.
Sources must all be used by at least one claim in the batch. Do not add unused
records to make an article look better researched.

## Article metadata

Use simple YAML front matter with one scalar per key and no duplicate keys,
aliases, nested structures, or hidden instructions. Optional `title` and
`product` are safe strings; `tags` is an array of safe strings.

| Field | Values in this edition |
| --- | --- |
| `wiki_type` | `qa`, `how-to`, `break-fix` |
| `article_format` | `concise` |
| `status` | `draft` |
| `review_status` | `pending-engineer-review` |
| `validation_method` | `agent-checklist` |
| `source_kind` | `current-session`, `provided-transcript`, `local-session` |
| `source_coverage` | `partial`; `complete-for-provided-transcript` only under the input contract |
| `content_mode` | `documentation-enriched`, `extraction-only` |
| `reference_status` | `incomplete`, `checklist-checked` |

How-to additionally requires `procedure_status`: `unverified`,
`documented-not-tested`, or `verified-in-source`.
Break-fix requires `root_cause_status`: `unknown`, `suspected`, or `confirmed`,
and `resolution_status`: `unverified`, `reported`, or `verified`.
QA must not inherit these type-specific outcome fields.

Default all templates to partial coverage, incomplete references, and unverified/
unknown outcomes. Upgrade only when actual evidence satisfies the relevant
contract. This edition never assigns `mechanically-checked` or `complete`,
nor `complete-for-selected-visible-events`.

Existing 0.7.x drafts and attestations are not silently rewritten, upgraded,
or certified. The evidence record shape is retained, but the new article
metadata is not claimed to pass the removed validator.

## Agent checklist

Use these as acceptance criteria, not a mandatory sequence of tool calls.
Check source support and privacy before persistence; confirm the saved result
through full readback. Reuse checks on unchanged content. After a correction,
recheck affected claims/files and cross-file dependencies instead of replaying
the entire checklist. Do not substitute field presence for actual inspection.
Keep detailed working review out of the article body.

| Check | Required inspection | Failure response |
| --- | --- | --- |
| Input and coverage | Exact selected source, all available requested pages, explicit gaps, honest source kind/coverage | Request supported input or narrow scope; never infer unseen turns |
| Structure | One selected template, one H1, ordered H2 sections, sequential Q/Step headings, no instructional leftovers | Correct draft; omit empty optional sections |
| Readability | Direct QA; exact UI actions or full commands; important impact up front; meaningful matching and result checks | Fill from permitted originals or block an unsafe/incomplete procedure |
| Companion shape | Valid JSON shape, schema version, required keys/types/enums, no duplicate keys/IDs, exact article basenames | Correct malformed/ambiguous records; report any unverified parsing limitation |
| Claim coverage | Every material answer, condition, command, check, cause, outcome, and diagram relation has a claim map and nearby source citation | Add supported mappings or remove/block unsupported claims |
| Original quotation | Inspect the actual original, then compare the short excerpt, companion text, and article quote exactly; identify redactions | Correct misquotes; never fabricate a matching companion |
| Locator and origin | Actual title/version/origin and precise safe locator agree in article and companion | Request missing source/location, not an invented reference |
| Entailment and scope | The cited passage supports this exact claim in this version/scope, not just the same topic | Qualify, remove, or block; true quotes do not rescue false claims |
| Chronology | Later corrections, meaningful failed checks, and contrary results are retained | Resolve by evidence or leave uncertainty explicit |
| Enrichment and outcomes | Added actions mapped, no inherited success, reported vs observed distinguished, mode honored | Correct labels; missing evidence cannot be fixed by stronger wording |
| Privacy | Inspect all text, JSON, filenames, URLs including decoded forms, code, captions, and labels for identities/credentials | Remove or visibly redact before persistence; stop if meaning is lost |
| Links and diagrams | Source anchors unique, IDs resolve, local files exist in this batch, no private/remote assets or active Mermaid | Fix links, simplify/omit diagram; do not fetch undeclared files |
| Delivery | Correct existing session parent, fresh create-only folder/files, complete readback, accurate saved/blocked/failed/deferred set | Repair local authoring/link issues; on write/access/integrity failure stop further writes and report exact subsets |

Use simple visible inline links and same-directory local basenames; no
traversal, device/absolute local links, hidden HTML, or undeclared file reads.
Check sibling fragments if used, or link to the file without a fragment.
Code blocks cannot supply visible source citations.

Use native JSON parsing or an approved scoped host operation when available.
Parsing verifies syntax only, not duplicate-key rejection, schema, privacy, or
semantic support unless those were actually checked. If unavailable, inspect the JSON
text against the schema and explicitly report that parsing was not machine
verified. Human/agent checks can miss duplicate keys, subtle misquotes, private
names, or omitted claims. Never report guaranteed redaction or deterministic
validation from this workflow.

Only after every applicable checklist item is checked, no required reference
gap remains, and saved content is read back may a delivered draft be described
as `checklist-checked`. If that metadata was updated, read back and recheck the
edited file too. Any unchecked item keeps references incomplete; material source
or privacy gaps block delivery of the affected article as a ready review draft.

## Independent review and publication

Generator self-review is not independent review. The engineer or a genuinely
separate reviewer must inspect every substantive claim, not merely the
generator-selected claim map, before relying on or distributing the draft.
Provide only de-identified files to an authorized reviewer, never raw sessions
or credentials. Do not launch paid review agents or a factory automatically.

The reviewer checks original authenticity, entailment, locator/version,
applicability, chronology, exact procedure inputs, execution evidence,
significant impact/rollback, privacy, diagram meaning, and delivery accuracy.
Qualified claims must carry their limitation in the article; unsupported claims,
unknown origins, misquotes, missing safety steps, and omitted claims require
changes.

This skill does not generate review attestations, authenticate reviewers, bind
reviews to cryptographic hashes, or automatically promote references to complete.
Any article/evidence edit invalidates prior review of that content; request
fresh review rather than reusing a stale approval. Keep final drafts pending
engineer review, even after the generator's checklist.

Independent review is distinct from explicit authorization to publish to a
defined audience. Neither local saving nor any checklist pass authorizes
publication, messaging, live-system changes, or executing the article's commands.
