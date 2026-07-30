"""Ensembl Fungi (REST /info/genomes/taxonomy) -- assembled genome availability.

Reuses the taxon-name cleanup and synonym-fallback logic already validated in
../../../Versão_2/one_health_pipeline/bin/query_ensembl.py --
including the fix for the "Eumycetoma causative agents" case (lessons, item 8).
Does not fabricate `coding_genes` -- this field does not exist on this endpoint
(lessons, item 4); the audit doesn't even try to read it.
"""
from ..common import timed_get
from .base import ProbeResult

ENSEMBL_REST_BASE = "https://rest.ensembl.org/info/genomes/taxonomy"


def clean_taxon_for_ensembl(label, organism_terms=None):
    if "(" in label:
        label = label.split("(")[0]
    label = label.replace("spp.", "").replace("causative agents", "").strip()
    if "Mucorales" in label:
        return "Mucorales"
    if "Eumycetoma" in label:
        if organism_terms:
            return organism_terms[0]
        return "Fungi"
    return label


def probe(pathogen, years=15):
    label = pathogen["taxon_label"]
    candidates = [clean_taxon_for_ensembl(label, pathogen.get("organism_terms"))]
    for term in pathogen.get("organism_terms", []):
        if term not in candidates:
            candidates.append(term)

    last_status = None
    last_latency = None
    any_fail = False

    for name in candidates:
        url = f"{ENSEMBL_REST_BASE}/{name}"
        headers = {"Content-Type": "application/json"}
        resp, latency_ms, err = timed_get(url, headers=headers)
        last_latency = latency_ms

        if err is not None:
            any_fail = True
            continue

        last_status = resp.status_code
        if resp.status_code != 200:
            any_fail = True
            continue

        try:
            data = resp.json()
        except ValueError:
            any_fail = True
            continue

        if isinstance(data, list) and len(data) > 0:
            return ProbeResult("ensembl", pathogen["id"], label,
                                attempted=True, ok=True, http_status=200,
                                latency_ms=latency_ms, raw_value=len(data),
                                note=f"Candidate used: '{name}'.")
        # 200 response with an empty list -- candidate had no result, try the next one

    if any_fail:
        return ProbeResult("ensembl", pathogen["id"], label,
                            attempted=True, ok=False, http_status=last_status,
                            latency_ms=last_latency,
                            error="network/parsing failure on at least one candidate -- see lessons, item 11")

    return ProbeResult("ensembl", pathogen["id"], label,
                        attempted=True, ok=True, http_status=200,
                        latency_ms=last_latency, raw_value=0,
                        note="All candidates responded 200 with an empty list -- actual zero, not a measurement failure.")
