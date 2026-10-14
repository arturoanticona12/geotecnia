"""Genera los entregables verificados de WSP 2024 e IDIEM 2025.
Uso: python build_verificado.py <carpeta datos_antamina>"""
import sys, os, json
import pandas as pd

base = sys.argv[1]
ext = os.path.join(base, 'extraido')
out = os.path.join(base, 'verificado')
os.makedirs(out, exist_ok=True)
VER = '[VERIFICACIÓN 2026-10-06] '

# ---------------------------------------------------------------- WSP 2024
w = pd.read_csv(os.path.join(ext, 'WSP_2024_codisposicion.csv'))
w0 = w.copy()
rel_ef = {'WSP24_C1': (22, 13.1, 59.7, '6.6:1'), 'WSP24_C2': (18, 10.7, 59.7, '8.3:1'), 'WSP24_C3': (15, 9.0, 59.7, '10.2:1')}
pg_graf = {'WSP24_C1': 'p.267-268', 'WSP24_C2': 'p.142-143', 'WSP24_C3': 'p.231-232'}
for i, r in w.iterrows():
    mix = r.set_id.rsplit('_', 1)[0]
    # 1) escalamiento: Dmax 10" es de la muestra recibida en laboratorio, no granulometría de terreno
    w.at[i, 'escalamiento'] = ('truncado (scalping) a 4" (corte definido por el cliente, IDIEM p.108); Dmax de la muestra recibida '
                               'en laboratorio 10" (IDIEM-A p.93, 46 191 kg en 5 maxisacos); granulometría de terreno no informada')
    if mix in rel_ef:
        nom, ef, p34, ratio = rel_ef[mix]
        # 2) contenido real de relave
        w.at[i, 'tipo_material'] = (f'Mezcla co-disposición: desmonte (clase no indicada) + {ef} % relave en masa seca total '
                                    f'(nominal del informe {nom} % aplicado solo a la fracción < 3/4")')
        w.at[i, 'litologia_proporcion'] = (f'Nominal (informe): intrusivo {100-nom} % / relave {nom} %, aplicado a la fracción < 3/4" '
                                           f'({p34} % de la masa); efectivo en masa seca total: desmonte intrusivo {100-ef:.1f} %, '
                                           f'relave {ef} % (intrusivo:relave ≈ {ratio}). Dentro del desmonte, por conteo de 38 fragmentos '
                                           f'de carga puntual (no por masa): tonalita 31 (82 %), caliza 7 (18 %)')
    else:
        w.at[i, 'litologia_proporcion'] = ('Intrusivo 100 % (sin relave). Por conteo de 38 fragmentos de carga puntual (no por masa ni '
                                           'petrografía): tonalita 31 (82 %), caliza 7 (18 %)')
    n = r.notas
    n = n.replace('rango 64.0–143.1 MPa, Tabla 6 p.12', 'rango 61.1–143.1 MPa según Tabla 6 p.12; el texto de p.12 dice 64.0 por error')
    if mix in rel_ef:
        nom, ef, p34, ratio = rel_ef[mix]
        n = n.replace('; duda abierta', '')
        n += (f'; {VER}contenido de relave RESUELTO: IDIEM indica "cortar el material ... en 4” y agregar un {nom}% de Relave integral ... '
              f'se trabaja el material integral bajo ¾”" ({pg_graf[mix]}); la curva de montaje (Gráfico 1) coincide con el desmonte '
              f'sobre 3/4" y se reproduce con {nom} % de relave solo en la fracción < 3/4" ⇒ relave efectivo {ef} % de la masa seca total. '
              'Confirmado también por: Gs global de Tabla 5 (se reproduce con pasante N°4 ≈ 34/33/32 %, no con 43/40/38 %) y por las '
              'granulometrías post-ensayo (C1: 33.6–37.1 % pasante N°4 a 490 kPa, imposible si el inicial fuera 42.8 %)')
    n += (f'; {VER}Gs global = valor del informe (Tabla 5 p.12, "ponderado proporcionado por el cliente" en hojas IDIEM): combina '
          'Gs aparente > N°4 = 2.87 (promedio de 8 muestras WSP Lima, ASTM C127, muestreadas por Antamina en feb-mar 2024, '
          'no del lote IDIEM recibido el 15-11-2023; Gs base seca media 2.78) con Gs < N°4 de IDIEM (C1 3.07 p.271/339; C4 2.80 '
          'p.110; C2 2.97 y C3 2.94 solo en Tabla 5, sin hoja en el anexo). e0 = Gs/ρd − 1 con ρd nominal de confección (hoja IDIEM); '
          'con Gs base seca el e0 bajaría ≈0.02-0.03. UCS, Los Ángeles y Gs>N°4 son de muestras WSP Lima (Tajo Mina, '
          'CD-ECU-001/CD-ERD-001/CD-EGS-001), no del material ensayado en IDIEM. Convención εv: negativo = compresión '
          '(declarada por IDIEM en hojas de edómetro, p.121: "deformación unitaria positiva indica hinchamiento"). '
          'Drenado: estado de máxima oblicuidad = estado de máximo desviador (σ′3 constante).')
    w.at[i, 'notas'] = n
