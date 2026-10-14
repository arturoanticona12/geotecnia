# -*- coding: utf-8 -*-
"""Construye Golder_2010_ROM_verificado.csv a partir del CSV extraído y de la transcripción verificada.
uso: python build_2010_cu.py <dir_datos_antamina>
"""
import sys, os, json, math
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from datos_transcritos_2010 import GOLDER_CU, VECTOR_HDR, VECTOR_SET, VECTOR_EXO, MOHR_GOLDER, VECTOR_ENV

base = sys.argv[1]
here = os.path.dirname(os.path.abspath(__file__))
src = os.path.join(base, 'extraido', 'Golder_2010_ROM.csv')
dst = os.path.join(base, 'verificado', 'Golder_2010_ROM_verificado.csv')
df = pd.read_csv(src)
orig = df.copy()

# curvas Vector: MN/HG/INT de la capa de texto (vector_curvas.json), EXO de la imagen
vj = json.load(open(os.path.join(here, 'vector_curvas.json')))
curvas = {}
for p, rows in vj.items():
    if rows:
        curvas[int(p)] = [(r[0], r[1], r[2], r[3], r[4]) for r in rows]
for p, rows in VECTOR_EXO.items():
    curvas[p] = rows
for p, rows in curvas.items():
    for r in rows:
        assert abs(r[4] - r[3] - r[1]) < 0.06, (p, r)
        assert abs((VECTOR_HDR[p][11] - r[3]) - r[2]) < 0.06, (p, r)  # s3c - s3' = u

PICO_VECTOR = {161: 1.5, 162: 1.0, 163: 1.0, 167: 1.25, 168: 1.0, 169: 0.5,
               173: 1.75, 174: 1.25, 175: 0.75, 179: 1.25, 180: 1.0, 181: 1.0}
NOTA_PICO = {
    173: 'El máximo numérico del desviador es a εa=1.75 %; el punto marcado como «pico» en la trayectoria de Vector (p.177) parece estar en εa≈2.5 % (q=357.3 kPa).',
    181: 'La curva NO tiene pico: el desviador crece hasta el final (496.8 kPa a 14 %). Vector marcó el punto a εa=1.0 % (verificado en la trayectoria p.183); se conserva como «pico Vector» solo por trazabilidad.',
    168: 'Pico local a εa=1.0 %; después el desviador vuelve a crecer y el máximo absoluto es al 14 %.',
    169: 'Pico local a εa=0.5 %; después el desviador vuelve a crecer y el máximo absoluto es al 14 %.',
    179: 'Pico local a εa=1.25 %; después el desviador vuelve a crecer y el máximo absoluto es al 14 %.',
    180: 'Pico local a εa=1.0 %; después el desviador vuelve a crecer y el máximo absoluto es al 14 %.',
}
VECTOR_PAGES = [161, 162, 163, 167, 168, 169, 173, 174, 175, 179, 180, 181]

newcols = ['sigma3c_kPa', 'sigma3f_kPa', 'sigma1f_kPa',
           'maxdev_eps_pct', 'maxdev_sigma3f_kPa', 'maxdev_sigma1f_kPa', 'maxdev_q_kPa', 'maxdev_u_kPa',
           'maxobl_eps_pct', 'maxobl_sigma3f_kPa', 'maxobl_sigma1f_kPa', 'maxobl_q_kPa', 'maxobl_u_kPa', 'maxobl_ratio',
           'B_valor', 'contrapresion_kPa', 'velocidad_pct_min', 'gamma_d_post_consol_kNm3', 'e_post_consol', 'S_final_pct',
           'e0_Gs_usado', 'verificacion_2026']
for c in newcols:
    df[c] = pd.NA
df['verificacion_2026'] = df['verificacion_2026'].astype(object)
for c in ['B_valor', 'e0_Gs_usado', 'contrapresion_kPa', 'maxobl_ratio']:
    df[c] = df[c].astype(object)

log = []  # discrepancias: (fila, ensayo_id, columna, anterior, correcto, pagina, razon)

