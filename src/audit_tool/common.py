"""Utilities shared by the audit tool.

This is not a copy of the common.py from the previous pipeline (../../Versão_2/one_health_pipeline/bin/) --
two deliberate differences:

1. Honest User-Agent by default, from the start. The previous project used a fake browser
   UA as the default and it got blocked by Zenodo's WAF (see
   ../docs/03_licoes_aprendidas.md, item 5) -- this tool never pretends to be a browser.
2. A single attempt per call, with no retry/backoff. The goal of the audit is to observe
   how the source behaves on a normal query -- masking a failure behind several
   retries would hide exactly the kind of instability this project wants to measure.
"""
import csv
import os
import sys
import time
import datetime

import requests

DEFAULT_TIMEOUT = 30
# Contact email sent in the User-Agent (e.g., for OpenAlex's "polite pool").
# Configurable via environment variable so a personal email isn't hardcoded in the
# public code -- see .env.example.
CONTACT_EMAIL = os.environ.get("AUDIT_CONTACT_EMAIL", "your-email@example.org")
DEFAULT_UA = f"OneHealthAuditTool/1.0 (mailto:{CONTACT_EMAIL})"


def log(msg):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}", file=sys.stderr, flush=True)


def load_pathogens(csv_path):
    pathogens = []
    with open(csv_path, mode="r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["lit_synonyms"] = [t.strip() for t in row["lit_synonyms"].split("|") if t.strip()]
            row["organism_terms"] = [t.strip() for t in row["organism_terms"].split("|") if t.strip()]
            pathogens.append(row)
    return pathogens


def or_group_tagged(terms, tag):
    """Applies the Entrez field tag to EACH term, not to the entire OR group --
    see ../docs/03_licoes_aprendidas.md, item 3, for why."""
    return " OR ".join([f'"{t}"[{tag}]' for t in terms])


def timed_get(url, params=None, headers=None, timeout=DEFAULT_TIMEOUT):
    """Single GET, no retry. Returns (response|None, latency_ms, error|None)."""
    if headers is None:
        headers = {"User-Agent": DEFAULT_UA}
    start = time.monotonic()
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=timeout)
        latency_ms = (time.monotonic() - start) * 1000
        return resp, latency_ms, None
    except requests.RequestException as e:
        latency_ms = (time.monotonic() - start) * 1000
        return None, latency_ms, str(e)
