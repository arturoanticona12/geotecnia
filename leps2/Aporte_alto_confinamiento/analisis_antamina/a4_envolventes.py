"""Análisis 6: envolvente probabilística por litología (Leps 3.0 actualizado con Antamina) y ponderación por la
composición del desmonte LE2. Modelo: ln(τ/σ0) = θ + m·x, x = ln(σn/σ0). Para cada litología, posterior del par medio
(θ, m) combinando la previa mundial (clase de Cylwik y e) con las posteriores de sus sets (cada una con su incertidumbre
más la variabilidad entre sets Σ); predicción para un material nuevo de esa litología: cov_post + Σ + σε²."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8"); pd.set_option("display.width", 220)
AQUI = Path(__file__).parent; RAIZ = AQUI.parent
P = json.load(open(RAIZ / "analisis" / "leps3_prob_parametros.json")); fe = P["fe"]; Sig = np.array(P["Sig"]); SX = np.array(P["sx"])
Q = pd.read_csv(AQUI / "sets_posterior.csv")
comp = pd.read_excel(RAIZ / "datos_antamina" / "base" / "antamina_base.xlsx", sheet_name="composicion_desmonte_LE2")
PA = 0.1013; S0 = 10 * PA; E_REF = 0.42            # e de referencia: mediana de los ensayos ROM de gran escala de Antamina
CL = {"Mármol": "low", "Hornfels": "moderate", "Intrusivo": "low", "Caliza": "low", "Marga-Limolita": "low"}
# solo materiales sin relave para las litologías (las mezclas se tratan aparte)
Q = Q[~Q.set_a.str.contains("ALT|C1_|C2_|C3_")]
Q.loc[Q.set_a.str.contains("DESM-COMP"), "litologia"] = "Mezcla compuesta (A/B/C)"
res = []
for lit in ["Mármol", "Hornfels", "Intrusivo", "Caliza", "Marga-Limolita"]:
    m0 = np.array([fe[f"C(clase)[{CL[lit]}]"] + fe["e"] * E_REF, fe["x"]])
    prec = np.linalg.inv(Sig * 1.0); num = prec @ m0           # previa del par medio de la litología: Σ (incertidumbre de clase)
    g = Q[Q.litologia == lit]
    for _, r in g.iterrows():
        C = np.array(json.loads(r["cov"])); th = r.theta + fe["e"] * (E_REF - r.e0)    # lleva θ del set a e de referencia
        W = np.linalg.inv(Sig + C); prec += W; num += W @ np.array([th, r.m_post])
    cov = np.linalg.inv(prec); mu = cov @ num
    res.append(dict(litologia=lit, n_sets=len(g), theta=mu[0], m=mu[1], covar=cov.tolist()))
R = pd.DataFrame(res)
SN = np.array([0.3, 1.0, 3.0, 6.0, 10.0, 15.0]); filas = []
# material nuevo de cada litología: (θ, m) ~ N(mu, covar + Σ) condicionada a m ≤ 1 (muestreo exacto de leps3) + σε(x)
sys.path.insert(0, str(RAIZ / "leps3")); import leps3 as L  # noqa: E402
EST = {r.litologia: L.Estado(np.array([r.theta, r.m]), np.array(r.covar) + Sig) for _, r in R.iterrows()}
for lit, est in EST.items():
    q = L.percentiles(SN, est, (50, 10, 5), n=200000, rng=np.random.default_rng(5))
    for p in (50, 10, 5):
        for sn, v in zip(SN, q[p]):
            filas.append(dict(litologia=lit, sn=sn, pct=f"P{p:02d}" if p < 10 else f"P{p}", phis=v))
T = pd.DataFrame(filas).pivot_table(index=["litologia", "pct"], columns="sn", values="phis")
print("Parámetros por litología (e = 0.42):")
print(R.assign(phi1=np.degrees(np.arctan(np.exp(R.theta))), sd_phi1=[np.degrees(np.sqrt(c[0][0]) * np.exp(t) / (1 + np.exp(2 * t))) for c, t in zip(R["covar"], R.theta)],
               sd_m=[np.sqrt(c[1][1]) for c in R["covar"]])[["litologia", "n_sets", "phi1", "sd_phi1", "m", "sd_m"]].round(3).to_string(index=False))
print("\nÁngulo secante φ′s (°) para un material nuevo de cada litología, por σ′n (MPa):")
print(T.round(1).to_string())
# ponderación por tonelaje (envolvente media del botadero y su P10 por mezcla de distribuciones)
w = comp.set_index("litologia_normalizada").pct_tonelaje_LE2 / 100
w = w.reindex(["Mármol", "Hornfels", "Intrusivo", "Caliza", "Marga-Limolita"]).fillna(0); w = w / w.sum()
rng = np.random.default_rng(11); out = []
for sn in SN:
    x = np.log(sn / S0); draws = []
    for lit, est in EST.items():
        n = int(round(200000 * w[lit]))
        if n == 0: continue
        th, m = L.muestras(est, n, rng)
        draws.append(th + m * x + rng.normal(0, 1, n) * L.sigma_eps(x))
    t = S0 * np.exp(np.concatenate(draws)); ph = np.degrees(np.arctan(t / sn))
    out.append(dict(sn=sn, P50=np.median(ph), P10=np.percentile(ph, 10), P05=np.percentile(ph, 5),
                    media_ponderada_P50=float(np.sum([w[l] * T.loc[(l, "P50"), sn] for l in w.index]))))
print("\nBotadero LE2 (mezcla por tonelaje: Mármol 39 %, Hornfels 19 %, Marga 19 %, Intrusivo 15 %, Caliza 8 %):")
print(pd.DataFrame(out).round(1).to_string(index=False))
R.to_csv(AQUI / "litologia_posterior.csv", index=False); T.to_csv(AQUI / "litologia_envolventes.csv"); pd.DataFrame(out).to_csv(AQUI / "botadero_envolvente.csv", index=False)

