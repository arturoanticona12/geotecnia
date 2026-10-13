"""Diagnóstico: por qué el punto φ′∞ = 0 del perfil r6 no termina. Ajusta el modelo en T = 0 con varios ζ0 y mide el
tiempo de cada etapa (EM de censura, REML de ψ, Gauss–Newton)."""
import sys, time
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, ".")
from lepsp_r6 import datos, ModeloR6, BETA0, PSI0

d = datos(); t0 = time.time()
for z in (0.15, 0.20):
    m = ModeloR6(d, 0.0, z, BETA0)
    t1 = time.time(); ll, _ = m.gn(PSI0); print(f"ζ0 {z}: gn inicial {time.time()-t1:.1f} s, ll {ll:.2f}", flush=True)
    t1 = time.time(); ch = m.imputar_censura(PSI0); print(f"  imputación {time.time()-t1:.1f} s, cambio máx {ch:.4f}", flush=True)
    t1 = time.time(); m.ajustar(PSI0); print(f"  REML ψ {time.time()-t1:.1f} s, ψ {np.round(m.psi, 3)}", flush=True)
    t1 = time.time(); m.ajustar_nl(m.psi, it_cens=6); print(f"  ajustar_nl {time.time()-t1:.1f} s, ll_obs {m.ll_obs():.2f}, β {np.round(m.beta_nl, 3)}", flush=True)
print(f"total {time.time()-t0:.0f} s")
