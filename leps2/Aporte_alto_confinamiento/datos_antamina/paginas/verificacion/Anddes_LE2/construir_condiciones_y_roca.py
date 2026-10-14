import json, pathlib
import pandas as pd

here = pathlib.Path(__file__).parent
base = here.parents[2]
ver = base / "verificado"
R = json.load(open(here / "tx_verif.json"))
C = {c["key"]: c for c in json.load(open(here / "tx_criterios.json"))}
NI = "no informado"

S = {
 "M": dict(nombre="Marmol M-1 al M-13", set_id="Ruma 01 (M-1 al M-13)", lit="Mármol", lit_inf="Marmol", prop="no aplica (una litología según la descripción)",
           origen="Perforación (proyecto «Perforaciones Geotécnicas e Hidrogeológicas 2023»); Zona «Patio de servicios / Botadero Este»; profundidad 40,00-90,00 m; código 01 (Ruma 01); compuesta de 13 submuestras M-1 a M-13; recepción 2023-11-23; fecha de muestreo no informada",
           clase="no indicada", clase_base="El texto no la menciona. Inferencia (no textual): desmonte ya depositado en el Botadero Este y recuperado por perforación a 40-90 m; por la definición de DECISIONES.md (transportado en camión) sería ROM, pero el informe no lo dice",
           gd=2.182, w_tx=6.8, w_ls=6.80, mds=2.425, wopt=6.8, gs=3.06, tx_dates="2024-04-16 / 2024-04-19", ls_dates="2024-07-16 / 2024-07-23",
           tx_inf="EPE-23.10.141_17,19,20,13,23,22,25,24,14,15,12,16,21_200_R0_TXCU (13 ítems)", ls_inf="EPE-23.10141_12al25_200_R0_LSDS",
           gran="Muestra recibida: 100 % pasa 3 in; 65/25/10 % grava/arena/finos; D30 2,77, D50 13,4, D60 22,2 mm (interpolados); D10 = 0,075 mm (no 1,54); Cu ≈ 296, Cc ≈ 4,6 (recalculados); NP; GP-GM",
           ls_n="300/600/1200", ret19=44),
 "H": dict(nombre="HORNFELS H-1 al H-12", set_id="Ruma 02 (H-1 al H-12)", lit="Hornfels", lit_inf="HORNFELS", prop="no aplica (una litología según la descripción)",
           origen="Perforación (proyecto «Perforaciones Geotécnicas e Hidrogeológicas 2023»); Zona «Patio de servicios / Botadero Este»; profundidad 40,00-90,00 m; código 02 (Ruma 02); compuesta de 12 submuestras H-1 a H-12; recepción 2023-11-23; fecha de muestreo no informada",
           clase="no indicada", clase_base="El texto no la menciona. Inferencia (no textual): desmonte del Botadero Este recuperado por perforación a 40-90 m; sería ROM por definición, no confirmado",
           gd=2.100, w_tx=6.0, w_ls=7.70, mds=2.333, wopt=7.7, gs=2.94, tx_dates="2024-01-25 / 2024-01-29", ls_dates="2024-07-24 / 2024-08-01",
           tx_inf="EPE-23.10.141_7,9,2,4,11,8,1,3,5,6,18,10_200_R0_TXCU (12 ítems)", ls_inf="EPE-23.10141_1al18_200_R0_LSDS",
           gran="Muestra recibida: 100 % pasa 3 in; 68/21/11 %; D30 3,56, D50 12,9, D60 19,6 mm (interpolados); D10 < 0,075 mm (no 1,54); LL 16, NP; GP-GM",
           ls_n="300/600/1200", ret19=41),
 "I": dict(nombre="Intrusivo I-1 al I-12", set_id="Ruma 03 / Fase 10 A (I-1 al I-12)", lit="Intrusivo", lit_inf="Intrusivo", prop="no aplica (una litología según la descripción)",
           origen="Perforación (proyecto «Perforaciones Geotécnicas e Hidrogeológicas 2023»); Zona «Botadero Este»; profundidad 20,00-60,00 m; código 03 (Ruma 03) / Fase 10 A; submuestras I-1 a I-11 (el TX dice I-1 al I-12, pero su N° de informe lista 11 ítems); recepción 2023-11-23; fecha de muestreo no informada",
           clase="no indicada", clase_base="El texto no la menciona. Inferencia (no textual): desmonte del Botadero Este recuperado por perforación a 20-60 m; sería ROM por definición, no confirmado. «Fase 10 A» no se explica en el informe",
           gd=1.921, w_tx=8.0, w_ls=9.80, mds=2.134, wopt=9.8, gs=2.75, tx_dates="2024-04-24 / 2024-04-29", ls_dates="2024-07-08 / 2024-07-15",
           tx_inf="EPE-23.10.141_28,27,26,43,34,35,41,39,40,38,36_200_R0_TXCU (11 ítems)", ls_inf="EPE-23.10141_26al43_200_R0_LSDS",
           gran="Muestra recibida: 100 % pasa 3 in; 63/29/8 %; D10 0,126, D30 2,98, D50 9,9, D60 15,3 mm; Cu 121, Cc 4,7; LL 17, NP; GP-GM",
           ls_n="300/600/1200", ret19=35),
 "P1": dict(nombre="Pila 01 Mármol + Hornfels", set_id="Pila 01 (MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B)", lit="Mezcla", lit_inf="Mármol + Hornfels", prop="Mármol + Hornfels; proporción no indicada",
           origen="Zona «Pilas Experimentales Medio Ambiente»; profundidad «--»; código Pila 01; N° de muestra MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B; recepción 2024-09-03; fecha y punto de muestreo no informados",
           clase="no indicada", clase_base="El texto no dice ROM, Chancado ni Enrocado. El N° de muestra contiene «Material B»: podría ser la clase de material de Antamina (A/B/C), que no es ROM/Chancado/Enrocado; inferencia no confirmada",
           gd=2.094, w_tx=7.4, w_ls=7.40, mds=2.327, wopt=7.4, gs=2.90, tx_dates="2024-10-02 / 2024-10-10", ls_dates="2024-10-15 / 2024-10-25",
           tx_inf="EPE-23.10.141_1,2,3,4_110_R0_TXCU", ls_inf="EPE-23.10.141_1,2,3,4_110_R0_LSDS",
           gran="Muestra recibida: 100 % pasa 3 in; 0 % bolonería; 59/30/11 %; D30 1,50, D50 8,0, D60 12,6 mm; D10 < 0,075 mm (no 1,54); NP; GP-GM informado, no verificable (podría ser GW-GM)",
           ls_n="300/600/1000", ret19=30),
 "P2": dict(nombre="Pila 02 Intrusivo", set_id="Pila 02 (MP2-A-M-1 a MP2-A-M-5, MP2-H-Material A)", lit="Intrusivo", lit_inf="Intrusivo", prop="no aplica (una litología según la descripción)",
           origen="Zona «Pilas Experimentales Medio Ambiente»; profundidad «--»; código Pila 02; N° de muestra MP2-A-M-1 a MP2-A-M-5 y MP2-H-Material A; recepción 2024-09-03; fecha y punto de muestreo no informados",
           clase="no indicada", clase_base="El texto no dice ROM, Chancado ni Enrocado. El N° de muestra contiene «Material A» (posible clase de material de Antamina, no ROM/Chancado/Enrocado); inferencia no confirmada",
           gd=1.831, w_tx=11.1, w_ls=11.10, mds=2.034, wopt=11.1, gs=2.74, tx_dates="2024-10-03 / 2024-10-10", ls_dates="2024-10-05 / 2024-10-15",
           tx_inf="EPE-23.10.141_5,6,7,8,9,10_110_R0_TXCU", ls_inf="EPE-23.10.141_5,6,7,8,9,10_110_R0_SUCS (sic, en el LSDS)",
           gran="Muestra recibida: 100 % pasa 3 in; 1 % bolonería (incoherente con 100 % < 3 in); 57/34/9 %; D10 0,084, D30 1,50, D50 7,1, D60 11,5 mm; Cu 137, Cc 2,3; NP; GW-GM",
           ls_n="300/600/1200", ret19=27),
}

