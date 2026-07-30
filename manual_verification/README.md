# Manual verification — results

**Update (2026-07-29): PubMed, OpenAlex, Zenodo, NCBI, and Ensembl were extended from
the spot-check (1 pathogen) to the full 19**, at the researcher's explicit and
repeated request ("I want 19 for all of them! I've already asked for this before!").
Together with LILACS, SciELO, and DDBJ (already extended on 2026-07-28), this
completes full manual coverage (19/19) for **8 of the 9 sources**. The one exception
remains FungiDB, for a structural reason documented below (mandatory login since
March 2025) — not for lack of effort. The `*_amostra.csv` files were replaced by
`*_19_pathogens.csv`.


Validation layer 2 as defined in `../docs/02_methodology.md`: manual verification of
the 6 sample pathogens, compared against the tool's automated output
(`../resultados/auditoria.csv`, gitignored as it is regenerable bulk output — the
files in this folder **are** version-controlled because they are the validation data
itself, not an automatic regeneration).

## LILACS — completed (2026-07-27)

**Why start here**: of the 9 sources, LILACS is the only one the automated tool
marks "ND" on all three axes for having no testable programmatic endpoint at all —
exactly the case where manual verification changes the result, not just confirms it.

### Two steps performed

1. **Reconfirmation of the API block** (not assumed from the previous project —
   tested again, today): a direct HTTP request to `pesquisa.bvsalud.org/portal/`
   returned **HTTP 403**, served by a Bunny Shield challenge
   (`/.bunny-shield/assets/...`) — the same behavior documented in
   `../docs/03_lessons_learned.md`, item 18, now verified on this date, not merely
   inherited.
2. **Real count via browser** (`claude-in-chrome`, which passes the JS challenge
   normally), using the "LILACS Plus Collection" filter of the BVS Regional Portal.
   Initially for the 6-pathogen sample (2026-07-27); **extended to the full 19 on
   2026-07-28**, at the researcher's explicit request. Results in
   `lilacs_19_pathogens.csv`.

### Result

The 6 original values matched the previous project, with a small upward variation
(+4 to +97, consistent with ~4 days of newly indexed publications) — a good sign of
methodological stability. The 13 additional pathogens (2026-07-28) range from 5
records (Talaromyces marneffei) to 3,863 (Paracoccidioides spp.), with no unexpected
"zero" among the 19 — that is, all 19 pathogens have real, substantial coverage in
LILACS, despite there being no API at all to access it programmatically.

### Score update (API axis, LILACS source)

Before: `api_score = "ND"` (not determined — the tool had never automatically
tested this).

After this verification: `api_score = 0` (confirmed, not merely assumed — no
real programmatic access, confirmed with a direct HTTP attempt made today). This is
different from "ND": ND means "we don't know", 0 here means "we know, and it is
absent". Updated in `../src/audit_tool/scoring.py`.

`documentacao_score` remains "ND", but for a different reason now: it is not lack of
testing, it is that the axis genuinely does not apply to a source with no API at all
(there is no API-behavior documentation to evaluate). This is a real gap in the
rubric — noted as an explicit limitation to discuss in the manuscript (kept local,
not part of this repository).

`integracao_score` also remains "ND": even with real data confirmed, there is no
common identifier between LILACS and the other 8 sources to test cross-referencing —
it remains undeterminable with the tool's current design (it could only compare if
the other sources returned the same records, which would require a shared identifier
that does not exist).

## SciELO — completed (2026-07-27)

Same pattern as LILACS: native search on `search.scielo.org` (via browser — it has
no WAF like BVS does, but the goal here is not to bypass a block, it is to measure
against the real value, since the automated source is a proxy known to
underestimate). Initially 6 pathogens (2026-07-27); **extended to the full 19 on
2026-07-28**. Results in `scielo_19_pathogens.csv`.

### Result: underestimation reconfirmed across the 19, with an exact number per pathogen

| Pathogen | Native SciELO | OpenAlex proxy | Underestimation |
|---|---|---|---|
| Cryptococcus neoformans | 335 | 6 | 55.8x |
| Candida auris | 16 | 2 | 8.0x |
| Aspergillus fumigatus | 171 | 5 | 34.2x |
| Candida albicans | 927 | 48 | 19.3x |
| Nakaseomyces glabrata | 97 | 9 | 10.8x |
| Histoplasma spp. | 187 | 7 | 26.7x |
| Eumycetoma | 20 | 2 | 10.0x |
| Mucorales | 521 | 11 | 47.4x |
| Fusarium spp. | 1,948* | 13 | not comparable — see note |
| Candida tropicalis | 268 | 19 | 14.1x |
| Candida parapsilosis | 247 | 11 | 22.5x |
| Scedosporium spp. | 33 | 4 | 8.3x |
| Lomentospora prolificans | 4 | 0 | zero was an artifact |
| Coccidioides spp. | 52 | 5 | 10.4x |
| Pichia kudriavzevii | 166 | 7 | 23.7x |
| Cryptococcus gattii | 84 | 0 | zero was an artifact |
| Talaromyces marneffei | 1 | 0 | zero was an artifact |
| Pneumocystis jirovecii | 136 | 3 | 45.3x |
| Paracoccidioides spp. | 371 | 0 | zero was an artifact |

