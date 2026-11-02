# Experimental design log (disclosed in the paper, Section "Threats to validity")

All entries are in chronological order. Nothing here was changed after looking at the v2 results.

## v1 (2026-11-02, archived in `data_v1/`)
- Simulator `sim.py` v1. A single traffic regime was used for both detector training and evaluation. Attackers had distinct packet sizes. The detector was a GBM.
- **Outcome:** GBM deployment AUC = 0.99999 (`data_v1/detector_and_setup.json`). Every method, including uncalibrated baselines, met every budget with negligible collateral (`data_v1/results_v1.json`).
- **Diagnosis:** the evaluation could not discriminate between methods, because the detection task was trivially separable. This mirrors the near-perfect accuracies reported on public 5G NIDS benchmarks (5G-NIDD, SliceSecure), which the literature attributes to benchmark artefacts.
- **Decision:** v1 is not reported as a result. It is disclosed here and in the paper.

## v2 (2026-11-02, the configuration reported in the paper)
Changes were motivated by documented NIDS failure modes: cross-domain degradation (Layeghy & Portmann 2023) and benchmark design smells (Flood et al. 2024). Only *detector diagnostics* were used to accept v2, never method outcomes.

1. **Separate regimes.** The detector is trained on a *benchmark regime* (v1-like traffic). It is deployed and evaluated on a *deployment regime* with:
    - more heavy eMBB users, with more variable rates;
    - URLLC event-driven alarm bursts and mMTC firmware-update bursts;
    - attackers that mimic their slice's packet size in 70% of cases;
    - an unseen low-and-slow attack class.
2. **Shorter observation window:** 30 steps instead of 60.
3. **Primary detector:** unsupervised Isolation Forest (trained on benign benchmark-regime traffic; score = benign-training quantile). Pilot diagnostics (300 vs. 300 episodes, seed 123): deployment AUC 0.89, and per-slice FPR at the 0.95 quantile was (0.13, 0.08, 0.0002).
4. **Secondary detector:** supervised GBM trained on the benchmark regime. Pilot deployment AUC 0.72; its scores are saturated (the thresholds from 0.5 to 0.99 behave almost identically). It is retained as a detector-agnostic check.
5. **Threshold grid for the Isolation Forest:** (0.9, 0.95, 0.99, 0.995, 0.999).

The budgets α = (0.05, 0.02, 0.05), δ = 0.1, weights w = (0.3, 0.5, 0.2), n_cal = 500, and 200 splits were all fixed **before** any v1 or v2 method results were computed, and were not changed.
