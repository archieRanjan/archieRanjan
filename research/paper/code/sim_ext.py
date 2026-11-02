"""Extension of sim.py for the pre-registered Study N (ANALYSIS_PLAN_v2.md): a *redirect* action.

A redirected UE's traffic is sent over the shared egress link to a scrubbing service in a
borrow-only class (guarantee 0, leftover-sharing weight W_SCRUB). The scrubber removes attack
traffic (assumed perfect). Benign traffic re-enters its original slice one slot later (hairpin),
so it crosses the shared link twice. This violates assumption A3: acting on one UE can add load
that harms non-acted UEs.

Action codes: -1 none, 0 rate-limit, 1 block, 2 redirect.
With no redirect actions this module reproduces sim.evaluate_policies exactly
(tests/test_sim_ext.py).
"""
import numpy as np
import sim

W_SCRUB = 0.20


def _serve_w(avail, C, gC, w):
    """Exact weighted water-filling with guarantees: x_s = min(d_s, g_s + w_s * theta).
    Runs as many rounds as there are classes (each round saturates >= 1 class or exhausts capacity)."""
    serve = np.minimum(avail, gC)
    rem = avail - serve
    left = C - serve.sum(1)
    for _ in range(avail.shape[1]):
        need = rem > 1e-12
        ww = need * w
        tot = ww.sum(1, keepdims=True)
        share = np.where(tot > 0, ww / np.maximum(tot, 1e-12), 0) * left[:, None]
        add = np.minimum(share, rem)
        serve += add; rem -= add; left = left - add.sum(1)
    return serve


def evaluate_policies_ext(ep, scores, tau, act, extra_actions=None, w_scrub=W_SCRUB):
    P = sim.PARAMS
    D = ep["D"][:, P["T_OBS"]:]
    U, T = D.shape
    s_u = ep["slice"]; att = ep["attacker"]
    acted = scores[None, :] >= tau[:, s_u]
    a_u = np.where(acted, act[:, s_u], -1)
    if extra_actions is not None:
        a_u = np.vstack([a_u, extra_actions])
    K = a_u.shape[0]
    cap = np.asarray(P["rl_cap"])[s_u]
    pol = np.broadcast_to(D, (K, U, T)).copy()
    rl = a_u == 0
    pol[rl] = np.minimum(pol[rl], cap[np.nonzero(rl)[1]][:, None])
    red = a_u == 2
    pol[(a_u == 1) | red] = 0.0
    redD = np.where(red[:, :, None], D[None], 0.0)                       # (K,U,T) traffic sent to scrubber
    ben_red = red & ~att[None]                                           # benign traffic returns
    S = np.zeros((K, 3, T + 1))
    for s in range(3):
        S[:, s, :T] = pol[:, s_u == s, :].sum(1)
    S_scr = np.zeros((K, T + 1)); S_scr[:, :T] = redD.sum(1)
    C = P["C"]; gC = np.r_[np.asarray(P["g"]) * C, 0.0]
    w = np.r_[np.asarray(P["g"]), w_scrub]
    buf = np.r_[np.asarray(P["buf"]), np.inf]
    q = np.zeros((K, 4)); drop = np.zeros((K, 4, T + 1)); delay = np.zeros((K, 4, T + 1))
    ret = np.zeros((K, 3))                                               # returning benign traffic for the next slot
    ret_hist = np.zeros((K, 3, T + 1))
    for t in range(T + 1):
        arr = np.column_stack([S[:, :, t] + ret, S_scr[:, t]])
        ret_hist[:, :, t] = ret
        avail = q + arr
        srv = _serve_w(avail, C, gC, w)
        q_new = avail - srv
        over = np.maximum(q_new - buf, 0.0)
        drop[:, :, t] = np.where(arr > 1e-12, np.minimum(over / np.maximum(arr, 1e-12), 1.0), 0.0)
        q = q_new - over
        delay[:, :, t] = q / np.maximum(srv, 1e-9) * (srv > 1e-9) + (srv <= 1e-9) * (q > 1e-9) * 1e3
        if t < T:
            back = np.where(ben_red, D[None, :, t], 0.0) * (1 - drop[:, 3, t])[:, None]   # (K,U)
            ret = np.stack([back[:, s_u == s].sum(1) for s in range(3)], 1)
        else:
            ret = np.zeros((K, 3))
    offered = D.sum(1)
    d_slice = drop[:, s_u, :]                                            # (K,U,T+1)
    deliv_direct = (pol * (1 - d_slice[:, :, :T])).sum(2)
    deliv_red = (np.where(ben_red[:, :, None], D[None], 0.0) * (1 - drop[:, 3, :T])[:, None, :]
                 * (1 - d_slice[:, :, 1:T + 1])).sum(2)
    deliv = deliv_direct + deliv_red
    ratio = np.where(offered > 1e-9, deliv / np.maximum(offered, 1e-9), 1.0)
    V = np.zeros((K, U), bool)
    m0, m1, m2 = s_u == 0, s_u == 1, s_u == 2
    V[:, m0] = ratio[:, m0] < P["sla_embb_tput"]
    V[:, m2] = ratio[:, m2] < P["sla_mmtc_deliv"]
    if m1.any():
        base = delay[:, 1, :T][:, None, :].repeat(m1.sum(), 1)
        hair = (delay[:, 1, 1:T + 1] + delay[:, 3, :T] + 1.0)[:, None, :].repeat(m1.sum(), 1)
        d_u = np.where(red[:, m1][:, :, None], hair, base)
        active = (D[m1] > 1e-9)[None].repeat(K, 0)
        d_u = np.where(active, d_u, np.nan)
        p95 = np.nan_to_num(np.nanpercentile(d_u, 95, axis=2), nan=0.0)
        V[:, m1] = (p95 > P["sla_urllc_delay"]) | (ratio[:, m1] < P["sla_urllc_deliv"])
    att_off = offered[att].sum()
    att_del = deliv[:, att].sum(1) / att_off if att_off > 0 else np.full(K, np.nan)
    return V, att_del


def episode_losses_ext(ep, scores, tau, act):
    """Same outputs as sim.episode_losses, plus the per-slice acted-benign fraction for the A3 check."""
    U = len(scores)
    none = -np.ones((1, U), int)
    oracle = np.where(ep["attacker"], 1, -1)[None]
    V, Ad = evaluate_policies_ext(ep, scores, tau, act, extra_actions=np.vstack([none, oracle]))
    V0 = V[-2]; ben = ~ep["attacker"]
    Lc = np.zeros((V.shape[0], 3)); Vb = np.zeros((V.shape[0], 3)); Fa = np.zeros((V.shape[0], 3))
    acted = np.vstack([scores[None, :] >= tau[:, ep["slice"]], np.zeros((1, U), bool), ep["attacker"][None]])
    for s in range(3):
        m = ben & (ep["slice"] == s)
        Lc[:, s] = (V[:, m] & ~V0[m]).mean(1)
        Vb[:, s] = V[:, m].mean(1)
        Fa[:, s] = acted[:, m].mean(1)
    return Lc, Vb, Ad, Fa
