"""Monte Carlo check of Proposition 1 with known true risks.

There are 60 policies with true per-slice risks around the budgets: 20 truly feasible, 40 infeasible
(just above the budget in one slice). Attack delivery is lower for riskier policies, an adversarial
selection objective. Losses are Bernoulli. Over 1500 calibration draws, the selected policy must
violate a budget in at most delta of draws (plus Monte Carlo slack)."""
import pathlib, sys
from types import SimpleNamespace
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "code"))
import methods as M

K = 60
alpha = np.array([0.05, 0.02, 0.05]); delta = 0.1
rng0 = np.random.default_rng(0)
true = np.tile(alpha * 0.5, (K, 1))
bad = np.arange(20, K); slc = rng0.integers(0, 3, len(bad))
true[bad, slc] = alpha[slc] * rng0.uniform(1.02, 1.3, len(bad))       # infeasible, barely
ctx = SimpleNamespace(K=K, I0=K, IOR=K + 1, alpha=alpha, delta=delta, w=np.array([0.3, 0.5, 0.2]))
att = np.r_[np.full(20, 0.6), np.linspace(0.1, 0.3, 40)]               # risky policies mitigate more


def draw(rng, n):
    L = np.zeros((n, K + 2, 3), np.float32)
    L[:, :K, :] = rng.random((n, K, 3)) < true[None]
    V = np.zeros((n, K + 2, 3), np.float32)
    A = np.tile(np.r_[att, 0.96, 0.0][None], (n, 1)).astype(np.float32)
    return L, V, A


def _run(fn, n=500, R=1500):
    rng = np.random.default_rng(1); viol = 0
    for _ in range(R):
        L, V, A = draw(rng, n)
        c, _ = fn(ctx, L, V, A, np.arange(n), rng)
        viol += c < K and (true[c] > alpha).any()
    return viol / R


def test_rcsir_fs_valid():
    f = _run(M.rcsir_fs); assert f <= delta + 0.025, f


def test_rcsir_bonferroni_valid():
    f = _run(M.rcsir); assert f <= delta + 0.025, f


def test_erm_is_not_valid_here():
    """Sanity check that the test has power: ERM picks risky policies often."""
    f = _run(M.erm); assert f > 0.3, f