# Sección B (no drenados): no aplica; se separan σ3c/σ3f/σ1f para homogeneidad
w['sigma3c_kPa'] = w['sigma3_kPa']
w['sigma3f_kPa'] = w['sigma3_kPa']
w['sigma1f_kPa'] = w['sigma1_kPa']
w['estado_max_oblicuidad'] = 'igual al de máximo desviador (CID, σ′3 constante)'
w.to_csv(os.path.join(out, 'WSP_2024_codisposicion_verificado.csv'), index=False, encoding='utf-8')

# ---------------------------------------------------------------- IDIEM 2025
d = pd.read_csv(os.path.join(ext, 'IDIEM_2025.csv'))
for i, r in d.iterrows():
    n = r.notas
    n = n.replace('Pico frágil: q_MIT cae de 8,57 a ~6,0 kgf/cm2 tras ea ≈ 8 %.',
                  'Pico frágil: q_MIT cae de 8,57 (εa 3,98 %) a 6,72 en εa = 8,05 % y a 5,80 al final (εa = 19,09 %) (p. 14).')
    n = n.replace('Humedad de confección 0,00 % (montaje seco, luego saturado con B >= 0,95).',
                  'Humedad de confección 0,00 % según hoja (el informe no describe si el montaje fue seco; luego saturado con B >= 0,95).')
    n += (f' {VER}Gs NO informado en IDIEM 2025 (ni en su anexo; las granulometrías iniciales están en el informe 1.966.314-A, no '
          'incluido). Referencia externa posible: WSP 2024 Codisposal 4 (100 % intrusivo, otro lote recibido el 15-11-2023, '
          'Dmax 4") Gs global = 2.85 (Tabla 5 p.12); recalculado con la curva de este ensayo (pasante N°4 21,2 %) daría 2.855. '
          'e0 condicional (NO del informe) = 2.85/2.10 − 1 = 0.357; tras consolidación 0.344 / 0.301 / 0.234. '
          'IDIEM 2025 (Fase 2-3, lote recibido 12-16 ago 2024, probetas 100×180 cm, Dmax 7", ρd 2,10, w 0 %) COMPLEMENTA y no repite '
          'a WSP 2024 Fase 1 (60×120 cm, Dmax 4", ρd 2,00, w 3 %); la numeración cambia: aquí Codisposal 1 = 100 % intrusivo. '
          'Convención εv: negativo = compresión, coherente con la declarada por IDIEM en edómetros (WSP 2024 p.121). '
          'Drenado: estado de máxima oblicuidad = estado de máximo desviador (verificado en la tabla).')
    d.at[i, 'notas'] = n
