"""Extracción de la caracterización de desmonte LE2 (Antamina) a CSV.
Uso: python -I extraer.py <carpeta 250903 Waste Charact> <carpeta extraido>
"""
import sys, os, openpyxl, pandas as pd, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
W, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)
FGEO = "Resultados Parametros  Geotecnicos LE2 (03092025).xlsx"
FFRAG = "Fragmentación Desmonte 2025.xlsx"
FWSC = "Waste Sample Characterization Rev C.pptx"
FPGR = "Parametros Geotecnicos Vs RMU LE2 03092025.pptx"

# ---------- correspondencias de litología ----------
RMU = {
    'END': ('Skarn', 'endoskarn (sigla END; expansión según la lista de litologías de WSC lámina 12, no definida en el xlsx)', 'skarn (metasomatismo de contacto)'),
    'EXO': ('Skarn', 'exoskarn (sigla EXO; expansión según WSC lámina 12)', 'skarn (metasomatismo de contacto)'),
    'HRN': ('Hornfels', 'hornfels (sigla HRN)', 'metamorfismo de contacto'),
    'INT': ('Intrusivo', 'intrusivo sin subtipo (sigla INT; el archivo no distingue monzonita / pórfido)', 'no indicada'),
    'LMH': ('Caliza', 'calizas de desmonte con hornfels ("LMH Calizas Desmonte (limestone Hornfels)", WSC lámina 12); probablemente agrupa también mármol, no confirmado', 'no indicada'),
    'XDP': ('Skarn', 'exoskarn "mayor desmonte" (WSC lámina 12); la sigla sugiere exoskarn diopsídico, no confirmado', 'skarn diopsídico (interpretación de la sigla)'),
    'N/D': ('', 'RMU no definida en el archivo (N/D)', ''),
}
RMU_CORR = {k: v[1] for k, v in RMU.items()}
BLQ = {  # litología del modelo de bloques MR24_RT
    'Intrusivo': ('Intrusivo', 'intrusivo sin subtipo', 'no indicada'),
    'Intrus-Estruct-Tab': ('Intrusivo', 'intrusivo en estructuras tabulares (diques/sills: interpretación del nombre)', 'no indicada'),
    'Marmol': ('Mármol', 'mármol sin subtipo (no distingue negro/blanco)', 'metamorfismo de contacto'),
    'Brechas-Intrus': ('Intrusivo', 'brecha intrusiva', 'no indicada'),
    'Marmol Diopsida': ('Mármol', 'mármol diopsídico', 'diopsidización (metamorfismo/metasomatismo)'),
    'Horfels': ('Hornfels', 'hornfels', 'metamorfismo de contacto'),
    'Horfel Diopsida': ('Hornfels', 'hornfels diopsídico', 'diopsidización (metamorfismo/metasomatismo)'),
    'Caliza': ('Caliza', 'caliza', 'no indicada'),
    'Margas-Limonitas': ('Otra', 'margas-"limonitas" (así escrito; probablemente margas-limolitas; en lámina 7 "Mangas-Limonitas")', 'no indicada'),
}

COLS = ['fuente', 'hoja_lamina', 'fila_o_ubicacion', 'nivel', 'id_muestra_o_unidad', 'rmu', 'litologia_informe', 'litologia', 'litologia_detalle', 'alteracion',
        'correspondencia_rmu_litologias', 'clase_desmonte', 'clase_material_informe', 'estadistico', 'n', 'este_m', 'norte_m', 'cota_m', 'anio',
        'UCS_MPa', 'Is50_axial_MPa', 'Is50_diametral_MPa', 'traccion_brasilena_MPa', 'phi_corte_directo_deg', 'c_corte_directo_MPa',
        'RMR', 'RQD_pct', 'FF_por_m', 'densidad_t_m3', 'abrasion_pct', 'CBWI_kWh_t', 'bond_BWI_kWh_t', 'crushability_pct', 'macon_abrasividad_g_t', 'bond_Ai', 'DWT_Axb',
        'toneladas_modelo', 'LA_pct', 'durabilidad', 'absorcion_pct', 'Gs', 'granulometria', 'notas']
rows = []


