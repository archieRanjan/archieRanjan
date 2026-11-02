# Introduction {#sec:intro}

When an intrusion detector flags a user equipment (UE) in a sliced 5G network, the operator can rate-limit, block or redirect its traffic at the user-plane function (UPF). Each action harms benign users whenever the detector is wrong. How much harm depends on the action and on the slice: a blocked eMBB download degrades throughput, while a few slots of extra queueing break a URLLC deadline. Operators are accountable for this service-level harm, not for the false-alarm rate as such [@sommer2010outside; @arp2022dos].

Two lines of work address parts of the problem:

- **Calibrated detection.** Finite-sample guarantees on false-positive or false-discovery rates [@bates2023outliers], including recent detectors that calibrate alert thresholds by conformal risk control [@youssef2026caliburn; @barrett2026firce; @farzaneh2025ccoad]. These certify an *alert-level* quantity.
- **Intrusion response.** Optimised defensive actions, with guarantees that hold relative to an assumed attacker and system model [@hammar2022optimalstopping; @hammar2024dynamic; @zonouz2014rre].

Neither certifies, without a model, the fraction of benign users in each slice whose service-level agreement (SLA) is broken *by the mitigation*.

This paper studies one question:

> *For detector-triggered mitigation in a sliced user plane, when does certifying each slice's action-induced SLA-violation risk directly admit more attack mitigation than certifying each slice's false-positive rate, at equal per-slice budgets and confidence?*

We do not claim to improve intrusion response in general. The comparison is between two ways of obtaining the same kind of guarantee.

The answer turns on a structural property of the user plane. If every action only *removes* traffic and the scheduler is a work-conserving weighted water-filling scheduler with per-slice buffers, then removing traffic never worsens the service of any other UE (Theorem 1). A per-slice false-positive certificate is then also a valid collateral certificate. Direct certification can gain only through the *harm ratio* between collateral and acted-benign fraction, and it pays for that with counterfactual replay and a larger hypothesis space. If an action *relocates* traffic, as redirection to a scrubbing service over the shared link does, the property fails, and the false-positive certificate can accept policies whose collateral exceeds the budget.

**Contributions.**

