# Frozen confirmatory analysis plan (v2)

Written and committed **before** any confirmatory data were generated. It responds to the external audit of 2 November 2026: post-hoc selection, a single shared episode pool, an unproven A3, missing non-monotone settings, and the test-set metric.

Nothing below may be changed after the confirmatory runs start. Deviations will be reported as deviations.

## Frozen method
- **Primary method:** RC-SIR-FS (fixed-sequence LTT, ordering from half D1, union-null HB p-values), exactly as in `code/experiments.py` at this commit.
- **Selection objective:** delivered attack fraction, with tie-breaker 1e-3·J.
- **Comparator for the primary endpoint:** Slice-FPR certified + block (Corollary 1).
- **Secondary comparators:** RC-SIR (Bonferroni), ERM (no margin), Pooled LTT, No action, Oracle.
- **Fixed settings:** budgets α = (0.05, 0.02, 0.05), δ = 0.1; detector = Isolation Forest; thresholds (0.9, 0.95, 0.99, 0.995, 0.999); action set {rate-limit, block}; n_cal = 500.

## Study C — independent confirmatory replications (new seeds, diverse scenarios)
- **Replications:** R = 8, with master seeds 3001 … 3008. None of these seeds was used before.
- **Per replication:**
  - Scenario parameters are drawn from the seed: per-slice UE counts scaled by U(0.75, 1.25); attack probability U(0.4, 0.8); guaranteed shares perturbed by U(0.85, 1.15) and renormalised; buffers scaled by U(0.75, 1.25); load range centre U(0.75, 0.95) with width 0.5; attack-slice probabilities ~ Dirichlet(4.5, 1.5, 4.0).
  - Fresh detector training on 600 benchmark-regime episodes.
  - Pool of 1500 deployment episodes.
- **Within each replication:** 50 random calibration/test splits (500/1000).
- **Endpoints:**
  - **C-E1 (validity):** per replication, the fraction of splits with any slice's realised test collateral above its budget.
    - Report a Clopper–Pearson 95% CI on the pooled frequency (400 splits).
    - Report separately "confident violations": the one-sided 95% Hoeffding lower bound of the test risk exceeds α_s. This separates calibration failures from test-set sampling error.
  - **C-E2 (primary efficacy):** per replication, the mean paired difference in delivered attack fraction, RC-SIR-FS minus Slice-FPR, over its 50 splits.
    - Inference is across the 8 independent replications: mean, two-sided 95% t-interval, and an exact sign test.
    - **Pre-registered claim:** "direct certification improves on FPR certification" is supported **only if** the t-interval upper bound < 0 **and** ≥ 7/8 replications have a negative mean difference.
    - Otherwise the claim is reported as not confirmed.
  - **C-E3:** the same paired analysis for RC-SIR-FS vs ERM (expected: no difference in mitigation, with ERM less valid at small n) and for RC-SIR vs Slice-FPR.

## Study N — non-monotone mitigation (redirection to a scrubbing service)
- **Action:** *redirect*. The UE's traffic is sent over the shared egress link to a scrubbing service, in a borrow-only class with guarantee 0 and leftover-sharing weight 0.20. The scrubber removes attack traffic; benign traffic returns one slot later into its original slice (hairpin). Benign traffic of a redirected UE therefore crosses the shared link twice.
- **Assumption:** the scrubber is a perfect filter of attack traffic (optimistic for mitigation).
- **Policy set:** per slice (τ, a) with a ∈ {block, redirect}; 11³ = 1331 policies. Base scenario (`sim.PARAMS`) with a new master seed 4001; 600 training and 1500 pool episodes.
- **Hypotheses:**
  - **N-H1 (A3 violated):** some (episode, policy, slice) has collateral > acted-benign fraction. Report the maximum and the frequency of the excess.
  - **N-H2 (FPR certificate breaks):** "Slice-FPR certified + redirect" (a per-slice FPR certificate with redirect as the action) has violation frequency > δ over 200 splits.
  - **N-H3 (direct certificate holds):** RC-SIR-FS over {block, redirect} has violation frequency ≤ δ (Proposition 1 does not need A3).
- Each hypothesis is reported as supported or not, whatever the outcome.

## Unchanged from v1
The published v1 results (`results/`) are kept as the exploratory study. The manuscript will label v1 "exploratory" and Studies C and N "confirmatory".
