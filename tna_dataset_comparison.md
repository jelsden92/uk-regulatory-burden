# TNA Statutory Powers & Duties Dataset — Comparison with this Project

**Date:** 2026-05-29
**Author note:** Honest assessment requested. This document is candid about overlap and what either project does that the other doesn't.

---

## 1. Inventory of the TNA dataset

The dataset is delivered as `duties.zip` containing 32 CSV files under `20260330/`, split by enactment type (and by ~150k-row parts for the largest types).

- **Total rows:** **1,841,827**
- **Generation:** stated by TNA contact as produced by Claude Sonnet 4.5 over UK in-force legislation
- **Schema (19 columns):**

| Column | Meaning |
|---|---|
| `dutyTempId`, `duty_uri` | Internal IDs |
| `enactment`, `enactmentTitle`, `enactmentYear`, `enactmentType`, `enactmentNum` | Source Act identification |
| `section`, `subsection` | Provision location |
| `actor` | Free-text actor name (e.g. "Secretary of State", "court", "company") |
| `actorIsBody` | Sparse — populated for ~19% of rows when the actor is a canonically named body |
| `actorIsAlias`, `actorDefinition` | Helpers for actor identification |
| `body_uri` | URI of the actor when it's a recognised legal entity |
| **`modality`** | **`duty` (58%) or `power` (42%)** |
| `action` | What the actor must / may do |
| `condition` | Triggering event, if any (filled in 70% of rows) |
| **`inference`** | **`explicit` (80%) or `implicit` (20%)** |
| **`priority`** | **`primary` (78%) or `secondary` (22%)** |

### Per-enactment-type row counts

| Type | Rows |
|---|---:|
| uksi | 778,608 |
| ukpga | 428,228 |
| eur | 149,646 |
| nisr | 118,537 |
| ssi | 82,010 |
| wsi | 63,511 |
| nisi | 57,098 |
| asp | 53,372 |
| eudn | 35,090 |
| nia | 17,892 |
| ukla | 15,087 |
| apni | 10,545 |
| anaw | 10,284 |
| ukcm | 8,029 |
| asc | 5,261 |
| EuropeanUnionDirective | 3,664 |
| mwa | 2,284 |
| aep | 1,551 |
| apgb | 375 |
| eudr | 361 |
| nisro | 192 |
| aip | 95 |
| aosp | 51 |
| ScottishAct | 45 |
| NorthernIrelandParliamentAct | 10 |
| mnia | 1 |
| **Total** | **1,841,827** |

Notice three legacy-format entries — `EuropeanUnionDirective` (3,664), `ScottishAct` (45), `NorthernIrelandParliamentAct` (10) — which appear to use older naming alongside the standard codes (`eudr`, `asp`, `apni`). The dataset hasn't been deduped against these.

---

## 2. Sample of 20 rows (full schema, abbreviated)

Selected at random across 6 leg_types to show what the data looks like.

| Type | Act | s. | actor | actorIsBody | modality | inference | priority | condition? |
|---|---|---|---|---|---|---|---|---|
| ukpga | Finance Act 2014 | 9 | Financial Services Authority | _empty_ | power | implicit | primary | yes |
| ukpga | Housing and Planning Act 2016 | 18 | court or tribunal | _empty_ | power | explicit | primary | yes |
| ukpga | Energy Act 2004 | 188 | Secretary of State | Secretary of State | duty | explicit | primary | no |
| ukpga | Proceeds of Crime Act 2002 | 97C | court | _empty_ | power | explicit | primary | yes |
| ukpga | Railways Act 2005 | 6 | Secretary of State | Secretary of State | duty | explicit | secondary | yes |
| uksi | Mallard Pass Solar Farm Order 2024 | 103 | Cadent Gas Limited | _empty_ | duty | explicit | primary | yes |
| uksi | Transfrontier Shipment of Radioactive Waste regs | 4 | competent authority of country of transit | _empty_ | power | implicit | primary | no |
| uksi | Invasive Alien Species (Enforcement) regs | 11 | regulator | _empty_ | duty | explicit | primary | yes |
| uksi | Cottam Solar Project Order 2024 | 119 | Network Rail | _empty_ | duty | explicit | primary | yes |
| uksi | Immingham Open Cycle Gas Turbine Order 2020 | 20 | developer | _empty_ | duty | explicit | primary | yes |
| eur | Comm Delegated Reg 523/2014 | 2 | institution | _empty_ | duty | implicit | primary | yes |
| eur | Comm Reg 965/2012 | j | operator | _empty_ | duty | explicit | secondary | yes |
| eur | Comm Reg 382/2005 | 3 | unspecified | _empty_ | duty | explicit | primary | yes |
| ssi | Cairngorms National Park Elections (Scotland) | 16 | any person | _empty_ | power | explicit | primary | yes |
| ssi | Stornoway Harbour Revision Order | 15 | Stornoway Harbour Authority | _empty_ | duty | explicit | primary | yes |
| ssi | FtT for Scotland Housing and Property Chamber | 19 | First-tier Tribunal | _empty_ | duty | explicit | primary | yes |
| ukla | Highgate Cemetery Act 2022 | 4 | burial authority | _empty_ | duty | explicit | primary | yes |
| ukla | Killingholme Generating Stations Act | 27 | appropriate company | _empty_ | duty | explicit | primary | yes |
| nisr | New Firefighters' Pension Scheme Order NI | 91 | Board | _empty_ | duty | explicit | primary | yes |
| nisr | Companies (NI) Bank Accounts Regs | 53 | company | _empty_ | duty | explicit | primary | yes |

