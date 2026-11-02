# Research decisions (continues `../checkpoint1/decision_log.md`)

| ID | Decision | Evidence | Status |
|---|---|---|---|
| R-01 | Re-examine C1 instead of accepting it. Its weakest point is "LTT applied to a new loss". | Checkpoint report §6; the brief | Done |
| R-02 | New novelty threats added: Einbinder et al. (TPAMI 2025, semi-supervised risk control), Prinster et al. (CPC, ICML 2026; authors now verified), an ICML 2026 O-RAN conformal-FAR detector (authors not retrieved). None certifies action-level, slice-indexed SLA outcomes. | `novelty/novelty_audit.md` | Done |
| R-03 | **Key re-scoping.** Lemma 1 shows that per-slice FPR certification bounds collateral under a monotone scheduler. The research question therefore becomes "direct vs FPR certification", with Slice-FPR as the strongest baseline. This replaces the checkpoint's claim that alert-level control *fails* to bound collateral (that claim is false under A3). | Lemma 1, proof plus numeric check | Done |
| R-04 | No real 5G data or testbed is available (repository empty; arXiv, Crossref and DataPort unreachable). Use a documented fluid simulator and restrict claims accordingly. | Environment audit | Done (limitation) |
| R-05 | Simulator v1 rejected (detector AUC 0.99999, all methods trivially pass). v2 has train/deploy regimes. Decided on detector diagnostics only. | `DESIGN_LOG.md`, `data_v1/` | Done, disclosed |
| R-06 | Primary detector switched to Isolation Forest, because the GBM scores were saturated under shift. GBM kept as a secondary check. | Pilot diagnostics | Done, disclosed |
| R-07 | **Implementation deviation corrected.** The first analysis used the selection objective J (benign violations) instead of the pre-specified R^a (attack delivered). Under J the constraints are never active. Corrected to R^a; J results archived in `data/results_J_objective.json`. | Checkpoint report §8 item 8 | Done, disclosed |
| R-08 | Default-argument bug (alpha bound at definition) fixed before the sensitivity runs. | Code review | Done |
| R-09 | Recommend RC-SIR-FS over RC-SIR. Both were specified before results; the choice is post hoc and disclosed. | Paired results | Done, disclosed |
| R-10 | Model-based response baseline (Hammar & Stadler) not reimplemented: it optimises a different criterion and needs an attacker model. | — | Limitation |
| R-11 | Target journal: IEEE TNSM (security management, closed-loop assurance). The contribution is a formulation, a structural result and an empirical characterisation; it is not a new statistical theorem. | — | Provisional |
| R-12 | Gate 1 (novelty) recorded as **conditionally passed**. The distinction from prior work is in what is certified and in Lemma 1 / Remark 1. The certification machinery is not new. Full-text verification of competitors remains impossible in this environment. | `novelty/novelty_audit.md` | Open risk |
