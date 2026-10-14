"""Construye Golder_2012_marmol.csv con valores verificados en imagen (ver resumen)."""
import csv, math, sys
from pathlib import Path

OUT = Path(sys.argv[1])
KG = 98.0665  # kPa por kg/cm2

COLS = ["fuente", "anio", "autor_informe", "laboratorio", "set_id", "ensayo_id", "litologia_informe", "litologia",
        "litologia_detalle", "litologia_proporcion", "alteracion", "tipo_material", "clase_desmonte", "tipo_ensayo",
        "saturado", "diametro_mm", "altura_mm", "Dmax_mm", "D10_mm", "D30_mm", "D50_mm", "D60_mm", "Cu", "Cc",
        "grava_pct", "arena_pct", "finos_pct", "escalamiento", "Gs", "gamma_d_kNm3", "e0", "e0_origen", "Dr_pct",
        "w_pct", "UCS_MPa", "sigma3_kPa", "sigma1_kPa", "q_kPa", "criterio_falla", "phi_sec_deg",
        "eps_axial_falla_pct", "eps_vol_falla_pct", "u_falla_kPa", "p_falla_kPa", "q_falla_und_kPa", "Su_kPa",
        "Bg_pct", "Br", "finos_post_pct", "sigma_n_kPa", "tau_kPa", "pagina", "verificado_imagen", "notas"]

# Granulometría inicial (Muestra Inicial, IDIEM pág. 3 de 61 = pág. PDF 27)
sizes = [178, 152, 127, 102, 76, 63.5, 50.8, 38.1, 25.4, 19.0, 9.52, 4.76, 2.0, 0.84, 0.42, 0.25, 0.11, 0.074]
passing = [100, 97.9, 93.2, 87.9, 75.5, 67.6, 59.2, 48.7, 38.0, 31.2, 20.3, 14.7, 10.8, 8.9, 7.9, 7.3, 5.5, 4.9]


def dx(p):
    for (d1, p1), (d2, p2) in zip(zip(sizes, passing), zip(sizes[1:], passing[1:])):
        if p2 <= p <= p1:
            return 10 ** (math.log10(d2) + (p - p2) / (p1 - p2) * (math.log10(d1) - math.log10(d2)))


D10, D30, D50, D60 = dx(10), dx(30), dx(50), dx(60)
Cu, Cc = D60 / D10, D30 ** 2 / (D10 * D60)
print(f"D10={D10:.2f} D30={D30:.2f} D50={D50:.2f} D60={D60:.2f} Cu={Cu:.1f} Cc={Cc:.2f}")

# Probetas: (n, tipo, s3 kg/cm2, fila pico [ea, ev, p, t] kg/cm2, pág. tabla, Bg, finos post, gd_post, e_post, vol drenado cm3)
tests = [
    (1, "Monotónico (ESTATICO)", 5, (17.27, -5.65, 14.08, 9.08), 29, 26.8, 8.2, 2.15, 0.256, 34670),
    (2, "Carga-descarga (CICLICO)", 5, (18.26, -6.95, 13.68, 8.68), 40, 28.6, 8.0, 2.16, 0.250, 41604),
    (3, "Carga-descarga (CICLICO)", 10, (18.00, -8.17, 24.87, 14.87), 52, 40.8, 8.5, 2.20, 0.227, 65378),
    (4, "Monotónico (ESTATICO)", 20, (19.59, -7.69, 49.66, 29.66), 55, 50.2, 10.7, 2.25, 0.200, 92453),
    (5, "Carga-descarga (CICLICO)", 20, (17.78, -9.67, 52.27, 32.27), 70, 55.4, 11.4, 2.29, 0.179, 116227),
]
base = dict(fuente="2012_Golder_Triaxiales Gran Escala en Marmol Negro.pdf", anio=2012,
            autor_informe="Golder Associates Perú, Technical Memorandum Doc. No. 446 (proy. 1014270482C/1194155017P); anexo IDIEM Informe 708.397-A",
            laboratorio="IDIEM, Universidad de Chile (Santiago)", set_id="G2012-MN-C",
            litologia_informe="Black marble rockfill (Mármol negro)", litologia="Mármol", litologia_detalle="mármol negro",
            litologia_proporcion="", alteracion="", tipo_material="Enrocado", clase_desmonte="C",
            saturado="sí", diametro_mm=1000, altura_mm=1800, Dmax_mm=177.8,
            D10_mm=round(D10, 2), D30_mm=round(D30, 2), D50_mm=round(D50, 2), D60_mm=round(D60, 2),
            Cu=34.4, Cc=4.1, grava_pct=round(100 - 14.7, 1), arena_pct=round(14.7 - 4.9, 1), finos_pct=4.9,
            escalamiento="Truncado (scalping) a 178 mm; Dmax de terreno 558.8 mm (macro-granulometría)",
            Gs=2.7, gamma_d_kNm3=round(2.10 * 9.81, 2), e0=0.286, e0_origen="informe", Dr_pct="", w_pct=0.09,
            UCS_MPa=round(992.5 * KG / 1000, 1), Br="", Su_kPa="", sigma_n_kPa="", tau_kPa="", u_falla_kPa="",
            p_falla_kPa="", q_falla_und_kPa="", verificado_imagen="sí")