def base(**k):
    r = {c: '' for c in COLS}
    r.update(k)
    return r


def lit_rmu(code):
    l = RMU.get(code, ('', '', ''))
    return dict(rmu=code, litologia_informe=code, litologia=l[0], litologia_detalle=l[1], alteracion=l[2],
                correspondencia_rmu_litologias=RMU_CORR.get(code, ''))


fgeo = os.path.join(W, FGEO)
CD = 'no indicada (núcleos de perforación del tajo LE2, roca in situ)'


def sheet(name, ucol, vcols, ycol, xyz, note):
    df = pd.read_excel(fgeo, sheet_name=name)
    df['_fila'] = df.index + 2
    df = df[df[ucol].notna()]
    for _, s in df.iterrows():
        r = base(fuente=FGEO, hoja_lamina=name, fila_o_ubicacion=f"fila {s['_fila']}", nivel='muestra (registro de ensayo)',
                 id_muestra_o_unidad=f"{name}-{s['_fila']}", clase_desmonte=CD, estadistico='valor individual', n=1,
                 este_m=s[xyz[0]], norte_m=s[xyz[1]], cota_m=s[xyz[2]], anio=s[ycol] if ycol else '', notas=note,
                 **lit_rmu(str(s[ucol]).strip()))
        for dst, src in vcols.items():
            v = pd.to_numeric(s[src], errors='coerce')
            r[dst] = '' if pd.isna(v) else v
            if pd.isna(v) and str(s[src]).strip() not in ('', 'nan'):
                r['notas'] += f" | valor original '{s[src]}'"
        rows.append(r)


sheet('UCS', 'RMU', {'UCS_MPa': 'Resist. Comp Simple (MPa)'}, 'Año',
      ['Este ( Coordenada Muestra )', 'Norte ( Coordenada Muestra )', 'Cota (Muestra)'], 'UCS de laboratorio en núcleo; coordenadas UTM')
sheet('PLTA', 'RMU', {'Is50_axial_MPa': 'Is(50)'}, 'Año',
      ['Coordenadas de la muestra Este   (m)', 'Coordenadas de la muestra Norte (m)', 'Coordenadas de la muestra Cota (m)'], 'carga puntual axial Is(50)')
sheet('PLTD', 'RMU', {'Is50_diametral_MPa': 'Is(50)'}, 'Año',
      ['Coordenadas de la muestra Este   (m)', 'Coordenadas de la muestra Norte (m)', 'Coordenadas de la muestra Cota (m)'], 'carga puntual diametral Is(50)')
sheet('Brazilian', 'Unidad Geotécnica', {'traccion_brasilena_MPa': 'Resistencia a la  tracción  (MPa)'}, 'Año',
      ['Este (Coordenada muestra)', 'Norte (Coordenada muestra )', 'Cota (Muestra)'], 'tracción indirecta (brasileño)')
sheet('Corte', 'Unidad Geotécnica', {'phi_corte_directo_deg': 'Angulo de Fricción (°)', 'c_corte_directo_MPa': 'Cohesión en (Mpa)'}, 'Año',
      ['Coordenadas de la muestra Este   (m)', 'Coordenadas de la muestra Norte (m)', 'Coordenadas de la muestra Cota (m)'],
      'corte directo: el archivo no indica si es sobre discontinuidad, roca intacta o pico/residual; φ y c por registro (muchos registros repetidos con igual φ, c y coordenadas casi iguales)')
sheet('RMR_RQD_FF', 'UG', {'RMR': 'RMR', 'RQD_pct': 'RQD Corregido', 'FF_por_m': 'Nro_Total_Estructuras/ Por metro (FF)'}, None,
      ['mid_x', 'mid_y', 'mid_z'], 'tramo de logueo geotécnico (punto medio); sin año')
n_muestras = len(rows)

