# -*- coding: utf-8 -*-
"""condiciones_Golder2010.csv y condiciones_Golder2021.csv (una fila por set). uso: python build_condiciones.py <dir_datos_antamina>"""
import sys, os, csv, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos_transcritos_2010 import GOLDER_CU, VECTOR_HDR, VECTOR_SET, MOHR_GOLDER, VECTOR_ENV
base = sys.argv[1]; here = os.path.dirname(os.path.abspath(__file__))
NI = 'no informado'
COLS = ['fuente','set_id','origen_muestra','clase_desmonte','litologia','litologia_detalle','litologia_proporcion','Dmax_campo_mm',
        'granulometria_campo','densidad_campo','escalamiento_metodo','Dmax_lab_mm','D_probeta_mm','H_probeta_mm','D_sobre_Dmax',
        'granulometria_lab','preparacion','gamma_d_montaje_kNm3','w_montaje_pct','Gs_valor','Gs_origen','e0_recalculado',
        'saturacion','contrapresion_kPa','consolidacion','gamma_d_post_consolidacion_kNm3','drenaje_corte','velocidad_pct_min',
        'deformacion_final_pct','criterio_falla_informe','hay_pico','hay_curva_tabulada','envolvente_informe','Bg_metodo',
        'UCS','Is50','LA_pct','durabilidad','absorcion_pct','paginas','notas_verificacion']
# ------------------------------------------------------------------ 2010
F10 = '2010_Golder_Caracterizacion ROM IPCC.pdf'
LIT = {'MN': ('Mármol', 'mármol negro (MAR-M-01)'), 'HG': ('Hornfels', 'hornfels gris (HOR-M-01)'),
       'INT': ('Intrusivo', 'intrusivo, sin subtipo (INT-M-01)'), 'EXO': ('Skarn', 'exoskarn diópsido (EXO-M-01)')}
FECHA = {('MN','A'):'02/07/2009',('HG','A'):'06/07/2009',('INT','A'):'07/07/2009',('EXO','A'):'29/08/2009',
         ('MN','B'):'22/09/2009',('HG','B'):'22/09/2009',('INT','B'):'23/09/2009',('EXO','B'):'23/09/2009'}
GRAN = {  # hoja de granulometría de terreno (ASTM D422/D1140): pag, D60, D30, D10, Cu, Cc, grava(N4-3"), arena, finos, bloques>12", cantos 3-12", SUCS, TM (Tabla 1), Cu/Cc figura
 ('MN','A'):(27,265.0,60.0,3.0,88.3,4.5,23.6,8.3,2.8,35.1,30.2,'GP-GM','35" (889 mm); 100 % pasa 35"','88.3/4.5 (Fig.3)'),
 ('HG','A'):(28,205.0,78.0,20.0,10.3,1.5,24.9,2.9,0.9,22.1,49.3,'GP','>35" (94.9 % pasa 35" = 889 mm)','10.3/1.5 (Fig.1)'),
 ('INT','A'):(29,183.0,55.0,9.0,20.3,1.8,31.4,6.5,1.6,21.8,38.8,'GP','30" (762 mm)','30.3/1.8 (Fig.4: Cu mal copiado; hoja 20.3)'),
 ('EXO','A'):(30,33.0,8.5,0.8,41.3,2.7,58.0,19.0,2.7,4.6,15.6,'GP','19" (483 mm)','41.3/2.7 (Fig.2)'),
 ('MN','B'):(31,50.5,11.2,0.1,476.4,23.4,43.3,15.5,7.2,0.0,34.0,'GP-GM','12" (305 mm) según Tabla 1; Tabla 2 repite 35"','485.3/26.6 (Fig.3)'),
 ('HG','B'):(32,63.0,23.8,6.8,9.3,1.3,56.3,5.4,2.7,0.0,35.6,'GP','12" (305 mm) según Tabla 1; Tabla 2 repite 35"','7.9/1.0 (Fig.1)'),
 ('INT','B'):(33,57.5,8.5,0.1,410.7,9.0,40.7,17.6,7.0,0.0,34.7,'GP-GM','12" (305 mm) según Tabla 1; Tabla 2 repite 30"','400/10 (Fig.4)'),
 ('EXO','B'):(34,18.9,5.1,0.2,84.0,6.0,60.9,23.0,5.4,0.0,10.7,'GP','12" (305 mm) según Tabla 1; Tabla 2 repite 19"','76.2/6.4 (Fig.2)')}
