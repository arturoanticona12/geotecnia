"""Presión de poros por consolidación en capa basal saturada bajo carga creciente (Terzaghi 1D, carga en rampa).
Capa de espesor Hs drenada arriba, base impermeable; carga total crece a q' = γ·R (R = velocidad de crecimiento, m/año)."""
import sys, json, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
GW = 9.81  # kN/m3
GAM = 21.0
YR = 365.25 * 86400


def u_base(k, M, Hs, R, Hfin=700.0, nz=60):
    cv = k * M * 1e3 / GW * YR   # m2/año  (M en MPa -> kPa)
    qd = GAM * R                  # kPa/año
    T = Hfin / R
    dz = Hs / nz
    dt = T / 3000  # implícito: incondicionalmente estable
    n = int(np.ceil(T / dt)); dt = T / n
    u = np.zeros(nz + 1)          # z=0 tope drenado, z=Hs base impermeable
    lam = cv * dt / dz ** 2
    # implícito (Crank-Nicolson simple -> uso implícito puro por estabilidad)
    A = np.zeros((nz + 1, nz + 1))
    for i in range(1, nz):
        A[i, i - 1] = -lam; A[i, i] = 1 + 2 * lam; A[i, i + 1] = -lam
    A[0, 0] = 1
    A[nz, nz] = 1 + 2 * lam; A[nz, nz - 1] = -2 * lam
    Ainv = np.linalg.inv(A)
    for _ in range(n):
        rhs = u + qd * dt; rhs[0] = 0
        u = Ainv @ rhs
    return u[-1], qd * T, cv


if __name__ == "__main__":
    Hs = 30.0
    rows = []
    # verificación vs solución estacionaria u = q'·Hs²/(2cv) para cv bajo-moderado
    ub, s, cv = u_base(1e-8, 100, Hs, 50)
    print(f"check: k=1e-8 M=100 R=50 -> u_base={ub:.0f} kPa ; estacionaria={GAM*50*Hs**2/(2*cv):.0f} kPa (cv={cv:.0f} m2/año)")
    for M in [50, 150]:
        for R in [25, 50, 100]:
            for k in [1e-5, 1e-6, 1e-7, 1e-8, 1e-9]:
                ub, sv, cv = u_base(k, M, Hs, R)
                rows.append(dict(M=M, R=R, k=k, u=ub, ru=ub / sv, cv=cv))
                print(f"M={M:3d} MPa  R={R:3d} m/año  k={k:.0e} m/s  cv={cv:9.0f} m²/año  u_base={ub:8.0f} kPa  Δu/σv(fin)={ub/sv:.3f}")
    json.dump(rows, open(sys.argv[1], "w"), indent=1)

