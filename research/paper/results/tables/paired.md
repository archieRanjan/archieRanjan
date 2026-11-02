| Comparison (A vs B) | Mean diff. attack delivered (A-B) | 2.5% / 50% / 97.5% quantile over splits | A better | Tie | Mean diff. J |
|:--|--:|--:|--:|--:|--:|
| RC-SIR vs Slice-FPR | +0.0402 | +0.0329 / +0.0401 / +0.0476 | 0.000 | 0.000 | +0.0017 |
| RC-SIR vs Pooled LTT | -0.0674 | -0.0853 / -0.0673 / -0.0503 | 1.000 | 0.000 | +0.0045 |
| RC-SIR-FS vs RC-SIR | -0.0828 | -0.0983 / -0.0876 / +0.0000 | 0.965 | 0.015 | -0.0066 |
| RC-SIR-FS vs Slice-FPR | -0.0427 | -0.0554 / -0.0479 / +0.0405 | 0.935 | 0.030 | -0.0048 |
| RC-SIR-FS vs Pooled LTT | -0.1493 | -0.1676 / -0.1541 / -0.0666 | 1.000 | 0.000 | -0.0021 |
| RC-SIR-FS vs ERM | +0.0065 | +0.0000 / +0.0000 / +0.0873 | 0.000 | 0.875 | +0.0000 |

: Paired comparisons on identical calibration/test splits (200 splits, n_cal = 500). Negative differences favour A.