DMAXC = {('MN','A'):889,('HG','A'):'>889',('INT','A'):762,('EXO','A'):483,('MN','B'):305,('HG','B'):305,('INT','B'):305,('EXO','B'):305}
DENS = {('MN','A'):(35,2.185,2.135,2.4),('HG','A'):(36,2.055,2.026,1.44),('INT','A'):(37,1.931,1.865,3.5),('EXO','A'):(38,2.350,2.273,3.4),
        ('MN','B'):(39,2.200,2.151,2.3),('HG','B'):(40,2.162,2.137,1.20),('INT','B'):(41,2.060,2.019,2.0),('EXO','B'):(42,2.418,2.357,2.6)}
IDX = {  # UCS lab (2 probetas), σc PL (Tabla 2) y Is50 medio, LA, durabilidad, absorción
 ('MN','A'):('44.7 MPa (41.0; 48.3), ASTM D2938, 2 probetas, p.66','13.7 kg/cm² (4 probetas; σc PL 32.24 MPa), p.74','62.1 (C535), p.50','43.4 % MgSO4, p.58','0.34 (C127), p.48'),
 ('HG','A'):('49.2 MPa (46.8; 51.6), p.67','31.1 kg/cm² (4; σc 72.99 MPa), p.75','23.7, p.51','0.7 % MgSO4, p.59','0.24, p.48'),
 ('INT','A'):('46.8 MPa (48.4; 45.1), p.68','34.2 kg/cm² (4; σc 80.56 MPa), p.76','49.8, p.52','33.4 % MgSO4, p.60','1.66, p.48'),
 ('EXO','A'):('73.3 MPa (79.3; 67.3), p.69','28.8 kg/cm² (4; σc 67.79 MPa), p.77','37.0, p.53','5.9 % MgSO4, p.61','1.44, p.48'),
 ('MN','B'):('49.6 MPa (41.5; 57.7), p.70','10.4 kg/cm² (8; σc 24.56 MPa), p.78','62.4, p.54','49.8 % MgSO4, p.62','0.33, p.48'),
 ('HG','B'):('65.5 MPa (62.6; 68.3), p.71','42.7 kg/cm² (8; σc 100.42 MPa), p.79','20.3, p.55','0.6 % MgSO4, p.63','0.12, p.48'),
 ('INT','B'):('54.0 MPa (56.1; 51.8), p.72','32.7 kg/cm² (8; σc Tabla 2 78.06 MPa, hoja 76.97 MPa), p.80','32.2, p.56','18.6 % MgSO4, p.64','2.17, p.48'),
 ('EXO','B'):('97.4 MPa (101.7; 93.1), p.73','53.0 kg/cm² (8; σc 124.78 MPa), p.81','27.6, p.57','6.7 % MgSO4, p.65','1.30, p.48')}
GSC = {('MN','A'):(2.717,2.696),('HG','A'):(2.737,2.733),('INT','A'):(2.461,2.451),('EXO','A'):(3.212,3.172),
       ('MN','B'):(2.725,2.725),('HG','B'):(2.740,2.740),('INT','B'):(2.647,2.647),('EXO','B'):(3.102,3.102)}
