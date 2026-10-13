"""Secciones típicas de botadero de desmonte ROM para los modos de falla de Hawley y Cunning (2017, §8.4) que dependen de la
resistencia del desmonte y de la fundación (2026-10-10). Desmonte con la curva propuesta de Leps 2.0 (e = 0.45, función τ–σ′n),
morrena drenada y roca de la Tabla 9-3 del diseño geotécnico del DDE (Stantec 2026). Morgenstern–Price, SA no circular optimizada.
  A  bancos de 60 m, bermas de 50 m, cara 1.33H:1V, H = 420 m, sobre roca; y con 5 m de morrena   -> rotacional; compuesta por la base
  B  un solo lift a 37°, H = 200 m, sobre ladera de 30° con 5 m de morrena; seco y saturada       -> cuña (fundación > 25°, presión de poros)
  C  bancos, H = 420 m, sobre 40 m de morrena horizontal; seco y saturada                        -> rotacional por la fundación; carga de pie
  D  bancos, H = 420 m, sobre ladera de 15° con 10 m de morrena; seco y saturada                  -> traslación de la base
Geometrías supuestas (típicas), no secciones del sitio. Escribe tipicas/*.yaml y claves.json."""
import json, math, sys
from pathlib import Path
import numpy as np
import yaml

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"; OUT = AQ / "tipicas_v3"; OUT.mkdir(exist_ok=True)       # v3: secos y saturados separados; en ladera, agua bajo la huella (lote 87)
A12 = json.load(open(AA / "a12_leps2_ponderada.json", encoding="utf-8"))
C = A12["curvas"]["Curva propuesta (mediana mundial)"]; PE0, M = C["pe0"], C["m"]
S0, OM, EB, GS, W, GW = 1.013, 20.0, 0.45, 2.75, 0.05, 9.81
GAM = round(GS * GW * (1 + W) / (1 + EB), 2); GSAT = round((GS + EB) / (1 + EB) * GW, 2)
sn = np.geomspace(0.002, 8.0, 81)
tau = np.tan(np.radians(PE0 - OM * EB)) * S0 ** (1 - M) * sn ** M
FUN = {"Leps2 e045": [[0.0, 0.0]] + [[round(float(s) * 1000, 2), round(float(t) * 1000, 2)] for s, t in zip(sn[::2], tau[::2])]}
# materiales secos en la base; el escenario saturado los reasigna a las variantes con nivel freático (así las figuras de los
# casos secos no muestran un nivel freático ficticio bajo la roca)
_DES = dict(gamma=GAM, gamma_sat=GSAT, modelo="funcion", funcion="Leps2 e045", resistencia_txt=f"Leps 2.0, curva propuesta (e = {EB:.2f})")
_MOR = dict(gamma=21.0, modelo="mohr-coulomb", c=0, phi=33, resistencia_txt="c′ = 0, φ′ = 33° (DDE, Tabla 9-3)")
MATS_SAT = [dict(nombre="Desmonte ROM", agua="nf", **_DES), dict(nombre="Morrena", agua="nf", **_MOR)]   # modelos saturados
MATS = [dict(nombre="Desmonte ROM", agua="ninguna", **_DES), dict(nombre="Morrena", agua="ninguna", **_MOR),
        dict(nombre="Roca", gamma=26.7, modelo="mohr-coulomb", c=1000, phi=45, agua="ninguna", resistencia_txt="c = 1000 kPa, φ = 45° (DDE, Tabla 9-3)")]
HB, CARA, BERMA = 60.0, 1.333, 50.0


def bancos(n):
    """Superficie por bancos desde el pie (0, 0): cara de HB m a CARA:1 y berma de BERMA m; devuelve puntos y cresta."""
    p = [(0.0, 0.0)]; x = y = 0.0
    for i in range(n):
        x += HB * CARA; y += HB; p.append((x, y))
        if i < n - 1:
            x += BERMA; p.append((x, y))
    return p


def un_lift(H, ang=37.0):
    return [(0.0, 0.0), (H / math.tan(math.radians(ang)), H)]


def r(p):
    return [[round(a, 2), round(b, 2)] for a, b in p]


