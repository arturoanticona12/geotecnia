"""Ajuste Hoek-Brown con s = 0 a las curvas Leps 2.0 de la Tabla de Power Curve, para el apartado de FLAC2D (2026-10-10).
σ1 − σ3 = σci·(mb·σ3/σci)^a = K·σ3^a, ajustado en ln(σ1 − σ3) con σ′3 de 0.02 a 6 MPa; error en φ′ del círculo de falla."""
import sys, json
from pathlib import Path
import numpy as np
sys.path.insert(0, sys.argv[1])
from modelos import sigma1, tau_leps2  # noqa: E402
AA = Path(sys.argv[2]); A12 = json.load(open(AA / "a12_leps2_ponderada.json", encoding="utf-8"))
C = A12["curvas"]["Curva propuesta (mediana mundial)"]; M = C["m"]; MAR = A12["marmol"]["central"]["pe0"]; PMG = MAR - A12["dclase"]
SCI = 100.0
s3 = np.geomspace(0.02, 6.0, 80); out = []
for nm, pe0, e in (("Curva propuesta", C["pe0"], 0.45), ("Curva propuesta", C["pe0"], 0.55), ("Curva propuesta", C["pe0"], 0.65),
                   ("Zona de mármol", MAR, 0.65), ("Zona de margas o caliza (provisional)", PMG, 0.65)):
    s1 = sigma1(tau_leps2, s3, pe0 - 20 * e, M); s1 = s1[0] if isinstance(s1, tuple) else s1
    q = s1 - s3; a, lnK = np.polyfit(np.log(s3), np.log(q), 1); K = np.exp(lnK); qh = K * s3 ** a
    dphi = np.degrees(np.arcsin(qh / (qh + 2 * s3))) - np.degrees(np.arcsin(q / (q + 2 * s3)))
    mb = (K / SCI ** (1 - a)) ** (1 / a)
    out.append(dict(nombre=nm, pe0=pe0, e=e, a=float(a), K=float(K), mb=float(mb), sci=SCI, err_q=[float((qh / q - 1).min() * 100), float((qh / q - 1).max() * 100)],
                    dphi=[float(dphi.min()), float(dphi.max())]))
    print(f"{nm:38s} e={e:.2f} a={a:.4f} K={K:.4f} mb={mb:.4f} (σci {SCI:.0f} MPa) err q {out[-1]['err_q'][0]:+.1f}..{out[-1]['err_q'][1]:+.1f} % dφ {dphi.min():+.2f}..{dphi.max():+.2f}°")
json.dump(dict(rango_s3=[0.02, 6.0], m=M, filas=out), open(AA / "a20_hoek_brown_flac.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