rows = []
def fila10(sid, lit, fase, diam, Dmaxlab, H, prep, gds, ws, Gs, e0s, sat, bp, consol, gdpost, vel, defin, crit, pico, curva, env, pags, notas):
    g = GRAN[(lit,fase)]; d = DENS[(lit,fase)]; ix = IDX[(lit,fase)]; gsc = GSC[(lit,fase)]
    clase = ('ROM. Base textual p.1: «La Fase A corresponde al conjunto de actividades realizadas en el material original procedente del tajo». '
             'Contradicción: las hojas de densidad in situ (p.35-38) rotulan «Material Chancado Fase A» en «Parte baja chancadora secundaria».') if fase=='A' else \
            ('Chancado. Base textual p.1: «La Fase B corresponde al conjunto de actividades realizadas en el material chancado»; LA p.54-57: «Material Chancado, en la planta secundaria».')
    rows.append(dict(fuente=F10, set_id=sid,
        origen_muestra=f'Acopio parte baja de chancadora secundaria (hojas de humedad/granulometría p.19-34); muestreado por personal de mina el {FECHA[(lit,fase)]}; tajo, fase y banco no informados; densidad in situ medida el {"02/09/2009" if fase=="A" else "25/09/2009"} en «Parte baja chancadora secundaria»',
        clase_desmonte=clase, litologia=LIT[lit][0], litologia_detalle=LIT[lit][1],
        litologia_proporcion='una sola litología por muestra; método de identificación no informado (nombre dado a la muestra)',
        Dmax_campo_mm=DMAXC[(lit,fase)],
        granulometria_campo=(f'Hoja p.{g[0]} (ASTM D422/D1140): D60={g[1]} mm, D30={g[2]} mm, D10={g[3]} mm, Cu={g[4]}, Cc={g[5]}; D50 y D80 no informados; '
                             f'bloques >12" {g[9]} %, cantos 3-12" {g[10]} %, grava {g[6]} %, arena {g[7]} %, finos {g[8]} %; SUCS {g[11]}; TM {g[12]}; Cu/Cc de la figura: {g[13]}'),
        densidad_campo=f'Reemplazo de agua ASTM D5030 (p.{d[0]}): γ húmeda {d[1]} t/m³, γd {d[2]} t/m³ (= {d[2]*9.81:.2f} kN/m³), w de la hoja {d[3]} %',
        escalamiento_metodo='Truncado (scalping) de la matriz: p.3 «Los ensayos de compresión triaxial CU se realizaron considerando materiales menores que 3"» y cuadro Ø 2.8"→3/8", 4"→5/8", 6"→1"; hojas: «Se usó material <3/8"» / «<5/8"»',
        Dmax_lab_mm=Dmaxlab, D_probeta_mm=diam, H_probeta_mm=H, D_sobre_Dmax=round(float(str(diam).split('/')[0])/Dmaxlab,1),
        granulometria_lab='no informada (no hay curva de la fracción ensayada; no se recalculó nada)',
        preparacion=prep, gamma_d_montaje_kNm3=gds, w_montaje_pct=ws, Gs_valor=Gs,
        Gs_origen=(f'ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. '
                   f'Gs grueso C127 bulk = {gsc[0]} (p.48); Tabla 2 da {gsc[1]}. Con Gs grueso e0 sería menor.'),
        e0_recalculado=e0s, saturacion=sat, contrapresion_kPa=bp, consolidacion=consol, gamma_d_post_consolidacion_kNm3=gdpost,
        drenaje_corte='no drenado (CU, ASTM D4767)', velocidad_pct_min=vel, deformacion_final_pct=defin, criterio_falla_informe=crit,
        hay_pico=pico, hay_curva_tabulada=curva, envolvente_informe=env,
        Bg_metodo='no informado (sin granulometría post-ensayo)', UCS=ix[0], Is50=ix[1], LA_pct=ix[2], durabilidad=ix[3]+' (hoja: sulfato de magnesio; texto p.2: sulfato de sodio)',
        absorcion_pct=ix[4], paginas=pags, notas_verificacion=notas))
