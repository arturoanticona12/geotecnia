import csv, json, math, os
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.normpath(os.path.join(HERE, "..", "..", "extraido"))
os.makedirs(OUT, exist_ok=True)
K = 98.0665
cols = ("fuente,anio,autor_informe,laboratorio,set_id,ensayo_id,litologia_informe,litologia,litologia_detalle,"
        "litologia_proporcion,alteracion,tipo_material,clase_desmonte,tipo_ensayo,saturado,diametro_mm,altura_mm,Dmax_mm,"
        "D10_mm,D30_mm,D50_mm,D60_mm,Cu,Cc,grava_pct,arena_pct,finos_pct,escalamiento,Gs,gamma_d_kNm3,e0,e0_origen,Dr_pct,"
        "w_pct,UCS_MPa,sigma3_kPa,sigma1_kPa,q_kPa,criterio_falla,phi_sec_deg,eps_axial_falla_pct,eps_vol_falla_pct,"
        "u_falla_kPa,p_falla_kPa,q_falla_und_kPa,Su_kPa,Bg_pct,Br,finos_post_pct,sigma_n_kPa,tau_kPa,pagina,"
        "verificado_imagen,notas").split(',')
FUENTE = "2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
AUT = "WSP Golder (Golder Associates Ltd./Perú) - Memo 20377053-001-TM-Rev1-401001; Doc 105-18028-MTE00420-MEM-430-G-0007 Rev1"
base = dict(fuente=FUENTE, anio=2022, autor_informe=AUT, tipo_material="Enrocado",
            clase_desmonte="", litologia_proporcion="")
HF = dict(litologia_informe="H6 Hornfel Gris / Hornfels (HR)", litologia="Hornfels",
          litologia_detalle="hornfels gris (H6), Tajo Fase 8; vetillas de calcita en núcleos UCS",
          alteracion="No presenta (descripción IDIEM de núcleos UCS, p72-76)")
MN = dict(litologia_informe="Mármol Negro (MN/MR)", litologia="Mármol", litologia_detalle="mármol negro",
          alteracion="")


def phi(q, s3):
    return round(math.degrees(math.asin(q / (q + 2 * s3))), 1)


rows = []
HFgran = dict(Dmax_mm=177.8, D10_mm=2.61, D30_mm=13.3, D50_mm=28.0, D60_mm=35.0, Cu=13.4, Cc=1.93, grava_pct=87.3,
              arena_pct=10.1, finos_pct=2.6,
              escalamiento="Ajustada a Dmax 178 mm (7\") para IDIEM; método de ajuste no declarado. Dmax de terreno ≈914 mm (36\", macro-granulometría M-001, p47)")
