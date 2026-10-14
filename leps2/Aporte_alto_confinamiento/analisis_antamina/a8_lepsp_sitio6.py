"""Leps-P aplicado al desmonte del sitio, ronda 6 (respuesta a los revisores):
- Previa con el Dmax de laboratorio de cada set (término ln Dmax del modelo de la ronda 6).
- Chequeo de conflicto con ajuste de Holm entre los sets del sitio (revisor E6) y regla asimétrica (C3): un set marcado
  se excluye de la actualización solo si es MÁS resistente que la previa (exclusión conservadora); un set más débil
  nunca se descarta (se usa y se informa).
- Envolvente por TIPO DE ROCA (revisor P1): cada tipo ensayado se representa por un set nuevo del mismo laboratorio, de su
  clase, e y Dmax, que comparte el efecto de laboratorio actualizado (la variabilidad entre sets queda en la envolvente).
  Con --muestra se usa la posterior de los sets ensayados (sensibilidad de la ronda 5).
- Densidad de colocación y escala a Dmax de campo de 1 m (media cero y τ_D por laboratorio; --datos-escala usa la media
  estimada; --weibull usa β_D = −0.05).
- Se guarda el φ′∞ de cada muestra para obtener envolventes en los extremos del perfil (Slide2, mecanismos de alto
  confinamiento).
Argumentos: --x2, --muestra, --lab-indep, --bD-indep, --weibull. Escribe lepsp_sitio6{suf}.json y lepsp_sitio6_muestras_*{suf}.npz."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "leps3"))
import lepsp as L  # noqa: E402

FORMA = "x2" if "--x2" in sys.argv else "acotada"; MUESTRA = "--muestra" in sys.argv; LABI = "--lab-indep" in sys.argv
BDI = "--bD-indep" in sys.argv; SUP_G = "weibull" if "--weibull" in sys.argv else "general"
SUF = "".join(s for s, f in (("_x2", FORMA == "x2"), ("_muestra", MUESTRA), ("_labindep", LABI), ("_bdindep", BDI), ("_weibull", SUP_G == "weibull")) if f)
d = pd.read_csv(AQ / "drenados_utilizables.csv", low_memory=False)
g = d[d.escala.isin(["0.6 m", "1.0 m"]) & (d.relave_pct_masa_total.fillna(0) == 0)].copy(); g["e_use"] = g.e0_adoptado.fillna(g.e0)
LIT = {"Mármol": ("A", "baja"), "Hornfels": ("B", "moderada"), "Intrusivo": ("C", "baja")}
sets, meta = [], []
for sid, gs in g.groupby("set_a"):
    lit = gs.litologia.iloc[0]; Dm = float(gs.Dmax_mm.iloc[0])
    sets.append(dict(calidad=LIT[lit][1], e=float(gs.e_use.iloc[0]), D=Dm, s3=gs.s3.values, s1=gs.s1.values, usar=True))
    meta.append(dict(set=sid, lit=LIT[lit][0], n=len(gs), dmax=Dm, e=float(gs.e_use.iloc[0])))
_, dg0 = L.actualizar_sitio(sets, forma=FORMA, n=4000, seed=1)
# Holm entre los sets del sitio; exclusión solo de sets marcados y más resistentes que la previa
ps = np.array([x["p_conflicto"] for x in dg0]); orden = np.argsort(ps); m_ = len(ps); ph = np.zeros(m_); acc = 0.0
for r_, i in enumerate(orden):
    acc = max(acc, min(1.0, (m_ - r_) * ps[i])); ph[i] = acc
for s, dg_, mt, p_h in zip(sets, dg0, meta, ph):
    marcado = p_h < 0.05; mas_fuerte = dg_["residuo_medio"] > 0
    s["usar"] = not (marcado and mas_fuerte)
    mt.update(p_conflicto=dg_["p_conflicto"], p_holm=float(p_h), residuo_medio=dg_["residuo_medio"], razon=dg_["rango_sn"], sn_max=dg_["sn_max"],
              marcado=bool(marcado), usado=s["usar"])
    print(f"  {mt['lit']} n={mt['n']} e={mt['e']:.3f} Dmax={mt['dmax']:.0f} mm p={dg_['p_conflicto']:.4f} Holm={p_h:.4f} residuo {dg_['residuo_medio']:+.3f} → "
          f"{'usado' if s['usar'] else 'NO usado (marcado y más resistente)'}{' (marcado, más débil: se usa)' if marcado and not mas_fuerte else ''}")
E_REF = float(np.median([x["e"] for x in meta])); D_GEO = float(np.exp(np.mean([np.log(x["dmax"]) for x in meta])))
TIPOS = {}
for i, mt in enumerate(meta):
    TIPOS.setdefault(mt["lit"], []).append(i)
nuevos, grupos = [], {}
if MUESTRA:
    for k, ii in TIPOS.items():
        us = [i for i in ii if meta[i]["usado"]]; grupos[k] = us if us else ii[:1]
else:
    for k, ii in TIPOS.items():                                   # set nuevo de cada tipo ensayado
        grupos[k] = [len(sets) + len(nuevos)]
        nuevos.append((sets[ii[0]]["calidad"], float(np.mean([meta[i]["e"] for i in ii])), float(np.exp(np.mean([np.log(meta[i]["dmax"]) for i in ii])))))
for k in ("D", "E"):
    grupos[k] = [len(sets) + len(nuevos)]; nuevos.append(("baja", E_REF, D_GEO))
mats, _ = L.actualizar_sitio(sets, nuevos, forma=FORMA, n=60000, seed=11, lab_comun_nuevos=not LABI)
mats, ret = L.restringir_conjunto_rango(mats)
print("fracción conservada por la restricción:", np.round(ret["por_material"], 3), "conjunta", round(ret["conjunta"], 3))
ALL_E = [x["e"] for x in meta] + [n_[1] for n_ in nuevos]; ALL_D = [x["dmax"] for x in meta] + [n_[2] for n_ in nuevos]
PESO = {"A": 0.35, "B": 0.25, "C": 0.20, "D": 0.10, "E": 0.10}
SNG = np.logspace(np.log10(0.05), np.log10(20), 60); XG = np.log(SNG / L.S0); nsel = len(mats[0].th)
F = L._P["formas"][FORMA]; PHI_K = np.array([s_.get("phi_cs", np.nan) for s_ in F["muestras"]])[mats[0].k]
OUT = dict(forma=FORMA, representa="muestra" if MUESTRA else "tipo", lab_indep=LABI, sets=meta, grupos=grupos, nuevos=nuevos, e_lab_ref=E_REF,
           sn=SNG.tolist(), retencion_restriccion=ret, pesos=PESO, escenarios={})


def tau_lit(k, e_campo, bD):
    if BDI and bD is not None:
        bD = np.random.default_rng(100 + "ABCDE".index(k)).permutation(bD)
    t = 0
    for i in grupos[k]:
        mt = mats[i]
        if e_campo is not None:
            mt = L.densidad(mt, e_campo - ALL_E[i] + (0.15 if k == "E" else 0.0))
        if bD is not None:
            mt = L.escala(mt, ALL_D[i], 1000.0, bD=bD)
        t = t + L.S0 * np.exp(L._media(mt, XG))
    return t / len(grupos[k])


phi = lambda t: np.degrees(np.arctan(t / SNG[None, :]))
i3 = int(np.argmin(np.abs(SNG - 3)))
for esc_e in (None, 0.65):
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
        nm_ = f"{'lab' if esc_e is None else 'e065'}_{sup}"
        np.savez_compressed(AQ / f"lepsp_sitio6_muestras_{nm_}{SUF}.npz", tau=tt.astype(np.float32), pesos=w, sn=SNG, nombres=np.array(list(T)), phi_k=PHI_K)
        b = OUT["escenarios"][clave]["botadero"]
        print(f"[{clave}] botadero P50/P05 a 1, 3 y 8 MPa: " + "; ".join(
            f"{nm}: " + ", ".join(f"{v['P50'][j]:.1f}/{v['P05'][j]:.1f}" for j in (int(np.argmin(np.abs(SNG - s_))) for s_ in (1, 3, 8))) for nm, v in b.items()))
OUT["ensayos"] = []
for s, mt in zip(sets, meta):
    sn_, tau_ = L._a_sn_tau(np.asarray(s["s3"]), np.asarray(s["s1"]), 0.86)
    OUT["ensayos"].append(dict(lit=mt["lit"], set=mt["set"], usado=mt["usado"], sn=sn_.tolist(), phis=np.degrees(np.arctan(tau_ / sn_)).tolist()))
json.dump(OUT, open(AQ / f"lepsp_sitio6{SUF}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0, default=float)
print(f"escrito lepsp_sitio6{SUF}.json")