Action and condition fields are full sentences — typically 100-300 chars. The classifications are sentence-level, not provision-level, so multiple TNA rows can come from a single section.

---

## 3. Does the dataset distinguish private actors from public bodies?

**Short answer: no, not directly.**

- `actorIsBody` is filled for only **18.9%** of rows (114,491 of 604,794 sampled) — and only when there's a canonical body URI to link to. Generic terms like "court", "regulator", "tribunal", "company" leave it blank.
- The `actor` column is **free text** and mixes public-body actors, private actors, and ambiguous categories in the same column. The top 40 values across the largest files:

| Rank | Actor (lowercased) | Count |
|---:|---|---:|
| 1 | undertaker | 46,593 |
| 2 | secretary of state | 42,680 |
| 3 | unspecified | 17,920 |
| 4 | scottish ministers | 11,477 |
| 5 | person | 10,226 |
| 6 | competent authority | 9,950 |
| 7 | court | 9,371 |
| 8 | applicant | 9,191 |
| 9 | local authority | 7,801 |
| 10 | commission | 7,658 |
| 11 | appropriate authority | 7,568 |
| 12 | operator | 6,558 |
| 13 | treasury | 5,768 |
| 14 | manufacturer | 5,614 |
| 15 | relevant authority | 5,287 |
| 16 | network rail | 5,156 |
| 17 | regulator | 4,713 |
| 18 | member state | 4,274 |
| 19 | ofcom | 3,918 |
| 20 | company | 3,601 |
| 21-40 | ... including hmrc, fca, caa, mmo, council, lord chancellor, scheme manager, administrator, tribunal, board, institution, authority, licensing authority, local planning authority, inspector, approval authority | |

This mixes:
- **Unambiguously public** — secretary of state, scottish ministers, court, treasury, hmrc, fca, ofcom, caa, mmo, regulator, ministers, lord chancellor, member state
- **Unambiguously private** — undertaker, applicant, operator, manufacturer, company, scheme manager (in some contexts)
- **Context-dependent** — local authority, competent authority, appropriate authority, board, institution, "person"

**There is no automated classification in the TNA dataset that lets a user filter to "duties on private actors" — the bedrock of regulatory-burden measurement.** Any user wanting that filter has to build their own on top.

A heuristic regex-based classifier (public-body markers + private-actor markers) applied to the 13 reference Acts gives this rough split, but it's lossy:

| | public | private | ambiguous | unspecified |
|---|---:|---:|---:|---:|
| Across 13 Acts | ~60% | ~25% | ~15% | <1% |

---

## 4. The three named Acts — TNA coverage

You named Bribery Act 2010, HSWA 1974, and ERA 1996. **None of these appear in `Reg Burden Project Validation.xlsx`** — the workbook contains 10 Acts, all different: Employers' Liability (Compulsory Insurance) Act 1969, Guard Dogs Act 1975, Late Payment of Commercial Debts (Interest) Act 1998, Noise Act 1996, Dangerous Dogs Act 1991, Christmas Day (Trading) Act 2004, Wild Mammals (Protection) Act 1996, Theft Act 1978, Corporate Manslaughter and Corporate Homicide Act 2007, Knives Act 1997.

For the three named Acts I extracted TNA's complete coverage but cannot compare against your manual workbook because the manual workbook doesn't have these Acts. The TNA numbers alone:

| Act | TNA rows | Duty | Power | Heuristic-Public | Heuristic-Private | Conditions filled | Mapped to user-style "private duty" |
|---|---:|---:|---:|---:|---:|---:|---:|
| **Bribery Act 2010** (ukpga/2010/23) | 44 | 20 | 24 | 23 | 13 | 24 | 7 |
| **HSWA 1974** (ukpga/1974/37) | 409 | 160 | 249 | 232 | 46 | 283 | 34 |
| **ERA 1996** (ukpga/1996/18) | 1,181 | 652 | 529 | 585 | 528 | 918 | 324 |

When the user-style filter (modality=duty AND actor=private) is applied, the per-Act counts collapse substantially — for HSWA from 409 → 34, and for Bribery from 44 → 7. ERA holds up better at 324 because it has many provisions framed as duties on employers.