V0 = math.pi * 50 ** 2 * 180
tx = [
    ("1", "1.555.677-B.2", "PROBETA 1", 10, 2.10, 3.0, 19.87, 13.13, -5.05, 28920.61, 20, 5.6, "233-236", "monótono",
     "máximo a εa=13.13 %; al final (19.05 %) t=18.81 kg/cm². Fecha en hoja '17-12-2022' (probable errata de 2021)"),
    ("2", "1.555.677-B.2", "PROBETA 2", 20, 2.10, 3.0, 46.19, 19.04, -7.14, 68762.28, 29, 8.0, "238-243", "monótono",
     "máximo coincide con el último registro (εa=19.04 %); curva aún ascendente, sin pico"),
    ("3", "1.555.677-B.2", "PROBETA 3", 25, 2.10, 3.0, 60.83, 17.83, -8.64, 92728.00, 37, 10.4, "245-250", "monótono",
     "máximo a εa=17.83 %; al final (19.63 %) t=60.49 kg/cm²"),
    ("4", "1.555.677-E", "PROBETA 1", 10, 2.06, 5.0, 19.48, 19.15, -6.35, 29390.00, 24, 6.8, "106-117", "carga-descarga",
     "máximo coincide con el último registro (εa=19.15 %)"),
    ("5", "1.555.677-E", "PROBETA 2", 20, 2.06, 5.0, 49.47, 18.80, -7.03, 73737.00, 36, 9.8, "119-167", "carga-descarga",
     "máximo a εa=18.80 %; último registro 19.33 % con t=48.76 kg/cm²"),
    ("6", "1.555.677-E", "PROBETA 3", 25, 2.06, 5.0, 65.92, 18.98, -8.34, 87571.00, 39, 13.5, "169-227", "carga-descarga",
     "máximo a εa=18.98 %; último registro 19.52 % con t=65.47 kg/cm². Probeta con geotextil adicional"),
]
for tid, rep, pid, s3k, gd, w, t, ea, ev, dV, bg, fp, pg, tipo, endn in tx:
    s3 = s3k * K; q = 2 * t * K; Gs = 2.75; e0 = Gs / gd - 1
    r = dict(base, **HF, **HFgran)
    r.update(laboratorio="IDIEM (Universidad de Chile), Informe " + rep,
             set_id="HF-1.0m-IDIEM-" + ("mono" if tipo == "monótono" else "cd"),
             ensayo_id=f"Tabla 3 Hornfels Probeta {tid} = IDIEM {rep} {pid}",
             tipo_ensayo="CID " + tipo + ("" if tipo == "monótono" else " (4 etapas: ciclos de carga-descarga hasta 50 % τu y luego carga monótona)"),
             saturado="sí (CO2 + agua desaireada, B>0.95)", diametro_mm=1000, altura_mm=1800, Gs=Gs,
             gamma_d_kNm3=round(gd * 9.81, 2), e0=round(e0, 3), e0_origen="calculado", w_pct=w, UCS_MPa="64.5",
             sigma3_kPa=round(s3), sigma1_kPa=round(s3 + q), q_kPa=round(q),
             criterio_falla="máximo desviador registrado (ensayo hasta εa≈20 %)",
             eps_axial_falla_pct=ea, eps_vol_falla_pct=ev, Bg_pct=bg, finos_post_pct=fp,
             pagina=f"10;{pg};62-63;41", verificado_imagen="sí",
             notas=(f"σ'c={s3k} kg/cm² (cámara−contrapresión). Tablas IDIEM en kg/cm² con q=(σ1−σ3)/2; aquí ×98.0665 y desviador=2q. "
                    f"t_max={t} kg/cm²; {endn}. φsec calculado (no informado por probeta) = {phi(q, s3)}°; el informe da rango 42–46° (Fig. 16, p19-20). "
                    "εv negativa = compresión (convención del informe). "
                    f"ΔV drenado en consolidación = {dV:.0f} cm³ (≈{dV / V0 * 100:.1f} % de V0) → e al inicio del corte ≈{(1 + e0) * (1 - dV / V0) - 1:.3f}. "
                    f"Gs no informado en hojas IDIEM: se adoptó Gs=2.75 ('calculated' por Golder para el mismo HR, p353); IDIEM usó Gs=2.60 'estimado' en el edómetro (con 2.60, e0={2.60 / gd - 1:.3f}). "
                    "UCS 64.5 MPa = media de M-1 (65) y M-2 (64), Tabla 1 p7; IDIEM 2022 obtuvo 24.5–40.8 MPa en núcleos con vetillas de calcita (p72-76). "
                    "Granulometría inicial = 'H6 Hornfel Gris (Inicial)' 1.0 m, p62 (D interpolados log-lineal). Bg de Tabla 7 (p41), reproducido desde las granulometrías p62-63. "
                    "Muestra remoldeada; compactada en 6 capas de 0.3 m con pisón vibrador, densidad objetivo 2.1 t/m³."))
    rows.append(r)

g015 = dict(Dmax_mm=25.4, D10_mm=0.19, D30_mm=1.73, D50_mm=4.55, D60_mm=6.4, Cu=34, Cc=2.5, grava_pct=49, arena_pct="",
            finos_pct="",
            escalamiento="Dmax 25.4 mm (1\"); curva aprox. paralela (factor ≈7) a la de 1.0 m según Fig. 3; método no declarado")
