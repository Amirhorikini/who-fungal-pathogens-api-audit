"""Per-axis scoring rubric (0-2), as defined in ../docs/02_methodology.md.

Score domain: 0, 1, 2, or "ND" (not determined -- distinct from 0; used
when there is not enough evidence to evaluate the axis, never as a synonym
for "confirmed failure"). This distinction is the same lesson already applied
in the previous project for "NA" vs. an actual zero (../docs/03_lessons_learned.md,
category D).

KNOWN_BASELINE holds the Documentation and Integration scores -- axes that cannot
be measured with a single automated HTTP call, so they use as a starting point
the evidence already cataloged in ../docs/03_lessons_learned.md (each entry
cites its source item). This is real evidence already collected, not
guesswork -- but it must be reconfirmed by the manual sample-verification
layer (../docs/02_methodology.md) before it goes into the paper as a final
result, not just as a baseline.

The API score is computed dynamically from the live probe (see
classify_api_probe below) -- it is the only axis fully automatable in this
version of the tool.
"""

KNOWN_BASELINE = {
    "ncbi": {
        "documentacao": 0,
        "documentacao_note": "db=assembly silently ignores mindate/maxdate/datetype=pdat (returns 0 with no warning); requires the non-standard GRLS field for date filtering. Lessons, item 15.",
        "integracao": 0,
        "integracao_note": "NCBI/GenBank is one of the 3 INSDC mirrors (along with DDBJ and EBI/ENA) -- high, expected structural overlap with this same tool's DDBJ counts, with no automatic deduplication (same evidence cited under 'ddbj' below, from the other side). Finding from this session, not from the original catalog.",
    },
    "pubmed": {
        "documentacao": 0,
        "documentacao_note": "Entrez tag syntax (scoped per term, not per OR group) is counterintuitive and previously caused ~53x of silent underestimation in the earlier pipeline (lessons, item 3) -- FIXED in this tool's code (common.py::or_group_tagged), cited here not as an active bug, but as evidence that the official Entrez documentation does not make this behavior obvious to someone implementing it from scratch.",
        "integracao": 0,
        "integracao_note": "~70% non-deduplicable overlap with OpenAlex (lessons, item 16); content classification contradicts OpenAlex in at least one confirmed case (item 19).",
    },
    "openalex": {
        "documentacao": 1,
        "documentacao_note": "API key treated as optional in the documentation; quota exhaustion with no clear advance warning occurred under moderate use without a key (lessons, item 7).",
        "integracao": 0,
        "integracao_note": "Same overlap issue with PubMed cited above (items 16 and 19) -- no common identifier for automatic deduplication.",
    },
    "scielo": {
        "documentacao": 0,
        "documentacao_note": "Access only via the OpenAlex publisher proxy; the ID/field originally used were invalid (silent HTTP 400), and even after the fix the proxy underestimates the actual source (lessons, items 2 and 17). RECONFIRMED on 2026-07-27 with exact per-pathogen figures (../../manual_verification/scielo_amostra.csv): 19.3x (Candida albicans), 10.8x (N. glabrata), 10.0x (Eumycetoma), 45.3x (P. jirovecii), zero-as-artifact (Lomentospora prolificans).",
        "integracao": 0,
        "integracao_note": "Not an integrated native source -- depends entirely on OpenAlex's partial, underestimated coverage (fresh evidence in ../../manual_verification/scielo_amostra.csv).",
    },
    "lilacs": {
        "api": 0,
        "api_note": "CONFIRMED (not ND) on 2026-07-27: a direct HTTP request to pesquisa.bvsalud.org returned HTTP 403 via a Bunny Shield challenge; the actual count was only obtained via browser (manual verification, ../../manual_verification/lilacs_amostra.csv). The absence of an API is not assumed, it is tested as of this date.",
        "documentacao": "ND",
        "documentacao_note": "Axis not applicable -- with no API, there is no API-behavior documentation to evaluate against reality.",
        "integracao": "ND",
        "integracao_note": "No common identifier with the other 8 sources to test cross-referencing, even with a confirmed real data point (../../manual_verification/lilacs_amostra.csv) -- not determinable with the tool's current design.",
    },
    "ensembl": {
        "documentacao": 1,
        "documentacao_note": "The coding-gene-count field does not exist on this endpoint, with no clear indication in the standard documentation consulted (lessons, item 4) -- the rest of the payload matches what is documented.",
        "integracao": 1,
        "integracao_note": "Name-based indexing changes between the new/old synonym for reclassified taxa (e.g., Nakaseomyces glabrata vs. Candida glabrata); no known direct overlap with the other sources.",
    },
    "zenodo": {
        "documentacao": 1,
        "documentacao_note": "WAF blocking for a generic browser User-Agent is not documented anywhere accessible (lessons, item 5); other behaviors match the official documentation.",
        "integracao": 2,
        "integracao_note": "Supplementary data source with no known overlap with the other 8 sources in the set.",
    },
    "ddbj": {
        "documentacao": 2,
        "documentacao_note": "UPDATED on 2026-07-28 (no longer ND): the actual endpoint was found (GET /search/api/entries/), officially documented via OpenAPI 3.1 at ddbj.nig.ac.jp/search/api-doc/. Tested live against 'Candida auris' -- the response matches the documented schema exactly (../../manual_verification/ddbj_amostra.csv). The previous project had never actually investigated this (lessons, category D) -- the API existed the whole time, it just hadn't been looked for.",
        "integracao": 0,
        "integracao_note": "DDBJ is one of the 3 INSDC mirrors (along with NCBI/GenBank and EBI/ENA) -- high, expected structural overlap with this same tool's NCBI counts, with no common identifier used for deduplication. Same overlap risk pattern as PubMed/OpenAlex (items 16 and 19), but for genomic data -- new finding from this session, not from the original catalog.",
    },
    "fungidb": {
        "documentacao": "ND",
        "documentacao_note": "Investigated on 2026-07-28 (no longer 'never tested', but still ND): the REST backend (/fungidb/service/...) responds without login for metadata (record-types, search definitions), but an actual organism search (e.g., 'OrganismsByText') requires a POST with a 'searchConfig' body whose exact shape was not confirmed with confidence -- replicating it by trial and error would risk reporting an unverified number, the very error this project exists to avoid. Not implemented.",
        "integracao": "ND",
        "integracao_note": "No reliable programmatic data to cross-reference with other sources; genomic coverage is mostly mirrored by NCBI (same structural issue as DDBJ, see above).",
        "api": "ND",
        "api_note": "NEW FINDING on 2026-07-28: the web interface (fungidb.org/fungidb/app/search) now requires login/registration ('Please log in to access this page') -- a VEuPathDB subscription-model change starting March 2025, undocumented in the previous project because it had never visited the UI. The underlying REST service still responds without authentication for metadata calls (tested: /service/, /service/record-types -> HTTP 200), but no organism count query was confirmed as replicable without login. Kept as 'ND', not '0', because this is not a confirmed absence of an API -- it is a new, partially workaroundable barrier that is not yet fully mapped.",
    },
}


