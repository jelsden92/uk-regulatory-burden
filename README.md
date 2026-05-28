**The first comprehensive measure of prescriptive regulatory burden in UK legislation — a UK equivalent of [QuantGov RegData](https://quantgov.org/).**

This repository contains the corpus-building pipeline, classification code, and methodology documents for a project that measures the stock and flow of legally binding obligations across the entire body of UK law in force. Results are forthcoming in a separate think-tank publication.

---

## Status

| Phase | State |
| --- | --- |
| Corpus build | **Complete — 69,462 fully digitised pieces of in-force UK legislation**, i.e. 100 % of the items that legislation.gov.uk currently exposes with substantive machine-readable XML. This is the analyser input. |
| Methodology | **Stable at v12** — six-category classification system; ground-truth validation against 10+ Acts on a line-by-line manual workbook |
| Classifier | Under development — hybrid rule-based and NLP pipeline with six-category classification, validated against manual ground-truth across 10+ Acts using line-by-line review |
| Results | **Forthcoming** in a separate think-tank paper |

The headline corpus figure — **69,462 pieces of fully digitised in-force UK legislation** — sits inside a wider universe of 119,841 in-force items catalogued by The National Archives. Reporting a single coverage ratio across that universe conflates two structurally different populations, so coverage is reported at three nested scopes:

| Scope | Description | In-force universe | In corpus | Coverage |
|---|---|---:|---:|---:|
| **A — Full universe** | Every in-force item across all 28 leg_types | 119,841 | 69,462 | **58.0 %** |
| **B — General application** | Excludes local & private Acts (ukla, ukppa, gbppa, eppa, gbla, uklp) | 89,548 | 69,272 | **77.4 %** |
| **C — Post-1990 general application** | Scope B AND year ≥ 1990 (modern regulatory law) | 67,403 | 61,349 | **91.0 %** |

The 91 % post-1990 figure is the most directly relevant denominator for any analysis of contemporary regulatory burden. The 58 % full-universe figure is reported for completeness — the 50,380-item residual is structural and not a retrieval failure: 15,895 items are catalogued but exist on legislation.gov.uk only as metadata-only XML shells pointing to PDF originals, and 34,484 items return HTTP 404 on `/data.xml` and are not digitised at all. An exhaustion sweep across the per-item API (`/data.xml`, `/data.xml?version=enacted`, `/enacted/data.xml`, `/data.xht`, `/data.akn`, `/data.feed`) plus a full cross-reference against the legislation.gov.uk Best Collection bulk download confirmed that no further substantive content is recoverable. See [`docs/coverage_methodology_note.md`](docs/coverage_methodology_note.md) and [`docs/coverage_table.csv`](docs/coverage_table.csv) for the full breakdown by legislation type.

The corpus manifest (`corpus_manifest.csv`) lists every item in the dataset by its `legislation.gov.uk` URL, title, year, and legislation type. The underlying XML text of each item is not redistributed here — it is sourced from [legislation.gov.uk](https://www.legislation.gov.uk) under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).

---

## Why this matters

No government, regulator, or researcher currently has a reliable answer to the question: how much regulation exists in the UK, and is it growing or shrinking? This project provides that answer for the first time.

Existing UK regulatory-burden estimates count pages, words, or statutory instruments — proxies that conflate prescriptive content with definitional text, repealed provisions, and devolved-government plumbing. This project counts **standing obligations on private actors**: the specific provisions that impose compliance costs on businesses, individuals, and the third sector.

Key methodological features:

- **Classification system** — the headline metric is **total private actor burden**, defined as `direct + implied + conditional obligations` combined and presented as a breakdown:
  - **Direct burdens** — obligations that apply at all times regardless of whether any regulatory action has been taken (example: an employer must pay the national minimum wage).
  - **Implied burdens** — obligations not directly stated as requirements but revealed through the structure of the law. This includes defence provisions where a business must prove it maintained adequate systems; rights granted to one party that create corresponding obligations on another; and provisions voiding contract terms unless certain conditions are met.
  - **Conditional burdens** — obligations that activate when a specific event occurs, typically regulatory action such as an inspection, improvement notice, or licence condition (example: a landlord must comply with an improvement notice once served).

  `public_body` obligations are excluded; `ambiguous` sentences are flagged for review.
- **Status filtering** — provisions marked Prospective, Repealed, Dead, or Discarded in the CLML XML are stripped before analysis, so the measure reflects law currently in force.
- **Penalty-as-consequence rule** — criminal-enforcement provisions are not double-counted as separate obligations.
- **Conditional obligations** — obligations triggered by regulatory action (improvement notices, licensing conditions, inspection powers) are captured as a distinct category, an area QuantGov does not address.
- **Devolution-aware** — Scotland, Wales, and Northern Ireland legislation is separately identified, allowing decomposition of the UK regulatory-fragmentation premium.

Full methodology: [`docs/methodology.md`](docs/methodology.md).
Research agenda and open questions: [`docs/research_agenda.md`](docs/research_agenda.md).
Implementation plan: [`docs/implementation_plan.md`](docs/implementation_plan.md).

---

## Repository contents

| Path | Purpose |
| --- | --- |
| `downloader.py` | Per-item XML download, CLML parsing, Status filtering, schedule classification |
| `bulk_loader.py` | Bulk-download orchestration over the legislation.gov.uk Bulk archive |
| `missing_si_downloader.py` | Targeted re-downloads to fill statutory-instrument coverage gaps |
| `analyser.py` | Sentence-level classifier — prescriptive-term detection, subject identification, six-category routing |
| `word_list.py` | Vocabulary lists (prescriptive verbs, public-body subjects, private-actor subjects, definitional patterns) |
| `test_run.py` | End-to-end harness for analysing a small set of Acts into `test_run.db` for benchmark validation |
| `corpus_manifest.csv` | Full list of corpus items (URL, title, year, type) |
| `docs/coverage_table.csv` | Three-column type-by-type coverage table: in-force universe / digitised with substantive XML / in our corpus |
| `docs/coverage_methodology_note.md` | Full coverage methodology: definitional rule, gap-fill procedure, structural-cause analysis |
| `docs/methodology.md` | Full methodology specification (v12) |
| `docs/research_agenda.md` | Open questions and future phases (v9) |
| `docs/implementation_plan.md` | Implementation plan and corpus state (v13) |
| `LICENSE` | MIT licence covering the source code |
| `LICENSE-docs` | CC-BY-4.0 covering methodology documents and the corpus manifest |

---

## How the pipeline works

```
                  legislation.gov.uk (CLML XML)
                              │
        ┌─────────────────────┼──────────────────────┐
        │                     │                      │
  bulk_loader.py        downloader.py        missing_si_downloader.py
   (bulk archive)       (per-item API)           (gap-fill)
        │                     │                      │
        └─────────────────────┴──────────────────────┘
                              │
                       Status filter
                  (strip Prospective/Repealed/
                   Dead/Discarded provisions)
                              │
                       legislation.db
                  (in-force corpus tagged
                   na_inforce=1; full_text +
                   schedule_text_prescriptive +
                   schedule_text_reference)
                              │
                         analyser.py
              ┌──────────────┴──────────────┐
              │     classify_subject_spacy  │
              │  word_list + spaCy subject  │
              │  detection + tier-4 default │
              └──────────────┬──────────────┘
                              │
                       results table
              (per-Act counts by category +
               sentence-level classifications)
```

The classifier is a hybrid rule-based + spaCy NLP pipeline. Prescriptive verbs are detected first-occurrence per sentence using longest-match against a curated vocabulary (`word_list.py`). Subjects are resolved by a three-tier default: (1) direct first-occurrence subject match against public-body or private-actor vocabularies, (2) spaCy dependency parse of the nominal subject of the prescriptive verb, (3) tier-4 default classification for sentences that cannot be confidently resolved. Definitional and procedural patterns are filtered out at sentence level. See `docs/methodology.md` for the full specification.

---

## How to replicate

### 1. Build the corpus

```bash
# Download the legislation.gov.uk Bulk archive separately
# (https://www.legislation.gov.uk/bulkdata) and place at ./Bulk download/

python bulk_loader.py            # Loads bulk XML into legislation.db
python missing_si_downloader.py  # Fills SI gaps via per-item API
```

Expected runtime: several days of wall time at the legislation.gov.uk rate limit (≈3 requests/second). The bulk-load step is single-shot; the gap-fill step is resumable.

### 2. Validate a small benchmark

```bash
python test_run.py
```

This downloads and analyses a configurable list of Acts into `test_run.db` and prints per-Act counts in each of the six categories, for comparison against the manual ground-truth workbook.

### 3. Run the full classifier

The full corpus run is performed on Google Colab with `en_core_web_trf` + GPU. The notebook is not included in this repository, available on request.

### Dependencies

```bash
python -m pip install requests beautifulsoup4 lxml spacy
python -m spacy download en_core_web_trf
```

Python 3.10+. SQLite 3.35+ for `legislation.db`.

---

## Data provenance and licensing

- **Source corpus:** [legislation.gov.uk](https://www.legislation.gov.uk), maintained by The National Archives, available under the [Open Government Licence v3.0](https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/).
- **Corpus manifest (`corpus_manifest.csv`):** derived dataset, CC-BY-4.0. Cite as: Elsden, J. (2026). *UK Regulatory Burden Measurement — corpus manifest.*
- **Methodology documents (`docs/*.md`):** CC-BY-4.0.
- **Source code:** MIT.

The 4.1 GB `legislation.db` containing full provision text is not redistributed via this repository — it can be reconstructed deterministically from the pipeline above. The analyser operates on the 69,462-row fully-digitised subset (`na_inforce = 1 AND length(full_text) >= 200`). The remaining 50,380 items in the National Archives in-force universe consist of 15,895 metadata-only XML shells pointing to PDF originals (the local/private series, retained EU Decisions, pre-1948 statutory instruments, pre-1900 ukpga) and 34,484 records that return HTTP 404 on `/data.xml` (concentrated in pre-1972 NI material and pre-1800 historical primary legislation). See [`docs/coverage_methodology_note.md`](docs/coverage_methodology_note.md) for the full characterisation.

---

## Citation

If you use this code, methodology, or corpus manifest, please cite:

> Elsden, J. (2026). *UK Regulatory Burden Measurement: methodology, corpus, and pipeline.* https://github.com/jelsden92/uk-regulatory-burden

A formal working-paper citation will be added when the results paper is published.

---

## Contact

Jethro Elsden — jelsden1000@gmail.com
