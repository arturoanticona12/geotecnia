import json, math, csv, pathlib
base = pathlib.Path(__file__).resolve().parents[2]
pag = base / "paginas" / "ensayos"; out = base / "extraido"
out.mkdir(exist_ok=True)
tx = json.loads((pag / "tx_parsed.json").read_text(encoding="utf-8"))
G = 9.81
LAB = "Anddes Geolab SAC"
# ---------- metadatos por muestra (verificados en imagen) ----------
S = {
 "M": dict(set_id="Ruma 01 (M-1 al M-13)", lit_inf="Marmol", lit="Mármol", prop="", zona="Patio de servicios / Botadero Este", prof="40,00-90,00 m",
      tx_pdf="Marmol M-1 al M-13 Triaxial CU 6,0.pdf", tx_inf="EPE-23.10.141_17,19,20,13,23,22,25,24,14,15,12,16,21_200_R0_TXCU",
      ds_pdf="Marmol M-1 al M-13 LSDS.pdf", ds_inf="EPE-23.10141_12al25_200_R0_LSDS",
      su_pdf="Marmol M-1 al M-13 SUCS.pdf", pr_pdf="Marmol M-1 al M-13 Proctor estándar.pdf", ca_pdf="Marmol M-1 al M-13 CA.pdf",
      MDS=2.425, wopt=6.8, Gs=3.06, clase="", sucs="GP-GM",
      env_eff=(40.0, 44.0, 28.9, 34.7), env_tot=(29.0, 19.0, 27.1, 18.1, "2 %"), Su={500: 188, 1000: 447, 2000: 1009}),
 "I": dict(set_id="Ruma 03 / Fase 10 A (I-1 al I-12)", lit_inf="Intrusivo", lit="Intrusivo", prop="", zona="Botadero Este", prof="20,00-60,00 m",
      tx_pdf="Intrusivo I-1 al I-12 Triaxial CU 6.0.pdf", tx_inf="EPE-23.10.141_28,27,26,43,34,35,41,39,40,38,36_200_R0_TXCU",
      ds_pdf="Intrusivo I-1 al I-12 LSDS.pdf", ds_inf="EPE-23.10141_26al43_200_R0_LSDS",
      su_pdf="Intrusivo I-1 al I-12 SUCS.pdf", pr_pdf="Intrusivo I-1 al I-12 Proctor estándar.pdf", ca_pdf="Intrusivo I-1 al I-12 CA.pdf",
      MDS=2.134, wopt=8.0, Gs=2.75, clase="", sucs="GP-GM",
      env_eff=(82.0, 44.0, 59.3, 34.7), env_tot=(163.0, 16.0, 156.9, 15.6, "2 %"), Su={500: 359, 1000: 492, 2000: 840}),
 "H": dict(set_id="Ruma 02 (H-1 al H-12)", lit_inf="HORNFELS", lit="Hornfels", prop="", zona="Patio de servicios / Botadero Este", prof="40,00-90,00 m",
      tx_pdf="HORNFELS H-1 al H-12 Triaxial CU 6.0.pdf", tx_inf="EPE-23.10.141_7,9,2,4,11,8,1,3,5,6,18,10_200_R0_TXCU",
      ds_pdf="HORNFELS H-1 al H-12 LSDS.pdf", ds_inf="EPE-23.10141_1al18_200_R0_LSDS",
      su_pdf="HORNFELS H-1 al H-12 SUCS.pdf", pr_pdf="HORNFELS H-1 al H-12 Proctor estándar.pdf", ca_pdf="HORNFELS H-1 al H-12 CA.pdf",
      MDS=2.333, wopt=6.0, Gs=2.94, clase="", sucs="GP-GM",
      env_eff=(72.0, 40.5, 55.0, 33.0), env_tot=(72.0, 16.5, 69.4, 15.9, "2 %"), Su={500: 278, 1000: 491, 2000: 837}),
 "P1": dict(set_id="Pila 01 (MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B)", lit_inf="Mármol + Hornfels", lit="Mezcla",
      prop="Mármol + Hornfels, proporción no indicada", zona="Pilas Experimentales Medio Ambiente", prof="--",
      tx_pdf="Pila 01 Mármol + Hornfels Triaxial CU 6.0.pdf", tx_inf="EPE-23.10.141_1,2,3,4_110_R0_TXCU",
      ds_pdf="Pila 01 Mármol + Hornfels LSDS.pdf", ds_inf="EPE-23.10.141_1,2,3,4_110_R0_LSDS",
      su_pdf="Pila 01 Mármol + Hornfels SUCS.pdf", pr_pdf="Pila 01 Mármol + Hornfels Proctor estándar.pdf", ca_pdf="Pila 01 Mármol + Hornfels CA.pdf",
      MDS=2.327, wopt=7.4, Gs=2.90, clase="B (inferido de «Material B» en el N° de muestra)", sucs="GP-GM",
      env_eff=(61.0, 42.0, 45.3, 33.9), env_tot=(0.0, 25.0, 0.0, 22.9, "15 %"), Su={500: 292, 1000: 607, 2000: 1532}),
 "P2": dict(set_id="Pila 02 (MP2-A-M-1 a MP2-A-M-5, MP2-H-Material A)", lit_inf="Intrusivo", lit="Intrusivo", prop="",
      zona="Pilas Experimentales Medio Ambiente", prof="--",
      tx_pdf="Pila 02 Intrusivo Triaxial CU 6.0.pdf", tx_inf="EPE-23.10.141_5,6,7,8,9,10_110_R0_TXCU",
      ds_pdf="Pila 02 Intrusivo LSDS.pdf", ds_inf="EPE-23.10.141_5,6,7,8,9,10_110_R0_SUCS (sic, impreso así en el LSDS)",
      su_pdf="Pila 02 Intrusivo SUCS.pdf", pr_pdf="Pila 02 Intrusivo Proctor estándar.pdf", ca_pdf="Pila 02 Intrusivo CA.pdf",
      MDS=2.034, wopt=11.1, Gs=2.74, clase="A (inferido de «Material A» en el N° de muestra)", sucs="GW-GM",
      env_eff=(57.0, 42.0, 42.7, 33.8), env_tot=(0.0, 24.0, 0.0, 22.2, "15 %"), Su={500: 300, 1000: 684, 2000: 1391}),
}
ORDER = ["M", "H", "I", "P1", "P2"]
TIPO_NOTA = {
 "M": "tipo_material no indicado: muestra de perforación (Perforaciones Geotécnicas e Hidrogeológicas 2023) en Patio de servicios / Botadero Este, 40-90 m; por su origen sería desmonte ya depositado en botadero (probablemente ROM), pero el informe no lo dice",
 "H": "tipo_material no indicado: muestra de perforación en Patio de servicios / Botadero Este, 40-90 m; probablemente desmonte ROM de botadero, no confirmado por el informe",
 "I": "tipo_material no indicado: muestra de perforación en Botadero Este (Ruma 03 / Fase 10 A), 20-60 m; probablemente desmonte ROM de botadero, no confirmado por el informe",
 "P1": "tipo_material no indicado: material de «Pilas Experimentales Medio Ambiente»; el informe no dice si es ROM, Chancado o Enrocado",
 "P2": "tipo_material no indicado: material de «Pilas Experimentales Medio Ambiente»; el informe no dice si es ROM, Chancado o Enrocado",
}
COMMON = ["fuente", "anio", "autor_informe", "laboratorio", "set_id", "ensayo_id", "litologia_informe", "litologia", "litologia_detalle",
          "litologia_proporcion", "alteracion", "tipo_material", "clase_desmonte", "tipo_ensayo", "saturado"]


