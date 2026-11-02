# Novelty audit (Gate 1)

**Access limitation (applies to every row).** Full texts could not be retrieved: arxiv.org, doi.org, Crossref and publisher sites are blocked in this environment. Every comparison below rests on abstracts, indexing records and search-engine excerpts. Novelty is therefore **not conclusively established**.

## Selected question
Direct certification of per-slice action-induced SLA collateral versus per-slice FPR certification (see `../research_question.md`).

## Closest prior work and mechanism-level comparison
| Work | Mechanism (from abstract/record) | Certifies | Slice-indexed | Action outcomes | Distribution-free | Threat level |
|---|---|---|---|---|---|---|
| CALIBURN, arXiv 2605.24696 (Youssef) | BOCPD + isotonic calibration + regime-dependent CRC for streaming alert thresholds | Alert FP budget | No (regimes, not slices) | No | Yes | High for C2; medium for this work |
| FIRCE, arXiv 2605.01962 (Barrett et al.) | Conformal evaluators + adaptive chunking; "response" = retraining | Drift decisions | No | No | Partly | Low |
| Bates et al., AoS 2023 | Conformal p-values, BH → FDR | Detection FDR | No | No | Yes | Basis of the FPR baseline |
| ICML 2026 O-RAN conformal FAR detector (authors not retrieved) | Mahalanobis score on AE errors + split conformal threshold | False-alarm rate | Not stated | No | Yes | High for C2; low here |
| ConFID (Elsevier IoT 2026) | Conformal one-class detector, FPR ≤ α | FPR | No | No | Yes | High for C2 |
| LTT (AoAS 2025), CRC (ICLR 2024) | Multiple testing / monotone-loss risk control | Generic risks | — | — | Yes | Mechanism used unchanged |
| Conformal Policy Control (Prinster et al., ICML 2026) | Calibrate deviation of a new policy from a safe policy; non-monotone CRC | Generic policy risk | No | Generic | Yes | Medium: closest "action-level" mechanism, but no network counterfactual or slice structure |
| Semi-supervised risk control (Einbinder et al., TPAMI 2025) | PPI with unlabeled data to reduce conservativeness | Generic risk | No | No | Yes | Low; possible future tool |
| Hammar & Stadler (TNSM 2022, 2024) | POMDP / optimal stopping; threshold response policies | Model-based optimality | No | Yes | **No** | Medium: same policy structure, different guarantee |
| RRE (TPDS 2014) | Game-theoretic response selection | Model-based | No | Yes | No | Low |
| SliceSecure (2023) | BiLSTM slice DDoS detection; slice impact measured | Detection accuracy | Yes | No | No | Low |

## Claim-by-claim verdict
| Claim | Verdict |
|---|---|
| Distribution-free risk control of a networking decision | **Not novel by itself**: LTT/CRC apply verbatim. |
| Certified quantity = per-slice, action-induced SLA collateral against the no-action counterfactual | **No prior instance found**. Distinct from alert-level FP control in what is controlled. Abstract-level evidence only. |
| Lemma 1 (FPR certification bounds collateral under monotone scheduling) | Elementary, but **not found stated** in the IDS/response literature reviewed. It reframes the comparison and is the main analytical contribution. |
| Twin-transfer proposition | A union-bound corollary; novel only as an application. The rigorous form proved vacuous in our setting (negative result). |
| Empirical characterisation of when direct certification pays | Novel to our knowledge; simulation-only. |

## Is this "an existing method applied to a new domain"?
Partly, and the manuscript says so. What goes beyond application:
1. The structural result (Lemma 1, Remark 1), which shows that the naive motivation — "alert-level control cannot bound collateral" — is false under A3.
2. The identification of the correct strong baseline.
3. Measured conditions under which the extra machinery helps or does not.

A reviewer may still judge the contribution incremental. Risk: **medium–high**.
