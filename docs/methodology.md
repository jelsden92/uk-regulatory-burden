# UK Regulatory Burden Measurement Project

**Phase 1 Methodology**

_Draft  |  Version 14  |  Corpus complete. **Classifier architecture reframed** (extraction → dual-model labelling → Legal-BERT); extraction rebuilt to a two-stage, section-level design._

> ARCHITECTURE NOTE (2026-06-14 reframe): The measurement *rules* in this document (what counts as a burden, the six categories, the decision rules) are unchanged and authoritative-pending-sign-off. What changed is *how classification is performed*. The rule-based analyser is **retired as a classifier**; only its extraction / candidate-filtering pipeline survives (`extract_candidates.py`). Classification is now: a high-recall candidate-extraction pipeline surfaces candidate provisions with context → Claude and Gemini classify them independently against the rubric → the human lead adjudicates disagreements → the validated labels train **Legal-BERT**, the production classifier. References below to the rule-based analyser / spaCy subject resolution describe the *retired* mechanism and are retained for history; the conceptual rules they implemented carry over to the rubric. The dropped work items (spaCy `trf` upgrade, Cat 2/Cat 5 rule-based detection, the `private_actor`→`direct_burden` tag migration) were obviated by this reframe.

> EXTRACTION UNIT (2026-07-03 rebuild): The candidate-extraction pipeline was rebuilt to a two-stage design. **The unit is the section/provision, not the sentence.** A DOM-keyed section anchor (outermost P-level for UK sections, EU articles and schedule P-levels, ∪ the innermost numbered `Division`/`Para` for EU recitals and schedule paragraphs) groups each provision and tags it with a `material_type`. **Stage 1** flags a whole section if any recall cue fires anywhere in it, so cue-less enumerated leaves are carried in on their chapeau rather than silently dropped (the earlier per-sentence emission dropped thousands of such leaves; the rebuild recovers them). Because one section can carry several distinct obligations — the unit-of-count rule (§ Decision Rules) governs how many — **Stage 2** (dual-model labelling; ratified design, not yet built) emits a **burden-set per section** with set-vs-set agreement. This does not change *what counts* as a burden; it changes the granularity at which candidates are surfaced and labelled, and closes the enumerated-leaf recall hole.

# 1. Overview and Motivation
This project creates the first comprehensive measure of the stock and flow of regulatory requirements in UK legislation. The methodology has been validated through ground truth analysis of 40+ Acts using a line-by-line manual classification workbook approach. Version 14 reflects completion of the corpus build phase and formalisation of key methodological decisions including the penalty-as-consequence rule, conditional obligation category, and Status filtering.

> Key contribution: First systematic, independently verifiable measure of prescriptive regulatory burden in UK legislation. Corpus comprises **69,885 fully digitised pieces of in-force UK legislation** — 100 % of the items that legislation.gov.uk currently exposes with substantive machine-readable XML, within a wider National Archives in-force universe of 119,841 catalogued items. Coverage is reported at three nested scopes: 58.3 % across the full universe, 77.8 % excluding local & private Acts, 91.6 % for post-1990 general-application legislation. Six-way classification system. Validated against manually derived ground truth across 40+ Acts.

# 2. Classification System

**Headline metric: total private actor burden = direct + implied + conditional obligations combined.** The three groups capture economically distinct compliance costs that all fall on non-governmental actors; they are presented as a breakdown of the headline total rather than as separate metrics. Public body obligations are excluded; ambiguous sentences are flagged for review.

| Group | Classification | Description | Role in headline |
| --- | --- | --- | --- |
| **Direct** | private_actor | Direct standing obligations on any non-governmental party | Part of headline total |
| **Implied** | implied_burden | Obligations expressed as defences ('it is a defence to prove/show') | Part of headline total |
| **Implied** | implied_burden_active | Implied burden requiring active compliance programme ('adequate procedures') | Part of headline total |
| **Conditional** | conditional_obligation | Obligations that activate only when a specific triggering event occurs — regulatory notice, licence grant, court order, regulatory inspection | Part of headline total |
| **Conditional** | conditional_burden | Anti-avoidance provisions and purpose-based constraints | Part of headline total |
| — | public_body | Obligations on government ministers, regulators, courts, statutory bodies | EXCLUDED |
| — | ambiguous | Subject cannot be reliably determined — flagged for review | FLAGGED |

