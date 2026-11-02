# Contribution–evidence matrix

| Contribution (as claimed in the manuscript) | Type | Evidence | Location | Strength |
|---|---|---|---|---|
| Definition of action-induced collateral against the π_0 counterfactual | Formulation | Definition 1; implemented in `sim.episode_losses` | paper §3; code | Definition (no empirical claim) |
| Lemma 1: collateral ≤ acted-benign fraction under A3 | Theory | Proof (paper §3); unit test `test_lemma1_actions_never_harm_non_acted_ues`; exhaustive pool check (max excess 2.6e-8) | `results.json: lemma1_check` | Proven under A3; A3 verified only for this simulator |
| Remark 1: the harm ratio is the only deterministic source of gain | Analysis (identity) | Harm-ratio table; budget sensitivity | `results/tables/harm_ratio.md`, `sensitivity.md` | Identity; prediction partially confirmed (the gain came via the statistical margin) |
| Proposition 1: validity of RC-SIR / RC-SIR-FS | Theory (follows from LTT) | Proof; 0 violations in 200 splits at all n | `main.md`, `ncal.md` | Proven; consistent empirically (not a tightness test) |
| Corollary 1: per-slice FPR certification is a collateral certificate | Theory | Lemma 1 + LTT; 0 violations | `main.md` | Proven under A3 |
| Proposition 2: twin transfer | Theory | Proof; experiment shows the rigorous ε̂ makes it vacuous at m = 300 | `twin.md` | Proven, but impractical as tested (negative) |
| Direct certification (FS) beats Slice-FPR at nominal budgets | Empirical | 0.417 vs 0.458 attack delivered; better in 93.5% of paired splits | `main.md`, `paired.md` | Simulation only; conditional |
| No advantage at small n, other budgets, or with Bonferroni | Empirical (negative) | n-sweep, sensitivity, paired RC-SIR vs Slice-FPR | `ncal.md`, `sensitivity.md`, `paired.md` | Simulation only |
| Uncalibrated selection violates budgets | Empirical | ERM 25.5% (n = 100), 10% (n = 500) | `ncal.md`, `main.md` | Simulation only |
| Multi-action policies give no measurable benefit | Empirical (negative) | 0.417 vs 0.418 | `ablation.md` | Simulation only |
| Calibration cost negligible; replay dominates | Empirical | 3.8 ms selection; 0.12 ms per policy-episode replay (fluid model, 4 vCPU) | `results.json: cost` | Machine-specific |
