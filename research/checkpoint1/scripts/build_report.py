"""Build the Checkpoint 1 report in two forms from manuscript/body.md:

1. manuscript/sn-checkpoint1.tex -- Springer Nature `sn-jnl` LaTeX source (compile on Overleaf or a
   TeX Live install that has the Springer Nature LaTeX template: sn-jnl.cls + sn-mathphys-num.bst).
2. build/checkpoint1_report.pdf  -- typeset preview in Springer-Nature-like layout (pandoc + citeproc +
   WeasyPrint; display math rendered to SVG with matplotlib mathtext), for sessions without LaTeX.

Usage (from research/checkpoint1):  python3 -I scripts/build_report.py
"""
import base64, hashlib, io, json, pathlib, re, subprocess

import yaml  # PyYAML (installed alongside matplotlib/weasyprint)

ROOT = pathlib.Path(__file__).resolve().parent.parent
MS, BUILD = ROOT / "manuscript", ROOT / "build"
BUILD.mkdir(exist_ok=True)
fm = yaml.safe_load((MS / "frontmatter.yaml").read_text())


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw).stdout


# ---------------------------------------------------------------- 1. Springer Nature LaTeX
body_tex = run(["pandoc", str(MS / "body.md"), "--from", "markdown", "--to", "latex", "--natbib",
                "--top-level-division=section"])
for a, b in {"✓": r"\ding{51}", "✗": r"\ding{55}", "→": r"$\rightarrow$", "×": r"$\times$"}.items():
    body_tex = body_tex.replace(a, b)
# pandoc emits \citep{a,b}; sn-mathphys-num gives numeric [1,2] for both \cite and \citep.
(MS / "body.tex").write_text(body_tex)

DECLARATIONS = r"""
\bmhead{Acknowledgements}
Literature screening, structuring and drafting were carried out with the assistance of an AI research
assistant (Claude Code). All bibliographic records carry an explicit verification status; no reference,
DOI or result was generated without a retrieved source.

\section*{Declarations}
\begin{itemize}
\item \textbf{Funding:} Not applicable / to be completed by the authors.
\item \textbf{Competing interests:} The authors declare no competing interests (to be confirmed).
\item \textbf{Ethics approval and consent to participate:} Not applicable (no human or animal data).
\item \textbf{Data availability:} The structured bibliography, literature matrix and scoring data are in
  \texttt{research/checkpoint1/data/}. No experimental data were generated at this checkpoint.
\item \textbf{Code availability:} \texttt{research/checkpoint1/scripts/} (bibliography generation, ranking,
  report build).
\item \textbf{Author contribution:} To be completed by the authors.
\end{itemize}
"""

main_tex = rf"""%% Springer Nature journal template (sn-jnl), numeric math/physics reference style.
%% Requires sn-jnl.cls and sn-mathphys-num.bst from the official Springer Nature LaTeX template
%% (https://www.springernature.com/gp/authors/campaigns/latex-author-support). Compile:
%%   pdflatex sn-checkpoint1 && bibtex sn-checkpoint1 && pdflatex sn-checkpoint1 && pdflatex sn-checkpoint1
\documentclass[pdflatex,sn-mathphys-num]{{sn-jnl}}
\usepackage{{graphicx,multirow,amsmath,amssymb,amsfonts,amsthm,mathrsfs,xcolor,textcomp,manyfoot,booktabs}}
\usepackage{{longtable,array,calc,pifont}}
\usepackage[title]{{appendix}}
\providecommand{{\tightlist}}{{\setlength{{\itemsep}}{{0pt}}\setlength{{\parskip}}{{0pt}}}}
\raggedbottom

\begin{{document}}

\title[{fm['short_title']}]{{{fm['title']}}}

\author*[1]{{\fnm{{[Author]}} \sur{{[To be supplied]}}}}\email{{[to be supplied]}}
\affil*[1]{{\orgname{{[Affiliation to be supplied]}}}}

\abstract{{{fm['abstract']}}}

\keywords{{{fm['keywords']}}}

\maketitle

\input{{body}}
{DECLARATIONS}
\bibliography{{references}}

\end{{document}}
"""
(MS / "sn-checkpoint1.tex").write_text(main_tex)

# ---------------------------------------------------------------- 2. PDF preview (HTML -> WeasyPrint)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.family"] = "STIXGeneral"

MATHTEXT_FIX = [(r"\qquad", r"\quad\quad"), (r"\;", r"\ "), (r"\Pr", r"\mathrm{Pr}"),
                (r"\arg\min", r"\mathrm{arg\,min}"), (r"\max_s", r"\max_{s}"),
                (r"\le ", r"\leq "), (r"\ge ", r"\geq ")]


def math_svg(tex, display):
    t = tex
    for a, b in MATHTEXT_FIX:
        t = t.replace(a, b)
    t = re.sub(r"\\(le|ge)(?![a-zA-Z])", r"\\\1q", t)
    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(0, 0, f"${t}$", fontsize=11 if display else 10.5)
    buf = io.BytesIO()
    fig.savefig(buf, format="svg", bbox_inches="tight", pad_inches=0.02, transparent=True)
    plt.close(fig)
    return buf.getvalue()


def walk(x):
    if isinstance(x, dict):
        if x.get("t") == "Math":
            kind, tex = x["c"][0]["t"], x["c"][1]
            disp = kind == "DisplayMath"
            svg = math_svg(tex, disp)
            name = hashlib.sha1(svg).hexdigest()[:12] + ".svg"
            (BUILD / "math").mkdir(exist_ok=True)
            (BUILD / "math" / name).write_bytes(svg)
            uri = "data:image/svg+xml;base64," + base64.b64encode(svg).decode()
            cls = "math display" if disp else "math inline"
            return {"t": "RawInline", "c": ["html", f'<img class="{cls}" alt="{tex.replace(chr(34), "")}" src="{uri}"/>']}
        return {k: walk(v) for k, v in x.items()}
    if isinstance(x, list):
        return [walk(v) for v in x]
    return x


ast = json.loads(run(["pandoc", str(MS / "body.md"), "--from", "markdown", "--to", "json"]))
ast = walk(ast)
tpl = (MS / "html-template.html").read_text()
html_body = run(["pandoc", "--from", "json", "--to", "html5", "--citeproc",
                 "--bibliography", str(MS / "references.bib"), "--csl", str(MS / "numeric.csl"),
                 "--number-sections", "--metadata", "reference-section-title=References",
                 "--metadata", "link-citations=true"], input=json.dumps(ast))
html = (tpl.replace("$TITLE$", fm["title"]).replace("$AUTHORS$", fm["authors"])
        .replace("$DATE$", fm["date"]).replace("$ABSTRACT$", fm["abstract"])
        .replace("$KEYWORDS$", fm["keywords"]).replace("$BODY$", html_body))
(BUILD / "checkpoint1_report.html").write_text(html)

from weasyprint import HTML
HTML(string=html, base_url=str(BUILD)).write_pdf(BUILD / "checkpoint1_report.pdf")
print("built:", MS / "sn-checkpoint1.tex", BUILD / "checkpoint1_report.pdf")
