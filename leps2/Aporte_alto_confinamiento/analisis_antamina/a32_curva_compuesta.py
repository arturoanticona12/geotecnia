"""Curva compuesta (pregunta de WA, 2026-10-12: «por ser fieles a grandes esfuerzos, ¿dejamos de lado los pequeños? se me ocurre una
curva compuesta»). Con las e0 del D854 de Golder (2010) (a8) y ω = 20°:
  (a) m = 0.85 en todo el rango (la que predice sin sesgo los ensayos mundiales sobre 4.60 MPa; a31);
  (b) m de Antamina (ajuste con nivel por set), en todo el rango;
  (c) compuesta: la m de Antamina hasta σt = 4.60 MPa (máximo de sus ensayos) y exponente local 0.85 sobre σt, continua en τ;
  (d) compuesta suave: el exponente local pasa de m_A a 0.85 linealmente en ln σ′n entre 4.60 y 7.86 MPa (máximo de la base mundial).
Para cada una: nivel φ′e0 (φ′1 por set con su m y φ′e0 = media de φ′1 + 20·e0), residuos de φ′s de los ensayos de Antamina por
rango de σ′n (medido − curva, a la e0 de cada ensayo), φ′s y ángulo tangente a e = 0.45 a varios σ′n. Escribe a32_curva_compuesta.json."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from modelos import sigma1, tau_leps2  # noqa: E402
S0, EB, OM, MH, ST, SW = 1.013, 0.45, 20.0, 0.85, 4.60, 7.86
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]
A = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
A["set"] = A.fuente_id + "|" + A.set_id.astype(str); A["e"] = A.e0_adoptado; A["tx"] = A.tipo == "TX"
SA = list(dict.fromkeys(A.set)); E_SET = np.array([A[A.set == s].e.mean() for s in SA])


def res_set(g, phi1, m):
    tx = g.tx.values; r = np.empty(len(g))
    if tx.any():
        s3 = g.s3.values[tx]; r[tx] = np.log(sigma1(tau_leps2, s3, phi1, m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
    if (~tx).any():
        r[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], phi1, m)) - np.log(g.tau_ds.values[~tx]))
    return r


def ajuste(m=None):
    """m común (libre si None) y φ′1 por set, solo Antamina."""
    ga = [A[A.set == s] for s in SA]
    def r(p):
        mm = p[0] if m is None else m; ph = p[1:] if m is None else p
        return np.concatenate([res_set(g, ph[i], mm) for i, g in enumerate(ga)])
    p0 = ([0.9] if m is None else []) + [40.0] * len(ga)
    lo = ([0.5] if m is None else []) + [15.0] * len(ga); hi = ([1.0] if m is None else []) + [70.0] * len(ga)
    x = least_squares(r, p0, bounds=(lo, hi)).x
    return (x[0], x[1:]) if m is None else (m, x)


def a_tau_sn(s3, s1, m):
    D, Sm = s1 - s3, s1 + s3
    sp = D / Sm if abs(m - 1) < 1e-6 else (np.sqrt(4 * m * (m - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (m - 1) * D)
    return Sm / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


def m_local(s, mA, tipo):
    if tipo == "un tramo":
        return np.full_like(np.asarray(s, float), mA)
    if tipo == "compuesta":
        return np.where(np.asarray(s) <= ST, mA, MH)
    t = np.clip((np.log(s) - np.log(ST)) / (np.log(SW) - np.log(ST)), 0, 1)       # suave
    return mA + (MH - mA) * t


def tau_curva(s, pe0, e, mA, tipo):
    """τ con exponente local m(σ): ln τ = ln τ(10pa) + ∫ m d ln σ (integral numérica en ln σ)."""
    s = np.atleast_1d(np.asarray(s, float)); out = np.empty_like(s)
    for i, x in enumerate(s):
        g = np.linspace(np.log(S0), np.log(x), 400); mm = m_local(np.exp(g), mA, tipo)
        out[i] = np.tan(np.radians(pe0 - OM * e)) * S0 * np.exp(np.trapz(mm, g))
    return out


mA, phA = ajuste(None); _, ph85 = ajuste(MH)
pe0A = float(np.mean(phA + OM * E_SET)); pe085 = float(np.mean(ph85 + OM * E_SET))
print(f"m de Antamina (nivel por set, e0 con D854): {mA:.3f} | φ′e0 {pe0A:.2f}° | con m = 0.85: φ′e0 {pe085:.2f}°")
CURVAS = {"(a) m = 0.85 en todo el rango": (pe085, MH, "un tramo"), f"(b) m de Antamina ({mA:.3f}) en todo el rango": (pe0A, mA, "un tramo"),
          f"(c) compuesta: {mA:.3f} hasta 4.60 MPa, 0.85 sobre": (pe0A, mA, "compuesta"), f"(d) compuesta suave (4.60–7.86 MPa)": (pe0A, mA, "suave")}
BINS = [(0, 0.5), (0.5, 2.0), (2.0, ST + 0.01)]
out = {"m_antamina": mA, "pe0_antamina": pe0A, "pe0_m085": pe085, "curvas": {}}
print("\nResiduo φ′s medido − curva (°) por rango de σ′n (media; n) | φ′s a e = 0.45: 1 / 4.6 / 7.86 / 10 / 15 MPa | ángulo tangente a 4.6 y 10 MPa")
for nm, (pe0, mm, tipo) in CURVAS.items():
    mconv = mm                                                     # conversión de los triaxiales con la m de la curva en su rango
    sn = A.sn_ds.values.copy(); tau = A.tau_ds.values.copy(); tx = A.tx.values
    sn[tx], tau[tx] = a_tau_sn(A.s3.values[tx], A.s1.values[tx], mconv)
    pred = np.array([tau_curva(s, pe0, e, mm, tipo)[0] for s, e in zip(sn, A.e.values)])
    d = np.degrees(np.arctan(tau / sn)) - np.degrees(np.arctan(pred / sn))
    bins = {f"{a}–{b:.1f}": (float(d[(sn > a) & (sn <= b)].mean()), int(((sn > a) & (sn <= b)).sum())) for a, b in BINS}
    S = np.array([1, 4.6, 7.86, 10, 15]); tq = tau_curva(S, pe0, EB, mm, tipo); phs = np.degrees(np.arctan(tq / S))
    tang = {s: float(np.degrees(np.arctan(m_local(s * 1.0001, mm, tipo) * tau_curva(s, pe0, EB, mm, tipo)[0] / s))) for s in (4.6, 10)}
    out["curvas"][nm] = dict(pe0=pe0, m=mm, tipo=tipo, residuo_por_rango=bins, phis=dict(zip(S.tolist(), phs.tolist())), tangente=tang)
    print(f"{nm:46s} " + " | ".join(f"{k}: {v[0]:+.1f} ({v[1]})" for k, v in bins.items()) + "  ||  "
          + " ".join(f"{x:5.1f}" for x in phs) + f"  || tang {tang[4.6]:.1f} / {tang[10]:.1f}")
json.dump(out, open(AQ / "a32_curva_compuesta.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
