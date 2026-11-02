# Introduction {#sec:intro}

This report is **Checkpoint 1** of an independent research-discovery mission. The mission asks for a novel, feasible, and defensible IEEE Transactions-level research problem in 5G/6G systems. Its deliverable is a *validated research direction and an executable plan*, not a manuscript with results. As the brief requires, the report stops after the initial checkpoint (Stages A–F, preliminary forms only). It contains **no experimental results and no performance numbers** for any proposed method. Every claim is tagged with one of four evidence levels:

- **[Verified]**: confirmed in a retrieved bibliographic or repository record.
- **[Inference]**: an evidence-supported inference by the authors of this report.
- **[Hypothesis]**: a falsifiable statement that has not yet been tested.
- **[Unverified]**: could not be checked in this session.

**Summary of the provisional outcome.** We screened 75 sources across ten 5G/6G research areas. Of these, 72 papers and preprints are usable; 3 entries are excluded from that count (2 software artefacts and 1 unconfirmed preprint). From them we generated eleven candidate problems. Six were rejected under the mandatory criteria and five retained; the three highest-scoring retained candidates (C1, C3, C6) went to an adversarial novelty audit. The most important negative finding is this: *detection-level* conformal false-alarm control for intrusion detection, the direction that best matched the team's prior background, has become crowded in 2025–2026 [@youssef2026caliburn; @barrett2026firce; @confid2026; @robustcids2026; @farzaneh2025ccoad]. It is therefore **rejected** as a primary topic.

The provisional primary recommendation moves the guarantee one layer down the control loop, from *alerts* to the *service-level consequences of mitigation actions*:

> **C1 — Risk-controlled, slice-aware intrusion response.** Calibrate detector-triggered mitigation policies (rate-limit, quarantine to a sinkhole slice, block) for a sliced 5G core. The calibration should come with a finite-sample, distribution-free guarantee that the *collateral SLA-violation risk imposed on benign users of each slice* stays below a slice-specific budget, while residual attack impact is minimised.

