"""Spot-check that the cached loss tables are reproducible from the recorded seeds.
Re-trains both detectors exactly as generate.py does, regenerates the first K_CHECK pool episodes,
recomputes their losses and compares with data/losses_pool.npz. Usage: python3 -I code/check_determinism.py
"""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).parent))
import sim
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest

K_CHECK = 6
ROOT = pathlib.Path(__file__).resolve().parent.parent
ss = np.random.SeedSequence(20261102); s_train, s_pool, s_shift, s_model = ss.spawn(4)
train = [sim.gen_episode(np.random.default_rng(s), None, "train") for s in s_train.spawn(600)]
Xtr = np.vstack([sim.features(e) for e in train]); ytr = np.concatenate([e["attacker"] for e in train])
seed = int(s_model.generate_state(1)[0])
gbm = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=seed).fit(Xtr, ytr)
iso = IsolationForest(n_estimators=200, random_state=seed).fit(Xtr[~ytr]); ref = np.sort(-iso.score_samples(Xtr[~ytr]))
TAU_I, ACT = sim.policy_grid((0.9, 0.95, 0.99, 0.995, 0.999)); TAU_G, _ = sim.policy_grid((0.5, 0.7, 0.85, 0.95, 0.99))
stored = np.load(ROOT / "data/losses_pool.npz")
pool_seeds = s_pool.spawn(1500)
worst = 0.0
for i in range(K_CHECK):
    ep = sim.gen_episode(np.random.default_rng(pool_seeds[i]), None)
    f = sim.features(ep)
    si = np.searchsorted(ref, -iso.score_samples(f), side="right") / len(ref)
    sg = gbm.predict_proba(f)[:, 1]
    for key, sc, tau in (("i", si, TAU_I), ("g", sg, TAU_G)):
        Lc, Vb, Ad = sim.episode_losses(ep, sc, tau, ACT)
        worst = max(worst, float(np.abs(Lc.astype(np.float32) - stored[f"Lc_{key}"][i]).max()),
                    float(np.abs(Vb.astype(np.float32) - stored[f"Vb_{key}"][i]).max()))
print(f"max abs difference over {K_CHECK} episodes x 2 detectors x 1333 policies: {worst:.3g}")
assert worst < 1e-6
print("DETERMINISM CHECK PASSED")
