"""m más defendible con la data de Antamina y la mundial (pedido de WA, 2026-10-12), su incertidumbre y su efecto a grandes esfuerzos.
1) Estimadores: Antamina sola (nivel por set, m común; bootstrap por sets), población mundial (pendientes por set, Paule–Mandel,
   todo el rango y σ′n ≥ 1 MPa; de a18), combinación jerárquica (precisiones) y ajuste conjunto con peso f (a30).
2) Prueba de extrapolación (la que decide para grandes esfuerzos): en cada set con ensayos altos, el nivel (φ′1) se fija con sus
   ensayos de menor esfuerzo y se predice el de mayor esfuerzo con cada m candidata; sesgo y error medio de la predicción.
   Mundo: los sets con algún ensayo sobre 4.60 MPa (σ′n ≤ 2 MPa para el nivel, ensayos > 4.60 MPa para predecir).
   Antamina: sets triaxiales con 3 o más niveles (los dos menores para el nivel, el mayor para predecir).
3) Efecto: φ′s y τ a e = 0.45 para el intervalo de m, con el nivel reajustado (φ′1 por sets, ω = 20°, como a30).
Escribe a31_m_defendible.json."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares, brentq
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from modelos import sigma1, tau_leps2  # noqa: E402
from lepsp_r6 import datos  # noqa: E402
S0, EB, OM = 1.013, 0.45, 20.0
A30 = json.load(open(AQ / "a30_dos_pasos.json", encoding="utf-8")); R18 = json.load(open(AQ / "a18_m_jerarquico.json", encoding="utf-8"))
A = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
A["set"] = A.fuente_id + "|" + A.set_id.astype(str); A["e"] = A.e0_adoptado; A["tx"] = A.tipo == "TX"
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]
SNX = A30["snx"]; W = datos(); W = W[~W.cens] if "cens" in W else W
MS = np.round(np.arange(0.78, 1.0001, 0.01), 2)
out = {"estimadores": {}}

# ---- 1) estimadores
RA, RM, RM1 = R18["antamina"], R18["variantes"]["rango completo"], R18["variantes"]["σ′n ≥ 1 MPa"]
out["estimadores"] = {
    "Antamina sola (a18, nivel por set)": dict(m=RA["m"], se=RA["se"]),
    "Mundo, todos los sets (mediana; P10–P90)": dict(m=RM["m_P50_sets"], p10=RM["m_P10_sets"], p90=RM["m_P90_sets"], tau=RM["tau"]),
    "Mundo, σ′n ≥ 1 MPa (mediana; P10–P90)": dict(m=RM1["m_P50_sets"], p10=RM1["m_P10_sets"], p90=RM1["m_P90_sets"], tau=RM1["tau"]),
    "Jerárquico (precisiones; a18, todo el rango)": dict(m=RM["post_media_sin_truncar"], sd=RM["post_sd_sin_truncar"], peso_antamina=RM["peso_antamina"]),
    "Jerárquico (precisiones; a18, σ′n ≥ 1 MPa)": dict(m=RM1["post_media_sin_truncar"], sd=RM1["post_sd_sin_truncar"], peso_antamina=RM1["peso_antamina"]),
    "Ajuste conjunto f = 50 % (a30)": dict(m=A30["paso1"]["0.5"]["m"], ic90=[A30["bootstrap"]["m"][0], A30["bootstrap"]["m"][2]])}
for k, v in out["estimadores"].items():
    print(f"{k:46s} " + " ".join(f"{a}={b:.3f}" for a, b in v.items() if isinstance(b, float)) + (f" ic90={v['ic90'][0]:.3f}–{v['ic90'][1]:.3f}" if "ic90" in v else ""))


# ---- 2) prueba de extrapolación
def pred_err(sn_lo, tau_lo, sn_hi, tau_hi, m):
    """Nivel con los ensayos bajos (media de ln tan φ′1), predicción en los altos; devuelve errores en φ′s (°), pred − medido."""
    lt1 = np.mean(np.log(tau_lo) - np.log(S0 ** (1 - m) * sn_lo ** m))
    tp = np.exp(lt1) * S0 ** (1 - m) * sn_hi ** m
    return np.degrees(np.arctan(tp / sn_hi)) - np.degrees(np.arctan(tau_hi / sn_hi))


SWH = W.groupby("Set").sn.max(); SWH = list(SWH[SWH > SNX].index)
casos_w = []
for s in SWH:
    g = W[W.Set == s]; lo = g[g.sn <= 2.0]; hi = g[g.sn > SNX]
    if len(lo) >= 1 and len(hi) >= 1:
        casos_w.append((lo.sn.values, lo.tau.values, hi.sn.values, hi.tau.values))
# Antamina: triaxiales; σ′n y τ con la conversión de cada m (Ec. 16), nivel con los dos menores σ′3, predicción del mayor
def a_tau_sn(s3, s1, m):
    D, Sm = s1 - s3, s1 + s3
    sp = D / Sm if abs(m - 1) < 1e-6 else (np.sqrt(4 * m * (m - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (m - 1) * D)
    return Sm / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


casos_a = [g.sort_values("s3") for _, g in A[A.tx].groupby("set") if g.s3.nunique() >= 3]
res = []
for m in MS:
    ew = np.concatenate([pred_err(*c, m) for c in casos_w])
    ea = []
    for g in casos_a:
        sn, tau = a_tau_sn(g.s3.values, g.s1.values, m); k = g.s3.values < g.s3.values.max()
        ea.append(pred_err(sn[k], tau[k], sn[~k], tau[~k], m))
    ea = np.concatenate(ea)
    res.append(dict(m=float(m), mundo_sesgo=float(ew.mean()), mundo_mae=float(np.abs(ew).mean()), mundo_mediana=float(np.median(ew)),
                    antamina_sesgo=float(ea.mean()), antamina_mae=float(np.abs(ea).mean()), n_w=len(ew), n_a=len(ea)))
R = pd.DataFrame(res); out["extrapolacion"] = res
print(f"\nPrueba de extrapolación (predicción − medido, en φ′s): mundo {len(casos_w)} sets / {R.n_w[0]} ensayos sobre {SNX:.2f} MPa; "
      f"Antamina {len(casos_a)} sets / {R.n_a[0]} ensayos (σ′3 máximo de cada set)")
print(R[["m", "mundo_sesgo", "mundo_mediana", "mundo_mae", "antamina_sesgo", "antamina_mae"]].round(2).to_string(index=False))
m_w0 = float(np.interp(0, R.mundo_sesgo.values, R.m.values))   # el sesgo crece con m if R.mundo_sesgo.min() < 0 < R.mundo_sesgo.max() else None
m_a0 = float(np.interp(0, R.antamina_sesgo.values, R.m.values)) if R.antamina_sesgo.min() < 0 < R.antamina_sesgo.max() else None
out["m_sin_sesgo"] = dict(mundo=m_w0, antamina=m_a0)
print(f"m sin sesgo de extrapolación: mundo {m_w0}, Antamina {m_a0}")
# bootstrap por sets de la m sin sesgo del mundo
rng = np.random.default_rng(31); bw = []
for _ in range(1000):
    idx = rng.integers(0, len(casos_w), len(casos_w)); sesg = []
    for m in MS:
        sesg.append(np.concatenate([pred_err(*casos_w[i], m) for i in idx]).mean())
    sesg = np.array(sesg)
    if sesg.min() < 0 < sesg.max():
        bw.append(float(np.interp(0, sesg, MS)))
out["m_sin_sesgo_mundo_ic90"] = [float(np.percentile(bw, 5)), float(np.percentile(bw, 95))]
print(f"  mundo, IC 90 % por sets: {out['m_sin_sesgo_mundo_ic90'][0]:.3f}–{out['m_sin_sesgo_mundo_ic90'][1]:.3f}")

# ---- 3) efecto en la resistencia a grandes esfuerzos (nivel reajustado a los sets de Antamina con cada m; ω = 20°)
E_SET = np.array(A30["e0_set"]); SA = A30["sets_antamina"]


def nivel(m):
    """φ′1 por set con m fija (residuos de a12) y φ′e0 = media de φ′1 + 20·e (paso 2 con ω = 20°)."""
    ph = []
    for s in SA:
        g = A[A.set == s]; tx = g.tx.values
        def r(p):
            rr = np.empty(len(g))
            if tx.any():
                s3 = g.s3.values[tx]; rr[tx] = np.log(sigma1(tau_leps2, s3, p[0], m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
            if (~tx).any():
                rr[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], p[0], m)) - np.log(g.tau_ds.values[~tx]))
            return rr
        ph.append(least_squares(r, [40.0], bounds=([15], [70])).x[0])
    return float(np.mean(np.array(ph) + OM * E_SET))


LB = lambda s: np.degrees(np.arctan(np.tan(np.radians(33 - OM * (EB - 0.6))) * (s / S0) ** (-0.1)))
HC = lambda s: np.degrees(np.arctan(1.446 * (s * 1000) ** 0.898 / (s * 1000)))
cand = sorted({0.859, round(A30["paso1"]["0.5"]["m"], 3), round(RM["post_media_sin_truncar"], 3), 1.0} |
              ({round(m_w0, 3)} if m_w0 else set()) | set(round(v, 3) for v in out["m_sin_sesgo_mundo_ic90"]))
print("\nEfecto (e = 0.45; nivel reajustado a Antamina, ω = 20°):  φ′s a 1 / 4.6 / 7.86 / 10 / 15 MPa  | τ a 10 MPa | sobre I93 y H&C hasta 15 MPa")
out["efecto"] = []
for m in cand:
    pe0 = nivel(m); ph = lambda s: float(np.degrees(np.arctan(np.tan(np.radians(pe0 - OM * EB)) * (s / S0) ** (m - 1))))
    v = dict(m=m, pe0=pe0, phis={s: ph(s) for s in (1, 4.6, 7.86, 10, 15)}, tau10=10 * np.tan(np.radians(ph(10))),
             sobre_cotas=bool(all(ph(s) > max(LB(s), HC(s)) for s in np.geomspace(0.5, 15, 40))))
    out["efecto"].append(v)
    print(f"  m {m:.3f}: φ′e0 {pe0:.2f}° | " + " ".join(f"{x:5.1f}" for x in v["phis"].values()) + f" | τ10 {v['tau10']:.2f} MPa | {v['sobre_cotas']}")
json.dump(out, open(AQ / "a31_m_defendible.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("escrito a31_m_defendible.json")
