# Decision-Tree Gap List — agenda for the stage-2 design session

**Date:** 2026-07-05 · **Status:** mapping exercise; **triage session CLOSED 2026-07-06** — all four stranger findings resolved (orphan-triage lane G25, typed-exclusion schema G2, review-queue taxonomy G21, devolution two-lens G18); five decision-tree nodes reclassified `OPEN → DECIDED-UNBUILT` (N1/G1, N3/G5, orphan, review, devolution — plus the four EXCLUDED nodes with the exclusion schema); **allocation pile → confirmed stage-2 design agenda** (see below); **parked pile → confirmed pilot-gated with named revisit triggers** (G10, G12, G15). Reclassified gaps: G1, G5, G2, G18, G21, G25.
**Companions:** `pipeline_architecture.mmd` (systems view), `candidate_decision_tree.mmd` (logic view).
**Method:** every decision node in the per-candidate tree was annotated `rule · executor · status`; this is the flat list of every node where the **rule is missing/vague**, the **executor is unallocated**, or the **required data/implementation does not exist**. Each entry says *what is missing* and *what kind of decision closes it* — it does **not** propose the answer.

**Closing-decision kinds:** `RUBRIC` (a rule the project lead writes/validates) · `ARCH` (an architecture / data-contract choice) · `LIST` (a reference list or vocabulary to build) · `IMPL` (code to write). Many gaps need more than one.

**Honest framing:** almost the entire per-candidate tree is OPEN or DESIGN. Layer-0 corpus and Layer-1 extraction are built and verified; **Layers 2–5, the counting spine, and every feedback loop are ratified-design-or-open.** The tree is not 30 small holes in a working machine — it is the map of the machine that stage-2 has to build. The value below is the *shape* of each hole.

## Index

| ID | Node / layer | What's undecided | Closes with | Status |
|----|---|---|---|---|
| G1 | N1 §4 exclusions | rule (§4 list) SETTLED; residual = executor allocation (deterministic vs LLM) + where the drop happens | ARCH+RUBRIC | DESIGN |
| G2 | exclusion outcome | RATIFIED: fine-grained two-tier typed exclusion (exclusion_family + exclusion_subclass); writer unbuilt | IMPL | DESIGN ★ |
| G3 | N2 amendment detect | §3 rule ratified, but executor unbuilt & `is_amendment_insertion` broken | IMPL+ARCH | DESIGN ✦ |
| G4 | N2 amendment residence | policy for suppressing amending-SI candidates vs the target; backlog tail | RUBRIC+IMPL | OPEN |
| G5 | N3 cross-ref resolve | rule (§3 count-at-source) SETTLED; residual = executor allocation (L2 pattern vs L3) + cross-ref resolver | IMPL+ARCH | DESIGN |
| G6 | N4 statutory bodies | canonical statutory-bodies registry does not exist | LIST+IMPL | OPEN ✦ |
| G7 | N4 function test | statutory-vs-contractual executor unallocated | ARCH | OPEN |
| G8 | N4 context terms | §5D term-flip needs per-Act definition resolution | IMPL+RUBRIC | OPEN |
| G9 | N5 decomposition | Layer-3 architecture question (unit → model) | ARCH | OPEN ✦ |
| G10 | N5 discriminator | burden-vs-condition rule not empirically tested | RUBRIC | OPEN |
| G11 | N5 → BERT | production model can't emit per-section multiplicity | ARCH | OPEN |
| G12 | N6 category axes | enum conflates trigger-timing & defence-structure | RUBRIC | DESIGN |
| G13 | N7 polarity review | "review" threshold not operationalised | RUBRIC+IMPL | DESIGN |
| G14 | N8 obligated party | no controlled party vocabulary | ARCH+LIST | DESIGN |
| G15 | N9 capacity boundary | economic/personal boundary deferred to phase 2/3 | RUBRIC+ARCH | OPEN ✦ |
| G16 | N9 economic floor | floor reporting needs capacity field + query | IMPL | OPEN |
| G17 | N10 provenance | Citation resolver unbuilt; must be fragment-grain | IMPL | OPEN |
| G18 | spine dedup | RATIFIED: two lenses — residence-based primary count + family_id enrichment relation (uniform/divergent); linker unbuilt, post-labelling | IMPL | DESIGN ✦ |
| G19 | spine join | body↔schedule / amend↔target join does not exist | ARCH+IMPL | OPEN ✦ |
| G20 | L5 set-vs-set | no burden-matching rule when model counts differ | ARCH+RUBRIC | OPEN ★ |
| G21 | L5 review queue | RATIFIED as SCHEMA (review_reason + feeds fields), not tooling; fields unbuilt pending label store | IMPL | DESIGN ★ |
| G22 | L5 label store | label store / version-control unbuilt (blocks all) | IMPL | DESIGN |
| G23 | BERT inference | no auto-accept-vs-review confidence policy | ARCH | OPEN ★ |
| G24 | L1 recall gate | recall ceiling = word_list union (silent FN) | LIST+IMPL | OPEN |
| G25 | L1 orphans | RATIFIED: typed orphan-triage lane (clear non-operative / escalate → standard path, orphan=true); lane unbuilt | IMPL | DESIGN ★ |
| G26 | L1/L3 EU recitals | no soft-law fast-path; retained-EU effect status | RUBRIC | OPEN ★ |
| G27 | L1 definitions | def capture bounded (≤8) & single-instrument | IMPL | OPEN |
| G28 | L0/L1 cache | pipeline still fetches live; cache repoint unbuilt | IMPL | OPEN |