# ---------- unidades: WSC lámina 2 ----------
L2 = [  # Material, UCS, BondCWI, Crushab, BondBWI, Macon, BondAi, DWT A*b
    ('M1', 44, 4.1, 46.14, 11.1, 942.6, 0.2306, 111.7), ('M2A', 156, 13.6, 36.80, 11.9, 1298.4, 0.5657, 44.6),
    ('M4B', 150, 13.9, 39.22, 13.1, 1047.6, 0.4470, 37.4), ('Waste-C/Std', 54, 12.6, 36.50, None, 39.4, 0.0261, 43.9),
    ('Waste-Fine', 83, 17.1, 28.72, None, 50.0, 0.0202, 35.6), ('Waste-Hard', 155, 16.0, 25.02, None, 778.0, 0.4810, 38.8)]
for m, u, cwi, cr, bwi, mac, ai, dwt in L2:
    ore = m.startswith('M')
    rows.append(base(fuente=FWSC, hoja_lamina='lámina 2 (tabla "Caracterización de la Roca – Análisis de Resistencia", imagen WSC_s02_5.png)',
                     fila_o_ubicacion=m, nivel='unidad (tipo de material)', id_muestra_o_unidad=m, litologia_informe=m, litologia='',
                     litologia_detalle=('tipo de mineral (no desmonte)' if ore else 'desmonte; litología no indicada'),
                     clase_desmonte=('no aplica (mineral)' if ore else 'no indicada; ensayos de conminución orientados a chancado'),
                     clase_material_informe=m, estadistico='valor informado (sin n)', UCS_MPa=u, CBWI_kWh_t=cwi, crushability_pct=cr,
                     bond_BWI_kWh_t=('' if bwi is None else bwi), macon_abrasividad_g_t=mac, bond_Ai=ai, DWT_Axb=dwt,
                     notas='Programa Mine-to-mill 2007/2009 (Fase 3) según nota de la lámina; "Bond CWI" = Bond crushing work index; DWT A*b rango 60–180 según nota'))

# ---------- unidades: WSC lámina 12, UCS del modelo de bloques por litología ----------
L12 = {'Brechas-Intrus': (403, 57.37, 7.06, 40.11, 53.27, 56.68, 60.86, 96.93), 'Caliza': (24434, 81.32, 5.50, 51.35, 77.37, 82.54, 82.97, 123.98),
       'Horfel Diopsida': (9983, 116.96, 18.00, 57.13, 105.91, 114.95, 130.48, 225.95), 'Horfels': (48510, 105.85, 16.57, 28.85, 97.20, 104.93, 115.31, 200.24),
       'Intrus-Estruct-Tab': (3137, 104.47, 19.33, 46.51, 92.40, 103.30, 113.28, 196.41), 'Intrusivo': (46813, 63.27, 14.16, 16.81, 54.08, 63.18, 71.39, 153.34),
       'Margas-Limonitas': (58104, 70.03, 7.89, 28.10, 68.32, 69.24, 72.17, 121.52), 'Marmol': (110698, 74.03, 13.87, 26.58, 65.84, 74.14, 80.91, 174.86),
       'Marmol Diopsida': (8020, 94.91, 11.10, 39.93, 89.48, 94.66, 102.08, 153.71)}
for lit, (n, mean, sd, mn, p25, p50, p75, mx) in L12.items():
    l = BLQ[lit]
    for est, v in [('media', mean), ('desv. estándar', sd), ('mínimo', mn), ('P25', p25), ('P50', p50), ('P75', p75), ('máximo', mx)]:
        rows.append(base(fuente=FWSC, hoja_lamina='lámina 12 (tabla MR24_UCS por Litología, imagen WSC_s12_4.png)', fila_o_ubicacion=lit,
                         nivel='unidad (bloques del modelo geológico MR24)', id_muestra_o_unidad=f'MR24-{lit}', litologia_informe=lit,
                         litologia=l[0], litologia_detalle=l[1], alteracion=l[2], clase_desmonte='no indicada (bloques de desmonte en el tajo)',
                         estadistico=est, n=n, UCS_MPa=v, notas='UCS asignado en el modelo de bloques (MR24_UCS), no ensayo directo; n = número de bloques'))

# lámina 5: medianas leídas de boxplots (aprox.)
L5 = {'Intrusivo': (63, 11.1), 'Intrus-Estruct-Tab': (103, 15.1), 'Marmol': (74, 12.4), 'Brechas-Intrus': (57, 10.3), 'Marmol Diopsida': (95, 14.4),
      'Horfels': (105, 15.2), 'Horfel Diopsida': (115, 16.0), 'Caliza': (82, 13.1), 'Margas-Limonitas': (69, 12.0)}
