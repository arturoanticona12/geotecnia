"""Memorándum del EoR, revisión 2 (2026-10-09): sensibilidades pedidas por los revisores (EoR Piteau, Stantec LE2, Antamina).
Todas con Leps 2.0 de Antamina sin ajuste de escala, tope φ′s ≤ 37° (ángulo de reposo) y Morgenstern–Price con SA no circular:
  700 m (límites de búsqueda de siempre): opción 2 con e = 0.65 (base), e = 0.55, perfil e(z) A (compresibilidad corregida),
           perfil e(z) V (Valenzuela), curva de mármol (m = 0.90) y opción 2 con m = 0.845 (mediana mundial);
  150, 400 y 700 m con superficie global forzada (entrada en la plataforma, salida cerca del pie): opción 2 con y sin tope.
γ = 17.17 kN/m³ (e = 0.65) en todos los casos (los perfiles e(z) cambian la resistencia, no el peso). Escribe eor2/*.yaml y claves.json."""
import json, math, sys
from pathlib import Path
import numpy as np
from generar_yaml_lepsp4 import GAM, escribir, grupo, tb
from generar_yaml_lepsp6 import fun

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"; sys.path.insert(0, str(AA))
import a13_perfil_e as PE  # noqa: E402  (perfiles e(σ′v) corregidos)
S0, CAP, OM = 1.013, 37.0, 20.0
A12 = json.load(open(AA / "a12_leps2_ponderada.json", encoding="utf-8"))
OP2 = A12["curvas"]["Curva propuesta (mediana mundial)"]["pe0"]; MC = A12["curvas"]["Curva propuesta (mediana mundial)"]["m"]; OP2_084 = A12["curvas"]["Mundial P10"]; MAR = A12["marmol"]["central"]["pe0"]
sn = np.geomspace(0.02, 8.0, 81)
tau = lambda pe0, m, e: np.tan(np.radians(pe0 - OM * np.asarray(e))) * S0 ** (1 - m) * sn ** m
tope = lambda t: np.minimum(t, sn * math.tan(math.radians(CAP)))
CURVAS = {"base e065": tope(tau(OP2, MC, 0.65)), "e055": tope(tau(OP2, MC, 0.55)), "perfil A": tope(tau(OP2, MC, PE.e_A(sn))),
          "perfil V": tope(tau(OP2, MC, PE.eV_of_sv(sn))), "marmol": tope(tau(MAR, MC, 0.65)), "m084": tope(tau(OP2_084["pe0"], OP2_084["m"], 0.65)),
          "base libre": tau(OP2, MC, 0.65), "e055 libre": tau(OP2, MC, 0.55), "perfil A libre": tau(OP2, MC, PE.e_A(sn)),
          "perfil V libre": tau(OP2, MC, PE.eV_of_sv(sn)), "marmol libre": tau(MAR, MC, 0.65),
          "m084 libre": tau(OP2_084["pe0"], OP2_084["m"], 0.65)}
OUT = AQ / "eor2"; OUT.mkdir(exist_ok=True); CLAVE = {}


E_GAM = 0.65                                      # e con que se calcula γ (todas las curvas de un lote usan el γ del caso base)


def modelo(nombre, H, claves, forzar, tipo="sa"):
    fs = {k: fun(sn, CURVAS[k]) for k in claves}; mats = []
    for k in claves:
        mats.append(dict(nombre=f"D {k}", gamma=GAM(E_GAM), modelo="funcion", funcion=k, agua="ninguna", resistencia_txt=f"Leps 2.0 Antamina {k}"))
        CLAVE[f"{nombre}|{k}"] = k
    base = mats[0]["nombre"]; escs = [dict(nombre=base[2:])] + [dict(nombre=m["nombre"][2:], reasignar={base: m["nombre"]}) for m in mats[1:]]
    g = grupo(H, base, escs, f"H{H:.0f}"); g["busqueda"]["tipo"] = tipo
    if forzar:                                    # salida entre −0.3H y 0.05H (pie), entrada en la plataforma (XC a XC + 0.8H)
        XC = H / tb; g["busqueda"]["limites"] = [-0.3 * H, 0.05 * H, XC, XC + 0.8 * H]
    escribir(nombre, fs, mats, [g], OUT)


