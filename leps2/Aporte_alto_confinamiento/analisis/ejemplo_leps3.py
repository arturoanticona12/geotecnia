"""Ejemplo aplicado de Leps 3.0 probabilístico: botadero genérico de 700 m (2H:1V, fundación horizontal), método de Bishop.
Envolventes por percentil: (a) material genérico de calidad moderada, e = 0.45; (b) desmonte del yacimiento de skarn,
mezcla de litologías ponderada por tonelaje. Para cada uno: P50, P10 de la envolvente media del material (escala de la
superficie de falla) y P10 puntual (incluye la dispersión dentro del material; cota conservadora)."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(RAIZ / "leps3"))
import leps3 as L  # noqa: E402
from slope import search  # noqa: E402

SN = np.logspace(-3, np.log10(20), 60)


def env_tabla(phis):
    """Envolvente τ(σn) interpolada en log σn a partir de φ′s en la grilla SN."""
    lt = np.log(SN * np.tan(np.radians(phis)))
    t = lambda s: np.exp(np.interp(np.log(np.maximum(s, 1e-6)), np.log(SN), lt, left=None, right=None)) * np.where(s < SN[0], np.maximum(s, 1e-6) / SN[0], 1)
    dt = lambda s: (t(np.maximum(s, 1e-6) * 1.001) - t(np.maximum(s, 1e-6) * 0.999)) / (0.002 * np.maximum(s, 1e-6))
    return t, dt


def mezcla(ests, w, p, puntual, n=200000, seed=3):
    """Percentil p de φ′s de la mezcla de litologías (pesos w). puntual=False: solo incertidumbre de la envolvente media."""
    rng = np.random.default_rng(seed); x = np.log(SN / L.S0); ys = []
    for k, est in ests.items():
        nk = int(round(n * w[k]))
        if nk == 0:
            continue
        th, m = L.muestras(est, nk, rng); y = th[:, None] + m[:, None] * x[None, :]
        if puntual:
            y = y + rng.normal(0, 1, (nk, 1)) * L.sigma_eps(x)[None, :]
        ys.append(y)
    ph = np.degrees(np.arctan(L.S0 * np.exp(np.vstack(ys)) / SN[None, :]))
    return np.percentile(ph, p, axis=0)


def promedio(ests, w, p, n=100000, seed=4):
    """Percentil p de φ′s de la envolvente media del botadero: τ = Σ w_k τ_k, con la envolvente media de cada litología
    muestreada de forma independiente (una superficie de escala de botadero cruza todas las litologías)."""
    rng = np.random.default_rng(seed); x = np.log(SN / L.S0); tau = 0
    for k, est in ests.items():
        if w[k] == 0:
            continue
        th, m = L.muestras(est, n, rng); tau = tau + w[k] * L.S0 * np.exp(th[:, None] + m[:, None] * x[None, :])
    return np.percentile(np.degrees(np.arctan(tau / SN[None, :])), p, axis=0)


# (a) material genérico
pr = L.previa("moderada", 0.45)
casos = {"Genérico|P50": L.percentiles(SN, pr, (50,), n=200000)[50],
         "Genérico|P10 envolvente media": L.percentiles(SN, pr, (10,), material_nuevo=False, n=200000)[10],
         "Genérico|P10 puntual": L.percentiles(SN, pr, (10,), n=200000)[10]}
# (b) desmonte del yacimiento (posteriores por litología del análisis del sitio; material nuevo de cada litología)
R = pd.read_csv(RAIZ / "analisis_antamina" / "litologia_posterior.csv")
ests = {r.litologia: L.Estado(np.array([r.theta, r.m]), np.array(json.loads(r.covar)) + L.SIGMA) for _, r in R.iterrows()}
comp = pd.read_excel(RAIZ / "datos_antamina" / "base" / "antamina_base.xlsx", sheet_name="composicion_desmonte_LE2")
w = comp.set_index("litologia_normalizada").pct_tonelaje_LE2.reindex(list(ests)).fillna(0); w = (w / w.sum()).to_dict()
casos["Skarn|P50"] = mezcla(ests, w, 50, True)
# caliza y margas no tienen ensayos y comparten la previa: un solo material (no independientes) para el promedio
e2 = {k: v for k, v in ests.items() if k != "Marga-Limolita"}; w2 = {k: w[k] for k in e2}; w2["Caliza"] += w["Marga-Limolita"]
casos["Skarn|P50 envolvente media del botadero"] = promedio(e2, w2, 50)
casos["Skarn|P10 envolvente media del botadero"] = promedio(e2, w2, 10)
casos["Skarn|P10 puntual"] = mezcla(ests, w, 10, True)

out = {}
for nm, ph in casos.items():
    r = search(700.0, 26.57, env_tabla(ph))
    out[nm] = dict(F=float(r["F"]), snmax=float(r["sn"].max()),
                   phi_s={f"{s:g}": float(np.interp(np.log(s), np.log(SN), ph)) for s in (1, 3, 6, 10)})
    print(f"{nm:32s} FS = {r['F']:.3f}  σ′n,max = {r['sn'].max():.2f} MPa  φ′s(3 MPa) = {out[nm]['phi_s']['3']:.1f}°")
json.dump(out, open(AQUI / "ejemplo_leps3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
# pares τ–σn (kPa) para un material de tipo función en Slide2
json.dump({nm: [(0.0, 0.0)] + [(round(s * 1000, 3), round(s * np.tan(np.radians(p)) * 1000, 3)) for s, p in zip(SN[::2], ph[::2])]
           for nm, ph in casos.items()}, open(AQUI / "ejemplo_leps3_funciones.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
