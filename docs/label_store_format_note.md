# Label Store — Record Format Note (v1.0)

**Purpose.** This note defines the on-disk format for the UK Regulatory Burden label
store. It is the single source all three labellers (Jethro, Claude, Gemini) emit from,
so that every proposal file has an **identical shape** and set-vs-set agreement can be
computed mechanically. It is a **schema, not tooling** — there is no queue software; a
"lane" is simply a `review_reason`-sorted view of records.

This note is docs-side and may be published. **No label data — proposal files,
adjudications, gold — is ever pushed to a public remote** (see the `.gitignore` moat).

Rubric of record: **`v1.0`** (`docs/validation_rubric.md`). Category IDs are canonical per
`category_mapping.md`.

---

## 1. The record model

Format: **leaf-anchored burden-set JSONL.** One line = one JSON object = **one
labeller's pass over one section** (a "record set"). The section is keyed by its
**qualified section identity**; each set carries a `burdens[]` array and an
`exclusions[]` array. A section with no burden is stored as one or more first-class
**typed exclusions**, never as an empty set.

```
{ section: {…}, burdens: [ … ], exclusions: [ … ], labeller_id, rubric_version, timestamp }
```

DOM-identity discipline: the **`id`** (and `section_index`) is the authoritative key;
`section_ref` and every leaf `ref` are **display-only** (they are not unique — e.g.
`24(1)` maps to five distinct provisions across one instrument, and `17(10)` repeats
within a single section).

### 1.1 `section` (identity block)

| field | type | notes |
|---|---|---|
| `id` | string | DOM identity, authoritative — e.g. `uksi/2016/1154#s30#d1dd6ac5a3e5` |
| `title` | string | e.g. `Environmental Permitting (E&W) Regs 2016` |
| `section_ref` | string | **display only** — e.g. `24`, `Article 30`, `27BA` |
| `section_index` | int | DOM index within the parent document (identity component) |

### 1.2 Record-set stamp (line level)

Every record in the set inherits these; they are stamped once per line.

| field | type | allowed / notes |
|---|---|---|
| `labeller_id` | string | `jethro` \| `claude` \| `gemini` (\| `gold` in `gold.jsonl`; adjudicator id in `adjudication.jsonl`) |
| `rubric_version` | string | `"v1.0"` |
| `timestamp` | string | ISO-8601 with UK offset, e.g. `2026-07-20T14:30:00+01:00` |

---

## 2. Burden record (`burdens[]`)

One record per **distinct** burden the section imposes. Fold particulars into their
general duty; split genuinely independent constraints (rubric §7).

| field | type | allowed values / notes |
|---|---|---|
| `burden_id` | string | set-local id, e.g. `b1`, `b2` (stable within the line) |
| `leaves` | array | leaf anchors — see §5. Chapeau-level anchoring permitted. |
| `category_id` | int | **1–6, canonical** (`category_mapping.md`) — the authoritative field |
| `category_tag` | string | presentational echo of the id (see crosswalk below) |
| `polarity` | string | `obligation` \| `prohibition` \| `review` |
| `obligated_party` | string | who bears it, as named in the provision (e.g. `the operator (permit holder)`) |
| `actor_capacity` | string | `economic` \| `personal` \| `both_either` \| `ambiguous` (rubric §1) |
| `introduced_by` | string \| null | amending instrument that inserted the provision; `null` if original / residence provision |
| `introduced_year` | int \| null | year of `introduced_by`; `null` if not applicable |
| `frontier_hook` | bool | `true` iff counted as a frontier proxy for an out-of-measure layer (rubric §3) |
| `frontier_target_type` | string \| null | `permit_licence` \| `notice` \| `byelaw` \| `regulator_rulebook` \| `other`; `null` when `frontier_hook=false` |
| `orphan` | bool | `true` iff the record came through the orphan-triage lane |
| `unapplied_amendment` | bool | `true` iff the payload is an enacted-but-unapplied pending insertion |
| `review_reason` | object \| null | see §4; `null` when not routed to review |
| `feeds` | array | see §4; `[]` in proposal files (recorded at resolution) |

