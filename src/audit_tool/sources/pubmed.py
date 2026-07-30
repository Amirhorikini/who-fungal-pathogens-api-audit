"""PubMed (E-utilities esearch) -- clinical/biomedical literature per organism.

Reuses the Entrez tag logic already validated in
../../../Versão_2/one_health_pipeline/bin/query_pubmed.py -- it does not replicate the
Fusarium/Mucorales MeSH override here (item 13 of the lessons catalog) nor the list
of reuse terms: the audit tests whether the source responds, it does not measure a reuse rate.
"""
from ..common import timed_get, or_group_tagged
from .base import ProbeResult

EUTILS_BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"


def probe(pathogen, years=15):
    import datetime
    end_year = datetime.datetime.now().year
    start_year = end_year - years

    term = or_group_tagged(pathogen["lit_synonyms"], "tiab")
    term += f" AND {start_year}:{end_year}[dp]"
    params = {"db": "pubmed", "term": term, "retmode": "json", "retmax": 0}

    resp, latency_ms, err = timed_get(EUTILS_BASE, params=params)

    if err is not None:
        return ProbeResult("pubmed", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, latency_ms=latency_ms, error=err)

    http_status = resp.status_code
    if http_status != 200:
        return ProbeResult("pubmed", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status, latency_ms=latency_ms)

    try:
        count = int(resp.json()["esearchresult"]["count"])
        return ProbeResult("pubmed", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=True, http_status=http_status,
                            latency_ms=latency_ms, raw_value=count)
    except (KeyError, ValueError, TypeError) as e:
        return ProbeResult("pubmed", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status,
                            latency_ms=latency_ms, error=f"unexpected response: {e}")
