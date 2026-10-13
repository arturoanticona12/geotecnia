# -*- coding: utf-8 -*-
"""Genera los entregables verificados WSP 2022 y Golder 2012.
Todos los números de este script se comprobaron en la imagen de la página citada
(PNG en esta misma carpeta)."""
import os, numpy as np, pandas as pd

BASE = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Aporte_alto_confinamiento\datos_antamina"
EXT = os.path.join(BASE, "extraido"); OUT = os.path.join(BASE, "verificado")
os.makedirs(OUT, exist_ok=True)
TAG = "[VERIF 2026-10-06] "
GW = 9.81

# ---------------------------------------------------------------- utilidades
def Dx(sieves, passing, pc):
    s = np.array(sieves, float); p = np.array(passing, float)
    if pc < p.min():
        return None
    return float(10 ** np.interp(pc, p[::-1], np.log10(s[::-1])))

def ret(p):
    p = np.array(list(p) + [0.0]); return -np.diff(np.r_[100.0, p])

def bg(ini, post):
    d = ret(ini) - ret(post); return float(d[d > 0].sum())

S_IDIEM = [177.8, 152.4, 127, 101.6, 76.2, 63.5, 50.8, 38.1, 25.4, 19, 9.52, 4.76, 2.0, 0.84, 0.42, 0.25, 0.11, 0.074]
HF_INI = [100, 96.6, 91.9, 86.4, 78.7, 74.1, 68.6, 63.8, 45.7, 37.8, 22.7, 12.7, 8.8, 6.1, 4.6, 3.8, 2.9, 2.6]      # WSP p62
MN11_INI = [100, 97.9, 93.2, 87.9, 75.5, 67.6, 59.2, 48.7, 38.0, 31.2, 20.3, 14.7, 10.8, 8.9, 7.9, 7.3, 5.5, 4.9]   # G p27 / W p66
MN21_INI = [100, 93.3, 85.2, 77.4, 73.2, 71.3, 69.3, 63.6, 51.9, 45.0, 32.6, 24.2, 20.1, 17.0, 15.5, 14.4, 12.1, 10.9]  # W p61
MN21_EDO = [100, 98.6, 97.4, 95.7, 93.6, 90.8, 87.2, 83.2, 76.0, 72.5, 65.9, 59.5, 49.5, 41.4, 36.9, 34.1, 28.6, 25.7]
MN11_POST = {1: [100, 98.2, 95.9, 91.0, 83.3, 77.3, 70.9, 60.6, 47.0, 41.7, 29.8, 23.2, 16.9, 13.6, 12.1, 11.2, 9.2, 8.2],
             2: [100, 99.4, 95.5, 92.1, 85.1, 79.7, 72.7, 62.8, 49.9, 43.3, 30.0, 23.2, 16.6, 13.1, 11.7, 10.9, 9.1, 8.0],
             3: [100, 99.4, 98.2, 94.8, 89.1, 84.5, 77.8, 69.1, 56.8, 49.6, 34.6, 26.4, 19.5, 15.1, 13.1, 11.9, 9.2, 8.5],
             4: [100, 100, 99.4, 97.0, 91.5, 87.2, 81.4, 73.5, 60.9, 54.4, 40.3, 32.0, 23.0, 17.7, 15.3, 14.0, 11.7, 10.7],
             5: [100, 99.7, 98.7, 95.7, 90.9, 87.2, 81.7, 74.2, 63.2, 58.6, 46.0, 34.3, 24.8, 19.3, 16.8, 15.4, 12.5, 11.4],
             6: [100, 99.1, 96.1, 92.8, 84.6, 77.8, 70.2, 60.6, 48.5, 43.9, 32.3, 24.6, 17.3, 13.5, 12.1, 11.5, 9.9, 9.4]}
BG11 = {k: round(bg(MN11_INI, v), 1) for k, v in MN11_POST.items()}
BG21_EDO = round(bg(MN21_INI, MN21_EDO), 1)
BG21_EDO_vs2011 = round(bg(MN11_INI, MN21_EDO), 1)

def gparams(ini):
    d = {k: Dx(S_IDIEM, ini, k) for k in (10, 30, 50, 60)}
    cu = d[60] / d[10] if d[10] else None
    cc = d[30] ** 2 / (d[10] * d[60]) if d[10] else None
    return d, cu, cc
