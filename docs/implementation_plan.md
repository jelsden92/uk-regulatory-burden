# UK Regulatory Burden Measurement

**Phase 1 Implementation Plan  —  Version 13**

_May 2026  |  Corpus complete. Validation in progress. Classifier next._

> STATUS: Corpus complete at 212,183 rows — 99.6%+ SI coverage, 100% post-1990 Acts. Status filtering active. 9 Acts validated in workbook. Next: complete 20 short Acts manually, build preliminary classifier, continue to 50 Acts, full Colab run.

# Immediate Next Steps
- 1. Complete manual validation of next 12 short Acts (links in Research Agenda)
- 2. Include 5-6 Victorian Acts in manual validation for classifier training data
- 3. Download all 12 manual review Acts into test_run.db — analyser counts ready for comparison
- 4. Build preliminary classifier at 20 Acts validated
- 5. Continue validation to 50 Acts
- 6. Sync Colab notebook (uk_reg_colab_v4.ipynb → v5) with all recent fixes
- 7. Full Stream B run on Colab after production classifier integrated

# Corpus — Final State

| Metric | Value |
| --- | --- |
| Total rows | 212,183 |
| uksi coverage | 99.6% (43,272/43,463) |
| ssi coverage | 99.9% (6,401/6,405) |
| wsi coverage | 99.7% (3,395/3,406) |
| nisr coverage | 86.7% (10,475/12,078) |
| Post-1990 ukpga | 100% — all significant Acts present |
| Companies Act 2006 | Present ✅ (2.97 MB) |
| Freedom of Information Act 2000 | Present ✅ |
| Status filtering | Active — 639,000+ no-force elements stripped |
| Permanently unrecoverable | ~12,000 items (never digitised) |
| Further downloads | Not recommended — diminishing returns confirmed |

# Six-Category Classification System

| Category | Detection | Key decisions |
| --- | --- | --- |
| private_actor | Word list + subject classification + tier4_default | Standing obligations on private actors |
| implied_burden | IMPLIED_OBLIGATION_WORDS ('shows that', 'proves that') | Defence provisions revealing compliance obligations |
| implied_burden_active | IB + ACTIVE_COMPLIANCE_MARKERS | Adequate procedures, due diligence type obligations |
| conditional_obligation | Trigger phrase check after subject classification | Obligations activated by notice, licence, order, or regulatory suspicion |
| conditional_burden | POSITIVE_ID_REQUIRED_TERMS | Anti-avoidance provisions |
| public_body | PUBLIC_BODY_SUBJECTS match | Excluded from headline metric |
| ambiguous | Clause opener / structural subject / no subject | Flagged for review |

# Key Word List Additions — Recent
- PRIVATE_ACTOR_SUBJECTS: 'the parties' — Late Payment Act commercial contract law
- PRESCRIPTIVE_WORDS obligations: 'it is an implied term' — Late Payment Act s.1(1)
- PRESCRIPTIVE_WORDS obligations: 'has the right not to be subjected/dismissed/treated' — employment anti-retaliation
- DEFINITIONAL_PATTERNS: 'shall operate to', 'shall take effect as', 'shall be deemed to have' — pre-1970 deemed consequences
- DEFINITIONAL_PATTERNS: 'shall not be construed as', 'no provision shall be made', 'no amendment shall be made' — ministerial restrictions
- STRUCTURAL_SUBJECTS: 'poll', 'votes', 'seat', 'seats', 'ballot', 'vacancy', 'allocation', 'register' — electoral machinery
- PUBLIC_BODY_SUBJECTS: 'a Scottish Minister', 'the First Minister', 'the Presiding Officer', 'a member of the Scottish Parliament' etc.

# Validation Workbook — Current State
Reg_Burden_Project_Validation.xlsx — 9 Acts complete with full line-by-line classification. Each row records: burden sentence, section reference, Direct Burden, Implied Burden, Conditional Burden, Ambiguous, Claude agrees, Resolution.