for lit, (u, cb) in L5.items():
    l = BLQ[lit]
    rows.append(base(fuente=FWSC, hoja_lamina='lámina 5 (boxplots UCS y CBWI por litología, WSC_s05_4.png y WSC_s05_6.png)', fila_o_ubicacion=lit,
                     nivel='unidad (bloques del modelo geológico MR24)', id_muestra_o_unidad=f'MR24-{lit}', litologia_informe=lit,
                     litologia=l[0], litologia_detalle=l[1], alteracion=l[2], clase_desmonte='no indicada',
                     estadistico='mediana (lectura gráfica aproximada, ±0.3 kWh/t)', CBWI_kWh_t=cb,
                     notas=f'UCS mediana leída ≈{u} MPa (coherente con la tabla de lámina 12); CBWI estimado con CWI = 8.02·ln(UCS) − 22.10 (lámina 3)'))

# lámina 17: toneladas por litología (aprox.)
L17 = {'Intrusivo': 0.69e9, 'Intrus-Estruct-Tab': 0.05e9, 'Caliza': 0.40e9, 'Margas-Limonitas': 0.95e9, 'Horfels': 0.79e9, 'Horfel Diopsida': 0.17e9,
       'Marmol': 1.80e9, 'Marmol Diopsida': 0.13e9, 'Brechas-Intrus': 0.003e9}
for lit, t in L17.items():
    l = BLQ[lit]
    rows.append(base(fuente=FWSC, hoja_lamina='lámina 17 (Toneladas acumuladas por litología, WSC_s17_6.png)', fila_o_ubicacion=lit,
                     nivel='unidad (bloques del modelo geológico MR24)', id_muestra_o_unidad=f'MR24-{lit}', litologia_informe=lit,
                     litologia=l[0], litologia_detalle=l[1], alteracion=l[2], clase_desmonte='no indicada',
                     estadistico='total (lectura gráfica aproximada, ±0.03e9 t)', toneladas_modelo=t,
                     notas='toneladas de desmonte en el modelo de bloques por litología (lámina 17, anexo)'))

# lámina 8: histogramas (modas aproximadas)
for desc, kw in [('núcleos: UCS', dict(UCS_MPa=55, notas='moda ≈50–65 MPa; rango ≈5–300 MPa; asimetría positiva (lectura gráfica)')),
                 ('bloques: UCS', dict(UCS_MPa=72, notas='moda ≈70–75 MPa; rango ≈20–225 MPa (lectura gráfica)')),
                 ('núcleos: abrasión', dict(abrasion_pct=22, notas='moda ≈20–25; rango ≈3–83; grupo secundario ≈60 (lectura gráfica); unidad "ABRASION_pc"')),
                 ('bloques: abrasión', dict(abrasion_pct=26, notas='modas ≈26 y ≈41 (bimodal); rango ≈12–67 (lectura gráfica)')),
                 ('núcleos: densidad', dict(densidad_t_m3=2.71, notas='moda ≈2.70–2.72; grupo secundario ≈2.40–2.55; rango 1.95–3.55 (lectura gráfica); unidad no indicada, se asume t/m³')),
                 ('bloques: densidad', dict(densidad_t_m3=2.71, notas='moda ≈2.70–2.72; secundarios ≈2.45 y ≈2.88; rango 2.15–3.45 (lectura gráfica); unidad no indicada'))]:
    rows.append(base(fuente=FWSC, hoja_lamina='lámina 8 (histogramas, WSC_s08_*.png)', fila_o_ubicacion=desc, nivel='conjunto (todas las litologías)',
                     id_muestra_o_unidad=desc, litologia='todas', litologia_detalle='todas las litologías juntas',
                     estadistico='moda (lectura gráfica aproximada)', clase_desmonte='no indicada', **kw))