r = dict(base, **HF, **g015)
r.update(laboratorio="Golder Associates Ltd., Burnaby (Lab ID B21-132)", set_id="HF-0.15m-Golder",
         ensayo_id="Tabla 3 Hornfels Probeta 7 = CID 6\" HR (Golder B21-132)",
         tipo_ensayo="CID carga-descarga (misma trayectoria de 4 etapas que IDIEM)",
         saturado="sí (B=0.99; Sat 99 % tras consolidación)", diametro_mm=152.0, altura_mm=327.0, Gs=2.75,
         gamma_d_kNm3=20.58, e0=0.31, e0_origen="informe", w_pct=3.4, UCS_MPa="64.5", sigma3_kPa=977,
         sigma1_kPa=5076, q_kPa=4100,
         criterio_falla="máximo desviador según hoja Golder ('Failure at maximum deviator stress')",
         eps_axial_falla_pct=11.44, eps_vol_falla_pct=-5.31, Bg_pct=15, pagina="10;350;353;351;6;41",
         verificado_imagen="sí",
         notas=("σ'3c en consolidación = 992 kPa; σ'3 en falla 977 kPa. Tras consolidación: γd 21.62 kN/m³, ec 0.25, Dc 14.90 cm, Hc 32.39 cm. "
                f"φsec calculado con la hoja = {phi(4100, 977)}°. INCONSISTENCIA: la curva desviador–εa (p351) sigue subiendo hasta ≈4,600 kPa a εa≈17.5 % (leído de gráfico); con ese valor φ≈44.6°, coherente con los 45° que cita el informe (p19). "
                "La leyenda de la hoja dice '-ve = dilation, +ve = contraction', pero la curva y el texto del informe indican compresión negativa; se conserva el signo de la hoja (−5.31 % = compresión). "
                "Granulometría inicial NO tabulada: D leídos de gráfico (Fig. 3, p6, marcadores vectoriales); ≈8.9 % pasa 0.15 mm; finos <0.075 mm no legibles. "
                "Texto: densidad objetivo 2.2 t/m³ (corrección Dorador 2018), pero la hoja da 20.58 kN/m³ (2.10 t/m³). ρmáx/ρmín índice HR (ASTM D4253/4254, p85): 2232 (seco)/2308 (húmedo)/1852 kg/m³; Dr no informado."))
rows.append(r)

usc = [("HR-LCTX2", "HF", 146.5, 266.7, 21.46, 2.71, 0.19, 0.38, 1420.40, 20.00, "1420.40", 373, "6\""),
       ("HR-CTX1", "HF", 100.0, 203.2, 21.46, "", None, 0.33, 1280.00, 1.68, "1280", 361, "4\""),
       ("HR-CTX4", "HF", 100.0, 203.2, 21.46, "", None, 0.20, 1210.54, 7.37, "1210.54", 367, "4\""),
       ("MN-CTX3", "MN", 100.0, 203.2, 22.07, "", None, 0.25, 1245.30, 4.89, "1245.3", 379, "4\""),
       ("MN-LCTX1", "MN", 146.5, 266.7, 22.07, 2.71, 0.21, 0.19, 1575.90, None, "1392.7", 385, "6\""),
       ("MN-LCTX2", "MN", 146.5, 266.7, 22.07, 2.71, 0.25, 0.38, 1550.50, None, "1414.80", 391, "6\"")]
