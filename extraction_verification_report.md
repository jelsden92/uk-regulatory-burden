# Extraction Rebuild — Verification Report

**Date:** 2026-07-03
**Subject:** `extract_candidates.py` rebuilt to the two-stage, section-level design; verified on the 7-Act set (fresh run, cached CLML XML — byte-identical to a live fetch).

## What was built

One candidate per **flagged section**, not per sentence. Section anchor = outermost P-level (UK sections / EU articles / schedule P-levels) ∪ innermost numbered `Division`/`Para` (EU recitals, schedule paragraphs), keyed on **DOM node identity** (`section_index`), never `section_ref`. Each section carries `material_type` (uk_body / uk_schedule / eu_article / eu_recital / orphan). **Stage-1** flags a section if ≥1 recall cue fires anywhere in its subtree; the full assembled block (chapeau + leaves, markers preserved) is emitted with **no truncation**, plus `leaves[]` as a structured list.

## Verification results (7 Acts: Bribery, Explosives, EP Regs, UK GDPR, ERA 1996, Land Reform Scotland, Commission Decision 2017/1283)

**(a) Section counts reproduce the measured baseline exactly**

| material_type | resolved | baseline | flagged (emitted) |
|---|---|---|---|
| uk_body | 727 | 727 ✅ | 571 |
| uk_schedule | 862 | 862 ✅ | 288 |
| eu_article | 106 | 106 ✅ | 78 |
| eu_recital | 611 | 611 ✅ | 145 |
| orphan | 2 sentences / 1 Act (flat fallback) | — | — |

Total candidate records emitted: **1,084**; all ids unique.

**(b) Recall hole closed** — 6,051 previously-dropped cue-less letter/roman leaves now ride inside their flagged sections (matches the predicted recovery exactly). Concrete: EP Regs reg 24 assembled block contains the two previously-dropped duties as cue-less leaves — `(i) "…cause the waste to be disposed of…"` and `(ii) "prevent the entry… of relevant gaseous waste…"`.

**(c) No truncation** — max assembled block 23,213 chars; 319 records exceed the old 2,000-char cap; zero records land exactly at 2,000 (the cap artifact is gone). Full text retained start-to-end.

**(d) DOM-identity keying** — 48 `section_ref` values are shared by >1 emitted record (would mis-merge if keyed on ref, e.g. Bribery "11" = an offence provision + a Schedule amendment); kept distinct via `section_index`. All 1,084 ids unique.

## Scope

Extraction (Layer 1) only. The Stage-2 labelling layer (burden-set per section, set-vs-set agreement, label store) is ratified design, not built. Reproduce via `python extract_candidates.py` (runs the 7 verification Acts).
