"""Publication figures: methodology diagrams and data figures.

Data figures read only committed result files: data/, data_confirm/, results/results.json and
results_confirm/results_confirm.json. Values recomputed here are asserted against the stored
results. Each figure is written as a vector PDF (LaTeX) and a 300-dpi PNG (preview) to ../figs/.
Usage: python3 -I code/figures.py
"""
import json, pathlib, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from sklearn.metrics import roc_curve, roc_auc_score

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import methods as M

ROOT = pathlib.Path(__file__).resolve().parent.parent
FIG = ROOT / "figs"; FIG.mkdir(exist_ok=True)
RES = json.loads((ROOT / "results/results.json").read_text())
RC = json.loads((ROOT / "results_confirm/results_confirm.json").read_text())
TAUS = (0.9, 0.95, 0.99, 0.995, 0.999)
ALPHA = np.array([0.05, 0.02, 0.05])
SL = ("eMBB", "URLLC", "mMTC")

# validated categorical palette (reference instance), fixed order; text never in series colour
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = ("#2a78d6", "#eb6834", "#1baf7a", "#eda100",
                                                          "#e87ba4", "#008300", "#6250d6", "#e34948")
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e4e3df", "#fcfcfb"
plt.rcParams.update({
    "font.family": "serif", "font.serif": ["STIXGeneral", "DejaVu Serif"], "mathtext.fontset": "stix",
    "font.size": 8, "axes.titlesize": 8.5, "axes.labelsize": 8, "xtick.labelsize": 7, "ytick.labelsize": 7,
    "legend.fontsize": 7, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2, "ytick.color": INK2,
    "axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6,
    "axes.axisbelow": True, "lines.linewidth": 1.6, "savefig.bbox": "tight", "savefig.pad_inches": 0.02,
    "legend.frameon": False, "pdf.fonttype": 42})


def save(fig, name):
    fig.savefig(FIG / f"{name}.pdf"); fig.savefig(FIG / f"{name}.png", dpi=300); plt.close(fig)
    print("wrote", name)


# ============================================================ methodology diagrams
def box(ax, x, y, w, h, text, fc="#ffffff", ec=MUTED, fs=7, bold=False, color=INK):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.006,rounding_size=0.012", fc=fc, ec=ec, lw=0.9, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=color, zorder=3,
            fontweight="bold" if bold else "normal", linespacing=1.25)


def arrow(ax, p, q, color=INK2, style="-|>", lw=0.9, ls="-", rad=0.0):
    ax.add_patch(FancyArrowPatch(p, q, arrowstyle=style, mutation_scale=8, color=color, lw=lw, ls=ls,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=1, shrinkB=1, zorder=4))


