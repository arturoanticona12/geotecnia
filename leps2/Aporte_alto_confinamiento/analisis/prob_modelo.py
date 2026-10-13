"""Leps 3.0 probabilístico: modelo lineal mixto en log–log.
    y_ij = ln(τ_ij/σ0) = θ_j + m_j x_ij + ε_ij,   x = ln(σ′n/σ0),  σ0 = 10 pa
    θ_j = β_clase + β_e·e_j + b0_j ;   m_j = μ_m + b1_j ;   (b0, b1) ~ N(0, Σ) ;   ε ~ N(0, σ_ε²(x))
θ_j = ln tan φ′1 del material j. Exploración: estructura de varianza, heterocedasticidad y curvatura que cambia con x."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db, PA  # noqa: E402
from modelos import CLASE  # noqa: E402

S0 = 10 * PA
df = load_db()
df = df[(df.s3.isna() | (df.s3 >= 0.06)) & (df.sn > 0) & df.e.notna()].copy()
df["clase"] = df["Material Type"].map(CLASE)
df["x"] = np.log(df.sn / S0); df["y"] = np.log(df.tau / S0); df["x2"] = df.x ** 2
cnt = df.groupby("Set").x.transform("size"); df = df[cnt >= 2]
print(f"ensayos {len(df)}, sets {df.Set.nunique()}, publicaciones {df.Reference.nunique()}")

M = {}
M["base"] = smf.mixedlm("y ~ 0 + C(clase) + e + x", df, groups=df["Set"], re_formula="~x").fit(method="lbfgs", reml=True)
M["curv"] = smf.mixedlm("y ~ 0 + C(clase) + e + x + x2", df, groups=df["Set"], re_formula="~x").fit(method="lbfgs", reml=True)
M["curv_ml"] = smf.mixedlm("y ~ 0 + C(clase) + e + x + x2", df, groups=df["Set"], re_formula="~x").fit(method="lbfgs", reml=False)
M["base_ml"] = smf.mixedlm("y ~ 0 + C(clase) + e + x", df, groups=df["Set"], re_formula="~x").fit(method="lbfgs", reml=False)
for k in ("base", "curv"):
    r = M[k]; print(f"\n== modelo {k}"); print(r.fe_params.round(4).to_string())
    cov = r.cov_re.values; s = np.sqrt(np.diag(cov))
    print(f"  sd(θ) = {s[0]:.4f} | sd(m) = {s[1]:.4f} | corr = {cov[0, 1] / (s[0] * s[1]):+.2f} | sd(ε) = {np.sqrt(r.scale):.4f}")
lr = 2 * (M["curv_ml"].llf - M["base_ml"].llf)
print(f"\nRazón de verosimilitud curvatura (x²): {lr:.1f} (gl 1); AIC base {M['base_ml'].aic:.1f} curv {M['curv_ml'].aic:.1f}")

# heterocedasticidad del residuo dentro del set
r = M["curv"]; df["res"] = r.resid
for lo, hi in [(-3.5, -2), (-2, -1), (-1, 0), (0, 1), (1, 2.2)]:
    g = df[(df.x >= lo) & (df.x < hi)].res
    print(f"  x {lo:+.1f}…{hi:+.1f} (σn {S0*np.exp(lo):.2f}–{S0*np.exp(hi):.2f} MPa): n {len(g):3d}, sd residuo {g.std():.4f}")

# equivalencias para el lector: φ'1 por calidad y e
fe = M["curv"].fe_params
for cl in ("good", "moderate", "low"):
    for e in (0.3, 0.45, 0.6):
        th = fe[f"C(clase)[{cl}]"] + fe["e"] * e
        print(f"  φ′1 medio {cl:8s} e={e}: {np.degrees(np.arctan(np.exp(th))):.1f}°")
print(f"  m medio en el anclaje = {fe['x']:.3f}; curvatura c = {fe.get('x2', 0):.4f} (m local = m + 2c·x)")