d['sigma3c_kPa'] = d['sigma3_kPa']
d['sigma3f_kPa'] = d['sigma3_kPa']
d['sigma1f_kPa'] = d['sigma1_kPa']
d['estado_max_oblicuidad'] = 'igual al de máximo desviador (CID, σ′3 constante)'
d.to_csv(os.path.join(out, 'IDIEM_2025_verificado.csv'), index=False, encoding='utf-8')

# ---------------------------------------------------------------- condiciones
NI = 'no informado'
origen_wsp = ('Desmonte "Desmonte de Mina (Intrusivo)", 46 191 kg en 5 maxisacos, y relave 10 630 kg, recibidos por IDIEM el '
              '15-11-2023 (IDIEM-A p.89); calicata y cota "---"; fase, banco o botadero no informados. Ensayos índice WSP Lima '
              'sobre muestras distintas: "Tajo Mina" / "Material Intrusivo / Tajo Mina", códigos CD-EGS-001, CD-ECU-001, '
              'CD-ERD-001, muestreo Antamina 10-02-2024 a 07-03-2024 (pp.45-82)')
clase = 'no indicada (el informe solo dice "desmonte tipo intrusivo" / "Desmonte de Mina (Intrusivo)", p.8 y p.89)'
lito = ('Intrusivo; detalle por conteo de 38 fragmentos ≥ ~37 mm de carga puntual IDIEM 1.914.482-G (pp.356-362, '
        'descripción visual del laboratorio, sin petrografía): tonalita 31 (82 %), caliza 7 (18 %); tonalita con vetillas de '
        'pirita, sulfuros de Cu, cuarzo, calcita; alteración sericítica, clorítica, local epidota/oxidación/arcillas/zeolitas')
gran_campo = ('no informada para terreno; muestra recibida (IDIEM-A p.93): Dmax 10", 96,2 % pasa 4", 57,4 % pasa 3/4", '
              '25,7 % pasa N°4, 6,6 % pasa N°200; 6,8 % retenido en 3"')
UCS = ('UCS 61,1–143,1 MPa, media 95,2 MPa (7 probetas ~49×107 mm, ASTM D7012 Método C, WSP Lima, Tabla 6 p.12 y pp.61-74; '
       'el texto dice mínimo 64,0 por error); Is50 por hoja 5,48 / 4,36 / 4,11 / 6,16 MPa (IDIEM 1.914.482-G, ASTM D5731, '
       'Tabla 6 p.364, promedios con fragmentos no válidos; solo válidos 5,49 / 4,90 / 3,27 / 6,12); Los Ángeles 21,2–39,9 %, '
       'media 30,4 % (8 muestras, ASTM C535 gradación 1 según fichas pp.75-82; el texto p.13 dice C131); durabilidad no informada; '
       'absorción 0,8–1,6 %, media 1,08 % (ASTM C127, Tabla 3 p.11)')
Bg_m = ('Marsal (1967): suma de diferencias positivas de % retenido inicial vs post (p.35); inicial = curva teórica de montaje '
        '(Gráfico 1); post: probeta secada, tamizado total hasta 1 1/2", cuarteo de 200 kg hasta N°4 y 4×2 kg lavados (IDIEM p.109); '
        'tamices 4", 3", 2", 1 1/2", 1", 3/4", 3/8", N°4, N°10, N°20, N°40, N°60, N°140, N°200')
