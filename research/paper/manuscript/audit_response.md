# Response to the external manuscript audit (2 November 2026)

| Audit item | Priority | What was done | Status | Evidence |
|---|---|---|---|---|
| Audit proofs and the risk-control implementation | P0 | Line-level checklist of Proposition 1 against code; known-risk Monte Carlo with an adversarial selection objective; standalone reimplementation shown to reproduce the published numbers exactly | **Done** | `proof_audit.md` §B; `tests/test_validity_montecarlo.py`; `tests/test_methods_consistency.py` |
| Prove monotonicity for the implemented scheduler and give a counterexample | P0/P1 | Theorem 1, a full proof for the exact water-filling scheduler with buffers. Counterexample: relocating action (redirect with hairpin), including cross-slice harm | **Done** | Appendix A; `proof_audit.md` §A; `tests/test_sim_ext.py` |
| Full-text novelty verification | P0 | Still impossible: arxiv.org, doi.org and publisher sites are blocked here. Additional metadata checks were run. The claim is narrowed so that novelty rests on the formulation, Theorem 1, Proposition 0 and the measured conditions, not on new statistics | **Partial** | `novelty/novelty_audit.md` |
| Independent confirmatory runs after freezing the method | P0 | Plan committed (d5518c3) before data. 8 independent replications with randomised scenarios and fresh detectors. Decision rule applied as written | **Done** | `ANALYSIS_PLAN_v2.md`; `results_confirm/` |
| Compatible response baselines / narrow the claim | P0 | Claim narrowed to "direct vs FPR certification"; title changed; model-based policies explicitly out of scope | **Done (narrowed)** | Introduction; Table 1 |
| Realistic 5G-core/UPF validation | P1 | **Blocked**: no testbed access in this environment; the team testbed is still uninspected | Open | `submission_readiness.md` |
| Non-monotone scheduling and correlated traffic | P1 | Non-monotone *actions* studied (Study N). Correlated/temporal traffic and congestion control are not modelled | Partial | Study N; Limitations |
| Twin transfer unusably conservative | P1 | Demoted to an appendix proposition plus a limitation | Done | Appendix A; §8 |
| Test-set metric vs population risk | Stat. | Clopper–Pearson CIs on violation frequencies; "confident violation" via a Hoeffding lower bound | Done | Tables 5–6 |
| Shared-pool dependence | Stat. | Primary inference across independent replications (t-interval, sign test) | Done | Study C |
| Post-hoc selection | Stat. | Exploratory results labelled as such; confirmatory plan frozen; post-hoc analyses of the new data labelled "exploratory" | Done | Appendix B; §6 |
| References (CALIBURN version, metadata) | P2 | CALIBURN cited as arXiv v2 with the abstract-page title; SliceSecure corrected to FNWF 2022; Amponis co-authors and pages; Layeghy author list confirmed | Done (metadata) | `references.bib`; R-18 |
| IEEE compile, abstract length, title | P2 | Abstract 169 words; new title. IEEEtran source updated (`\appendices`, labels, citations statically checked). **Not compiled** (no TeX available) | Partial | `main.tex` |

## What the new evidence changed
The audit's central doubt was confirmed. The primary improvement claim did **not** survive pre-registered confirmation: mean −0.030, 95% CI [−0.071, +0.011], 6 / 8 replications. The paper's conclusion was rewritten accordingly:
- For traffic-removing actions, FPR certification is a valid and cheaper default (Theorem 1).
- Direct certification matters for relocating actions, where the FPR criterion loses validity.

That last point rests on a post-hoc large-sample analysis; the pre-registered finite-sample test, N-H2, was not supported.
