"""Leps-P, efecto de tamaño de probeta (ronda 3). Correcciones pedidas por los revisores:
1. Solo grupos con razón de tamaños R = Dmax,máx/Dmax,mín ≥ 2 (sensibilidad: todos).
2. Interceptos de set ajustados por relación de vacíos con βe del modelo (en vez de filtrar por «similitud»).
3. A la varianza de cada intercepto se suma la varianza entre sets no relacionada con el tamaño (sdθ_set² del modelo).
4. Dependencia por publicación: los grupos de una misma publicación se combinan primero (inverso de la varianza) y el
   metaanálisis se hace entre publicaciones (sensibilidad: por grupo).
Metaanálisis de efectos aleatorios con τ² por REML y IC de Hartung–Knapp; meta-regresión con τ² REML y EE de Knapp–Hartung.
Escribe lepsp_escala3.csv y lepsp_escala3.json."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import t as tdist
from scipy.optimize import minimize_scalar
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar  # noqa: E402

PAR = json.load(open(AQ / "lepsp_parametros_r2.json", encoding="utf-8"))["formas"]["x2"]
BE = dict(zip(PAR["nombres"], PAR["beta"]))["e"]
SD_SET = float(np.median([np.exp(s["psi"][3]) for s in PAR["muestras"]]))      # sdθ entre sets (no atribuible al tamaño)
# ronda 4: por defecto NO se suma la varianza entre sets (factor 0: τ mayor, conservador); factor 1 = ronda 3 (sensibilidad)
FACT = float(sys.argv[1]) if len(sys.argv) > 1 else 0.0; SUF = "" if FACT == 0.0 else f"_f{FACT:g}"
d = preparar(load_db(), CLASE); d = d[d.Dmax.notna()].copy(); d["Cu"] = pd.to_numeric(d["Cu-BT"], errors="coerce")
filas = []
for (ref, mat), g in d.groupby(["pub", "Material Type"]):
    if g.Dmax.nunique() < 2 or len(g) < 4:
        continue
    sets = g.Set.unique(); S = np.c_[[(g.Set == s).values.astype(float) for s in sets]].T
    X = np.c_[S, g.x.values]; b, *_ = np.linalg.lstsq(X, g.y.values, rcond=None)
    r = g.y.values - X @ b; dof = max(len(g) - X.shape[1], 1); s2 = r @ r / dof
    C = s2 * np.linalg.pinv(X.T @ X); es = np.array([g[g.Set == s].e.mean() for s in sets])
    cs = b[:-1] - BE * es; vcs = np.diag(C)[:-1] + FACT * SD_SET ** 2
    lnD = np.array([np.log(g[g.Set == s].Dmax.iloc[0]) for s in sets])
    if np.ptp(lnD) < 1e-9:
        continue
    A = np.c_[np.ones(len(sets)), lnD]; W = np.diag(1 / vcs); Cb = np.linalg.inv(A.T @ W @ A); bb = Cb @ A.T @ W @ cs
    i0, i1 = int(np.argmin(lnD)), int(np.argmax(lnD))
    cu0, cu1 = g[g.Set == sets[i0]].Cu.mean(), g[g.Set == sets[i1]].Cu.mean()
    filas.append(dict(pub=ref, material=mat, n=len(g), n_sets=len(sets), R=float(np.exp(np.ptp(lnD))), m=b[-1], bD=bb[1], se_bD=np.sqrt(Cb[1, 1]),
                      dlnCu=np.log(cu1 / cu0) if np.isfinite(cu0 * cu1) and cu0 > 0 else np.nan, de=es[i1] - es[i0],
                      angular=bool(g["Ang rat"].iloc[0] >= 7.5) if pd.notna(g["Ang rat"].iloc[0]) else np.nan))
T = pd.DataFrame(filas).sort_values("bD").reset_index(drop=True)


def tau2_reml(y, v, A):
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
        from scipy.stats import chi2 as _chi2

        def Qg(t2_):
            w = 1 / (v + t2_); m_ = (w * y).sum() / w.sum(); return float((w * (y - m_) ** 2).sum())
        from scipy.optimize import brentq
        lo_t, hi_t = _chi2.ppf(0.975, k - 1), _chi2.ppf(0.025, k - 1)
        t_lo = 0.0 if Qg(0.0) < lo_t else brentq(lambda t: Qg(t) - lo_t, 0.0, 10.0)
        t_hi = 0.0 if Qg(0.0) < hi_t else brentq(lambda t: Qg(t) - hi_t, 0.0, 10.0)
        out["tau_ci"] = [float(np.sqrt(t_lo)), float(np.sqrt(t_hi))]
    if etq:
        print(f"{etq:52s} k={k:2d}  βD={b[0]:+.4f}  IC 95 % KH [{out['ci'][0][0]:+.3f}, {out['ci'][0][1]:+.3f}]  τ={out['tau']:.3f}")
    return out


def por_pub(T):
    """Combina los grupos de cada publicación (inverso de la varianza; la varianza entre grupos de una publicación se
    estima por REML si hay ≥ 3 grupos, si no se suma la τ global)."""
    rows = []
    for p, g in T.groupby("pub"):
        y, v = g.bD.values, g.se_bD.values ** 2
        if len(g) == 1:
            rows.append(dict(pub=p, bD=y[0], v=v[0], k=1))
        else:
            t2 = tau2_reml(y, v, np.ones((len(y), 1))); w = 1 / (v + t2)
            rows.append(dict(pub=p, bD=float((w * y).sum() / w.sum()), v=float(1 / w.sum()), k=len(g)))
    return pd.DataFrame(rows)


pd.set_option("display.width", 250)
print(f"βe = {BE:.3f}; sdθ entre sets añadida = {SD_SET:.3f}")
print(T[["pub", "material", "n_sets", "R", "bD", "se_bD", "dlnCu", "de", "angular"]].round(3).to_string(index=False))
OUT = {}
for etq, sel in (("R ≥ 2", T.R >= 2), ("todos", T.R > 0)):
    Tg = T[sel]; Pp = por_pub(Tg)
    OUT[f"grupos {etq}"] = meta(Tg.bD.values, Tg.se_bD.values ** 2, f"Por grupo, {etq}")
    OUT[f"publicaciones {etq}"] = meta(Pp.bD.values, Pp.v.values, f"Por publicación, {etq} ({len(Pp)} publicaciones)")
# meta-regresión (por grupo, R ≥ 2, casos completos)
M = T[(T.R >= 2)].dropna(subset=["dlnCu", "angular"])
A = np.c_[np.ones(len(M)), M.dlnCu, M.angular.astype(float)]
mr = meta(M.bD.values, M.se_bD.values ** 2, A=A)
print(f"\nMeta-regresión βD ~ 1 + Δln Cu + angular (k = {len(M)}, τ² REML, EE Knapp–Hartung):")
for nm, b_, s_, c_ in zip(["intercepto", "Δln Cu", "angular"], mr["b"], mr["se_kh"], mr["ci"]):
    print(f"  {nm:10s} {b_:+.4f} ± {s_:.4f}  IC 95 % [{c_[0]:+.3f}, {c_[1]:+.3f}]")
OUT["metaregresion"] = mr
P = OUT["publicaciones R ≥ 2"]
OUT["libreria"] = dict(general=dict(b=P["b"][0], se_hk=P["se_kh"][0], tau=P["tau"]))
OUT["factor_var_set"] = FACT
print("τ (publicaciones, R ≥ 2):", round(P["tau"], 4), "IC 95 % Q-profile:", np.round(P.get("tau_ci", [np.nan, np.nan]), 4))
T.to_csv(AQ / f"lepsp_escala3{SUF}.csv", index=False)
json.dump(OUT, open(AQ / f"lepsp_escala3{SUF}.json", "w", encoding="utf-8"), indent=1, default=float)
print(f"\nescrito lepsp_escala3{SUF}.csv y lepsp_escala3{SUF}.json")
