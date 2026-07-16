# Coverage methodology note

**Headline corpus figure: 69,885 fully digitised pieces of in-force UK legislation** — every item that legislation.gov.uk currently exposes with substantive machine-readable CLML body content (`NumberOfProvisions > 0`, `full_text >= 200` chars). This is the analyser input. (Up from 69,462 after ingesting **423 net-new recoverable items** surfaced by the completed API-exhaustion sweep — see "Exhaustion sweep" below.)

Within the wider National Archives in-force universe of **119,841 catalogued items**, the remaining **49,956-item difference** is structural — overwhelmingly local/private Acts and pre-modern instruments held only as PDF scans (Tier 2 / Tier 3 below). The picture depends on which scope of the statute book is in view:

## Scope-stratified coverage

The full-universe 58.3 % coverage figure conflates two structurally different populations: (i) general-application legislation — Public Acts, Statutory Instruments, devolved primary and secondary law — which is essentially fully digitised, and (ii) local and private Acts — bespoke statutes addressed to named persons, places or companies — which have historically been published only as PDF scans. Reporting a single ratio masks this. The three scopes below disentangle them:

| Scope | Description | In-force universe | In corpus w/ text | Coverage |
|---|---|---:|---:|---:|
| **A — Full universe** | Every in-force item across all 28 leg_types | 119,841 | 69,885 | **58.3 %** |
| **B — General application** | Excludes ukla / ukppa / gbppa / eppa / gbla / uklp (Local + Private + Personal Acts) | 89,548 | 69,695 | **77.8 %** |
| **C — Post-1990 general application** | Scope B AND year ≥ 1990 (modern regulatory law) | 67,403 | 61,745 | **91.6 %** |

The 91.6 % figure for modern general-application law is the most directly relevant denominator for any analysis of contemporary regulatory burden. The 58.3 % full-universe figure is included for completeness and so the structural composition of the gap can be inspected directly. (The Scope B and C corpus numerators — 69,695 and 61,745 — are lower than the 69,885 headline because they exclude the 190 texted local/private-Act items, which fall outside a general-application denominator by nature.)

## Three-tier structural breakdown (Scope A)

