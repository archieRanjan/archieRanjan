"""Generate data for the pre-registered confirmatory studies (ANALYSIS_PLAN_v2.md).

Study C: 8 independent replications (master seeds 3001..3008). Each has a scenario drawn from its
         seed, a freshly trained Isolation-Forest detector, and a 1500-episode deployment pool.
         Actions are {rate-limit, block}, as in the main study.
Study N: master seed 4001, base scenario, actions {block, redirect} (sim_ext).
Outputs: ../data_confirm/C_rep{r}.npz, ../data_confirm/N.npz, plus *.json with the scenario and
detector diagnostics.
Usage: python3 -I confirm_generate.py [C|N|all]
"""
import copy, json, pathlib, sys, time
from multiprocessing import Pool
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

sys.path.insert(0, str(pathlib.Path(__file__).parent))
import sim, sim_ext

OUT = pathlib.Path(__file__).resolve().parent.parent / "data_confirm"; OUT.mkdir(exist_ok=True)
BASE = copy.deepcopy(sim.PARAMS)
TAUS_I = (0.9, 0.95, 0.99, 0.995, 0.999)
N_TRAIN, N_POOL = 600, 1500


def draw_scenario(rng):
    g = np.asarray(BASE["g"]) * rng.uniform(0.85, 1.15, 3); g = g / g.sum()
    c = rng.uniform(0.75, 0.95)
    return dict(n_ue=tuple(int(round(n * rng.uniform(0.75, 1.25))) for n in BASE["n_ue"]),
                p_attack=float(rng.uniform(0.4, 0.8)), g=tuple(float(x) for x in g),
                buf=tuple(float(b * rng.uniform(0.75, 1.25)) for b in BASE["buf"]),
                attack_slice_p=tuple(float(x) for x in rng.dirichlet((4.5, 1.5, 4.0))),
                load_range=(float(c - 0.25), float(c + 0.25)))


def set_params(scen):
    sim.PARAMS.clear(); sim.PARAMS.update(copy.deepcopy(BASE))
    if scen:
        sim.PARAMS.update({k: v for k, v in scen.items() if k != "load_range"})


def make_eps(seedseq, n, regime, load_range):
    out = []
    for s in seedseq.spawn(n):
        r = np.random.default_rng(s)
        out.append(sim.gen_episode(r, r.uniform(*load_range), regime))
    return out


def grid(actions):
    per = [(np.inf, actions[0])] + [(t, a) for t in TAUS_I for a in actions]
    T = np.array([[per[i][0], per[j][0], per[k][0]] for i in range(11) for j in range(11) for k in range(11)])
    A = np.array([[per[i][1], per[j][1], per[k][1]] for i in range(11) for j in range(11) for k in range(11)])
    return T, A


def work(args):
    ep, sc, scen, mode = args
    set_params(scen)
    if mode == "C":
        T, A = grid((0, 1))
        Lc, Vb, Ad = sim.episode_losses(ep, sc, T, A)
        return Lc, Vb, Ad, None
    T, A = grid((1, 2))
    return sim_ext.episode_losses_ext(ep, sc, T, A)


def run(seed, scen, mode, tag):
    t0 = time.time()
    set_params(scen)
    lr = scen["load_range"] if scen else (0.6, 1.1)
    ss = np.random.SeedSequence(seed); _, s_train, s_pool, s_model = ss.spawn(4)
    train = make_eps(s_train, N_TRAIN, "train", lr)
    Xtr = np.vstack([sim.features(e) for e in train]); ytr = np.concatenate([e["attacker"] for e in train])
    iso = IsolationForest(n_estimators=200, random_state=int(s_model.generate_state(1)[0])).fit(Xtr[~ytr])
    ref = np.sort(-iso.score_samples(Xtr[~ytr]))
    pool = make_eps(s_pool, N_POOL, "deploy", lr)
    scores = [np.searchsorted(ref, -iso.score_samples(sim.features(e)), side="right") / len(ref) for e in pool]
    with Pool(4) as p:
        res = p.map(work, [(e, s, scen, mode) for e, s in zip(pool, scores)], chunksize=4)
    lab = np.concatenate([e["attacker"] for e in pool]); slc = np.concatenate([e["slice"] for e in pool])
    sc = np.concatenate(scores)
    arrs = dict(Lc=np.stack([r[0] for r in res]).astype(np.float32), Vb=np.stack([r[1] for r in res]).astype(np.float32),
                Ad=np.stack([r[2] for r in res]).astype(np.float32), score=sc, label=lab, slice=slc,
                ep_index=np.concatenate([[i] * len(e["slice"]) for i, e in enumerate(pool)]),
                has_attack=np.array([e["attacker"].any() for e in pool]), load=np.array([e["load"] for e in pool]))
    if mode == "N":
        arrs["Fa"] = np.stack([r[3] for r in res]).astype(np.float32)
    np.savez_compressed(OUT / f"{tag}.npz", **arrs)
    meta = dict(seed=seed, mode=mode, scenario=scen, taus=TAUS_I, n_train=N_TRAIN, n_pool=N_POOL,
                auc=float(roc_auc_score(lab, sc)), attack_episode_frac=float(arrs["has_attack"].mean()),
                runtime_s=time.time() - t0)
    (OUT / f"{tag}.json").write_text(json.dumps(meta, indent=1))
    print(tag, json.dumps({k: meta[k] for k in ("auc", "attack_episode_frac", "runtime_s")}), flush=True)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("N", "all"):
        run(4001, None, "N", "N")
    if which in ("C", "all"):
        for r in range(1, 9):
            seed = 3000 + r
            scen = draw_scenario(np.random.default_rng(np.random.SeedSequence(seed).spawn(4)[0]))
            run(seed, scen, "C", f"C_rep{r}")
