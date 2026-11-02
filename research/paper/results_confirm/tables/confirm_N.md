| Method | Viol. freq. [95% CP CI] | Confident viol. | Coll. eMBB | Coll. URLLC | Coll. mMTC | Attack delivered | Fallback |
|:--|--:|--:|--:|--:|--:|--:|--:|
| RC-SIR-FS | 0.000 [0.000, 0.018] | 0.000 | 0.0094 | 0.0022 | 0.0000 | 0.448 | 0.00 |
| Slice-FPR+redirect | 0.000 [0.000, 0.018] | 0.000 | 0.0202 | 0.0005 | 0.0000 | 0.533 | 0.00 |
| Slice-FPR+block | 0.000 [0.000, 0.018] | 0.000 | 0.0074 | 0.0011 | 0.0053 | 0.546 | 0.00 |
| ERM | 0.035 [0.014, 0.071] | 0.000 | 0.0406 | 0.0064 | 0.0013 | 0.253 | 0.00 |
| No action | 0.000 [0.000, 0.018] | 0.000 | 0.0000 | 0.0000 | 0.0000 | 0.967 | 1.00 |
| Oracle | 0.000 [0.000, 0.018] | 0.000 | 0.0000 | 0.0000 | 0.0000 | 0.000 | 0.00 |

: Study N, actions {block, redirect}, 200 splits (n_cal = 500). Redirect violates assumption A3.
