"""Hoeffding-Bentkus p-value used for Learn-then-Test risk control (Angelopoulos et al., AoAS 2025)."""
import numpy as np
from scipy.stats import binom


def hb_pvalue(rhat, alpha, n):
    """Hoeffding-Bentkus p-value for H0: E[L] > alpha, losses in [0,1] (Angelopoulos et al., LTT)."""
    rhat = np.minimum(rhat, alpha)
    with np.errstate(divide="ignore", invalid="ignore"):
        h = np.where(rhat > 0, rhat * np.log(rhat / alpha), 0) + (1 - rhat) * np.log((1 - rhat) / (1 - alpha))
    p_h = np.exp(-n * h)
    p_b = np.e * binom.cdf(np.ceil(n * rhat), n, alpha)
    return np.minimum(p_h, p_b)
