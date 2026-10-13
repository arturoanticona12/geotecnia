"""Relación de vacíos del desmonte con la profundidad y curvas Leps 2.0 de Antamina (opción 2, m = 0.90) para:
  (1) e constante = 0.45, 0.55, 0.65;
  (2) perfil e(z) con densificación desde e = 0.65 en superficie, con dos leyes que acotan el rango:
      A — compresibilidad del edómetro de Antamina más suelto (mármol, Golder, e0 = 0.455): Cc = 0.134 entre 0.05 y 1 MPa
          y 0.056 sobre 1 MPa (pendientes medidas en edometros.csv; la de 1–5 MPa se extrapola);
      V — forma de la curva de diseño de Valenzuela et al. (2008) (Hawley y Cunning 2017, Fig. 5.6, p. PDF 108), leída a mano
          (γd vs. altura; e con Gs = 2.75, el que hace coincidir sus dos ejes), desplazada para partir de e = 0.65.
  La envolvente con densificación usa e(σ′v) con σ′v = σ′n: en la base de una dovela σ′n ≤ σ′v, así que asignar a cada σ′n la e
  de una profundidad menor (más suelta) es del lado prudente.
Escribe a13_perfil_e.json."""
import sys, json, math
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent
OP2 = dict(json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8"))["parametros"]); OP2["m"] = OP2["m_a"]   # revisión 10: curva simple
PE0, M, OM, S0, GS, W, GW = OP2["pe0"], OP2["m"], 20.0, 1.013, 2.75, 0.05, 9.81
E_TOP, SA = 0.45, 0.05   # e base en superficie (γ del DDE, 2026-10-10; antes 0.65)
# Valenzuela et al. (2008), curva de diseño (línea segmentada), γd (t/m³) vs. altura (m); lectura manual ±0.02 t/m³
HV = np.array([0, 40, 80, 120, 160, 200, 240, 280, 320, 360, 400, 440, 480, 520, 560, 600], float)
GDV = np.array([1.84, 1.90, 1.95, 2.00, 2.05, 2.10, 2.14, 2.18, 2.21, 2.24, 2.27, 2.30, 2.32, 2.34, 2.355, 2.37])
EV = GS / GDV - 1.0


# Cc de la rama de carga monótona del edómetro Golder Test 1 (mármol, probeta de 0.24 m, e0 = 0.455 con Gs = 2.70 supuesto),
# sin los ciclos de descarga y recarga (corregido 2026-10-09: antes se mezclaban y salían 0.134 y 0.056)
import pandas as pd  # noqa: E402
_ED = pd.read_csv(AQ.parent / "datos_antamina" / "base" / "edometros.csv")
_G = _ED[_ED.ensayo_id.str.startswith("MN-edo-0.24m")].reset_index(drop=True)
_G = _G.iloc[: int(np.argmax(np.diff(_G.sigma_v_kPa.values) < 0)) + 1]   # rama de carga monótona: hasta la primera descarga
_cc = lambda lo, hi: float(-np.polyfit(np.log10(_G[(_G.sigma_v_kPa >= lo) & (_G.sigma_v_kPa <= hi)].sigma_v_kPa),
                                      _G[(_G.sigma_v_kPa >= lo) & (_G.sigma_v_kPa <= hi)].e, 1)[0])
CC1, CC2 = _cc(200, 800), _cc(1200, 4800)                         # 0.2–0.8 MPa y 1.2–4.8 MPa


def e_A(sv):
    sv = np.maximum(np.asarray(sv, float), SA)
    return np.where(sv <= 1.0, E_TOP - CC1 * np.log10(sv / SA), E_TOP - CC1 * np.log10(1.0 / SA) - CC2 * np.log10(sv / 1.0))


gam = lambda e: GS * GW * (1 + W) / (1 + e) / 1000.0           # MN/m³
# perfil con la profundidad (integración de σ′v = ∫γ dz, desmonte seco)
z = np.linspace(0, 700, 1401); sv_A = np.zeros_like(z); eA = np.zeros_like(z); eA[0] = E_TOP
for i in range(1, len(z)):
    sv_A[i] = sv_A[i - 1] + gam(eA[i - 1]) * (z[i] - z[i - 1]); eA[i] = float(e_A(sv_A[i]))
eVz = E_TOP + (np.interp(z, HV, EV, right=np.nan) - EV[0])
sv_V = np.concatenate([[0], np.cumsum(gam(np.nan_to_num(eVz[:-1], nan=eVz[np.isfinite(eVz)][-1])) * np.diff(z))])
eV_of_sv = lambda sv: np.interp(sv, sv_V[np.isfinite(eVz)], eVz[np.isfinite(eVz)], right=np.nan)   # sin dato sobre el σ′v de 600 m (fin de la curva)
phis = lambda sn, e: np.degrees(np.arctan(np.tan(np.radians(PE0 - OM * np.asarray(e))) * S0 ** (1 - M) * np.asarray(sn) ** M / np.asarray(sn)))
SN = np.array([0.05, 0.1, 0.2, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15])
out = dict(Cc1=CC1, Cc2=CC2, pe0=PE0, m=M, e_top=E_TOP, z=z[::20].tolist(), sv_A=sv_A[::20].tolist(), e_A=eA[::20].tolist(), sv_V=sv_V[::20].tolist(),
           e_V=[None if not np.isfinite(v) else float(v) for v in eVz[::20]], sn=SN.tolist(), curvas={})
for e in (0.45, 0.55, 0.65):
    out["curvas"][f"e = {e:.2f}"] = dict(phi=phis(SN, e).tolist(), phi1=PE0 - OM * e)
out["curvas"]["Perfil A (edómetro Antamina)"] = dict(phi=phis(SN, e_A(SN)).tolist(), e=e_A(SN).tolist())
out["curvas"]["Perfil V (Valenzuela et al. 2008)"] = dict(phi=phis(SN, eV_of_sv(SN)).tolist(), e=eV_of_sv(SN).tolist())
for zz in (0, 100, 200, 300, 400, 500, 600, 700):
    j = int(np.argmin(np.abs(z - zz)))
    print(f"z {zz:3d} m: perfil A σ′v {sv_A[j]:5.2f} MPa e {eA[j]:.3f} | perfil V σ′v {sv_V[j]:5.2f} MPa e {eVz[j]:.3f}")
for k, v in out["curvas"].items():
    print(f"{k:34s} " + "  ".join(f"{s:g}: {p:.1f}" for s, p in zip(SN, v["phi"])))
SF = np.geomspace(0.1, 15, 90); out["sn_fino"] = SF.tolist()
out["fino"] = {f"e = {e:.2f}": phis(SF, e).tolist() for e in (0.45, 0.55, 0.65)}
out["fino"]["Perfil A (edómetro Antamina)"] = phis(SF, e_A(SF)).tolist(); out["fino"]["Perfil V (Valenzuela et al. 2008)"] = phis(SF, eV_of_sv(SF)).tolist()
json.dump(out, open(AQ / "a13_perfil_e.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
