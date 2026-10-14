"""Presión de poros en la capa basal saturada de un botadero sobre ladera (ronda 2).
Cada columna de la capa basal se carga a velocidad R (m/año de crecimiento del botadero sobre ella) hasta su espesor
final h(x); consolidación 1D de Terzaghi con carga en rampa (Olson 1977), tope drenado hacia el desmonte y base impermeable
(roca). u total = hidrostática de la capa (nivel en su tope) + exceso. Devuelve puntos [x, y, u] para Slide2 y σ′v."""
import numpy as np

GW, GAM, YR = 9.81, 21.0, 365.25 * 86400


def perfil_exceso(k, M, Hs, R, h, nz=30):
    """Exceso de presión (kPa) en nz+1 profundidades (0 = tope drenado, Hs = base) al final de cargar h metros a R m/año."""
    if h <= 0:
        return np.zeros(nz + 1)
    cv = k * M * 1e3 / GW * YR; qd = GAM * R; T = h / R; dz = Hs / nz
    n = max(200, int(np.ceil(T / (Hs ** 2 / cv / 50)))); n = min(n, 20000); dt = T / n; lam = cv * dt / dz ** 2
    A = np.zeros((nz + 1, nz + 1))
    for i in range(1, nz):
        A[i, i - 1] = -lam; A[i, i] = 1 + 2 * lam; A[i, i + 1] = -lam
    A[0, 0] = 1; A[nz, nz] = 1 + 2 * lam; A[nz, nz - 1] = -2 * lam
    Ainv = np.linalg.inv(A); u = np.zeros(nz + 1)
    for _ in range(n):
        rhs = u + qd * dt; rhs[0] = 0; u = Ainv @ rhs
    return u


def malla(geo, k, R, M=50.0, Hs=30.0, dx=100.0, nzp=4, ceros=False):
    """geo: dict(top(x), fnd(x), x0, x1). Puntos [x, y, u_total] en la capa basal; con ceros=True agrega u = 0 a 5 m sobre
    y bajo la capa. Sin ceros (defecto) la malla se asigna solo a la capa y el desmonte y la roca se declaran secos: los
    saltos 0 → MPa en 5 m hacen oscilar la interpolación de Slide2 (lote 62: FS = 0 por presiones extrapoladas)."""
    P, S = [], []
    for x in np.arange(geo["x0"], geo["x1"] + 1e-6, dx):
        yf = geo["fnd"](x); ytop_capa = yf + Hs; h = max(geo["top"](x) - ytop_capa, 0.0)
        ue = perfil_exceso(k, M, Hs, R, h)
        for f in np.linspace(0, 1, nzp + 1):                         # f = 0 tope de la capa, 1 = base
            z = f * Hs; y = ytop_capa - z; ex = float(np.interp(z, np.linspace(0, Hs, len(ue)), ue)); uh = GW * z
            sv = GAM * (h + z); P.append([round(x, 1), round(y, 2), round(uh + ex, 1)]); S.append([round(x, 1), round(y, 2), round(sv - uh - ex, 1)])
        if ceros:
            P.append([round(x, 1), round(ytop_capa + 5, 2), 0.0]); P.append([round(x, 1), round(yf - 5, 2), 0.0])
    P = [[float(a) for a in p] for p in P]; S = [[float(a) for a in s] for s in S]
    return P, S                                                           # S: σ′v (kPa) en los mismos puntos de la capa


if __name__ == "__main__":
    import math, sys
    sys.stdout.reconfigure(encoding="utf-8")
    H, BETA, THETA, HB = 700.0, 26.57, 10.0, 30.0; tb, tt = math.tan(math.radians(BETA)), math.tan(math.radians(THETA))
    geo = dict(top=lambda x: min(max(x * tb, 0.0), H), fnd=lambda x: x * tt, x0=150.0, x1=(H - HB) / tt - 50)
    for R in (25, 100, 300, 600):
        for k in (1e-6, 1e-7, 1e-8, 1e-9):
            P, S = malla(geo, k, R)
            u = np.array([p[2] for p in P]); sv = np.array([s[2] for s in S])
            # ru medio en la capa (exceso + hidrostática) respecto de σv total
            print(f"R = {R:3d} m/año  k = {k:.0e}  u máx = {u.max() / 1000:5.2f} MPa   σ′v mín en la capa = {sv.min() / 1000:5.2f} MPa")
