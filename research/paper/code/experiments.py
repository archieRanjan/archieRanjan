"""Stage 2: calibration methods, repeated-split experiments, tables and figures.

Reads ../data/losses_*.npz (from generate.py) and writes:
  ../results/results.json   every number quoted in the paper
  ../results/tables/*.md|*.tex
  ../figs/*.pdf|*.png
Usage: python3 -I experiments.py
"""
import json, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import numpy as np
from riskcontrol import hb_pvalue
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA, RES, FIG = ROOT / "data", ROOT / "results", ROOT / "figs"
(RES / "tables").mkdir(parents=True, exist_ok=True); FIG.mkdir(exist_ok=True)

ALPHA = np.array([0.05, 0.02, 0.05])      # per-slice collateral budgets eMBB, URLLC, mMTC
DELTA = 0.10                               # 1 - confidence
W = np.array([0.3, 0.5, 0.2])             # slice weights of the objective
N_BEN = np.array([14, 10, 16])            # benign UEs per slice (fixed by the simulator)
R_SPLITS, N_CAL = 200, 500
SPLIT_SEED = 7
SL = ("eMBB", "URLLC", "mMTC")

pool = np.load(DATA / "losses_pool.npz"); shift = np.load(DATA / "losses_shift.npz")
setup = json.loads((DATA / "detector_and_setup.json").read_text())
K_ALL = pool["Lc_g"].shape[1]; K = K_ALL - 2           # last two: pi_0, oracle
I0, IOR = K, K + 1
TAUS = GRID = SAME = BLOCK_ONLY = None


def set_grid(taus):
    """Policy grid for the detector in use (must match generate.py)."""
    global TAUS, GRID, SAME, BLOCK_ONLY
    TAUS = tuple(taus)
    per = [(np.inf, 0)] + [(t, a) for t in TAUS for a in (0, 1)]
    GRID = [(per[i], per[j], per[k]) for i in range(11) for j in range(11) for k in range(11)]
    SAME = [c for c in range(K) if GRID[c][0] == GRID[c][1] == GRID[c][2]]
    BLOCK_ONLY = [c for c in range(K) if all(p[1] == 1 or np.isinf(p[0]) for p in GRID[c])]


# ---------------------------------------------------------------- statistics
def objective(Vb, Ad):
    j = (Vb * W).sum(-1)
    return j


OBJECTIVE = "attack"     # pre-specified in the checkpoint report: minimise residual attack impact


def sel_obj(Vb, Ad, idx):
    """Selection objective on calibration episodes idx. 'attack': mean delivered attack fraction over
    attack episodes (+1e-3 * J as tie-breaker). 'J': weighted benign violation (secondary analysis)."""
    J = objective(Vb[idx, :K].mean(0), None)
    if OBJECTIVE == "J":
        return J
    with np.errstate(invalid="ignore"):
        a = np.nanmean(Ad[idx, :K], 0)
    return np.nan_to_num(a, nan=0.0) + 1e-3 * J


def select(cert, J):
    """Among certified configs choose min J; fall back to pi_0 when none is certified."""
    idx = np.flatnonzero(cert)
    return int(idx[np.argmin(J[idx])]) if len(idx) else I0


def m_rcsir(Lc, Vb, Ad, cal, rng, family=None, alpha=None):
    alpha = ALPHA if alpha is None else alpha
    n = len(cal)
    R = Lc[cal, :K].mean(0)                                  # (K,3)
    fam = np.arange(K) if family is None else np.asarray(family)
    if np.any(alpha <= 0):
        return I0, 0
    p = hb_pvalue(R[fam], alpha[None, :], n).max(1)         # union null over slices
    cert = np.zeros(K, bool); cert[fam] = p <= DELTA / len(fam)
    J = sel_obj(Vb, Ad, cal)
    return select(cert, J), int(cert.sum())


