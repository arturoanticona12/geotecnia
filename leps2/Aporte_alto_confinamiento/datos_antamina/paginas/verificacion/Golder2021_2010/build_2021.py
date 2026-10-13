# -*- coding: utf-8 -*-
"""Construye Golder_2021_commingling_verificado.csv. uso: python build_2021.py <dir_datos_antamina>"""
import sys, os, json, re
import pandas as pd
here = os.path.dirname(os.path.abspath(__file__))
base = sys.argv[1]
df = pd.read_csv(os.path.join(base, 'extraido', 'Golder_2021_commingling.csv'))
cur = json.load(open(os.path.join(here, 'g21_curvas.json'), encoding='cp1252'))
est = json.load(open(os.path.join(here, 'g21_estados.json')))
pages = [108,109,110,115,116,117,122,123,124,129,130,131,136,137,138,143,144,145,150,151,152,157,158,159,164,165,166,171,172,173]
# Tabla 8 (p.20-22) verificada en imagen: (w0, gd0, e0, s3, w_antes, gd_antes, e_antes, w_fin, gd_fin, e_fin, qmax)
T8 = [(2.0,2.089,0.32,98,10.1,2.156,0.28,9.1,2.204,0.25,283),(2.0,2.089,0.32,399,9.0,2.193,0.26,7.5,2.267,0.22,1518),
      (2.0,2.087,0.32,1200,7.7,2.263,0.22,5.9,2.361,0.17,4647),(1.6,1.802,0.55,101,10.3,2.163,0.29,9.1,2.163,0.26,596),
      (1.6,1.802,0.55,400,9.1,2.219,0.26,7.8,2.288,0.22,1977),(1.6,1.802,0.55,1203,8.3,2.269,0.23,6.4,2.369,0.18,4658),
      (3.3,1.802,0.58,100,10.0,2.204,0.29,8.9,2.259,0.26,540),(3.3,1.802,0.58,402,9.2,2.249,0.27,7.7,2.323,0.23,1780),
      (3.3,1.802,0.58,1202,8.2,2.306,0.23,6.5,2.396,0.19,4469),(8.1,1.802,0.66,103,11.9,2.197,0.37,10.2,2.279,0.32,434),
      (8.2,1.801,0.67,404,11.0,2.253,0.33,9.4,2.340,0.28,1356),(8.2,1.802,0.67,1202,10.0,2.300,0.30,8.3,2.396,0.25,3863),
      (2.5,1.802,0.55,98,10.1,2.174,0.28,9.0,2.229,0.25,547),(2.5,1.802,0.55,402,9.1,2.222,0.26,7.4,2.309,0.21,1714),
      (2.5,1.802,0.55,1203,8.5,2.254,0.24,6.4,2.365,0.18,4529),(5.0,1.802,0.58,98,10.0,2.209,0.29,8.7,2.273,0.25,493),
      (5.0,1.802,0.58,402,9.3,2.244,0.27,7.6,2.331,0.22,1700),(5.0,1.802,0.58,1200,8.0,2.318,0.23,6.0,2.432,0.17,4461),
      (8.5,1.802,0.67,100,11.8,2.217,0.36,10.4,2.288,0.31,445),(8.5,1.802,0.67,401,10.8,2.264,0.33,9.2,2.345,0.28,1470),
      (8.5,1.802,0.67,1204,9.7,2.321,0.30,7.8,2.425,0.24,4170),(1.6,1.802,0.55,102,10.1,2.171,0.29,9.8,2.228,0.25,614),
      (1.6,1.802,0.55,409,9.2,2.218,0.26,7.7,2.294,0.22,1818),(1.6,1.802,0.55,1202,8.6,2.247,0.24,6.7,2.348,0.19,4670),
      (3.3,1.802,0.58,98,10.1,2.207,0.29,8.9,2.266,0.26,602),(3.3,1.802,0.58,409,9.1,2.252,0.26,7.6,2.331,0.22,1736),
      (3.3,1.802,0.23,1204,8.0,2.316,0.23,6.0,2.428,0.17,4407),(8.1,1.802,0.67,96,12.1,2.197,0.37,10.4,2.281,0.32,437),
      (8.1,1.802,0.67,400,11.1,2.245,0.34,9.2,2.343,0.28,1415),(8.1,1.802,0.67,1206,10.0,2.310,0.30,7.8,2.433,0.23,3751)]
new = ['sigma3c_kPa','sigma3f_kPa','sigma1f_kPa','hoja_maxdev_eps_pct','hoja_maxdev_q_kPa','hoja_maxdev_sigma3f_kPa','hoja_maxdev_sigma1f_kPa',
       'maxobl_eps_pct','maxobl_q_kPa','maxobl_sigma3f_kPa','maxobl_sigma1f_kPa','maxobl_ratio','eps_final_pct','q_final_kPa','hay_pico',
       'B_valor','celda_kPa','contrapresion_kPa','velocidad_pct_min','gamma_d_post_consol_kNm3','e_post_consol','Gs_origen','e0_recalculado','verificacion_2026']
for c in new:
    df[c] = pd.Series([pd.NA]*len(df), dtype=object)
