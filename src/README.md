# Audit tool — usage

Implementation of the CLI described in `../docs/04_produto.md`. Actually tested
against the real APIs (not a skeleton/stub) — see "Tested status" section below.

## Setup

```bash
python3 -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

Optional: set your contact e-mail (sent in the User-Agent header of calls to public
APIs, e.g. OpenAlex, to enter the "polite pool" with a higher rate limit).
Copy `../.env.example` to `../.env` and fill in `AUDIT_CONTACT_EMAIL`, or export the
variable directly:

```bash
export AUDIT_CONTACT_EMAIL="your-email@domain.org"   # or set on Windows
```

Without this, the tool uses a generic placeholder (`your-email@example.org`) — it
works, but with no quota priority.

## Usage

```bash
# list available sources and pathogens
python audit.py --list-sources
python audit.py --list-pathogens

# run a single combination
python audit.py --source ncbi --pathogen "Candida auris"

# run everything (9 sources x 19 pathogens = 171 combinations) and generate a report
python audit.py --all --output ../resultados/auditoria.csv --excel
```

## What each report row contains

Per source-pathogen combination: a 0-2 score (or "ND" = not determined) on each of
the three axes (`api_score`, `documentacao_score`, `integracao_score`) with the
justification alongside it (`*_note`), plus the raw result of the live probe
(`http_status`, `latency_ms`, `raw_value`, `probe_error`).

**Important note on the axes**: `api_score` is computed dynamically from a real HTTP
call made at execution time — it is the only fully automated axis in this version.
`documentacao_score` and `integracao_score` are based on a baseline cited in
`../docs/03_licoes_aprendidas.md` — they remain a fixed score per source, not
recalculated per source-pathogen combination; explicitly acknowledged as a
limitation of the current product, discussed further in the manuscript (kept local,
not part of this repository).

## Tested status (updated 2026-07-29)

Actually run against the real APIs, not just syntactically checked — it went through
the full layer of 171 combinations (9 sources x 19 pathogens), 3 times over the
course of development, and had the count axis (`raw_value`) manually reconfirmed for
all 19 pathogens across 8 of the 9 sources (`../verificacao_manual/`):

- `ncbi`, `pubmed`, `openalex`, `scielo`, `ensembl`, `zenodo`, `ddbj` — real HTTP call
  confirmed, `http_status=200` in practically 100% of the 19 combinations for each
  (isolated rate-limiting episodes documented in the manuscript, kept local),
  with `raw_value` manually reconfirmed for all 19 pathogens.
- `lilacs` — API confirmed absent (not "ND"): a direct HTTP test returns 403 (Bunny
  Shield). Real data obtained via manual browser verification for the complete 19
  pathogens (`../verificacao_manual/lilacs_19_patogenos.csv`).
- `fungidb` — investigated, remains "ND" as a deliberate decision: the web UI
  requires login (a VEuPathDB policy change, ~Mar/2025), the REST backend responds
  without login only for metadata, not for a per-organism count with enough
  confidence to report without risking a wrong number (`../verificacao_manual/README.md`).

**DDBJ is no longer a stub** — it had a real, documented endpoint (OpenAPI 3.1) that
had never been looked for before this project. See `../verificacao_manual/README.md`,
section "DDBJ".

**NCBI Assembly**: the site's legacy search interface was discontinued during this
project (redirects straight to a single genome for any query, not only single-result
ones) — the `esearch` API used by the `ncbi.py` module continues to work normally;
what changed was only the manual-verification path, adapted to NCBI Datasets (see
`../verificacao_manual/README.md`, section "NCBI").

## What's missing (next implementation steps)

- Compute `documentacao_score`/`integracao_score` dynamically per source-pathogen
  combination (currently a static per-source baseline, though already citing
  concrete evidence, including the DDBJ/NCBI overlap identified in this session) —
  would require running all 9 sources for the same pathogen and comparing results
  against each other.
- Resolve taxonomic synonymy and hierarchy (genus/order) against a formal reference
  base (e.g., NCBI Taxonomy, Index Fungorum), instead of the hand-maintained
  candidate list in `pathogens_19.csv` — the current list already captures several
  known synonyms, but manual verification found cases it does not cover (e.g., the
  *Cryptococcus gattii* species complex on Ensembl, incomplete Mucorales genera on
  NCBI).
- FungiDB: attempt reverse-engineering of the `searchConfig` body for the
  `OrganismsByText` search only if there is dedicated time for it with careful
  validation — do not force it by guessing.
