"""Leps-P, ronda 6: datos depurados y modelo extendido (respuesta a los seis revisores).

Datos (auditoría D3, E10): se exige σ′3 informado (se quitan 16 puntos leídos de curvas ajustadas) y se eliminan
ensayos duplicados (Ho-ee, transcripción de Ho-dd con otra e; repeticiones de 19D, UC13/TRS/4 y «C recycled»).
Se agrega la columna «lab» (programa de laboratorio): la unidad independiente para validación y pruebas (D1).

Modelo (misma forma acotada de la ronda 5):
    y = x + ln[T + (e^η − T)·e^(−ζx)] + ε
    η = β_c + β_e e + β_D ln(Dmax/D_REF) + u_η            (E2: el tamaño entra al modelo; G_s deja de absorberlo)
    ζ = ζ0 + δζ_moderate + δζ_low + u_ζ                     (G3: decaimiento por clase de calidad de roca)
con tres extensiones de la verosimilitud, activables por separado:
  - truncamiento (C1/G4/E7): la base excluyó los sets con φ′1 < 31°; como en x = 0 la envolvente vale tan φ′s = e^η,
    cada set aporta −ln Φ((μ_η,set − η_t)/s_η), η_t = ln tan 31°, s_η² = G_p,ηη + G_s,ηη;
  - censura (B2/G2): ensayos con εa ≥ EPS_CENS en el máximo desviador (deformación cerca del límite del equipo) se
    tratan como τ ≥ τ_obs; se imputan con la esperanza condicional truncada dentro del bloque de la publicación
    (EM aproximado, tipo Tobit), iterada con el ajuste;
  - Dmax faltante (52 ensayos de 4 publicaciones): se imputa como Ds/6 si hay diámetro de probeta; si no, la mediana.
Estimación como en la ronda 5: linealización de primer orden, Gauss–Newton para los efectos fijos y REML para ψ.
Uso: python lepsp_r6.py diag   → efecto de cada extensión en (25°, ζ0 = 0.30)."""
import sys, json, time, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo  # noqa: E402

CL = ["good", "moderate", "low"]
D_REF = 100.0                                   # mm: tamaño máximo de referencia de los valores de diseño
ETA_T = float(np.log(np.tan(np.radians(31.0))))  # truncamiento de la base (Cylwik et al. 2025)
EPS_CENS = 19.0                                  # % de deformación axial en el máximo desviador

LAB = {"Donaghe & Cohen (1978)": "L1", "Donaghe & Torrey (1979)": "L1", "Al-Hussaini (1983)": "L1",
       "SMHEA (1965)": "L2", "SMHEA(1966)": "L2", "SMHEA(1967)": "L2", "SMHEA(1968)": "L2", "SMEC (1973)": "L3", "SMEC (1976-80)": "L3",
       "HEC (1970)": "L4", "HEC (1971)": "L4", "HEC (1984)": "L4", "Marsal (1971)": "L5", "Marsal (1973)": "L5", "Marsal et al. (1965)": "L5",
       "Indraratna et al (1993)": "L6", "Indraratna et al (1998)": "L6", "Ionescu and Indraratna (2003)": "L6",
       "Ovalle et al (2014)": "L7", "Ovalle et al. (2020)": "L7"}


def datos(limpiar=True):
    d = preparar(load_db(), CLASE)
    n0 = len(d)
    if limpiar:
        dup = ((d.Set == "Holtz & Gibbs (1956) | Ho-ee") | ((d.Set == "SMHEA(1966) | ZD/3A/2/L/19D-c") & (d.s3 < 0.6)) |
               ((d.Set == "Ionescu and Indraratna (2003) | C recycled") & (d.s3 == 0.06)) | ((d.Set == "SMEC (1976-80) | UC13/TRS/4-c") & (d.s3 < 0.6)))
        d = d[d.s3.notna() & ~dup]
        d = d[d.groupby("Set").sn.transform("size") >= 2].reset_index(drop=True)
    d["lab"] = d.pub.map(LAB).fillna(d.pub)
    D = d.Dmax.copy(); ds = pd.to_numeric(d["Ds (mm)"], errors="coerce")
    D = D.fillna(ds / 6.0); d["Dmax_imp"] = d.Dmax.isna(); D = D.fillna(D.median())
    d["Dm"] = D; d["lnD"] = np.log(D / D_REF)
    d["cens"] = d.eax >= EPS_CENS
    d["y_obs"] = d.y.values
    d.attrs["n_quitados"] = n0 - len(d)
    return d


