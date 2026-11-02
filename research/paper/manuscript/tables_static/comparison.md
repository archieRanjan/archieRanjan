| Approach | What it certifies or optimises | Key assumption | Difference from this work | Compared here |
|:--|:--|:--|:--|:--|
| Conformal outlier / alert-threshold control [@bates2023outliers; @youssef2026caliburn] | Alert-level FPR, FDR or false-positive budget | Exchangeability | Certifies slice-indexed SLA outcomes of actions | Exploratory: 1% FPR operating point |
| Per-slice certified FPR (Corollary 1) | Collateral, via Theorem 1 | Monotone scheduling and traffic-removing actions | Direct certification does not need monotonicity | Primary comparator (all studies) |
| LTT / CRC [@angelopoulos2025ltt; @angelopoulos2024crc] | Generic risks by multiple testing | i.i.d. calibration | Used unchanged; we add the counterfactual slice-collateral formulation and the structural analysis | — |
| Conformal policy control [@prinster2026cpc] | Risk of deviating from a safe policy | Safe reference policy | Network counterfactual, slice structure, relocating actions | Not compared (different setting) |
| Optimal-stopping / game-theoretic response [@hammar2022optimalstopping; @zonouz2014rre] | Model-optimal response | Attacker and system model | No model; distribution-free per-slice certificate | Not compared (different criterion) |
| Pooled certification (ablation) | One certificate across slices | — | Per-slice budgets | Exploratory, Study C |
| Empirical constrained selection (ERM) | No guarantee | — | Statistical margin | All studies |

: Comparison with the closest approaches. Qualitative columns are based on the cited papers' abstracts.
