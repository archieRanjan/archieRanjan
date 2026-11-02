# Research specification

## Primary research question (one sentence)
In a sliced 5G user plane where detector-triggered per-UE mitigation (rate-limit or block) is calibrated offline, does certifying each slice's *action-induced SLA-violation risk* directly admit more attack mitigation than certifying each slice's *false-positive rate*, at the same per-slice budgets α_s and confidence 1−δ, and under what conditions?

## Problem statement
An operator applies a threshold policy π_λ, with λ = (τ_s, a_s) for s ∈ {eMBB, URLLC, mMTC} and a_s ∈ {rate-limit, block}, to detector scores. It must choose λ to minimise the delivered attack fraction R^a(λ) while guaranteeing, with probability ≥ 1−δ over the calibration data, that the action-induced collateral R^c_s(λ) ≤ α_s for every slice.
- **Strongest existing alternative:** per-slice certified FPR control (the slice-stratified form of conformal / risk-controlled detectors), which by Lemma 1 also bounds collateral.
- **Candidate advance:** certify R^c_s directly from counterfactual replays.

## System model
Three-slice egress link (C = 100 units/slot) with hierarchical guaranteed shares (0.55, 0.25, 0.20) and borrowing. Per-slice FIFO buffers. Per-UE policing before queueing. Episodes have a 30-slot observation window followed by a 120-slot action window. Details: `code/sim.py` (PARAMS).

## Threat model
Up to 4 attacking UEs per episode, inside any slice (probabilities 0.45, 0.15, 0.40), with three attack types:
- constant floods;
- pulsing floods;
- low-and-slow sources (deployment regime only).

70% of deployment attackers mimic the packet size of their slice. Attackers do not adapt to the detector or the thresholds (adaptive attackers are out of scope).

## Assumptions and justification
| ID | Assumption | Justification / test |
|---|---|---|
| A1 | Calibration and deployment episodes are i.i.d. | Holds by construction in the simulator. Violated by temporal dependence in practice → limitation. Load-shift experiment included. |
| A2 | Collateral can be evaluated for every λ by replay or a twin | Replay engine = simulator. Twin with 8% capacity error tested (Proposition 2). |
| A3 | Scheduler monotonicity (less traffic from others never hurts a UE) | Verified numerically: unit test plus all 1500×1331×3 pool entries (max excess 2.6e-8, float32 rounding). Not proven for real UPFs. |

## Mathematical objective
min_{λ∈Λ} R^a(λ) s.t. R^c_s(λ) ≤ α_s ∀s, with Pr{∀s: R^c_s(λ̂) ≤ α_s} ≥ 1−δ.
- α = (0.05, 0.02, 0.05), δ = 0.1.
- |Λ| = 1331.

## Falsifiable hypotheses
| ID | Hypothesis | Test | Falsified if |
|---|---|---|---|
| H1 | Certified methods (RC-SIR, RC-SIR-FS, Slice-FPR) keep the realised per-slice collateral within budget in ≥ 1−δ of splits | 200 splits, n = 500, plus the n-sweep | Violation frequency > δ beyond Monte Carlo error |
| H2 | Empirical constraint satisfaction without a margin (ERM) violates budgets more often than δ for small n | n-sweep | ERM violation frequency ≤ δ for all n |
| H3 (primary) | At equal α and δ, direct certification delivers less attack traffic than Slice-FPR | Paired splits | Mean paired difference ≥ 0, or a majority of splits favour Slice-FPR |
| H4 | The gain concentrates where the harm ratio ρ_s ≪ 1 (Remark 1) | Harm-ratio table + budget sensitivity | Gain appears where ρ ≈ 1, or no gain where ρ ≪ 1 and thresholds lie in the band |

## Scope boundaries
Simulation only (no RAN, no 5G core software, no real traces). Episodic, non-adaptive attackers. Offline calibration. No PHY-layer effects.

## Success / failure criteria
- **Success:** H1 holds, and H3 holds for at least the nominal configuration, with conditions characterised (H4).
- **Failure:** H1 fails (the method is invalid), or H3 fails everywhere (the contribution reduces to a negative result, which is then reported as such).

## Outcome (from `results/results.json`)
| Hypothesis | Outcome |
|---|---|
| H1 | Supported: 0 violations in all certified configurations. |
| H2 | Supported: ERM violated in 25.5% / 15.5% / 10.0% of splits at n = 100 / 250 / 500. |
| H3 | Conditionally supported. Only the fixed-sequence variant beats Slice-FPR at nominal budgets (0.417 vs 0.458 attack delivered; better in 93.5% of splits). The Bonferroni variant is worse in 100% of splits. There is no gain at n ≤ 250 or at α × 0.5 / × 2. |
| H4 | Partially supported. The gain arises in eMBB (ρ ≈ 0.54), via the statistical-margin component rather than the deterministic band. |

## Revised question and confirmatory outcome (after the external audit; see ANALYSIS_PLAN_v2.md)

**Question (narrowed):** *When* does direct certification admit more mitigation than per-slice FPR certification? The paper makes no claim about intrusion response in general.

| Pre-registered endpoint | Outcome (`results_confirm/results_confirm.json`) |
|---|---|
| C-E1 validity | Supported: 0 / 400 splits for all certified methods (95% CP upper bound 0.009). ERM 0.003. No "confident" violations. |
| C-E2 primary (FS − Slice-FPR < 0) | **Not confirmed.** Mean −0.030, 95% t-interval [−0.071, +0.011]; 6 / 8 replications negative; sign-test p = 0.29. |
| C-E3 secondary | Bonferroni − Slice-FPR = +0.051 [+0.009, +0.092] (worse). FS − ERM = +0.052 [+0.011, +0.093] (ERM mitigates more). |
| N-H1 A3 violated under redirect | Supported: 1.0% of entries; max excess 0.93 |
| N-H2 FPR + redirect violates budgets in finite samples | **Not supported** (0 / 200) |
| N-H3 direct certification valid under redirect | Supported (0 / 200) |

**Post-hoc (exploratory):**
- Large-sample analysis: 31 of 441 FPR-feasible policies with redirect have collateral above the budget (0 in the monotone study).
- Heterogeneity across replications tracks the Remark 1 margin band (Spearman −0.85, n = 8).
