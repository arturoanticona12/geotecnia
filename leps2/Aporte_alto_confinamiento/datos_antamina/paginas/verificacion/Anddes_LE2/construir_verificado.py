import pandas as pd, json, pathlib
here = pathlib.Path(__file__).parent
base = here.parents[2]
ext = base / "extraido"
ver = base / "verificado"
ver.mkdir(exist_ok=True)
R = json.load(open(here / "tx_verif.json"))
C = {c["key"]: c for c in json.load(open(here / "tx_criterios.json"))}
m = {"Marmol": "M", "HORNFELS": "H", "Intrusivo": "I", "Pila 01": "P1", "Pila 02": "P2"}
GS = {"M": 3.06, "H": 2.94, "I": 2.75, "P1": 2.90, "P2": 2.74}


def key_of(f):
    return [v for kk, v in m.items() if f.startswith(kk)][0]


def local_peak(rows):
    q = [r[1] for r in rows]
    for i in range(1, len(q) - 1):
        win = q[max(0, i - 3):i + 4]
        if q[i] == max(win) and q[i] > min(q[i + 1:i + 4]) * 1.01:
            return rows[i]
    return None


# ---------------- TX ----------------
tx = pd.read_csv(ext / "ensayos_triaxial_CU.csv", dtype=str)
new = []
for idx, r in tx.iterrows():
    k = key_of(r.fuente)
    s = r.ensayo_id.split(" kPa")[0]
    key = f"{k}_{s} kPa"
    c = C[key]
    d = R[key]
    s3c = c["s3c"]
    row = r.to_dict()
    row["Dmax_mm"] = "no informado"
    row["tipo_material"] = "no indicada"
    row["sigma3c_kPa"] = s3c
    for tag, st in (("qmax", c["qmax"]), ("oblmax", c["obl"]), ("e15", c["e15"])):
        row[f"eps_{tag}_pct"] = st["eps"]
        row[f"sigma3f_{tag}_kPa"] = st["s3f"]
        row[f"sigma1f_{tag}_kPa"] = st["s1f"]
        row[f"u_{tag}_kPa"] = st["u"]
        row[f"q_{tag}_kPa"] = st["q"]
        row[f"ratio_{tag}"] = round(st["ratio"], 3)
        row[f"p_mit_{tag}_kPa"] = st["pp"]
        row[f"t_mit_{tag}_kPa"] = st["qq"]
    lp = local_peak(d["rows"])
    if lp and lp[1] < c["qmax"]["q"] - 0.05:
        row["pico_local_previo"] = (f"q={lp[1]} kPa a eps={lp[0]} % (u={lp[2]} kPa; sigma3f={round(s3c - lp[2], 1)}; "
                                    f"sigma1f={round(s3c - lp[2] + lp[1], 1)} kPa); el maximo global esta a {c['qmax']['eps']} %")
    else:
        row["pico_local_previo"] = "no (el maximo desviador es el primer pico)" if c["qmax"]["eps"] < 14 else "no hay pico previo"
    g = GS[k]
    rc = d["rho"][1]
    wf = d["w"][1]
    row["e_post_consolidacion_calc"] = round(g / rc - 1, 3)
    row["dV_consolidacion_pct_calc"] = c["dV_cons_pct"]
    row["Sr_post_consol_calc"] = round(wf / 100 * g / (g / rc - 1), 2)
    row["Gs_implicito_Sr1_calc"] = c["Gs_imp_Sr1"]
    row["velocidad_pct_min_calc"] = round(0.025 / 31.0 * 100, 4)
    row["verificado_imagen"] = "sí"
    row["notas_verificacion"] = (
        "Verificado 2026-10-06 contra la imagen de p.1, p.3-5 y p.7. En el CSV original sigma3_kPa es el σ′3 de consolidación (σ′3c) y sigma1_kPa es σ′1 en la falla al 15 %: "
        "q_kPa ≠ sigma1_kPa − sigma3_kPa porque mezclan estados; usar sigma3f_*/sigma1f_*. Estados recalculados: σ′3f = σ′3c − u; σ′1f = σ′3f + q. "
        "Criterios: qmax = máximo desviador tabulado; oblmax = máxima σ′1/σ′3 recalculada; e15 = 15 % (criterio del informe). "
        "Gs = valor rotulado en la curva de 100 % de saturación del Proctor (no ensayado). Dmax de la probeta y método de compactación (capas, pisón) no informados; "
        "en el formato está marcado «Grado de compactación: Medio».")
    new.append(row)
txv = pd.DataFrame(new)
txv.to_csv(ver / "ensayos_triaxial_CU_verificado.csv", index=False, encoding="utf-8")

