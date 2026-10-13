"""¿Qué propiedades del material explican la variación de m entre sets en la base mundial de Leps 2.0? (respaldo del memo,
revisión 7, 2026-10-10). Mismos sets y pendientes que a18 (≥ 3 ensayos, σ′n máx/mín ≥ 2). Correlación de Spearman de m con
e, ln(Dmax/100 mm), UCS, σ′n máximo y Bg; m por clase de Leps 2.0; y dispersión entre materiales τ (DerSimonian–Laird) sin y con
covariables (e, lnD, clase). Escribe a19_m_covariables.json."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from lepsp_r6 import datos  # noqa: E402
S0 = 1.013


def pendientes(W):
    out = []
    for s, g in W.groupby("Set"):
        g = g[(g.sn > 0) & (g.tau > 0)]
        if len(g) >= 3 and g.sn.max() / g.sn.min() >= 2:
            x, y = np.log(g.sn.values / S0), np.log(g.tau.values / S0); X = np.c_[np.ones(len(x)), x]
            b = np.linalg.lstsq(X, y, rcond=None)[0]; r = y - X @ b
            se = np.sqrt((r @ r) / (len(x) - 2) * np.linalg.inv(X.T @ X)[1, 1])
            out.append(dict(set=s, m=b[1], se=max(se, 1e-3), clase=g.clase.iloc[0]))
    return pd.DataFrame(out)


def tau_dl(m, se, X):
    """Dispersión entre materiales τ por Paule–Mandel con covariables: τ² tal que la Q generalizada = k − p. Antes era
    DerSimonian–Laird, inflado por los sets con s_i casi nulo (τ = 0.085 > desviación estándar bruta 0.064; auditoría 2026-10-10)."""
    from scipy.optimize import brentq
    k, p = X.shape
    def q(t2):
        w = 1 / (se ** 2 + t2); b = np.linalg.solve(X.T @ (w[:, None] * X), X.T @ (w * m)); r = m - X @ b; return np.sum(w * r ** 2) - (k - p)
    return float(np.sqrt(brentq(q, 0.0, 1.0))) if q(0.0) > 0 else 0.0


W = datos(); T = pendientes(W)
agg = W.groupby("Set").agg(e=("e", "mean"), lnD=("lnD", "mean"), ucs=("UCS", lambda s: pd.to_numeric(s, errors="coerce").mean()),
                           snmax=("sn", "max"), bg=("Bg", lambda s: pd.to_numeric(s, errors="coerce").mean()))
T = T.merge(agg, left_on="set", right_index=True)
rho = T[["m", "e", "lnD", "ucs", "snmax", "bg"]].corr(method="spearman")["m"].drop("m")
X0 = np.ones((len(T), 1)); X1 = pd.get_dummies(T[["e", "lnD", "clase"]], columns=["clase"], drop_first=True).astype(float); X1.insert(0, "c", 1.0)
out = dict(n_sets=len(T), m_sd_sets=float(T.m.std()), spearman={k: float(v) for k, v in rho.items()}, max_abs_spearman=float(rho.abs().max()),
           m_por_clase={c: dict(n=int(len(q)), media=float(q.m.mean()), de=float(q.m.std())) for c, q in T.groupby("clase")},
           tau_sin_covariables=tau_dl(T.m.values, T.se.values, X0), tau_con_e_lnD_clase=tau_dl(T.m.values, T.se.values, X1.values),
           base_sn_max=float(W.sn.max()), base_n_ensayos=int(len(W)), base_n_sobre_5=int((W.sn > 5).sum()), base_sets_sobre_5=int(W[W.sn > 5].Set.nunique()))
print(json.dumps(out, indent=1, ensure_ascii=False))
json.dump(out, open(AQ / "a19_m_covariables.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
