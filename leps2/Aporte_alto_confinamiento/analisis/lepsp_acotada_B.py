"""Prueba de forma (ronda 3): ¿qué forma extrapola mejor dentro de un mismo material?
En cada pliegue LOPO se ajustan la cuadrática M2 y la acotada (φ′cs, ζ por ML perfilada en la grilla de la cresta, solo
con el entrenamiento). Para cada set de la publicación excluida con ≥ 2 ensayos a σ′n ≤ 1.5 MPa y ≥ 1 a σ′n ≥ 2 MPa se
actualiza solo el nivel (pivote en x̄, igual que lepsp.actualizar) y se predicen los ensayos altos. El nivel del material
queda fijado por sus propios ensayos, así que la comparación aísla la forma de la envolvente.
Escribe lepsp_acotada_B.csv."""
import sys, time
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada import d, ModeloNL, beta_inicial, disenio_m2, media  # noqa: E402
from lepsp_modelo import Modelo  # noqa: E402

PH = np.arange(12.0, 30.01, 2.0); ZE = np.round(np.arange(0.15, 0.451, 0.05), 3)


def nivel(G, R, rl, xl):
    """Actualización de solo nivel con pivote en x̄: devuelve (b, C) de (b0, b1)."""
    xb = float(np.mean(xl)); T = np.array([[1.0, xb], [0.0, 1.0]]); Gq = T @ G @ T.T
    z1 = np.ones((len(xl), 1)); g0 = Gq[0, 0]
    c = 1 / (1 / g0 + (z1.T @ np.linalg.solve(R, z1)).item()); q0 = c * (z1.T @ np.linalg.solve(R, rl)).item()
    q1 = Gq[1, 0] / g0 * q0; v11 = Gq[1, 1] - Gq[1, 0] ** 2 / g0 + (Gq[1, 0] / g0) ** 2 * c
    Cq = np.array([[c, Gq[1, 0] / g0 * c], [Gq[1, 0] / g0 * c, v11]]); Ti = np.linalg.inv(T)
    return Ti @ np.array([q0, q1]), Ti @ Cq @ Ti.T


def predB(mu_lo, mu_hi, Xl, Xh, Cb, m, te, lo, hi):
    G = m.Gp + m.Gs; xl = te.x.values[lo]; xh = te.x.values[hi]
    R = np.diag(m.sigma_eps(xl) ** 2); rl = te.y.values[lo] - mu_lo
    b, C = nivel(G, R, rl, xl); Zh = np.c_[np.ones_like(xh), xh]
    mu = mu_hi + Zh @ b
    v = np.einsum("ij,jk,ik->i", Zh, C, Zh) + np.einsum("ij,jk,ik->i", Xh, Cb, Xh) + m.sigma_eps(xh) ** 2
    return mu, np.sqrt(v)


def main():
  filas = []; t0 = time.time()
  for g in d.pub.unique():
    te = d[d.pub == g].reset_index(drop=True)
    casos = [(gi[gi.sn <= 1.5].index.values, gi[gi.sn >= 2].index.values) for _, gi in te.groupby("Set")]
    casos = [(lo, hi) for lo, hi in casos if len(lo) >= 2 and len(hi) >= 1]
    if not casos:
        continue
    tr = d[d.pub != g].reset_index(drop=True)
    mq = Modelo(tr, disenio_m2(tr), ["g", "m", "l", "e", "x", "x2"]).ajustar()
    mejor = None
    for ph in PH:
        for z in ZE:
            mm = ModeloNL(tr, np.tan(np.radians(ph)), z, beta_inicial(tr))
            ll, _ = mm.gn(mq.psi)
            if mejor is None or ll > mejor[0]:
                mejor = (ll, ph, z, mm.beta_nl.copy())
    _, ph, z, b0 = mejor
    mb = ModeloNL(tr, np.tan(np.radians(ph)), z, b0).ajustar_nl(mq.psi)
    Xq = disenio_m2(te); fb, Jb = media(mb.beta_nl, te, mb.T, mb.lam)
    for lo, hi in casos:
        muq, sdq = predB(Xq[lo] @ mq.beta, Xq[hi] @ mq.beta, Xq[lo], Xq[hi], mq.cov_beta, mq, te, lo, hi)
        mub, sdb = predB(fb[lo], fb[hi], Jb[lo], Jb[hi], mb.cov_beta, mb, te, lo, hi)
        for k, ii in enumerate(hi):
            filas.append(dict(pub=g, Set=te.Set[ii], x=te.x[ii], y=te.y[ii], mu_q=muq[k], sd_q=sdq[k], mu_b=mub[k], sd_b=sdb[k], phi_cs=ph, zeta=z))
    print(f"  {g[:40]:40s} sets {len(casos)}  φcs={ph} ζ={z} ({time.time()-t0:.0f} s)", flush=True)
  pd.DataFrame(filas).to_csv(AQ / "lepsp_acotada_B.csv", index=False)
  print("escrito lepsp_acotada_B.csv", len(filas))


if __name__ == "__main__":
    main()