log = []
for k, p in enumerate(pages):
    i = k
    h = cur[str(p)]['h']; e = est[str(p)]
    t = T8[k]
    assert abs(df.at[i,'sigma3_kPa'] - t[3]) < 0.5 and abs(df.at[i,'q_kPa'] - t[10]) < 0.5, (i, p)
    assert abs(df.at[i,'e0'] - t[2]) < 0.006 or (k == 26), (i, df.at[i,'e0'], t[2])
    md, mo, last = e['maxq'], e['maxobl'], e['last']
    assert abs(df.at[i,'eps_axial_falla_pct'] - md[0]) < 0.006, (i, p)
    rows = [r for r in cur[str(p)]['rows'] if abs(r[4]-r[3]-r[1]) <= 0.06 and r[3] > 0]
    df.at[i,'sigma3c_kPa'] = t[3]
    df.at[i,'sigma3f_kPa'] = df.at[i,'sigma3_kPa']; df.at[i,'sigma1f_kPa'] = df.at[i,'sigma1_kPa']
    df.at[i,'hoja_maxdev_eps_pct'], df.at[i,'hoja_maxdev_q_kPa'], df.at[i,'hoja_maxdev_sigma3f_kPa'], df.at[i,'hoja_maxdev_sigma1f_kPa'] = md[0], md[1], md[3], md[4]
    df.at[i,'maxobl_eps_pct'], df.at[i,'maxobl_q_kPa'], df.at[i,'maxobl_sigma3f_kPa'], df.at[i,'maxobl_sigma1f_kPa'] = mo[0], mo[1], mo[3], mo[4]
    df.at[i,'maxobl_ratio'] = round(mo[4]/mo[3], 3)
    df.at[i,'eps_final_pct'] = last[0]; df.at[i,'q_final_kPa'] = last[1]
    drop = (md[1]-last[1])/md[1]*100
    df.at[i,'hay_pico'] = ('sí (q final {:.1f} % menor que el máximo)'.format(drop) if (last[0]-md[0] > 1.0 and drop > 2.0)
                           else 'no (máximo en la última lectura o caída < 2 %)')
    df.at[i,'B_valor'] = h['B']; df.at[i,'celda_kPa'] = h['celda']; df.at[i,'contrapresion_kPa'] = h['contra']
    df.at[i,'velocidad_pct_min'] = 0.111
    df.at[i,'gamma_d_post_consol_kNm3'] = round(t[5]*9.81, 2); df.at[i,'e_post_consol'] = t[6]
    Gs = df.at[i,'Gs']
    df.at[i,'Gs_origen'] = (f'«G. Específica (Promedio)» impresa en la hoja triaxial p.{p}; no coincide con la Tabla 5 '
                            '(finos D854 ni gruesos C127); el informe no explica cómo se obtuvo')
    df.at[i,'e0_recalculado'] = round(Gs/t[1]-1, 3)
    dif = md[1]-t[10]
    df.at[i,'verificacion_2026'] = (f'Tabla 8 (p.20-22) y hoja p.{p} verificadas en imagen. q_kPa = Tabla 8 ({t[10]}); máximo de la hoja {md[1]:.2f} kPa a εa={md[0]} % '
                                    f'(diferencia {dif:+.1f} kPa). Máx. oblicuidad {mo[4]/mo[3]:.3f} a εa={mo[0]} %. B={h["B"]}, celda {h["celda"]} kPa, contrapresión {h["contra"]} kPa.')
# permeabilidad
K = {30:(179,'5.6E-06','5.60E-06',1.802,2.219),31:(180,'8.9E-07','8.90E-06',1.801,2.253),32:(181,'8.1E-06','8.10E-06',1.802,2.222),
     33:(182,'1.4E-06','1.40E-06',1.802,2.264),34:(183,'6.7E-06','6.70E-06',1.802,2.218),35:(184,'2.5E-06','2.50E-06',1.802,2.245)}
for i,(p,kh,kt,gd0,gdf) in K.items():
    df.at[i,'sigma3c_kPa'] = 399
    df.at[i,'B_valor'] = '≥0.99' if p in (179,180,183,184) else '≥0.98'
    df.at[i,'celda_kPa'] = 661; df.at[i,'contrapresion_kPa'] = 262
    df.at[i,'gamma_d_post_consol_kNm3'] = round(gdf*9.81, 2)
    df.at[i,'Gs_origen'] = 'Gs de la hoja triaxial del mismo material (la hoja de permeabilidad no da Gs)'
    df.at[i,'e0_recalculado'] = round(df.at[i,'Gs']/gd0-1, 3)
    df.at[i,'verificacion_2026'] = f'Hoja p.{p} verificada en imagen: k20 = {kh} m/s; Tabla 9 (p.23) = {kt} m/s.' + (' DISCREPANCIA: se adopta la hoja.' if kh != kt.replace('0E','E') and p == 180 else '')
df.to_csv(os.path.join(base, 'verificado', 'Golder_2021_commingling_verificado.csv'), index=False, encoding='utf-8')
print('ok', len(df))
for i in range(30):
    print(i, df.at[i,'ensayo_id'], df.at[i,'B_valor'], re.findall(r'B=([\d.]+)', str(df.at[i,'notas']))[:1], df.at[i,'hay_pico'], df.at[i,'e0'], df.at[i,'e0_recalculado'])