sets = [
    # set, mezcla, Gs, ρd, gran_lab, dV, ρpost, pag_post, ea_fin, pico_nota, pags, tipo, mezcla_txt
    ('WSP24_C1_MON', 'C1', 2.93, 2.07, 'D10 0,13; D30 2,1; D50 12,0; D60 19,2 mm; Cu 148; Cc 1,8; finos 7,1 %; pasa N°4 34,0 % (digitalizado del Gráfico 1 p.268; recalculado exacto con desmonte p.93 + relave p.355: D30 2,15; Cc 1,87; finos 7,0 %)',
     (10700, 19000, 32200), (2.14, 2.19, 2.28), 'p.339', (19.94, 20.55, 20.85), 'monótona', 'pp.274-281'),
    ('WSP24_C1_CD', 'C1', 2.93, 2.07, 'igual a C1_MON',
     (8200, 11800, 21300), (2.12, 2.14, 2.21), 'p.341', (19.99, 20.55, 20.79), 'carga-descarga (ciclos a εa 2, 5 y 8 %, Tabla 10 p.18)', 'pp.283-326'),
    ('WSP24_C2_MON', 'C2', 2.90, 2.03, 'D10 0,135; D30 2,8; D50 12,2; D60 19,0 mm; Cu 141; Cc 3,1; finos 7,1 %; pasa N°4 32,8 % (digitalizado Gráfico 1 p.143; recalculado exacto: D30 2,88; Cc 3,2; finos 7,0 %)',
     (8500, 16000, 22600), (2.08, 2.13, 2.17), 'p.217', (19.94, 20.29, 20.60), 'monótona', 'pp.148-155'),
    ('WSP24_C2_CD', 'C2', 2.90, 2.03, 'igual a C2_MON',
     (9100, 17400, 26900), (2.09, 2.14, 2.20), 'p.219', (19.45, 20.17, 20.15), 'carga-descarga (ciclos a εa 2, 5 y 8 %, Tabla 10 p.18)', 'pp.157-204'),
    ('WSP24_C3_MON', 'C3', 2.89, 2.05, 'D10 0,14; D30 3,4; D50 12,4; D60 19,0 mm; Cu 137; Cc 4,5; finos 7,1 %; pasa N°4 31,8 % (digitalizado Gráfico 1 p.232; recalculado exacto: D30 3,51; Cc 4,6; finos 6,9 %)',
     (9800, 14300, 27000), (2.11, 2.14, 2.22), 'p.255', (19.96, 20.05, 20.25), 'monótona', 'pp.236-243'),
    ('WSP24_C4_MON', 'C4', 2.85, 2.00, 'D10 0,20; D30 5,59; D50 13,3; D60 19,2 mm; Cu 96; Cc 8,1; finos 6,9 %; pasa N°4 26,7 % (calculado de la tabla p.93 truncada a 4"; verificado)',
     (3100, 17400, 22500), (2.02, 2.11, 2.14), 'p.130', (20.26, 20.70, 20.98), 'monótona', 'pp.111-118'),
]
mix = {'C1': ('Codisposal 1: intrusivo + relave, nominal 3.5:1 (78/22) aplicado a la fracción < 3/4"; relave efectivo 13,1 % de la masa seca total', 3.07, 'IDIEM p.271/339'),
       'C2': ('Codisposal 2: nominal 4.5:1 (82/18) aplicado a la fracción < 3/4"; relave efectivo 10,7 % de la masa seca total', 2.97, 'solo WSP Tabla 5 p.12'),
       'C3': ('Codisposal 3: nominal 5.5:1 (85/15) aplicado a la fracción < 3/4"; relave efectivo 9,0 % de la masa seca total', 2.94, 'solo WSP Tabla 5 p.12'),
       'C4': ('Codisposal 4: 100 % desmonte intrusivo, sin relave', 2.80, 'IDIEM p.110')}
