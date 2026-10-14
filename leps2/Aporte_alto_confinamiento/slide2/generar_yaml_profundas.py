"""Fallas profundas (σ′n alto) en secciones típicas de botadero de 720 m, para el anexo del memo (2026-10-10): modos profundos de
Hawley y Cunning (2017, §8.4.1.2 y §8.4.2) que dependen de la resistencia del desmonte a alto confinamiento. Desmonte con la curva
propuesta de Leps 2.0 (e = 0.45, función τ–σ′n hasta 15 MPa); morrena drenada y roca de la Tabla 9-3 del DDE. Bancos de 60 m,
bermas de 50 m, caras 1.33H:1V (12 bancos). Morgenstern–Price, SA no circular optimizada, dos búsquedas forzadas:
  global    entrada en la plataforma desde la cresta (xc a xc + H) y salida entre −0.3H y +0.05H del pie;
  profunda  entrada a más de 0.5H detrás de la cresta (xc + 0.5H a xc + 1.5H, o hasta el contacto con la ladera).
Secciones (geometrías supuestas, no del sitio):
  P1  fundación horizontal de roca                          -> rotacional profunda
  P2  5 m de morrena horizontal sobre roca; seca y saturada -> compuesta por la base
  P3  ladera de 15° con 10 m de morrena; seca y con agua bajo la huella -> traslación de la base
  P4  ladera de 20° con 5 m de morrena; seca y con agua bajo la huella  -> cuña
Un modelo seco y uno saturado por sección. Escribe profundas/*.yaml y geometria.json (superficie de la fundación por sección)."""
import json, math
from pathlib import Path
import numpy as np
import yaml

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"; OUT = AQ / "profundas"; OUT.mkdir(exist_ok=True)
A12 = json.load(open(AA / "a12_leps2_ponderada.json", encoding="utf-8"))
C = A12["curvas"]["Curva propuesta (mediana mundial)"]; PE0, M = C["pe0"], C["m"]
S0, OM, EB, GS, W, GW = 1.013, 20.0, 0.45, 2.75, 0.05, 9.81
GAM = round(GS * GW * (1 + W) / (1 + EB), 2); GSAT = round((GS + EB) / (1 + EB) * GW, 2)
sn = np.geomspace(0.002, 15.0, 91)
tau = np.tan(np.radians(PE0 - OM * EB)) * S0 ** (1 - M) * sn ** M
FUN = {"Leps2 e045": [[0.0, 0.0]] + [[round(float(s) * 1000, 2), round(float(t) * 1000, 2)] for s, t in zip(sn[::2], tau[::2])]}
_DES = dict(gamma=GAM, gamma_sat=GSAT, modelo="funcion", funcion="Leps2 e045", resistencia_txt=f"Leps 2.0, curva propuesta (e = {EB:.2f})")
_MOR = dict(gamma=21.0, modelo="mohr-coulomb", c=0, phi=33, resistencia_txt="c′ = 0, φ′ = 33° (DDE, Tabla 9-3)")
ROCA = dict(nombre="Roca", gamma=26.7, modelo="mohr-coulomb", c=1000, phi=45, agua="ninguna", resistencia_txt="c = 1000 kPa, φ = 45° (DDE, Tabla 9-3)")
MATS = {"seco": [dict(nombre="Desmonte ROM", agua="ninguna", **_DES), dict(nombre="Morrena", agua="ninguna", **_MOR), ROCA],
        "saturado": [dict(nombre="Desmonte ROM", agua="nf", **_DES), dict(nombre="Morrena", agua="nf", **_MOR), ROCA]}
HB, CARA, BERMA, NB = 60.0, 1.333, 50.0, 12
H = HB * NB


def bancos():
    p = [(0.0, 0.0)]; x = y = 0.0
    for i in range(NB):
        x += HB * CARA; y += HB; p.append((x, y))
        if i < NB - 1:
            x += BERMA; p.append((x, y))
    return p


