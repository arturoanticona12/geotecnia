"""Construye Golder_2010_ROM.csv. Lee del texto extraído las hojas CU (todas verificadas en imagen:
corte_1..8.png, vec_*.png, p179-181.png, mohr_stack.png) y agrega metadatos de las Tablas 2-4."""
import csv, math, re, sys
from pathlib import Path

txt = Path(sys.argv[1]).read_text(encoding="utf-8")
OUT = Path(sys.argv[2])
parts = re.split(r"=== PÁGINA (\d+) ===", txt)
pg = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}

COLS = ["fuente", "anio", "autor_informe", "laboratorio", "set_id", "ensayo_id", "litologia_informe", "litologia",
        "litologia_detalle", "litologia_proporcion", "alteracion", "tipo_material", "clase_desmonte", "tipo_ensayo",
        "saturado", "diametro_mm", "altura_mm", "Dmax_mm", "D10_mm", "D30_mm", "D50_mm", "D60_mm", "Cu", "Cc",
        "grava_pct", "arena_pct", "finos_pct", "escalamiento", "Gs", "gamma_d_kNm3", "e0", "e0_origen", "Dr_pct",
        "w_pct", "UCS_MPa", "sigma3_kPa", "sigma1_kPa", "q_kPa", "criterio_falla", "phi_sec_deg",
        "eps_axial_falla_pct", "eps_vol_falla_pct", "u_falla_kPa", "p_falla_kPa", "q_falla_und_kPa", "Su_kPa",
        "Bg_pct", "Br", "finos_post_pct", "sigma_n_kPa", "tau_kPa", "pagina", "verificado_imagen", "notas"]

LIT = {  # clave: (litologia_informe, litologia, detalle)
    "MN": ("Mármol Negro", "Mármol", "mármol negro"),
    "HG": ("Hornfels Gris", "Hornfels", "hornfels gris"),
    "INT": ("Intrusivo", "Intrusivo", ""),
    "EXO": ("Exoskarn Diopsido", "Skarn", "exoskarn diópsido"),
}
# Tabla 2 (pág. 8): UCS de laboratorio (MPa, promedio de 2), σc por carga puntual (MPa), Los Ángeles (%),
# durabilidad (pérdida corregida % en sulfato de magnesio), Gs fino (D854)
T2 = {("A", "MN"): (44.7, 32.24, 62.1, 43.4, 2.763), ("A", "HG"): (49.2, 72.99, 23.7, 0.7, 2.791),
      ("A", "INT"): (46.8, 80.56, 49.8, 33.4, 2.674), ("A", "EXO"): (73.3, 67.79, 37.0, 5.9, 3.484),
      ("B", "MN"): (49.6, 24.56, 62.4, 49.8, 2.747), ("B", "HG"): (65.5, 100.42, 20.3, 0.6, 2.802),
      ("B", "INT"): (54.0, 78.06, 32.2, 18.6, 2.742), ("B", "EXO"): (97.4, 124.78, 27.6, 6.7, 3.338)}
TM_TERRENO = {"MN": 35, "HG": 35, "INT": 30, "EXO": 19}  # pulgadas, Tabla 2 Fase A

# Envolventes de las hojas de laboratorio (Mohr, pág. resumen + 2), verificadas: (c, phi, c', phi')
GOLDER_SETS = {  # página resumen: (fase, mat, diámetro nominal, envolvente)
    82: ("A", "MN", '2.8"', (871, 10, 259, 31)), 87: ("A", "HG", '2.8"', (149, 15, 33, 35)),
    92: ("A", "INT", '2.8"', (313, 10, 103, 30)), 97: ("A", "EXO", '2.8"', (80, 11, 0, 29)),
    102: ("A", "HG", '4"', (376, 3, 272, 14)), 107: ("A", "INT", '4"', (0, 17, 0, 36)),
    112: ("A", "EXO", '4"', (4, 17, 29, 26)),
    117: ("B", "MN", '2.8"', (927, 15, 188, 35)), 122: ("B", "HG", '2.8"', (23, 18, 0, 40)),
    127: ("B", "INT", '2.8"', (162, 15, 42, 34)), 132: ("B", "EXO", '2.8"', (102, 16, 0, 37)),
    137: ("B", "MN", '4"', (47, 11, 67, 16)), 142: ("B", "HG", '4"', (0, 15, 22, 21)),
    147: ("B", "INT", '4"', (7, 12, 0, 23)), 152: ("B", "EXO", '4"', (0, 14, 14, 26)),
}
TABLA = {"A": "Tabla 3 (pág. 9)", "B": "Tabla 4 (pág. 10)"}
DMAX = {'2.8"': 9.5, '4"': 15.9, '6"': 25.4}
DMAX_TXT = {'2.8"': '3/8"', '4"': '5/8"', '6"': '1"'}

