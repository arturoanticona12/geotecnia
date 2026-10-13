"""Curva de resistencia Leps 2.0 del desmonte de Antamina (documento para el EoR de botaderos, 2026-10-09).

Decisiones acordadas con el usuario:
- una sola curva para todo el desmonte ensayado (sin separar litologías), ajustada solo con ensayos de Antamina;
- sin sets con relave (relave_pct_masa_total > 0 se excluye);
- Leps 2.0 personalizado (Cylwik et al. 2025, Ec. 26): τ = tan(φ′e=0 − ω·e)·(10pa)^(1−m)·σ′n^m, con ω = 20° (Ec. 25) porque el
  rango de e de los ensayos (0.30–0.43) no permite ajustarlo; se ajustan φ′e=0 y m en tensiones principales (círculo tangente);
- tres escenarios de datos: S1 todos con ajuste de escala (pares 0.15 m / 1.0 m del mismo material), S2 solo gran escala,
  S3 todos sin distinción;
- colocación por volteo: e = 0.65 (Ec. 27 de Leps 2.0: −20°·Δe); Leps 2.0 no tiene término de tamaño (Dmax 1 m: sin ajuste);
- incertidumbre: bootstrap por sets (curva media) y, sobre la σ′n máxima ensayada, tres hipótesis de curvatura: m de Antamina,
  m = 0.9 (Leps 2.0) y la pendiente local de la base mundial a σ′n ≥ 1 MPa (mediana y percentiles 10–90 de los sets).
Salida: a9_leps2_antamina.json"""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; R = AQ.parent; sys.path.insert(0, str(R / "analisis"))
from modelos import sigma1, tau_leps2, S0  # noqa: E402
OMEGA = 20.0; E_COL = 0.45; RNG = np.random.default_rng(2026); NB = 1000

# revisión 5 (2026-10-10): triaxiales drenados (TX) y cortes directos de gran escala (DS) de Anddes (2024), de a8_ensayos_ajuste.py
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
d["set"] = d.fuente_id + "|" + d.set_id.astype(str); d["chico"] = d.Dmax_mm <= 30          # Dmax 25 mm: probetas de 6 in y caja de corte directo
d["e"] = d.e0_adoptado; d["tx"] = d.tipo == "TX"
print(f"Ajuste: {len(d)} ensayos ({int(d.tx.sum())} TX, {int((~d.tx).sum())} DS), {d.set.nunique()} sets; gran escala {int((~d.chico).sum())}, Dmax 25 mm {int(d.chico.sum())}")
# peso del corte directo: el residuo en ln τ se escala para que un grado de error en φ′ pese igual que en el triaxial (residuo en ln q)
_fx = np.arcsin((d.s1 - d.s3) / (d.s1 + d.s3))[d.tx]; _fd = np.arctan(d.tau_ds / d.sn_ds)[~d.tx]
C_DS = float(np.mean(np.cos(_fx) / (np.sin(_fx) * (1 - np.sin(_fx)))) / np.mean(1 / (np.sin(_fd) * np.cos(_fd))))
print(f"factor del residuo de corte directo: {C_DS:.3f}")


def resid(g, pe0, m, off=None):
    """Residuos: ln q (TX) y C_DS·ln τ (DS). off: desplazamiento de φ′1 (°) por ensayo (ajuste de escala)."""
    e = g.e.values - (0 if off is None else off) / OMEGA; tx = g.tx.values; r = np.empty(len(g))
    if tx.any():
        r[tx] = np.log(q_pred(g.s3.values[tx], e[tx], pe0, m)) - np.log((g.s1 - g.s3).values[tx])
    if (~tx).any():
        r[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], pe0 - OMEGA * e[~tx], m)) - np.log(g.tau_ds.values[~tx]))
    return r


def q_pred(s3, e, pe0, m):
    phi1 = pe0 - OMEGA * e
    return sigma1(tau_leps2, s3, phi1, m)[0] - s3


