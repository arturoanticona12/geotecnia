# -*- coding: utf-8 -*-
"""indices_roca_Golder2010.csv: una fila por determinación o estadístico informado (verificado en imagen)."""
import sys, os, csv
base = sys.argv[1]
F = '2010_Golder_Caracterizacion ROM IPCC.pdf'
LIT = {'MN': ('Mármol Negro', 'Mármol', 'mármol negro'), 'HG': ('Hornfels Gris', 'Hornfels', 'hornfels gris'),
       'INT': ('Intrusivo', 'Intrusivo', 'sin subtipo'), 'EXO': ('Exoskarn Diopsido', 'Skarn', 'exoskarn diópsido')}
FASE = {'A': ('A', 'ROM (Fase A = «material original procedente del tajo», p.1)'), 'B': ('B', 'Chancado (Fase B = «material chancado», p.1)')}
rows = []
def add(lit, fase, ensayo, norma, prop, valor, unidad, n, probeta, detalle, fecha, pag, nota=''):
    li = LIT[lit]
    rows.append(dict(fuente=F, litologia_informe=li[0], litologia=li[1], litologia_detalle=li[2], fase=FASE[fase][0],
                     clase_desmonte=FASE[fase][1], ensayo=ensayo, norma=norma, propiedad=prop, valor=valor, unidad=unidad,
                     n_probetas=n, probeta_id=probeta, detalle=detalle, fecha_ensayo=fecha, pagina=pag,
                     verificado_imagen='sí', notas=nota))
# --- UCS (ASTM D2938), por probeta: diam cm, long cm, L/D, factor, carga kgf, sigma_c MPa
UCS = {('MN','A',66,'09/07/2009'):[(4.57,8.92,1.95,1.00,6870,41.0),(4.58,8.95,1.95,1.00,8140,48.3)],
       ('HG','A',67,'09/07/2009'):[(4.61,9.12,1.98,1.00,7980,46.8),(4.58,9.13,1.99,1.00,8670,51.6)],
       ('INT','A',68,'09/07/2009'):[(4.57,9.30,2.04,1.00,8080,48.4),(4.60,9.16,1.99,1.00,7640,45.1)],
       ('EXO','A',69,'02/09/2009'):[(4.56,10.02,2.20,1.01,13050,79.3),(4.57,10.10,2.21,1.01,11120,67.3)],
       ('MN','B',70,'30/09/2009'):[(4.55,8.96,1.97,1.00,6900,41.5),(4.59,8.94,1.95,1.00,9770,57.7)],
       ('HG','B',71,'30/09/2009'):[(4.60,9.20,2.00,1.00,10600,62.6),(4.59,9.34,2.03,1.00,11500,68.3)],
       ('INT','B',72,'30/09/2009'):[(4.49,9.33,2.08,1.00,9020,56.1),(4.53,9.39,2.07,1.00,8480,51.8)],
       ('EXO','B',73,'30/09/2009'):[(4.54,9.46,2.08,1.01,16690,101.7),(4.61,9.45,2.05,1.00,15800,93.1)]}
T2 = {  # Tabla 2 (p.8): gamma_insitu, w, gd, Gs_grueso, Gs_fino, durab, LA, sc_PL, UCS, k, asent, TM
 ('MN','A'):(2.185,2.2,2.135,2.696,2.763,43.4,62.1,32.24,44.7,None,None,35),('HG','A'):(2.055,2.4,2.026,2.733,2.791,0.7,23.7,72.99,49.2,'3.20E-06',None,35),
 ('INT','A'):(1.931,3.8,1.865,2.451,2.674,33.4,49.8,80.56,46.8,'2.50E-06',None,30),('EXO','A'):(2.35,3.1,2.273,3.172,3.484,5.9,37,67.79,73.3,None,None,19),
 ('MN','B'):(2.2,2.9,2.151,2.725,2.747,49.8,62.4,24.56,49.6,None,4.8,35),('HG','B'):(2.162,2.3,2.137,2.74,2.802,0.6,20.3,100.42,65.5,'2.60E-06',5.6,35),
 ('INT','B'):(2.06,2.7,2.019,2.647,2.742,18.6,32.2,78.06,54,'2.20E-06',3.6,30),('EXO','B'):(2.418,3,2.357,3.102,3.338,6.7,27.6,124.78,97.4,None,5.1,19)}