*The native Fusarium query was run **without** the botanical exclusion filter
(lessons, item 9) — the results include heavy agricultural literature (e.g.,
"Fusarium wilt of banana", pineapple and wheat cultivars), so 1,948 is not directly
comparable to the automated value (13) without reapplying the same filter. This
reconfirms live, today, the very problem documented in item 9 — it is not an error
of this verification, it is evidence of the same phenomenon.

**Statistical summary (n=14 comparable pathogens, excluding Fusarium and the 4
"zero was an artifact" cases: Lomentospora prolificans, Cryptococcus gattii,
Talaromyces marneffei, Paracoccidioides spp.)**: underestimation of **8.0x to
55.8x**, mean **24.0x** (standard deviation **15.9x**), median **20.9x**. The high
standard deviation shows the underestimation varies considerably across pathogens,
even though it is always large — not a constant factor. This supersedes the
approximate 10-51x range that came only from the previous project — it is now a
direct measurement from this session, across the 19 pathogens of the study, not an
extrapolation from 5 cases. SciELO's `documentacao_score` and `integracao_score`
remain `0` (they already were, they were not "ND") — only the score's supporting
note was updated in `../src/audit_tool/scoring.py`, with this evidence.

## DDBJ — completed, positive finding (2026-07-28)

Unlike LILACS/SciELO, the task here was not "check a number" — it was the
investigation, never truly carried out in the previous project, of whether a real
programmatic endpoint exists. **Result: it does, and no one had looked.**

Protocol: open `ddbj.nig.ac.jp/search/` in the browser, run a search for "Candida
auris", inspect the network requests fired by the page (`read_network_requests`).
Finding: `GET /search/api/entries/?keywords=...` — a real REST API, with official
OpenAPI 3.1 documentation published at `ddbj.nig.ac.jp/search/api-doc/`. Tested
against the documented response before implementing it (not assumed): the schema
matched exactly.

Implemented in `../src/audit_tool/sources/ddbj.py` — no longer a stub. Since it
became a real source in the automated layer, it already runs on all 19 pathogens as
of implementation (no extra browser cost — it is an API call, not manual
verification). Full values in `ddbj_19_pathogens.csv` (e.g., Candida albicans =
41,904 entries in the 15-year window; smallest value: Paracoccidioides spp. = 408).

**Caveat found and already recorded in `../src/audit_tool/scoring.py`**: DDBJ is one
of the 3 INSDC mirrors (along with NCBI/GenBank and EBI/ENA) — high, expected
structural overlap with this same tool's NCBI counts, with no automatic
deduplication. Same overlap risk pattern as PubMed/OpenAlex (lessons, items 16 and
19), now identified for genomic data — a new finding from this session, not
inherited from the original catalog.

## FungiDB — investigated, negative finding + unexpected discovery (2026-07-28)

Same protocol: open `fungidb.org/fungidb/app/search`. Immediate result: **"Please
log in to access this page"** — VEuPathDB (the organization behind FungiDB) moved
to a mandatory subscription/login model starting in March 2025. This was not
documented in the previous project because the UI had never actually been visited.

Further investigation: the REST backend (`fungidb.org/fungidb/service/...`) still
responds without login for metadata calls (`/service/`, `/service/record-types` →
HTTP 200) — that is, the API has not disappeared entirely. But the actual
organism search (`OrganismsByText`) requires a `POST` call with a `searchConfig`
body whose exact shape was not confirmed with confidence in this session.
**Deliberate decision: do not implement by trial and error** — guessing the body
structure and reporting an unverified number would repeat exactly the type of error
this entire project exists to prevent (see `../docs/03_lessons_learned.md`).
`fungidb.py` remains a stub; `scoring.py` documents the investigation with the date
and the specific reason, leaving no silent gap.

## PubMed, OpenAlex, Zenodo — completed, 19/19 (2026-07-29)

Extended from the 1-pathogen spot-check (Candida albicans, 2026-07-28) to the full
19, using the same query-parity technique already validated for LILACS/SciELO/DDBJ:
generate the search URL on each source's public site by literally reusing the tool's
query-construction function (`or_group_tagged`, same synonyms, same 15-year window),
run it via browser, read the total. Result in
`pubmed_openalex_zenodo_19_pathogens.csv`.

