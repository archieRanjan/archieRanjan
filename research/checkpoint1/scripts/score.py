"""Weighted ranking of candidate problems (Stage C). Weights are fixed by the mission brief.
The score is a structured summary of judgement, NOT evidence of publishability."""
import csv, json, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
W = {"novelty": .25, "significance": .20, "feasibility": .20, "rigor": .15, "validation": .10, "fit": .10}
assert abs(sum(W.values()) - 1) < 1e-9
rows = list(csv.DictReader(open(ROOT / "data/candidate_scores.csv")))
for r in rows:
    r["weighted"] = round(sum(W[k] * float(r[k]) for k in W), 2)
rows.sort(key=lambda r: (r["hard_reject"] == "yes", -r["weighted"]))
with open(ROOT / "data/candidate_ranking.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
# LaTeX table body for the manuscript
lines = []
for i, r in enumerate(rows, 1):
    flag = "Rejected" if r["hard_reject"] == "yes" else ("Shortlist" if i <= 3 else "Retained")
    lines.append(f"{i} & {r['id']} & {r['novelty']} & {r['significance']} & {r['feasibility']} & {r['rigor']} & "
                 f"{r['validation']} & {r['fit']} & {r['weighted']:.2f} & {flag}\\\\")
(ROOT / "manuscript/ranking_rows.tex").write_text("\n".join(lines) + "\n")
print(json.dumps([(r["id"], r["weighted"], r["hard_reject"]) for r in rows]))
