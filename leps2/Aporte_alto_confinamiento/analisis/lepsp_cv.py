"""Leps-P, paso 2: validación fuera de muestra.
Modo A: sin ensayos del sitio (material nuevo de un laboratorio nuevo). Agrupación: publicación (LOPO) y tipo de roca (LORO).
Modo B: actualización con ensayos del sitio de σ′n ≤ 1.5 MPa y predicción de σ′n ≥ 2 MPa, con diagnóstico de conflicto
previa–datos; variantes: actualización completa (θ, m) y solo θ cuando hay conflicto o el rango de esfuerzos es estrecho.
Salida: lepsp_cv_A.csv, lepsp_cv_B.csv."""
import sys, warnings, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import chi2
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo  # noqa: E402

d = preparar(load_db(), CLASE)
CL = ["good", "moderate", "low"]
lnU = np.log(d.UCS.fillna(d.UCS.median()) / 100.0).values


def disenio(dd, esp):
    dum = np.c_[[(dd.clase == c).values.astype(float) for c in CL]].T
    e, x = dd.e.values, dd.x.values
    if esp == "M0":
        return np.c_[dum, e, x]
    if esp == "M2":
        return np.c_[dum, e, x, x ** 2]
    if esp == "M5":
        lu = np.log(dd.UCS.fillna(d.UCS.median()) / 100.0).values
        return np.c_[np.ones(len(dd)), lu, e, x]


def zcol(x, esp):
    """Columnas de X que multiplican a b0 y b1 no cambian; la pendiente local efectiva depende de x² en M2."""
    return np.c_[np.ones_like(x), x]


def pred_A(m, dte, esp):
    X = disenio(dte, esp); x = dte.x.values; Z = zcol(x, esp)
    mu = X @ m.beta
    G = m.Gp + m.Gs
    v = np.einsum("ij,jk,ik->i", Z, G, Z) + np.einsum("ij,jk,ik->i", X, m.cov_beta, X) + m.sigma_eps(x) ** 2
    return mu, np.sqrt(v)


def leps2_ref(dtr, dte):
    """Referencia: Leps 2.0 publicado (m = 0.9) con dispersión constante estimada en el entrenamiento."""
    f = lambda dd: np.log(np.tan(np.radians(dd.clase.map({"good": 53, "moderate": 50, "low": 47}).values - 20 * dd.e.values))) + 0.9 * dd.x.values
    s = np.std(dtr.y.values - f(dtr))
    return f(dte), np.full(len(dte), s)


filas = []; filasB = []; t0 = time.time()
SOLO_B = len(sys.argv) > 1 and sys.argv[1] == "B"          # rehace solo el modo B (M2) y conserva lepsp_cv_A.csv
for agrup in (["pub"] if SOLO_B else ["pub", "Material Type"]):
    for esp in (["M2"] if SOLO_B else (["M0", "M2", "M5"] if agrup == "pub" else ["M0", "M5"])):
        for g in d[agrup].unique():
            tr = d[d[agrup] != g].reset_index(drop=True); te = d[d[agrup] == g].reset_index(drop=True)
            if tr.clase.isna().any() or te.clase.isna().any():
                continue
            m = Modelo(tr, disenio(tr, esp), [f"b{i}" for i in range(disenio(tr, esp).shape[1])]).ajustar()
            mu, sd = pred_A(m, te, esp)
            mu0, sd0 = leps2_ref(tr, te)
            for k in range(len(te)):
                filas.append(dict(agrup=agrup, esp=esp, grupo=g, pub=te.pub[k], Set=te.Set[k], x=te.x[k], y=te.y[k],
                                  mu=mu[k], sd=sd[k], mu0=mu0[k], sd0=sd0[k]))
            # ---- modo B (solo en LOPO)
            if agrup != "pub":
                continue
            X = disenio(te, esp); G = m.Gp + m.Gs
            for s, gi in te.groupby("Set"):
                lo = gi[gi.sn <= 1.5].index.values; hi = gi[gi.sn >= 2].index.values
                if len(lo) < 2 or len(hi) < 1:
                    continue
                xl = te.x.values[lo]; Zl = np.c_[np.ones_like(xl), xl]; R = np.diag(m.sigma_eps(xl) ** 2)
                Cb = m.cov_beta
                rl = te.y.values[lo] - X[lo] @ m.beta
                # diagnóstico de conflicto: distancia de Mahalanobis bajo la predictiva previa
                Vprev = Zl @ G @ Zl.T + X[lo] @ Cb @ X[lo].T + R
                D2 = float(rl @ np.linalg.solve(Vprev, rl)); pval = 1 - chi2.cdf(D2, len(lo))
                rango = np.exp(xl.max() - xl.min())
                xh = te.x.values[hi]; Zh = np.c_[np.ones_like(xh), xh]
                for modo in ["completo", "solo_theta_si_conflicto"]:
                    usa_m = not (modo == "solo_theta_si_conflicto" and (pval < 0.05 or rango < 3))
                    if usa_m:
                        Gi = np.linalg.inv(G); Cp = np.linalg.inv(Gi + Zl.T @ np.linalg.solve(R, Zl)); bp = Cp @ Zl.T @ np.linalg.solve(R, rl)
                    else:
                        # solo nivel, pivote en el centro de los datos x̄ (igual que lepsp.actualizar)
                        xb = float(np.mean(xl)); T = np.array([[1.0, xb], [0.0, 1.0]]); Gq = T @ G @ T.T
                        z1 = np.ones((len(lo), 1)); g0 = Gq[0, 0]
                        c = 1 / (1 / g0 + (z1.T @ np.linalg.solve(R, z1)).item()); q0 = c * (z1.T @ np.linalg.solve(R, rl)).item()
                        q1 = Gq[1, 0] / g0 * q0; v11 = Gq[1, 1] - Gq[1, 0] ** 2 / g0 + (Gq[1, 0] / g0) ** 2 * c
                        Cq = np.array([[c, Gq[1, 0] / g0 * c], [Gq[1, 0] / g0 * c, v11]]); Ti = np.linalg.inv(T)
                        bp = Ti @ np.array([q0, q1]); Cp = Ti @ Cq @ Ti.T
                    muh = X[hi] @ m.beta + Zh @ bp
                    vh = np.einsum("ij,jk,ik->i", Zh, Cp, Zh) + np.einsum("ij,jk,ik->i", X[hi], Cb, X[hi]) + m.sigma_eps(xh) ** 2
                    muA, sdA = pred_A(m, te.loc[hi], esp)
                    for k, ii in enumerate(hi):
                        filasB.append(dict(esp=esp, modo=modo, pub=g, Set=s, x=te.x[ii], y=te.y[ii], mu=muh[k], sd=np.sqrt(vh[k]),
                                           muA=muA[k], sdA=sdA[k], pval=pval, rango=rango, conflicto=pval < 0.05, n_lo=len(lo)))
        print(f"{agrup:14s} {esp}: listo ({time.time()-t0:.0f} s)", flush=True)
if not SOLO_B:
    pd.DataFrame(filas).to_csv(AQUI / "lepsp_cv_A.csv", index=False)
pd.DataFrame(filasB).to_csv(AQUI / "lepsp_cv_B.csv", index=False)
print("escrito lepsp_cv_A.csv y lepsp_cv_B.csv")