def setv(i, col, val, pag, razon, tol=0.051):
    old = df.at[i, col]
    changed = False
    try:
        if pd.isna(old) and not (isinstance(val, float) and math.isnan(val)):
            changed = True
        elif isinstance(val, (int, float)) and abs(float(old) - float(val)) > tol:
            changed = True
        elif isinstance(val, str) and str(old) != val:
            changed = True
    except Exception:
        changed = str(old) != str(val)
    if changed:
        log.append((i, df.at[i, 'ensayo_id'], col, old, val, pag, razon))
    df.at[i, col] = val

i = 0
for sid, s in GOLDER_CU.items():
    for k, t in enumerate(s['ensayos']):
        (s3c, H0, D0, w0, gd0, e0, S0, wf, gdf, ef, Sf, rate, eps, s1t, s1e, s3t, s3e) = t
        assert df.at[i, 'set_id'] == sid and abs(df.at[i, 'sigma3_kPa'] - s3c) < 0.5, (i, sid)
        pag = s['pag']
        q = s1e - s3e
        u = s3t - s3e
        note_q = ''
        if abs((s1t - s3t) - q) > 0.5:
            note_q = f' En la hoja σ1−σ3 (totales) = {s1t - s3t} kPa y σ1\'−σ3\' = {q} kPa (diferencia de redondeo de la hoja); se adopta el valor efectivo.'
        df.at[i, 'sigma3c_kPa'] = s3c
        df.at[i, 'sigma3f_kPa'] = s3e
        df.at[i, 'sigma1f_kPa'] = s1e
        setv(i, 'sigma3_kPa', s3e, pag, "sigma3_kPa contenía σ'3 de consolidación mezclado con σ'1 en la falla; ahora es σ'3 en la falla (la consolidación pasa a sigma3c_kPa)")
        setv(i, 'sigma1_kPa', s1e, pag, "σ'1 en la falla leído en la hoja")
        setv(i, 'q_kPa', q, pag, "q = σ'1f − σ'3f con los valores impresos en la hoja" + note_q)
        setv(i, 'q_falla_und_kPa', q, pag, "q = σ'1f − σ'3f con los valores impresos en la hoja")
        setv(i, 'u_falla_kPa', u, pag, "Δu en la falla = σ3 − σ'3 impresos en la hoja (exceso sobre la contrapresión)")
        setv(i, 'p_falla_kPa', round((s1e + 2 * s3e) / 3, 1), pag, "p' = (σ'1f + 2σ'3f)/3 recalculado con σ'3f impreso")
        setv(i, 'eps_axial_falla_pct', eps, pag, 'εa en la falla de la hoja')
        setv(i, 'gamma_d_kNm3', round(gd0 * 9.81, 2), pag, 'γd inicial de la hoja × 9.81')
        setv(i, 'e0', e0, pag, 'e0 inicial de la hoja')
        setv(i, 'Gs', s['Gs'], pag, 'G. Específica Promedio de la hoja')
        setv(i, 'w_pct', w0, pag, 'humedad inicial de la hoja')
        setv(i, 'diametro_mm', round(D0 * 10, 1), pag, 'diámetro inicial de la hoja')
        setv(i, 'altura_mm', round(H0 * 10, 1), pag, 'altura inicial de la hoja')
        for c in ['maxdev_eps_pct', 'maxdev_sigma3f_kPa', 'maxdev_sigma1f_kPa', 'maxdev_q_kPa', 'maxdev_u_kPa']:
            df.at[i, c] = {'maxdev_eps_pct': eps, 'maxdev_sigma3f_kPa': s3e, 'maxdev_sigma1f_kPa': s1e,
                           'maxdev_q_kPa': q, 'maxdev_u_kPa': u}[c]
        for c in ['maxobl_eps_pct', 'maxobl_sigma3f_kPa', 'maxobl_sigma1f_kPa', 'maxobl_q_kPa', 'maxobl_u_kPa', 'maxobl_ratio']:
            df.at[i, c] = 'no informado'
        df.at[i, 'B_valor'] = 'no informado'
        df.at[i, 'contrapresion_kPa'] = 'no informado'
        df.at[i, 'velocidad_pct_min'] = rate
        df.at[i, 'gamma_d_post_consol_kNm3'] = round(gdf * 9.81, 2)
        df.at[i, 'e_post_consol'] = ef
        df.at[i, 'S_final_pct'] = Sf
        df.at[i, 'e0_Gs_usado'] = f"{s['Gs']} (D854, «G. Específica Promedio» de la hoja y p.49); e0 recalculado = {s['Gs'] / gd0 - 1:.3f}"
        df.at[i, 'criterio_falla'] = 'Esfuerzo desviador máximo (criterio impreso en la hoja Golder)'
        df.at[i, 'verificado_imagen'] = 'sí'
        df.at[i, 'pagina'] = f"{pag};{s['mohr']};8;{9 if '-A-' in sid else 10};49"
        extra = (f" VERIFICACIÓN 2026-10-06 (imagen p.{pag}): σ'3c={s3c}; en la falla σ1={s1t}, σ1'={s1e}, σ3={s3t}, σ3'={s3e} kPa"
                 f" (impresos); Δu={u} kPa; q=σ'1−σ'3={q} kPa.{note_q} Tras consolidar: γd={gdf} g/cm3, e={ef}, S={Sf} %."
                 " La hoja Golder no tabula la curva (solo gráficos): máxima oblicuidad no informada; el estado de «máximo desviador» es el impreso."
                 f" {s['obs']}.")
        n = str(df.at[i, 'notas'])
        n = n.replace("sigma3_kPa = σ'3 de consolidación; sigma1_kPa = σ'1 en la falla; q_kPa = σ1−σ3 = σ'1−σ'3.",
                      "[Convención corregida en la verificación: sigma3_kPa y sigma1_kPa son ahora σ'3 y σ'1 en la falla; σ'3 de consolidación en sigma3c_kPa.]")
        import re
        n = re.sub(r"σ3'f=\d+ kPa", f"σ3'f={s3e} kPa", n)
        n = n.replace('u_falla = exceso de presión de poros en la falla = σ3c − σ\'3f', 'u_falla = Δu en la falla = σ3 − σ\'3 impresos')
        df.at[i, 'notas'] = n + extra
        df.at[i, 'verificacion_2026'] = 'verificado en imagen; esfuerzos separados (consolidación / falla)'
        i += 1