The backup is **C3**, SLA-weighted multi-slice quickest attack detection. Both recommendations are explicitly **provisional**. Section [9](#sec:gaps) lists the full-text reads and infrastructure checks that must pass before Phase 2.

# Methodology of this checkpoint {#sec:method}

**Search protocol.** We ran targeted web searches (about 60 queries, standard and extended) on 2 November 2026. They covered ten topic clusters from the brief (Section [3](#sec:landscape)), plus explicit adversarial searches for each shortlisted claim (Section [6](#sec:audit)). For each source we recorded the citation, venue, year, DOI or preprint identifier, the problem, contribution, method, environment, findings, limitations, relevance, and verification status. The structured bibliography is `data/bibliography.json`. The matrix (`data/literature_matrix.csv`) and the BibTeX file are generated from it by `scripts/build_bib.py`.

**Verification levels.** Each entry is labelled V-DOI, V-META, V-PRE, PARTIAL, or UNVERIFIED (Table 1). **No DOI was guessed.** Where a DOI did not appear in any retrieved record, the field is left blank.

**Hard constraints of this session [Verified].** The container's network policy blocked arxiv.org, doi.org, api.crossref.org, OpenAlex, and Semantic Scholar (HTTP 403 or DNS failure). Only a search-engine interface was available. As a result:

1. **No full text was read.** Every entry was reviewed at the abstract and metadata level. Limitations marked [A] in the matrix are the authors' own statements; those marked [I] are our inferences and must be confirmed against the full text.
2. DOIs could not be resolved independently.
3. The repository supplied for this mission was **empty**: no prior manuscripts, code, configurations, logs, or datasets. Claims about the team's prior work and testbed therefore stay **[Unverified]**.

| Level | Meaning | Count |
|:--|:--|--:|
| V-DOI | Title, authors, venue, year, and DOI seen together in a retrieved record | 24 |
| V-META | Metadata verified; DOI not seen (left blank) | 20 |
| V-PRE | Preprint (or software artefact) exists; no peer-reviewed version confirmed | 19 |
| PARTIAL | Exists; at least one metadata field conflicts or is unconfirmed | 11 |
| UNVERIFIED | Seen once; must not be cited until checked | 1 |
| **Total** | 45 of the 75 entries are dated 2023–2026; 7 are surveys used only as background | **75** |

: Verification status of the structured bibliography.

**Honest assessment of the minimum literature target.** The brief asks for at least 60 *verified* relevant papers. We have 72 usable papers and preprints, so the count is met. The *depth* of verification is weaker than a Transactions-grade review requires: only 24 entries have a confirmed DOI, 19 are preprints, and none was read in full. We therefore treat the landscape as **sufficient for screening and ranking, but not for final novelty claims**. Phase 1 of the roadmap (Section [8](#sec:roadmap)) closes this gap.

# Stage A — Research landscape {#sec:landscape}

Table 2 organises the evidence into ten clusters. The full per-paper matrix (75 rows × 19 fields) is supplied as `data/literature_matrix.csv`.

| # | Cluster | Representative verified works | State of the art (evidence level) | Open space |
|:-:|:--|:--|:--|:--|
| L1 | Validity of ML-NIDS evaluation | [@sommer2010outside; @arp2022dos; @pendlebury2019tesseract; @engelen2021troubleshooting; @flood2024smells; @apruzzese2023sok; @jacobs2022emperor] | Benchmark results are inflated by sampling bias, temporal leakage, label errors, and shortcut features. There is a broad consensus that false-positive cost, not accuracy, blocks deployment. [Verified, abstract level] | Operational, cost-aware evaluation is still rare. |
| L2 | Cross-domain generalisation | [@layeghy2023xcross; @sarhan2022standard; @farzaneh2024dtl5g] | Detectors degrade sharply across datasets; NetFlow feature standardisation enables cross-testing. [Verified] | No 5G slice-aware cross-domain study found. [Inference] |
| L3 | 5G-specific security data and detection | [@samarakoon2022nidd; @siriwardhana2025nidd; @khan2023slicesecure; @amponis2022pfcp; @manca2026sage5gc; @slicespoof2025; @xu2025rogue] | Detection dominates. Reported accuracies are near-perfect (for example 99.99% in [@khan2023slicesecure], per its abstract). SAGE-5GC shows adversarial fragility. [Verified] | **Response and mitigation, and their service-level side effects, are almost absent.** [Inference] |
| L4 | Drift and conformal security | [@yang2021cade; @han2023owad; @barbero2022transcendent; @barrett2026firce; @youssef2026caliburn; @robustcids2026; @confid2026; @farzaneh2025ccoad; @rbsid2025] | 2025–2026 saw a surge of conformal and risk-calibrated IDS: FPR or FDR control, regime-dependent CRC, robustness to adversarial orbits. [Verified, preprint level] | Detection-level guarantees are now crowded; *action-level* guarantees are not. [Inference] |
| L5 | Distribution-free risk-control theory | [@tibshirani2019weighted; @barber2023beyond; @gibbs2021aci; @gibbs2024online; @bates2023outliers; @angelopoulos2024crc; @angelopoulos2025ltt; @crcnonmono2026; @cora2026; @cpc2026] | Mature tools exist for monotone (CRC) and non-monotone or multiple (LTT) risks, covariate shift, and online shift. Action gating with risk control is appearing in other domains (GUI agents). [Verified] | Not yet applied to coupled, multi-action network mitigation, as far as found. [Inference] |
| L6 | Intrusion response and mitigation | [@hammar2022optimalstopping; @hammar2024dynamic; @hammar2023recursive; @hammar2025conjectural; @zonouz2014rre; @regard2023; @liu2021jaqen] | Model-based optimal response (POMDPs, stochastic games, optimal stopping) yields threshold policies; line-rate DDoS mitigation exists in P4. [Verified] | No distribution-free guarantee on *collateral* harm; no slice awareness. [Inference] |
| L7 | Slicing and SLA-aware resource management | [@foukas2017survey; @foukas2017orion; @afolabi2018slicing; @bega2019deepcog; @salvat2018overbooking; @proactiveassurance2024] | Asymmetric SLA-violation costs and overbooking create cross-slice coupling. [Verified] | Coupling between security actions and SLAs is unexplored. [Inference] |
| L8 | O-RAN and AI-native RAN control | [@polese2023understanding; @polese2023coloran; @bonati2023openrangym; @bonati2021colosseum; @fiandrino2023explora; @brachdelprever2025pacifista; @groen2024implementing; @groen2024securing] | xApp development, explainability, conflict management (PACIFISTA, TMC 2025), interface security. [Verified] | All require RAN or RIC infrastructure that is not available here. |
| L9 | Adversarial attacks on learned slicing | [@shi2021attackdefend; @shi2021flooding; @tashman2026adversarial; @wang2023robustslicing] | Jamming and flooding against DRL slicing cause slice-dependent SLA violations. [Verified, preprint level] | Crowded, and it needs PHY access. |
| L10 | Digital twins, energy, FL, LLM, QCD | [@ferriolgalmes2023routenetfermi; @almasan2022ndt; @lopezperez2022energy; @lavaur2022fl; @flaccshield2026; @zhou2024llmtelecom; @boateng2025llm; @tartakovsky2006novel; @fellouris2016second; @qcdslice_github] | GNN twins give point predictions. Energy work needs RAN measurements. FL-IDS and LLM-ops are crowded or hype-driven. Multistream QCD theory is mature. [Verified] | Calibrated twins (C6) and SLA-weighted multi-slice QCD (C3) are moderately open. [Inference] |

: Structured research landscape.

**Cross-cutting observations.**

1. **[Inference]** The 5G security literature is stuck at the *detection* stage on near-saturated benchmarks. Clusters L1 and L4 already explain why accuracy claims are unreliable.
2. **[Verified]** Mature distribution-free risk-control tools (L5) exist, and conformal IDS work (L4) uses them, but only on *alert-level* quantities such as FPR, FDR, and alert budgets.
3. **[Inference]** The *service-level consequence* of acting on alerts is what operators pay for in a sliced network, and especially in URLLC. It is governed by model-based response theory (L6) that offers no finite-sample guarantee under model misspecification. It is also coupled across slices through shared resources (L7).

The intersection of points 2 and 3 is the gap pursued by C1.

**Coverage limitations.** PHY-layer and IEEE TWC-style original research (beamforming, ISAC, RIS) is under-represented. It was screened out early because nothing indicates that the team has PHY or SDR infrastructure (Section [7](#sec:feas)). This is a deliberate scoping decision, recorded in the decision log as D-04, not evidence that PHY topics are less important.

# Stage B — Candidate research problems {#sec:candidates}

We generated eleven candidates, one more than the ten required, so that the rejected C11 could be documented. Each is summarised along the brief's five dimensions: A (problem), B (novelty), C (technical depth), D (feasibility), and E (evaluation). The shortlisted candidates are expanded in Sections [6](#sec:audit) and [8](#sec:rec).

**C1 — Risk-controlled, slice-aware intrusion response.**

- *A.* Mitigation actions taken on imperfect detections (rate-limiting, quarantine, blocking) harm benign users. In a sliced core this harm propagates through shared UPF and transport resources, and its cost differs sharply by slice (URLLC versus mMTC). Current IDS work bounds alert-level error but not the SLA damage of the actions taken.
- *B.* Closest works: CALIBURN [@youssef2026caliburn] (FP-budgeted alerts), FIRCE [@barrett2026firce] ("response" means retraining), CORA [@cora2026] (risk-controlled action gating, non-network), Hammar & Stadler [@hammar2022optimalstopping] (model-based optimal response), and SliceSecure [@khan2023slicesecure] (slice detection only). **Missing piece [Inference]:** a distribution-free, per-slice guarantee on the *collateral SLA risk of a multi-action mitigation policy* under cross-slice coupling.
- *C.* Multi-risk LTT calibration over a structured policy space, counterfactual loss evaluation with a twin-error propagation bound, and robustness to temporal dependence and shift.
- *D.* Needs an emulated sliced 5G core (Open5GS or free5GC with UERANSIM), a traffic and attack harness, and KPI measurement. Moderate to high complexity. Main risk: the cost of counterfactual replay.
- *E.* See Section [8](#sec:rec).

**C2 — Slice-stratified conformal false-alarm control for 5G NIDS (detection only).**

- *A.* Bound the per-slice FPR of a detector.
- *B.* **Contradicted.** Marginal FPR and FDR control [@bates2023outliers], conformal IDS [@confid2026; @barbero2022transcendent; @barrett2026firce], regime-dependent CRC [@youssef2026caliburn], and online conformal FDR [@farzaneh2025ccoad] already exist. Stratifying by slice is a Mondrian-style re-grouping and too thin for a Transactions paper.
- *C.* Low.
- *D.* High feasibility.
- *E.* Straightforward.
- **Rejected:** gap contradicted.

**C3 — SLA-weighted multi-slice quickest attack detection.**

- *A.* Detect attack onset across slice streams so as to minimise *SLA-weighted* detection delay subject to *heterogeneous per-slice* false-alarm constraints, with streams coupled by shared resources.
- *B.* Closest works: [@tartakovsky2006novel; @fellouris2016second], plus an unpublished simulation [@qcdslice_github]. **Missing piece [Inference]:** heterogeneous delay weights and false-alarm constraints with coupled streams.
- *C.* Asymptotic optimality analysis is possible and necessary.
- *D.* Trace-driven evaluation is feasible.
- *E.* Delay versus ARL curves against CUSUM and SUM-CUSUM variants.
- **Risk:** the result may be a corollary of the existing multichannel theory.

**C4 — Leakage-audited cross-testbed benchmark for 5G NIDS.**

- **Rejected.** It probably overlaps the team's own leakage-audit work [Unverified: prior work not provided], and a 5G-NIDD realistic-split package already exists [@tvquynh2026repro]. Valuable as *infrastructure* for C1, not as the contribution.

**C5 — Conflict-aware xApp composition with guarantees.**

- **Rejected.** PACIFISTA [@brachdelprever2025pacifista] covers conflict detection and severity, and no RAN or RIC infrastructure has been verified.

**C6 — Calibrated-uncertainty GNN digital twin for slice SLA prediction.**

- *A.* GNN twins [@ferriolgalmes2023routenetfermi] give point estimates; operators need calibrated SLA-violation risk.
- *B.* No conformal-twin work was found in this session's searches, but **the search was shallow [Unverified]**.
- *C.* Conformal regression over graph-structured, exchangeability-breaking data.
- *D.* Feasible on public RouteNet datasets, but the 5G relevance is indirect (wired topologies).
- *E.* Coverage and width against Bayesian and ensemble GNNs.

**C7 — Adversarial robustness of DRL RAN-slicing controllers.**

- **Rejected.** It needs PHY, RAN, or SDR access, and the topic is crowded [@shi2021attackdefend; @tashman2026adversarial; @wang2023robustslicing].

**C8 — Uncertainty-aware RAN sleep-mode control.**

- **Rejected.** It needs RAN energy measurements [@lopezperez2022energy]; in simulation alone it cannot support operational claims.

**C9 — Federated slice-level IDS under non-IID data.**

- **Rejected.** Crowded [@lavaur2022fl; @flaccshield2026], with no identifiable new contribution.

**C10 — Adversarially robust 5GC PFCP anomaly detection.**

- *Retained but not shortlisted.* SAGE-5GC [@manca2026sage5gc] has just defined the evaluation protocol; a defence paper would be incremental unless it adds certified robustness [@robustcids2026].

**C11 — LLM-driven intent-based slice orchestration.**

- **Rejected.** Hype-driven, with no falsifiable evaluation possible without operator intents and data [@zhou2024llmtelecom; @boateng2025llm].

# Stage C — Weighted ranking {#sec:rank}

Scores run from 1 to 10 and use the brief's weights: novelty 25%, significance 20%, feasibility 20%, rigour 15%, validation 10%, fit 10%. They are computed reproducibly by `scripts/score.py` from `data/candidate_scores.csv`. **The weighted total summarises our judgement; it is not evidence of publishability.**

| Rank | ID | Nov. | Sig. | Feas. | Rig. | Val. | Fit | Weighted | Decision |
|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:--|
| 1 | C1 | 7 | 8 | 7 | 8 | 7 | 8 | 7.45 | Shortlist (primary) |
| 2 | C3 | 6 | 7 | 7 | 8 | 6 | 7 | 6.80 | Shortlist (backup) |
| 3 | C6 | 6 | 7 | 6 | 7 | 6 | 7 | 6.45 | Shortlist |
| 4 | C10 | 4 | 7 | 6 | 6 | 6 | 6 | 5.70 | Retained |
| 5 | C4 | 4 | 6 | 8 | 5 | 7 | 5 | 5.75 | Rejected (overlap) |
| 6 | C2 | 3 | 6 | 8 | 6 | 7 | 5 | 5.65 | Rejected (gap contradicted) |
| 7 | C8 | 5 | 8 | 2 | 6 | 3 | 7 | 5.15 | Rejected (infrastructure) |
| 8 | C5 | 4 | 8 | 2 | 7 | 3 | 7 | 5.05 | Rejected (prior work and infrastructure) |
| 9 | C9 | 3 | 5 | 7 | 5 | 5 | 4 | 4.80 | Rejected (no contribution) |
| 10 | C7 | 4 | 7 | 2 | 6 | 3 | 6 | 4.60 | Rejected (infrastructure and crowding) |
| 11 | C11 | 3 | 6 | 5 | 4 | 4 | 5 | 4.45 | Rejected (unfalsifiable) |

: Weighted ranking. Hard-rejected candidates are placed below retained ones regardless of score.

**Score justifications for the shortlist.**

- **C1, novelty 7 rather than 9.** The statistical mechanism (LTT) and the idea of risk-controlled action gating [@cora2026] both exist. Novelty must come from the *network-specific structure*: per-slice budgets, multi-action policies, cross-slice coupling, and counterfactual evaluation. That novelty is plausible but has not been confirmed against full texts of [@youssef2026caliburn; @rbsid2025; @cpc2026].
- **C1, feasibility 7.** An emulated core is standard practice, but the existing testbed has not been audited.
- **C3, rigour 8, novelty 6.** Strong theory is possible, but [@fellouris2016second] may already subsume the core result.
- **C6, feasibility 6.** Public datasets exist, but the 5G link is indirect.

# Stage D — Adversarial novelty audit {#sec:audit}

## C1: risk-controlled slice-aware intrusion response

**Five most threatening prior works.** These were identified from abstracts; full-text comparison is pending.

1. CALIBURN [@youssef2026caliburn]: regime-dependent CRC for alert thresholds under an FP budget.
2. FIRCE [@barrett2026firce]: "intrusion response" plus conformal evaluation, but the response is retraining.
3. CORA and Conformal Policy Control [@cora2026; @cpc2026]: risk-controlled gating of actions.
4. Hammar & Stadler [@hammar2022optimalstopping; @hammar2024dynamic]: optimal intrusion-response policies with threshold structure (IEEE TNSM).
5. SliceSecure and the sinkhole-slice idea [@khan2023slicesecure]: per-slice attack impact.

A sixth, RBSID [@rbsid2025], is risk-calibrated Bayesian decisions and must be read.

| Claim | CALIBURN | FIRCE | CORA/CPC | LTT | Hammar–Stadler | RRE | SliceSecure | Jaqen | Status of claim |
|:--|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:-:|:--|
| K1 Finite-sample distribution-free guarantee | ✓ (alerts) | ~ | ✓ | ✓ | ✗ | ✗ | ✗ | ✗ | **Not novel alone** |
| K2 Guarantee on service-level consequence of actions | ✗? | ✗ | ~ (generic harm) | — | ✗ (model-based cost) | ✗ | ✗ | ✗ | Plausibly novel [Inference] |
| K3 Heterogeneous per-slice budgets | ✗? | ✗ | ✗ | — | ✗ | ✗ | ✗ | ✗ | Plausibly novel; thin alone |
| K4 Multi-action, non-monotone policy calibration | ✗? | ✗ | ~ (CPC) | ✓ (tool) | ✓ (not distribution-free) | ✓ | ✗ | ✗ | Novel only in combination with K2 |
| K5 Cross-slice coupling via counterfactual replay or twin, with error bound | ✗ | ✗ | ✗ | ✗ | ~ (emulation) | ✗ | ✗ | ✗ | **Core novelty candidate** [Hypothesis] |
| K6 Validation on a sliced 5G core with measured SLA KPIs | ✗ | ✗ (IoT) | ✗ | ✗ | ✗ (IT) | ✗ | ~ (detection) | ✗ | Novel *if* the testbed exists |

: Claim-by-claim novelty matrix for C1 (✓ covered, ~ partially, ✗ not covered, ? unknown without full text, — not applicable).

**Incremental-novelty risk.** If K2–K5 reduce to "apply LTT to a new loss", reviewers will call the work an application paper. The contribution must therefore include:

- **(i)** a problem formulation in which collateral risk is defined against an *oracle-mitigation counterfactual*, so that it isolates harm due to detection and action error;
- **(ii)** a twin-in-the-loop calibration result that propagates surrogate error into the guarantee, with an empirical bound on that error;
- **(iii)** a quantified analysis of temporal dependence across episodes;
- **(iv)** evidence that alert-level control (K1 alone) *fails* to bound per-slice collateral risk, the key falsifiable claim.

**Strongest likely reviewer objections.**

1. "This is LTT applied to networking."
2. "The i.i.d.-episode assumption is unrealistic for traffic."
3. "Emulated RAN, so no 5G claims."
4. "The counterfactual replay is expensive; its fidelity is unproven."
5. "The baselines are straw men."

The plan in Section [8](#sec:rec) answers each one.

## C3: SLA-weighted multi-slice quickest detection

**Threats.** Multistream QCD with second-order optimality [@fellouris2016second]; adaptive CUSUM for intrusions [@tartakovsky2006novel]; an unpublished multi-slice QCD simulation reporting cross-slice coherence effects [@qcdslice_github]. Fewer than five threats were found because QCD-for-5G-slicing is sparsely published, but the mature general theory is itself the main threat.

**Novelty matrix (summary).** Heterogeneous false-alarm constraints per stream: *unknown*, possibly covered in the multichannel literature (not searched in depth). SLA-weighted delay: plausibly novel. Coupled streams due to shared resources: partially addressed in [@qcdslice_github].

**Objection.** "It is a corollary of known multichannel CUSUM results." **Verdict:** survives as the backup only.

## C6: calibrated GNN digital twin

**Threats.** RouteNet-Fermi [@ferriolgalmes2023routenetfermi] and the NDT vision paper [@almasan2022ndt]. We have **not** searched specifically for conformal or uncertainty-aware GNN network models; this is a known gap, G-07. **Verdict:** survives provisionally, ranked third.

# Stage E — Real-world feasibility audit {#sec:feas}

| Resource | Status | Evidence |
|:--|:--|:--|
| Compute (this session) | 4 vCPU, 15 GB RAM, no GPU, no LaTeX toolchain | **[Verified]** by inspection |
| Network egress (this session) | Search only; scholarly APIs and arXiv blocked | **[Verified]** by proxy logs |
| Prior manuscripts and code | Repository empty | **[Verified]** |
| 5G-NIDD | Public (IEEE DataPort, DOI 10.21227/xtep-hv36) | **[Verified]**, record only |
| 5GC PFCP dataset; SliceSecure dataset | Public on DataPort | **[Verified]**, record only; label-quality concern noted |
| 5G-SliciNdd (team dataset) | Not provided | **[Unverified]** |
| Team 5G testbed (eMBB/URLLC/mMTC shaping) | Described in the brief, not inspected | **[Unverified]**: core, RAN, UPF, orchestration, isolation, and mitigation hooks all unknown |
| Open-source sliced-core scaffolding | Open5GS Docker with per-slice UPF [@xu2025rogue] | **[Verified]** that the repository is referenced |
| RAN / SDR / RIC | None found | **[Unverified]**; treated as unavailable |

: Feasibility audit.

**Choice of validation method for C1.** The claims concern *core- and user-plane mitigation and the resulting per-slice KPIs*. An **emulated sliced 5G core** (Open5GS or free5GC with UERANSIM, a per-slice UPF, and tc/nftables enforcement) can test them directly. Radio realism is not required, provided the claims are restricted to that scope, and the emulated RAN will be stated as a threat to validity. It is combined with **trace-driven replay** from 5G-NIDD and the PFCP dataset for scale and repeated splits. Pure simulation is insufficient, because the collateral loss depends on real queueing and enforcement behaviour. A physical RAN is *not* required to test the hypotheses. **No new equipment is essential.** Access to and an audit of the team testbed is the main dependency (G-01).

# Stage F — Provisional recommendation {#sec:rec}

## Primary (provisional): C1

1. **Title (working).** *Certified Collateral-Risk Control for Slice-Aware Intrusion Response in 5G Networks*.
2. **Target journal.** IEEE Transactions on Network and Service Management (TNSM). Its scope covers security management, closed-loop automation, and service assurance, and it has published the closest response work [@hammar2022optimalstopping]. The alternative is IEEE TIFS if the theoretical component turns out to be stronger.
3. **Motivation and problem.** See C1 in Section [4](#sec:candidates).
4. **Closest work and remaining gap.** See Table 4.
5. **Formal hypothesis [Hypothesis].**
    - **H1 (validity):** under exchangeable calibration episodes, the calibrated policy keeps the realised per-slice collateral risk at or below $\alpha_s$ for every slice, with probability at least $1-\delta$.
    - **H2 (necessity):** a policy built on alert-level FPR control or pooled calibration, at the same nominal level, violates the URLLC collateral budget in a measurable fraction of splits.
    - **H3 (utility):** at equal certified collateral budgets, the method's residual attack impact is no worse than that of a model-based threshold response policy [@hammar2022optimalstopping] tuned on the same data.
6. **Candidate contributions.**
    - **(a)** The formulation: oracle-counterfactual collateral risk per slice.
    - **(b)** Twin-in-the-loop LTT calibration with surrogate-error propagation.
    - **(c)** A dependence- and shift-aware extension with a monitored recalibration trigger.
    - **(d)** An open, reproducible sliced-core mitigation testbed and benchmark protocol.
7. **Methodology.** Detector-agnostic: supervised gradient boosting and unsupervised Kitsune [@mirsky2018kitsune]. A structured threshold-policy family over actions. LTT with Hoeffding–Bentkus p-values and fixed-sequence or graph-based FWER control [@angelopoulos2025ltt].
8. **Formulation (preliminary).** Let $s\in\mathcal{S}$ index slices. Let $e$ be an episode (a time window), $\mathcal{B}_s(e)$ the set of benign UEs of slice $s$, and $\pi_\lambda$ a policy that maps detector scores and slice identity to actions in $\mathcal{A}=\{\emptyset,\mathsf{RL}(\rho),\mathsf{Q},\mathsf{B}\}$. With $V_u(e;\pi)$ the SLA-violation indicator of UE $u$ under policy $\pi$, and $\pi^\star$ oracle mitigation, define
    $$L^{c}_s(e;\lambda)=\frac{1}{|\mathcal{B}_s(e)|}\sum_{u\in\mathcal{B}_s(e)}\mathbb{1}\{V_u(e;\pi_\lambda)=1,\;V_u(e;\pi^\star)=0\},\qquad R^{c}_s(\lambda)=\mathbb{E}_e[L^{c}_s(e;\lambda)].$$
    Let $R^{a}(\lambda)$ be the expected residual attack impact. The target is
    $$\hat{\lambda}=\arg\min_{\lambda\in\hat{\Lambda}}\hat{R}^{a}(\lambda),\qquad \hat{\Lambda}=\{\lambda:\ H_{s,\lambda}:R^c_s(\lambda)>\alpha_s\ \mathrm{rejected}\ \forall s\},$$
    with FWER control at level $\delta$ over all pairs $(s,\lambda)$, which yields $\Pr\{\max_s(R^c_s(\hat{\lambda})-\alpha_s)\le 0\}\ge 1-\delta$. This follows from LTT [@angelopoulos2025ltt] and is *not* claimed as novel. **Proposition to be proved [Hypothesis]:** if a twin $\tilde{L}$ satisfies $|\tilde{L}^c_s-L^c_s|\le\varepsilon_s$ with probability at least $1-\eta$, then calibrating at $\alpha_s-\varepsilon_s$ certifies the real system at $\alpha_s$ with probability at least $1-\delta-\eta$. **To be developed:** a degradation term for $\beta$-mixing episodes or for TV-bounded shift, following [@barber2023beyond].
9. **Architecture.** Detector → score bus → policy engine (calibrated thresholds per slice and action) → enforcement at the UPF (N3/N6 nftables and tc per UE, keyed by TEID or IP; quarantine via re-association to a sinkhole S-NSSAI) → KPI telemetry → calibration store and drift monitor (for example OWAD-style [@han2023owad]).
10. **Data and testbed.** 5G-NIDD and PFCP traces for the replay arm. Team testbed or Open5GS-based emulation for counterfactual episodes. Benign traffic profiles per slice (eMBB bulk, URLLC periodic small packets, mMTC sparse).
11. **Baselines.**
    - B0: no mitigation.
    - B1: fixed-threshold block.
    - B2: conformal FPR-controlled detector with block (CALIBURN or Bates-style).
    - B3: pooled, non-slice LTT.
    - B4: cost-sensitive Bayes rule.
    - B5: optimal-stopping threshold response (T-SPSA) [@hammar2022optimalstopping].
    - B6: oracle (upper bound).

    **Ablations:** remove slice stratification; remove twin-error correction; single-action versus multi-action; vary calibration size $n$. **Metrics:** realised per-slice collateral risk; frequency with which the guarantee is violated across at least 200 random and temporal splits; residual attack bytes; URLLC p99 latency; eMBB goodput; decision latency.
12. **Limitations and threats to validity.**
    - Emulated RAN: no radio claims.
    - Exchangeability of episodes.
    - Limited attack diversity (volumetric floods and scans; PFCP).
    - Adaptive attackers who game the thresholds.
    - Twin fidelity.
13. **Feasibility.** Moderate. All software is open source; the main effort is the replay engine.
14. **Major risks and mitigations.**
    - The certified set may be empty at a realistic $n$ → use fixed-sequence testing, coarser policy grids, or larger budgets for mMTC.
    - Replay may be too slow → use a surrogate twin with an $\varepsilon$ bound.
    - A full read may show that a threat paper (CALIBURN, RBSID, CPC) already covers K2 → fall back to C3.
15. **Minimum evidence before submission.**
    - H1 holds empirically on both replay and emulation.
    - H2 is demonstrated, or the paper is re-scoped.
    - The proposition is proved.
    - Code and data are released.
    - A full-text novelty audit against all six threats is complete.

**Why C1 over the alternatives.** It is the only candidate that

- **(i)** survives the hard-rejection criteria with an identifiable contribution,
- **(ii)** reuses the team's assets (slice-stratified security, uncertainty, and the slice-differentiated testbed) without duplicating detection-level work, and
- **(iii)** can be tested with infrastructure that is plausibly available.

## Backup (provisional): C3

*SLA-weighted multi-slice quickest attack detection under heterogeneous false-alarm constraints.* **Target:** IEEE TNSM, or IEEE Transactions on Signal and Information Processing over Networks if the theory dominates. Activate it if the C1 full-text audit finds K2 or K5 already covered.

# Stage G (outline) — Phased roadmap {#sec:roadmap}

The detailed roadmap is withheld until the direction is approved, as the brief requires. Gate criteria for the first two phases:

- **Phase 1 (novelty validation).** Obtain and read the full texts of the six C1 threats, plus targeted searches G-02 to G-07.
  - **Go** if K2 and K5 remain uncovered.
  - **Stop or switch to C3** otherwise.
- **Phase 2 (formulation).** Prove the twin-error proposition and specify the dependence model.
  - **Go** if the proof holds and the certified set is non-empty in a pilot replay of 5G-NIDD with n of 500 episodes or fewer.
- **Phases 3–8** follow the brief: baselines, implementation, experiments, ablation, writing, and audit.

Effort estimate (assumes one full-time researcher with access to the testbed): Phases 1–2 in 4–6 weeks; Phases 3–6 in 4–6 months. **[Hypothesis]**

# Evidence and access gaps {#sec:gaps}

| ID | Gap | Blocks | Action needed |
|:--|:--|:--|:--|
| G-01 | Team testbed not inspected (core, RAN, UPF, isolation, mitigation hooks) | Stage E, C1 feasibility | Provide configs, topology, and logs, or grant access |
| G-02 | Full text of CALIBURN (and its retitled version), RBSID, CPC, CORA | C1 novelty (K2, K4) | Allow arxiv.org in the network policy, or upload the PDFs |
| G-03 | Full text of Hammar & Stadler TNSM 2022 / 2024 and TIFS 2025 | C1 baselines and novelty | IEEE Xplore access |
| G-04 | CALM-5G (arXiv 2610.17962) existence and content | C1 / C2 novelty | Resolve the identifier |
| G-05 | DOIs for the 20 V-META and 11 PARTIAL entries | Bibliography integrity | Allow doi.org and Crossref |
| G-06 | Team's prior manuscripts (5G-SliciNdd, leakage audit, slice-stratified security) | Overlap rule | Upload them |
| G-07 | Targeted search on conformal or uncertainty-aware GNN network twins; multichannel QCD with heterogeneous constraints | C6, C3 novelty | Phase 1 |
| G-08 | Whether C-PP-COAD used 5G-NIDD (sources conflict) | C2 rejection evidence (non-critical) | Full text |

: Evidence and access gaps.

# Conclusion {#sec:conc}

Within the stated verification limits, the evidence supports *abandoning* detection-level conformal false-alarm control as a primary topic. It supports pursuing **certified collateral-risk control for slice-aware intrusion response (C1)** as a provisional primary direction, with **C3** as the backup. The checkpoint stops here, pending approval and the closure of gaps G-01 to G-03.