for (li,fa,pg,fe),pr in UCS.items():
    for j,(d,L,ld,fc,P,s) in enumerate(pr,1):
        add(li,fa,'Compresión uniaxial simple','ASTM D2938','UCS (σc estandarizada según Protodyakonov)',s,'MPa',1,f'probeta {j}',
            f'Ø={d} cm; L={L} cm; L/D={ld}; factor={fc}; carga={P} kgf; muestra preparada en laboratorio',fe,pg)
    m = round(sum(x[5] for x in pr)/2, 2)
    add(li,fa,'Compresión uniaxial simple','ASTM D2938','UCS promedio (Tabla 2)',T2[(li,fa)][8],'MPa',2,'promedio',
        f'promedio recalculado de las hojas = {m} MPa','',f'8;{pg}')
# --- Carga puntual (ASTM D5731), por probeta: Ø mm, altura mm, A/D, De2 mm2, carga kg, Is, Is50, sigma_c kg/cm2 ; carga axial, falla tipo L
PL = {('MN','A',74,'09/07/2009'):[(45.80,41.40,0.90,2414,325,13.5,13.4,321),(45.80,38.30,0.84,2233,350,15.7,15.3,367),(45.80,41.10,0.90,2397,306,12.8,12.6,304),(45.80,44.50,0.97,2595,347,13.4,13.5,323)],
      ('HG','A',75,'09/07/2009'):[(45.90,37.80,0.82,2209,649,29.4,28.6,685),(45.80,38.90,0.85,2268,806,35.6,34.8,835),(45.90,41.20,0.90,2408,735,30.5,30.3,726),(45.90,46.00,1.00,2688,805,30.0,30.5,731)],
      ('INT','A',76,'09/07/2009'):[(45.90,38.70,0.84,2262,844,37.3,36.5,875),(45.90,43.10,0.94,2519,873,34.7,34.7,833),(45.70,42.20,0.92,2455,701,28.5,28.4,682),(45.90,39.00,0.85,2279,869,38.1,37.3,896)],
      ('EXO','A',77,'02/09/2009'):[(45.70,50.00,1.09,2909,756,26.0,26.9,645),(45.60,47.70,1.05,2769,742,26.8,27.4,658),(45.70,48.30,1.06,2810,902,32.1,33.0,791),(45.80,48.60,1.06,2834,770,27.2,27.9,671)],
      ('MN','B',78,'29/09/2009'):[(45.60,41.90,0.92,2433,279,11.4,11.4,273),(46.00,43.40,0.94,2542,244,9.6,9.6,231),(45.70,44.90,0.98,2613,229,8.8,8.8,212),(46.00,43.60,0.95,2554,262,10.3,10.3,248),(46.00,38.40,0.83,2249,250,11.1,10.8,260),(46.00,41.20,0.90,2413,293,12.1,12.0,289),(45.80,40.20,0.88,2344,226,9.6,9.5,228),(45.60,43.60,0.96,2531,277,10.9,11.0,263)],
      ('HG','B',79,'29/09/2009'):[(46.00,43.20,0.94,2530,937,37.0,37.1,892),(46.00,42.80,0.93,2507,1226,48.9,48.9,1175),(46.00,44.50,0.97,2606,930,35.7,36.0,864),(46.00,44.00,0.96,2577,1171,45.4,45.7,1098),(46.00,44.00,0.96,2577,1244,48.3,48.6,1166),(46.00,45.00,0.98,2636,1133,43.0,43.5,1044),(45.90,44.30,0.97,2589,1056,40.8,41.1,987),(45.90,44.20,0.96,2583,1032,40.0,40.3,966)],
      ('INT','B',80,'29/09/2009'):[(46.00,43.00,0.93,2518,724,28.8,28.8,691),(45.90,43.40,0.95,2536,892,35.2,35.3,846),(46.00,42.90,0.93,2513,852,33.9,33.9,815),(46.00,44.30,0.96,2595,874,33.7,34.0,815),(46.00,43.00,0.93,2518,841,33.4,33.5,803),(46.00,45.30,0.98,2653,698,26.3,26.6,640),(46.00,44.90,0.98,2630,900,34.2,34.6,831),(46.00,45.50,0.99,2665,917,34.4,34.9,838)],
      ('EXO','B',81,'29/09/2009'):[(46.00,42.00,0.91,2460,1403,57.0,56.8,1364),(45.90,42.00,0.92,2455,1318,53.7,53.5,1283),(46.00,42.40,0.92,2483,1546,62.3,62.2,1492),(46.00,40.80,0.89,2390,829,34.7,34.3,824),(46.00,39.60,0.86,2319,1068,46.1,45.3,1087),(46.00,41.90,0.91,2454,1468,59.8,59.6,1430),(46.00,41.90,0.91,2454,1548,63.1,62.8,1507),(45.80,45.00,0.98,2624,1290,49.2,49.7,1193)]}
