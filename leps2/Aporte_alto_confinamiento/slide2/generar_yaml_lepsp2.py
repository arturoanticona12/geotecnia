"""Leps-P, estabilidad (ronda 2): botadero de 700 m sobre ladera de 10° con capa basal saturada de 30 m que NO aflora en el
pie (desde x = 150 m; el pie se apoya en roca). Presión de poros: malla u(x, z) de consolidación con carga en rampa
(analisis/consol2.py) para un barrido de k y velocidad de carga R. Resistencia drenada de Leps-P (P50 y P05 de la envolvente
media del botadero) en el desmonte y en la capa basal. Sensibilidad no drenada: Su = r·σ′v efectivo (coherente con u).
Búsqueda no circular por recocido simulado sin restricción; para los casos no drenados, además, mínimo con entrada en la
plataforma (x ≥ cresta). Escribe un .yaml por velocidad R (para correr en paralelo) y uno para los casos no drenados."""
import json, math, sys
from pathlib import Path
import yaml
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from consol2 import malla  # noqa: E402

F = json.load(open(AQ.parent / "analisis" / "lepsp_funciones_slide2.json", encoding="utf-8"))
FUN = {"Sitio P50": F["e=0.65 P50"], "Sitio P05": F["e=0.65 P05"]}            # botadero, densidad de campo, escala general
FUN = {k: [[round(a, 2), round(b, 2)] for a, b in v] for k, v in FUN.items()}
GAM = 21.0; H, BETA, THETA, HB, X0B = 700.0, 26.57, 10.0, 30.0, 150.0
tb, tt = math.tan(math.radians(BETA)), math.tan(math.radians(THETA)); XC = H / tb; XE = H / tt; XR = XE + 1500; yr = XR * tt
xb1 = (H - HB) / tt
geo = dict(top=lambda x: min(max(x * tb, 0.0), H), fnd=lambda x: x * tt, x0=X0B, x1=xb1 - 50)


def geometria(basal):
    return dict(exterior=[[-1500, -400], [XR, -400], [XR, yr], [XE, H], [XC, H], [0, 0], [-1500, 0]],
                limites=[[[0, 0], [XE, H]], [[X0B, X0B * tt], [X0B, X0B * tt + HB], [xb1, H]]],
                materiales_en=[{"punto": [1500, 500], "material": "Desmonte Sitio P50"},
                               {"punto": [1500, 1500 * tt + HB / 2], "material": basal},
                               {"punto": [1000, -200], "material": "Roca"}])


# la malla de presiones se asigna solo a la capa basal (agua: presiones); desmonte y roca secos (lote 62 sin esto: FS = 0)
materiales = [dict(nombre=f"Desmonte {k}", gamma=GAM, modelo="funcion", funcion=k, agua="ninguna", resistencia_txt=f"Leps-P, site waste rock, {k[-3:]}") for k in FUN]
materiales += [dict(nombre=f"Basal {k}", gamma=GAM, modelo="funcion", funcion=k, resistencia_txt=f"Basal layer, Leps-P {k[-3:]}") for k in FUN]
materiales += [dict(nombre="Roca", gamma=26, modelo="mohr-coulomb", c=1000, phi=45, agua="ninguna")]
SA_LIBRE = dict(tipo="sa", limites=[-1500, XE], parametros={"optimize": 1})
SA_PLAT = dict(tipo="sa", limites=[-300, 150, XC, XE - 200], parametros={"optimize": 1})
ESC = [dict(nombre="P50"), dict(nombre="P05", reasignar={"Desmonte Sitio P50": "Desmonte Sitio P05", "Basal Sitio P50": "Basal Sitio P05"})]


def escribir(nombre, grupos, extra_mat=(), fdisc=None):
    desc = dict(nombre=nombre, titulo="Leps-P: pore pressure sweep", unidades="metric", direccion="der-izq",
                materiales=materiales + list(extra_mat), funciones=FUN, grupos=grupos)
    if fdisc:
        desc["funciones_discretas"] = fdisc
    (AQ / f"{nombre}.yaml").write_text(yaml.safe_dump(desc, allow_unicode=True, sort_keys=False), encoding="utf-8")


KS = (1e-6, 1e-7, 1e-8, 1e-9); RS = (25, 100, 300, 600)
for R in RS:
    grupos = []
    for k in KS:
        P, _ = malla(geo, k, R)
        grupos.append(dict(nombre=f"R{R} k{k:.0e}", geometria=geometria("Basal Sitio P50"), agua=dict(metodo="presiones", puntos=P),
                           busqueda=SA_LIBRE, metodos=["spencer", "gle"], escenarios=ESC, vista=dict(xlim=[-800, 4200], ylim=[-400, 1100])))
    escribir(f"lepsp_u_R{R}", grupos)
# ---- no drenado: Su = r σ′v (σ′v coherente con u de dos estados) — material discreto con puntos en toda la capa
fdisc, extra, grupos = {}, [], []
for (R, k) in [(25, 1e-6), (100, 1e-8), (600, 1e-8)]:
    P, S = malla(geo, k, R)
    for r in (0.17, 0.09):
        nm = f"Su r{r} R{R} k{k:.0e}"
        fdisc[nm] = dict(tipo="no-drenado", puntos=[[x, y, round(max(r * s, 1.0), 1)] for x, y, s in S])
        extra.append(dict(nombre=f"Basal {nm}", gamma=GAM, modelo="discreta", funcion=nm, resistencia_txt=f"Undrained basal layer, Su = {r} sigma'v"))
        for bus, etq in ((SA_LIBRE, "libre"), (SA_PLAT, "plataforma")):
            grupos.append(dict(nombre=f"{nm} {etq}", geometria=geometria(f"Basal {nm}"), busqueda=bus, metodos=["spencer", "gle"],
                               escenarios=[dict(nombre="P50")], vista=dict(xlim=[-800, 4200], ylim=[-400, 1100])))
escribir("lepsp_nodrenado2", grupos, extra, fdisc)
print("escritos:", [f"lepsp_u_R{R}.yaml" for R in RS] + ["lepsp_nodrenado2.yaml"])
