"""Comentario del 2026-10-12 (p. 18 del memo): a grandes esfuerzos la curva propuesta queda bajo las cotas inferiores de Hawley y
Cunning (2017) y de Indraratna et al. (1993). Este script cuantifica: (1) dónde cruza cada cota y la sensibilidad del DDE
(33° de 5 a 10 MPa, 30° sobre 10 MPa; IFF-115-G-0001_B, nota 4); (2) cómo quedan los ensayos altos de la base mundial y de
Antamina frente a la curva, cada uno evaluado a su propia e (sin trasladar los puntos). Escribe a25_alta_tension.json."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import brentq
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from lepsp_r6 import datos  # noqa: E402
C = json.load(open(AQ / "a12_leps2_ponderada.json", encoding="utf-8"))["curvas"]["Curva propuesta (mediana mundial)"]
PE0, M, S0, OM, EB = C["pe0"], C["m"], 1.013, 20.0, 0.45
tau_c = lambda s, e=EB: np.tan(np.radians(PE0 - OM * e)) * S0 ** (1 - M) * np.asarray(s, float) ** M
phi_s = lambda tau, s: np.degrees(np.arctan(np.asarray(tau) / np.asarray(s)))
cotas = {"Indraratna et al. (1993), forma de Cylwik et al. (2025)":
         lambda s: s * np.tan(np.radians(33.0 - OM * (EB - 0.6))) * (np.asarray(s, float) / S0) ** (0.9 - 1),
         "Hawley y Cunning (2017), cota inferior": lambda s: 1.446 * (np.asarray(s, float) * 1000) ** 0.898 / 1000}
out = {"curva": dict(pe0=PE0, m=M, e=EB), "cruces": {}, "tabla": {}}
print(f"Curva propuesta: φ′e0 {PE0:.2f}°, m {M:.4f}, e {EB}")
for nom, f in cotas.items():
    g = lambda s: tau_c(s) - f(s)
    try:
        sx = brentq(g, 0.05, 50)
    except ValueError:
        sx = None
    out["cruces"][nom] = sx
    print(f"  cruza {nom}: σ′n = {sx:.2f} MPa" if sx else f"  no cruza {nom} en 0.05–50 MPa")
print("\nσ′n (MPa) | curva φ′s | Indraratna | H&C | DDE sens.")
for s in (1, 2, 4.6, 5, 7.86, 10, 12, 15):
    fila = dict(curva=float(phi_s(tau_c(s), s)), i93=float(phi_s(cotas[list(cotas)[0]](s), s)), hc=float(phi_s(cotas[list(cotas)[1]](s), s)),
                dde=(33.0 if 5 <= s <= 10 else 30.0 if s > 10 else None))
    out["tabla"][s] = fila
    print(f"  {s:5.2f} | {fila['curva']:5.1f} | {fila['i93']:5.1f} | {fila['hc']:5.1f} | {fila['dde'] or '-'}")
# ensayos altos: base mundial (741) y Antamina (ajuste), cada uno frente a la curva a su propia e
W = datos(); W = W[~W.cens] if "cens" in W else W
A = pd.read_csv(AQ / "a10_puntos.csv"); A["tau"] = A.sn * np.tan(np.radians(A.phis))     # φ′s medido, a la e del ensayo
print("\nEnsayos frente a la curva (a su propia e): Δφ′s = φ′s ensayo − φ′s curva")
res = {}
for nom, d, ccol in (("Base mundial (Cylwik et al. 2025)", W, None), ("Antamina (ajuste)", A, None)):
    sn = d["sn"].to_numpy(float); tau = d["tau"].to_numpy(float) if "tau" in d else None
    e = d["e"].to_numpy(float)
    if tau is None:
        continue
    dphi = phi_s(tau, sn) - phi_s(tau_c(sn, e), sn)
    for lo, hi in ((2, 4.6), (4.6, 7.9), (3, 7.9)):
        k = (sn > lo) & (sn <= hi)
        if k.sum() == 0:
            continue
        r = dict(n=int(k.sum()), bajo_curva=int((dphi[k] < 0).sum()), dphi_mediana=float(np.median(dphi[k])),
                 dphi_p10=float(np.percentile(dphi[k], 10)), dphi_min=float(dphi[k].min()))
        res[f"{nom} | {lo}–{hi} MPa"] = r
        print(f"  {nom:36s} σ′n {lo}–{hi} MPa: n {r['n']:3d} | bajo la curva {r['bajo_curva']:3d} | Δφ′ mediana {r['dphi_mediana']:+.1f}° "
              f"P10 {r['dphi_p10']:+.1f}° mín {r['dphi_min']:+.1f}°")
out["ensayos"] = res
json.dump(out, open(AQ / "a25_alta_tension.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
