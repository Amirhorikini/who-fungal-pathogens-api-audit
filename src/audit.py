#!/usr/bin/env python3
"""Data-infrastructure reliability audit tool --
integration / API / documentation, for the 9 sources covering the 19 WHO
fungal priority pathogens.

See ../docs/02_methodology.md and ../docs/04_product.md for the full design.

Usage:
    python audit.py --list-sources
    python audit.py --list-pathogens
    python audit.py --source ncbi --pathogen "Candida albicans"
    python audit.py --all
    python audit.py --all --output resultados/auditoria.csv --excel
"""
import argparse
import os
import sys

for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from audit_tool.common import load_pathogens, log
from audit_tool.sources import REGISTRY
from audit_tool.scoring import score_combination
from audit_tool import report

DEFAULT_PATHOGENS_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pathogens_19.csv")
DEFAULT_OUTPUT_CSV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "resultados", "auditoria.csv")


def find_pathogen(pathogens, name_or_id):
    name_or_id_lower = name_or_id.strip().lower()
    for p in pathogens:
        if p["id"] == name_or_id or p["taxon_label"].lower() == name_or_id_lower:
            return p
        if name_or_id_lower in [s.lower() for s in p["lit_synonyms"]]:
            return p
    return None


def run_one(source_name, pathogen):
    module = REGISTRY[source_name]
    probe_result = module.probe(pathogen)
    return score_combination(probe_result)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", default=DEFAULT_PATHOGENS_CSV, help="Pathogens CSV (default: pathogens_19.csv)")
    ap.add_argument("--source", choices=sorted(REGISTRY.keys()), help="Run only one source")
    ap.add_argument("--pathogen", help="Pathogen name (taxon_label or synonym) or id")
    ap.add_argument("--all", action="store_true", help="Run all 9 sources x all pathogens from --input")
    ap.add_argument("--output", default=DEFAULT_OUTPUT_CSV, help="Output CSV path")
    ap.add_argument("--excel", action="store_true", help="Also export .xlsx (requires openpyxl)")
    ap.add_argument("--list-sources", action="store_true")
    ap.add_argument("--list-pathogens", action="store_true")
    args = ap.parse_args()

    if args.list_sources:
        for name in sorted(REGISTRY.keys()):
            print(name)
        return

    pathogens = load_pathogens(args.input)

    if args.list_pathogens:
        for p in pathogens:
            print(f"{p['id']}\t{p['taxon_label']}")
        return

    if args.all:
        rows = []
        total = len(REGISTRY) * len(pathogens)
        done = 0
        for source_name in sorted(REGISTRY.keys()):
            for pathogen in pathogens:
                done += 1
                log(f"[{done}/{total}] {source_name} x {pathogen['taxon_label']}")
                rows.append(run_one(source_name, pathogen))

        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        report.write_csv(rows, args.output)
        if args.excel:
            excel_path = os.path.splitext(args.output)[0] + ".xlsx"
            report.write_excel(rows, excel_path)
        return

    if args.source and args.pathogen:
        pathogen = find_pathogen(pathogens, args.pathogen)
        if pathogen is None:
            log(f"Pathogen not found: '{args.pathogen}'. Use --list-pathogens to see valid names.")
            sys.exit(1)
        row = run_one(args.source, pathogen)
        for k, v in row.items():
            print(f"{k}: {v}")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
