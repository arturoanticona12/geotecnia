"""Leps-P, ronda 6 (revisor R3): mecanismos de alto confinamiento, donde la forma de la envolvente importa.
Botadero de altura H con talud global 2H:1V, solo Morgenstern–Price (GLE, medio seno) y búsqueda no circular por recocido
simulado con optimización. Geometrías:
  comp     — fundación competente horizontal (referencia de la ronda 5);
  debil25/30 — capa de fundación débil de 10 m bajo el botadero (c′ = 0, φ′ = 25° o 30°) sobre roca competente;
  inc10/20 — fundación competente inclinada 10° o 20° hacia el pie (relleno de valle);
  agua100  — nivel freático basal 100 m sobre la base, que sale por la cara (Hu = 1 en el desmonte; envolventes drenadas).
Envolventes (pares σ′n–τ tabulados hasta 8 MPa; por encima, la extrapolación lineal de Slide2 queda declarada):
  dump-average del sitio con la forma acotada (P50, P05), la cuadrática (P50, P05), Leps 2.0 (m = 0.9, mediana) y la forma
  acotada con φ′∞ en los extremos del perfil (P05). Uso: python generar_yaml_lepsp6.py [prueba] → alto6/*.yaml"""
import json, math, sys
from pathlib import Path
import numpy as np
import yaml
from generar_yaml_lepsp4 import GAM, escribir

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"
BETA = 26.57; tb = math.tan(math.radians(BETA)); SN_MAX = 8.0


def fun(sn, t, sn_max=SN_MAX):
    """Pares [σ′n, τ] en kPa desde el origen, cada dos puntos de la grilla, hasta sn_max MPa."""
    k = sn <= sn_max + 1e-9
    return [[0.0, 0.0]] + [[round(float(s) * 1000, 2), round(float(v) * 1000, 2)] for s, v in zip(sn[k][::2], t[k][::2])]


def geometria(H, tipo):
    XC = H / tb; XR = XC + 3.0 * H; yb = -0.5 * H
    if tipo in ("comp", "agua100"):
        g = dict(exterior=[[-2.0 * H, yb], [XR, yb], [XR, H], [XC, H], [0, 0], [-2.0 * H, 0]], limites=[[[0, 0], [XR, 0]]],
                 materiales_en=[{"punto": [XC, H / 2], "material": "DUMP"}, {"punto": [XC, -0.25 * H], "material": "Roca"}])
        return g, [-1.5 * H, XR]
    if tipo.startswith("debil"):
        t = 10.0
        g = dict(exterior=[[-2.0 * H, yb], [XR, yb], [XR, H], [XC, H], [0, 0], [-2.0 * H, 0]],
                 limites=[[[0, 0], [XR, 0]], [[-2.0 * H, -t], [XR, -t]]],
                 materiales_en=[{"punto": [XC, H / 2], "material": "DUMP"}, {"punto": [XC, -t / 2], "material": "Debil"},
                                {"punto": [-H, -t / 2], "material": "Debil"}, {"punto": [XC, -0.25 * H], "material": "Roca"}])
        return g, [-1.5 * H, XR]
    th = math.tan(math.radians(float(tipo[3:])))                     # inc10, inc20
    xe = min(XR, H / th)                                              # el desmonte termina donde el terreno llega a la cota H
    xr = xe + 0.6 * H; xl = -1.5 * H; ybot = xl * th - 0.5 * H
    sup = [[xl, xl * th], [0, 0], [XC, H], [xe, H]] if xe < XR else [[xl, xl * th], [0, 0], [XC, H], [XR, H]]
    if xe >= XR:                                                      # terreno bajo la plataforma: cierre vertical en XR
        ext = [[xl, ybot], [XR, ybot], [XR, H], [XC, H], [0, 0], [xl, xl * th]]
        lim = [[[0, 0], [XR, XR * th]]]
    else:
        ext = [[xl, ybot], [xr, ybot], [xr, xr * th], [xe, H], [XC, H], [0, 0], [xl, xl * th]]
        lim = [[[0, 0], [xe, H]]]
    xm = 0.5 * XC; ym = 0.5 * (min(H, xm * tb) + xm * th)              # entre la cara del talud (y = x·tan β) y el terreno
    g = dict(exterior=ext, limites=lim, materiales_en=[{"punto": [xm, ym], "material": "DUMP"}, {"punto": [XC, XC * th - 0.25 * H], "material": "Roca"}])
    return g, [xl + 0.1 * H, (xr if xe < XR else XR) - 0.1 * H]


def grupo(H, tipo, base, escs):
    geo, lim = geometria(H, tipo)
    for m in geo["materiales_en"]:
        if m["material"] == "DUMP":
            m["material"] = base
    gr = dict(nombre=f"{tipo} H{H:.0f}", geometria=geo, busqueda=dict(tipo="sa", limites=lim, parametros={"optimize": 1}), metodos=["gle"],
              escenarios=escs, vista=dict(xlim=[-0.8 * H, H / tb + 1.6 * H], ylim=[-0.6 * H, 1.4 * H]))
    if tipo == "agua100":
        hw = 100.0; gr["agua"] = dict(metodo="hu", nivel_freatico=[[-2.0 * H, 0], [0, 0], [hw / tb, hw], [H / tb + 3.0 * H, hw]])
    return gr


def materiales_base(tipo):
    out = [dict(nombre="Roca", gamma=26, modelo="mohr-coulomb", c=1000, phi=45)]
    if tipo.startswith("debil"):
        out.append(dict(nombre="Debil", gamma=20, modelo="mohr-coulomb", c=0, phi=float(tipo[5:])))
    return out


if __name__ == "__main__":
    prueba = "prueba" in sys.argv
    if prueba:                                                       # control de geometría con las envolventes de la ronda 5
        Z = np.load(AA / "lepsp_sitio3_muestras_e065_general.npz"); sn = Z["sn"]; T = np.tensordot(Z["pesos"], Z["tau"], 1)
        ENV = {"B P50": np.percentile(T, 50, axis=0), "B P05": np.percentile(T, 5, axis=0)}
    else:
        E = np.load(AA / "lepsp6_envolventes_alto.npz"); sn = E["sn"]; ENV = {k: E[k] for k in E.files if k != "sn"}
    OUT = AQ / ("alto6_prueba" if prueba else "alto6"); OUT.mkdir(exist_ok=True); CLAVE = {}
    casos = [(700.0, t) for t in ("comp", "debil25", "debil30", "inc10", "inc20", "agua100")] + [(400.0, "debil25"), (400.0, "inc10")]
    for H, tipo in casos:
        funciones, mats = {}, []
        for nm, t in ENV.items():
            cod = f"{tipo[:3]}{int(H)} {nm}"[:20]; funciones[cod] = fun(sn, t); CLAVE[cod] = f"{tipo}|{H:.0f}|{nm}"
            agua = "nf" if tipo == "agua100" else "ninguna"
            mats.append(dict(nombre=f"D {cod}", gamma=GAM(0.65), modelo="funcion", funcion=cod, agua=agua, resistencia_txt=f"Leps-P {nm}"))
        base = mats[0]["nombre"]
        escs = [dict(nombre=base[2:])] + [dict(nombre=m["nombre"][2:], reasignar={base: m["nombre"]}) for m in mats[1:]]
        escribir(f"alto_{tipo}_H{H:.0f}", funciones, mats + materiales_base(tipo)[1:], [grupo(H, tipo, base, escs)], OUT)   # escribir() agrega la roca
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(casos), "modelos,", len(casos) * len(ENV), "escenarios en", OUT)