HFd, HFcu, HFcc = gparams(HF_INI)
MNd, MNcu, MNcc = gparams(MN11_INI)
M21d, _, _ = gparams(MN21_INI)

# granulometrías de terreno (WSP p47 hornfels; p52 mármol 2020)
S_F = [914.4, 406.4, 254.0, 203.2, 152.4, 101.6, 76.2, 63.5, 50.8, 38.1, 25.4, 19.05, 12.7, 9.525, 4.76, 2.36, 1.19, 0.6, 0.42, 0.15, 0.075]
HF_F = [100, 88.21, 76.98, 76.98, 58.34, 58.34, 43.65, 41.74, 41.43, 36.40, 31.49, 27.88, 22.49, 19.43, 13.14, 9.57, 6.38, 4.66, 4.02, 2.90, 2.49]
MN_F = [100, 95.11, 82.35, 82.35, 68.61, 68.61, 57.83, 47.73, 43.30, 35.72, 29.48, 25.45, 20.46, 18.05, 11.95, 9.76, 7.85, 6.58, 6.18, 5.12, 4.07]
def fstr(pas):
    d = {k: Dx(S_F, pas, k) for k in (10, 50, 80)}
    return d

hfF = fstr(HF_F); mnF = fstr(MN_F)

def e0(gs, rho):
    return gs / rho - 1.0

V0 = np.pi * 50.0 ** 2 * 180.0  # cm3, probeta 1.0 x 1.8 m
def rho_c(rho0, dV):
    return rho0 / (1 - dV / V0)

# ---------------------------------------------------------------- impresión de control
print("Bg 2011 Marsal recalculado:", BG11)
print("Bg mármol 2021 edómetro: con inicial 2021 =", BG21_EDO, "; con inicial 2011 =", BG21_EDO_vs2011)
print("HF IDIEM inicial:", {k: round(v, 3) for k, v in HFd.items()}, "Cu=%.2f Cc=%.3f" % (HFcu, HFcc))
print("MN 2011 inicial:", {k: round(v, 3) for k, v in MNd.items()}, "Cu=%.2f Cc=%.3f" % (MNcu, MNcc))
print("MN 2021 inicial:", {k: (round(v, 2) if v else None) for k, v in M21d.items()})
print("Campo HF:", {k: (round(v, 2) if v else None) for k, v in hfF.items()})
print("Campo MN 2020:", {k: (round(v, 2) if v else None) for k, v in mnF.items()})
for lab, r0, dv in [("B2-P1", 2.10, 28920.61), ("B2-P2", 2.10, 68762.28), ("B2-P3", 2.10, 92728.0),
                    ("E-P1", 2.06, 29390.0), ("E-P2", 2.06, 73737.0), ("E-P3", 2.06, 87571.0),
                    ("G12-P1", 2.10, 34670.0), ("G12-P5", 2.10, 116227.0)]:
    print("rho_c", lab, round(rho_c(r0, dv), 3), "t/m3 ->", round(rho_c(r0, dv) * GW, 2), "kN/m3")

# ================================================================ CSV verificados
wsp = pd.read_csv(os.path.join(EXT, "WSP_2022_hornfels3B.csv"), dtype=str)
gol = pd.read_csv(os.path.join(EXT, "Golder_2012_marmol.csv"), dtype=str)
disc = []  # (archivo, fila, ensayo_id, columna, anterior, correcto, pagina, razon)

def setv(df, name, i, col, new, pag, razon, registrar=True):
    old = df.at[i, col]
    old_s = "" if (old is None or (isinstance(old, float) and np.isnan(old)) or str(old) == "nan") else str(old)
    new_s = "" if new is None else str(new)
    if registrar and old_s != new_s:
        disc.append((name, i + 2, df.at[i, "ensayo_id"], col, old_s, new_s, pag, razon))
    df.at[i, col] = new_s

def addnote(df, i, txt):
    old = df.at[i, "notas"]; old = "" if str(old) == "nan" else str(old)
    df.at[i, "notas"] = (old + " " if old else "") + TAG + txt

