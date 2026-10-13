# -*- coding: utf-8 -*-
"""Tablas de condiciones por set (VERIFICACION.md, sección A). Cada dato se comprobó en la
imagen de la página citada (PNG en esta carpeta). 'no informado' = no está en el informe."""
import os, pandas as pd
BASE = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Aporte_alto_confinamiento\datos_antamina"
OUT = os.path.join(BASE, "verificado")
NI = "no informado"
COLS = ["fuente", "set_id", "tipo_ensayo", "n_probetas", "origen_muestra", "clase_desmonte", "litologia", "litologia_detalle",
        "litologia_proporcion", "Dmax_campo_mm", "granulometria_campo", "densidad_campo", "escalamiento_metodo", "Dmax_lab_mm",
        "D_probeta_mm", "H_probeta_mm", "D_sobre_Dmax", "granulometria_lab", "preparacion", "gamma_d_montaje_kNm3",
        "w_montaje_pct", "Gs_valor", "Gs_origen", "e0_recalculado", "e0_csv_extraido", "e0_alternativas", "saturacion",
        "contrapresion_kPa", "consolidacion", "gamma_d_post_consolidacion_kNm3", "drenaje_corte", "velocidad_pct_min",
        "deformacion_final_pct", "criterio_falla_informe", "hay_pico", "hay_curva_tabulada", "Bg_metodo", "UCS",
        "Is50", "LA_pct", "durabilidad", "absorcion_pct", "paginas", "verificado_imagen", "notas"]

W = "2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
G = "2012_Golder_Triaxiales Gran Escala en Marmol Negro.pdf"

# --- bloques comunes -------------------------------------------------------------
HF_ORIG = ("Tajo Mina, Fase 8 / Norte, Pala 11, polígono 8-NP-4193-46-03, cota 4193 m s.n.m.; macro-granulometría M-001 muestreada 23/10/2020 por W. Paz (p47). "
           "Muestras UCS/LA M-001: 'Tajo Mina - Fase 8', lugar 'Acopio punto F / M-01 y M-02', 31/10/2020 (p48–p51). Texto: del Tajo al Acopio G (p4). "
           "Lote IDIEM 'H6 HORNFEL GRIS': fecha y lugar de muestreo '----', recibido 12/04/2021 (p59, p231). 39 t enviadas a IDIEM (<7\"), 200 kg a Golder y USC (<1\") (p5–p6)")
HF_LIT = "Hornfels gris (H6, 'HG (Hornfels Gris)'); descripción visual en hojas; sin petrografía ni conteo de fragmentos; núcleos IDIEM con vetillas de calcita, sin alteración (p72–p76)"
HF_CLASE = "C: rótulo manuscrito 'MATERIAL TIPO C – HORNFELS GRIS – TAJO MINA FASE 8' en fotos de probetas UCS/LA (p8, p48–p51). Material de enrocado 3B para recrecimiento de la presa (p3)"
HF_CAMPO = ("Macro-granulometría M-001 (ASTM D5519/D6913, p47): 100 % pasa 36\" (914 mm); 88.2 % pasa 16\"; 58.3 % pasa 6\"; 31.5 % pasa 1\"; 13.1 % pasa #4; 2.49 % pasa #200; "
            "Cu 33.0 y Cc 2.5 (calculados por el informe con material <3\"); GW-GM; humedad en blanco. Calculado aquí (log-lineal, curva completa): D10≈2.6 mm, D50≈86 mm, D80≈288 mm")
MN21_ORIG = ("Tajo Mina, Fase 8 Sur (Pala 10, rótulo de foto), polígono 8-NP-4133-25-04, Acopio punto G; muestreado 23–24/11/2020 por A. Tabata / M. Vilela (p52–p56); texto: Acopio Punto G (p8). "
             "Lote IDIEM 'MARMOL (REG 41061)' / 'MARMOL NEGRO': recibido 12/04/2021, muestreo '----' (p59, p322). 7 t a IDIEM (<7\"), 200 kg a Golder y USC (<1\")")
MN21_CAMPO = ("Macro-granulometría M-001 mármol (p52): 100 % pasa 36\"; 95.1 % pasa 16\"; 68.6 % pasa 6\"; 29.5 % pasa 1\"; 11.95 % pasa #4; 4.07 % pasa #200; Cu 113.1, Cc 7.0 (informe, mat. <3\"); GP-GM; humedad 4.2 %. "
              "Calculado aquí: D10≈2.6 mm, D50≈66 mm, D80≈193 mm")
MN21_CLASE = "C: rótulo 'MATERIAL TIPO C – MARMOL NEGRO (MN) – polígono 8-NP-4133-25-04 – Acopio punto G – Fase 8 Sur Pala 10' en fotos UCS/LA (p9, p53–p56)"
DENS_CAMPO = "no informada (sin ensayo de densidad in situ). La 'densidad especificada' de 2.1 t/m³ se describe como ≈97 % del Proctor estándar ESTIMADO por correlación (Dorador et al. 2018), no medido (p31–p32)"
UCS_HF = ("(1) Golder 2021a, CQA Antamina, ASTM D7012 Método C: muestra M-001/M-01: 66.0 y 64.5 MPa (prom. 65.3), M-001/M-02: 65.1 y 62.5 MPa (prom. 63.8); núcleos 74–74.6 mm, L/D 1.9 (p49, p51); "
          "la Tabla 1 (p7) los resume como 65 y 64 MPa (la carga de M-2, 27,259 kg, es errata: el promedio de la hoja es 28,258.5 kg). "
          "(2) IDIEM 1.555.677-D (15/06/2022), ASTM D7012-14e1, 3 núcleos de 54 mm del lote 'H6 HORNFEL GRIS' enviado a IDIEM: 26.3, 40.8 y 24.5 MPa (corregidos a D50; 25.9, 40.2, 24.1 a D54); "
          "ρd de roca 2.66, 2.71, 2.69 g/cm³; falla 'Mixta (Tipo B2)'; vetillas de calcita (p72, p74, p76). El texto del memo solo cita (1)")
