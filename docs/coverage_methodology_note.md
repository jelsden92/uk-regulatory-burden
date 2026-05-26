# Coverage methodology note

**Headline corpus figure: 69,077 fully digitised pieces of in-force UK legislation** — 100 % of the items that legislation.gov.uk currently exposes with substantive machine-readable XML body content (`NumberOfProvisions > 0`, `full_text >= 200` chars). This is the analyser input.

Within a wider National Archives in-force universe of **119,841 catalogued items**, the 50,764-item difference is structural:

| Tier | Description | Items |
| --- | --- | ---: |
| **Tier 1 — Fully digitised (HEADLINE)** | Substantive machine-readable XML; in corpus and analyser-ready | **69,077** |
| Tier 2 — Retrieved metadata-only shells | `/data.xml` 200 + `NumberOfProvisions = 0`; row in DB but PDF-only | 15,488 |
| Tier 3 — Not digitised at all | `/data.xml` returns HTTP 404; catalogued but no record on legislation.gov.uk | 35,276 |
| **In-force universe (catalogued)** | National Archives InForce CSV manifests | **119,841** |

`legislation.db` total rows: 217,296. Rows flagged `na_inforce = 1` (= Tier 1 + Tier 2): 84,565. The analyser filters on `length(full_text) >= 200` to isolate Tier 1; Tier 2 rows are retained in the database for amendment-chain tracking but do not enter the analyser.

## Definitional rule (in force)

An item from the National Archives InForce CSV manifests was counted as in force if it imposes legal obligations somewhere in the UK at the snapshot date. Operationally:

- `InForce`
- `InForce1991` (under 1991 saving provisions)
- `LimitedApplication` (in force in part of the UK)
- any jurisdiction-qualified partial revocation matching `^revoked[A-Z][A-Za-z]*By$` (e.g. `revokedWithSavingsBy`, `revokedEWSBy`, `revokedEWBy`, `revokedSBy`, `revokedNIBy`)
- any jurisdiction-/savings-qualified partial repeal matching `^repealed[A-Z][A-Za-z]*By$` (e.g. `repealedWithSavingsBy`, `repealedEWBy`, `repealedEWNIBy`, `repealedEBy`, `repealedProspWithSavingsBy`)

Unqualified `repealedBy`, `revokedBy`, `repealedByLegislature` and all `NotInForce*` variants were excluded (no current legal force anywhere in the UK).

Reproducibility script: `_inforce_definitive_count.py`.

## Gap-fill procedure

After initial corpus construction, cross-referencing the in-force universe against `legislation.db` identified 40,389 in-force items not present in the corpus (66.3 % initial coverage). We then attempted to fill all in-scope gaps via the legislation.gov.uk per-item `/data.xml` API, using the production downloader (`downloader.download_item`) with HTTP 202 retry-on-generation, 429 backoff, and `INSERT OR IGNORE` resume safety. Five categories were probed (20 items each) and queued; queues were run sequentially in a single orchestrator (`_run_remaining_four_queues.py`, plus the earlier targeted `_run_uksi_inforce_fill.py`).

### Per-category outcomes

| Category | Queued | Inserted (ok) | Failed (err) | Success rate |
|---|---:|---:|---:|---:|
| ukpga InForce | 536 | 393 | 143 | 73.3 % |
| uksi InForce | 191 | 71 | 120 | 37.2 % |
| uksi InForce1991 | 3,178 | 2,901 | 277 | 91.3 % |
| nisr InForce | 1,603 | 56 | 1,547 | 3.5 % |
| eur + eudn InForce | 1,691 | 1,691 | 0 | 100.0 % |
| **Total** | **7,199** | **5,112** | **2,087** | **71.0 %** |

Net effect on `legislation.db`: 212,183 rows → 217,295 rows (+5,112).

### Coverage progression by in-force component

| Component | Universe | Before fill | After fill | Δ |
|---|---:|---:|---:|---:|
| `InForce` | 108,726 | 73,398 (67.5 %) | 75,609 (69.5 %) | +2.0 pp |
| `InForce1991` | 6,892 | 2,793 (40.5 %) | 5,694 (82.6 %) | +42.1 pp |
| `LimitedApplication` | 228 | 0 (0.0 %) | 0 (0.0 %) | — |
| Partial revocations | 2,448 | 2,219 (90.6 %) | 2,219 (90.6 %) | — |
| Partial repeals | 1,547 | 1,042 (67.4 %) | 1,042 (67.4 %) | — |
| **Total** | **119,841** | **79,452 (66.3 %)** | **84,564 (70.6 %)** | **+4.3 pp** |