r = lambda p: [[round(a, 2), round(b, 2)] for a, b in p]
SUP = bancos(); XC = SUP[-1][0]


def seccion(t, alfa, xl=-600.0, prof=400.0):
    """Morrena de espesor vertical t (0 = sin capa) sobre roca; fundación horizontal (alfa = 0) o inclinada alfa."""
    ta = math.tan(math.radians(alfa)); yf = lambda x: x * ta
    xi = H / ta if alfa > 0 else XC + 1.6 * H; xr = xi + (400.0 if alfa > 0 else 0.0)
    ybot = yf(xl) - t - prof
    techo = [(xr, yf(xr) - t)] + (([(xi, H)] if alfa > 0 else []) + [(0.0, 0.0)] if t == 0 else []) + [(xl, yf(xl) - t)]  # vértices compartidos
    reg = [dict(material="Roca", poligono=r([(xl, ybot), (xr, ybot)] + techo))]
    if t > 0:
        top = [(xr, yf(xr))] + ([(xi, H)] if alfa > 0 else []) + [(0.0, 0.0), (xl, yf(xl))]
        reg.append(dict(material="Morrena", poligono=r([(xl, yf(xl) - t), (xr, yf(xr) - t)] + top)))
    reg.append(dict(material="Desmonte ROM", poligono=r(SUP + ([(xi, H)] if alfa > 0 else [(xr, H), (xr, 0.0)]))))
    return dict(regiones=reg), xl, xr, xi, yf


def nf(xl, xr, xi, t, alfa):
    """Saturado: en fundación horizontal, nivel freático en el techo de la morrena en todo el modelo; en ladera, solo bajo la
    huella del botadero y en la base de la morrena fuera de ella (presión de poros que la carga no deja disipar)."""
    ta = math.tan(math.radians(alfa)); yf = lambda x: x * ta
    if alfa == 0:
        return dict(metodo="hu", nivel_freatico=[[xl, 0.0], [xr, 0.0]])
    d = t - 0.2
    return dict(metodo="hu", nivel_freatico=r([(xl, yf(xl) - d), (-2.0, yf(-2.0) - d), (0.0, 0.0), (xi, H), (xi + 2.0, yf(xi + 2.0) - d), (xr, yf(xr) - d)]))