LA_HF = "15.5 (M-01) y 17.3 (M-02); prom. 16.4. ASTM C535, gradación 2, 1000 rev. (p48, p50). El texto (p38) dice 'promedio de 17 %'"
UCS_MN21 = ("(1) Golder 2021a, ASTM D7012 C: M-001: 45.6 y 42.9 MPa (prom. 44.3); M-002: 42.6 y 40.5 MPa (prom. 41.5); núcleos 68.5–69 mm (p54, p56); Tabla 2 (p8): 44 y 42 MPa. "
            "(2) IDIEM 1.555.677-D, 3 núcleos 54 mm de 'REG 41061' (= lote de mármol del edómetro IDIEM 2021): 96.6, 66.9 y 103.5 MPa (D50); ρd roca 2.74–2.75 g/cm³; falla por matriz (Tipo A) (p78, p80, p82)")
LA_MN21 = "55.8 (M-001) y 45.2 (M-002), ASTM C535 gradación 2 (p53, p55). El texto (p38) dice 'entre 45 % y 50 %': el 55.8 % lo contradice"
UCS_MN11 = ("Informe 379 (Golder 2011), 8 probetas M1-1…M4-2, Ø 45–45.5 mm, L/D 2.0: 540, 1110, 1080, 1310, 560, 620, 1380, 1340 kg/cm² (= 53–135 MPa; prom. 97.3 MPa) "
            "(Golder 2012 Tabla 1 p3). WSP 2022 Tabla 2 (p8) recalcula de la carga: 53, 108, 106, 129, 54, 61, 136, 132 MPa (mismos ensayos; diferencia solo de redondeo). Norma no indicada; Informe 379 no incluido")
LA_MN11 = "44 y 41 (2 muestras; Informe 379; Golder 2012 p17). WSP p38 lo resume como 43 %. Norma no indicada"
HF_LAB_GRAD = ("IDIEM inicial (p62, ASTM D422): 100 % pasa 177.8 mm; D10 2.61, D30 13.3, D50 28.0, D60 35.0 mm; Cu 13.4, Cc 1.94 (recalculados log-lineal; el informe no los da); "
               "grava 87.3, arena 10.1, finos 2.6 %")
SMALL_GRAD = ("Sin tabla: solo curva 'INICIAL 0.15m' (Fig. 3 p6 hornfels; Fig. 4 p7 mármol, idénticas). Leída de la figura: 100 % pasa 25.4 mm, ≈72 % 9.5 mm, ≈51 % 4.76 mm, ≈32 % 2 mm, ≈9 % 0.15 mm; "
              "D10≈0.19, D30≈1.7, D50≈4.6, D60≈6.4 mm; Cu≈34")
BG_IDIEM = "Marsal (1967): suma de diferencias positivas de % retenido por fracción, antes y después; tamices 7\" a #200 (18 tamices) + fondo"

rows = []
def R(**k):
    d = {c: k.get(c, NI) for c in COLS}; rows.append(d)

# ===================== WSP 2022 =====================
R(fuente=W, set_id="HF-1.0m-IDIEM-mono", tipo_ensayo="CID monótono (IDIEM 1.555.677-B.2)", n_probetas="3 (σ'c 10, 20, 25 kg/cm²)",
  origen_muestra=HF_ORIG, clase_desmonte=HF_CLASE, litologia="Hornfels", litologia_detalle=HF_LIT, litologia_proporcion="no aplica (monolitológico)",
  Dmax_campo_mm="entre 406 y 914 (100 % pasa 36\"; 11.8 % retenido en 16\"); valor exacto no informado", granulometria_campo=HF_CAMPO, densidad_campo=DENS_CAMPO,
  escalamiento_metodo="'ajustadas a granulometrías con tamaño menor a 178 mm (7\")' (p4); método no declarado (ni paralelo ni truncado)",
  Dmax_lab_mm="177.8", D_probeta_mm="1000", H_probeta_mm="1800", D_sobre_Dmax="5.6", granulometria_lab=HF_LAB_GRAD,
  preparacion="Molde Ø1.0×1.8 m con 2 membranas de 5 mm y geotextil; 6 capas de 0.3 m de material seco compactadas con pisón vibrador a ρd objetivo 2.1 t/m³; vacío ≈30 kPa para desmoldar (p11). Densidad 'especificada' (≈97 % Proctor estándar estimado) (p31)",
  gamma_d_montaje_kNm3="20.60 (ρd 2.10 g/cm³ en las 3 hojas)", w_montaje_pct="3.00 (hojas p233, p238, p245)",
  Gs_valor="2.75", Gs_origen="NO ensayado sobre estas probetas: las hojas IDIEM no traen Gs. 2.75 = 'Specific Gravity (calculated)' de Golder Burnaby sobre el mismo lote <1\" (p350, p353), método no descrito. Otros valores del mismo material: 2.71 'Estimated' (USC, p373) y 2.60 'estimado' (IDIEM edómetro, p300), este último incompatible con ρd de núcleos 2.66–2.71",
  e0_recalculado="0.310", e0_csv_extraido="0.31", e0_alternativas="Gs 2.71 → 0.290; Gs 2.60 → 0.238",
  saturacion="CO2 24 h + agua desaireada; saturada si B > 0.95 (p13). Valor de B por probeta no informado",
  contrapresion_kPa="196 (P1), 98 (P2), 196 (P3) [2.00/1.00/2.00 kg/cm², hojas p233/p238/p245]",
  consolidacion="Isotrópica, incremental hasta σ'c = 10, 20 y 25 kg/cm² (981, 1961, 2452 kPa); ΔV drenado 28,920.61 / 68,762.28 / 92,728 cm³; duración no informada",
  gamma_d_post_consolidacion_kNm3="no informado; calculado de ΔV/V0 (V0=1.4137 m³): 21.03, 21.65, 22.05",
  drenaje_corte="Drenado", velocidad_pct_min="no informada en hoja ('--'); texto: carga controlada ≈98 kPa/min (p13)",
  deformacion_final_pct="19.05 / 19.04 / 19.63", criterio_falla_informe="'Ángulo de fricción máximo' (p19) a partir del máximo de t=(σ1−σ3)/2",
  hay_pico="P1: pico leve (máx. a 13.13 %, −5.3 % al final); P2: no (máx. = último punto); P3: meseta (máx. 17.83 %)",
  hay_curva_tabulada="sí (εa, εv, p, q en kg/cm²; p233–p250)", Bg_metodo=BG_IDIEM + "; post-ensayo p62–p63. Bg Tabla 7: 20, 29, 37 (recalculado 20.3, 29.3, 36.5)",
  UCS=UCS_HF, Is50=NI, LA_pct=LA_HF, durabilidad=NI, absorcion_pct=NI,
  paginas="4–8;11;13;31;41;47–51;59;62–63;72–76;233–250;300;350;373", verificado_imagen="sí",
  notas="Fechas de las hojas '17-12-2022 a 23-12-2022' posteriores a la emisión del memo (sept. 2022): errata. Probeta 2 con contrapresión distinta (1 kg/cm²).")

