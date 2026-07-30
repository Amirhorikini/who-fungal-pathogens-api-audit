# Final product format

## Decision: a command-line interface (CLI), in Python

Among the three options (CLI, manual checklist, spreadsheet), the decision is not
mutually exclusive by nature — each solves a different part of the problem. But only
one can be the **central product**, because only one can execute the automated layer
defined in `02_methodology.md` (9 sources x 19 pathogens, up to 171 combinations). A
checklist or a spreadsheet, on their own, cannot query 9 live APIs.

| Option | Why it is not the central product |
|---|---|
| Manual checklist (rubric on paper/PDF only) | Executes nothing — would require manually repeating the check for each of the 171 combinations on every use, the opposite of what the research question argues is infeasible in an emergency |
| Spreadsheet (data structure only) | Records the result but does not produce it — needs something that queries the 9 APIs and fills the spreadsheet |
| **CLI (Python) — chosen** | Executes the query against the 9 sources, applies the scoring rubric automatically where possible, and generates the report — directly reuses the modules already written and debugged in `../Versão_2/one_health_pipeline/bin/` |

## How the checklist and spreadsheet fit in, without becoming competing products

- **Checklist** = the 0-2 per-axis scoring rubric (already defined in
  `02_methodology.md`) does not disappear — it becomes the decision logic the CLI
  applies internally, and it also serves as a printed/readable reference for
  whoever performs manual verification of the 6-pathogen sample, ensuring the manual
  and automated criteria are exactly the same.
- **Spreadsheet** = an output format, not the mechanism. The CLI exports the
  consolidated result as CSV/Excel (the same pattern as the previous project's
  `merge_results.py` — 1 row per source-pathogen combination, 3 score columns plus
  evidence/textual note for each axis), and the sample's manual verification is
  recorded in a separate, comparable spreadsheet, used to calculate the tool's
  accuracy (validation layer 2).

## High-level architecture (draft, subject to revision during implementation)

```
audit.py --source ncbi --pathogen "Candida albicans"    # runs one combination
audit.py --all                                          # runs all 171 combinations
audit.py --report                                       # consolidates into CSV/Excel
```

- Reuses, as a starting point, the query modules already existing in
  `../Versão_2/one_health_pipeline/bin/` (one per source) — not as a direct copy, but
  as a reference, because several of these modules carry the internal bugs
  catalogued in `03_lessons_learned.md` (category D) that need to be fixed or
  rewritten, not inherited.
- Each source module, besides collecting the data (as it already did), returns a
  `ProbeResult` used to compute the **API** axis score per source-pathogen
  combination (via a live probe). **Correction (2026-07-28, finding from critical
  review)**: the Documentation and Integration axes are **not** recalculated per
  combination in this version — they come from `KNOWN_BASELINE` in `scoring.py`, a
  fixed score per source (9 values), repeated across the 19 report rows for tabular
  consistency, not measured case by case. See `02_methodology.md`, section "Real
  limitation, found during critical review".
- Structured output (CSV/JSON) is the contract between the CLI and the consolidated
  report — the same logic as the previous `merge_results.py`, adapted for the 3
  per-axis scores instead of a reuse count/percentage.

## What this does NOT yet decide

- Whether the CLI runs via Nextflow (like the previous project) or as a simpler,
  direct Python script — the previous project used Nextflow because of parallelism
  across the 9 sources, but that may be over-engineering for a leaner audit tool.
  To be decided during the implementation phase, not now.
- **How to make Documentation and Integration genuinely pathogen-sensitive** (today
  they are a fixed score per source — see above). Likely next step: Documentation
  could check, per combination, whether the expected field/format actually came
  back in the response (not just whether the source responded); Integration could
  automatically compare the `raw_value` of two related sources (e.g., PubMed vs.
  OpenAlex) for the same pathogen and flag a large divergence. Neither is
  implemented.