for sid, s in GOLDER_CU.items():
    fase = sid.split('-')[1]; lit = sid.split('-')[2]
    E = s['ensayos']
    big = '4in' in sid
    diam = '/'.join(f'{t[2]*10:.1f}' for t in E); H = '/'.join(f'{t[1]*10:.1f}' for t in E)
    Dmaxlab = 15.9 if big else 9.5
    d0 = E[0][2]*10
    gds = '/'.join(f'{t[4]*9.81:.2f}' for t in E); ws = '/'.join(f'{t[3]}' for t in E)
    e0s = '/'.join(f'{s["Gs"]/t[4]-1:.3f}' for t in E) + ' (hoja: ' + '/'.join(str(t[5]) for t in E) + ')'
    gdpost = '/'.join(f'{t[8]*9.81:.2f}' for t in E) + ' (γd ' + '/'.join(str(t[8]) for t in E) + ' g/cm³; e ' + '/'.join(str(t[9]) for t in E) + '; S final ' + '/'.join(str(t[10]) for t in E) + ' %)'
    vel = '/'.join(str(t[11]) for t in E)
    m = MOHR_GOLDER[sid]
    env = f"Hoja Mohr p.{s['mohr']}: total c={m[0]} kPa φ={m[1]}°; efectiva c'={m[2]} kPa φ'={m[3]}°"
    if sid.startswith('G2010-A') and not big:
        env += f"; Tabla 3 (p.9) da estos c y c' en kg/cm² aunque rotula kPa ({m[0]}→{round(m[0]/98.0665)}, {m[2]}→{round(m[2]/98.0665)})"
    notas = []
    if sid == 'G2010-A-EXO-4in':
        notas.append('Probetas 2 y 3 montadas a γd 2.056 y 2.046 g/cm³, por debajo de la γd mínima de laboratorio 2.175 (p.43) y de la «densidad mínima 2.180» declarada: e0 0.695/0.703 > emax=0.602 (con Gs 3.484).')
    if sid in ('G2010-B-EXO-2.8in', 'G2010-B-EXO-4in'):
        notas.append('Saturación final >100 % (hasta 105.2 %): Gs 3.338 o γd inconsistentes; e0 incierto.')
    if sid == 'G2010-B-MN-4in':
        notas.append('Probeta 3 a γd 1.722 (< γd mínima 1.821); la Tabla 4 da 1.722 como «promedio».')
    if 'A-' in sid:
        notas.append('Densidad «de campo» usada para montar = la de la hoja de densidad in situ rotulada «Material Chancado Fase A».')
    rows_prep = s['obs'] + '; método de compactación y número de capas no informados'
    fila10(sid, lit, fase, diam, Dmaxlab, H, rows_prep, gds, ws, s['Gs'], e0s,
           'no informado (B no figura; S final ≈100 % según la hoja)', NI,
           f"isotrópica según ASTM D4767 (σ'3c = {'/'.join(str(t[0]) for t in E)} kPa); duración no informada; t50 «-»",
           gdpost, vel, 'no informada numéricamente (solo gráficos)', 'Esfuerzo desviador máximo (hoja Golder)',
           'no determinable: la hoja Golder solo da el estado de falla y gráficos', 'no (solo gráficos q-εa, u-εa, p\'-q)', env,
           f"{s['pag']}-{s['pag']+4};8;{9 if fase=='A' else 10};{GRAN[(lit,fase)][0]};{DENS[(lit,fase)][0]};48;49", ' '.join(notas))