✦ = named in the calibration note (expected). ★ = newly surfaced by this mapping (not on the anticipated list).

---

## Gate & structural rules (Layers 1–2)

**G1 — §4 non-operative exclusion: executor allocation (rule settled).** `[N1 · ARCH+RUBRIC · DECIDED-UNBUILT]`
The §4 non-operative exclusion list is **settled** — it survived three reviews untouched, so the *rule* is decided; N1 is `DECIDED-UNBUILT`, the same shape as N2/G3 (rule ratified, executor unbuilt). What remains is an **executor-allocation question, now on the stage-2 allocation agenda:** (a) which §4 classes are safe as deterministic L2 drops (`shall be deemed`, `shall be defrayed`) versus which need L3 judgement (`list-of-contents vs list-of-requirements`, definitional-embedded-in-prohibition); (b) which layer runs the drop — noting Layer 1 is deliberately high-recall and never drops (§4 signals are non-blocking hints), and the ratified Stage-2 output is a *burden-set per section* with no obvious slot for "this candidate is non-operative, drop it" (see G2). *Closes with:* the deterministic-vs-judgement allocation per §4 class (RUBRIC), and the exclusion-stage architecture (ARCH).

**G2 — Typed EXCLUSION record: fine-grained two-tier schema RATIFIED.** `[exclusion outcome · IMPL · DECIDED-UNBUILT ★]`
A candidate surfaced by L1 that carries no burden gets a first-class *typed exclusion* record — for the extraction→count funnel, for audit, and as **negative training data for Legal-BERT** (rubric §7 wants worked negatives). "Empty burden-set" and "typed exclusion" are not the same thing. **Ratified design (2026-07-06) — fine-grained, two-tier:** every excluded candidate records `exclusion_family` + `exclusion_subclass`.
- **Families (4, load-bearing):** `non_operative` · `amendment_machinery` · `counted_at_source` · `public_body_or_no_one`. They map 1:1 to the four EXCLUDED tree nodes (X_NOP / X_AMD / X_PTR / X_PUB).
- **Sub-classes (recorded, best-effort):** within `non_operative` — `deeming`, `definitional`, `machinery_procedural`, `powers_to_make_secondary`, `scheme_machinery`, `list_of_contents`; within `counted_at_source` — `cross_reference`, `compliance_hook`, `enabling_power`, `penalty_as_consequence` (plus `secondary_offence_reference` if judged distinct from `cross_reference` — flagged as a call to make); plus `mixed_other` available in **both** families so dual-pattern cases don't stall.
- **Two-tier agreement rule:** dual-model agreement is computed on the **family only** — the count-relevant judgement — and family disagreements route to review. Sub-class mismatches within an agreed family are **logged, never adjudicated**.
- **Rationale on record:** the sub-class judgement is already made en route to the family call (§4 is a pattern list; matching a pattern *is* identifying the sub-class), so fine typing keeps a paid-for judgement at the cost of one field — buying the diagnostic over-identification audit (false positives locatable by class), sharper typed negatives for Legal-BERT, and the exclusion population as descriptive corpus data.