NB = 7                                           # good, moderate, low, e, lnD, δζ_moderate, δζ_low
NOMBRES = CL + ["e", "lnD", "dz_moderate", "dz_low"]


def media3(beta, dd, T, z0, clase_z=True):
    """f, J (∂f/∂β) y Z (∂f/∂η, ∂f/∂ζ) en u = 0."""
    dum = np.c_[[(dd.clase == c).values.astype(float) for c in CL]].T
    e, x, lD = dd.e.values, dd.x.values, dd.lnD.values
    eta = dum @ beta[:3] + beta[3] * e + beta[4] * lD
    zeta = z0 + (beta[5] * dum[:, 1] + beta[6] * dum[:, 2] if clase_z else 0.0)
    E = np.exp(eta); q = np.exp(-zeta * x)
    g = np.maximum(T + (E - T) * q, 1e-9); f = x + np.log(g)
    w = E * q / g; dz = -x * (E - T) * q / g
    J = np.c_[dum * w[:, None], w * e, w * lD, dz * dum[:, 1], dz * dum[:, 2]]
    if not clase_z:
        J[:, 5:] = 0.0
    return f, J, np.c_[w, dz]


class ModeloR6(Modelo):
    def __init__(self, dd, T, z0, beta0, trunc=True, cens=True, clase_z=True, usar_D=True):
        self.dd, self.T, self.z0 = dd.copy(), T, z0
        self.trunc, self.cens, self.clase_z, self.usar_D = trunc, cens, clase_z, usar_D
        b = np.zeros(NB); b[:len(beta0)] = beta0; self.beta_nl = b
        f, J, Z = media3(self.beta_nl, self.dd, T, z0, clase_z)
        J = self._mascara(J)
        d2 = self.dd.copy(); d2["y"] = self.dd.y.values - f + J @ self.beta_nl
        super().__init__(d2, J, NOMBRES); self.Zall = Z
        # sets para el truncamiento: primera fila de cada set (clase, e y lnD son constantes en el set)
        self.set_idx = self.dd.groupby("Set").head(1).index.values

    def _mascara(self, J):
        J = J.copy()
        if not self.usar_D:
            J[:, 4] = 0.0
        if not self.clase_z:
            J[:, 5:] = 0.0
        # columnas nulas → parámetro fijo en 0 (pequeña regularización para que X'V⁻¹X sea invertible)
        return J

    def _V(self, ip, Zs, Gp, Gs, a):
        x = self.x[ip]; Z = self.Zall[ip]
        V = Z @ Gp @ Z.T
        for ind in Zs:
            Zi = Z * ind[:, None]; V += Zi @ Gs @ Zi.T
        V[np.diag_indices_from(V)] += np.exp(a[0] + a[1] * x) ** 2
        return V

    def _activos(self):
        return [j for j in range(NB) if not ((j == 4 and not self.usar_D) or (j >= 5 and not self.clase_z))]

    def reml(self, psi, devolver=False):
        """REML de lepsp_modelo restringido a los efectos fijos activos, más el término de truncamiento."""
        act = self._activos(); Xf = self.X
        self.X = Xf[:, act]
        try:
            out = super().reml(psi, devolver=True)
        finally:
            self.X = Xf
        if not isinstance(out, tuple):
            return out if not devolver else (out, None, None)
        ll, b_act, C_act = out
        b = np.zeros(NB); b[act] = b_act; C = np.zeros((NB, NB)); C[np.ix_(act, act)] = C_act
        if self.trunc:
            ll += self._pen_trunc(psi, self.beta_nl)
        return (ll, b, C) if devolver else ll

    def _mu_eta_sets(self, beta):
        r = self.dd.loc[self.set_idx]
        dum = np.c_[[(r.clase == c).values.astype(float) for c in CL]].T
        return dum @ beta[:3] + beta[3] * r.e.values + beta[4] * r.lnD.values, dum, r

    def _pen_trunc(self, psi, beta):
        # La selección (sets con φ′1 < 31° excluidos) actúa sobre cada set DADO el efecto de su publicación, que la verosimilitud
        # de los datos ya integra: se usa solo la varianza entre sets. Con la varianza marginal (publicación + set) y sets
        # tratados como independientes, inflar G_p «premiaba» hasta ln 2 por set (≈ +150 en total) y el MCMC derivaba a
        # sd(η)_pub ≈ 1 (ronda 6, corregido el 2026-10-07).
        Gp, Gs, _ = self.desempacar(psi); s = np.sqrt(Gs[0, 0])
        mu, _, _ = self._mu_eta_sets(beta)
        return -float(np.sum(norm.logcdf((mu - ETA_T) / s)))

    def _paso_trunc(self, psi, beta, C):
        """Corrección de β por el truncamiento: un paso de Newton con la curvatura de los datos (C = (X'V⁻¹X)⁻¹)."""
        Gp, Gs, _ = self.desempacar(psi); s = np.sqrt(Gs[0, 0])               # ver _pen_trunc
        mu, dum, r = self._mu_eta_sets(beta); z = (mu - ETA_T) / s
        lam = np.exp(norm.logpdf(z) - norm.logcdf(z))           # razón de Mills inversa
        dmu = np.c_[dum, r.e.values, r.lnD.values, np.zeros((len(mu), 2))]
        grad = -(lam / s) @ dmu                                  # ∂(−Σ ln Φ)/∂β
        return C @ grad

    def imputar_censura(self, psi):
        """E-step: para cada ensayo censurado, y* = E[y | y ≥ y_obs, resto del bloque] con la normal condicional."""
        if not self.cens or not self.dd.cens.any():
            return 0.0
        Gp, Gs, a = self.desempacar(psi)
        f, _, _ = media3(self.beta_nl, self.dd, self.T, self.z0, self.clase_z)
        ycur = self.dd.y.values.copy(); cambio = 0.0
        for ip, Zs in self.bloques:
            c = np.where(self.dd.cens.values[ip])[0]
            if len(c) == 0:
                continue
            V = self._V(ip, Zs, Gp, Gs, a); r = ycur[ip] - f[ip]
            for k in c:
                o = np.r_[0:k, k + 1:len(ip)]
                if len(o):
                    w = np.linalg.solve(V[np.ix_(o, o)], V[o, k]); m = f[ip][k] + w @ r[o]; v = V[k, k] - V[k, o] @ w
                else:
                    m, v = f[ip][k], V[k, k]
                s = np.sqrt(max(v, 1e-8)); al = (self.dd.y_obs.values[ip][k] - m) / s
                ynew = m + s * np.exp(norm.logpdf(al) - norm.logsf(al))
                cambio = max(cambio, abs(ynew - ycur[ip][k])); ycur[ip[k]] = ynew; r[k] = ynew - f[ip][k]
        self.dd["y"] = ycur
        return cambio

    def relinealizar(self):
        f, J, Z = media3(self.beta_nl, self.dd, self.T, self.z0, self.clase_z)
        J = self._mascara(J)
        self.X = J; self.y = self.dd.y.values - f + J @ self.beta_nl; self.Zall = Z

    def gn(self, psi, it=30, tol=1e-7):
        for _ in range(it):
            self.relinealizar(); ll, b, C = self.reml(psi, devolver=True)
            if b is None:
                return -1e12, None
            if self.trunc:
                b = b + self._paso_trunc(psi, b, C)
            paso = b - self.beta_nl; self.beta_nl = self.beta_nl + paso
            if np.max(np.abs(paso)) < tol:
                break
        self.relinealizar(); ll, b, C = self.reml(psi, devolver=True)
        act = self._activos()
        return ll - 0.5 * np.linalg.slogdet(C[np.ix_(act, act)])[1], C

    def ajustar_nl(self, psi0, it_cens=8):
        self.gn(psi0)
        for i in range(3 + (it_cens if self.cens else 0)):
            if self.cens:
                ch = self.imputar_censura(psi0)
            self.ajustar(psi0); psi0 = self.psi; self.gn(psi0)
            if self.cens and i >= 2 and ch < 1e-4:
                break
        self.relinealizar(); self.ll, _, self.cov_beta = self.reml(self.psi, devolver=True); self.beta = self.beta_nl
        self.ml, _ = self.gn(self.psi)
        return self

    def ll_obs(self, psi=None, beta=None):
        """Log-verosimilitud de los datos OBSERVADOS (comparable entre φ′∞, ζ0 y formas): densidad normal de los ensayos no
        censurados (bloque por publicación, con la covarianza de primer orden) + Σ ln P(y ≥ y_obs | no censurados del
        bloque) de los censurados (aproximación: censurados condicionalmente independientes entre sí) + truncamiento."""
        psi = self.psi if psi is None else psi; beta = self.beta_nl if beta is None else beta
        Gp, Gs, a = self.desempacar(psi)
        f, _, Z = media3(beta, self.dd, self.T, self.z0, self.clase_z); Zsave = self.Zall; self.Zall = Z
        yo = self.dd.y_obs.values; cen = self.dd.cens.values if self.cens else np.zeros(len(yo), bool); ll = 0.0
        try:
            for ip, Zs in self.bloques:
                V = self._V(ip, Zs, Gp, Gs, a); r = yo[ip] - f[ip]; c = cen[ip]; u = ~c
                if u.any():
                    Vu = V[np.ix_(u, u)]; L = np.linalg.cholesky(Vu); z = np.linalg.solve(L, r[u])
                    ll += -0.5 * (z @ z) - np.log(np.diag(L)).sum() - 0.5 * u.sum() * np.log(2 * np.pi)
                for k in np.where(c)[0]:
                    if u.any():
                        w = np.linalg.solve(Vu, V[u, k]); m = w @ r[u]; v = V[k, k] - V[k, u] @ w
                    else:
                        m, v = 0.0, V[k, k]
                    ll += norm.logsf((r[k] - m) / np.sqrt(max(v, 1e-10)))
        finally:
            self.Zall = Zsave
        if self.trunc:
            ll += self._pen_trunc(psi, beta)
        return float(ll)

    def predecir(self, dte):
        f, J, Z = media3(self.beta_nl, dte, self.T, self.z0, self.clase_z); x = dte.x.values; J = self._mascara(J)
        v = np.einsum("ij,jk,ik->i", Z, self.Gp + self.Gs, Z) + np.einsum("ij,jk,ik->i", J, self.cov_beta, J) + self.sigma_eps(x) ** 2
        return f, np.sqrt(v), J, Z


