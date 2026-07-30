"""NCBI Assembly (db=assembly) -- assembled genome availability per organism.

Reuses the endpoint and Entrez tag logic already validated in
../../../Versão_2/one_health_pipeline/bin/query_ncbi.py (esearch with
or_group_tagged, date filtering via the GRLS field, not mindate/maxdate -- see
../../docs/03_licoes_aprendidas.md, items 3 and 15).
"""
from ..common import timed_get, or_group_tagged
from .base import ProbeResult

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


def probe(pathogen, years=15):
    import datetime
    end_year = datetime.datetime.now().year
    start_year = end_year - years

    term = or_group_tagged(pathogen["organism_terms"], "Organism")
    term += f' AND ("{start_year}/01/01"[GRLS] : "{end_year}/12/31"[GRLS])'
    params = {"db": "assembly", "term": term, "retmode": "json", "retmax": 0}

    resp, latency_ms, err = timed_get(EUTILS_BASE, params=params)

    if err is not None:
        return ProbeResult("ncbi", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, latency_ms=latency_ms, error=err)

    http_status = resp.status_code
    if http_status != 200:
        return ProbeResult("ncbi", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status, latency_ms=latency_ms)

    try:
        count = int(resp.json()["esearchresult"]["count"])
        return ProbeResult("ncbi", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=True, http_status=http_status,
                            latency_ms=latency_ms, raw_value=count)
    except (KeyError, ValueError, TypeError) as e:
        return ProbeResult("ncbi", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status,
                            latency_ms=latency_ms, error=f"unexpected response: {e}")
