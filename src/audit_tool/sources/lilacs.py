"""LILACS/BVS -- no confirmed programmatic endpoint.

pesquisa.bvsalud.org blocks direct HTTP requests (WAF with a JS challenge,
confirmed in the previous project -- see ../../docs/03_lessons_learned.md, item 18).
There is also no publisher/source in OpenAlex that identifies LILACS content.
`attempted=False`: this source currently has no programmatic path to test
automatically -- this is not a network failure, it is a confirmed absence of an API.
"""
from .base import ProbeResult


def probe(pathogen, years=15):
    return ProbeResult(
        "lilacs", pathogen["id"], pathogen["taxon_label"],
        attempted=False, ok=False,
        note="No confirmed programmatic endpoint -- actual access only via browser (WAF blocks direct requests). See lessons, item 18.",
    )
