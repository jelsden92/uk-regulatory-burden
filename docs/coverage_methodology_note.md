# Coverage methodology note

**Headline corpus figure: 69,462 fully digitised pieces of in-force UK legislation** — 100 % of the items that legislation.gov.uk currently exposes with substantive machine-readable XML body content (`NumberOfProvisions > 0`, `full_text >= 200` chars). This is the analyser input.

Within a wider National Archives in-force universe of **119,841 catalogued items**, the 50,380-item difference is structural. The breakdown depends on which scope of the statute book is in view:

## Scope-stratified coverage

The headline 58 % figure conflates two structurally different populations: (i) general-application legislation — Public Acts, Statutory Instruments, devolved primary and secondary law — which is essentially fully digitised, and (ii) local and private Acts — bespoke statutes addressed to named persons, places or companies — which have historically been published only as PDF scans. Reporting a single ratio masks this. The three scopes below disentangle them:

| Scope | Description | In-force universe | In corpus w/ text | Coverage |
|---|---|---:|---:|---:|
| **A — Full universe** | Every in-force item across all 28 leg_types | 119,842 | 69,462 | **58.0 %** |
| **B — General application** | Excludes ukla / ukppa / gbppa / eppa / gbla / uklp (Local + Private + Personal Acts) | 89,548 | 69,272 | **77.4 %** |
| **C — Post-1990 general application** | Scope B AND year ≥ 1990 (modern regulatory law) | 67,403 | 61,349 | **91.0 %** |

The 91 % figure for modern general-application law is the most directly relevant denominator for any analysis of contemporary regulatory burden. The 58 % full-universe figure is included for completeness and so the structural composition of the gap can be inspected directly.

## Three-tier structural breakdown (Scope A)

| Tier | Description | Items |
|---|---|---:|
| **Tier 1 — Fully digitised (HEADLINE)** | Substantive machine-readable XML; in corpus and analyser-ready | **69,462** |
| Tier 2 — Retrieved metadata-only shells | `/data.xml` 200 + `NumberOfProvisions = 0` or content stripped as Prospective/Repealed; row in DB but no analyser-usable text | 15,895 |
| Tier 3 — Not digitised at all | `/data.xml` returns HTTP 404; catalogued but no record on legislation.gov.uk | 34,484 |
| **In-force universe (catalogued)** | National Archives InForce CSV manifests | **119,841** |

`legislation.db` total rows: 218,088. Rows flagged `na_inforce = 1` (= Tier 1 + Tier 2): 85,357. The analyser filters on `length(full_text) >= 200` to isolate Tier 1; Tier 2 rows are retained in the database for amendment-chain tracking but do not enter the analyser.

## Definitional rule (in force)

An item from the National Archives InForce CSV manifests was counted as in force if it imposes legal obligations somewhere in the UK at the snapshot date. Operationally:

- `InForce`
- `InForce1991` (under 1991 saving provisions)
- `LimitedApplication` (in force in part of the UK)
- any jurisdiction-qualified partial revocation matching `^revoked[A-Z][A-Za-z]*By$` (e.g. `revokedWithSavingsBy`, `revokedEWSBy`, `revokedEWBy`, `revokedSBy`, `revokedNIBy`)
- any jurisdiction-/savings-qualified partial repeal matching `^repealed[A-Z][A-Za-z]*By$` (e.g. `repealedWithSavingsBy`, `repealedEWBy`, `repealedEWNIBy`, `repealedEBy`, `repealedProspWithSavingsBy`)

Unqualified `repealedBy`, `revokedBy`, `repealedByLegislature` and all `NotInForce*` variants were excluded (no current legal force anywhere in the UK).

Reproducibility script: `_inforce_definitive_count.py`.

## Exhaustion sweep — all retrieval channels tested

Before publishing these figures, every plausible retrieval channel on legislation.gov.uk was tested across every leg_type with an in-force gap. Findings:

| Channel | Items recovered |
|---|---:|
| `/data.xml` per-item probe (re-attempt of DB shells) | extrapolated ~580 (subset of Best Collection result) |
| `/data.xml?version=enacted` and `/enacted/data.xml` | 0 — same shells as canonical |
| `/data.xht` (XHTML rendering) | 0 — every "hit" was page-chrome containing a "View as PDF" notice |
| `/data.akn` (Akoma Ntoso) | 0 — metadata stub only |
| `/data.feed` (Atom) | 0 — existence signal only, no text |
| **Best Collection bulk download** | **792 items ingested → 385 became substantive after Prospective/Repealed strip** |

The Best Collection ingestion was the only channel adding net substantive content (+385 items to the headline). All 792 BC items are now in the DB with `na_inforce = 1`; the 407 that became shells after the Prospective/Repealed strip count toward Tier 2.

**Reproducibility:** the full sweep is documented in `api_exhaustion_findings.md` and `api_exhaustion_verification.md`, with output artefacts under `_probe_sweep/`.

## Confirmed unrecoverable types

Eight leg_types are confirmed unrecoverable by any digital channel — `/data.xml` 100 % HTTP 404 AND absent from Best Collection. **12,259 in-force items in total**, all surviving only as scanned PDFs in the original print collection:

| type | in-force | digitised |
|---|---:|---:|
| gbppa (GB private acts, pre-1801) | 5,317 | 0 |
| ukppa (UK private & personal acts) | 3,839 | 0 |
| eppa (English private acts, pre-1707) | 1,611 | 0 |
| uksro (UK statutory rules & orders, pre-1948) | 1,146 | 0 |
| aip (Acts of the Irish Parliament, pre-1800) | 144 | 9 |
| gbla (GB local acts, pre-1801) | 107 | 0 |
| aosp (Acts of the Old Scottish Parliament, pre-1707) | 21 | 65 (already in corpus) |
| uklp (UK local & personal acts) | 11 | 0 |

(The 11 aip/aosp items that do have BC content are already in the corpus from earlier ingestion runs.)

## Items catalogued in-force but not digitised in full

The remaining ~38,000-item structural gap consists of items the National Archives has catalogued as in-force but has not yet digitised with substantive XML. Three dominant pockets:

- **ukla — 19,219 items.** UK Local Acts. The series is effectively undigitised at the body-text level: 99 % of in-force items return a metadata-only shell pointing to a PDF. Excluding ukla alone moves coverage from 58 % to 71 %.
- **nisr — ~5,848 items.** NI Statutory Rules. Approximately 1,547 return hard HTTP 404 on `/data.xml`; the remainder return metadata-only shells. The 50/50 nisr re-probe in 2026-05 confirmed every sampled failure as a clean structural 404, not a transient retrieval error.
- **eudn — 994 items.** Retained EU Decisions. The `/data.xml` endpoint returns a valid record for every item but with `NumberOfProvisions = 0`, pointing to a PDF version of the Commission Decision.

## Why the local and private Acts gap does not materially affect the regulatory burden measure

Local and private Acts apply, by their constitutional nature, to named persons, places, or institutions identified within the Act itself — a particular railway company, named landowners, a specific bridge, a single corporation — and impose no obligations of general application on the public or on regulated entities of a class. Excluding them from the analyser denominator therefore does not reduce the regulatory burden being measured, because they never formed part of the regulatory burden that any UK private actor outside the named subjects could face. This is why Scope B (77.4 %) is the most defensible denominator for general-application regulatory-burden analysis, and Scope C (91.0 %) for modern regulatory-burden analysis.

## Phase 2 target list

`missing_inforce_legislation.csv` contains the in-force items not present in `legislation.db`, with columns `item_url, title, year, leg_type, status, data_xml_url`. This is the Phase 2 target list for PDF-OCR digitisation or further per-item retrieval as the National Archives completes its digitisation programme.

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
| `InForce_results_47/result_table_*.csv` | Source manifests from The National Archives (18 files). |
