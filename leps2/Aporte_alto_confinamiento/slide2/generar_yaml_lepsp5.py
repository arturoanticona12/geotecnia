"""Leps-P, ronda 5: igual que generar_yaml_lepsp4.py (Morgenstern–Price, SA no circular) con los parámetros de la
ronda 5 y dos casos de sensibilidad nuevos a 700 m:
- «e065 bD indep»: desplazamiento de escala independiente por tipo de roca (a8 --bD-indep);
- «e065 tau r3»: τ_D = 0.049, el de la ronda 3 (sensibilidad hacia abajo; a8 --tau-r3).
Control de convergencia de la búsqueda: el caso que gobierna (700 m, e = 0.65, correlación del modelo, P50 y P05) con
búsqueda circular Auto Refine. Escribe det5/ (con claves.json) y mc5/ (600 envolventes por caso)."""
import json
from pathlib import Path
import numpy as np
from generar_yaml_lepsp4 import escen, fun, grupo, escribir, GAM, NMC, POR

AQ = Path(__file__).parent
CASOS = {"e065": ("lepsp_sitio3_muestras_e065_general.npz", 0.65), "e065 sin escala": ("lepsp_sitio3_muestras_e065_ninguno.npz", 0.65),
         "e065 escala datos": ("lepsp_sitio3_muestras_e065_datos.npz", 0.65), "lab sin escala": ("lepsp_sitio3_muestras_lab_ninguno.npz", None),
         "lab escala": ("lepsp_sitio3_muestras_lab_general.npz", None), "x2 e065": ("lepsp_sitio3_muestras_e065_general_x2.npz", 0.65),
         "e065 bD indep": ("lepsp_sitio3_muestras_e065_general_bdindep.npz", 0.65), "e065 tau r3": ("lepsp_sitio3_muestras_e065_general_taur3.npz", 0.65)}
if __name__ == "__main__":
    funciones, materiales, mats_por_caso, CLAVE = {}, [], {}, {}
    CODE_E = {"model": "M", "comonotonic": "C"}
    for ic, (caso, (npz, e)) in enumerate(CASOS.items()):
        sn, ESC = escen(npz); mats_por_caso[caso] = []
        for esc_, T in ESC.items():
            for q in (50, 5):
                cod = CODE_E.get(esc_, "T" if esc_.startswith("weakest tested") else "W")
                nm = f"c{ic} {cod} P{q:02d}"; funciones[nm] = fun(sn, np.percentile(T, q, axis=0)); CLAVE[nm] = f"{caso}|{esc_}|P{q:02d}"
                g = 21.0 if e is None else (GAM(0.80) if esc_ == "weakest E" else GAM(e))
                materiales.append(dict(nombre=f"D {nm}", gamma=g, modelo="funcion", funcion=nm, agua="ninguna", resistencia_txt=f"Leps-P {nm}"))
                mats_por_caso[caso].append(f"D {nm}")
    DET = AQ / "det5"; n_esc = 0
    for H in (150.0, 400.0, 700.0):
        for caso in (["e065"] if H < 700 else list(CASOS)):
            lista = mats_por_caso[caso]; base = lista[0]
            escs = [dict(nombre=base[2:])] + [dict(nombre=mm[2:], reasignar={base: mm}) for mm in lista[1:]]
            usadas = {mm[2:] for mm in lista}
            escribir(f"det_H{H:.0f}_c{list(CASOS).index(caso)}", {k: v for k, v in funciones.items() if k in usadas},
                     [mt for mt in materiales if mt["nombre"] in lista], [grupo(H, base, escs, f"H{H:.0f}")], DET)
            n_esc += len(escs)
    # control de convergencia: búsqueda circular Auto Refine del caso que gobierna
    lista = ["D c0 M P50", "D c0 M P05"]; g = grupo(700.0, lista[0], [dict(nombre="c0 M P50"), dict(nombre="c0 M P05", reasignar={lista[0]: lista[1]})], "H700 circular")
    g["busqueda"] = dict(tipo="auto-refine", limites=g["busqueda"]["limites"])
    escribir("det_H700_conv", {k: v for k, v in funciones.items() if k in ("c0 M P50", "c0 M P05")}, [mt for mt in materiales if mt["nombre"] in lista], [g], DET)
    (DET / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    print("determinístico:", n_esc + 2, "escenarios en", len(list(DET.glob("*.yaml"))), "modelos en", DET)
    sn, ESC = escen(CASOS["e065"][0]); rng = np.random.default_rng(700); (AQ / "mc5").mkdir(exist_ok=True)
    for caso, clave, gm in (("modelo", "model", GAM(0.65)), ("E", "weakest E", GAM(0.80))):
        T = ESC[clave]; idx = rng.choice(T.shape[0], NMC, replace=False)
        np.save(AQ / "mc5" / f"indices_{caso}.npy", idx)
        for b in range(NMC // POR):
            fs, ms = {}, []
            for k, j in enumerate(idx[b * POR:(b + 1) * POR]):
                nm = f"{caso} r{b * POR + k:03d}"; fs[nm] = fun(sn, T[j])
                ms.append(dict(nombre=f"D {nm}", gamma=gm, modelo="funcion", funcion=nm, agua="ninguna", resistencia_txt=f"Leps-P realizacion {nm}"))
            base = ms[0]["nombre"]; escs = [dict(nombre=base[2:])] + [dict(nombre=m["nombre"][2:], reasignar={base: m["nombre"]}) for m in ms[1:]]
            escribir(f"lepsp5_mc_{caso}_{b:02d}", fs, ms, [grupo(700.0, base, escs, "H700")], AQ / "mc5")
    print(f"Monte Carlo: {2 * NMC // POR} modelos de {POR} realizaciones en", AQ / "mc5")
