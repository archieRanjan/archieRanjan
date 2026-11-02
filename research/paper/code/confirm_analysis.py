"""Pre-registered analysis of Studies C and N (ANALYSIS_PLAN_v2.md). Writes ../results_confirm/.
Usage: python3 -I confirm_analysis.py
"""
import json, pathlib, sys
import numpy as np
from scipy import stats
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import methods as M

ROOT = pathlib.Path(__file__).resolve().parent.parent
DC, OUT = ROOT / "data_confirm", ROOT / "results_confirm"
(OUT / "tables").mkdir(parents=True, exist_ok=True)
TAUS = (0.9, 0.95, 0.99, 0.995, 0.999)
N_CAL, SPLIT_SEED, ETA = 500, 7, 0.05


def cp_ci(k, n):
    r = stats.binomtest(int(k), int(n)).proportion_ci(confidence_level=0.95, method="exact")
    return [float(r.low), float(r.high)]


def run_splits(ctx, d, methods, R):
    L, V, A = d["Lc"], d["Vb"], d["Ad"]; N = L.shape[0]
    rng = np.random.default_rng(SPLIT_SEED); out = {m: [] for m in methods}
    for _ in range(R):
        perm = rng.permutation(N); cal, test = np.sort(perm[:N_CAL]), np.sort(perm[N_CAL:])
        for m, fn in methods.items():
            c, nc = fn(L, V, A, cal, rng)
            Rs = L[test, c].mean(0); nt = len(test)
            lower = Rs - np.sqrt(np.log(1 / ETA) / (2 * nt))            # one-sided Hoeffding lower bound
            out[m].append(dict(cfg=int(c), R=Rs.tolist(), viol=bool((Rs > ctx.alpha).any()),
                               conf_viol=bool((lower > ctx.alpha).any()), Ad=float(np.nanmean(A[test, c])),
                               J=float((V[test, c].mean(0) * ctx.w).sum()), fallback=bool(c == ctx.I0)))
    return out


def summ(rows):
    v = sum(r["viol"] for r in rows); n = len(rows)
    return dict(n=n, viol=v / n, viol_ci=cp_ci(v, n), conf_viol=sum(r["conf_viol"] for r in rows) / n,
                Ad=float(np.mean([r["Ad"] for r in rows])), J=float(np.mean([r["J"] for r in rows])),
                collateral=np.mean([r["R"] for r in rows], 0).tolist(),
                fallback=float(np.mean([r["fallback"] for r in rows])))


res = {"plan": "ANALYSIS_PLAN_v2.md", "n_cal": N_CAL, "split_seed": SPLIT_SEED}

# ------------------------------------------------------------------ Study C
names = ["RC-SIR-FS", "Slice-FPR+block", "RC-SIR", "ERM", "Pooled LTT", "No action", "Oracle"]
reps, rows_all = [], {m: [] for m in names}
for r in range(1, 9):
    f = DC / f"C_rep{r}.npz"
    if not f.exists():
        continue
    d = np.load(f); meta = json.loads((DC / f"C_rep{r}.json").read_text())
    ctx = M.Ctx(taus=TAUS, actions=(0, 1)); N = d["Lc"].shape[0]
    F = M.fpr_matrix(ctx, d["score"], d["label"], d["slice"], d["ep_index"], N)
    nben = np.array(meta["scenario"]["n_ue"], float)
    meth = {"RC-SIR-FS": lambda L, V, A, cal, rng: M.rcsir_fs(ctx, L, V, A, cal, rng),
            "Slice-FPR+block": lambda L, V, A, cal, rng: M.slice_fpr(ctx, F, cal, 1),
            "RC-SIR": lambda L, V, A, cal, rng: M.rcsir(ctx, L, V, A, cal, rng),
            "ERM": lambda L, V, A, cal, rng: M.erm(ctx, L, V, A, cal, rng),
            "Pooled LTT": lambda L, V, A, cal, rng: M.pooled(ctx, L, V, A, cal, rng, nben),
            "No action": lambda *a: (ctx.I0, 1), "Oracle": lambda *a: (ctx.IOR, 1)}
    out = run_splits(ctx, d, meth, 50)
    for m in names:
        rows_all[m] += out[m]
    diff = lambda a, b: float(np.mean([x["Ad"] - y["Ad"] for x, y in zip(out[a], out[b])]))
    reps.append(dict(rep=r, seed=meta["seed"], auc=meta["auc"], scenario=meta["scenario"],
                     attack_episode_frac=meta["attack_episode_frac"],
                     per_method={m: summ(out[m]) for m in names},
                     d_fs_fpr=diff("RC-SIR-FS", "Slice-FPR+block"), d_fs_erm=diff("RC-SIR-FS", "ERM"),
                     d_bonf_fpr=diff("RC-SIR", "Slice-FPR+block"),
                     frac_splits_fs_better=float(np.mean([x["Ad"] < y["Ad"] for x, y in zip(out["RC-SIR-FS"], out["Slice-FPR+block"])]))))