# ---------------- LSDS ----------------
ls = pd.read_csv(ext / "ensayos_corte_directo.csv", dtype=str)
rows = []
for i, r in ls.iterrows():
    k = key_of(r.fuente)
    row = r.to_dict()
    g = GS[k]
    rf = float(r.rho_d_final_gcm3)
    wf = float(r.w_final_pct)
    Sr = wf / 100 * g / (g / rf - 1)
    row["saturado"] = "no confirmado («saturados durante el ensayo, salvo excepciones», p.2)"
    row["Sr_final_calc"] = round(Sr, 2)
    row["escalamiento"] = ("no informado; TM de ensayo 1 in (p.2). La MDS de referencia (90 %) es la del Proctor sobre la fracción < 19 mm (3/4 in), "
                           "inferido de la corrección por sobretamaño")
    row["verificado_imagen"] = "sí"
    if k in ("P1", "P2"):
        extra = "Sr final 0,73-0,81 y, en P1 a 1000 kPa, w final = w inicial (7,40 %): no hay evidencia de saturación."
    elif k == "I":
        extra = "Sr final 0,88-0,96: saturación incompleta o Gs menor que el rotulado."
    else:
        extra = "Sr final 0,95-1,12 (valores > 1 indican incertidumbre de Gs o de la w final)."
    row["notas_verificacion"] = ("Verificado 2026-10-06 contra la imagen de p.1 y p.2: σn, τ pico, τ a 6,6 cm, ángulos secantes, c, φ, μ, alturas, w y ρd coinciden. "
                                 f"Sr final recalculado con el Gs rotulado {g}: {Sr:.2f}. " + extra)
    rows.append(row)
pd.DataFrame(rows).to_csv(ver / "ensayos_corte_directo_verificado.csv", index=False, encoding="utf-8")

# ---------------- Indices ----------------
ix = pd.read_csv(ext / "ensayos_indices.csv", dtype=str)
extra = {
    "M": dict(ret19=44, Pc=43.7, gs_line=3.05, gs_min=3.03, D10v="0,075 (pasa 10 % por 0,075 mm; interpolación)",
              sucs="GP-GM verificable: con D10 = 0,075 mm, Cc ≈ 4,6 > 3, así que es GP",
              bloq="Mármol P50 2,70 (P16-P84 2,69-2,73); Mármol diopsídico P50 2,85"),
    "H": dict(ret19=41, Pc=40.4, gs_line=2.93, gs_min=2.88, D10v="< 0,075 (pasa 11 % por 0,075 mm; no medible por tamizado)",
              sucs="GP-GM se mantiene: con D10 < 0,075 mm, Cc > 8, así que es GP",
              bloq="Horfels P50 2,70 (2,69-2,73); Horfel diopsida P50 2,87"),
    "I": dict(ret19=35, Pc=35.1, gs_line=2.74, gs_min=2.69, D10v="0,126 (coincide con el 0,13 informado)",
              sucs="GP-GM verificable (Cc 4,6-4,7 > 3)", bloq="Intrusivo P50 2,45 (2,40-2,52)"),
    "P1": dict(ret19=30, Pc=29.9, gs_line=2.89, gs_min=2.87, D10v="< 0,075 (pasa 11 % por 0,075 mm; no medible por tamizado)",
               sucs=("NO verificable: Cc = 0,11 sale del D10 erróneo; con D10 entre 0,059 y 0,075 mm sería Cc 2,4-3,0 (GW-GM) "
                     "y con D10 < 0,059 mm sería GP-GM"),
               bloq="Mármol 2,70 / Horfels 2,70 (proporción de la mezcla no indicada)"),
    "P2": dict(ret19=27, Pc=27.3, gs_line=2.73, gs_min=2.68, D10v="0,084 (coincide con el 0,08 informado)",
               sucs="GW-GM verificable (Cu 137, Cc 2,3)", bloq="Intrusivo P50 2,45 (2,40-2,52)"),
}
rows = []
for i, r in ix.iterrows():
    k = key_of(r.fuente)
    e = extra[k]
    row = r.to_dict()
    row["Gs_origen"] = "rótulo «Curva 100% saturación (Gs= x)» del gráfico Proctor; no hay ensayo ASTM D854; fracción < 19 mm"
    row["Gs_linea_saturacion_calc"] = e["gs_line"]
    row["Gs_minimo_Sr1_Proctor_calc"] = e["gs_min"]
    row["retenido_19mm_pct"] = e["ret19"]
    row["sobretamano_Pc_calc_pct"] = e["Pc"]
    row["D10_verificado_mm"] = e["D10v"]
    row["SUCS_verificacion"] = e["sucs"]
    row["densidad_bloques_LE2_t_m3"] = e["bloq"]
    row["w_natural_condicion"] = ("humedad de la muestra tal como se recibió (recepción 2023-11-23 o 2024-09-03, ensayo meses después); "
                                  "no es la humedad in situ")
    row["verificado_imagen"] = "sí"
    row["notas_verificacion"] = (
        "Verificado 2026-10-06 contra la imagen de SUCS p.1-2, Proctor p.1 y CA p.1. D10 = 1,54 mm (M, H, P1) es un valor erróneo del formato "
        "(idéntico en tres muestras); los Cu y Cc informados salen de él. "
        f"«Fuera de método»/«Método C»: el % retenido en 3/4 in es {e['ret19']} % (ASTM D698 Método C admite hasta 30 %). La corrección por sobretamaño del propio informe "
        f"implica Pc = {e['Pc']} %, igual al retenido en 3/4 in, de modo que el Proctor se hizo sobre la fracción < 19 mm. "
        f"La línea de saturación dibujada corresponde a Gs ≈ {e['gs_line']} (rótulo {r.Gs}), y el punto Proctor más húmedo exige Gs ≥ {e['gs_min']} para que Sr ≤ 1.")
    rows.append(row)
pd.DataFrame(rows).to_csv(ver / "ensayos_indices_verificado.csv", index=False, encoding="utf-8")
print("ok", len(txv), len(rows))
print(txv[["ensayo_id", "set_id", "pico_local_previo"]].to_string())