for lid, mat, D, H, gd, Gs, ec, csr, qmax, ea, q20, pg, dia in usc:
    lit = HF if mat == "HF" else MN
    r = dict(base, **lit, **g015)
    gs_use = Gs if Gs != "" else 2.71
    e0 = gs_use * 9.81 / gd - 1
    gsnote = " (Gs estimado USC)" if Gs != "" else " (Gs no informado para probetas 4\"; se adoptó 2.71 de las probetas 6\" USC)"
    r.update(laboratorio="University of South Carolina (USC), GDS ELDyn", set_id=f"{mat}-USC-ciclico-350",
             ensayo_id=f"USC {lid} ({dia}, CSR={csr})",
             tipo_ensayo="Triaxial cíclico drenado (compresión-extensión) + carga monótona drenada post-cíclica",
             saturado="sí (B=0.95–0.97)", diametro_mm=D, altura_mm=H, Gs=Gs, gamma_d_kNm3=gd, e0=round(e0, 3),
             e0_origen="calculado", w_pct=5.0, UCS_MPa=("64.5" if mat == "HF" else ""), sigma3_kPa=350,
             sigma1_kPa=round(350 + qmax, 1), q_kPa=qmax,
             criterio_falla="máximo desviador en la carga monótona post-cíclica (hoja USC 'Max. Principal Stress Difference')",
             eps_axial_falla_pct=(ea if ea is not None else ""),
             Bg_pct=(8 if mat == "HF" else 6), pagina=f"10;{pg};41", verificado_imagen="sí",
             notas=(f"Hoja USC marcada DRAFT. Velocidad 5 %/h; 'Max. Axial Strain'={20.0 if ea is None else ea} %, desviador a esa deformación={q20} kPa"
                    + ("" if ea is not None else " (el máximo ocurrió antes; εa del máximo no informada)") + ". "
                    f"φsec calculado (post-cíclico) = {phi(qmax, 350)}°. e después de consolidación (hoja) = {ec if ec is not None else 'no informado'}. "
                    f"e0 calculado con Gs={gs_use}{gsnote}. "
                    "Bg de Tabla 7 es un valor único (celda combinada) para el conjunto de probetas cíclicas del material. "
                    "Correspondencia con Tabla 3 ambigua: Tabla 3 asigna Hornfels 6\"-0.50, 4\"-0.40, 4\"-0.33 y Mármol 6\"-0.25, 6\"-0.20, 4\"-0.40; el anexo USC da HR 6\"-0.38, 4\"-0.33, 4\"-0.20 y MN 4\"-0.25, 6\"-0.19, 6\"-0.38. "
                    "Granulometría = curva objetivo 0.15 m leída de Fig. 3/4 (no hay granulometría por probeta). σ'3=350 kPa: bajo confinamiento."))
    if lid == "MN-LCTX1":
        r['notas'] += " e0 calculado (0.205) < e tras consolidación (0.21): inconsistencia de Gs/γd en la hoja."
    rows.append(r)

r = dict(base, **MN, **g015)
r.update(laboratorio="Golder Associates Ltd., Burnaby (Lab ID B21-132)", set_id="MN-0.15m-Golder",
         ensayo_id="Tabla 3 Mármol Negro Probeta 6 = CID 6\" MR (Golder B21-132)", tipo_ensayo="CID carga-descarga",
         saturado="sí (B=0.99)", diametro_mm=151.9, altura_mm=330.0, Gs=2.70, gamma_d_kNm3=20.37, e0=0.30,
         e0_origen="informe", w_pct=3.5, sigma3_kPa=982, sigma1_kPa=4805, q_kPa=3823,
         criterio_falla="máximo desviador (hoja Golder)", eps_axial_falla_pct=18.51, eps_vol_falla_pct=-6.51,
         Bg_pct=30, pagina="10;357;355;7;41", verificado_imagen="sí",
         notas=(f"σ'3c consolidación 976 kPa; tras consolidación γd 21.50 kN/m³, ec 0.23. φsec calculado = {phi(3823, 982)}°; el texto (p24) dice 45° para esta probeta (inconsistente). "
                "Errata en hoja: w post 27.4 % y saturación 319 %. Convención de εv como en Hornfels 6\". Mármol de la campaña 2021. "
                "UCS mármol 2021: 42–44 MPa (Tabla 2) vs 66.9–103.5 MPa (IDIEM 2022, REG 41061, p78-82). ρmáx/ρmín índice MR (p86): 2297 (seco)/2398 (húmedo)/1905 kg/m³. Granulometría leída de Fig. 4 (p7)."))
rows.append(r)

MNgran = dict(Dmax_mm=178, D10_mm=1.39, D30_mm=17.6, D50_mm=39.5, D60_mm=51.9, Cu=37.4, Cc=4.3, grava_pct=85.3,
              arena_pct=9.8, finos_pct=4.9, escalamiento="Dmax 178 mm (7\"); método no declarado")