SUB = {"M": "M-1 a M-13 (13; el N° de informe TX lista 13 ítems)", "H": "H-1 a H-12 (12; el N° de informe TX lista 12 ítems)", "I": "I-1 a I-11 (11): así lo dicen SUCS, Proctor, CA y LSDS, y el N° de informe TX lista 11 ítems; el encabezado TX y los nombres de archivo dicen I-1 al I-12 (error probable)", "P1": "MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B (4)", "P2": "MP2-A-M-1 a MP2-A-M-5, MP2-H-Material A (6)"}
rows = []
for k, s in S.items():
    gdk = round(s["gd"] * 9.81, 2)
    e0 = round(s["gs"] / s["gd"] - 1, 3)
    common = dict(fuente_set=s["nombre"], set_id=s["set_id"], submuestras_verificadas=SUB[k], origen_muestra=s["origen"], clase_desmonte=s["clase"], clase_desmonte_base=s["clase_base"],
                  litologia_informe=s["lit_inf"], litologia=s["lit"], litologia_detalle="no informado (sin subtipo ni alteración)", litologia_proporcion=s["prop"],
                  litologia_metodo="descripción del solicitante («Las muestras han sido proporcionadas e identificadas por el solicitante»); sin petrografía ni conteo",
                  Dmax_campo_mm="no informado (la muestra recibida pasa 100 % por 3 in = 75 mm, tamaño limitado por la perforación o el muestreo)" if k in ("M", "H", "I") else "no informado (la muestra recibida pasa 100 % por 3 in = 75 mm)",
                  granulometria_campo="no informada; solo la de la muestra recibida: " + s["gran"],
                  densidad_campo=NI, Gs_valor=s["gs"],
                  Gs_origen=f"leído del rótulo «Curva 100% saturación (Gs={s['gs']})» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ {s['gs']-0.01:.2f}",
                  e0_recalculado=e0, Bg_metodo="no informado (no hay granulometría después del ensayo)", UCS="no informado en estos informes", Is50="no informado en estos informes",
                  LA_pct=NI, durabilidad=NI, absorcion_pct="no informado (el Proctor da «w» de la fracción sobre tamaño, que no es absorción)")
    # TX row
    keys = [f"{k}_{x} kPa" for x in ("500", "1000", "2000")]
    Bs = "/".join(f"{R[x]['B'][0]:.2f}" for x in keys)
    rcs = "; ".join(f"{x.split('_')[1]}: {R[x]['rho'][1]:.3f} g/cm³ = {R[x]['rho'][1]*9.81:.2f} kN/m³" for x in keys)
    dvs = "/".join(f"{C[x]['dV_cons_pct']}" for x in keys)
    picos = []
    for x in keys:
        c = C[x]
        picos.append(f"{x.split('_')[1]}: máx. q {c['qmax']['q']} a {c['qmax']['eps']} %")
    tx = dict(common, tipo_ensayo="Triaxial CU (CIU) 6 in, ASTM D4767-11 (2020)", fechas_ensayo=s["tx_dates"], informe=s["tx_inf"],
              escalamiento_metodo="no informado (el TX no declara tamizado, truncamiento ni escalamiento)",
              Dmax_lab_mm="no informado", D_probeta_mm=152.0, H_probeta_mm=310.0, D_sobre_Dmax="no calculable (Dmax de probeta no informado); si fuera la fracción < 19 mm del Proctor, D/Dmax = 8 (supuesto, no documentado)",
              granulometria_lab="no informada para la probeta",
              preparacion=f"«Reconstituido al 90% de la máxima densidad seca (MDS) de {s['mds']:.3f} g/cm³ y óptimo contenido de agua de {s['w_tx']:.1f} %» (p.1-7). Método (pisón, vibración), número de capas y fracción usada: no informados. Formato marca «Grado de compactación: Medio». Densa respecto de la colocación: no se puede juzgar",
              gamma_d_montaje_kNm3=gdk, rho_d_montaje_gcm3=s["gd"], w_montaje_pct=s["w_tx"],
              w_montaje_vs_proctor=("igual al óptimo Proctor" if abs(s["w_tx"] - s["wopt"]) < 0.05 else f"DISTINTO: TX {s['w_tx']} % rotulado «óptimo»; Proctor da {s['wopt']} % y el LSDS usa {s['w_ls']:.1f} %"),
              saturacion=f"método no informado; B = {Bs} (500/1000/2000 kPa)", contrapresion_kPa=187,
              consolidacion=f"isotrópica; σ′3c = 500, 1000 y 2000 kPa (celda 687/1187/2187 − 187); duración no informada; ΔV de consolidación recalculado {dvs} %",
              gamma_d_post_consolidacion_kNm3=rcs, drenaje_corte="no drenado con medición de u", velocidad_pct_min="0,025 cm/min sobre H = 31,0 cm = 0,081 %/min",
              deformacion_final_pct=15.0, criterio_falla_informe="15 % de deformación axial para la envolvente efectiva y Su (p.1); envolvente total a 2 % (M, H, I) o 15 % (P1, P2) en p.7, pedida por el cliente",
              hay_pico="; ".join(picos), hay_curva_tabulada="sí: 28 puntos de 0 a 15 % por probeta (q, u, p, q, p′, q′, q′/p′, σ′1/σ′3), p.3-5",
              pagina="TX p.1, p.3-5, p.7")
    ls = dict(common, tipo_ensayo="Corte directo gran escala CD, ASTM D3080/D3080M-23", fechas_ensayo=s["ls_dates"], informe=s["ls_inf"],
              escalamiento_metodo="no informado; «TM: 1 in» en el esquema de la caja (p.2). Ni el truncamiento ni la granulometría de la probeta se informan",
              Dmax_lab_mm=25.4, D_probeta_mm="caja cuadrada 305 × 305", H_probeta_mm=178.0, D_sobre_Dmax="lado/TM = 305/25,4 = 12,0; altura/TM = 7,0",
              granulometria_lab="no informada",
              preparacion=f"ρd inicial {s['gd']:.3f} g/cm³ (= 90 % de la MDS {s['mds']:.3f}, que corresponde a la fracción < 19 mm) y w {s['w_ls']:.2f} % (p.2). Método de compactación y capas: no informados",
              gamma_d_montaje_kNm3=gdk, rho_d_montaje_gcm3=s["gd"], w_montaje_pct=s["w_ls"],
              w_montaje_vs_proctor=("igual al óptimo Proctor" if abs(s["w_ls"] - s["wopt"]) < 0.05 else "distinto"),
              saturacion="«Los especímenes fueron saturados durante el ensayo, salvo excepciones» (p.2); sin verificación. Sr final recalculado: ver ensayos_corte_directo_verificado.csv",
              contrapresion_kPa="no aplica", consolidacion=f"16,0 h al esfuerzo normal σn = {s['ls_n']} kPa", gamma_d_post_consolidacion_kNm3="no informado (solo ρd final después del corte, p.2)",
              drenaje_corte="drenado (CD)", velocidad_pct_min="0,5 mm/min (desplazamiento horizontal); separación de cajas 1,0 mm; fin a unos 65 mm",
              deformacion_final_pct="unos 65 mm de desplazamiento horizontal", criterio_falla_informe="τ pico y τ a 6,6 cm de desplazamiento; envolvente lineal por mínimos cuadrados",
              hay_pico="pico poco marcado: τ pico y τ a 6,6 cm difieren menos de 5 % salvo I a 1200 kPa (945,1 → 885,6 kPa; caída visible después de unos 4,3 cm en el gráfico p.2) y P1/P2 a 300 kPa (356,3 → 340,0; 353,9 → 349,1)",
              hay_curva_tabulada="no (solo gráficos τ-δh y δv-δh)", pagina="LSDS p.1-2")
    rows += [tx, ls]
