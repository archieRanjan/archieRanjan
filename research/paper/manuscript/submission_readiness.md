# Submission readiness (revised after the confirmatory studies)

**Verdict: NOT ready for TNSM submission.** The work is a sound but modest study. Its primary improvement hypothesis was not confirmed, and its positive structural results are proven or shown only within a simulator.

| Condition | Status |
|---|---|
| One focused research question | Met (narrowed: when direct certification beats FPR certification) |
| Novelty checked | **Partial**: metadata and abstracts only; full texts inaccessible |
| Method implemented and validated | Met: proof audit, Monte Carlo, consistency tests |
| Strong baselines | Met for the narrowed claim (Slice-FPR, ERM, pooled). Model-based response is out of scope by design |
| Findings support conclusions | Met: conclusions follow the confirmatory outcome, including the negative result |
| Mathematics checked | Met for the model (Theorem 1 proven). Real-UPF monotonicity is unproven |
| Reproducibility | Met: 18 tests, a determinism check, a frozen plan, all numbers placeholder-resolved |
| References verified | **Partial**: metadata verified; full texts not read; three preprints cited |
| Figures/tables from data | Met |
| Writing quality | Improved. A human edit pass is still needed |
| Limitations disclosed | Met |
| Critical review | Met (`manuscript_review.md`, `audit_response.md`) |
| IEEE format | **Partial**: IEEEtran source, not compiled here |

**What would make it Transactions-worthy (human decisions required):**
1. **Real-system evidence:** run Studies C and N on a UPF with real enforcement (e.g., Open5GS with tc/nftables and per-slice classes) and real congestion-controlled traffic. Measure whether Theorem 1's conditions hold and whether relocating actions (redirect or scrubbing) produce finite-sample violations of FPR certificates.
2. **A stronger relocation study:** pre-register a study whose *design* targets the regime in which FPR certification fails in finite samples (larger n, tighter cross-slice budgets). This is the most promising route to a positive, non-incremental result.
3. **Full-text novelty check** of CALIBURN, Conformal Policy Control and Einbinder et al.
4. **Venue:** if real-system evidence cannot be added, a letter or conference venue (e.g., CNSM, NOMS) fits the current contribution better than TNSM.