base = dict(fuente="2010_Golder_Caracterizacion ROM IPCC.pdf", anio=2010,
            autor_informe="Golder Associates Perú, Memorando técnico 'Caracterización material de ROM – Proyecto IPCC' (proy. 099-4151017, 25-mar-2010)",
            litologia_proporcion="", alteracion="", clase_desmonte="", tipo_ensayo="CU", Br="", Bg_pct="",
            finos_post_pct="", sigma_n_kPa="", tau_kPa="", Su_kPa="", phi_sec_deg="", eps_vol_falla_pct="",
            D10_mm="", D30_mm="", D50_mm="", D60_mm="", Cu="", Cc="", grava_pct="", arena_pct="", finos_pct="", Dr_pct="")


def lit(r, mat):
    a, b, c = LIT[mat]
    r.update(litologia_informe=a, litologia=b, litologia_detalle=c)


def tipo(fase):
    return "ROM" if fase == "A" else "Chancado"


rows = []
for p, (fase, mat, dn, env) in GOLDER_SETS.items():
    t = pg[p]
    s3 = re.findall(r"Esfuerzo Efectivo Inicial \(σ3\)\s*\n?\s*(\d+) kPa", t)
    ini = re.findall(r"INICIAL\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)", t)
    fin = re.findall(r"FINAL\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)", t)
    eps = re.findall(r"Deformación Axial en la Falla \(%\):\n([\d.]+)", t)
    fail = re.findall(r"Criterios de falla:\n(\d+)\n(\d+)\n(\d+)", t)
    rate = re.findall(r"Razón de Deformación \(%/min\):\n([\d.]+)", t)
    obs = re.search(r"Remoldeado a la densidad (de campo|mínima) δ\s*=\s*([\d.]+)\s*gr/cm3 y\s+(\d+)% de humedad", t)
    inf = re.search(r"(GL-48\d-09)", pg[p + 1] + pg[p + 2])
    assert len(s3) == len(ini) == len(fin) == len(eps) == len(fail) == 3, p
    ucs, pl, la, dur, gs = T2[(fase, mat)]
    for i in range(3):
        H, D, A, w, gd, e, S = map(float, ini[i])
        gdf, ef = float(fin[i][4]), float(fin[i][5])
        s1, s1p, s3c = map(float, fail[i])
        assert int(s3[i]) == int(s3c)
        q = s1 - s3c
        s3p = s1p - q
        u = s3c - s3p
        r = dict(base)
        lit(r, mat)
        r.update(laboratorio="Golder Associates Perú – Laboratorio de Mecánica de Suelos (Lima)",
                 set_id=f"G2010-{fase}-{mat}-{dn.replace(chr(34), 'in')}",
                 ensayo_id=f"{inf.group(1) if inf else ''} Prueba Nº {i + 1} (σ3c={s3c:.0f} kPa)",
                 tipo_material=tipo(fase), saturado="sí", diametro_mm=round(D * 10, 1), altura_mm=round(H * 10, 1),
                 Dmax_mm=DMAX[dn],
                 escalamiento=f"Truncado: se ensayó la fracción < {DMAX_TXT[dn]} de la matriz; TM de terreno {TM_TERRENO[mat]}\" (Fase A, Tabla 2)"
                              + ("; Fase B chancada, TM 9\"–12\" según texto pág. 2" if fase == "B" else ""),
                 Gs=gs, gamma_d_kNm3=round(gd * 9.81, 2), e0=e, e0_origen="informe", w_pct=w, UCS_MPa=ucs,
                 sigma3_kPa=s3c, sigma1_kPa=s1p, q_kPa=q, criterio_falla="Esfuerzo desviador máximo (hoja Golder)",
                 eps_axial_falla_pct=float(eps[i]), u_falla_kPa=round(u, 0),
                 p_falla_kPa=round((s1p + 2 * s3p) / 3, 1), q_falla_und_kPa=round(s1p - s3p, 0),
                 pagina=f"{p};{p + 2};{8};{9 if fase == 'A' else 10}", verificado_imagen="sí")
        r["notas"] = (
            f"Fase {fase} ({'material original del tajo = ROM' if fase == 'A' else 'material chancado = Chancado'}). "
            f"Probeta remoldeada a la densidad {obs.group(1)} δ={obs.group(2)} g/cm3 y {obs.group(3)} % de humedad (solicitado por el cliente). "
            f"Diámetro nominal {dn}. Inicial: S={S} %; final (post-consolidación): gd={gdf} g/cm3, e={ef}. "
            f"Velocidad {rate[i]} %/min. Hoja da σ1, σ1', σ3, σ3' en la falla; σ3'f={s3p:.0f} kPa. "
            f"sigma3_kPa = σ'3 de consolidación; sigma1_kPa = σ'1 en la falla; q_kPa = σ1−σ3 = σ'1−σ'3. "
            f"u_falla = exceso de presión de poros en la falla = σ3c − σ'3f (negativo = succión/dilatancia). "
            f"p_falla = (σ'1+2σ'3)/3 (calculado), q_falla_und = σ'1−σ'3. Gs = D854 de finos (hoja CU y pág. 49). "
            f"UCS_MPa = compresión simple de laboratorio (promedio de 2, Tabla 2); σc por carga puntual = {pl} MPa; "
            f"Los Ángeles {la} %; durabilidad (sulfato de magnesio, pérdida corregida) {dur} %. "
            f"Envolvente de la hoja Golder (Mohr máximo, pág. {p + 2}): total c={env[0]} kPa φ={env[1]}°, efectiva c'={env[2]} kPa φ'={env[3]}°. "
            + ("En la Tabla 3 (pág. 9) los valores 2.8\" de Fase A aparecen ≈100 veces menores (parecen kg/cm2 rotulados kPa). "
               if fase == "A" and dn == '2.8"' else "")
            + "Granulometría de la fracción ensayada no informada (solo granulometría de terreno, ver resumen). "
            "Saturación final ≈100 %; el parámetro B no figura en la hoja. SUCS informado por el cliente.")
        rows.append(r)