cond = pd.DataFrame(rows)
cond.insert(0, "fuente", "Anddes Geolab 2024 (solicitud EPE-23.10.141)")
cond.to_csv(ver / "condiciones_Anddes2024.csv", index=False, encoding="utf-8")

# --------- indices de roca LE2 ---------
st = json.load(open(here / "le2_stats.json"))
resumen = {  # valores de la hoja Resumen (fila, col) leídos con openpyxl data_only
    ("UCS", "END"): (39.339, 28.1, 21.969), ("UCS", "EXO"): (72.681, 66.677, 49.571), ("UCS", "HRN"): (96.776, 75.2, 58.16),
    ("UCS", "INT"): (57.741, 50.6, 39.53), ("UCS", "LMH"): (68.0, 56.272, 44.321), ("UCS", "XDP"): (98.689, 97.988, 2021),
    ("PLTA", "END"): (2.770, 1.972, 1.451), ("PLTA", "EXO"): (5.075, 4.710, 3.412), ("PLTA", "HRN"): (5.437, 4.872, 4.280),
    ("PLTA", "INT"): (3.981, 3.477, 2.145), ("PLTA", "LMH"): (3.681, 3.490, 2.783), ("PLTA", "XDP"): (7.261, 6.849, 4.879),
    ("PLTD", "END"): (3.858, 2.648, 1.740), ("PLTD", "EXO"): (6.459, 5.922, 4.576), ("PLTD", "HRN"): (5.618, 4.963, 4.280),
    ("PLTD", "INT"): (5.661, 4.868, 3.667), ("PLTD", "LMH"): (3.813, 3.547, 2.855), ("PLTD", "XDP"): (7.822, 7.180, 5.685),
    ("Brazilian", "END"): (4.247, 3.385, 2.400), ("Brazilian", "EXO"): (7.701, 7.150, 6.042), ("Brazilian", "HRN"): (9.785, 9.710, 8.701),
    ("Brazilian", "INT"): (7.412, 7.250, 5.928), ("Brazilian", "LMH"): (6.647, 6.388, 5.510), ("Brazilian", "XDP"): (8.941, 8.515, 7.106),
}
lit = {"END": ("Skarn", "endoskarn (sigla; no definida en el xlsx ni en texto de las pptx)"),
       "EXO": ("Skarn", "exoskarn (sigla; no definida en texto)"),
       "HRN": ("Hornfels", "hornfels (sigla; no definida en texto)"),
       "INT": ("Intrusivo", "intrusivo sin subtipo (sigla; no definida en texto)"),
       "LMH": ("Caliza", "«LMH Calizas Desmonte (limestone Hornfels)» (WSC lámina 12, texto); inclusión de mármol no confirmada"),
       "XDP": ("Skarn", "«XDP Exoskarn mayor desmonte» (WSC lámina 12, texto); la lámina lista «Exo Diopsídico» entre las litologías"),
       "N/A": ("sin RMU", "registros con RMU «N/A» (UCS filas 2388-2393), fuera de las fórmulas del Resumen"),
       "N/D": ("sin RMU", "registros con RMU «N/D», fuera de las fórmulas del Resumen")}