def m_rcsir_fs(Lc, Vb, Ad, cal, rng, alpha=None, family=None):
    alpha = ALPHA if alpha is None else alpha
    if np.any(alpha <= 0):
        return I0, 0
    """Fixed-sequence LTT: order by a data-independent half, test sequentially on the other half."""
    perm = rng.permutation(cal); a, b = perm[: len(cal) // 2], perm[len(cal) // 2:]
    Ra = Lc[a, :K].mean(0); Jall = sel_obj(Vb, Ad, cal)
    order = np.lexsort((sel_obj(Vb, Ad, a), (Ra / alpha).max(1)))   # primary: risk ratio on half a
    Rb = Lc[b, :K].mean(0)
    p = hb_pvalue(Rb, alpha[None, :], len(b)).max(1)
    cert = np.zeros(K, bool)
    if family is not None:
        fam = set(int(f) for f in family); order = [c for c in order if c in fam]
    for c in order:
        if p[c] <= DELTA:
            cert[c] = True
        else:
            break
    return select(cert, Jall), int(cert.sum())


def m_erm(Lc, Vb, Ad, cal, rng):
    """Empirical constrained minimisation (no statistical margin): min J s.t. Rhat_s <= alpha_s."""
    R = Lc[cal, :K].mean(0); J = sel_obj(Vb, Ad, cal)
    return select((R <= ALPHA).all(1), J), int((R <= ALPHA).all(1).sum())


def m_pooled(Lc, Vb, Ad, cal, rng):
    """Pooled LTT: one (tau, action) for all slices; budget on benign-averaged collateral."""
    pooledL = (Lc[cal, :K] * N_BEN).sum(-1) / N_BEN.sum()
    a_pool = float((ALPHA * N_BEN).sum() / N_BEN.sum())
    fam = np.array(SAME)
    p = hb_pvalue(pooledL[:, fam].mean(0), a_pool, len(cal))
    cert = np.zeros(K, bool); cert[fam] = p <= DELTA / len(fam)
    return select(cert, sel_obj(Vb, Ad, cal)), int(cert.sum())


def fixed_cfg(t, a):
    return GRID.index(((t, a), (t, a), (t, a)))


def m_fixed(*_):
    """Static shipped operating point: block above the 99th percentile of benign training scores
    (Isolation Forest) or above p = 0.5 (GBM)."""
    return fixed_cfg(0.99 if TAUS[0] >= 0.9 else 0.5, 1), 1


def make_fpr(score_key):
    def m_fpr(Lc, Vb, Ad, cal, rng, alpha_fpr=0.01):
        """Alert-level conformal FPR control: smallest grid tau whose conformal upper bound on the
        benign-UE false-positive rate is <= 1%, then block (CALIBURN/ConFID-style operating point)."""
        ue = np.isin(pool["ep_index"], cal) & (~pool["label"])
        s = pool[score_key][ue]; n = len(s)
        for t in TAUS:
            if ((s >= t).sum() + 1) / (n + 1) <= alpha_fpr:
                return fixed_cfg(t, 1), 1
        return I0, 0
    return m_fpr


def slice_fpr_matrix(score_key):
    """Episode-level benign acted fraction FPR[e, s, j] = share of benign UEs of slice s in episode e
    whose score >= TAUS[j]. Under Lemma 1 this upper-bounds the action-induced collateral."""
    sc, lab, sl, ei = pool[score_key], pool["label"], pool["slice"], pool["ep_index"]
    F = np.zeros((N, 3, len(TAUS)))
    for s in range(3):
        m = (~lab) & (sl == s)
        cnt = np.bincount(ei[m], minlength=N)
        for j, t in enumerate(TAUS):
            F[:, s, j] = np.bincount(ei[m], weights=(sc[m] >= t).astype(float), minlength=N) / np.maximum(cnt, 1)
    return F


def make_slice_fpr(F):
    def m_slice_fpr(Lc, Vb, Ad, cal, rng):
        """Strongest alert-level competitor: per-slice certified FPR control (Mondrian-style, LTT/HB
        p-values, fixed-sequence over decreasing thresholds since FPR is monotone in tau, Bonferroni
        over the three slices), then block. By Lemma 1 it also certifies collateral."""
        chosen = []
        for s in range(3):
            pick = (np.inf, 0)
            for j in reversed(range(len(TAUS))):               # most conservative threshold first
                if hb_pvalue(F[cal, s, j].mean(), ALPHA[s], len(cal)) <= DELTA / 3:
                    pick = (TAUS[j], 1)
                else:
                    break
            chosen.append(pick)
        return GRID.index(tuple(chosen)), 1
    return m_slice_fpr


def m_oracle(*_):
    return IOR, 1


def m_none(*_):
    return I0, 1


METHODS = {"RC-SIR (ours)": lambda *a: m_rcsir(*a), "RC-SIR-FS (ours)": m_rcsir_fs,
           "ERM (no margin)": m_erm, "Pooled LTT": m_pooled, "Conformal FPR 1% + block": make_fpr("score_i"),
           "Fixed threshold + block": m_fixed, "No action": m_none, "Oracle": m_oracle}


def evaluate(method, Lc, Vb, Ad, cal_pool_n, test_from, rng_seed=SPLIT_SEED, R=R_SPLITS, n_cal=N_CAL,
             test_arrays=None):
    """Repeated random splits. test_arrays: optional (Lc,Vb,Ad) of a separate test population."""
    rng = np.random.default_rng(rng_seed)
    rows = []
    for r in range(R):
        perm = rng.permutation(cal_pool_n)
        cal = np.sort(perm[:n_cal]); test = np.sort(perm[n_cal:])
        c, ncert = method(Lc, Vb, Ad, cal, rng)
        if test_arrays is None:
            tL, tV, tA = Lc[test, c], Vb[test, c], Ad[test, c]
        else:
            tL, tV, tA = test_arrays[0][:, c], test_arrays[1][:, c], test_arrays[2][:, c]
        Rs = tL.mean(0)
        rows.append(dict(cfg=c, ncert=ncert, R=Rs, viol=bool((Rs > ALPHA).any()), viol_s=(Rs > ALPHA),
                         J=float((tV.mean(0) * W).sum()), Vb=tV.mean(0), Ad=float(np.nanmean(tA)),
                         fallback=(c == I0)))
    return summarize(rows)


def summarize(rows):
    R = np.array([r["R"] for r in rows]); Vb = np.array([r["Vb"] for r in rows])
    n = len(rows); v = np.mean([r["viol"] for r in rows])
    return dict(n_splits=n, viol_freq=float(v), viol_freq_mc_se=float(np.sqrt(v * (1 - v) / n)),
                viol_freq_per_slice=np.mean([r["viol_s"] for r in rows], 0).tolist(),
                collateral_mean=R.mean(0).tolist(), collateral_p90=np.quantile(R, 0.9, axis=0).tolist(),
                collateral_all=R.tolist(),
                J_mean=float(np.mean([r["J"] for r in rows])), J_sd=float(np.std([r["J"] for r in rows])),
                Vb_mean=Vb.mean(0).tolist(), attack_delivered_mean=float(np.mean([r["Ad"] for r in rows])),
                fallback_rate=float(np.mean([r["fallback"] for r in rows])),
                ncert_median=float(np.median([r["ncert"] for r in rows])),
                cfg_mode=describe(int(np.bincount([r["cfg"] for r in rows]).argmax())))


def describe(c):
    if c == I0: return "no action"
    if c == IOR: return "oracle"
    return "; ".join(f"{SL[s]}: " + ("off" if np.isinf(GRID[c][s][0]) else f"{'RL' if GRID[c][s][1] == 0 else 'block'}@{GRID[c][s][0]}")
                     for s in range(3))


res = {"objective": OBJECTIVE, "setup": setup, "alpha": ALPHA.tolist(), "delta": DELTA, "weights": W.tolist(), "n_cal": N_CAL,
       "R_splits": R_SPLITS, "grid_size": K}
set_grid(setup["taus"]["iforest"])                    # primary detector: Isolation Forest
L, V, A = pool["Lc_i"], pool["Vb_i"], pool["Ad_i"]
N = L.shape[0]
F_I = slice_fpr_matrix("score_i")
METHODS = {**{k: v for k, v in METHODS.items() if k in ("RC-SIR (ours)", "RC-SIR-FS (ours)")},
           "Slice-FPR certified + block": make_slice_fpr(F_I),
           **{k: v for k, v in METHODS.items() if k not in ("RC-SIR (ours)", "RC-SIR-FS (ours)")}}
# Lemma 1 assumption test: action-induced collateral can only fall on acted benign UEs
_tidx = {t: j for j, t in enumerate(TAUS)}
_bound = np.zeros((N, K, 3))
for c in range(K):
    for s in range(3):
        t = GRID[c][s][0]
        _bound[:, c, s] = 0.0 if np.isinf(t) else F_I[:, s, _tidx[t]]
res_lemma = {"max_excess_collateral_over_acted_fraction": float((L[:, :K] - _bound).max()),
             "frac_entries_violating_1e-6": float(((L[:, :K] - _bound) > 1e-6).mean()),
             "mean_ratio_collateral_to_acted_fraction_when_acted": float(L[:, :K][_bound > 0].sum() / _bound[_bound > 0].sum())}
res["lemma1_check"] = res_lemma
# harm ratio rho_s(tau, action) = E[collateral] / E[acted benign fraction] (Proposition 2)
res["harm_ratio"] = {}
for s in range(3):
    for t in TAUS:
        for act_ in (0, 1):
            cfg = [(np.inf, 0)] * 3; cfg[s] = (t, act_); c = GRID.index(tuple(cfg))
            den = F_I[:, s, _tidx[t]].mean()
            res["harm_ratio"][f"{SL[s]}|{t}|{'RL' if act_ == 0 else 'block'}"] = {
                "acted_benign_frac": float(den), "collateral": float(L[:, c, s].mean()),
                "rho": float(L[:, c, s].mean() / den) if den > 0 else None}
res["pool_stats"] = {"episodes": int(N), "attack_episode_frac": float(pool["has_attack"].mean()),
                     "pi0_benign_violation": V[:, I0].mean(0).tolist(),
                     "oracle_benign_violation": V[:, IOR].mean(0).tolist(),
                     "pi0_benign_violation_attack_eps": V[pool["has_attack"], I0].mean(0).tolist()}

# E1/E2 main comparison (GBM detector)
res["main"] = {m: evaluate(f, L, V, A, N, None) for m, f in METHODS.items()}
# E3 calibration size
res["ncal"] = {}
for n in (100, 250, 500, 750, 1000):
    res["ncal"][n] = {m: {k: v for k, v in evaluate(METHODS[m], L, V, A, N, None, n_cal=n).items() if k != "collateral_all"}
                      for m in ("RC-SIR (ours)", "RC-SIR-FS (ours)", "Slice-FPR certified + block", "ERM (no margin)")}
# E4 ablations
res["ablation"] = {
    "RC-SIR block-only actions": evaluate(lambda *a: m_rcsir(*a, family=BLOCK_ONLY), L, V, A, N, None),
    "RC-SIR multi-action (full)": res["main"]["RC-SIR (ours)"],
    "RC-SIR-FS block-only actions": evaluate(lambda *a: m_rcsir_fs(*a, family=BLOCK_ONLY), L, V, A, N, None),
    "RC-SIR-FS multi-action (full)": res["main"]["RC-SIR-FS (ours)"]}
# E6 distribution shift: calibrate on nominal pool, test on high-load episodes
S = (shift["Lc_i"], shift["Vb_i"], shift["Ad_i"])
res["shift"] = {m: evaluate(METHODS[m], L, V, A, N, None, test_arrays=S)
                for m in ("RC-SIR (ours)", "RC-SIR-FS (ours)", "ERM (no margin)", "Pooled LTT")}
res["shift"]["RC-SIR recalibrated on shifted data (n=200)"] = evaluate(METHODS["RC-SIR (ours)"], *S, S[0].shape[0], None, n_cal=200)
# E7 twin-in-the-loop calibration: calibrate on twin losses, test on real losses
Lt, Vt, At = pool["Lc_t"], pool["Vb_t"], pool["Ad_t"]


def twin_eval(correction, m_pair=300, eta=0.05):
    rng = np.random.default_rng(SPLIT_SEED); rows = []
    for r in range(R_SPLITS):
        perm = rng.permutation(N)
        pair, cal, test = perm[:m_pair], np.sort(perm[m_pair:m_pair + N_CAL]), perm[m_pair + N_CAL:]
        gap = np.abs(Lt[pair, :K] - L[pair, :K]).mean(0).max(0)            # plug-in sup_lambda gap per slice
        if correction == "none":
            alpha = ALPHA
        elif correction == "plug-in":
            alpha = ALPHA - gap
        else:  # 'hoeffding': rigorous union bound over all (lambda, slice)
            alpha = ALPHA - gap - np.sqrt(np.log(3 * K / eta) / (2 * m_pair))
        c, nc = TWIN_METHOD(Lt, Vt, At, cal, rng, alpha=np.where(alpha > 0, alpha, -1))
        Rs = L[test, c].mean(0)
        rows.append(dict(cfg=c, ncert=nc, R=Rs, viol=bool((Rs > ALPHA).any()), viol_s=Rs > ALPHA,
                         J=float((V[test, c].mean(0) * W).sum()), Vb=V[test, c].mean(0),
                         Ad=float(np.nanmean(A[test, c])), fallback=c == I0))
    out = summarize(rows); out["gap_last_split"] = gap.tolist(); return out


TWIN_METHOD = m_rcsir_fs
res["twin"] = {"Twin, no correction": twin_eval("none"), "Twin, plug-in gap correction": twin_eval("plug-in"),
               "Twin, Hoeffding gap correction (Prop. 1)": twin_eval("hoeffding")}
res["twin_mean_abs_gap_per_slice"] = np.abs(Lt[:, :K] - L[:, :K]).mean(0).max(0).tolist()

# E8 paired comparison RC-SIR vs Slice-FPR (same splits): distribution over calibration draws
def paired(mA, mB, Lx=None, Vx=None, Ax=None, n_cal=N_CAL):
    Lx = L if Lx is None else Lx; Vx = V if Vx is None else Vx; Ax = A if Ax is None else Ax
    rng = np.random.default_rng(SPLIT_SEED); dA, dJ = [], []
    for r in range(R_SPLITS):
        perm = rng.permutation(N); cal, test = np.sort(perm[:n_cal]), np.sort(perm[n_cal:])
        ca, _ = METHODS[mA](Lx, Vx, Ax, cal, rng); cb, _ = METHODS[mB](Lx, Vx, Ax, cal, rng)
        dA.append(np.nanmean(Ax[test, ca]) - np.nanmean(Ax[test, cb]))
        dJ.append(((Vx[test, ca].mean(0) - Vx[test, cb].mean(0)) * W).sum())
    dA, dJ = np.array(dA), np.array(dJ)
    q = lambda v: [float(np.quantile(v, 0.025)), float(np.median(v)), float(np.quantile(v, 0.975))]
    return {"attack_delivered_diff_mean": float(dA.mean()), "attack_delivered_diff_q": q(dA),
            "frac_splits_A_better_attack": float((dA < 0).mean()), "frac_splits_tie_attack": float((dA == 0).mean()),
            "J_diff_mean": float(dJ.mean()), "J_diff_q": q(dJ), "frac_splits_A_better_J": float((dJ < 0).mean()),
            "frac_splits_tie_J": float((dJ == 0).mean())}


res["paired"] = {"RC-SIR vs Slice-FPR": paired("RC-SIR (ours)", "Slice-FPR certified + block"),
                 "RC-SIR vs Pooled LTT": paired("RC-SIR (ours)", "Pooled LTT"),
                 "RC-SIR-FS vs RC-SIR": paired("RC-SIR-FS (ours)", "RC-SIR (ours)"),
                 "RC-SIR-FS vs Slice-FPR": paired("RC-SIR-FS (ours)", "Slice-FPR certified + block"),
                 "RC-SIR-FS vs Pooled LTT": paired("RC-SIR-FS (ours)", "Pooled LTT"),
                 "RC-SIR-FS vs ERM": paired("RC-SIR-FS (ours)", "ERM (no margin)")}
# E9 sensitivity to the budget scale
res["sensitivity"] = {}
_alpha0 = ALPHA.copy()
for scale in (0.5, 1.0, 2.0):
    ALPHA = _alpha0 * scale
    res["sensitivity"][scale] = {m: {k: v for k, v in evaluate(METHODS[m], L, V, A, N, None, R=100).items() if k != "collateral_all"}
                                 for m in ("RC-SIR (ours)", "RC-SIR-FS (ours)", "Slice-FPR certified + block", "ERM (no margin)")}
ALPHA = _alpha0
# E10 computational cost of calibration (wall-clock, this machine)
import time as _time
_rng = np.random.default_rng(0); _cal = np.sort(_rng.permutation(N)[:N_CAL]); _t = []
for _ in range(20):
    t0 = _time.perf_counter(); METHODS["RC-SIR (ours)"](L, V, A, _cal, _rng); _t.append(_time.perf_counter() - t0)
res["cost"] = {"rcsir_calibration_s_median": float(np.median(_t)), "grid_size": K, "n_cal": N_CAL,
               "generate_wallclock_s_4vcpu": float(setup["runtime_s"]),
               "policy_episode_evaluations": int((setup["n"]["pool"] * 3 + setup["n"]["shift"] * 2) * (K + 2)),
               "ms_per_policy_episode_evaluation_4vcpu": float(1e3 * setup["runtime_s"] / ((setup["n"]["pool"] * 3 + setup["n"]["shift"] * 2) * (K + 2)))}

# E5 detector-agnostic check: supervised GBM trained on the benchmark regime
set_grid(setup["taus"]["gbm"])
Lg, Vg, Ag = pool["Lc_g"], pool["Vb_g"], pool["Ad_g"]
res["gbm"] = {m: evaluate(f, Lg, Vg, Ag, N, None) for m, f in
              {"RC-SIR (ours)": METHODS["RC-SIR (ours)"], "Slice-FPR certified + block": make_slice_fpr(slice_fpr_matrix("score_g")),
               "ERM (no margin)": m_erm, "Pooled LTT": m_pooled,
               "Conformal FPR 1% + block": make_fpr("score_g"), "Fixed threshold + block": m_fixed,
               "No action": m_none, "Oracle": m_oracle}.items()}
set_grid(setup["taus"]["iforest"])

# ---------------------------------------------------------------- tables
def fmt(x, d=3): return f"{x:.{d}f}"


def table(block, name, caption, cols=("viol", "coll", "J", "Ad", "fb")):
    hdr = ["Method", "Viol. freq. (±MC s.e.)", "Collateral eMBB", "Collateral URLLC", "Collateral mMTC",
           "Benign viol. J", "Attack delivered", "Fallback"]
    lines = ["| " + " | ".join(hdr) + " |", "|" + "|".join([":--"] + ["--:"] * (len(hdr) - 1)) + "|"]
    tex = []
    for m, r in block.items():
        row = [m, f"{fmt(r['viol_freq'], 3)} ± {fmt(r['viol_freq_mc_se'], 3)}",
               *[fmt(x, 4) for x in r["collateral_mean"]], fmt(r["J_mean"], 4), fmt(r["attack_delivered_mean"], 3),
               fmt(r["fallback_rate"], 2)]
        lines.append("| " + " | ".join(row) + " |")
        tex.append(" & ".join(x.replace("±", r"$\pm$") for x in row) + r" \\")
    md = "\n".join(lines) + f"\n\n: {caption}\n"
    (RES / "tables" / f"{name}.md").write_text(md)
    (RES / "tables" / f"{name}.tex").write_text("\n".join(tex) + "\n")
    return md


tables = {}
cap_main = (f"Main comparison, Isolation-Forest detector, {R_SPLITS} random splits (n_cal = {N_CAL}, n_test = {N - N_CAL}). "
            f"Budgets alpha = (0.05, 0.02, 0.05), delta = {DELTA}. Collateral = mean realised test collateral risk; "
            "viol. freq. = fraction of splits where any slice exceeds its budget (target <= delta for certified methods).")
tables["main"] = table(res["main"], "main", cap_main)
sens_lines = ["| Budget scale | Method | Viol. freq. | Coll. eMBB | Coll. URLLC | Coll. mMTC | Benign viol. J | Attack delivered |", "|--:|:--|--:|--:|--:|--:|--:|--:|"]
for sc_, blk in res["sensitivity"].items():
    for m, r in blk.items():
        sens_lines.append(f"| {sc_} | {m} | {r['viol_freq']:.3f} | " + " | ".join(f"{v:.4f}" for v in r["collateral_mean"]) + f" | {r['J_mean']:.4f} | {r['attack_delivered_mean']:.3f} |")
(RES / "tables" / "sensitivity.md").write_text("\n".join(sens_lines) + "\n\n: Sensitivity to the budget scale (alpha multiplied by the factor; 100 splits each).\n")
tables["gbm"] = table(res["gbm"], "gbm", "Detector-agnostic check with the supervised gradient-boosting detector trained on the benchmark regime (same protocol; probability-threshold grid).")
tables["shift"] = table(res["shift"], "shift", f"Distribution shift: calibrated on nominal-load episodes (load in [0.6, 1.1]), tested on {shift['Lc_i'].shape[0]} high-load episodes (load in [1.1, 1.35]). Last row: recalibration on 200 shifted episodes, tested on the remaining 200.")
tables["twin"] = table(res["twin"], "twin", "Twin-in-the-loop calibration: losses for calibration come from a twin that over-estimates capacity by 8%; realised collateral is measured on the nominal simulator.")
tables["ablation"] = table(res["ablation"], "ablation", "Ablation: multi-action (rate-limit or block per slice) versus block-only policy families.")
ncal_lines = ["| n_cal | Method | Viol. freq. | URLLC collateral | Benign viol. J | Fallback | Median #certified |", "|--:|:--|--:|--:|--:|--:|--:|"]
for n, blk in res["ncal"].items():
    for m, r in blk.items():
        ncal_lines.append(f"| {n} | {m} | {fmt(r['viol_freq'])} | {fmt(r['collateral_mean'][1], 4)} | {fmt(r['J_mean'], 4)} | {fmt(r['fallback_rate'], 2)} | {r['ncert_median']:.0f} |")
tables["ncal"] = "\n".join(ncal_lines) + "\n\n: Effect of calibration-set size (200 splits each).\n"
(RES / "tables" / "ncal.md").write_text(tables["ncal"])
pl = ["| Comparison (A vs B) | Mean diff. attack delivered (A-B) | 2.5% / 50% / 97.5% quantile over splits | A better | Tie | Mean diff. J |", "|:--|--:|--:|--:|--:|--:|"]
for k_, v_ in res["paired"].items():
    q_ = v_["attack_delivered_diff_q"]
    pl.append(f"| {k_} | {v_['attack_delivered_diff_mean']:+.4f} | {q_[0]:+.4f} / {q_[1]:+.4f} / {q_[2]:+.4f} | {v_['frac_splits_A_better_attack']:.3f} | {v_['frac_splits_tie_attack']:.3f} | {v_['J_diff_mean']:+.4f} |")
(RES / "tables" / "paired.md").write_text("\n".join(pl) + "\n\n: Paired comparisons on identical calibration/test splits (200 splits, n_cal = 500). Negative differences favour A.\n")
hl = ["| Slice | Threshold | Action | Acted benign fraction | Collateral | Harm ratio rho |", "|:--|--:|:--|--:|--:|--:|"]
for k_, v_ in res["harm_ratio"].items():
    s_, t_, a_ = k_.split("|")
    hl.append(f"| {s_} | {t_} | {a_} | {v_['acted_benign_frac']:.4f} | {v_['collateral']:.4f} | " + ("--" if v_["rho"] is None else f"{v_['rho']:.3f}") + " |")
(RES / "tables" / "harm_ratio.md").write_text("\n".join(hl) + "\n\n: Measured harm ratio (Proposition 2) for single-slice policies over all 1500 pool episodes.\n")

# ---------------------------------------------------------------- figures
plt.rcParams.update({"font.size": 8, "font.family": "serif", "axes.spines.top": False, "axes.spines.right": False})
show = ["RC-SIR (ours)", "RC-SIR-FS (ours)", "Slice-FPR certified + block", "ERM (no margin)", "Pooled LTT", "Conformal FPR 1% + block", "Fixed threshold + block"]
fig, axs = plt.subplots(1, 3, figsize=(7.2, 2.7), sharey=False)
for s in range(3):
    data = [np.array(res["main"][m]["collateral_all"])[:, s] for m in show]
    axs[s].boxplot(data, showfliers=False, widths=0.6)
    axs[s].axhline(ALPHA[s], color="#b2182b", ls="--", lw=1)
    axs[s].set_title(f"{SL[s]} (budget {ALPHA[s]})"); axs[s].set_xticks(range(1, len(show) + 1))
    axs[s].set_xticklabels(["RC-SIR", "RC-SIR-FS", "Slice-FPR", "ERM", "Pooled", "FPR-1%", "Fixed"], rotation=45, ha="right")
    axs[s].set_yscale("symlog", linthresh=0.01)
axs[0].set_ylabel("Realised test collateral risk")
fig.tight_layout(); [fig.savefig(FIG / f"fig_collateral.{e}", dpi=200) for e in ("pdf", "png")]; plt.close(fig)

fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.4))
ns = list(res["ncal"].keys())
for m, mk in zip(("RC-SIR (ours)", "RC-SIR-FS (ours)", "Slice-FPR certified + block", "ERM (no margin)"), ("o-", "s-", "d-.", "^--")):
    ax[0].plot(ns, [res["ncal"][n][m]["viol_freq"] for n in ns], mk, label=m, ms=3)
    ax[1].plot(ns, [res["ncal"][n][m]["attack_delivered_mean"] for n in ns], mk, label=m, ms=3)
