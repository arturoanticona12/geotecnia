"""Extrae proporción de litologías y propiedades de roca por litología.

Salidas en ...\\Aporte_alto_confinamiento\\datos_antamina\\extraido\\
  - litologias_proporcion.csv
  - propiedades_roca_por_litologia.csv
Supuestos (verificados en 02_relaciones_salida.txt):
  - SIMULACIONES: bloque de 20 x 20 x 15 m (grilla rotada 45°, espaciamiento 20 m en u y v,
    15 m en Z) -> 6000 m3 por bloque; toneladas = 6000 * MR24_BD.
  - Grupo litológico de cada código RT tomado de las etiquetas Geologia_2024 del propio
    archivo de ensayes (p. ej. 'Metamorfico_16'). Códigos sin etiqueta -> 'sin leyenda'.
"""
from pathlib import Path
import numpy as np
import pandas as pd

BASE = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3"
            r"\Revisión de literatura\Leps 2.0")
SRC = BASE / "Data Antamina" / "250903 Waste Charact"
OUT = BASE / "Aporte_alto_confinamiento" / "datos_antamina" / "extraido"
OUT.mkdir(parents=True, exist_ok=True)

sim = pd.read_csv(SRC / "SIMULACIONES_MR2024_V3.csv", skiprows=1)
asy = pd.read_csv(SRC / "Merged_Table_Assay_lito_12JUNIO2025_ult.csv", low_memory=False)
asy["largo_m"] = asy["to"] - asy["from"]

# ---- leyenda de grupo desde Geologia_2024 (dato del archivo, no interpretación) ----
lab = asy["Geologia_2024"].dropna().unique()
grupo_rt = {int(s.rsplit("_", 1)[1]): s.rsplit("_", 1)[0] for s in lab}
def grupo(code):
    try:
        return grupo_rt.get(int(code), "sin leyenda")
    except (ValueError, TypeError):
        return "sin leyenda"

VOL = 20 * 20 * 15
sim["vol_m3"] = VOL
sim["t"] = VOL * sim["MR24_BD"]
sim["periodo"] = sim["XLE2WST_AMIN"].astype(str)
sim["anio_LOM25"] = sim["LOM25_AMIN_LE2"].astype("Int64").astype(str).replace("<NA>", "sin dato")
sim["fase_LOM25"] = sim["LOM25_FASES_LE2"].fillna("sin dato").astype(str)

filas = []
def acumula(df, archivo, base, agrup_col, agrup_nombre, lito_col, lito_nombre, medidas):
    keys = [lito_col] if agrup_col is None else [agrup_col, lito_col]
    g = df.groupby(keys, dropna=False)[list(medidas)].sum().reset_index()
    n = df.groupby(keys, dropna=False).size().reset_index(name="n_registros")
    g = g.merge(n, on=keys)
    if agrup_col is None:
        g["agrupacion"] = "total"; g["clave"] = "total"
    else:
        g["agrupacion"] = agrup_nombre; g["clave"] = g[agrup_col].astype(str)
    base_col = medidas[0]
    g["pct"] = 100 * g[base_col] / g.groupby("clave")[base_col].transform("sum")
    g["archivo"] = archivo; g["base_medida"] = base
    g["codigo_tipo"] = lito_nombre
    g["litologia_codigo"] = g[lito_col].astype(str)
    g["grupo_geologia_2024"] = g[lito_col].map(grupo) if lito_nombre != "ROCKCODE" else \
        g[lito_col].map(rc2num).map(grupo)
    for m in ("toneladas", "volumen_m3", "metros", "n_registros"):
        if m not in g:
            g[m] = np.nan
    filas.append(g[["archivo", "base_medida", "agrupacion", "clave", "codigo_tipo",
                    "litologia_codigo", "grupo_geologia_2024", "n_registros",
                    "volumen_m3", "toneladas", "metros", "pct"]])

rc2num = asy.groupby("ROCKCODE")["ROCKCODE_NUMEQ"].agg(lambda s: s.mode().iloc[0])

s2 = sim.rename(columns={"t": "toneladas", "vol_m3": "volumen_m3"})
for col, nom in ((None, None), ("periodo", "periodo_XLE2WST_AMIN"),
                 ("anio_LOM25", "anio_LOM25_AMIN_LE2"), ("fase_LOM25", "fase_LOM25_FASES_LE2")):
    acumula(s2, "SIMULACIONES_MR2024_V3", "toneladas (6000 m3 x MR24_BD); pct sobre toneladas",
            col, nom, "MR24_RT", "MR24_RT", ["toneladas", "volumen_m3"])

