# Research question

## Final statement

> Is the current infrastructure for accessing genomic and bibliographic data on WHO
> priority fungal pathogens — fragmented across sources with no integration, missing
> APIs in some, and unreliable documentation in the rest — ready to support, without
> manual verification, a surveillance team's decision about the availability of a
> reference genome for an emerging strain?

## How this question was reached

Starting point (vague, first formulation): *"Is what exists in the databases usable?
Are we ready to look back?"*

Refinement, in order:

1. **Focus on need + access tool** — this is not about the quality of the primary
   data itself, it is about whether the *access tool* (API, search, documentation)
   allows one to trust what it returns.
2. **Motivating scenario: pandemic/emergency.** The question only holds real weight
   when tied to a situation with no time (and often no technical expertise) for
   manual verification — which is exactly what this project and the previous one had
   to do repeatedly to trust the numbers (e.g., manual browser-based verification of
   SciELO/LILACS, see `03_lessons_learned.md`).
3. **Concrete scenario chosen**: an epidemiological surveillance team trying to
   quickly determine whether an assembled reference genome already exists for an
   emerging fungal strain. This shifts the focus away from purely bibliometric
   sources (PubMed, OpenAlex, SciELO — literature reuse) toward genomic availability
   sources (NCBI, Ensembl, DDBJ — "does an assembled genome exist for this
   organism?").
4. **Three dimensions of unreliability**, added explicitly by the researcher after an
   initial formulation that only covered "reliability under time pressure":
   - **Integration** — sources do not talk to each other (different formats,
     identifiers, and behaviors; non-deduplicated overlap between PubMed/OpenAlex;
     contradictory results between sources for the same pathogen).
   - **Lack of API** — genuine absence of a programmatic API in some sources (not
     merely an unstable or poorly documented API), forcing manual browser-based
     verification.
   - **Lack of documentation** — missing, outdated, or simply incorrect
     documentation, leading to incorrect assumptions about field names, IDs, date
     filter formats, etc.

## Motivating scenario (final agreed form)

> During a pandemic, the access tool needs to be reliable even without manual
> verification, because a surveillance team has no time — and often no technical
> expertise — to open a browser and check whether the number the API returned
> matches reality. It will act directly on whatever the tool reports, right or
> wrong. And what makes it unreliable is not always "wrong number": it can be a
> source with no integration with the others, a source with no API at all, or a
> source with misleading documentation.

## Final product

**An audit tool/checklist plus a tool paper** (not a purely narrative paper). See
`02_methodology.md` for the design.

Justification of the choice, among three paths considered:

| Path | Why it was not chosen |
|---|---|
| Methodology/scientometrics paper (text only, no tool) | Faster, but risks being read as a "bug report" with no reusable product |
| Technical note/perspective for the organizations (NCBI, OpenAlex, BIREME) | Greater potential impact, but depends on third-party reaction, outside the researcher's control |
| **Tool/checklist + tool paper (chosen)** | Builds on the pipeline already developed in the previous project; produces something another group can run, not just read |

## Scope

**In scope**: the 9 sources inherited from the previous project — NCBI (Assembly/SRA/GEO),
PubMed, OpenAlex, SciELO, LILACS, Ensembl Fungi, Zenodo, DDBJ, FungiDB — evaluated on
the three axes (integration, API, documentation) for the 19 WHO priority fungal
pathogens (WHO FPPL 2022).

**Out of scope (for now)**: continuous/long-term monitoring of the infrastructure
(see `02_methodology.md`, discarded alternative in favor of a single validation
round); assessment of the quality of the primary data itself (e.g., the quality of a
deposited genome) — the focus is the reliability of the *access layer*, not the
underlying data.

## Product format

Decided: a command-line interface (CLI) tool in Python, with the scoring rubric and
the results spreadsheet as components of it, not competing alternatives. Full
justification: `04_product.md`.

## Still open

- Success criterion for the reviewer: what counts as a publishable contribution in
  this tool+paper format, versus what the previous project's simulated review board
  already flagged as insufficient (see `../Versão_2/conselho/`).
- Whether execution uses Nextflow (like the previous project) or a direct Python
  script — see `04_product.md`, final section.
