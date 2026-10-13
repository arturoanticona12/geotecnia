"""Construye extraido/IDIEM_2025.csv a partir de las tablas parseadas (tx_data.json) y la granulometría digitalizada."""
import json, csv, math, sys, os
import numpy as np

here = os.path.dirname(os.path.abspath(__file__))
out = sys.argv[1]
data = json.load(open(os.path.join(here, "tx_data.json")))
KPA = 98.0665  # kPa por kgf/cm2

# Granulometría de montaje (Gráfico 1, p. 8) digitalizada por píxel; tamices nominales ASTM
gsd = [(0.075, 5.5), (0.106, 6.7), (0.25, 10.7), (0.425, 12.6), (0.85, 14.9), (2.0, 17.7), (4.75, 21.2),
       (9.5, 24.4), (19.0, 30.8), (25.0, 35.1), (37.5, 42.3), (50.0, 47.0), (63.0, 56.3), (75.0, 65.2),
       (100.0, 84.9), (125.0, 95.1), (150.0, 98.2), (177.8, 100.0)]
D = np.log10([g[0] for g in gsd]); P = np.array([g[1] for g in gsd])
def Dx(x): return 10 ** np.interp(x, P, D)
D10, D30, D50, D60 = (Dx(x) for x in (10, 30, 50, 60))
Cu, Cc = D60 / D10, D30 ** 2 / (D10 * D60)
finos = 5.5; arena = 21.2 - 5.5; grava = 100 - 21.2
print(f"D10={D10:.3f} D30={D30:.2f} D50={D50:.1f} D60={D60:.1f} Cu={Cu:.0f} Cc={Cc:.1f}")

cols = ["fuente","anio","autor_informe","laboratorio","set_id","ensayo_id","litologia_informe","litologia","litologia_detalle","litologia_proporcion","alteracion","tipo_material","clase_desmonte",
        "tipo_ensayo","saturado","diametro_mm","altura_mm","Dmax_mm","D10_mm","D30_mm","D50_mm","D60_mm","Cu","Cc",
        "grava_pct","arena_pct","finos_pct","escalamiento","Gs","gamma_d_kNm3","e0","e0_origen","Dr_pct","w_pct","UCS_MPa",
        "sigma3_kPa","sigma1_kPa","q_kPa","criterio_falla","phi_sec_deg","eps_axial_falla_pct","eps_vol_falla_pct",
        "u_falla_kPa","p_falla_kPa","q_falla_und_kPa","Su_kPa","Bg_pct","Br","finos_post_pct","sigma_n_kPa","tau_kPa",
        "pagina","verificado_imagen","notas"]