cm = pd.DataFrame(rows, columns=COLS)
cm.to_csv(os.path.join(OUT, 'caracterizacion_muestras.csv'), index=False, encoding='utf-8')
print('caracterizacion_muestras', cm.shape, 'muestras', n_muestras)
print(cm.groupby(['fuente', 'hoja_lamina']).size().to_string())

# ---------- parametros_RMU ----------
wb = openpyxl.load_workbook(fgeo, data_only=True)
ws = wb['Resumen']
params = [('C', 'UCS', 'MPa', 'UCS'), ('D', 'Is50 axial', 'MPa', 'PLTA'), ('E', 'Is50 diametral', 'MPa', 'PLTD'), ('F', 'tracción brasileña', 'MPa', 'Brazilian'),
          ('G', 'φ corte directo', '°', 'Corte'), ('H', 'c corte directo', 'MPa', 'Corte'), ('I', 'RMR', '-', 'RMR_RQD_FF'), ('J', 'RQD', '%', 'RMR_RQD_FF'),
          ('K', 'FF', 'estructuras/m', 'RMR_RQD_FF')]
src = {'UCS': ('UCS', 'RMU', 'Resist. Comp Simple (MPa)'), 'Is50 axial': ('PLTA', 'RMU', 'Is(50)'), 'Is50 diametral': ('PLTD', 'RMU', 'Is(50)'),
       'tracción brasileña': ('Brazilian', 'Unidad Geotécnica', 'Resistencia a la  tracción  (MPa)'),
       'φ corte directo': ('Corte', 'Unidad Geotécnica', 'Angulo de Fricción (°)'), 'c corte directo': ('Corte', 'Unidad Geotécnica', 'Cohesión en (Mpa)'),
       'RMR': ('RMR_RQD_FF', 'UG', 'RMR'), 'RQD': ('RMR_RQD_FF', 'UG', 'RQD Corregido'), 'FF': ('RMR_RQD_FF', 'UG', 'Nro_Total_Estructuras/ Por metro (FF)')}
AUX = {"UCS": "UCS_rev", "PLTA": "plta_rev", "PLTD": "pldt_rev", "Brazilian": "Sheet7", "Corte": "Sheet8", "RMR_RQD_FF": "RMR_RQD_FF (cols J–W)"}
cache = {}


def data(p):
    s, u, v = src[p]
    if s not in cache:
        cache[s] = pd.read_excel(fgeo, sheet_name=s)
    d = cache[s]
    d = d[d[u].notna()].copy()
    d[v] = pd.to_numeric(d[v], errors='coerce')
    return d, u, v


prow = []
start = {'END': 7, 'EXO': 11, 'HRN': 15, 'INT': 19, 'LMH': 23, 'XDP': 27}
statrow = {'media': 0, 'P50': 2, 'P35': 3}
for code, r0 in start.items():
    l = RMU[code]
    for col, p, un, sh in params:
        d, u, v = data(p)
        x = d[d[u] == code][v].dropna()
        rec = {'media': x.mean(), 'P50': x.quantile(.5), 'P35': x.quantile(.35), 'P16': x.quantile(.16), 'P84': x.quantile(.84),
               'desv. estándar': x.std(), 'mínimo': x.min(), 'máximo': x.max()}
        for est in ['media', 'P50', 'P35', 'P16', 'P84', 'desv. estándar', 'mínimo', 'máximo']:
            vi = ws[f'{col}{r0 + statrow[est]}'].value if est in statrow else ''
            nota = ''
            if est in statrow and isinstance(vi, (int, float)) and abs(vi - rec[est]) > 0.01 * max(1, abs(rec[est])):
                nota = f'DISCREPANCIA: valor del Resumen {vi} distinto del recalculado {rec[est]:.3f}'
                if code == 'XDP' and p == 'UCS' and est == 'P35':
                    nota += ' (la fórmula UCS!J2394 usa la columna F = año: error de la hoja; usar el recalculado)'
            if est in ('P16', 'P84'):
                nota = (nota + ' ').strip() + f'percentiles 16/84 también calculados en la hoja auxiliar {AUX[sh]}'
            prow.append(dict(rmu=code, litologia_informe=code, litologia=l[0], litologia_detalle=l[1], alteracion=l[2],
                             correspondencia_rmu_litologias=RMU_CORR[code], parametro=p, unidad=un, estadistico=est,
                             valor_informe=('' if vi in (None, '', ' --', '--') else vi), valor_recalculado=round(float(rec[est]), 4), n=len(x),
                             base=('estadística de ensayos de laboratorio en núcleos (roca intacta)' if sh in ('UCS', 'PLTA', 'PLTD', 'Brazilian') else
                                   'estadística de ensayos de corte directo en núcleos (tipo de superficie no indicado)' if sh == 'Corte' else
                                   'estadística de logueo geotécnico de tramos de sondaje'),
                             fuente=f'{FGEO} / {FPGR}',
                             hoja_lamina=(f'xlsx Resumen fila {r0 + statrow[est]} col {col}; hoja {sh}; PGR lámina 4; WSC lámina 12 (sin RMR/RQD/FF)'
                                          if est in statrow else f'xlsx hoja {sh} (recalculado)'),
                             notas=nota))
