import json, os, math, csv
here = os.path.dirname(os.path.abspath(__file__))
outdir = os.path.join(os.path.dirname(os.path.dirname(here)), "extraido")
os.makedirs(outdir, exist_ok=True)
P = json.load(open(os.path.join(here, "triax_parse2.json")))
src = open(os.path.join(here, "check.py"), encoding="utf-8").read()
T8 = eval(src.split("T8 = ")[1].split("\nfor r in P")[0])  # Tabla 8 verificada en imagen (p.20-22)

COLS = ["fuente","anio","autor_informe","laboratorio","set_id","ensayo_id","litologia_informe","litologia","litologia_detalle","litologia_proporcion","alteracion","tipo_material","clase_desmonte","tipo_ensayo","saturado","diametro_mm","altura_mm","Dmax_mm","D10_mm","D30_mm","D50_mm","D60_mm","Cu","Cc","grava_pct","arena_pct","finos_pct","escalamiento","Gs","gamma_d_kNm3","e0","e0_origen","Dr_pct","w_pct","UCS_MPa","sigma3_kPa","sigma1_kPa","q_kPa","criterio_falla","phi_sec_deg","eps_axial_falla_pct","eps_vol_falla_pct","u_falla_kPa","p_falla_kPa","q_falla_und_kPa","Su_kPa","Bg_pct","Br","finos_post_pct","sigma_n_kPa","tau_kPa","pagina","verificado_imagen","notas"]
FUENTE = "2021_Golder_Ensayos de Laboratorio Commingling.pdf"
AUTOR = "Golder Associates Perú (miembro de WSP), informe 101-20110-LTE01220-INF-420-G-0013 Rev. 0 (28/04/2021)"
LAB = "Laboratorio de Mecánica de Suelos de Golder Associates Perú, Lima"
LIT_INF = "Desmonte Tipo A (intrusivo), Tipo B (mármol y hornfels), Tipo C (hornfels); compuesto 0.35 A : 0.15 B : 0.50 C (masa seca)"
LIT_INF_MIX = LIT_INF + "; relave compuesto 0.33 M1 : 0.33 M2A : 0.33 M4B"
LIT_DET = "Tipo B = mármol y hornfels (el informe no separa su reparto); sin subtipos (mármol blanco/negro, skarn, etc.) indicados"
LIT_PROP = "Intrusivo 35 %; Mármol + Hornfels 15 % (Tipo B, reparto no indicado); Hornfels 50 % (proporciones del desmonte, masa seca)"
ESC = "Truncado (scalping): desmonte limitado a partículas < 1\" (100 % pasa 25.4 mm); Dmax de terreno no indicado"
CLASE = "Compuesto de Tipos A, B y C (tipificación geoquímica por potencial de generación de acidez)"
RELAVE = {1: "relave filtrado (~86 % sólidos)", 2: "relave en pasta (~80 % sólidos)", 4: "relave cicloneado (~86 % sólidos; 80 % gruesos / 20 % finos)"}
# set: (set_id, informe, alt, prop, pct_relave, Gs, pag_gran, D10, D30, D50, D60, Cu, Cc, G, S, F, sucs, c_t7, phi_t7, c_lab, phi_lab, pag_env)
S = {
 1: ("G21-DESM-COMP","II0471",None,None,0,2.762,46,0.0778,1.5869,7.3703,10.1146,129.97,3.20,59.5,30.8,9.7,"GP-GM",0,40,0,41,112),
 2: ("G21-ALT1-9:1","II0520",1,"9:1",10,2.793,47,0.0507,0.6621,5.7715,8.7665,172.96,0.99,53.6,33.3,13.1,"GM",84,40,83,40,119),
 3: ("G21-ALT1-4:1","II0521",1,"4:1",20,2.846,48,0.0443,0.2874,4.0365,7.4082,167.06,0.25,47.7,36.4,15.9,"GM",59,40,58,40,126),
 4: ("G21-ALT1-1:1","II0522",1,"1:1",50,3.000,49,0.0208,0.0952,0.2833,0.7395,35.57,0.59,29.8,44.0,26.2,"SM",24,38,22,38,133),
 5: ("G21-ALT2-9:1","II0523",2,"9:1",10,2.789,50,0.0526,0.6079,6.3687,10.6137,201.90,0.66,53.7,33.2,13.1,"GM",53,40,53,40,140),
 6: ("G21-ALT2-4:1","II0524",2,"4:1",20,2.851,51,0.0394,0.2431,3.9094,7.5292,191.11,0.20,47.7,35.5,16.8,"GM",41,40,41,40,147),
 7: ("G21-ALT2-1:1","II0525",2,"1:1",50,3.006,52,0.0215,0.1020,0.3191,1.0164,47.36,0.48,29.9,44.8,25.3,"SM",29,39,29,39,154),
 8: ("G21-ALT4-9:1","II0526",4,"9:1",10,2.793,53,0.0654,0.7774,5.7170,8.5892,131.25,1.08,53.7,34.9,11.4,"GW-GM",62,40,62,40,161),
 9: ("G21-ALT4-4:1","II0527",4,"4:1",20,2.846,54,0.0593,0.3140,4.0732,7.1259,120.18,0.23,47.7,39.6,12.7,"GM",66,39,66,39,168),
 10: ("G21-ALT4-1:1","II0528",4,"1:1",50,3.003,55,0.0449,0.1250,0.3076,0.6814,15.19,0.51,29.8,51.5,18.7,"SM",51,37,51,37,175),
}
T8PAGE = {1: 20, 2: 20, 3: 20, 4: 20, 5: 21, 6: 21, 7: 21, 8: 21, 9: None, 10: 22}

