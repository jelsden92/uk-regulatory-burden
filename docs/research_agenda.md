# UK Regulatory Burden Measurement

**Research Agenda: Issues, Open Questions and Future Phases**

_June 2026  |  Version 10 — **Architecture reframed: extraction pipeline → dual-model labelling → Legal-BERT**_

> VERSION 10 UPDATE (2026-06-14 REFRAME — central change): We are **no longer fixing the rule-based classifier.** The architecture is now: a high-recall candidate-extraction pipeline (`extract_candidates.py`) surfaces candidate burden sentences with context; Claude and Gemini independently classify them against the rubric; the human lead adjudicates disagreements; the validated labels train **Legal-BERT**, the production classifier that runs the corpus. The rule-based classifier is retired *as a classifier* — only its extraction / candidate-filtering pipeline survives.
>
> **DROPPED / superseded by the reframe** (one line why): **trf spaCy upgrade** — only served rule-based subject resolution, replaced by Legal-BERT + LLM labelling; **Cat 2 / Cat 5 classifier fixes** — the filter only surfaces, the LLM+human layer assigns category; **`private_actor`→`direct_burden` tag migration** — rule-based output retired, nothing to migrate (rubric tags become the label schema).
>
> **RESOLVED**: the structured CLML XML is cached locally in `Bulk download/` (~98%+ corpus coverage) — **no 69k crawl is needed, ever.** Parsing source priority is **revised-current PRIMARY, best-collection FALLBACK** (this reversed an earlier "best-collection only" conclusion: BC serves stale *as-made* text for thousands of amended SIs and lacks 7 in-force retained-EU items present only in revised-current).
>
> **LIVE NEXT STEPS**: repoint `extract_candidates.py` to read the local bulk downloads (revised-current primary, BC fallback, variants read from files not the stale `best_collection_index.json`); hold the cue inventory / high-recall discipline as the measurement ceiling; dual-model labelling + human-adjudication workflow; build validated training data toward Legal-BERT; **rubric v2 awaiting the project lead's full sign-off before it is authoritative**; deferred line-by-line calibration reads once the pipeline is stable.
>
> **QUEUED FOR LATER (corpus-run-time, not now)**: physical `analyser.py` deletion + dependent-script cleanup (currently retired via banner); a variant-aware, priority-resolved local file index; a small *targeted* fetch of the exhaustion-sweep gap-fillers (~1,082 bulk-absent items, one at a time). **STILL RUNNING**: the Colab API-exhaustion sweep.
>
> Corpus state (unchanged): 212,183 rows, 69,462 distinct in-force items, 99.6%+ SI coverage, status filtering removing 639,000+ no-force elements. Short-act validation workbook established. Methodological decisions formalised: penalty-as-consequence, the Cat 2 (organic trigger) vs Cat 5 (external-authority trigger) split, evidence supply as part of parent obligation, nested burdens, licence-to-operate as Direct.

# PART 1 — Novel Contributions

| Contribution | Significance |
| --- | --- |
| Conditional obligation category | Captures obligations triggered by regulatory action including inspection/seizure powers — not measured by QuantGov |
| Implied burden category | Captures 'failure to prevent' obligations invisible to word counting |
| Penalty-as-consequence rule | Criminal enforcement provisions correctly excluded — methodological rigour over QuantGov |
| Status filtering | 611,920+ repealed/prospective elements excluded — genuinely current regulatory burden only |
| Devolution compliance premium | First quantification of compliance cost of UK regulatory fragmentation |
| Four-nation territorial decomposition | Scotland/Wales/NI specific analysis |
| Subject classification | Separates private actor from public body |
| Era-aware drafting conventions | Accounts for 'shall' meaning different things across legislative eras |
| Short act validation workbook | Line-by-line ground truth with direct/implied/conditional/ambiguous taxonomy |
| 212,183 item corpus | 99.6%+ modern SI coverage — most comprehensive UK legislative dataset for regulatory analysis |

# PART 2 — Corpus Final State

| Source | Items added | Coverage achieved |
| --- | --- | --- |
| Revised Current bulk download | 72,681 | Primary legislation ~86%; SIs ~11% |
| Best Collection bulk download | 63,536 | Filled enacted-only SIs |
| Missing SI fill (uksi/ssi/nisr/wsi) | 54,484 | uksi 11% → 99.6% |
| UnknownStatusPDFOnly | 14,895 | 20,262 items with XML despite PDF label |
| InForce1991 | 2,793 | In force at the 1 Feb 1991 *Statutes in Force* base date (the foundation of the Statute Law Database); 6,892 such items in the universe, 2,793 ingested here |
| JurisdictionLimited | 2,931 | Items in force in some jurisdictions only |
| Retry sweep | 546 | Partial recovery of network failures |
| Total | 212,183 | 99.6%+ modern SIs; 100% post-1990 Acts |

