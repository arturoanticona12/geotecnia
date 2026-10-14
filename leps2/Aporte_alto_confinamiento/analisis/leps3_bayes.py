"""Leps 3.0, actualización de m con ensayos del sitio (contracción bayesiana normal–normal).
1) Distribución poblacional de m por set (en q, σ3 ≥ 60 kPa): media μm y varianza entre sets τ² (método de momentos,
   descontando el error de estimación de cada set).
2) Para un set nuevo: m_post = (m_set/se² + μm/τ²)/(1/se² + 1/τ²); φ'1 se reajusta con m_post.
3) Validación modo B (calibración σ'n ≤ 1.5 MPa → predicción σ'n ≥ 2 MPa) y modo C (calibración con todo σ'n ≤ 3 MPa →
   predicción σ'n > 3 MPa), con μm y τ² estimados sin la publicación evaluada.
También entrega cuantiles del error de extrapolación con m = 0.87 por rango de σ'n (bandas del modo B)."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import sigma1, tau_leps2  # noqa: E402

df = load_db()
df = df[(df["Lab Test"] == "TRX") & (df.s3 >= 0.06) & df.s1.notna()].copy(); df["q"] = df.s1 - df.s3


def ajuste(s3, q, m=None):
    """Devuelve (φ1, m, se_m). Con m dado, solo φ1."""
    if m is not None:
        r = least_squares(lambda p: np.log(sigma1(tau_leps2, s3, np.full(len(s3), p[0]), m)[0] - s3) - np.log(q), [41], bounds=([15], [70]))
        return r.x[0], m, np.nan
    r = least_squares(lambda p: np.log(sigma1(tau_leps2, s3, np.full(len(s3), p[0]), p[1])[0] - s3) - np.log(q), [41, 0.87],
                      bounds=([15, 0.5], [70, 1.0]))
    J = r.jac; dof = max(len(q) - 2, 1); s2 = np.sum(r.fun ** 2) / dof
    try:
        cov = np.linalg.inv(J.T @ J) * s2; se = np.sqrt(max(cov[1, 1], 1e-8))
    except np.linalg.LinAlgError:
        se = np.inf
    return r.x[0], r.x[1], se


# --------------------------------------------- 1. población de m (sets con ≥ 3 ensayos y razón de esfuerzos ≥ 4)
pop = []
for s, g in df.groupby("Set"):
    if len(g) >= 3 and g.s3.max() / g.s3.min() >= 4:
        f1, m, se = ajuste(g.s3.values, g.q.values)
        if np.isfinite(se) and 0.5 < m < 1.0:
            pop.append(dict(Set=s, pub=g.Reference.iloc[0], m=m, se=se, s3max=g.s3.max()))
P = pd.DataFrame(pop)


def poblacion(sub):
    w = 1 / sub.se ** 2; mu = np.sum(w * sub.m) / np.sum(w)
    tau2 = max(np.var(sub.m, ddof=1) - np.median(sub.se ** 2), 1e-5)
    # media con ponderación de efectos aleatorios
    w2 = 1 / (sub.se ** 2 + tau2); mu = np.sum(w2 * sub.m) / np.sum(w2)
    return mu, tau2


mu, tau2 = poblacion(P)
print(f"Población: {len(P)} sets, {P.pub.nunique()} publicaciones | μm = {mu:.3f} | τ (entre sets) = {np.sqrt(tau2):.3f} | "
      f"mediana se(m) = {P.se.median():.3f}")
for lo, hi in [(0, 1), (1, 2.5), (2.5, 5)]:
    sb = P[(P.s3max >= lo) & (P.s3max < hi)]
    print(f"  sets con σ3,max {lo}–{hi} MPa: n = {len(sb)}, μm = {poblacion(sb)[0]:.3f}" if len(sb) > 3 else "")


# --------------------------------------------- 2–3. validación
def evaluar(corte_cal, corte_pred, etiqueta):
    rows = []
    for s, g in df.groupby("Set"):
        cal = g[g.sn <= corte_cal]; pre = g[g.sn > corte_pred]
        if len(cal) < 2 or len(pre) < 1:
            continue
        pb = g.Reference.iloc[0]; mu_, t2_ = poblacion(P[P.pub != pb])
        out = {}
        for nm, m_ in [("m=0.9", 0.9), ("m=0.87", 0.87), ("μm del pliegue", mu_)]:
            f1, _, _ = ajuste(cal.s3.values, cal.q.values, m_); out[nm] = (f1, m_)
        if len(cal) >= 3:
            f1l, ml, sel = ajuste(cal.s3.values, cal.q.values)
            mpost = (ml / sel ** 2 + mu_ / t2_) / (1 / sel ** 2 + 1 / t2_) if np.isfinite(sel) else mu_
            out["m libre del set"] = (f1l, ml)
        else:
            mpost = mu_
        f1p, _, _ = ajuste(cal.s3.values, cal.q.values, mpost); out["Bayes (Leps 3.0)"] = (f1p, mpost)
        # previa centrada en el m de extrapolación (0.87) con la dispersión poblacional entre sets
        if len(cal) >= 3 and np.isfinite(sel):
            mp87 = (ml / sel ** 2 + 0.87 / t2_) / (1 / sel ** 2 + 1 / t2_)
        else:
            mp87 = 0.87
        f1q, _, _ = ajuste(cal.s3.values, cal.q.values, mp87); out["Bayes previa 0.87"] = (f1q, mp87)
        for nm, (f1, m_) in out.items():
            qp = sigma1(tau_leps2, pre.s3.values, np.full(len(pre), f1), m_)[0] - pre.s3.values
            for k in range(len(pre)):
                rows.append(dict(Set=s, pub=pb, modelo=nm, sn=pre.sn.values[k], ncal=len(cal), err=qp[k] / pre.q.values[k] - 1))
    R = pd.DataFrame(rows)
    print(f"\n{etiqueta}: sets {R.Set.nunique()}, publicaciones {R.pub.nunique()}")
    for nm in ["m=0.9", "m=0.87", "μm del pliegue", "m libre del set", "Bayes (Leps 3.0)", "Bayes previa 0.87"]:
        b = R[R.modelo == nm]
        if b.empty:
            continue
        print(f"  {nm:18s} n={len(b):3d} sesgo {100*b.err.mean():+5.1f} % | EAM {100*b.err.abs().mean():4.1f} % | "
              f"P90 sobreest. {100*np.percentile(b.err, 90):+5.1f} % | peor {100*b.err.max():+5.1f} %")
    return R


RB = evaluar(1.5, 2.0, "Modo B (calibración σ'n ≤ 1.5 MPa, predicción σ'n > 2 MPa)")
RC = evaluar(3.0, 3.0, "Modo C (calibración σ'n ≤ 3 MPa, predicción σ'n > 3 MPa)")

# --------------------------------------------- bandas del modo B con m = 0.87
b = RB[RB.modelo == "m=0.87"]
print("\nBandas de extrapolación con m = 0.87 (modo B): factor sobre q no excedido en 90 % y 80 %")
for lo, hi in [(2, 3), (3, 8)]:
    x = 1 / (1 + b[(b.sn > lo) & (b.sn <= hi)].err)
    print(f"  σ'n {lo}–{hi} MPa: n = {len(x)}, P10 = {np.percentile(x, 10):.3f}, P20 = {np.percentile(x, 20):.3f}")
json.dump(dict(mu=mu, tau=float(np.sqrt(tau2)), nsets=len(P)), open(AQUI / "leps3_bayes.json", "w"), indent=1)
P.to_csv(AQUI / "leps3_poblacion_m.csv", index=False); RB.to_csv(AQUI / "leps3_bayes_B.csv", index=False); RC.to_csv(AQUI / "leps3_bayes_C.csv", index=False)