# Vector
for sid in ['G2010-B-MN-6in','G2010-B-HG-6in','G2010-B-INT-6in','G2010-B-EXO-6in']:
    lit = sid.split('-')[2]
    ps = [p for p, s in VECTOR_SET.items() if s == sid]
    hs = [VECTOR_HDR[p] for p in ps]
    Gs = {'MN':2.747,'HG':2.802,'INT':2.742,'EXO':3.338}[lit]
    env = VECTOR_ENV[sid]
    notas = 'Vector no informa Gs, e0 ni granulometría; e0 calculado con Gs D854 de Golder. Vector no indica el tamaño máximo: el 1" sale del cuadro de p.3.'
    if lit in ('MN','INT'):
        notas += ' Cabeceras MN e INT idénticas en w inicial (4.50 %) y w final (8.50/8.84/9.56 %): posible plantilla copiada.'
    pico = {'MN':'sí en las 3 probetas (εa 1.0-1.5 %), con ablandamiento posterior',
            'HG':'500 kPa: pico a 1.25 %; 250 y 125 kPa: pico local temprano y luego endurecimiento hasta 14 %',
            'INT':'sí en las 3 (εa 0.75-1.75 %); a 125 kPa σ\'3 cae a ≈13 kPa (casi licuación)',
            'EXO':'500 y 250 kPa: pico local temprano y luego endurecimiento; 125 kPa: sin pico (endurece hasta 14 %)'}[lit]
    fila10(sid, lit, 'B', '/'.join(f'{h[2]*10:.1f}' for h in hs), 25.4, '/'.join(f'{h[0]*10:.1f}' for h in hs),
           'Remoldeado (estado «Remoldeado» en la hoja Vector); criterio de densidad y método de compactación no informados',
           '/'.join(f'{h[6]*9.81:.2f}' for h in hs), '/'.join(f'{h[4]:.2f}' for h in hs), Gs,
           '/'.join(f'{Gs/h[6]-1:.3f}' for h in hs),
           f"Parámetro B = {'/'.join(str(h[8]) for h in hs)} (menor que 0.95)", '/'.join(str(h[10]) for h in hs),
           f"isotrópica; σ'3c = 500/250/125 kPa (celda {'/'.join(str(h[9]) for h in hs)} kPa); duración no informada",
           '/'.join(f'{h[7]*9.81:.2f}' for h in hs) + ' (γd final de consolidación ' + '/'.join(str(h[7]) for h in hs) + ' g/cm³)',
           '0.082 (0.01 pulg/min sobre H=31 cm)', '14', 'Pico de esfuerzo desviador y 12 % de deformación (Vector)', pico, 'sí (tabla εa, Δσ, u, σ\'3, σ\'1, p, q, oblicuidad)',
           f"Hoja p.{env[0]}: pico total c={env[1][0]} φ={env[1][1]}°, efectiva c'={env[1][2]} φ'={env[1][3]}°; 12 %: total c={env[2][0]} φ={env[2][1]}°, efectiva c'={env[2][2]} φ'={env[2][3]}°",
           f"{ps[0]}-{ps[0]+5};3;10;{GRAN[(lit,'B')][0]};{DENS[(lit,'B')][0]};49", notas)
