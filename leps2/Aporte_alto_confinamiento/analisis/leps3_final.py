"""Variantes finales en modo predictivo (LOPO) y bandas de error por nivel de esfuerzo para una envolvente de diseño."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import sigma1, tau_leps2, CLASE  # noqa: E402

df = load_db()
df = df[(df["Lab Test"] == "TRX") & (df.s3 > 0) & df.s1.notna() & df.e.notna()].copy()
df["q"] = df.s1 - df.s3; df["ci"] = df["Material Type"].map(CLASE).map({"good": 0, "moderate": 1, "low": 2})
S3, Q, E, CI, PUB = df.s3.values, df.q.values, df.e.values, df.ci.values, df.Reference.values
PUBL = np.array([53, 50, 47.0])


def pred(phie0, w, m, idx):
    return sigma1(tau_leps2, S3[idx], phie0[CI[idx]] - w * E[idx], m)[0] - S3[idx]


def fit(idx, m_fijo=None):
    idx = idx[S3[idx] >= 0.06]                     # guía 60-600: sin σ3 < 60 kPa
    if m_fijo is None:
        f = lambda p: np.log(np.maximum(pred(np.array(p[:3]), p[3], p[4], idx), 1e-6) / Q[idx])
        return least_squares(f, [53, 50, 47, 20, 0.88], bounds=([35] * 3 + [0, 0.6], [70] * 3 + [45, 1])).x
    f = lambda p: np.log(np.maximum(pred(np.array(p[:3]), p[3], m_fijo, idx), 1e-6) / Q[idx])
    return np.r_[least_squares(f, [53, 50, 47, 20], bounds=([35] * 3 + [0], [70] * 3 + [45])).x, m_fijo]


V = {"Publicado, m = 0.9": lambda tr, te: pred(PUBL, 20, 0.9, te),
     "Publicado φ'1, m = 0.87": lambda tr, te: pred(PUBL, 20, 0.87, te),
     "Publicado φ'1, m = 0.85": lambda tr, te: pred(PUBL, 20, 0.85, te),
     "Reajuste σ3 ≥ 60 kPa, m libre": lambda tr, te: (lambda p: pred(p[:3], p[3], p[4], te))(fit(tr)),
     "Reajuste σ3 ≥ 60 kPa, m = 0.87": lambda tr, te: (lambda p: pred(p[:3], p[3], p[4], te))(fit(tr, 0.87))}
ERR = {}
for nm, fn in V.items():
    e = np.full(len(df), np.nan)
    for pb in np.unique(PUB):
        tr, te = np.where(PUB != pb)[0], np.where(PUB == pb)[0]
        e[te] = fn(tr, te) / Q[te] - 1
    ERR[nm] = e
bins = [(0.06, 0.3), (0.3, 1), (1, 2), (2, 5)]
print("Modo A, LOPO (sesgo / error absoluto medio / percentil 90 de sobreestimación, en q):")
for nm, e in ERR.items():
    print(f"  {nm:32s} " + " | ".join(
        f"σ3 {a}–{b}: {100*e[(S3>=a)&(S3<b)].mean():+5.1f}/{100*np.abs(e[(S3>=a)&(S3<b)]).mean():4.1f}/{100*np.percentile(e[(S3>=a)&(S3<b)],90):+5.1f}"
        for a, b in bins))
pall = fit(np.arange(len(df))); p87 = fit(np.arange(len(df)), 0.87)
print("  reajuste m libre (todos): φe0 = %.1f/%.1f/%.1f ω = %.1f m = %.3f" % tuple(pall))
print("  reajuste m = 0.87 (todos): φe0 = %.1f/%.1f/%.1f ω = %.1f" % tuple(p87[:4]))

# bandas de diseño: cuantiles de ln(q_obs/q_pred) por rango de esfuerzo, convertidos a reducción de φ'1 equivalente
print("\nBandas para envolvente de diseño (modelo «Publicado φ'1, m = 0.87»):")
e = ERR["Publicado φ'1, m = 0.87"]; r = np.log1p(e)
filas = []
for a, b in [(0.06, 0.3), (0.3, 1), (1, 2), (2, 5)]:
    mk = (S3 >= a) & (S3 < b)
    # cuantil 10 % de q_obs/q_pred = 1/(1+e) -> factor sobre q para no ser excedido 90 %
    f10 = np.percentile(1 / (1 + e[mk]), 10); f20 = np.percentile(1 / (1 + e[mk]), 20)
    filas.append(dict(rango=f"{a}–{b}", n=int(mk.sum()), sd_ln=r[mk].std(), factor_q_p10=f10, factor_q_p20=f20))
B = pd.DataFrame(filas); print(B.round(3).to_string(index=False))
# equivalencia del factor en φ'1 para φ'1 = 41° (por iteración: φ'1 que produce q·factor a σ3 típico del rango)
for row in filas:
    s3t = np.sqrt(float(row["rango"].split("–")[0]) * float(row["rango"].split("–")[1]))
    q41 = sigma1(tau_leps2, np.array([s3t]), np.array([41.0]), 0.87)[0][0] - s3t
    for etq in ("factor_q_p10", "factor_q_p20"):
        obj = lambda f1: (sigma1(tau_leps2, np.array([s3t]), np.array([f1]), 0.87)[0][0] - s3t) / q41 - row[etq]
        lo, hi = 20.0, 41.0
        for _ in range(60):
            mid = (lo + hi) / 2; lo, hi = (mid, hi) if obj(mid) < 0 else (lo, mid)
        row[etq.replace("factor_q", "dphi1")] = (lo + hi) / 2 - 41
B = pd.DataFrame(filas); print(B[["rango", "n", "dphi1_p10", "dphi1_p20"]].round(1).to_string(index=False))
json.dump(dict(bandas=filas, reajuste_libre=pall.tolist(), reajuste_087=p87.tolist()), open(AQUI / "leps3_final.json", "w"), indent=1)
