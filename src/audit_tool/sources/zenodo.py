"""Zenodo (records API, Elasticsearch syntax) -- supplementary data/materials.

Reuses the endpoint and honest header already validated in
../../../Versão_2/one_health_pipeline/bin/query_zenodo.py -- the default fake-browser
UA was blocked by the WAF (lessons, item 5); this tool already uses an honest
User-Agent by default in common.py, so no special handling is needed here beyond
keeping the defensive parsing of `hits.total`.
"""
from ..common import timed_get
from .base import ProbeResult

ZENODO_URL = "https://zenodo.org/api/records"


def or_group_quoted(terms):
    return "(" + " OR ".join([f'"{t}"' for t in terms]) + ")"


def extract_total(data):
    total = data.get("hits", {}).get("total")
    if isinstance(total, dict):
        return total.get("value")
    return total


def probe(pathogen, years=15):
    import datetime
    end_year = datetime.datetime.now().year
    start_year = end_year - years

    pathogen_or = or_group_quoted(pathogen["lit_synonyms"])
    date_clause = f"metadata.publication_date:[{start_year} TO {end_year}]"
    params = {"q": f"{pathogen_or} AND {date_clause}", "size": 1, "page": 1}

    resp, latency_ms, err = timed_get(ZENODO_URL, params=params)

    if err is not None:
        return ProbeResult("zenodo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, latency_ms=latency_ms, error=err)

    http_status = resp.status_code
    if http_status != 200:
        return ProbeResult("zenodo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status, latency_ms=latency_ms)

    try:
        total = extract_total(resp.json())
        if total is None:
            return ProbeResult("zenodo", pathogen["id"], pathogen["taxon_label"],
                                attempted=True, ok=False, http_status=http_status,
                                latency_ms=latency_ms, error="'hits.total' missing from response")
        return ProbeResult("zenodo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=True, http_status=http_status,
                            latency_ms=latency_ms, raw_value=int(total))
    except (KeyError, ValueError, TypeError) as e:
        return ProbeResult("zenodo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status,
                            latency_ms=latency_ms, error=f"unexpected response: {e}")
