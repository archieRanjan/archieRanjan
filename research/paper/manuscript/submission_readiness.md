# Submission readiness

**Verdict: NOT ready for submission. Ready for internal human review.**

| Condition (brief §17) | Status |
|---|---|
| 1. One clearly defined research question | Met |
| 2. Novelty thoroughly checked | **Partially.** Abstract-level only; full texts were not accessible. |
| 3. Core method implemented and validated | Met (simulation) |
| 4. Strong baselines reproduced or faithfully implemented | **Partially.** The strongest alert-level baseline is implemented; the model-based response baseline is not. |
| 5. Findings support the conclusions | Met. The conclusions are conditional and include negative results. |
| 6. Mathematical claims checked | Met, except that A3 is checked numerically, not proven. |
| 7. Every measurement reproducible | Met (determinism and rerun checks) |
| 8. Every reference verified | **Partially.** See `manuscript_review.md`, Reviewer E. |
| 9. Tables and figures supported by data | Met |
| 10. Coherent, rigorous, no inflated language | Met (prohibited-phrase scan; conditional claims) |
| 11. Limitations disclosed | Met |
| 12. Critical review completed | Met (`manuscript_review.md`) |
| 13. Journal requirements | **Partially.** IEEEtran source provided, but it was not compiled here (no TeX), so page count and formatting are unverified. Author information and funding are missing. |

**Blocking items before submission**
1. Compile `main.tex` with IEEEtran and check layout and length against TNSM limits.
2. Verify the four PARTIAL references and read the full texts of CALIBURN, CPC and Einbinder et al.
3. Ideally, validate A3 and the utility comparison on a real UPF or a packet-level emulator with slice-labelled traffic; at minimum, discuss this as future work (already done).
4. Add author, affiliation and funding information.
5. Decide whether the contribution is sufficient for TNSM or better suited to a letter or conference venue (see Reviewer A).
