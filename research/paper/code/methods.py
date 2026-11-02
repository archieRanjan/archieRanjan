"""Standalone implementations of the certification methods, frozen as in experiments.py at commit d5518c3.
tests/test_methods_consistency.py checks that they reproduce results/results.json (v1 study) exactly.

All functions take a Ctx describing the policy grid. Loss arrays are Lc (N,K+2,3), Vb (N,K+2,3), Ad (N,K+2);
the last two policy indices are pi_0 and the oracle.
"""
from dataclasses import dataclass, field
import numpy as np
from riskcontrol import hb_pvalue


@dataclass
class Ctx:
    taus: tuple
    actions: tuple = (0, 1)              # per-slice action codes in the grid
    alpha: np.ndarray = field(default_factory=lambda: np.array([0.05, 0.02, 0.05]))
    delta: float = 0.10
    w: np.ndarray = field(default_factory=lambda: np.array([0.3, 0.5, 0.2]))

    def __post_init__(self):
        per = [(np.inf, self.actions[0])] + [(t, a) for t in self.taus for a in self.actions]
        self.per = per
        self.grid = [(per[i], per[j], per[k]) for i in range(11) for j in range(11) for k in range(11)]
        self.K = len(self.grid); self.I0 = self.K; self.IOR = self.K + 1
        self.same = [c for c in range(self.K) if self.grid[c][0] == self.grid[c][1] == self.grid[c][2]]
        self.index = {g: i for i, g in enumerate(self.grid)}


def sel_obj(ctx, Vb, Ad, idx):
    J = (Vb[idx, :ctx.K].mean(0) * ctx.w).sum(-1)
    with np.errstate(invalid="ignore"):
        a = np.nanmean(Ad[idx, :ctx.K], 0)
    return np.nan_to_num(a, nan=0.0) + 1e-3 * J


def _select(ctx, cert, J):
    idx = np.flatnonzero(cert)
    return int(idx[np.argmin(J[idx])]) if len(idx) else ctx.I0


def rcsir(ctx, Lc, Vb, Ad, cal, rng, alpha=None):
    alpha = ctx.alpha if alpha is None else alpha
    if np.any(alpha <= 0):
        return ctx.I0, 0
    R = Lc[cal, :ctx.K].mean(0)
    p = hb_pvalue(R, alpha[None, :], len(cal)).max(1)
    cert = p <= ctx.delta / ctx.K
    return _select(ctx, cert, sel_obj(ctx, Vb, Ad, cal)), int(cert.sum())


def rcsir_fs(ctx, Lc, Vb, Ad, cal, rng, alpha=None):
    alpha = ctx.alpha if alpha is None else alpha
    if np.any(alpha <= 0):
        return ctx.I0, 0
    perm = rng.permutation(cal); a, b = perm[: len(cal) // 2], perm[len(cal) // 2:]
    Ra = Lc[a, :ctx.K].mean(0); Jall = sel_obj(ctx, Vb, Ad, cal)
    order = np.lexsort((sel_obj(ctx, Vb, Ad, a), (Ra / alpha).max(1)))
    p = hb_pvalue(Lc[b, :ctx.K].mean(0), alpha[None, :], len(b)).max(1)
    cert = np.zeros(ctx.K, bool)
    for c in order:
        if p[c] <= ctx.delta:
            cert[c] = True
        else:
            break
    return _select(ctx, cert, Jall), int(cert.sum())


def erm(ctx, Lc, Vb, Ad, cal, rng):
    R = Lc[cal, :ctx.K].mean(0); ok = (R <= ctx.alpha).all(1)
    return _select(ctx, ok, sel_obj(ctx, Vb, Ad, cal)), int(ok.sum())


def pooled(ctx, Lc, Vb, Ad, cal, rng, n_ben):
    pooledL = (Lc[cal, :ctx.K] * n_ben).sum(-1) / n_ben.sum()
    a_pool = float((ctx.alpha * n_ben).sum() / n_ben.sum())
    fam = np.array(ctx.same)
    p = hb_pvalue(pooledL[:, fam].mean(0), a_pool, len(cal))
    cert = np.zeros(ctx.K, bool); cert[fam] = p <= ctx.delta / len(fam)
    return _select(ctx, cert, sel_obj(ctx, Vb, Ad, cal)), int(cert.sum())


def fpr_matrix(ctx, score, label, slc, ep_index, N):
    F = np.zeros((N, 3, len(ctx.taus)))
    for s in range(3):
        m = (~label) & (slc == s)
        cnt = np.bincount(ep_index[m], minlength=N)
        for j, t in enumerate(ctx.taus):
            F[:, s, j] = np.bincount(ep_index[m], weights=(score[m] >= t).astype(float), minlength=N) / np.maximum(cnt, 1)
    return F


def slice_fpr(ctx, F, cal, action):
    """Per-slice certified FPR (fixed sequence over decreasing thresholds, Bonferroni over slices)."""
    chosen = []
    for s in range(3):
        pick = (np.inf, ctx.actions[0])
        for j in reversed(range(len(ctx.taus))):
            if hb_pvalue(F[cal, s, j].mean(), ctx.alpha[s], len(cal)) <= ctx.delta / 3:
                pick = (ctx.taus[j], action)
            else:
                break
        chosen.append(pick)
    return ctx.index[tuple(chosen)], 1
