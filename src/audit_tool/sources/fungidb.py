"""FungiDB -- no confirmed count endpoint.

Same situation as the previous query_fungidb.py (explicit stub -- see
../../docs/03_lessons_learned.md, category D): the actual search depends on
predefined "questions" via POST with a specific JSON body, not confirmed.
`attempted=False`, not a "0" or a network failure.
"""
from .base import ProbeResult


def probe(pathogen, years=15):
    return ProbeResult(
        "fungidb", pathogen["id"], pathogen["taxon_label"],
        attempted=False, ok=False,
        note="Requires predefined 'questions' via POST that are not confirmed -- not automatically testable in this version of the tool.",
    )
