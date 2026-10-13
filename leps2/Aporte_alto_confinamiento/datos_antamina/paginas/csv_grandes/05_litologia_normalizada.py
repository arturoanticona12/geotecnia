"""Agrega litologia_normalizada (Intrusivo, Hornfels, Mármol, Skarn, Caliza, Otra, sin asignar)
a los CSV extraídos, conservando el código original.

Regla: solo se asigna cuando el propio dato lo dice:
  - RT 1, 2 -> Intrusivo (etiqueta Geologia_2024 'Intrusivo_1/2'); ROCKCODE con NUMEQ 1 -> Intrusivo.
  - RT 20, 22, 23 -> Skarn (subtipo Endoskarn); RT 31-37 -> Skarn (subtipo Exoskarn) (etiquetas Geologia_2024).
  - RT 50 -> Otra (subtipo Brechas) (etiqueta 'Brechas_50').
  - Lithology 'Marble' -> Mármol; 'Diop. Hornfels' -> Hornfels (texto explícito).
  - Todo lo demás -> 'sin asignar'.
Columna aparte 'litologia_tentativa': hipótesis por la inicial de las siglas ROCKCODE agrupadas en cada código
(H* -> Hornfels, M* -> Mármol, C* -> Caliza), apoyada en Lithology 'Diop. Hornfels' ~ HGV (NUMEQ 14) y
'Marble' ~ MCGB (NUMEQ 16). NO es leyenda oficial: debe confirmarla el cliente.
"""
from pathlib import Path
import re
import pandas as pd

OUT = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura"
           r"\Leps 2.0\Aporte_alto_confinamiento\datos_antamina\extraido")

SA = "sin asignar"
# código RT numérico -> (normalizada, subtipo, criterio, tentativa)
RT = {
    1: ("Intrusivo", "RT1", "Geologia_2024=Intrusivo_1", "Intrusivo"),
    2: ("Intrusivo", "RT2", "Geologia_2024=Intrusivo_2", "Intrusivo"),
    10: (SA, "Sedimentario_10", "Geologia_2024=Sedimentario_10 (no especifica caliza)", "Caliza (hipótesis: siglas C*)"),
    11: (SA, "Sedimentario_11", "Geologia_2024=Sedimentario_11 (no especifica caliza)", "Caliza (hipótesis: Sedimentario; RT11~NUMEQ10, siglas C*)"),
    13: (SA, "Metamorfico_13", "Geologia_2024=Metamorfico_13 (no distingue hornfels/mármol)", "Hornfels (hipótesis: siglas HG, HGS, HC)"),
    14: (SA, "Metamorfico_14", "Geologia_2024=Metamorfico_14 (no distingue hornfels/mármol)", "Hornfels (hipótesis: siglas HBV, HGV, HCB, HDP; 'Diop. Hornfels'~HGV)"),
    16: (SA, "Metamorfico_16", "Geologia_2024=Metamorfico_16 (no distingue hornfels/mármol)", "Mármol (hipótesis: siglas MC, MG, MGS, MPA, MCGB; 'Marble'~MCGB)"),
    19: (SA, "Metamorfico_19", "Geologia_2024=Metamorfico_19 (no distingue hornfels/mármol)", "Mármol (hipótesis: sigla MDP)"),
    20: ("Skarn", "Endoskarn_20", "Geologia_2024=Endoskarn_20", "Skarn"),
    22: ("Skarn", "Endoskarn_22", "Geologia_2024=Endoskarn_22", "Skarn"),
    23: ("Skarn", "Endoskarn_23", "Geologia_2024=Endoskarn_23", "Skarn"),
    50: ("Otra", "Brechas_50", "Geologia_2024=Brechas_50", "Otra (Brechas)"),
}
for c in (31, 32, 34, 35, 36, 37):
    RT[c] = ("Skarn", f"Exoskarn_{c}", f"Geologia_2024=Exoskarn_{c}", "Skarn")
for c in (51, 52, 53):
    RT[c] = (SA, f"RT{c}", "código sin etiqueta en los datos", "sin hipótesis")

NUMEQ_TENT = {1: "Intrusivo", 10: "Caliza (hipótesis: siglas C*)", 13: "Hornfels (hipótesis: siglas H*)",
              14: "Hornfels (hipótesis: siglas H*)", 16: "Mármol (hipótesis: siglas M*)",
              19: "Mármol (hipótesis: sigla MDP)"}
ROCK2NUM = {'BCHG': 13, 'BCIPPA': 1, 'BCIPPAO': 1, 'BCIPPEO': 1, 'BCM': 16, 'BMHG': 13, 'BMIPPA': 1, 'C': 10,
            'CA': 10, 'CBMN': 10, 'CF': 10, 'CG': 10, 'CGS': 10, 'CM': 10, 'CN': 10, 'DI': 1, 'HBV': 14, 'HC': 13,
            'HCB': 14, 'HDP': 14, 'HG': 13, 'HGS': 13, 'HGV': 14, 'HMGV': 14, 'HV': 14, 'IPHPE': 1, 'IPPA': 1,
            'IPPAMO': 1, 'IPPAO': 1, 'IPPEO': 1, 'M': 16, 'MC': 16, 'MCB': 16, 'MCGB': 16, 'MDL': 16, 'MDP': 19,
            'MG': 16, 'MGS': 16, 'MPA': 16}


def por_rockcode(sig):
    n = ROCK2NUM.get(sig)
    if n is None:
        return None
    if n == 1:
        return ("Intrusivo", sig, "ROCKCODE agrupado en ROCKCODE_NUMEQ=1 (Intrusivo_1)", "Intrusivo")
    return (SA, sig, f"ROCKCODE agrupado en ROCKCODE_NUMEQ={n}; sigla sin leyenda", NUMEQ_TENT[n])


