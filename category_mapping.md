# UK Regulatory Burden — Canonical Category & Polarity Mapping

**This is the canonical reference for the label schema. Cite it wherever categories are published.**

**Numeric IDs are canonical and rename-proof.** The data, model, and pipeline key on the integer ID only. The names below are a *presentation layer* — they may change (e.g. for a publication or a specific audience) without touching any data, model, or code. When names change, update the "Rubric name" column here; the IDs never change.

_Note: `private_actor` is the **parent class** (the provision imposes a private-actor burden at all) — it is NOT a category. `actor_capacity` (economic / personal / both / ambiguous) is a separate classification axis, not part of this table._

Last updated: 2026-07-03. Category names track the rubric; the two conditional renames below are folded into the next rubric revision.

## Categories

| ID | Rubric name (presentational) | One-line definition |
| --- | --- | --- |
| 1 | Direct burden | A standing obligation or prohibition that applies at all times, requiring continuous compliance activity (e.g. holding a licence to operate). |
| 2 | Conditional burden (operational) | An obligation triggered by an event or circumstance arising within the actor's own activities — whether or not the actor deliberately caused it — requiring an immediate, direct compliance action when it occurs. |
| 3 | Implied burden (IB) | An obligation revealed through a defence provision rather than stated as a direct command; satisfiable by after-the-fact explanation, without pre-existing operational setup. |
| 4 | Implied burden active (IBA) | As IB, but the defence structurally requires an active, pre-existing compliance programme built and maintained in advance; cannot be satisfied by after-the-fact explanation. |
| 5 | Conditional burden (regulator-triggered) | An obligation activated by an external regulator's discretionary decision (notice, warrant, inspection) to which the actor must submit; the regulator, not the actor, controls the trigger. |
| 6 | Ambiguous | Genuinely unclear which of categories 1–5 applies after careful reading; routed to human review rather than forced. |

## Polarity (a separate attribute on every category)

| Value | Definition |
| --- | --- |
| obligation | The operative requirement is that the actor DO something (file, maintain, report, ensure, hold). |
| prohibition | The operative requirement is that the actor REFRAIN from something (must not, shall not, no person shall; includes offence-as-prohibition). |
| review | Genuinely ambiguous after applying the operative-requirement rule; routed to human/LLM adjudication. |

## Discriminator note — categories 2 vs 5

The two "Conditional burden" categories differ only by **who controls the trigger**: Cat 2 = an event/circumstance within the actor's own activities (a workplace death → operational); Cat 5 = an external regulator's discretionary decision (an inspection demand → regulator-triggered). The shared family word "Conditional burden" plus the parenthetical differentiator encodes this distinction (IB/IBA-style), replacing the earlier bare "Conditional" names that risked conflation.
