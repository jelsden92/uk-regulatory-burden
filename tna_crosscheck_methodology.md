# TNA Cross-Check — Validation Methodology

This document defines an additional validation layer for the project's classifier: a section-level cross-reference of `private_actor` classifications against The National Archives' *Statutory Powers and Duties Dataset*. Where TNA records a clearly-public-body actor at the same section, the project's classification is flagged as a **candidate false positive** for manual review.

The layer is documented as part of §9 of `docs/methodology.md`.

---

## 1. Purpose

The classifier resolves sentence subjects to one of `private_actor`, `public_body`, or `ambiguous`. Errors in this resolution directly inflate or deflate the regulatory-burden measure. The TNA dataset offers a second LLM-derived attribution of the *same* corpus, with a free-text `actor` field that — once filtered to clearly-public-body actors — provides an external check on the project's classifications. The check is one-directional and conservative: it does not validate that TNA's classifications are correct, only that **disagreement at the section level is a strong signal worth a human eye**.

## 2. Scope

- The check runs over the **13-Act benchmark suite** (`_run_13act_benchmark.py`).
- For each Act, only sentences classified as `private_actor` are tested.
- Sentences classified as `public_body`, `ambiguous`, `implied_burden`, `conditional_burden`, etc. are out of scope for this particular check.

## 3. Strict public-body actor whitelist

A TNA row only triggers a flag when its `actor` field matches one of the following regexes (case-insensitive, word-boundary anchored):

| Term | Notes |
|---|---|
| secretary of state | Crown minister |
| court / courts | Judicial body |
| regulator | Generic statutory regulator |
| constable | Police officer |
| minister / ministers | Crown / devolved minister |
| justice of the peace | Magistrate |
| registrar | Court / Companies House etc. |
| tribunal | Judicial body |
| judge | Judicial officer |
| sheriff | Scottish judicial officer |
| Lord Chancellor | Crown officer |
| the Treasury | HM Treasury |
| HMRC, Her Majesty's Revenue | Tax authority |
| commissioner / commissioners | Statutory commissioners |
| police | Police force |
| Attorney General | Crown law officer |
| Crown Court | Judicial body |

Any TNA row whose `actor` matches one of these strict markers is treated as a clearly-public-body row. Generic terms like "authority", "board", "competent authority" are deliberately excluded — they are too context-dependent.

## 4. Matching logic — two complementary heuristics

A single match method has blind spots, so the check uses two heuristics in parallel. A sentence flagged by **either** heuristic is reported.

### Heuristic (a) — section-prefix extraction

Many of the project's extracted sentences carry the parsed section/subsection number as a leading token (e.g. `"2 1 It shall be the duty of every employer to ensure..."` is section 2, subsection 1). When extractable:

1. Regex `^\s*(\d+)(?:\s+(\d+))?\s+` against the sentence text → `(section, subsection)`.
2. Parse TNA's section URI (e.g. `/section/2/1/a` → `("2", "1")`).
3. If the section number matches **any** strict-public-body TNA row in that Act, flag the sentence.

### Heuristic (b) — content-word overlap

Many sentences have no extractable section prefix (extractor noise, definitional preludes, or sentences mid-section). For these:

1. Tokenize TNA `action` and the user sentence to lowercased content words (no stopwords; words ≥ 3 chars).
2. Compute the intersection of content-word sets.
3. Match if the intersection covers **≥ 60 %** of TNA's action content words **AND** the absolute overlap is **≥ 4 words**.

A cap of 3 candidates per TNA row prevents combinatorial blow-up on the largest Acts.

## 5. Output

The cross-check produces:

- `_tna_crosscheck_candidates.csv` — one row per candidate FP, columns: `bench_path`, `sentence_id`, `match_type`, `matched_word`, `is_in_schedule`, `tna_section`, `tna_modality`, `tna_actors_in_section`, `tna_action_example`, `sentence_text`.
- `_tna_crosscheck_candidates.json` — full structured output including per-Act summary counts.
- `_tna_crosscheck.log` — console output of the run.

## 6. Headline figures (run 2026-05-29)

Across the 13-Act benchmark:

| Act | user_PA | TNA_rows | TNA_strict_pub | matched_a | matched_b | unique_flagged |
|---|---:|---:|---:|---:|---:|---:|
| ukpga/2000/8 (FSMA) | 484 | 5,325 | 1,638 | 4 | 147 | 151 |
| ukpga/1996/18 (ERA) | 279 | 1,181 | 525 | 17 | 76 | 93 |
| ukpga/2010/15 (Equality) | 177 | 854 | 313 | 40 | 14 | 54 |
| eur/2016/679 (UK GDPR) | 126 | 338 | 129 | 0 | 38 | 38 |
| asp/2003/2 (Land Reform) | 102 | 1,053 | 394 | 11 | 52 | 63 |
| ukpga/1998/47 (NI Act) | 153 | 1,146 | 454 | 38 | 23 | 61 |
| ukpga/1974/37 (HSW) | 69 | 409 | 123 | 10 | 6 | 16 |
| ukpga/1998/41 (Competition) | 62 | 553 | 161 | 11 | 6 | 17 |
| uksi/2016/1154 (Env Permitting) | 82 | 886 | 321 | 0 | 15 | 15 |
| ukpga/1875/17 (Explosives) | 8 | 0 | 0 | 0 | 0 | 0 |
| ukpga/2010/23 (Bribery) | 7 | 44 | 13 | 0 | 0 | 0 |
| ukpga/1957/31 (Occupiers' Liab.) | 4 | 0 | 0 | 0 | 0 | 0 |
| wsi/2024/388 (Special Schools Wales) | 144 | 395 | 29 | 0 | 7 | 7 |
| **Total** | **1,697** | | | **131** | **384** | **515** |

**Flag rate: 30.3 % of `private_actor` classifications in the benchmark are candidate false positives.**

Two benchmark Acts (Explosives 1875, Occupiers' Liability 1957) have zero TNA rows — likely below TNA's primary-modality threshold or an extraction omission — so they generate no candidates by construction.

## 7. Interpretation

A 30 % flag rate is high enough to motivate classifier refinement but not so high as to invalidate the corpus measure. Each candidate is **not** an automatic false positive — the cross-check surfaces *disagreements*, and manual review will resolve some in the project's favour and some in TNA's. Typical surface patterns observed in the initial run:

- **Tribunal / court action mis-attributed to private actor.** The project's three-tier subject default sometimes picks up the private actor mentioned earlier in a sentence (e.g. "the employer") and attributes the prescriptive verb to them, when the verb actually governs the tribunal's order or the court's discretion.
- **Secretary of State decisions wrapped in private-actor framing.** Sentences of the form "Where a relevant officer has been … appointed in connection with an employer's insolvency, the Secretary of State shall not make a payment…" are correctly attributed by TNA to the Secretary of State; the project's classifier sometimes picks up "employer" as the subject because it appears first.
- **Amendment-insertion sentences.** Some `private_actor` flags come from amendment text (`"after the words 'subsection (1)(b)' there shall be inserted…"`) where the verb is a drafting instruction, not a duty. These already feed into the `amendment_insertion_text` column but a small number leak through. They are valid candidate FPs.

## 8. Workflow

1. Run `_tna_crosscheck.py`. Output: `_tna_crosscheck_candidates.csv`.
2. Reviewer opens the CSV and manually classifies each candidate as:
   - **Confirmed FP** — the project misclassified; classifier rule needs adjustment.
   - **Not FP — sentence is genuinely about a private actor**, TNA disagrees but is wrong.
   - **Not FP — sentence is mixed** (some private + some public attribution in the same sentence).
3. Confirmed FPs are aggregated and fed back into either (a) `word_list.py` vocabulary refinement or (b) `analyser.classify_subject_spacy` rule changes.
4. After each refinement, re-run the cross-check and report the change in flag rate.

## 9. Limitations of this cross-check

- **Relies on TNA's own accuracy.** If TNA misclassifies an actor, this layer will surface a false-positive flag (a "candidate FP" that on review is actually a true positive in the project). The mitigation is human-in-the-loop review; the cross-check is a candidate generator, not an oracle.
- **Section-prefix extraction is fragile.** Sentences that don't carry a leading section number escape heuristic (a). Heuristic (b) catches many of these but text-overlap matching has its own noise floor.
- **The strict whitelist is narrow by design.** Public-body terms like "authority", "board", "agency", "council", "ministers" (lowercase, generic) are excluded to keep the FP-of-the-FP-check low. This means some legitimate public-body attributions in TNA will not trigger a flag here. A broader whitelist could be defined as a separate, less-strict layer.
- **Acts with no TNA rows are out of scope.** The two affected benchmark Acts (Explosives 1875, Occupiers' Liability 1957) need a separate validation method.

## 10. Reproducibility

| Artefact | Purpose |
|---|---|
| `_tna_crosscheck.py` | The cross-check script |
| `_tna_crosscheck_candidates.csv` | Flat list of candidate FPs |
| `_tna_crosscheck_candidates.json` | Structured candidates + per-Act summary |
| `_tna_crosscheck.log` | Console output of the run |
| `_tna_extracted.json` | TNA rows for all 13 benchmark Acts |
| `tna_dataset_comparison.md` | Broader TNA-vs-project comparison report |
