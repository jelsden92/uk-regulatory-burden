# UK Regulatory Burden Measurement Project

**Phase 1 Methodology**

_Draft — May 2026  |  Version 12  |  Corpus complete; validation in progress_

# 1. Overview and Motivation
This project creates the first comprehensive measure of the stock and flow of regulatory requirements in UK legislation. The methodology has been validated through ground truth analysis of 40+ Acts using a line-by-line manual classification workbook approach. Version 12 reflects completion of the corpus build phase and formalisation of key methodological decisions including the penalty-as-consequence rule, conditional obligation category, and Status filtering.

> Key contribution: First systematic, independently verifiable measure of prescriptive regulatory burden in UK legislation. Covers 212,183 pieces of legislation — 99.6%+ of modern SIs, 100% of significant post-1990 primary legislation. Six-way classification system. Validated against manually derived ground truth across 40+ Acts.

# 2. Classification System — Six Categories

| Classification | Description | Treatment |
| --- | --- | --- |
| private_actor | Direct standing obligations on any non-governmental party | HEADLINE METRIC |
| implied_burden | Obligations expressed as defences ('it is a defence to prove/show') | REPORTED SEPARATELY |
| implied_burden_active | Implied burden requiring active compliance programme ('adequate procedures') | REPORTED SEPARATELY |
| conditional_obligation | Obligations that activate only when a specific triggering event occurs — regulatory notice, licence grant, court order, regulatory inspection | REPORTED SEPARATELY |
| conditional_burden | Anti-avoidance provisions and purpose-based constraints | REPORTED SEPARATELY |
| public_body | Obligations on government ministers, regulators, courts, statutory bodies | EXCLUDED |
| ambiguous | Subject cannot be reliably determined — flagged for review | FLAGGED |

> CONDITIONAL OBLIGATION: Obligations that only activate when a specific triggering event occurs are classified as conditional_obligation. This includes: (1) regulatory enforcement actions — improvement notices, enforcement notices, remedial orders; (2) licensing conditions — obligations activated when a licence is granted; (3) regulatory inspection/seizure powers — private actors face a conditional burden of submission when a regulator suspects non-compliance, even without a finding of guilt. These represent genuine but contingent compliance costs, economically distinct from standing obligations.

> PENALTY-AS-CONSEQUENCE RULE: Criminal penalty provisions describing consequences of breaching an obligation stated elsewhere in the same Act are NOT counted as separate obligations. The regulatory burden consists of the underlying obligation, not the enforcement mechanism. The specific manner in which compliance must be demonstrated (e.g. supplying evidence to an authority) is part of the parent obligation, not a separate burden.

> UN-COMMENCED PROVISIONS: Provisions never brought into force are excluded. The CLML XML Status attribute is used — elements marked Prospective, Repealed, Dead, Discarded, or Prospective Repealed are stripped at parse time using BeautifulSoup decompose(). This removed 611,920 Repealed + 27,098 Prospective + 365 other no-force elements across the corpus.

# 3. Key Methodological Decisions
## 3.1 Penalty as Consequence
Criminal penalty provisions are consequences of obligations, not separate obligations. 'A person guilty of an offence shall be liable to imprisonment' — already counted when the offence was defined. 'A person who fails to comply with this Act shall be guilty of an offence' — consequence of the underlying obligation.

## 3.2 Conditional Burden vs Direct Burden
A burden is conditional when it only activates upon a triggering event. Examples: Noise Act 1996 s.8 — guilty of offence only if warning notice served (conditional). ELCI Act 1969 s.1 — every employer shall insure (standing/direct). Wild Mammals Act 1996 s.4 — must submit to search if constable suspects (conditional — the condition is suspicion, not guilt).

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
After subject classification, sentences are checked for conditional trigger phrases: 'if a warning notice has been served', 'if an enforcement notice has been served', 'where a notice has been served', 'if a licence has been granted', 'where a licence is in force', 'if an order has been made'. When present, classified as conditional_obligation.

# 5. Era-Aware Drafting

| Era | Key patterns | Treatment |
| --- | --- | --- |
| Pre-1920 Victorian | 'Shall be guilty of a misdemeanour/felony', 'shall forfeit and pay', 'every person who...shall be liable', material-as-subject drafting | Victorian obligation pre-check: [every/any + noun + who/that/which + penalty] = primary obligation |
| 1920-1970 | 'Shall operate to', 'shall take effect as', 'shall be deemed to', 'shall vest in' — deemed legal consequences not obligations | Added to DEFINITIONAL_PATTERNS — filters false positives in property and commercial law |
| 1970-2000 | 'Shall' dominant; EU-style 'are prohibited', 'is prohibited' enters post-1972 | Standard handling; EU prohibition vocabulary in PRESCRIPTIVE_WORDS |
| Post-2000 | 'Must' dominant; OPC drafting guidelines reserve 'must' for obligations | High confidence — 'must' almost always genuine obligation |

# 6. Corpus — Final State

| Metric | Value |
| --- | --- |
| Total legislation rows | 212,183 |
| Year range | 1267 – 2026 |
| Stream | B (current in-force) with Status filtering |
| uksi coverage | 43,272 / 43,463 = 99.6% |
| ssi coverage | 6,401 / 6,405 = 99.9% |
| wsi coverage | 3,395 / 3,406 = 99.7% |
| ukpga coverage | 3,226 / 3,762 = 85.8% (missing items are pre-1900 local/private Acts) |
| Significant post-1990 ukpga missing | Zero — 100% coverage |
| Status elements stripped | 611,920 Repealed + 27,098 Prospective + 365 other |
| Permanently unrecoverable | ~12,000 items (catalogued but never digitised) |
| Local/private Acts | Structural exclusion — XML not available via API |

