"""Leps-P, ronda 4: validación fuera de muestra (LOPO) de la forma acotada con efectos aleatorios en (η, ζ).
En cada pliegue: (φ′∞, ζ0) por ML perfilada solo con el entrenamiento, reajuste y predicción.
Modo A: todos los ensayos de la publicación excluida.
Modo B: sets con ≥ 2 ensayos a σ′n ≤ 1.5 MPa y ≥ 1 a σ′n ≥ 2 MPa. Vector aumentado v = (u, δβ) con previa
blockdiag(G, C_β): la actualización reduce también la incertidumbre de los efectos fijos (ronda 3 no lo hacía).
Variantes:
  nivel        actualización de corte del nivel en x̄ de cada set, set por set
  conjunta     actualización gaussiana completa de v, set por set
  previa       sin actualizar
  descarte     nivel, salvo sets con conflicto (p < 0.05), que quedan en la previa
  sitio        procedimiento recomendado: diagnóstico → descarte → actualización de corte conjunta de todos los sets de la
               publicación con efecto de publicación (laboratorio) común; los sets descartados heredan el efecto común
  ingenuo_m090, ingenuo_mtr   ajustes de φ′1 por MCO con m fija (0.90 o mediana dentro de set del entrenamiento)
Escribe lepsp_cv4_A.csv y lepsp_cv4_B.csv."""
import sys, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import chi2
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada2 import d, ModeloNL2, media2, BETA0, PSI0  # noqa: E402
from lepsp_cv3 import casos_B, m_dentro, rmse_ingenuo  # noqa: E402

PH = np.arange(16.0, 30.01, 2.0); ZE = np.round(np.arange(0.20, 0.451, 0.05), 3)


def corte(P, A_lo, s2, r, A_hi):
    """Actualización de corte del escalar q = aᵀv (a = fila en x̄) con residuos r de varianza s2; predicción en A_hi."""
    a = A_lo; g0 = float(a @ P @ a); c = 1 / (1 / g0 + np.sum(1 / s2)); q = c * np.sum(r / s2)
    k = A_hi @ P @ a / g0
    return k * q, np.einsum("ij,jk,ik->i", A_hi, P, A_hi) - k ** 2 * g0 + k ** 2 * c


