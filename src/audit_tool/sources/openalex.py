"""OpenAlex (works?filter=...) -- broad literature per organism.

Reuses the filter syntax already validated in
../../../Versão_2/one_health_pipeline/bin/query_openalex.py.
"""
from ..common import timed_get, CONTACT_EMAIL
from .base import ProbeResult

OPENALEX_URL = "https://api.openalex.org/works"


def format_search(terms):
    return " OR ".join([f'"{t}"' for t in terms])


def probe(pathogen, years=15, email=CONTACT_EMAIL):
    import datetime
    end_year = datetime.datetime.now().year
    start_year = end_year - years

    pathogen_clause = f"title_and_abstract.search:({format_search(pathogen['lit_synonyms'])})"
    date_filter = f"from_publication_date:{start_year}-01-01,to_publication_date:{end_year}-12-31"
    params = {"filter": f"{pathogen_clause},{date_filter}", "per_page": 1}
    headers = {"User-Agent": f"OneHealthAuditTool/1.0 (mailto:{email})"}

    resp, latency_ms, err = timed_get(OPENALEX_URL, params=params, headers=headers)

    if err is not None:
        return ProbeResult("openalex", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, latency_ms=latency_ms, error=err)

    http_status = resp.status_code
    if http_status != 200:
        return ProbeResult("openalex", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status, latency_ms=latency_ms)

    try:
        count = int(resp.json().get("meta", {}).get("count", 0))
        return ProbeResult("openalex", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=True, http_status=http_status,
                            latency_ms=latency_ms, raw_value=count)
    except (KeyError, ValueError, TypeError) as e:
        return ProbeResult("openalex", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status,
                            latency_ms=latency_ms, error=f"unexpected response: {e}")