for p in VECTOR_PAGES:
    sid = VECTOR_SET[p]
    H0, Hf, D0, Df, w0, wf, gd0, gdf, B, cel, bp, s3c = VECTOR_HDR[p]
    assert df.at[i, 'set_id'] == sid and abs(df.at[i, 'sigma3_kPa'] - s3c) < 0.5, (i, sid, p)
    rows = curvas[p]
    pk = [r for r in rows if abs(r[0] - PICO_VECTOR[p]) < 1e-6][0]
    md = max(rows, key=lambda r: r[1])
    mo = max(rows[1:], key=lambda r: r[4] / r[3])
    eps, q, u, s3e, s1e = pk
    setv(i, 'sigma3_kPa', s3e, p, "sigma3_kPa contenía σ'3 de consolidación; ahora σ'3 en el pico de Vector")
    setv(i, 'sigma1_kPa', s1e, p, "σ'1 en el pico (tabla de la hoja Vector)")
    setv(i, 'q_kPa', q, p, "q = σ'1 − σ'3 en el pico (tabla de la hoja Vector)")
    setv(i, 'q_falla_und_kPa', q, p, 'q = σ1−σ3 en el pico')
    setv(i, 'u_falla_kPa', u, p, 'P. poros de la tabla Vector en el pico')
    setv(i, 'p_falla_kPa', round((s1e + 2 * s3e) / 3, 1), p, "p' = (σ'1+2σ'3)/3 recalculado")
    setv(i, 'eps_axial_falla_pct', eps, p, 'εa del pico')
    setv(i, 'gamma_d_kNm3', round(gd0 * 9.81, 2), p, 'γd inicial de la hoja × 9.81')
    setv(i, 'w_pct', w0, p, 'humedad inicial de la hoja')
    setv(i, 'diametro_mm', round(D0 * 10, 1), p, 'diámetro inicial')
    setv(i, 'altura_mm', round(H0 * 10, 1), p, 'altura inicial')
    Gs = df.at[i, 'Gs']
    setv(i, 'e0', round(Gs / gd0 - 1, 3), p, 'e0 recalculado con Gs D854 de Golder (Vector no informa Gs ni e0)', tol=0.0015)
    df.at[i, 'sigma3c_kPa'] = s3c
    df.at[i, 'sigma3f_kPa'] = s3e
    df.at[i, 'sigma1f_kPa'] = s1e
    df.at[i, 'maxdev_eps_pct'], df.at[i, 'maxdev_q_kPa'], df.at[i, 'maxdev_u_kPa'], df.at[i, 'maxdev_sigma3f_kPa'], df.at[i, 'maxdev_sigma1f_kPa'] = md
    df.at[i, 'maxobl_eps_pct'], df.at[i, 'maxobl_q_kPa'], df.at[i, 'maxobl_u_kPa'], df.at[i, 'maxobl_sigma3f_kPa'], df.at[i, 'maxobl_sigma1f_kPa'] = mo
    df.at[i, 'maxobl_ratio'] = round(mo[4] / mo[3], 3)
    df.at[i, 'B_valor'] = B
    df.at[i, 'contrapresion_kPa'] = bp
    df.at[i, 'velocidad_pct_min'] = round(0.01 * 2.54 / H0 * 100, 3)
    df.at[i, 'gamma_d_post_consol_kNm3'] = round(gdf * 9.81, 2)
    df.at[i, 'e_post_consol'] = round(Gs / gdf - 1, 3)
    df.at[i, 'S_final_pct'] = 'no informado'
    df.at[i, 'e0_Gs_usado'] = f'{Gs} (D854 Golder, p.49; Vector no informa Gs)'
    env = VECTOR_ENV[sid]
    df.at[i, 'criterio_falla'] = 'Pico de esfuerzo desviador (criterio de Vector; primer máximo)' if p != 181 else 'Punto marcado como «pico» por Vector (la curva no tiene pico)'
    df.at[i, 'verificado_imagen'] = 'sí'
    df.at[i, 'pagina'] = f'{p};{env[0]};3;10;49'
    extra = (f" VERIFICACIÓN 2026-10-06 (imagen p.{p}): σ'3c={s3c} kPa, celda {cel} kPa, contrapresión {bp} kPa, B={B}, velocidad 0.01 pulg/min."
             f" Pico Vector εa={eps} %: σ'3={s3e}, σ'1={s1e}, q={q}, Δu={u} kPa. Máximo desviador del ensayo: εa={md[0]} %, q={md[1]} kPa."
             f" Máxima oblicuidad: σ'1/σ'3={mo[4] / mo[3]:.3f} a εa={mo[0]} %. Final de consolidación (Vector): H={Hf} cm, D={Df} cm, γd={gdf} g/cm3, w final={wf} %. ")
    if p in NOTA_PICO:
        extra += NOTA_PICO[p] + ' '
    if sid in ('G2010-B-MN-6in', 'G2010-B-INT-6in'):
        extra += 'Las cabeceras de mármol negro e intrusivo 6" repiten w inicial 4.50 % y w final 8.50/8.84/9.56 % (posible plantilla copiada). '
    n = str(df.at[i, 'notas'])
    df.at[i, 'notas'] = n + extra
    df.at[i, 'verificacion_2026'] = 'verificado en imagen; esfuerzos separados; estados de máximo desviador y máxima oblicuidad de la tabla Vector'
    i += 1

assert i == len(df)
# comprobaciones
for j in range(len(df)):
    assert abs(df.at[j, 'sigma1_kPa'] - df.at[j, 'sigma3_kPa'] - df.at[j, 'q_kPa']) < 0.06, j
    assert abs(df.at[j, 'sigma1f_kPa'] - df.at[j, 'sigma3f_kPa'] - df.at[j, 'q_kPa']) < 0.06, j
os.makedirs(os.path.dirname(dst), exist_ok=True)
df.to_csv(dst, index=False, encoding='utf-8')
n_bad_before = int(((orig.sigma1_kPa - orig.sigma3_kPa - orig.q_kPa).abs() > 0.5).sum())
print('filas', len(df), 'filas con q != sigma1 - sigma3 en el CSV extraído:', n_bad_before)
pd.DataFrame(log, columns=['fila', 'ensayo_id', 'columna', 'valor_anterior', 'valor_correcto', 'pagina', 'razon']).to_csv(
    os.path.join(here, 'log_cambios_2010.csv'), index=False, encoding='utf-8')
print('cambios registrados', len(log))
import collections
print(collections.Counter(c for _, _, c, *_ in log))