**Category crosswalk** (id is canonical / rename-proof; tag and name are presentational):

| `category_id` | `category_tag` | presentational name (`category_mapping.md`) |
|---|---|---|
| 1 | `direct` | Direct burden |
| 2 | `conditional_direct` | Conditional burden (operational) |
| 3 | `implied_burden` | Implied burden (IB) |
| 4 | `implied_burden_active` | Implied burden active (IBA) |
| 5 | `conditional_burden` | Conditional burden (regulator-triggered) |
| 6 | `ambiguous` | Ambiguous |

---

## 3. Exclusion record (`exclusions[]`)

One record per span of the section that carries **no countable private-actor burden**.

| field | type | allowed values / notes |
|---|---|---|
| `leaves` | array | leaf anchors — see §5 |
| `exclusion_family` | string | `non_operative` \| `counted_at_source` \| `public_body_or_no_one` \| `structural` |
| `exclusion_subclass` | string | best-effort fine-grained label; `mixed_other` available as catch-all |
| `review_reason` | object \| null | see §4; `null` when not routed |
| `feeds` | array | see §4; `[]` in proposal files |

Dual-model exclusion agreement is computed on **`exclusion_family` only**; sub-class
mismatches within an agreed family are logged, not adjudicated.

**Exclusion sub-classes** (best-effort; `mixed_other` available in any family). The four
families are the load-bearing joint (exclusion taxonomy v2, ratified 2026-07-20):
`structural` = *operative-but-not-a-burden* (distinct from `public_body_or_no_one` =
*binds-no-one*); `amendment_machinery` sits under `counted_at_source` because the rule is
count-at-consolidated-target.

| family | sub-classes |
|---|---|
| `non_operative` | `deeming`, `definitional`, `machinery_procedural`, `powers_to_make_secondary`, `scheme_machinery`, `list_of_contents` |
| `counted_at_source` | `cross_reference`, `compliance_hook`, `enabling_power`, `penalty_as_consequence`, `amendment_machinery`, `secondary_offence_reference` |
| `public_body_or_no_one` | e.g. `public_body_duty`, `regulator_duty`, `no_addressee` |
| `structural` | `bare_permission`, `scope_eligibility`, `condition_factor_list`, `single_act_specification`, `procedural_right_v_state`, `liability_attribution`, `burden_removal` |

---

## 4. Review-routing fields

Present on any burden or exclusion record. `review_reason` is set by the labeller (or by
disagreement detection); `feeds` is populated **at resolution** (i.e. in
`adjudication.jsonl` / `gold.jsonl`, `[]` in the raw proposal files).

`review_reason` = `{ "primary": <value>, "secondary": <value> | null }` — primary is the
route that fired first in tree order.

| `review_reason` value | when |
|---|---|
| `model_disagreement` | labellers diverge (set count or per-record labels) |
| `hybrid_actor` | "person exercising public functions" / relevant-person ambiguity |
| `ambiguous_leaf` | a leaf straddles categories |
| `cat6_category` | classified Ambiguous (category 6) |
| `polarity_review` | polarity genuinely unresolved after the operative-requirement rule |
| `orphan_escalation` | orphan-lane record needing a human eye |
| `context_term` | resolution needs a defined term / context not in the served candidate |

(`low_confidence` and `family_link` are reserved for the production / Legal-BERT phase.)

`feeds` ∈ `registry` \| `rubric_example` \| `unit_rule_evidence` \| `training_data` \|
`definitions` (array; a record may feed more than one).

---

## 5. Leaf anchoring

A leaf anchor is an array of `{ "leaf": <int>, "ref": <string> }` objects.

- `leaf` — the **0-based index** into the section's served `leaves[]`. This is the
  authoritative anchor (leaf `ref` is not unique within a section).
