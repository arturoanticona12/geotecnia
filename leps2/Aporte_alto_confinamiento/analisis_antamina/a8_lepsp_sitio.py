"""Leps-P aplicado al desmonte del sitio (ronda 4), forma central «acotada» (efectos en η y ζ); sensibilidad «x2».
- Sets de gran escala sin relave; un solo laboratorio → efecto de laboratorio común (lepsp.actualizar_sitio).
- Diagnóstico de conflicto en una primera pasada; los sets en conflicto no informan la actualización.
- Un material por tipo de roca: promedio de los sets usados; si ninguno pasó el diagnóstico, un solo material previo de
  su clase que comparte el efecto de laboratorio. Dmax de laboratorio del propio set.
- Densidad de colocación (lepsp.densidad, actúa sobre η) y escala a dmax 1 m (lepsp.escala; τ conservador).
- Tipos de roca por clase de calidad (anonimización): A, C, D, E de calidad baja; B moderada. D y E sin ensayos;
  E con degradación Δe = +0.15 en campo.
Argumentos: --x2 (forma cuadrática), --lab-indep (D y E con efecto de laboratorio independiente).
Escribe lepsp_sitio3{suf}.json y lepsp_sitio3_muestras_{esc}{suf}.npz."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "leps3"))
import lepsp as L  # noqa: E402

FORMA = "x2" if "--x2" in sys.argv else "acotada"; LABI = "--lab-indep" in sys.argv
BDI = "--bD-indep" in sys.argv; SUP_G = "tau_r3" if "--tau-r3" in sys.argv else "general"     # sensibilidades de la ronda 5
SUF = ("_x2" if FORMA == "x2" else "") + ("_labindep" if LABI else "") + ("_bdindep" if BDI else "") + ("_taur3" if SUP_G == "tau_r3" else "")
d = pd.read_csv(AQ / "drenados_utilizables.csv", low_memory=False)
g = d[d.escala.isin(["0.6 m", "1.0 m"]) & (d.relave_pct_masa_total.fillna(0) == 0)].copy(); g["e_use"] = g.e0_adoptado.fillna(g.e0)
LIT = {"Mármol": ("A", "baja"), "Hornfels": ("B", "moderada"), "Intrusivo": ("C", "baja")}
sets, meta = [], []
for sid, gs in g.groupby("set_a"):
    lit = gs.litologia.iloc[0]
    sets.append(dict(calidad=LIT[lit][1], e=float(gs.e_use.iloc[0]), s3=gs.s3.values, s1=gs.s1.values, usar=True))
    meta.append(dict(set=sid, lit=LIT[lit][0], n=len(gs), dmax=float(gs.Dmax_mm.iloc[0]), e=float(gs.e_use.iloc[0])))
_, dg0 = L.actualizar_sitio(sets, forma=FORMA, n=4000, seed=1)
for s, dg_, mt in zip(sets, dg0, meta):
    s["usar"] = dg_["p_conflicto"] >= 0.05; mt.update(p_conflicto=dg_["p_conflicto"], razon=dg_["rango_sn"], sn_max=dg_["sn_max"], usado=s["usar"])
    print(f"  {mt['lit']} n={mt['n']} e={mt['e']:.3f} razón σ′n={dg_['rango_sn']:.2f} p={dg_['p_conflicto']:.4f} → {'usado' if s['usar'] else 'NO usado (conflicto)'}")
E_REF = float(np.median([m_["e"] for m_ in meta]))
mats, _ = L.actualizar_sitio(sets, [("baja", E_REF), ("baja", E_REF)], forma=FORMA, n=60000, seed=11, lab_comun_nuevos=not LABI)
mats, ret = L.restringir_conjunto_rango(mats)
print("fracción conservada por la restricción:", np.round(ret["por_material"], 3), "conjunta", round(ret["conjunta"], 3))
grupos = {}
for i, mt in enumerate(meta):
    grupos.setdefault(mt["lit"], []).append(i)
for k in list(grupos):
    usados = [i for i in grupos[k] if meta[i]["usado"]]
    grupos[k] = usados if usados else grupos[k][:1]          # un material por tipo de roca
grupos["D"] = [len(sets)]; grupos["E"] = [len(sets) + 1]
DM = lambda i: meta[i]["dmax"] if i < len(sets) else float(np.exp(np.mean([np.log(m_["dmax"]) for m_ in meta])))
EL = lambda i, k: meta[i]["e"] if i < len(sets) else E_REF
PESO = {"A": 0.35, "B": 0.25, "C": 0.20, "D": 0.10, "E": 0.10}
SNG = np.logspace(np.log10(0.05), np.log10(20), 60); XG = np.log(SNG / L.S0); nsel = len(mats[0].th)
OUT = dict(forma=FORMA, lab_indep=LABI, sets=meta, grupos=grupos, e_lab_ref=E_REF, sn=SNG.tolist(), retencion_restriccion=ret, pesos=PESO, escenarios={})


def tau_lit(k, e_campo, bD):
    if BDI and bD is not None:                          # efecto de escala independiente por tipo de roca
        bD = np.random.default_rng(100 + "ABCDE".index(k)).permutation(bD)
    t = 0
    for i in grupos[k]:
        mt = mats[i]
        if e_campo is not None:
            mt = L.densidad(mt, e_campo - EL(i, k) + (0.15 if k == "E" else 0.0))
        if bD is not None:
            mt = L.escala(mt, DM(i), 1000.0, bD=bD)
        t = t + L.S0 * np.exp(L._media(mt, XG))
    return t / len(grupos[k])


phi = lambda t: np.degrees(np.arctan(t / SNG[None, :]))
i3 = int(np.argmin(np.abs(SNG - 3)))
for esc_e in (None, 0.55, 0.65):
    for sup in ("general", "datos", "ninguno"):
        bD = None if sup == "ninguno" else L.muestras_bD(nsel, SUP_G if sup == "general" else sup, seed=5)
        T = {k: tau_lit(k, esc_e, bD) for k in grupos}
        w = np.array([PESO[k] for k in T]); tt = np.array(list(T.values()))
        prom = np.tensordot(w, tt, 1); comon = np.tensordot(w, np.sort(tt, axis=1), 1)
        debil_ens = min([k for k in T if k in "ABC"], key=lambda k: np.median(phi(T[k])[:, i3]))
        debil = min(T, key=lambda k: np.median(phi(T[k])[:, i3]))
        clave = f"e={'lab' if esc_e is None else esc_e}|{sup}"
        OUT["escenarios"][clave] = dict(
            litologias={k: {f"P{q:02d}": np.percentile(phi(v), q, 0).tolist() for q in (5, 10, 50)} for k, v in T.items()},
            botadero={nm: {f"P{q:02d}": np.percentile(phi(v), q, 0).tolist() for q in (5, 10, 50)} for nm, v in
                      [("model", prom), ("comonotonic", comon), (f"weakest tested ({debil_ens})", T[debil_ens]), (f"weakest ({debil})", T[debil])]})
        if (esc_e, sup) in ((None, "ninguno"), (None, "general"), (0.65, "general"), (0.65, "ninguno"), (0.65, "datos")):
            nm_ = f"{'lab' if esc_e is None else 'e065'}_{sup}"
            np.savez_compressed(AQ / f"lepsp_sitio3_muestras_{nm_}{SUF}.npz", tau=tt, pesos=w, sn=SNG, nombres=np.array(list(T)))
        b = OUT["escenarios"][clave]["botadero"]
        print(f"[{clave}] botadero P50/P05 a 3 y 20 MPa: " + "; ".join(f"{nm}: {v['P50'][i3]:.1f}/{v['P05'][i3]:.1f}, {v['P50'][-1]:.1f}/{v['P05'][-1]:.1f}" for nm, v in b.items()))
OUT["ensayos"] = []
for s, mt in zip(sets, meta):
    sn_, tau_ = L._a_sn_tau(np.asarray(s["s3"]), np.asarray(s["s1"]), 0.86)
    OUT["ensayos"].append(dict(lit=mt["lit"], set=mt["set"], usado=mt["usado"], sn=sn_.tolist(), phis=np.degrees(np.arctan(tau_ / sn_)).tolist()))
json.dump(OUT, open(AQ / f"lepsp_sitio3{SUF}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0, default=float)
print(f"escrito lepsp_sitio3{SUF}.json")