> CONDITIONAL OBLIGATION: Obligations that only activate when a specific triggering event occurs are classified as conditional_obligation. This includes: (1) regulatory enforcement actions — improvement notices, enforcement notices, remedial orders; (2) specific obligations attached to a licence's conditions once it has been granted and that would not exist absent that grant; (3) regulatory inspection/seizure powers — private actors face a conditional burden of submission when a regulator suspects non-compliance, even without a finding of guilt. These represent genuine but contingent compliance costs, economically distinct from standing obligations.
>
> LICENCE TO OPERATE IS A DIRECT BURDEN (not conditional): The requirement to hold or maintain a licence, permit, registration, or authorisation in order to carry on an activity at all is a **Direct burden** — a standing constraint on operating, present continuously and not contingent on any external triggering event. It is classified as direct, never as a conditional obligation. The contingency in a conditional obligation is an external event (a notice served, an inspection, an order made); the contingency in "you may not operate without a licence" is the actor's own continuing choice to operate, which is exactly what a standing constraint is. Only obligations arising from the *specific conditions* of a licence once granted (item (2) above) are conditional — the duty to hold the licence itself is direct.

> PENALTY-AS-CONSEQUENCE RULE: Criminal penalty provisions describing consequences of breaching an obligation stated elsewhere in the same Act are NOT counted as separate obligations. The regulatory burden consists of the underlying obligation, not the enforcement mechanism. The specific manner in which compliance must be demonstrated (e.g. supplying evidence to an authority) is part of the parent obligation, not a separate burden.

> UN-COMMENCED PROVISIONS: Provisions never brought into force are excluded. The CLML XML Status attribute is used — elements marked Prospective, Repealed, Dead, Discarded, or Prospective Repealed are stripped at parse time using BeautifulSoup decompose(). This removed 611,920 Repealed + 27,098 Prospective + 365 other no-force elements across the corpus.

# 3. Key Methodological Decisions
## 3.1 Penalty as Consequence
Criminal penalty provisions are consequences of obligations, not separate obligations. 'A person guilty of an offence shall be liable to imprisonment' — already counted when the offence was defined. 'A person who fails to comply with this Act shall be guilty of an offence' — consequence of the underlying obligation.

## 3.2 Conditional Burden vs Direct Burden
A burden is conditional when it only activates upon a triggering event. Examples: Noise Act 1996 s.8 — guilty of offence only if warning notice served (conditional). ELCI Act 1969 s.1 — every employer shall insure (standing/direct). Wild Mammals Act 1996 s.4 — must submit to search if constable suspects (conditional — the condition is suspicion, not guilt).

**Licence to operate is Direct, not conditional.** A requirement to hold or maintain a licence, permit, registration, or authorisation in order to carry on an activity (e.g. "a person shall not carry on a regulated activity unless authorised", "an operator must hold a licence", "the holder shall maintain the licence in force") is a Direct burden: a standing constraint on operating that applies continuously for as long as the actor operates. It is not contingent on any external regulatory event, so it is never classified as a conditional obligation. The distinction: the requirement *to hold* the licence is direct; an obligation that arises only from the *specific conditions* of a licence once granted, and would not exist absent that grant, is conditional. In the classifier this falls out naturally — such provisions match a prescriptive term ("shall not", "must", "may not") and are classified as direct via normal subject resolution; no licence-grant phrase is treated as a conditional trigger.

## 3.3 Implied Burden
Defence provisions revealing standing compliance obligations: 'if he shows that' / 'it is a defence to prove that' creates an implied burden to maintain evidence and records. Distinct from conditional burden — implied burdens are standing obligations revealed through defence structure; conditional burdens activate on external triggers.

