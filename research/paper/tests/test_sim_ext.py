import pathlib, sys
import numpy as np
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "code"))
import sim, sim_ext


def test_ext_reproduces_base_simulator_without_redirect():
    rng = np.random.default_rng(21)
    for _ in range(5):
        ep = sim.gen_episode(rng); U = len(ep["slice"])
        acts = rng.integers(-1, 2, (30, U))
        V0, A0 = sim.evaluate_policies(ep, np.zeros(U), np.full((0, 3), np.inf), np.zeros((0, 3), int), extra_actions=acts)
        V1, A1 = sim_ext.evaluate_policies_ext(ep, np.zeros(U), np.full((0, 3), np.inf), np.zeros((0, 3), int), extra_actions=acts)
        assert np.array_equal(V0, V1)
        assert np.allclose(np.nan_to_num(A0), np.nan_to_num(A1), atol=1e-9)


def test_redirect_can_harm_non_acted_ues():
    """Hand-built counterexample to A3: redirecting a benign eMBB UE (30 units/slot) puts its traffic
    on the shared link twice (scrub class + hairpin return). Total offered load rises from 96 to 126
    units on a 100-unit link, and the non-acted URLLC UE (40 units/slot, borrowing beyond its
    guarantee of 25) is pushed into violation. This is cross-slice harm from an action on another slice."""
    P = sim.PARAMS; T = P["T_OBS"] + P["T_ACT"]
    D = np.zeros((3, T)); D[0] = 30.0; D[1] = 26.0; D[2] = 40.0      # two heavy eMBB UEs + URLLC load
    ep = dict(D=D, slice=np.array([0, 0, 1]), attacker=np.zeros(3, bool), psize=np.zeros(3), load=1.0)
    acts = np.array([[-1, -1, -1], [2, -1, -1]])
    V, _ = sim_ext.evaluate_policies_ext(ep, np.zeros(3), np.full((0, 3), np.inf), np.zeros((0, 3), int), extra_actions=acts)
    # UE 2 (URLLC) is never acted on: fine without action, violated when UE 0 is redirected
    assert not V[0, 2] and V[1, 2]
    assert not V[0, 1] and not V[1, 1]