mn11 = [("1", "Probeta 1 (σ'c = 5 kg/cm²) ESTATICO", 5, 9.08, 17.27, -5.65, 34670, 13, 8.2, "252", "monótono"),
        ("3", "Probeta 2 (σ'c = 5 kg/cm²) CICLICO", 5, 8.68, 18.26, -6.95, 41604, 14, 8.0, "254-263", "carga-descarga"),
        ("4", "Probeta 3 (σ'c = 10 kg/cm²) CICLICO", 10, 14.87, 18.00, -8.17, 65378, 20, 8.5, "265-275", "carga-descarga"),
        ("2", "Probeta 4 (σ'c = 20 kg/cm²) ESTATICO", 20, 29.66, 19.59, -7.69, 92453, 25, 10.7, "277-278", "monótono"),
        ("5", "Probeta 5 (σ'c = 20 kg/cm²) CICLICO", 20, 32.27, 17.78, -9.67, 116227, 28, 11.4, "280-293", "carga-descarga")]
for tid, pid, s3k, t, ea, ev, dV, bg, fp, pg, tipo in mn11:
    s3 = s3k * K; q = 2 * t * K
    r = dict(base, **MN, **MNgran)
    r.update(laboratorio="IDIEM (2011), Informe 708.397-A", set_id="MN-1.0m-IDIEM-2011",
             ensayo_id=f"Tabla 3 Mármol Negro Probeta {tid} = IDIEM 708.397-A {pid}", tipo_ensayo="CID " + tipo,
             saturado="no indicado en la hoja (procedimiento IDIEM saturado)", diametro_mm=1000, altura_mm=1800, Gs=2.70,
             gamma_d_kNm3=round(2.10 * 9.81, 2), e0=round(2.70 / 2.10 - 1, 3), e0_origen="calculado", w_pct=0.09,
             sigma3_kPa=round(s3), sigma1_kPa=round(s3 + q), q_kPa=round(q),
             criterio_falla="máximo desviador registrado (ensayo hasta εa≈20 %)", eps_axial_falla_pct=ea,
             eps_vol_falla_pct=ev, Bg_pct=bg, finos_post_pct=fp, pagina=f"10;{pg};66-67;41", verificado_imagen="sí",
             notas=(f"DUPLICADO: ensayo de 2011 ya reportado en Golder (2012) — no sumar dos veces. t_max={t} kg/cm²; φsec calculado = {phi(q, s3)}° (informe: 40° a 0.5 MPa → 36° a 2.0 MPa, p24). "
                    f"ΔV consolidación {dV} cm³ (≈{dV / V0 * 100:.1f} %). Gs=2.70 'peso específico integral' de la hoja del odómetro 2011 (p295). UCS mármol 2011: 53–136 MPa (Tabla 2). "
                    "Granulometría inicial 'Muestra Inicial' 2011 (p66); finos post = columna de la probeta (p66-67). εv negativa = compresión."))
    rows.append(r)


def edo(set_id, eid, lit, lab, D, H, gd, Gs, e0, eo, w, smax, evmax, bg, pg, notes, gran):
    r = dict(base, **lit, **gran)
    r.update(laboratorio=lab, set_id=set_id, ensayo_id=eid, tipo_ensayo="edómetro (compresión unidimensional)",
             saturado="sí (inundado a carga inicial)", diametro_mm=D, altura_mm=H, Gs=Gs,
             gamma_d_kNm3=round(gd * 9.81, 2), e0=e0, e0_origen=eo, w_pct=w, Bg_pct=bg, pagina=pg,
             verificado_imagen="sí", notas=f"σv máx = {smax} kPa; εv a σv máx = {evmax} %. " + notes)
    rows.append(r)


edo("HF-edo-1.0m", "Tabla 4 Hornfels Probeta 1 = IDIEM 1.555.677-B.1 (H6 Hornfel Gris)", HF,
    "IDIEM, Informe 1.555.677-B.1 (encabezado de hoja 1.555.677-A)", 1000, 700, 2.10, 2.60, 0.238, "informe", 1.69,
    round(70 * K), 5.01, 23, "31;300-302;62;41",
    "Curva completa en WSP_2022_edometro.csv. Gs 2.60 'estimado' por IDIEM. Permeabilidad 3.5e-2 → 3.5e-3 cm/s (588–6865 kPa, Tabla 5). Fecha inicio '05-11-2022' (errata; término 20-01-2022). Altura 0.70 m (Tabla en p4 dice 0.9 m).",
    HFgran)
