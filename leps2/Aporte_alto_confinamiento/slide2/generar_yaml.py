"""Genera la descripción YAML del botadero genérico de 700 m para verificar en Slide2 los FS calculados en Python.
Grupo 1: fundación horizontal (búsqueda circular). Grupo 2: ladera de 10° (búsqueda no circular)."""
import math
from pathlib import Path
import yaml

PA = 101.3  # kPa
H, BETA, THETA = 700.0, 26.57, 10.0
XC = H / math.tan(math.radians(BETA))          # cresta
XE = H / math.tan(math.radians(THETA))         # fin de plataforma contra la ladera
XR = 5000.0


def tau_corr(s, phi1=41.0, a=3.72):
    ph = phi1 - a * max(math.log10(s / (10 * PA)), 0.0)
    return math.tan(math.radians(ph)) * (10 * PA) ** 0.1 * s ** 0.9


pts = [0, 25, 50, 100, 200, 400, 700, 1013] + list(range(1500, 16001, 500))
funcion = [[float(s), round(tau_corr(s) if s > 0 else 0.0, 2)] for s in pts]

a41 = math.tan(math.radians(41)) * (10 * PA) ** 0.1
a38 = math.tan(math.radians(38)) * (10 * PA) ** 0.1

materiales = [
    dict(nombre="Desmonte Leps41", gamma=21, modelo="potencia", pca=round(a41, 4), pcb=0.9, pcc=0, pcd=0,
         resistencia_txt="Leps 2.0: φ′1 = 41°, m = 0.9"),
    dict(nombre="Desmonte Leps38", gamma=21, modelo="potencia", pca=round(a38, 4), pcb=0.9, pcc=0, pcd=0,
         resistencia_txt="Leps 2.0: φ′1 = 38°, m = 0.9"),
    dict(nombre="Desmonte m087 41", gamma=21, modelo="potencia", pca=round(math.tan(math.radians(41)) * (10 * PA) ** 0.13, 4),
         pcb=0.87, pcc=0, pcd=0, resistencia_txt="Leps 2.0: φ′1 = 41°, m = 0.87"),
    dict(nombre="Desmonte m087 38", gamma=21, modelo="potencia", pca=round(math.tan(math.radians(38)) * (10 * PA) ** 0.13, 4),
         pcb=0.87, pcc=0, pcd=0, resistencia_txt="Leps 2.0: φ′1 = 38°, m = 0.87"),
    dict(nombre="Roca", gamma=26, modelo="mohr-coulomb", c=1000, phi=45),
    dict(nombre="Leps3 diseno 41", gamma=21, modelo="funcion", funcion="L3 d41",
         resistencia_txt="Leps 3.0, diseño P10: φ′1 = 41°, m = 0.87"),
    dict(nombre="Leps3 diseno 38", gamma=21, modelo="funcion", funcion="L3 d38",
         resistencia_txt="Leps 3.0, diseño P10: φ′1 = 38°, m = 0.87"),
]
import json  # noqa: E402
_F = json.load(open(Path(__file__).parents[1] / "analisis" / "ejemplo_leps3_funciones.json"))
FUNCIONES = {"L3 d41": [list(p) for p in _F["d41"]], "L3 d38": [list(p) for p in _F["d38"]]}

escenarios = [
    dict(nombre="Leps 2.0 phi1 41"),
    dict(nombre="Leps 2.0 phi1 38", reasignar={"Desmonte Leps41": "Desmonte Leps38"}),
    dict(nombre="m 0.87 phi1 41", reasignar={"Desmonte Leps41": "Desmonte m087 41"}),
    dict(nombre="m 0.87 phi1 38", reasignar={"Desmonte Leps41": "Desmonte m087 38"}),
    dict(nombre="L3 diseno phi1 41", reasignar={"Desmonte Leps41": "Leps3 diseno 41"}),
    dict(nombre="L3 diseno phi1 38", reasignar={"Desmonte Leps41": "Leps3 diseno 38"}),
]

g1 = dict(
    nombre="Fundacion horizontal",
    geometria=dict(
        exterior=[[-1500, -400], [XR, -400], [XR, H], [XC, H], [0, 0], [-1500, 0]],
        limites=[[[0, 0], [XR, 0]]],
        materiales_en=[{"punto": [2000, 300], "material": "Desmonte Leps41"},
                       {"punto": [1000, -200], "material": "Roca"}]),
    busqueda=dict(tipo="auto-refine", limites=[-1500, XR]),
    metodos=["bishop", "spencer"],
    escenarios=escenarios,
    vista=dict(xlim=[-800, 4200], ylim=[-400, 1100]),
)
yr = XR * math.tan(math.radians(THETA))
g2 = dict(
    nombre="Ladera 10 grados",
    geometria=dict(
        exterior=[[-1500, -400], [XR, -400], [XR, yr], [XE, H], [XC, H], [0, 0], [-1500, 0]],
        limites=[[[0, 0], [XE, H]]],
        materiales_en=[{"punto": [1500, 500], "material": "Desmonte Leps41"},
                       {"punto": [1000, -200], "material": "Roca"}]),
    busqueda=dict(tipo="sa", limites=[-1500, XE], parametros={"optimize": 1}),
    metodos=["janbu-simplificado", "janbu-corregido", "spencer", "gle"],
    escenarios=escenarios,
    vista=dict(xlim=[-800, 4200], ylim=[-400, 1100]),
)

desc = dict(
    nombre="Botadero_700m_verificacion",
    titulo="Botadero genérico de 700 m: verificación de FS con envolventes Leps 2.0",
    unidades="metric",
    direccion="der-izq",
    materiales=materiales,
    funciones=FUNCIONES,
    grupos=[g1, g2],
)
out = Path(__file__).with_name("botadero_700m.yaml")
out.write_text(yaml.safe_dump(desc, allow_unicode=True, sort_keys=False), encoding="utf-8")
print("escrito", out, "| a41 =", round(a41, 4), "a38 =", round(a38, 4))


