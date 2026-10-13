"""Reevalúa la log-verosimilitud observada de cada punto del perfil r6 con el término de truncamiento corregido
(varianza entre sets), en sus parámetros guardados (sin reajustar), y la compara con la del perfil original."""
import json, glob, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8"); sys.path.insert(0, ".")
from lepsp_r6 import datos, ModeloR6

d = datos(); P = json.load(open("lepsp_perfil6.json", encoding="utf-8")); mx = P["ml_max"]; filas = []
for r in P["perfil"]:
    if not r["psi"]:
        continue
    m = ModeloR6(d, np.tan(np.radians(r["phi"])), r["zeta"], np.array(r["beta"])); psi = np.array(r["psi"]); b = np.array(r["beta"])
    ll = m.ll_obs(psi, b); filas.append((r["phi"], r["ml"], ll))
mx2 = max(f[2] for f in filas)
for ph, a, b_ in filas:
    print(f"  φ′∞ {ph:4.0f}°  ΔML original {a - mx:+7.2f}  corregido {b_ - mx2:+7.2f}  (desplazamiento {b_ - a:+.2f})")
json.dump([dict(phi=p, ml_original=a, ml_corregido=b_) for p, a, b_ in filas], open("lepsp_perfil6_retrunc.json", "w", encoding="utf-8"), indent=1)