a2 = asy.rename(columns={"largo_m": "metros"})
a2["periodo"] = a2["GM_LE2WASTE_Output"].astype(str)
for lc in ("ROCKCODE_NUMEQ", "ROCKCODE"):
    for col, nom in ((None, None), ("periodo", "periodo_GM_LE2WASTE_Output"),
                     ("plp_GM_FASES_LE2_Output", "fase_plp_GM_FASES_LE2_Output")):
        acumula(a2, "Merged_Table_Assay_lito", "metros de sondaje; pct sobre metros",
                col, nom, lc, lc, ["metros"])

prop = pd.concat(filas, ignore_index=True)
prop["pct"] = prop["pct"].round(3)
prop["toneladas"] = prop["toneladas"].round(0)
prop["metros"] = prop["metros"].round(2)
prop.to_csv(OUT / "litologias_proporcion.csv", index=False, encoding="utf-8-sig")

# ---------------- propiedades por litología ----------------
def stats(series, w=None):
    s = series.dropna()
    d = {"n": len(s)}
    if len(s) == 0:
        return d
    q = s.quantile([.05, .10, .25, .5, .75, .90, .95])
    d.update(media=s.mean(), desv_est=s.std(), cv=s.std() / s.mean() if s.mean() else np.nan,
             min=s.min(), p05=q[.05], p10=q[.10], p25=q[.25], p50=q[.5], p75=q[.75],
             p90=q[.90], p95=q[.95], max=s.max())
    if w is not None:
        ww = w.loc[s.index]
        d["media_pond"] = np.average(s, weights=ww) if ww.sum() > 0 else np.nan
    return d

rows = []
def agrega(df, archivo, var, unidad, lito_col, codigo_tipo, nota, w=None, filtro=None):
    d = df if filtro is None else df[filtro]
    for code, sub in d.groupby(lito_col):
        r = stats(sub[var], None if w is None else sub[w])
        rows.append(dict(archivo=archivo, variable=var, unidad=unidad, codigo_tipo=codigo_tipo,
                         litologia_codigo=str(code), grupo_geologia_2024=grupo(str(code).split("_")[0]),
                         nota=nota, **r))
    r = stats(d[var], None if w is None else d[w])
    rows.append(dict(archivo=archivo, variable=var, unidad=unidad, codigo_tipo=codigo_tipo,
                     litologia_codigo="TODOS", grupo_geologia_2024="", nota=nota, **r))

SIMN = "SIMULACIONES_MR2024_V3"
nota_sim = "estadística sobre bloques del modelo (cada bloque 6000 m3); valores modelados, no ensayos"
for v, u in (("MR24_BD", "t/m3"), ("MR24_UCS", "MPa"), ("MR24_ABRA", "sin unidad declarada"),
             ("MR24_AXB", "sin unidad declarada"), ("MR24_BWI", "sin unidad declarada (kWh/t?)")):
    agrega(sim, SIMN, v, u, "MR24_RT", "MR24_RT", nota_sim)

AS = "Merged_Table_Assay_lito"
asy["RT_UCS_Fuente"] = asy["RT_UCS"] + "|" + asy["Fuente"].fillna("")
agrega(asy, AS, "UCS_MPa", "MPa", "RT_UCS", "RT_UCS",
       "todas las fuentes (Core_PLT + Core_UCS)", filtro=asy.UCS_MPa.notna())
agrega(asy, AS, "UCS_MPa", "MPa", "RT_UCS_Fuente", "RT_UCS|Fuente",
       "separado por fuente: Core_PLT (carga puntual) / Core_UCS", filtro=asy.UCS_MPa.notna())
agrega(asy, AS, "UCS_MPa", "MPa", "Lithology", "Lithology",
       "UCS por código Lithology (texto libre de la base geotécnica)", filtro=asy.UCS_MPa.notna())
agrega(asy, AS, "RQD_pc", "%", "RT_RQD", "RT_RQD",
       "media_pond = ponderada por largo de intervalo", w="largo_m", filtro=asy.RQD_pc.notna())
