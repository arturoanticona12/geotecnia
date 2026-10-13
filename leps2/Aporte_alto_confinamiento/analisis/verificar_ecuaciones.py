"""Verificación simbólica y numérica de las ecuaciones de Cylwik et al. (2025)."""
import sys
import numpy as np
import sympy as sp
sys.stdout.reconfigure(encoding="utf-8")

s, pa, K, m, ph, s1, s3, p1 = sp.symbols("sigma_n p_a K m phi sigma1 sigma3 phi1", positive=True)
tau = K * pa * (s / pa) ** m                                       # Ec. 1
tanphi = sp.diff(tau, s)                                           # Ec. 2
print("Ec. 2:", sp.simplify(tanphi - K * m * (s / pa) ** (m - 1)) == 0)
print("Ec. 3 (τ = σn tanφ/m):", sp.simplify(tau - s * tanphi / m) == 0)
print("Ec. 6 (K):", sp.simplify((tau.subs(s, 10 * pa) / (10 * pa)).subs(K, sp.tan(p1) * 10 ** (1 - m)) - sp.tan(p1)) == 0)

# Ecs. 13–16: circulo tangente
D, S = s1 - s3, s1 + s3
sn13 = S / 2 - D / 2 * sp.sin(ph); t14 = D / 2 * sp.cos(ph)
eq15 = sp.expand((t14 - sn13 * sp.tan(ph) / m) * m * sp.cos(ph))   # τ = σn tanφ / m
paper15 = D / 2 * (1 - m) * sp.sin(ph) ** 2 - S / 2 * sp.sin(ph) + m * D / 2
print("Ec. 15:", sp.simplify(sp.expand(eq15.rewrite(sp.sin)) - sp.expand(paper15)).equals(0) or
      sp.simplify(sp.trigsimp(eq15 - paper15)) == 0)

# numérico para Ecs. 10–12, 16, 17, 18, 21, 23
rng = np.random.default_rng(0); PA = 0.1013; mx = []
for _ in range(2000):
    mm = rng.uniform(0.6, 0.99); f1 = np.radians(rng.uniform(30, 50)); sn = 10 ** rng.uniform(-2, 1.2)
    KK = np.tan(f1) * 10 ** (1 - mm); t = KK * PA * (sn / PA) ** mm; tf = KK * mm * (sn / PA) ** (mm - 1)
    phi = np.arctan(tf); beta = phi / 2 + np.pi / 4
    S1 = sn + t * np.tan(beta); S3 = sn - t / np.tan(beta)          # Ecs. 10–11
    d, ss = S1 - S3, S1 + S3
    sphi16 = (np.sqrt(4 * mm * (mm - 1) * d ** 2 + ss ** 2) - ss) / (2 * (mm - 1) * d)       # Ec. 16
    tphi1_17 = (20 * PA) ** (mm - 1) * d * np.sqrt(1 - sphi16 ** 2) * (ss - d * sphi16) ** (-mm)  # Ec. 17
    s1_18 = S3 + S3 * 2 * sphi16 / ((1 - mm) * sphi16 ** 2 - sphi16 + mm)                      # Ec. 18
    s3_21 = PA * (KK * mm / np.tan(phi)) ** (1 / (1 - mm)) * (mm * (np.sin(phi) + 1) - np.sin(phi)) / (mm * (np.sin(phi) + 1))  # Ec. 21
    tphi23 = (KK * (1.714 * mm - 0.714) - 0.289 * np.log(mm) - 0.007) * (S3 / PA) ** (0.528 * mm ** 2 + 0.0021 * mm - 0.528)
    s1_23 = S3 + S3 * 2 * np.sin(np.arctan(tphi23)) / ((1 - mm) * np.sin(np.arctan(tphi23)) ** 2 - np.sin(np.arctan(tphi23)) + mm)
    mx.append([abs(sphi16 - np.sin(phi)), abs(np.arctan(tphi1_17) - f1), abs(s1_18 / S1 - 1), abs(s3_21 / S3 - 1),
               abs(s1_23 / S1 - 1) if (0.7 < mm < 1 and 25 < np.degrees(f1) < 50) else 0])
mx = np.array(mx).max(axis=0)
print(f"Ec. 16 |Δ sinφ| máx = {mx[0]:.1e}; Ec. 17 |Δφ1| máx = {np.degrees(mx[1]):.1e}°; Ec. 18 error σ1 = {mx[2]:.1e}; "
      f"Ec. 21 error σ3 = {mx[3]:.1e}; Ec. 23 error σ1 máx = {100 * mx[4]:.2f} % (rango 0.7<m<1, 25°<φ1<50°)")
