"""Build the manuscript: IEEEtran LaTeX source (manuscript/main.tex) and a PDF preview (manuscript/manuscript.pdf).

Every number in the text is a placeholder {{path::to::value@fmt}} resolved from results/results.json;
tables are {{table:name}} (results/tables/name.md or manuscript/tables_static/name.md) and figures
{{figure:name|caption}}. The resolved Markdown is saved as manuscript/paper_filled.md for auditing.
No TeX engine is available in the build environment, so the PDF preview is typeset with WeasyPrint.
Usage: python3 -I code/build_paper.py
"""
import base64, io, json, pathlib, re, shutil, subprocess
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS, RES, FIG = ROOT / "manuscript", ROOT / "results", ROOT / "figs"
res = json.loads((RES / "results.json").read_text())
res_confirm = json.loads((ROOT / "results_confirm" / "results_confirm.json").read_text())
fm = yaml.safe_load((MS / "frontmatter.yaml").read_text())
TABLE_NO, FIG_NO = {}, {}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout




def lookup(path):
    cur = res
    if path[0] == "confirm":
        cur, path = res_confirm, path[1:]
    for p in path:
        cur = cur[int(p)] if isinstance(cur, list) else cur[p]
    return cur


def fmt_val(v, f):
    if f == "pct": return f"{100 * v:.1f}%"
    if f == "ms": return f"{1000 * v:.1f}"
    return format(v, f) if f else str(v)


def fill_numbers(text):
    def rep(m):
        spec, _, f = m.group(1).rpartition("@") if "@" in m.group(1) else (m.group(1), "", "")
        return fmt_val(lookup(spec.split("::")), f)
    return re.sub(r"\{\{(?!table:|figure:|algorithm)(.+?)\}\}", rep, text)


def read_table(name):
    for d in (RES / "tables", ROOT / "results_confirm" / "tables", MS / "tables_static"):
        if (d / f"{name}.md").exists():
            return (d / f"{name}.md").read_text()
    raise FileNotFoundError(name)


def md_table_to_latex(md, label):
    lines = [l for l in md.strip().splitlines() if l.strip()]
    cap = next((l[2:].strip() for l in lines if l.startswith(": ")), "")
    rows = [l for l in lines if l.startswith("|")]
    hdr = [c.strip() for c in rows[0].strip("|").split("|")]
    align = ["l" if c.strip().startswith(":") and not c.strip().endswith(":") else "r" for c in rows[1].strip("|").split("|")]
    body = [[c.strip() for c in r.strip("|").split("|")] for r in rows[2:]]
    def tex(s):
        s = re.sub(r"\[@([^\]]+)\]", lambda m: r"\cite{" + ",".join(k.strip().lstrip("@") for k in m.group(1).split(";")) + "}", s)
        for a, b in (("%", r"\%"), ("&", r"\&"), ("_", r"\_"), ("#", r"\#"), ("±", r"$\pm$"), ("≤", r"$\le$"), ("<", r"$<$"), ("~", r"\textasciitilde{}")):
            s = s.replace(a, b)
        s = s.replace(r"\cite{", "\\cite{").replace(r"\_", "_") if s.startswith(r"\cite") else s
        return s
    def tex_cell(s):
        parts = re.split(r"(\[@[^\]]+\])", s)
        out = ""
        for p in parts:
            if p.startswith("[@"):
                out += r"\cite{" + ",".join(k.strip().lstrip("@") for k in p[1:-1].split(";")) + "}"
            else:
                for a, b in (("\\", r"\textbackslash{}"), ("%", r"\%"), ("&", r"\&"), ("_", r"\_"), ("#", r"\#"), ("±", r"$\pm$"),
                             ("≤", r"$\le$"), ("<", r"$<$"), (">", r"$>$"), ("~", r"\textasciitilde{}"), ("–", "--")):
                    p = p.replace(a, b)
                out += p
        return out
    wide = len(hdr) > 4
    env = "table*" if wide else "table"
    colspec = "".join("p{%.2f\\linewidth}" % (0.9 / len(hdr)) if wide and any(len(r[i]) > 25 for r in body) else a for i, a in enumerate(align))
    out = [rf"\begin{{{env}}}[!t]", r"\centering", rf"\caption{{{tex_cell(cap)}}}", rf"\label{{{label}}}", r"\footnotesize",
           r"\resizebox{\linewidth}{!}{%" if wide else "", rf"\begin{{tabular}}{{{colspec}}}", r"\toprule",
           " & ".join(r"\textbf{" + tex_cell(h) + "}" for h in hdr) + r" \\", r"\midrule"]
    out += [" & ".join(tex_cell(c) for c in r) + r" \\" for r in body]
    out += [r"\bottomrule", r"\end{tabular}", "}" if wide else "", rf"\end{{{env}}}"]
    return "\n".join(x for x in out if x != "")


