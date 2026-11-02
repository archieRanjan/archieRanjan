"""methods.py must reproduce the v1 published numbers (results/results.json) exactly."""
import json, pathlib, sys
import numpy as np
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import methods as M


def _eval(fn, L, V, A, N, R=200, n_cal=500, seed=7):
    rng = np.random.default_rng(seed); ad = []
    for _ in range(R):
        perm = rng.permutation(N); cal, test = np.sort(perm[:n_cal]), np.sort(perm[n_cal:])
        c, _ = fn(L, V, A, cal, rng)
        ad.append(float(np.nanmean(A[test, c])))
    return float(np.mean(ad))


def test_reproduces_v1_main_results():
    pool = np.load(ROOT / "data/losses_pool.npz"); res = json.loads((ROOT / "results/results.json").read_text())
    ctx = M.Ctx(taus=(0.9, 0.95, 0.99, 0.995, 0.999))
    L, V, A = pool["Lc_i"], pool["Vb_i"], pool["Ad_i"]; N = L.shape[0]
    F = M.fpr_matrix(ctx, pool["score_i"], pool["label"], pool["slice"], pool["ep_index"], N)
    checks = {"RC-SIR-FS (ours)": lambda L, V, A, cal, rng: M.rcsir_fs(ctx, L, V, A, cal, rng),
              "RC-SIR (ours)": lambda L, V, A, cal, rng: M.rcsir(ctx, L, V, A, cal, rng),
              "Slice-FPR certified + block": lambda L, V, A, cal, rng: M.slice_fpr(ctx, F, cal, 1),
              "ERM (no margin)": lambda L, V, A, cal, rng: M.erm(ctx, L, V, A, cal, rng),
              "Pooled LTT": lambda L, V, A, cal, rng: M.pooled(ctx, L, V, A, cal, rng, np.array([14, 10, 16]))}
    for name, fn in checks.items():
        assert abs(_eval(fn, L, V, A, N) - res["main"][name]["attack_delivered_mean"]) < 1e-9, name
