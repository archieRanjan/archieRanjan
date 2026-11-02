# Proof and implementation audit (responds to audit §2)

## A. Monotonicity of the implemented scheduler (A3 becomes a theorem for this model)

**Model.** This is the code in `sim._serve` and `sim.evaluate_policies`.
- Slices s ∈ S, guarantees g_s C > 0 with Σ_s g_s ≤ 1, leftover weights w_s = g_s > 0, buffers B_s.
- In slot t, the available amount is a_s = q_s + A_s (backlog plus arrivals).

**Lemma A (allocation).** The implemented procedure returns x_s(a) = min(a_s, g_s C + w_s θ(a)), where θ(a) = sup{θ ≥ 0 : Σ_s min(a_s, g_s C + w_s θ) ≤ C} (θ = ∞ if Σ a_s ≤ C). The following hold:
1. θ is non-increasing in every a_{s'}.
2. The residual r_s = a_s − x_s = max(0, a_s − g_s C − w_s θ) is non-decreasing in every coordinate of a.
3. If r_s > 0, then x_s = g_s C + w_s θ, which is non-increasing in a.

*Proof.*
- **The procedure computes x.** It first serves min(a_s, g_s C). Each subsequent round splits the leftover in proportion to w among classes with remaining demand. In every round, either all classes with demand absorb their full share (the leftover is exhausted), or at least one class saturates and leaves the set. So |S| rounds suffice, and the code runs exactly |S| (3 in `sim`, 4 in `sim_ext`). The fixed point is the weighted water level θ, giving x_s = min(a_s, g_s C) + min((a_s − g_s C)^+, w_s θ) = min(a_s, g_s C + w_s θ).
- **Item 1.** Φ(θ; a) = Σ_s min(a_s, g_s C + w_s θ) is non-decreasing in a and in θ, so {θ : Φ(θ; a) ≤ C} shrinks as a grows.
- **Items 2–3.** These follow directly from item 1. ∎

**Lemma B (queues).** The dynamics are:
- q_s(t+1) = min(B_s, r_s(t));
- overflow O_s(t) = max(0, r_s(t) − B_s);
- drop fraction f_s(t) = O_s(t)/A_s(t) (0 if A_s(t) = 0).

If arrivals satisfy A' ≤ A component-wise in every slot, then q' ≤ q and O' ≤ O in every slot.

*Proof.* By induction on t. Since a' = q' + A' ≤ q + A = a, Lemma A(2) gives r' ≤ r; min and max(·, 0) preserve the order. ∎

**Theorem 1 (A3 holds for this scheduler).** Let u be a benign UE of slice s that is not acted on. Suppose every action only reduces offered traffic pointwise (rate-limit: min(D, cap) ≤ D; block: 0). Then in every slot f'_s(t) ≤ f_s(t) and delay'_s(t) ≤ delay_s(t). Hence u's delivered fraction weakly increases, its 95th-percentile delay weakly decreases, and V_u(π_λ) ≤ V_u(π_0).

*Proof.* Fix t. Write Δ = A_s − A'_s ≥ 0. Actions in other slices enter only through θ, i.e. the case Δ = 0.
- **Drop fraction.** If O' = 0, the claim is trivial. Otherwise O' > 0, so r'_s > 0. By Lemma A(3), x'_s = g_s C + w_s θ' ≥ g_s C + w_s θ ≥ x_s. By Lemma B, O ≥ O' > 0, so O = q + A_s − x_s − B_s. Then
  O' = q' + A_s − Δ − x'_s − B_s ≤ O − Δ, and f' = O'/(A_s − Δ) ≤ (O − Δ)/(A_s − Δ) ≤ O/A_s.
  The last step uses O ≤ A_s, which holds because q ≤ B_s after truncation in the previous slot and x_s ≥ 0.
- **Delay.** delay = q(t+1)/x_s(t). If q'(t+1) = 0, the claim is trivial. Otherwise r'_s > 0, and also r_s ≥ r'_s > 0. Both allocations are then at the water level, so x'_s ≥ x_s > 0 (because g_s > 0), and q'(t+1) ≤ q(t+1). Hence delay' ≤ delay. The code's sentinel for x_s = 0 with q > 0 can never trigger, because x_s ≥ g_s C > 0 whenever r_s > 0.
- **SLA indicators.** u's own arrivals are unchanged. Delivered = Σ_t D_u(t)(1 − f_s(t)) is monotone. The 95th percentile of delay over u's active slots is monotone because percentiles are monotone and the active set is unchanged. ∎

**Corollary (Lemma 1 of the paper)** follows: collateral can only fall on acted UEs.

**Numerical confirmation:**
- unit test `test_lemma1_actions_never_harm_non_acted_ues` (1000 random action patterns);
- exhaustive check over 1500 × 1331 × 3 pool entries, maximum excess 2.6e-8 (float32).

**Counterexample (A3 fails when actions relocate rather than remove traffic).** With *redirect* to a scrubbing service over the same link (`sim_ext`), A' ≤ A no longer holds:
- the redirected traffic enters a fourth class;
- benign traffic re-enters its slice one slot later.

`tests/test_sim_ext.py::test_redirect_can_harm_non_acted_ues` gives a concrete instance. Two eMBB UEs offer 30 and 26 units/slot, and a URLLC UE offers 40, on a 100-unit link. Without action, all SLAs hold. Redirecting the 30-unit eMBB UE raises the total offered load to 126 and pushes the *non-acted URLLC UE in another slice* into violation. Study N measures how often this happens under realistic policies.

**Other ways A3 can fail in real systems (not modelled):**
- congestion-controlled senders that increase their rate when competitors are removed (this hurts third parties only through queueing, and only under non-fair schedulers);
- AQM with shared, non-isolated queues;
- application retry storms after rate-limiting.

## B. Proposition 1 implementation checklist (`code/methods.py`, `code/riskcontrol.py`)

| Item (audit §2) | Status | Evidence |
|---|---|---|
| Episode losses bounded in [0,1] and averaged correctly | ✓ | L^c_s is a mean of indicators over |B_s(e)| ≥ 1 benign UEs (the scenarios always have ≥ 1 benign UE per slice); p-values use episode-level means, so i.i.d. episodes satisfy the HB conditions |
| HB p-value matches LTT | ✓ | `riskcontrol.hb_pvalue`: min{exp(−n·h(min(R̂, α), α)), e·P[Bin(n, α) ≤ ⌈nR̂⌉]}. Bentkus is valid for [0,1]-bounded losses |
| Policy space fixed independently of data | ✓ | Grid built from constants in `Ctx.__post_init__` |
| Ordering uses only the ordering half D1 | ✓ | `rcsir_fs`: `order` computed from `Ra` and `sel_obj(..., a)` only; p-values from `b` only |
| Fallback | ✓ | π_0 index `I0` is returned only when nothing is certified; it is never tested; R^c(π_0) = 0 by definition |
| Joint per-slice coverage | ✓ | Union null: p_λ = max_s p_{s,λ} |
| Selection after certification | ✓ | Selection is among certified policies only; the guarantee holds simultaneously for all of them on the FWER event |
| Empirical validity with known risks | ✓ | `tests/test_validity_montecarlo.py`: adversarial selection objective; the selected policy violated in 0.07% of 1500 draws for both variants (δ = 10%); ERM in 100% (the test has power) |
| Standalone implementation equals the published one | ✓ | `tests/test_methods_consistency.py` reproduces the v1 numbers exactly |

## C. Proposition 2 (twin transfer)
The proof is correct (union bound), but it is **operationally vacuous** in our setting: the Hoeffding union term (≈0.14 at m = 300) exceeds every budget. It is demoted to a stated limitation in the revised manuscript.