R(fuente=W, set_id="HF-1.0m-IDIEM-cd", tipo_ensayo="CID carga-descarga, 4 etapas (IDIEM 1.555.677-E)", n_probetas="3 (σ'c 10, 20, 25 kg/cm²)",
  origen_muestra=HF_ORIG, clase_desmonte=HF_CLASE, litologia="Hornfels", litologia_detalle=HF_LIT, litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914; no informado exacto", granulometria_campo=HF_CAMPO, densidad_campo=DENS_CAMPO,
  escalamiento_metodo="no declarado (p4)", Dmax_lab_mm="177.8", D_probeta_mm="1000", H_probeta_mm="1800", D_sobre_Dmax="5.6", granulometria_lab=HF_LAB_GRAD,
  preparacion="Igual procedimiento que los monótonos (p11), pero las hojas dan ρd 2.06 g/cm³ y w 5 %, menor que el objetivo 2.1 t/m³",
  gamma_d_montaje_kNm3="20.21 (ρd 2.06 g/cm³; p106, p119, p169)", w_montaje_pct="5.00",
  Gs_valor="2.75", Gs_origen="Igual que set monótono (Golder 'calculated', otro laboratorio, mismo lote)",
  e0_recalculado="0.335", e0_csv_extraido="0.335", e0_alternativas="Gs 2.71 → 0.316; Gs 2.60 → 0.262",
  saturacion="CO2 + agua desaireada, B > 0.95 (p13); B por probeta no informado", contrapresion_kPa="98 (1.00 kg/cm² en las 3 hojas)",
  consolidacion="Isotrópica a 10, 20, 25 kg/cm²; ΔV 29,390 / 73,737 / 87,571 cm³; duración no informada",
  gamma_d_post_consolidacion_kNm3="no informado; calculado de ΔV: 20.64, 21.32, 21.54",
  drenaje_corte="Drenado", velocidad_pct_min="no informada en hoja; texto ≈98 kPa/min (p13)",
  deformacion_final_pct="19.15 / 19.33 / 19.52",
  criterio_falla_informe="Ángulo de fricción máximo (p19); etapas: 33 % τu + 1 ciclo; 50 % τu + 3 ciclos parciales; 15 ciclos a 50 % τu; carga monótona hasta ≈20 % (p13)",
  hay_pico="P4: no (máx. = último punto 19.15 %); P5: meseta (18.80 %); P6: meseta (18.98 %)",
  hay_curva_tabulada="sí (p106–p227, con ciclos)", Bg_metodo=BG_IDIEM + "; Tabla 7: 24, 36, 39 (recalculado 24.2, 35.5, 38.9)",
  UCS=UCS_HF, Is50=NI, LA_pct=LA_HF, durabilidad=NI, absorcion_pct=NI, paginas="13;41;62–63;104–227", verificado_imagen="sí",
  notas="Asignación de columnas post-ensayo de 20 y 25 kgf/cm² (p63) confirmada por Bg recalculado vs Tabla 7.")

R(fuente=W, set_id="HF-0.15m-Golder", tipo_ensayo="CID carga-descarga Ø6\" (Golder Burnaby B21-132, ASTM D7181-11)", n_probetas="1 (σ'3c 992 kPa)",
  origen_muestra=HF_ORIG, clase_desmonte=HF_CLASE, litologia="Hornfels", litologia_detalle=HF_LIT, litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914", granulometria_campo=HF_CAMPO, densidad_campo=DENS_CAMPO,
  escalamiento_metodo="material <1\" (p4: '24.5 mm (1\")', errata de 25.4); método no declarado; densidad 'estimada con base en Dorador et al. (2018) a partir de granulometría y densidades mín./máx.' (p14)",
  Dmax_lab_mm="25.4", D_probeta_mm="152.0", H_probeta_mm="327.0", D_sobre_Dmax="6.0", granulometria_lab=SMALL_GRAD,
  preparacion="Reconstituida, compactada en capas hasta densidad objetivo (p14); 'Saturation Method: Dry' (p353). ρmáx/ρmín índice del material 1\" (ASTM D4253/D4254): 2232 (seco), 2308 (húmedo) / 1852 kg/m³ (p85)",
  gamma_d_montaje_kNm3="20.58", w_montaje_pct="3.4", Gs_valor="2.75", Gs_origen="Hoja Golder 'Specific Gravity (calculated)' (p350, p353); procedimiento no descrito; coherente con e0 0.31",
  e0_recalculado="0.311", e0_csv_extraido="0.31", e0_alternativas="Gs 2.71 → 0.292",
  saturacion="B = 0.99; Sat 99 % tras consolidación (p353)", contrapresion_kPa="688 (σpwp, p353)",
  consolidacion="Isotrópica, σ'3c 992 kPa (σcell 1667 kPa); ΔV −386 cc; t100 0.0 min",
  gamma_d_post_consolidacion_kNm3="21.62 (ec 0.25)", drenaje_corte="Drenado", velocidad_pct_min="0.0167 (1.00 %/h)",
  deformacion_final_pct="≈17.6 (curva p351)", criterio_falla_informe="'Failure at maximum deviator stress' (p350)",
  hay_pico="La hoja da máx. 4100 kPa a 11.44 %, pero la curva p351 sigue subiendo hasta ≈4600 kPa a ≈17.5 %: inconsistencia",
  hay_curva_tabulada="no (solo gráficos p351–p352)", Bg_metodo="Bg Marsal 15 (Tabla 7 p41); granulometría post solo en gráfico (Fig. 35); no verificable",
  UCS=UCS_HF, Is50=NI, LA_pct=LA_HF, durabilidad=NI, absorcion_pct=NI, paginas="4;6;14;41;85;350–353", verificado_imagen="sí",
  notas="La hoja de hornfels dice 'Sample: MR' y la curva 'CID 6\" MR' (errata de rótulo).")