BETA0 = np.array([0.19, 0.093, 0.023, -0.52, 0.0, 0.0, 0.0])
PSI0 = np.array([np.log(0.06), np.log(0.05), 0.0, np.log(0.08), np.log(0.05), 0.0, np.log(0.035), -0.3])


def resumen(m):
    r = m.resumen(); se = np.sqrt(np.clip(np.diag(m.cov_beta), 0, None))
    return dict(ml=float(m.ml), beta=dict(zip(NOMBRES, np.round(m.beta_nl, 4))), se=dict(zip(NOMBRES, np.round(se, 4))),
                pub=np.round(r["pub"], 3).tolist(), set=np.round(r["set"], 3).tolist(), a=np.round(r["a"], 3).tolist())


if __name__ == "__main__" and sys.argv[1:2] == ["diag"]:
    t0 = time.time(); T = np.tan(np.radians(25.0)); z0 = 0.30
    d0 = datos(limpiar=False); d1 = datos()
    print(f"datos: {len(d0)} → {len(d1)} ensayos ({d1.attrs['n_quitados']} quitados), {d1.Set.nunique()} sets, {d1.pub.nunique()} publicaciones, "
          f"{d1.lab.nunique()} laboratorios; censurados (εa ≥ {EPS_CENS:g} %): {int(d1.cens.sum())}; Dmax imputado: {int(d1.Dmax_imp.sum())}")
    casos = [("r5 (sin limpieza ni extensiones)", d0, dict(trunc=False, cens=False, clase_z=False, usar_D=False)),
             ("limpio", d1, dict(trunc=False, cens=False, clase_z=False, usar_D=False)),
             ("+ lnD", d1, dict(trunc=False, cens=False, clase_z=False, usar_D=True)),
             ("+ ζ por clase", d1, dict(trunc=False, cens=False, clase_z=True, usar_D=True)),
             ("+ truncamiento", d1, dict(trunc=True, cens=False, clase_z=True, usar_D=True)),
             ("+ censura (completo)", d1, dict(trunc=True, cens=True, clase_z=True, usar_D=True))]
    out = {}
    for nm, dd, kw in casos:
        m = ModeloR6(dd, T, z0, BETA0, **kw).ajustar_nl(PSI0); out[nm] = resumen(m)
        print(f"{nm:34s} ML {m.ml:9.2f}  β {np.round(m.beta_nl, 3)}  pub {np.round(m.resumen()['pub'], 3)}  set {np.round(m.resumen()['set'], 3)}  a {np.round(m.a, 3)} ({time.time()-t0:.0f} s)", flush=True)
    json.dump(out, open(AQ / "lepsp_r6_diag.json", "w", encoding="utf-8"), indent=1)
