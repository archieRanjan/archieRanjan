"""Unit and integration tests. Run: python3 -m pytest -q tests  (from research/paper)."""
import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "code"))
import sim
from riskcontrol import hb_pvalue


def test_hb_pvalue_is_valid_under_null():
    """Under H0 (true risk slightly above alpha) the rejection rate at level d must be <= d."""
    rng = np.random.default_rng(0); alpha, d, n = 0.05, 0.1, 300
    rej = [hb_pvalue(rng.binomial(1, alpha + 0.005, n).mean(), alpha, n) <= d for _ in range(4000)]
    assert np.mean(rej) <= d


def test_hb_pvalue_has_power_when_risk_small():
    rng = np.random.default_rng(1)
    rej = [hb_pvalue(rng.binomial(1, 0.005, 500).mean(), 0.05, 500) <= 0.1 for _ in range(500)]
    assert np.mean(rej) > 0.95


def test_policy_grid():
    T, A = sim.policy_grid((0.9, 0.95, 0.99, 0.995, 0.999))
    assert T.shape == (1331, 3)
    assert len({tuple(r) for r in np.column_stack([T, A])}) == 1331


def test_episode_determinism():
    a = sim.gen_episode(np.random.default_rng(5)); b = sim.gen_episode(np.random.default_rng(5))
    assert np.array_equal(a["D"], b["D"]) and np.array_equal(a["attacker"], b["attacker"])


def test_features_use_observation_window_only():
    ep = sim.gen_episode(np.random.default_rng(3)); f0 = sim.features(ep)
    ep2 = dict(ep); ep2["D"] = ep["D"].copy(); ep2["D"][:, sim.PARAMS["T_OBS"]:] *= 7.0
    assert np.allclose(f0, sim.features(ep2))


def test_scheduler_conservation():
    rng = np.random.default_rng(2); C = 100.0; gC = np.array(sim.PARAMS["g"]) * C
    avail = rng.uniform(0, 120, (500, 3)); srv = sim._serve(avail, C, gC)
    assert np.all(srv <= avail + 1e-9) and np.all(srv.sum(1) <= C + 1e-6)
    # work conservation: capacity is not left idle while some slice still has demand
    idle = C - srv.sum(1); unmet = (avail - srv).sum(1)
    assert np.all((idle < 1e-6) | (unmet < 1e-6))


def test_lemma1_actions_never_harm_non_acted_ues():
    """Lemma 1 (monotonicity), checked numerically: removing traffic of acted UEs never turns a
    non-acted UE's SLA from satisfied to violated."""
    rng = np.random.default_rng(11)
    for _ in range(25):
        ep = sim.gen_episode(rng); U = len(ep["slice"])
        acts = -np.ones((40, U), int)
        for k in range(40):
            m = rng.random(U) < 0.3; acts[k, m] = rng.integers(0, 2, m.sum())
        V, _ = sim.evaluate_policies(ep, np.zeros(U), np.full((0, 3), np.inf), np.zeros((0, 3), int),
                                     extra_actions=np.vstack([-np.ones((1, U), int), acts]))
        V0 = V[0]
        for k in range(40):
            non_acted = acts[k] == -1
            assert not np.any(V[k + 1][non_acted] & ~V0[non_acted])


def test_seed_streams_disjoint():
    ss = np.random.SeedSequence(20261102); a, b, c, d = ss.spawn(4)
    assert len({tuple(x.generate_state(4)) for x in (a, b, c, d)}) == 4
