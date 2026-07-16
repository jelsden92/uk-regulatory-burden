# UK Regulatory Burden Measurement

**Phase 1 Implementation Plan  —  Version 15**

_July 2026  |  Corpus complete. **Architecture reframed: extraction pipeline → dual-model labelling → Legal-BERT.** Extraction rebuilt to a two-stage, section-level design (2026-07-03). Rule-based classifier retired._

> STATUS: Corpus complete (212,183 rows; 98%+ structured XML cached locally). The rule-based classifier is **retired as a classifier** — only its extraction / candidate-filtering pipeline survives. Classification now: a high-recall candidate-extraction pipeline surfaces candidate burden sentences with context; Claude and Gemini independently classify them against the rubric; the human lead adjudicates disagreements; the validated labels train **Legal-BERT**, which is the production classifier that runs the corpus.

# Architecture (2026-06-14 REFRAME — central change)

The earlier plan was to keep fixing the rule-based classifier (`analyser.py`) and run it over the corpus. **That is superseded.** The rule-based keyword/subject-resolution classification was tuned for precision and was, on a preliminary read, **over-identifying private-actor obligations** (precise rate pending a larger unflagged sample — see Limitations; treat as a *preliminary* finding, not established). The new architecture:

1. **`extract_candidates.py` — high-recall, two-stage candidate pipeline (rebuilt 2026-07-03).** Reuses `downloader`'s ingest + CLML status filter and the `word_list` vocabulary. **The unit is the section/provision, not the sentence.** A DOM-keyed section anchor groups each provision — outermost P-level (UK sections / EU articles / schedule P-levels) ∪ innermost numbered `Division`/`Para` (EU recitals, schedule paragraphs) — tagged with `material_type` (uk_body / uk_schedule / eu_article / eu_recital / orphan). **Stage 1** flags a section if ≥1 recall cue fires *anywhere in its subtree*, so a cue-less enumerated leaf rides in on its chapeau's cue instead of being silently dropped (the previous per-sentence emission dropped ~7,786 such leaves across the 7-Act set; the rebuild recovers 6,051 of them). Each flagged section is emitted as ONE candidate: the full assembled block (chapeau + leaves, markers/structure preserved, **no truncation** — the old `sentence[:2000]` cap is removed), plus `leaves[]` as a structured list. Keyed on DOM node identity (`section_index`), never `section_ref` (which is non-unique — "24(1)" maps to five distinct provisions in EP Regs). `candidate_cue` / `material_type` / `is_in_schedule` are HINTS; no category/polarity label is emitted here.
2. **Dual-model labelling (RATIFIED DESIGN — not yet built).** Because the candidate unit is the section and one section may carry several distinct burdens, Stage 2 emits a **burden-set per section** (optimised for the common 1–2-burden case but structurally able to represent the multi-duty tail). Claude and Gemini independently decompose and classify each section against the rubric (six categories + polarity), and agreement is **set-vs-set** (same count, same per-burden labels), not single-label match. The label store / version-control is established here before any real label is emitted. This is the next deliberate design step.

