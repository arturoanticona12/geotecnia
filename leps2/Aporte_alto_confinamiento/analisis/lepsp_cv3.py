"""Leps-P, validación fuera de muestra de la forma acotada (ronda 3), según el preregistro de PLAN_RONDA3.md.
LOPO: en cada pliegue se elige (φ′cs, ζ) por ML perfilada sobre la grilla de la cresta, solo con el entrenamiento, y se
reajusta el modelo. Modo A: todos los ensayos de la publicación excluida. Modo B: sets con ≥ 2 ensayos a σ′n ≤ 1.5 MPa y
≥ 1 a σ′n ≥ 2 MPa; se predicen los altos con:
  nivel (regla principal) · previa · conjunta · procedimiento (descartar si p < 0.05, si no nivel) ·
  ingenuo_m090 (φ′1 por MCO con m = 0.90) · ingenuo_mtr (m = pendiente media dentro de set del entrenamiento).
La DE predictiva de los ajustes ingenuos es su RMSE fuera de muestra en las publicaciones de entrenamiento (mismo
criterio de partición), sin usar la publicación excluida. Escribe lepsp_cv3_A.csv y lepsp_cv3_B.csv."""
import sys, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import chi2
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada import d, ModeloNL, beta_inicial, disenio_m2, media  # noqa: E402
from lepsp_acotada_B import nivel  # noqa: E402
from lepsp_modelo import Modelo  # noqa: E402

PH = np.arange(12.0, 32.01, 2.0); ZE = np.round(np.arange(0.15, 0.451, 0.05), 3)


def casos_B(dd):
    out = []
    for s, gi in dd.groupby("Set"):
        lo = gi[gi.sn <= 1.5].index.values; hi = gi[gi.sn >= 2].index.values
        if len(lo) >= 2 and len(hi) >= 1:
            out.append((s, lo, hi))
    return out


def m_dentro(dd):
    """Pendiente log–log media dentro de set (sets con ≥ 3 ensayos y razón de σ′n ≥ 2)."""
    ms = []
    for _, g in dd.groupby("Set"):
        if len(g) >= 3 and g.sn.max() / g.sn.min() >= 2:
            ms.append(np.polyfit(g.x, g.y, 1)[0])
    return float(np.median(ms))


def rmse_ingenuo(dd, m):
    r = []
    for _, lo, hi in casos_B(dd):
        th = np.mean(dd.y.values[lo] - m * dd.x.values[lo]); r += list(dd.y.values[hi] - (th + m * dd.x.values[hi]))
    return float(np.sqrt(np.mean(np.square(r))))


def main():
    filasA, filasB = [], []; t0 = time.time()
    for g in d.pub.unique():
        tr = d[d.pub != g].reset_index(drop=True); te = d[d.pub == g].reset_index(drop=True)
        if tr.clase.isna().any() or te.clase.isna().any():
            continue
        mq = Modelo(tr, disenio_m2(tr), ["g", "m", "l", "e", "x", "x2"]).ajustar()
        mejor = None
        for ph in PH:
            for z in ZE:
                mm = ModeloNL(tr, np.tan(np.radians(ph)), z, beta_inicial(tr)); ll, _ = mm.gn(mq.psi)
                if mejor is None or ll > mejor[0]:
                    mejor = (ll, ph, z, mm.beta_nl.copy())
        _, ph, z, b0 = mejor
        mb = ModeloNL(tr, np.tan(np.radians(ph)), z, b0).ajustar_nl(mq.psi)
        f, J = media(mb.beta_nl, te, mb.T, mb.lam); x = te.x.values; Z = np.c_[np.ones_like(x), x]; G = mb.Gp + mb.Gs
        sdA = np.sqrt(np.einsum("ij,jk,ik->i", Z, G, Z) + np.einsum("ij,jk,ik->i", J, mb.cov_beta, J) + mb.sigma_eps(x) ** 2)
        for k in range(len(te)):
            filasA.append(dict(pub=g, Set=te.Set[k], x=x[k], y=te.y[k], mu=f[k], sd=sdA[k], phi_cs=ph, zeta=z))
        cB = casos_B(te)
        if cB:
            mtr = m_dentro(tr); s090 = rmse_ingenuo(tr, 0.90); s_tr = rmse_ingenuo(tr, mtr)
            for s, lo, hi in cB:
                xl, xh = x[lo], x[hi]; R = np.diag(mb.sigma_eps(xl) ** 2); rl = te.y.values[lo] - f[lo]
                Zl, Zh = np.c_[np.ones_like(xl), xl], np.c_[np.ones_like(xh), xh]
                Vprev = Zl @ G @ Zl.T + J[lo] @ mb.cov_beta @ J[lo].T + R
                pval = 1 - chi2.cdf(float(rl @ np.linalg.solve(Vprev, rl)), len(lo))
                base_v = np.einsum("ij,jk,ik->i", J[hi], mb.cov_beta, J[hi]) + mb.sigma_eps(xh) ** 2
                bN, CN = nivel(G, R, rl, xl)
                Cp = np.linalg.inv(np.linalg.inv(G) + Zl.T @ np.linalg.solve(R, Zl)); bJ = Cp @ Zl.T @ np.linalg.solve(R, rl)
                pr = (f[hi], sdA[hi])
                var = {"nivel": (f[hi] + Zh @ bN, np.sqrt(np.einsum("ij,jk,ik->i", Zh, CN, Zh) + base_v)),
                       "previa": pr,
                       "conjunta": (f[hi] + Zh @ bJ, np.sqrt(np.einsum("ij,jk,ik->i", Zh, Cp, Zh) + base_v))}
                var["procedimiento"] = pr if pval < 0.05 else var["nivel"]
                for nm, m_, s_ in (("ingenuo_m090", 0.90, s090), ("ingenuo_mtr", mtr, s_tr)):
                    th = np.mean(te.y.values[lo] - m_ * xl); var[nm] = (th + m_ * xh, np.full(len(hi), s_))
                for nm, (mu, sd) in var.items():
                    for k, ii in enumerate(hi):
                        filasB.append(dict(variante=nm, pub=g, Set=s, x=x[ii], y=te.y[ii], mu=mu[k], sd=sd[k], pval=pval, m_tr=mtr))
        print(f"  {g[:40]:40s} n={len(te):3d} sets B {len(cB)}  φcs={ph} ζ={z} ({time.time()-t0:.0f} s)", flush=True)
    pd.DataFrame(filasA).to_csv(AQ / "lepsp_cv3_A.csv", index=False); pd.DataFrame(filasB).to_csv(AQ / "lepsp_cv3_B.csv", index=False)
    print("escrito lepsp_cv3_A.csv y lepsp_cv3_B.csv")


if __name__ == "__main__":
    main()
