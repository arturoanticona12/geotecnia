"""Mapa del error de la aproximación explícita (Ec. 23 de Cylwik et al., 2025) en σ1, frente a la solución exacta."""
import sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
PA = 0.1013


def exacto(mm, f1, sn):
    K = np.tan(f1) * 10 ** (1 - mm); t = K * PA * (sn / PA) ** mm; tf = K * mm * (sn / PA) ** (mm - 1)
    b = np.arctan(tf) / 2 + np.pi / 4
    return sn - t / np.tan(b), sn + t * np.tan(b), K


def aprox(mm, K, s3):
    tp = (K * (1.714 * mm - 0.714) - 0.289 * np.log(mm) - 0.007) * (s3 / PA) ** (0.528 * mm ** 2 + 0.0021 * mm - 0.528)
    sp_ = np.sin(np.arctan(tp))
    return s3 + s3 * 2 * sp_ / ((1 - mm) * sp_ ** 2 - sp_ + mm)


sn = np.logspace(-2, 1.3, 400)
rangos = [(0, .06), (.06, .6), (.6, 2), (2, 5), (5, 10)]
print("error máx |σ1 aprox/exacto − 1| (%) por m, φ1 y rango de σ3 (MPa)")
print("  m    φ1  | <0.06  | 0.06–0.6 | 0.6–2 | 2–5   | 5–10")
for mm in (0.7, 0.8, 0.85, 0.9, 0.95):
    for f1d in (25, 35, 45, 50):
        s3, s1, K = exacto(mm, np.radians(f1d), sn)
        e = 100 * np.abs(aprox(mm, K, s3) / s1 - 1)
        r = [e[(s3 >= lo) & (s3 < hi)].max() if np.any((s3 >= lo) & (s3 < hi)) else np.nan for lo, hi in rangos]
        print(f"{mm:5.2f} {f1d:3d}° | " + " | ".join(f"{x:6.2f}" for x in r))
