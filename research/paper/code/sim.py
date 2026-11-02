"""Fluid simulator of a sliced 5G user-plane egress (UPF N6 -> data network) under attack, plus
per-UE feature extraction and vectorised evaluation of per-slice mitigation policies.

Everything here is a *model*. It is not a 5G testbed and no real traffic is used. All parameters
are listed in PARAMS and reported in the paper.

Slices: 0 = eMBB, 1 = URLLC, 2 = mMTC.
Scheduler: hierarchical token-bucket-like sharing. Each slice has a guaranteed rate g_s*C and may
borrow idle capacity up to C (work-conserving). Borrowing couples the slices: an attack that
borrows idle capacity removes headroom from the other slices' bursts.
Episode: observation window (T_OBS steps, no action, features computed) followed by an action
window (T_ACT steps, chosen actions applied, SLAs measured).
"""
from __future__ import annotations
import numpy as np

PARAMS = dict(
    C=100.0,                       # egress capacity (traffic units per step)
    g=(0.55, 0.25, 0.20),          # guaranteed shares eMBB, URLLC, mMTC
    buf=(200.0, 12.0, 60.0),       # per-slice buffer (units)
    n_ue=(14, 10, 16),             # benign UEs per slice
    T_OBS=30, T_ACT=120,                 # observation window shortened from 60 (v1) to 30
    p_attack=0.6, max_attackers=4, attack_slice_p=(0.45, 0.15, 0.40),
    rl_cap=(3.0, 1.0, 0.5),        # rate-limit cap per slice (units/step)
    # SLA definitions (per benign UE, measured over the action window)
    sla_embb_tput=0.90,            # delivered/offered >= 0.90
    sla_urllc_delay=2.0, sla_urllc_deliv=0.99,   # p95 queueing delay <= 2 steps and delivery >= 0.99
    sla_mmtc_deliv=0.95,
)
SLICE_NAMES = ("eMBB", "URLLC", "mMTC")


# ----------------------------------------------------------------------------- traffic
def _onoff(rng, T, p_on_off, p_off_on, start_on):
    s = np.empty(T, bool); cur = start_on
    u = rng.random(T)
    for t in range(T):
        s[t] = cur
        cur = (u[t] >= p_on_off) if cur else (u[t] < p_off_on)
    return s