# ---------------- Golder 2012
GN = "Golder_2012_marmol.csv"
bg_rep = {0: "26.8", 1: "28.6", 2: "40.8", 3: "50.2", 4: "55.4", 5: "28.8"}
for i in range(6):
    k = i + 1
    setv(gol, GN, i, "Bg_pct", f"{BG11[k]:.1f}", "17;27;28",
         f"La Tabla 5 (p17) informa {bg_rep[i]}, que es la suma de |ΔW| (positivas y negativas) = 2×Bg. Con la definición que el propio informe declara (suma de diferencias positivas, Marsal 1967) y las granulometrías IDIEM p27–28 resulta {BG11[k]:.1f}. WSP 2022 Tabla 7 (p41) corrige a {round(BG11[k])}.")
    addnote(gol, i, f"Bg corregido: Tabla 5 (p17) da {bg_rep[i]} = Σ|ΔW| = 2×Bg Marsal; recalculado {BG11[k]:.1f} con p27–28 (coincide con WSP 2022 Tabla 7). Registro PRIMARIO de los ensayos IDIEM 708.397-A; WSP 2022 (Anexo B p252–295) los reproduce idénticos fila a fila.")
# pico
pico = {0: "máximo t=9.08 a εa=17.27 %; al final (19.97 %) t=8.66 (−4.6 %): pico leve",
        1: "máximo t=8.68 a 18.26 %; final 20.39 % t=8.53 (−1.7 %): meseta",
        2: "máximo t=14.87 a 18.00 %; final 18.73 % t=14.69 (−1.2 %): meseta",
        3: "máximo t=29.66 a 19.59 %; final 19.97 % t=29.50 (−0.5 %): sin pico",
        4: "máximo t=32.27 a 17.78 %; final 19.74 % t=31.33 (−2.9 %): pico leve"}
for i, t in pico.items():
    addnote(gol, i, "Forma de la curva (tabla IDIEM): " + t + ". Ensayo controlado por carga (velocidad '--' en la hoja).")
# edómetro
setv(gol, GN, 5, "e0_origen", "calculado", "13;72",
     "El informe no tabula e0 del edómetro: p13 dice que e se estimó con Gs=2.7 supuesto; 2.70/2.100−1=0.286. La hoja p72 da e=0.284 a 0.18 kg/cm² (tras asentamiento inicial), no en confección.")
setv(gol, GN, 5, "Bg_pct", f"{BG11[6]:.1f}", "17;27;28", "Ver fila de la probeta 1: Tabla 5 = 2×Bg.", registrar=False)
addnote(gol, 5, "CORRECCIÓN de las notas comunes: el edómetro NO se saturó con CO2 ni tuvo contrapresión; se armó en 3 capas de 0.3 m con pisón vibratorio a 2.1 t/m³, carga de asiento 0.18 kg/cm² e inundación a esa carga (asentamiento 0.8 mm = 0.09 %) (p13). Carga máx. 60 kg/cm² (5884 kPa) en 20 incrementos de 2 y 4 de 5 kg/cm²; cada escalón hasta deformación nula ≥100 min. εv a 60 kg/cm² = (90−81.87)/90 = 9.03 %.")
for i in range(6):
    gol.at[i, "verificado_imagen"] = "sí"

# ---------------- WSP 2022
WN = "WSP_2022_hornfels3B.csv"
contra = {0: "2.00 kg/cm² (196 kPa)", 1: "1.00 kg/cm² (98 kPa)", 2: "2.00 kg/cm² (196 kPa)",
          3: "1.00 kg/cm² (98 kPa)", 4: "1.00 kg/cm² (98 kPa)", 5: "1.00 kg/cm² (98 kPa)"}
picoW = {0: "máximo t=19.87 a 13.13 %, final 19.05 % t=18.81 (−5.3 %): pico leve",
         1: "máximo = último punto (19.04 %): sin pico, curva aún creciente",
         2: "máximo t=60.83 a 17.83 %, final 19.63 % t=60.49: meseta",
         3: "máximo = último punto (19.15 %): sin pico",
         4: "máximo t=49.47 a 18.80 %, final 19.33 % t=48.76: meseta",
         5: "máximo t=65.92 a 18.98 %, final 19.52 % t=65.47: meseta"}