# ---------------- VECTOR (6") ----------------
num = re.compile(r"^-?\d+,\d+$")


def vec_rows(p):
    vals = [float(l.strip().replace(",", ".")) for l in pg[p].splitlines() if num.match(l.strip())]
    k = next(j for j in range(len(vals) - 2) if vals[j] == 0 and vals[j + 1] == 0 and vals[j + 2] == 0)
    rows_ = {}
    for j in range(k, len(vals) - 8, 9):
        rr = vals[j:j + 9]
        if abs((rr[4] - rr[3]) - rr[1]) < 0.5:
            rows_[rr[0]] = rr
    m = re.search(r"Altura\s*\n\(cm\)\n([\d,]+)\n([\d,]+)\n([\d,]+)\nDiámetro\s*\n\(cm\)\n([\d,]+)\n([\d,]+)\nkPa\n(\d+)\nHumedad\s*\n\(%\)\n([\d,]+)\n([\d,]+)\nkPa\n(\d+)\n([\d,]+)\n([\d,]+)\nkPa\n(\d+)", pg[p])
    h = [x.replace(",", ".") for x in m.groups()]
    hdr = dict(H0=float(h[0]), Hf=float(h[1]), B=float(h[2]), D0=float(h[3]), Df=float(h[4]), celda=int(h[5]),
               w0=float(h[6]), wf=float(h[7]), cp=int(h[8]), gd0=float(h[9]), gdf=float(h[10]), s3c=int(h[11]))
    return hdr, rows_


# (pág., mat, ε elegido para el pico) ; envolvente Vector "pico de esf. desviador" (c, φ, c', φ') de la pág. de trayectorias
VEC = [(161, "MN", 1.50), (162, "MN", 1.00), (163, "MN", 1.00),
       (167, "HG", 1.25), (168, "HG", 1.00), (169, "HG", 0.50),
       (173, "INT", 1.75), (174, "INT", 1.25), (175, "INT", 0.75)]
VEC_ENV = {"MN": (165, (60, 29.6, 25, 36.4), (0, 26, 10, 38)), "HG": (171, (None, None, 6, 29.2), (None, None, 5, 39.2)),
           "INT": (177, (None, None, 0, 27.9), (None, None, 0, 38.1)), "EXO": (183, (0, 24.3, 0, 34.1), (66, 25.5, 0, 42))}
# Exoskarn: tablas sin capa de texto, transcritas de la imagen (págs. 179-181)
EXO = [
    (179, dict(H0=31.00, Hf=30.84, B=0.89, D0=15.15, Df=14.92, celda=705, w0=3.50, wf=8.70, cp=205, gd0=2.353, gdf=2.440, s3c=500),
     [1.25, 700.75, 219.95, 280.05, 980.80], [14.00, 986.22, 254.51, 245.49, 1231.71]),
    (180, dict(H0=31.00, Hf=30.87, B=0.88, D0=15.15, Df=15.01, celda=455, w0=3.50, wf=8.76, cp=205, gd0=2.354, gdf=2.409, s3c=250),
     [1.00, 309.36, 117.86, 132.14, 441.51], [14.00, 486.13, 118.02, 131.98, 618.10]),
    (181, dict(H0=31.00, Hf=30.91, B=0.90, D0=15.15, Df=15.02, celda=330, w0=3.50, wf=9.14, cp=205, gd0=2.332, gdf=2.380, s3c=125),
     [1.00, 126.07, 60.43, 64.57, 190.64], [14.00, 496.79, -10.53, 135.53, 632.32]),
]
items = []
for p, mat, ep in VEC:
    hdr, rr = vec_rows(p)
    last = rr[max(rr)]
    items.append((p, mat, hdr, rr[ep], last))