def across(key):
    x = np.array([rp[key] for rp in reps]); n = len(x)
    ci = stats.t.interval(0.95, n - 1, loc=x.mean(), scale=x.std(ddof=1) / np.sqrt(n)) if n > 1 else (np.nan, np.nan)
    neg = int((x < 0).sum()); pos = int((x > 0).sum())
    sign_p = float(stats.binomtest(neg, neg + pos, 0.5).pvalue) if neg + pos > 0 else 1.0
    return dict(values=x.tolist(), mean=float(x.mean()), t95=[float(ci[0]), float(ci[1])], n_negative=neg,
                n_positive=pos, sign_test_p=sign_p)


if reps:
  res["C"] = dict(replications=reps, pooled_over_splits={m: summ(rows_all[m]) for m in names},
                primary_FS_minus_SliceFPR=across("d_fs_fpr"), FS_minus_ERM=across("d_fs_erm"),
                Bonferroni_minus_SliceFPR=across("d_bonf_fpr"))
  p = res["C"]["primary_FS_minus_SliceFPR"]
  res["C"]["primary_claim_supported"] = bool(p["t95"][1] < 0 and p["n_negative"] >= 7) if len(reps) == 8 else None

# ------------------------------------------------------------------ Study N
if (DC / "N.npz").exists():
    d = np.load(DC / "N.npz"); ctx = M.Ctx(taus=TAUS, actions=(1, 2)); N = d["Lc"].shape[0]
    excess = d["Lc"][:, :ctx.K] - d["Fa"][:, :ctx.K]
    F = M.fpr_matrix(ctx, d["score"], d["label"], d["slice"], d["ep_index"], N)
    meth = {"RC-SIR-FS": lambda L, V, A, cal, rng: M.rcsir_fs(ctx, L, V, A, cal, rng),
            "Slice-FPR+redirect": lambda L, V, A, cal, rng: M.slice_fpr(ctx, F, cal, 2),
            "Slice-FPR+block": lambda L, V, A, cal, rng: M.slice_fpr(ctx, F, cal, 1),
            "ERM": lambda L, V, A, cal, rng: M.erm(ctx, L, V, A, cal, rng),
            "No action": lambda *a: (ctx.I0, 1), "Oracle": lambda *a: (ctx.IOR, 1)}
    out = run_splits(ctx, d, meth, 200)
    # where does A3 fail? single-slice redirect policies
    single = {}
    for s in range(3):
        for t in TAUS:
            cfg = [(np.inf, 1)] * 3; cfg[s] = (t, 2); c = ctx.index[tuple(cfg)]
            single[f"slice{s}|{t}|redirect"] = dict(collateral_all_slices=d["Lc"][:, c].mean(0).tolist(),
                                                     acted_frac=d["Fa"][:, c].mean(0).tolist())
    res["N"] = dict(auc=json.loads((DC / "N.json").read_text())["auc"],
                    A3_excess_max=float(excess.max()), A3_excess_frac_entries=float((excess > 1e-6).mean()),
                    A3_excess_frac_policies_any=float((excess > 1e-6).any(axis=(0, 2)).mean()),
                    per_method={m: summ(out[m]) for m in meth}, single_slice_redirect=single,
                    H1_supported=bool(excess.max() > 1e-6))
    pm = res["N"]["per_method"]
    res["N"]["H2_supported"] = bool(pm["Slice-FPR+redirect"]["viol"] > 0.1)
    res["N"]["H3_supported"] = bool(pm["RC-SIR-FS"]["viol"] <= 0.1)

