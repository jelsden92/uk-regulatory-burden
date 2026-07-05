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

## Route elsewhere — NOT a rubric edit

**→ `project_decision_log.docx` ("The recurring patterns" section) — a new named pattern.**
Staged here per the "everything into the notes, batched" instruction; ready to paste into the decision log on your say-so (I did not edit the docx).

- **Pattern name (proposed): "One rule, multiple textual homes."** A single substantive rule has more than one place it can be written down, so the same burden risks being counted twice or zero times depending on which home the labeller lands on.
- **Evidence — third consecutive review catch of this species:** IB double-meaning (defence vs primary prohibition) → enabling-power / SI double-count (hook vs resulting instrument) → amendment double-count (amending instruction vs consolidated target).
- **Why it recurs here:** a **consolidated-plus-amending corpus** structurally creates multiple homes for one rule. This is the project's **characteristic failure surface** — recognise the next instance by shape, and reach for count-at-source.

---
_This file is the running home for rubric-revision items only (plus, clearly fenced above, anything staged for another destination). Merge the rubric items into §7 / the relevant sections at the next revision, then prune them from here; move the "Route elsewhere" block to its destination and prune it too._
