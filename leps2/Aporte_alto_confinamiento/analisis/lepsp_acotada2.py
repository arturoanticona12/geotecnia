"""Leps-P, ronda 4: envolvente acotada con efectos aleatorios sobre los parámetros mecánicos de cada material.

    y = x + ln[T + (e^η − T)·e^(−ζx)] + ε,   η = β_c + β_e e + u_η,   ζ = ζ0 + u_ζ
    u = (u_η, u_ζ) = u_publicación + u_set,   u_p ~ N(0, G_p),  u_s ~ N(0, G_s),   ln σε(x) = a0 + a1 x

Cada material tiene su propia envolvente que decae hacia la asíntota común T = tan φ′∞ (pendiente local ≤ 1 si ζ > 0).
Estimación: linealización de primer orden de los efectos aleatorios en u = 0 (Lindstrom y Bates 1990):
y ≈ f(β, ζ0) + Z u, Z = [∂f/∂η, ∂f/∂ζ]; los efectos fijos por Gauss–Newton y la varianza por REML (lepsp_modelo).
(φ′∞, ζ0) se perfilan en una grilla. Uso: python lepsp_acotada2.py [completo]"""
import sys, json, time, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo  # noqa: E402

d = preparar(load_db(), CLASE)
CL = ["good", "moderate", "low"]


def media2(beta, dd, T, z0):
    """f, J (∂f/∂β: good, moderate, low, e) y Z (∂f/∂η, ∂f/∂ζ) en u = 0."""
    dum = np.c_[[(dd.clase == c).values.astype(float) for c in CL]].T
    e, x = dd.e.values, dd.x.values
    eta = dum @ beta[:3] + beta[3] * e; E = np.exp(eta); q = np.exp(-z0 * x)
    g = np.maximum(T + (E - T) * q, 1e-9); f = x + np.log(g)
    w = E * q / g; dz = -x * (E - T) * q / g
    return f, np.c_[dum * w[:, None], w * e], np.c_[w, dz]


class ModeloNL2(Modelo):
    def __init__(self, dd, T, z0, beta0):
        self.dd, self.T, self.z0, self.beta_nl = dd, T, z0, np.asarray(beta0, float)
        f, J, Z = media2(self.beta_nl, dd, T, z0)
        d2 = dd.copy(); d2["y"] = dd.y.values - f + J @ self.beta_nl
        super().__init__(d2, J, CL + ["e"]); self.Zall = Z

    def _V(self, ip, Zs, Gp, Gs, a):
        x = self.x[ip]; Z = self.Zall[ip]
        V = Z @ Gp @ Z.T
        for ind in Zs:
            Zi = Z * ind[:, None]; V += Zi @ Gs @ Zi.T
        V[np.diag_indices_from(V)] += np.exp(a[0] + a[1] * x) ** 2
        return V

    def relinealizar(self):
        f, J, Z = media2(self.beta_nl, self.dd, self.T, self.z0)
        self.X = J; self.y = self.dd.y.values - f + J @ self.beta_nl; self.Zall = Z

    def gn(self, psi, it=25, tol=1e-7):
        for _ in range(it):
            self.relinealizar(); ll, b, C = self.reml(psi, devolver=True)
            paso = b - self.beta_nl; self.beta_nl = self.beta_nl + paso
            if np.max(np.abs(paso)) < tol:
                break
        self.relinealizar(); ll, b, C = self.reml(psi, devolver=True)
        return ll - 0.5 * np.linalg.slogdet(C)[1], C

    def ajustar_nl(self, psi0):
        self.gn(psi0)
        for _ in range(3):
            self.ajustar(psi0); psi0 = self.psi; self.gn(psi0)
        self.relinealizar(); self.ll, _, self.cov_beta = self.reml(self.psi, devolver=True); self.beta = self.beta_nl
        return self

    def predecir(self, dte):
        f, J, Z = media2(self.beta_nl, dte, self.T, self.z0); x = dte.x.values
        v = np.einsum("ij,jk,ik->i", Z, self.Gp + self.Gs, Z) + np.einsum("ij,jk,ik->i", J, self.cov_beta, J) + self.sigma_eps(x) ** 2
        return f, np.sqrt(v), J, Z


BETA0 = np.array([0.19, 0.093, 0.023, -0.52])
PSI0 = np.array([np.log(0.06), np.log(0.05), 0.0, np.log(0.08), np.log(0.05), 0.0, np.log(0.035), -0.3])


def ml_grid(dd, PH, ZE, psi):
    ML = np.full((len(PH), len(ZE)), -np.inf); B = {}
    for i, ph in enumerate(PH):
        for j, z in enumerate(ZE):
            m = ModeloNL2(dd, np.tan(np.radians(ph)), z, BETA0)
            try:
                ML[i, j], _ = m.gn(psi); B[(i, j)] = m.beta_nl.copy()
            except Exception:
                pass
    return ML, B


if __name__ == "__main__":
    t0 = time.time()
    # ψ de arranque: ajuste completo en un punto de la cresta de la ronda 3
    m0 = ModeloNL2(d, np.tan(np.radians(24.0)), 0.275, BETA0).ajustar_nl(PSI0)
    print("ψ inicial:", np.round(m0.psi, 3), f"({time.time()-t0:.0f} s)")
    PH = np.r_[0.0, np.arange(10.0, 36.01, 2.0)]; ZE = np.round(np.arange(0.10, 0.601, 0.05), 3)
    ML, B = ml_grid(d, PH, ZE, m0.psi)
    i0, j0 = np.unravel_index(np.argmax(ML), ML.shape)
    print(f"perfil (ψ fija): máx φ′∞ = {PH[i0]}°, ζ0 = {ZE[j0]}, ML {ML[i0, j0]:.2f}; φ′∞ = 0: máx ML {ML[0].max():.2f} ({time.time()-t0:.0f} s)")
    for i, ph in enumerate(PH):
        print(f"  φ′∞ {ph:4.0f}: " + " ".join(f"{ML[i, j] - ML[i0, j0]:6.1f}" for j in range(len(ZE))))
    print("  ζ0:       " + " ".join(f"{z:6.2f}" for z in ZE))
    mf = ModeloNL2(d, np.tan(np.radians(PH[i0])), ZE[j0], B[(i0, j0)]).ajustar_nl(m0.psi)
    mlf, _ = mf.gn(mf.psi); r = mf.resumen()
    print(f"ajuste completo en el óptimo: ML {mlf:.2f}; β = {np.round(mf.beta_nl, 4)}; pub sd(η, ζ, ρ) = {np.round(r['pub'], 3)}; set = {np.round(r['set'], 3)}; a = {np.round(r['a'], 3)}")
    json.dump(dict(phi=PH.tolist(), zeta=ZE.tolist(), ml=ML.tolist(), opt=[float(PH[i0]), float(ZE[j0])], ml_opt=float(mlf),
                   beta=mf.beta_nl.tolist(), psi=mf.psi.tolist()), open(AQ / "lepsp_acotada2_grilla.json", "w", encoding="utf-8"), indent=1)
    print(f"({time.time()-t0:.0f} s)")
