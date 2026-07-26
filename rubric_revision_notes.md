# Rubric — pending edits for the next revision

Running list of changes to fold into `uk_reg_validation_rubric_v2_draft.docx` on the **next** pass. These are batched deliberately — they go in alongside the project lead's full sign-off read, in one edit, not piecemeal. Do NOT rebuild the rubric document to apply any single item here.

## Batched for the next revision (from 2026-07-03)

**1. Rename the two conditional categories (trigger-distinction, IB/IBA-style shared-family naming).**
- Cat 2: "Conditional direct obligation" → **"Conditional burden (operational)"**
- Cat 5: "Conditional burden" → **"Conditional burden (regulator-triggered)"**
- Rationale: the bare shared word "Conditional" risked conflating Cat 2 and Cat 5; the names now carry the trigger-control discriminator. (Decision recorded in `project_decision_log.docx`, 2026-07-03.)

**2. Cat 2 gains an anchoring line + contrast pair.**
- Anchoring line: *the trigger is an event or circumstance arising within the actor's own activities, whether or not the actor deliberately caused it.*
- Contrast pair: *a workplace death → Cat 2 (operational); a regulator's inspection demand → Cat 5 (regulator-triggered).*

**3. Schema-mapping section: state the canonical-ID rule.**
- Add: **"Numeric category IDs (1–6) are canonical and rename-proof; names are presentational — see `category_mapping.md`."** The rubric names become a presentation layer over the IDs.

---

## Batched for the next revision (from 2026-07-05 — v2.2 review triage)

Responses to the v2.2 review, ratified by the project lead. Fold into the named sections at the next revision.

**4. §3 (decision rules) — textual amendments are machinery, not burdens.**
- Rule (ratified): a provision whose operative content is the textual amendment of another instrument ("for X substitute Y", "after subsection (2) insert—") is **not itself a burden — it is machinery**. The burden it creates or modifies is counted **once, at the amended target in its consolidated in-force form** (which is what the corpus holds — Stream B `/data.xml`).
- This is count-at-source applied to amendments: counting the amending instruction *and* the consolidated target double-counts.
- Honest caveat to include: legislation.gov.uk's revised text carries an editorial backlog of unapplied effects, so a small tail of amendments will not yet be reflected in their targets — a known, bounded under-count, not hidden.

