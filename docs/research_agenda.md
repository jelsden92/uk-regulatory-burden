# UK Regulatory Burden Measurement

**Research Agenda: Issues, Open Questions and Future Phases**

_May 2026  |  Version 9 — Corpus complete; classifier development next_

> VERSION 9 UPDATE: Corpus build complete — 212,183 rows, 99.6%+ SI coverage. Status filtering removing 639,000+ no-force elements. Short act validation workbook established with 9 Acts fully validated. Key methodological decisions formalised: penalty-as-consequence, conditional obligation scope (including regulatory inspection powers), evidence supply as part of parent obligation, nested burdens.

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
| InForce1991 | 2,793 | Pre-Statute Law Database era legislation |
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

# PART 4 — Classifier Development

| Phase | Training data | Target | Status |
| --- | --- | --- | --- |
| Preliminary | ~20 Acts validated | Test accuracy on held-out Acts | Next — after 20 Acts complete |
| Production | ~50 Acts validated | Full run pipeline integration | ~4-6 weeks |
| Active learning | Medium-confidence cases reviewed | 94-96% accuracy | Post-run |

# PART 5 — Future Phases
- Phase 2 — Regulatory rulebooks (FCA Handbook, PRA Rulebook)
- Phase 3 — Monetisation and sectoral attribution
- Phase 4 — Planning system
- Phase 5 — Professional regulatory bodies
- Phase 6 — Post-Brexit divergence tracking
- Phase 7 — International comparisons
- Phase 8 — Productivity link

*Version 9 — May 2026. Corpus complete 212,183 rows. Short act validation workbook. Classifier development next.*