## 3.4 Definitional Tests vs Prohibitions
A definitional standard embedded in a prohibition is not a separate burden. 'Contract terms are void unless there is a substantial remedy' — one burden (the prohibition on contracting out). 'A remedy shall be regarded as substantial unless...' — the definitional test, not a separate burden. Counting both would be double-counting.

## 3.5 Evidence Supply as Part of Parent Obligation
Where a provision requires an organisation to supply evidence of compliance to an authority, this is part of the parent obligation not a separate burden. Corporate Manslaughter Act s.9(4)(b) — supply evidence that remedial steps taken — is part of the s.9 remedial order obligation.

## 3.6 Nested Burdens
Some definitional provisions define the scope of who bears a primary obligation. Corporate Manslaughter Act s.2 defines 'relevant duty of care' — determining which organisations face the s.1 obligation. These are scope definitions not additional burdens. The primary obligation is s.1; s.2 defines its application.

# 4. Prescriptive Language — Key Terms
## 4.1 Obligation Terms (selected)

| Term | Notes |
| --- | --- |
| shall / must | Core terms. |
| is required to / are required to / is to / are to | Standard obligations. |
| has a duty to / it is the duty of / it shall be the duty of | Formal duty imposition. |
| is under a duty to / is under an obligation to / is subject to a duty | Duty variants. |
| shall disclose / shall declare | Disclosure obligations — financial services, company law. |
| has the right not to be subjected / has the right not to be dismissed | Anti-retaliation provisions expressed as worker rights — employer obligations. |
| owes a duty / owes the same duty | Common law duty codifications. POSITIVE_ID_REQUIRED. |
| commits an offence if / is guilty of an offence / shall be guilty of an offence | Criminal prohibitions. Subject to guilt cross-reference check. |
| shall be guilty of a misdemeanour / shall be guilty of a felony | Victorian criminal terminology. |
| there is implied / there shall be implied / it is an implied term / there is an implied term | Implied term obligations — LTA 1985, Sale of Goods, Late Payment Act. |
| the parties | Added to PRIVATE_ACTOR_SUBJECTS — Late Payment Act and commercial contract law. |

## 4.2 Hierarchical Penalty Filtering
PENALTY_ONLY_TERMS ('shall be liable to', 'is liable to' etc.) are filtered when a cross-reference marker is present ('guilty of an offence under', 'contravenes this Act', 'fails to comply with this Act'). Without cross-reference — the penalty IS the primary obligation — classified normally.

## 4.3 Conditional Obligation Detection
After subject classification, sentences are checked for conditional trigger phrases: 'if a warning notice has been served', 'if an enforcement notice has been served', 'where a notice has been served', 'if an order has been made'. When present, classified as conditional_obligation. Note: phrases such as 'where a licence is in force' or 'if a licence has been granted' are **not** by themselves conditional triggers — the standing requirement to hold a licence to operate is a Direct burden (§3.2). Only a distinct obligation arising from the licence's specific conditions once granted is conditional.

# 5. Era-Aware Drafting

| Era | Key patterns | Treatment |
| --- | --- | --- |
| Pre-1920 Victorian | 'Shall be guilty of a misdemeanour/felony', 'shall forfeit and pay', 'every person who...shall be liable', material-as-subject drafting | Victorian obligation pre-check: [every/any + noun + who/that/which + penalty] = primary obligation |
| 1920-1970 | 'Shall operate to', 'shall take effect as', 'shall be deemed to', 'shall vest in' — deemed legal consequences not obligations | Added to DEFINITIONAL_PATTERNS — filters false positives in property and commercial law |
| 1970-2000 | 'Shall' dominant; EU-style 'are prohibited', 'is prohibited' enters post-1972 | Standard handling; EU prohibition vocabulary in PRESCRIPTIVE_WORDS |
| Post-2000 | 'Must' dominant; OPC drafting guidelines reserve 'must' for obligations | High confidence — 'must' almost always genuine obligation |