for (li,fa,pg,fe),pr in PL.items():
    for j,(d,h,ad,de2,P,Is,Is50,sc) in enumerate(pr,1):
        det=f'Muestra cilíndrica, carga axial, falla tipo L; Ø={d} mm; altura={h} mm; A/D={ad}; De²={de2} mm²; carga={P} kg; Is={Is} kg/cm²'
        add(li,fa,'Carga puntual','ASTM D5731','Is(50)',Is50,'kg/cm²',1,f'M-{j}',det,fe,pg)
        add(li,fa,'Carga puntual','ASTM D5731','σc estimada (hoja)',sc,'kg/cm²',1,f'M-{j}',det+f'; σc={sc} kg/cm² = {sc*0.0980665:.2f} MPa',fe,pg)
    n=len(pr); mis=sum(x[6] for x in pr)/n; msc=sum(x[7] for x in pr)/n
    add(li,fa,'Carga puntual','ASTM D5731','Is(50) promedio (calculado aquí de la hoja)',round(mis,2),'kg/cm²',n,'promedio','no informado como tal en el informe; promedio aritmético de las probetas','',str(pg))
    nota = ''
    if (li,fa)==('INT','B'):
        nota='DISCREPANCIA: el promedio de la hoja (784.9 kg/cm² = 76.97 MPa) no coincide con la Tabla 2 (78.06 MPa) ni con la Fig. 4.'
    add(li,fa,'Carga puntual','ASTM D5731','σc estimada promedio (Tabla 2)',T2[(li,fa)][7],'MPa',n,'promedio',
        f'promedio recalculado de la hoja = {msc:.1f} kg/cm² = {msc*0.0980665:.2f} MPa','',f'8;{pg}',nota)
# --- Los Ángeles ASTM C535 (gradación 3"-2½", 2½"-2", 2"-1½"; 1000 rev.)
LA = {('MN','A'):(50,'04/07/2009',10104,3834,6270,62.1),('HG','A'):(51,'06/07/2009',10138,7738,2400,23.7),('INT','A'):(52,'08/07/2009',10002,5024,4978,49.8),
      ('EXO','A'):(53,'01/09/2009',10110,6367,3743,37.0),('MN','B'):(54,'26/09/2009',10039,3776,6263,62.4),('HG','B'):(55,'26/09/2009',10018,7980,2038,20.3),
      ('INT','B'):(56,'26/09/2009',10035,6805,3230,32.2),('EXO','B'):(57,'26/09/2009',9999,7241,2758,27.6)}
for (li,fa),(pg,fe,pi,pf,pm,la) in LA.items():
    add(li,fa,'Abrasión Los Ángeles','ASTM C535 / NTP 400.020','Desgaste por abrasión (1000 revoluciones)',la,'%',1,'única',
        f'peso inicial {pi} g, final {pf} g, pérdida {pm} g; fracciones 3"-2½", 2½"-2", 2"-1½"'+('; Fase B: «Material chancado, en la planta secundaria»' if fa=='B' else ''),fe,f'{pg};8')
