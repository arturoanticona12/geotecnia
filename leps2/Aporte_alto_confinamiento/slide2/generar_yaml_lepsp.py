"""Descripción YAML para verificar en Slide2 los análisis de estabilidad de Leps-P.
Grupos 1–3: botaderos de 150, 400 y 700 m sobre fundación horizontal competente (búsqueda circular Auto Refine).
Grupo 4: botadero de 700 m sobre ladera de 10° con capa basal de 30 m (búsqueda no circular por recocido simulado y
optimización); escenarios secos. Grupo 5: igual, con capa basal saturada (ru = 0.2). Grupo 6: igual, con la capa
basal no drenada, Su = r·σ′v (material discreto, Su en una grilla de puntos), r = 0.17 (fluencia) y r = 0.09 (licuada)."""
import json, math
from pathlib import Path
import yaml

AQUI = Path(__file__).parent
F = json.load(open(AQUI.parent / "analisis" / "lepsp_funciones_slide2.json", encoding="utf-8"))
CORTO = {"Desmonte del sitio, P50": "Sitio P50", "Desmonte del sitio, P05 (característico)": "Sitio P05",
         "Desmonte del sitio, segregación (litología más débil), P05": "Segregacion P05",
         "Material genérico moderado e = 0.45, P50": "Generico P50", "Material genérico moderado e = 0.45, P05 (característico)": "Generico P05"}
FUNCIONES = {CORTO[k]: [[round(a, 2), round(b, 2)] for a, b in v] for k, v in F.items()}
GAM = 21.0; BETA, THETA, HB = 26.57, 10.0, 30.0; tb, tt = math.tan(math.radians(BETA)), math.tan(math.radians(THETA))
TXT = {"Sitio P50": "Leps-P, desmonte del sitio, P50", "Sitio P05": "Leps-P, desmonte del sitio, P05",
       "Segregacion P05": "Leps-P, litologia mas debil, P05", "Generico P50": "Leps-P, material generico, P50",
       "Generico P05": "Leps-P, material generico, P05"}
materiales = [dict(nombre=f"Desmonte {k}", gamma=GAM, modelo="funcion", funcion=k, resistencia_txt=TXT[k]) for k in FUNCIONES]
materiales += [dict(nombre=f"Basal {k}", gamma=GAM, modelo="funcion", funcion=k, resistencia_txt="Capa basal: " + TXT[k]) for k in ("Sitio P50", "Sitio P05")]
materiales += [dict(nombre=f"Basal ru {k}", gamma=GAM, modelo="funcion", funcion=k, resistencia_txt="Capa basal saturada: " + TXT[k]) for k in ("Sitio P50", "Sitio P05")]
materiales += [dict(nombre="Roca", gamma=26, modelo="mohr-coulomb", c=1000, phi=45)]


def esc(lista, base="Sitio P50", basal=False):
    out = []
    for k in lista:
        r = {} if k == base else {f"Desmonte {base}": f"Desmonte {k}"}
        if basal and k != base:
            r[f"Basal {base}"] = f"Basal {k}"
        out.append(dict(nombre=k, **({"reasignar": r} if r else {})))
    return out


grupos = []
for H in (150.0, 400.0, 700.0):
    XC = H / tb; XR = XC + 3.0 * H
    grupos.append(dict(
        nombre=f"H{H:.0f} fundacion horizontal",
        geometria=dict(exterior=[[-2.0 * H, -0.5 * H], [XR, -0.5 * H], [XR, H], [XC, H], [0, 0], [-2.0 * H, 0]],
                       limites=[[[0, 0], [XR, 0]]],
                       materiales_en=[{"punto": [XC, H / 2], "material": "Desmonte Sitio P50"}, {"punto": [XC, -0.25 * H], "material": "Roca"}]),
        busqueda=dict(tipo="auto-refine", limites=[-1.5 * H, XR]),
        metodos=["bishop", "spencer", "gle"],
        escenarios=esc(list(FUNCIONES)),
        vista=dict(xlim=[-0.6 * H, XC + 1.4 * H], ylim=[-0.5 * H, 1.6 * H])))
