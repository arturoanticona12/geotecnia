"""Leps-P aplicado al desmonte del yacimiento de skarn (ronda 2).
- Sets de gran escala sin relave, cada uno con su Dmax y e; un solo laboratorio → efecto de laboratorio común
  (lepsp.actualizar_sitio). Sets en conflicto con la previa no informan la actualización (se reportan).
- Densidad de campo: escenarios e = e_lab (probetas) y e = 0.55, 0.65 (desmonte vertido), vía βe.
- Escala a campo (dmax 1 m) con supuestos 'general' y 'paralela'; restricción de pendiente solo en el rango calibrado.
- Caliza y marga sin ensayos por separado; la marga con un escenario de degradación (Δe = +0.15).
- Envolvente media del botadero con pesos ilustrativos y tres supuestos de correlación.
Escribe lepsp_sitio2.json y lepsp_sitio2_muestras.npz."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent; sys.path.insert(0, str(RAIZ / "leps3"))
import lepsp as L  # noqa: E402

d = pd.read_csv(AQUI / "drenados_utilizables.csv", low_memory=False)
g = d[d.escala.isin(["0.6 m", "1.0 m"]) & (d.relave_pct_masa_total.fillna(0) == 0)].copy()
g["e_use"] = g.e0_adoptado.fillna(g.e0)
LIT = {"Mármol": ("Metamorphic carbonate", "baja"), "Hornfels": ("Hornfels", "moderada"), "Intrusivo": ("Intrusive", "baja")}
SENS = "--marmol-buena" in sys.argv                                   # sensibilidad: mármol en clase «buena» (roca calcárea de cantera)
if SENS:
    LIT["Mármol"] = ("Metamorphic carbonate", "buena")
SUF = "_marmol_buena" if SENS else ""
BETA_E = dict(zip(L._P["formas"]["x2"]["nombres"], L._P["formas"]["x2"]["beta"]))["e"]
# ---- 1) actualización conjunta, primero con todos los sets para obtener el diagnóstico de conflicto
sets, meta = [], []
for sid, gs in g.groupby("set_a"):
    lit = gs.litologia.iloc[0]
    sets.append(dict(calidad=LIT[lit][1], e=float(gs.e_use.iloc[0]), s3=gs.s3.values, s1=gs.s1.values, usar=True))
    meta.append(dict(set=sid, lit=lit, n=len(gs), dmax=float(gs.Dmax_mm.iloc[0]), e=float(gs.e_use.iloc[0])))
_, dg0 = L.actualizar_sitio(sets, n=4000, seed=1)
for s, dg_, mt in zip(sets, dg0, meta):
    s["usar"] = dg_["p_conflicto"] >= 0.05; mt.update(p_conflicto=dg_["p_conflicto"], razon=dg_["rango_sn"], sn_max=dg_["sn_max"], usado=s["usar"])
    print(f"  {mt['set']:38s} {mt['lit']:10s} n={mt['n']} Dmax={mt['dmax']:5.1f} e={mt['e']:.3f} razón σ′n={dg_['rango_sn']:.2f} p={dg_['p_conflicto']:.4f} → {'usado' if s['usar'] else 'NO usado (conflicto)'}")
E_LAB_REF = float(np.median([m_["e"] for m_ in meta]))
NUEVOS = [("baja", E_LAB_REF), ("baja", E_LAB_REF)]                 # caliza, marga (a e de referencia del laboratorio)
N = 60000
mats, dg = L.actualizar_sitio(sets, NUEVOS, n=N, seed=11)
# ---- 2) agrupar por litología: media de τ de sus sets (si hay varios); Dmax de laboratorio = media geométrica de sus sets
SNG = np.logspace(np.log10(0.05), np.log10(20), 60); XG = np.log(SNG / L.S0)
grupos = {}
for i, mt in enumerate(meta):
    grupos.setdefault(LIT[mt["lit"]][0], []).append(i)
grupos["Limestone (untested)"] = [len(sets)]; grupos["Marl (untested)"] = [len(sets) + 1]
DLAB = {k: float(np.exp(np.mean([np.log(meta[i]["dmax"]) for i in v]))) if v[0] < len(sets) else float(np.exp(np.mean([np.log(m_["dmax"]) for m_ in meta])))
        for k, v in grupos.items()}
ELAB = {k: float(np.mean([meta[i]["e"] for i in v])) if v[0] < len(sets) else E_LAB_REF for k, v in grupos.items()}
OUT = dict(sets=meta, e_lab_ref=E_LAB_REF, dlab=DLAB, elab=ELAB, sn=SNG.tolist(), escenarios={})
mats_r, ret = L.restringir_conjunto_rango(mats); OUT["retencion_restriccion"] = ret
print("fracción conservada por la restricción (σ′n ≤ 7.9 MPa):", np.round(ret["por_material"], 3), "conjunta", round(ret["conjunta"], 3))
PESO = {"Metamorphic carbonate": 0.35, "Hornfels": 0.25, "Intrusive": 0.20, "Limestone (untested)": 0.10, "Marl (untested)": 0.10}


def tau_lit(ms, k, e_campo, supuesto, bD, degr=0.0):
    """τ(σ′n) por muestra para la litología k a escala de campo y densidad e_campo."""
    t = 0
    for i in grupos[k]:
        mt = ms[i]; de = (e_campo - ELAB[k] if e_campo is not None else 0.0) + degr
        th = mt.th + BETA_E * de + bD * np.log(1000.0 / DLAB[k])
        t = t + L.S0 * np.exp(th[:, None] + mt.m[:, None] * XG + mt.c2[:, None] * XG ** 2)
    return t / len(grupos[k])


phi = lambda t: np.degrees(np.arctan(t / SNG[None, :]))
nsel = len(mats_r[0].th)
for esc_e in (None, 0.55, 0.65):
    for sup in ("general", "paralela", "ninguno"):
        if sup == "ninguno" and esc_e is not None:
            continue
        bD = np.zeros(nsel) if sup == "ninguno" else L.muestras_bD(nsel, sup, seed=5)
        T = {k: tau_lit(mats_r, k, esc_e, sup, bD, degr=0.15 if (k.startswith("Marl") and esc_e is not None) else 0.0) for k in grupos}
        w = np.array([PESO[k] for k in T]); tt = np.array(list(T.values()))
        prom = np.tensordot(w, tt, 1); comon = np.tensordot(w, np.sort(tt, axis=1), 1)
        debil_ens = min([k for k in T if "untested" not in k], key=lambda k: np.median(phi(T[k])[:, -1]))
        debil = min(T, key=lambda k: np.median(phi(T[k])[:, -1]))
        clave = f"e={'lab' if esc_e is None else esc_e}|{sup}"
        OUT["escenarios"][clave] = dict(
            litologias={k: {f"P{q:02d}": np.percentile(phi(v), q, 0).tolist() for q in (5, 10, 50)} for k, v in T.items()},
            botadero={nm: {f"P{q:02d}": np.percentile(phi(v), q, 0).tolist() for q in (5, 10, 50)} for nm, v in
                      [("model", prom), ("comonotonic", comon), (f"weakest tested ({debil_ens})", T[debil_ens]), (f"weakest ({debil})", T[debil])]})
        if esc_e in (None, 0.65) and sup == "general" and not SENS:
            np.savez_compressed(AQUI / f"lepsp_sitio2_muestras_{'lab' if esc_e is None else 'e065'}.npz", tau=tt, pesos=w, sn=SNG, nombres=np.array(list(T)))
        i15 = -1; i3 = int(np.argmin(np.abs(SNG - 3)))
        b = OUT["escenarios"][clave]["botadero"]
        print(f"\n[{clave}]  botadero P50/P05 a 3 y 20 MPa: " + "; ".join(f"{nm}: {v['P50'][i3]:.1f}/{v['P05'][i3]:.1f}, {v['P50'][i15]:.1f}/{v['P05'][i15]:.1f}" for nm, v in b.items()))
# puntos de ensayo del sitio (σ′n, φ′s) convertidos con m = 0.86, para las figuras
OUT["ensayos"] = []
for s, mt in zip(sets, meta):
    sn_, tau_ = L._a_sn_tau(np.asarray(s["s3"]), np.asarray(s["s1"]), 0.86)
    OUT["ensayos"].append(dict(lit=LIT[mt["lit"]][0], set=mt["set"], usado=mt["usado"], sn=sn_.tolist(), phis=np.degrees(np.arctan(tau_ / sn_)).tolist()))
json.dump(OUT, open(AQUI / f"lepsp_sitio2{SUF}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0, default=float)
print("\nescrito lepsp_sitio2.json")