for p, f in [('CWI estimado', 'CWI (kWh/t) = 8.02·log(UCS) − 22.10 (log natural, según los valores de la tabla)'),
             ('Crushability estimada', 'Crushability (%) = 286.06/√UCS − 0.012')]:
    prow.append(dict(rmu='todas', litologia='todas', parametro=p, unidad='kWh/t' if 'CWI' in p else '%', estadistico='correlación', valor_informe=f,
                     base='regresión con 4 materiales (M1, Waste-C/Std, Waste-Fine, Waste-Hard)', fuente=FWSC, hoja_lamina='lámina 3',
                     notas='no es parámetro geotécnico; relaciona UCS con energía de chancado'))
pr = pd.DataFrame(prow)
pr.to_csv(os.path.join(OUT, 'parametros_RMU.csv'), index=False, encoding='utf-8')
print('parametros_RMU', pr.shape)
print(pr[pr.notas.str.contains('DISCREP', na=False)][['rmu', 'parametro', 'estadistico', 'valor_informe', 'valor_recalculado']].to_string())

# ---------- fragmentación ----------
ff = os.path.join(W, FFRAG)
df = pd.read_excel(ff, header=4)
df['_fila'] = df.index + 6
df = df[df['Año'].notna()]
ren = {'Fecha de Voladura': 'fecha_voladura', 'Fecha de análisis': 'fecha_analisis', 'Equipo': 'equipo', 'Fase': 'fase', 'Proyecto': 'proyecto_voladura',
       'POLIGONO': 'poligono', 'COTA': 'cota_banco_m', 'Tipo de material': 'clase_material_informe', 'Target (cm)': 'target_cm', 'Clasificación': 'clasificacion',
       'Zona': 'zona', 'Cantidad de fotos': 'n_fotos', 'Xc (cm)': 'Xc_cm', 'b': 'b', 'n': 'n_RR', '<1 cm': 'pasa_1cm_frac', '< 2 cm': 'pasa_2cm_frac',
       'P10 (cm)': 'P10_cm', 'P20 (cm)': 'P20_cm', 'P30 (cm)': 'P30_cm', 'P40 (cm)': 'P40_cm', 'P50 (cm)': 'P50_cm', 'P60 (cm)': 'P60_cm', 'P70 (cm)': 'P70_cm',
       'P80 (cm)': 'P80_cm', 'P90 (cm)': 'P90_cm', 'Xmax (cm)': 'Xmax_cm', 'DIG RATE (t/h)': 'dig_rate_t_h', 'Ton': 'toneladas', 'Kg cargados': 'kg_explosivo',
       'FP': 'factor_potencia_kg_t', 'FE (MJ/Tn)': 'factor_energia_MJ_t', 'Altura taladro (m)': 'altura_taladro_m', 'Taco (m)': 'taco_m',
       'Diámetro taladro (")': 'diametro_taladro_in', 'Burden': 'burden_m', 'Spacing': 'espaciamiento_m', 'Subdrill': 'sobreperforacion_m',
       'CANTIDAD DE TALADROS': 'n_taladros', 'Explosivo': 'explosivo', 'COMBUSTIBLE': 'combustible',
       '< 1/2"': 'modeloRR_pasa_0.5in', '< 1"': 'modeloRR_pasa_1in', '< 2"2': 'modeloRR_pasa_2in', '< 4"': 'modeloRR_pasa_4in', '< 6"': 'modeloRR_pasa_6in',
       'Xc (in)': 'Xc_in', 'P10 (cm)2': 'modeloRR_P10_cm', 'P20 (cm)2': 'modeloRR_P20_cm', 'P30 (cm)2': 'modeloRR_P30_cm', 'P40 (cm)2': 'modeloRR_P40_cm',
       'P50 (cm)2': 'modeloRR_P50_cm', 'P60 (cm)2': 'modeloRR_P60_cm', 'P70 (cm)2': 'modeloRR_P70_cm', 'P80 (cm)2': 'modeloRR_P80_cm',
       'P90 (cm)2': 'modeloRR_P90_cm', 'Xmax (cm)2': 'modeloRR_Xmax_cm', 'OBSERVACIÓN': 'observacion'}
