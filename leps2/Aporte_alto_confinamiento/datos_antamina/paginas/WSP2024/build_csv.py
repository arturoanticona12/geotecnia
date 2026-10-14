"""Construye extraido/WSP_2024_codisposicion.csv a partir de tx_parsed.jsonl (hojas IDIEM verificadas en imagen)
y de las tablas del cuerpo del informe WSP (verificadas en imagen)."""
import json, csv, math
from pathlib import Path

here = Path(__file__).resolve().parent
out = here.parents[1] / "extraido" / "WSP_2024_codisposicion.csv"
KG = 98.0665  # kPa por kgf/cm2

tx = [json.loads(l) for l in (here / "tx_parsed.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]

# Por mezcla: (nombre, %relave nominal, Gs global p.12, rho_d, pág. granulometría, D10, D30, D50, D60, Cu, Cc, grava, arena, finos)
mix = {
    "Codisposal 1": dict(code="C1", rel=22, ratio="3.5:1", Gs=2.93, rho=2.07, pg=268, D10=0.129, D30=2.13, D50=12.0, D60=19.2, Cu=148, Cc=1.84, gr=66.0, ar=26.9, fi=7.1, gran="leído de gráfico (digitalizado, Gráfico 1 p.268)", rep="E"),
    "Codisposal 2": dict(code="C2", rel=18, ratio="4.5:1", Gs=2.90, rho=2.03, pg=143, D10=0.135, D30=2.82, D50=12.2, D60=19.0, Cu=141, Cc=3.10, gr=67.2, ar=25.8, fi=7.1, gran="leído de gráfico (digitalizado, Gráfico 1 p.143)", rep="C"),
    "Codisposal 3": dict(code="C3", rel=15, ratio="5.5:1", Gs=2.89, rho=2.05, pg=232, D10=0.139, D30=3.43, D50=12.4, D60=19.0, Cu=137, Cc=4.46, gr=68.2, ar=24.7, fi=7.1, gran="leído de gráfico (digitalizado, Gráfico 1 p.232)", rep="D"),
    "Codisposal 4": dict(code="C4", rel=0, ratio="solo intrusivo", Gs=2.85, rho=2.00, pg=93, D10=0.200, D30=5.59, D50=13.3, D60=19.2, Cu=96, Cc=8.13, gr=73.3, ar=19.8, fi=6.9, gran="calculado de la tabla de granulometría inicial del desmonte (p.93) truncada bajo 4\" (pasante/96.2), coincide con Gráfico 1 p.108", rep="B"),
}
# Bg (Tabla 15, p.35-36) y finos post-ensayo (tablas IDIEM): clave (code, tipo, s3 kgf/cm2)
Bg = {("C1","M",5):9.6,("C1","M",10):18.3,("C1","M",20):16.9,("C1","CD",5):6.0,("C1","CD",10):11.8,("C1","CD",20):16.9,
      ("C2","M",5):7.8,("C2","M",10):8.6,("C2","M",20):13.5,("C2","CD",5):13.0,("C2","CD",10):15.8,("C2","CD",20):15.2,
      ("C3","M",5):6.3,("C3","M",10):15.2,("C3","M",20):19.4,
      ("C4","M",5):8.3,("C4","M",10):8.5,("C4","M",20):17.6}
Bg_pg = {"C1":"35","C2":"36","C3":"36","C4":"36"}
# (finos post %, % retenido N°4 post, página)
post = {("C1","M",5):(7.6,62.9,344),("C1","M",10):(11.8,48.9,344),("C1","M",20):(11.1,52.1,344),
        ("C1","CD",5):(6.9,66.4,344),("C1","CD",10):(7.1,64.0,344),("C1","CD",20):(10.5,55.1,344),
        ("C2","M",5):(8.2,60.6,221),("C2","M",10):(7.8,61.2,221),("C2","M",20):(9.4,57.6,221),
        ("C2","CD",5):(10.9,54.4,222),("C2","CD",10):(11.5,52.6,222),("C2","CD",20):(10.3,53.8,222),
        ("C3","M",5):(7.2,66.5,257),("C3","M",10):(9.0,56.5,257),("C3","M",20):(11.5,52.4,257),
        ("C4","M",5):(6.9,67.5,132),("C4","M",10):(7.4,70.2,132),("C4","M",20):(11.0,58.1,132)}
# densidad seca post consolidación (g/cm3) — tablas resumen IDIEM
rho_c = {("C1","M",5):(2.14,339),("C1","M",10):(2.19,339),("C1","M",20):(2.28,339),
         ("C1","CD",5):(2.12,341),("C1","CD",10):(2.14,341),("C1","CD",20):(2.21,341),
         ("C2","M",5):(2.08,217),("C2","M",10):(2.13,217),("C2","M",20):(2.17,217),
         ("C2","CD",5):(2.09,219),("C2","CD",10):(2.14,219),("C2","CD",20):(2.20,219),
         ("C3","M",5):(2.11,255),("C3","M",10):(2.14,255),("C3","M",20):(2.22,255),
         ("C4","M",5):(2.02,130),("C4","M",10):(2.11,130),("C4","M",20):(2.14,130)}
cyc_vol = {"9100","17400","26900","8200","11800","21300"}  # volúmenes de consolidación de las probetas carga-descarga (Tablas 5 C y 7 E)

cols = ["fuente","anio","autor_informe","laboratorio","set_id","ensayo_id","litologia_informe","litologia","litologia_detalle","litologia_proporcion","alteracion","tipo_material","clase_desmonte",
        "tipo_ensayo","saturado","diametro_mm","altura_mm","Dmax_mm","D10_mm","D30_mm","D50_mm","D60_mm","Cu","Cc",
        "grava_pct","arena_pct","finos_pct","escalamiento","Gs","gamma_d_kNm3","e0","e0_origen","Dr_pct","w_pct","UCS_MPa",
        "sigma3_kPa","sigma1_kPa","q_kPa","criterio_falla","phi_sec_deg","eps_axial_falla_pct","eps_vol_falla_pct",
        "u_falla_kPa","p_falla_kPa","q_falla_und_kPa","Su_kPa","Bg_pct","Br","finos_post_pct","sigma_n_kPa","tau_kPa",
        "pagina","verificado_imagen","notas"]
rows = []
order = {"C1":1,"C2":2,"C3":3,"C4":4}
for t in tx:
    name = t["muestra"].split(" (")[0]
    m = mix[name]; code = m["code"]
    cyc = t["head"]["vol_cons"].replace(",00","") in cyc_vol and code in ("C1","C2")
    typ = "CD" if cyc else "M"
    s3k = round(t["s3"]); s3 = s3k * KG
    qdev = 2 * t["qmax"] * KG
    s1 = s3 + qdev
    phi = math.degrees(math.asin(t["qmax"] / t["pmax"]))
    e0 = m["Gs"] / m["rho"] - 1
    rc, rcp = rho_c[(code,typ,s3k)]
    ec = m["Gs"] / rc - 1
    fpost, ret4, ppost = post[(code,typ,s3k)]
    vol_cons = float(t["head"]["vol_cons"].replace(",", "."))
    tipo_mat = (f"Mezcla co-disposición: desmonte (clase no indicada) + {m['rel']} % relave"
                if m["rel"] else "Desmonte (clase no indicada), 100 % intrusivo, sin relave")
    pk = t["page_peak"]; p0 = t["pages"].split("-")[0]
    notas = [f"{name} ({m['ratio']} intrusivo:relave en masa según informe)" if m["rel"] else "Codisposal 4 (100 % intrusivo)",
             "carga monótona" if typ=="M" else "carga-descarga drenada sin extensión: ciclos a εa=2 % (1+0.5q), 5 % (15 completos+0.75q+0.5q) y 8 % (2 completos+0.75q+0.5q), luego hasta 20 % (Tabla 10 p.18)",
             f"IDIEM informa q=(σ1−σ3)/2 y p=(σ1+σ3)/2 en kgf/cm²; máx. q/2={t['qmax']:.2f} y p={t['pmax']:.2f} kgf/cm² (p.{pk}); convertido con 1 kgf/cm²=98.0665 kPa; σ3 nominal del informe {int(s3k*98)} kPa ({s3k} kgf/cm²), contrapresión 1 kgf/cm²",
             f"criterio: máximo desviador en toda la curva (corte a carga controlada hasta εa≈20 %); phi_sec calculado como asin(q/p) con datos IDIEM y coincide con Fig. 13 p.27 (±0.1°)",
             "εv: convención IDIEM, negativo = contracción (compresión); todas las probetas contractivas al pico",
             f"vol. drenado en consolidación {vol_cons:.0f} cm³; ρd post-consolidación {rc:.2f} g/cm³ (p.{rcp}) → e_c≈{ec:.3f} (calculado con Gs global)",
             f"post-ensayo: % retenido N°4 = {ret4} (p.{ppost})",
             f"granulometría de ensayo: {m['gran']}",
             "Gs global de la mezcla (Tabla 5 p.12; Gs>N°4 = 2.87 aparente ASTM C127, Gs<N°4 ASTM D854)",
             "Dmax de terreno de la muestra 10\" (254 mm, p.93); probeta truncada a 4\"",
             "UCS = promedio de 7 ensayos ASTM D7012 sobre intrusivo (rango 64.0–143.1 MPa, Tabla 6 p.12); Is50 4.1–6.2 MPa (IDIEM-F p.364)",
             "clase de desmonte (ROM/Chancado/Enrocado) no indicada en el informe; muestra de 5 maxisacos de 'Desmonte de Mina (Intrusivo)'"]
    if typ == "M" and code == "C4" and s3k == 10:
        notas.append("q aún creciente al final del ensayo (máximo en el último punto, εa=20.70 %): no se alcanzó pico")
    if typ == "CD" and code == "C2" and s3k == 5:
        notas.append("IDIEM advierte: tras el 3er ciclo (8 %) aumento de deformación por cicleo; usar con precaución después del 8 %; el máximo q se dio al inicio de la etapa de 8 %")
    if typ == "CD":
        notas.append("en carga-descarga el máximo q puede coincidir con el punto de inicio de un ciclo")
    if m["rel"]:
        notas.append(f"ver resumen: la curva 'teórica' de ensayo coincide con desmonte + {m['rel']} % de relave aplicado solo a la fracción bajo 3/4\" (≈{m['rel']*0.597:.1f} % de la masa total); duda abierta")
    rows.append({
        "fuente":"2024_WSP_Ensayos gran escala mezcla co-disposicion.pdf","anio":2024,
        "autor_informe":"WSP Perú – 101-20110-LTE01220-IFF-420-G-0003 Rev.0 (proyecto 2094151472); anexos IDIEM 1.914.482-A a F",
        "laboratorio":"IDIEM (Universidad de Chile)",
        "set_id":f"WSP24_{code}_{'MON' if typ=='M' else 'CD'}",
        "ensayo_id":f"IDIEM {t['rep']} {name} Probeta {t['probeta']} ({'TX M' if typ=='M' else 'TX C/D'}) Pc {s3k} kgf/cm2",
        "litologia_informe":"Desmonte de Mina (Intrusivo)" + (" + Relave" if m["rel"] else ""),
        "litologia":"Intrusivo",
        "litologia_detalle":"tonalita (31 de 38 fragmentos de carga puntual, IDIEM-F pp.356-362); incluye fragmentos de caliza (7 de 38)",
        "litologia_proporcion":(f"Desmonte intrusivo {100-m['rel']} %; relave {m['rel']} % (nominal en masa)" if m["rel"] else "Intrusivo 100 % (nominal)")
                               + "; dentro del desmonte, por conteo de fragmentos de carga puntual: tonalita 82 %, caliza 18 %",
        "alteracion":"tonalita: sericitización, cloritización, epidotización, oxidación, arcillas/zeolitización locales; caliza sin alteración (carga puntual IDIEM-F)",
        "tipo_material":tipo_mat,"clase_desmonte":"",
        "tipo_ensayo":"CID" if typ=="M" else "CID carga-descarga",
        "saturado":"sí","diametro_mm":600,"altura_mm":1200,"Dmax_mm":101.6,
        "D10_mm":m["D10"],"D30_mm":m["D30"],"D50_mm":m["D50"],"D60_mm":m["D60"],"Cu":m["Cu"],"Cc":m["Cc"],
        "grava_pct":m["gr"],"arena_pct":m["ar"],"finos_pct":m["fi"],
        "escalamiento":"truncado (scalping) a 4\"; Dmax de terreno 10\"",
        "Gs":m["Gs"],"gamma_d_kNm3":round(m["rho"]*9.81,2),"e0":round(e0,3),"e0_origen":"calculado","Dr_pct":"","w_pct":3.0,
        "UCS_MPa":95.2,
        "sigma3_kPa":round(s3,1),"sigma1_kPa":round(s1,1),"q_kPa":round(qdev,1),
        "criterio_falla":"máximo desviador (hasta εa≈20 %)","phi_sec_deg":round(phi,1),
        "eps_axial_falla_pct":t["ea"],"eps_vol_falla_pct":t["ev"],
        "u_falla_kPa":"","p_falla_kPa":"","q_falla_und_kPa":"","Su_kPa":"",
        "Bg_pct":Bg[(code,typ,s3k)],"Br":"","finos_post_pct":fpost,"sigma_n_kPa":"","tau_kPa":"",
        "pagina":f"{p0};{pk};15;{m['pg']};{Bg_pg[code]};{ppost}",
        "verificado_imagen":"sí",
        "notas":"; ".join(notas),
        "_k":(order[code], typ, s3k)})
rows.sort(key=lambda r: r["_k"])
out.parent.mkdir(exist_ok=True)
with out.open("w", encoding="utf-8", newline="") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)
for r in rows:
    print(r["set_id"], r["sigma3_kPa"], r["q_kPa"], r["sigma1_kPa"], r["phi_sec_deg"], r["eps_axial_falla_pct"], r["eps_vol_falla_pct"], r["Bg_pct"], r["finos_post_pct"], r["e0"])
print(len(rows), "filas ->", out)