edo("HF-edo-0.24m-2.1", "Tabla 4 Hornfels Probeta 2 (Golder 0.24 m)", HF, "Golder Associates Ltd., Burnaby", 240, "",
    2.1, "", "", "", "", 4799, 6.1, 12, "31;35;41",
    "Curva SOLO en gráfico (Fig. 33c, p35): leída de marcadores vectoriales. Tabla 4 y texto: se compactó a 2.1 t/m³ (no se logró 2.3); Tabla 7 la rotula 2.3 t/m³. Altura ≈0.20 m (texto). Sin hoja de laboratorio en anexo C.",
    dict(Dmax_mm=25.4))
edo("HF-edo-0.24m-1.8", "Tabla 4 Hornfels Probeta 3 (Golder 0.24 m)", HF, "Golder Associates Ltd., Burnaby", 240, "",
    1.8, "", "", "", "", 4799, 17.5, 8, "31;35;41",
    "Curva SOLO en gráfico (Fig. 33d, p35), leída de marcadores vectoriales; texto: 17 % a 4.8 MPa. Densidad ≈92 % Proctor estándar.",
    dict(Dmax_mm=25.4))
edo("MN-edo-1.0m-2021", "Tabla 4 Mármol Negro Probeta 2 = IDIEM 1.555.677-A REV2 MARMOL (REG 41061)", MN,
    "IDIEM, Informe 1.555.677-A REV2", 1000, 700, 2.10, 2.60, 0.238, "informe", 1.50, round(70 * K), 6.39, 45,
    "31;324;41", "Curva completa en WSP_2022_edometro.csv. Permeabilidad 1.2e-2 → 2.7e-3 cm/s (Tabla 6).", {})
edo("MN-edo-1.0m-2011", "Tabla 4 Mármol Negro Probeta 1 = IDIEM 708.397-A Probeta 6 Odómetro", MN,
    "IDIEM (2011), Informe 708.397-A", 949.7, 900, 2.10, 2.70, 0.284, "informe", 0.088, round(60 * K), 9.03, 14,
    "31;295;67;41",
    "DUPLICADO de Golder (2012). e=0.284 a 0.18 kg/cm² en estado seco. Tabla 7 indica 6,800 kPa pero la hoja llega a 60 kg/cm² (5,884 kPa). εv=(90−81.87)/90.",
    {})
edo("MN-edo-0.24m-1.86", "Tabla 4 Mármol Negro Probeta 4 = Golder 'Test 1' MR (B21-132)", MN,
    "Golder Associates Ltd., Burnaby", 241, 202, 1.856, 2.70, 0.455, "informe", 1.20, 4799, 15.63, 21, "31;359;41",
    "Gs 2.70 'assumed'. Primer escalón (0→200 kPa) produce 6.86 %. El texto (p31) invierte la numeración de las probetas 3/4 de mármol respecto de Tabla 4 y cita 17 % (la hoja da 15.63 % a 4,799 kPa).",
    {})

with open(os.path.join(OUT, "WSP_2022_hornfels3B.csv"), 'w', newline='', encoding='utf-8') as f:
    wr = csv.DictWriter(f, fieldnames=cols)
    wr.writeheader()
    for r in rows:
        wr.writerow({c: ("" if r.get(c) is None else r.get(c, "")) for c in cols})
print('rows', len(rows))

E = json.load(open(os.path.join(HERE, 'edo.json')))
H24 = json.load(open(os.path.join(HERE, 'edo024_hf.json')))
ed = []
for s, e_, ev, p in E['HF']:
    ed.append(("HF-edo-1.0m (IDIEM)", round(s * K, 1), e_, ev, p, "tabla IDIEM; σ kg/cm²×98.0665; e con Gs 2.60 (estimado)"))
for s, e_, ev, p in E['MN21']:
    ed.append(("MN-edo-1.0m-2021 (IDIEM)", round(s * K, 1), e_, ev, p, "tabla IDIEM; e con Gs 2.60 (estimado)"))
T = [0.18, 0.18, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40, 45, 50, 55, 60, 50, 40, 36,
     32, 28, 24, 20, 16, 12, 8, 4, 0.18]
assert len(T) == len(E['MN11'])
for i, (s, (hh, rho, ev, p)) in enumerate(zip(T, E['MN11'])):
    ed.append(("MN-edo-1.0m-2011 (IDIEM 708.397-A)", round(s * K, 1), round((90 - hh) / 90 * 100, 2), ev, 295,
               "εv=(90−H)/90 con H de la hoja; e de la hoja" + ("; estado seco" if i == 0 else ("; tras saturación" if i == 1 else ""))))