for p, hdr, pk, last in EXO:
    items.append((p, "EXO", hdr, pk, last))

for p, mat, hdr, pk, last in items:
    eps, dev, u, s3p, s1p = pk[:5]
    ucs, pl, la, dur, gs = T2[("B", mat)]
    e0 = gs / hdr["gd0"] - 1
    envp, env_pk, env12 = VEC_ENV[mat]
    r = dict(base)
    lit(r, mat)
    r.update(laboratorio="Vector Perú S.A.C. – Laboratorio Geotécnico (Lima), informe VP-209-09E",
             set_id=f"G2010-B-{mat}-6in", ensayo_id=f"VP-209-09E σ'c={hdr['s3c']} kPa",
             tipo_material="Chancado", saturado="sí",
             diametro_mm=hdr["D0"] * 10, altura_mm=hdr["H0"] * 10, Dmax_mm=DMAX['6"'],
             escalamiento=f"Truncado: fracción < 1\" (memo pág. 3); Fase B chancada, TM 9\"–12\" según texto pág. 2",
             Gs=gs, gamma_d_kNm3=round(hdr["gd0"] * 9.81, 2), e0=round(e0, 3), e0_origen="calculado",
             w_pct=hdr["w0"], UCS_MPa=ucs, sigma3_kPa=hdr["s3c"], sigma1_kPa=round(s1p, 1), q_kPa=round(dev, 1),
             criterio_falla="Pico (primer máximo) del esfuerzo desviador, criterio de envolvente 'pico' de Vector",
             eps_axial_falla_pct=eps, u_falla_kPa=round(u, 1), p_falla_kPa=round((s1p + 2 * s3p) / 3, 1),
             q_falla_und_kPa=round(s1p - s3p, 1), pagina=f"{p};{envp};10;8", verificado_imagen="sí")
    extra = ""
    if last[1] > dev + 1:
        extra = (f"Comportamiento con endurecimiento posterior: a ε={last[0]} % (fin del ensayo) desviador={last[1]} kPa, "
                 f"u={last[2]} kPa, σ'3={last[3]} kPa, σ'1={last[4]} kPa. ")
    if p == 173:
        extra += "El punto marcado por Vector en la trayectoria (pág. 177) parece estar cerca de ε≈2.5 % (p'≈350, t≈178), no en el pico del desviador. "
    if p == 181:
        extra += "Sin pico definido: el desviador crece hasta el final; se adopta ε=1.0 % porque es el punto marcado por Vector (pág. 183). "
    if mat in ("MN", "INT"):
        extra += ("Cabeceras de Mármol e Intrusivo idénticas en altura/diámetro/humedad/densidad inicial (posible copia de plantilla). ")
    if mat == "EXO":
        extra += "Valores transcritos de la imagen (la página no tiene capa de texto). "
    r["notas"] = (
        f"Fase B (material chancado). Probeta 6\" ensayada por Vector para Golder (Estado: remoldeado). "
        f"Presión de celda {hdr['celda']} kPa, contrapresión {hdr['cp']} kPa, B={hdr['B']} (<0.95). Velocidad 0.01 pulg/min. "
        f"Final: H={hdr['Hf']} cm, D={hdr['Df']} cm, w={hdr['wf']} %, gd={hdr['gdf']} g/cm3. "
        f"e0 calculado con Gs de finos D854 de Golder para el mismo material y fase (pág. 49), Gs no informado por Vector. "
        f"La hoja Vector da p=(σ'1+σ'3)/2 y q=(σ'1−σ'3)/2; aquí p_falla=(σ'1+2σ'3)/3 y q_falla_und=σ'1−σ'3 (recalculados). "
        f"u_falla = presión de poros en exceso informada por Vector. "
        f"Envolvente Vector 'pico' (pág. {envp}): " + (f"c={env_pk[0]} kPa φ={env_pk[1]}° (totales), " if env_pk[0] is not None else "")
        + f"c'={env_pk[2]} kPa φ'={env_pk[3]}°; al 12 %: c'={env12[2]} kPa φ'={env12[3]}°. "
        + extra + f"σc carga puntual {pl} MPa; Los Ángeles {la} %; durabilidad {dur} %.")
    rows.append(r)

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in COLS})
print("filas:", len(rows))
for r in rows:
    print(r["set_id"], r["ensayo_id"], r["sigma3_kPa"], r["sigma1_kPa"], r["q_kPa"], r["u_falla_kPa"], r["e0"], r["eps_axial_falla_pct"])
