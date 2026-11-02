# Data provenance

**No external dataset is used.** All data are synthetic and produced by `code/generate.py` from master seed 20261102 using independent `numpy.random.SeedSequence` streams.

| Stream | Episodes | Regime | Use |
|---|---|---|---|
| train | 600 | benchmark (`regime="train"`) | Detector training only (never calibration or test) |
| pool | 1500 | deployment | Calibration/test splits (disjoint within each split) |
| shift | 400 | deployment, load factor in [1.1, 1.35] | Load-shift test; recalibration experiment |
| model | — | — | Random state of the detectors |

**Files (`data/`):**

| File | Contents |
|---|---|
| `losses_pool.npz` | Per-episode loss tables for both detectors and the twin: `Lc_*` (N, 1333, 3), `Vb_*` (N, 1333, 3), `Ad_*` (N, 1333). The last two policies are π_0 and the oracle. Also per-UE scores, labels, slice ids and episode index. |
| `losses_shift.npz` | The same tables for the shift stream (Isolation Forest and GBM; no twin). |
| `detector_and_setup.json` | Detector diagnostics (AUC, per-slice FPR/TPR per threshold), all simulator parameters, seed, runtime. |
| `results_J_objective.json` | Archived analysis that used the incorrect J selection objective (see `research_decisions.md`, R-07). |

`data_v1/` holds the rejected v1 simulator outputs (see `DESIGN_LOG.md`).

**Leakage controls:**
- Detector features use only the observation window (unit test `test_features_use_observation_window_only`).
- Training episodes come from a separate seed stream and regime.
- Calibration and test episodes are disjoint in every split (`test_no_episode_overlap_between_calibration_and_test`).
- Collateral and attack outcomes are measured only in the action window.

**Integrity:** `code/check_determinism.py` regenerates sample episodes from the seeds and matches the stored tables exactly (`logs/determinism_check.log`).

## Confirmatory data (`data_confirm/`, Studies C and N; ANALYSIS_PLAN_v2.md)

| File | Contents |
|---|---|
| `C_rep{1..8}.npz` / `.json` | One independent replication each (master seed 3000 + r). The scenario is drawn from the seed; a fresh Isolation Forest is trained on 600 benchmark-regime episodes; 1500 deployment episodes. Arrays `Lc`, `Vb`, `Ad` cover 1331 policies plus π_0 and the oracle, with actions {rate-limit, block}. |
| `N.npz` / `.json` | Seed 4001, base scenario, actions {block, redirect} (`sim_ext`); additionally `Fa` (acted-benign fraction per policy) |

These seeds were never used before the plan was committed.