import sys
sa = lambda l: dict(tipo="sa", limites=[round(v, 1) for v in l], parametros={"optimize": 1})
if sys.argv[1:2] == ["entradas"]:  # lotes 90 y 91: roca horizontal, entrada forzada a distancias crecientes detrás de la cresta
    LARGO = sys.argv[2:] == ["largas"]
    OUT = AQ / ("profundas_entradas_largas" if LARGO else "profundas_entradas"); OUT.mkdir(exist_ok=True)
    KS = (3.0, 4.0, 5.0) if LARGO else (0.25, 0.5, 1.0, 1.5, 2.0)
    geo, xl, xr, xi, yf = seccion(0.0, 0.0)
    xr2 = XC + (KS[-1] + 0.6) * H                       # plataforma más larga que la entrada más lejana
    for rg in geo["regiones"]:
        rg["poligono"] = [[xr2 if abs(p[0] - xr) < 0.01 else p[0], p[1]] for p in rg["poligono"]]
    escs = [dict(nombre=f"Seco, entrada a {k:g}H", busqueda=sa([-0.3 * H, 0.05 * H, XC + (k - 0.05) * H, XC + (k + 0.05) * H])) for k in KS]
    g = dict(nombre="R0 roca horizontal", etiqueta=f"Bancos, {H:.0f} m; fundación horizontal de roca", geometria=geo, busqueda=escs[0]["busqueda"],
             metodos=["gle"], vista=dict(xlim=[-600, 3800], ylim=[-500, 1700]) if not LARGO else dict(xlim=[-600, 6000], ylim=[-500, 2800]), escenarios=escs)
    desc = dict(nombre="prof_R0_entradas", titulo="Fallas profundas forzadas (roca horizontal)", unidades="metric", direccion="der-izq",
                materiales=MATS["seco"], funciones=FUN, grupos=[g])
    (OUT / "prof_R0_entradas.yaml").write_text(yaml.safe_dump(desc, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (OUT / "geometria.json").write_text(json.dumps(dict(secciones={"R0 roca horizontal": dict(alfa=0.0, t=0.0, xi=xr2, H=H)}, gam=GAM, gsat=GSAT,
                                                       gamma_morrena=21.0), indent=1, ensure_ascii=False), encoding="utf-8")
    print("entradas:", [round(XC + k * H) for k in KS], "xr", round(xr2)); sys.exit()
if sys.argv[1:] == ["roca"]:      # lote 89: fundación de roca, para que la superficie profunda corte el desmonte (σ′n alta en el desmonte)
    OUT = AQ / "profundas_roca"; OUT.mkdir(exist_ok=True)
    SECC = [("R0 roca horizontal", "Fundación horizontal de roca", 0.0, 0.0, False),
            ("R10 roca ladera 10", "Ladera de roca de 10°", 0.0, 10.0, False),
            ("R20 roca ladera 20", "Ladera de roca de 20°", 0.0, 20.0, False)]
else:                             # lote 88: fundación con morrena (la superficie busca la fundación)
    SECC = [("P1 roca", "Fundación horizontal de roca", 0.0, 0.0, False),
            ("P2 morrena 5 m", "5 m de morrena horizontal sobre roca", 5.0, 0.0, True),
            ("P3 ladera 15", "Ladera de 15° con 10 m de morrena", 10.0, 15.0, True),
            ("P4 ladera 20", "Ladera de 20° con 5 m de morrena", 5.0, 20.0, True)]
sa = lambda l: dict(tipo="sa", limites=[round(v, 1) for v in l], parametros={"optimize": 1})
GEO = {}
for nom, et, t, alfa, con_agua in SECC:
    geo, xl, xr, xi, yf = seccion(t, alfa)
    xtop = min(XC + 1.5 * H, xi + (100.0 if alfa > 0 else 0.0))
    busq = {"global": sa([-0.3 * H, 0.05 * H, XC, min(XC + H, xtop)]), "profunda": sa([-0.3 * H, 0.05 * H, XC + 0.5 * H, xtop])}
    GEO[nom] = dict(alfa=alfa, t=t, xi=xi, H=H)
    for cond in (("seco", "saturado") if con_agua else ("seco",)):
        escs = [dict(nombre=f"{'Seco' if cond == 'seco' else 'Saturado'}, {b}", busqueda=q) for b, q in busq.items()]
        g = dict(nombre=nom, etiqueta=f"Bancos, {H:.0f} m; {et}", geometria=geo, busqueda=busq["global"], metodos=["gle"],
                 vista=dict(xlim=[-600, 3000], ylim=[-500, 1300]) if xi < 2700 else dict(xlim=[-600, 4600], ylim=[-500, 2100]), escenarios=escs)
        if cond == "saturado":
            g["agua"] = nf(xl, xr, xi, t, alfa)
        desc = dict(nombre=f"prof_{nom.split()[0]}_{cond}", titulo="Fallas profundas en secciones tipicas (Hawley y Cunning 2017, 8.4)",
                    unidades="metric", direccion="der-izq", materiales=MATS[cond], funciones=FUN, grupos=[g])
        (OUT / f"prof_{nom.split()[0]}_{cond}.yaml").write_text(yaml.safe_dump(desc, allow_unicode=True, sort_keys=False), encoding="utf-8")
(OUT / "geometria.json").write_text(json.dumps(dict(secciones=GEO, gam=GAM, gsat=GSAT, gamma_morrena=21.0), indent=1, ensure_ascii=False), encoding="utf-8")
print(f"{len(list(OUT.glob('*.yaml')))} modelos en {OUT} | H {H:.0f} m, cresta x = {XC:.0f} | γ {GAM} γsat {GSAT}")
