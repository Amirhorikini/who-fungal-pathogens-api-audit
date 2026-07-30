# Session summary — new project (data infrastructure reliability audit)

A full redesign session, starting from scratch, based on everything learned from a
previous project by the same author. Consolidated on 2026-07-28, with an extension of
the manual verification and an editorial review of the manuscript on 2026-07-29.
**Project complete at this phase**: the manuscript in Portuguese is ready for the
author's target conference (`manuscrito/Manuscrito_completo_PT-BR.docx`). This file
preserves the narrative record of how the project was conducted; the current state
and repository structure are in `README.md`.

---

## How we got here

The researcher asked to use a guided conversation (Socratic mode) before any code, to
avoid repeating the same mistakes as the previous project. The research question
changed direction several times throughout the conversation before converging:

1. Vague starting point: "is what exists in the databases usable?"
2. Tied to a concrete scenario: epidemiological surveillance during a pandemic,
   deciding whether a reference genome already exists for an emerging strain —
   with no time for manual verification.
3. Expanded to three axes of unreliability (not just "wrong number"): lack of
   **integration** between sources, lack of **API**, lack of reliable
   **documentation**.
4. Final product decided: not a narrative paper — a **reusable audit tool** (Python
   CLI) + a tool paper describing its design and validation.

## Final research question

> Is the current infrastructure for accessing genomic and bibliographic data on WHO
> priority fungal pathogens — fragmented across sources with no integration, missing
> APIs in some, and unreliable documentation in the rest — ready to support, without
> manual verification, a surveillance team's decision about the availability of a
> reference genome for an emerging strain?

Full detail: `docs/01_research_question.md`.

## Methodology defined

- **Evaluation model**: a per-axis score (0-2: integration / API / documentation),
  not a single verdict — because the three problems do not always come together in
  the same source.
- **Validation**: a full automated layer (9 sources x 19 pathogens = 171
  combinations) + manual verification on a sample of 6 pathogens chosen for
  diversity of failure mode (not a random sample): Candida albicans, Eumycetoma,
  Nakaseomyces glabrata, Fusarium spp., Lomentospora prolificans, Pneumocystis
  jirovecii.

Full detail: `docs/02_methodology.md`, `docs/04_product.md`.

## Tool implemented (`src/`)

Python CLI (`audit.py`), one module per source (`audit_tool/sources/`), a scoring
rubric citing real evidence (`audit_tool/scoring.py`), CSV/Excel export
(`audit_tool/report.py`). Actually run against all 9 sources, not a skeleton.

## Automated audit result (171/171 combinations, 3 runs in this session)

| Source | API | Documentation | Integration |
|---|---|---|---|
| NCBI | 2 | 0 | 0 |
| PubMed | 2 | 0 | 0 |
| OpenAlex | 2 (with 1 observed HTTP 429 episode) | 1 | 0 |
| SciELO (proxy) | 2 | 0 | 0 |
| Ensembl | 2 | 1 | 1 |
| Zenodo | 2 | 1 | 2 |
| DDBJ | 2 (new endpoint, found in this session) | 2 | 0 |
| LILACS | 0 (confirmed absent) | ND | ND |
| FungiDB | ND (finding: requires login since Mar/2025) | ND | ND |

## Manual verification — final extension: 19/19 pathogens across 8 of the 9 sources (2026-07-29)

The original design called for a sample of 6 pathogens; the researcher explicitly
requested extending it to the full 19 ("I want 19 for all of them!"), carried out in
two stages.

- **LILACS**: API block reconfirmed (HTTP 403, Bunny Shield); real count via browser
  for all 19 pathogens, with no unexpected zeros.
- **SciELO**: systematic underestimation confirmed across the 19: 8.0x to 55.8x, mean
  24.0x, standard deviation 15.9x, median 20.9x (n=14 comparable).
- **DDBJ**: positive finding — a real, documented API (OpenAPI 3.1), never previously
  identified. Implemented, no longer a stub, runs on all 19 pathogens.
- **FungiDB**: well-documented negative finding — the UI requires login (a VEuPathDB
  policy change, ~Mar/2025); the backend responds without login only for metadata,
  not for a per-organism count with enough confidence to implement without risking a
  wrong number. Remains 0/19, deliberately, to avoid reporting an unverified number.
- **PubMed, OpenAlex, Zenodo**: extended from the 1-pathogen spot-check to the full
  19. PubMed and OpenAlex nearly exact across 19/19 (differences <0.3%). Zenodo exact
  in 18/19; Candida auris showed a real API-vs-site discrepancy (68 vs. 161) not
  explained by a query error.
- **NCBI**: the Assembly legacy search interface stopped working as a results list
  during this session (redirects straight to a single genome, for any query) —
  a platform change captured live. Extended to the 19 via NCBI Datasets
  (by taxon): 4/19 exact, 14/19 close. Side finding: automatic taxonomic
  reclassification of 3 organisms (Candidozyma auris, Nakaseomyces glabratus,
  Lodderomyces parapsilosis).
- **Ensembl**: extended from the partial verification (2 exact + 1 qualitative
  finding) to the full 19: 16/19 exact. Two original findings — *N. glabrata*
  reconciles exactly (1+10=11) by adding the historical synonym to the
  grammatically correct form of the epithet; *Cryptococcus gattii* does not
  reconcile, with an undercount of ~3.2x (API=5, actual=16) due to a cryptic
  species complex.

Full detail, with numbers and citations: `manual_verification/README.md`.

## Relevant side finding (a process lesson, not just a data one)

A PubMed comparison initially appeared to diverge substantially on the first attempt
(24,845 vs. 28,182) — the cause was an error in the verification query itself
(a forgotten synonym), not a tool bug. Once corrected, it matched exactly. Worth
keeping as a reminder: a "finding" of divergence needs a second check before becoming
a conclusion — the same principle this project applies to the sources it audits.

## Repository structure

```
Projeto/
├── README.md                 # overview and status
├── SESSION_SUMMARY.md        # this file
├── LICENSE / .gitignore
├── docs/                     # design reasoning (RQ, methodology, lessons, product)
├── manuscrito/                # manuscript skeleton (results/discussion still empty)
├── src/                       # the tool (Python CLI)
├── manual_verification/        # layer-2 validation evidence (version-controlled)
└── resultados/                # bulk audit output (gitignored, regenerable)
```

## Remaining open items

- Formalize `documentacao_score`/`integracao_score` as a dynamic calculation per
  source-pathogen combination (currently a fixed score per source, a baseline with
  cited evidence) — explicitly acknowledged as a limitation and future work in the
  manuscript.
- Investigate whether FungiDB's `searchConfig` body can be replicated with
  confidence (without forcing it by guessing).
- Translate the manuscript into English (required by the journal; the current
  version is PT-BR for the author's target conference).
- No git commit has been made yet — everything is staged, pending the researcher's
  decision.