# --- Durabilidad ASTM C88 con SULFATO DE MAGNESIO (hojas); texto p.2 dice «Sulfato de Sodio»
DU = {('MN','A'):(58,1504.49,31.4,67.6,21.0,22.3,43.4),('HG','A'):(59,1510.85,0.5,1.2,0.3,0.4,0.7),('INT','A'):(60,1501.38,35.3,29.5,23.6,9.7,33.4),
      ('EXO','A'):(61,1505.55,3.9,9.9,2.6,3.3,5.9),('MN','B'):(62,1504.33,53.1,43.1,35.6,14.2,49.8),('HG','B'):(63,1505.42,0.5,0.8,0.4,0.3,0.6),
      ('INT','B'):(64,1508.5,16.0,23.7,10.7,7.8,18.6),('EXO','B'):(65,1510.65,5.1,10.0,3.4,3.3,6.7)}
for (li,fa),(pg,pi,l1,l2,c1,c2,tot) in DU.items():
    det=(f'Sulfato de MAGNESIO (título de la hoja); solo se ensayó la gradación 2 (1½"-¾", {pi} g): pérdida 1½"-1" = {l1} %, 1"-¾" = {l2} %;'
         f' corregidas {c1} % + {c2} %; la hoja cita el límite de 18 % (ASTM C33)')
    nota='El texto p.2 dice «Inalterabilidad en Sulfato de Sodio (ASTM C88)»; las 8 hojas dicen sulfato de magnesio.'
    if fa=='B': nota+=' Fecha de la hoja (10.09.09) anterior al muestreo de la Fase B (22-23/09/2009).'
    add(li,fa,'Durabilidad (inalterabilidad)','ASTM C88 / NTP 400.016','Pérdida corregida total',tot,'%',1,'única',det,'10/09/2009',f'{pg};8',nota)
# --- Gs y absorción C127 (p.48, 01.12.09) y D854 (p.49)
C127 = {('HG','A'):(2.737,2.743,2.755,0.24),('INT','A'):(2.461,2.502,2.566,1.66),('EXO','A'):(3.212,3.259,3.368,1.44),('MN','A'):(2.717,2.727,2.743,0.34),
        ('HG','B'):(2.740,2.744,2.749,0.12),('INT','B'):(2.647,2.704,2.808,2.17),('EXO','B'):(3.102,3.142,3.233,1.30),('MN','B'):(2.725,2.734,2.750,0.33)}
D854 = {('HG','A'):2.791,('INT','A'):2.674,('EXO','A'):3.484,('MN','A'):2.763,('HG','B'):2.802,('INT','B'):2.742,('EXO','B'):3.338,('MN','B'):2.747}
for k,(b,s,a,ab) in C127.items():
    li,fa=k
    add(li,fa,'Gravedad específica agregado grueso','ASTM C127 / NTP 400.021','Gs bulk (PEM)',b,'-',1,'única','','01/12/2009','48')
    add(li,fa,'Gravedad específica agregado grueso','ASTM C127 / NTP 400.021','Gs SSS',s,'-',1,'única','','01/12/2009','48')
    add(li,fa,'Gravedad específica agregado grueso','ASTM C127 / NTP 400.021','Gs aparente (PEA)',a,'-',1,'única','','01/12/2009','48')
    add(li,fa,'Absorción','ASTM C127 / NTP 400.021','Absorción',ab,'%',1,'única','','01/12/2009','48')
    t2=T2[k][3]
    nota = '' if abs(t2-b)<0.0005 else f'DISCREPANCIA: Tabla 2 da Gs grueso {t2}; la hoja C127 da bulk {b} (ni SSS ni aparente coinciden).'
    add(li,fa,'Gravedad específica agregado grueso','Tabla 2','Gs material grueso (Tabla 2)',t2,'-',1,'resumen','','','8',nota)
    add(li,fa,'Gravedad específica de sólidos','ASTM D854','Gs (fracción fina; fracción no especificada)',D854[k],'-',1,'única','picnómetro; muestra seca 30-80 g','','49')
    add(li,fa,'Gravedad específica de sólidos','Tabla 2','Gs material fino (Tabla 2)',T2[k][4],'-',1,'resumen','','','8')