agrega(asy, AS, "RQD_pc", "%", "ROCKCODE", "ROCKCODE",
       "media_pond = ponderada por largo de intervalo", w="largo_m", filtro=asy.RQD_pc.notna())
agrega(asy, AS, "ABRASION_pc", "%", "RT_Abrasion", "RT_Abrasion", "",
       filtro=asy.ABRASION_pc.notna())
agrega(asy, AS, "DTADJ", "t/m3 (supuesto)", "ROCA", "ROCA",
       "densidad ajustada (DTADJ) por código ROCA", filtro=asy.DTADJ.notna())

pr = pd.DataFrame(rows)
num = pr.select_dtypes("number").columns.drop("n")
pr[num] = pr[num].round(4)
pr["litologia_codigo"] = pr["litologia_codigo"].str.replace(r"\.0$", "", regex=True)
pr["grupo_geologia_2024"] = [grupo(c.split("_")[0].split("|")[0]) if c != "TODOS" else ""
                             for c in pr["litologia_codigo"]]
pr.loc[pr.codigo_tipo.isin(["Lithology", "ROCKCODE"]), "grupo_geologia_2024"] = \
    pr.loc[pr.codigo_tipo.isin(["Lithology", "ROCKCODE"]), "litologia_codigo"].map(
        lambda c: grupo(rc2num.get(c, np.nan)))
pr.to_csv(OUT / "propiedades_roca_por_litologia.csv", index=False, encoding="utf-8-sig")

# ---------------- resúmenes en pantalla para el informe ----------------
print("leyenda grupos:", dict(sorted(grupo_rt.items())))
print("ROCKCODE->NUMEQ:", rc2num.to_dict())
t = prop[(prop.archivo == SIMN) & (prop.agrupacion == "total")]
print("\nSIM total:\n", t[["litologia_codigo", "grupo_geologia_2024", "n_registros",
                          "toneladas", "pct"]].sort_values("pct", ascending=False).to_string())
print("Total t:", t.toneladas.sum(), " Mm3:", t.volumen_m3.sum() / 1e6)
gp = t.groupby("grupo_geologia_2024")["pct"].sum()
print(gp.to_string())
for lc in ("ROCKCODE_NUMEQ", "ROCKCODE"):
    t2 = prop[(prop.archivo == AS) & (prop.agrupacion == "total") & (prop.codigo_tipo == lc)]
    print(f"\nASSAY total {lc}:\n", t2[["litologia_codigo", "grupo_geologia_2024", "metros", "pct"]]
          .sort_values("pct", ascending=False).to_string())
    print("Total m:", t2.metros.sum())
pp = prop[(prop.archivo == SIMN) & (prop.agrupacion == "periodo_XLE2WST_AMIN")]
print("\nSIM pct por periodo:\n", pp.pivot(index="clave", columns="litologia_codigo",
                                          values="pct").round(1).to_string())
print("\nSIM Mt por periodo:\n", (pp.groupby("clave").toneladas.sum() / 1e6).round(1).to_string())
pf = prop[(prop.archivo == SIMN) & (prop.agrupacion == "fase_LOM25_FASES_LE2")]
print("\nSIM pct por fase:\n", pf.pivot(index="clave", columns="litologia_codigo",
                                       values="pct").round(1).to_string())
ps = pr[(pr.archivo == SIMN)]
print("\nSIM props:\n", ps.pivot(index="litologia_codigo", columns="variable",
                                values="p50").to_string())
pu = pr[(pr.variable == "UCS_MPa") & (pr.codigo_tipo == "RT_UCS|Fuente")]
print("\nUCS por RT|Fuente:\n", pu[["litologia_codigo", "n", "media", "p50", "cv"]].to_string())
pq = pr[(pr.variable == "RQD_pc") & (pr.codigo_tipo == "RT_RQD")]
print("\nRQD por RT:\n", pq[["litologia_codigo", "n", "media_pond", "p25", "p50"]].to_string())
pd_ = pr[(pr.variable == "DTADJ")]
print("\nDTADJ:\n", pd_[["litologia_codigo", "n", "media", "p50"]].to_string())
pa = pr[(pr.variable == "ABRASION_pc")]
print("\nABRASION:\n", pa[["litologia_codigo", "n", "media", "p50"]].to_string())
print("\nfilas proporcion:", len(prop), " filas propiedades:", len(pr))
