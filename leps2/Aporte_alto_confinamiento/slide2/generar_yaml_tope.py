"""Efecto del tope de 37° (ángulo de reposo) en el FS de botaderos de Antamina (memorándum del EoR, 2026-10-09).
Curvas Leps 2.0 de Antamina con m = 0.90 a e = 0.65 (a12_leps2_ponderada.json y a10_leps2_curvatura.json):
opción 1 (cada ensayo pesa igual) y opción 2 (ponderada por LE2), cada una con y sin tope φ′s ≤ 37°.
Geometría y búsqueda de los análisis anteriores (generar_yaml_lepsp4.grupo: talud global 2H:1V, fundación competente
horizontal, SA no circular optimizada, Morgenstern–Price), alturas 150, 400 y 700 m; γ = 17.17 kN/m³ (e = 0.65).
Tabla σ′n–τ de 0.02 a 8 MPa (fun de generar_yaml_lepsp6, cada dos puntos). Escribe tope/*.yaml y claves.json."""
import json, math
from pathlib import Path
import numpy as np
from generar_yaml_lepsp4 import GAM, escribir, grupo
from generar_yaml_lepsp6 import fun

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"; S0 = 1.013; CAP = 37.0; E = 0.65
PE0 = {"op1": json.load(open(AA / "a10_leps2_curvatura.json", encoding="utf-8"))["curvas"]["Leps 2.0 (m = 0.90)"]["pe0"],
       "op2": json.load(open(AA / "a12_leps2_ponderada.json", encoding="utf-8"))["curvas"]["Leps 2.0 (m = 0.90)"]["pe0"]}
sn = np.geomspace(0.02, 8.0, 81)
OUT = AQ / "tope"; OUT.mkdir(exist_ok=True); CLAVE = {}
for H in (150.0, 400.0, 700.0):
    funciones, mats = {}, []
    for op, pe0 in PE0.items():
        tau = math.tan(math.radians(pe0 - 20 * E)) * S0 ** 0.1 * sn ** 0.9
        for tope in (False, True):
            t = np.minimum(tau, sn * math.tan(math.radians(CAP))) if tope else tau
            cod = f"{op} {'tope' if tope else 'libre'}"; funciones[cod] = fun(sn, t); CLAVE[f"{H:.0f}|{cod}"] = cod
            mats.append(dict(nombre=f"D {cod}", gamma=GAM(E), modelo="funcion", funcion=cod, agua="ninguna", resistencia_txt=f"Leps 2.0 Antamina {cod}"))
    base = mats[0]["nombre"]
    escs = [dict(nombre=base[2:])] + [dict(nombre=m["nombre"][2:], reasignar={base: m["nombre"]}) for m in mats[1:]]
    escribir(f"tope_H{H:.0f}", funciones, mats, [grupo(H, base, escs, f"H{H:.0f}")], OUT)
(OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
print("3 modelos, 12 escenarios en", OUT, "| φ′e=0:", {k: round(v, 2) for k, v in PE0.items()})
