"""Generate references.bib and literature_matrix.csv from data/bibliography.json.

Usage: python3 -I scripts/build_bib.py   (run from research/checkpoint1)
"""
import csv, json, collections, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
data = json.loads((ROOT / "data/bibliography.json").read_text())
entries = data["entries"]

keys = [e["key"] for e in entries]
dup = [k for k, c in collections.Counter(keys).items() if c > 1]
assert not dup, f"duplicate keys: {dup}"

VENUE_FIELD = {"article": "journal", "inproceedings": "booktitle", "misc": "howpublished"}

def bib(e):
    authors = e["authors"]
    if authors.startswith("("):  # unknown authors: keep as a literal, never parse as a name
        authors = "{[Authors not retrieved]}"
    f = {"author": authors, "title": "{" + e["title"] + "}",
         VENUE_FIELD[e["type"]]: e["venue"], "year": str(e["year"])}
    for k in ("volume", "number", "pages"):
        if e.get(k):
            f[k] = e[k]
    if e.get("doi"):
        f["doi"] = e["doi"]
    if e.get("arxiv"):
        f["eprint"] = e["arxiv"]; f["archivePrefix"] = "arXiv"
    if e.get("url"):
        f["url"] = e["url"]
    f["note"] = f"Verification: {e['status']}" + (f". {e['notes']}" if e.get("notes") else "")
    body = ",\n".join(f"  {k} = {{{v}}}" for k, v in f.items())
    return f"@{e['type']}{{{e['key']},\n{body}\n}}\n"

(ROOT / "manuscript/references.bib").write_text(
    "% Auto-generated from data/bibliography.json -- do not edit by hand.\n\n" + "\n".join(bib(e) for e in entries))

cols = ["id", "key", "authors", "title", "venue", "year", "doi", "arxiv", "url", "area", "problem",
        "contribution", "method", "env", "findings", "limitations", "relevance", "status", "notes"]
with open(ROOT / "data/literature_matrix.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols)
    w.writeheader()
    for i, e in enumerate(entries, 1):
        w.writerow({"id": i, **{c: e.get(c, "") for c in cols[1:]}})

status = collections.Counter(e["status"] for e in entries)
areas = collections.Counter(e["area"].split(" / ")[0] for e in entries)
recent = sum(1 for e in entries if e["year"] >= 2023)
surveys = sum(1 for e in entries if e["method"] == "Survey.")
artefacts = sum(1 for e in entries if e["venue"] == "GitHub repository")
summary = {"total": len(entries), "status": dict(status), "year_ge_2023": recent,
           "surveys": surveys, "software_artefacts": artefacts,
           "peer_reviewed_or_preprint_papers": len(entries) - artefacts,
           "usable_for_count_(excl_UNVERIFIED_and_artefacts)": len(entries) - artefacts - status.get("UNVERIFIED", 0),
           "areas": dict(areas)}
(ROOT / "data/bibliography_summary.json").write_text(json.dumps(summary, indent=2))
print(json.dumps(summary, indent=2))
