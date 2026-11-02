import json, pathlib, sys
import yaml
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "code"))
import sim

CFG = yaml.safe_load((ROOT / "configs/experiment_config.yaml").read_text())


def test_sim_params_match_config():
    for k, v in CFG["sim"].items():
        got = sim.PARAMS[k]
        assert (list(got) if isinstance(got, tuple) else got) == v, k


def test_recorded_setup_matches_config():
    setup = json.loads((ROOT / "data/detector_and_setup.json").read_text())
    assert setup["master_seed"] == CFG["master_seed"]
    assert setup["n"] == CFG["n_episodes"]
    assert setup["twin_capacity"] == CFG["twin_capacity_scale"]
    assert [list(setup["taus"][k]) for k in ("iforest", "gbm")] == [CFG["thresholds"][k] for k in ("iforest", "gbm")]


def test_results_match_config():
    r = json.loads((ROOT / "results/results.json").read_text())
    assert r["alpha"] == CFG["alpha"] and r["delta"] == CFG["delta"] and r["n_cal"] == CFG["n_cal"]
    assert r["R_splits"] == CFG["splits"] and r["objective"] == CFG["selection_objective"]


def test_no_episode_overlap_between_calibration_and_test():
    """Splits are permutations of distinct episode indices: calibration and test never share an episode."""
    import numpy as np
    rng = np.random.default_rng(CFG["split_seed"])
    for _ in range(50):
        perm = rng.permutation(CFG["n_episodes"]["pool"])
        cal, test = set(perm[:CFG["n_cal"]]), set(perm[CFG["n_cal"]:])
        assert not cal & test and len(cal | test) == CFG["n_episodes"]["pool"]