ax[0].axhline(DELTA, color="#b2182b", ls="--", lw=1, label=r"$\delta$"); ax[0].set_xlabel("calibration episodes n"); ax[0].set_ylabel("budget-violation frequency")
ax[1].axhline(res["main"]["No action"]["attack_delivered_mean"], color="gray", ls=":", lw=1, label="No action")
ax[1].set_xlabel("calibration episodes n"); ax[1].set_ylabel("delivered attack fraction"); ax[1].legend(fontsize=6, frameon=False)
fig.tight_layout(); [fig.savefig(FIG / f"fig_ncal.{e}", dpi=200) for e in ("pdf", "png")]; plt.close(fig)

# strip bulky per-split arrays from the JSON except for the main block
for blk in ("gbm", "shift", "twin", "ablation"):
    for m in res[blk]:
        res[blk][m] = {k: v for k, v in res[blk][m].items() if k != "collateral_all"}
(RES / "results.json").write_text(json.dumps(res, indent=1, default=lambda o: o.tolist() if hasattr(o, "tolist") else str(o)))
print(json.dumps({k: {m: (round(v["viol_freq"], 3), [round(x, 4) for x in v["collateral_mean"]], round(v["J_mean"], 4), round(v["fallback_rate"], 2))
                      for m, v in res[k].items()} for k in ("main", "gbm", "shift", "twin", "ablation")}, indent=1))