def gen_episode(rng, load=None, regime="deploy"):
    """Return dict with per-UE offered traffic D[u, t] (T_OBS+T_ACT), slice id, attacker flag,
    per-UE mean packet size (used as a feature), and the episode load factor.

    regime="train": benchmark-like regime used to train the detector (v1 traffic: no heavy-user
    variability, no alarm/firmware bursts, no packet-size spoofing).
    regime="deploy": operational regime (v2 traffic): additional benign behaviours and evasive
    attackers that the detector has not seen. This models the cross-domain degradation of NIDS
    documented in the literature."""
    dep = regime == "deploy"
    P = PARAMS; T = P["T_OBS"] + P["T_ACT"]
    rho = rng.uniform(0.6, 1.1) if load is None else load
    rows, sl, att, psz = [], [], [], []
    # eMBB benign: on/off video-like, 15% heavy bulk users
    for _ in range(P["n_ue"][0]):
        if rng.random() < (0.25 if dep else 0.15):        # deploy: more, and more varied, heavy users
            r = 10.0 * rho * (rng.lognormal(0, 0.4) * rng.lognormal(0, 0.15, T) if dep else rng.lognormal(0, 0.2) * np.ones(T))
        else:
            base = 6.0 * rho * rng.lognormal(0, 0.5)
            on = _onoff(rng, T, 0.05, 0.08, rng.random() < 0.6)
            r = on * base * rng.lognormal(0, 0.25, T)
        rows.append(r); sl.append(0); att.append(False); psz.append(rng.normal(1200, 120))
    # URLLC benign: periodic + small bursts; 10% event-driven alarm bursts
    for _ in range(P["n_ue"][1]):
        r = 0.6 * rho * np.ones(T)
        b = rng.random(T) < 0.03
        for t in np.flatnonzero(b):
            r[t:t + 3] += 4.0
        if dep and rng.random() < 0.20:               # deploy: event-driven alarm bursts (20% of UEs)
            t0 = rng.integers(0, T - 10); r[t0:t0 + 10] += rng.uniform(3.0, 8.0)
        rows.append(r); sl.append(1); att.append(False); psz.append(rng.normal(220, 30))
    # mMTC benign: sparse small reports
    for _ in range(P["n_ue"][2]):
        r = (rng.random(T) < 0.10) * 0.3 * rho
        if dep and rng.random() < 0.05:               # deploy: firmware-update burst
            t0 = rng.integers(0, T - 20); r[t0:t0 + 20] += rng.uniform(1.0, 3.0)
        rows.append(r); sl.append(2); att.append(False); psz.append(rng.normal(110, 15))
    # attackers
    if rng.random() < P["p_attack"]:
        for _ in range(rng.integers(1, P["max_attackers"] + 1)):
            s = rng.choice(3, p=P["attack_slice_p"])
            kind = rng.choice(3) if dep else rng.choice(2)   # 0 flood, 1 pulse, 2 low-and-slow (deploy only)
            t0 = rng.integers(0, P["T_OBS"] // 2)
            r = np.zeros(T)
            benign_size = rng.normal([1200, 220, 110][s], [120, 30, 15][s])
            spoof = dep and rng.random() < 0.7          # deploy: 70% of attackers mimic the slice's packet size
            if kind == 0:
                r[t0:] = rng.uniform(6, 16) if dep else rng.uniform(8, 20); size = benign_size if spoof else rng.normal(90, 20)
            elif kind == 1:
                per = rng.integers(6, 14); amp = rng.uniform(8, 20) if dep else rng.uniform(15, 30)
                r[t0:] = amp * ((np.arange(T - t0) % per) < per // 2); size = benign_size if spoof else rng.normal(150, 40)
            else:
                r[t0:] = rng.uniform(2, 5); size = benign_size
            rows.append(r * rng.lognormal(0, 0.1, T)); sl.append(int(s)); att.append(True); psz.append(size)
    return dict(D=np.maximum(np.array(rows), 0.0), slice=np.array(sl), attacker=np.array(att),
                psize=np.array(psz), load=rho)


def features(ep):
    """Per-UE features computed on the observation window only (no look-ahead)."""
    X = ep["D"][:, :PARAMS["T_OBS"]]
    mean = X.mean(1); std = X.std(1); mx = X.max(1)
    active = (X > 1e-9).mean(1)
    p2m = mx / (mean + 1e-6)
    diff = np.abs(np.diff(X, axis=1)).mean(1)
    onehot = np.eye(3)[ep["slice"]]
    return np.column_stack([mean, std, mx, active, p2m, diff, ep["psize"], onehot])


# ----------------------------------------------------------------------------- scheduler
def _serve(avail, C, gC):
    """avail: (K, 3) backlog+arrivals. Guaranteed share first, then idle capacity water-filled
    in proportion to the guaranteed weights among slices that still have demand."""
    serve = np.minimum(avail, gC)
    rem = avail - serve
    left = C - serve.sum(1)
    w = np.asarray(gC) / C
    for _ in range(3):
        need = rem > 1e-12
        ww = need * w
        tot = ww.sum(1, keepdims=True)
        share = np.where(tot > 0, ww / np.maximum(tot, 1e-12), 0) * left[:, None]
        add = np.minimum(share, rem)
        serve += add; rem -= add; left = left - add.sum(1)
    return serve


def evaluate_policies(ep, scores, tau, act, capacity_scale=1.0, extra_actions=None):
    """Evaluate K policies on one episode.

    tau: (K, 3) per-slice score thresholds (np.inf = never act); act: (K, 3) action per slice
    (0 = rate-limit, 1 = block). extra_actions: optional (M, U) explicit per-UE action matrices
    (-1 none, 0 RL, 1 block) appended after the K threshold policies (used for pi_0 and the oracle).
    Returns per-policy violation indicators V (K', U) for every UE, and the delivered fraction of
    attack traffic (K',).
    """
    P = PARAMS
    D = ep["D"][:, P["T_OBS"]:]                       # action window (U, T)
    U, T = D.shape
    s_u = ep["slice"]
    acted = scores[None, :] >= tau[:, s_u]            # (K, U)
    a_u = np.where(acted, act[:, s_u], -1)            # (K, U)
    if extra_actions is not None:
        a_u = np.vstack([a_u, extra_actions])
    K = a_u.shape[0]
    cap = np.asarray(P["rl_cap"])[s_u]               # (U,)
    pol = np.broadcast_to(D, (K, U, T)).copy()
    rl = a_u == 0
    pol[rl] = np.minimum(pol[rl], cap[np.nonzero(rl)[1]][:, None])
    pol[a_u == 1] = 0.0
    S = np.zeros((K, 3, T))
    for s in range(3):
        S[:, s, :] = pol[:, s_u == s, :].sum(1)
    C = P["C"] * capacity_scale
    gC = np.asarray(P["g"]) * C
    buf = np.asarray(P["buf"])
    q = np.zeros((K, 3)); drop = np.zeros((K, 3, T)); delay = np.zeros((K, 3, T))
    for t in range(T):
        arr = S[:, :, t]
        avail = q + arr
        srv = _serve(avail, C, gC)
        q_new = avail - srv
        over = np.maximum(q_new - buf, 0.0)
        drop[:, :, t] = np.where(arr > 1e-12, np.minimum(over / np.maximum(arr, 1e-12), 1.0), 0.0)
        q = q_new - over
        delay[:, :, t] = q / np.maximum(srv, 1e-9) * (srv > 1e-9) + (srv <= 1e-9) * (q > 1e-9) * 1e3
    offered = D.sum(1)                                 # (U,)
    deliv = (pol * (1 - drop[:, s_u, :])).sum(2)       # (K, U)
    ratio = np.where(offered > 1e-9, deliv / np.maximum(offered, 1e-9), 1.0)
    V = np.zeros((K, U), bool)
    m0, m1, m2 = s_u == 0, s_u == 1, s_u == 2
    V[:, m0] = ratio[:, m0] < P["sla_embb_tput"]
    V[:, m2] = ratio[:, m2] < P["sla_mmtc_deliv"]
    if m1.any():
        d_u = delay[:, 1, :][:, None, :].repeat(m1.sum(), 1)       # (K, U1, T)
        active = (D[m1] > 1e-9)[None].repeat(K, 0)
        d_u = np.where(active, d_u, np.nan)
        p95 = np.nanpercentile(d_u, 95, axis=2)
        p95 = np.nan_to_num(p95, nan=0.0)
        V[:, m1] = (p95 > P["sla_urllc_delay"]) | (ratio[:, m1] < P["sla_urllc_deliv"])
    att = ep["attacker"]
    att_off = offered[att].sum()
    att_del = deliv[:, att].sum(1) / att_off if att_off > 0 else np.full(K, np.nan)
    return V, att_del


def policy_grid(taus=(0.5, 0.7, 0.85, 0.95, 0.99)):
    """All per-slice (tau, action) combinations; 'off' counted once per slice -> 11^3 = 1331."""
    per = [(np.inf, 0)] + [(t, a) for t in taus for a in (0, 1)]
    T = np.array([[per[i][0], per[j][0], per[k][0]] for i in range(len(per)) for j in range(len(per)) for k in range(len(per))])
    A = np.array([[per[i][1], per[j][1], per[k][1]] for i in range(len(per)) for j in range(len(per)) for k in range(len(per))])
    return T, A


def episode_losses(ep, scores, tau, act, capacity_scale=1.0):
    """Return per-policy losses for one episode.
    Lc (K,3): action-induced collateral = frac. of benign UEs of slice s violated under the policy
              but NOT under no-action pi_0.
    Vb (K,3): total benign SLA-violation fraction per slice under the policy.
    Ad (K,):  delivered fraction of attack traffic (nan when there is no attacker).
    Also returns the same quantities for pi_0 and the oracle (blocks exactly the attackers)."""
    U = len(scores)
    none = -np.ones((1, U), int)
    oracle = np.where(ep["attacker"], 1, -1)[None]
    V, Ad = evaluate_policies(ep, scores, tau, act, capacity_scale, extra_actions=np.vstack([none, oracle]))
    V0 = V[-2]
    ben = ~ep["attacker"]
    Lc = np.zeros((V.shape[0], 3)); Vb = np.zeros((V.shape[0], 3))
    for s in range(3):
        m = ben & (ep["slice"] == s)
        Lc[:, s] = (V[:, m] & ~V0[m]).mean(1)
        Vb[:, s] = V[:, m].mean(1)
    return Lc, Vb, Ad