# 6. Corpus — Final State

The corpus is built against the National Archives InForce CSV manifests under a definitional rule covering `InForce`, `InForce1991`, `LimitedApplication`, and any jurisdiction- or savings-qualified partial-revocation/repeal status — i.e. any item that imposes legal obligations somewhere in the UK at the snapshot date. The wider catalogued universe contains 119,841 unique items. Within that universe, items fall into three tiers of digitisation status. The analyser operates on Tier 1 only.

### The three-tier digitisation hierarchy

| Tier | Description | Items | % of universe |
| --- | --- | ---: | ---: |
| **Tier 1 — Fully digitised** | `/data.xml` returns substantive XML with `NumberOfProvisions > 0`; corpus row has `full_text >= 200` chars. **This is the analyser input — the headline corpus figure.** | **69,885** | **58.3 %** |
| Tier 2 — Retrieved but metadata-only | `/data.xml` returns valid XML with `NumberOfProvisions = 0` (title, year, number, PDF link only), or content stripped at parse time as Prospective/Repealed. Row exists in `legislation.db` with `na_inforce = 1` but no analyser-usable body text. | 31,407 | 26.2 % |
| Tier 3 — Not digitised at all | `/data.xml` returns HTTP 404. Item is catalogued in the InForce manifest but has no XML or HTML representation on legislation.gov.uk. | 18,505 | 15.4 % |
| **Total — In-force universe** | National Archives InForce manifest under the in-force definitional rule | **119,841** | 100.0 % |

| Metric | Value |
| --- | --- |
| **Headline corpus figure (Tier 1, analyser input)** | **69,885** |
| In-force universe (National Archives InForce manifests) | 119,841 |
| `legislation.db` total rows | 218,089 |
| Rows flagged `na_inforce = 1` | 85,358 |
| Year range | 1267 – 2026 |
| Stream | B (current in-force) with Status filtering |
| Status elements stripped at parse time | 611,920 Repealed + 27,098 Prospective + 365 other |

### Scope-stratified coverage

| Scope | Description | In-force universe | In corpus | Coverage |
| --- | --- | ---: | ---: | ---: |
| **A — Full universe** | Every in-force item across all 28 leg_types | 119,841 | 69,885 | **58.3 %** |
| **B — General application** | Excludes ukla / ukppa / gbppa / eppa / gbla / uklp | 89,548 | 69,695 | **77.8 %** |
| **C — Post-1990 general application** | Scope B AND year ≥ 1990 | 67,403 | 61,745 | **91.6 %** |

Full per-type breakdown: [`coverage_table.csv`](coverage_table.csv). Methodology, exhaustion sweep, and structural-gap characterisation: [`coverage_methodology_note.md`](coverage_methodology_note.md).

> CORPUS STATEMENT: The analyser operates on **69,885 fully digitised pieces of in-force UK legislation** — every item from the National Archives InForce manifests that legislation.gov.uk currently exposes with substantive machine-readable XML, after an exhaustion sweep across every retrieval channel (`/data.xml`, `/data.xml?version=enacted`, `/enacted/data.xml`, `/data.xht`, `/data.akn`, `/data.feed`) and a full cross-reference against the legislation.gov.uk Best Collection bulk download. Coverage on the full in-force universe is 58.3 %; excluding local and private Acts (which apply only to named persons, places, or institutions and do not impose general-application obligations) raises this to 77.8 %; restricting to post-1990 general-application law raises it to 91.6 %. The remaining structural gap (Tier 2 digitised-but-no-analyser-usable-text, 31,407; Tier 3 not digitised, 18,505) cannot be brought into the analyser without either further National Archives digitisation or an OCR pipeline against original-print PDFs; neither falls within the methodology of this study.

# 7. Validation Approach

