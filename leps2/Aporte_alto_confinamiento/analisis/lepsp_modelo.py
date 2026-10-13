"""Leps-P: modelo lineal mixto de tres niveles (publicación → set → ensayo) en log–log, con heterocedasticidad
estimada dentro de la verosimilitud. Estimación por REML propio (integra los efectos fijos y aleatorios de forma
analítica) y muestreo MCMC de los hiperparámetros sobre la verosimilitud REML (propaga su incertidumbre).

    y = X β + Z (b_pub + b_set) + ε,   y = ln(τ/σ0),  x = ln(σ′n/σ0),  z = (1, x)
    b_pub ~ N(0, G_p),  b_set ~ N(0, G_s),  ln σ_ε(x) = a0 + a1 x
"""
import numpy as np, pandas as pd
from scipy.optimize import minimize

PA = 0.1013
S0 = 10 * PA


def preparar(df, clase_map):
    d = df[(df.s3.isna() | (df.s3 >= 0.06)) & (df.sn > 0) & df.e.notna()].copy()
    d["clase"] = d["Material Type"].map(clase_map)
    d = d[d.groupby("Set").sn.transform("size") >= 2].reset_index(drop=True)
    d["x"] = np.log(d.sn / S0); d["y"] = np.log(d.tau / S0)
    d["pub"] = d.Reference.astype(str)
    return d


def _chol2(p):
    """Covarianza 2×2 a partir de (ln sd0, ln sd1, atanh ρ)."""
    s0, s1, r = np.exp(p[0]), np.exp(p[1]), np.tanh(p[2])
    return np.array([[s0 * s0, r * s0 * s1], [r * s0 * s1, s1 * s1]])


class Modelo:
    """X: matriz de efectos fijos (n×k). Índices de publicación y set. psi = 8 hiperparámetros."""

    def __init__(self, d, X, nombres, het=True):
        self.d, self.X, self.nombres, self.het = d, np.asarray(X, float), list(nombres), het
        self.y = d.y.values; self.x = d.x.values
        self.bloques = []
        for p, ip in d.groupby("pub").groups.items():
            ip = np.asarray(ip)
            sets = d.loc[ip, "Set"].values
            Zs = [(sets == s).astype(float) for s in pd.unique(sets)]
            self.bloques.append((ip, Zs))

    def _V(self, ip, Zs, Gp, Gs, a):
        x = self.x[ip]; Z = np.c_[np.ones_like(x), x]
        V = Z @ Gp @ Z.T
        for ind in Zs:
            Zi = Z * ind[:, None]; V += Zi @ Gs @ Zi.T
        se = np.exp(a[0] + a[1] * x) if self.het else np.full_like(x, np.exp(a[0]))
        V[np.diag_indices_from(V)] += se ** 2
        return V

    def desempacar(self, psi):
        return _chol2(psi[0:3]), _chol2(psi[3:6]), psi[6:8]

    def reml(self, psi, devolver=False):
        Gp, Gs, a = self.desempacar(psi)
        k = self.X.shape[1]; XtVX = np.zeros((k, k)); XtVy = np.zeros(k); ld = 0.0; cache = []
        for ip, Zs in self.bloques:
            V = self._V(ip, Zs, Gp, Gs, a)
            try:
                L = np.linalg.cholesky(V)
            except np.linalg.LinAlgError:
                return -1e12
            ld += 2 * np.log(np.diag(L)).sum()
            Xi = np.linalg.solve(L, self.X[ip]); yi = np.linalg.solve(L, self.y[ip])
            XtVX += Xi.T @ Xi; XtVy += Xi.T @ yi; cache.append((ip, Zs, L, Xi, yi))
        try:
            C = np.linalg.cholesky(XtVX)
        except np.linalg.LinAlgError:
            return -1e12
        beta = np.linalg.solve(XtVX, XtVy)
        q = sum(((yi - Xi @ beta) ** 2).sum() for _, _, _, Xi, yi in cache)
        ll = -0.5 * (ld + 2 * np.log(np.diag(C)).sum() + q)
        if devolver:
            return ll, beta, np.linalg.inv(XtVX)
        return ll

    def ajustar(self, psi0=None):
        if psi0 is None:
            psi0 = np.array([np.log(0.05), np.log(0.03), 0, np.log(0.08), np.log(0.04), -0.3, np.log(0.035), 0.0])
        if not self.het:
            f = lambda p: -self.reml(np.r_[p, 0.0])
            r = minimize(f, psi0[:7], method="Nelder-Mead", options=dict(maxiter=20000, maxfev=20000, xatol=1e-5, fatol=1e-6))
            r = minimize(f, r.x, method="L-BFGS-B"); self.psi = np.r_[r.x, 0.0]
        else:
            f = lambda p: -self.reml(p)
            r = minimize(f, psi0, method="Nelder-Mead", options=dict(maxiter=20000, maxfev=20000, xatol=1e-5, fatol=1e-6))
            r = minimize(f, r.x, method="L-BFGS-B"); self.psi = r.x
        self.ll, self.beta, self.cov_beta = self.reml(self.psi, devolver=True)
        self.Gp, self.Gs, self.a = self.desempacar(self.psi)
        return self

    def resumen(self):
        sd = lambda G: (np.sqrt(G[0, 0]), np.sqrt(G[1, 1]), G[0, 1] / np.sqrt(G[0, 0] * G[1, 1]))
        return dict(ll=self.ll, beta=dict(zip(self.nombres, self.beta)), se=dict(zip(self.nombres, np.sqrt(np.diag(self.cov_beta)))),
                    pub=sd(self.Gp), set=sd(self.Gs), a=tuple(self.a))

    def sigma_eps(self, x, a=None):
        a = self.a if a is None else a
        return np.exp(a[0] + a[1] * np.asarray(x)) if self.het else np.full(np.shape(x), np.exp(a[0]))

    def residuos_marginales(self):
        return self.y - self.X @ self.beta


def mcmc_hiper(mod, n=4000, burn=1000, paso=None, seed=0):
    """Metrópolis adaptativo sobre la verosimilitud REML (previas planas en la parametrización log/atanh)."""
    rng = np.random.default_rng(seed); p = mod.psi.copy(); lp = mod.reml(p); k = len(p)
    S = np.eye(k) * (0.05 if paso is None else paso) ** 2; cad = []; acc = 0
    for i in range(n + burn):
        q = rng.multivariate_normal(p, S); lq = mod.reml(q)
        if np.log(rng.random()) < lq - lp:
            p, lp = q, lq; acc += 1
        cad.append(p.copy())
        if 200 <= i < burn and i % 100 == 0:
            S = np.cov(np.array(cad[-200:]).T) * 2.38 ** 2 / k + np.eye(k) * 1e-6
    return np.array(cad[burn:]), acc / (n + burn)
