"""Leps-P, ronda 4: estabilidad solo en Slide2 y solo con Morgenstern–Price (GLE, función de fuerzas entre dovelas de
medio seno). Botaderos de 150, 400 y 700 m, talud global 2H:1V, fundación horizontal competente y drenada; desmonte
con envolvente τ–σ′n tabulada (material función) de a8_lepsp_sitio.py. Búsqueda no circular por recocido simulado con
optimización.
- Determinístico (lepsp4_det.yaml): envolventes P50 y P05 de cada escenario de correlación y de los casos que separan
  densidad y escala; γ coherente con e (17.2 kN/m³ con e = 0.65; 15.7 para el tipo de roca E con e = 0.80; 21 en
  laboratorio).
- Monte Carlo (mc/lepsp4_mc_<caso>_NN.yaml): 600 envolventes muestreadas por caso (700 m; correlación del modelo y solo
  tipo de roca E), 25 realizaciones por modelo, cada una con su propia búsqueda de la superficie crítica."""
import json, math, sys
from pathlib import Path
import numpy as np
import yaml

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"
GS, W = 2.75, 0.05; GAM = lambda e: round(GS * 9.81 * (1 + W) / (1 + e), 2)
BETA = 26.57; tb = math.tan(math.radians(BETA)); NMC = 600; POR = 25


def escen(npz):
    Z = np.load(AA / npz); tau = Z["tau"]; w = Z["pesos"]; sn = Z["sn"]; nom = list(Z["nombres"])
    i3 = int(np.argmin(np.abs(sn - 3))); med = [np.median(np.degrees(np.arctan(t[:, i3] / sn[i3]))) for t in tau]
    i_d = int(np.argmin(med)); i_dt = int(np.argmin([m if n in "ABC" else 99 for m, n in zip(med, nom)]))
    return sn, {"model": np.tensordot(w, tau, 1), "comonotonic": np.tensordot(w, np.sort(tau, axis=1), 1),
                f"weakest tested {nom[i_dt]}": tau[i_dt], f"weakest {nom[i_d]}": tau[i_d]}


def fun(sn, t):
    """Pares [σ′n, τ] en kPa (origen incluido), cada dos puntos de la grilla."""
    return [[0.0, 0.0]] + [[round(float(s) * 1000, 2), round(float(v) * 1000, 2)] for s, v in zip(sn[::2], t[::2])]


def grupo(H, mat0, escs, nombre):
    XC = H / tb; XR = XC + 3.0 * H
    return dict(nombre=nombre, geometria=dict(exterior=[[-2.0 * H, -0.5 * H], [XR, -0.5 * H], [XR, H], [XC, H], [0, 0], [-2.0 * H, 0]],
                                              limites=[[[0, 0], [XR, 0]]],
                                              materiales_en=[{"punto": [XC, H / 2], "material": mat0}, {"punto": [XC, -0.25 * H], "material": "Roca"}]),
                busqueda=dict(tipo="sa", limites=[-1.5 * H, XR], parametros={"optimize": 1}), metodos=["gle"],
                escenarios=escs, vista=dict(xlim=[-0.6 * H, XC + 1.4 * H], ylim=[-0.5 * H, 1.6 * H]))


def escribir(nombre, funciones, materiales, grupos, carpeta=AQ):
    desc = dict(nombre=nombre, titulo="Leps-P ronda 4: estabilidad Morgenstern-Price", unidades="metric", direccion="der-izq",
                materiales=materiales + [dict(nombre="Roca", gamma=26, modelo="mohr-coulomb", c=1000, phi=45)], funciones=funciones, grupos=grupos)
    carpeta.mkdir(exist_ok=True); (carpeta / f"{nombre}.yaml").write_text(yaml.safe_dump(desc, allow_unicode=True, sort_keys=False), encoding="utf-8")


CASOS = {"e065": ("lepsp_sitio3_muestras_e065_general.npz", 0.65), "e065 sin escala": ("lepsp_sitio3_muestras_e065_ninguno.npz", 0.65),
         "e065 escala datos": ("lepsp_sitio3_muestras_e065_datos.npz", 0.65), "lab sin escala": ("lepsp_sitio3_muestras_lab_ninguno.npz", None),
         "lab escala": ("lepsp_sitio3_muestras_lab_general.npz", None), "x2 e065": ("lepsp_sitio3_muestras_e065_general_x2.npz", 0.65)}
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
    # un modelo por (altura, caso): 8 escenarios cada uno, para calcular en paralelo
    DET = AQ / "det4b"; n_esc = 0
    for H in (150.0, 400.0, 700.0):
        for caso in (["e065"] if H < 700 else list(CASOS)):
            lista = mats_por_caso[caso]; base = lista[0]
            escs = [dict(nombre=base[2:])] + [dict(nombre=mm[2:], reasignar={base: mm}) for mm in lista[1:]]
            usadas = {mm[2:] for mm in lista}
            escribir(f"det_H{H:.0f}_c{list(CASOS).index(caso)}", {k: v for k, v in funciones.items() if k in usadas},
                     [mt for mt in materiales if mt["nombre"] in lista], [grupo(H, base, escs, f"H{H:.0f}")], DET)
            n_esc += len(escs)
    import json as _j; (DET / "claves.json").write_text(_j.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    print("determinístico:", n_esc, "escenarios en", len(list(DET.glob("*.yaml"))), "modelos en", DET)
    # ---- Monte Carlo: 600 envolventes por caso, 700 m
    sn, ESC = escen(CASOS["e065"][0]); rng = np.random.default_rng(700); (AQ / "mc4").mkdir(exist_ok=True)
    for caso, clave, g in (("modelo", "model", GAM(0.65)), ("E", "weakest E", GAM(0.80))):
        T = ESC[clave]; idx = rng.choice(T.shape[0], NMC, replace=False)
        np.save(AQ / "mc4" / f"indices_{caso}.npy", idx)
        for b in range(NMC // POR):
            fs, ms = {}, []
            for k, j in enumerate(idx[b * POR:(b + 1) * POR]):
                nm = f"{caso} r{b * POR + k:03d}"; fs[nm] = fun(sn, T[j])
                ms.append(dict(nombre=f"D {nm}", gamma=g, modelo="funcion", funcion=nm, agua="ninguna", resistencia_txt=f"Leps-P realizacion {nm}"))
            base = ms[0]["nombre"]; escs = [dict(nombre=base[2:])] + [dict(nombre=m["nombre"][2:], reasignar={base: m["nombre"]}) for m in ms[1:]]
            escribir(f"lepsp4_mc_{caso}_{b:02d}", fs, ms, [grupo(700.0, base, escs, "H700")], AQ / "mc4")
    print(f"Monte Carlo: {2 * NMC // POR} modelos de {POR} realizaciones en", AQ / "mc4")