par = {"UCS": ("UCS", "MPa", "hoja UCS col. E"), "PLTA": ("Is50 axial", "MPa", "hoja PLTA col. C"), "PLTD": ("Is50 diametral", "MPa", "hoja PLTD col. C"),
       "Brazilian": ("tracción brasileña", "MPa", "hoja Brazilian col. E")}
out = []
for sh, (pn, un, src) in par.items():
    for rmu, v in st[sh]["stats"].items():
        rs = resumen.get((sh, rmu))
        note = ""
        if (sh, rmu) == ("UCS", "XDP"):
            note = "ERROR del Resumen: P35 = 2021 porque la fórmula UCS!J2394 usa F2394:F2471 (columna Año). Correcto: 70,84 MPa. El error se repite en PGR lámina 4 y WSC lámina 12."
        if (sh, rmu) == ("PLTA", "HRN"):
            note = "El promedio del Resumen usa C950:C1478 y los percentiles C950:C1479; con todas las filas, la media es 5,435 (Resumen 5,437)."
        if sh == "PLTD" and st[sh]["nonnum"]:
            nn = [x for x in st[sh]["nonnum"] if x[1] == rmu]
            if nn:
                note += f" {len(nn)} filas sin valor numérico excluidas."
        if sh == "PLTA" and rmu == "INT":
            note += " 1 fila con «N/D» excluida (fila 1763)."
        out.append(dict(rmu=(rmu + " (sin RMU)") if rmu in ("N/A", "N/D") else rmu, litologia=lit[rmu][0], litologia_detalle=lit[rmu][1], parametro=pn, unidad=un, n=v["n"],
                        media=round(v["media"], 3), P50=round(v["P50"], 3), P35=round(v["P35"], 3), P16=round(v["P16"], 3), P84=round(v["P84"], 3),
                        desv_est=round(v["sd"], 3) if v["sd"] is not None else "", minimo=round(v["min"], 3), maximo=round(v["max"], 3),
                        resumen_media=rs[0] if rs else "no aplica", resumen_P50=rs[1] if rs else "no aplica", resumen_P35=rs[2] if rs else "no aplica",
                        coincide_resumen=("no (P35)" if (sh, rmu) == ("UCS", "XDP") else ("sí" if rs else "no aplica")),
                        base="ensayos de laboratorio en testigos (roca intacta); percentiles = PERCENTILE.INC", fuente="Resultados Parametros  Geotecnicos LE2 (03092025).xlsx; " + src,
                        notas=note.strip()))
