"""Envolventes del promedio del botadero (colocado: e = 0.65, E con 0.80; Dmax 1 m; escala con media cero) para los
mecanismos de alto confinamiento en Slide2 (ronda 6, revisor R3):
  B P50, B P05 — forma acotada (lepsp_sitio6_muestras_e065_general.npz);
  Q P50, Q P05 — forma cuadrática (…_e065_general_x2.npz);
  L2 P50      — Leps 2.0 publicado (Cylwik et al. 2025: φ′e=0 − 20e, m = 0.9) por tipo de roca, ponderado por masa, sin
                escala (la práctica habitual);
  Flo P05, Fhi P05 — forma acotada restringida a las muestras con φ′∞ en los extremos del intervalo de 3 unidades del perfil.
Escribe lepsp6_envolventes_alto.npz (sn en MPa; τ en MPa) y un resumen en consola."""
import json, sys
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; AN = AQ.parent / "analisis"
S0 = 10 * 0.1013
B = np.load(AQ / "lepsp_sitio6_muestras_e065_general.npz"); Q = np.load(AQ / "lepsp_sitio6_muestras_e065_general_x2.npz")
sn = B["sn"]; tb = np.tensordot(B["pesos"], B["tau"].astype(float), 1); tq = np.tensordot(Q["pesos"], Q["tau"].astype(float), 1)
PR = json.load(open(AN / "lepsp_perfil6.json", encoding="utf-8")); mx = PR["ml_max"]
ban = [r["phi"] for r in PR["perfil"] if r["ml"] >= mx - 3.0]; flo, fhi = min(ban), max(ban)
phk = B["phi_k"]; ENV = {"B P50": np.percentile(tb, 50, 0), "B P05": np.percentile(tb, 5, 0), "Q P50": np.percentile(tq, 50, 0), "Q P05": np.percentile(tq, 5, 0)}
for nm, f in (("Flo P05", flo), ("Fhi P05", fhi)):
    sel = np.isclose(phk, f)
    if sel.sum() < 200:                                  # pocas muestras exactamente en el extremo: las más cercanas del lado
        orden = np.argsort(np.abs(phk - f)); sel = np.zeros(len(phk), bool); sel[orden[:600]] = True
    ENV[nm] = np.percentile(tb[sel], 5, 0); print(f"{nm}: φ′∞ ≈ {f:.0f}° ({int(sel.sum())} muestras)")
# Leps 2.0 publicado, colocado (sin escala): A, C, D, E calidad baja (47°), B moderada (50°); e = 0.65 (E: 0.80)
PESO = {"A": 0.35, "B": 0.25, "C": 0.20, "D": 0.10, "E": 0.10}; PHI0 = {"A": 47, "B": 50, "C": 47, "D": 47, "E": 47}
t2 = sum(w * np.tan(np.radians(PHI0[k] - 20 * (0.80 if k == "E" else 0.65))) * S0 ** 0.1 * sn ** 0.9 for k, w in PESO.items())
ENV["L2 P50"] = t2
np.savez(AQ / "lepsp6_envolventes_alto.npz", sn=sn, **ENV)
for s_ in (1, 3, 8):
    j = int(np.argmin(np.abs(sn - s_)))
    print(f"σ′n {sn[j]:.2f} MPa: " + "  ".join(f"{k} {np.degrees(np.arctan(v[j] / sn[j])):.1f}°" for k, v in ENV.items()))
print("escrito lepsp6_envolventes_alto.npz; φ′∞ extremos", flo, fhi)
