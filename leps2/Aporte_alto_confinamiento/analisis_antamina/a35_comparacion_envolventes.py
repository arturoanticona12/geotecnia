"""Representatividad de la curva propuesta frente a Leps (1970) y a Indraratna et al. (1993) (pedido del usuario, 2026-10-13).
Compara cada envolvente con los ensayos de Antamina, cada ensayo a su σ′n y a su e0:
  - Curva propuesta: Leps 2.0 con φ′e=0 = 48.47°, ω = 20°, m = 0.85, evaluada a la e0 del ensayo, sin el tope (límite de diseño a e = 0.45).
  - Leps (1970), envolventes superior, media e inferior, y cota inferior de Indraratna et al. (1993), en la forma de la Ec. 9 de
    Cylwik et al. (2025): φ′1 = 46°, 41°, 36° y 33°, m = 0.9, sin dependencia de e.
Residuo = φ′s medido − φ′s de la envolvente (°); negativo = la envolvente sobreestima la resistencia del ensayo.
Bloques: (1) los 37 ensayos del ajuste; (2) los mismos, con la curva propuesta validada dejando fuera cada set (el nivel se recalcula
sin el set que se predice: validación cruzada por sets); (3) los 36 triaxiales CU de contraste (a16), no usados en el ajuste.
También: forma (m) con la prueba de extrapolación de la base mundial (a31) y φ′s de cada envolvente a e = 0.45 (diseño).
Escribe a35_comparacion.json y a35_residuos.csv."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from tope import TOPE  # noqa: E402
S0, OM, EB = 1.013, 20.0, 0.45
A33 = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8")); PE0, MC = A33["parametros"]["pe0"], A33["parametros"]["m_a"]
A31 = json.load(open(AQ / "a31_m_defendible.json", encoding="utf-8"))
S34 = pd.read_csv(AQ / "a34_phi1_sets.csv"); NIV_SET = dict(zip(S34.set, S34.phi_e0))
assert abs(np.mean(list(NIV_SET.values())) - PE0) < 1e-6

# ensayos del ajuste: misma conversión que a11 (triaxiales a σ′n–τ con la m de la curva)
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False); tx = (d.tipo == "TX").values
sn = d.sn_ds.values.copy(); tau = d.tau_ds.values.copy()
D, Sm = (d.s1 - d.s3).values[tx], (d.s1 + d.s3).values[tx]
sp = (np.sqrt(4 * MC * (MC - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (MC - 1) * D)
sn[tx] = Sm / 2 - D / 2 * sp; tau[tx] = D / 2 * np.sqrt(1 - sp ** 2)
P = pd.DataFrame(dict(set=(d.fuente_id + "|" + d.set_id.astype(str)).values, litologia=d.litologia.values, tipo=d.tipo.values,
                      sn=sn, e=d.e0_adoptado.values, phis=np.degrees(np.arctan(tau / sn))))

phis_l2 = lambda s, pe0, e, m=MC: np.degrees(np.arctan(np.tan(np.radians(pe0 - OM * e)) * (s / S0) ** (m - 1)))
phis_09 = lambda s, p1: np.degrees(np.arctan(np.tan(np.radians(p1)) * (s / S0) ** (0.9 - 1)))
MOD = {"Curva propuesta": lambda s, e: phis_l2(s, PE0, e),   # sin tope: el tope es un límite de diseño a e = 0.45, no parte del ajuste
       "Leps (1970), superior": lambda s, e: phis_09(s, 46.0), "Leps (1970), media": lambda s, e: phis_09(s, 41.0),
       "Leps (1970), inferior": lambda s, e: phis_09(s, 36.0), "Indraratna et al. (1993)": lambda s, e: phis_09(s, 33.0)}
RANGOS = [("Todos", 0, 99), ("σ′n < 0.5 MPa", 0, 0.5), ("0.5–2 MPa", 0.5, 2), ("2–4.62 MPa", 2, 99)]


def stats(r):
    r = np.asarray(r, float)
    return dict(n=int(len(r)), media=float(r.mean()), mediana=float(np.median(r)), mae=float(np.abs(r).mean()),
                rmse=float(np.sqrt((r ** 2).mean())), bajo=int((r < 0).sum()))


out = {"definicion": "residuo = φ′s medido − φ′s de la envolvente, a σ′n y e0 del ensayo (°)", "tope": TOPE, "ajuste": {}, "loso": {}, "cu": {}}
for nm, f in MOD.items():
    P[nm] = P.phis - f(P.sn.values, P.e.values)
    out["ajuste"][nm] = {rg: stats(P[nm][(P.sn > a) & (P.sn <= b)]) for rg, a, b in RANGOS}
# validación cruzada por sets: nivel = media de φ′e=0 de los otros 12 sets
P["pe0_loso"] = [(sum(NIV_SET.values()) - NIV_SET[s]) / (len(NIV_SET) - 1) for s in P.set]
P["Curva propuesta, sin su set"] = P.phis - phis_l2(P.sn.values, P.pe0_loso.values, P.e.values)
out["loso"] = {rg: stats(P["Curva propuesta, sin su set"][(P.sn > a) & (P.sn <= b)]) for rg, a, b in RANGOS}
# triaxiales CU de contraste (a16), no usados en el ajuste
C = pd.read_csv(AQ / "a16_contraste.csv")
for nm, f in MOD.items():
    out["cu"][nm] = stats(C.phis - f(C.sn.values, C.e.values))
out["cu_n_grupos"] = C.grupo.value_counts().to_dict()
# forma: prueba de extrapolación de la base mundial (a31): nivel con σ′n ≤ 2 MPa, predicción de los ensayos > 4.6 MPa
ext = {round(r["m"], 2): r for r in A31["extrapolacion"]}
out["forma"] = {str(m): dict(sesgo=ext[m]["mundo_sesgo"], mae=ext[m]["mundo_mae"], n=ext[m]["n_w"]) for m in (0.85, 0.9)}
# φ′s de cada envolvente a e = 0.45
SNT = [1.0, 4.6, 10.0]
out["diseno"] = {nm: [float(f(np.array([s]), np.array([EB]))[0]) for s in SNT] for nm, f in MOD.items()}
out["diseno_sn"] = SNT
# φ′1 de los ensayos: a su e0 (sin normalizar) y a e = 0.45
out["phi1_sets_e0"] = dict(media=float(S34.phi1.mean()), e0_media=float(S34.e0.mean()))
out["phi1_sets_eb"] = float(np.mean(S34.phi_e0 - OM * EB))
P.to_csv(AQ / "a35_residuos.csv", index=False, encoding="utf-8-sig")
json.dump(out, open(AQ / "a35_comparacion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for nm in MOD:
    a = out["ajuste"][nm]["Todos"]; c = out["cu"][nm]
    print(f"{nm:28s} ajuste: media {a['media']:+5.2f} mediana {a['mediana']:+5.2f} MAE {a['mae']:4.2f} RMSE {a['rmse']:4.2f} bajo {a['bajo']:2d}/{a['n']}"
          f" | CU: media {c['media']:+5.2f} MAE {c['mae']:4.2f} bajo {c['bajo']}/{c['n']}")
a = out["loso"]["Todos"]; print(f"{'Curva propuesta, sin su set':28s} ajuste: media {a['media']:+5.2f} mediana {a['mediana']:+5.2f} MAE {a['mae']:4.2f} RMSE {a['rmse']:4.2f} bajo {a['bajo']}/{a['n']}")
for nm in MOD:
    print(nm, {rg: round(v["media"], 2) for rg, v in out["ajuste"][nm].items()})
print("diseño e = 0.45:", {k: [round(x, 1) for x in v] for k, v in out["diseno"].items()})
print("φ′1 sets: a su e0", out["phi1_sets_e0"], "a e = 0.45", round(out["phi1_sets_eb"], 2), "| forma", out["forma"])
print("escrito a35_comparacion.json y a35_residuos.csv")
