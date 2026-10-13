"""Curva propuesta compuesta (decisión de WA, 2026-10-12): Leps 2.0 con exponente local variable.
  τ(σ′n, e) = tan(φ′e=0 − ω·e) · 10pa · exp(∫_{ln 10pa}^{ln σ′n} m(x) dx),   x = ln σ′n
  m(x) = m_A                              para σ′n ≤ σ_a (4.23 MPa, máximo σ′n de los ensayos de Antamina convertidos con m = 1)
       = m_A + (m_H − m_A)·(x − x_a)/(x_b − x_a)  entre σ_a y σ_b (7.86 MPa, máximo de la base mundial de Leps 2.0)
       = m_H                              para σ′n ≥ σ_b
Con m_A = 1 (ajuste a Antamina, nivel por set) la curva es lineal hasta 4.23 MPa; m_H = 0.85 es el exponente que predice sin sesgo
los ensayos mundiales sobre 4.6 MPa (a31). La integral tiene forma cerrada (abajo). El ángulo tangente es atan(m(x)·τ/σ′n)."""
import json
from pathlib import Path
import numpy as np

S0 = 1.013
# 2026-10-12: la curva adoptada es la SIMPLE (m_a = m_h = 0.85: ley de potencia de Leps 2.0); la forma compuesta queda disponible
PAR_DEF = dict(pe0=48.47, omega=20.0, m_a=0.85, m_h=0.85, s_a=4.23, s_b=7.86)


def parametros():
    p = Path(__file__).with_name("a33_curva_propuesta.json")
    return json.load(open(p, encoding="utf-8"))["parametros"] if p.exists() else dict(PAR_DEF)


def integral_m(sn, m_a, m_h, s_a, s_b):
    """∫ m(x) dx desde ln 10pa hasta ln σ′n (forma cerrada; válida para σ′n por debajo o por encima de 10pa)."""
    x = np.log(np.asarray(sn, float)); x0, xa, xb = np.log(S0), np.log(s_a), np.log(s_b)
    k = (m_h - m_a) / (xb - xa)
    def F(t):                                   # primitiva de m(x), continua, F(x0) se resta
        t = np.asarray(t, float)
        f1 = m_a * t
        f2 = m_a * t + k * (t - xa) ** 2 / 2
        f3 = m_a * xb + k * (xb - xa) ** 2 / 2 + m_h * (t - xb)
        return np.where(t <= xa, f1, np.where(t <= xb, f2, f3))
    return F(x) - F(np.full_like(x, x0))


def m_local(sn, m_a, m_h, s_a, s_b):
    x = np.log(np.asarray(sn, float)); t = np.clip((x - np.log(s_a)) / (np.log(s_b) - np.log(s_a)), 0, 1)
    return m_a + (m_h - m_a) * t


def tau(sn, e, p=None):
    p = p or parametros()
    return np.tan(np.radians(p["pe0"] - p["omega"] * np.asarray(e, float))) * S0 * np.exp(integral_m(sn, p["m_a"], p["m_h"], p["s_a"], p["s_b"]))


def phis(sn, e, p=None):
    return np.degrees(np.arctan(tau(sn, e, p) / np.asarray(sn, float)))


def tangente(sn, e, p=None):
    """φ′t y c′t (MPa) de la recta tangente: tan φ′t = m(σ)·τ/σ′n, c′t = τ − σ′n·tan φ′t."""
    p = p or parametros(); t = tau(sn, e, p); m = m_local(sn, p["m_a"], p["m_h"], p["s_a"], p["s_b"])
    tf = m * t / np.asarray(sn, float)
    return np.degrees(np.arctan(tf)), t - np.asarray(sn, float) * tf


if __name__ == "__main__":                      # control: con m_a = m_h la curva es la ley de potencia de Leps 2.0
    p = dict(PAR_DEF, m_a=0.9, m_h=0.9); s = np.array([0.1, 1, 5, 10])
    ref = np.tan(np.radians(p["pe0"] - 20 * 0.45)) * S0 ** 0.1 * s ** 0.9
    print("control ley de potencia, |Δτ| máx:", float(np.abs(tau(s, 0.45, p) - ref).max()))
    p = dict(PAR_DEF); print("compuesta, φ′s a e = 0.45:", {float(x): round(float(v), 2) for x, v in zip([1, 4.6, 7.86, 10, 15], phis([1, 4.6, 7.86, 10, 15], 0.45, p))})