rows = []
for s, m, Gs, rd, gl, dV, rp, pp, ef, tipo, pags in sets:
    e0 = Gs / rd - 1
    rows.append(dict(
        fuente='2024_WSP_Ensayos gran escala mezcla co-disposicion.pdf', set_id=s,
        origen_muestra=origen_wsp, clase_desmonte=clase, material_mezcla=mix[m][0],
        litologia='Intrusivo', litologia_detalle='tonalita (dominante) con fragmentos de caliza',
        litologia_proporcion='por conteo de fragmentos (no masa): tonalita 82 %, caliza 18 % (n = 38); ' + lito,
        Dmax_campo_mm='no informado (Dmax de la muestra recibida 254 mm = 10", IDIEM-A p.93)',
        granulometria_campo=gran_campo,
        densidad_campo=NI,
        escalamiento_metodo='truncado (scalping) en 4" definido por el cliente; "se trabaja el material integral bajo 3/4"" (IDIEM p.108/142/231/267)',
        Dmax_lab_mm=101.6, D_probeta_mm=600, H_probeta_mm=1200, D_sobre_Dmax=round(600 / 101.6, 2),
        granulometria_lab=gl,
        preparacion=('capas en molde rígido con geomembrana de caucho y geotextil; peso y espesor controlados por capa; vacío y '
                     'montaje con grúa (p.16-17, IDIEM p.108); número de capas y energía no informados; ρd objetivo definida por el '
                     f'cliente ({rd:.2f} g/cm³, Tabla 9 p.15); criterio (% Proctor, Dr) no informado; Dr implícita con ρdmín/ρdmáx '
                     'de Tabla 8 (material < 3", no < 4"): C1 58 %, C2 51 %, C3 61 %, C4 50 % (no del informe)'),
        gamma_d_montaje_kNm3=round(rd * 9.81, 2), w_montaje_pct=3.0,
        Gs_valor=Gs,
        Gs_origen=(f'Gs global ponderado del informe (Tabla 5 p.12; hojas IDIEM: "ponderado proporcionado por el cliente"): '
                   f'Gs aparente > N°4 = 2.87 (WSP Lima, ASTM C127, otra muestra) y Gs < N°4 = {mix[m][1]} ({mix[m][2]}, ASTM D854)'),
        e0_recalculado=round(e0, 3),
        saturacion='CO2 + agua hasta flujo constante; B > 0,95 en todas (p.17)',
        contrapresion_kPa=98.1,
        consolidacion=('isotrópica, incrementos continuos hasta σ′3c = 490/980/1960 kPa (5/10/20 kgf/cm²); fin al estabilizar εv; '
                       f'duración no informada; ΔV drenado {dV[0]}/{dV[1]}/{dV[2]} cm³'),
        gamma_d_post_consolidacion_kNm3=f'{rp[0]*9.81:.2f} / {rp[1]*9.81:.2f} / {rp[2]*9.81:.2f} ({rp[0]}/{rp[1]}/{rp[2]} g/cm³, {pp}); e_c = '
                                        + ' / '.join(f'{Gs/x-1:.3f}' for x in rp),
        drenaje_corte=f'drenado, {tipo}',
        velocidad_pct_min='no informado ("--" en hojas; corte a carga controlada)',
        deformacion_final_pct=f'{ef[0]} / {ef[1]} / {ef[2]}',
        criterio_falla_informe='máximo φ′ (pico) por probeta, Fig. 13 p.27; no ajusta envolventes',
        hay_pico='sí (máximo de q); C4 a 980 kPa: máximo al final (εa 20,7 %), límite inferior' if m == 'C4' else 'sí (máximo de q)',
        hay_curva_tabulada=f'sí, εa-εv-p-q en kgf/cm² ({pags})',
        Bg_metodo=Bg_m,
        UCS_Is50_LA_durabilidad_absorcion=UCS,
    ))
pd.DataFrame(rows).to_csv(os.path.join(out, 'condiciones_WSP2024.csv'), index=False, encoding='utf-8')