> COVERAGE STATEMENT: The corpus covers 212,183 pieces of legislation — 99.6%+ of modern SIs, 100% of significant post-1990 primary legislation, and approximately 85-90% of all in-force legislation available as machine-readable XML on legislation.gov.uk. The remaining gap consists of local and private Acts structurally excluded from the National Archives API and pre-1948 legislation never digitised.

# 7. Validation Results — 40+ Act Sample
## 7.1 Manual Validation Workbook
Ground truth validation uses a structured Excel workbook (Reg_Burden_Project_Validation.xlsx) with columns: Act name, type, URL, burden sentence, section reference, Direct Burden, Implied Burden, Conditional Burden, Ambiguous, Claude agrees, Resolution. Each provision is classified manually and compared against analyser output sentence by sentence.

## 7.2 Short Act Validation Results

| Act | Manual count | Breakdown | Key finding |
| --- | --- | --- | --- |
| ELCI Act 1969 | 4 | 1 direct + 2 implied + 1 conditional | Insurance obligation + certificate display/production |
| Guard Dogs Act 1975 | 6 | 5 direct + 1 conditional | s.2 un-commenced — Status filtering now excludes correctly |
| Late Payment Act 1998 | 8 direct + 1 ambiguous | 8 direct | UCTA extensions as direct burdens; judicial discretion excluded |
| Noise Act 1996 | 1 conditional | 1 conditional | s.8 conditional on warning notice — paradigm case |
| Dangerous Dogs Act 1991 | 5 direct + 1 conditional | 5 prohibitions + s.3 conditional | s.3 out of control = conditional on dog's behaviour |
| Christmas Day Trading 2004 | 2 direct | 2 direct | Employment provisions in ERA 1996 not in Act itself |
| Wild Mammals Protection 1996 | 1 direct + 2 implied + 2 conditional | s.1 offence + s.2 defences + s.4 constable powers | Constable seizure = conditional burden on private actor |
| Theft Act 1978 | 1 direct | s.3 making off without payment | ss.1-2 repealed by Fraud Act 2006 — Status filtering critical |
| Corporate Manslaughter 2007 | 1 direct + 2 conditional | s.1 offence + s.9 remedial + s.10 publicity | Evidence supply = part of parent obligation not separate burden |

## 7.3 Key Methodological Findings from Short Act Validation
- Penalty-as-consequence: criminal enforcement provisions correctly excluded once the underlying obligation is counted
- Conditional burden scope: regulatory inspection/seizure powers create conditional burdens even where private actor is suspected not convicted — the condition is suspicion not guilt
- Evidence supply: requirement to supply evidence of compliance is part of parent obligation, not a separate burden
- Nested burdens: definitional provisions defining scope of primary obligations are not separate burdens
- Judicial discretion provisions: courts exercising discretion is not a private actor burden
- Un-commenced provisions: Status filtering now correctly excludes these — Guard Dogs Act s.2 paradigm case
- Christmas Day Trading Act: employment provisions inserted into ERA 1996 — obligations counted there not in the 2004 Act

# 8. Benchmark — Current Baselines

| Act | PA excl | IB | IBA |
| --- | --- | --- | --- |
| Financial Services and Markets Act 2000 | 397 | 1 | 0 |
| Employment Rights Act 1996 | 278 | 6 | 1 |
| Equality Act 2010 | 149 | 9 | 1 |
| Special School Residential Services (Wales) Regs 2024 | 144 | 0 | 0 |
| UK GDPR | 126 | 5 | 0 |
| Land Reform (Scotland) Act 2003 | 98 | 1 | 0 |
| Northern Ireland Act 1998 | 91 | 1 | 0 |
| Health and Safety at Work etc. Act 1974 | 56 | 0 | 0 |
| Competition Act 1998 | 40 | 0 | 0 |
| Environmental Permitting (E&W) Regulations 2016 | 14 | 1 | 0 |
| Explosives Act 1875 | 8 | 1 | 0 |
| Bribery Act 2010 | 6 | 2 | 1 |
| Occupiers Liability Act 1957 | 4 | 0 | 0 |
| Total | 1,411 | — | — |

# 9. Known Limitations
- Sub-clause overcounting: primary solution is classifier — not addressable by pattern matching without regression risk
- Framework Act overcounting: tier4_default false positives in administrative machinery — classifier primary solution
- Constitutional Act overcounting: electoral machinery partially addressed; classifier required for full fix
- Local and private Acts: structurally excluded — XML not available via API
- Pre-1948 legislation: ~12,000 items catalogued but never digitised — permanently unrecoverable
- Companies Act 2006: NOW IN CORPUS ✅ (previously flagged as missing)
- Freedom of Information Act 2000: NOW IN CORPUS ✅
- Devolution compliance: parallel E&W and Scotland provisions counted separately — methodologically intentional

*Version 12 — May 2026. Corpus complete at 212,183 rows. Six-way classification. Status filtering. Short act validation workbook. Penalty-as-consequence rule. Conditional obligation category formalised.*