If you want a Bribery/HSWA/ERA comparison against ground truth, **you'd need to add those Acts to the validation workbook** with line-by-line direct/implied/conditional classifications.

---

## 5. Comparison against the 10 workbook Acts

Where I do have ground truth, the picture is more interesting. Workbook counts vs TNA-mapped-to-user-taxonomy:

| Act | WB direct | WB implied | WB cond | **WB total** | TNA-PrivD | TNA-Direct | TNA-Implied | TNA-Cond |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Employers Liability 1969 | 1 | 2 | 1 | **4** | 5 | 0 | 0 | 5 |
| Guard Dogs 1975 | 3 | 0 | 0 | **3** | 6 | 1 | 0 | 5 |
| Late Payment 1998 | 8 | 0 | 0 | **9** | 1 | 0 | 0 | 1 |
| Noise 1996 | 0 | 0 | 1 | **1** | 6 | 2 | 0 | 4 |
| Dangerous Dogs 1991 | 5 | 0 | 1 | **6** | 15 | 3 | 0 | 12 |
| Christmas Day 2004 | 2 | 0 | 0 | **2** | 2 | 0 | 0 | 2 |
| Wild Mammals 1996 | 1 | 2 | 2 | **5** | 0 | 0 | 0 | 0 |
| Theft 1978 | 1 | 0 | 0 | **1** | 0 | 0 | 0 | 0 |
| Corp Manslaughter 2007 | 1 | 0 | 2 | **3** | 4 | 0 | 0 | 4 |
| Knives 1997 | 2 | 5 | 2 | **9** | 2 | 0 | 0 | 2 |

**Critical observations from section-level matching:**

- **Section-level overlap on workbook entries: 22/43 matched** (the unmatched are mostly workbook rows with no section number recorded, or Acts where TNA structures provisions differently).
- For sections both sides cover, **TNA decomposes more granularly**: e.g. Dangerous Dogs s.1(2) appears once per sub-paragraph in the workbook (5 entries) but 16 times in TNA per sub-paragraph (TNA captures every implied sub-action).
- **TNA misses offence-as-obligation provisions consistently**:
  - Theft Act 1978 s.3(1) "making off without payment" — workbook captures as direct burden; TNA has 0 rows
  - Wild Mammals 1996 s.1 the basic cruelty prohibition — workbook captures as direct burden; TNA has 0 rows
  - Knives Act 1997 s.1(1) marketing offence — workbook captures as direct; TNA has 0 rows
  - Corporate Manslaughter 2007 s.1(1) the central offence — workbook captures as direct; TNA has 0 rows
- **TNA's "condition" field is over-populated relative to the project's "conditional obligation" category.** TNA marks `condition` for any structural "if X then Y" framing (70% of rows), whereas the project's "conditional obligation" is a narrower category for genuine triggering events (enforcement notices, licence conditions, regulator-initiated actions). The TNA-mapped-Cond column above heavily overstates true conditional burdens.
- **Late Payment 1998 has only 22 TNA rows total** (of which 12 are duties) — but the workbook has 9 manual entries identifying contract-void rules. This Act's burden flows from contract-voiding implied terms, which TNA seems to under-capture.

The pattern is consistent: **TNA captures structural duties well but undercounts prohibition-style obligations (= offences), and overcounts conditional duties by treating structural conditionals as enforcement-triggered.**

---

## 6. Assessment

### 6a. How much overlap is there?

**Substantial — TNA is solving an overlapping problem with a similar scaffold.** The five fields `modality`, `actor`, `condition`, `inference`, `priority` together come close to the project's `(actor=private/public, type=direct/implied/conditional)` taxonomy. If you had to retrofit the project's classifications onto the TNA data, you could do most of it from these five fields plus a public/private actor classifier.

Concretely: if you took TNA's data and applied (a) modality=duty filter (b) public/private actor classifier (c) condition-presence flag → you'd reproduce most of the project's per-Act counts. The published TNA dataset would, by itself, be enough for a directionally correct stock-and-flow measure of regulatory burden — once you bolt on the public/private classifier.

### 6b. What the project still adds that TNA doesn't