| Source | Exact or near-exact match | Largest discrepancy |
|---|---|---|
| PubMed | 19/19 (differences of -2 to +26, over totals ranging from hundreds to tens of thousands) | Candida albicans: API 28,208, site 28,182 (diff=26) |
| OpenAlex | 19/19 (differences of -61 to +1) | Candida albicans: API 75,989, site 76,050 (diff=-61) |
| Zenodo | 18/19 exact | **Candida auris: API 68, site 161 (diff=-93, ~2.4x) — see finding below** |

The small differences in PubMed/OpenAlex (typically <0.3% of the total) are
consistent with the hours/days elapsed between running the automated audit and the
manual verification, plus ongoing indexing on both databases — they do not indicate
a structural failure, unlike the systematic underestimation pattern already seen in
SciELO.

### Finding: Zenodo, Candida auris — real discrepancy not explained by a query error

The API and the site return different numbers (68 vs. 161) for the identical query
confirmed via `read_network_requests` (same URL, same parameters sent by the browser
to the `/api/records` endpoint). Explicitly tested whether `sort=bestmatch` would
explain the difference — removing the parameter, both modes still return 68. Unlike
the PubMed methodological finding (item below), here **no error was found in the
verification**: the divergence between the value served by the API and the value
rendered on Zenodo's own search page, for the same query, appears to be real —
possibly the site-side cache diverging from the API's live index. Recorded as an
unresolved anomaly, not a forced conclusion.

### Methodological finding (reconfirmed): a verification discrepancy is not always a source discrepancy

Repeating the caution already recorded in the original spot-check: when scaling up
to the 19, any large difference was re-checked against the possibility of an error
in the verification query itself before being recorded as a source finding (this is
how the initial PubMed discrepancy, on 2026-07-28, turned out to be a forgotten
synonym, not a real problem with the source).

## NCBI — completed, 19/19, with an alternative method (2026-07-29)

**The Assembly legacy search interface (`ncbi.nlm.nih.gov/assembly/?term=...`), used
in the 2026-07-28 spot-check, stopped working as a results list.** Tested again,
today, for all 19 -- every query, not only single-result ones, redirects straight to
a single genome record page (`ncbi.nlm.nih.gov/datasets/genome/GCF_...`), regardless
of how many results the API indicates exist. This is not a query limitation: it is a
real, current platform change (the NCBI Datasets page already notes an ongoing
transition process). A finding in its own right, not inherited from anywhere.

**Alternative method used for the 19**: the current genome browser,
`ncbi.nlm.nih.gov/datasets/genome/?taxon=<name>`, which shows a real count filterable
by taxon. It is not an exact methodological match with the tool (it does not apply
the same `GRLS` 2011-2026 date filter, and it resolves by taxon ID rather than the
Entrez synonym grouping used in `probe()`) -- hence treated as a "close" comparison,
not an "exact" one, following the same cautious pattern already used for the
Candida albicans spot-check. Data in `ncbi_19_pathogens.csv`.

| Result | Count | Pathogens |
|---|---|---|
| Exact match | 4/19 | Scedosporium (21=21), Lomentospora prolificans (7=7), Cryptococcus gattii (8=8), Paracoccidioides (17=17) |
| Close (small difference, same order of magnitude) | 14/19 | see CSV |
| Incomplete taxonomic scope in the API | 1/19 | Mucorales: API uses only 3 genera (Rhizopus/Mucor/Lichtheimia) = 204; the full Mucorales order in NCBI Datasets = 275 (includes Cunninghamella, Backusella, Gilbertella, etc.) |

**Side finding: taxonomic reclassification also present in NCBI.** NCBI Datasets
automatically resolves several of the names used by the tool to the currently
accepted taxonomic synonym: "Candida auris" → **Candidozyma auris**; "Candida
glabrata"/"Nakaseomyces glabrata" → **Nakaseomyces glabratus**; "Candida
parapsilosis" → **Lodderomyces parapsilosis**. This reinforces, in a third
independent source (after Ensembl, see below), that nomenclatural instability in
pathogenic fungi is not an isolated problem of a single infrastructure -- it is a
characteristic of the domain that any audit tool needs to handle explicitly, not a
one-off failure of a specific source.

## Ensembl — completed, 19/19 (2026-07-29)

Extended from the 2026-07-28 partial verification (2 exact matches + 1 qualitative
finding) to the full 19, using the "Filter" field of the official
`fungi.ensembl.org/species.html` table and reading the rendered table text
(`get_page_text`) -- a more reliable method than the general search UI used in the
initial attempt, which returned inconsistent result types across pathogens. Data in
`ensembl_19_pathogens.csv`.