**5. Schema notes — provenance fields (from the #4 discussion).**
- Add two fields to each burden: **`introduced_by`** (the amending instrument; the parent instrument itself for original text) and **`introduced_year`**. Best-effort from markup/metadata, **explicitly nullable — labelling never stalls on lineage.**
- Rationale for the split: **residence** (which instrument the burden is *part of* — keys the count) and **provenance** (which instrument *introduced* it — keys the growth-over-time analysis) are separate attributes answering different questions. Recording both makes "burdens by Act" and "burdens introduced by instrument/year" two group-bys over the same records.
- **Pricing measurement (2026-07-05, 7-Act verification set) — coverage is excellent ON THE TEST SET:**
  - **1,403 / 1,403 (100%)** of burden-bearing (cue-carrying) `<Addition>` fragments carry a machine-readable `<Citation>` (URI → instrument type + year).
  - **2,374 / 2,374 (100%)** textual-amendment commentaries (CLML Type F) likewise; all `<Addition>` nodes overall 16,348 / 16,366 (99.9%).
  - Provenance lives in the Commentary referenced by each `<Addition>` (`CommentaryRef` → `Commentary/@id`); commentaries survive the current `strip_metadata`, so no strip change is needed.
  - **CALIBRATION (do not overstate):** the 100% is on 7 Acts that lean **modern and CLML-clean**. Pre-digital-era consolidations are where amendment annotation (the `<Commentary>`/`<Citation>` machinery this rides on) is thinnest, so **corpus-wide coverage is unconfirmed** and would plausibly sag. **Methodology claim until confirmed:** *"amendment provenance verified recoverable on the test set; corpus-wide coverage TBC."* A spot-check on older consolidations is **queued, not run** (see `project_decision_log.docx`, 2026-07-05). Fields stay nullable so labelling never stalls; the growth-over-time claim is hedged to the test set until the spot-check lands.
  - **Caveat (a) — grain:** provenance is single-valued only at the **fragment / burden** grain, not the section. 22.4% of amendment-touched sections were patched by **more than one** instrument (max 16). This confirms `introduced_by` belongs on the burden, exactly as the rubric attaches it — not on the section.
  - **Caveat (b) — wrong hook:** the current `is_amendment_insertion` flag fires only when a *whole section* nests inside `<Addition>`, which is ≈0 of real amendments (they are inline fragment insertions). Provenance must be resolved at the `<Addition>`-fragment grain in stage-2, **not** read off that flag. (Finding only — not a stage-2 build now.)

**6. §7 (open items) — reword the multiplicity prerequisite (reframing accepted; resolution deferred).**
- Reword to name the **full** consequence: the multiplicity question decides the labelling I/O contract **AND** the production-model architecture (per-candidate classification vs counting head vs BIO/span tagging vs decompose-then-classify) — **one decision, not two**.
- Do **not** resolve it in the rubric; it is formally on the **stage-2 design agenda**. Note that the leaf-anchored burden-set schema keeps all of these options open.

**7. §2 (categories) — precedence rule for the two conflated axes (stated simplification, not a restructure).**
- Add: **defence-revealed expression dominates the category call** — a burden revealed through a defence is IB/IBA regardless of its trigger profile.
- Log as a **deliberate simplification**, revisitable if the pilot shows defence-revealed burdens with materially different trigger profiles actually mattering.

**8. §1 (economic/personal) — the economic-floor reporting rule + a capacity-classification rule.**
- **Reporting rule:** the economic floor = **economic-tagged burdens only**; `both/either` is reported as **its own line** ("X certainly economic, plus Y applying in either capacity, plus Z unresolved"). Not folded into the floor.
- **Capacity-classification rule:** classify **the activity the duty attaches to, not the grammatical subject**. Test — is the regulated activity, in practice, done in one capacity or both?
  - Activity only done economically (operating a slaughterhouse, employing, providing a regulated service) → **economic**, regardless of "any person" phrasing.
  - Activity only done in personal life → **personal**.
  - Activity genuinely done in **both** capacities under an identical undifferentiated duty (driving, land ownership, possession, waste handling) → **both/either**.
  - Can't determine the activity's capacity profile → **ambiguous**.
  - Qualifier (a): **context resolves surface universality** — if the scheme's definitions/thresholds/licensing context make it a commercial regime, it's economic despite "any person".
  - Qualifier (b): where **the law itself splits capacities** (private driving vs driving for hire), follow the scheme — the split duties classify separately, and neither is both/either.
  - `both/either` requires the **positive** judgement "binds identically in either capacity"; mere uncertainty is `ambiguous`.

**9. Smaller gaps (one line each).**
- **Tag strings for Cats 2–6:** cross-reference `category_mapping.md` (numeric IDs canonical; names presentational). (Extends item 3.)
- **"With legal force":** delegated to the corpus layer (`na_inforce` / CLML status filtering) — labellers do not re-litigate currency; the same line covers commencement.
- **§2A addition:** a defence-revealed burden takes the **polarity of the underlying standard it reveals** (Wild Mammals → prohibition; Bribery s.7 → obligation).

---

## Batched for the next revision (from 2026-07-06 — triage session; completes the file for the v2.3 build)

Three rubric-touching items from the triage that resolved the four "stranger" findings. Fold into the named sections at the next revision. Full designs live in `docs/decision_tree_gaps.md` (G18, G2, G25) and `docs/implementation_plan.md`.

**10. §1 (near count-not-magnitude) — devolution labelling instruction.**
- Parallel jurisdictional instruments (uksi / ssi / wsi / nisr counterparts) **count separately** — the primary count is **residence-based**, one burden per instrument, exactly as the unit rule and amendment rule already work.
- The deduplicated **"distinct rules"** view is a **downstream analysis lens**, built post-labelling. **Labellers NEVER make a sameness / duplication judgement** — classify what is in front of you; family-linking happens later. (Design: G18, two-lens.)

**11. §4 (+ the relevant §3 rules) + schema-mapping — exclusion typing instruction.** _(Family enum updated to exclusion taxonomy v2, ratified 2026-07-18 — see the flag below.)_
- A candidate that carries no burden is recorded as a **typed exclusion**, not dropped silently: **`exclusion_family`** ∈ {non_operative, counted_at_source, public_body_or_no_one, **structural**} + a best-effort **`exclusion_subclass`** (the §4 / §3 pattern matched), per the ratified **fine-grained two-tier** design; **`mixed_other`** is available in all families for dual-pattern cases.
- **`amendment_machinery`** is a **`counted_at_source` subclass** (not a family) — the amendment rule is count-at-consolidated-target, the family's purest case. **`structural`** (operative-but-not-a-burden under the counting rules — a distinct joint from `non_operative`, which has no operative content) carries subclasses: `bare_permission`, `scope_eligibility`, `condition_factor_list`, `single_act_specification`, `procedural_right_v_state`, `liability_attribution`, `burden_removal`.
- Dual-model agreement is computed on the **family** (the count-relevant call); sub-class mismatches within an agreed family are logged, not adjudicated. (Design: G2.)
- **✔ MERGED — rubric v1.0.1 (2026-07-18):** the authoritative `docs/validation_rubric.md` §2A/§4 now carry the v2 family enum (structural family; `amendment_machinery` as a `counted_at_source` subclass; structural subclasses enumerated; "mixed_other … in any family"). Published as **v1.0.1** (recording-schema alignment only; no counting rules changed) and mirrored in the docx master (`uk_reg_validation_rubric_v1_0.docx`). Pending flag cleared.

**12. Schema / pipeline section — orphan-lane pointer.**
- Orphan candidates (`n_leaves=0`, partial context) **route to a triage lane before classification**: an LLM first-pass clears clearly-non-operative fragments (typed exclusion, per item 11) and **escalates the rest**; escalated fragments **re-enter the standard classification path context-enriched**, flagged **`orphan=true`**. See `docs/implementation_plan.md` for the lane design. (Design: G25.)

---

## Batched for the next revision (from 2026-07-15 — round-3 / v2.6 follow-up)

**13. FSMA proxy consistency — one statutory home per rule-layer.** The comply-with-rulebook frontier proxy (rubric §3) has **ONE statutory home per rule-layer** and is counted **once, there** — never re-counted at each rule-mandating section. For the FCA Handbook the home is the **s.137A general-rule-making-and-enforcement complex**; when FSMA 2000 is labelled, do NOT re-count the proxy at every "the FCA must make rules…" provision (FSMA has dozens of them — round-3 extraction surfaced ~20+ rule-making sections). Guards against the frontier proxy inflating the FSMA burden count by re-counting at each rule-mandating section. (Not a v2.6 rubric edit — a labelling-convention note for when FSMA is worked.)

---

## Route elsewhere — NOT a rubric edit

**→ `project_decision_log.docx` ("The recurring patterns" section) — a new named pattern.**
Staged here per the "everything into the notes, batched" instruction; ready to paste into the decision log on your say-so (I did not edit the docx).

- **Pattern name (proposed): "One rule, multiple textual homes."** A single substantive rule has more than one place it can be written down, so the same burden risks being counted twice or zero times depending on which home the labeller lands on.
- **Evidence — third consecutive review catch of this species:** IB double-meaning (defence vs primary prohibition) → enabling-power / SI double-count (hook vs resulting instrument) → amendment double-count (amending instruction vs consolidated target).
- **Why it recurs here:** a **consolidated-plus-amending corpus** structurally creates multiple homes for one rule. This is the project's **characteristic failure surface** — recognise the next instance by shape, and reach for count-at-source.

---

## Published / reconciled — pilot adjudication (2026-07-21)

**Rubric v1.1 PUBLISHED** (`docs/validation_rubric.md` + docx master + Pages). Six additions folded from the pilot adjudication: (i) constituted-duties rule (§3, never-zero-a-power-section); (ii) specifications-vs-embedded-duties test (§1, breach-without-attempting); (iii) IB boundary + named-target discipline (§2A/§3, schema gains `source_target`); (iv) compliant-actor test (§3); (v) polarity conventions (§2A, refrain-entirely vs when-doing + per-condition); (vi) capacity note (§1, ambiguous = unresolvable not broad). **No previously-traced counts change.**

**Format-note shape reconciliation — DONE (this was the open nested-vs-flat item).** The label-store record shape is the **FLAT identity form** — top-level `id` / `title` / `section_ref` / `section_index` / `section_key` — exactly as the pilot legs were built, NOT the nested `section{}` of the earlier format-note draft. `docs/label_store_format_note.md` §1 / §1.1 / §7 aligned to the flat shape and the `rubric_version` stamp bumped to v1.1; `source_target` added to the schema. Aligning the note to the built files (rather than re-shaping the data) was the ratified direction.

---

## Batched for the next revision (from 2026-07-24 — calibration-15 adjudication; the **v1.2** target)

**Build after the full calibration batch completes under v1.1 — one rubric version per batch. Do NOT rebuild to apply any single item.** Folds the calibration-15 adjudication (gold + adjudication.jsonl, batch `calibration-2026-07`). Categories throughout are ANALYTICAL — no burden counts change under any item here.

**14. (i) §2 — the control test (constitutive category redefinition; ratified 2026-07-24).** Replace the frequency/"day-to-day" framing of the Cat 1 / Cat 2 boundary with the **control axis**:
- **Cat 1 (direct)** = burdens attached to the actor's **own chosen operations** — standing standards AND duties that follow from the actor's own acts (hire → statement; sell → confirmation; transfer → notify).
- **Cat 2 (conditional / operational)** = triggered by events **substantially outside the actor's control** (death of a worker; a breach discovered; a worker qualifying; a third-party request). The **HSWA s.2(7) convention is now a RULE, not a convention**; undifferentiated change-triggers → Cat 2.
- **Cat 5** (befallen-by-regulator) unchanged.
- The axis in one line: **cost-of-doing-business (Cat 1) vs cost-of-things-happening-to-you (Cat 2/5).** Frequency and "day-to-day" are rejected as actor-relative; the clock test is rejected as measuring compliance-structure not burden-incidence (see the decision-log entry).
- **Worked gallery** to add: CRA s.9 / s.13 deemed terms → Cat 1; ERA s.1 written statement → Cat 1; LRSA s.23 reinstatement-after-ploughing → Cat 1; ERA 27BA guaranteed-hours (worker qualifying) → stays Cat 2; GDPR Art 13 disclosure-on-collection → Cat 1. (Full flip-list in `_calibration_adjudication_summary.md`.)

**15. (ii) §4/§2 — defence rule reordered (revealed-check leads) + the two-step discriminator.** State the order explicitly: **run the defence-revealed check FIRST** (is there an orphan private standard with no primary home elsewhere?). If yes → IB/IBA and it counts; if no → structural/burden_removal. Then the **two-step discriminator** for IB-vs-IBA and for defence-vs-screen: (1) **restate-as-imperative** (does the limb restate as a positive standard the actor must meet?); (2) **breachable-while-compliant** (could a compliant actor breach it?). Both yes → active pre-existing programme = **IBA**; restatable but satisfiable after the fact = **IB**; neither → not a burden (screens culpability). **Five-species set** (worked): FHW reg 11 (IBA) · ML reg 52B(3)(b) (IBA) vs 52B(3)(a) (screen) · TDA s.24 (IBA) · Bribery s.13(1) (structural) · Wild Mammals (IB/prohibition, exhaustion test). **One-revealed-standard-one-burden dedup note:** where two defence limbs reveal the *same* underlying standard, count it once (do not multiply the burden by the number of defence limbs).

**16. (iii) §4 — `culpability_filter` structural/burden_removal subclass + companion finding.** Add **`culpability_filter`** as a named `structural`/`burden_removal` subclass: a defence limb that screens the actor's mental state (knowledge, reasonable belief) rather than revealing a conduct standard — e.g. ML 52B(3)(a) ("did not know and had no reason to suspect"). **Companion finding (route to methodology, not a counting change):** tagging culpability_filter makes the **strict-liability share of the corpus a publishable dimension** — the proportion of offences with vs without a culpability screen. Retro-tag example: **RTA 1988 s.143(3)** ("no reason to believe uninsured").

**17. (iv) §3 — count notice-regimes, not demand-types + the statute-vs-instrument line.** A single notice/demand regime is **one burden**, not one-per-demand-type: **reg 66 (ML 2017)** — the (1) written-notice power, (3) officer-requirement, (1A) SAR-copy and (8) third-party extension are one comply-with-notice burden; **reg 36 (EPR)** — the enforcement-notice and incident-notice regimes are the constituted duties (per the v1.1 constituted-duties rule). **Statute-vs-instrument line:** where the statute itself spells out the duties (Factories s.10A inform/accommodate) count them **in-section** and the notice is trigger-only (no frontier); where the duty is "comply with the notice's own terms" (reg 66, HSWA s.22) it is a **frontier proxy**. Reg 36 / reg 66 are the paired worked example.

**18. (v) §3/§2A — frontier = content-carrying only + enum destinies.** A frontier proxy is counted only where the out-of-measure target **carries the operative content** (the notice/permit/byelaw/rulebook is where the rules actually live). Enum destinies for `frontier_target_type`: **notice** and **permit_licence** are **permanently proxied** (their contents are administrative, never enter the statute-book corpus); **byelaw** and **regulator_rulebook** are **expansion-eligible** (a future scope widening could take the layer in-measure, re-classifying those proxies to counted_at_source). Record this so the proxy population's future is a query, not archaeology.

**19. (vi) §3 — the who-serves-the-notice gate (Cat 2 vs Cat 5).** When a notice triggers a duty, decide the category by **who serves it**: an **external regulator/inspector** (HSE inspector for HSWA s.22; the employment medical adviser / EMAS for Factories s.10A) → **Cat 5**; an event within the actor's own operations → Cat 2. The server of the notice, not the existence of a notice, controls the category.

**20. (vii) §5 — formula-in-gateway vs formula-in-defence.** Where a numeric/qualitative formula appears, distinguish a **gateway formula** (defines who/what is in scope — folds as scope-eligibility, carries no burden) from a **defence formula** (a standard the actor must meet, revealed through a defence — routes through the defence-revealed check, item 15). Same formula-shaped text, opposite treatment by where it sits.

**21. (viii) Schema — `has_deadline` derived flag (DEFERRED, noted only).** The clock information dropped from the category axis survives as an **optional derived flag `has_deadline`** (true where the burden carries an explicit time-limit). **Not built now** — recorded so the compliance-timing view can be reconstructed later without re-labelling. Future, not this revision.

---
_This file is the running home for rubric-revision items only (plus, clearly fenced above, anything staged for another destination). Merge the rubric items into §7 / the relevant sections at the next revision, then prune them from here; move the "Route elsewhere" block to its destination and prune it too._