**Record schema notes (ratified 2026-07-06).** A burden record carries `{category, polarity, obligated_party, actor_capacity, provenance, orphan, family_id}` (`orphan=true` for records that came through the orphan-triage lane — see `docs/decision_tree_gaps.md` G25; `family_id` nullable, populated by the post-labelling devolution family-linker — see `docs/decision_tree_gaps.md` G18). Devolution / parallel-instrument duplicates use a **two-lens** design: the **primary count is residence-based** (parallel jurisdictional instruments count separately, no similarity test on the spine), and a separate **enrichment lens** links duplicate families (`family_id`; uniform/divergent) to answer the "distinct regulatory control" question — built post-labelling, pre-publication; the methodology reports both lenses (G18). A candidate that carries **no** burden is stored as a first-class **typed exclusion**, not an empty set: `exclusion_family` ∈ {`non_operative`, `amendment_machinery`, `counted_at_source`, `public_body_or_no_one`} plus a best-effort `exclusion_subclass` (fine-grained, two-tier). Dual-model agreement on exclusions is computed on the **family only** (family disagreements → review; sub-class mismatches within an agreed family are logged, not adjudicated). Full design and rationale: `docs/decision_tree_gaps.md` G2. The orphan lane's triage output uses the same exclusion fields. A burden counted as a **frontier proxy** under the deepest-visible-layer rule (rubric §3 — a statutory duty to comply with an *out-of-measure* instrument: permit/licence/notice, byelaw, regulator rulebook) additionally carries `frontier_hook = true` and `frontier_target_type` ∈ {`permit_licence`, `notice`, `byelaw`, `regulator_rulebook`, `other`}, making the proxy population enumerable so a future scope expansion (re-classifying proxies to `counted_at_source` as the layer's own contents are counted) is a query, not archaeology.

Any record routed to review also carries two **review-metadata** fields (present from the first pilot adjudication): `review_reason` — primary (the route that fired first in tree order) + optional secondary — ∈ {`model_disagreement`, `hybrid_actor`, `ambiguous_leaf`, `cat6_category`, `polarity_review`, `orphan_escalation`, `context_term`, , `low_confidence` and `family_link` reserved for production}; and `feeds` (recorded at resolution) ∈ {`registry`, `rubric_example`, `unit_rule_evidence`, `training_data`, `definitions`}, so adjudication harvest is mechanical. This is a **schema, not queue tooling** — lanes are just `review_reason`-sorted records. The **same schema serves both phases**: dual-model disagreement is the training-data-phase uncertainty signal, while in production Legal-BERT's `low_confidence` routes to review where disagreement did (rules-layer lanes and the random audit run unchanged through both). Full design: `docs/decision_tree_gaps.md` G21.
3. **Human adjudication.** Agreements → high confidence + light spot-check; disagreements (category OR polarity) → the high-value review queue, adjudicated by the human lead against the rubric.
4. **Legal-BERT (production classifier).** The validated labels train a fine-tuned Legal-BERT, which runs the full corpus. The same extraction pipeline feeds it.

The rubric (`uk_reg_validation_rubric_v2_draft.docx`) is the conceptual classification guide for steps 2–3. It is **awaiting the project lead's full sign-off before it is authoritative (v1.0).**

# DROPPED / SUPERSEDED by the reframe

| Item | Why dropped |
| --- | --- |
| **spaCy `en_core_web_trf` upgrade** | Only served rule-based *subject resolution*, which Legal-BERT + LLM labelling replaces. (`SPACY_MODEL` constant landed; validation runs cancelled.) |
| **Category 2 / Category 5 classifier fixes** (`conditional_direct` detection; redefining `conditional_burden`) | The candidate filter only needs to *surface* these sentences; the LLM+human layer assigns the category. No rule-based heuristic needed. |
| **`private_actor` → `direct_burden` tag migration** | The rule-based classification output is retired, so there is nothing to migrate. The rubric tags become the LLM/Legal-BERT label schema (greenfield), not a DB migration. |

# RESOLVED — structured XML is cached locally (no corpus crawl, ever)

The raw structured CLML XML is already on disk in `Bulk download/` — the DB storing only flattened text did not mean the source XML was gone. **~98% of the in-force corpus (68,380 / 69,462) is on disk;** no 69k-item crawl of legislation.gov.uk is required.

- **Source priority (decisive, per distinct item_url):** revised-current's `revised` variant → best-collection's `revised` variant where RC lacks it → `made`/`enacted` ONLY where no revision exists in either source. This **reversed an earlier "best-collection only" conclusion**: best-collection serves stale *as-made* text for thousands of amended SIs (51,255 corpus SIs are `made`-only in BC; ~5,822 have a revised version only in revised-current, ~27% materially different) and lacks 7 in-force retained-EU items that exist only in revised-current.
- **Read variant info from the files on disk, not `best_collection_index.json`** — that index is stale on variants and trusting it would reintroduce the stale-text problem.

