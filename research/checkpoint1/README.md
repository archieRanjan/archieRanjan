# Checkpoint 1 — 5G/6G Research Discovery (Springer Nature format)

Deliverables for Checkpoint 1 (Stages A–F, preliminary) of the research-discovery mission.
**There are no experimental results at this checkpoint, by design.**

| Path | Content |
|---|---|
| `build/checkpoint1_report.pdf` | Typeset report (Springer Nature-style layout, numeric references) |
| `manuscript/sn-checkpoint1.tex` + `body.tex` + `references.bib` | Springer Nature `sn-jnl` LaTeX source (`sn-mathphys-num` style) |
| `manuscript/body.md`, `frontmatter.yaml` | Single source of the report text |
| `data/bibliography.json` | Structured bibliography (75 entries, each with a verification level and provenance) — **source of truth** |
| `data/literature_matrix.csv` | Literature matrix (problem, contribution, method, environment, findings, limitations, relevance, status) |
| `data/candidate_scores.csv`, `data/candidate_ranking.csv` | Stage C scores and weighted ranking |
| `decision_log.md` | Research decision log |
| `scripts/` | Reproducible generation of the bibliography, ranking, and report |

## Rebuild

```bash
pip install weasyprint matplotlib pyyaml
python3 -I scripts/build_bib.py && python3 -I scripts/score.py && python3 -I scripts/build_report.py
```

To compile the LaTeX, add `sn-jnl.cls` and `sn-mathphys-num.bst` from the official Springer Nature LaTeX template (for example on Overleaf), then:

```bash
pdflatex sn-checkpoint1 && bibtex sn-checkpoint1 && pdflatex sn-checkpoint1 && pdflatex sn-checkpoint1
```