- `ref` — display echo of that leaf's ref, for human readability only.
- **Chapeau-level anchoring** (per the Layer-1 work): anchor the burden to the chapeau
  leaf's index alone; folded particulars are implied and need not be listed.
- **Whole-section anchor:** `"leaves": []` — used when the section has no leaves
  (`n_leaves = 0`) or the burden genuinely attaches at section level.

---

## 6. Files

All under `label_store/`, version-controlled locally, **never pushed to a public remote.**

| file | shape | role |
|---|---|---|
| `labels_jethro.jsonl` | record-sets (§1) | Jethro's independent proposals |
| `labels_claude.jsonl` | record-sets (§1) | Claude's independent proposals |
| `labels_gemini.jsonl` | record-sets (§1) | Gemini's independent proposals |
| `adjudication.jsonl` | adjudication records (§6.1) | divergence + argument + ruling + feeds |
| `gold.jsonl` | record-sets (§1), `labeller_id: "gold"` | settled truth: agreement ∪ rulings |

### 6.1 `adjudication.jsonl` record

```
{
  "section":   { id, title, section_ref, section_index },
  "locus":     { "kind": "burden" | "exclusion", "leaves": [ … ], "proposal_ref": "b1" },
  "divergence": "<review_reason.primary that triggered>",
  "proposals": { "jethro": { …record… }, "claude": { … }, "gemini": { … } },
  "argument_summary": "<free text: the competing readings and why>",
  "ruling":    { …the settled burden/exclusion record… },
  "feeds":     [ "rubric_example", "training_data" ],
  "labeller_id": "<adjudicator>", "rubric_version": "v1.0", "timestamp": "…"
}
```

`gold.jsonl` is derived: sections where all labellers agree are copied through; sections
with a divergence take the `ruling` from `adjudication.jsonl`. Same record-set shape as a
labels file, stamped `labeller_id: "gold"`.

---

## 7. Worked example (one record)

A single `labels_*.jsonl` line for **EPR (E&W) Regs 2016, reg 24** (`section_index` 30) —
a dry-run section, chosen only to fix the *shape*. This is **illustrative of shape, not a
gold label.** Leaf indices are the 0-based positions in that section's served `leaves[]`
(`12` = `24(3)` chapeau; `11` = `24(2)`; `20` = `24(6)` chapeau).

```json
{
  "section": {
    "id": "uksi/2016/1154#s30#d1dd6ac5a3e5",
    "title": "Environmental Permitting (E&W) Regs 2016",
    "section_ref": "24",
    "section_index": 30
  },
  "burdens": [
    {
      "burden_id": "b1",
      "leaves": [ { "leaf": 12, "ref": "24(3)" } ],
      "category_id": 2,
      "category_tag": "conditional_direct",
      "polarity": "obligation",
      "obligated_party": "the operator (permit holder)",
      "actor_capacity": "economic",
      "introduced_by": null,
      "introduced_year": null,
      "frontier_hook": false,
      "frontier_target_type": null,
      "orphan": false,
      "unapplied_amendment": false,
      "review_reason": null,
      "feeds": []
    }
  ],
  "exclusions": [
    {
      "leaves": [ { "leaf": 11, "ref": "24(2)" } ],
      "exclusion_family": "non_operative",
      "exclusion_subclass": "permissive_power",
      "review_reason": null,
      "feeds": []
    },
    {
      "leaves": [ { "leaf": 20, "ref": "24(6)" } ],
      "exclusion_family": "public_body_or_no_one",
      "exclusion_subclass": "regulator_duty",
      "review_reason": null,
      "feeds": []
    }
  ],
  "labeller_id": "jethro",
  "rubric_version": "v1.0",
  "timestamp": "2026-07-20T14:30:00+01:00"
}
```

A record routed to review differs only in the routing fields, e.g. on a burden:

```json
"review_reason": { "primary": "ambiguous_leaf", "secondary": "polarity_review" },
"feeds": []
```