ALGO_TEX = r"""\begin{algorithm}[!t]
\caption{RC-SIR / RC-SIR-FS certification and selection}\label{alg:rcsir}
\begin{algorithmic}[1]
\REQUIRE calibration episodes $e_1,\dots,e_n$; policy set $\Lambda$; budgets $\alpha_s$; level $\delta$; variant
\FOR{$i=1$ \TO $n$} \STATE replay $e_i$ under every $\lambda\in\Lambda$ and $\pi_0$; record $L^c_s(e_i;\lambda)$, $L^a(e_i;\lambda)$ \ENDFOR
\IF{variant = Bonferroni}
  \STATE $p_\lambda\gets\max_s p^{\mathrm{HB}}(\hat R_s(\lambda);\alpha_s,n)$; \quad $\hat\Lambda\gets\{\lambda:p_\lambda\le\delta/|\Lambda|\}$
\ELSE
  \STATE split calibration set into halves $D_1,D_2$; order $\Lambda$ by $\max_s\hat R^{(D_1)}_s(\lambda)/\alpha_s$
  \STATE $\hat\Lambda\gets\emptyset$; \FOR{$\lambda$ in that order} \IF{$\max_s p^{\mathrm{HB}}(\hat R^{(D_2)}_s(\lambda);\alpha_s,|D_2|)\le\delta$} \STATE $\hat\Lambda\gets\hat\Lambda\cup\{\lambda\}$ \ELSE \STATE \textbf{break} \ENDIF \ENDFOR
\ENDIF
\STATE \textbf{return} $\arg\min_{\lambda\in\hat\Lambda}\hat R^a(\lambda)$ if $\hat\Lambda\neq\emptyset$, else $\pi_0$
\end{algorithmic}
\end{algorithm}"""

ALGO_MD = """<div class="algo"><b>Algorithm 1.</b> RC-SIR / RC-SIR-FS certification and selection<br/>
<b>Input:</b> calibration episodes e<sub>1..n</sub>; policy set Λ; budgets α<sub>s</sub>; level δ.<br/>
1. Replay every e<sub>i</sub> under all λ ∈ Λ and π<sub>0</sub>; record L<sup>c</sup><sub>s</sub>(e<sub>i</sub>;λ) and L<sup>a</sup>(e<sub>i</sub>;λ).<br/>
2. <i>Bonferroni:</i> p<sub>λ</sub> = max<sub>s</sub> p<sup>HB</sup>(R̂<sub>s</sub>(λ); α<sub>s</sub>, n); certify {λ : p<sub>λ</sub> ≤ δ/|Λ|}.<br/>
2'. <i>Fixed sequence:</i> split into halves D<sub>1</sub>, D<sub>2</sub>; order Λ by max<sub>s</sub> R̂<sub>s</sub><sup>(D1)</sup>(λ)/α<sub>s</sub>; test in order on D<sub>2</sub> at level δ, stop at the first non-rejection.<br/>
3. Return argmin<sub>λ∈Λ̂</sub> R̂<sup>a</sup>(λ), or π<sub>0</sub> if Λ̂ is empty.</div>"""


