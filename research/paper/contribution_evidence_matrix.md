# Contribution–evidence matrix (revised after the confirmatory studies)

| Claim in the revised manuscript | Type | Evidence | Strength |
|---|---|---|---|
| Collateral definition against the π_0 counterfactual | Formulation | Definition 1; `sim.episode_losses` | Definition |
| Theorem 1: the implemented scheduler is monotone under traffic-removing actions | Theory | Proof (Appendix A, `proof_audit.md`); unit test; exhaustive pool check | Proven for the model; not for real UPFs |
| Lemma 1 / Corollary 1: FPR certification bounds collateral | Theory | Follows from Theorem 1; 0 large-sample invalid policies in the monotone study | Proven under Theorem 1's conditions |
| Proposition 0: relocating actions break Lemma 1, including across slices | Theory (construction) + data | Unit test; Study N: excess in 1.0% of entries, max 0.93; cross-slice URLLC harm | Shown by construction and in simulation |
| Proposition 1: validity of RC-SIR / RC-SIR-FS | Theory (LTT corollary) | Proof; known-risk Monte Carlo (0.07% vs δ = 10%); 0 / 400 and 0 / 200 confirmatory violations | Proven; empirically consistent (not a tightness test) |
| Direct certification improves mitigation over FPR certification | Empirical | **Not confirmed** (Study C: −0.030 [−0.071, +0.011]) | Negative / inconclusive |
| The gain depends on the margin band (Remark 1) | Empirical, post hoc | Spearman −0.85 over 8 replications | Exploratory only |
| Under relocation the FPR criterion accepts over-budget policies | Empirical, post hoc | 31 / 441 in the large-sample analysis; 0 finite-sample violations | Exploratory; small magnitude (≤ 0.0044) |
| Direct certification remains valid under relocation | Empirical, pre-registered | Study N, 0 / 200 | Supported (simulation) |
| Bonferroni direct certification is worse than FPR certification | Empirical, pre-registered secondary | +0.051 [+0.009, +0.092] | Supported (simulation) |
| A guarantee costs mitigation when budgets are slack | Empirical, pre-registered secondary | FS − ERM = +0.052 [+0.011, +0.093] | Supported (simulation) |
| Twin transfer | Theory | Proposition 2 is valid but vacuous at m = 300 | Negative |
