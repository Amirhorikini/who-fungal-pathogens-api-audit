"""SciELO -- via the OpenAlex publisher proxy.

*** WARNING: this proxy is known to underestimate 10-51x against native SciELO
(see ../../docs/03_licoes_aprendidas.md, item 17). The probe below measures
whether the proxy responds, not whether the number is reliable -- this source's
documentation/integration score in scoring.py already reflects this known
underestimation. Direct querying of native SciELO requires a browser (WAF with a
JS challenge) and is not automatable in this version of the tool -- it belongs to
the manual sample-verification layer, not the automated layer.
"""
from ..common import timed_get, CONTACT_EMAIL
from .base import ProbeResult
from .openalex import format_search

OPENALEX_URL = "https://api.openalex.org/works"
SCIELO_PUBLISHER_ID = "P4310312277"


def probe(pathogen, years=15, email=CONTACT_EMAIL):
    import datetime
    end_year = datetime.datetime.now().year
    start_year = end_year - years

    pathogen_clause = f"title_and_abstract.search:({format_search(pathogen['lit_synonyms'])})"
    date_filter = f"from_publication_date:{start_year}-01-01,to_publication_date:{end_year}-12-31"
    source_filter = f"primary_location.source.host_organization:{SCIELO_PUBLISHER_ID}"
    params = {"filter": f"{pathogen_clause},{date_filter},{source_filter}", "per_page": 1}
    headers = {"User-Agent": f"OneHealthAuditTool/1.0 (mailto:{email})"}

    resp, latency_ms, err = timed_get(OPENALEX_URL, params=params, headers=headers)

    if err is not None:
        return ProbeResult("scielo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, latency_ms=latency_ms, error=err,
                            note="OpenAlex proxy -- see the warning at the top of the module about known underestimation.")

    http_status = resp.status_code
    if http_status != 200:
        return ProbeResult("scielo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status, latency_ms=latency_ms,
                            note="OpenAlex proxy -- see the warning at the top of the module about known underestimation.")

    try:
        count = int(resp.json().get("meta", {}).get("count", 0))
        return ProbeResult("scielo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=True, http_status=http_status,
                            latency_ms=latency_ms, raw_value=count,
                            note="Value via OpenAlex proxy -- 10-51x underestimation confirmed against native SciELO (lessons, item 17). Do not use as an actual count without the manual verification layer.")
    except (KeyError, ValueError, TypeError) as e:
        return ProbeResult("scielo", pathogen["id"], pathogen["taxon_label"],
                            attempted=True, ok=False, http_status=http_status,
                            latency_ms=latency_ms, error=f"unexpected response: {e}")