meta = {  # probeta: (paginas tabla, pagina grafico, vol drenado cm3, rho_d post consolidacion, contrapresion, camara, fechas)
    "1": ("10-14", 15, 16200, 2.12, 1.0, 6.0, "23-12-2024 a 26-12-2024"),
    "2": ("16-20", 21, 57500, 2.19, 2.0, 12.0, "17-01-2025 a 20-01-2025"),
    "3": ("22-27", 28, 131400, 2.31, 1.0, 21.0, "10-01-2025 a 12-01-2025"),
}
rows = []
for pr, r in data.items():
    ea, ev, p, q = (np.array([x[k] for x in r]) for k in range(4))
    pg = [x[4] for x in r]
    i = int(np.argmax(q))
    s3 = p[0] - q[0]
    dev = 2 * q[i]
    s1 = s3 + dev
    phi = math.degrees(math.asin(q[i] / p[i]))
    tp, gp, dv, rho_c, bp, cam, fechas = meta[pr]
    V0 = math.pi * 50 ** 2 * 180
    notas = (f"Fechas {fechas}. sigma3' = presión de cámara {cam:.2f} - contrapresión {bp:.2f} = {s3:.2f} kgf/cm2 "
             f"(1 kgf/cm2 = 98.0665 kPa). El informe tabula p=(s1+s3)/2 y q=(s1-s3)/2 (notación MIT); q_kPa de esta fila "
             f"es el desviador s1-s3 = 2·q_MIT = {dev:.2f} kgf/cm2. Falla = fila con q_MIT máximo de la tabla "
             f"({q[i]:.2f} kgf/cm2 en p. {pg[i]}). phi secante calculado (no informado) = asin(q/p) = {phi:.1f}°. "
             f"Al final del ensayo: ea = {ea[-1]:.2f} %, q_MIT = {q[-1]:.2f} kgf/cm2, ev = {ev[-1]:.2f} %. "
             f"Mínimo de ev = {ev.min():.2f} % en ea = {ea[int(np.argmin(ev))]:.2f} %. "
             f"Convención de ev del informe: negativo = contracción (compresión); no la declara explícitamente, se infiere "
             f"de la forma de las curvas (contracción inicial, dilatancia posterior en probeta 1). "
             f"Densidad seca de confección 2,10 g/cm3 (gamma_d de la columna); volumen drenado en consolidación {dv} cm3 "
             f"(εv,cons ≈ {dv / V0 * 100:.2f} %), densidad seca post consolidación {rho_c} g/cm3 = {rho_c * 9.81:.2f} kN/m3 (Tabla 4, p. 29). "
             f"Gs no informado: e0 no calculable. Humedad de confección 0,00 % (montaje seco, luego saturado con B >= 0,95). "
             f"Corte a carga controlada; velocidad de deformación no informada ('---'). Probeta remoldeada según granulometría del cliente. "
             f"Granulometría única de montaje (Gráfico 1, p. 8) digitalizada de la imagen (±0,5 %): no hay tabla numérica; "
             f"D10, D30, D50, D60, Cu, Cc y porcentajes calculados por interpolación log-lineal, leído de gráfico. "
             f"Granulometrías post-ensayo pendientes (Tabla 1): sin Bg. Tipo de desmonte (ROM/Chancado/Enrocado) no indicado en el informe: "
             f"muestra 'Intrusivo' (sin subtipo, mineralogía, alteración ni origen: calicata y cota '---' en Tabla 2, p. 6) enviada como material perturbado en maxisacos y cortada en 7\".")
    if pr == "2":
        notas += " El máximo ocurre en la meseta final (ea 12,97 %); el ensayo termina en ea = 15,02 % sin caída marcada: el pico podría no estar plenamente desarrollado."
    if pr == "3":
        notas += " El Gráfico 4 (p. 28) que corresponde a esta probeta está rotulado por error como 'probeta 1' en el pie."
    if pr == "1":
        notas += " Pico frágil: q_MIT cae de 8,57 a ~6,0 kgf/cm2 tras ea ≈ 8 %."
    rows.append({
        "fuente": "2025_IDIEM_Triaxiales Gran Escala Codisposal 100 Intrusivo.pdf", "anio": 2025,
        "autor_informe": "IDIEM, Informe de Ensayo Especial N°1.966.314-B Rev. 01 (24-01-2025), para WSP Perú / Cía. Minera Antamina",
        "laboratorio": "IDIEM, División Geotecnia Laboratorio (Santiago, Chile)",
        "set_id": "Codisposal 1 (100% Intrusivo)", "ensayo_id": f"Probeta {pr}", "litologia_informe": "Intrusivo", "litologia": "Intrusivo", "litologia_detalle": "", "litologia_proporcion": "", "alteracion": "",
        "tipo_material": "Mezcla co-disposición: clase de desmonte no indicada + 0 % relave (Codisposal 1 = 100 % Intrusivo)",
        "clase_desmonte": "", "tipo_ensayo": "CID", "saturado": "sí", "diametro_mm": 1000, "altura_mm": 1800,
        "Dmax_mm": 177.8, "D10_mm": round(D10, 2), "D30_mm": round(D30, 1), "D50_mm": round(D50, 1), "D60_mm": round(D60, 1),
        "Cu": round(Cu), "Cc": round(Cc, 1), "grava_pct": round(grava, 1), "arena_pct": round(arena, 1), "finos_pct": finos,
        "escalamiento": "truncado (scalping): corte en 7\" (177,8 mm) sobre banda definida por el cliente; Dmax de terreno no indicado",
        "Gs": "", "gamma_d_kNm3": round(2.10 * 9.81, 2), "e0": "", "e0_origen": "", "Dr_pct": "", "w_pct": 0.0, "UCS_MPa": "",
        "sigma3_kPa": round(s3 * KPA, 1), "sigma1_kPa": round(s1 * KPA, 1), "q_kPa": round(dev * KPA, 1),
        "criterio_falla": "máximo desviador", "phi_sec_deg": "",
        "eps_axial_falla_pct": ea[i], "eps_vol_falla_pct": ev[i],
        "u_falla_kPa": "", "p_falla_kPa": "", "q_falla_und_kPa": "", "Su_kPa": "", "Bg_pct": "", "Br": "", "finos_post_pct": "",
        "sigma_n_kPa": "", "tau_kPa": "",
        "pagina": f"{tp};{gp};8;29", "verificado_imagen": "sí", "notas": notas,
    })
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["ensayo_id"], r["sigma3_kPa"], r["sigma1_kPa"], r["q_kPa"], r["eps_axial_falla_pct"], r["eps_vol_falla_pct"])