def expand(text, mode):
    def tab(m):
        name = m.group(1)
        md = fill_numbers(read_table(name))
        if mode == "latex":
            return "\n```{=latex}\n" + md_table_to_latex(md, "tab:" + name) + "\n```\n"
        cap = next((l[2:].strip() for l in md.splitlines() if l.startswith(": ")), "")
        body = "\n".join(l for l in md.splitlines() if not l.startswith(": "))
        html_tab = run(["pandoc", "--from", "markdown", "--to", "html5", "--citeproc", "--bibliography", str(MS / "references.bib"),
                        "--csl", str(MS / "ieee-numeric.csl"), "--metadata", "suppress-bibliography=true"], input=body)
        return (f'\n```{{=html}}\n<div class="span" id="tab:{name}"><div class="tbl-num">Table {TABLE_NO[name]}<br/>{cap}</div>'
                + html_tab + "</div>\n```\n")
    def figr(m):
        name, cap = m.group(1), m.group(2)
        if mode == "latex":
            env, width = ("figure", "\\columnwidth") if name in ("fig_forest", "fig_hetero") else ("figure*", "0.95\\textwidth")
            return ("\n```{=latex}\n\\begin{" + env + "}[!t]\\centering\\includegraphics[width=" + width + "]{figures/" + name +
                    ".pdf}\\caption{" + cap + "}\\label{fig:" + name.replace("fig_", "") + "}\\end{" + env + "}\n```\n")
        return (f'\n::: {{.span .figbox #fig:{name}}}\n![]({(FIG / (name + ".png")).as_posix()}){{width=96%}}\n\n'
                f'[**Fig. {FIG_NO[name]}.** {cap}]{{.figcap}}\n:::\n')
    text = re.sub(r"\{\{table:([A-Za-z_]+)\}\}", tab, text)
    text = re.sub(r"\{\{figure:([a-z_]+)\|(.+?)\}\}", figr, text)
    text = text.replace("{{algorithm}}", "\n```{=latex}\n" + ALGO_TEX + "\n```\n" if mode == "latex" else "\n" + ALGO_MD + "\n")
    text = fill_numbers(text)
    assert "{{" not in text, re.findall(r"\{\{.*?\}\}", text)[:3]
    return text


src = (MS / "paper.md").read_text()
for i, n in enumerate(dict.fromkeys(re.findall(r"\{\{table:([A-Za-z_]+)\}\}", src)), 1):
    TABLE_NO[n] = i
for i, n in enumerate(dict.fromkeys(re.findall(r"\{\{figure:([a-z_]+)\|", src)), 1):
    FIG_NO[n] = i


def number_refs(text, mode):
    """Cross-references are written as Table [?](#tab:name) / Fig. [?](#fig:name) and numbered automatically."""
    if mode == "latex":
        text = re.sub(r"Table \[[^\]]*\]\(#tab:(\w+)\)", r"Table~\\ref{tab:\1}", text)
        return re.sub(r"Fig\. \[[^\]]*\]\(#fig:(\w+)\)", r"Fig.~\\ref{fig:\1}", text)
    text = re.sub(r"Table \[[^\]]*\]\(#tab:(\w+)\)", lambda m: f"Table {TABLE_NO[m.group(1)]}", text)
    return re.sub(r"Fig\. \[[^\]]*\]\(#fig:(\w+)\)", lambda m: f"Fig. {FIG_NO['fig_' + m.group(1)]}", text)

# map the hand-written cross-reference numbers to labels in LaTeX
REFMAP = {"tab:cmp": "tab:comparison", "tab:main": "tab:main", "tab:paired": "tab:paired", "tab:harm": "tab:harm_ratio"}
filled_md = number_refs(expand(src, "html"), "html"); (MS / "paper_filled.md").write_text(filled_md)
abstract = fill_numbers(fm["abstract"])


# ---------------------------------------------------------------- IEEEtran LaTeX
latex_md = number_refs(expand(src, "latex"), "latex")
latex_md = re.sub(r"Section \[\d+\]\(#(sec:\w+)\)", r"Section~\\ref{\1}", latex_md)
latex_md = re.sub(r"Appendix \[[^\]]*\]\(#(app:\w+)\)", r"Appendix~\\ref{\1}", latex_md)
tex = run(["pandoc", "--from", "markdown", "--to", "latex", "--natbib", "--top-level-division=section"], input=latex_md)
tex = tex.replace(r"\citep{", r"\cite{").replace(r"\citet{", r"\cite{")
tex = re.sub(r"\\label\{(sec:\w+)\}", r"\\label{\1}", tex)
for a, b in {"≤": r"$\le$", "≥": r"$\ge$", "±": r"$\pm$", "–": "--", "—": "---", "×": r"$\times$", "∎": r"$\square$", "−": "-"}.items():
    tex = tex.replace(a, b)
import re as _re
_i = tex.find("\\section*{Appendix A")
if _i >= 0:
    tex = tex[:_i] + "\\appendices\n" + tex[_i:]
    tex = _re.sub(r"\\section\*\{Appendix [AB]: ([^}]*)\}", r"\\section{\1}", tex)
(MS / "body.tex").write_text(tex)
figdir = MS / "figures"; figdir.mkdir(exist_ok=True)
for f in FIG.glob("*.pdf"):
    shutil.copy(f, figdir / f.name)
