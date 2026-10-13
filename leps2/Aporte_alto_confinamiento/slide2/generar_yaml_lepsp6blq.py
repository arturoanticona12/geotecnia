"""HiBER, ronda 6: verificación de los mecanismos de fundación débil con búsqueda por bloques (lote 72).
En el lote 70 la búsqueda no circular por recocido simulado (SA) encontró superficies que cruzaban la capa débil de 25° solo en
6–16 % de su base. Aquí se fuerza el deslizamiento a lo largo de la capa con Block Search (polilínea dentro de la capa, extremos
aleatorios, cuña activa y pasiva con ángulos aleatorios) y se agregan capas más débiles y una capa débil inclinada:
  debil15, debil20, debil25 — capa horizontal de 10 m (c′ = 0) bajo el botadero de 700 m, sobre roca competente;
  incdeb   — fundación inclinada 10° hacia el pie con una capa débil de 10 m paralela (φ′ = 20°).
Modelos: bloques en los cuatro casos y SA en los tres nuevos (debil15, debil20, incdeb), para comparar con el lote 70.
Envolventes del promedio del botadero: acotada P50 y P05, cuadrática P05 y Leps 2.0 publicado (lepsp6_envolventes_alto.npz).
Uso: python generar_yaml_lepsp6blq.py → bloques6/*.yaml + claves.json"""
import json, math
from pathlib import Path
import numpy as np
from generar_yaml_lepsp4 import GAM, escribir
from generar_yaml_lepsp6 import fun, geometria, tb

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"; H = 700.0; T_CAPA = 10.0; TH_INC = math.tan(math.radians(10.0))
ENVS = ("B P50", "B P05", "Q P05", "L2 P50")


def geometria_incdeb():
    g, lim = geometria(H, "inc10"); xl = -1.5 * H
    pts = [p for p in g["exterior"]]; xder = max(p[0] for p in pts)
    g["limites"] = g["limites"] + [[[xl, xl * TH_INC - T_CAPA], [xder, xder * TH_INC - T_CAPA]]]
    xm = 0.5 * H / tb; g["materiales_en"] = [m for m in g["materiales_en"] if m["material"] != "Roca"] + [
        {"punto": [xm, xm * TH_INC - T_CAPA / 2], "material": "Debil"}, {"punto": [xl / 2, xl / 2 * TH_INC - T_CAPA / 2], "material": "Debil"},
        {"punto": [xm, xm * TH_INC - 0.25 * H], "material": "Roca"}]
    return g, lim


def grupo(tipo, base, escs, bloques):
    g, lim = geometria_incdeb() if tipo == "incdeb" else geometria(H, tipo)
    for m in g["materiales_en"]:
        if m["material"] == "DUMP":
            m["material"] = base
    if bloques:
        th = TH_INC if tipo == "incdeb" else 0.0; x0, x1 = -0.4 * H, H / tb + 0.4 * H
        bus = dict(tipo="bloques", muestras=20000, angulo_izq=[110, 165], angulo_der=[15, 80], convexas=False, optimizar=False,
                   objetos=[dict(tipo="polilinea", puntos=[[x0, x0 * th - T_CAPA / 2], [x1, x1 * th - T_CAPA / 2]],
                                 extremo_izq="aleatorio", extremo_der="aleatorio")])
    else:
        bus = dict(tipo="sa", limites=lim, parametros={"optimize": 1})
    return dict(nombre=f"{tipo} {'bloques' if bloques else 'SA'}", geometria=g, busqueda=bus, metodos=["gle"], escenarios=escs,
                vista=dict(xlim=[-0.8 * H, H / tb + 1.6 * H], ylim=[-0.6 * H, 1.4 * H]))


if __name__ == "__main__":
    E = np.load(AA / "lepsp6_envolventes_alto.npz"); sn = E["sn"]
    OUT = AQ / "bloques6"; OUT.mkdir(exist_ok=True); CLAVE = {}; n = 0
    casos = [(t, True) for t in ("debil15", "debil20", "debil25", "incdeb")] + [(t, False) for t in ("debil15", "debil20", "incdeb")]
    for tipo, blq in casos:
        phi = 20.0 if tipo == "incdeb" else float(tipo[5:]); nombre = f"blq_{tipo}_{'B' if blq else 'SA'}"
        funciones, mats = {}, []
        for nm in ENVS:
            cod = f"{tipo[:3]}{tipo[-2:]}{'B' if blq else 'S'} {nm}"; funciones[cod] = fun(sn, E[nm]); CLAVE[f"{nombre}|{cod}"] = f"{tipo}|{'bloques' if blq else 'SA'}|{nm}"
            mats.append(dict(nombre=f"D {cod}", gamma=GAM(0.65), modelo="funcion", funcion=cod, agua="ninguna", resistencia_txt=f"HiBER {nm}"))
        base = mats[0]["nombre"]
        escs = [dict(nombre=base[2:])] + [dict(nombre=m["nombre"][2:], reasignar={base: m["nombre"]}) for m in mats[1:]]
        escribir(nombre, funciones, mats + [dict(nombre="Debil", gamma=20, modelo="mohr-coulomb", c=0, phi=phi)], [grupo(tipo, base, escs, blq)], OUT)
        n += len(escs)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(casos), "modelos,", n, "escenarios en", OUT)
