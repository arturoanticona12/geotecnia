"""Leps 3.0: criterio probabilístico de resistencia al corte para enrocados y desmonte de mina.

Implementación de referencia. Unidades: MPa y grados.

Modelo (lineal mixto en log–log, calibrado con la base de Arrieta, 2025; Cylwik et al., 2025):
    y = ln(τ/σ0) = θ + m·x + ε,   x = ln(σ′n/σ0),   σ0 = 10 pa
    θ = β[calidad] + βe·e + b0,   m = μm + b1,   (b0, b1) ~ N(0, Σ),   ε ~ N(0, σε(x)²)
θ = ln tan φ′1. La envolvente se restringe a m ≤ 1 (no convexa).

Uso típico:
    pr = previa("moderada", e=0.45)                      # material sin ensayos
    po = actualizar(pr, s3=[0.5, 1.0, 2.0], s1=[...])    # con triaxiales drenados del sitio
    percentiles([1, 5, 10], po, [10, 50])                # φ′s por percentil y σ′n
"""
from __future__ import annotations
import math, warnings
from dataclasses import dataclass, field
import numpy as np
from scipy.stats import truncnorm

PA = 0.1013
S0 = 10 * PA
# Parámetros poblacionales (ajuste REML sobre 767 ensayos, 226 sets, 36 publicaciones; σ′3 ≥ 60 kPa)
# (copiados de analisis/leps3_prob_parametros.json)
BETA = {"buena": 0.26352970, "moderada": 0.14042655, "baja": 0.02744628}
BETA_E = -0.58911458
MU_M = 0.85995228
SIGMA = np.array([[0.00943769, -0.00133991], [-0.00133991, 0.00262612]])   # σθ 0.097, σm 0.051, ρ −0.27
XC = np.array([-1.5, -0.5, 0.5, 1.5])                         # centros de rangos de x
SX = np.array([0.03397966, 0.02840229, 0.02902815, 0.01884854])  # σε por rango (dispersión dentro del material)
SN_MAX_BASE = 7.9                                 # σ′n máximo de la base mundial (MPa)


def sigma_eps(x):
    return np.interp(x, XC, SX)


@dataclass
class Estado:
    """Distribución de (θ, m) de un material: media, covarianza y σ′n máximo ensayado (None si no hay ensayos)."""
    media: np.ndarray
    cov: np.ndarray
    sn_max_ensayado: float | None = None
    n_ensayos: int = 0
    notas: list = field(default_factory=list)


def previa(calidad: str, e: float) -> Estado:
    """Material sin ensayos propios: calidad «buena», «moderada» o «baja» (Tabla 5 de Cylwik et al., 2025) y e inicial."""
    return Estado(np.array([BETA[calidad] + BETA_E * e, MU_M]), SIGMA.copy())


def phi1_mediana(est: Estado) -> float:
    return math.degrees(math.atan(math.exp(est.media[0])))


def _a_sn_tau(s3, s1, m):
    """Ecs. 13, 14 y 16 de Cylwik et al. (2025)."""
    D, S = s1 - s3, s1 + s3
    sp = D / S if abs(m - 1) < 1e-6 else (np.sqrt(4 * m * (m - 1) * D ** 2 + S ** 2) - S) / (2 * (m - 1) * D)
    return S / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


def actualizar(est: Estado, s3, s1, iter_=4) -> Estado:
    """Posterior gaussiana exacta de (θ, m) con triaxiales drenados del mismo material (σ′3 y σ′1 en la falla, MPa).
    La conversión a (σ′n, τ) usa el m vigente y se itera."""
    s3, s1 = np.asarray(s3, float), np.asarray(s1, float)
    if np.any(s1 <= s3) or np.any(s3 <= 0):
        raise ValueError("Se requiere σ′1 > σ′3 > 0")
    m_c = min(est.media[1], 1.0)
    sn, mu, C = s3, est.media, est.cov
    for _ in range(max(iter_, 1)):
        sn, tau = _a_sn_tau(s3, s1, m_c)
        x = np.log(sn / S0); y = np.log(tau / S0)
        Z = np.c_[np.ones_like(x), x]; Rinv = np.diag(1 / sigma_eps(x) ** 2); Si = np.linalg.inv(est.cov)
        C = np.linalg.inv(Si + Z.T @ Rinv @ Z); mu = C @ (Si @ est.media + Z.T @ Rinv @ y)
        m_c = float(np.clip(mu[1], 0.5, 1.0))
    smax = float(sn.max()) if est.sn_max_ensayado is None else max(est.sn_max_ensayado, float(sn.max()))
    return Estado(mu, C, smax, est.n_ensayos + len(s3), est.notas + [f"actualizado con {len(s3)} ensayos"])


def muestras(est: Estado, n=20000, rng=None):
    """(θ, m) de la distribución condicionada a m ≤ 1 (exacto: m truncada y θ | m)."""
    rng = np.random.default_rng(0) if rng is None else rng
    mu, C = est.media, est.cov
    sm = math.sqrt(C[1, 1]); b = (1.0 - mu[1]) / sm
    m = np.asarray(truncnorm.rvs(-np.inf, b, loc=mu[1], scale=sm, size=n, random_state=rng), float)
    th = mu[0] + C[0, 1] / C[1, 1] * (m - mu[1]) + rng.normal(0, math.sqrt(C[0, 0] - C[0, 1] ** 2 / C[1, 1]), n)
    return th, m


def _dominio(sn, est):
    sn = np.atleast_1d(sn)
    if np.any(sn > SN_MAX_BASE):
        warnings.warn(f"σ′n > {SN_MAX_BASE} MPa: fuera del rango de la base mundial; extrapolación.", stacklevel=3)
    if est.sn_max_ensayado and np.any(sn > 3 * est.sn_max_ensayado):
        warnings.warn("σ′n > 3 veces el máximo ensayado en el sitio: los intervalos no están verificados en ese rango.", stacklevel=3)


def percentiles(sn, est: Estado, ps=(10, 50, 90), material_nuevo=True, n=20000, rng=None):
    """Percentiles del ángulo secante φ′s (°) a cada σ′n. material_nuevo=True incluye la dispersión dentro del material
    (resistencia de un punto); False da la incertidumbre de la envolvente media del material."""
    sn = np.atleast_1d(np.asarray(sn, float)); _dominio(sn, est)
    rng = np.random.default_rng(1) if rng is None else rng
    th, m = muestras(est, n, rng); x = np.log(sn / S0)
    y = th[:, None] + m[:, None] * x[None, :]
    if material_nuevo:
        y = y + rng.normal(0, 1, (n, 1)) * sigma_eps(x)[None, :]
    ph = np.degrees(np.arctan(S0 * np.exp(y) / sn[None, :]))
    return {p: np.percentile(ph, p, axis=0) for p in ps}


def tau_percentil(sn, est: Estado, p=10, **kw):
    sn = np.atleast_1d(np.asarray(sn, float))
    return sn * np.tan(np.radians(percentiles(sn, est, (p,), **kw)[p]))


def tabla_slide2(est: Estado, p=50, sn_max=16.0, n_pts=30, unidades="kPa", **kw):
    """Pares (σ′n, τ) del percentil p para un material de tipo función (p. ej., Slide2)."""
    f = 1000.0 if unidades == "kPa" else 1.0
    sn = np.logspace(math.log10(0.01), math.log10(sn_max), n_pts)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        t = tau_percentil(sn, est, p, **kw)
    return [(0.0, 0.0)] + [(round(a * f, 3), round(b * f, 3)) for a, b in zip(sn, t)]
