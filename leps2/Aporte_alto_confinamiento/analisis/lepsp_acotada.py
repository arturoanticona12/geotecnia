"""Leps-P, ronda 3: envolvente acotada por el estado crítico dentro del modelo jerárquico, validada en modo A (LOPO).

    tan φ′s = T + (tan φ′1 − T)·exp(−λx),   T = tan φ′cs,  x = ln(σ′n/σ0)
    y = ln(τ/σ0) = x + ln[T + (e^η − T) e^(−λx)] + b0 + b1 x + ε,   η = β_c + β_e e

Mismos efectos aleatorios (publicación y set sobre nivel y pendiente en log–log) y misma heterocedasticidad que el
modelo cuadrático M2. Los efectos fijos no lineales se estiman por Gauss–Newton (linealización de la media) con la
REML de lepsp_modelo.Modelo. (φ′cs, λ) son globales y se eligen en cada pliegue por verosimilitud máxima (ML) perfilada
sobre una grilla, solo con los datos de entrenamiento (sin mirar la publicación excluida).
Argumento 'full' (defecto): ajuste con todos los datos + LOPO. Salida: lepsp_acotada_A.csv, lepsp_acotada.json."""
import sys, json, time, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo  # noqa: E402

d = preparar(load_db(), CLASE)
CL = ["good", "moderate", "low"]
GRID_PHI = [28.0, 31.0, 34.0, 37.0, 40.0]
GRID_LAM = [0.15, 0.25, 0.40, 0.60, 0.90]


def media(beta, dd, T, lam):
    """f(x) y jacobiano respecto de (β_good, β_moderate, β_low, β_e)."""
    dum = np.c_[[(dd.clase == c).values.astype(float) for c in CL]].T
    e, x = dd.e.values, dd.x.values
    eta = dum @ beta[:3] + beta[3] * e
    a = np.exp(eta) * np.exp(-lam * x); den = np.maximum(T + (np.exp(eta) - T) * np.exp(-lam * x), 1e-6)
    f = x + np.log(den); w = a / den
    return f, np.c_[dum * w[:, None], w * e]


class ModeloNL(Modelo):
    """Modelo con media no lineal: se reemplaza y por la pseudo-respuesta de la linealización."""

    def __init__(self, dd, T, lam, beta0):
        self.dd, self.T, self.lam, self.beta_nl = dd, T, lam, np.asarray(beta0, float)
        f, J = media(self.beta_nl, dd, T, lam)
        d2 = dd.copy(); d2["y"] = dd.y.values - f + J @ self.beta_nl
        super().__init__(d2, J, ["good", "moderate", "low", "e"])

    def relinealizar(self):
        f, J = media(self.beta_nl, self.dd, self.T, self.lam)
        self.X = J; self.y = self.dd.y.values - f + J @ self.beta_nl

    def gn(self, psi, it=25, tol=1e-7):
        """Gauss–Newton para β con ψ fija; devuelve la log-verosimilitud ML."""
        for _ in range(it):
            self.relinealizar()
            ll, b, C = self.reml(psi, devolver=True)
            paso = b - self.beta_nl; self.beta_nl = self.beta_nl + paso
            if np.max(np.abs(paso)) < tol:
                break
        self.relinealizar(); ll, b, C = self.reml(psi, devolver=True)
        return ll - 0.5 * np.linalg.slogdet(C)[1], C          # ML = REML + ½ log|XᵀV⁻¹X| = REML − ½ log|C|

    def ajustar_nl(self, psi0):
        self.gn(psi0)
        for _ in range(3):                                       # alternar ψ (REML de la linealización) y β (GN)
            self.ajustar(psi0); psi0 = self.psi; self.gn(psi0)
        self.relinealizar(); self.ll, b, self.cov_beta = self.reml(self.psi, devolver=True)
        self.beta = self.beta_nl
        return self

    def predecir(self, dte):
        f, J = media(self.beta_nl, dte, self.T, self.lam); x = dte.x.values; Z = np.c_[np.ones_like(x), x]
        v = np.einsum("ij,jk,ik->i", Z, self.Gp + self.Gs, Z) + np.einsum("ij,jk,ik->i", J, self.cov_beta, J) + self.sigma_eps(x) ** 2
        return f, np.sqrt(v)