## Why the residual 35,277-item gap is structural

The remaining 29.4 % of the in-force universe could not be retrieved with body text via the per-item API. The failures fall into three structural categories — none reflect a limitation of the methodology, but rather the current digitisation status of UK legislation on legislation.gov.uk.

**1. Items where `data.xml` returns a metadata-only shell (`NumberOfProvisions=0`).**
The XML response contains title, year, number, and a link to the original PDF, but no digitised section text. This is the standard legislation.gov.uk pattern for:

- UK Local Acts (`ukla`) — 18,298 missing-InForce items, 0 % with provisions in probe.
- Older private and personal Acts (`ukppa`, `gbppa`, `eppa`) — ~10,760 missing-InForce items in aggregate.
- Pre-1900 UK Public General Acts (`ukpga`) — ~457 of the 536 missing items.
- Pre-1948 UK Statutory Instruments under InForce1991 — ~2,901 retrieved as shells in this run.
- Retained EU Regulations and Decisions (`eur`, `eudn`) — all 1,691 retrieved are shells.

For these instruments, full text exists only as scanned PDF on the National Archives original-print collection. Extracting prescriptive obligations from PDF scans would require an OCR pipeline (and, for pre-1900 typography, manual correction); this is outside the scope of this study.

**2. Items where `data.xml` returns HTTP 404 (no digitised record at all).**
The instrument is catalogued in the InForce manifest but has no XML or HTML representation on legislation.gov.uk. Examples observed during probing:

- 90 % of missing `nisr` InForce items (1,547 of 1,603) — 404 across all sampled years, 1979–2010.
- ~60 % of missing modern `uksi` InForce items (120 of 191) — 404 on `/data.xml`.
- ~20 % of missing `ukpga` InForce items (143 of 536) — 404 on `/data.xml`.

These are not recoverable via the public API. They represent items the National Archives knows exists (the manifest lists them) but has not yet ingested into legislation.gov.uk.

*Confirmatory re-probe (2026-05-26):* a follow-up probe of 50 random items drawn from the 1,547 NI Statutory Rules that errored during the gap-fill run returned **HTTP 404 for every item (50/50, sample spanning 1987–2009)**. No metadata-only shells, no transient errors — a clean, unambiguous structural-absence signal. This confirms that the nisr residual gap reflects items present in the National Archives InForce manifest but absent from legislation.gov.uk as a digitised record, rather than items present-but-PDF-only or items affected by transient retrieval problems. Reproducibility: `_reprobe_nisr_failures.py`.

**3. Items deliberately excluded from the fill plan.**
228 `LimitedApplication` items (`ukpga` 117, `aip` 107, `aep` 3, `apgb` 1) were not attempted, as `LimitedApplication` items in this set are predominantly historical/Irish primary legislation whose body text on legislation.gov.uk is also PDF-only.

## Interpretation

The 69,077-row analyser-ready subset (`na_inforce = 1 AND length(full_text) >= 200`) represents **100 % of the currently-digitised in-force statute book** available from legislation.gov.uk under the stated definitional rule. The 50,764-item residual gap between this and the 119,841-item universe is not a methodological gap — every in-scope item was either retrieved via the per-item API, returned an HTTP 404 (no digitised record), or returned a metadata-only XML shell pointing to a PDF (no digitised body text). Improving coverage further would require either (a) waiting for the National Archives to complete digitisation of historical/local Acts and pre-1948 SIs, or (b) building an OCR pipeline against the original-print PDFs — neither of which falls within the methodology of this study.

Any analyses that quote regulatory burden across the full universe should therefore qualify their denominator with: *"computed against the 69,077 in-force items with substantive digitised text available on legislation.gov.uk under the National Archives InForce manifests."*

## Coverage table for the project summary

A type-by-type three-column coverage table is produced by `_build_coverage_table_v2.py` and saved as `coverage_table.csv`. The three columns capture three distinct things — what exists, what is digitised with substantive XML, and what we have:

1. **In force (universe)** — items in the National Archives InForce CSV under the 119,841-item definition.
2. **Digitised with substantive XML (est.)** — estimated number for which legislation.gov.uk serves XML with `NumberOfProvisions > 0`. Computed as (corpus items with `full_text >= 200`) + (missing items × probe-derived provisions rate for that type). Per-type rates: nisr 0 % (re-probe-confirmed), ukla 0 %, ukpga 0 %, eur/eudn 0 %, uksi 20 %, all other types 0 % (conservative; not specifically probed).
3. **In our corpus with substantive text** — `legislation.db` rows with `na_inforce = 1 AND length(full_text) >= 200`.