## 7.1 Manual Validation Workbook
Ground truth validation uses a structured Excel workbook (Reg_Burden_Project_Validation.xlsx) with columns: Act name, type, URL, burden sentence, section reference, Direct Burden, Implied Burden, Conditional Burden, Ambiguous, Claude agrees, Resolution. Each provision is classified manually.

Under the reframed architecture the workbook now serves three roles: (1) **ground truth for the rubric** against which the dual-model (Claude + Gemini) labels are adjudicated; (2) the **recall check for the candidate-extraction filter** — every manually-identified burden must be surfaced by the high-recall filter (a dropped burden is an uncorrectable silent false negative); (3) **seed training data for Legal-BERT**. It is no longer used to tune a rule-based classifier.

## 7.2 Short Act Validation Sample

Manual ground-truth validation has been completed for a short-Act sample spanning insurance, dangerous-animal law, criminal law, commercial debt, environmental protection, employment, and corporate liability. The sample covers the four sub-categories of private-actor burden (direct, implied, conditional obligation, conditional burden), provides paradigm cases for each, and stress-tests the penalty-as-consequence, evidence-supply, and Status-filter rules against historical Acts. Per-Act validation counts are not published here ahead of the forthcoming think tank paper.

## 7.3 Key Methodological Findings from Short Act Validation
- Penalty-as-consequence: criminal enforcement provisions correctly excluded once the underlying obligation is counted
- Conditional burden scope: regulatory inspection/seizure powers create conditional burdens even where private actor is suspected not convicted — the condition is suspicion not guilt
- Evidence supply: requirement to supply evidence of compliance is part of parent obligation, not a separate burden
- Nested burdens: definitional provisions defining scope of primary obligations are not separate burdens
- Judicial discretion provisions: courts exercising discretion is not a private actor burden
- Un-commenced provisions: Status filtering now correctly excludes these — Guard Dogs Act s.2 paradigm case
- Christmas Day Trading Act: employment provisions inserted into ERA 1996 — obligations counted there not in the 2004 Act

# 8. Benchmark Validation

The methodology has been validated against a 13-act core benchmark suite spanning diverse legislative categories — criminal law, employment, financial services, environmental regulation, consumer protection, and devolved legislation. Benchmark counts are not published here ahead of the forthcoming think tank paper.

# 9. Relationship to the National Archives Statutory Powers and Duties Dataset

In May 2026 the National Archives released the *Statutory Powers and Duties Dataset* — a 1.84-million-row corpus of duty and power statements generated by Claude Sonnet 4.5 over the UK in-force statute book. Each row carries an `enactment`, `section`, `actor` (free-text), `modality` (`duty` or `power`), `condition`, `inference` (`explicit` or `implicit`), and `priority` (`primary` or `secondary`). The dataset covers most of the same legislation as this project's corpus.

**It is not equivalent to a regulatory-burden measure.** Three structural reasons:

1. **No private/public actor classification.** TNA's `actor` field is free text and mixes "Secretary of State", "court", "regulator" with "applicant", "operator", "manufacturer", "company". The `actorIsBody` flag is populated for only ~19 % of rows. Filtering to "duties on private actors" — the bedrock of regulatory-burden measurement — requires a classifier the TNA dataset does not provide.

2. **Offence-as-obligation provisions are systematically undercounted.** Provisions that create offences ("a person who … is guilty of an offence") impose obligations *not to* commit the prohibited act and are captured by this project as direct burdens. Validation against ten Acts in the project's manual workbook shows TNA records zero rows for several such provisions — Theft Act 1978 s.3(1), Knives Act 1997 s.1(1), Wild Mammals (Protection) Act 1996 s.1, Corporate Manslaughter and Corporate Homicide Act 2007 s.1(1).

3. **The `condition` field is over-populated relative to a true "conditional obligation" category.** TNA marks `condition` for any structural "if X then Y" framing (~70 % of rows), whereas this project reserves the conditional category for obligations triggered by external regulatory action (enforcement notices, licence conditions, inspection powers).