common_note = ("Material: enrocado de mármol negro para la presa de relaves (texto: 'angular run-of-the-mine material', Tipo C, Fase 5, "
               "polígono 12022607, cota 4478); clasificado aquí como Enrocado por su uso. Gs=2.7 SUPUESTO por el informe (no medido); "
               "e0 del informe con ese Gs. Probeta remoldeada, compactada en 6 capas de 0.3 m con placa vibratoria a gd=2.10 t/m3, "
               "saturada con CO2 + agua, contrapresión 2 kg/cm2, B>0.95. Ensayo controlado por carga (incrementos). "
               "D10–D60 calculados por interpolación log-lineal de la granulometría inicial IDIEM (pág. 27); Cu=34.4 y Cc=4.1 "
               "son los del informe (Fig. 1, pág. 2); con esa interpolación resultan Cu≈37.4 y Cc≈4.3. "
               "grava/arena/finos con cortes 4.76 mm y 0.074 mm. UCS_MPa = promedio de 8 compresiones simples del Informe 379 "
               "(540–1380 kg/cm2 = 53–135 MPa; Tabla 1, pág. 3). Los Ángeles 44 % y 41 % (pág. 17). "
               "Convención εv del informe: negativo = compresión (pág. 8). Conversión 1 kg/cm2 = 98.0665 kPa.")
rows = []
for n, tipo, s3, (ea, ev, p, t), pag, bg, fpost, gdc, ec, vd in tests:
    q = 2 * t
    s1 = s3 + q
    assert abs((p - t) - s3) < 0.02
    phi = math.degrees(math.asin(t / p))
    r = dict(base)
    r.update(ensayo_id=f"Test {n} / Probeta {n} ({'σ' + chr(39)}c = {s3} kg/cm²)", tipo_ensayo="CID",
             sigma3_kPa=round(s3 * KG, 1), sigma1_kPa=round(s1 * KG, 1), q_kPa=round(q * KG, 1),
             criterio_falla="Máximo desviador (pico de t) en la tabla IDIEM",
             phi_sec_deg=round(phi, 1), eps_axial_falla_pct=ea, eps_vol_falla_pct=ev, Bg_pct=bg,
             finos_post_pct=fpost, pagina=f"7;{pag};27;28;17;10",
             notas=(f"Tipo de carga: {tipo}. Tabla IDIEM en kg/cm2 con p=(σ1+σ3)/2 y q=(σ1−σ3)/2; en la falla p={p}, t={t} kg/cm2. "
                    f"phi_sec = asin(t/p) calculado; coincide con la Fig. 5 (pág. 10, leído de gráfico). "
                    f"Tras consolidación: gd={gdc} t/m3, e={ec} (Tabla 3, pág. 7); volumen drenado en consolidación {vd} cm3. "
                    f"finos_post = % pasa #200 de la granulometría post-ensayo IDIEM (págs. 27-28). " + common_note))
    rows.append(r)

# Edómetro (Probeta 6)
r = dict(base)
r.update(ensayo_id="Probeta 6 Odómetro", tipo_ensayo="edómetro", diametro_mm=949.7, altura_mm=900,
         sigma3_kPa="", sigma1_kPa="", q_kPa="", criterio_falla="", phi_sec_deg="", eps_axial_falla_pct="",
         eps_vol_falla_pct="", Bg_pct=28.8, finos_post_pct=9.4, w_pct=0.088, pagina="72;17;28",
         notas=("Edómetro de gran escala (diámetro promedio 94.97 cm, altura 90 cm; pág. 72). gd=2.100 g/cm3, w=0.088 %, "
                "e0=0.284 en estado seco a 0.18 kg/cm2 (Gs integral 2.700). Carga máxima σ'v=60 kg/cm2 (5884 kPa): e=0.170, "
                "gd=2.309 g/cm3. Asentamiento por inundación 0.8 mm (0.09 %). Módulo E≈400 kg/cm2 (σ'v<40) a ≈800 kg/cm2 (40–60). "
                "Permeabilidad 1.4E-1 a 8.2E-2 cm/s entre σ'v=6 y 60 kg/cm2 (Tabla 4, pág. 16). " + common_note))
rows.append(r)

with OUT.open("w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    for r in rows:
        w.writerow({c: r.get(c, "") for c in COLS})
print("filas:", len(rows))
for r in rows:
    print(r["ensayo_id"], r["sigma3_kPa"], r["sigma1_kPa"], r["q_kPa"], r["phi_sec_deg"])