Consumers: the four EXCLUDED tree nodes and the orphan-triage lane (G25), which emits the same fields. *Closes with:* implementing the exclusion writer + store (IMPL; folds into the label store, G22).

**G3 — Amendment detection: rule ratified, executor unbuilt, existing flag broken.** `[N2 · IMPL+ARCH · DECIDED-UNBUILT ✦]`
The §3 amendment-machinery rule **is ratified** (amendment = machinery; count at the consolidated target), so this node is `DECIDED-UNBUILT` **at best** — the rule is decided but nothing executes it. The one field that promises the capability, `is_amendment_insertion`, is actively **broken**: `_in_amendment()` fires only when a whole section nests inside `<Addition>`, so it flagged **0 of 1,084** candidates despite 16,366 `<Addition>` nodes (real amendments are inline fragment insertions). It is logged as a bug in `project_decision_log.docx` (2026-07-05, pattern #3 Named ≠ actual — sibling of the `section_ref` "JOIN KEY" entry). **Detection must be at the `<Addition>`-fragment grain**, not the section flag. *Before Stage 2, the field is fixed or renamed so nothing builds on a false signal.* *Closes with:* the fragment-grain detector (IMPL) and an executor decision — markup-rule L4 vs LLM L3 (ARCH); the *rule* is not the gap.

**G4 — Amendment residence policy is incomplete.** `[N2/spine · RUBRIC+IMPL · OPEN]`
The rule says count the burden once, at the amended target in consolidated form. But amending SIs are themselves separate corpus items, so their amendment provisions will surface as candidates. There is no policy suppressing those so the count lands once at the target, and the legislation.gov.uk editorial backlog means a small tail of targets is not yet updated → **zero-count**. *Closes with:* a residence/suppression rule (RUBRIC) and its enforcement in the spine (IMPL). Overlaps G18.

**G5 — Count-at-source: executor allocation + cross-ref resolver (rule settled).** `[N3 · IMPL+ARCH · DECIDED-UNBUILT]`
The §3 count-at-source family — cross-refs, compliance/contravention hooks, enabling powers, penalty-as-consequence, offence primary-vs-secondary — is **settled** (several members ratified this month), so N3 is `DECIDED-UNBUILT`, the same shape as N2/G3. What remains is an **executor-allocation question, now on the stage-2 allocation agenda** (L2 pattern vs L3 model), plus its dependency: count-at-source and the offence primary-vs-secondary distinction both require resolving "a requirement under section X" / "contravenes section 4" to the referenced provision — possibly in another instrument — and no such resolver exists. Without it, offence cross-references and compliance hooks can't be reliably separated from primary burdens. *Closes with:* the reference-resolution component (IMPL), and the deterministic-vs-LLM allocation (ARCH).

## Actor classification (Layer 4)

**G6 — Statutory-bodies registry does not exist.** `[N4 · LIST+IMPL · OPEN ✦]`
The §5C function test needs a canonical list of statutory bodies (FSCS, FOS, regulators, named officeholders) with their public/private status. `word_list.PUBLIC_BODY_SUBJECTS` / `PRIVATE_ACTOR_SUBJECTS` are keyword cues built for the *retired* analyser and are **not imported by `extract_candidates.py`** — they are unwired, and a keyword list is not a registry. *Closes with:* building the registry (LIST) and wiring a lookup (IMPL).

**G7 — Function-source test executor unallocated.** `[N4 · ARCH · OPEN]`
"Statutory source = public / contractual source = private, funding-irrelevant" is a judgement with a hybrid→review escape. Whether it runs as an L4 lookup, an L3 LLM call, or both (lookup then LLM for misses) is undecided. *Closes with:* an architecture decision (ARCH).

**G8 — Context-dependent terms unresolved.** `[N4 · IMPL+RUBRIC · OPEN]`
§5D terms ("scheme manager" = public in FSMA, private in occupational pensions) flip by Act. Resolution needs the Act's own definitions; the extractor attaches ≤8 same-document definitions and no cross-instrument ones. *Closes with:* definition-resolution code (IMPL) and a fallback rule for the unresolved case (RUBRIC → route to review).

## Decomposition & the unit of count (Layer 3 / counting spine)

**G9 — Decomposition executor = the Layer-3 architecture question.** `[N5 · ARCH · OPEN ✦]`
How a section becomes N burden units — per-candidate classifier, counting head, BIO/span tagging, or decompose-then-classify — is the single decision that fixes both the labelling I/O contract and the production-model shape. Formally deferred to stage-2 (rubric §7 item 1, notes item 6). **Selection criterion:** the chosen architecture must emit **usable confidence outputs** — production review depends on confidence-thresholding *replacing* disagreement as the model-side uncertainty signal (G21, G23), and the four candidate architectures differ in how naturally they provide it. *Closes with:* the stage-2 architecture choice (ARCH).

**G10 — Burden-vs-condition discriminator not empirically tested.** `[N5 · RUBRIC · OPEN]`
The unit rule's core call — obligation-leaf (count each) vs condition/factor-leaf (count once) — is defined but not yet run against real chapeau-plus-list provisions from the corpus (§7 item 3). Until tested, the two models will diverge on multiplicity. **Revisit trigger (parked, pilot-gated):** Jethro's hand-labelling pass + the dry run — the §7 field-test. *Closes with:* a validation pass and any resulting rule tightening (RUBRIC).

**G11 — Legal-BERT cannot emit per-section multiplicity.** `[N5→BERT · ARCH · OPEN]`
A per-candidate production classifier structurally cannot reproduce "3 burdens in this section" or cross-candidate merges without a counting/tagging scheme. The labelled unit (burden) and the model's emission grain (candidate) are mismatched. Companion to G9. *Closes with:* the same architecture choice, viewed from the production side (ARCH).

**G12 — Category enum conflates two axes.** `[N6 · RUBRIC · DESIGN]`
Cats 1/2/5 classify by trigger-timing; Cats 3/4 (IB/IBA) by defence-structure. Resolved *for now* by the defence-dominance precedence rule (notes item 7) as a stated simplification — logged as pilot-contingent (may need an orthogonal defence flag if defence-revealed burdens show materially different trigger profiles). **Revisit trigger (parked, pilot-gated):** a pilot showing defence-revealed burdens with materially different trigger profiles. *Closes with:* a post-pilot rubric decision (RUBRIC).

## Per-burden attributes (Layers 3–4)

**G13 — Polarity "review" threshold not operationalised.** `[N7 · RUBRIC+IMPL · DESIGN]`
`review` is reserved for genuine post-rule uncertainty, "not a dumping ground" — but nothing measures or enforces that discipline, so the bucket can bloat once a batch runs (§7 item 9). *Closes with:* a threshold/audit rule (RUBRIC) and its monitoring (IMPL).

**G14 — Obligated_party has no controlled vocabulary.** `[N8 · ARCH+LIST · DESIGN]`
Free-text party ("employer" / "operator" / "any person") is the field on which actor-capacity, dedup, and aggregation all depend. Without a controlled taxonomy those downstream steps are unstable. *Closes with:* a schema decision (ARCH) and a party taxonomy (LIST).

**G15 — Actor-capacity boundary deferred to phase 2/3.** `[N9 · RUBRIC+ARCH · OPEN ✦]`
Phase 1 uses generous `ambiguous`; the economic figure is a **floor**, not a share. The activity-profile rule (notes item 8: classify the activity not the subject; scheme-splits follow the scheme; both/either needs a positive judgement) is new and untested. **Revisit trigger (parked, pilot-gated):** pilot data, including the both/either base-rate question. *Closes with:* the deferred-phase refinement plan (ARCH) and validation of the activity-profile rule on real cases (RUBRIC).

**G16 — Economic-floor reporting needs schema + query support.** `[N9 · IMPL · OPEN]`
The reporting rule (floor = economic-only; both/either and ambiguous as separate lines) requires the capacity field to exist and a reporting query to segment it. Neither is built. *Closes with:* implementation once the field lands (IMPL).

**G17 — Provenance resolver unbuilt (data is there).** `[N10 · IMPL · OPEN]`
`introduced_by` / `introduced_year` are ~100% machine-recoverable (`Addition`→`Commentary`→`Citation`, measured 1,403/1,403 burden-bearing insertions), but no code extracts them, and they must attach at the **fragment/burden** grain — 22.4% of amendment-touched sections were patched by >1 instrument (max 16), so a section-level field is wrong. Fields are nullable, so labelling won't stall; the growth-over-time analysis depends on this being built. *Closes with:* the fragment-grain resolver (IMPL).

## Counting spine

**G18 — Devolution / parallel-instrument duplicates: two-lens design RATIFIED.** `[spine · IMPL · DECIDED-UNBUILT ✦]`
The "one rule, multiple textual homes" pattern means the same regulatory control can appear in several instruments; but *intentional* devolution duplicates (parallel E&W / Scotland / Wales / NI provisions) must not be silently collapsed. **Ratified design (2026-07-06) — two lenses:**
- **Primary (labelling-time) count = residence-based.** Parallel duties in four jurisdictional instruments are **four burdens** — consistent with the unit rule and the amendment rule; **no similarity test touches the counting spine.** This lens answers *"how much prescriptive content does the in-force statute book contain."*
- **Duplicate-family relation (enrichment lens).** Burdens gain a nullable **`family_id`**; families carry a **uniform / divergent** flag, with the differing fields recorded. This lens answers *"how much distinct regulatory control does society face."* **Acceptance test:** Route-A (one UK instrument) and Route-B (four parallel instruments) must **coincide** on this lens. Required **before first publication** (the project's "control on society" framing lives here); **built post-labelling.**

**Mechanism (five stages, structure-first):** (a) candidate instrument-family pairs from Layer-0 metadata (year, counterpart types `uksi`/`ssi`/`wsi`/`nisr`, title similarity, extent); (b) structural alignment of burdens within paired instruments (position + section skeleton); (c) text similarity as **confirmer only** — never creates a link without the structural scaffolding; (d) uncertain band → review queue (`family_link` added to `review_reason`, a **production-era** lane, G21); (e) attribute comparison → uniform/divergent tagging.

**Acceptance bar — good-enough, asymmetric, measured:** precision favoured over recall (a missed link biases the distinct-rules count *conservatively* = cheap; a false merge overclaims sameness = the expensive direction, kept fussy). Errors are **bounded and non-propagating** — this is an enrichment layer, and the **primary count is untouched.** Achieved link-precision is validated by a stratified hand-audited sample and **stated in the methodology** — the claim is *characterised* error, not minimal error.

**Scope for publication:** devolution counterparts only; cross-sector template parallels are future analysis, not publication-gating.

The **methodology reports both lenses with this rationale**, which pre-empts the devolution-artefact critique (that the statute-book count inflates by counting parallel instruments). *Closes with:* building the family-linker (IMPL), post-labelling / pre-publication. Related: G19 (body↔schedule / amend↔target join), G20 (set-vs-set matching), G4 (amendment residence).

**G19 — Body↔schedule / amend↔target join does not exist.** `[spine · ARCH+IMPL · OPEN ✦]`
A burden's operative clause and its schedule detail — or an amending Act's insertion and its target section — live in different sections or items. `section_ref` is non-unique (48 collisions on the 7-Act set) and DOM-identity keys are per-item only. There is no cross-section/cross-item burden-grouping key. *Closes with:* a grouping-key design (ARCH) and its implementation (IMPL). Related to G4/G17.

## Adjudication & review (Layer 5)

**G20 — Set-vs-set agreement has no burden-matching rule.** `[L5 · ARCH+RUBRIC · OPEN ★]`
Agreement is defined for the equal-count/equal-label case. When Claude and Gemini emit *different burden counts* for one section, there is no rule to align the two burden-sets, score partial agreement, or decide what routes to review. This is the common disagreement mode, not an edge case. *Closes with:* a matching/scoring algorithm (ARCH) and an adjudication rule (RUBRIC).

**G21 — Review-queue taxonomy: ratified as SCHEMA (not infrastructure).** `[L5 · IMPL · DECIDED-UNBUILT ★]`
At least five distinct review reasons converge on one queue with no typed reason recorded. **Ratified design (2026-07-06) — two label-record fields, present from the first pilot adjudication, not a queue tool:**
- **`review_reason`** — primary (the route that fired **first in tree order**) plus optional **secondary** for compound cases. Values: `model_disagreement`, `hybrid_actor`, `ambiguous_leaf`, `cat6_category`, `polarity_review`, `orphan_escalation`, `context_term` — plus `low_confidence` and `family_link` (devolution-family uncertain band, G18), both **reserved for the production phase** (see phase note below).
- **`feeds`** — recorded **at resolution**: `registry` | `rubric_example` | `unit_rule_evidence` | `training_data` | `definitions`. This is what makes adjudication harvest **mechanical** — rulings flow to the statutory-bodies registry (G6), the rubric's worked examples, the unit-rule field-test evidence (G10), the training set — rather than archaeological.
- **No queue tooling is built.** During labelling, *lanes* = sorting records by `review_reason` before an adjudication session; *priority* = one line of guidance (gating lanes first: `model_disagreement` blocks training data, `hybrid_actor` blocks the registry, `ambiguous_leaf` feeds the unit-rule test; the rest pool). Production-era tooling, if any, is a main-run design question that inherits these fields.
- **Phase note:** the same `review_reason` schema serves both phases with a different traffic mix — dual-model disagreement is the *training-data-phase* model-side uncertainty signal; in production, `low_confidence` (Legal-BERT confidence-threshold) routes to review where disagreement did. The rules-layer lanes (`hybrid_actor`/unlisted-body, `orphan_escalation`, `context_term`) and the random audit slice run through **both** phases unchanged.

*Closes with:* implementing the two fields (IMPL; folds into the label store, G22). **Set-vs-set burden-matching mechanics stay OPEN** — that is the Layer-3 architecture question (G20/G9, allocation agenda), not the taxonomy.

**G22 — Label store / version-control unbuilt.** `[L5 · IMPL · DESIGN]`
Ratified as "established before any real label is emitted" — the persistence, versioning, and label-provenance layer. It blocks every downstream step (adjudication, training data, BERT). *Closes with:* building it (IMPL).

**G23 — Production-inference confidence/routing undefined.** `[BERT · ARCH · OPEN ★]`
At corpus run-time there is no policy for when a Legal-BERT output is auto-accepted vs routed to review, nor what triggers the active-learning retrain loop. The feedback loops are drawn but ungoverned. *Closes with:* a thresholding/routing decision (ARCH).

## Intake edges & recall (Layers 0–1)

**G24 — Recall ceiling = the word_list union.** `[L1 · LIST+IMPL · OPEN]`
A genuine burden phrased with none of the cue vocabulary is never surfaced and is invisible downstream (silent false negative). This is an upstream *gate* with no "unknown burden" branch; the only control is empirical recall audit against ground truth. *Closes with:* ongoing recall additions (LIST) and a standing recall-audit harness (IMPL). Partly acknowledged in the implementation plan.

**G25 — Orphan / partial-context candidates: typed triage lane RATIFIED.** `[L1 · IMPL · DECIDED-UNBUILT ★]`
`material_type='orphan'` records are per-sentence with `n_leaves=0`; `context_quality='partial'` records lack ref/heading, so they do not fit the section-with-leaves tree. **Ratified handling (2026-07-06):** orphans do **not** enter the main pipeline directly — they route to a **typed orphan-triage lane**.
1. An **LLM first-pass clears** clearly-non-operative fragments, recording the typed §4 exclusion (`exclusion_family`/`exclusion_subclass`, G2). The verdict is **asymmetric** — clear only what is *clearly* non-operative, escalate everything else — and the triage pass does **not** label burdens.
2. **Escalated** fragments are enriched with retrievable surrounding raw text and **re-enter the standard classification path** (decomposition → category → polarity → obligated_party → actor_capacity → provenance) under the normal dual-model + review machinery — **same record shape, no parallel pipeline**; the retrieved context is part of the candidate the models *see*, not just the human view.
3. Every orphan-derived record carries **`orphan=true`** to the final burden record, so the slice stays distinguishable (auditable for elevated disagreement / reliability) without being differently shaped.

The lane is the **second consumer of the exclusion-label schema** (G2; N1's §4 exclusions is the first). *Closes with:* building the lane (IMPL). *Related measurement:* corpus-wide orphan-rate check queued pre-labelling (implementation plan) — an anomalous rate signals a Layer-1 sectioning failure, not a queue to process.

**G26 — EU recital / retained-EU material has no fast-path.** `[L1/L3 · RUBRIC · OPEN ★]`
`eu_recital` sections are surfaced (with a `recital_suspect` hint) but recitals are near-always non-operative soft-law; without a routing rule they either add noise or draw inconsistent LLM calls. Retained/assimilated-EU direct-effect and applicability status is also unaddressed in the tree. *Closes with:* a material-type routing rule (RUBRIC).

**G27 — Definition capture is bounded and single-instrument.** `[L1 · IMPL · OPEN]`
The extractor attaches ≤8 defined terms from the same document. A classification hinging on a 9th term, or on a term defined in another instrument, can misfire — most acutely for the §5D context-term flips (G8). *Closes with:* raising/relaxing the cap and cross-instrument definition lookup (IMPL).

**G28 — Cache repoint pending.** `[L0/L1 · IMPL · OPEN]`
`extract_candidates.py` still fetches `/data.xml` live; the ratified local-cache read (revised-current primary / best-collection fallback, three-tier variant priority, variants read from files not the stale index) is unbuilt. Affects reproducibility, scale, and — critically — *which text edition* is classified. *Closes with:* the repoint (IMPL).

---

## Stage-2 allocation agenda — CONFIRMED (2026-07-06)

The allocation pile transfers to the stage-2 design session **as-is** — nothing in it needs a decision before that session. The confirmed agenda is the set of `UNALLOCATED` executor questions (the rules above them are settled; these are ARCH/IMPL allocations, not open rule questions):

- **N1 §4 exclusions (G1)** — executor: L2-deterministic vs L3-model split (+ where the drop happens).
- **N3 count-at-source (G5)** — resolution machinery: L2 pattern vs L3, plus the cross-reference / offence-target resolver.
- **N4 actor (G6 / G7)** — statutory-bodies registry wiring, and the function-source test executor.
- **N10 provenance (G17)** — the fragment-grain Citation resolver.
- **Decomposition architecture (G9 / G11 / G20)** — the load-bearing Layer-3 choice (per-candidate / counting-head / BIO-tag / decompose-then-classify), which fixes set-vs-set matching (G20) and the production-model shape. **Selection criterion: must emit usable confidence outputs** (production review depends on confidence-thresholding replacing disagreement — G21 / G23).

## Reading of the map

- **Known-unknowns confirmed (✦):** G3 (amendment detection at `<Addition>`-fragment grain), G6 (statutory-bodies list), G9 (decomposition architecture), G15 (capacity deferral), G18 (dedup policy), G19 (body↔schedule join) — all present, as the calibration note required.
- **Newly surfaced (★):** G2 (exclusion-record schema), G20 (set-vs-set burden matching), G21 (review-queue taxonomy), G23 (BERT inference routing), G25 (orphan handling), G26 (EU-recital fast-path). These are the holes the diagram exposed that were not on the anticipated list — mostly at the **Layer-5 adjudication schema** and the **intake edges**, i.e. the two ends the rubric talks about least.
- **The load-bearing decision:** G9/G11 (the decomposition architecture) sits under G2, G18, G19, G20 and the whole schema. It is the one to take first in the stage-2 session — most other ARCH gaps resolve differently depending on it.
- **Not one gap type but four:** the map is roughly `RUBRIC ×9, ARCH ×11, LIST ×3, IMPL ×17` (with overlaps; refreshed 2026-07-06 after the triage reclassifications — the ratified items shed their RUBRIC/ARCH open-question content and are now IMPL-to-build). **Status distribution: 11 DECIDED-UNBUILT, 17 OPEN** (0 built — the Layer-0/1 built items sit outside this gap list). The ARCH cluster is the stage-2 agenda proper; the IMPL cluster is downstream of it; the RUBRIC items are the project lead's to close and several (G10, G12, G15) are explicitly pilot-contingent (parked, with revisit triggers recorded against each).