ci = dict(
    fuente='2025_IDIEM_Triaxiales Gran Escala Codisposal 100 Intrusivo.pdf', set_id='Codisposal 1 (100% Intrusivo)',
    origen_muestra='"Intrusivo" 139 184 kg y "Relave" 64 864 kg, perturbadas, en maxisacos, recibidas el 12, 14 y 16-08-2024 (Tabla 2 p.6); calicata y cota "---"; tajo, fase, banco no informados',
    clase_desmonte='no indicada (solo "Intrusivo", p.3 y p.6)',
    material_mezcla='Codisposal 1 = 100 % intrusivo, sin relave (numeración de Fase 2-3, distinta de WSP 2024)',
    litologia='Intrusivo', litologia_detalle=NI, litologia_proporcion=NI + ' (sin conteo, descripción ni petrografía)',
    Dmax_campo_mm=NI, granulometria_campo=NI + ' (granulometría inicial en informe 1.966.314-A, no incluido)', densidad_campo=NI,
    escalamiento_metodo='truncado: "el cliente ha decidido cortar el material en 7”" (p.8)',
    Dmax_lab_mm=177.8, D_probeta_mm=1000, H_probeta_mm=1800, D_sobre_Dmax=round(1000 / 177.8, 2),
    granulometria_lab='solo gráfico (Gráfico 1 p.8), digitalizado: D10 0,22; D30 17,4; D50 53,9; D60 67,7 mm; Cu 315; Cc 20,8; finos 5,5 %; pasa N°4 21,2 % (verificado en imagen ±0,5 %)',
    preparacion='capas en molde rígido con geomembrana; peso y espesor por capa (p.8); ρd 2,10 g/cm³ definida por el cliente; criterio (% Proctor, Dr) no informado; n.° de capas no informado',
    gamma_d_montaje_kNm3=round(2.10 * 9.81, 2), w_montaje_pct=0.0,
    Gs_valor=NI,
    Gs_origen='no informado en IDIEM 2025; posible referencia externa 2.85 (WSP 2024 Tabla 5, Codisposal 4, otro lote y otra curva)',
    e0_recalculado='no calculable con el informe; condicional con Gs 2.85 (WSP 2024): 0.357',
    saturacion='B ≥ 0,95 (p.8); método no descrito',
    contrapresion_kPa='98,1 / 196,1 / 98,1 (1 / 2 / 1 kgf/cm², pp.10, 16, 22)',
    consolidacion='isotrópica hasta σ′3c = 490/981/1961 kPa (cámara 6/12/21 − contrapresión 1/2/1 kgf/cm²); fin al estabilizar εv; duración no informada; ΔV 16 200/57 500/131 400 cm³',
    gamma_d_post_consolidacion_kNm3='20,80 / 21,48 / 22,66 (2,12/2,19/2,31 g/cm³, Tabla 4 p.29; verificado con ΔV/V0)',
    drenaje_corte='drenado, monótona, carga controlada por escalones de esfuerzo vertical (p.8)',
    velocidad_pct_min='no informado ("---")',
    deformacion_final_pct='19,09 / 15,02 / 16,70',
    criterio_falla_informe='no informa criterio ni φ; tabla p-q (MIT) hasta el final',
    hay_pico='probeta 1 sí (frágil, εa 3,98 %); probetas 2 y 3 meseta (máx. en 12,97 y 11,18 %)',
    hay_curva_tabulada='sí, εa-εv-p-q en kgf/cm² (pp.10-14, 16-20, 22-27)',
    Bg_metodo='no informado (granulometrías post-ensayo pendientes, Tabla 1)',
    UCS_Is50_LA_durabilidad_absorcion=NI + ' en IDIEM 2025 (para el lote de Fase 1 ver WSP 2024; no es el mismo lote)',
)
pd.DataFrame([ci]).to_csv(os.path.join(out, 'condiciones_IDIEM2025.csv'), index=False, encoding='utf-8')

# resumen de cambios para el md
chg = []
for c in w.columns:
    if c in w0.columns:
        k = (w[c].astype(str) != w0[c].astype(str)).sum()
        if k: chg.append((c, int(k)))
print('Cambios WSP:', chg)
print('Filas WSP', len(w), 'IDIEM', len(d))