> KEY DECISIONS FORMALISED IN WORKBOOK: (1) Penalty as consequence — not counted separately; (2) Conditional burden includes regulatory inspection/seizure powers — condition is suspicion not guilt; (3) Evidence supply is part of parent obligation; (4) Judicial discretion provisions are not private actor burdens; (5) Definitional tests are not separate from the prohibitions they define; (6) Nested burdens — scope definitions are not additional obligations.

# Replication Guide — Building a Similar Regulatory Burden Measure
## Step 1 — Data Acquisition
- Register for access to research.legislation.gov.uk/statute-book-data
- Download Revised Current bulk ZIP — all legislation types (~2.5GB)
- Download Best Collection bulk ZIP — fills gaps where only enacted version exists (~1.35GB)
- Run missing_si_downloader.py against InForce CSV to fill remaining SI gaps (~57,000 items)
- Run PDFOnly, InForce1991, JurisdictionLimited queues for maximum coverage
- Add name and email to user agent string — required by National Archives fair use policy

## Step 2 — Database Setup
- SQLite database with legislation table (item_url, title, year, leg_type, stream, full_text, schedule_text, territorial_extent)
- bulk_loader.py reads CLML XML files, calls parse_xml() with Status filtering, inserts into DB
- Status filtering: strip_no_force_provisions() decomposes elements with Status in {Prospective, Repealed, Dead, Discarded, Prospective Repealed}
- Resume-safe loading — skip already-present items by item_url

## Step 3 — Word List Construction
- Core prescriptive words by category: obligations, prohibitions, penalty terms, implied obligation words
- Public body subjects — comprehensive list of ministerial, regulatory, and judicial roles
- Structural subjects and clause openers — filters false positives from structural provisions
- Definitional patterns — filters interpretive, scope, and legal consequence provisions
- Era-aware additions for pre-1970 legislation — 'shall operate to', 'shall be deemed to' etc.

## Step 4 — Classification Architecture
- Nine-step subject classification: recital → public body → contract nsubj → tracker → clause opener → structural → first occurrence → spaCy → tier4_default
- Six output categories: private_actor, implied_burden, implied_burden_active, conditional_obligation, conditional_burden, public_body, ambiguous
- Confidence flag system: high/medium/low based on classification method
- Special rules: PENALTY_ONLY_TERMS cross-reference check, guilt cross-reference check, implied term override, Victorian obligation pre-check

## Step 5 — Validation Approach
- Line-by-line manual classification workbook — read each Act, record burden sentence with classification type
- Compare against analyser output sentence by sentence
- Target 150 Acts across diverse categories including Victorian/pre-war legislation
- Each validated Act simultaneously builds classifier training data

## Step 6 — Classifier Development
- Fine-tune Legal-BERT on labelled sentences from validation workbook
- Preliminary classifier at 20 Acts — test accuracy
- Production classifier at 150 Acts — integrate into full run pipeline
- Active learning loop — expert review of medium-confidence cases feeds retraining

## Step 7 — Full Run
- Upload legislation.db to Google Colab (Pro — A100 GPU, High RAM)
- Run uk_reg_colab_v5.ipynb with DB_PATH=legislation.db, STREAM=B
- Expected runtime: 24-48 hours for 212,000 items
- Post-run: stratified validation sample, active learning, output generation

## Step 8 — Extending to Other Jurisdictions
- Australian legislation: legislation.gov.au provides similar XML API
- Canadian legislation: laws-lois.justice.gc.ca
- Irish legislation: irishstatutebook.ie
- Adapt word lists for jurisdiction-specific drafting conventions
- EU legislative drafting uses 'are prohibited', 'is prohibited' — already in word list

*Version 13 — May 2026. Corpus complete 212,183 rows. Six-category classification. Status filtering. Short act workbook. Replication guide. Classifier development next.*
