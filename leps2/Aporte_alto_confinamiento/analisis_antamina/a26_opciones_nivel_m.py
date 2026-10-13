"""Comentarios del 2026-10-12: (1) la composición de diseño del DDE (IFF-115-G-0001_B, p. 42: intrusivo y exoskarn 44 %,
hornfels y mármol 56 %; sin zonificación por litología ni margas) reemplaza la composición LE2 del modelo de bloques;
(2) a grandes esfuerzos la curva queda bajo las cotas de Hawley y Cunning (2017) e Indraratna et al. (1993).
Matriz de opciones: ponderación de los ensayos × m. φ′e0 ajustado como en a12 (mismo residuo y ω), y para cada curva:
φ′1 a e = 0.45, φ′s a varios σ′n, cruces con las cotas y Δφ′s de los ensayos altos (Antamina y base mundial, a su propia e).
Escribe a26_opciones_nivel_m.json."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares, brentq
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from modelos import sigma1, tau_leps2  # noqa: E402
from lepsp_r6 import datos  # noqa: E402
OM, EB, S0 = 20.0, 0.45, 1.013
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
d = d[d.litologia.isin(["Mármol", "Hornfels", "Intrusivo"])].copy()
d["set"] = d.fuente_id + "|" + d.set_id.astype(str); d["e"] = d.e0_adoptado; d["tx"] = d.tipo == "TX"
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]


def resid(g, pe0, m):                                    # el de a12 (triaxial en ln q; corte directo en ln τ con C_DS)
    e = g.e.values; tx = g.tx.values; r = np.empty(len(g))
    if tx.any():
        s3 = g.s3.values[tx]; r[tx] = np.log(sigma1(tau_leps2, s3, pe0 - OM * e[tx], m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
    if (~tx).any():
        r[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], pe0 - OM * e[~tx], m)) - np.log(g.tau_ds.values[~tx]))
    return r


def ajuste(g, m, pesos=None):
    w = 1.0 if pesos is None else np.sqrt((g.litologia.map(pesos) / g.litologia.map(g.litologia.value_counts())).values * len(g) / sum(pesos.values()))
    return float(least_squares(lambda p: w * resid(g, p[0], m), [49], bounds=([30], [70])).x[0])


A12 = json.load(open(AQ / "a12_leps2_ponderada.json", encoding="utf-8"))["curvas"]
PONDERACIONES = {
    "LE2 del modelo de bloques (actual; margas y caliza con la resistencia del mármol)": "actual",
    "DDE: intrusivo 44 %, hornfels 28 %, mármol 28 %": {"Intrusivo": 0.44, "Hornfels": 0.28, "Mármol": 0.28},
    "Cada ensayo igual": None}
MS = {"0.859 (mediana mundial, actual)": 0.8587, "0.923 (P90 mundial)": 0.9228, "0.957 (posterior jerárquica)": 0.9568, "1.00 (lineal)": 1.0}
cota_i93 = lambda s: s * np.tan(np.radians(33.0 - OM * (EB - 0.6))) * (s / S0) ** (0.9 - 1)
cota_hc = lambda s: 1.446 * (s * 1000) ** 0.898 / 1000
W = datos(); W = W[~W.cens] if "cens" in W else W
A = pd.read_csv(AQ / "a10_puntos.csv"); A["tau"] = A.sn * np.tan(np.radians(A.phis))
out = {}
for pn, pw in PONDERACIONES.items():
    print(f"\n=== {pn}")
    print("  m      | φ′e0   φ′1(e=.45) | φ′s 1   4.6   10    15 MPa | cruza I93  H&C  | Antamina >3 MPa: bajo/n, Δφ′ med | mundial >4.6: bajo/n, Δφ′ med")
    for mn, m in MS.items():
        if pw == "actual":
            k = {0.8587: "Curva propuesta (mediana mundial)", 0.9228: "Mundial P90"}.get(m)
            if k is None:
                print(f"  {mn:30s} (no calculado en a12: requiere la mezcla con margas)"); continue
            pe0 = A12[k]["pe0"]
        else:
            pe0 = ajuste(d, m, pw)
        tc = lambda s, e=EB: np.tan(np.radians(pe0 - OM * e)) * S0 ** (1 - m) * np.asarray(s, float) ** m
        ps = lambda s: float(np.degrees(np.arctan(tc(s) / s)))
        cr = {}
        for nom, f in (("i93", cota_i93), ("hc", cota_hc)):
            try:
                cr[nom] = brentq(lambda s: tc(s) - f(s), 0.05, 100)
            except ValueError:
                cr[nom] = None
        def contraste(D, lo):
            k = D.sn.to_numpy() > lo
            dphi = np.degrees(np.arctan(D.tau.to_numpy()[k] / D.sn.to_numpy()[k])) - np.degrees(np.arctan(tc(D.sn.to_numpy()[k], D.e.to_numpy()[k]) / D.sn.to_numpy()[k]))
            return int((dphi < 0).sum()), int(k.sum()), float(np.median(dphi))
        ca, cw = contraste(A, 3.0), contraste(W, 4.6)
        r = dict(m=m, pe0=pe0, phi1=pe0 - OM * EB, phis={s: ps(s) for s in (1, 4.6, 10, 15)}, cruce_i93=cr["i93"], cruce_hc=cr["hc"],
                 antamina_sobre3=ca, mundial_sobre46=cw)
        out[f"{pn} | m {mn}"] = r
        f_ = lambda x: f"{x:5.1f}" if x else "  no "
        print(f"  {mn:30s} | {pe0:5.2f}  {pe0 - OM * EB:5.2f}     | {ps(1):5.1f} {ps(4.6):5.1f} {ps(10):5.1f} {ps(15):5.1f} | {f_(cr['i93'])} {f_(cr['hc'])} | "
              f"{ca[0]}/{ca[1]}, {ca[2]:+.1f}° | {cw[0]}/{cw[1]}, {cw[2]:+.1f}°")
json.dump(out, open(AQ / "a26_opciones_nivel_m.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("\nReferencias: cota Indraratna a 10 MPa 30.0°, H&C 29.5°; sensibilidad DDE 33° (5–10 MPa) y 30° (>10 MPa).")
