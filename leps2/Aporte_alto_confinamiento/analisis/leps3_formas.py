"""Modo B (calibrar con σ'n ≤ 1.5 MPa, predecir σ'n ≥ 2 MPa) para varias formas de envolvente.
Para cada forma se precalcula, en una grilla de parámetros globales, el error de cada set; luego se elige el parámetro
dejando fuera cada publicación (LOPO). Errores en q = σ1 − σ3."""
import sys, json, warnings, itertools, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import minimize_scalar
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import sigma1, tau_leps2, tau_leps3, S0, CLASE  # noqa: E402

df = load_db()
df = df[(df["Lab Test"] == "TRX") & (df.s3 > 0) & df.s1.notna()].copy(); df["q"] = df.s1 - df.s3


def tau_bolton(sn, phi1, phics, scr):
    """Bolton (1986) en forma secante: φs = φcs + (φ1 − φcs)·ln(σcr/σn)/ln(σcr/σ0), con φs ≥ φcs."""
    phis = phics + (phi1 - phics) * np.maximum(np.log(scr / sn), 0) / np.log(scr / S0)
    return sn * np.tan(np.radians(phis))


def tau_tanpot(sn, phi1, phics, n):
    """tan φs = tan φcs + (tan φ1 − tan φcs)·(σn/σ0)^−n."""
    tc = np.tan(np.radians(phics))
    return sn * (tc + (np.tan(np.radians(phi1)) - tc) * (sn / S0) ** (-n))


FORMAS = {
    "Potencia (Leps 2.0)": (tau_leps2, [(m,) for m in np.round(np.arange(0.80, 0.951, 0.01), 2)]),
    "Bolton con piso": (tau_bolton, list(itertools.product(range(26, 41, 2), [3, 5, 8, 12, 20, 30, 50, 80, 150, 300]))),
    "Decaimiento a φcs": (tau_tanpot, list(itertools.product(range(26, 41, 2), [0.05, 0.1, 0.15, 0.2, 0.3, 0.45, 0.6, 0.8]))),
    "Piso suave (v1)": (tau_leps3, list(itertools.product(range(26, 41, 2), [1, 2, 4, 8, 15, 30, 60, 120]))),
}

sets = []
for s, g in df.groupby("Set"):
    lo = g[g.sn <= 1.5]; hi = g[g.sn >= 2]
    if len(lo) >= 2 and len(hi) >= 1:
        sets.append((s, g.Reference.iloc[0], lo.s3.values, lo.q.values, hi.s3.values, hi.q.values, hi.sn.values))
print(f"sets {len(sets)}, publicaciones {len({x[1] for x in sets})}")

t0 = time.time(); TAB = {}
for nombre, (fn, grilla) in FORMAS.items():
    E = []   # E[j][i] = errores del set i con el parámetro j
    for par in grilla:
        fila = []
        for (s, pb, s3l, ql, s3h, qh, snh) in sets:
            obj = lambda f1: np.sum(np.log(np.maximum(sigma1(fn, s3l, np.full(len(s3l), f1), *par)[0] - s3l, 1e-6) / ql) ** 2)
            f1 = minimize_scalar(obj, bounds=(15, 70), method="bounded", options={"xatol": 0.01}).x
            qp = sigma1(fn, s3h, np.full(len(s3h), f1), *par)[0] - s3h
            fila.append(qp / qh - 1)
        E.append(fila)
    TAB[nombre] = (grilla, E)
    print(f"  {nombre}: {len(grilla)} puntos de grilla ({time.time() - t0:.0f} s)")

pubs = sorted({x[1] for x in sets}); SN = [x[6] for x in sets]; PB = [x[1] for x in sets]
print("\nLOPO (parámetro global elegido sin la publicación evaluada; criterio: mínimo error cuadrático medio en ln q):")
res = {}
for nombre, (grilla, E) in TAB.items():
    errs, sns, elegidos = [], [], []
    for pb in pubs:
        tr = [i for i in range(len(sets)) if PB[i] != pb]; te = [i for i in range(len(sets)) if PB[i] == pb]
        costo = [np.mean(np.concatenate([np.log1p(E[j][i]) ** 2 for i in tr])) for j in range(len(grilla))]
        j = int(np.argmin(costo)); elegidos.append(grilla[j])
        for i in te:
            errs.append(E[j][i]); sns.append(SN[i])
    e = np.concatenate(errs); sn = np.concatenate(sns)
    # parámetro con todos los datos
    costo = [np.mean(np.concatenate([np.log1p(E[j][i]) ** 2 for i in range(len(sets))])) for j in range(len(grilla))]
    jbest = int(np.argmin(costo))
    res[nombre] = dict(param_todos=list(map(float, grilla[jbest])), elegidos=[list(map(float, x)) for x in elegidos])
    m2, m3 = sn >= 2, sn >= 3
    print(f"  {nombre:22s} parámetro (todos): {grilla[jbest]} | σn≥2: sesgo {100*e[m2].mean():+5.1f} % EAM {100*np.abs(e[m2]).mean():4.1f} % "
          f"| σn≥3: sesgo {100*e[m3].mean():+5.1f} % EAM {100*np.abs(e[m3]).mean():4.1f} % (n={m3.sum()}) | rango elegido: "
          f"{min(map(tuple, elegidos))}–{max(map(tuple, elegidos))}")
json.dump(res, open(AQUI / "leps3_formas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# ------------------------------------------------- control de regresión a la media para la interacción densidad × esfuerzo
from common import within_set  # noqa: E402
w = within_set(load_db()); h = w[w.sn >= S0].copy(); h["L"] = np.log10(h.sn / S0)
q5 = {"good": 53, "moderate": 50, "low": 47}
h["phi1_pred"] = [q5.get(CLASE.get(m_), 50) - 20 * e_ for m_, e_ in zip(h.mat, h.e)]
h["d"] = h.phi1_pred - h.phi1_pred.mean()
c = np.linalg.lstsq(np.c_[h.L, h.L * h.d], h.dphi1, rcond=None)[0]
rng = np.random.default_rng(3); ss = h.Set.unique(); bs = []
for _ in range(1000):
    dd = pd.concat([h[h.Set == k] for k in rng.choice(ss, len(ss))])
    bs.append(np.linalg.lstsq(np.c_[dd.L, dd.L * dd.d], dd.dphi1, rcond=None)[0][1])
print(f"\nInteracción con moderador independiente (φ'1 predicho por calidad y e, no por los ensayos): "
      f"término {c[1]:+.3f} °/década por grado, IC 90 % [{np.percentile(bs, 5):+.3f}, {np.percentile(bs, 95):+.3f}]")