(OUT / "results_confirm.json").write_text(json.dumps(res, indent=1))

# ------------------------------------------------------------------ tables
L = ["| Rep | Seed | AUC | UEs (eMBB/URLLC/mMTC) | p_attack | Viol. FS | Viol. Slice-FPR | Viol. ERM | Attack del. FS | Attack del. Slice-FPR | Mean diff (FS−FPR) | Splits FS better |",
     "|--:|--:|--:|:--|--:|--:|--:|--:|--:|--:|--:|--:|"]
for rp in reps:
    pm = rp["per_method"]
    L.append(f"| {rp['rep']} | {rp['seed']} | {rp['auc']:.3f} | {'/'.join(map(str, rp['scenario']['n_ue']))} | {rp['scenario']['p_attack']:.2f} | "
             f"{pm['RC-SIR-FS']['viol']:.2f} | {pm['Slice-FPR+block']['viol']:.2f} | {pm['ERM']['viol']:.2f} | {pm['RC-SIR-FS']['Ad']:.3f} | "
             f"{pm['Slice-FPR+block']['Ad']:.3f} | {rp['d_fs_fpr']:+.3f} | {rp['frac_splits_fs_better']:.2f} |")
if reps: (OUT / "tables" / "confirm_C_reps.md").write_text("\n".join(L) + "\n\n: Study C, eight independent replications (50 splits each, n_cal = 500). Viol. = fraction of splits in which any slice's test collateral exceeded its budget.\n")
L = ["| Method | Viol. freq. [95% CP CI] | Confident viol. | Coll. eMBB | Coll. URLLC | Coll. mMTC | Attack delivered | Fallback |", "|:--|--:|--:|--:|--:|--:|--:|--:|"]
for m, s in res.get("C", {}).get("pooled_over_splits", {}).items():
    L.append(f"| {m} | {s['viol']:.3f} [{s['viol_ci'][0]:.3f}, {s['viol_ci'][1]:.3f}] | {s['conf_viol']:.3f} | " + " | ".join(f"{x:.4f}" for x in s["collateral"]) + f" | {s['Ad']:.3f} | {s['fallback']:.2f} |")
if reps: (OUT / "tables" / "confirm_C_pooled.md").write_text("\n".join(L) + "\n\n: Study C pooled over 400 splits (8 replications × 50). Confident viol. = a one-sided 95% Hoeffding lower bound on the test risk exceeds the budget.\n")
if "N" in res:
    L = ["| Method | Viol. freq. [95% CP CI] | Confident viol. | Coll. eMBB | Coll. URLLC | Coll. mMTC | Attack delivered | Fallback |", "|:--|--:|--:|--:|--:|--:|--:|--:|"]
    for m, s in res["N"]["per_method"].items():
        L.append(f"| {m} | {s['viol']:.3f} [{s['viol_ci'][0]:.3f}, {s['viol_ci'][1]:.3f}] | {s['conf_viol']:.3f} | " + " | ".join(f"{x:.4f}" for x in s["collateral"]) + f" | {s['Ad']:.3f} | {s['fallback']:.2f} |")
    (OUT / "tables" / "confirm_N.md").write_text("\n".join(L) + "\n\n: Study N, actions {block, redirect}, 200 splits (n_cal = 500). Redirect violates assumption A3.\n")
print(json.dumps({k: v for k, v in res.get("C", {}).items() if k not in ("replications", "pooled_over_splits")}, indent=1))
if "N" in res:
    print(json.dumps({k: v for k, v in res["N"].items() if k not in ("single_slice_redirect",)}, indent=1))