R(fuente=W, set_id="HF-USC-ciclico-350", tipo_ensayo="Triaxial cíclico drenado (compresión-extensión) + carga monótona drenada post-cíclica (USC, GDS ELDyn)",
  n_probetas="3 (HR-LCTX2 6\" CSR 0.38; HR-CTX1 4\" CSR 0.33; HR-CTX4 4\" CSR 0.20)",
  origen_muestra=HF_ORIG, clase_desmonte=HF_CLASE, litologia="Hornfels", litologia_detalle=HF_LIT, litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914", granulometria_campo=HF_CAMPO, densidad_campo=DENS_CAMPO, escalamiento_metodo="material <1\"; no declarado",
  Dmax_lab_mm="25.4", D_probeta_mm="146.5 / 100 / 100", H_probeta_mm="266.7 / 203.2 / 203.2", D_sobre_Dmax="5.8 / 3.9 / 3.9", granulometria_lab=SMALL_GRAD,
  preparacion="Hojas USC: 'Moist Tamping' con w=5 %. Texto p15: 'preparada en estado seco con densidad 2.2 t/m³, equivalente a IDIEM corregida por tamaño (Dorador et al. 2018)' — contradice la hoja",
  gamma_d_montaje_kNm3="21.46 (las 3)", w_montaje_pct="5.00", Gs_valor="2.71",
  Gs_origen="'Estimated Specific Gravity' USC en la hoja 6\" (p373); las de 4\" no traen Gs",
  e0_recalculado="0.239", e0_csv_extraido="0.239", e0_alternativas="Gs 2.75 → 0.257; e tras consolidación (HR-LCTX2) 0.19 (p373)",
  saturacion="CO2 + agua desaireada; B = 0.95 (LCTX2), 0.97 (CTX1), 0.96 (CTX4)", contrapresion_kPa="≈444–451 (presión de poros inicial, p361/p367/p373)",
  consolidacion="Isotrópica σ'c = 350 kPa", gamma_d_post_consolidacion_kNm3=NI, drenaje_corte="Drenado (cíclico y post-cíclico)",
  velocidad_pct_min="cíclico: 19.4–20.2 kPa/min; post-cíclico 5.00 %/h = 0.083 %/min",
  deformacion_final_pct="20.00 / 1.68 / 7.37 (Max. Axial Strain de las hojas)",
  criterio_falla_informe="'Max. Principal Stress Difference' (hoja USC)",
  hay_pico="LCTX2: no (máx. = valor a 20 %). CTX1 y CTX4: ensayo post-cíclico detenido a 1.68 % y 7.37 %: el 'máximo' es el último punto, no falla",
  hay_curva_tabulada="no (gráficos)", Bg_metodo="Un único Bg = 8 para los 3 cíclicos (Tabla 7 p41); no verificable",
  UCS=UCS_HF, Is50=NI, LA_pct=LA_HF, durabilidad=NI, absorcion_pct=NI, paginas="10;15;28–29;41;361–378", verificado_imagen="sí",
  notas="CSR de las hojas (0.38, 0.33, 0.20) no coincide con Tabla 3 (0.50, 0.40, 0.33) ni con los diámetros. HR-CTX1 y HR-CTX4 tienen masas idénticas (3665.03/3490.50 g): no son mediciones independientes.")

R(fuente=W, set_id="HF-edo-1.0m", tipo_ensayo="Edómetro Ø1.0 m (IDIEM 1.555.677-B.1; encabezado de hoja 1.555.677-A), con permeabilidad de carga constante",
  n_probetas="1", origen_muestra=HF_ORIG, clase_desmonte=HF_CLASE, litologia="Hornfels", litologia_detalle=HF_LIT, litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914", granulometria_campo=HF_CAMPO, densidad_campo=DENS_CAMPO, escalamiento_metodo="no declarado",
  Dmax_lab_mm="177.8", D_probeta_mm="1000 (área 7853.98 cm²)", H_probeta_mm="700 (hoja p300; p4 dice 0.9 m)", D_sobre_Dmax="5.6", granulometria_lab=HF_LAB_GRAD,
  preparacion="Capas de 0.3 m con pisón vibratorio pequeño a 2.1 t/m³ (p32); muestra remoldeada, método B (p300)",
  gamma_d_montaje_kNm3="20.60 (2.100 g/cm³)", w_montaje_pct="1.69", Gs_valor="2.60",
  Gs_origen="'Peso específico estimado, para cálculo de parámetros entregados' (IDIEM p300, nota 3). No ensayado. Incompatible con ρd de núcleos del mismo lote 2.66–2.71 g/cm³",
  e0_recalculado="0.238", e0_csv_extraido="0.238", e0_alternativas="Gs 2.75 → 0.310; Gs 2.71 → 0.290",
  saturacion="Inundada a la carga de asiento (texto p32: 18 kPa); '(*) lectura después de saturar' (p300)", contrapresion_kPa="no aplica",
  consolidacion="Carga vertical hasta 70 kg/cm² (6865 kPa), con descarga-recarga a 60 kg/cm²; escalones de 2 kg/cm²; 8–48 h por escalón (p32)",
  gamma_d_post_consolidacion_kNm3="final 2.205 g/cm³ húmedo (no seco); e final 0.179 (p300)", drenaje_corte="no aplica",
  velocidad_pct_min="no aplica", deformacion_final_pct="5.014 a 70 kg/cm²; 4.743 tras descarga", criterio_falla_informe="no aplica",
  hay_pico="no aplica", hay_curva_tabulada="sí (σv, εv, e; p300–p302; 69 filas comprobadas contra WSP_2022_edometro.csv)",
  Bg_metodo=BG_IDIEM + "; Bg 23 (Tabla 7; recalculado 23.0, p62)", UCS=UCS_HF, Is50=NI, LA_pct=LA_HF, durabilidad=NI, absorcion_pct=NI,
  paginas="32;35;37;41;62;298–302", verificado_imagen="sí", notas="Fecha de hoja '05-11-2022'; IDIEM p298 indica trabajos 05/11/2021–20/01/2022.")