pagsH = {0: "233", 1: "238", 2: "245", 3: "106", 4: "119", 5: "169"}
for i in range(6):
    addnote(wsp, i, f"Contrapresión en la hoja: {contra[i]} (p{pagsH[i]}). {picoW[i]}. Gs NO figura en las hojas IDIEM; 2.75 es el Gs 'calculated' de Golder Burnaby sobre el mismo lote (<1\"). UCS: Tabla 1 (Golder 2021a, ASTM D7012 C, núcleos ~74 mm de muestras M-001/M-002, Acopio punto F, 31/10/2020) da 65 y 64 MPa; IDIEM 1.555.677-D (ASTM D7012-14e1, núcleos 54 mm del MISMO lote enviado a IDIEM 'H6 HORNFEL GRIS') da 26.3, 40.8 y 24.5 MPa (D50) — ver verificacion_WSP2022_Golder2012.md.")
    setv(wsp, WN, i, "clase_desmonte", "C (rótulo 'Material tipo C' en fotos de muestras Golder 2021a; no indicado para el lote IDIEM)", "8;48-51",
         "Las fotos de las probetas UCS/LA de hornfels (p8, p48–p51) están rotuladas 'MATERIAL TIPO C'.")
    setv(wsp, WN, i, "escalamiento", "Ajustada a <178 mm (7\") para IDIEM; método de ajuste no declarado (p4). Terreno (M-001, p47): 100 % pasa 36\" (914 mm) y 11.8 % queda retenido en 16\" (406 mm); Dmax real entre 406 y 914 mm, no informado", "4;47",
         "La hoja M-001 no da Dmax de terreno de 914 mm: 914 mm es el primer tamiz (100 % pasa); hay 11.8 % retenido en 16\".")
for i in (6,):
    addnote(wsp, i, "Hoja p350 rotula 'Sample: MR' y la curva p351 'CID 6\" MR' aunque es Hornfels (HR): errata de rótulo. La curva p351 llega a ≈4600 kPa a ≈17.5 %; la hoja (p350/p353) informa σ1−σ3 máx = 4100 kPa a 11.44 %: inconsistencia interna, se mantiene el valor tabulado. Velocidad 1.00 %/h (0.0167 %/min). Contrapresión (σpwp) 688 kPa; σ'3c 992 kPa. γd post-consolidación 21.62 kN/m³, ec 0.25.")
    setv(wsp, WN, i, "clase_desmonte", "C (rótulo 'Material tipo C' en fotos de muestras Golder 2021a)", "8;48-51", "Igual que filas IDIEM de hornfels.")
# USC
usc = {7: ("HR", "20.00", None), 8: ("HR", "1.68", "1.68"), 9: ("HR", "7.37", "7.37"),
       10: ("MN", "4.89", "4.89"), 11: ("MN", "20.00", None), 12: ("MN", "20.00", None)}
for i, (lit, emax, trunc) in usc.items():
    if trunc:
        setv(wsp, WN, i, "criterio_falla", f"máximo desviador alcanzado en la carga monótona post-cíclica; la hoja da 'Max. Axial Strain' = {trunc} % y el desviador a esa deformación es igual al máximo: ensayo detenido antes de la falla, el valor es una cota inferior de la resistencia",
             {8: "361", 9: "367", 10: "379"}[i],
             f"La carga post-cíclica terminó a εa = {trunc} % (hoja USC): el máximo coincide con el último punto, no es una falla.")
    if i in (8, 9, 10):
        setv(wsp, WN, i, "Gs", "2.71", {8: "361;373", 9: "367;373", 10: "379;385"}[i],
             "La hoja de 4\" no trae Gs, pero el e0 de la fila (0.239/0.205) se calculó con 2.71 ('Estimated Specific Gravity' de las hojas USC de 6\"); se completa para que la fila sea coherente.")
    addnote(wsp, i, "Preparación según hoja USC: 'Moist Tamping' con w=5.00 % (el texto p15 dice 'estado seco'). Velocidad post-cíclica 5.00 %/h (0.083 %/min).")
    if lit == "HR":
        setv(wsp, WN, i, "clase_desmonte", "C (rótulo 'Material tipo C' en fotos de muestras Golder 2021a)", "8;48-51", "Igual que filas IDIEM de hornfels.", registrar=(i == 7))
for i in (8, 9):
    addnote(wsp, i, "HR-CTX1 y HR-CTX4 tienen masas idénticas (3665.03 g húmeda; 3490.50 g seca): no son mediciones independientes (probables valores objetivo).")
for i in (11, 12):
    addnote(wsp, i, "MN-LCTX1 y MN-LCTX2 tienen masas idénticas (10620.87/10115.11 g). La hoja da e tras consolidación 0.21 (LCTX1) y 0.25 (LCTX2), MAYORES que e0=0.205 calculado con su propio γd=22.07 y Gs=2.71: inconsistencia interna de la hoja USC.")
