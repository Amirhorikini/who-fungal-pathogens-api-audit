# Methodology

## Evaluation model: per-axis score

Each of the 9 data sources receives **three separate scores**, not a single
binary verdict ("reliable"/"unreliable"):

- **Integration** — is the source interoperable with the others (compatible
  identifiers, non-contradictory results for the same search object, absence of
  non-deduplicable overlap)?
- **API** — does a real, documented programming interface exist, with stable access
  (no WAF/anti-bot blocking, no dependence on scraping a search results page)?
- **Documentation** — does the API's real behavior match what the documentation
  promises (field names, date filter formats, whether an access key is required,
  rate limits)?

**Why not a single verdict**: the previous project (`../Versão_2/`) showed, in
practice, that these three problems do not always come together — a source may have
a stable API but misleading documentation (e.g., NCBI Assembly), or have real,
substantial data but no programmatic API at all (e.g., LILACS). Collapsing this into
a single verdict would hide that nuance. See `03_licoes_aprendidas.md` for the
specific evidence behind each case.

### Objective per-axis scoring criteria (0-2 scale)

Each axis is scored from 0 to 2 per source, with criteria anchored in observable
evidence — not the evaluator's subjective judgment. The definition of each level
draws directly on the failure types already catalogued in `03_licoes_aprendidas.md`,
so the scale is calibrated against real cases, not hypothetical ones.

**Integration**
| Score | Criterion |
|---|---|
| 0 | Contradictory results or non-deduplicable overlap with another source in the set, with no way to resolve it automatically (e.g., the PubMed vs. OpenAlex case for *P. jirovecii*, item 19) |
| 1 | Known, documentable overlap/divergence, but with no automatic resolution — requires a manual decision by the tool's user on every use |
| 2 | Identifiers/format compatible with at least one other source in the set, allowing automatic cross-referencing or deduplication |

**API**
| Score | Criterion |
|---|---|
| 0 | No real programmatic API — only browser access or scraping blocked by a WAF/anti-bot system (e.g., LILACS, item 18) |
| 1 | API exists but is unstable, incomplete, or limited (severe rate limit, exhaustible quota, intermittent blocking — e.g., OpenAlex without a key, item 7) |
| 2 | Stable API, no workaround needed, no history of blocking observed during validation |

**Documentation**
| Score | Criterion |
|---|---|
| 0 | Real behavior diverges from the documentation in a way that produces a silent error — a wrong result with no signal (e.g., `db=assembly` ignoring the date filter with no warning, item 15) |
| 1 | Divergence exists but the error is visible/detectable (e.g., an explicit HTTP 400/403, not an incorrect result with no warning) |
| 2 | Observed behavior matches what is documented, with no divergence found during validation |

Score per source = the three scores reported side by side (not summed into a single
index), preserving the earlier decision not to collapse them into a binary verdict.
A sum/average (0-6) may be reported as a visual summary, but it never replaces the
three individual scores in the raw results.

## Validation design

**Decision**: a **single, systematic** validation round (not continuous, not an
indefinitely running monitoring service). The tool is validated once, formally, and
that validation becomes the core of the tool paper's "Methods" section.

Alternatives considered and set aside for now:

| Alternative | Why it was set aside (not eliminated — becomes future work) |
|---|---|
| Continuous verification built into the tool (redundant automatic check on every run) | More robust to silent long-term API changes, but too complex to build for the project's first version |
| Scheduled periodic revalidation (e.g., every 6 months) | A reasonable middle ground, but still requires recurring re-execution infrastructure not needed to answer the current research question |

### Two validation layers

1. **Automated layer — full coverage.** The tool runs against all 9 sources x 19
   pathogens (up to 171 combinations), reusing the pipeline already built in the
   previous project. Low computational cost — it is re-execution of queries already
   implemented, not new manual work.
2. **Manual verification layer — a representative sample, not all 171 combinations.**
   Manual, hands-on verification (as was already done for SciELO/LILACS in the
   previous project) is the real effort bottleneck — it is not feasible to repeat it
   for all 171 combinations. It follows the standard design of a diagnostic-test
   validation study: validate against a representative sample of the gold standard,
   not against the entire population, and generalize from the accuracy measured in
   that sample.

### Sample selection criteria for manual verification

Proposed sample: **6 of the 19 pathogens**, chosen to cover the case-specific failure
types already documented in `03_licoes_aprendidas.md`, not for convenience or volume:

| Pathogen | Why it is in the sample |
|---|---|
| Candida albicans | "Standard" case — simple name, high N across all sources; serves as a baseline with no known edge case |
| Eumycetoma causative agents | Clinical label, not a taxonomic name — already broke the Ensembl fallback (item 8); tests robustness to non-standard names |
| Nakaseomyces glabrata (Candida glabrata) | Recent taxonomic reclassification with an older synonym still in current use — tests whether the source recognizes both names |
| Fusarium spp. | Divergent search method across sources (MeSH in PubMed vs. keyword filter in the others, item 13) — tests the integration axis directly |
| Lomentospora prolificans | Smallest N in the set (33 deposits, 265 PubMed) — tests source behavior at low volume, where "zero" could be real or a measurement failure |
| Pneumocystis jirovecii | Documented source of contradiction between PubMed and OpenAlex (item 19) — tests the integration axis on an already-confirmed case, not a hypothetical one |

Each of the 6 is manually verified across the 9 sources (54 verified combinations
instead of 171), with the explicit logic that the choice prioritizes diversity of
failure mode over statistical representativeness of a random sample — consistent
with the goal of testing the tool against already-known failure types, not
estimating a generalizable error rate through probabilistic sampling. This
limitation (non-random sample) is to be stated explicitly in the paper.

### Update (2026-07-28): coverage extended for 3 of the 9 sources

At the researcher's explicit request, **LILACS, SciELO, and DDBJ had their manual
verification extended from the 6-pathogen sample to the full 19 pathogens** — not
because the 6-pathogen sample had failed (it had not: both sources showed exactly the
pattern the sample had already detected), but because, for these three sources
specifically, the cost of extending was low enough to justify full coverage:

- **DDBJ**: near-zero cost — it became a real API source, so the 19 come free from
  the automated layer, with no extra manual work.
- **LILACS and SciELO**: real cost (26 additional browser navigations), but still
  feasible within a session, and these are precisely the two sources with the
  strongest finding of the study (systematic underestimation/absence of an API) —
  worth having the complete data, not just the sample, for this specific finding.

**The other 6 sources remain on the original design** (6-pathogen sample, or a
1-pathogen spot-check, or not verified) — the sampling logic remains valid there;
there was no decision to abandon sampling as a general principle, only to apply full
coverage where the cost-benefit balance changed. See `../verificacao_manual/README.md`
for the updated status of each source.

## Why the unit of analysis cannot be just "per source"

Evidence from the previous project: failures were frequently specific to the *case*
queried, not a generic, stable property of the entire source. Examples:

- The Ensembl bug for "Eumycetoma causative agents" (item 8) only appeared because
  this is a clinical label, not a taxon name — other Ensembl pathogens did not
  trigger this fallback.
- Fusarium/Mucorales broke in a way (contamination by agricultural literature) that
  Candida albicans did not, across the same 4 literature sources (item 9).

For this reason the automated layer covers all 171 full combinations (source x
pathogen), not just 9 generic per-source checks — even though the more expensive
manual verification needs to be sampled.

### Real limitation, found during critical review (2026-07-28): this only holds for the API axis

The argument above is true and implemented **for the API axis**: `api_score` is
computed from a live probe per combination, and it does capture case-specific
failures (e.g., an OpenAlex HTTP 429, an isolated Zenodo timeout).

**It is not true, in the current version of the tool, for the Documentation and
Integration axes.** `score_combination()` in `src/audit_tool/scoring.py` assigns the
scores for these two axes from `KNOWN_BASELINE[source]` — a fixed score per source,
repeated identically across the 19 rows of each source in the report. This was
identified during an independent critical review of this project and **was not
clearly stated** in earlier versions of this document or in the manuscript. The
171-combination table is real and complete for the API axis; for Documentation and
Integration, it is a per-source score (9 values, not 171) repeated per row to
preserve the tabular format — not a case-sensitive measurement as the earlier text
implied.

**Consequence**: the claim that "each source module applies the 3-axis rubric, not
just the raw count" (`04_produto.md`) needs to be read with this caveat. Properly
fixing this (making Documentation/Integration pathogen-sensitive) is future work, not
implemented in this version — see `04_produto.md`, section "What this does NOT yet
decide".

## Metrics inherited from the previous project — do not reuse without review

The previous project had a "reuse rate" metric with precision validated on only
2/19 pathogens (20-50%, never formalized as a confidence interval). This metric **is
not the object of this project** — the current product does not measure data reuse,
it measures the reliability of the access infrastructure. Mentioned here only to
avoid confusing the two when rereading `../Versão_2/`.
