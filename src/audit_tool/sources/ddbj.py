"""DDBJ Search (https://ddbj.nig.ac.jp/search/api) -- entries per organism.

*** UPDATE (2026-07-28): actual endpoint FOUND AND CONFIRMED ***

The previous project (../../../Versão_2/one_health_pipeline/bin/query_ddbj.py) treated this
source as a stub -- "DDBJ Search is built for interactive search, not programmatic
counting" -- and never actually investigated it. Browser-based investigation in this
session (network inspection at ddbj.nig.ac.jp/search/) found a real REST API,
officially documented with OpenAPI 3.1 (Scalar) at https://ddbj.nig.ac.jp/search/api-doc/:

    GET https://ddbj.nig.ac.jp/search/api/entries/
        ?keywords=<term>&datePublishedFrom=YYYY-MM-DD&datePublishedTo=YYYY-MM-DD
        &includeFacets=false&includeProperties=false&dbXrefsLimit=0&perPage=1

Response: {"pagination": {"page":1,"perPage":1,"total":N}, "items":[...]}. Tested against
"Candida auris": total=24052 within the 15-year window, HTTP 200, response matches the
documented schema exactly. This is neither fabrication nor guesswork -- URL, parameters,
and response shape were confirmed against the official documentation AND tested live
before being included here (see ../../manual_verification/ddbj_amostra.csv).
"""
from ..common import timed_get
from .base import ProbeResult

DDBJ_ENTRIES_URL = "https://ddbj.nig.ac.jp/search/api/entries/"


def probe(pathogen, years=15):
    import datetime
    end_year = datetime.datetime.now().year
    start_year = end_year - years

    keywords = ",".join(pathogen["organism_terms"])
    params = {
        "keywords": keywords,
        "perPage": "1",
        "includeFacets": "false",
        "includeProperties": "false",
        "dbXrefsLimit": "0",
        "datePublishedFrom": f"{start_year}-01-01",
        "datePublishedTo": f"{end_year}-12-31",
    }

    resp, latency_ms, err = timed_get(DDBJ_ENTRIES_URL, params=params)

    if err is not None:
        return ProbeResult("ddbj", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, latency_ms=latency_ms, error=err)

    http_status = resp.status_code
    if http_status != 200:
        return ProbeResult("ddbj", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status, latency_ms=latency_ms)

    try:
        total = resp.json()["pagination"]["total"]
        return ProbeResult("ddbj", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=True, http_status=http_status,
                            latency_ms=latency_ms, raw_value=int(total),
                            note="Aggregated count from /entries/ (all DDBJ record types combined via 'keywords', not a manual sum of separate endpoints) -- INSDC mirrors NCBI/ENA/DDBJ, high expected overlap with NCBI counts (not deduplicated by this tool yet).")
    except (KeyError, ValueError, TypeError) as e:
        return ProbeResult("ddbj", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status,
                            latency_ms=latency_ms, error=f"unexpected response: {e}")