def horizontal(nombre, sup, t, xl=-400.0, extra=600.0, prof=300.0):
    """Fundación horizontal: capa de morrena de espesor t (0 = sin capa) sobre roca."""
    xc, H = sup[-1]; xr = xc + extra
    reg = [dict(material="Roca", poligono=r([(xl, -t - prof), (xr, -t - prof), (xr, -t), (xl, -t)]))]
    if t > 0:
        reg.append(dict(material="Morrena", poligono=r([(xl, -t), (xr, -t), (xr, 0), (xl, 0)])))
    reg.append(dict(material="Desmonte ROM", poligono=r(sup + [(xr, H), (xr, 0)])))
    return dict(regiones=reg), (xl, xr), -t - prof


def ladera(nombre, sup, t, alfa, xl=-500.0, extra=300.0, prof=250.0):
    """Fundación inclinada alfa (sube hacia el interior): morrena de espesor vertical t sobre roca; el desmonte llena hasta
    que su plataforma corta la ladera."""
    ta = math.tan(math.radians(alfa)); xc, H = sup[-1]; xi = H / ta
    assert xi > xc, f"{nombre}: la ladera corta la superficie antes de la cresta"
    yf = lambda x: x * ta; xr = xi + extra; ybot = yf(xl) - t - prof
    reg = [dict(material="Roca", poligono=r([(xl, ybot), (xr, ybot), (xr, yf(xr) - t), (xl, yf(xl) - t)])),
           dict(material="Morrena", poligono=r([(xl, yf(xl) - t), (xr, yf(xr) - t), (xr, yf(xr)), (xi, H), (0.0, 0.0), (xl, yf(xl))])),  # vértices compartidos con el desmonte
           dict(material="Desmonte ROM", poligono=r(sup + [(xi, H)]))]
    return dict(regiones=reg), (xl, xr), ybot, yf


def agua_seca(ybot):
    return None                                   # seco: sin nivel freático (materiales base sin agua)


def nf_huella(xl, xr, t, alfa, H):
    """Nivel freático en la superficie de la fundación solo bajo la huella del botadero (pie a contacto con la ladera) y en la
    base de la morrena fuera de ella: presión de poros que la carga no deja disipar (H&C 2017, §8.4.1.2). Con el nivel
    freático en toda la ladera (lote 86) la capa de morrena de 30° era inestable sin botadero y la superficie la recorría
    entera (FS 0.93), una condición no consistente."""
    ta = math.tan(math.radians(alfa)); yf = lambda x: x * ta; xi = H / ta; d = t - 0.2
    return dict(metodo="hu", nivel_freatico=r([(xl, yf(xl) - d), (-2.0, yf(-2.0) - d), (0.0, 0.0), (xi, H), (xi + 2.0, yf(xi + 2.0) - d), (xr, yf(xr) - d)]))


GR, CLAVE = [], {}
def grupo(nombre, etiqueta, geo, lim, vista, escenarios, xc=None, xtop=None, H=None):
    """Dos búsquedas por condición de agua (lote 83: la búsqueda libre en todo el contorno se iba a la ladera natural o a un
    banco): «libre» con entrada y salida solo en la superficie del botadero (bancos, pie), y «global» con entrada en la
    plataforma (xc a xtop) y salida entre −0.3H y +0.05H del pie (rotacional, compuesta, cuña, traslación de la base)."""
    sa = lambda l: dict(tipo="sa", limites=[round(v, 1) for v in l], parametros={"optimize": 1})
    escs = []
    for e in escenarios:
        e = {k: v for k, v in e.items() if v is not None}
        base = e["nombre"]; et = e.get("etiqueta", base)
        escs.append(dict(e, nombre=f"{base}, libre", etiqueta=f"{et}, superficie libre", busqueda=sa([0.0, lim[1]])))
        # lote 84: la búsqueda libre no siempre encontró el pie (C saturada dio el banco superior); búsqueda propia del pie
        escs.append(dict(e, nombre=f"{base}, pie", etiqueta=f"{et}, falla de pie", busqueda=sa([-0.15 * H, 0.02 * H, 0.1 * H, 0.7 * H])))
        escs.append(dict(e, nombre=f"{base}, global", etiqueta=f"{et}, superficie global", busqueda=sa([-0.3 * H, 0.05 * H, xc, xtop])))
    GR.append(dict(nombre=nombre, etiqueta=etiqueta, geometria=geo, busqueda=sa([0.0, lim[1]]), metodos=["gle"], vista=vista, escenarios=escs))
    for e in escs:
        CLAVE[f"{nombre}|{e['nombre']}"] = e["etiqueta"]