def ajuste(g, m_fijo=None, desp=None, mmax=1.0):
    """Mínimos cuadrados en ln q (TX) y ln τ (DS). desp: desplazamiento de φ′1 (°) por ensayo (ajuste de escala)."""
    if m_fijo is None:
        r = least_squares(lambda p: resid(g, p[0], p[1], desp), [50, 0.9], bounds=([30, 0.6], [70, mmax]))
        return r.x[0], r.x[1]
    r = least_squares(lambda p: resid(g, p[0], m_fijo, desp), [50], bounds=([30], [70]))
    return r.x[0], m_fijo


def phi_s(sn, pe0, m, e=E_COL):
    return np.degrees(np.arctan(tau_leps2(np.asarray(sn, float), pe0 - OMEGA * e, m) / np.asarray(sn, float)))


def a_tau_sn(s3, s1, m):
    D, Sm = s1 - s3, s1 + s3
    sp = D / Sm if abs(m - 1) < 1e-6 else (np.sqrt(4 * m * (m - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (m - 1) * D)
    return Sm / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


def sn_tau(g, m):
    """σ′n y τ de cada ensayo: conversión de Leps 2.0 en los TX, medidos en los DS."""
    sn, tau = g.sn_ds.values.astype(float).copy(), g.tau_ds.values.astype(float).copy(); tx = g.tx.values
    sn[tx], tau[tx] = a_tau_sn(g.s3.values[tx], g.s1.values[tx], m)
    return sn, tau


# ---- ajuste de escala con los pares del mismo material (hornfels y mármol a 0.15 m y 1.0 m)
grande = d[~d.chico & d.tx]
pares = {"Hornfels": "Hornfels", "Mármol": "Mármol"}
desp = []
for lit in pares:
    gg = grande[grande.litologia == lit]; ch = d[d.chico & d.tx & (d.litologia == lit)]
    if len(gg) == 0 or len(ch) == 0:
        continue
    pe0, m = ajuste(gg)
    for _, t in ch.iterrows():                                      # φ′e=0 que reproduce el ensayo chico con el m de su material
        r = least_squares(lambda p: np.log(q_pred(np.array([t.s3]), np.array([t.e]), p[0], m)) - np.log(t.s1 - t.s3), [pe0], bounds=([30], [75]))
        desp.append(dict(litologia=lit, ensayo=t.ensayo_id, s3=t.s3, pe0_grande=pe0, m=m, pe0_chico=r.x[0], dif=r.x[0] - pe0))
DESP = pd.DataFrame(desp); DPHI = float(DESP.dif.mean())
print("Pares de escala:\n", DESP.round(2).to_string(index=False), f"\n→ desplazamiento medio de probeta 0.15 m a 1.0 m: {-DPHI:+.2f}°")

ESC = {"S1": (d, True), "S2": (d[~d.chico], False), "S3": (d, False)}
SN = np.array([0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0])
out = dict(datos=dict(n=len(d), sets=int(d.set.nunique()), n_grande=int((~d.chico).sum()), n_chico=int(d.chico.sum()),
                      s3_max=float(d.s3.max()), e_rango=[float(d.e.min()), float(d.e.max())], n_tx=int(d.tx.sum()), n_ds=int((~d.tx).sum()), c_ds=C_DS),
           escala=dict(pares=DESP.to_dict("records"), desplazamiento=-DPHI), esc={})
for k, (g, corr) in ESC.items():
    desp_ = np.where(g.chico.values, DPHI, 0.0) if corr else None    # la probeta chica rinde DPHI más que la curva de 1 m (corregido 2026-10-09: antes −DPHI)
    pe0, m = ajuste(g, desp=desp_); pe09, _ = ajuste(g, 0.9, desp=desp_)
    m_libre = float(ajuste(g, desp=desp_, mmax=1.3)[1])
    sets = g.set.unique(); boot = []
    for _ in range(NB):
        sel = RNG.choice(sets, len(sets)); gb = pd.concat([g[g.set == s] for s in sel])
        db = np.where(gb.chico.values, DPHI, 0.0) if corr else None
        try:
            boot.append(ajuste(gb, desp=db))
        except Exception:
            pass
    B = np.array(boot); curvas = np.array([phi_s(SN, a, b) for a, b in B])
    sn_t, tau_t = sn_tau(g, m); snmax = float(sn_t.max())
    # residuos por set (φ′1 equivalente con el m ajustado)
    out["esc"][k] = dict(n=len(g), sets=len(sets), pe0=pe0, m=m, m_libre=m_libre, pe0_m09=pe09, phi1_lab=pe0 - OMEGA * float(g.e.median()),
                         phi1_col=pe0 - OMEGA * E_COL, phi1_col_m09=pe09 - OMEGA * E_COL, sn_max=snmax,
                         m_boot=[float(np.percentile(B[:, 1], q)) for q in (5, 50, 95)], pe0_boot=[float(np.percentile(B[:, 0], q)) for q in (5, 50, 95)],
                         sn=SN.tolist(), phi_med=phi_s(SN, pe0, m).tolist(), phi_m09=phi_s(SN, pe09, 0.9).tolist(),
                         phi_b05=np.percentile(curvas, 5, 0).tolist(), phi_b95=np.percentile(curvas, 95, 0).tolist())
    o = out["esc"][k]
    print(f"{k}: n {o['n']} sets {o['sets']}  φ′e=0 {pe0:.1f}° m {m:.3f} (boot 5–95: {o['m_boot'][0]:.2f}–{o['m_boot'][2]:.2f})  "
          f"φ′1 a e={E_COL} {o['phi1_col']:.1f}°  [m=0.9: φ′e=0 {pe09:.1f}°, φ′1 {o['phi1_col_m09']:.1f}°]  σ′n máx {snmax:.2f} MPa")
    print("   φ′s a e=0.65 (mediana / banda 90 %): " + "  ".join(f"{s:g}: {a:.1f} ({b:.1f}–{c:.1f})" for s, a, b, c in zip(SN, o["phi_med"], o["phi_b05"], o["phi_b95"])))

# ---- m sin cota (hasta 1.3) por subconjunto, sin ajuste de escala (para el texto; antes «1.03 sin hornfels» estaba escrito a mano)
mlib = {}
for nm, q in (("todos", d), ("sin hornfels", d[d.litologia != "Hornfels"]), ("mármol", d[d.litologia == "Mármol"]),
              ("intrusivo", d[d.litologia == "Intrusivo"]), ("hornfels", d[d.litologia == "Hornfels"])):
    mlib[nm] = float(ajuste(q, mmax=1.3)[1]); print(f"m sin cota, {nm}: {mlib[nm]:.3f} ({len(q)} ensayos)")
out["m_libre"] = mlib
# ---- curvatura a alta tensión en la base mundial (pendiente local por set con σ′n ≥ 1 MPa)
from lepsp_r6 import datos  # noqa: E402
W = datos(); W = W[~W.cens] if "cens" in W else W
fil = []
for s, g in W.groupby("Set"):
    g = g[g.sn >= 1.0]
    if len(g) >= 3 and g.sn.max() / g.sn.min() >= 2:
        fil.append(dict(set=s, m=float(np.polyfit(g.x, g.y, 1)[0]), sn_max=float(g.sn.max())))
M = pd.DataFrame(fil); out["mundial"] = dict(n_sets=len(M), m_p10=float(M.m.quantile(0.1)), m_p50=float(M.m.median()), m_p90=float(M.m.quantile(0.9)))
print(f"Base mundial, pendiente local a σ′n ≥ 1 MPa: {len(M)} sets, m P10 {out['mundial']['m_p10']:.3f}, P50 {out['mundial']['m_p50']:.3f}, P90 {out['mundial']['m_p90']:.3f}")
# control de regresión: solo TX debe reproducir la revisión 4 (φ′e=0 = 48.71° con m = 0.9, sin ajuste de escala)
_pe_tx = ajuste(d[d.tx], 0.9)[0]; out["control_solo_tx_pe0_m09"] = _pe_tx
print(f"CONTROL solo TX, m = 0.9: φ′e=0 {_pe_tx:.3f}° (revisión 4: 48.71°)")
out["solo_ds_pe0_m09"] = ajuste(d[~d.tx], 0.9)[0]; print(f"solo DS, m = 0.9: φ′e=0 {out['solo_ds_pe0_m09']:.3f}°")
json.dump(out, open(AQ / "a9_leps2_antamina.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=float)
print("escrito a9_leps2_antamina.json")