def common(k, fuente, inf, ensayo_id, tipo):
    s = S[k]
    return dict(fuente=fuente, anio=2024, autor_informe=f"{LAB}; solicitud EPE-23.10.141; informe {inf}", laboratorio=LAB,
                set_id=s["set_id"], ensayo_id=ensayo_id, litologia_informe=s["lit_inf"], litologia=s["lit"], litologia_detalle="",
                litologia_proporcion=s["prop"], alteracion="", tipo_material="", clase_desmonte=s["clase"], tipo_ensayo=tipo)


def r(x, n=1):
    return None if x is None else round(x, n)


# ---------- TRIAXIAL ----------
txcols = COMMON + ["diametro_mm", "altura_mm", "Dmax_mm", "escalamiento", "Gs", "gamma_d_kNm3", "rho_d_gcm3", "e0", "e0_origen", "Dr_pct", "w_pct",
    "B", "contrapresion_kPa", "presion_celda_kPa", "altura_consol_mm", "diametro_consol_mm", "rho_d_consol_gcm3", "w_final_pct",
    "sigma3_kPa", "sigma1_kPa", "q_kPa", "criterio_falla", "eps_axial_falla_pct", "u_falla_kPa", "p_falla_kPa", "q_falla_und_kPa", "ratio_s1s3_falla", "Su_kPa",
    "q_dev_max_kPa", "eps_q_dev_max_pct", "u_q_dev_max_kPa", "p_q_dev_max_kPa", "ratio_s1s3_max", "eps_ratio_max_pct",
    "c_ef_serie_kPa", "phi_ef_serie_deg", "a_ef_serie_kPa", "alfa_ef_serie_deg", "c_tot_serie_kPa", "phi_tot_serie_deg", "envolvente_total_criterio",
    "pagina", "verificado_imagen", "notas"]
