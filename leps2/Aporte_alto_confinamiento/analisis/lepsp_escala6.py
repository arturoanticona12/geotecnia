"""Leps-P, ronda 6: efecto del tamaño de probeta dentro de material, con los datos depurados (lepsp_r6.datos) y la
dependencia por PROGRAMA DE LABORATORIO (auditoría D1; revisor E2: las series de un mismo laboratorio no son
independientes). Igual que lepsp_escala3.py (grupos publicación × material con ≥ 2 tamaños; interceptos de set ajustados
por e con β_e del modelo; τ² por REML, IC de Knapp–Hartung, IC de τ por perfil de Q) y además:
  - combinación por laboratorio (principal) y por publicación (sensibilidad);
  - dependencia del efecto con la tensión (revisor G7): en cada grupo, y ~ sets + m x + βDx (lnD − lnD̄)·x, y metaanálisis de βDx;
  - intervalo de predicción de un material nuevo con t de k − 2 grados de libertad (Higgins et al. 2009).
Escribe lepsp_escala6.csv y lepsp_escala6.json."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import t as tdist
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_r6 import datos  # noqa: E402
from scipy.optimize import minimize_scalar, brentq  # noqa: E402
from scipy.stats import chi2 as _chi2  # noqa: E402


def tau2_reml(y, v, A):
    """Copia de lepsp_escala3 (ese script corre todo al importarse)."""
    def nll(t2):
        W = np.diag(1 / (v + t2)); Cb = np.linalg.inv(A.T @ W @ A); b = Cb @ A.T @ W @ y; r = y - A @ b
        return 0.5 * (np.sum(np.log(v + t2)) + np.linalg.slogdet(A.T @ W @ A)[1] + r @ W @ r)
    return float(minimize_scalar(nll, bounds=(0, 1.0), method="bounded").x)


def meta(y, v, etq="", A=None):
    k = len(y); A = np.ones((k, 1)) if A is None else A; p = A.shape[1]
    t2 = tau2_reml(y, v, A); W = np.diag(1 / (v + t2)); Cb = np.linalg.inv(A.T @ W @ A); b = Cb @ A.T @ W @ y
    r = y - A @ b; s2 = max(1.0, (r @ W @ r) / (k - p)) if k > p else np.nan            # Knapp–Hartung (truncado en 1)
    se = np.sqrt(np.diag(Cb) * s2); q = tdist.ppf(0.975, k - p) if k > p else np.nan
    out = dict(k=k, b=b.tolist(), se_kh=se.tolist(), ci=[[float(bi - q * si), float(bi + q * si)] for bi, si in zip(b, se)], tau=float(np.sqrt(t2)))
    if p == 1 and k > 2:                                    # IC 95 % de τ por perfil de Q (Viechtbauer 2007)
        def Qg(t2_):
            w = 1 / (v + t2_); m_ = (w * y).sum() / w.sum(); return float((w * (y - m_) ** 2).sum())
        lo_t, hi_t = _chi2.ppf(0.975, k - 1), _chi2.ppf(0.025, k - 1)
        t_lo = 0.0 if Qg(0.0) < lo_t else brentq(lambda t: Qg(t) - lo_t, 0.0, 10.0)
        t_hi = 0.0 if Qg(0.0) < hi_t else brentq(lambda t: Qg(t) - hi_t, 0.0, 10.0)
        out["tau_ci"] = [float(np.sqrt(t_lo)), float(np.sqrt(t_hi))]
    if etq:
        print(f"{etq:52s} k={k:2d}  βD={b[0]:+.4f}  IC 95 % KH [{out['ci'][0][0]:+.3f}, {out['ci'][0][1]:+.3f}]  τ={out['tau']:.3f}")
    return out

M6 = AQ / "lepsp_mcmc6.json"
BE = json.load(open(M6, encoding="utf-8"))["beta"]["e"] if M6.exists() else -0.537
d = datos(); d = d[~d.Dmax_imp & ~d.cens].copy(); d["Cu"] = pd.to_numeric(d["Cu-BT"], errors="coerce")
filas = []
for (ref, mat), g in d.groupby(["pub", "Material Type"]):
    if g.Dmax.nunique() < 2 or len(g) < 4:
        continue
    sets = g.Set.unique(); S = np.c_[[(g.Set == s).values.astype(float) for s in sets]].T
    X = np.c_[S, g.x.values]; b, *_ = np.linalg.lstsq(X, g.y.values, rcond=None)
    r = g.y.values - X @ b; dof = max(len(g) - X.shape[1], 1); s2 = r @ r / dof; C = s2 * np.linalg.pinv(X.T @ X)
    es = np.array([g[g.Set == s].e.mean() for s in sets]); cs = b[:-1] - BE * es; vcs = np.diag(C)[:-1]
    lnD = np.array([np.log(g[g.Set == s].Dmax.iloc[0]) for s in sets])
    if np.ptp(lnD) < 1e-9:
        continue
    A = np.c_[np.ones(len(sets)), lnD]; W = np.diag(1 / vcs); Cb = np.linalg.inv(A.T @ W @ A); bb = Cb @ A.T @ W @ cs
    # interacción con la tensión: pendiente distinta según el tamaño (lnD centrado en el grupo)
    lDg = np.log(g.Dmax.values) - lnD.mean(); X2 = np.c_[S, g.x.values, lDg * g.x.values]
    b2, *_ = np.linalg.lstsq(X2, g.y.values, rcond=None); r2 = g.y.values - X2 @ b2; dof2 = max(len(g) - X2.shape[1], 1)
    C2 = (r2 @ r2 / dof2) * np.linalg.pinv(X2.T @ X2)
    i0, i1 = int(np.argmin(lnD)), int(np.argmax(lnD))
    filas.append(dict(pub=ref, lab=g.lab.iloc[0], material=mat, n=len(g), n_sets=len(sets), R=float(np.exp(np.ptp(lnD))),
                      D_min=float(np.exp(lnD.min())), D_max=float(np.exp(lnD.max())), m=b[-1], bD=bb[1], se_bD=np.sqrt(Cb[1, 1]),
                      bDx=b2[-1], se_bDx=np.sqrt(C2[-1, -1]), de=es[i1] - es[i0]))
T = pd.DataFrame(filas).sort_values("bD").reset_index(drop=True)


def combinar(T, clave, col="bD", secol="se_bD"):
    rows = []
    for p, g in T.groupby(clave):
        y, v = g[col].values, g[secol].values ** 2
        if len(g) == 1:
            rows.append(dict(u=p, y=y[0], v=v[0], k=1))
        else:
            t2 = tau2_reml(y, v, np.ones((len(y), 1))); w = 1 / (v + t2)
            rows.append(dict(u=p, y=float((w * y).sum() / w.sum()), v=float(1 / w.sum()), k=len(g)))
    return pd.DataFrame(rows)


def prediccion(o):
    k = o["k"]; q = tdist.ppf(0.975, k - 2) if k > 2 else np.nan; s = np.sqrt(o["tau"] ** 2 + o["se_kh"][0] ** 2)
    return [float(o["b"][0] - q * s), float(o["b"][0] + q * s)]


pd.set_option("display.width", 250)
print(f"βe = {BE:.3f}; datos depurados sin Dmax imputado ni censurados")
print(T[["pub", "lab", "material", "n_sets", "R", "D_min", "D_max", "bD", "se_bD", "bDx", "se_bDx"]].round(3).to_string(index=False))
OUT = {}
for etq, sel in (("R ≥ 2", T.R >= 2), ("todos", T.R > 0)):
    Tg = T[sel]
    OUT[f"grupos {etq}"] = meta(Tg.bD.values, Tg.se_bD.values ** 2, f"Por grupo, {etq}")
    for clave, nom in (("lab", "laboratorios"), ("pub", "publicaciones")):
        Cc = combinar(Tg, clave); o = meta(Cc.y.values, Cc.v.values, f"Por {nom[:-1]}, {etq} ({len(Cc)} {nom})"); o["prediccion95"] = prediccion(o)
        OUT[f"{nom} {etq}"] = o
    Cx = combinar(Tg, "lab", "bDx", "se_bDx"); OUT[f"interaccion laboratorios {etq}"] = meta(Cx.y.values, Cx.v.values, f"βDx por laboratorio, {etq}")
L = OUT["laboratorios R ≥ 2"]
OUT["rango_razon_tamanos"] = [float(T[T.R >= 2].R.min()), float(T[T.R >= 2].R.max())]
OUT["rango_Dmax_mm"] = [float(T[T.R >= 2].D_min.min()), float(T[T.R >= 2].D_max.max())]
OUT["libreria"] = dict(general=dict(b=0.0, se_hk=L["se_kh"][0], tau=L["tau"], tau_ci=L.get("tau_ci"), nota="media cero; τ por laboratorio (ronda 6)"),
                       datos=dict(b=L["b"][0], se_hk=L["se_kh"][0], tau=L["tau"], nota="media estimada por laboratorio"),
                       weibull=dict(b=-0.05, se_hk=L["se_kh"][0], tau=L["tau"], nota="sensibilidad: escala de Weibull (β_D = −0.05)"))
print("τ_D por laboratorio (R ≥ 2):", round(L["tau"], 4), "IC Q-profile", np.round(L.get("tau_ci", [np.nan, np.nan]), 4), "| predicción 95 %", np.round(L["prediccion95"], 3))
T.to_csv(AQ / "lepsp_escala6.csv", index=False)
json.dump(OUT, open(AQ / "lepsp_escala6.json", "w", encoding="utf-8"), indent=1, default=float)
print("escrito lepsp_escala6.csv y lepsp_escala6.json")