# PART 3 — Validation Roadmap
## Short Act Manual Validation (current phase)

Manual ground-truth validation has been completed for a short-Act sample spanning insurance, dangerous-animal law, criminal law, commercial debt, environmental protection, employment, and corporate liability. The sample covers the four sub-categories of private-actor burden (direct, implied, conditional obligation, conditional burden) and is used as paradigm cases for classifier development. Per-Act counts are not published here ahead of the forthcoming think tank paper.

## Next 12 Short Acts for Manual Review

| Act | URL | Category |
| --- | --- | --- |
| Knives Act 1997 | ukpga/1997/21 | Criminal |
| Firearms (Amendment) Act 1997 | ukpga/1997/5 | Criminal |
| Fireworks Act 2003 | ukpga/2003/22 | Consumer/commercial |
| Gangmasters (Licensing) Act 2004 | ukpga/2004/11 | Licensing |
| Sunday Trading Act 1994 | ukpga/1994/20 | Commercial |
| Deer Act 1991 | ukpga/1991/54 | Environmental |
| Protection of Badgers Act 1992 | ukpga/1992/51 | Environmental |
| Dog Fouling (Scotland) Act 2003 | asp/2003/12 | Scottish Parliament |
| Environment (Wales) Act 2016 | anaw/2016/3 | Welsh legislation |
| Financial Services (Distance Marketing) Regs 2004 | uksi/2004/2095 | Financial services SI |
| Parental Bereavement Leave Regs 2020 | uksi/2020/249 | Employment SI |
| Sale of Food and Drugs Act 1875 | ukpga/1875/63 | Victorian |

## Victorian/Pre-War Acts — Classifier Training Priority
The classifier needs training examples from Victorian and pre-war legislation to handle archaic drafting conventions. Target 5-6 Victorian Acts out of the 20 manual reviews. Priority candidates:
- Pawnbrokers Act 1872 — early licensing obligations
- Sale of Food and Drugs Act 1875 — food adulteration prohibitions
- Truck Act 1831 — employer wage payment obligations
- Celluloid and Cinematograph Film Act 1922 — fire safety obligations
- Conspiracy and Protection of Property Act 1875 — industrial relations

# PART 4 — Classifier Development (REFRAMED)

The classifier is no longer the rule-based analyser. Pipeline: **high-recall extraction → dual-model (Claude + Gemini) labelling against the rubric → human adjudication of disagreements → Legal-BERT trained on the validated labels (production).** The candidate filter's recall is the ceiling for both training data and production — a dropped candidate is an uncorrectable silent false negative — so recall discipline (the `word_list` cue union, audited empirically against ground truth) is the measurement ceiling.

| Phase | Input | Target | Status |
| --- | --- | --- | --- |
| Extraction pipeline | locally-cached bulk XML | high-recall candidate JSONL + context | `extract_candidates.py` built; **repoint to local bulk next** |
| Dual-model labelling | candidate sentences + rubric | independent Claude/Gemini labels; disagreements → review | workflow to operationalise |
| Human adjudication | disagreement + hard-case queue | validated training labels | ongoing via workbook + rubric |
| Legal-BERT (production) | validated labels | fine-tuned classifier runs the corpus | after sufficient labelled data |
| Active learning | low-confidence / disagreement cases | iterative accuracy gains | post-initial-train |

> PRELIMINARY (not established): a preliminary read indicated the *retired* rule-based analyser over-identified private-actor obligations; the precise rate awaits a larger randomised unflagged sample and must be treated as a preliminary finding, not a published figure. It is part of the rationale for the reframe, not a result.

# PART 5 — Future Phases
- Phase 2 — Regulatory rulebooks (FCA Handbook, PRA Rulebook)
- Phase 3 — Monetisation and sectoral attribution
- Phase 4 — Planning system
- Phase 5 — Professional regulatory bodies
- Phase 6 — Post-Brexit divergence tracking
- Phase 7 — International comparisons
- Phase 8 — Productivity link

*Version 9 — May 2026. Corpus complete 212,183 rows. Short act validation workbook. Classifier development next.*
