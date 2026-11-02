# Reproducing every number in the manuscript

Run all commands from `research/paper/`.

```bash
pip install -r requirements.txt
```

```bash
python3 -m pytest -q tests
```

```bash
python3 -I code/generate.py
```

```bash
python3 -I code/check_determinism.py
```

```bash
python3 -I code/experiments.py
```

```bash
python3 -I code/build_paper.py
```

What each step does:

| Step | Purpose | Runtime / output |
|---|---|---|
| `pytest` | 12 unit and integration tests | ≈2 s |
| `generate.py` | Detector training + 7.06 M policy–episode replays | ≈15 min on 4 vCPU; writes `data/` |
| `check_determinism.py` | Seeds → identical loss tables | ≈1 min |
| `experiments.py` | All experiments | ≈1 min; writes `results/results.json`, `results/tables/`, `figs/` |
| `build_paper.py` | Manuscript build | Writes `manuscript/main.tex`, `body.tex`, `manuscript.pdf`, `paper_filled.md` |

**Traceability:** every number in `manuscript/paper.md` is a placeholder `{{path::to::key@format}}` resolved from `results/results.json`. `paper_filled.md` shows the resolved text. Search `paper.md` for a number's placeholder to find its source key.

**Compiling the IEEE PDF:** this environment has no TeX. On a TeX installation with IEEEtran, run:

```bash
cd manuscript && pdflatex main && bibtex main && pdflatex main && pdflatex main
```

**Verified here:**
- A second run of `experiments.py` reproduces `results.json` exactly, except wall-clock timing.
- `check_determinism.py` reports a maximum difference of 0.