txrows = []
for k in ORDER:
    s = S[k]
    for sp in sorted(tx[k], key=lambda o: float(o["s3"][-1].replace(",", "."))):
        s3 = float(sp["s3"][-1].replace(",", ".")); rows = sp["rows"]
        f = rows[-1]
        assert f[0] == 15.0
        eps, dq, u, p, qm, pp, qq, qp, ratio = f
        s3f = s3 - u; s1f = s3f + dq
        assert abs((s1f + s3f) / 2 - pp) < 0.2, (k, s3, pp)
        assert abs(sp["cell"][-1] - sp["bp"][-1] - s3) < 0.5
        qmax = max(rows, key=lambda x: x[1]); rmax = max(rows, key=lambda x: x[8])
        rho0 = sp["rho"][0]; e0 = s["Gs"] / rho0 - 1
        c = common(k, s["tx_pdf"], s["tx_inf"], f"{s3:.0f} kPa (Esf. efect. inicial)", "CU (CIU, ASTM D4767-11(2020))")
        c.update(saturado="sí", diametro_mm=r(sp["Diametro"][0] * 10), altura_mm=r(sp["Altura"][0] * 10), Dmax_mm="",
            escalamiento="no indicado (probeta reconstituida; muestra de terreno TM 3 in)",
            Gs=s["Gs"], gamma_d_kNm3=r(rho0 * G, 2), rho_d_gcm3=rho0, e0=r(e0, 3), e0_origen="calculado", Dr_pct="", w_pct=sp["w"][0],
            B=sp["B"][0], contrapresion_kPa=sp["bp"][-1], presion_celda_kPa=sp["cell"][-1], altura_consol_mm=r(sp["Altura"][1] * 10),
            diametro_consol_mm=r(sp["Diametro"][1] * 10), rho_d_consol_gcm3=sp["rho"][1], w_final_pct=sp["w"][1],
            sigma3_kPa=s3, sigma1_kPa=r(s1f), q_kPa=dq, criterio_falla="deformación límite 15 % (criterio del informe para envolvente efectiva y Su)",
            eps_axial_falla_pct=eps, u_falla_kPa=u, p_falla_kPa=pp, q_falla_und_kPa=qq, ratio_s1s3_falla=ratio, Su_kPa=s["Su"][int(s3)],
            q_dev_max_kPa=qmax[1], eps_q_dev_max_pct=qmax[0], u_q_dev_max_kPa=qmax[2], p_q_dev_max_kPa=qmax[5], ratio_s1s3_max=rmax[8], eps_ratio_max_pct=rmax[0],
            c_ef_serie_kPa=s["env_eff"][0], phi_ef_serie_deg=s["env_eff"][1], a_ef_serie_kPa=s["env_eff"][2], alfa_ef_serie_deg=s["env_eff"][3],
            c_tot_serie_kPa=s["env_tot"][0], phi_tot_serie_deg=s["env_tot"][1], envolvente_total_criterio=f"trazada al {s['env_tot'][4]} de deformación",
            pagina=f"{ {2000: 3, 1000: 4, 500: 5}[int(s3)] };1;7", verificado_imagen="sí")
        notas = [f"Probeta reconstituida al 90 % de la MDS Proctor estándar ({s['MDS']} g/cm³) y w óptimo {s['wopt']} %",
                 "σ3 = esfuerzo efectivo de consolidación isotrópica (celda − contrapresión)",
                 "p′ y q′ en convención MIT: p′=(σ′1+σ′3)/2, q′=(σ1−σ3)/2; q_kPa es el desviador completo",
                 "σ′1 calculado = σ3 − u + desviador (cuadra con p′ del informe)",
                 f"e0 calculado con Gs={s['Gs']} (Gs de la curva de 100 % saturación del Proctor) y ρd inicial",
                 "Dmax de la probeta no indicado en el informe TX (el LSDS usa TM 1 in; el Proctor separa sobretamaño)",
                 "c′ y φ′ de la serie: envolvente efectiva al 15 % de deformación (p.1); totales en p.7 (interpretación pedida por el cliente)",
                 "Velocidad 0,025 cm/min",
                 TIPO_NOTA[k]]
        if k == "P2" and s3 == 2000:
            notas.append("w final (10,5 %) menor que w inicial (11,1 %), tal cual en el informe")
        if qmax[0] >= 14.0:
            notas.append("desviador máximo al final del ensayo (14-15 %): comportamiento dilatante")
        c["notas"] = "; ".join(notas)
        txrows.append(c)

