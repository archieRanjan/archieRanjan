# Introduction {#sec:intro}

Network slicing places services with very different tolerances on shared user-plane resources. A URLLC slice tolerates a few milliseconds of queueing; an eMBB slice is judged on sustained throughput; an mMTC slice on delivery of sparse reports. When an intrusion detector flags a user equipment (UE), the operator can rate-limit or block its traffic at the user-plane function (UPF). Neither action is free. A benign UE that is wrongly blocked loses its service, and a rate-limited bursty URLLC client misses its deadline. The cost of a false alarm is therefore set by the *action* taken and by the *slice* in which it is taken, not by the alarm alone [@sommer2010outside; @arp2022dos].

Recent work has made the false-alarm side of intrusion detection statistically controllable. Conformal outlier tests give finite-sample false-positive or false-discovery guarantees [@bates2023outliers]. Several 2025–2026 detectors calibrate alert thresholds against an explicit false-positive budget using conformal risk control or conformal evaluation [@youssef2026caliburn; @barrett2026firce; @farzaneh2025ccoad; @barbero2022transcendent]. What these methods certify is an *alert-level* quantity. Intrusion-response work, conversely, optimises the choice of defensive actions, but with model-based guarantees that hold only relative to an assumed attacker and system model [@hammar2022optimalstopping; @hammar2024dynamic; @zonouz2014rre]. Neither line of work certifies the quantity an operator of a sliced network is accountable for: the fraction of benign users in each slice whose service-level agreement (SLA) is broken *because of* the mitigation.

This paper asks one question:

> *In a sliced 5G user plane where detector-triggered mitigation is calibrated offline, does certifying each slice's action-induced SLA-violation risk directly admit more attack mitigation than certifying each slice's false-positive rate, at the same per-slice budgets and confidence level, and under what conditions?*

The question is not rhetorical. We show (Lemma 1) that when the user-plane scheduler is *monotone* (removing traffic never worsens the service of other UEs), the action-induced collateral of a slice is bounded by its acted-benign fraction. A per-slice false-positive-rate certificate is then also a valid collateral certificate. Direct certification can only win through the gap between the two, which we call the *harm ratio*, and must pay for it with a larger hypothesis space and the need to evaluate counterfactual outcomes.

**Contributions.**

1. We formalise *action-induced collateral risk* per slice against the no-action counterfactual, and prove that under scheduler monotonicity it is upper-bounded by the per-slice acted-benign fraction (Lemma 1). This identifies per-slice certified false-positive control as the correct strong baseline and isolates the harm ratio as the only source of possible gain (Remark 1).
2. We give a replay-based certification procedure, RC-SIR, that applies Learn-then-Test (LTT) risk control [@angelopoulos2025ltt] over a space of 1331 per-slice multi-action policies. It uses union-null p-values across slices and either Bonferroni or data-split fixed-sequence family-wise error control. We also prove a transfer result for calibrating on a replay twin with bounded error (Proposition 2). The statistical machinery is existing; the contribution is the formulation, the structural result that determines when the machinery helps, and its measured consequences.
3. We report a reproducible simulation study of a three-slice user plane with a detector deployed under domain shift (Isolation Forest, pool AUC {{setup::iforest::auc_pool@.3f}}). Over 200 calibration/test splits:
    - No certified method exceeded its budgets.
    - Uncalibrated constrained selection did, in {{ncal::100::ERM (no margin)::viol_freq@pct}} of splits at 100 calibration episodes.
    - With fixed-sequence testing, direct certification delivered {{main::RC-SIR-FS (ours)::attack_delivered_mean@.3f}} of attack traffic, against {{main::Slice-FPR certified + block::attack_delivered_mean@.3f}} for per-slice FPR certification (better in {{paired::RC-SIR-FS vs Slice-FPR::frac_splits_A_better_attack@pct}} of paired splits).
    - The advantage disappears with small calibration sets, at halved or doubled budgets, and with Bonferroni control. Multi-action policies brought no measurable benefit.