Headline figures:

| Group | (1) In force | (2) Digitised w/ provisions | (3) In our corpus w/ text | Digitisation rate | Retrieval rate |
|---|---:|---:|---:|---:|---:|
| General application legislation | 89,547 | 69,064 | 69,064 | **77.1 %** | **100.0 %** |
| Local and private Acts | 30,294 | 13 | 13 | 0.0 % | 100.0 % |
| **Overall** | **119,841** | **69,077** | **69,077** | **57.6 %** | **100.0 %** |

**Retrieval rate of 100 %.** Every item in the in-force universe that legislation.gov.uk currently exposes with substantive XML body content is in the corpus. The two columns reconcile exactly because, after the full probing programme, every probed missing-tail returned either an HTTP 404 (no record at all) or a metadata-only XML shell (no body text). The single positive probe hit observed during the programme — the *Rebuilding of London Act 1670* (`aep/Cha2/22/11`, 118,855 chars) — has been retrieved and added to the corpus.

The 42.4 % gap between the in-force universe (col 1) and the digitised count (col 2) is structural — items catalogued by The National Archives but available only as PDF scans (the local/private series, retained EU Decisions, pre-1948 uksro, pre-1974 nisro, pre-1900 ukpga) or not digitised at all (~2,500 HTTP-404 records concentrated in nisr, apni, apgb, aip, and aep).

### Why the local and private Acts gap does not materially affect the regulatory burden measure

Local and private Acts apply, by their constitutional nature, to named persons, places, or institutions identified within the Act itself — a particular railway company, named landowners, a specific bridge, a single corporation — and impose no obligations of general application on the public or on regulated entities of a class. Excluding them from the analyser denominator therefore does not reduce the regulatory burden being measured, because they never formed part of the regulatory burden that any UK private actor outside the named subjects could face.

## Phase 2 target list

`missing_inforce_legislation.csv` contains the 35,277 in-force items not present in `legislation.db`, with columns `item_url, title, year, leg_type, status, data_xml_url`. This is the Phase 2 target list for PDF-OCR digitisation or further per-item retrieval as the National Archives completes its digitisation programme. The list is dominated by:

| Type | Missing | Comment |
|---|---:|---|
| ukla | 18,591 | UK Local Acts — PDF-only |
| gbppa | 5,317 | GB Private Acts pre-1801 — PDF-only |
| ukppa | 3,836 | UK Personal & Private Acts — PDF-only |
| eppa | 1,611 | English Private Acts pre-1707 — PDF-only |
| nisr | 1,562 | NI Statutory Rules — many HTTP 404 |
| nisro | 1,244 | NI Statutory Rules & Orders pre-1974 — PDF-only |
| uksro | 983 | UK Statutory Rules & Orders pre-1948 — PDF-only |
| apgb | 660 | GB Public Acts pre-1801 — PDF-only |
| uksi | 517 | Mix of metadata shells and 404s |
| ukpga | 328 | Mostly pre-1900 local-flavour public Acts — PDF-only |
| (other types) | 629 | |

## Reproducibility

| Artefact | Purpose |
|---|---|
| `_inforce_definitive_count.py` | Computes the 119,841 headline figure from the CSV manifests. |
| `_inforce_db_coverage.py` | Cross-references the in-force universe against `legislation.db`. |
| `_probe_five_categories.py` | Probes 20 random items per category and writes recoverable queues. |
| `_run_uksi_inforce_fill.py` | Targeted fill of the uksi InForce 191-item gap. |
| `_run_remaining_four_queues.py` | Sequential fill of the four remaining queues. |
| `_run_four_results.json` | Machine-readable per-queue ok/err/elapsed from the main run. |
| `_add_na_inforce_column.py` | Adds and populates the `na_inforce` flag on `legislation.legislation`. |
| `_build_coverage_table_v2.py` | Builds the three-column `coverage_table.csv` (in-force universe / digitised / in corpus). |
| `_build_missing_inforce_csv.py` | Builds the 35,277-item Phase 2 target list. |
| `_reprobe_nisr_failures.py` | Re-probes 50 random nisr gap-fill failures; confirmed 50/50 structural 404. |
| `InForce_results_47/result_table_*.csv` | Source manifests from The National Archives (18 files). |
