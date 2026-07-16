# Project Anchor — objective + scope

The canonical, **single** anchor for the UK Regulatory Burden Measurement project. It fixes both **what** the project counts (the objective: aim, unit, methodological commitments, output) and the **scope boundary** (which layers of binding rules the measure reaches, how content is typed, and how it is counted at the edge). Subsequent methodological, scoping, or technical decisions must be anchored here; refer back explicitly when proposing changes.

> **Reconciled 2026-07-16.** This document absorbs the former `project_scope_anchor.md` (created 2026-07-14 in the v2.5 scope batch; extended 2026-07-15 with the v2.6 capacity-axis batch). The separate scope-anchor file is retired — this is now the one anchor. Items from the original objective anchor that were overtaken by later decisions are superseded inline and flagged **(superseded …)**.

## Core aim

To produce the **first comprehensive, validated measure of prescriptive regulatory burden falling on private actors across the entire UK statute book**.

## Unit of measurement

The **count of legally binding obligations and prohibitions** imposed on private actors — businesses, individuals, and third-sector organisations — by UK legislation. Not a word count, page count, or document count: a count of provisions that impose compliance cost on non-governmental actors.

## What counts — scope ruling (statutory private-law duties, both sides)

The measure counts **statutory obligations as defined in the rubric, not a pre-sorted "regulation" subset**. A statutory obligation with legal force on a private actor counts whether its parent statute is "regulatory" or private-law, whether it binds the trader or the consumer side, and whether it is a mandatory term or a displaceable default (e.g. CRA 2015 s.25 — the consumer's duty to pay at the contract rate counts).

**Deeming distinction.** *Interpretive* deeming (labels something for a scheme's purposes — "treated as hazardous for the purposes of any legislation") is excluded. *Substance-creating* deeming (a statutory implied/deemed contract term bringing a live duty between private parties into existence — "every contract is to be treated as including a term that…") is counted and re-attributed to the obligated party (CRA 2015 s.13 → 1 trader burden vs Commission Decision 2000/532 → 0).

## Four key methodological commitments

1. **Private actor focus.** Systematically excluding obligations on public bodies (ministers, regulators, courts, named officeholders). The public/private actor distinction is the bedrock filter; everything else builds on it.

2. **Six-category taxonomy (numeric IDs 1–6 canonical, rename-proof; names presentational — see `category_mapping.md`).** Every classified provision falls into one of:
   - **1 `direct`** — a standing obligation/prohibition on a private actor
   - **2 `conditional_direct`** — *Conditional burden (operational)*: triggered by an event within the actor's own activities
   - **3 `implied_burden`** — obligation revealed through a defence provision ("it is a defence to prove…")
   - **4 `implied_burden_active`** — implied burden requiring an active, pre-existing compliance programme ("adequate procedures")
   - **5 `conditional_burden`** — *Conditional burden (regulator-triggered)*: triggered by an external regulator's act (notice, inspection, order)
   - **6 `ambiguous`** — genuine category uncertainty, flagged for review

   Plus a **polarity** attribute (obligation / prohibition / review) on every burden (rubric §2A). *(Superseded the original Cat-2/Cat-5 names "conditional obligation" / "conditional burden", which conflated the trigger-control distinction.)*

3. **Manual validation.** Every methodological decision validated against line-by-line ground truth across multiple Acts. The validation workbook is the authoritative ground truth; classifier outputs are assessed against it; methodological adjustments require workbook evidence.

4. **Section-anchored extraction; the unit of count is the distinct burden.** *(Supersedes the original "sentence-level classification" commitment.)* After the 2026-06-14 pipeline reframe and the 2026-07-03 extraction rebuild, candidates are surfaced at the **section/provision** grain (DOM-anchored; eight `material_type`s — see the implementation plan), and the **unit of measurement is the distinct burden** (rubric §1 unit rule): one section can carry several burdens and one burden can span several sentences. Not word-counting, not document-level, and no longer sentence-level — the count tracks burdens, not grammar.

## Capacity axis — economic vs personal (v2.6)

Each burden carries a capacity tag, applied *after* the private/public gate. *(Supersedes the earlier activity-profile formulation.)* Capacity turns on whether the duty attaches to **voluntary market activity on the burdened actor's side**:
- **economic** — the actor is exchanging or producing-for-exchange (selling, buying, letting, hiring, employing, working for pay, producing/supplying for the market), formal or informal, **either side** of the transaction. Private eBay seller → economic; business buyer → economic; consumer's duty to pay → economic.
- **compulsion carve-out (side-specific)** — a scheme-**compelled** transaction does not confer economic capacity on the compelled party; classify by the underlying activity. Dog-chip fee, MOT, compulsory motor insurance → **personal** for the owner/driver; the provider (vet, garage, insurer) → economic.
- **personal** — no market activity on the actor's side (ownership, status, conduct, consumption).
- **both/either** and **ambiguous** — unchanged.
- **Splits:** a role-split within one exchange (trader/consumer) → both economic, the split lives in `obligated_party`; a market-vs-non-market split of an activity (driving for hire vs privately) → the split decides capacity.
- **Floor:** economic floor = burdens on voluntary market activity (**includes consumer-side transactors**); the business-burden cut = economic ∧ business-side `obligated_party`, reported as its own line.

## What is in and out of measure

**In measure — the centrally published statute book:** in-force UK legislation that legislation.gov.uk exposes as machine-readable text (the Tier-1 corpus; see the coverage note for digitisation coverage within this layer).

**Out of measure — distinguished, not lumped:**
- **Binding out-of-corpus instruments.** Byelaws, traffic regulation orders (TROs), permit / licence / authorisation conditions, and regulator rulebooks (the **FCA and PRA Handbooks** the heavyweight cases). Legally binding, but not part of the centrally published statute book — their internal contents are not counted.
- **Non-binding regulator guidance.** Codes of practice, guidance notes and the like. Out of measure on a *different* ground (non-binding) — never conflated with the binding layer above.

## The frontier principle — deepest layer the measure can see

Count each burden **once, at the deepest layer the measure can see** (count-at-source, generalised across the scope boundary):
- An in-measure compliance/contravention hook (duty to comply with in-corpus legislation) stays **excluded** — counted at its own target.
- A statutory duty to comply with an **out-of-measure** binding instrument **IS counted, once, as a frontier proxy** — it stands at the visible frontier for the invisible layer behind it (which would otherwise be captured nowhere). One proxy per out-of-measure target; never an enumeration of that target's internal contents.
- Frontier proxies are tagged (`frontier_hook`, `frontier_target_type`) so the population is enumerable and reportable as *"N frontier duties standing proxy for out-of-measure layers."*

## The scope-expansion flip

Counts are **not additive across scope expansions.** If a future phase brings an out-of-measure layer into measure (e.g. a regulator's rulebook — see Future phases), that layer's contents are counted there and the corresponding frontier proxies **re-classify to `counted_at_source`** — so the same rule is never counted in two scopes at once.

## Growth-analysis consequence

Regulation migrates between layers with no net change in burden. The **FSMA 2023** REUL→FCA/PRA-rulebook transfer will show as a statute-book financial-services burden **decline that is layer-migration, not deregulation**; the growth/flow analysis names it as an adjustment when the data exists.

## Output

A number — **total private actor obligations in UK in-force legislation** — broken down by:
- **Legislation type** (`ukpga`, `uksi`, `ssi`, `wsi`, `nisr`, `asp`, `nia`, `apni`, `eur`, `eudn`, etc.)
- **Territorial extent** (England, Wales, Scotland, Northern Ireland, UK-wide; supports the devolution fragmentation analysis)
- **Subject area** (employment, environment, financial services, consumer protection, criminal law, etc.)
- **Year of enactment / provenance** (`introduced_by` / `introduced_year`; supports historical flow analysis)
- **Obligation type** (the six-category breakdown above) and **polarity**
- **Capacity** (economic / personal / both / ambiguous — the economic floor and business-burden cut)

Plus the **frontier-proxy** line (N duties standing proxy for out-of-measure layers) reported alongside, never folded into the statute-book count.

## Future phases

The headline measure is Phase 1. Subsequent phases extend the framework to:
- **Regulatory rulebooks** — extending beyond legislation to the prescriptive content of the FCA Handbook, Ofcom rulebooks, PRA Rulebook, etc. This is the archetypal **scope expansion**: those layers are currently *out of measure* (frontier proxies stand in for them), and bringing them in triggers the scope-expansion flip above.
- **Historical flow analysis** — measuring the rate of obligation addition and removal over time, by Government, by department (keyed on provenance; mind the layer-migration adjustment above).
- **International comparison** — applying the same methodology to other jurisdictions (US, EU, Commonwealth) to support comparative regulatory-burden analysis.

## Decision-making rule

When making suggestions about methodology, scope, or technical decisions, ask:
- Does this advance the count of private-actor obligations?
- Does it respect the **public/private filter**, the **six-category taxonomy**, the **manual-validation** requirement, the **unit-of-count (distinct burden) rule**, and the **in/out-of-measure scope boundary**?
- Does it move the work closer to the headline number, or does it serve a future phase?

If a proposed change moves the project away from these anchors without clear justification, flag it as a divergence and surface the trade-off explicitly.

## What the methodology paper documents

The classification system, the validation results, and the headline number with confidence intervals. The paper is not yet published; the corpus, classifier, methodology, and validation workbook are the inputs.

## Cross-references

- `docs/methodology.md` — full methodology (v14), the six-category taxonomy and key rules
- the validation rubric (current draft; owns the operative labelling rules — §1 unit rule + capacity axis, §2/§2A categories + polarity, §3 count-at-source / frontier proxies, §4 non-operative + deeming)
- `category_mapping.md` — canonical numeric category IDs ↔ presentational names
- `docs/coverage_methodology_note.md` — corpus coverage, scope-stratified figures, and the "Regulatory layers beyond the statute book" scope disclosure
- `docs/implementation_plan.md` — pipeline, schema notes (frontier fields; eight `material_type`s), and the documented eight-type baseline
- `Reg Burden Project Validation.xlsx` — manual validation workbook (ground truth)
- `tna_dataset_comparison.md` / `tna_crosscheck_methodology.md` — comparison with, and validation layer derived from, TNA's Statutory Powers and Duties dataset