All results come from a fluid simulator, not from a 5G testbed. Section [8](#sec:limits) discusses what this does and does not establish.

# Related Work {#sec:related}

**Evaluation validity of ML-based intrusion detection.**

- Operational cost of errors and evaluation pitfalls are long-standing concerns [@sommer2010outside; @arp2022dos].
- Benchmark datasets contain labelling and design flaws [@engelen2021troubleshooting; @flood2024smells].
- Detectors degrade sharply across domains [@layeghy2023xcross].
- 5G-specific datasets report near-perfect detection [@siriwardhana2025nidd; @khan2023slicesecure; @amponis2022pfcp], while adversarial evaluation of 5G-core detectors exposes fragility [@manca2026sage5gc].

Our first simulator version reproduced the near-perfect-detection artefact; we discarded it for that reason (Section [8](#sec:limits)).

**Calibrated intrusion detection.** Conformal p-values support exact FDR control for outlier detection [@bates2023outliers]. TRANSCENDENT uses conformal evaluation to reject drifting samples [@barbero2022transcendent]. FIRCE couples conformal evaluators with drift-triggered retraining [@barrett2026firce]. CALIBURN sets streaming alert thresholds by regime-dependent conformal risk control under a false-positive budget [@youssef2026caliburn]. An online conformal detector controls a smoothed false-discovery rate [@farzaneh2025ccoad]. All of these certify detector outputs. None certifies the service-level effect of the action taken on an alert, and none partitions the guarantee by slice. Our per-slice FPR baseline is the natural slice-stratified extension of these methods.

**Risk control.**

- Conformal risk control bounds monotone losses [@angelopoulos2024crc].
- LTT handles non-monotone and multiple risks by multiple testing [@angelopoulos2025ltt].
- Weighted and online variants address shift [@tibshirani2019weighted; @barber2023beyond; @gibbs2021aci].
- Conformal policy control regulates a new policy against a safe reference policy [@prinster2026cpc].
- Prediction-powered risk control uses unlabelled data to reduce conservativeness [@einbinder2025ssrc].

RC-SIR uses LTT without modification. Its departure is in what is certified (counterfactual, slice-indexed SLA outcomes) and in the structural analysis of when certification of that quantity is worth its cost.

**Intrusion response and mitigation.**

- Hammar and Stadler derive threshold-structured optimal response policies via optimal stopping and stochastic games [@hammar2022optimalstopping; @hammar2024dynamic].
- RRE selects responses in a partially observable game [@zonouz2014rre].
- Switch-native systems mitigate volumetric DDoS at line rate [@liu2021jaqen].

These works optimise response quality under a model; they do not provide distribution-free bounds on collateral harm. Our policies have the threshold structure these works motivate.

**Slicing.**

- RAN slicing with performance isolation [@foukas2017orion].
- Overbooking [@salvat2018overbooking] and asymmetric SLA-cost forecasting [@bega2019deepcog] show that slices share and borrow capacity, which is the coupling our scheduler models.
- Network digital twins [@ferriolgalmes2023routenetfermi] are candidate replay engines for the counterfactual evaluation that RC-SIR requires.
- Attacks on learned slicing controllers produce slice-dependent SLA violations [@tashman2026adversarial].

Table [1](#tab:cmp) summarises the comparison.

{{table:comparison}}

# System Model and Problem Formulation {#sec:model}

**User plane.** An egress link of capacity $C$ serves slices $s \in \mathcal{S}=\{\mathrm{eMBB},\mathrm{URLLC},\mathrm{mMTC}\}$. Slice $s$ is guaranteed $g_s C$ and may borrow idle capacity up to $C$, as in hierarchical token-bucket sharing. Each slice has a finite FIFO buffer; within a slice, drops and queueing delay are shared by its UEs. Time is slotted.

**Episodes and detector.** An episode $e$ consists of an observation window of $T_o$ slots and an action window of $T_a$ slots. A detector maps the observation-window features of UE $u$ to a score $z_u \in [0,1]$. $\mathcal{B}_s(e)$ is the set of benign UEs of slice $s$ in episode $e$.

**Policies.** A policy $\pi_\lambda$ is parameterised by $\lambda=(\tau_s,a_s)_{s\in\mathcal{S}}$, a threshold and an action $a_s\in\{\mathsf{RL},\mathsf{B}\}$ (rate-limit to a slice-specific cap, or block). Every UE of slice $s$ with $z_u\ge\tau_s$ receives action $a_s$ for the whole action window; $\tau_s=\infty$ means no action. $\pi_0$ takes no action. With five thresholds and two actions per slice, $|\Lambda|=11^3=1331$.

**SLA outcomes.** $V_u(e;\pi)\in\{0,1\}$ indicates that benign UE $u$ violates its slice SLA during the action window under policy $\pi$:

- eMBB: delivered/offered ratio below 0.90;
- URLLC: 95th-percentile queueing delay above 2 slots, or delivery below 0.99;
- mMTC: delivery below 0.95.

**Definition 1 (action-induced collateral).** For slice $s$ and policy $\pi_\lambda$,
$$L^{c}_s(e;\lambda)=\frac{1}{|\mathcal{B}_s(e)|}\sum_{u\in\mathcal{B}_s(e)}\mathbb{1}\{V_u(e;\pi_\lambda)=1,\;V_u(e;\pi_0)=0\},\qquad R^{c}_s(\lambda)=\mathbb{E}_e[L^{c}_s(e;\lambda)].$$
The counterfactual $\pi_0$ separates harm caused by mitigation from harm caused by the attack itself.

**Objective.** Let $L^{a}(e;\lambda)\in[0,1]$ be the fraction of attack traffic delivered under $\pi_\lambda$ in an episode containing attackers, and $R^a(\lambda)$ its expectation. The operator seeks
$$\min_{\lambda\in\Lambda} R^{a}(\lambda)\quad\text{s.t.}\quad R^{c}_s(\lambda)\le\alpha_s\;\;\forall s\in\mathcal{S},$$
and requires the selected $\hat{\lambda}$ to satisfy all constraints with probability at least $1-\delta$ over the calibration data.

**Assumptions.**

- **A1:** calibration and deployment episodes are i.i.d. draws from the same distribution.
- **A2:** $L^c_s(e;\lambda)$ can be evaluated for every $\lambda$ on a calibration episode by replaying its traffic, either in a replay engine or in a twin whose error is bounded as in Proposition 2.
- **A3 (monotone scheduling):** if the offered traffic of a set of UEs is reduced pointwise in time, no other UE's delivered fraction decreases and no other UE's queueing delay increases.

A3 holds for work-conserving fair schedulers with per-UE policing applied before queueing. It can fail with congestion-control feedback or non-work-conserving shapers. For our simulator we verify it numerically rather than analytically (Section [6](#sec:results)).

**Lemma 1.** Under A3, for every episode $e$, policy $\lambda$ and slice $s$,
$$L^{c}_s(e;\lambda)\le F_s(e;\tau_s):=\frac{1}{|\mathcal{B}_s(e)|}\sum_{u\in\mathcal{B}_s(e)}\mathbb{1}\{z_u\ge\tau_s\}.$$

*Proof.* Let $u\in\mathcal{B}_s(e)$ with $z_u<\tau_s$, so $u$ is not acted on. Under $\pi_\lambda$ the offered traffic of every other UE is pointwise no larger than under $\pi_0$, and $u$'s own traffic is unchanged. By A3, $u$'s delivered fraction is no smaller and its delay no larger under $\pi_\lambda$. Hence $V_u(e;\pi_\lambda)\le V_u(e;\pi_0)$, and $u$ contributes zero to $L^c_s$. Only acted UEs can contribute, each at most $1/|\mathcal{B}_s(e)|$. ∎

**Remark 1 (where a gain can come from).** Write $R^{c}_s(\lambda)=\rho_s(\lambda)\,\Phi_s(\tau_s)$, with $\Phi_s(\tau)=\mathbb{E}[F_s(e;\tau)]$ and harm ratio $\rho_s\in[0,1]$. A per-slice FPR certificate admits only thresholds with $\Phi_s(\tau_s)\le\alpha_s$. Direct certification admits $\Phi_s(\tau_s)\le\alpha_s/\rho_s$. Direct certification can therefore select more aggressive thresholds only when $\rho_s$ is substantially below one *and* the threshold grid contains points in the band $(\alpha_s,\alpha_s/\rho_s]$, after allowing for the statistical margin of each test. The remark is an identity, but it predicts where the gain should and should not appear, and we test that prediction.

# Certification Procedure {#sec:method}

For each calibration episode $e_i$, $i=1,\dots,n$, the replay engine evaluates $L^c_s(e_i;\lambda)$ and $L^a(e_i;\lambda)$ for all $\lambda\in\Lambda$. Let $\hat{R}_s(\lambda)$ be the empirical mean of $L^c_s$ over the calibration episodes. For each $\lambda$ we test the union null $H_\lambda:\exists s,\;R^c_s(\lambda)>\alpha_s$ with the p-value
$$p_\lambda=\max_{s\in\mathcal{S}} p^{\mathrm{HB}}\big(\hat{R}_s(\lambda);\alpha_s,n\big),$$
where $p^{\mathrm{HB}}$ is the Hoeffding–Bentkus p-value for $[0,1]$-bounded losses used in LTT [@angelopoulos2025ltt]. The certified set $\hat{\Lambda}$ is obtained with family-wise error rate (FWER) control at level $\delta$, in one of two variants:

- **Bonferroni (RC-SIR):** $\hat{\Lambda}=\{\lambda: p_\lambda\le\delta/|\Lambda|\}$.
- **Fixed sequence (RC-SIR-FS):** the calibration set is split in half. The first half orders policies by $\max_s \hat{R}_s(\lambda)/\alpha_s$, ties broken by empirical attack delivery. The second half tests $H_\lambda$ in that order at level $\delta$, stopping at the first non-rejection.

The deployed policy is $\hat{\lambda}=\arg\min_{\lambda\in\hat{\Lambda}}\hat{R}^a(\lambda)$, computed on the full calibration set, with $\pi_0$ as the fallback when $\hat{\Lambda}=\emptyset$. Algorithm 1 summarises the procedure.

{{algorithm}}

**Proposition 1 (validity).** Under A1–A2, both variants satisfy $\Pr\{\forall s:\ R^c_s(\hat{\lambda})\le\alpha_s\}\ge1-\delta$.

*Proof.*

1. Under $H_\lambda$ there is a slice $s^\ast$ with $R^c_{s^\ast}(\lambda)>\alpha_{s^\ast}$. Since $p_\lambda\ge p^{\mathrm{HB}}_{s^\ast}$ and $p^{\mathrm{HB}}$ is super-uniform under that null, $p_\lambda$ is a valid p-value for $H_\lambda$.
2. Bonferroni controls the FWER at $\delta$. Fixed-sequence testing does too, because the ordering is a function of the first half only, and the second half is independent of it under A1.
3. On the complement of a family-wise error, every $\lambda\in\hat{\Lambda}$ satisfies all constraints, so any selection rule over $\hat{\Lambda}$, including one that uses all calibration data, inherits the guarantee.
4. The fallback $\pi_0$ has $R^c_s=0$. ∎

The result is a direct consequence of LTT [@angelopoulos2025ltt]; we state it to make the union-null construction and the selection step explicit.

**Corollary 1 (per-slice FPR baseline).** Certify for each slice the smallest threshold with $\Phi_s(\tau_s)\le\alpha_s$, testing thresholds from the most conservative downwards (valid fixed-sequence testing because $F_s$ is monotone in $\tau$) at level $\delta/|\mathcal{S}|$, and block above it. By Lemma 1 this also satisfies the collateral constraints with probability at least $1-\delta$. It requires no replay, only benign scores.

**Proposition 2 (calibration on a twin).** Suppose calibration uses twin losses $\tilde{L}^c_s$, and on an event $E$ with $\Pr(E)\ge1-\eta$, $|\tilde{R}^c_s(\lambda)-R^c_s(\lambda)|\le\varepsilon_s$ for all $\lambda,s$. Certifying the twin at budgets $\alpha_s-\varepsilon_s$ yields $\Pr\{\forall s: R^c_s(\hat{\lambda})\le\alpha_s\}\ge1-\delta-\eta$.

*Proof.* On $E$ intersected with the twin certification event, $R^c_s(\hat{\lambda})\le\tilde{R}^c_s(\hat{\lambda})+\varepsilon_s\le\alpha_s$. A union bound completes the proof. ∎

To estimate $\varepsilon_s$ we use $m$ paired twin/real episodes: $\hat{\varepsilon}_s=\max_\lambda m^{-1}\sum_j|\tilde{L}^c_s-L^c_s|+\sqrt{\log(3|\Lambda|/\eta)/(2m)}$. This is valid by Hoeffding's inequality with a union bound, because $|\tilde{R}-R|\le\mathbb{E}|\tilde{L}-L|$.

**Complexity.** Calibration costs $O(n|\Lambda||\mathcal{S}|)$ operations for the risk means plus $O(|\Lambda|)$ p-values. The dominant cost is replay: $|\Lambda|$ policy evaluations per calibration episode, each $O(UT_a)$ for $U$ UEs.

# Experimental Setup {#sec:setup}

**Simulator.**

- Capacity $C=100$ units/slot, guaranteed shares $(0.55,0.25,0.20)$, buffers $(200,12,60)$ units.
- 14, 10 and 16 benign UEs per slice; $T_o=30$, $T_a=120$ slots.
- With probability 0.6, an episode contains 1–4 attackers, placed in eMBB, URLLC and mMTC with probabilities $(0.45,0.15,0.40)$.
- Attack types: constant floods, pulsing floods, and (in deployment only) low-and-slow sources.
- Rate-limit caps are $(3.0,1.0,0.5)$ units/slot.

All parameters are listed in `code/sim.py` and recorded in `results/results.json`.

**Training versus deployment regime.** The detector is trained on a *benchmark* regime. Deployment episodes come from an *operational* regime that adds:

- more variable heavy eMBB users,
- URLLC alarm bursts and mMTC firmware-update bursts,
- attackers that mimic their slice's packet size in 70% of cases,
- an unseen low-and-slow attack class.

This models the cross-domain degradation documented for real detectors [@layeghy2023xcross].

**Detectors.** The primary detector is an Isolation Forest [@liu2008iforest] trained on benign benchmark-regime UEs. Its score is the empirical quantile of benign training scores, so thresholds are $\{0.9,0.95,0.99,0.995,0.999\}$. A gradient-boosting classifier trained on labelled benchmark-regime UEs is a secondary check. Both use scikit-learn [@pedregosa2011sklearn]. Each detector has seven per-UE features computed on the observation window only (mean, standard deviation, maximum, activity fraction, peak-to-mean ratio, mean absolute increment, mean packet size) plus slice indicators. Deployment pool AUCs were {{setup::iforest::auc_pool@.3f}} (Isolation Forest) and {{setup::gbm::auc_pool@.3f}} (gradient boosting).

**Data.** Seeds derive from one master seed (20261102) through independent `SeedSequence` streams:

- 600 training episodes (benchmark regime);
- a pool of 1500 deployment episodes ({{pool_stats::attack_episode_frac@pct}} containing attacks);
- 400 high-load deployment episodes (load factor in $[1.1,1.35]$ instead of $[0.6,1.1]$).

Every pool episode is replayed under all 1331 policies, $\pi_0$ and the oracle (which blocks exactly the attackers), for both detectors and for a twin that overestimates capacity by 8%.

**Protocol.**

- Budgets $\alpha=(0.05,0.02,0.05)$, $\delta=0.1$.
- Selection objective: mean delivered attack fraction over calibration episodes that contain attackers, plus $10^{-3}J$ as a tie-breaker, where $J=\sum_s w_s\,\overline{V}_s$ is the weighted benign SLA-violation rate with $w=(0.3,0.5,0.2)$.
- 200 random splits of the pool into $n=500$ calibration and 1000 test episodes.
- These settings and the objective were fixed before results were computed (Section [8](#sec:limits) records one implementation deviation and its correction).
- A split counts as a *violation* if any slice's realised test collateral exceeds its budget. Certified methods should violate in at most a fraction $\delta$ of splits.

**Baselines.** All baselines select among the same 1331 policies and the same replayed outcomes:

- **Slice-FPR:** Corollary 1, the strongest alert-level competitor.
- **Pooled LTT:** one shared $(\tau,a)$ certified on benign-averaged collateral.
- **Conformal FPR 1%:** a single threshold with conformal benign FPR at most 1%, then block. This is the operating point of alert-level calibrated detectors.
- **Fixed threshold:** block above the 99th benign-training percentile.
- **ERM:** minimise empirical $\hat{R}^a$ subject to $\hat{R}_s\le\alpha_s$, without a statistical margin.
- **No action and Oracle:** reference points.

A model-based optimal-stopping response [@hammar2022optimalstopping] is not reproduced; Section [8](#sec:limits) explains why.

# Results {#sec:results}

**Assumption checks.**

- **A3.** Over all $1500\times1331\times3$ episode–policy–slice combinations, collateral never exceeded the acted-benign fraction by more than {{lemma1_check::max_excess_collateral_over_acted_fraction@.1e}}, which is float32 rounding.
- **Unit tests.** A randomised test over 1000 arbitrary per-UE action patterns found no non-acted UE whose SLA status worsened.
- **Harm ratio.** Pooled over acted policies it was {{lemma1_check::mean_ratio_collateral_to_acted_fraction_when_acted@.2f}}, but it varies strongly with slice and action (Table [4](#tab:harm)):
    - about {{harm_ratio::eMBB|0.99|block::rho@.2f}} for eMBB at threshold 0.99;
    - about {{harm_ratio::URLLC|0.99|block::rho@.2f}} for URLLC;
    - {{harm_ratio::mMTC|0.95|RL::rho@.2f}} for rate-limiting in mMTC, against {{harm_ratio::mMTC|0.95|block::rho@.2f}} for blocking there.

  By Remark 1, direct certification can gain mainly in eMBB.

**Validity and the main comparison.** Table [2](#tab:main) reports the main comparison. No certified method exceeded its budgets in any of the 200 splits. ERM, which enforces the budgets only empirically, violated them in {{main::ERM (no margin)::viol_freq@pct}} of splits at $n=500$. As $n$ decreases this rises to {{ncal::250::ERM (no margin)::viol_freq@pct}} at $n=250$ and {{ncal::100::ERM (no margin)::viol_freq@pct}} at $n=100$ (Fig. [2](#fig:ncal)). At $n=500$ the ERM violation frequency equals the nominal $\delta$, so at that calibration size the empirical rule is not worse than the target level; the certificate matters at smaller $n$. The realised collateral of the certified methods stayed well below the budgets (for example {{main::RC-SIR-FS (ours)::collateral_mean::0@.3f}} against 0.05 in eMBB), which shows that the certificates are conservative. Fig. [1](#fig:collateral) shows the distribution of realised collateral.

{{table:main}}

{{figure:fig_collateral|Realised test collateral per slice over 200 splits (log-linear axis); dashed lines are the budgets.}}

**Direct versus FPR certification.** With fixed-sequence testing, RC-SIR-FS delivered {{main::RC-SIR-FS (ours)::attack_delivered_mean@.3f}} of attack traffic, against {{main::Slice-FPR certified + block::attack_delivered_mean@.3f}} for Slice-FPR. Paired over identical splits (Table [3](#tab:paired)), the mean difference was {{paired::RC-SIR-FS vs Slice-FPR::attack_delivered_diff_mean@+.3f}}, and RC-SIR-FS was better in {{paired::RC-SIR-FS vs Slice-FPR::frac_splits_A_better_attack@pct}} of splits. The 97.5% quantile of the difference was {{paired::RC-SIR-FS vs Slice-FPR::attack_delivered_diff_q::2@+.3f}}: in a minority of splits the half-sample split costs more than the harm-ratio gain.

The modal RC-SIR-FS policy blocked at threshold 0.99 in eMBB, where Slice-FPR certified only 0.995. At 0.99 the eMBB acted-benign fraction is {{harm_ratio::eMBB|0.99|block::acted_benign_frac@.3f}}. That is below the 0.05 budget, but too close to it for the Hoeffding–Bentkus test to certify at level $\delta/3$ with 500 episodes. The collateral at the same threshold, {{harm_ratio::eMBB|0.99|block::collateral@.3f}}, leaves enough margin. The gain is thus the statistical-margin component of Remark 1, not the deterministic band.

With Bonferroni control, RC-SIR was *worse* than Slice-FPR in every split (mean difference {{paired::RC-SIR vs Slice-FPR::attack_delivered_diff_mean@+.3f}}). Correcting over 1331 hypotheses costs more margin than the harm ratio returns.

Against pooled certification and the alert-level operating points, direct certification delivered less attack traffic ({{main::Pooled LTT::attack_delivered_mean@.3f}} for Pooled LTT, {{main::Conformal FPR 1% + block::attack_delivered_mean@.3f}} for 1% conformal FPR).

{{table:paired}}

**When the advantage disappears.**

- **Small calibration sets.** At $n\le250$ RC-SIR-FS often fell back to no action, or certified less than Slice-FPR, which needs no replay and tests only five monotone thresholds per slice (Fig. [2](#fig:ncal)). At $n=250$ the delivered attack fractions were {{ncal::250::RC-SIR-FS (ours)::attack_delivered_mean@.3f}} versus {{ncal::250::Slice-FPR certified + block::attack_delivered_mean@.3f}}; at $n=1000$, {{ncal::1000::RC-SIR-FS (ours)::attack_delivered_mean@.3f}} versus {{ncal::1000::Slice-FPR certified + block::attack_delivered_mean@.3f}}.
- **Other budgets.** Halving the budgets gave {{sensitivity::0.5::RC-SIR-FS (ours)::attack_delivered_mean@.3f}} versus {{sensitivity::0.5::Slice-FPR certified + block::attack_delivered_mean@.3f}}; doubling them gave {{sensitivity::2.0::RC-SIR-FS (ours)::attack_delivered_mean@.3f}} versus {{sensitivity::2.0::Slice-FPR certified + block::attack_delivered_mean@.3f}}. Both are effectively ties, because no grid threshold falls in the band of Remark 1.
- **Action space.** Restricting RC-SIR-FS to block-only policies changed the delivered attack fraction from {{ablation::RC-SIR-FS multi-action (full)::attack_delivered_mean@.3f}} to {{ablation::RC-SIR-FS block-only actions::attack_delivered_mean@.3f}}. Rate-limiting is harmless in mMTC, but at the selected thresholds it also lets more attack traffic through, so it is rarely chosen.
- **Saturated detector.** With the gradient-boosting detector, whose scores are saturated (no benign UE scored above 0.5), every method selected the same policy ({{gbm::RC-SIR (ours)::attack_delivered_mean@.3f}} delivered).

{{figure:fig_ncal|Left: budget-violation frequency versus calibration size (dashed line: $\delta$). Right: delivered attack fraction versus calibration size.}}

**Load shift.** Calibrating on nominal-load episodes and testing on high-load episodes produced no violations for RC-SIR-FS ({{shift::RC-SIR-FS (ours)::viol_freq@.3f}}), because collateral in this model is driven by acting on benign UEs, which load changes little. Recalibrating on only 200 shifted episodes left too few samples to certify any policy (fallback rate {{shift::RC-SIR recalibrated on shifted data (n=200)::fallback_rate@.2f}}). We do not claim robustness to shifts that change benign score distributions.

**Twin calibration.** Calibrating on a twin with 8% optimistic capacity, without correction, produced no violations ({{twin::Twin, no correction::viol_freq@.3f}}). The largest per-slice mean twin/real gap was {{twin_mean_abs_gap_per_slice::0@.3f}} (eMBB). The rigorous correction of Proposition 2 with $m=300$ paired episodes subtracts a Hoeffding term of about 0.14, larger than every budget, so the certified set was always empty (fallback rate {{twin::Twin, Hoeffding gap correction (Prop. 1)::fallback_rate@.2f}}). A plug-in correction without the concentration term retained most of the utility ({{twin::Twin, plug-in gap correction::attack_delivered_mean@.3f}} delivered) but is not covered by Proposition 2. A practical twin-transfer certificate needs a tighter, policy-specific bound.

**Cost.**

- Selection and certification on 500 episodes took {{cost::rcsir_calibration_s_median@ms}} ms (median).
- Replay dominates: {{cost::policy_episode_evaluations@,}} policy–episode evaluations took {{cost::generate_wallclock_s_4vcpu@.0f}} s on 4 vCPUs, i.e. {{cost::ms_per_policy_episode_evaluation_4vcpu@.3f}} ms each in this fluid model.
- A packet-level twin or a testbed would be orders of magnitude slower per evaluation. This favours Slice-FPR whenever replay is expensive.

{{table:harm_ratio}}

# Discussion {#sec:discussion}

The answer to the research question is conditional. Certifying action-induced collateral directly admitted more mitigation than certifying false-positive rates only when three conditions held:

1. the harm ratio of the slice that limits the policy was well below one;
2. the threshold grid had points in the resulting band;
3. there were enough calibration episodes for a powerful testing procedure (fixed-sequence ordering rather than Bonferroni).

When any of these failed, per-slice FPR certification was as good or better, and much cheaper, because it needs only benign detector scores rather than counterfactual replays.

For operators this suggests a practical order of work:

1. Certify per-slice FPR first. Under a monotone scheduler (Lemma 1) it already bounds collateral.
2. Estimate harm ratios per slice and action.
3. Invest in replay-based certification only where those ratios are small.

# Limitations and Threats to Validity {#sec:limits}

**Simulation only.** All results come from a fluid model of a three-slice egress link with synthetic traffic, not from a 5G core, a RAN or real traces. The checkpoint that preceded this study found no accessible testbed. 5G-NIDD [@siriwardhana2025nidd] could not be retrieved in the execution environment, and it carries no slice labels or SLA outcomes, so it could not supply $L^c_s$. The guarantees are properties of the procedure under A1–A3 and do not depend on the simulator; the *utility* comparisons do.

**Assumption A3.** Monotonicity was verified for our scheduler, not for real UPF implementations. Congestion-controlled transports, active queue management and adaptive application behaviour can violate it. If A3 fails, Lemma 1 and Corollary 1 fail, and per-slice FPR certification no longer bounds collateral. Direct certification (Proposition 1) does not need A3.

**Design iterations, disclosed.**

1. *First traffic model.* It used a single regime and gave a detector with AUC 0.99999, under which every method trivially met its budgets. We replaced it with the train/deploy regime model before analysing method results, and archived it.
2. *Objective.* The first full analysis used the benign-violation index $J$ as the selection objective, contrary to the pre-specified formulation (minimise $R^a$). Under $J$ the constraints were never active and no method violated its budgets. We corrected the objective; the $J$-objective results are archived.
3. *Recommended variant.* Both certification variants were specified before results. Recommending the fixed-sequence variant is a post-hoc choice that the results motivated.

The full record is in `DESIGN_LOG.md` and `research_decisions.md`.

**Statistics.**

- The 200 splits reuse one pool of 1500 episodes, so split-level summaries describe variability over calibration draws, not independent replications. We therefore report quantiles and win fractions rather than p-values for method differences.
- A violation frequency of zero over 200 splits is consistent with the target $\delta=0.1$, but it does not show that the bound is tight. The budgets were rarely binding for certified methods.

**Episodes.** Actions are fixed for the whole action window. Episodes are i.i.d. by construction, whereas real traffic has temporal dependence that A1 ignores.

**Baselines not reproduced.** Model-based intrusion-response policies [@hammar2022optimalstopping; @hammar2024dynamic] require an attacker model and simulator interface that we did not reimplement faithfully. They optimise a different criterion and provide no collateral certificate, so they would answer a different question.

# Conclusion {#sec:conclusion}

We asked whether certifying the per-slice SLA collateral of mitigation actions buys more attack mitigation than certifying per-slice false-positive rates. Under a monotone user-plane scheduler, false-positive certification already bounds collateral. Direct certification can only exploit the harm ratio, at the price of counterfactual replay and a larger hypothesis space.

In our simulation study both certified approaches always met their budgets, while uncalibrated selection did not. Direct certification with fixed-sequence testing reduced delivered attack traffic relative to per-slice FPR certification in most calibration draws at nominal budgets and moderate calibration sizes. It lost that advantage with small calibration sets, at other budget levels, and with Bonferroni control.

Validating A3 on a real UPF, obtaining slice-labelled traces with SLA outcomes, and tightening twin-transfer bounds are the steps needed before these findings can inform deployment.