# ---------- CORTE DIRECTO (transcrito de imagen p.1 y p.2) ----------
DS = {
 "M": dict(sn=[300, 600, 1200], tp=[219.5, 469.5, 984.3], fp=[36, 38, 39], tr=[208.0, 469.2, 973.5], fr=[35, 38, 39], env_p=(0.0, 39.0, 0.68), env_r=(0.0, 38.7, 0.67),
           w0=6.80, rho0=2.183, wf=[9.90, 9.60, 9.00], rhof=[2.322, 2.396, 2.456], hf=[16.7, 16.2, 15.8], fechas="2024-07-16 / 2024-07-23", muestra="M-1 al M-13"),
 "H": dict(sn=[300, 600, 1200], tp=[255.7, 476.1, 998.1], fp=[40, 38, 40], tr=[250.8, 473.9, 998.1], fr=[40, 38, 40], env_p=(0.0, 39.5, 0.69), env_r=(0.0, 39.5, 0.69),
           w0=7.70, rho0=2.100, wf=[10.60, 9.70, 8.90], rhof=[2.227, 2.293, 2.350], hf=[16.8, 16.3, 15.9], fechas="2024-07-24 / 2024-08-01", muestra="H-1 al H-12"),
 "I": dict(sn=[300, 600, 1200], tp=[228.1, 468.1, 945.1], fp=[37, 38, 38], tr=[218.3, 451.8, 885.6], fr=[36, 37, 36], env_p=(0.0, 38.1, 0.67), env_r=(0.0, 36.5, 0.64),
           w0=9.80, rho0=1.921, wf=[11.90, 11.40, 11.00], rhof=[2.006, 2.026, 2.091], hf=[17.0, 16.9, 16.3], fechas="2024-07-08 / 2024-07-15", muestra="I-1 al I-11"),
 "P1": dict(sn=[300, 600, 1000], tp=[356.3, 625.3, 947.3], fp=[50, 46, 43], tr=[340.0, 625.3, 931.2], fr=[49, 46, 43], env_p=(109.6, 40.1, 0.70), env_r=(100.0, 40.0, 0.70),
           w0=7.40, rho0=2.094, wf=[8.50, 8.00, 7.40], rhof=[2.191, 2.248, 2.290], hf=[17.0, 16.6, 16.3], fechas="2024-10-15 / 2024-10-25", muestra="MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B"),
 "P2": dict(sn=[300, 600, 1200], tp=[353.9, 633.7, 1019.2], fp=[50, 47, 40], tr=[349.1, 631.7, 991.5], fr=[49, 46, 40], env_p=(161.1, 36.0, 0.63), env_r=(169.2, 34.9, 0.61),
           w0=11.10, rho0=1.831, wf=[11.70, 11.40, 10.90], rhof=[1.907, 1.941, 1.995], hf=[17.1, 16.8, 16.3], fechas="2024-10-05 / 2024-10-15", muestra="MP2-A-M-1 a MP2-A-M-5, MP2-H-Material A"),
}
TXW = {"M": 6.8, "H": 6.0, "I": 8.0, "P1": 7.4, "P2": 11.1}
dscols = COMMON + ["caja_mm", "diametro_mm", "altura_mm", "Dmax_mm", "escalamiento", "Gs", "gamma_d_kNm3", "rho_d_gcm3", "e0", "e0_origen", "Dr_pct", "w_pct",
   "sigma_n_kPa", "tau_kPa", "criterio_falla", "phi_sec_deg", "tau_66mm_kPa", "phi_sec_66mm_deg", "tau_residual_kPa",
   "c_pico_serie_kPa", "phi_pico_serie_deg", "coef_friccion_pico", "c_66mm_serie_kPa", "phi_66mm_serie_deg", "coef_friccion_66mm",
   "altura_final_mm", "rho_d_final_gcm3", "w_final_pct", "pagina", "verificado_imagen", "notas"]