G = [(0, 0, 0.455), (200, 6.86, .355), (400, 8.11, .337), (800, 9.93, .310), (1200, 10.85, .297), (1600, 11.61, .286),
     (1999, 12.13, .278), (2400, 12.66, .270), (2800, 13.18, .263), (3200, 13.73, .255), (3600, 14.22, .248),
     (3999, 14.72, .240), (4399, 15.02, .236), (4799, 15.63, .227), (4000, 15.42, .230), (3200, 15.19, .234),
     (2400, 14.92, .238), (1600, 14.62, .242), (1200, 14.46, .244), (2200, 14.82, .239), (3200, 15.16, .234),
     (4000, 15.42, .230), (4800, 15.67, .227), (3000, 15.16, .234), (1000, 14.42, .245), (0, 12.89, .267)]
for i, (s, ev_, e_) in enumerate(G):
    ed.append(("MN-edo-0.24m-1.86 (Golder Test 1)", s, ev_, e_, 359,
               "hoja Golder; εv=ΣΔH/H0; e con Gs 2.70 assumed" + ("; estado inicial" if i == 0 else "")))
for k, lab, fig in [('HF_P2_024', "HF-edo-0.24m-2.1 (Golder)", "c"), ('HF_P3_024', "HF-edo-0.24m-1.8 (Golder)", "d")]:
    for s, ev_ in H24[k]:
        s2 = 0 if s < 30 else s
        ed.append((lab, s2, max(ev_, 0.0), "", 35,
                   f"leído de gráfico (marcadores vectoriales Fig. 33{fig}); incertidumbre ≈±30 kPa y ±0.05 %"))
with open(os.path.join(OUT, "WSP_2022_edometro.csv"), 'w', newline='', encoding='utf-8') as f:
    wr = csv.writer(f)
    wr.writerow(["ensayo_id", "sigma_v_kPa", "eps_v_pct", "e", "pagina", "notas"])
    for row in ed:
        wr.writerow(row)
print('edo rows', len(ed))


def first_load(seq):
    out = []; m = -1
    for s, e in seq:
        if s >= m:
            out.append((s, e)); m = s
        else:
            break
    return out


def M(seq, a, b):
    xs = [x[0] for x in seq]; ys = [x[1] for x in seq]
    return (b - a) / ((np.interp(b, xs, ys) - np.interp(a, xs, ys)) / 100) / 1000


def Cc(seq, a, b):
    xs = [x[0] for x in seq]; es = [x[1] for x in seq]
    return (np.interp(a, xs, es) - np.interp(b, xs, es)) / math.log10(b / a)


hf = first_load([(s * K, e) for s, e, _, _ in E['HF']][1:])
mn = first_load([(s * K, e) for s, e, _, _ in E['MN21']][1:])
p2 = first_load([(s, e) for s, e in H24['HF_P2_024']])
p3 = first_load([(s, e) for s, e in H24['HF_P3_024']])
g = first_load([(s, e) for s, e, _ in G])
mn11 = first_load([(s * K, (90 - h) / 90 * 100) for s, (h, _, _, _) in zip(T, E['MN11'])][1:])
for n, sq in [('HF1.0', hf), ('MN21', mn), ('HFP2', p2), ('HFP3', p3), ('MNg', g), ('MN11', mn11)]:
    print(n, 'M 0-500', round(M(sq, sq[0][0], 500)), 'M 500-4500', round(M(sq, 500, 4500)),
          'Msec max', round(sq[-1][0] / (sq[-1][1] / 100) / 1000), 'max', sq[-1])
hfe = first_load([(s * K, ev) for s, _, ev, _ in E['HF']][1:])
mne = first_load([(s * K, ev) for s, _, ev, _ in E['MN21']][1:])
print('Cc HF 981-6865', round(Cc(hfe, 981, 6865), 3), 'MN21', round(Cc(mne, 981, 6865), 3),
      'MNg 1000-4799', round(Cc([(s, e) for s, _, e in G[1:14]], 1000, 4799), 3))
