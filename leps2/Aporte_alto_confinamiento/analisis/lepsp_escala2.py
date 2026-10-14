"""Leps-P, efecto de tamaño de probeta (ronda 2). Por grupo (misma publicación y tipo de roca, ≥ 2 Dmax):
y = c_set + m·x (m común) → βD = pendiente de c_set frente a ln Dmax (MCO con error de los c_set; si hay más de dos sets,
se suma la varianza residual entre sets). Metaanálisis de efectos aleatorios (DerSimonian–Laird) con IC de Hartung–Knapp;
dirección de los cambios de Cu y e; meta-regresión βD ~ Δln Cu + Δe + angulosidad; sensibilidad al criterio de similitud.
Escribe lepsp_escala2.csv y lepsp_escala2.json (y conserva el formato de lepsp_escala.json para la librería)."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import t as tdist
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar  # noqa: E402

d = preparar(load_db(), CLASE); d = d[d.Dmax.notna()].copy(); d["Cu"] = pd.to_numeric(d["Cu-BT"], errors="coerce")
filas = []
for (ref, mat), g in d.groupby(["pub", "Material Type"]):
    if g.Dmax.nunique() < 2 or len(g) < 4:
        continue
    sets = g.Set.unique(); S = np.c_[[(g.Set == s).values.astype(float) for s in sets]].T
    X = np.c_[S, g.x.values]; b, *_ = np.linalg.lstsq(X, g.y.values, rcond=None)
    r = g.y.values - X @ b; dof = max(len(g) - X.shape[1], 1); s2 = r @ r / dof
    C = s2 * np.linalg.pinv(X.T @ X); cs = b[:-1]; vcs = np.diag(C)[:-1]; m = b[-1]
    lnD = np.array([np.log(g[g.Set == s].Dmax.iloc[0]) for s in sets])
    if np.ptp(lnD) < 1e-9:
        continue
    if len(sets) == 2:
        bD = (cs[1] - cs[0]) / (lnD[1] - lnD[0]); se = np.sqrt(vcs[0] + vcs[1]) / abs(lnD[1] - lnD[0])
    else:
        A = np.c_[np.ones(len(sets)), lnD]; w = 1 / vcs; W = np.diag(w)
        bb = np.linalg.solve(A.T @ W @ A, A.T @ W @ cs); res = cs - A @ bb
        tau2s = max(0.0, (res @ W @ res - (len(sets) - 2)) / max(w.sum() - (w ** 2).sum() / w.sum(), 1e-12))
        W2 = np.diag(1 / (vcs + tau2s)); Cb = np.linalg.inv(A.T @ W2 @ A); bb = Cb @ A.T @ W2 @ cs; bD, se = bb[1], np.sqrt(Cb[1, 1])
    i0, i1 = int(np.argmin(lnD)), int(np.argmax(lnD))
    cu0, cu1 = g[g.Set == sets[i0]].Cu.mean(), g[g.Set == sets[i1]].Cu.mean(); e0, e1 = g[g.Set == sets[i0]].e.mean(), g[g.Set == sets[i1]].e.mean()
    ang = g["Ang rat"].iloc[0]
    filas.append(dict(pub=ref, material=mat, n=len(g), n_sets=len(sets), Dmax=f"{np.exp(lnD.min()):g}–{np.exp(lnD.max()):g}", R=float(np.exp(np.ptp(lnD))),
                      m=m, bD=bD, se_bD=se, dlnCu=np.log(cu1 / cu0) if np.isfinite(cu0 * cu1) and cu0 > 0 else np.nan, de=e1 - e0,
                      angular=bool(ang >= 7.5) if pd.notna(ang) else np.nan, origen=g.Origin.iloc[0]))
T = pd.DataFrame(filas).sort_values("bD").reset_index(drop=True)


def meta(T, etq=""):
    y, v = T.bD.values, T.se_bD.values ** 2; k = len(y); w = 1 / v; bf = (w * y).sum() / w.sum()
    Q = (w * (y - bf) ** 2).sum(); tau2 = max(0, (Q - (k - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    ws = 1 / (v + tau2); b = (ws * y).sum() / ws.sum(); se_z = np.sqrt(1 / ws.sum())
    se_hk = np.sqrt((ws * (y - b) ** 2).sum() / ((k - 1) * ws.sum())) if k > 1 else np.nan
    q = tdist.ppf(0.975, k - 1) if k > 1 else np.nan; mbar = T.m.mean()
    r = dict(n=k, b=b, se=se_z, tau=np.sqrt(tau2), ci_z=[b - 1.96 * se_z, b + 1.96 * se_z], se_hk=se_hk, ci_hk=[b - q * se_hk, b + q * se_hk],
             kappa=-b / (1 - mbar), kappa_ci_hk=[-(b + q * se_hk) / (1 - mbar), -(b - q * se_hk) / (1 - mbar)], m_bar=mbar)
    if etq:
        print(f"{etq:58s} k={k:2d}  βD={b:+.4f}  IC z [{r['ci_z'][0]:+.3f},{r['ci_z'][1]:+.3f}]  IC HK [{r['ci_hk'][0]:+.3f},{r['ci_hk'][1]:+.3f}]  τ={r['tau']:.3f}  κ={r['kappa']:.2f} (HK {r['kappa_ci_hk'][0]:.2f}–{r['kappa_ci_hk'][1]:.2f})")
    return r


pd.set_option("display.width", 250)
print(T[["pub", "material", "n", "n_sets", "Dmax", "R", "m", "bD", "se_bD", "dlnCu", "de", "angular"]].round(3).to_string(index=False))
R = {"todos": meta(T, "Todos los grupos")}
for cu_r, de_r in [(1.1, 0.03), (1.25, 0.05), (1.5, 0.05), (2.0, 0.10)]:
    sim = (T.dlnCu.abs() <= np.log(cu_r)) & (T.de.abs() <= de_r)
    R[f"similares Cu≤{cu_r} Δe≤{de_r}"] = meta(T[sim], f"Similares: |Δln Cu| ≤ ln {cu_r}, |Δe| ≤ {de_r}") if sim.sum() >= 2 else None
R["angulares"] = meta(T[T.angular == True], "Angulares (voladura o chancado)")
R["redondeados"] = meta(T[T.angular == False], "Redondeados o subredondeados") if (T.angular == False).sum() >= 2 else None
# meta-regresión (efectos aleatorios con τ² de DL del modelo nulo; casos completos)
M = T.dropna(subset=["dlnCu", "de", "angular"]); A = np.c_[np.ones(len(M)), M.dlnCu, M.de, M.angular.astype(float)]
W = np.diag(1 / (M.se_bD ** 2 + R["todos"]["tau"] ** 2)); Cb = np.linalg.inv(A.T @ W @ A); bb = Cb @ A.T @ W @ M.bD.values
print("\nMeta-regresión βD ~ 1 + Δln Cu + Δe + angular  (k = %d):" % len(M))
for nm, v_, s_ in zip(["intercepto", "Δln Cu", "Δe", "angular"], bb, np.sqrt(np.diag(Cb))):
    print(f"  {nm:10s} {v_:+.4f} ± {s_:.4f}  (z = {v_ / s_:+.2f})")
R["metaregresion"] = dict(k=len(M), coef=dict(zip(["intercepto", "dlnCu", "de", "angular"], bb.tolist())), se=np.sqrt(np.diag(Cb)).tolist())
# dirección: ¿qué cambió con Dmax en los grupos con βD > 0?
P = T[T.bD > 0]
print(f"\nGrupos con βD > 0: {len(P)}; Cu aumenta con Dmax en {int((P.dlnCu > np.log(1.25)).sum())}, e disminuye en {int((P.de < -0.05).sum())}, "
      f"ninguno de los dos en {int(((P.dlnCu <= np.log(1.25)) | P.dlnCu.isna()).mul((P.de >= -0.05)).sum())}")
T.to_csv(AQUI / "lepsp_escala2.csv", index=False)
json.dump(R, open(AQUI / "lepsp_escala2.json", "w"), indent=1, default=float)