if "92" in sys.argv:          # revisión 9 (2026-10-12): curva ajustada con todos los ensayos con igual peso (opción B); sin mármol
    EB = 0.45; E_GAM = EB; OUT = AQ / "eor7"; OUT.mkdir(exist_ok=True)
    CURVAS = {"base libre": tau(OP2, MC, EB), "e055 libre": tau(OP2, MC, 0.55), "e065 libre": tau(OP2, MC, 0.65),
              "perfil A libre": tau(OP2, MC, PE.e_A(sn)), "perfil V libre": tau(OP2, MC, PE.eV_of_sv(sn)),
              "m084 libre": tau(OP2_084["pe0"], OP2_084["m"], EB), "base tope": tope(tau(OP2, MC, EB))}
    assert abs(PE.E_TOP - EB) < 1e-9, "a13 debe partir de la e base"
    modelo("eor7_H700", 700.0, ["base libre", "e055 libre", "e065 libre", "perfil A libre", "perfil V libre", "m084 libre", "base tope"], False)
    modelo("eor7_cuckoo_H700", 700.0, ["base libre"], False, "cuckoo")
    modelo("eor7_pso_H700", 700.0, ["base libre"], False, "pso")
    for H in (150.0, 400.0, 700.0):
        modelo(f"eor7_global_H{H:.0f}", H, ["base libre", "base tope"], True)
    for H in (150.0, 400.0):
        modelo(f"eor7_libre_H{H:.0f}", H, ["base libre", "base tope"], False)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(print("lote 92 en", OUT, "| e base", EB, "| γ", GAM(EB), "| φ′e=0", round(OP2, 2), "| m", round(MC, 3)))
if "82" in sys.argv:          # revisión 8 (2026-10-10): e base 0.45, coherente con γ = 19.6 kN/m³ del DDE; 0.55 y 0.65 como sensibilidad
    EB = 0.45; E_GAM = EB; OUT = AQ / "eor6"; OUT.mkdir(exist_ok=True)
    CURVAS = {"base libre": tau(OP2, MC, EB), "e055 libre": tau(OP2, MC, 0.55), "e065 libre": tau(OP2, MC, 0.65),
              "perfil A libre": tau(OP2, MC, PE.e_A(sn)), "perfil V libre": tau(OP2, MC, PE.eV_of_sv(sn)),
              "m084 libre": tau(OP2_084["pe0"], OP2_084["m"], EB), "marmol libre": tau(MAR, MC, EB), "base tope": tope(tau(OP2, MC, EB))}
    assert abs(PE.E_TOP - EB) < 1e-9, "a13 debe partir de la e base"
    modelo("eor6_H700", 700.0, ["base libre", "e055 libre", "e065 libre", "perfil A libre", "perfil V libre", "m084 libre", "marmol libre", "base tope"], False)
    modelo("eor6_cuckoo_H700", 700.0, ["base libre"], False, "cuckoo")
    modelo("eor6_pso_H700", 700.0, ["base libre"], False, "pso")
    for H in (150.0, 400.0, 700.0):
        modelo(f"eor6_global_H{H:.0f}", H, ["base libre", "base tope"], True)
    for H in (150.0, 400.0):
        modelo(f"eor6_libre_H{H:.0f}", H, ["base libre", "base tope"], False)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(print("lote 82 en", OUT, "| e base", EB, "| γ", GAM(EB), "| φ′e=0", round(OP2, 2), "| m", round(MC, 3), "| mármol", round(MAR, 2)))
