"""Opción 2 de la curva única de Antamina y curva de zona del mármol (revisión 3, 2026-10-09, sin ajuste de escala).
Opción 2 = composición LE2 (cinco litologías):
  - litologías ensayadas (mármol 39 %, hornfels 19 %, intrusivo 15 %): Leps 2.0 ajustado a sus ensayos por mínimos cuadrados
    ponderados (cada ensayo pesa w_lit / n_lit; la mezcla de 6 in no entra);
  - margas y caliza (19 % + 8 % = 27 %, sin ensayos): como máximo la resistencia del mármol ajustado, la litología ensayada más
    débil (revisión 3, pedido del EoR: antes la clase baja de Leps 2.0, 47°, quedaba sobre el mármol); valor central = mármol;
  - promedio de resistencia (τ) con los pesos LE2 a la e de colocación, expresado como un φ′e=0 equivalente (mismo m y ω).
Incertidumbre, para cada hipótesis de curvatura de a10 (m fijo), con bootstrap por sets estratificado por litología (600 réplicas):
  - «curva media»: nivel (bootstrap, ω = 20°, e = 0.65) y margas y caliza entre el mármol y una clase Leps 2.0 menos
    (φ′e=0 del mármol − U(0, 3°));
  - «total»: además ω ~ U(15°, 25°) (reajuste con ese ω) y e de colocación ~ U(0.55, 0.75).
Curva de mármol: ajuste solo con los ensayos de mármol (2 sets), con su banda de bootstrap.
Lee a10_leps2_curvatura.json; escribe a12_leps2_ponderada.json."""
import sys, json, math, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from modelos import sigma1, tau_leps2  # noqa: E402
OMEGA, EC, S0 = 20.0, 0.45, 1.013   # e base 0.45 (γ del DDE, 2026-10-10; antes 0.65)
# revisión del 2026-10-12 (comentarios de WA; decisión «opción B»): la curva propuesta se ajusta con todos los ensayos con igual
# peso, sin composición por litología ni margas y caliza, y sin zonificación (el DDE trata el desmonte ROM como un solo material).
# Control: la producción por litología desde 2021 del DDE (IFF-115-G-0001_B, Tabla 3-1: intrusivo y exoskarn 44 %, hornfels y
# mármol 56 %, este repartido por igual) se guarda en pe0_dde. Antes: LE2 del modelo de bloques (mármol 39, hornfels 19,
# intrusivo 15, margas y caliza 27 % con la resistencia del mármol), que dejaba la curva bajo las cotas de Indraratna y de
# Hawley y Cunning a grandes esfuerzos.
WT = {"Intrusivo": 0.44, "Hornfels": 0.28, "Mármol": 0.28}; W_SIN = 0.0; PE0_BAJA = 47.0; DCLASE = 0.0
PESAR = False                       # opción B: sin ponderación por litología
OM_R, E_R, NB = (15.0, 25.0), (0.35, 0.55), 600   # e base ± 0.10
# revisión 5 (2026-10-10): triaxiales (TX) y cortes directos de gran escala (DS), de a8_ensayos_ajuste.py; mismo residuo que a9
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
d = d.copy()                         # 2026-10-12 (WA): las dos mezclas entran en la curva (desmonte como un solo material)
d["set"] = d.fuente_id + "|" + d.set_id.astype(str); d["e"] = d.e0_adoptado; d["tx"] = d.tipo == "TX"
dL = d[d.litologia.isin(WT)]         # control con la composición del DDE: solo las litologías con peso
C = json.load(open(AQ / "a10_leps2_curvatura.json", encoding="utf-8"))
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]


def resid(g, pe0, m, om):
    e = g.e.values; tx = g.tx.values; r = np.empty(len(g))
    if tx.any():
        s3 = g.s3.values[tx]; r[tx] = np.log(sigma1(tau_leps2, s3, pe0 - om * e[tx], m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
    if (~tx).any():
        r[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], pe0 - om * e[~tx], m)) - np.log(g.tau_ds.values[~tx]))
    return r


def ajuste(g, m, pesar=True, om=OMEGA):
    w = np.sqrt((g.litologia.map(WT) / g.litologia.map(g.litologia.value_counts())).values * len(g) / sum(WT.values())) if pesar else 1.0
    r = least_squares(lambda p: w * resid(g, p[0], m, om), [49], bounds=([30], [70]))
    return float(r.x[0])


def tan_mezcla(pe0_t, pe0_s, e=EC, om=OMEGA):
    """tan φ′1 del promedio de τ a la e dada: ensayadas (73 %) con pe0_t y margas+caliza (27 %) con pe0_s."""
    wt = sum(WT.values())
    return (wt * np.tan(np.radians(pe0_t - om * e)) + W_SIN * np.tan(np.radians(pe0_s - om * e))) / (wt + W_SIN)