# A: bancos sobre roca, sin y con 5 m de morrena
sup = bancos(7)
for t, nom in ((0.0, "A roca"), (5.0, "A morrena 5 m")):
    geo, (xl, xr), yb = horizontal(nom, sup, t)
    grupo(nom, f"Bancos, 420 m, fundación de roca{'' if t == 0 else ' con 5 m de morrena'}", geo, [xl, sup[-1][0] + 400],
          dict(xlim=[-400, 1500], ylim=[-350, 600]), [dict(nombre="Seco", agua=agua_seca(yb))],
          xc=sup[-1][0], xtop=sup[-1][0] + 0.8 * 420.0, H=420.0)
# B: un solo lift a 37° sobre ladera de 30°, morrena de 5 m
sup = un_lift(200.0)
geo, (xl, xr), yb, yf = ladera("B", sup, 5.0, 30.0, xl=-400.0)
grupo("B ladera 30", "Un lift a 37°, 200 m, ladera de 30° con 5 m de morrena", geo, [xl, 200.0 / math.tan(math.radians(30.0))],  # libre: solo el botadero (lote 84: la ladera saturada sobre la plataforma daba FS 0.16)
      dict(xlim=[-400, 700], ylim=[-170, 380]),
      [dict(nombre="Seco", agua=agua_seca(yb)), dict(nombre="Fundacion saturada", etiqueta="Fundación saturada",
                                                       agua=nf_huella(xl, xr, 5.0, 30.0, 200.0))],
      xc=sup[-1][0], xtop=xr - 100, H=200.0)
# C: bancos sobre 40 m de morrena horizontal
sup = bancos(7)
geo, (xl, xr), yb = horizontal("C", sup, 40.0)
grupo("C morrena 40 m", "Bancos, 420 m, sobre 40 m de morrena", geo, [xl, sup[-1][0] + 400], dict(xlim=[-400, 1500], ylim=[-350, 600]),
      [dict(nombre="Seco", agua=agua_seca(yb)), dict(nombre="Fundacion saturada", etiqueta="Fundación saturada",
                                                       agua=dict(metodo="hu", nivel_freatico=[[xl, 0.0], [xr, 0.0]]))],
      xc=sup[-1][0], xtop=sup[-1][0] + 0.8 * 420.0, H=420.0)
# D: bancos sobre ladera de 15° con 10 m de morrena
geo, (xl, xr), yb, yf = ladera("D", sup, 10.0, 15.0)
grupo("D ladera 15", "Bancos, 420 m, ladera de 15° con 10 m de morrena", geo, [xl, xr - 150],
      dict(xlim=[-500, 1900], ylim=[-550, 650]),
      [dict(nombre="Seco", agua=agua_seca(yb)), dict(nombre="Fundacion saturada", etiqueta="Fundación saturada",
                                                       agua=nf_huella(xl, xr, 10.0, 15.0, 420.0))],
      xc=sup[-1][0], xtop=xr - 150, H=420.0)

# un .slmd por grupo, para calcular en paralelo
for g in GR:                                      # un modelo seco y, si corresponde, uno saturado por sección
    for cond, escs, mats in (("seco", [e for e in g["escenarios"] if "agua" not in e], MATS),
                             ("saturado", [e for e in g["escenarios"] if "agua" in e], MATS_SAT + MATS[2:])):
        if not escs:
            continue
        nom = "tip_" + g["nombre"].replace(" ", "_") + "_" + cond
        desc = dict(nombre=nom, titulo="Secciones tipicas de botadero (Hawley y Cunning 2017, 8.4)", unidades="metric", direccion="der-izq",
                    materiales=mats, funciones=FUN, grupos=[dict(g, escenarios=escs)])
        (OUT / f"{nom}.yaml").write_text(yaml.safe_dump(desc, allow_unicode=True, sort_keys=False), encoding="utf-8")
(OUT / "claves.json").write_text(json.dumps(CLAVE, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(GR)} grupos, {len(CLAVE)} escenarios en {OUT} | γ {GAM} γsat {GSAT} | φ′e0 {PE0:.2f} m {M:.3f}")
