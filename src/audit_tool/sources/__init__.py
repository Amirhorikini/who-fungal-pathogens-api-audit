"""One module per data source, each exposing probe(pathogen) -> ProbeResult."""
from . import ncbi, pubmed, openalex, scielo, lilacs, ensembl, zenodo, ddbj, fungidb

REGISTRY = {
    "ncbi": ncbi,
    "pubmed": pubmed,
    "openalex": openalex,
    "scielo": scielo,
    "lilacs": lilacs,
    "ensembl": ensembl,
    "zenodo": zenodo,
    "ddbj": ddbj,
    "fungidb": fungidb,
}