for i in (10, 11, 12, 13, 22, 24):
    setv(wsp, WN, i, "clase_desmonte", "C (rótulo 'Material tipo C' en fotos de muestras M-001/M-002 de mármol 2020, Golder 2021a)", "9;53-56",
         "Fotos de las probetas UCS/LA de mármol negro rotuladas 'MATERIAL TIPO C', polígono 8-NP-4133-25-04, Acopio punto G.", registrar=(i == 10))
    addnote(wsp, i, "Origen mármol 2021: Tajo Mina Fase 8 Sur (Pala 10), polígono 8-NP-4133-25-04, Acopio punto G, muestreado 23–24/11/2020 (p52–p56). Densidad seca de núcleos IDIEM del mismo lote (REG 41061) 2.74–2.75 g/cm³ (p78, p80, p82): un Gs de 2.60, 2.70 o 2.71 es físicamente incompatible (Gs ≥ 2.75).")
addnote(wsp, 13, "Velocidad 1.00 %/h. σpwp 1104 kPa; σ'3c 976 kPa. La hoja trae w post 27.4 % y Sat 319 % (erratas). Curva p355 coherente con 3823 kPa a 18.51 %.")

# Mármol 2011 duplicados (filas 14-18) -> armonizar con el registro primario Golder 2012
gmap = {14: 0, 15: 1, 16: 2, 17: 3, 18: 4}
for i, g in gmap.items():
    for col in ("sigma3_kPa", "sigma1_kPa", "q_kPa"):
        setv(wsp, WN, i, col, gol.at[g, col], "252-293 (=Golder 2012 p29-70)",
             "Se armoniza con el registro primario (conversión exacta kg/cm²×98.0665); el CSV extraído había redondeado a enteros.", registrar=False)
    setv(wsp, WN, i, "saturado", "sí (CO2 24 h + agua desaireada; B>0.95; contrapresión 2 kg/cm²)", "Golder 2012 p7; WSP p252",
         "Golder 2012 p7 (registro primario) describe la saturación; la hoja reproducida en WSP p252 muestra contrapresión 2.00 kg/cm².")
    setv(wsp, WN, i, "Cu", "34.4", "Golder 2012 p2", "Valor del informe primario (Fig. 1). 37.4 era un recálculo por interpolación log-lineal; se deja en notas.")
    setv(wsp, WN, i, "Cc", "4.1", "Golder 2012 p2", "Valor del informe primario (Fig. 1). 4.3 era recálculo.")
    setv(wsp, WN, i, "Dmax_mm", "177.8", "Golder 2012 p2; W p66", "Mismo valor que el registro primario (177.8 mm = 7\").", registrar=False)
    setv(wsp, WN, i, "e0_origen", "informe (Golder 2012 Tabla 3, p7; Gs 2.70 supuesto)", "Golder 2012 p7",
         "e0=0.286 está tabulado en el informe primario.")
    setv(wsp, WN, i, "UCS_MPa", "97.3", "8; Golder 2012 p3",
         "Promedio de las 8 UCS del Informe 379 (Tabla 2 WSP p8 / Tabla 1 Golder 2012 p3); el registro primario lo usa.")
    setv(wsp, WN, i, "Bg_pct", f"{BG11[g+1]:.1f}", "41; Golder 2012 p27-28",
         f"Tabla 7 da {wsp.at[i,'Bg_pct']} (redondeado); recálculo Marsal {BG11[g+1]:.1f}.", registrar=False)
    setv(wsp, WN, i, "escalamiento", "Truncado (scalping) a 178 mm; Dmax de terreno 558.8 mm (macro-granulometría) — Golder 2012 p2", "Golder 2012 p2",
         "El registro primario sí declara el método: 'scalped at 178 mm'.")
    setv(wsp, WN, i, "clase_desmonte", "C ('Type C rockfill', Golder 2012 p1)", "Golder 2012 p1", "Informe primario.", registrar=(i == 14))
    addnote(wsp, i, "DUPLICADO de Golder_2012_marmol.csv (registro primario: Golder 2012 Doc. 446 + IDIEM 708.397-A). Tablas q–εa–εv idénticas fila a fila entre ambos PDF (comparación automática, 16/346/402/54/504 filas). No contar dos veces. Origen: Fase 5, polígono 12022607, cota 4478 (Golder 2012 p1), NO Acopio G.")
