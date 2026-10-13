"""Relaciones entre códigos, tamaño de bloque y consistencia entre archivos."""
from pathlib import Path
import numpy as np
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_rows", 400)

BASE = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3"
            r"\Revisión de literatura\Leps 2.0\Data Antamina\250903 Waste Charact")
sim = pd.read_csv(BASE / "SIMULACIONES_MR2024_V3.csv", skiprows=1)
asy = pd.read_csv(BASE / "Merged_Table_Assay_lito_12JUNIO2025_ult.csv", low_memory=False)

print("== Grilla rotada: u=(X+Y)/sqrt2, v=(Y-X)/sqrt2 ==")
u = (sim.X + sim.Y) / np.sqrt(2); v = (sim.Y - sim.X) / np.sqrt(2)
for n, s in (("u", u), ("v", v)):
    d = pd.Series(np.sort(s.round(2).unique())).diff().round(2).value_counts().head(4)
    print(n, d.to_dict())
print("duplicados XYZ:", sim.duplicated(["X", "Y", "Z"]).sum())

print("\n== SIM: XLE2WST_AMIN vs LOM25_AMIN_LE2 ==")
print(pd.crosstab(sim.XLE2WST_AMIN, sim.LOM25_AMIN_LE2.fillna(-1)).to_string())
print("\n== SIM: LOM25_FASES_LE2 vs XLE2WST_AMIN ==")
print(pd.crosstab(sim.LOM25_FASES_LE2.fillna("NaN"), sim.XLE2WST_AMIN).to_string())

print("\n== SIM: estadísticas por MR24_RT ==")
g = sim.groupby("MR24_RT")[["MR24_BD", "MR24_UCS", "MR24_ABRA", "MR24_AXB", "MR24_BWI"]]
print(g.agg(["count", "mean", "std", "min", "max"]).round(3).to_string())
print("\nValores modales por RT (¿asignación constante?):")
for c in ["MR24_AXB", "MR24_BWI", "MR24_ABRA", "MR24_UCS", "MR24_BD"]:
    m = sim.groupby("MR24_RT")[c].agg(lambda s: s.value_counts(normalize=True).iloc[0])
    print(c, m.round(3).to_dict())

print("\n== ASSAY: ROCKCODE -> ROCKCODE_NUMEQ ==")
print(pd.crosstab(asy.ROCKCODE, asy.ROCKCODE_NUMEQ).to_string())
print("\n== ASSAY: Geologia_2024 -> ROCA ==")
print(pd.crosstab(asy.Geologia_2024, asy.ROCA).to_string())
print("\n== ASSAY: RT_UCS prefijo vs ROCA ==")
geo = asy[asy.Fuente.notna()].copy()
geo["rt_ucs_num"] = geo.RT_UCS.str.split("_").str[0]
print(pd.crosstab(geo.rt_ucs_num, geo.ROCA.fillna(-1)).to_string())
print("\n== ASSAY: ROCKCODE_NUMEQ vs ROCA (filas geotec) ==")
print(pd.crosstab(geo.ROCKCODE_NUMEQ, geo.ROCA.fillna(-1)).to_string())
print("\n== ASSAY: Lithology vs ROCKCODE (top) ==")
ct = pd.crosstab(geo.Lithology, geo.ROCKCODE)
print((ct.idxmax(axis=1) + " " + (ct.max(axis=1) / ct.sum(axis=1)).round(2).astype(str)).to_string())

print("\n== ASSAY: RT_RQD prefijo vs ROCKCODE_NUMEQ ==")
r = asy[asy.RT_RQD.notna()].copy()
r["rq"] = r.RT_RQD.str.split("_").str[0]
print(pd.crosstab(r.rq, r.ROCKCODE_NUMEQ).to_string())

print("\n== ASSAY: GM_LE2WASTE vs plp_GM_YEAR ==")
print(pd.crosstab(asy.GM_LE2WASTE_Output, asy.plp_GM_YEAR_LE2_Output).to_string())
print("\n== ASSAY: GM_YEAR vs GM_LE2WASTE ==")
print(pd.crosstab(asy.GM_YEAR_LE2_Output, asy.GM_LE2WASTE_Output).to_string())

print("\n== ASSAY: duplicación de intervalos ==")
print("dup holeid/from/to:", asy.duplicated(["holeid", "from", "to"]).sum())
print("solapes:", (asy.sort_values(["holeid", "from"]).groupby("holeid")["from"].shift(-1)
                   < asy.sort_values(["holeid", "from"])["to"]).sum())
print("SAMPLETYPE en filas Fuente:", geo.groupby("Fuente").SAMPLETYPE.value_counts().head(20).to_string())
print("\nfilas con ROCA vs Fuente:", pd.crosstab(asy.ROCA.notna(), asy.Fuente.fillna("NaN")).to_string())
print("\nUCS por Fuente:\n", geo.groupby("Fuente").UCS_MPa.describe().to_string())
print("\nDTADJ (nota: solo donde ROCA no nula):\n", asy.DTADJ.describe().to_string())