# --- Densidad in situ ASTM D5030 (reemplazo de agua)
DI = {('MN','A'):(35,'02/09/2009',1249.1,2.4,1220,571.7,2.185,2.135),('HG','A'):(36,'02/09/2009',1460.1,1.44,1439,710.6,2.055,2.026),
      ('INT','A'):(37,'02/09/2009',1357.2,3.5,1311,702.9,1.931,1.865),('EXO','A'):(38,'02/09/2009',1743.7,3.4,1687,742.1,2.350,2.273),
      ('MN','B'):(39,'25/09/2009',837.2,2.3,818,380.5,2.200,2.151),('HG','B'):(40,'25/09/2009',1053,1.20,1041,487,2.162,2.137),
      ('INT','B'):(41,'25/09/2009',1569.6,2.0,1539,762,2.060,2.019),('EXO','B'):(42,'25/09/2009',1047,2.6,1020,433,2.418,2.357)}
for (li,fa),(pg,fe,ph,w,ps,vol,gh,gd) in DI.items():
    det=f'«Location: Parte baja chancadora secundaria»; «Lift: Material Chancado Fase {fa}»; peso húmedo {ph} kg, w={w} %, peso seco {ps} kg, volumen de agua {vol} L'
    nota='La hoja rotula la Fase A como «Material Chancado Fase A», en contradicción con p.1 (Fase A = material original del tajo).' if fa=='A' else ''
    add(li,fa,'Densidad in situ (reemplazo de agua)','ASTM D5030-89','Densidad húmeda',gh,'t/m³',1,'única',det,fe,f'{pg};8',nota)
    add(li,fa,'Densidad in situ (reemplazo de agua)','ASTM D5030-89','Densidad seca',gd,'t/m³',1,'única',det,fe,f'{pg};8',nota)
# --- Densidad máxima y mínima (ASTM D4253/4254), fracción < 5/8"
DM = {('EXO','A'):(43,2.175,2.621),('MN','B'):(44,1.821,2.236),('HG','B'):(45,1.861,2.308),('INT','B'):(46,1.833,2.237),('EXO','B'):(47,2.161,2.647)}
for (li,fa),(pg,mi,ma) in DM.items():
    add(li,fa,'Densidad mínima','ASTM D4254','γd mínima (promedio de 3)',mi,'g/cm³',3,'promedio','material preparado, pasante malla 5/8"','18/12/2009',str(pg))
    add(li,fa,'Densidad máxima','ASTM D4253','γd máxima (promedio de 3)',ma,'g/cm³',3,'promedio','material preparado, pasante malla 5/8"','18/12/2009',str(pg))
# --- Permeabilidad pared flexible ASTM D5084 método C
PE = {('INT','A'):(157,'2.5E-06','03/11/2009','<5/8"; γd 1.863→1.875; σ\'=20 kPa; B=0.99'),('HG','A'):(158,'3.3E-06','03/11/2009','<5/8"; γd 2.026→2.037; σ\'=20 kPa; B=0.96'),
      ('INT','B'):(159,'2.2E-06','18/03/2010','γd 2.011→2.017; H=10.5 cm; σ\'=20 kPa; B=0.96'),('HG','B'):(160,'2.6E-06','18/03/2010','γd 2.136→2.163; H=10.5 cm; σ\'=20 kPa; B=0.98')}
for (li,fa),(pg,k,fe,det) in PE.items():
    nota = 'DISCREPANCIA: Tabla 2 da 3.20E-06 m/s; la hoja da 3.3E-06 (promedio de las 4 últimas lecturas).' if (li,fa)==('HG','A') else ''
    if fa=='B': nota += ' La Tabla 2 rotula la unidad de la Fase B como cm/s; la hoja da m/s.'
    add(li,fa,'Permeabilidad pared flexible','ASTM D5084-03 método C','k20',k,'m/s',1,'única',det,fe,f'{pg};8',nota.strip())
out = os.path.join(base,'verificado','indices_roca_Golder2010.csv')
with open(out,'w',newline='',encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print('filas', len(rows))