These are **exhaustive per-item counts** from the completed API-exhaustion sweep (every
in-force item with a coverage gap probed across all retrieval channels; see "Exhaustion
sweep" below), not extrapolations.

| Tier | Description | Items |
|---|---|---:|
| **Tier 1 — Fully digitised (corpus headline)** | Substantive machine-readable CLML; in corpus and analyser-ready | **69,885** |
| Tier 2 — Digitised but no analyser-usable text | On legislation.gov.uk but PDF-only / `NumberOfProvisions = 0` / Akoma-Ntoso-only — `data.xml` yields no CLML body | 31,407 |
| Tier 3 — Not digitised | `/data.xml` (and all channels) return HTTP 404; catalogued but no record on legislation.gov.uk | 18,505 |
| Pre-modern name-slug Acts (counted in Tier 1) | In corpus under chapter-coded URIs; catalogued under slug IDs — see "Pre-modern identifier reconciliation" | 44 |
| **In-force universe (catalogued)** | National Archives InForce CSV manifests (`_inforce_definitive_count.py`) | **119,841** |

Tiers reconcile to the universe: 69,885 + 31,407 + 18,505 + 44 = **119,841**. **Tier 2 =
31,407 = 29,872 + 1,535** — the same set of items counted two ways: 29,872 metadata-only/
PDF shells (the `shell` verdict in the exhaustion-sweep table below) plus 1,535 items that
are digitised but not CLML-ingestable (Akoma-Ntoso/PDF-only, deferred to phase 2). The
29,872 reported in the sweep table is therefore the shell component of this same Tier 2,
not a competing total.

`legislation.db` total rows: 218,089. Rows flagged `na_inforce = 1`: 85,358 (of which
69,885 carry `length(full_text) >= 200` and so enter the analyser; the remaining 15,473
are in-DB shells retained for amendment-chain tracking). The wider Tier-2 figure (31,407)
counts all digitised-but-empty in-force items, most of which are not held in the DB.

## In-force universe by decade

The in-force statute book has a long pre-modern tail. Counting the full National Archives in-force universe (the manifest denominator, not just the items held in `legislation.db`), only ~56 % of in-force items date from 1990 onward, and the pre-1900 universe alone is 25,842 items — overwhelmingly local/private and pre-modern Acts surviving only as PDF scans. The analyser-ready **Tier-1 corpus**, by contrast, *is* overwhelmingly modern: ~89 % of it dates from 1990 onward and the 2000s and 2010s alone account for ~56 % of it, precisely because digitisation coverage rises sharply at the 1990 Statute Law Database base date (below). The table sets the in-force universe against the Tier-1 corpus (`na_inforce = 1 AND full_text >= 200`); the coverage column is the universe-based ratio and reconciles to the "All types" column of the per-type matrix that follows.

| Decade | In-force universe | In Tier-1 corpus | Coverage |
|---|---:|---:|---:|
| pre-1900 | 25,842 | 724 | 3% |
| 1900s | 2,087 | 48 | 2% |
| 1910s | 1,322 | 57 | 4% |
| 1920s | 1,431 | 99 | 7% |
| 1930s | 1,493 | 97 | 6% |
| 1940s | 1,037 | 198 | 19% |
| 1950s | 1,591 | 396 | 25% |
| 1960s | 2,972 | 743 | 25% |
| 1970s | 5,918 | 1,534 | 26% |
| 1980s | 8,528 | 4,065 | 48% |
| 1990s | 16,797 | 14,207 | 85% |
| 2000s | 21,213 | 19,876 | 94% |
| 2010s | 20,455 | 19,237 | 94% |
| 2020s | 9,149 | 8,604 | 94% |
| **Total** | **119,835** | **69,885** | **58%** |

Coverage rises sharply at ~1990 (3–26 % for pre-1980 decades vs 85–94 % from the 1990s on). This is the Statute Law Database baseline effect: older in-force items (those carried into the revised dataset at the 1 February 1991 base date — see "Definitional rule" below) are disproportionately held as PDF-only or `NumberOfProvisions = 0` shells without machine-readable CLML, so they are catalogued as in force but lack analyser-usable text. The universe totals 119,835 here rather than 119,841 because six in-force items carry a blank or unparseable year and fall into no decade bucket. Of the 119,841 in-force items, 85,358 are held in `legislation.db` — of which 69,885 carry substantive text (the Tier-1 corpus) and 15,473 are retained as in-DB shells for amendment-chain tracking.

## Corpus composition by decade and leg_type

Tier-1 corpus (analyser-ready, `na_inforce = 1 AND full_text >= 200`) cross-tabulated by decade and the seven largest leg_types; `other` aggregates the remaining 18 types (chiefly `ukla`, `nisi`, `asp`, `apni`, `nia`, `ukcm`, `aep`, `aosp`). Totals reconcile to the 69,885 headline.

| Decade | uksi | nisr | ssi | eur | ukpga | wsi | eudn | other | Total |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pre-1900 | 0 | 0 | 0 | 0 | 559 | 0 | 0 | 165 | 724 |
| 1900s | 0 | 0 | 0 | 0 | 45 | 0 | 0 | 3 | 48 |
| 1910s | 0 | 0 | 0 | 0 | 57 | 0 | 0 | 0 | 57 |
| 1920s | 0 | 0 | 0 | 0 | 89 | 0 | 0 | 10 | 99 |
| 1930s | 0 | 0 | 0 | 0 | 87 | 0 | 0 | 10 | 97 |
| 1940s | 47 | 0 | 0 | 0 | 126 | 0 | 0 | 25 | 198 |
| 1950s | 184 | 0 | 0 | 1 | 140 | 0 | 0 | 71 | 396 |
| 1960s | 373 | 0 | 0 | 4 | 257 | 0 | 2 | 107 | 743 |
| 1970s | 1,050 | 6 | 0 | 22 | 318 | 0 | 9 | 129 | 1,534 |
| 1980s | 3,434 | 13 | 0 | 50 | 382 | 0 | 54 | 132 | 4,065 |
| 1990s | 12,053 | 1,165 | 75 | 79 | 405 | 19 | 135 | 276 | 14,207 |
| 2000s | 11,754 | 2,567 | 2,528 | 626 | 303 | 1,267 | 494 | 337 | 19,876 |
| 2010s | 9,530 | 2,110 | 2,475 | 2,224 | 290 | 1,232 | 1,030 | 346 | 19,237 |
| 2020s | 4,969 | 900 | 1,258 | 234 | 202 | 765 | 115 | 161 | 8,604 |
| **Total** | **43,394** | **6,761** | **6,336** | **3,240** | **3,260** | **3,283** | **1,839** | **1,772** | **69,885** |

Reading the matrix: UK statutory instruments (`uksi`, 43,394 / 62 % of the corpus) dominate every modern decade. The devolved secondary-law streams switch on with devolution — Scottish SIs (`ssi`), Welsh SIs (`wsi`) and the bulk of NI Statutory Rules (`nisr`) appear from 1999/2000 onward. Retained EU law (`eur` + `eudn`) peaks in the 2010s. Primary legislation (`ukpga`) is the only stream with meaningful pre-1900 presence and stays roughly flat (~200–400 per decade) throughout, reflecting the far lower volume but longer survival of Acts. Reproduced from `legislation.db` via the `na_inforce` flag; query in `_inforce_definitive_count.py` lineage.

## Coverage by decade and leg_type

The table below converts the corpus counts above into **coverage ratios**: each cell is the share of that leg_type's *in-force universe* in that decade — counted from the National Archives manifests under the same definitional rule (`is_in_force` in `_inforce_definitive_count.py`) — that is present in the Tier-1 corpus with substantive text. Numerator = Tier-1 corpus (`na_inforce = 1 AND full_text >= 200`); denominator = in-force manifest items of that type and decade. A dash (–) means no in-force items of that type exist in that decade; cells shown as 100 % include rounding (numerator ≈ denominator). The bottom-right cell reconciles to the headline ratio (69,885 / 119,841 = 58 %).

| Decade | uksi | nisr | ssi | eur | ukpga | wsi | eudn | other | All types |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| pre-1900 | – | – | – | – | 46% | – | – | 1% | 3% |
| 1900s | – | – | – | – | 66% | – | – | 0% | 2% |
| 1910s | – | – | – | – | 61% | – | – | 0% | 4% |
| 1920s | – | – | – | – | 82% | – | – | 1% | 7% |
| 1930s | – | – | – | – | 72% | – | – | 1% | 6% |
| 1940s | 20% | – | – | – | 85% | – | – | 4% | 19% |
| 1950s | 24% | – | – | 100% | 81% | – | 0% | 11% | 25% |
| 1960s | 22% | – | – | 67% | 90% | – | 12% | 11% | 25% |
| 1970s | 29% | 1% | – | 22% | 94% | – | 9% | 12% | 26% |
| 1980s | 60% | 1% | – | 33% | 98% | – | 18% | 30% | 48% |
| 1990s | 100% | 39% | 100% | 19% | 100% | 100% | 29% | 90% | 85% |
| 2000s | 99% | 77% | 100% | 77% | 100% | 98% | 63% | 100% | 94% |
| 2010s | 95% | 78% | 97% | 100% | 100% | 94% | 99% | 100% | 94% |
| 2020s | 96% | 79% | 97% | 100% | 100% | 95% | 100% | 100% | 94% |
| **All decades** | **85%** | **54%** | **98%** | **82%** | **79%** | **96%** | **65%** | **5%** | **58%** |

Reading the coverage matrix: modern general-application law is near-complete — from the 2000s on, `uksi`, `ssi`, `wsi` and `ukpga` all sit at 94–100 %. The two persistent gaps among general-application types are **`nisr`** (NI Statutory Rules, 54 % overall; ~77–79 % even in recent decades — the largest general-application shortfall, confirmed structural 404s) and **retained EU law** (`eudn` 65 %, `eur` 82 %, dragged down by PDF-only Commission Decisions/Regulations). The **`other`** column reads 5 % overall because its denominator is dominated by local and private Acts (`ukla`, `gbppa`, `ukppa`, `eppa`) that survive only as PDF scans — by constitutional nature these impose no general-application burden and are excluded from the Scope B/C denominators (see below). Pre-1980 coverage is low across the board: the in-force statute book of those decades is disproportionately held as pre-CLML shells under the `InForce1991` baseline.

## Definitional rule (in force)

An item from the National Archives InForce CSV manifests was counted as in force if it imposes legal obligations or prohibitions somewhere in the UK at the snapshot date. Operationally:

- `InForce`
- `InForce1991` (in force at the **1 February 1991 base date** of the revised statute book — the date to which *Statutes in Force* had been revised when it was taken as the originating text for the Statute Law Database; not "1991 saving provisions")
- `LimitedApplication` (in force in part of the UK)
- any jurisdiction-qualified partial revocation matching `^revoked[A-Z][A-Za-z]*By$` (e.g. `revokedWithSavingsBy`, `revokedEWSBy`, `revokedEWBy`, `revokedSBy`, `revokedNIBy`)
- any jurisdiction-/savings-qualified partial repeal matching `^repealed[A-Z][A-Za-z]*By$` (e.g. `repealedWithSavingsBy`, `repealedEWBy`, `repealedEWNIBy`, `repealedEBy`, `repealedProspWithSavingsBy`)

Unqualified `repealedBy`, `revokedBy`, `repealedByLegislature` and all `NotInForce*` variants were excluded (no current legal force anywhere in the UK).

**Open question on `InForce1991` (flagged for The National Archives).** The `InForce1991` status (6,892 items in the in-force universe) marks legislation carried into the revised dataset as in force at the 1 February 1991 *Statutes in Force* base date. It is not independently confirmed here whether every such item remains in force *today*, or whether the status records only its standing as at the 1991 baseline, not subsequently reconfirmed. These items are disproportionately pre-modern, so the **pre-1980 coverage denominator** (and hence the low pre-1980 coverage ratios in the by-decade table above) is mildly sensitive to this question; the post-1990 Scope-C figures are unaffected. Pending clarification from The National Archives, `InForce1991` is counted as in force, consistent with its treatment on legislation.gov.uk.

Reproducibility script: `_inforce_definitive_count.py`.

## Pre-modern identifier reconciliation (name-slug vs chapter-coded)

Coverage matching compares National Archives in-force identifiers against corpus
identifiers by normalised-string equality (host, `/id/` and trailing slash stripped,
lowercased). This is exact and reliable for the modern `type/year/number` scheme and
for numeric regnal citations (`ukla/Geo3/41/100`), which the catalogue and
legislation.gov.uk share. It does **not** reconcile a small set of pre-1800 Acts that
the Archives cite by descriptive name-slug (`aep/Hen3/52/stat-marlbr`) while
legislation.gov.uk serves them under a chapter-coded regnal URI (`aep/Hen3c23/52/23`).
The two schemes are disjoint, so a string match fails and the Act is wrongly counted
as missing / not retrievable.

These are reconciled by an explicit override table (`medieval_slug_overrides.csv`,
built by `build_slug_overrides.py`). The match is decided at the `(leg_type, monarch,
regnal-year)` group level, refined by statute/session number for `stN`-style slugs;
it confirms that the Act's regnal-year group is **present in the corpus**, not that
each work-list row is independently title-matched to a specific provision. On that
basis **17 medieval Acts (44 work-list rows) are reconciled as already in the corpus**
under a chapter-coded URI — including Magna Carta (1297), the Statutes of Marlborough
(1267) and Westminster the First (1275) and Second (1285), Quia Emptores (1290),
Confirmation of the Charters, the Statute concerning Tallage, and the Treason Act 1351.
For 8 of the 17 the regnal-year cell contains a single statute (so group presence is
equivalent to per-statute presence); for the multi-statute cells the slugs are either
statute-number-disambiguated or correspond one-to-one to the cell's corpus entries, so
in this dataset every reconciliation is also correct at the specific-statute level —
but the matching *guarantee* is at the regnal-year-group granularity. A further
**2 statute-number variants** (5 Ric. 2 Stat. 1, 1381; 1 Geo. 2 Stat. 2) were reviewed
and confirmed as **genuine gaps** — the former repealed by the Criminal Law Act 1977,
the latter not served by legislation.gov.uk as a distinct in-force item.

The residual numeric impact on coverage is ≈0.1 % and does not affect the headline
figures. The limitation is recorded here, and patched by the override table, rather
than addressed by a general slug↔chapter-code canonicaliser, which the scale (≈140
candidate items across the whole work-list, of which 44 reconciled) does not warrant.
Note the strict distinction maintained throughout: items the matcher reports absent
are "not **ingested**", which is not the same claim as "not **digitised** on
legislation.gov.uk" — the gap between the two is the subject of the exhaustion sweep
below.

## Exhaustion sweep — all retrieval channels tested

Every in-force item with a coverage gap (50,765 items) was probed across all retrieval
channels on legislation.gov.uk — `/data.xml`, `/data.xml?version=enacted`,
`/enacted/data.xml`, `/data.xht`, `/data.akn`, and per-year point-in-time endpoints —
to an exhaustive per-item verdict (355,343 probes total). This replaces the earlier
sample-based extrapolation. Per-item verdicts:

| Verdict | Items | Meaning |
|---|---:|---|
| recoverable (substantive CLML) | 2,344 | a channel returned ingestable body text |
| already in corpus | 44 | pre-modern slug false-404, present under chapter-coded URI |
| shell (digitised, no CLML body) | 29,872 | 200 but `NumberOfProvisions = 0` / PDF-only |
| not digitised (404) | 18,505 | absent from every channel |
| incomplete | 0 | the 200 timed-out items were re-probed to definitive verdicts |

**Validation.** A stratified independent re-check (`validate_frontier.py`, hitting the
canonical HTML page — a different signal than the `data.xml` the sweep keyed on)
confirmed the negative verdicts: **false-404 rate 0 / 487 (95% CI 0.0–0.8%)** among
sampled `not_digitised` items, and **50 / 50** of a `shell` control re-confirmed as
PDF-only. The only systematic false-404s were the ~140 pre-modern name-slug items,
reconciled separately above.

**Recoverable ingest.** Of the 2,344 recoverable, 386 were already in the corpus (a
stale work-list — chiefly the 385 Best-Collection items ingested earlier) and **423
were ingested as net-new CLML Tier-1** via the existing pipeline (`_ingest_recoverable.py`;
source priority revised-current → Best-Collection revised → made/enacted; no-force
provisions stripped; `na_inforce = 1`). This is what moved the headline 69,462 → **69,885**.
Ingested by type: uksi 145, nisr 130, eur 92, ssi 22, wsi 17, eudn 7, ukpga 6, asc 1, asp 1, nisro 1, mwa 1.

**Deferred to phase 2 (counted): 1,535 items.** The remaining recoverables are digitised
but **not CLML-ingestable** — their `data.xml` is a 0-provision / PDF-only shell and they
registered as "recoverable" only via an Akoma-Ntoso representation the analyser does not
parse. These are not pipeline-ingestable today and are deferred to the phase-2 target
list (below), counted toward Tier 2. Composition is predominantly **uksi 755 + nisr 425**
(not retained-EU: eur 50 + eudn 18 = 68), then ukla 178, ukpga 31, nisro 25, wsi 22,
uksro 17, ssi 10, nisi 4.

**Reproducibility:** sweep checkpoint `_exhaustion_ckpt_v3.db` (md5 `681772dd…`);
aggregation `aggregate_exhaustion_sweep.py` → `exhaustion_recoverability_by_type.csv` /
`..._by_type_year.csv`; validation `validate_frontier.py` → `validation_results.csv`;
ingest `_ingest_recoverable.py`. Earlier sample-based work is in `api_exhaustion_findings.md`
/ `api_exhaustion_verification.md` with artefacts under `_probe_sweep/`.

## Confirmed unrecoverable types

Six leg_types returned **0 recoverable items** in the completed sweep (n ≥ 20): every
in-force gap item is a metadata-only/PDF shell or a hard 404 across all channels.
**11,104 in-force gap items**, surviving only as scanned PDFs in the original print
collection:

| type | gap items | shell (PDF-only) | not digitised (404) |
|---|---:|---:|---:|
| gbppa (GB private acts, pre-1801) | 5,317 | 0 | 5,317 |
| ukppa (UK private & personal acts) | 3,839 | 842 | 2,997 |
| eppa (English private acts, pre-1707) | 1,611 | 20 | 1,591 |
| apni (Acts of the NI Parliament) | 172 | 172 | 0 |
| aip (Acts of the Irish Parliament, pre-1800) | 144 | 0 | 144 |
| aosp (Acts of the Old Scottish Parliament, pre-1707) | 21 | 0 | 21 |

The earlier sample-based list named eight types; the completed sweep found recoverable
items in `uksro` and `gbla`, so they no longer qualify, and `uklp` (11 items) falls below
the n ≥ 20 threshold. Counts are in-force **gap** items per type — some of these types
also hold items already in the corpus from earlier ingestion (e.g. `aosp` has 65 in
corpus, not part of the gap); those are unaffected.

## Items catalogued in-force but not digitised in full

The 49,956-item structural gap (Tier 2 + Tier 3) is dominated by local/private Acts and pre-modern instruments. The composition, from the completed sweep:

- **Local & private Acts** (`ukla` 19,219, `gbppa` 5,317, `ukppa` 3,839, `eppa` 1,611, `gbla`/`uklp`). `ukla` (UK Local Acts) is the single largest pocket — ~99 % PDF-only shells; excluding it alone moves full-universe coverage from 58.3 % to ~71 %. These are excluded from Scope B/C by nature (addressed to named persons/places).
- **NI Statutory Rules (`nisr`)** — the largest *general-application* gap: 5,293 in-force gap items (3,731 PDF-only shells, 1,562 hard 404s), and **3,443 of the post-1990 Scope-C gap (61 % of it)**. The 2026-05 nisr re-probe confirmed the failures as clean structural 404s, not transient errors. The nisr in-force universe closes exactly: **12,479 catalogued in force = 6,761 in corpus with text (54 %) + 5,293 unrecoverable gap + 425 recoverable items deferred to phase 2**; the 130 net-new nisr the sweep ingested are already counted inside the 6,761, not a separate addend.
- **Retained EU law (`eudn` + `eur`)** — ~1,624 in-force gap items, almost all PDF-only Commission Decisions/Regulations (`data.xml` is a 0-provision shell pointing to a PDF); **1,156 of the Scope-C gap (~20 %)**.
- **Local UK SIs** — within Scope C, ~796 `uksi` are PDF-only. Spot-checking against canonical pages confirms these are genuine PDF-only **local instruments** — predominantly road/traffic orders (temporary prohibitions, speed limits, trunk-road/motorway restrictions), plus parish electoral-arrangement and diocesan orders — not misclassified digitised SIs. The 91.6 % Scope-C figure therefore holds.

## Why the local and private Acts gap does not materially affect the regulatory burden measure

Local and private Acts apply, by their constitutional nature, to named persons, places, or institutions identified within the Act itself — a particular railway company, named landowners, a specific bridge, a single corporation — and impose no obligations or prohibitions of general application on the public or on regulated entities of a class. Excluding them from the analyser denominator therefore does not reduce the regulatory burden being measured, because they never formed part of the regulatory burden that any UK private actor outside the named subjects could face. This is why Scope B (77.8 %) is the most defensible denominator for general-application regulatory-burden analysis, and Scope C (91.6 %) for modern regulatory-burden analysis.

## Regulatory layers beyond the statute book — what is out of measure

The measure covers the **centrally published statute book** — the in-force legislation legislation.gov.uk exposes as machine-readable text (the Tier-1 corpus above). Legally binding rules also live in other layers this measure does not reach, and they must be **distinguished from non-binding material, not lumped together**:

- **Binding out-of-corpus instruments — out of measure.** Byelaws, traffic regulation orders (TROs), permit / licence / authorisation conditions, and regulator rulebooks (the **FCA and PRA Handbooks** are the heavyweight cases) are legally binding but are not part of the centrally published statute book, so their internal contents are not counted.
- **Non-binding regulator guidance — out of measure.** Codes of practice, guidance notes and similar material carry no direct legal obligation; they are out of measure on a different ground (non-binding), not conflated with the binding layer above.

**Frontier proxies — the one place the statute book reaches across the boundary.** Where the statute book *itself* imposes a duty to comply with one of these out-of-measure instruments ("it is an offence to contravene a permit condition"; "contravention of a byelaw under this section is an offence"), that compliance duty **is counted, once**, as a *frontier proxy* — standing at the visible frontier for the invisible layer of rules behind it. This is the deepest-visible-layer rule in rubric §3. The count is **one proxy per out-of-measure target**, never an enumeration of that target's internal contents. Frontier proxies are tagged (`frontier_hook = true`, `frontier_target_type`) so the population is enumerable and reportable as *"N frontier duties standing proxy for out-of-measure layers."* These out-of-measure layers are a natural subject for a later phase (the objective anchor already names regulatory rulebooks as a future extension); bucketing them is **confirmed as a job for later, not now**.

### Growth analysis — regulation migrates between layers

Because binding rules live in several layers, regulation can **migrate between them with no net change in regulatory burden**. The clearest live case is the **Financial Services and Markets Act 2023** transfer of retained EU law (REUL) into the FCA/PRA rulebooks: as those requirements move from the statute book (in measure) to the regulators' Handbooks (out of measure), the measure will record a **decline in statute-book financial-services burden that is layer-migration, not deregulation**. The growth / flow analysis must **name this as an adjustment when the data exists**, so a migration is not read as a removal. (Counts are not additive across scope expansions: if a future phase brings a rulebook layer into measure, its contents are counted there and the corresponding frontier proxies re-classify to `counted_at_source` — rubric §3 — so the same rule is never counted twice.)

## Phase 2 target list

`missing_inforce_legislation.csv` contains the in-force items not present in `legislation.db`, with columns `item_url, title, year, leg_type, status, data_xml_url`. This is the Phase 2 target list for PDF-OCR digitisation or further per-item retrieval as the National Archives completes its digitisation programme.

The completed sweep adds a second, counted phase-2 category: **1,535 items that are digitised but not CLML-ingestable** — their `data.xml` is a 0-provision/PDF-only shell, and they register as recoverable only via an Akoma-Ntoso representation the current pipeline does not parse. Composition: predominantly `uksi` 755 + `nisr` 425 (not retained-EU: `eur` 50 + `eudn` 18), then `ukla` 178, `ukpga` 31, `nisro` 25, `wsi` 22, `uksro` 17, `ssi` 10, `nisi` 4. A future Akoma-Ntoso parser is the natural route to capture the subset that carries real AKN provision text; the PDF-only remainder needs OCR.

## Reproducibility

| Artefact | Purpose |
|---|---|
| `_inforce_definitive_count.py` | Computes the 119,841 headline figure from the CSV manifests. |
| `_inforce_db_coverage.py` | Cross-references the in-force universe against `legislation.db`. |
| `_probe_sweep_all_types.py` | 50-item `/data.xml` probe across every leg_type. |
| `_reprobe_db_shells.py` | 100-item probe of DB shells (na_inforce=1, full_text < 200). |
| `_alt_endpoint_retry.py` | Six-endpoint probe of high-impact shell pools. |
| `_alt_xht_reclassify.py` | Refined XHTML content classifier (rejects chrome-only responses). |
| `_bulk_collection_index.py` | Indexes every file in the Best Collection bulk download. |
| `_bulk_collection_xref_v2.py` | Cross-references BC against project-canonical in-force universe. |
| `_ingest_bc_792.py` | Ingests the 792 BC items identified as recoverable; updates shells / inserts new rows. |
| `_scope_stratified_coverage.py` | Computes the three-scope coverage table. |
| `_verify_three_checks.py` | Independent verification of the three headline claims. |
| `_build_coverage_table_v2.py` | Builds the type-by-type `coverage_table.csv`. |
| `aggregate_exhaustion_sweep.py` | Aggregates the completed sweep checkpoint to per-item verdicts (incl. slug + re-probe overrides). |
| `build_slug_overrides.py` | Builds the pre-modern name-slug reconciliation table (`medieval_slug_overrides.csv`). |
| `validate_frontier.py` | Independent canonical-page validation of negative verdicts (false-404 / shell). |
| `_ingest_recoverable.py` | Ingests CLML-substantive recoverables via the existing pipeline; defers AKN/PDF-only to phase 2. |
| `InForce_results_47/result_table_*.csv` | Source manifests from The National Archives (18 files). |
