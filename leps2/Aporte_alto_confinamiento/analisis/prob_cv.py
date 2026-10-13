"""Calibración probabilística de Leps 3.0 (modelo jerárquico log–log) con validación dejando fuera cada publicación.
Modo A: predicción sin ensayos del sitio (calidad de roca y e).  Modo B: actualización con ensayos del sitio de
σ′n ≤ 1.5 MPa (posterior gaussiana exacta) y predicción de σ′n ≥ 2 MPa.
Métricas: cobertura de intervalos centrales de 80 % y 90 %, frecuencia bajo el percentil 10 (debe ser ~10 %),
ancho medio del intervalo de 80 % y CRPS. Referencia: Leps 2.0 publicado con dispersión log-normal constante."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
from scipy.stats import norm
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db, PA  # noqa: E402
from modelos import CLASE  # noqa: E402

S0 = 10 * PA
df = load_db()
df = df[(df.s3.isna() | (df.s3 >= 0.06)) & (df.sn > 0) & df.e.notna()].copy()
df["clase"] = df["Material Type"].map(CLASE)
df["x"] = np.log(df.sn / S0); df["y"] = np.log(df.tau / S0)
df = df[df.groupby("Set").x.transform("size") >= 2].reset_index(drop=True)
XB = [-np.inf, -1.0, 0.0, 1.0, np.inf]                      # rangos de x para σε(x)
CL = ["good", "low", "moderate"]


def ajustar(d):
    r = smf.mixedlm("y ~ 0 + C(clase) + e + x", d, groups=d["Set"], re_formula="~x").fit(method="lbfgs", reml=True)
    fe = r.fe_params; Sig = r.cov_re.values
    # residuo condicional por rango de x (heterocedasticidad)
    res = d.y - r.fittedvalues
    sx = [res[(d.x >= a) & (d.x < b)].std() for a, b in zip(XB[:-1], XB[1:])]
    return dict(fe=fe, Sig=Sig, sx=np.array(sx), s=np.sqrt(r.scale))


def sigma_eps(p, x):
    return p["sx"][np.clip(np.digitize(x, XB[1:-1]), 0, 3)]


def crps(mu, sd, y):
    z = (y - mu) / sd
    return sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))


def metricas(mu, sd, y):
    z = (y - mu) / sd
    return dict(n=len(y), cob80=np.mean(np.abs(z) <= 1.2816), cob90=np.mean(np.abs(z) <= 1.6449),
                bajo_p10=np.mean(z < -1.2816), ancho80=np.mean(2 * 1.2816 * sd), crps=np.mean(crps(mu, sd, y)),
                sesgo=np.mean(np.exp(y - mu) - 1))


filasA, filasB = [], []
for pb in df.Reference.unique():
    tr = df[df.Reference != pb]; te = df[df.Reference == pb]
    p = ajustar(tr)
    # ---- modo A
    fe = p["fe"]; th = np.array([fe[f"C(clase)[{c}]"] for c in te.clase]) + fe["e"] * te.e.values
    mu = th + fe["x"] * te.x.values
    Z = np.c_[np.ones(len(te)), te.x.values]
    var = np.einsum("ij,jk,ik->i", Z, p["Sig"], Z) + sigma_eps(p, te.x.values) ** 2
    # referencia: Leps 2.0 publicado + dispersión constante (estimada en el pliegue de entrenamiento)
    phi1 = np.array([{"good": 53, "moderate": 50, "low": 47}[c] for c in te.clase]) - 20 * te.e.values
    mu0 = np.log(np.tan(np.radians(phi1))) + 0.9 * te.x.values
    phi1tr = np.array([{"good": 53, "moderate": 50, "low": 47}[c] for c in tr.clase]) - 20 * tr.e.values
    s0 = np.std(tr.y.values - (np.log(np.tan(np.radians(phi1tr))) + 0.9 * tr.x.values))
    for k in range(len(te)):
        filasA.append(dict(pub=pb, x=te.x.values[k], y=te.y.values[k], mu=mu[k], sd=np.sqrt(var[k]), mu0=mu0[k], sd0=s0))
    # ---- modo B: por set, posterior con ensayos σn ≤ 1.5 MPa
    for s, g in te.groupby("Set"):
        lo = g[g.sn <= 1.5]; hi = g[g.sn >= 2]
        if len(lo) < 2 or len(hi) < 1:
            continue
        cl = g.clase.iloc[0]; e = g.e.iloc[0]
        m0 = np.array([fe[f"C(clase)[{cl}]"] + fe["e"] * e, fe["x"]])
        Zl = np.c_[np.ones(len(lo)), lo.x.values]; Rl = np.diag(sigma_eps(p, lo.x.values) ** 2)
        Sinv = np.linalg.inv(p["Sig"]); Pc = np.linalg.inv(Sinv + Zl.T @ np.linalg.inv(Rl) @ Zl)
        mc = Pc @ (Sinv @ m0 + Zl.T @ np.linalg.inv(Rl) @ lo.y.values)
        Zh = np.c_[np.ones(len(hi)), hi.x.values]
        muh = Zh @ mc; vh = np.einsum("ij,jk,ik->i", Zh, Pc, Zh) + sigma_eps(p, hi.x.values) ** 2
        for k in range(len(hi)):
            filasB.append(dict(pub=pb, Set=s, x=hi.x.values[k], y=hi.y.values[k], mu=muh[k], sd=np.sqrt(vh[k])))
A = pd.DataFrame(filasA); B = pd.DataFrame(filasB)

print("MODO A (sin ensayos del sitio), validación dejando fuera cada publicación")
print("  rango σ′n (MPa)  | modelo              |   n | cob 80 % | cob 90 % | bajo P10 | ancho 80 % (ln) | CRPS   | sesgo τ")
for a, b in [(-np.inf, -1), (-1, 0), (0, 1), (1, np.inf)]:
    d = A[(A.x >= a) & (A.x < b)]
    etq = f"{S0*np.exp(a) if np.isfinite(a) else 0:.2f}–{S0*np.exp(b) if np.isfinite(b) else 9:.2f}"
    for nm, mu, sd in [("Leps 3.0 jerárquico", d.mu, d.sd), ("Leps 2.0 + σ const.", d.mu0, d.sd0)]:
        m = metricas(mu.values, sd.values, d.y.values)
        print(f"  {etq:16s} | {nm:19s} | {m['n']:3d} | {m['cob80']:7.0%} | {m['cob90']:7.0%} | {m['bajo_p10']:7.0%} | "
              f"{m['ancho80']:14.3f} | {m['crps']:.4f} | {m['sesgo']:+.1%}")
print("\nMODO B (actualizado con ensayos del sitio de σ′n ≤ 1.5 MPa; predicción σ′n ≥ 2 MPa)")
m = metricas(B.mu.values, B.sd.values, B.y.values)
print(f"  sets {B.Set.nunique()}, ensayos {m['n']}: cobertura 80 % {m['cob80']:.0%} | 90 % {m['cob90']:.0%} | bajo P10 {m['bajo_p10']:.0%} | "
      f"ancho 80 % {m['ancho80']:.3f} | CRPS {m['crps']:.4f} | sesgo {m['sesgo']:+.1%}")
pfin = ajustar(df)
sd = np.sqrt(np.diag(pfin["Sig"]))
print(f"\nParámetros con la base entera: fijos {dict(pfin['fe'].round(4))}")
print(f"  sd(θ) {sd[0]:.4f}, sd(m) {sd[1]:.4f}, corr {pfin['Sig'][0,1]/sd[0]/sd[1]:+.2f}, σε por rango de x {np.round(pfin['sx'], 4)}")
json.dump(dict(fe=pfin["fe"].to_dict(), Sig=pfin["Sig"].tolist(), sx=pfin["sx"].tolist(), XB=[-9, -1, 0, 1, 9]),
          open(AQUI / "leps3_prob_parametros.json", "w"), indent=1)
A.to_csv(AQUI / "prob_cv_A.csv", index=False); B.to_csv(AQUI / "prob_cv_B.csv", index=False)