dsrows = []
for k in ORDER:
    s = S[k]; t = DS[k]
    for i in range(3):
        c = common(k, s["ds_pdf"], s["ds_inf"], f"Ensayo {i + 1} (σn {t['sn'][i]} kPa)", "corte directo CD gran escala (ASTM D3080/D3080M-23)")
        c.update(saturado="sí", caja_mm="305 × 305", diametro_mm=305, altura_mm=178, Dmax_mm=25.4,
            escalamiento="no indicado; TM de ensayo 1 in (muestra de terreno TM 3 in)",
            Gs=s["Gs"], gamma_d_kNm3=r(t["rho0"] * G, 2), rho_d_gcm3=t["rho0"], e0=r(s["Gs"] / t["rho0"] - 1, 3), e0_origen="calculado", Dr_pct="", w_pct=t["w0"],
            sigma_n_kPa=t["sn"][i], tau_kPa=t["tp"][i], criterio_falla="pico (máximo τ en ~65 mm de recorrido)", phi_sec_deg=t["fp"][i],
            tau_66mm_kPa=t["tr"][i], phi_sec_66mm_deg=t["fr"][i], tau_residual_kPa="",
            c_pico_serie_kPa=t["env_p"][0], phi_pico_serie_deg=t["env_p"][1], coef_friccion_pico=t["env_p"][2],
            c_66mm_serie_kPa=t["env_r"][0], phi_66mm_serie_deg=t["env_r"][1], coef_friccion_66mm=t["env_r"][2],
            altura_final_mm=r(t["hf"][i] * 10), rho_d_final_gcm3=t["rhof"][i], w_final_pct=t["wf"][i], pagina="1;2", verificado_imagen="sí")
        notas = ["Caja cuadrada 30,5 × 30,5 cm, altura 17,8 cm, TM 1 in; separación de cajas 1,0 mm; velocidad 0,5 mm/min; consolidación 16 h",
                 "Espécimen saturado durante el ensayo «salvo excepciones» (condición estándar del laboratorio)",
                 "τ a 6,6 cm es el valor a gran desplazamiento informado; no es residual verdadero (no hay inversión de caja)",
                 f"ρd inicial {t['rho0']} g/cm³ = 90 % de la MDS Proctor ({s['MDS']} g/cm³)",
                 f"e0 calculado con Gs={s['Gs']} (curva de saturación del Proctor)",
                 f"N° de muestra en el LSDS: {t['muestra']}; fechas {t['fechas']}",
                 TIPO_NOTA[k]]
        if k == "P1":
            notas.append("σn máximo 1000 kPa (no 1200 kPa como en las demás series); c = 109,6 kPa de la envolvente lineal refleja curvatura (φ secante 50° a 300 kPa)")
        if k == "P2":
            notas.append("c = 161,1 kPa de la envolvente lineal refleja curvatura (φ secante 50° a 300 kPa); el N° de informe impreso termina en _SUCS")
        if abs(t["w0"] - TXW[k]) > 0.05:
            notas.append(f"w inicial del LSDS ({t['w0']} %) difiere del w del triaxial ({TXW[k]} %) con la misma ρd")
        if k == "I":
            notas.append("el LSDS indica I-1 al I-11 (el TX indica I-1 al I-12)")
        c["notas"] = "; ".join(notas)
        dsrows.append(c)