with open(os.path.join(base,'verificado','condiciones_Golder2010.csv'),'w',newline='',encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
print('2010', len(rows))
# ------------------------------------------------------------------ 2021
F21 = '2021_Golder_Ensayos de Laboratorio Commingling.pdf'
cur = json.load(open(os.path.join(here,'g21_curvas.json'), encoding='cp1252'))
SETS = [('G21-DESM-COMP',[108,109,110],None,2.762,'0 %',(0,40),(0,41,112),46,'GP-GM','D10=0.0778, D30=1.5869, D50=7.3703, D60=10.1146 mm, Cu=129.97, Cc=3.20; grava 59.5 %, arena 30.8 %, finos 9.7 % (limo 9.2, arcilla 0.5)'),
        ('G21-ALT1-9:1',[115,116,117],179,2.793,'10 % relave filtrado (~86 % sólidos)',(84,40),(83,40,119),47,'GM','D10=0.0507, D30=0.6621, D50=5.7715, D60=8.7665 mm, Cu=172.96, Cc=0.99; grava 53.6, arena 33.3, finos 13.1 %'),
        ('G21-ALT1-4:1',[122,123,124],None,2.846,'20 % relave filtrado',(59,40),(58,40,126),48,'GM','D10=0.0443, D30=0.2874, D50=4.0365, D60=7.4082 mm, Cu=167.06, Cc=0.25; grava 47.7, arena 36.4, finos 15.9 %'),
        ('G21-ALT1-1:1',[129,130,131],180,3.000,'50 % relave filtrado',(24,38),(22,38,133),49,'SM','D10=0.0208, D30=0.0952, D50=0.2833, D60=0.7395 mm, Cu=35.57, Cc=0.59; grava 29.8, arena 44.0, finos 26.2 %'),
        ('G21-ALT2-9:1',[136,137,138],181,2.789,'10 % relave en pasta (~80 % sólidos)',(53,40),(53,40,140),50,'GM','D10=0.0526, D30=0.6079, D50=6.3687, D60=10.6137 mm, Cu=201.90, Cc=0.66; grava 53.7, arena 33.2, finos 13.1 %'),
        ('G21-ALT2-4:1',[143,144,145],None,2.851,'20 % relave en pasta',(41,40),(41,40,147),51,'GM','D10=0.0394, D30=0.2431, D50=3.9094, D60=7.5292 mm, Cu=191.11, Cc=0.20; grava 47.7, arena 35.5, finos 16.8 %'),
        ('G21-ALT2-1:1',[150,151,152],182,3.006,'50 % relave en pasta',(29,39),(29,39,154),52,'SM','D10=0.0215, D30=0.1020, D50=0.3191, D60=1.0164 mm, Cu=47.36, Cc=0.48; grava 29.9, arena 44.8, finos 25.3 %'),
        ('G21-ALT4-9:1',[157,158,159],183,2.793,'10 % relave cicloneado (~86 % sólidos; 80 % gruesos/20 % finos)',(62,40),(62,40,161),53,'GW-GM','D10=0.0654, D30=0.7774, D50=5.7170, D60=8.5892 mm, Cu=131.25, Cc=1.08; grava 53.7, arena 34.9, finos 11.4 %'),
        ('G21-ALT4-4:1',[164,165,166],None,2.846,'20 % relave cicloneado',(66,39),(66,39,168),54,'GM','D10=0.0593, D30=0.3140, D50=4.0732, D60=7.1259 mm, Cu=120.18, Cc=0.23; grava 47.7, arena 39.6, finos 12.7 %'),
        ('G21-ALT4-1:1',[171,172,173],184,3.003,'50 % relave cicloneado',(51,37),(51,37,175),55,'SM','D10=0.0449, D30=0.1250, D50=0.3076, D60=0.6814 mm, Cu=15.19, Cc=0.51; grava 29.8, arena 51.5, finos 18.7 %')]
T8gd = {'G21-DESM-COMP':(2.089,2.089,2.087),}
K = {179:'5.6E-06',180:'8.9E-07 (Tabla 9: 8.90E-06)',181:'8.1E-06',182:'1.4E-06',183:'6.7E-06',184:'2.5E-06'}
rows = []
for sid, ps, kp, Gs, rel, t7, hoja, pg, sucs, gran in SETS:
    hs = [cur[str(p)]['h'] for p in ps]
    gd0 = [float(h['ini'][4]) for h in hs]
    if sid == 'G21-DESM-COMP': gd0 = [2.089, 2.089, 2.087]
    elif sid == 'G21-ALT1-1:1': gd0 = [1.802, 1.801, 1.802]
    else: gd0 = [1.802]*3
    w0 = [h['ini'][3] for h in hs]
    comp = sid == 'G21-DESM-COMP'
    rows.append(dict(fuente=F21, set_id=sid,
        origen_muestra='no informado (tajo, fase, banco o botadero no indicados). Muestras Tipo A/B/C recibidas en el laboratorio Golder Lima el 11/08/2020 (Tabla 1, p.6-7); relaves del segundo lote (16/09 y 21/10/2020, p.7 y p.9)',
        clase_desmonte='no indicada. El informe solo tipifica A/B/C por geoquímica: p.6 «cuya tipificación obedece a consideraciones geoquímicas de potencial de generación de acidez»; no dice ROM, Chancado ni Enrocado',
        litologia='Mezcla' + ('' if comp else ' (desmonte + relave)'),
        litologia_detalle='Tipo A (intrusivo), Tipo B (mármol y hornfels), Tipo C (hornfels), según p.6 y p.27; base de la identificación no informada (sin petrografía ni conteo)',
        litologia_proporcion='desmonte compuesto 0.35 A : 0.15 B : 0.50 C en masa seca (p.6, p.9; «información proporcionada por Antamina», LOM EVA1 y EVA3A) ⇒ intrusivo 35 %, mármol+hornfels 15 % (reparto no informado), hornfels 50 %' + ('' if comp else f'; mezcla con {rel} en masa seca'),
        Dmax_campo_mm='no informado', granulometria_campo='no informada (solo se ensayaron muestras truncadas a 1")',
        densidad_campo='no informada',
        escalamiento_metodo='Truncado (scalping): p.9 «Las muestras primigenias de desmonte Tipo A, Tipo B y Tipo C fueron limitadas a partículas menores a una pulgada, debido a las limitaciones inherentes a los equipos de laboratorio»; aplicado antes de mezclar. p.29: los resultados «no representan de manera verídica el comportamiento de los materiales in-situ a escala real»',
        Dmax_lab_mm=25.4, D_probeta_mm=152.4, H_probeta_mm=305.1, D_sobre_Dmax=6.0,
        granulometria_lab=f'Hoja p.{pg} (ASTM D422/D7928, hidrómetro): {gran}; SUCS {sucs}; no recalculada',
        preparacion=('Remoldeado «a la densidad seca de 2.084 g/cm3 y 2.0 % de humedad» (hojas p.108-110); real 2.089/2.089/2.087 g/cm³ = 90 % del Proctor estándar corregido por sobretamaño (22.72 kN/m³, ASTM D698 + D4718, p.97) o 92 % del no corregido (22.26). Método de compactación y capas no informados' if comp else
                     f'Remoldeado «a la DS 1.8 g/cm3 ... según solicitud del cliente» (hojas p.{ps[0]}-{ps[2]}); ≈78-80 % del Proctor estándar de la Tabla 6 (suelta). Método de compactación y capas no informados'),
        gamma_d_montaje_kNm3='/'.join(f'{g*9.81:.2f}' for g in gd0), w_montaje_pct='/'.join(w0), Gs_valor=Gs,
        Gs_origen=f'«G. Específica (Promedio)» impresa en las hojas triaxiales (p.{ps[0]}-{ps[2]}); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor',
        e0_recalculado='/'.join(f'{Gs/g-1:.3f}' for g in gd0) + ' (Tabla 8: ' + {'G21-DESM-COMP':'0.32/0.32/0.32','G21-ALT1-1:1':'0.66/0.67/0.67','G21-ALT2-1:1':'0.67/0.67/0.67','G21-ALT4-1:1':'0.67/0.67/0.67','G21-ALT4-4:1':'0.58/0.58/0.23 (0.23 es error)'}.get(sid, '/'.join([{2.793:'0.55',2.789:'0.55',2.846:'0.58',2.851:'0.58'}.get(Gs,'')]*3)) + ')',
        saturacion='Por contrapresión; B = ' + '/'.join(str(h['B']) for h in hs),
        contrapresion_kPa='/'.join(h['contra'] for h in hs),
        consolidacion=f"isotrópica; σ'3c = {'/'.join(h['s3c'] for h in hs)} kPa (celda {'/'.join(h['celda'] for h in hs)} kPa); duración no informada (t90 en la hoja)",
        gamma_d_post_consolidacion_kNm3='/'.join(f'{float(h["final_consol"][4])*9.81:.2f}' for h in hs) + ' (hojas; Tabla 8 «antes del corte» equivalente)',
        drenaje_corte='drenado (CID, ASTM D7181)', velocidad_pct_min=0.111,
        deformacion_final_pct='≈20 (13.85 en Alt.2 4:1 a 1200 kPa)' if sid=='G21-ALT2-4:1' else '≈20',
        criterio_falla_informe='«Esfuerzo Desv. Máximo» (hoja; pero σ1 impreso corresponde a εa≈16 %); Tabla 8 «Máx. Esfuerzo Desviador»',
        hay_pico='ver columna hay_pico del CSV verificado (por probeta)', hay_curva_tabulada='sí',
        envolvente_informe=f"Tabla 7 (p.19): c={t7[0]} kPa φ={t7[1]}°; hoja p.{hoja[2]}: c={hoja[0]} kPa φ={hoja[1]}°",
        Bg_metodo='no informado (sin granulometría post-ensayo)', UCS='no ensayado', Is50='no ensayado', LA_pct='no ensayado', durabilidad='no ensayado',
        absorcion_pct=('compuesto 0.54 % (C127, Tabla 5 y p.86); A 3.39, B 1.22, C 0.61 % (p.83-85)' if comp else 'gruesos de la mezcla, C127 (p.87-95); ver resumen'),
        paginas=f'6;9;11;15;18;19;20-22;{pg};{ps[0]}-{ps[2]};{hoja[2]}' + (f';23;{kp}' if kp else ''),
        notas_verificacion=('' if not kp else f'Permeabilidad pared flexible ASTM D5084 (p.{kp}) a σ\'=399 kPa sobre la probeta triaxial de ≈400 kPa: k20 = {K[kp]} m/s.')))
with open(os.path.join(base,'verificado','condiciones_Golder2021.csv'),'w',newline='',encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=COLS); w.writeheader(); w.writerows(rows)
print('2021', len(rows))


