# Lessons learned — evidence catalog from the previous project

Source: `../Versão_2/one_health_pipeline/README.md` (sections "Corrections applied",
2026-07-22 and 2026-07-23) and `../Versão_2/RESUMO_FINAL_SESSAO.md`. The 20 failures
below are reproduced based on those two documents — no number or description was
invented here; see the original README for the full technical detail of each item.

**How to use this document**: each item was originally discovered as a "pipeline
bug". Here they are reclassified by what actually caused the problem, to inform the
design of the tool (`02_metodologia.md`). Not every item is evidence of a failure in
the *external infrastructure* — several are internal bugs in the previous code,
listed separately because they are still a relevant lesson (how not to repeat the
same mistake in the new tool), but they do not count as a "bad score" for any
external source.

## A — Evidence of documentation failure (external source)

| # orig. | Source | What the documentation promised vs. what the API did |
|---|---|---|
| 2 | SciELO (via OpenAlex) | The publisher ID and field name originally used did not correspond to any real data; returned an HTTP 400 silently converted to "NA" |
| 4 | Ensembl Fungi | Endpoint does not expose coding-gene counts — not documented as absent, which led to filling in a fabricated per-genus value in the previous version of the pipeline |
| 7 | OpenAlex | API key treated as optional in the documentation; without it, the quota runs out after moderate use (~22h blocked) with no clear advance warning |
| 15 | NCBI Assembly (`db=assembly`) | Does not accept the standard `mindate`/`maxdate`/`datetype=pdat` parameters — silently returns 0; the date filter needs the non-standard `GRLS` field, undocumented in the common Entrez usage flow |

## B — Evidence of absent or unstable API (external source)

| # orig. | Source | Nature of the problem |
|---|---|---|
| 5 | Zenodo | Blocks any request with a spoofed browser User-Agent via WAF — access policy not documented anywhere accessible |
| 17 | SciELO | No real API of its own — access only via proxy (publisher filter in OpenAlex), which underestimated counts by 10-51x for the 19 pathogens, confirmed by manual browser verification |
| 18 | LILACS | No programmatic access equivalent whatsoever — `pesquisa.bvsalud.org` blocks direct requests (WAF with a JS challenge); accessible only via a real browser |

## C — Evidence of lack of integration between sources

| # orig. | Sources involved | Nature of the problem |
|---|---|---|
| 16 | PubMed + OpenAlex | ~70% content overlap between the two sources, with no common identifier enabling automatic deduplication — summing the two as "total literature" counts nearly the same article twice |
| 19 | PubMed vs. OpenAlex | For *Pneumocystis jirovecii*, the two sources gave contradictory reuse rates (0% vs. 4.27%) by classifying the same type of content differently — not an error in either one alone, it is a lack of comparable criteria between them |
| 3 | NCBI + PubMed (Entrez syntax) | The field-tag placement behavior (`[Organism]`, `[tiab]`) is counterintuitive and not standardized the way most users assume — applying the tag to the entire OR group instead of to each term caused ~53x underestimation, with no error or warning |

## D — Internal bugs in the previous pipeline (not evidence about the external source)

Relevant as an engineering lesson for the new tool, not as a "score" for any
external source:

- **#1** — Broken imports (`ImportError`) in `query_lilacs.py`/`query_scielo.py`: the
  modules never actually ran.
- **#6** — Dependency (`openpyxl`) used in the code but missing from `requirements.txt`.
- **#10, 11** — Network/parsing failure silently converted into `0`, instead of
  "not measured" — masking the difference between "genuinely zero" and "measurement
  failure".
- **#12** — `merge_results.py` converted every "NA" into `0` during final
  consolidation, contradicting the project's own methodological documentation.
- **#8** — The Ensembl fallback for non-taxonomic clinical labels (e.g., "Eumycetoma
  causative agents") mistakenly fell back to searching the entire Fungi kingdom.

**Direct lesson for the new tool**: the audit tool itself needs to avoid these same
patterns — never convert a "measurement failure" into zero, never mask a network
error as a valid result, always explicitly distinguish "the source says there is no
data" from "we could not measure".

## E — Metric-validity failures (out of scope for the current project)

These are not about the access infrastructure, but about the design of the previous
project's "reuse" metric — kept here only to avoid confusion when rereading
`../Versão_2/`:

- **#14** — The "reuse" term list had precision close to zero in its first version;
  redesigned to ~20-50% precision validated on only 2/19 pathogens.
- **#9, 13** — Filter for agricultural-literature contamination in Fusarium/Mucorales,
  partially resolved using MeSH vocabulary only in PubMed.
- **#20** — Synonym-artifact check in *N. glabrata*: investigated, confirmed not to
  be a bug.

## Quantitative summary

- **20 corrections catalogued** in the previous project.
- **4** show evidence of external-source documentation failure (category A).
- **3** show evidence of external-source API absence/instability (category B).
- **3** show evidence of lack of integration between sources (category C).
- **5** are internal pipeline bugs, not evidence about external sources (category D).
- **5** are about the validity of the reuse metric, out of scope for this project (category E).

This already provides an initial empirical basis that the three axes of the
evaluation model (`02_metodologia.md`) are not hypothetical — each one has at least 3
documented cases of real occurrence across the same 9 sources this project intends to
formally audit.