1. **Formulation and structure.** We define per-slice action-induced collateral against the no-action counterfactual. We prove (Theorem 1, Appendix [A](#app:proof)) that the scheduler used in our evaluation is monotone, so collateral is bounded by the acted-benign fraction (Lemma 1). We also show by construction that relocating actions break this bound, including across slices.
2. **Certification procedure.** RC-SIR applies Learn-then-Test (LTT) [@angelopoulos2025ltt] over 1331 per-slice policies, with union-null p-values and fixed-sequence family-wise error control. The machinery is existing and used unchanged. We verify its implementation against known-risk Monte Carlo cases.
3. **Evidence, with pre-registered confirmation.** An exploratory study, followed by a confirmatory analysis plan committed before data generation:
    - eight independent replications with randomised scenarios (Study C);
    - a non-monotone action study (Study N).

    Certified methods kept every budget in all 400 confirmatory splits. The pre-registered improvement claim of direct over FPR certification was **not confirmed**: the mean paired difference in delivered attack fraction was -0.030, with 95% interval [-0.071, +0.011], and 6 of 8 replications favoured direct certification. Under relocating actions, a post-hoc large-sample analysis shows the FPR criterion accepting policies whose collateral exceeds the budget. No finite-sample violation was observed (pre-registered hypothesis N-H2 not supported), and direct certification stayed valid.

All evidence comes from a fluid simulator. Section [8](#sec:limits) states what this does not establish.

# Related Work {#sec:related}

**Validity of ML-based intrusion detection.**

- Evaluation pitfalls and the operational cost of errors are well documented [@sommer2010outside; @arp2022dos].
- Benchmark datasets contain design and labelling flaws [@engelen2021troubleshooting; @flood2024smells].
- Detectors degrade across domains [@layeghy2023xcross].
- 5G datasets report near-perfect detection [@siriwardhana2025nidd; @khan2023slicesecure; @amponis2022pfcp], whereas adversarial evaluation of 5G-core detectors shows fragility [@manca2026sage5gc].

**Calibrated detection.**

- Conformal p-values give exact FDR control for outlier detection [@bates2023outliers].
- TRANSCENDENT uses conformal evaluation to reject drifting samples [@barbero2022transcendent].
- FIRCE couples conformal evaluators with retraining [@barrett2026firce].
- CALIBURN sets streaming alert thresholds by regime-dependent conformal risk control [@youssef2026caliburn].
- An online conformal detector controls a smoothed FDR [@farzaneh2025ccoad].

These methods certify detector outputs. Our per-slice FPR baseline is their slice-stratified analogue.

**Risk control.**

- Conformal risk control (CRC) bounds monotone losses [@angelopoulos2024crc].
- LTT handles non-monotone and multiple risks by multiple testing [@angelopoulos2025ltt].
- Weighted and adaptive variants address shift [@tibshirani2019weighted; @barber2023beyond; @gibbs2021aci].
- Conformal policy control regulates deviations from a safe policy [@prinster2026cpc].
- Prediction-powered risk control reduces conservativeness using unlabelled data [@einbinder2025ssrc].

**Response and mitigation.**

- Optimal-stopping and game-theoretic methods derive threshold response policies under a model [@hammar2022optimalstopping; @hammar2024dynamic; @zonouz2014rre].
- Switch-native systems mitigate volumetric attacks at line rate [@liu2021jaqen].

**Slicing.**

- RAN slicing with performance isolation [@foukas2017orion].
- Overbooking [@salvat2018overbooking] and SLA-cost-aware forecasting [@bega2019deepcog] show that slices share and borrow capacity.
- Network digital twins [@ferriolgalmes2023routenetfermi] are candidate replay engines.
- Attacks on learned slicing controllers produce slice-dependent SLA violations [@tashman2026adversarial].

Table 1 summarises the differences.


```{=html}
<div class="span" id="tab:comparison"><div class="tbl-num">Table 1<br/>Comparison with the closest approaches. Qualitative columns are based on the cited papers' abstracts.</div><table>
<colgroup>
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
<col style="width: 20%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Approach</th>
<th style="text-align: left;">What it certifies or optimises</th>
<th style="text-align: left;">Key assumption</th>
<th style="text-align: left;">Difference from this work</th>
<th style="text-align: left;">Compared here</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">Conformal outlier / alert-threshold
control <span class="citation"
data-cites="bates2023outliers youssef2026caliburn">[1, 2]</span></td>
<td style="text-align: left;">Alert-level FPR, FDR or false-positive
budget</td>
<td style="text-align: left;">Exchangeability</td>
<td style="text-align: left;">Certifies slice-indexed SLA outcomes of
actions</td>
<td style="text-align: left;">Exploratory: 1% FPR operating point</td>
</tr>
<tr class="even">
<td style="text-align: left;">Per-slice certified FPR (Corollary 1)</td>
<td style="text-align: left;">Collateral, via Theorem 1</td>
<td style="text-align: left;">Monotone scheduling and traffic-removing
actions</td>
<td style="text-align: left;">Direct certification does not need
monotonicity</td>
<td style="text-align: left;">Primary comparator (all studies)</td>
</tr>
<tr class="odd">
<td style="text-align: left;">LTT / CRC <span class="citation"
data-cites="angelopoulos2025ltt angelopoulos2024crc">[3, 4]</span></td>
<td style="text-align: left;">Generic risks by multiple testing</td>
<td style="text-align: left;">i.i.d. calibration</td>
<td style="text-align: left;">Used unchanged; we add the counterfactual
slice-collateral formulation and the structural analysis</td>
<td style="text-align: left;">—</td>
</tr>
<tr class="even">
<td style="text-align: left;">Conformal policy control <span
class="citation" data-cites="prinster2026cpc">[5]</span></td>
<td style="text-align: left;">Risk of deviating from a safe policy</td>
<td style="text-align: left;">Safe reference policy</td>
<td style="text-align: left;">Network counterfactual, slice structure,
relocating actions</td>
<td style="text-align: left;">Not compared (different setting)</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Optimal-stopping / game-theoretic response
<span class="citation"
data-cites="hammar2022optimalstopping zonouz2014rre">[6, 7]</span></td>
<td style="text-align: left;">Model-optimal response</td>
<td style="text-align: left;">Attacker and system model</td>
<td style="text-align: left;">No model; distribution-free per-slice
certificate</td>
<td style="text-align: left;">Not compared (different criterion)</td>
</tr>
<tr class="even">
<td style="text-align: left;">Pooled certification (ablation)</td>
<td style="text-align: left;">One certificate across slices</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">Per-slice budgets</td>
<td style="text-align: left;">Exploratory, Study C</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Empirical constrained selection (ERM)</td>
<td style="text-align: left;">No guarantee</td>
<td style="text-align: left;">—</td>
<td style="text-align: left;">Statistical margin</td>
<td style="text-align: left;">All studies</td>
</tr>
</tbody>
</table>
</div>
```


# System Model and Formulation {#sec:model}

**User plane.** An egress link of capacity $C$ serves slices $s\in\mathcal{S}$, each with a guaranteed rate $g_sC>0$ (with $\sum_s g_s\le1$), a leftover-sharing weight $w_s=g_s$ and a buffer $B_s$. In each slot the scheduler allocates
$$x_s=\min\big(a_s,\;g_sC+w_s\theta\big),$$
where $a_s$ is backlog plus arrivals and the water level $\theta$ is the largest value for which $\sum_s x_s\le C$. Overflow beyond $B_s$ is dropped. Drop fraction and queueing delay are shared by the UEs of a slice.

**Episodes, detector and policies.**

- An episode has an observation window ($T_o$ slots) and an action window ($T_a$ slots).
- The detector maps observation-window features of UE $u$ to $z_u\in[0,1]$.
- A policy $\pi_\lambda$ with $\lambda=(\tau_s,a_s)_{s\in\mathcal{S}}$ applies action $a_s$ to every UE of slice $s$ with $z_u\ge\tau_s$; $\pi_0$ takes no action.
- Actions are rate-limiting ($\mathsf{RL}$), blocking ($\mathsf{B}$) and, in Study N, redirection ($\mathsf{R}$).
- With five thresholds and two actions per slice, $|\Lambda|=1331$.

**SLA outcomes.** $V_u(e;\pi)\in\{0,1\}$ indicates that benign UE $u$ violates its slice SLA in the action window of episode $e$:

- eMBB: delivered/offered below 0.90;
- URLLC: 95th-percentile delay above 2 slots, or delivery below 0.99;
- mMTC: delivery below 0.95.

**Definition 1 (action-induced collateral).**
$$L^{c}_s(e;\lambda)=\frac{1}{|\mathcal{B}_s(e)|}\sum_{u\in\mathcal{B}_s(e)}\mathbb{1}\{V_u(e;\pi_\lambda)=1,\;V_u(e;\pi_0)=0\},\qquad R^c_s(\lambda)=\mathbb{E}_e[L^c_s(e;\lambda)].$$

**Problem.** Let $R^a(\lambda)$ be the expected fraction of attack traffic delivered in episodes that contain attackers. The goal is
$$\min_{\lambda}R^a(\lambda)\;\;\text{s.t.}\;\;R^c_s(\lambda)\le\alpha_s\;\forall s,$$
with the selected $\hat{\lambda}$ satisfying all constraints with probability at least $1-\delta$ over the calibration data.

**Assumptions.**

- **A1:** calibration and deployment episodes are i.i.d.
- **A2:** $L^c_s(e;\lambda)$ can be evaluated for every $\lambda$ by replaying calibration episodes.

**Theorem 1 (monotonicity of the scheduler).** Suppose every action only reduces the traffic of the acted UE pointwise in time (as $\mathsf{RL}$ and $\mathsf{B}$ do). Then, for every benign UE that is not acted on, the per-slot drop fraction and queueing delay of its slice do not increase. Hence $V_u(e;\pi_\lambda)\le V_u(e;\pi_0)$.

The proof is in Appendix [A](#app:proof). It uses the closed form of the allocation, a queue-comparison induction, and the inequality $(O-\Delta)/(A-\Delta)\le O/A$ for overflow $O\le A$.

**Lemma 1.** Under the conditions of Theorem 1,
$$L^c_s(e;\lambda)\le F_s(e;\tau_s)=\frac{1}{|\mathcal{B}_s(e)|}\sum_{u\in\mathcal{B}_s(e)}\mathbb{1}\{z_u\ge\tau_s\}.$$

*Proof.* By Theorem 1, non-acted benign UEs contribute zero, and each acted UE contributes at most $1/|\mathcal{B}_s(e)|$. ∎

**Remark 1.** Write $R^c_s=\rho_s\Phi_s$, with $\Phi_s(\tau)=\mathbb{E}[F_s(e;\tau)]$ and harm ratio $\rho_s\in[0,1]$. A per-slice FPR certificate requires $\Phi_s\le\alpha_s$; direct certification requires only $\rho_s\Phi_s\le\alpha_s$. A gain is possible only where $\rho_s<1$ and the threshold grid, after statistical margins, contains points between the two conditions.

**Proposition 0 (relocation breaks Lemma 1).** If an action relocates traffic onto shared resources rather than removing it, $F_s$ need not bound $L^c_s$, even for slices in which no UE is acted on.

*Proof (by construction).* Take two eMBB UEs offering 30 and 26 units/slot and a URLLC UE offering 40 units/slot on a link with $C=100$ and shares $(0.55,0.25,0.20)$. Without action, all SLAs hold. Redirecting the first eMBB UE to a borrow-only scrubbing class whose benign output re-enters eMBB one slot later raises the offered load to 126. The URLLC UE, which is not acted on and lies in another slice, then violates its SLA. Its slice has $F_{\mathrm{URLLC}}=0$ but $L^c_{\mathrm{URLLC}}=1$. This case is a unit test in the released code. ∎

# Certification Procedure {#sec:method}

For calibration episodes $e_1,\dots,e_n$, replay yields $L^c_s(e_i;\lambda)$ and $L^a(e_i;\lambda)$ for all $\lambda$. Let $\hat{R}_s(\lambda)$ be the empirical mean collateral. Each $\lambda$ is tested against the union null $H_\lambda:\exists s,\,R^c_s(\lambda)>\alpha_s$ with
$$p_\lambda=\max_s p^{\mathrm{HB}}(\hat{R}_s(\lambda);\alpha_s,n),$$
where $p^{\mathrm{HB}}$ is the Hoeffding–Bentkus p-value for $[0,1]$-bounded losses [@angelopoulos2025ltt]. Family-wise error is controlled at $\delta$ in one of two ways:

- **Bonferroni (RC-SIR):** threshold $\delta/|\Lambda|$.
- **Fixed sequence (RC-SIR-FS):** policies are ordered on half of the calibration set by $\max_s\hat{R}_s/\alpha_s$ and tested in that order on the other half, stopping at the first non-rejection.

The deployed policy minimises empirical $\hat{R}^a$ over the certified set, with $10^{-3}J$ as a tie-breaker, where $J$ is the weighted benign-violation rate. The fallback is $\pi_0$. Algorithm 1 gives the steps.


<div class="algo"><b>Algorithm 1.</b> RC-SIR / RC-SIR-FS certification and selection<br/>
<b>Input:</b> calibration episodes e<sub>1..n</sub>; policy set Λ; budgets α<sub>s</sub>; level δ.<br/>
1. Replay every e<sub>i</sub> under all λ ∈ Λ and π<sub>0</sub>; record L<sup>c</sup><sub>s</sub>(e<sub>i</sub>;λ) and L<sup>a</sup>(e<sub>i</sub>;λ).<br/>
2. <i>Bonferroni:</i> p<sub>λ</sub> = max<sub>s</sub> p<sup>HB</sup>(R̂<sub>s</sub>(λ); α<sub>s</sub>, n); certify {λ : p<sub>λ</sub> ≤ δ/|Λ|}.<br/>
2'. <i>Fixed sequence:</i> split into halves D<sub>1</sub>, D<sub>2</sub>; order Λ by max<sub>s</sub> R̂<sub>s</sub><sup>(D1)</sup>(λ)/α<sub>s</sub>; test in order on D<sub>2</sub> at level δ, stop at the first non-rejection.<br/>
3. Return argmin<sub>λ∈Λ̂</sub> R̂<sup>a</sup>(λ), or π<sub>0</sub> if Λ̂ is empty.</div>


**Proposition 1 (validity).** Under A1–A2, both variants satisfy $\Pr\{\forall s:R^c_s(\hat{\lambda})\le\alpha_s\}\ge1-\delta$. No monotonicity is required.

*Proof.* $p_\lambda$ is valid for $H_\lambda$, because it dominates the valid p-value of a violating slice. Bonferroni, and fixed-sequence testing with an ordering independent of the testing half, control the family-wise error. On the complement of a family-wise error, every certified policy is feasible, so selection among them preserves the guarantee. $\pi_0$ has zero collateral. ∎

This is a direct consequence of LTT.

**Corollary 1 (Slice-FPR certificate).** Testing $\Phi_s(\tau)\le\alpha_s$ from the most conservative threshold downwards at level $\delta/|\mathcal{S}|$ per slice certifies the per-slice FPR. Under Theorem 1 it certifies collateral. Under relocating actions it does not (Proposition 0).

**Implementation verification.**

- **Known-risk Monte Carlo.** The certified variants were tested on synthetic loss tables with known risks and an adversarial selection objective that rewards risky policies. Over 1500 calibration draws, the selected policy violated a budget in 0.07% of draws for both variants ($\delta=10\%$). Uncertified constrained selection did so in 100% of draws.
- **Consistency.** A standalone reimplementation reproduces all published exploratory numbers exactly.

**Complexity.** Certification costs $O(n|\Lambda||\mathcal{S}|)$ operations. Replay dominates: $|\Lambda|$ policy evaluations per calibration episode.

# Experimental Design {#sec:setup}

**Simulator.**

- Three slices, $C=100$ units/slot, shares $(0.55,0.25,0.20)$, buffers $(200,12,60)$, and 14/10/16 benign UEs per slice in the base scenario.
- Observation and action windows of 30 and 120 slots.
- Up to four attackers per episode: floods, pulsing floods and low-and-slow sources.
- Rate-limit caps $(3,1,0.5)$ units/slot.

**Detector shift.** The detector is trained on a *benchmark* regime and deployed in an *operational* regime with:

- additional benign behaviours (variable heavy users, URLLC alarm bursts, mMTC firmware bursts);
- attackers that mimic their slice's packet size in 70% of cases;
- an unseen low-and-slow class.

This models cross-domain degradation [@layeghy2023xcross]. The detector is an Isolation Forest [@liu2008iforest] trained on benign benchmark-regime UEs; its score is the benign-training quantile. Thresholds are $\{0.9,0.95,0.99,0.995,0.999\}$. Implementation uses scikit-learn [@pedregosa2011sklearn].

**Fixed settings.** $\alpha=(0.05,0.02,0.05)$, $\delta=0.1$, $n=500$ calibration episodes.

**Exploratory study (v1).**

- One pool of 1500 episodes, 200 calibration/test splits.
- Sweeps over $n$ and budget scale.
- Load-shift and twin experiments.
- A second (supervised) detector.

During this study we made two design changes, both disclosed in Appendix [B](#app:deviations): we replaced a first simulator version, and we corrected the selection objective. We also chose the fixed-sequence variant after seeing results.

**Confirmatory studies.** Their analysis plan was committed to the repository before any confirmatory data existed, and was not modified.

**Study C** (eight independent replications, new seeds):

- Each replication draws its scenario: UE counts ×U(0.75,1.25), attack probability U(0.4,0.8), perturbed shares and buffers, load range, and attack-slice probabilities.
- Each trains a new detector on 600 episodes and generates 1500 deployment episodes, analysed over 50 splits.
- **Primary endpoint:** the mean paired difference in delivered attack fraction (RC-SIR-FS minus Slice-FPR), with inference across replications by a t-interval and an exact sign test.
- **Pre-registered decision rule:** the improvement claim is supported only if the 95% upper bound is below zero *and* at least 7 of 8 replications favour RC-SIR-FS.
- **Validity:** violation frequency with Clopper–Pearson intervals, plus "confident violations" whose one-sided 95% Hoeffding lower bound on the test risk exceeds the budget. The latter separates calibration failures from test-set sampling error.

**Study N** (non-monotone actions):

- Actions are block or redirect, in the base scenario with a new seed.
- Redirection sends traffic through a borrow-only scrubbing class (weight 0.20) that removes attack traffic. Benign traffic returns to its slice one slot later.
- Hypotheses:
  - N-H1: Lemma 1 fails empirically;
  - N-H2: Slice-FPR with redirect violates its budgets in more than $\delta$ of splits;
  - N-H3: RC-SIR-FS remains valid.

**Baselines.** All are evaluated on identical replayed outcomes:

- **Slice-FPR:** Corollary 1, the strongest certified alternative.
- **Pooled LTT:** one shared $(\tau,a)$.
- **ERM:** empirical constrained selection without a margin.
- **Conformal FPR 1%** and a **fixed threshold:** alert-level operating points (exploratory study only).
- **No action** and the **Oracle** (which blocks exactly the attackers).

Model-based response policies [@hammar2022optimalstopping] optimise a different criterion and are outside the scope of the comparison.

# Results {#sec:results}

## Exploratory study


```{=html}
<div class="span" id="tab:main"><div class="tbl-num">Table 2<br/>Main comparison, Isolation-Forest detector, 200 random splits (n_cal = 500, n_test = 1000). Budgets alpha = (0.05, 0.02, 0.05), delta = 0.1. Collateral = mean realised test collateral risk; viol. freq. = fraction of splits where any slice exceeds its budget (target <= delta for certified methods).</div><table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Method</th>
<th style="text-align: right;">Viol. freq. (±MC s.e.)</th>
<th style="text-align: right;">Collateral eMBB</th>
<th style="text-align: right;">Collateral URLLC</th>
<th style="text-align: right;">Collateral mMTC</th>
<th style="text-align: right;">Benign viol. J</th>
<th style="text-align: right;">Attack delivered</th>
<th style="text-align: right;">Fallback</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">RC-SIR (ours)</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0061</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0032</td>
<td style="text-align: right;">0.0305</td>
<td style="text-align: right;">0.498</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">RC-SIR-FS (ours)</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0181</td>
<td style="text-align: right;">0.0024</td>
<td style="text-align: right;">0.0031</td>
<td style="text-align: right;">0.0240</td>
<td style="text-align: right;">0.417</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Slice-FPR certified + block</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0061</td>
<td style="text-align: right;">0.0025</td>
<td style="text-align: right;">0.0031</td>
<td style="text-align: right;">0.0288</td>
<td style="text-align: right;">0.458</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">ERM (no margin)</td>
<td style="text-align: right;">0.100 ± 0.021</td>
<td style="text-align: right;">0.0191</td>
<td style="text-align: right;">0.0025</td>
<td style="text-align: right;">0.0083</td>
<td style="text-align: right;">0.0243</td>
<td style="text-align: right;">0.409</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Pooled LTT</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0191</td>
<td style="text-align: right;">0.0025</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0260</td>
<td style="text-align: right;">0.566</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">Conformal FPR 1% + block</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0061</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0426</td>
<td style="text-align: right;">0.775</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Fixed threshold + block</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0191</td>
<td style="text-align: right;">0.0025</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0260</td>
<td style="text-align: right;">0.566</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">No action</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0799</td>
<td style="text-align: right;">0.963</td>
<td style="text-align: right;">1.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Oracle</td>
<td style="text-align: right;">0.000 ± 0.000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0217</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.00</td>
</tr>
</tbody>
</table>
</div>
```


- **Validity.** No certified method exceeded its budgets in 200 splits. ERM violated them in 10.0% of splits at $n=500$ (equal to $\delta$) and in 25.5% at $n=100$ (Fig. 1).
- **Direct vs FPR certification.** RC-SIR-FS delivered 0.417 of attack traffic, against 0.458 for Slice-FPR; it was better in 93.5% of paired splits (Table 3).
- **Bonferroni variant.** It was worse than Slice-FPR in every split.
- **Where the advantage vanishes.** It disappeared at $n\le250$ and at budgets scaled by 0.5 or 2.
- **Action set.** Rate-limiting added nothing over block-only policies (0.417 vs 0.418).
- **Harm ratios.** Measured over single-slice policies, they were about 0.54 in eMBB, 0.95 in URLLC and 0.99 for blocking in mMTC. Consistent with Remark 1, the gain came from eMBB.
- **Twin calibration.** Calibrating on a twin with an 8% capacity error produced no violations without correction. The rigorous twin-error correction (a union-bound Hoeffding term of about 0.14 at 300 paired episodes) exceeded every budget, so twin-based certification with a guarantee was not practical here.


```{=html}
<div class="span" id="tab:paired"><div class="tbl-num">Table 3<br/>Paired comparisons on identical calibration/test splits (200 splits, n_cal = 500). Negative differences favour A.</div><table style="width:100%;">
<colgroup>
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
<col style="width: 16%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Comparison (A vs B)</th>
<th style="text-align: right;">Mean diff. attack delivered (A-B)</th>
<th style="text-align: right;">2.5% / 50% / 97.5% quantile over
splits</th>
<th style="text-align: right;">A better</th>
<th style="text-align: right;">Tie</th>
<th style="text-align: right;">Mean diff. J</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">RC-SIR vs Slice-FPR</td>
<td style="text-align: right;">+0.0402</td>
<td style="text-align: right;">+0.0329 / +0.0401 / +0.0476</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">+0.0017</td>
</tr>
<tr class="even">
<td style="text-align: left;">RC-SIR vs Pooled LTT</td>
<td style="text-align: right;">-0.0674</td>
<td style="text-align: right;">-0.0853 / -0.0673 / -0.0503</td>
<td style="text-align: right;">1.000</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">+0.0045</td>
</tr>
<tr class="odd">
<td style="text-align: left;">RC-SIR-FS vs RC-SIR</td>
<td style="text-align: right;">-0.0828</td>
<td style="text-align: right;">-0.0983 / -0.0876 / +0.0000</td>
<td style="text-align: right;">0.965</td>
<td style="text-align: right;">0.015</td>
<td style="text-align: right;">-0.0066</td>
</tr>
<tr class="even">
<td style="text-align: left;">RC-SIR-FS vs Slice-FPR</td>
<td style="text-align: right;">-0.0427</td>
<td style="text-align: right;">-0.0554 / -0.0479 / +0.0405</td>
<td style="text-align: right;">0.935</td>
<td style="text-align: right;">0.030</td>
<td style="text-align: right;">-0.0048</td>
</tr>
<tr class="odd">
<td style="text-align: left;">RC-SIR-FS vs Pooled LTT</td>
<td style="text-align: right;">-0.1493</td>
<td style="text-align: right;">-0.1676 / -0.1541 / -0.0666</td>
<td style="text-align: right;">1.000</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">-0.0021</td>
</tr>
<tr class="even">
<td style="text-align: left;">RC-SIR-FS vs ERM</td>
<td style="text-align: right;">+0.0065</td>
<td style="text-align: right;">+0.0000 / +0.0000 / +0.0873</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.875</td>
<td style="text-align: right;">+0.0000</td>
</tr>
</tbody>
</table>
</div>
```



<figure id="fig:fig_ncal"><img src="/home/user/archieRanjan/research/paper/figs/fig_ncal.png"/><figcaption><b>Fig. 1.</b> Exploratory study. Left: budget-violation frequency versus calibration size (dashed: $\delta$). Right: delivered attack fraction.</figcaption></figure>


## Confirmatory Study C (independent replications)

**Validity.** Pooled over 400 splits, RC-SIR-FS, RC-SIR, Slice-FPR and Pooled LTT never exceeded a budget (95% Clopper–Pearson upper bound 0.009). ERM exceeded one in 0.003 of splits. No violation of any method was "confident", i.e. distinguishable from test-set sampling error.

**Primary endpoint (not confirmed).** The mean paired difference in delivered attack fraction, RC-SIR-FS minus Slice-FPR, was -0.030, with 95% t-interval [-0.071, +0.011]. 6 of 8 replications favoured RC-SIR-FS (exact sign test $p=0.29$). The pre-registered criterion (upper bound below zero and at least 7 of 8 replications) was not met.

The effect was heterogeneous (Table 4):

- one replication showed a large gain (-0.144);
- four showed small gains;
- two were slightly negative.

**Secondary endpoints.**

- The Bonferroni variant was worse than Slice-FPR: +0.051, interval [+0.009, +0.092].
- Uncertified ERM delivered less attack traffic than RC-SIR-FS: RC-SIR-FS minus ERM was +0.052, interval [+0.011, +0.093]. That is the price of the certificate in scenarios where the budgets are slack.

**Heterogeneity (post hoc, exploratory).** We counted the eMBB, URLLC and mMTC thresholds in each replication's population at which the FPR test needs more margin than the collateral test. These are thresholds where the acted fraction exceeds $\alpha_s/2$ while collateral stays below $\alpha_s/2$, or where the acted fraction exceeds $\alpha_s$ while collateral stays below it. The count correlated with the gain (Spearman $\rho=-0.85$, eight replications). The three replications without such thresholds showed no gain. This agrees with Remark 1 but was not pre-registered.


```{=html}
<div class="span" id="tab:confirm_C_reps"><div class="tbl-num">Table 4<br/>Study C, eight independent replications (50 splits each, n_cal = 500). Viol. = fraction of splits in which any slice's test collateral exceeded its budget.</div><table>
<colgroup>
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
<col style="width: 8%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: right;">Rep</th>
<th style="text-align: right;">Seed</th>
<th style="text-align: right;">AUC</th>
<th style="text-align: left;">UEs (eMBB/URLLC/mMTC)</th>
<th style="text-align: right;">p_attack</th>
<th style="text-align: right;">Viol. FS</th>
<th style="text-align: right;">Viol. Slice-FPR</th>
<th style="text-align: right;">Viol. ERM</th>
<th style="text-align: right;">Attack del. FS</th>
<th style="text-align: right;">Attack del. Slice-FPR</th>
<th style="text-align: right;">Mean diff (FS−FPR)</th>
<th style="text-align: right;">Splits FS better</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: right;">1</td>
<td style="text-align: right;">3001</td>
<td style="text-align: right;">0.887</td>
<td style="text-align: left;">14/12/13</td>
<td style="text-align: right;">0.52</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.412</td>
<td style="text-align: right;">0.417</td>
<td style="text-align: right;">-0.005</td>
<td style="text-align: right;">0.10</td>
</tr>
<tr class="even">
<td style="text-align: right;">2</td>
<td style="text-align: right;">3002</td>
<td style="text-align: right;">0.922</td>
<td style="text-align: left;">15/12/15</td>
<td style="text-align: right;">0.62</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.363</td>
<td style="text-align: right;">0.394</td>
<td style="text-align: right;">-0.031</td>
<td style="text-align: right;">0.98</td>
</tr>
<tr class="odd">
<td style="text-align: right;">3</td>
<td style="text-align: right;">3003</td>
<td style="text-align: right;">0.915</td>
<td style="text-align: left;">14/10/15</td>
<td style="text-align: right;">0.78</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.301</td>
<td style="text-align: right;">0.330</td>
<td style="text-align: right;">-0.028</td>
<td style="text-align: right;">1.00</td>
</tr>
<tr class="even">
<td style="text-align: right;">4</td>
<td style="text-align: right;">3004</td>
<td style="text-align: right;">0.878</td>
<td style="text-align: left;">11/8/19</td>
<td style="text-align: right;">0.53</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.02</td>
<td style="text-align: right;">0.633</td>
<td style="text-align: right;">0.642</td>
<td style="text-align: right;">-0.009</td>
<td style="text-align: right;">0.92</td>
</tr>
<tr class="odd">
<td style="text-align: right;">5</td>
<td style="text-align: right;">3005</td>
<td style="text-align: right;">0.862</td>
<td style="text-align: left;">12/9/20</td>
<td style="text-align: right;">0.63</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.679</td>
<td style="text-align: right;">0.670</td>
<td style="text-align: right;">+0.008</td>
<td style="text-align: right;">0.04</td>
</tr>
<tr class="even">
<td style="text-align: right;">6</td>
<td style="text-align: right;">3006</td>
<td style="text-align: right;">0.878</td>
<td style="text-align: left;">15/11/12</td>
<td style="text-align: right;">0.43</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.484</td>
<td style="text-align: right;">0.629</td>
<td style="text-align: right;">-0.144</td>
<td style="text-align: right;">1.00</td>
</tr>
<tr class="odd">
<td style="text-align: right;">7</td>
<td style="text-align: right;">3007</td>
<td style="text-align: right;">0.885</td>
<td style="text-align: left;">14/9/16</td>
<td style="text-align: right;">0.70</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.424</td>
<td style="text-align: right;">0.455</td>
<td style="text-align: right;">-0.031</td>
<td style="text-align: right;">0.96</td>
</tr>
<tr class="even">
<td style="text-align: right;">8</td>
<td style="text-align: right;">3008</td>
<td style="text-align: right;">0.871</td>
<td style="text-align: left;">11/9/17</td>
<td style="text-align: right;">0.61</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.00</td>
<td style="text-align: right;">0.671</td>
<td style="text-align: right;">0.668</td>
<td style="text-align: right;">+0.002</td>
<td style="text-align: right;">0.00</td>
</tr>
</tbody>
</table>
</div>
```



```{=html}
<div class="span" id="tab:confirm_C_pooled"><div class="tbl-num">Table 5<br/>Study C pooled over 400 splits (8 replications × 50). Confident viol. = a one-sided 95% Hoeffding lower bound on the test risk exceeds the budget.</div><table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Method</th>
<th style="text-align: right;">Viol. freq. [95% CP CI]</th>
<th style="text-align: right;">Confident viol.</th>
<th style="text-align: right;">Coll. eMBB</th>
<th style="text-align: right;">Coll. URLLC</th>
<th style="text-align: right;">Coll. mMTC</th>
<th style="text-align: right;">Attack delivered</th>
<th style="text-align: right;">Fallback</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">RC-SIR-FS</td>
<td style="text-align: right;">0.000 [0.000, 0.009]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0172</td>
<td style="text-align: right;">0.0016</td>
<td style="text-align: right;">0.0099</td>
<td style="text-align: right;">0.496</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">Slice-FPR+block</td>
<td style="text-align: right;">0.000 [0.000, 0.009]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0117</td>
<td style="text-align: right;">0.0016</td>
<td style="text-align: right;">0.0092</td>
<td style="text-align: right;">0.526</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">RC-SIR</td>
<td style="text-align: right;">0.000 [0.000, 0.009]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0064</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0057</td>
<td style="text-align: right;">0.576</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">ERM</td>
<td style="text-align: right;">0.003 [0.000, 0.014]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0272</td>
<td style="text-align: right;">0.0029</td>
<td style="text-align: right;">0.0238</td>
<td style="text-align: right;">0.443</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Pooled LTT</td>
<td style="text-align: right;">0.000 [0.000, 0.009]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0276</td>
<td style="text-align: right;">0.0029</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.599</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">No action</td>
<td style="text-align: right;">0.000 [0.000, 0.009]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.971</td>
<td style="text-align: right;">1.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Oracle</td>
<td style="text-align: right;">0.000 [0.000, 0.009]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.00</td>
</tr>
</tbody>
</table>
</div>
```


## Confirmatory Study N (relocating actions)

**N-H1 (supported).** Under redirection, collateral exceeded the acted-benign fraction in 1.0% of episode–policy–slice entries, by up to 0.93. Two examples:

- Redirecting in eMBB at threshold 0.995 gave eMBB collateral 0.0272 against an acted fraction of 0.0146.
- Redirecting in eMBB at 0.95 caused URLLC collateral of 0.0055, although no URLLC UE was acted on.

**N-H2 (not supported).** Slice-FPR with redirection violated its budgets in 0.000 of 200 splits (95% CI up to 0.018). The finite-sample margin of the FPR test kept it at conservative thresholds, where the excess collateral stayed below the budgets.

A post-hoc large-sample analysis (not pre-registered) treats all 1500 episodes as the population:

- **Redirect study:** 31 of the 441 policies that satisfy the per-slice FPR criterion have collateral above a budget, all of them involving redirection. The largest excess is 0.0044.
- **Monotone study:** the corresponding count is 0, as Lemma 1 requires.

The FPR certificate is therefore invalid in principle under relocation. In this model the error was small enough to be masked by statistical slack.

**N-H3 (supported).** RC-SIR-FS violated in 0.000 of splits (CI up to 0.018). It also delivered less attack traffic (0.448) than Slice-FPR with redirection (0.533) or with blocking (0.546). This utility comparison is exploratory. ERM violated in 3.5% of splits.


```{=html}
<div class="span" id="tab:confirm_N"><div class="tbl-num">Table 6<br/>Study N, actions {block, redirect}, 200 splits (n_cal = 500). Redirect violates assumption A3.</div><table>
<colgroup>
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
<col style="width: 12%" />
</colgroup>
<thead>
<tr class="header">
<th style="text-align: left;">Method</th>
<th style="text-align: right;">Viol. freq. [95% CP CI]</th>
<th style="text-align: right;">Confident viol.</th>
<th style="text-align: right;">Coll. eMBB</th>
<th style="text-align: right;">Coll. URLLC</th>
<th style="text-align: right;">Coll. mMTC</th>
<th style="text-align: right;">Attack delivered</th>
<th style="text-align: right;">Fallback</th>
</tr>
</thead>
<tbody>
<tr class="odd">
<td style="text-align: left;">RC-SIR-FS</td>
<td style="text-align: right;">0.000 [0.000, 0.018]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0094</td>
<td style="text-align: right;">0.0022</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.448</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">Slice-FPR+redirect</td>
<td style="text-align: right;">0.000 [0.000, 0.018]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0202</td>
<td style="text-align: right;">0.0005</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.533</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">Slice-FPR+block</td>
<td style="text-align: right;">0.000 [0.000, 0.018]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0074</td>
<td style="text-align: right;">0.0011</td>
<td style="text-align: right;">0.0053</td>
<td style="text-align: right;">0.546</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">ERM</td>
<td style="text-align: right;">0.035 [0.014, 0.071]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0406</td>
<td style="text-align: right;">0.0064</td>
<td style="text-align: right;">0.0013</td>
<td style="text-align: right;">0.253</td>
<td style="text-align: right;">0.00</td>
</tr>
<tr class="odd">
<td style="text-align: left;">No action</td>
<td style="text-align: right;">0.000 [0.000, 0.018]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.967</td>
<td style="text-align: right;">1.00</td>
</tr>
<tr class="even">
<td style="text-align: left;">Oracle</td>
<td style="text-align: right;">0.000 [0.000, 0.018]</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.0000</td>
<td style="text-align: right;">0.000</td>
<td style="text-align: right;">0.00</td>
</tr>
</tbody>
</table>
</div>
```


## Cost

- Certification and selection on 500 episodes took 4.6 ms.
- Replay dominates: 0.122 ms per policy–episode evaluation in the fluid model on 4 vCPUs, i.e. about 0.16 s per calibration episode for 1331 policies.
- Slice-FPR needs no replay. A packet-level twin or testbed replay would be far slower, which favours Slice-FPR whenever its utility is comparable.

# Discussion {#sec:discussion}

The evidence supports a narrower answer than our exploratory study suggested.

**Under traffic-removing actions** (rate-limiting, blocking) and a monotone scheduler:

- Per-slice FPR certification is already a collateral certificate (Theorem 1).
- Direct certification did not deliver a confirmed improvement across independent scenarios.
- A gain appears only when the threshold grid contains points that the FPR test cannot certify but the collateral test can. In our replications this depended on the eMBB harm ratio and on how close the acted fraction was to the budget.
- Since Slice-FPR needs only benign scores and no replay, it is the reasonable default in this regime.

**When actions relocate traffic** (redirection to a scrubbing service over shared links, hairpinning, rerouting), the FPR criterion loses its justification. In the large-sample limit it accepted policies whose collateral exceeded the budget, including harm to slices in which no UE was acted on. Direct certification needs no monotonicity and remained valid. In Study N it also delivered less attack traffic than either FPR-certified variant, but that comparison was exploratory.

The practical recommendation is therefore to decide by *action type*:

- **Traffic-removing actions:** use per-slice FPR certification.
- **Traffic-relocating actions:** use direct, replay-based certification, and expect to need a replay engine with known fidelity.

**Cost of a guarantee.** In scenarios with slack budgets, the uncertified empirical rule mitigated more and rarely violated. A guarantee costs attack mitigation, and that cost is visible in our data.

# Limitations and Threats to Validity {#sec:limits}

**Simulation only.**

- All evidence comes from a fluid model with synthetic traffic.
- No 5G core, UPF or RAN was available to this study.
- Public 5G intrusion datasets [@siriwardhana2025nidd] lack slice labels and SLA outcomes, so they cannot provide $L^c_s$.
- The guarantees (Proposition 1) do not depend on the simulator; the utility comparisons and the size of the harm ratios do.
- Theorem 1 is proven for the modelled scheduler only. Congestion control, active queue management on shared queues, application retries and enforcement delay are not modelled; each could break monotonicity or change the harm ratios.

**Statistics.**

- Exploratory splits reuse one pool; confirmatory inference uses eight independent replications, which is a small number.
- Zero observed violations are consistent with the guarantee but say nothing about its tightness: realised collateral was well below the budgets.

**Not compared.**

- Model-based response policies [@hammar2022optimalstopping; @hammar2024dynamic].
- Adaptive attackers.
- Temporal dependence between episodes.

**Twin transfer.** Proposition 2 in Appendix [A](#app:proof) gives a valid but, at our sample sizes, vacuous guarantee.

# Conclusion {#sec:conclusion}

We compared two ways of certifying the collateral SLA harm of detector-triggered mitigation in a sliced user plane: certifying it directly from counterfactual replay, or certifying per-slice false-positive rates.

For the scheduler we model, a proof shows that traffic-removing actions cannot harm non-acted UEs. Per-slice false-positive certification is then a sufficient collateral certificate. Across eight pre-registered independent replications, direct certification did not improve attack mitigation by a confirmed margin, and its Bonferroni form was worse.

Relocating actions break the monotonicity argument: the false-positive criterion accepted policies with excess collateral, while direct certification remained valid.

The results argue for choosing the certificate by action type. They also identify what is still needed: monotonicity analysis for real UPF implementations, replay engines with bounded error, and slice-labelled traces with SLA outcomes.

# Appendix A: Proofs {#app:proof .unnumbered}

**Allocation.**

- The implemented scheduler first serves $\min(a_s,g_sC)$ and then divides leftover capacity in proportion to $w$ among classes with remaining demand.
- Each round either exhausts the leftover or saturates at least one class, so $|\mathcal{S}|$ rounds give the exact water-filling solution $x_s=\min(a_s,g_sC+w_s\theta)$.
- $\Phi(\theta;a)=\sum_s\min(a_s,g_sC+w_s\theta)$ is non-decreasing in $a$ and $\theta$, so $\theta$ is non-increasing in every $a_{s'}$. Hence:
  - the residual $r_s=\max(0,a_s-g_sC-w_s\theta)$ is non-decreasing in every coordinate of $a$;
  - $r_s>0$ implies $x_s=g_sC+w_s\theta$.

**Queues.** With $q_s(t+1)=\min(B_s,r_s(t))$ and overflow $O_s(t)=\max(0,r_s(t)-B_s)$, componentwise smaller arrivals in every slot give $q'\le q$ and $O'\le O$, by induction.

**Proof of Theorem 1.** Fix slot $t$ and slice $s$ of a non-acted benign UE. Let $A_s$ be the slot's arrivals and $\Delta=A_s-A'_s\ge0$.

- **Drop fraction.**
  - If $O'>0$, then $r'_s>0$, so $x'_s=g_sC+w_s\theta'\ge g_sC+w_s\theta\ge x_s$.
  - Since $O\ge O'>0$, $O=q+A_s-x_s-B_s$.
  - Then $O'\le O-\Delta$, and $f'=O'/(A_s-\Delta)\le(O-\Delta)/(A_s-\Delta)\le O/A_s=f$, using $O\le A_s$ (because $q\le B_s$).
- **Delay.**
  - If $q'(t+1)>0$, both residuals are positive, so $x'_s\ge x_s\ge g_sC>0$ and delay$'=q'(t+1)/x'_s\le q(t+1)/x_s=$ delay.
- **SLA indicators.** The UE's own arrivals are unchanged. Its delivered fraction $\sum_tD_u(t)(1-f_s(t))$ and its 95th-percentile delay over unchanged active slots are therefore monotone. ∎

**Proposition 2 (twin transfer).** Suppose $|\tilde{R}^c_s(\lambda)-R^c_s(\lambda)|\le\varepsilon_s$ for all $\lambda,s$ on an event of probability at least $1-\eta$. Certifying the twin at $\alpha_s-\varepsilon_s$ gives $\Pr\{\forall s:R^c_s(\hat{\lambda})\le\alpha_s\}\ge1-\delta-\eta$, by a union bound. Estimating $\varepsilon_s$ from $m$ paired episodes requires a uniform deviation term of order $\sqrt{\log(|\mathcal{S}||\Lambda|/\eta)/2m}$, which is about 0.14 at $m=300$.

# Appendix B: Disclosed Deviations {#app:deviations .unnumbered}

1. **First simulator.** It had a single traffic regime and yielded a detector with AUC 0.99999, which made every method trivially valid. It was replaced by the benchmark/operational regime model before method results were analysed, and archived.
2. **Selection objective.** The first full exploratory analysis used $J$ as the selection objective, contrary to the pre-specified objective $R^a$. This was corrected; the $J$-objective results are archived.
3. **Recommended variant.** RC-SIR-FS was chosen as the recommended variant after the exploratory results. The confirmatory studies were designed to test it on new data.
4. **Supervised detector.** A gradient-boosting detector with saturated scores made all methods coincide. It is reported only in the repository.
