"""Stage 1: train the detectors and build the per-episode loss tables (cached in ../data/).

Deterministic: every random stream derives from MASTER_SEED.
Usage: python3 -I generate.py   (≈30 min on 4 cores)
"""
import json, pathlib, sys, time
from multiprocessing import Pool
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, IsolationForest
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import sim

MASTER_SEED = 20261102
N_TRAIN, N_POOL, N_SHIFT = 600, 1500, 400
TWIN_CAPACITY = 1.08            # the "twin" over-estimates egress capacity by 8%
OUT = pathlib.Path(__file__).resolve().parent.parent / "data"
OUT.mkdir(exist_ok=True)
ss = np.random.SeedSequence(MASTER_SEED)
s_train, s_pool, s_shift, s_model = ss.spawn(4)


def make_eps(seedseq, n, load_range=None, regime="deploy"):
    rngs = [np.random.default_rng(s) for s in seedseq.spawn(n)]
    eps = []
    for r in rngs:
        load = None if load_range is None else r.uniform(*load_range)
        eps.append(sim.gen_episode(r, load, regime))
    return eps


# ---------------------------------------------------------------- detectors
t0 = time.time()
train = make_eps(s_train, N_TRAIN, regime="train")   # detector trained on the benchmark regime
Xtr = np.vstack([sim.features(e) for e in train]); ytr = np.concatenate([e["attacker"] for e in train])
seed_model = int(s_model.generate_state(1)[0])
gbm = HistGradientBoostingClassifier(max_iter=200, learning_rate=0.1, random_state=seed_model).fit(Xtr, ytr)
iso = IsolationForest(n_estimators=200, random_state=seed_model).fit(Xtr[~ytr])
ref = -iso.score_samples(Xtr[~ytr])                  # benign training anomaly scores
ref.sort()


def iso_score(X):  # empirical CDF of training-benign anomaly scores -> [0, 1]
    return np.searchsorted(ref, -iso.score_samples(X), side="right") / len(ref)


TAUS_G = (0.5, 0.7, 0.85, 0.95, 0.99)                 # GBM probability thresholds
TAUS_I = (0.9, 0.95, 0.99, 0.995, 0.999)              # Isolation-Forest benign-quantile thresholds
TAU_G, ACT = sim.policy_grid(TAUS_G)
TAU_I, _ = sim.policy_grid(TAUS_I)
K = len(TAU_G)


def work(args):
    ep, sc_g, sc_i, twin = args
    out = {}
    out["g"] = sim.episode_losses(ep, sc_g, TAU_G, ACT)
    if sc_i is not None:
        out["i"] = sim.episode_losses(ep, sc_i, TAU_I, ACT)
    if twin:
        out["t"] = sim.episode_losses(ep, sc_i, TAU_I, ACT, capacity_scale=TWIN_CAPACITY)
    return out


def build(eps, with_iso, with_twin, tag):
    feats = [sim.features(e) for e in eps]
    sg = [gbm.predict_proba(f)[:, 1] for f in feats]
    si = [iso_score(f) for f in feats] if with_iso else [None] * len(eps)
    with Pool(4) as p:
        res = p.map(work, [(e, a, b, with_twin) for e, a, b in zip(eps, sg, si)], chunksize=4)
    arrs = {}
    for key in res[0]:
        arrs[f"Lc_{key}"] = np.stack([r[key][0] for r in res]).astype(np.float32)
        arrs[f"Vb_{key}"] = np.stack([r[key][1] for r in res]).astype(np.float32)
        arrs[f"Ad_{key}"] = np.stack([r[key][2] for r in res]).astype(np.float32)
    lab = np.concatenate([e["attacker"] for e in eps]); slc = np.concatenate([e["slice"] for e in eps])
    np.savez_compressed(OUT / f"losses_{tag}.npz", **arrs,
                        load=np.array([e["load"] for e in eps]),
                        has_attack=np.array([e["attacker"].any() for e in eps]),
                        n_attackers=np.array([e["attacker"].sum() for e in eps]),
                        score_g=np.concatenate(sg), score_i=np.concatenate(si) if with_iso else np.array([]),
                        label=lab, slice=slc, ep_index=np.concatenate([[i] * len(e["slice"]) for i, e in enumerate(eps)]))
    return lab, slc, np.concatenate(sg), (np.concatenate(si) if with_iso else None)


pool = make_eps(s_pool, N_POOL)
lab, slc, sg, si = build(pool, True, True, "pool")
shift = make_eps(s_shift, N_SHIFT, load_range=(1.1, 1.35))
lab_s, slc_s, sg_s, si_s = build(shift, True, False, "shift")

det = {"train_ues": int(len(ytr)), "train_attackers": int(ytr.sum())}
for name, s in (("gbm", sg), ("iforest", si)):
    det[name] = {"auc_pool": float(roc_auc_score(lab, s)),
                 "fpr_at_0.5_per_slice": [float((s[(~lab) & (slc == k)] >= 0.5).mean()) for k in range(3)],
                 "tpr_at_0.5_per_slice": [float((s[lab & (slc == k)] >= 0.5).mean()) if (lab & (slc == k)).any() else None for k in range(3)],
                 "per_threshold": {str(th): {"fpr": [float((s[(~lab) & (slc == k)] >= th).mean()) for k in range(3)],
                                             "tpr": [float((s[lab & (slc == k)] >= th).mean()) for k in range(3)]}
                                   for th in (TAUS_G if name == "gbm" else TAUS_I)}}
det["gbm"]["auc_shift"] = float(roc_auc_score(lab_s, sg_s))
det["iforest"]["auc_shift"] = float(roc_auc_score(lab_s, si_s))
det["taus"] = {"gbm": TAUS_G, "iforest": TAUS_I}
det["traffic_model_version"] = "v2 (train/deploy regimes)"
det["grid_size"] = K
det["params"] = {k: (list(v) if isinstance(v, tuple) else v) for k, v in sim.PARAMS.items()}
det["master_seed"] = MASTER_SEED; det["twin_capacity"] = TWIN_CAPACITY
det["n"] = {"train": N_TRAIN, "pool": N_POOL, "shift": N_SHIFT}
det["runtime_s"] = time.time() - t0
(OUT / "detector_and_setup.json").write_text(json.dumps(det, indent=2))
print(json.dumps(det, indent=2))
