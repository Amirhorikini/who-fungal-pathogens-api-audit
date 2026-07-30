# Reliability Audit of the Data Infrastructure for WHO Priority Fungal Pathogens

> Project complete. Audit protocol implemented and tested, two-layer validation
> complete. The accompanying manuscript is drafted separately and is **not**
> included in this public repository (unpublished academic work, kept local by
> design — see `GITHUB_CHECKLIST.md`).

Nine public genomic and bibliographic data sources are often treated as
interchangeable by anyone who needs a quick answer about a fungal pathogen —
"is there an assembled reference genome?", "is there relevant clinical literature?".
This project audits whether that trust is justified, testing each source live, three
times, against the 19 World Health Organization priority fungal pathogens, and
comparing what each API returns against a gold standard obtained independently from
the source's own public interface. The result is a reusable audit tool and a
scientific paper with empirical evidence — not assumption — of where that trust
holds up and where it does not.

## Key findings

- **SciELO** underestimates its own coverage by 8.0x-55.8x (mean 24.0x) when
  accessed through the only available programmatic path, a proxy via OpenAlex.
- **LILACS** has no programming interface whatsoever (HTTP 403 confirmed), despite
  real and substantial content for all 19 pathogens.
- **DDBJ** had a real, documented API that had never previously been identified.
- **FungiDB** started requiring login at some point between the literature consulted
  and the execution of this study — shifting from a usable source to a blocked one
  without notice.
- **Taxonomic instability** (reclassification of pathogenic fungal species) was
  triangulated independently across two genomic sources (Ensembl and NCBI), causing
  undercounts of up to 3.2x when the source does not recognize the current synonym.

Full source-by-source detail, with numbers: [`verificacao_manual/README.md`](verificacao_manual/README.md).

## Research question

> Is the current infrastructure for accessing genomic and bibliographic data on WHO
> priority fungal pathogens — fragmented across sources with no integration, missing
> APIs in some, and unreliable documentation in the rest — ready to support, without
> manual verification, a surveillance team's decision about the availability of a
> reference genome for an emerging strain?

Full detail, motivating scenario, and scope: [`docs/01_pergunta_de_pesquisa.md`](docs/01_pergunta_de_pesquisa.md).

## Final product

