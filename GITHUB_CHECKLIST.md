# Checklist before publishing to GitHub

## Current state

- Remote repository created: `https://github.com/Amirhorikini/who-fungal-pathogens-api-audit`
- Local `origin` remote configured to point to it.
- No commit has been made yet — creating a commit and running `git push` are externally
  visible actions and, by default security practice, require your explicit confirmation
  before they happen.
- **The manuscript is deliberately excluded from this public repository.** The
  `manuscrito/` folder (unpublished manuscript, including the internal peer-review
  report) is listed in `.gitignore` and is never staged. Only the audit code and its
  supporting evidence/documentation are published.

## What's already ready in the directory

- [x] `README.md` — project overview
- [x] `LICENSE` — MIT
- [x] `.gitignore` — excludes `resultados/` (generated data), `manuscrito/`
      (unpublished manuscript), and `secrets.config`/`.env`
- [x] `CITATION.cff` — citation file, repository URL filled in
- [x] `src/` — audit protocol code, tested
- [x] `src/requirements.txt` — dependencies
- [x] `docs/`, `verificacao_manual/` — documentation and evidence
- [x] Full manual verification (19/19 pathogens) for 8 of the 9 sources — CSVs in
      `verificacao_manual/*_19_patogenos.csv`
- [x] Everything above translated to English

## What's left to decide before publishing

1. **Confirm no real credential is in any staged file** — checked in this session
   (`AUDIT_CONTACT_EMAIL` uses a placeholder default, no hardcoded personal email
   or API key found); worth a final `git status` / `git diff --staged` check before
   the first commit.
2. **Decide whether `resultados/auditoria.csv` (generated data, currently gitignored)
   should also be published** — useful for reproducibility, but it is regenerable data;
   an alternative is to publish only the code and let the reader run
   `python audit.py --all` themselves.

## After publishing

- Consider archiving a version on Zenodo (generates a citable DOI, a common practice
  in JBS "tool papers" — see the 4 of 5 reviewed papers that link to GitHub in the
  availability section).