# LIVE NEXT STEPS

1. **DONE (2026-07-03) — extraction rebuilt to the two-stage section-level design and verified** on the 7-Act set: resolved-section counts reproduce the measured baseline exactly (727 uk_body / 862 schedule / 106 eu_article / 611 eu_recital); 6,051 previously-dropped cue-less leaves now recovered inside their flagged sections; max assembled block 23,213 chars with zero truncation; section_ref collisions kept distinct via DOM-identity keying.
   - **DONE (2026-07-16) — tier-3 anchor added (old-drafting orphan fix).** A third anchor tier catches schedule/annex prose-and-list content and bare-`<P>` body tail-clauses that tiers 1–2 (frozen) drop to orphan. **The four documented counters are PROVABLY UNTOUCHED** (verified old-vs-new on identical XML: 727/862/106/611 identical); tier-3 output routes into **three NEW material_types — `uk_schedule_unnumbered`, `eu_annex`, `uk_body_tail`** (taxonomy 5→8). 7-Act deltas: **+44 `uk_schedule_unnumbered`, +2 `uk_body_tail`, orphan_sents 2→0** (Explosives 1875 `uk_body` stays 51; its 2 tail-clauses re-home to `uk_body_tail`). Round-3 pool: all 36 orphans re-home (20 UK-schedule-sentences → 19 `uk_schedule_unnumbered`, 16 EU-annex-sentences → 10 `eu_annex`; per-entry grouping merges per-sentence orphans), 0 residual, 0 new orphans; section sizes sane (no mega/dust). Grain rule: **per-entry (enumerated lists) / whole-form (statutory forms) / paragraph-block**. Verified `_layer1_orphan_investigation.md` §F.
   - **DONE (2026-07-16) — taxonomy semantics v2: types describe CONTENT, not anchoring history (project-lead sign-off).** `eu_annex` now means *annex content in an EU-family instrument*, full stop — at every anchor tier — not "annex content that used to orphan". Schedule-mapped content in `eur`/`eudn` instruments re-types **`uk_schedule` → `eu_annex`** whichever tier anchored it (pre-check: all EU-family Schedule content is annex — no protocols/appendices — so the flip is unambiguous). **Typing-only delta:** anchoring, grain, boundaries, refs and headings are byte-identical (verified old-vs-new: **0 non-type diffs**; the only differences are enumerable `uk_schedule → eu_annex` re-typings — **20 sections on the 7-Act baseline** (GDPR annexes), **30 candidates on the round-3 EU pool**). Ref/heading now key on the **anchor tier**, not the type label, so re-typing tiers-1/2 annex content leaves its refs untouched.
   - **RE-BASELINE (supersedes 727/862/106/611; project-lead signed off).** The documented reference is now the **eight-type** 7-Act count set: **`uk_body` 727 · `uk_schedule` 842 · `eu_article` 106 · `eu_recital` 611 · `uk_schedule_unnumbered` 44 · `eu_annex` 20 · `uk_body_tail` 2** (total sections 2,352, unchanged). The old four-type baseline (uk_body 727 / uk_schedule **862** / eu_article 106 / eu_recital 611) is retained as the **superseded historical baseline** — `uk_schedule` moved 862 → 842 as its 20 EU-annex sections re-typed to `eu_annex`.
   - **Content-based type definitions (semantics v2).** `uk_body` = operative body section of a UK instrument · `uk_schedule` = numbered schedule provision of a UK instrument · `uk_schedule_unnumbered` = unnumbered schedule prose/list/form of a UK instrument · `uk_body_tail` = bare-`<P>` body tail-clause (extent/application) of a UK instrument · `eu_article` = article of an EU-family instrument · `eu_recital` = recital / numbered preamble unit of an EU-family instrument · `eu_annex` = **annex content of an EU-family instrument (any tier)** · `orphan` = text outside any anchorable structure (post-fix: editorial / residue only).
