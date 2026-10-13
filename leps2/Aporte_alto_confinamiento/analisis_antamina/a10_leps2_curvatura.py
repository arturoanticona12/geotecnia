"""Curva Leps 2.0 de Antamina: nivel anclado a los ensayos y curvatura por hipótesis (alto confinamiento).
Para cada m fijo (1.00 Antamina; 0.93 P90, 0.845 P50 y 0.79 P10 de la pendiente local mundial a σ′n ≥ 1 MPa; 0.90 Leps 2.0)
se ajusta φ′e=0 con los 22 ensayos sin relave (escenario S1, probetas de 6 in con el ajuste de escala de a9) y se calcula φ′s a
e = 0.65 con su banda de bootstrap por sets (90 %). También guarda los puntos de ensayo llevados a e = 0.65 (−20°·Δe, Ec. 27)
para las figuras. Lee a9_leps2_antamina.json; escribe a10_leps2_curvatura.json y a10_puntos.csv."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
import a9_leps2_antamina as A  # noqa: E402  (reejecuta a9: datos, ajuste y escala; ~5 min)

R9 = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8")); W = R9["mundial"]
g = A.d.copy(); DESP = None                 # escenario S3: sin ajuste de escala (revisión EoR/Stantec, 2026-10-09)
# revisión 7: m de la base mundial de Leps 2.0 (a18: 170 sets, rango completo); la linealidad de Antamina no se usa para la curvatura
R18 = json.load(open(AQ / "a18_m_jerarquico.json", encoding="utf-8"))["variantes"]["rango completo"]
KC = "Curva propuesta (mediana mundial)"
MS = {"Mundial P90": R18["m_P90_sets"], KC: R18["m_P50_sets"], "Mundial P10": R18["m_P10_sets"]}
SN = np.unique(np.round(np.r_[np.geomspace(0.1, 15.0, 31), 8.0, 10.0, 12.0], 3)); sets = g.set.unique(); rng = np.random.default_rng(9)   # SN hasta 15 MPa (sobre 7.9 MPa: extrapolación)
out = dict(sn=SN.tolist(), e_col=A.E_COL, curvas={}, sn_max_ensayos=R9["esc"]["S1"]["sn_max"])
for nm, m in MS.items():
    pe0, _ = A.ajuste(g, m, desp=DESP); boot = []
    for _ in range(600):
        sel = rng.choice(sets, len(sets)); gb = pd.concat([g[g.set == s] for s in sel])
        boot.append(A.ajuste(gb, m)[0])
    b = np.array(boot)
    out["curvas"][nm] = dict(m=m, pe0=pe0, pe0_b=[float(np.percentile(b, 5)), float(np.percentile(b, 95))], phi1_col=pe0 - A.OMEGA * A.E_COL,
                             phi=A.phi_s(SN, pe0, m).tolist(), phi_b05=A.phi_s(SN, np.percentile(b, 5), m).tolist(), phi_b95=A.phi_s(SN, np.percentile(b, 95), m).tolist())
    c = out["curvas"][nm]
    print(f"{nm:22s} m {m:.3f}  φ′e=0 {pe0:.2f}° (90 %: {c['pe0_b'][0]:.2f}–{c['pe0_b'][1]:.2f})  φ′1(e=0.65) {c['phi1_col']:.1f}°  "
          + "  ".join(f"{s:g} MPa {A.phi_s([s], pe0, m)[0]:.1f}°" for s in (1, 2, 3, 5, 8)))
# puntos de ensayo a e = 0.65 (conversión con m = 0.9, Ecs. 13–16)
sn_t, tau_t = A.sn_tau(g, MS[KC])                 # TX: conversión de Leps 2.0; DS: σ′n y τ medidos (revisión 5)
P = pd.DataFrame(dict(set=g.set.values, litologia=g.litologia.values, escala=g.escala.values, tipo=g.tipo.values, s3=g.s3.values, e=g.e.values, sn=sn_t,
                      phis=np.degrees(np.arctan(tau_t / sn_t)), eps_a=g.eps_axial_falla_pct.values))
P["phis_e065"] = P.phis - A.OMEGA * (A.E_COL - P.e)
P.to_csv(AQ / "a10_puntos.csv", index=False)
json.dump(out, open(AQ / "a10_leps2_curvatura.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(P.round(2).to_string(index=False))