# ---- ladera de 10°
H = 700.0; XC = H / tb; XE = H / tt; XR = XE + 1500; yr = XR * tt
x_b0 = HB / (tb - tt); x_b1 = (H - HB) / tt


def geo_ladera(basal):
    return dict(exterior=[[-1500, -400], [XR, -400], [XR, yr], [XE, H], [XC, H], [0, 0], [-1500, 0]],
                limites=[[[0, 0], [XE, H]], [[x_b0, x_b0 * tb], [x_b1, H]]],
                materiales_en=[{"punto": [1500, 500], "material": "Desmonte Sitio P50"},
                               {"punto": [1500, 1500 * tt + HB / 2], "material": basal},
                               {"punto": [1000, -200], "material": "Roca"}])


comun = dict(busqueda=dict(tipo="sa", limites=[-1500, XE], parametros={"optimize": 1}), metodos=["spencer", "gle"],
             vista=dict(xlim=[-800, 4200], ylim=[-400, 1100]))
grupos.append(dict(nombre="H700 ladera 10 seco", geometria=geo_ladera("Basal Sitio P50"),
                   escenarios=esc(["Sitio P50", "Sitio P05"], basal=True), **comun))
grupos.append(dict(nombre="H700 ladera 10 basal ru 0.2", geometria=geo_ladera("Basal ru Sitio P50"),
                   escenarios=[dict(nombre="Sitio P50"), dict(nombre="Sitio P05", reasignar={"Desmonte Sitio P50": "Desmonte Sitio P05",
                                                                                         "Basal ru Sitio P50": "Basal ru Sitio P05"})],
                   agua=dict(metodo="ru"), **comun))
for m in materiales:
    m["ru"] = 0.2 if str(m["nombre"]).startswith("Basal ru") else 0.0
# ---- base no drenada: Su = r σ′v en la capa basal (grilla de puntos; σ′v = γ × espesor sobre el punto)
top = lambda x: min(max(x * tb, 0.0), H)


def puntos_su(r):
    P = []
    for x in [x_b0 + i * (x_b1 - x_b0) / 40 for i in range(41)]:
        for f in (0.05, 0.5, 0.95):
            y = x * tt + f * HB
            if y < top(x):
                P.append([round(x, 1), round(y, 2), round(r * GAM * (top(x) - y), 1)])
    return P


FDISC = {f"Su r {r}": dict(tipo="no-drenado", puntos=puntos_su(r)) for r in (0.17, 0.09)}
for r in (0.17, 0.09):
    materiales.append(dict(nombre=f"Basal no drenada r {r}", gamma=GAM, modelo="discreta", funcion=f"Su r {r}", ru=0.0,
                           resistencia_txt=f"Capa basal no drenada, Su = {r} sigma'v"))
comun_global = dict(comun, busqueda=dict(tipo="sa", limites=[-300, 150, 900, 3500], parametros={"optimize": 1}))   # mecanismo global: salida en el pie, entrada en la plataforma
grupos.append(dict(nombre="H700 ladera 10 basal no drenada", geometria=geo_ladera("Basal no drenada r 0.17"),
                   escenarios=[dict(nombre="r 0.17 (fluencia)"), dict(nombre="r 0.09 (licuada)", reasignar={"Basal no drenada r 0.17": "Basal no drenada r 0.09"})],
                   **comun_global))
import sys  # noqa: E402
if len(sys.argv) > 1 and sys.argv[1] == "nodrenado":
    grupos = [grupos[-1]]; nombre = "lepsp_nodrenado"
else:
    nombre = "lepsp_estabilidad"
desc = dict(nombre=nombre, titulo="Leps-P: verificacion de estabilidad de botaderos", unidades="metric",
            direccion="der-izq", materiales=materiales, funciones=FUNCIONES, funciones_discretas=FDISC, grupos=grupos)
out = AQUI / f"{nombre}.yaml"; out.write_text(yaml.safe_dump(desc, allow_unicode=True, sort_keys=False), encoding="utf-8")
print("escrito", out, "| grupos:", [g["nombre"] for g in grupos])