def asigna(codigo_tipo, codigo):
    c = str(codigo)
    if c in ("TODOS", "total"):
        return ("", "", "", "")
    if codigo_tipo in ("ROCKCODE",):
        return por_rockcode(c) or (SA, c, "sigla no reconocida", "sin hipótesis")
    if codigo_tipo == "ROCKCODE_NUMEQ":
        n = int(float(c))
        base = ("Intrusivo", f"NUMEQ{n}", "ROCKCODE_NUMEQ=1 agrupa siglas IPP*/DI", "Intrusivo") if n == 1 else \
            (SA, f"NUMEQ{n}", "ROCKCODE_NUMEQ sin leyenda (no equivale 1:1 al RT)", NUMEQ_TENT[n])
        return base
    if codigo_tipo == "Lithology":
        if c == "Marble":
            return ("Mármol", c, "texto Lithology explícito", "Mármol")
        if c == "Diop. Hornfels":
            return ("Hornfels", c, "texto Lithology explícito", "Hornfels")
        first = re.split(r"[ /&]+", c)[0]
        r = por_rockcode(first)
        if r and first == c:
            return r
        if r:  # mezcla de siglas
            return (SA if r[0] != "Intrusivo" or not set(re.split(r"[ /&]+", c)) <= {k for k, v in ROCK2NUM.items() if v == 1} else "Intrusivo",
                    c, "texto Lithology compuesto", r[3] + " (mezcla)")
        return (SA, c, "texto Lithology sin equivalente ROCKCODE", "sin hipótesis")
    # códigos RT (MR24_RT, ROCA, RT_UCS, RT_RQD, RT_Abrasion, 'RT|Fuente')
    m = re.match(r"^(\d+)", c)
    if not m:
        return (SA, c, "código no numérico", "sin hipótesis")
    n = int(m.group(1))
    norm, sub, crit, tent = RT.get(n, (SA, f"RT{n}", "código sin etiqueta", "sin hipótesis"))
    return (norm, sub, crit, tent)


def anota(df):
    res = [asigna(t, c) for t, c in zip(df["codigo_tipo"], df["litologia_codigo"])]
    df = df.drop(columns=[k for k in ("litologia_normalizada", "subtipo", "criterio_asignacion",
                                      "litologia_tentativa") if k in df], errors="ignore")
    pos = df.columns.get_loc("litologia_codigo") + 1
    for i, name in enumerate(("litologia_normalizada", "subtipo", "criterio_asignacion", "litologia_tentativa")):
        df.insert(pos + i, name, [r[i] for r in res])
    return df


prop = pd.read_csv(OUT / "litologias_proporcion.csv", dtype={"litologia_codigo": str, "clave": str})
prop = prop[~prop.codigo_tipo.isin(["litologia_normalizada", "litologia_tentativa"])]
prop = anota(prop)

# filas agregadas por litología normalizada y tentativa (mismas agrupaciones)
extra = []
base_codes = prop[prop.codigo_tipo.isin(["MR24_RT", "ROCKCODE"])]
for col in ("litologia_normalizada", "litologia_tentativa"):
    g = (base_codes.groupby(["archivo", "base_medida", "agrupacion", "clave", col], dropna=False)
         [["n_registros", "volumen_m3", "toneladas", "metros", "pct"]].sum(min_count=1).reset_index())
    g["codigo_tipo"] = col
    g["litologia_codigo"] = g[col]
    g["litologia_normalizada"] = g[col] if col == "litologia_normalizada" else ""
    g["subtipo"] = ""; g["criterio_asignacion"] = "suma de filas por código"
    g["litologia_tentativa"] = g[col] if col == "litologia_tentativa" else ""
    g["grupo_geologia_2024"] = ""
    extra.append(g[prop.columns])
prop = pd.concat([prop] + extra, ignore_index=True)
prop["pct"] = prop["pct"].round(3)
prop.to_csv(OUT / "litologias_proporcion.csv", index=False, encoding="utf-8-sig")

pr = pd.read_csv(OUT / "propiedades_roca_por_litologia.csv", dtype={"litologia_codigo": str})
pr = anota(pr)
pr.to_csv(OUT / "propiedades_roca_por_litologia.csv", index=False, encoding="utf-8-sig")

# ------- resumen -------
pd.set_option("display.width", 250)
for arch, ct in (("SIMULACIONES_MR2024_V3", None), ("Merged_Table_Assay_lito", None)):
    for col in ("litologia_normalizada", "litologia_tentativa"):
        t = prop[(prop.archivo == arch) & (prop.agrupacion == "total") & (prop.codigo_tipo == col)]
        print(f"\n{arch} total por {col}:\n", t[["litologia_codigo", "toneladas", "metros", "pct"]].to_string())
t = prop[(prop.archivo == "SIMULACIONES_MR2024_V3") & (prop.agrupacion == "periodo_XLE2WST_AMIN")
         & (prop.codigo_tipo == "litologia_tentativa")]
print("\nSIM por período (tentativa, %):\n", t.pivot(index="clave", columns="litologia_codigo", values="pct").round(1).to_string())
print("\nAsignación por código (propiedades):")
print(pr[["codigo_tipo", "litologia_codigo", "litologia_normalizada", "litologia_tentativa"]]
      .drop_duplicates(["codigo_tipo", "litologia_codigo"]).query("codigo_tipo in ['MR24_RT','ROCA','Lithology']").to_string())
print("\nsin asignar por codigo_tipo (propiedades):\n", pr[pr.litologia_normalizada == SA].groupby("codigo_tipo").size().to_string())
print("filas:", len(prop), len(pr))