mezcla = lambda pe0_t, pe0_s, e=EC, om=OMEGA: float(np.degrees(np.arctan(tan_mezcla(pe0_t, pe0_s, e, om)))) + om * e
phis = lambda sn, pe0, m, e=EC, om=OMEGA: np.degrees(np.arctan(np.tan(np.radians(pe0 - om * e)) * (np.asarray(sn, float) / S0) ** (m - 1)))
SN = np.array(C["sn"]); SNF = np.unique(np.round(np.concatenate([[0.01, 0.02, 0.03, 0.05], SN, [0.5, 1, 1.5, 2, 3, 4, 4.48, 4.6, 5, 6, 8, 10, 12, 15]]), 3))
rng = np.random.default_rng(12)
out = dict(curvas={}, marmol={}, n=len(d), sn_fino=SNF.tolist(), dclase=DCLASE, omega_rango=OM_R, e_rango=E_R,
           pesos_LE2=dict(WT, **{"Margas y caliza (resistencia del mármol)": W_SIN}))
por_lit = {l: g.set.unique() for l, g in d.groupby("litologia")}
mm = d[d.litologia == "Mármol"]
for nm, v in C["curvas"].items():
    m = v["m"]; pt = ajuste(d, m, pesar=PESAR); pdde = ajuste(dL, m, pesar=True); pmar = ajuste(mm, m, pesar=False)
    ps = min(PE0_BAJA, pmar); pe0 = mezcla(pt, ps)
    bm, bt = [], []
    for _ in range(NB):
        sel = [s for ss in por_lit.values() for s in rng.choice(ss, len(ss))]; gb = pd.concat([d[d.set == s] for s in sel])
        gm = gb[gb.litologia == "Mármol"]; u = rng.uniform(0, DCLASE)
        bm.append(mezcla(ajuste(gb, m, pesar=PESAR), min(PE0_BAJA, ajuste(gm, m, pesar=False)) - u))
        om = rng.uniform(*OM_R); ec = rng.uniform(*E_R)
        t1 = tan_mezcla(ajuste(gb, m, pesar=PESAR, om=om), min(PE0_BAJA, ajuste(gm, m, pesar=False, om=om)) - u, ec, om)
        bt.append(np.degrees(np.arctan(t1 * (SNF / S0) ** (m - 1))))
    bm, bt = np.array(bm), np.array(bt)
    out["curvas"][nm] = dict(m=m, pe0=pe0, pe0_ensayadas=pt, pe0_dde=pdde, pe0_marmol=pmar, pe0_sin=ps,
                             pe0_b=[float(np.percentile(bm, 5)), float(np.percentile(bm, 95))], sd_pe0=float(bm.std(ddof=1)),
                             phi1_col=pe0 - OMEGA * EC, phi=phis(SN, pe0, m).tolist(),
                             phi_b05=phis(SN, np.percentile(bm, 5), m).tolist(), phi_b95=phis(SN, np.percentile(bm, 95), m).tolist(),
                             phi_t05=np.percentile(bt, 5, axis=0).tolist(), phi_t95=np.percentile(bt, 95, axis=0).tolist(),
                             sd_phi1_total=float(np.std(bt[:, int(np.argmin(np.abs(SNF - S0)))], ddof=1)))
    c = out["curvas"][nm]
    print(f"{nm:22s} m {m:.3f}  todos igual {pt:.2f}°  [control DDE 44/56: {pdde:.2f}°]  mármol {pmar:.2f}°  → curva {pe0:.2f}° (90 %: {c['pe0_b'][0]:.2f}–{c['pe0_b'][1]:.2f}, "
          f"σ {c['sd_pe0']:.2f})  φ′1(0.65) {c['phi1_col']:.2f}°  σ φ′1 total {c['sd_phi1_total']:.2f}°  [opción 1: {v['phi1_col']:.2f}°]")
sets_m = mm.set.unique()
for m in (C["curvas"]["Curva propuesta (mediana mundial)"]["m"],):
    pe0 = ajuste(mm, m, pesar=False)
    b = np.array([ajuste(pd.concat([mm[mm.set == s] for s in rng.choice(sets_m, len(sets_m))]), m, pesar=False) for _ in range(200)])
    out["marmol"]["central"] = dict(m=m, pe0=pe0, phi1_col=pe0 - OMEGA * EC, phi=phis(SN, pe0, m).tolist(), n=len(mm), sets=int(mm.set.nunique()),
                                     pe0_b=[float(np.percentile(b, 5)), float(np.percentile(b, 95))])
    print(f"Mármol solo, m {m:.3f}: φ′e=0 {pe0:.2f}° (90 %: {np.percentile(b, 5):.2f}–{np.percentile(b, 95):.2f})  φ′1(e=0.65) {pe0 - OMEGA * EC:.2f}°  "
          f"({len(mm)} ensayos, {mm.set.nunique()} sets)")
json.dump(out, open(AQ / "a12_leps2_ponderada.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("escrito a12_leps2_ponderada.json")