def beta_inicial(dd):
    return np.array([0.19, 0.093, 0.023, -0.52])


def elegir(dtr, psi):
    """(φcs, λ) por ML perfilada en la grilla, con ψ fija (la del modelo cuadrático del mismo entrenamiento)."""
    mejor = None; tabla = []
    for ph in GRID_PHI:
        for lam in GRID_LAM:
            m = ModeloNL(dtr, np.tan(np.radians(ph)), lam, beta_inicial(dtr))
            try:
                ll, _ = m.gn(psi)
            except Exception:
                ll = -np.inf
            tabla.append((ph, lam, float(ll)))
            if mejor is None or ll > mejor[2]:
                mejor = (ph, lam, ll, m.beta_nl.copy())
    return mejor, tabla


def disenio_m2(dd):
    dum = np.c_[[(dd.clase == c).values.astype(float) for c in CL]].T
    return np.c_[dum, dd.e.values, dd.x.values, dd.x.values ** 2]


if __name__ == "__main__":
    t0 = time.time(); out = {}
    # ---- ajuste con todos los datos
    m2 = Modelo(d, disenio_m2(d), ["g", "m", "l", "e", "x", "x2"]).ajustar()
    (ph, lam, ll, b0), tabla = elegir(d, m2.psi)
    mf = ModeloNL(d, np.tan(np.radians(ph)), lam, b0).ajustar_nl(m2.psi)
    ml_m2 = m2.ll - 0.5 * np.linalg.slogdet(m2.cov_beta)[1]
    ml_nl, _ = mf.gn(mf.psi)
    out["completo"] = dict(phi_cs=ph, lam=lam, beta=mf.beta_nl.tolist(), se=np.sqrt(np.diag(mf.cov_beta)).tolist(), psi=mf.psi.tolist(),
                           ml_acotada=float(ml_nl), ml_m2=float(ml_m2), k_m2=6, k_acotada=6, grilla=tabla)
    print(f"completo: φcs = {ph}°, λ = {lam}, β = {np.round(mf.beta_nl, 4)}, ML acotada {ml_nl:.1f} vs M2 {ml_m2:.1f} ({time.time()-t0:.0f} s)", flush=True)
    if "completo" in sys.argv:                                     # prueba rápida: solo el ajuste con todos los datos
        print("grilla (φcs, λ, ML):", sorted(tabla, key=lambda t: -t[2])[:6]); sys.exit()
    # ---- LOPO
    filas = []
    for g in d.pub.unique():
        tr = d[d.pub != g].reset_index(drop=True); te = d[d.pub == g].reset_index(drop=True)
        if tr.clase.isna().any() or te.clase.isna().any():
            continue
        m2f = Modelo(tr, disenio_m2(tr), ["g", "m", "l", "e", "x", "x2"]).ajustar()
        (ph, lam, ll, b0), _ = elegir(tr, m2f.psi)
        mf = ModeloNL(tr, np.tan(np.radians(ph)), lam, b0).ajustar_nl(m2f.psi)
        mu, sd = mf.predecir(te)
        for k in range(len(te)):
            filas.append(dict(pub=g, Set=te.Set[k], x=te.x[k], y=te.y[k], mu=mu[k], sd=sd[k], phi_cs=ph, lam=lam))
        print(f"  {g[:40]:40s} n={len(te):3d} φcs={ph} λ={lam} ({time.time()-t0:.0f} s)", flush=True)
    pd.DataFrame(filas).to_csv(AQUI / "lepsp_acotada_A.csv", index=False)
    json.dump(out, open(AQUI / "lepsp_acotada.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("escrito lepsp_acotada_A.csv y lepsp_acotada.json")