missing = [k for k in ren if k not in df.columns]
print('columnas no encontradas:', missing)
fr = df.rename(columns=ren)
keep = list(dict.fromkeys(ren.values()))
fr = fr[['_fila'] + [c for c in keep if c in fr.columns]].rename(columns={'_fila': 'fila_excel'})
for c in ['P10', 'P50', 'P80', 'P90']:
    fr[f'D{c[1:]}_mm'] = pd.to_numeric(fr[f'{c}_cm'], errors='coerce') * 10
fr['Dmax_mm'] = pd.to_numeric(fr['Xmax_cm'], errors='coerce') * 10
for c in ['fecha_voladura', 'fecha_analisis']:
    fr[c] = pd.to_datetime(fr[c]).dt.date
fr.insert(0, 'hoja', 'ANÁLISIS DE FRAGMENTACIÓN')
fr.insert(0, 'fuente', FFRAG)
fr.insert(3, 'clase_desmonte', 'ROM (fragmentación post-voladura en el frente de carguío, por análisis de fotos)')
fr.insert(4, 'litologia', '')
fr.insert(5, 'litologia_detalle', 'no indicada en el archivo')
fr['notas'] = ('P10–P90 y Xmax medidos por análisis de imagen (n_fotos); modeloRR_* = bloque "MODELO ROSIN-RAMMLER" del archivo (valores pegados, sin fórmula); '
               'las fracciones modeloRR_pasa_* no son coherentes con P10–P90 medidos (ver resumen)')
fr.to_csv(os.path.join(OUT, 'fragmentacion.csv'), index=False, encoding='utf-8')
print('fragmentacion', fr.shape)
num = ['P10_cm', 'P50_cm', 'P80_cm', 'P90_cm', 'Xmax_cm', 'Xc_cm', 'n_RR', 'pasa_1cm_frac', 'pasa_2cm_frac', 'factor_potencia_kg_t']
for c in num:
    fr[c] = pd.to_numeric(fr[c], errors='coerce')
print(fr.groupby('clase_material_informe')[num].agg(['count', 'median']).round(2).T.to_string())
print(fr.groupby('fase')[['P50_cm', 'P80_cm', 'Xmax_cm']].agg(['count', 'median']).round(1).to_string())
print(fr.groupby('zona')[['P50_cm', 'P80_cm', 'Xmax_cm']].agg(['count', 'median']).round(1).to_string())
print(fr[num].describe(percentiles=[.1, .5, .9]).round(2).to_string())
print(fr.groupby(['fase', 'clase_material_informe']).size().unstack().to_string())
print('cotas por fase', fr.groupby('fase')['cota_banco_m'].agg(['min', 'max']).to_string())
print('outliers b>10 o n>5:', fr[(pd.to_numeric(fr.b, errors='coerce') > 10) | (fr.n_RR > 5)][['fila_excel', 'b', 'n_RR', 'P30_cm']].to_string())
print('P30 > P40:', fr[fr.P30_cm > pd.to_numeric(fr.P40_cm, errors='coerce')][['fila_excel', 'P20_cm', 'P30_cm', 'P40_cm']].to_string())