abs_tex = run(["pandoc", "--from", "markdown", "--to", "latex"], input=abstract).strip()
main = rf"""%% IEEE Transactions journal manuscript (IEEEtran, journal mode).
%% Compile with the official IEEEtran class and IEEEtran.bst (TeX Live or Overleaf):
%%   pdflatex main && bibtex main && pdflatex main && pdflatex main
\documentclass[journal]{{IEEEtran}}
\usepackage{{amsmath,amssymb,amsfonts,graphicx,booktabs,algorithmic,algorithm,cite,url,array,xcolor}}
\usepackage[hidelinks]{{hyperref}}
\providecommand{{\tightlist}}{{\setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\newtheorem{{lemma}}{{Lemma}}\newtheorem{{proposition}}{{Proposition}}
\begin{{document}}
\title{{{fm['title']}}}
\author{{[Author names and affiliations to be supplied]}}
\markboth{{IEEE Transactions on Network and Service Management (submitted)}}{{{fm['short_title']}}}
\maketitle
\begin{{abstract}}
{abs_tex}
\end{{abstract}}
\begin{{IEEEkeywords}}
{fm['keywords']}
\end{{IEEEkeywords}}
\input{{body}}
\section*{{Acknowledgment}}
{fm['ack']}
\section*{{Code and Data Availability}}
{run(["pandoc", "--from", "markdown", "--to", "latex"], input=fm['declarations']).strip()}
\bibliographystyle{{IEEEtran}}
\bibliography{{references}}
\end{{document}}
"""
(MS / "main.tex").write_text(main)

# ---------------------------------------------------------------- PDF preview (WeasyPrint)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["mathtext.fontset"] = "stix"


def math_svg(t, display):
    for a, b in [(r"\qquad", r"\quad\quad"), (r"\;", r"\ "), (r"\Pr", r"\mathrm{Pr}"), (r"\arg\min", r"\mathrm{arg\,min}"),
                 (r"\dots", r"\ldots"), (r"\ast", "*")]:
        t = t.replace(a, b)
    t = re.sub(r"\\[Bb]ig[lr]?(?![a-zA-Z])", "", t)
    t = re.sub(r"\\(le|ge)(?![a-zA-Z])", r"\\\1q", t)
    t = re.sub(r"\\text\{([^}]*)\}", lambda m: r"\mathrm{" + m.group(1).replace(" ", r"\ ") + "}", t)
    fig = plt.figure(figsize=(0.01, 0.01)); fig.text(0, 0, f"${t}$", fontsize=10.5 if display else 9.6)
    buf = io.BytesIO(); fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.02, transparent=True); plt.close(fig)
    return buf.getvalue()


def walk(x):
    if isinstance(x, dict):
        if x.get("t") == "Math":
            disp = x["c"][0]["t"] == "DisplayMath"
            uri = "data:image/svg+xml;base64," + base64.b64encode(math_svg(x["c"][1], disp)).decode()
            return {"t": "RawInline", "c": ["html", f'<img class="math {"display" if disp else "inline"}" src="{uri}"/>']}
        return {k: walk(v) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v) for v in x]
    return x


def to_html(md, extra=()):
    ast = walk(json.loads(run(["pandoc", "--from", "markdown", "--to", "json"], input=md)))
    return run(["pandoc", "--from", "json", "--to", "html5", *extra], input=json.dumps(ast))


csl = MS / "ieee-numeric.csl"
html_body = to_html(filled_md, ["--citeproc", "--bibliography", str(MS / "references.bib"), "--csl", str(csl),
                                "--number-sections", "--metadata", "reference-section-title=References",
                                "--metadata", "link-citations=true"])
tpl = (MS / "html-template.html").read_text()
html = (tpl.replace("$TITLE$", fm["title"]).replace("$AUTHORS$", fm["authors"]).replace("$DATE$", fm["date"])
        .replace("$JOURNAL$", fm["journal"]).replace("$ABSTRACT$", to_html(abstract).replace("<p>", "").replace("</p>", ""))
        .replace("$KEYWORDS$", fm["keywords"]).replace("$ACK$", fm["ack"])
        .replace("$DECL$", to_html(fm["declarations"]).replace("<p>", "").replace("</p>", "")).replace("$BODY$", html_body))
(MS / "manuscript_preview.html").write_text(html)
from weasyprint import HTML
HTML(string=html, base_url=str(MS)).write_pdf(MS / "manuscript.pdf")
print("built", MS / "main.tex", MS / "manuscript.pdf")