def main():
    filasA, filasB = [], []; t0 = time.time()
    for g in d.pub.unique():
        tr = d[d.pub != g].reset_index(drop=True); te = d[d.pub == g].reset_index(drop=True)
        if tr.clase.isna().any() or te.clase.isna().any():
            continue
        m0 = ModeloNL2(tr, np.tan(np.radians(24.0)), 0.30, BETA0).ajustar_nl(PSI0)
        mejor = None
        for ph in PH:
            for z in ZE:
                mm = ModeloNL2(tr, np.tan(np.radians(ph)), z, BETA0); ll, _ = mm.gn(m0.psi)
                if mejor is None or ll > mejor[0]:
                    mejor = (ll, ph, z, mm.beta_nl.copy())
        _, ph, z, b0 = mejor
        mb = ModeloNL2(tr, np.tan(np.radians(ph)), z, b0).ajustar_nl(m0.psi)
        f, sdA, J, Z = mb.predecir(te); x = te.x.values; G = mb.Gp + mb.Gs; C = mb.cov_beta
        for k in range(len(te)):
            filasA.append(dict(pub=g, Set=te.Set[k], x=x[k], y=te.y[k], mu=f[k], sd=sdA[k], phi_cs=ph, zeta=z))
        cB = casos_B(te)
        if cB:
            mtr = m_dentro(tr); s090 = rmse_ingenuo(tr, 0.90); s_tr = rmse_ingenuo(tr, mtr)
            P1 = np.zeros((6, 6)); P1[:2, :2] = G; P1[2:, 2:] = C                      # v = (u_η, u_ζ, δβ)
            Af = lambda ii, xx=None: np.c_[media2(mb.beta_nl, te.iloc[ii].assign(x=xx if xx is not None else te.x.values[ii]), mb.T, mb.z0)[2],
                                            media2(mb.beta_nl, te.iloc[ii].assign(x=xx if xx is not None else te.x.values[ii]), mb.T, mb.z0)[1]]
            pinfo = {}
            for s, lo, hi in cB:
                xl, xh = x[lo], x[hi]; s2 = mb.sigma_eps(xl) ** 2; rl = te.y.values[lo] - f[lo]
                Al = Af(lo); Ah = Af(hi); xb = float(np.mean(xl)); Ab = Af(lo[:1], np.array([xb]))[0]
                Vp = Al @ P1 @ Al.T + np.diag(s2); pval = 1 - chi2.cdf(float(rl @ np.linalg.solve(Vp, rl)), len(lo)); pinfo[s] = pval
                se_h = mb.sigma_eps(xh) ** 2
                dn, vn = corte(P1, Ab, s2, rl, Ah)
                K = P1 @ Al.T @ np.linalg.inv(Vp); Pp = P1 - K @ Al @ P1; mj = K @ rl
                var = {"nivel": (f[hi] + dn, np.sqrt(vn + se_h)), "previa": (f[hi], sdA[hi]),
                       "conjunta": (f[hi] + Ah @ mj, np.sqrt(np.einsum("ij,jk,ik->i", Ah, Pp, Ah) + se_h))}
                var["descarte"] = var["previa"] if pval < 0.05 else var["nivel"]
                for nm, m_, sv in (("ingenuo_m090", 0.90, s090), ("ingenuo_mtr", mtr, s_tr)):
                    th = np.mean(te.y.values[lo] - m_ * xl); var[nm] = (th + m_ * xh, np.full(len(hi), sv))
                for nm, (mu, sd) in var.items():
                    for k, ii in enumerate(hi):
                        filasB.append(dict(variante=nm, pub=g, Set=s, x=x[ii], y=te.y[ii], mu=mu[k], sd=sd[k], pval=pval, m_tr=mtr))
            # procedimiento recomendado: actualización conjunta de los sets de la publicación con laboratorio común
            nS = len(cB); D = 2 + 2 * nS + 4; Pq = np.zeros((D, D)); Pq[:2, :2] = mb.Gp; Pq[-4:, -4:] = C
            for j in range(nS):
                Pq[2 + 2 * j:4 + 2 * j, 2 + 2 * j:4 + 2 * j] = mb.Gs
            rows, rv, ys = [], [], []
            for j, (s, lo, hi) in enumerate(cB):
                if pinfo[s] < 0.05:
                    continue
                xb = float(np.mean(x[lo])); ab = Af(lo[:1], np.array([xb]))[0]
                for ii in lo:
                    rw = np.zeros(D); rw[:2] = ab[:2]; rw[2 + 2 * j:4 + 2 * j] = ab[:2]; rw[-4:] = ab[2:]
                    rows.append(rw); rv.append(mb.sigma_eps(np.array([x[ii]]))[0] ** 2); ys.append(te.y.values[ii] - f[ii])
            m_post, P_post = np.zeros(D), Pq
            if rows:
                Rm = np.array(rows); S = Rm @ Pq @ Rm.T + np.diag(rv); K = Pq @ Rm.T @ np.linalg.inv(S)
                m_post = K @ np.array(ys); P_post = Pq - K @ Rm @ Pq
            for j, (s, lo, hi) in enumerate(cB):
                Ah = Af(hi); H = np.zeros((len(hi), D)); H[:, :2] = Ah[:, :2]; H[:, 2 + 2 * j:4 + 2 * j] = Ah[:, :2]; H[:, -4:] = Ah[:, 2:]
                mu = f[hi] + H @ m_post; sd = np.sqrt(np.einsum("ij,jk,ik->i", H, P_post, H) + mb.sigma_eps(x[hi]) ** 2)
                for k, ii in enumerate(hi):
                    filasB.append(dict(variante="sitio", pub=g, Set=s, x=x[ii], y=te.y[ii], mu=mu[k], sd=sd[k], pval=pinfo[s], m_tr=mtr))
        print(f"  {g[:40]:40s} n={len(te):3d} sets B {len(cB)}  φ′∞={ph} ζ0={z} ({time.time()-t0:.0f} s)", flush=True)
    pd.DataFrame(filasA).to_csv(AQ / "lepsp_cv4_A.csv", index=False); pd.DataFrame(filasB).to_csv(AQ / "lepsp_cv4_B.csv", index=False)
    print("escrito lepsp_cv4_A.csv y lepsp_cv4_B.csv")


if __name__ == "__main__":
    main()