2. **Repoint `extract_candidates.py` to read the local bulk downloads** — revised-current primary, best-collection fallback, with the three-tier variant priority above; read variants from files, not the stale index. (Currently it fetches `/data.xml` live; only needed because the cache wasn't yet wired in.)
3. **Design + build Stage 2 — dual-model labelling.** The burden-set-per-section schema, set-vs-set agreement, and the label store / version-control are ratified but NOT yet built; this is the next deliberate design step (no real label is emitted until the store is in place).
4. **Hold the cue inventory / high-recall discipline as the measurement ceiling.** The `word_list` union is the candidate vocabulary; recall additions (rights/entitlements, void/contracting-out, Victorian `shall forfeit`, enforcement-submit, etc.) closed real holes. Audit recall empirically against ground-truth before scaling — anything dropped is invisible downstream.
5. **Build the validated training data toward Legal-BERT.**
6. **Rubric v2 → v1.0** — awaiting the project lead's full sign-off before it is authoritative.
7. **Deferred: line-by-line calibration reads** once the extraction pipeline is stable.

# PRE-LABELLING MEASUREMENT CHECKLIST (run once, before labelling begins — do NOT run yet)

Three one-off corpus measurements to run after bulk extraction and before labelling starts. Each states its result in the methodology; none is a processing queue.

1. **Older-consolidation amendment-provenance spot-check.** The 100% `introduced_by`/`introduced_year` recoverability figure is test-set only (7 modern, CLML-clean Acts). Spot-check older consolidations, where amendment annotation is thinnest, before any corpus-wide provenance claim. Methodology claim until then: *"verified recoverable on the test set; corpus-wide coverage TBC."* (Decision log 2026-07-05; `docs/decision_tree_gaps.md` G17.)
2. **Corpus-wide orphan-rate measurement.** Once bulk extraction runs, measure the orphan rate (`material_type='orphan'`) across the full corpus, once. Expectation: small, mostly editorial junk. An **anomalous** rate (e.g. whole instrument classes orphaning) is a **Layer-1 sectioning failure to investigate, not a queue to process.** Feeds the orphan-triage lane (`docs/decision_tree_gaps.md` G25).
   - **Taxonomy-completeness certificate (added 2026-07-16, tier-3 fix / G29).** Report at corpus scale, per **`leg_type × material_type`**, BOTH the orphan rate AND the **section-size distribution**. **Near-zero orphans + sane sizes everywhere = the eight-type taxonomy's empirical completeness certificate.** A spike in either is a **missing ninth type announcing itself.** Crucially, **post-tier-3 a taxonomy gap surfaces as a mega-section or a type-misassignment, NOT an orphan spike** (the tier-3 fallback anchors almost everything, so an un-modelled structure now lands in the wrong type at a wrong grain rather than orphaning) — so **monitor size distributions and type mix, not orphan rate alone.**
3. **Unconsolidated-amendment tail enumeration.** From the changes / unapplied-effects data, enumerate amendments **enacted but unapplied** at the corpus snapshot date — by target instrument and effect type, with the **insertion subset broken out** as the potential uncounted-burden bound. **Decision gate:** if the insertion tail is *material*, its payload text routes through the orphan lane (context-enriched from the target Act, flagged `unapplied_amendment=true`) and the methodology states the measure **includes enumerated pending insertions**; if *immaterial*, the quantified bound is the treatment. Either way the tail is **stated, never silent.**
4. **Definition-extraction coverage by era.** Round-3 extraction over fresh instruments returned **zero defined-term context on every pre-1900 Act and every EU instrument** — the `build_definitions` step keys on the modern inline `"X" means/includes` pattern, which Victorian drafting ("the word 'X' shall mean") and EU drafting (a dedicated Article 2 / Annex, cross-referenced not inline) don't match. **`context_quality` therefore correlates with era.** Flag this wherever **era-stratified disagreement rates** are read — older/EU material carries thinner defined-term context, so higher disagreement there is partly an extraction artefact, not a rule-difficulty signal — and **queue a definition-pattern extension** (Victorian + EU definition shapes). (Round-3 finding; see `_test_round_3_extraction_findings.md` and the item-8 Layer-1 orphan investigation.)

# QUEUED FOR LATER (corpus-run-time, not now)

- Physical deletion of `analyser.py` + cleanup of the ~15 dependent throwaway scripts (currently retired via banner; deferred until `extract_candidates.py` is validated at scale).
- A variant-aware, priority-resolved local file index (item_url → chosen file under the three-tier rule).
- A small *targeted* fetch of the exhaustion-sweep gap-fillers (the ~1,082 items absent from the bulk, e.g. old ukpga) — one at a time, never a crawl.
- **Amendment-provenance corpus-wide spot-check** — moved to the **Pre-labelling measurement checklist** above (item 1).
- **PRE-STAGE-2: fix or rename `is_amendment_insertion`.** The field fires 0/1,084 (broken — detects whole-section nesting, not inline `<Addition>` fragments). The ratified §3 amendment-machinery rule needs a working detector at the `<Addition>`-fragment grain. Fix or rename before anything in Stage 2 builds on it. (Decision log 2026-07-05; `docs/decision_tree_gaps.md` G3.)

# STILL RUNNING
- The Colab API-exhaustion sweep (resumable, durable v3 checkpoint).

# Corpus — Final State

| Metric | Value |
| --- | --- |
| Total rows | 212,183 |
| In-force corpus (na_inforce=1, text≥200) | 69,462 distinct items (zero double-counting) |
| Structured XML cached locally | ~98% of in-force corpus, in `Bulk download/` |
| uksi coverage | 99.6% (43,272/43,463) |
| Post-1990 ukpga | 100% — all significant Acts present |
| Status filtering | Active — 639,000+ no-force elements stripped |
| Permanently unrecoverable | ~12,000 items (never digitised) |
| Further downloads | Not recommended — diminishing returns confirmed |

# The Six Rubric Categories (assigned by LLM+human → Legal-BERT, NOT rule-based detection)

The taxonomy is unchanged; what changed is *who assigns it*. Detection is no longer keyword/subject-resolution — the candidate filter only surfaces; classification is the rubric-driven LLM+human+Legal-BERT layer. Plus a separate **polarity** attribute (obligation / prohibition / review) on every category.

| Rubric category | Tag |
| --- | --- |
| Direct burden | `direct` |
| Conditional direct obligation | `conditional_direct` |
| Implied burden | `implied_burden` |
| Implied burden active | `implied_burden_active` |
| Conditional burden | `conditional_burden` |
| Ambiguous | `ambiguous` |

> Note: `private_actor` is the parent class (the sentence imposes a private-actor burden), not a category tag. (The rule-based analyser used `private_actor` as the Direct leaf; that classifier is retired, so no DB migration is performed.)

# Candidate-filter vocabulary (`word_list`) — the measurement ceiling

The vocabulary now serves the high-recall **candidate filter**, not rule-based classification. The union of all cue sets surfaces candidates; precision signals (definitional / structural / clause-opener / purpose-clause) are **non-blocking hints**, never silent drops. Recall additions that closed real holes: rights/entitlements (§5B correlative duties), restriction-as-prohibition, void/contracting-out (was wrongly in the drop list), responsibility framing, defence framing, Victorian penalty-as-obligation (`shall forfeit`), enforcement-submit (Cat-5 duties), and a leading-imperative-verb backstop for list-item fragments.

# Validation Workbook — Current State
`Reg_Burden_Project_Validation.xlsx` — short-Act sample with full line-by-line classification (burden sentence, section reference, Direct/Implied/Conditional/Ambiguous, Claude agrees, Resolution). Now serves as ground truth for the rubric, the recall check for the candidate filter, and seed training data for Legal-BERT.

> KEY DECISIONS FORMALISED: (1) Penalty as consequence — not counted separately; (2) Conditional categories split by trigger control — organic operational event (Cat 2 `conditional_direct`) vs external authority act (Cat 5 `conditional_burden`); (3) Evidence supply is part of parent obligation; (4) Judicial discretion is not a private-actor burden; (5) Definitional tests are not separate from the prohibitions they define; (6) Nested/scope definitions are not additional burdens; (7) Licence to operate is a Direct burden, not conditional.

# Replication Guide — Building a Similar Regulatory Burden Measure
## Step 1 — Data Acquisition
- Register for research.legislation.gov.uk/statute-book-data.
- Download **Revised Current** bulk ZIP (the current consolidated/amended text — the PRIMARY source) and **Best Collection** bulk ZIP (fallback, fills items with only an enacted/made version). Keep both: Best Collection serves *as-made* text and must not be the sole source for amended SIs.
- Fill remaining SI gaps from the InForce CSV; add name + email to the user-agent per National Archives fair-use policy.

## Step 2 — Database / cache Setup
- SQLite `legislation` table + the bulk XML retained on disk (structure is needed for context attachment; flattened text alone is insufficient).
- Status filtering: `strip_no_force_provisions()` decomposes elements with Status in {Prospective, Repealed, Dead, Discarded, Prospective Repealed}.
- Resume-safe, deduplicated by item_url.

## Step 3 — Candidate Vocabulary
- Union of prescriptive cue sets (obligations, prohibitions, implied, penalty-as-obligation, rights, void, responsibility, enforcement-submit) — tuned for RECALL.
- Non-operative / structural / clause-opener lists kept as non-blocking HINTS only.

## Step 4 — Extraction Pipeline (not rule-based classification)
- Structure-preserving, **section-anchored** CLML walk: group each provision by DOM node identity, tag `material_type`, assemble chapeau + leaves (markers preserved, **no truncation**), attach heading / section ref / definitions; flag `context_quality` honestly (full/partial).
- Stage 1: emit **one high-recall candidate per flagged section** (a section is flagged if any cue fires anywhere in its subtree), carrying the assembled block + `leaves[]`, as JSONL + index. No labels assigned here.

## Step 5 — Validation / Ground Truth
- Line-by-line manual workbook = rubric ground truth + candidate-filter recall check + Legal-BERT seed data.

## Step 6 — Classification (dual-model + Legal-BERT) — Stage 2, RATIFIED DESIGN, not yet built
- Claude + Gemini independently decompose each section into a **burden-set** and classify against the rubric; agreement is **set-vs-set**; human adjudicates disagreements. The label store / version-control is set up before any real label is emitted.
- Fine-tune Legal-BERT on the validated labels; it is the production classifier.
- Active-learning loop: disagreements and low-confidence cases feed retraining.

## Step 7 — Full Run
- Run the extraction pipeline over the locally-cached bulk XML (revised-current primary, best-collection fallback) — no crawl.
- Legal-BERT classifies the candidate stream; stratified validation sample; output generation.

## Step 8 — Extending to Other Jurisdictions
- AU (legislation.gov.au), CA (laws-lois.justice.gc.ca), IE (irishstatutebook.ie) — adapt the candidate vocabulary to jurisdiction-specific drafting; the extraction → dual-model → BERT architecture transfers.

*Version 15 — July 2026. Architecture reframed: high-recall extraction → dual-model labelling → Legal-BERT. Extraction rebuilt to a two-stage, section-level design (section anchor DOM-keyed; Stage-1 subtree flagging; assembled chapeau+leaves, no truncation) and verified on the 7-Act set. Stage-2 labelling (burden-set per section, set-vs-set agreement) is ratified design, not yet built. Rule-based classifier retired (extraction pipeline survives). Structured XML cached locally; revised-current primary / best-collection fallback. trf upgrade, Cat 2/5 fixes, and tag migration dropped as obviated.*