# densidad: modelo de bloques (MR24_BD), RT identificado por conteo con WSC lámina 12
bd = [("16", "Marmol", "Mármol", 110698, 2.700, 2.712, 2.687, 2.731, 2.559, 3.458),
      ("19", "Marmol Diopsida", "Mármol", 8020, 2.851, 2.848, 2.790, 2.902, 2.620, 3.195),
      ("13", "Horfels", "Hornfels", 48510, 2.700, 2.706, 2.685, 2.726, 2.557, 3.210),
      ("14", "Horfel Diopsida", "Hornfels", 9983, 2.870, 2.860, 2.787, 2.920, 2.591, 3.113),
      ("1", "Intrusivo", "Intrusivo", 46813, 2.452, 2.461, 2.403, 2.517, 2.166, 3.085),
      ("2", "Intrus-Estruct-Tab", "Intrusivo", 3137, 2.667, 2.690, 2.631, 2.720, 2.542, 3.440),
      ("53", "Brechas-Intrus", "Intrusivo", 403, 2.619, 2.657, 2.505, 2.824, 2.368, 3.351),
      ("10", "Caliza", "Caliza", 24434, 2.710, 2.709, 2.699, 2.717, 2.633, 2.752),
      ("11", "Margas-Limonitas", "Otra", 58104, 2.710, 2.711, 2.703, 2.723, 2.590, 2.770)]
for rt, nm, ln, n, p50, mean, p16, p84, mn, mx in bd:
    out.append(dict(rmu=f"MR24_RT {rt}", litologia=ln, litologia_detalle=nm, parametro="densidad de bloque MR24_BD", unidad="t/m³ (unidad no indicada; presumible)",
                    n=n, media=mean, P50=p50, P35="", P16=p16, P84=p84, desv_est="", minimo=mn, maximo=mx,
                    resumen_media="no aplica", resumen_P50="no aplica", resumen_P35="no aplica", coincide_resumen="no aplica",
                    base="MODELO de bloques (valor estimado, no ensayo); la litología se asignó al código RT porque el n de bloques y la media/desv. de MR24_UCS coinciden exactamente con la tabla de WSC lámina 12",
                    fuente="SIMULACIONES_MR2024_V3.csv (columnas MR24_RT, MR24_BD)",
                    notas="No hay densidad, Gs ni absorción por RMU en el xlsx. WSC lámina 8 solo da histogramas globales (pico en 2,70-2,72)."))
pd.DataFrame(out).to_csv(ver / "indices_roca_LE2.csv", index=False, encoding="utf-8")
print(len(cond), len(out))

