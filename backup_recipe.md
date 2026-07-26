# Artifacts backup — canonical recipe

The recipe for `UKRegBurden_artifacts_YYYY-MM-DD.zip`, the emailable project snapshot kept in
`C:\Users\jethr\Backups\UKRegBurden\`. Written 2026-07-05 so the contents never have to be
reverse-engineered again. Prior backups: `…_2026-06-29.zip`, `…_2026-07-03.zip`.

## What goes in

The working tree at repo root + `docs/`, **excluding** the categories below. Concretely, the
2026-07-05 backup was **derived from the 2026-07-03 zip's file list** (162 files) with the
deliberate changes recorded under "Recipe changes" — not a fresh whole-tree sweep, so the set is
stable and reviewable.

Included categories:
- **Pipeline + analysis code:** all `*.py` at root (core pipeline `extract_candidates.py`,
  `downloader.py`, `word_list.py`, `analyser.py`, `md_to_docx.py`, plus the `_*.py` analysis/probe
  scripts that document how figures were produced).
- **Docs:** `docs/*.md`, `docs/*.csv`, `docs/*.mmd` (methodology, implementation plan, research
  agenda, coverage note + table, and the decision-tree diagrams + gap list).
- **Root docs / notes:** `category_mapping.md`, `rubric_revision_notes.md`,
  `project_objective_anchor.md`, `tna_crosscheck_methodology.md`, `tna_dataset_comparison.md`,
  `extraction_verification_report.md`, `README.md`, the `api_exhaustion_*` / `exhaustion_v3_*` notes.
- **Untracked operational context (git-EXCLUDED — this backup is its ONLY protection):**
  `CLAUDE.md` (repo root) — the project knowledge base Claude Code loads at session start. It is
  gitignored as moat/operational context, so it lives only in the working tree and is in NO git
  history. It MUST be captured in every backup (a whole-tree zip will include it as a normal file;
  just don't let a git-only export miss it).
- **Word artefacts:** all `uk_reg_*.docx` version history, `project_decision_log.docx`, the coverage
  and TNA email `.docx`, the rubric drafts.
- **Auto-memory store (OUTSIDE the repo tree — pull in explicitly):**
  `C:\Users\jethr\.claude\projects\C--Users-jethr-OneDrive-Documents-OwnProjects-UKRegBurden\memory\`
  — the Claude Code project memory directory. Since 2026-07-26 it holds only working-preference
  memories (`MEMORY.md` + `user_*.md` + `feedback_honest_status.md`); the durable project facts were
  folded into the git-tracked root `CLAUDE.md`. Back up the whole `memory\` folder so the working
  preferences survive a machine loss (they are not in git). It is not under the repo root, so a
  whole-tree zip of the repo will miss it — copy it in as its own `memory/` subfolder.
- **Candidate outputs (CURRENT format only):** `candidates.jsonl`, `candidates_index.csv`,
  `candidates_dropped_dups.jsonl`. These MUST be the section-anchored format (fields `text`,
  `leaves`, `n_leaves`), never the retired per-sentence format (field `sentence`).
- **Validation / TNA / analysis data:** `validation_*.csv`, `tna_crosscheck_review_*.csv`,
  `tna_unflagged_sample_for_review.csv`, the `_tna_*` / `_ingest_*` / `_recoverable_*` intermediates,
  the `draft email to TNA.docx` and `na_*` email drafts.

## What stays out (exclusions)

- `*.db` (legislation.db, exhaustion checkpoints) — regenerable / huge.
- `Bulk download/` — GBs of source CLML XML.
- `*.zip` — including duties.zip, InForce_results zips, and prior artifact backups.
- `__pycache__/`, `.git/`.
- **Bulk corpus manifests** — `corpus_manifest.csv` (~35 MB), `InForce_results_47/*.csv` (~90 MB),
  `missing_*.csv`, `download_queue_ukla.csv`. **(Recipe change 2026-07-05 vs 07-03, which had
  included them.)** They bloat the zip ~10× for corpus-inventory data reproducible from the DB.

## Recipe changes (2026-07-05)

1. **Dropped the bulk corpus manifests** (see above) — deliberate; keeps the backup emailable
   (~2 MB vs ~21 MB).
2. **Dropped the `candidates_sample2.*` trio** — a redundant per-sentence fossil over the same 7
   Acts as `candidates.jsonl`; removed to end the two-formats confusion.
3. **Added current artefacts absent from the 07-03 set:** `uk_reg_methodology_v14.docx`,
   `uk_reg_plan_v15.docx`, `uk_reg_validation_rubric_v2_draft (3).docx`,
   `docs/pipeline_architecture.mmd`, `docs/candidate_decision_tree.mmd`, `docs/decision_tree_gaps.md`.

## How to rebuild

`candidates.jsonl` must be current first: `python extract_candidates.py` (regenerates over the 7
verification Acts in section-anchored format). Then zip the recipe set to
`C:\Users\jethr\Backups\UKRegBurden\UKRegBurden_artifacts_<today>.zip`. On OneDrive, force
hydration (copy the files) before zipping — dehydrated placeholders raise PermissionError on direct
read. Verify the zip contains `candidates.jsonl` in section-anchored format and excludes the bulk
manifests before emailing.