def classify_api_probe(probe):
    """API score (0-2) derived from a live ProbeResult -- the only axis
    fully automated in this version of the tool."""
    if not probe.attempted:
        return "ND", "No confirmed programmatic count endpoint -- not automatically testable."

    if probe.ok and probe.http_status == 200:
        latency_txt = f"{probe.latency_ms:.0f} ms" if probe.latency_ms is not None else "latency not measured"
        return 2, f"Interpretable HTTP 200 response ({latency_txt})."

    if probe.http_status == 429:
        return 1, "HTTP 429 (rate/quota limit) -- API exists but is degraded under load."

    if probe.http_status in (401, 403):
        return 0, f"HTTP {probe.http_status} -- access blocked (authentication or anti-bot)."

    if probe.error:
        return 0, f"Network/timeout/parsing failure: {probe.error}"

    if probe.http_status is not None:
        return 0, f"Unexpected HTTP {probe.http_status}."

    return "ND", "Inconclusive probe result."


def score_combination(probe):
    """Combines the 3 axes for a ProbeResult, returning a dict ready for the report."""
    baseline = KNOWN_BASELINE[probe.source]

    if not probe.attempted and "api" in baseline:
        # Source with no automated probe, but with manual-verification evidence
        # (see ../../manual_verification/) that already confirms the score -- it
        # doesn't stay "ND" just because the tool can't test this on its own.
        api_score, api_note = baseline["api"], baseline["api_note"]
    else:
        api_score, api_note = classify_api_probe(probe)

    return {
        "source": probe.source,
        "pathogen_id": probe.pathogen_id,
        "pathogen_label": probe.pathogen_label,
        "api_score": api_score,
        "api_note": api_note,
        "documentacao_score": baseline["documentacao"],
        "documentacao_note": baseline["documentacao_note"],
        "integracao_score": baseline["integracao"],
        "integracao_note": baseline["integracao_note"],
        "http_status": probe.http_status,
        "latency_ms": round(probe.latency_ms, 1) if probe.latency_ms is not None else "",
        "raw_value": probe.raw_value,
        "probe_error": probe.error or "",
        "probe_note": probe.note,
    }