# ------------------------------------------------------------------ EXPLORATORY (post hoc, not in the plan)
# Large-sample limit: treat all pool episodes as the population. A policy is "FPR-feasible" if its
# per-slice acted-benign fraction Phi_s <= alpha_s for every slice, which is what a per-slice FPR
# certificate accepts as n -> infinity. It is "invalid" if its true collateral exceeds a budget.
# Under A3 (Lemma 1) there can be no invalid FPR-feasible policy; under redirect there can.
expl = {}
alphas = {"nominal": np.array([0.05, 0.02, 0.05]), "tight URLLC/mMTC (0.05, 0.005, 0.005)": np.array([0.05, 0.005, 0.005])}
if (DC / "N.npz").exists():
    d = np.load(DC / "N.npz"); ctx = M.Ctx(taus=TAUS, actions=(1, 2))
    Phi = d["Fa"][:, :ctx.K].mean(0); Rc = d["Lc"][:, :ctx.K].mean(0)
    red = np.array([any(p[1] == 2 and np.isfinite(p[0]) for p in g) for g in ctx.grid])
    for name, a in alphas.items():
        feas = (Phi <= a).all(1); inval = feas & (Rc > a).any(1)
        expl[f"N|{name}"] = dict(fpr_feasible=int(feas.sum()), invalid=int(inval.sum()),
                                 invalid_with_redirect=int((inval & red).sum()),
                                 max_excess_over_budget=float((Rc - a)[feas].max()) if feas.any() else None)
mono = ROOT / "data/losses_pool.npz"
if mono.exists():
    d = np.load(mono); ctx = M.Ctx(taus=TAUS, actions=(0, 1)); N = d["Lc_i"].shape[0]
    F = M.fpr_matrix(ctx, d["score_i"], d["label"], d["slice"], d["ep_index"], N).mean(0)       # (3, taus)
    tidx = {t: j for j, t in enumerate(TAUS)}
    Phi = np.array([[0.0 if np.isinf(g[s][0]) else F[s, tidx[g[s][0]]] for s in range(3)] for g in ctx.grid])
    Rc = d["Lc_i"][:, :ctx.K].mean(0)
    for name, a in alphas.items():
        feas = (Phi <= a).all(1); inval = feas & (Rc > a + 1e-9).any(1)
        expl[f"monotone v1 pool|{name}"] = dict(fpr_feasible=int(feas.sum()), invalid=int(inval.sum()))
res["exploratory_large_sample_fpr_feasibility"] = expl
(OUT / "results_confirm.json").write_text(json.dumps(res, indent=1))
print(json.dumps(expl, indent=1))

# EXPLORATORY (post hoc): does Remark 1 explain the heterogeneity across Study C replications?
# For each replication (all 1500 episodes as the population) and each slice/threshold with action
# "block": band = (Phi_s > alpha_s) and (R^c_s <= alpha_s), i.e. thresholds that only direct
# certification can accept. We also record the margin-band, a weaker condition:
# alpha_s/2 < Phi_s <= alpha_s and R^c_s <= alpha_s/2 (the FPR test needs a margin the
# collateral test does not).
het = []
for rp in res.get("C", {}).get("replications", []):
    d = np.load(DC / f"C_rep{rp['rep']}.npz"); ctx = M.Ctx(taus=TAUS, actions=(0, 1)); N = d["Lc"].shape[0]
    F = M.fpr_matrix(ctx, d["score"], d["label"], d["slice"], d["ep_index"], N).mean(0)
    band = mband = 0; rows = {}
    for s in range(3):
        for j, t in enumerate(TAUS):
            cfg = [(np.inf, 0)] * 3; cfg[s] = (t, 1); c = ctx.index[tuple(cfg)]
            Rc = float(d["Lc"][:, c, s].mean()); Phi = float(F[s, j]); a = float(ctx.alpha[s])
            band += Phi > a and Rc <= a
            mband += (a / 2 < Phi <= a) and Rc <= a / 2
            rows[f"{s}|{t}"] = (round(Phi, 4), round(Rc, 4))
    het.append(dict(rep=rp["rep"], diff=rp["d_fs_fpr"], band=int(band), margin_band=int(mband), phi_rc=rows))
if het:
    x = np.array([h["band"] + h["margin_band"] for h in het]); y = np.array([h["diff"] for h in het])
    res["exploratory_heterogeneity"] = dict(rows=het, spearman=float(stats.spearmanr(x, y).statistic) if x.std() > 0 else None)
    (OUT / "results_confirm.json").write_text(json.dumps(res, indent=1))
    for h in het:
        print(h["rep"], round(h["diff"], 3), "band", h["band"], "margin_band", h["margin_band"], {k: v for k, v in h["phi_rc"].items() if k.startswith("0|")})
    print("spearman(band+margin_band, diff) =", res["exploratory_heterogeneity"]["spearman"])