# edómetros
setv(wsp, WN, 19, "finos_post_pct", "9.5", "62", "Granulometría post edómetro IDIEM p62 (#200 = 9.5 %).")
addnote(wsp, 19, "Gs 2.60 'estimado' por IDIEM (p300, nota 3) es incompatible con la densidad seca de núcleos del mismo lote (2.66–2.71 g/cm³, p72–p76). Con Gs=2.75 (Golder), e0=0.310.")
# mármol 2021 edómetro
setv(wsp, WN, 22, "Bg_pct", f"{BG21_EDO:.1f}", "41;61",
     f"Tabla 7 informa 45. Con las granulometrías IDIEM del mismo ensayo (inicial y post edómetro 2021, p61) el Bg de Marsal es {BG21_EDO:.1f}. El 45 se reproduce ({BG21_EDO_vs2011:.1f}) solo si se compara la curva post-2021 con la inicial de 2011 (p66): error probable de WSP.")
for col, val, raz in [("Dmax_mm", "177.8", "p61: 100 % pasa 7\" (177.8 mm)."),
                      ("D30_mm", f"{M21d[30]:.2f}", "Interpolación log-lineal de la granulometría inicial p61."),
                      ("D50_mm", f"{M21d[50]:.1f}", "Ídem."),
                      ("D60_mm", f"{M21d[60]:.1f}", "Ídem."),
                      ("grava_pct", "75.8", "100−24.2 (pasa #4)."),
                      ("arena_pct", "13.3", "24.2−10.9."),
                      ("finos_pct", "10.9", "Pasa #200 inicial p61."),
                      ("finos_post_pct", "25.7", "Pasa #200 post edómetro p61.")]:
    setv(wsp, WN, 22, col, val, "61", raz)
addnote(wsp, 22, "D10 < 0.074 mm (10.9 % pasa #200): no determinable, por eso no hay Cu ni Cc.")
setv(wsp, WN, 23, "finos_post_pct", "9.4", "67 (=Golder 2012 p28)", "Granulometría post odómetro IDIEM 2011.")
setv(wsp, WN, 23, "Bg_pct", f"{BG11[6]:.1f}", "41; Golder 2012 p27-28", "Recálculo Marsal (Tabla 7 redondea a 14; Golder 2012 Tabla 5 da 28.8 = 2×Bg).", registrar=False)
for col, val in [("Dmax_mm", "177.8"), ("D10_mm", gol.at[0, "D10_mm"]), ("D30_mm", gol.at[0, "D30_mm"]),
                 ("D50_mm", gol.at[0, "D50_mm"]), ("D60_mm", gol.at[0, "D60_mm"]), ("Cu", "34.4"), ("Cc", "4.1"),
                 ("grava_pct", "85.3"), ("arena_pct", "9.8"), ("finos_pct", "4.9"), ("UCS_MPa", "97.3")]:
    setv(wsp, WN, 23, col, val, "66; Golder 2012 p2-3,27", "Se completa con la granulometría inicial y UCS del registro primario (mismo material 2011).")
addnote(wsp, 23, "DUPLICADO de Golder_2012_marmol.csv (Probeta 6 Odómetro); hoja p295 idéntica a Golder 2012 p72. e0=0.284 es el valor a 0.18 kg/cm² (estado seco); en confección 2.70/2.100−1=0.286.")
setv(wsp, WN, 24, "Dmax_mm", "25.4", "6", "Material enviado a Golder <1\" (p6); la hoja p359 no da granulometría.")
for i in range(len(wsp)):
    wsp.at[i, "verificado_imagen"] = "sí"

wsp.to_csv(os.path.join(OUT, "WSP_2022_hornfels3B_verificado.csv"), index=False, encoding="utf-8")
gol.to_csv(os.path.join(OUT, "Golder_2012_marmol_verificado.csv"), index=False, encoding="utf-8")
pd.DataFrame(disc, columns=["archivo", "fila_csv", "ensayo_id", "columna", "valor_anterior", "valor_correcto", "pagina", "razon"]).to_csv(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "discrepancias_filas.csv"), index=False, encoding="utf-8")
print("discrepancias por fila registradas:", len(disc))