Not a purely narrative paper — a **reusable audit protocol/checklist** (`src/`) that
audits each data source along three axes (integration, API availability,
documentation quality), accompanied by a manuscript describing its design and
validation. The manuscript itself is not part of this public repository (see
[Repository structure](#repository-structure)).

Full methodological design (per-axis scoring model, validation strategy):
[`docs/02_metodologia.md`](docs/02_metodologia.md).

## Quick start

```bash
cd src
python3 -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# optional: contact e-mail for the APIs' User-Agent header (see .env.example)
export AUDIT_CONTACT_EMAIL="your-email@domain.org"

python audit.py --list-sources
python audit.py --source ncbi --pathogen "Candida auris"      # a single combination
python audit.py --all --output ../resultados/auditoria.csv    # all 171 combinations
```

More usage details: [`src/README.md`](src/README.md).

## The 9 data sources

NCBI (Assembly), PubMed, OpenAlex, SciELO, LILACS, Ensembl Fungi, Zenodo, DDBJ, FungiDB —
audited against the 19 WHO priority fungal pathogens (full list with
synonyms: `src/pathogens_19.csv`, also reproduced in the paper's Supplementary Material).

## Result, in one sentence per source

| Source | Manual coverage (19 pathogens) | Main finding |
|---|---|---|
| LILACS | 19/19 | No programmatic API (HTTP 403), but real and substantial content |
| SciELO | 19/19 | Automated proxy underestimates by 8.0-55.8x (mean 24.0x) |
| DDBJ | 19/19 | Real, documented API, never previously identified |
| PubMed | 19/19 | Near-exact match with the public interface |
| OpenAlex | 19/19 | Near-exact match with the public interface |
| Zenodo | 19/19 | 18/19 exact; 1 real, unexplained discrepancy (Candida auris) |
| NCBI | 19/19 | Legacy search interface discontinued; triple taxonomic reclassification confirmed |
| Ensembl | 19/19 | 16/19 exact; severe undercount (3.2x) for *Cryptococcus gattii* due to species complex |
| FungiDB | 0/19 | Blocked by a login wall since ~Mar/2025 (finding from this session) |

Full detail, with numbers and methodology per source:
[`verificacao_manual/README.md`](verificacao_manual/README.md).

### Per-axis score (automated layer, 0-2 scale)

| Source | Interface (API) | Documentation | Integration | Evidence (Doc./Integ.) |
|---|---|---|---|---|
| NCBI | 2 | 0 | 0 | Baseline |
| PubMed | 2 | 0 | 0 | Baseline |
| OpenAlex | 2 (with degradation under sustained use) | 1 | 0 | Baseline |
| SciELO (proxy) | 2 (inherits OpenAlex's degradation) | 0 | 0 | Reconfirmed in this study |
| Ensembl | 2 | 1 | 1 | Baseline |
| Zenodo | 2 | 1 | 2 | Baseline |
| DDBJ | 2 | 2 | 0 | New source, evidence from this study |
| LILACS | 0 | Not applicable | Undetermined | Interface reconfirmed in this study |
| FungiDB | Undetermined | Undetermined | Undetermined | Investigated in this study |

Five of the nine sources still rely on a baseline for the documentation and
integration axes (a declared limitation, discussed in the manuscript) — only the
programming-interface axis is recalculated per source-pathogen combination in this
version of the audit protocol.

### Map of taxonomic instability found

| Organism (tool label) | Alternative/current name | Source(s) | Result |
|---|---|---|---|
| Nakaseomyces glabrata | Candida glabrata + Nakaseomyces glabratus | Ensembl | Exact reconciliation (1+10=11=API) |
| Cryptococcus gattii | 5-species cryptic complex | Ensembl | Severe undercount (API=5, actual=16, ~3.2x) |
| Candida auris | Candidozyma auris | NCBI Datasets | Close, not exact (API=948, Datasets=869) |
| Candida glabrata | Nakaseomyces glabratus | NCBI Datasets | Close, not exact (API=108, Datasets=101) |
| Candida parapsilosis | Lodderomyces parapsilosis | NCBI Datasets | Close, not exact (API=105, Datasets=103) |
| Candida auris | -- (isolates vs. reference genome) | Ensembl | Qualitative finding (API=7, site=1) |
| Mucorales | -- (order level, not a synonym) | NCBI and Ensembl | Incomplete scope in the candidate list |

Three reclassifications resolved by NCBI Datasets and one by Ensembl were discovered
fully independently, on infrastructures with different curation and code — full
interpretation is in the manuscript (not part of this public repository).

### Complete raw data

Per-pathogen values (19 x 8 sources) and the full snapshot of the 171 automated
combinations are reproduced in the manuscript's Supplementary Material and, in raw
form, in `verificacao_manual/*_19_patogenos.csv` and `resultados/auditoria.csv`
(regenerable via `python audit.py --all`, not version-controlled).

## Repository structure

```
.
├── README.md
├── SESSION_SUMMARY.md                  # narrative summary of how the project was conducted
├── GITHUB_CHECKLIST.md                 # what's left to decide before publishing
├── CITATION.cff
├── LICENSE
├── .gitignore
├── .env.example                        # optional variables (e.g., API contact e-mail)
├── docs/                               # internal project design
│   ├── 01_pergunta_de_pesquisa.md      # RQ, motivating scenario, scope
│   ├── 02_metodologia.md               # per-axis scoring model + validation design
│   ├── 03_licoes_aprendidas.md         # failures from the previous project, categorized
│   └── 04_produto.md                   # format decision: CLI + rubric + output spreadsheet
├── src/                                 # the audit protocol (Python CLI)
│   ├── audit.py
│   ├── pathogens_19.csv
│   └── audit_tool/
└── verificacao_manual/                  # layer-2 validation evidence (version-controlled)
    ├── README.md                        # full source-by-source narrative
    └── *_19_patogenos.csv               # raw data for each manual verification
```

Not shown above: a `manuscrito/` folder exists locally with the manuscript draft and
its supplementary material, but it is deliberately excluded from this public
repository (listed in `.gitignore`) — it is unpublished academic work, kept local
until it goes through peer review and formal publication.

## Tool (`src/`)

```
src/
├── audit.py                # CLI — see src/README.md for usage
├── pathogens_19.csv         # the 19 pathogens, with literature and organism synonyms
├── requirements.txt
└── audit_tool/
    ├── common.py            # honest HTTP, no masked retries
    ├── scoring.py            # 0-2 per-axis rubric + cited baseline
    ├── report.py             # CSV/Excel export
    └── sources/              # one module per source (ncbi, pubmed, openalex, scielo,
                               #  lilacs, ensembl, zenodo, ddbj, fungidb)
```

Tested against all 9 sources (8 with a confirmed live API; FungiDB correctly marked
"ND" due to access being blocked, not for lack of testing). Run in full (171/171
combinations) 3 times over the course of development — detail in `src/README.md`,
section "Tested status". `resultados/` (output of `--all`) is not version-controlled
(see `.gitignore`); the validation data itself (`verificacao_manual/`) is
version-controlled.

## Status

- [x] Research question defined and confirmed
- [x] Evaluation model (per-axis score) defined and implemented
- [x] Two-layer validation design (full automated layer + manual verification)
- [x] Automated layer: 171/171 combinations, run 3 times
- [x] Full manual verification (19/19 pathogens) for 8 of the 9 sources
- [x] FungiDB investigated and documented as a structural blocker (not silently left out)
- [x] Manuscript drafted in Portuguese, formatted to the Springer Nature template used
      by the *Journal of Biomedical Semantics*, with Supplementary Material (kept local,
      not part of this repository)
- [x] No secrets/API keys in the code — contact e-mail configurable via an
      environment variable (see `.env.example`)
- [x] Repository translated to English and published
- [ ] Dynamic `documentacao_score`/`integracao_score` per source-pathogen combination
      (currently a fixed score per source — an acknowledged limitation, discussed in
      the manuscript)
- [ ] English translation of the manuscript itself (required by the journal; the
      current version is PT-BR for the author's target conference)

## How to cite

See [`CITATION.cff`](CITATION.cff). Summary: Amir Barbosa, Universidade de Ribeirão Preto
(UNAERP), 2026.

## Relationship to the previous project

The code in this project is new, and its research question differs from that of an
earlier project by the same author (outside this repository), which queried the same
9 sources to measure data reuse in the literature, not access reliability. That
earlier project served as a source of technical lessons reused here (see
`docs/03_licoes_aprendidas.md`), but it is neither a code dependency nor a source of
reused results. The manuscript (kept local, not part of this repository) does not
reference that earlier project — it describes this work as the first to apply this
audit design.

## License

MIT — see [`LICENSE`](LICENSE).