def fmt(x, nd):
    return f"{x:.{nd}f}"

def base(st, prel, alt):
    if alt is None:
        tm = "No indicada (desmonte compuesto; el informe no dice si es ROM, Chancado o Enrocado)"
        li, lp = LIT_INF, LIT_PROP
    else:
        tm = f"Mezcla co-disposición: desmonte de clase no indicada + {prel} % relave"
        li, lp = LIT_INF_MIX, LIT_PROP + f"; la mezcla lleva además {prel} % de relave en masa seca"
    return dict(fuente=FUENTE, anio=2021, autor_informe=AUTOR, laboratorio=LAB, set_id=st[0],
                litologia_informe=li, litologia="Mezcla", litologia_detalle=LIT_DET, litologia_proporcion=lp,
                alteracion="", tipo_material=tm, clase_desmonte=CLASE, saturado="sí", Dmax_mm="25.4",
                D10_mm=st[7], D30_mm=st[8], D50_mm=st[9], D60_mm=st[10], Cu=st[11], Cc=st[12],
                grava_pct=st[13], arena_pct=st[14], finos_pct=st[15], escalamiento=ESC, Gs=st[5],
                Dr_pct="", UCS_MPa="", u_falla_kPa="", p_falla_kPa="", q_falla_und_kPa="", Su_kPa="",
                Bg_pct="", Br="", finos_post_pct="", sigma_n_kPa="", tau_kPa="", verificado_imagen="sí")

rows = []
for r in P:
    s, k = r["set"], r["esp"]
    st = S[s]; t = T8[s][k - 1]
    sid, inf, alt, prop, prel, Gs, gp = st[:7]
    c7, p7, cl, pl, penv = st[17:22]
    w0, rho0, e0, s3, wc, rc, ec, wf, rf, ef, q = t
    phis = math.degrees(math.asin(q / (q + 2 * s3)))
    e0v = e0
    n = []
    n.append(f"CID (ASTM D7181) en celda de 6\"; remoldeado a ρd≈{rho0} g/cm³ y w={w0} %; saturado por contrapresión (B={r['B']}; celda {r['celda']:.0f} kPa; contrapresión {r['contra']:.0f} kPa); t90={r['t90']} min; 0.111 %/min; corrección por membrana.")
    if alt is not None:
        n.append(f"Alternativa {alt} ({RELAVE[alt]}), desmonte:relave {prop} en masa seca ({prel} % relave).")
    n.append(f"Tras consolidación (Tabla 8): w={wc} %, ρd={rc} g/cm³, e={ec}. Final de corte (Tabla 8): w={wf} %, ρd={rf} g/cm³, e={ef}.")
    n.append(f"q_kPa = máximo desviador de la Tabla 8; en la hoja de laboratorio el máximo es {r['lab_qmax']:.1f} kPa a εa={r['lab_eps']} % (σ3'={r['lab_s3p']:.1f}; σ1'={r['lab_s1p']:.1f} kPa); εa y εv salen de esa fila.")
    if r["at_end"]:
        n.append(f"El máximo coincide con la última lectura (εa≈{r['eps_end']} %): sin pico, sigue endureciendo al terminar el ensayo.")
    n.append(f"La hoja dice 'Criterio de falla: Esfuerzo Desv. Máximo' pero da σ1'={r['fall_s1p']:.0f} y σ3={r['fall_s3']:.0f} kPa a εa={r['eps_f']} %, que no es el máximo de su tabla; los círculos de Mohr del laboratorio usan esos valores.")
    n.append("εv con la convención del informe: negativo = contracción, positivo = dilatación.")
    n.append(f"φsec calculado (c=0) con q de Tabla 8: {phis:.1f}°. Envolvente del set: Tabla 7 (p.19) c={c7} kPa, φ={p7}°; hoja de laboratorio (p.{penv}) c={cl} kPa, φ={pl}°.")
    n.append(f"Gs = 'G. Específica Promedio' de la hoja triaxial; SUCS {st[16]}; no plástico. γd y e0 = estado remoldeado inicial (antes de saturar).")
    n.append("Clase ROM/Chancado/Enrocado no indicada en el informe; A/B/C es tipificación geoquímica. Alteración no indicada.")
    if s == 9 and k == 3:
        e0v = 0.58
        n.append("e0: la Tabla 8 (p.22) dice 0.23 (error tipográfico); la hoja p.166 da 0.58 y Gs/ρd−1 = 2.846/1.802−1 = 0.58; se adopta 0.58.")
    if s == 6 and k == 3:
        n.append("Ensayo terminado a εa=13.85 % (las 4 últimas filas de la hoja repiten esa lectura en rojo).")
    if s == 10 and k == 2:
        n.append("σ3' bajó a 383–396 kPa al final del corte (p.172); σ3' de 'falla' en la hoja = 379 kPa.")
    if s == 2 and k == 1:
        n.append("Tabla 8 da ρd antes del corte 2.163 g/cm³, igual al final de corte (posible error de transcripción; la hoja p.115 da 2.16 tras consolidación y 2.252 al final del corte).")
    if s == 1:
        n.append("Los valores de 'Etapa final de corte' de la Tabla 8 no coinciden con la hoja de laboratorio (hoja: e final 0.31 / 0.23 / 0.187).")
    if s == 1 and k == 1:
        n.append("Probeta densa a bajo σ3: pico a εa≈4 % con dilatación (εv=+0.32 % en el pico; +2.03 % al final).")
    row = base(st, prel, alt)
    t8p = T8PAGE[s] if T8PAGE[s] else (21 if k == 1 else 22)
    row.update(ensayo_id=f"{inf}-E{k}", tipo_ensayo="CID (triaxial consolidado isotrópicamente drenado, ASTM D7181)",
               diametro_mm=fmt(r["ini"][1] * 10, 1), altura_mm=fmt(r["ini"][0] * 10, 1),
               gamma_d_kNm3=fmt(rho0 * 9.81, 2), e0=e0v, e0_origen="informe", w_pct=w0,
               sigma3_kPa=s3, sigma1_kPa=s3 + q, q_kPa=q, criterio_falla="Máximo esfuerzo desviador (Tabla 8)",
               phi_sec_deg="", eps_axial_falla_pct=r["lab_eps"], eps_vol_falla_pct=r["lab_ev"],
               pagina=f"{t8p};{r['pagina']};{gp}", notas=" ".join(n))
    rows.append(row)