# ---------- INDICES ----------
GR = {  # % que pasa: 3, 2, 1.5, 1, 3/4, 3/8 in, #4, #10, #20, #40, #60, #100, #140, #200
 "M": [100, 85, 75, 63, 56, 44, 35, 27, 22, 18, 15, 13, 12, 10],
 "H": [100, 91, 83, 68, 59, 43, 32, 26, 21, 18, 16, 14, 13, 11],
 "I": [100, 90, 84, 73, 65, 49, 37, 24, 18, 15, 13, 11, 9, 8],
 "P1": [100, 93, 87, 78, 70, 53, 41, 32, 26, 22, 19, 16, 13, 11],
 "P2": [100, 93, 89, 81, 73, 55, 43, 32, 26, 22, 18, 15, 12, 9]}
SZ = [75, 50, 37.5, 25, 19, 9.5, 4.75, 2.0, 0.85, 0.425, 0.25, 0.15, 0.106, 0.075]
GN = "Poorly graded gravel with silt and sand / Grava pobremente gradada con limo y arena"
RPT = {  # D10, D30, D60, Cu, Cc, bolonería, grava, arena, finos, LL, LP, IP, nombre
 "M": (1.54, 2.76, 22.04, 14.29, 0.22, "--", 65, 25, 10, "NP", "NP", "NP", GN),
 "H": (1.54, 3.55, 19.45, 12.61, 0.42, "--", 68, 21, 11, 16, "NP", "NP", GN),
 "I": (0.13, 3.03, 15.35, 121.26, 4.74, "--", 63, 29, 8, 17, "NP", "NP", GN),
 "P1": (1.54, 1.47, 12.51, 8.11, 0.11, 0, 59, 30, 11, "NP", "NP", "NP", GN),
 "P2": (0.08, 1.45, 11.49, 138.86, 2.21, 1, 57, 34, 9, "NP", "NP", "NP", "Well-graded gravel with silt and sand / Grava bien gradada con limo y arena")}