**What this project adds on top of TNA's data:**

- A private/public actor classifier, built around `word_list.PUBLIC_BODY`, `word_list.PRIVATE_ACTOR`, and the three-tier subject-resolution default in `analyser.classify_subject_spacy`.
- The penalty-as-consequence rule (§3.1) preventing offence + penalty double-counting.
- Offence-as-obligation capture: prohibition-style provisions enter the corpus as direct burdens.
- A narrower definition of conditional obligation (§3.2) tied to enforcement-action triggers.
- A manual ground-truth validation workbook against which classifier outputs are assessed.
- The regulatory-burden framing itself — selecting which provisions impose compliance cost on non-governmental actors, rather than enumerating all powers and duties of all actors.

**Adopting TNA's dataset as an additional validation layer.** The two datasets cover overlapping ground but with different decompositions, so cross-referencing them surfaces classification errors on both sides. The cross-check method is documented in `tna_crosscheck_methodology.md`; in summary, every sentence this project flags as `private_actor` in the 13-Act benchmark is checked against TNA's rows for the same Act and section. If TNA records a clearly-public-body actor at that section (Secretary of State, court, tribunal, regulator, constable, justice of the peace, registrar, Lord Chancellor, Treasury, HMRC, commissioner, police), the project's classification is flagged as a candidate false positive for manual review. Initial run: 515 candidate FPs from 1,697 `private_actor` classifications across the 13-Act benchmark (30.3 %). Manual review of these candidates is documented in the workbook; surviving candidates feed back into classifier refinements.

# 10. Known Limitations
- **Rule-based over-identification (PRELIMINARY — not established):** a preliminary read indicated the *retired* rule-based analyser over-identified private-actor obligations (non-operative modality the main driver). The precise rate awaits a larger randomised unflagged sample and must be treated as a preliminary finding, **not a published figure**. It is part of the rationale for the reframe to dual-model + Legal-BERT classification, not a result.
- Sub-clause overcounting: addressed by the Legal-BERT classifier layer, not by pattern matching (which carried regression risk)
- Framework Act overcounting: rule-based `tier4_default` false positives in administrative machinery — resolved by moving classification to the LLM+human+Legal-BERT layer
- Constitutional Act overcounting: electoral machinery — same resolution (classification layer, not keyword rules)
- Local and private Acts: structurally excluded — XML not available via API (~30,000 items catalogued as metadata-only shells on legislation.gov.uk)
- Pre-1948 statutory instruments and historical primary legislation: catalogued but never digitised with substantive XML — recovery would require an OCR pipeline against original-print PDFs
- Companies Act 2006: NOW IN CORPUS ✅ (previously flagged as missing)
- Freedom of Information Act 2000: NOW IN CORPUS ✅
- Devolution compliance: parallel E&W and Scotland provisions counted separately — methodologically intentional

*Version 14. Corpus complete: 69,885 fully digitised pieces of in-force UK legislation, within a wider National Archives in-force universe of 119,841 catalogued items. Coverage at three nested scopes: 58.3 % full universe / 77.8 % excluding local & private Acts / 91.6 % post-1990 general application. Classifier architecture reframed: high-recall extraction (`extract_candidates.py`, reading locally-cached bulk XML — revised-current primary / best-collection fallback) → dual-model (Claude + Gemini) labelling against the rubric → human adjudication → Legal-BERT production classifier. Extraction rebuilt (2026-07-03) to a two-stage, section-level design: DOM-keyed section anchor, Stage-1 subtree flagging, assembled chapeau+leaves with no truncation; Stage-2 burden-set-per-section labelling is ratified design, not yet built. Rule-based classifier retired (extraction pipeline survives). trf upgrade, Cat 2/5 rule-based fixes, and the tag migration dropped as obviated. Six-category rubric + polarity. Status filtering. Short act validation workbook. Penalty-as-consequence rule. Conditional split (organic vs external trigger) formalised. Licence-to-operate as Direct burden.*