for sid, rho, tit, bgv, pg in [("HF-edo-0.24m-2.1", "2.1", "Probeta 2", "12 (Tabla 7 la rotula 2.3 t/m³; Tabla 4 y texto dicen 2.1)", "33c"),
                               ("HF-edo-0.24m-1.8", "1.8", "Probeta 3", "8", "33d")]:
    R(fuente=W, set_id=sid, tipo_ensayo=f"Edómetro Ø0.24 m (Golder Burnaby) – {tit}", n_probetas="1",
      origen_muestra=HF_ORIG, clase_desmonte=HF_CLASE, litologia="Hornfels", litologia_detalle=HF_LIT, litologia_proporcion="no aplica",
      Dmax_campo_mm="entre 406 y 914", granulometria_campo=HF_CAMPO, densidad_campo=DENS_CAMPO,
      escalamiento_metodo="material <1\"; densidad corregida por tamaño según Dorador et al. (2018) (p32)",
      Dmax_lab_mm="25.4", D_probeta_mm="240", H_probeta_mm="≈200", D_sobre_Dmax="9.4", granulometria_lab=SMALL_GRAD,
      preparacion=("Pistón de compactación estándar, en capas ('de 0.3 m', errata para 0.20 m de altura) (p32). " +
                   ("Objetivo 2.3 t/m³ (densidad especificada corregida) no alcanzable: se compactó a 2.1 t/m³ (≈97 % Proctor) (p31 nota 4, p32)" if rho == "2.1" else "Densidad menor, ≈92 % Proctor estándar estimado (p31–p32)")),
      gamma_d_montaje_kNm3=f"{float(rho)*9.81:.2f}", w_montaje_pct=NI, Gs_valor=NI, Gs_origen="no informado (no hay hoja del ensayo)",
      e0_recalculado="no calculable sin Gs", e0_csv_extraido="(vacío)", e0_alternativas=f"Gs 2.75 → {2.75/float(rho)-1:.3f}",
      saturacion="no informado (el 0.24 m no mide permeabilidad, p37)", contrapresion_kPa="no aplica",
      consolidacion="hasta 4.8 MPa (p32)", gamma_d_post_consolidacion_kNm3=NI, drenaje_corte="no aplica", velocidad_pct_min="no aplica",
      deformacion_final_pct=("≈6 % a 4.8 MPa (texto p32)" if rho == "2.1" else "≈17 % a 4.8 MPa (texto p32)"),
      criterio_falla_informe="no aplica", hay_pico="no aplica", hay_curva_tabulada=f"no: solo gráfico (Fig. {pg}); la curva del CSV de edómetros es digitalizada",
      Bg_metodo="Bg " + bgv + "; granulometría post solo en Fig. 35; no verificable",
      UCS=UCS_HF, Is50=NI, LA_pct=LA_HF, durabilidad=NI, absorcion_pct=NI, paginas="31–35;41", verificado_imagen="sí (texto y figura)", notas="")