PR = {  # γd máx, w opt, γd corr, w corr, Gs bulk sobretamaño, w sobretamaño, método, puntos ρd/γd/w
 "M": (23.780, 6.8, 25.754, 3.9, 2.94, 0.1, "ASTM D698-12(2021) (fuera de método)", "2,4/23,1/3,6; 2,4/23,7/5,8; 2,4/23,7/7,7; 2,4/23,1/9,5"),
 "H": (22.876, 7.7, 24.533, 4.7, 2.80, 0.3, "ASTM D698-12(2021) (fuera de método)", "2,2/21,9/4,4; 2,3/22,6/6,1; 2,3/22,9/8,1; 2,2/21,9/10,1"),
 "I": (20.930, 9.8, 22.230, 6.7, 2.56, 1.0, "ASTM D698-12(2021) (fuera de método)", "2,0/19,2/5,0; 2,0/19,9/7,3; 2,1/20,8/9,0; 2,1/20,3/11,1"),
 "P1": (22.819, 7.4, 24.012, 5.4, 2.79, 0.8, "ASTM D698-12(2021) Método C", "2,2/21,9/3,4; 2,3/22,3/5,0; 2,3/22,8/7,1; 2,3/22,4/9,0"),
 "P2": (19.951, 11.1, 20.797, 8.6, 2.39, 2.0, "ASTM D698-12(2021) Método C", "2,0/19,4/7,1; 2,0/19,7/9,3; 2,0/20,0/11,0; 2,0/19,5/13,0")}
CA = {"M": (3, 710.0, 24174.0), "H": (3, 757.0, 23114.0), "I": (5, 1211.0, 23683.0), "P1": (3, 216.0, 7696.0), "P2": (6, 542.0, 9822.0)}


def Dx(k, x):
    p = GR[k]
    for i in range(len(p) - 1):
        if p[i] >= x >= p[i + 1]:
            if p[i] == p[i + 1]:
                return SZ[i + 1]
            t = (x - p[i + 1]) / (p[i] - p[i + 1])
            return 10 ** (math.log10(SZ[i + 1]) + t * (math.log10(SZ[i]) - math.log10(SZ[i + 1])))
    return None


ixcols = ["fuente", "anio", "autor_informe", "laboratorio", "set_id", "litologia_informe", "litologia", "litologia_detalle", "litologia_proporcion", "alteracion",
  "tipo_material", "clase_desmonte", "zona", "profundidad", "Dmax_mm", "D10_mm", "D30_mm", "D50_mm", "D60_mm", "Cu", "Cc",
  "D10_interp_mm", "D30_interp_mm", "D60_interp_mm", "Cu_interp", "Cc_interp",
  "bolones_pct", "grava_pct", "arena_pct", "finos_pct", "granulometria_pct_pasa", "LL", "LP", "IP", "SUCS", "nombre_grupo",
  "proctor_metodo", "gamma_d_max_kNm3", "rho_d_max_gcm3", "w_opt_pct", "gamma_d_max_corr_kNm3", "w_opt_corr_pct", "Gs_bulk_sobretamano", "w_sobretamano_pct",
  "proctor_puntos_rho_gd_w", "Gs", "w_natural_pct", "w_natural_calc_pct", "TM_visual_CA", "pagina", "verificado_imagen", "notas"]