def fig_system():
    fig, ax = plt.subplots(figsize=(7.16, 3.1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    cols = (BLUE, ORANGE, AQUA)
    # UE groups
    box(ax, 0.006, 0.10, 0.134, 0.82, "", fc="#ffffff", ec=GRID)
    for s, (y, c) in enumerate(zip((0.70, 0.45, 0.20), cols)):
        ax.text(0.07, y + 0.15, SL[s] + " UEs", fontsize=7, color=INK2, ha="center", zorder=4)
        for k in range(4):
            mal = (s == 0 and k == 2) or (s == 2 and k == 1)
            ax.add_patch(Rectangle((0.012 + k * 0.03, y + 0.03), 0.022, 0.09, fc=c if not mal else "#ffffff",
                                   ec=c, lw=1.2, hatch="////" if mal else None, zorder=4))
    ax.text(0.07, 0.04, "hatched = attacker", fontsize=6, color=MUTED, ha="center")
    # detector and policy (top lane)
    box(ax, 0.19, 0.64, 0.15, 0.26, "Detector\n(Isolation Forest):\nscore $z_u$ from the\nobservation window $T_o$", fc="#f4f7fc", ec=BLUE, fs=6.6)
    box(ax, 0.39, 0.64, 0.15, 0.26, "Certified policy $\\hat\\lambda$\n$(\\tau_s,a_s)$ per slice:\nthreshold + action", fc="#f4f7fc", ec=BLUE, fs=6.6)
    arrow(ax, (0.14, 0.77), (0.19, 0.77))
    arrow(ax, (0.34, 0.77), (0.39, 0.77))
    # enforcement (bottom lane)
    box(ax, 0.39, 0.10, 0.15, 0.42, "UPF enforcement\n(per UE)\n\nRL: $\\min(D_u,\\mathrm{cap}_s)$\nB: drop\nR: redirect (Study N)", fc="#ffffff", ec=INK2, fs=6.6)
    arrow(ax, (0.465, 0.64), (0.465, 0.52)); ax.text(0.47, 0.575, "actions", fontsize=5.8, color=INK2)
    arrow(ax, (0.14, 0.31), (0.39, 0.31)); ax.text(0.265, 0.335, "user-plane traffic", fontsize=5.8, color=INK2, ha="center")
    # scheduler
    box(ax, 0.59, 0.10, 0.18, 0.80, "", fc="#fafaf8", ec=INK2)
    ax.text(0.68, 0.845, "Egress scheduler", ha="center", fontsize=6.8, color=INK, zorder=4)
    ax.text(0.68, 0.755, "capacity $C$\n$x_s=\\min(a_s,g_sC+w_s\\theta)$", ha="center", fontsize=6.0, color=INK2, zorder=4)
    for s, (y, c) in enumerate(zip((0.56, 0.38, 0.20), cols)):
        ax.add_patch(Rectangle((0.605, y), 0.10, 0.11, fc="#ffffff", ec=c, lw=1.2, zorder=4))
        for k in range(4):
            ax.add_patch(Rectangle((0.61 + k * 0.0235, y + 0.015), 0.019, 0.08, fc=c, ec="none", alpha=0.25 + 0.15 * k, zorder=5))
        ax.text(0.712, y + 0.055, f"{SL[s]}\n$g_s,B_s$", fontsize=6.0, va="center", color=INK2, zorder=4)
    arrow(ax, (0.54, 0.31), (0.59, 0.31))
    # outcomes and scrubbing
    box(ax, 0.82, 0.62, 0.172, 0.28, "Per-UE SLA outcome $V_u$\ncollateral $L^c_s$ vs. $\\pi_0$\nattack delivered $L^a$", fc="#f1faf6", ec=AQUA, fs=6.4)
    arrow(ax, (0.77, 0.76), (0.82, 0.76))
    box(ax, 0.82, 0.10, 0.172, 0.30, "Scrubbing service\n(borrow-only class)\nremoves attack traffic;\nbenign returns at $t{+}1$", fc="#fdf3ef", ec=ORANGE, fs=6.2)
    arrow(ax, (0.77, 0.16), (0.82, 0.16), color=ORANGE, ls="--")
    arrow(ax, (0.82, 0.34), (0.757, 0.62), color=ORANGE, ls="--", rad=-0.25)
    ax.text(0.905, 0.47, "hairpin: redirected benign\ntraffic crosses the link twice", fontsize=5.8, color=INK2, ha="center")
    save(fig, "fig_system")


def fig_workflow():
    fig, ax = plt.subplots(figsize=(7.16, 2.5)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    steps = [("Calibration\nepisodes\n$e_1,\\dots,e_n$", "#ffffff", MUTED),
             ("Counterfactual\nreplay under all\n$\\lambda\\in\\Lambda$ and $\\pi_0$", "#f4f7fc", BLUE),
             ("Loss tables\n$L^c_s(e_i;\\lambda)$\n$L^a(e_i;\\lambda)$", "#ffffff", MUTED),
             ("Split $D_1|D_2$;\norder $\\Lambda$ on $D_1$\nby $\\max_s\\hat R_s/\\alpha_s$", "#f4f7fc", BLUE),
             ("Test in order on $D_2$:\n$\\max_s p^{HB}_s\\leq\\delta$;\nstop at first failure", "#f4f7fc", BLUE),
             ("Deploy the certified\npolicy with least $\\hat R^a$\n(else $\\pi_0$)", "#f1faf6", AQUA)]
    w, gap = 0.145, 0.018; x0 = 0.006
    for i, (tx, fc, ec) in enumerate(steps):
        x = x0 + i * (w + gap)
        box(ax, x, 0.50, w, 0.42, tx, fc=fc, ec=ec, fs=6.5)
        ax.text(x + 0.012, 0.885, str(i + 1), fontsize=6, color=MUTED)
        if i:
            arrow(ax, (x - gap, 0.71), (x, 0.71))
    box(ax, x0 + w + gap, 0.04, 2 * w + gap, 0.32,
        "Slice-FPR baseline (Corollary 1)\nbenign scores only, no replay;\ntest $\\Phi_s(\\tau)\\leq\\alpha_s$ per slice at $\\delta/3$",
        fc="#fdf3ef", ec=ORANGE, fs=6.4)
    arrow(ax, (x0 + w / 2, 0.50), (x0 + w + gap, 0.20), color=ORANGE, ls="--", rad=0.25)
    box(ax, x0 + 4 * (w + gap), 0.04, 2 * w + gap, 0.32,
        "Guarantee (Proposition 1)\n$\\Pr\\{\\forall s: R^c_s(\\hat\\lambda)\\leq\\alpha_s\\}\\geq 1-\\delta$\nno monotonicity assumption",
        fc="#ffffff", ec=INK2, fs=6.4)
    save(fig, "fig_workflow")


def fig_study_design():
    fig, ax = plt.subplots(figsize=(7.16, 2.1)); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    box(ax, 0.006, 0.56, 0.245, 0.36, "Exploratory study (v1)\n1 pool, 1500 episodes\n200 splits; sweeps", fc="#ffffff", ec=MUTED, fs=6.6)
    box(ax, 0.006, 0.06, 0.245, 0.36, "Disclosed deviations (App. B)\nsimulator v1 replaced;\nobjective corrected; FS post hoc", fc="#fafaf8", ec=GRID, fs=6.2, color=INK2)
    ax.plot([0.315, 0.315], [0.06, 0.92], color=RED, lw=1.4, ls=(0, (3, 2)), zorder=0)
    box(ax, 0.268, 0.40, 0.094, 0.18, "plan\ncommitted\n(d5518c3)", fc="#ffffff", ec=RED, fs=5.8)
    box(ax, 0.38, 0.56, 0.29, 0.36, "Study C: 8 independent replications\nnew seeds, random scenarios,\nfresh detectors; 50 splits each", fc="#f4f7fc", ec=BLUE, fs=6.5)
    box(ax, 0.38, 0.06, 0.29, 0.36, "Primary: FS $-$ Slice-FPR $<0$\n(95% upper bound $<0$ and\n$\\geq 7/8$ replications)", fc="#ffffff", ec=BLUE, fs=6.4)
    box(ax, 0.70, 0.56, 0.293, 0.36, "Study N: relocating actions\n{block, redirect}, seed 4001\n200 splits", fc="#fdf3ef", ec=ORANGE, fs=6.5)
    box(ax, 0.70, 0.06, 0.293, 0.36, "N-H1: Lemma 1 fails\nN-H2: FPR certificate violates\nN-H3: direct certificate valid", fc="#ffffff", ec=ORANGE, fs=6.4)
    for x in (0.525, 0.85):
        arrow(ax, (x, 0.56), (x, 0.42), color=MUTED)
    arrow(ax, (0.125, 0.56), (0.125, 0.42), color=MUTED)
    save(fig, "fig_study_design")


# ============================================================ data figures
def grid_index(actions):
    return M.Ctx(taus=TAUS, actions=actions)


def fig_lemma():
    """Policy-level collateral R^c_s vs acted-benign fraction Phi_s: monotone study vs redirect study."""
    fig, axs = plt.subplots(1, 2, figsize=(7.16, 2.7), sharey=True)
    d = np.load(ROOT / "data/losses_pool.npz"); ctx = grid_index((0, 1)); N = d["Lc_i"].shape[0]
    F = M.fpr_matrix(ctx, d["score_i"], d["label"], d["slice"], d["ep_index"], N).mean(0)
    tidx = {t: j for j, t in enumerate(TAUS)}
    Phi = np.array([[0.0 if np.isinf(g[s][0]) else F[s, tidx[g[s][0]]] for s in range(3)] for g in ctx.grid])
    R = d["Lc_i"][:, :ctx.K].mean(0)
    dn = np.load(ROOT / "data_confirm/N.npz"); ctxn = grid_index((1, 2))
    Phin = dn["Fa"][:, :ctxn.K].mean(0); Rn = dn["Lc"][:, :ctxn.K].mean(0)
    for ax, P, Rr, title in ((axs[0], Phi, R, "Rate-limit / block (monotone)"), (axs[1], Phin, Rn, "Block / redirect (Study N)")):
        for s, c in zip(range(3), (BLUE, ORANGE, AQUA)):
            ax.scatter(P[:, s], Rr[:, s], s=9, color=c, alpha=0.55, lw=0, label=SL[s])
        lim = 0.32
        ax.plot([0, lim], [0, lim], color=INK2, lw=1, ls="--")
        ax.text(0.255, 0.238, "$R^c_s=\\Phi_s$", rotation=33, fontsize=6.5, color=INK2)
        ax.set_xlim(-0.005, lim); ax.set_ylim(-0.005, lim); ax.set_title(title, color=INK)
        ax.set_xlabel("acted-benign fraction $\\Phi_s$ (population)")
        above = (Rr > P + 1e-6).sum()
        ax.text(0.31, 0.012, f"(policy, slice) pairs above bound: {above} of {Rr.size}", fontsize=6.3, color=INK, ha="right")
    axs[0].set_ylabel("collateral $R^c_s$ (population)")
    axs[1].legend(loc="upper right", bbox_to_anchor=(1.0, 0.66), markerscale=1.6, title="slice", title_fontsize=7)
    # inset: zoom on the redirect region near the origin
    ins = axs[1].inset_axes([0.12, 0.47, 0.38, 0.33])
    for s, c in zip(range(3), (BLUE, ORANGE, AQUA)):
        ins.scatter(Phin[:, s], Rn[:, s], s=6, color=c, alpha=0.6, lw=0)
    ins.plot([0, 0.06], [0, 0.06], color=INK2, lw=0.8, ls="--"); ins.set_xlim(-0.001, 0.06); ins.set_ylim(-0.001, 0.08)
    ins.tick_params(labelsize=5.5); ins.text(0.002, 0.07, "zoom near origin", fontsize=5.8, color=INK2); ins.grid(True, lw=0.4)
    save(fig, "fig_lemma")


def fig_harm():
    hr = RES["harm_ratio"]
    fig, axs = plt.subplots(1, 3, figsize=(7.16, 2.3), sharey=True)
    x = np.arange(len(TAUS)); bw = 0.36
    for s, ax in enumerate(axs):
        for k, (act, c) in enumerate((("RL", BLUE), ("block", ORANGE))):
            vals = [hr[f"{SL[s]}|{t}|{act}"]["rho"] for t in TAUS]
            v = np.array([np.nan if a is None else a for a in vals], float)
            ax.bar(x + (k - 0.5) * bw, np.nan_to_num(v), width=bw - 0.04, color=c, label="rate-limit" if act == "RL" else "block")
            for xi, vi in zip(x, v):
                if np.isnan(vi):
                    ax.text(xi + (k - 0.5) * bw, 0.02, "n/a", ha="center", fontsize=5.5, color=MUTED, rotation=90)
        ax.set_xticks(x); ax.set_xticklabels([str(t) for t in TAUS]); ax.set_title(SL[s], color=INK)
        ax.set_xlabel("threshold $\\tau_s$"); ax.set_ylim(0, 1.05); ax.axhline(1, color=INK2, lw=0.8, ls=":")
    axs[0].set_ylabel("harm ratio $\\rho_s=R^c_s/\\Phi_s$")
    axs[0].legend(loc="upper left", ncol=1)
    save(fig, "fig_harm")


def split_diffs(rep):
    """Recompute the per-split paired differences (FS - Slice-FPR) exactly as confirm_analysis.py does."""
    d = np.load(ROOT / f"data_confirm/C_rep{rep}.npz"); ctx = grid_index((0, 1)); N = d["Lc"].shape[0]
    F = M.fpr_matrix(ctx, d["score"], d["label"], d["slice"], d["ep_index"], N)
    L, V, A = d["Lc"], d["Vb"], d["Ad"]
    rng = np.random.default_rng(7); out = []
    for _ in range(50):
        perm = rng.permutation(N); cal, test = np.sort(perm[:500]), np.sort(perm[500:])
        c1, _ = M.rcsir_fs(ctx, L, V, A, cal, rng); c2, _ = M.slice_fpr(ctx, F, cal, 1)
        out.append(float(np.nanmean(A[test, c1]) - np.nanmean(A[test, c2])))
    return np.array(out)


def fig_forest():
    reps = RC["C"]["replications"]; prim = RC["C"]["primary_FS_minus_SliceFPR"]
    fig, ax = plt.subplots(figsize=(3.5, 3.0))
    for i, rp in enumerate(reps):
        dd = split_diffs(rp["rep"])
        assert abs(dd.mean() - rp["d_fs_fpr"]) < 1e-9, "recomputation mismatch"
        y = len(reps) - i
        lo, hi = np.quantile(dd, [0.025, 0.975])
        ax.plot([lo, hi], [y, y], color=BLUE, lw=1.4, alpha=0.55, solid_capstyle="round")
        ax.scatter([dd.mean()], [y], s=26, color=BLUE, zorder=3, edgecolor=SURF, lw=0.8)
        ax.text(0.205, y, f"{rp['frac_splits_fs_better']:.2f}", va="center", fontsize=6.5, color=INK2)
    y = 0
    ax.plot(prim["t95"], [y, y], color=INK, lw=2.2, solid_capstyle="round")
    ax.scatter([prim["mean"]], [y], s=40, marker="D", color=INK, zorder=3)
    ax.axvline(0, color=INK2, lw=0.9, ls="--")
    ax.set_yticks(range(0, len(reps) + 1)); ax.set_yticklabels(["pooled\n(t 95% CI)"] + [f"rep {r['rep']}" for r in reps][::-1])
    ax.text(0.205, len(reps) + 0.75, "share of splits\nFS better", fontsize=5.8, color=INK2, ha="left", va="center")
    ax.set_ylim(-0.6, len(reps) + 1.2)
    ax.set_xlim(-0.33, 0.24)
    ax.set_xlabel("$\\Delta$ delivered attack fraction (FS $-$ Slice-FPR)\n$\\leftarrow$ direct certification better")
    ax.set_title("Study C: per-replication paired difference", color=INK)
    save(fig, "fig_forest")


def fig_tradeoff():
    reps = RC["C"]["replications"]
    fig, axs = plt.subplots(1, 2, figsize=(7.16, 2.6))
    meth = (("RC-SIR-FS", BLUE, "o"), ("Slice-FPR+block", ORANGE, "s"), ("ERM", AQUA, "^"))
    for m, c, mk in meth:
        xs = [max(np.array(r["per_method"][m]["collateral"]) / ALPHA) for r in reps]
        ys = [r["per_method"][m]["Ad"] for r in reps]
        axs[0].scatter(xs, ys, s=30, color=c, marker=mk, label=m.replace("+block", ""), edgecolor=SURF, lw=0.6, zorder=3)
    for r in reps:
        pts = [(max(np.array(r["per_method"][m]["collateral"]) / ALPHA), r["per_method"][m]["Ad"]) for m, _, _ in meth]
        axs[0].plot(*zip(*pts), color=GRID, lw=0.8, zorder=1)
    axs[0].axvline(1, color=RED, lw=1, ls="--"); axs[0].text(1.01, 0.33, "budget", color=INK2, fontsize=6.5, rotation=90)
    axs[0].set_xlabel("mean realised collateral / budget (worst slice)"); axs[0].set_ylabel("delivered attack fraction")
    axs[0].set_title("Study C: mitigation vs. budget use (per replication)", color=INK); axs[0].legend(loc="upper left", bbox_to_anchor=(0.0, 1.0), ncol=3, columnspacing=0.8, handletextpad=0.2)
    axs[0].set_ylim(0.27, 0.74)
    axs[0].set_xlim(0, 1.1)
    # validity: violation frequency with CP CI, pooled
    po = RC["C"]["pooled_over_splits"]; names = ["RC-SIR-FS", "Slice-FPR+block", "RC-SIR", "Pooled LTT", "ERM"]
    cols = [BLUE, ORANGE, VIOLET, MAGENTA, AQUA]
    for i, (n, c) in enumerate(zip(names, cols)):
        v = po[n]["viol"]; lo, hi = po[n]["viol_ci"]
        axs[1].plot([lo, hi], [i, i], color=c, lw=2.2, solid_capstyle="round"); axs[1].scatter([v], [i], color=c, s=28, zorder=3, edgecolor=SURF, lw=0.6)
    axs[1].axvline(0.10, color=RED, lw=1, ls="--"); axs[1].text(0.098, -0.35, "$\\delta=0.10$", fontsize=6.5, color=INK2, ha="right")
    axs[1].set_yticks(range(len(names))); axs[1].set_yticklabels([n.replace("+block", "") for n in names]); axs[1].invert_yaxis()
    axs[1].set_xlim(-0.003, 0.12); axs[1].set_xlabel("budget-violation frequency, 400 splits (95% Clopper–Pearson)")
    axs[1].set_title("Study C: validity", color=INK)
    save(fig, "fig_tradeoff")


def fig_study_n():
    dn = np.load(ROOT / "data_confirm/N.npz"); ctx = grid_index((1, 2))
    Phi = dn["Fa"][:, :ctx.K].mean(0); R = dn["Lc"][:, :ctx.K].mean(0)
    x = (Phi / ALPHA).max(1); y = (R / ALPHA).max(1)
    red = np.array([any(p[1] == 2 and np.isfinite(p[0]) for p in g) for g in ctx.grid])
    fig, axs = plt.subplots(1, 2, figsize=(7.16, 2.7), gridspec_kw=dict(width_ratios=[1.25, 1], wspace=0.55))
    ax = axs[0]
    ax.add_patch(Rectangle((0, 1), 1, 2.0, fc="#fdecec", ec="none", zorder=0))
    ax.text(0.03, 1.55, "FPR criterion accepts,\ncollateral exceeds budget", fontsize=6.5, color=INK)
    ax.scatter(x[red], y[red], s=8, color=ORANGE, alpha=0.5, lw=0, label="includes redirect", zorder=2)
    ax.scatter(x[~red], y[~red], s=14, color=BLUE, alpha=0.9, lw=0, label=f"block only ({(~red).sum()})", zorder=3)
    inv = (x <= 1) & (y > 1)
    ax.scatter(x[inv], y[inv], s=26, facecolor="none", edgecolor=RED, lw=1.0, label=f"invalid accepted ({inv.sum()})")
    ax.axvline(1, color=INK2, lw=0.8, ls="--"); ax.axhline(1, color=INK2, lw=0.8, ls="--")
    ax.set_xscale("symlog", linthresh=0.1); ax.set_yscale("symlog", linthresh=0.1)
    ax.set_xlim(0, 12); ax.set_ylim(0, 12)
    ax.set_xlabel("$\\max_s \\Phi_s/\\alpha_s$ (FPR criterion)"); ax.set_ylabel("$\\max_s R^c_s/\\alpha_s$ (true collateral)")
    ax.set_title("Study N: 1331 policies, population values", color=INK); ax.legend(loc="lower right", markerscale=1.5)
    assert inv.sum() == RC["exploratory_large_sample_fpr_feasibility"]["N|nominal"]["invalid"]
    # right: finite-sample outcomes
    pm = RC["N"]["per_method"]; names = ["RC-SIR-FS", "Slice-FPR+redirect", "Slice-FPR+block", "ERM"]
    cols = [BLUE, ORANGE, "#b5531f", AQUA]
    ax = axs[1]; yy = np.arange(len(names))
    ax.barh(yy, [pm[n]["Ad"] for n in names], color=cols, height=0.6)
    for i, n in enumerate(names):
        ax.text(pm[n]["Ad"] + 0.01, i, f"{pm[n]['Ad']:.3f}  (viol. {pm[n]['viol']:.3f})", va="center", fontsize=6.5, color=INK)
    ax.set_yticks(yy); ax.set_yticklabels(names); ax.invert_yaxis(); ax.set_xlim(0, 0.85)
    ax.set_xlabel("delivered attack fraction (200 splits)"); ax.set_title("Study N: finite-sample results", color=INK)
    ax.grid(axis="y", visible=False)
    save(fig, "fig_study_n")


def fig_hetero():
    het = RC["exploratory_heterogeneity"]["rows"]
    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    xs = np.array([h["band"] + h["margin_band"] for h in het], float); ys = np.array([h["diff"] for h in het])
    jit = np.array([-0.08, 0.10, -0.05, -0.12, 0.08, 0.0, 0.12, -0.02])[:len(xs)]
    ax.scatter(xs + jit, ys, s=34, color=BLUE, edgecolor=SURF, lw=0.7, zorder=3)
    off = {1: (-30, -4), 2: (5, 4), 3: (5, 3), 4: (5, 2), 5: (5, 2), 6: (5, 2), 7: (5, -8), 8: (5, -8)}
    for h, xj, y in zip(het, xs + jit, ys):
        ax.annotate(f"rep {h['rep']}", (xj, y), xytext=off.get(h["rep"], (4, 2)), textcoords="offset points", fontsize=6, color=INK2)
    ax.axhline(0, color=INK2, lw=0.8, ls="--")
    ax.set_xticks([0, 1]); ax.set_xlim(-0.4, 1.4)
    ax.set_xlabel("thresholds in the Remark 1 band (count)"); ax.set_ylabel("mean $\\Delta$ attack delivered (FS $-$ FPR)")
    ax.set_title(f"Post hoc: heterogeneity (Spearman {RC['exploratory_heterogeneity']['spearman']:.2f}, n=8)", color=INK)
    save(fig, "fig_hetero")


def fig_detector():
    d = np.load(ROOT / "data/losses_pool.npz"); sc, lab, sl = d["score_i"], d["label"], d["slice"]
    fig, axs = plt.subplots(1, 2, figsize=(7.16, 2.5))
    for s, c in zip(range(3), (BLUE, ORANGE, AQUA)):
        m = sl == s
        fpr, tpr, _ = roc_curve(lab[m], sc[m]); auc = roc_auc_score(lab[m], sc[m])
        axs[0].plot(fpr, tpr, color=c, label=f"{SL[s]} (AUC {auc:.2f})")
    for t in TAUS:
        f = (sc[~lab] >= t).mean(); tp = (sc[lab] >= t).mean()
        axs[0].scatter([f], [tp], s=12, color=INK, zorder=3)
    axs[0].plot([0, 1], [0, 1], color=GRID, lw=0.8, ls="--")
    axs[0].set_xscale("symlog", linthresh=0.01); axs[0].set_xlim(0, 1)
    axs[0].set_xlabel("false-positive rate (benign UEs)"); axs[0].set_ylabel("true-positive rate")
    axs[0].set_title("Isolation Forest under deployment shift (pool)", color=INK); axs[0].legend(loc="lower right")
    axs[0].text(0.0012, 0.30, "dots: grid thresholds,\nall slices pooled", fontsize=6, color=INK2)
    bins = np.linspace(0, 1, 41)
    for s, c in zip(range(3), (BLUE, ORANGE, AQUA)):
        axs[1].hist(sc[(~lab) & (sl == s)], bins=bins, histtype="step", color=c, lw=1.4, density=True, label=f"benign {SL[s]}")
    axs[1].hist(sc[lab], bins=bins, histtype="stepfilled", color=INK2, alpha=0.18, density=True, label="attackers (all)")
    for t in TAUS:
        axs[1].axvline(t, color=MUTED, lw=0.5, ls=":")
    axs[1].set_yscale("log"); axs[1].set_xlabel("score $z_u$ (benign-training quantile)"); axs[1].set_ylabel("density (log)")
    axs[1].set_title("Score distributions; dotted: grid thresholds", color=INK); axs[1].legend(loc="upper left", fontsize=6)
    save(fig, "fig_detector")


def fig_ncal():
    """Restyled version of the exploratory n-sweep (values from results/results.json)."""
    nc = RES["ncal"]; ns = sorted(nc, key=int); x = [int(n) for n in ns]
    meth = (("RC-SIR-FS (ours)", "RC-SIR-FS", BLUE, "o", "-"), ("Slice-FPR certified + block", "Slice-FPR", ORANGE, "s", "-"),
            ("RC-SIR (ours)", "RC-SIR (Bonferroni)", VIOLET, "D", "-"), ("ERM (no margin)", "ERM", AQUA, "^", "--"))
    fig, axs = plt.subplots(1, 2, figsize=(7.16, 2.5))
    for key, lab, c, mk, ls in meth:
        axs[0].plot(x, [nc[n][key]["viol_freq"] for n in ns], color=c, marker=mk, ms=4, ls=ls, label=lab)
        axs[1].plot(x, [nc[n][key]["attack_delivered_mean"] for n in ns], color=c, marker=mk, ms=4, ls=ls, label=lab)
    axs[0].axhline(0.1, color=RED, lw=1, ls=":"); axs[0].text(1000, 0.106, "$\\delta=0.10$", ha="right", fontsize=6.5, color=INK2)
    axs[0].set_xlabel("calibration episodes $n$"); axs[0].set_ylabel("budget-violation frequency (200 splits)")
    axs[0].text(550, 0.016, "RC-SIR-FS, Slice-FPR, RC-SIR: 0 at every $n$ (overlapping)", ha="center", fontsize=6.5, color=INK2)
    axs[0].set_title("Exploratory: validity vs. calibration size", color=INK)
    axs[1].axhline(RES["main"]["No action"]["attack_delivered_mean"], color=MUTED, lw=1, ls=":")
    axs[1].text(1000, RES["main"]["No action"]["attack_delivered_mean"] - 0.04, "no action", ha="right", fontsize=6.5, color=INK2)
    axs[1].set_xlabel("calibration episodes $n$"); axs[1].set_ylabel("delivered attack fraction")
    axs[1].set_title("Exploratory: mitigation vs. calibration size", color=INK); axs[1].legend(loc="center right")
    save(fig, "fig_ncal")


if __name__ == "__main__":
    fig_system(); fig_workflow(); fig_study_design()
    fig_lemma(); fig_harm(); fig_ncal(); fig_forest(); fig_tradeoff(); fig_study_n(); fig_hetero(); fig_detector()