if "81" in sys.argv:          # revisión 7: m de la base mundial (mediana); «m084 libre» es ahora la curva con m = P10 mundial
    OUT = AQ / "eor5"; OUT.mkdir(exist_ok=True)
    modelo("eor5_H700", 700.0, ["base libre", "e055 libre", "perfil A libre", "perfil V libre", "m084 libre", "marmol libre", "base e065"], False)
    modelo("eor5_cuckoo_H700", 700.0, ["base libre"], False, "cuckoo")
    modelo("eor5_pso_H700", 700.0, ["base libre"], False, "pso")
    for H in (150.0, 400.0, 700.0):
        modelo(f"eor5_global_H{H:.0f}", H, ["base libre", "base e065"], True)
    for H in (150.0, 400.0):
        modelo(f"eor5_libre_H{H:.0f}", H, ["base libre", "base e065"], False)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(print("lote 81 en", OUT, "| φ′e=0", round(OP2, 2), "| m", round(MC, 3), "| mármol", round(MAR, 2), "| m P10", round(OP2_084["m"], 3)))
if "79" in sys.argv:          # revisión 5: curvas con el corte directo de Anddes (2024) en el ajuste; mismos casos que la revisión 3
    OUT = AQ / "eor4"; OUT.mkdir(exist_ok=True)
    modelo("eor4_H700", 700.0, ["base libre", "e055 libre", "perfil A libre", "perfil V libre", "m084 libre", "marmol libre", "base e065"], False)
    modelo("eor4_cuckoo_H700", 700.0, ["base libre"], False, "cuckoo")
    modelo("eor4_pso_H700", 700.0, ["base libre"], False, "pso")
    for H in (150.0, 400.0, 700.0):
        modelo(f"eor4_global_H{H:.0f}", H, ["base libre", "base e065"], True)
    for H in (150.0, 400.0):
        modelo(f"eor4_libre_H{H:.0f}", H, ["base libre", "base e065"], False)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(print("lote 79 en", OUT, "| φ′e=0 opción 2", round(OP2, 2), "| mármol", round(MAR, 2)))
if "77" in sys.argv:          # lote 77: revisión 3 (margas y caliza con la resistencia del mármol), todo con la curva vigente
    OUT = AQ / "eor3"; OUT.mkdir(exist_ok=True)
    modelo("eor3_H700", 700.0, ["base libre", "e055 libre", "perfil A libre", "perfil V libre", "m084 libre", "marmol libre", "base e065"], False)
    modelo("eor3_cuckoo_H700", 700.0, ["base libre"], False, "cuckoo")      # control de convergencia de la búsqueda
    modelo("eor3_pso_H700", 700.0, ["base libre"], False, "pso")
    for H in (150.0, 400.0, 700.0):
        modelo(f"eor3_global_H{H:.0f}", H, ["base libre", "base e065"], True)
    for H in (150.0, 400.0):
        modelo(f"eor3_libre_H{H:.0f}", H, ["base libre", "base e065"], False)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(print("lote 77 en", OUT, "| φ′e=0 opción 2", round(OP2, 2), "| mármol", round(MAR, 2)))
if "76" in sys.argv:          # lote 76: mármol y m = 0.84 sin tope (el usuario quitó el tope, 2026-10-09)
    OUT = AQ / "eor2c"; OUT.mkdir(exist_ok=True)
    modelo("eor2c_H700", 700.0, ["marmol libre", "m084 libre"], False)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8"); sys.exit(print("lote 76 en", OUT))
if "75" in sys.argv:          # lote 75: FS global sin tope (el tope cambia la falla global ≤ 0.003; lote 74)
    OUT = AQ / "eor2b"; OUT.mkdir(exist_ok=True)
    modelo("eor2b_H700", 700.0, ["e055 libre", "perfil A libre", "perfil V libre", "base libre"], False)
    (OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8"); sys.exit(print("lote 75 en", OUT))
modelo("eor2_H700", 700.0, ["base e065", "e055", "perfil A", "perfil V", "marmol", "m084"], False)
for H in (150.0, 400.0, 700.0):
    modelo(f"eor2_global_H{H:.0f}", H, ["base e065", "base libre"], True)
(OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
print("4 modelos,", len(CLAVE), "escenarios en", OUT, "| φ′e=0 opción 2", round(OP2, 2), "| mármol", round(MAR, 2), "| Cc", round(PE.CC1, 3), round(PE.CC2, 3))