ixrows = []
for k in ORDER:
    s = S[k]; g = RPT[k]; p = PR[k]; ca = CA[k]
    d10, d30, d60, d50 = Dx(k, 10), Dx(k, 30), Dx(k, 60), Dx(k, 50)
    c = dict(fuente=f"{s['su_pdf']} | {s['pr_pdf']} | {s['ca_pdf']}", anio=2024, autor_informe=f"{LAB}; solicitud EPE-23.10.141 (informes _SUCS, _PR, _CA)",
       laboratorio=LAB, set_id=s["set_id"], litologia_informe=s["lit_inf"], litologia=s["lit"], litologia_detalle="", litologia_proporcion=s["prop"], alteracion="",
       tipo_material="", clase_desmonte=s["clase"], zona=s["zona"], profundidad=s["prof"], Dmax_mm=75,
       D10_mm=g[0], D30_mm=g[1], D50_mm=r(d50, 2), D60_mm=g[2], Cu=g[3], Cc=g[4],
       D10_interp_mm=r(d10, 3), D30_interp_mm=r(d30, 2), D60_interp_mm=r(d60, 2), Cu_interp=r(d60 / d10, 1) if d10 else None, Cc_interp=r(d30 ** 2 / (d10 * d60), 2) if d10 else None,
       bolones_pct=g[5], grava_pct=g[6], arena_pct=g[7], finos_pct=g[8],
       granulometria_pct_pasa="; ".join(f"{z} mm:{v}" for z, v in zip(SZ, GR[k])), LL=g[9], LP=g[10], IP=g[11], SUCS=s["sucs"], nombre_grupo=g[12],
       proctor_metodo=p[6], gamma_d_max_kNm3=p[0], rho_d_max_gcm3=s["MDS"], w_opt_pct=p[1], gamma_d_max_corr_kNm3=p[2], w_opt_corr_pct=p[3],
       Gs_bulk_sobretamano=p[4], w_sobretamano_pct=p[5], proctor_puntos_rho_gd_w=p[7], Gs=s["Gs"], w_natural_pct=ca[0],
       w_natural_calc_pct=r(ca[1] / ca[2] * 100, 2), TM_visual_CA="3 in",
       pagina="SUCS p.1 (granulometría), p.2 (límites, SUCS); Proctor p.1; CA p.1", verificado_imagen="sí")
    notas = ["Dmax = 75 mm (3 in, 100 % pasa); tamizado ASTM D6913 método A, muestra disturbada",
             "D50 y columnas *_interp calculados por interpolación log-lineal de la curva (no informados)",
             "Gs no medido directamente: es el valor rotulado en la curva de 100 % saturación del Proctor (fracción no indicada)",
             "MDS y w óptimo sin corregir son la base de las probetas TX y LSDS (90 % MDS); también se informan valores corregidos por sobretamaño",
             "w natural informado redondeado a entero; w_natural_calc = masa de agua / masa seca de la hoja CA",
             TIPO_NOTA[k]]
    if k in ("M", "H", "P1"):
        notas.append(f"D10 informado ({g[0]} mm) es incoherente con la curva ({GR[k][-1]} % pasa 0,075 mm), el D10 real es <= 0,075 mm; Cu y Cc informados son dudosos")
    if d10 is None:
        notas.append(f"D10_interp, Cu_interp y Cc_interp vacíos: {GR[k][-1]} % pasa 0,075 mm, así que D10 < 0,075 mm y queda fuera del rango del tamizado (requiere sedimentación)")
    if k == "P1":
        notas.append("D30 informado (1,47) menor que D10 informado (1,54): error del informe")
    if k == "P2":
        notas.append("bolonería 1 % pero pasa 100 % por 3 in; grava+arena+finos = 100")
    if k in ("M", "H", "I"):
        notas.append("Proctor marcado «Fuera de método»")
    if abs(p[1] - TXW[k]) > 0.05:
        notas.append(f"w óptimo de esta hoja Proctor ({p[1]} %) difiere del «óptimo» declarado y usado en el TX ({TXW[k]} %); el LSDS usa {p[1]} %")
    if k == "I":
        notas.append("SUCS, Proctor y CA listan I-1 a I-11 (el TX dice I-1 al I-12)")
    c["notas"] = "; ".join(notas)
    ixrows.append(c)

for name, cols, rows in [("ensayos_triaxial_CU.csv", txcols, txrows), ("ensayos_corte_directo.csv", dscols, dsrows), ("ensayos_indices.csv", ixcols, ixrows)]:
    with open(out / name, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
        for row in rows:
            w.writerow({c: ("" if row.get(c) is None else row.get(c, "")) for c in cols})
    print(name, len(rows), "filas")
for row in txrows:
    print(row["litologia_informe"][:9], row["sigma3_kPa"], row["q_kPa"], row["u_falla_kPa"], row["sigma1_kPa"], row["p_falla_kPa"], row["q_falla_und_kPa"],
          "qmax", row["q_dev_max_kPa"], row["eps_q_dev_max_pct"], "e0", row["e0"], "B", row["B"])
for row in ixrows:
    print(row["set_id"][:8], "D10i", row["D10_interp_mm"], "D30i", row["D30_interp_mm"], "D50", row["D50_mm"], "D60i", row["D60_interp_mm"], "Cu", row["Cu_interp"], "Cc", row["Cc_interp"], "w", row["w_natural_calc_pct"])
