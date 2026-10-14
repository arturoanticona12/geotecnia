"""Envolvente acotada: perfil de verosimilitud (ML) en una grilla fina de (φ′cs, ζ) con todos los datos, y variante con
φ′cs por clase de calidad (desplazamiento común Δ entre clases no se estima: se prueba φ′cs = φ0 + δ_c con δ de la
grilla). Pesos ∝ exp(ML) (previa plana en la grilla) para propagar la incertidumbre de (φ′cs, ζ).
Escribe lepsp_acotada_grilla.json."""
import sys, json, time
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada import d, ModeloNL, beta_inicial, disenio_m2  # noqa: E402
from lepsp_modelo import Modelo  # noqa: E402

t0 = time.time()
m2 = Modelo(d, disenio_m2(d), ["g", "m", "l", "e", "x", "x2"]).ajustar(); psi = m2.psi
PH = np.r_[0.0, np.arange(10.0, 34.01, 2.0)]; ZE = np.round(np.arange(0.10, 0.551, 0.05), 3)
ML = np.full((len(PH), len(ZE)), -np.inf); B = {}
for i, ph in enumerate(PH):
    for j, z in enumerate(ZE):
        m = ModeloNL(d, np.tan(np.radians(ph)), z, beta_inicial(d))
        try:
            ML[i, j], _ = m.gn(psi); B[(i, j)] = m.beta_nl.tolist()
        except Exception:
            pass
i0, j0 = np.unravel_index(np.argmax(ML), ML.shape)
w = np.exp(ML - ML.max()); w /= w.sum()
pm = float((w.sum(1) * PH).sum()); ps = float(np.sqrt((w.sum(1) * (PH - pm) ** 2).sum()))
zm = float((w.sum(0) * ZE).sum()); zs = float(np.sqrt((w.sum(0) * (ZE - zm) ** 2).sum()))
print(f"máximo: φcs = {PH[i0]}°, ζ = {ZE[j0]}  (ML {ML[i0, j0]:.2f}; {time.time()-t0:.0f} s)")
print(f"pesos: φcs = {pm:.2f} ± {ps:.2f}°, ζ = {zm:.3f} ± {zs:.3f};  corr = {float(((PH[:, None]-pm)*(ZE[None, :]-zm)*w).sum()/(ps*zs)):+.2f}")
print("ΔML ≤ 2 (≈ IC 95 % del perfil 2D ~ ΔML ≤ 3.0):")
for i, ph in enumerate(PH):
    print(f"  φcs {ph:4.0f}: " + " ".join(f"{ML[i, j] - ML[i0, j0]:6.1f}" for j in range(len(ZE))))
print("  ζ:        " + " ".join(f"{z:6.2f}" for z in ZE))
json.dump(dict(phi=PH.tolist(), zeta=ZE.tolist(), ml=ML.tolist(), opt=[float(PH[i0]), float(ZE[j0])], beta_opt=B[(i0, j0)],
               psi=psi.tolist(), phi_media=pm, phi_sd=ps, zeta_media=zm, zeta_sd=zs),
          open(AQ / "lepsp_acotada_grilla.json", "w", encoding="utf-8"), indent=1)