R(fuente=W, set_id="MN-USC-ciclico-350", tipo_ensayo="Triaxial cíclico drenado + carga monótona post-cíclica (USC)",
  n_probetas="3 (MN-CTX3 4\" CSR 0.25; MN-LCTX1 6\" CSR 0.19; MN-LCTX2 6\" CSR 0.38)",
  origen_muestra=MN21_ORIG, clase_desmonte=MN21_CLASE, litologia="Mármol", litologia_detalle="mármol negro (MN)", litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914 (100 % pasa 36\"; 4.9 % retenido en 16\")", granulometria_campo=MN21_CAMPO, densidad_campo=DENS_CAMPO,
  escalamiento_metodo="material <1\"; no declarado", Dmax_lab_mm="25.4", D_probeta_mm="100 / 146.5 / 146.5", H_probeta_mm="203.2 / 266.7 / 266.7",
  D_sobre_Dmax="3.9 / 5.8 / 5.8", granulometria_lab=SMALL_GRAD,
  preparacion="Hojas: 'Moist Tamping', w=5 %. Texto p15 dice estado seco a 2.2 t/m³",
  gamma_d_montaje_kNm3="22.07 (las 3)", w_montaje_pct="5.00", Gs_valor="2.71", Gs_origen="'Estimated Specific Gravity' USC (p385, p391); no ensayado; < ρd de núcleos REG 41061 (2.74–2.75)",
  e0_recalculado="0.205", e0_csv_extraido="0.205", e0_alternativas="Gs 2.75 → 0.222; la hoja da e tras consolidación 0.21 y 0.25 (> e0): inconsistente",
  saturacion="B = 0.97 (CTX3), 0.95 (LCTX1), 0.96 (LCTX2)", contrapresion_kPa="≈431–451 (presión de poros inicial)",
  consolidacion="Isotrópica σ'c = 350 kPa", gamma_d_post_consolidacion_kNm3=NI, drenaje_corte="Drenado",
  velocidad_pct_min="cíclico 18.75–20.19 kPa/min; post-cíclico 0.083 (5 %/h)", deformacion_final_pct="4.89 / 20.00 / 20.00",
  criterio_falla_informe="'Max. Principal Stress Difference'", hay_pico="CTX3: detenido a 4.89 % (no falla); LCTX1: máx. 1575.9 y 1392.7 a 20 % (pico); LCTX2: máx. 1550.5 y 1414.8 a 20 % (pico)",
  hay_curva_tabulada="no", Bg_metodo="Bg único = 6 (Tabla 7); no verificable", UCS=UCS_MN21, Is50=NI, LA_pct=LA_MN21, durabilidad=NI, absorcion_pct=NI,
  paginas="10;15;30;41;52–56;379–396", verificado_imagen="sí", notas="MN-LCTX1 y MN-LCTX2 con masas idénticas.")

R(fuente=W, set_id="MN-0.15m-Golder", tipo_ensayo="CID carga-descarga Ø6\" (Golder Burnaby)", n_probetas="1 (σ'3c 976 kPa)",
  origen_muestra=MN21_ORIG, clase_desmonte=MN21_CLASE, litologia="Mármol", litologia_detalle="mármol negro", litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914", granulometria_campo=MN21_CAMPO, densidad_campo=DENS_CAMPO, escalamiento_metodo="material <1\"; no declarado",
  Dmax_lab_mm="25.4", D_probeta_mm="151.9", H_probeta_mm="330.0", D_sobre_Dmax="6.0", granulometria_lab=SMALL_GRAD,
  preparacion="Reconstituida, 'Saturation Method: Dry' (p357); ρmáx/ρmín índice 1\": 2297 (seco) / 2398 (húmedo) / 1905 kg/m³ (p86)",
  gamma_d_montaje_kNm3="20.37", w_montaje_pct="3.5", Gs_valor="2.70", Gs_origen="Hoja Golder 'calculated' (p354, p357); no ensayado; < ρd núcleos REG 41061",
  e0_recalculado="0.300", e0_csv_extraido="0.30", e0_alternativas="Gs 2.75 → 0.324",
  saturacion="B = 0.99 (p357)", contrapresion_kPa="1104 (σpwp)", consolidacion="Isotrópica σ'3c 976 kPa (σcell 2081); ΔV −192.9 cc",
  gamma_d_post_consolidacion_kNm3="21.50 (ec 0.23)", drenaje_corte="Drenado", velocidad_pct_min="0.0167 (1.00 %/h)", deformacion_final_pct="≈22.4 (curva p355)",
  criterio_falla_informe="'Failure at maximum deviator stress': 3823 kPa a 18.51 %, εv −6.51 %", hay_pico="sí: cae después de 18.5 % (p355)",
  hay_curva_tabulada="no", Bg_metodo="Bg 30 (Tabla 7); no verificable", UCS=UCS_MN21, Is50=NI, LA_pct=LA_MN21, durabilidad=NI, absorcion_pct=NI,
  paginas="7;41;86;354–357", verificado_imagen="sí", notas="w post 27.4 % y Sat 319 % en la hoja: erratas. Texto (p26) da φ 45°; con la hoja φsec = 41.3°.")

R(fuente=W, set_id="MN-1.0m-IDIEM-2011", tipo_ensayo="CID monótono (2) y carga-descarga (3), IDIEM 708.397-A — DUPLICADO de Golder 2012",
  n_probetas="5", origen_muestra="Ver condiciones_Golder2012.csv (registro primario): Fase 5, polígono 12022607, cota 4478; NO del Acopio G",
  clase_desmonte="C ('Type C rockfill', Golder 2012 p1)", litologia="Mármol", litologia_detalle="mármol negro", litologia_proporcion="no aplica",
  Dmax_campo_mm="558.8 (Golder 2012 p2)", granulometria_campo="ver Golder 2012", densidad_campo="no informada",
  escalamiento_metodo="truncado (scalping) a 178 mm (Golder 2012 p2); WSP no lo dice", Dmax_lab_mm="177.8", D_probeta_mm="1000", H_probeta_mm="1800", D_sobre_Dmax="5.6",
  granulometria_lab="p66 = Golder 2012 p27", preparacion="ver Golder 2012", gamma_d_montaje_kNm3="20.60", w_montaje_pct="0.09", Gs_valor="2.70",
  Gs_origen="supuesto (Golder 2012 p3, p7)", e0_recalculado="0.286", e0_csv_extraido="0.286", e0_alternativas="—",
  saturacion="CO2 + agua, B > 0.95 (Golder 2012 p7); el CSV extraído decía 'no indicado'", contrapresion_kPa="196 (2.00 kg/cm²)",
  consolidacion="ver Golder 2012", gamma_d_post_consolidacion_kNm3="21.09, 21.19, 21.58, 22.07, 22.46 (Golder 2012 Tabla 3)", drenaje_corte="Drenado",
  velocidad_pct_min="'--' (controlado por carga)", deformacion_final_pct="19.97 / 20.39 / 18.73 / 19.97 / 19.74", criterio_falla_informe="máximo t (ángulo máximo, p26)",
  hay_pico="ver Golder 2012", hay_curva_tabulada="sí (p252–p293, idénticas a Golder 2012 p29–p70)",
  Bg_metodo="Marsal; Tabla 7: 13, 25, 14, 20, 28 (correcto; Golder 2012 Tabla 5 los duplica)", UCS=UCS_MN11, Is50=NI, LA_pct=LA_MN11, durabilidad=NI, absorcion_pct=NI,
  paginas="10;41;66–67;252–293", verificado_imagen="sí", notas="Registro primario: Golder 2012. No contar dos veces.")

R(fuente=W, set_id="MN-edo-1.0m-2021", tipo_ensayo="Edómetro Ø1.0 m (IDIEM 1.555.677-A REV2) con permeabilidad", n_probetas="1",
  origen_muestra=MN21_ORIG, clase_desmonte=MN21_CLASE, litologia="Mármol", litologia_detalle="mármol negro, 'MARMOL (REG 41061)'", litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914", granulometria_campo=MN21_CAMPO, densidad_campo=DENS_CAMPO, escalamiento_metodo="no declarado",
  Dmax_lab_mm="177.8", D_probeta_mm="1000", H_probeta_mm="700", D_sobre_Dmax="5.6",
  granulometria_lab="IDIEM inicial (p61): D10 < 0.074 (10.9 % pasa #200); D30 7.68, D50 23.5, D60 33.6 mm (recalculados); grava 75.8, arena 13.3, finos 10.9 %. Post: 25.7 % finos",
  preparacion="Capas de 0.3 m con pisón vibratorio a 2.1 t/m³ (p32); remoldeada, método B (p324)", gamma_d_montaje_kNm3="20.60", w_montaje_pct="1.50",
  Gs_valor="2.60", Gs_origen="'estimado' por IDIEM (p324 nota 3); incompatible con ρd 2.74–2.75 de núcleos REG 41061 del mismo lote",
  e0_recalculado="0.238", e0_csv_extraido="0.238", e0_alternativas="Gs 2.70 → 0.286; Gs 2.75 → 0.310",
  saturacion="inundada; '(*) lectura después de saturar'", contrapresion_kPa="no aplica",
  consolidacion="hasta 70 kg/cm² (6865 kPa) con descarga-recarga a 60 kg/cm²", gamma_d_post_consolidacion_kNm3="e final 0.163 (p324)",
  drenaje_corte="no aplica", velocidad_pct_min="no aplica", deformacion_final_pct="6.386 a 70 kg/cm²; 6.071 tras descarga",
  criterio_falla_informe="no aplica", hay_pico="no aplica", hay_curva_tabulada="sí (p324; 69 filas comprobadas contra WSP_2022_edometro.csv)",
  Bg_metodo=BG_IDIEM + ". Tabla 7 da 45; con p61 (inicial y post del MISMO ensayo) resulta 37.8. El 45 se reproduce (45.6) comparando con la inicial de 2011: error probable",
  UCS=UCS_MN21, Is50=NI, LA_pct=LA_MN21, durabilidad=NI, absorcion_pct=NI, paginas="32–37;41;61;78–82;322–324", verificado_imagen="sí", notas="")

R(fuente=W, set_id="MN-edo-1.0m-2011", tipo_ensayo="Edómetro IDIEM 708.397-A — DUPLICADO de Golder 2012", n_probetas="1",
  origen_muestra="Golder 2012 (Fase 5, polígono 12022607, cota 4478)", clase_desmonte="C (Golder 2012 p1)", litologia="Mármol", litologia_detalle="mármol negro", litologia_proporcion="no aplica",
  Dmax_campo_mm="558.8", granulometria_campo="ver Golder 2012", densidad_campo="no informada", escalamiento_metodo="truncado a 178 mm (Golder 2012 p2)",
  Dmax_lab_mm="177.8", D_probeta_mm="949.7", H_probeta_mm="900", D_sobre_Dmax="5.3", granulometria_lab="= Golder 2012 p27",
  preparacion="3 capas de 0.3 m, pisón vibratorio, 2.1 t/m³ (Golder 2012 p13)", gamma_d_montaje_kNm3="20.60", w_montaje_pct="0.088",
  Gs_valor="2.70", Gs_origen="'Peso específico integral 2,700' (p295) = supuesto (Golder 2012 p13)", e0_recalculado="0.286 (confección); 0.284 a 0.18 kg/cm² (hoja)",
  e0_csv_extraido="0.284", e0_alternativas="—", saturacion="inundada a 0.18 kg/cm²", contrapresion_kPa="no aplica",
  consolidacion="hasta 60 kg/cm² (5884 kPa)", gamma_d_post_consolidacion_kNm3="ρd 2.309 g/cm³ (22.65 kN/m³) a 60 kg/cm²; e 0.170", drenaje_corte="no aplica",
  velocidad_pct_min="no aplica", deformacion_final_pct="9.03", criterio_falla_informe="no aplica", hay_pico="no aplica",
  hay_curva_tabulada="sí (p295 = Golder 2012 p72; 38 filas comprobadas)", Bg_metodo="Marsal; Tabla 7: 14 (correcto; Golder 2012 da 28.8 = 2×Bg)",
  UCS=UCS_MN11, Is50=NI, LA_pct=LA_MN11, durabilidad=NI, absorcion_pct=NI, paginas="41;67;295",
  verificado_imagen="sí", notas="La Tabla 7 (p41) asigna 6800 kPa como esfuerzo máximo, pero la hoja llega a 60 kg/cm² (5884 kPa).")

R(fuente=W, set_id="MN-edo-0.24m-1.86", tipo_ensayo="Edómetro Ø0.24 m (Golder 'Test 1', ASTM D2435 Método B)", n_probetas="1",
  origen_muestra=MN21_ORIG, clase_desmonte=MN21_CLASE, litologia="Mármol", litologia_detalle="mármol negro", litologia_proporcion="no aplica",
  Dmax_campo_mm="entre 406 y 914", granulometria_campo=MN21_CAMPO, densidad_campo=DENS_CAMPO, escalamiento_metodo="material <1\"; densidad corregida (Dorador 2018)",
  Dmax_lab_mm="25.4", D_probeta_mm="241.0", H_probeta_mm="202.0", D_sobre_Dmax="9.5", granulometria_lab=SMALL_GRAD,
  preparacion="Densidad menor, ≈92 % Proctor estándar estimado (Tabla 4: Probeta 4, 1.8 t/m³; el texto p33 invierte la numeración 3/4)",
  gamma_d_montaje_kNm3="18.21 (ρd 1856 kg/m³)", w_montaje_pct="1.20", Gs_valor="2.70", Gs_origen="'Assumed' (p359)",
  e0_recalculado="0.455", e0_csv_extraido="0.455", e0_alternativas="Gs 2.75 → 0.482", saturacion="final S 100 % (p359)",
  contrapresion_kPa="no aplica", consolidacion="hasta 4799–4800 kPa con descarga-recarga; 'Advanced to 15 kPa due to swelling' (p358)",
  gamma_d_post_consolidacion_kNm3="ρd final 2213 kg/m³; e 0.220", drenaje_corte="no aplica", velocidad_pct_min="no aplica",
  deformacion_final_pct="15.63 a 4799 kPa (15.67 a 4800 tras recarga)", criterio_falla_informe="no aplica", hay_pico="no aplica",
  hay_curva_tabulada="sí (p359; 26 filas comprobadas)", Bg_metodo="Bg 21 (Tabla 7); no verificable", UCS=UCS_MN21, Is50=NI, LA_pct=LA_MN21,
  durabilidad=NI, absorcion_pct=NI, paginas="31–36;41;358–359", verificado_imagen="sí",
  notas="El edómetro de 2.3 t/m³ (Tabla 4 Probeta 3) no tiene hoja; Bg '-' en Tabla 7. Texto (p31) cita 17 % de εv para la probeta suelta; la hoja da 15.63 %.")

pd.DataFrame(rows, columns=COLS).to_csv(os.path.join(OUT, "condiciones_WSP2022.csv"), index=False, encoding="utf-8")

# ===================== Golder 2012 =====================
rows.clear()
G_ORIG = ("'Type C rockfill from Phase 5, Polygon 12022607, elevation 4478', ~16,000 kg, 'angular run-of-the-mine material'; muestreo según Informe 379 (Golder 2011, no incluido) (p1–p2). "
          "IDIEM: fecha de muestreo '---', lugar 'Realizado por Cliente', recepción abril 2011 (p25)")
G_CAMPO = "Solo gráfico (Fig. 1 p2): macro-granulometría 'Run-of-Mine' con Dmax 558.8 mm, Cu 35.0, Cc 2.5; ≈3–4 % pasa 0.074 mm (lectura del gráfico). D10/D50/D80 no tabulados"
G_LAB = ("IDIEM inicial (p27): 100/97.9/93.2/87.9/75.5/67.6/59.2/48.7/38.0/31.2/20.3/14.7/10.8/8.9/7.9/7.3/5.5/4.9 % pasa 178…0.074 mm. "
         "Informe: Cu 34.4, Cc 4.1 (Fig. 1). Recalculado log-lineal: D10 1.39, D30 17.6, D50 39.5, D60 51.9 mm; Cu 37.4, Cc 4.3; grava 85.3, arena 9.8, finos 4.9 %")
R(fuente=G, set_id="G2012-MN-C", tipo_ensayo="CID monótono (P1, P4) y carga-descarga (P2, P3, P5), IDIEM 708.397-A", n_probetas="5 (σ'c 5, 5, 10, 20, 20 kg/cm²)",
  origen_muestra=G_ORIG, clase_desmonte="C ('identified by Antamina as Type C rockfill', p1). Material de presa; origen ROM ('run-of-the-mine') (p2)",
  litologia="Mármol", litologia_detalle="mármol negro ('black marble rockfill'); descripción visual; sin petrografía", litologia_proporcion="no aplica",
  Dmax_campo_mm="558.8 ('oversize particles up to 559 mm', p2)", granulometria_campo=G_CAMPO, densidad_campo="no informada",
  escalamiento_metodo="Truncado: 'scalped at 178 mm to produce samples for testing with comparable grain size curves' (p2)",
  Dmax_lab_mm="177.8", D_probeta_mm="1000", H_probeta_mm="1800", D_sobre_Dmax="5.6", granulometria_lab=G_LAB,
  preparacion="Molde Ø1.0×1.8 m, 2 membranas 5 mm + geotextil; 6 capas de 0.3 m de material SECO con pisón vibratorio pequeño a ρd objetivo 2.1 t/m³; vacío 0.3 kg/cm² (p5). Criterio: densidad objetivo (sin % Proctor ni Dr)",
  gamma_d_montaje_kNm3="20.60 (2.10 g/cm³ en las 5 hojas)", w_montaje_pct="0.09 (hojas)", Gs_valor="2.70",
  Gs_origen="SUPUESTO: 'The specific gravity of this rock type was not determined' (p3); 'estimated assuming Gs=2.7' (p7); IDIEM 'Peso específico integral 2,700' (p72)",
  e0_recalculado="0.286", e0_csv_extraido="0.286", e0_alternativas="sin dato de densidad de roca para acotar Gs",
  saturacion="CO2 24 h + agua destilada desaireada; saturada con B > 95 % (p7); B por probeta no informado",
  contrapresion_kPa="196 (2 kg/cm²; p7 y hojas)", consolidacion="Isotrópica en incrementos hasta σ'c (p7); ΔV 34,670 / 41,604 / 65,378 / 92,453 / 116,227 cm³; duración no informada",
  gamma_d_post_consolidacion_kNm3="21.09, 21.19, 21.58, 22.07, 22.46 (2.15, 2.16, 2.20, 2.25, 2.29 t/m³; e 0.256, 0.250, 0.227, 0.200, 0.179; Tabla 3 p7)",
  drenaje_corte="Drenado", velocidad_pct_min="no informada ('--'); controlado por carga en incrementos (p7)",
  deformacion_final_pct="19.97 / 20.39 / 18.73 / 19.97 / 19.74",
  criterio_falla_informe="'Peak friction angle' estimado por ensayo (p10) = máximo de t=(σ1−σ3)/2",
  hay_pico="No marcado: máximo a 17–20 % con caída posterior ≤ 4.6 % (P1 −4.6 %, P2 −1.7 %, P3 −1.2 %, P4 −0.5 %, P5 −2.9 %)",
  hay_curva_tabulada="sí (p29–p70)",
  Bg_metodo="Marsal (1967) declarado como 'sum of the positive differences' (p17); tamices 7\" a #200 (p27–p28). PERO la Tabla 5 (26.8, 28.6, 40.8, 50.2, 55.4) es Σ|ΔW| = 2×Bg; Bg correcto 13.4, 14.3, 20.4, 25.1, 27.7",
  UCS=UCS_MN11, Is50=NI, LA_pct=LA_MN11, durabilidad=NI, absorcion_pct=NI, paginas="1–3;5;7;10;17;25–29;31–70", verificado_imagen="sí",
  notas="Registro PRIMARIO de estos ensayos; WSP 2022 (p252–p293, p66–p67) los reproduce idénticos. No hay ensayos no drenados (sección B de VERIFICACION.md no aplica).")
R(fuente=G, set_id="G2012-MN-C", tipo_ensayo="Edómetro de gran escala (Probeta 6) con permeabilidad de carga constante", n_probetas="1",
  origen_muestra=G_ORIG, clase_desmonte="C (p1)", litologia="Mármol", litologia_detalle="mármol negro", litologia_proporcion="no aplica",
  Dmax_campo_mm="558.8", granulometria_campo=G_CAMPO, densidad_campo="no informada", escalamiento_metodo="Truncado a 178 mm (p2)",
  Dmax_lab_mm="177.8", D_probeta_mm="949.7", H_probeta_mm="900", D_sobre_Dmax="5.3", granulometria_lab=G_LAB,
  preparacion="Capas de 0.3 m, pisón vibratorio pequeño, 3 capas de material seco a 2.1 t/m³ (p13)", gamma_d_montaje_kNm3="20.60 (2.100)", w_montaje_pct="0.088",
  Gs_valor="2.70", Gs_origen="supuesto (p13)", e0_recalculado="0.286 (confección)", e0_csv_extraido="0.286", e0_alternativas="hoja: 0.284 a 0.18 kg/cm²",
  saturacion="Inundación a carga de asiento 0.18 kg/cm²; colapso 0.8 mm (0.09 %) (p13)", contrapresion_kPa="no aplica",
  consolidacion="Hasta 60 kg/cm² (5884 kPa): 20 incrementos de 2 kg/cm² y 4 de 5 kg/cm²; cada uno hasta sin deformación ≥100 min; los dos últimos ≈15 días; descarga en 12 etapas; ≈2.5 meses (p13)",
  gamma_d_post_consolidacion_kNm3="ρd 2.309 (22.65 kN/m³), e 0.170 a 60 kg/cm² (p72)", drenaje_corte="no aplica", velocidad_pct_min="no aplica",
  deformacion_final_pct="9.03 a 60 kg/cm²", criterio_falla_informe="no aplica", hay_pico="no aplica", hay_curva_tabulada="sí (p72)",
  Bg_metodo="Igual que triaxiales; Tabla 5 da 28.8 (= 2×Bg); correcto 14.4",
  UCS=UCS_MN11, Is50=NI, LA_pct=LA_MN11, durabilidad=NI, absorcion_pct=NI, paginas="13–17;28;72–79", verificado_imagen="sí",
  notas="k = 1.4E-1 a 8.2E-2 cm/s entre 6 y 60 kg/cm² (Tabla 4 p16). Módulo E ≈400 kg/cm² (σ'v<40) a ≈800 kg/cm² (40–60) (p15).")
pd.DataFrame(rows, columns=COLS).to_csv(os.path.join(OUT, "condiciones_Golder2012.csv"), index=False, encoding="utf-8")
print("ok")