| Result | Count | Detail |
|---|---|---|
| Exact match | 16/19 | Cryptococcus neoformans (41), Aspergillus fumigatus (6), Candida albicans (26), Histoplasma (5), Eumycetoma/Madurella mycetomatis (1), Fusarium (72), Candida tropicalis (1), Candida parapsilosis (1), Scedosporium (1), Lomentospora prolificans (1), Coccidioides (8), Pichia kudriavzevii (4), Talaromyces marneffei (4), Pneumocystis jirovecii (1), Paracoccidioides (5), and N. glabrata after reconciliation (see finding 1) |
| Qualitative finding (already documented) | 1/19 | Candida auris: API=7 isolates vs. the site shows 1 "featured genome" (two legitimate and different counting methods, not an error) |
| False negative due to taxonomic level | 1/19 | Mucorales: filtering by "Mucorales" returns nothing (0), because the table's "Classification" column shows the subphylum (e.g., Mucoromycotina), not the order -- confirmed that the genus Rhizopus alone already has 7 genomes under that subphylum. API=18. |
| Severe undercount due to species complex | 1/19 | **Cryptococcus gattii: API=5, table=16 (new finding, see below)** |

### Finding 1: Nakaseomyces glabrata — exact reconciliation via grammatical-gender genus variant

Searching for "Nakaseomyces glabrata" (feminine form) in the table returns **0**
results. Searching for "Candida glabrata" (historical synonym) returns **1**. The
hypothesis tested -- that the specific epithet's ending changes according to the
grammatical gender of the generic name ("-a" feminine in *Candida*, "-us" masculine
in *Nakaseomyces*) -- was confirmed by searching for "**Nakaseomyces glabratus**"
(masculine ending): **10** results. Adding 1 + 10 = **11**, exactly matching the
API's `raw_value` (11). An original methodological finding of this session:
taxonomic instability in pathogenic fungi can manifest not only as a synonym swap
(old vs. new genus), but as **grammatical gender agreement** within the binomial
system itself -- a silent undercounting mechanism that a naive text search (only the
feminine form, more intuitive for a speaker of a gendered language) would not detect
without knowing to search both forms.

### Finding 2: Cryptococcus gattii — severe undercount due to a cryptic species complex (new)

Searching for "Cryptococcus gattii" in the table returns **16** genomes (VGI-VGIV
lineages, isolates CA1280/CA1873/E566/EJB2/NT-10/Ru294/Ram5/WM276/etc.). The API
returns **5** -- less than a third. Unlike the N. glabrata finding (which
reconciles perfectly by summing the two name variants), here the divergence is large
and could not be reconciled with a second simple search: the "*Cryptococcus gattii*
species complex" was formally split into several cryptic species (*C. gattii* sensu
stricto, *C. deuterogattii*, *C. bacillisporus*, *C. tetragattii*, *C. decagattii*),
and the tool's search candidate (`'Cryptococcus gattii'`) likely resolves to a taxon
ID restricted to just one of these cryptic species, while the site's table still
uses the old complex name as the display label for all lineages, regardless of the
formal reclassification. **Same general mechanism as finding 1 (synonymy/species
complex instability in pathogenic fungi), but here producing an undercount of
~3.2x in the API instead of an exact reconciliation** -- evidence that this
mechanism is not always harmless when the two name forms are unified in the
comparison; sometimes it results in a real loss of coverage.

Ensembl's `documentacao_score` and `integracao_score` remain at the lessons-catalog
baseline (this session's extension covered the count, not the qualitative axes) --
the coverage caveat is discussed further in the manuscript (kept local, not part of
this repository).

## NCBI -- instrument-vs-source control test (2026-07-29)

Not a manual verification in the browser sense -- this checks whether the tool's own
HTTP call to NCBI Assembly can be trusted, by comparing it against Biopython
(`Bio.Entrez.esearch`), a widely used, community-maintained third-party client for
the same Entrez API. The goal: isolate whether any observed divergence reflects a
limitation of this project's script, or a genuine property of the source itself.

**Method**: for all 19 pathogens, the exact same query term built by
`src/audit_tool/common.py::or_group_tagged()` (including OR-combined multi-term
cases, e.g. *Nakaseomyces glabrata* / *Candida glabrata*) was submitted twice --
once through the script's own live probe, once through
`Bio.Entrez.esearch(db="assembly", term=...)` -- and the returned counts compared.

**Result: 19/19 exact matches.** Full data in `ncbi_biopython_control_test.csv`.
This does not rule out an instrument/source confound for the other 8 sources (not
tested this way), but for NCBI specifically it shows the script's plain
`requests`-based HTTP call reproduces a reference client's behavior exactly --
the divergence already documented elsewhere between the script and NCBI Datasets
(e.g. 948 vs. 869 for *Candida auris*) reflects a real difference between NCBI's own
interfaces, not a bug in this script. Added to the manuscript's Limitations section
and as Supplementary Table S6.