1. **Private/public actor classification baked in.** TNA's `actor` is free text; classifying it correctly is the entire methodological core of any "regulatory burden" measure. The project does this; TNA does not.
2. **Penalty-as-consequence rule.** TNA appears to enumerate every "must" clause without explicitly handling penalty provisions as consequences of the underlying obligation. The project does — preventing double-counting of "X is an offence; the penalty is Y".
3. **Offence-as-obligation capture.** TNA undercounts prohibition-style obligations (no offence-creating provisions for Theft Act s.3, Knives Act s.1, Wild Mammals s.1, Corp Manslaughter s.1). The project explicitly counts these as direct burdens.
4. **Tight definition of "conditional obligation".** The project distinguishes structural conditionals (if/then statutory framing) from genuine conditional obligations (triggered by external regulatory action — enforcement notices, licences, inspections). TNA conflates these in its `condition` field.
5. **The "regulatory burden" framing.** TNA's project is neutral — it enumerates powers AND duties of every actor, suitable for ontology-building. The project is explicitly oriented to measure compliance cost on non-governmental actors. This is a framing choice that has methodological consequences (which the project documents explicitly via the methodology note).
6. **Devolution-aware decomposition.** The project tracks E&W vs Scotland vs NI counts separately and exposes a fragmentation premium. TNA's dataset has the structural fields but doesn't surface this.
7. **Cross-validated against a manual workbook.** The project has a paradigm-case validation workbook with 10 Acts manually classified. TNA's dataset has no published accuracy assessment that I've seen.

### 6c. What should change in methodology or framing now that TNA's dataset exists?

These recommendations are anchored to `project_objective_anchor.md`: the project's core aim is a private-actor-focused, manually-validated, sentence-level measure of regulatory burden. That anchor governs everything below.

1. **TNA's dataset is a cross-check validation input, not a substitute for the extraction pipeline.** The project's own corpus → classifier → six-category taxonomy pipeline is what produces the headline measure. TNA's rows are most useful as a *second-opinion attribution* against which our `private_actor` / `public_body` classifications can be cross-referenced — exactly the role formalised in `tna_crosscheck_methodology.md`. Replacing the pipeline with TNA's data would drop the public/private classifier (commitment #1), the penalty-as-consequence rule (§3.1), the offence-as-obligation capture, and the tight conditional-obligation definition (§3.2). All four are distinctive contributions and all four would be lost.

2. **The project remains the first comprehensive measure of UK regulatory burden — TNA's dataset is a different artefact.** "Regulatory burden" in the project's terminology is, by definition, the compliance cost imposed on private actors by legally binding obligations and prohibitions (per `project_objective_anchor.md`). TNA's *Statutory Powers and Duties Dataset* enumerates duties and powers of every actor — public and private — without filtering for burden. The two artefacts cover overlapping legislation but answer different questions:
   - TNA: *What duties and powers does the statute book contain, and on whom?*
   - Project: *How much regulatory burden — defined as direct + implied + conditional obligations on private actors — does the statute book impose?*
   - The project's headline claim ("first comprehensive measure of prescriptive regulatory burden in UK legislation") stands. TNA's prior work doesn't compete with that claim because TNA's dataset is not a burden measure. The README and methodology preamble can be cited as-is.

3. **Add Bribery 2010, HSWA 1974, ERA 1996 to the manual validation workbook.** You referenced them as validated, but they're not in the workbook. Either expand the workbook to include them (so the next comparison is real) or correct the project's claims about which Acts have been manually validated. This serves commitment #3 directly.

4. **Acknowledge TNA's prior work in the README and methodology.** The credibility of the project goes up, not down, if you cite TNA's dataset, show the comparison transparently, and explain exactly what the project adds on top. The acknowledgement is already drafted in `docs/methodology.md §9`; ensure the README reflects the same framing when ready for publication.

5. **Keep the corpus exhaustion sweep running.** It tests whether legislation.gov.uk's machine-readable holdings are exhaustively in the corpus — a question about corpus completeness, not about classification. The sweep advances commitment #1 (comprehensive statute-book coverage) and is independent of TNA's classification work. Do not kill it on the grounds that TNA has done extraction; the two answer different questions.

6. **Use the TNA cross-check as an additional validation layer.** Section-level disagreement (project flags `private_actor`, TNA records a clearly-public-body actor at the same section) becomes a candidate false positive feeding back into classifier refinement. This is now operational via `_tna_crosscheck.py` and is documented in `tna_crosscheck_methodology.md` and in `docs/methodology.md §9`.

### Closing line

The TNA dataset does not displace the project. It complements it: TNA enumerates duties and powers; the project measures regulatory burden on private actors specifically. The project's headline output — *the count of legally binding obligations and prohibitions on private actors* — is exactly the question TNA's dataset doesn't directly answer, and the four methodological commitments in `project_objective_anchor.md` are the reason it can.

---

## Reproducibility

| Artefact | Purpose |
|---|---|
| `_tna_analysis.py` | Heuristic public/private classifier + workbook comparison |
| `_tna_extracted.json` | TNA rows for 13 reference Acts |
| `_tna_analysis.json` | Per-Act summaries and workbook ground-truth counts |
| `_tna_analysis.log` | Console output of the analysis script |
| `20260330/` | Raw extracted TNA CSVs (1.8M rows total) |
| `Reg Burden Project Validation.xlsx` | Project manual ground-truth workbook (10 Acts, 43 rows) |