PERM = [("G21-ALT1-9:1",2,179,1.65,1.802,9.11,2.219,"5.6E-06","5.60E-06","≥0.99"),
        ("G21-ALT1-1:1",4,180,8.2,1.801,11.0,2.253,"8.9E-07","8.90E-06","≥0.99"),
        ("G21-ALT2-9:1",5,181,2.5,1.802,9.1,2.222,"8.1E-06","8.10E-06","≥0.98"),
        ("G21-ALT2-1:1",7,182,8.5,1.802,10.8,2.264,"1.4E-06","1.40E-06","≥0.98"),
        ("G21-ALT4-9:1",8,183,1.63,1.802,9.24,2.218,"6.7E-06","6.70E-06","≥0.99"),
        ("G21-ALT4-1:1",10,184,8.14,1.802,11.11,2.245,"2.5E-06","2.50E-06","≥0.99")]
for sid, s, pg, w0, rho0, wf, rf, kk, k9, B in PERM:
    st = S[s]; alt, prop, prel, Gs = st[2], st[3], st[4], st[5]
    n = [f"Permeabilidad en pared flexible, ASTM D5084-16a Método C, a σ' = 399 kPa (celda 661 kPa, contrapresión 262 kPa), gradiente 1–2; B {B}.",
         f"k20 = {kk} m/s (promedio de las 5 últimas lecturas, hoja p.{pg}).",
         f"Alternativa {alt} ({RELAVE[alt]}), desmonte:relave {prop} ({prel} % relave).",
         f"Final: w={wf} %, ρd={rf} g/cm³ (igual a la probeta triaxial de ~400 kPa tras consolidar; el informe dice que se midió como parte de los triaxiales).",
         "e0 calculado con el Gs de la hoja triaxial del mismo material.",
         "Clase ROM/Chancado/Enrocado no indicada; alteración no indicada."]
    if s == 4:
        n.append("DISCREPANCIA: la Tabla 9 (p.23) y la Figura 11 dan 8.90E-06 m/s; la hoja de laboratorio (verificada en imagen) da 8.9E-07 m/s. Se adopta la hoja. La conclusión del informe de que en la Alt. 1 la k aumenta con el relave se apoya en el valor de la Tabla 9.")
    else:
        n.append(f"Tabla 9 (p.23): {k9} m/s, concuerda.")
    row = base(st, prel, alt)
    row.update(ensayo_id=f"{st[1]}-K", tipo_ensayo="Permeabilidad (pared flexible, ASTM D5084)",
               diametro_mm="152", altura_mm="305", gamma_d_kNm3=fmt(rho0 * 9.81, 2), e0=fmt(Gs / rho0 - 1, 3),
               e0_origen="calculado", w_pct=w0, sigma3_kPa=399, sigma1_kPa="", q_kPa="", criterio_falla="",
               phi_sec_deg="", eps_axial_falla_pct="", eps_vol_falla_pct="", pagina=f"23;{pg};{st[6]}", notas=" ".join(n))
    rows.append(row)

fn = os.path.join(outdir, "Golder_2021_commingling.csv")
with open(fn, "w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=COLS)
    w.writeheader()
    for x in rows:
        w.writerow(x)
print(fn, len(rows))
