"""Reconstrucción de la leyenda de códigos de roca (MR24_RT y ROCKCODE) con evidencia cuantitativa:
número de bloques y UCS del modelo MR2024 frente a la tabla de WSC lámina 12, grupo Geologia_2024 y siglas de sondaje."""
import sys
from pathlib import Path
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_colwidth", 70)
D = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\250903 Waste Charact")
R = Path(__file__).parent

# 1) modelo de bloques: estadísticas por RT
bm = pd.read_csv(D / "SIMULACIONES_MR2024_V3.csv", low_memory=False, skiprows=1)
bm["ton"] = 6000 * bm.MR24_BD
g = bm.groupby("MR24_RT").agg(n_bloques=("MR24_RT", "size"), UCS_media=("MR24_UCS", "mean"), UCS_mediana=("MR24_UCS", "median"),
                              BD_media=("MR24_BD", "mean"), ton=("ton", "sum")).reset_index()
g["pct_ton"] = 100 * g.ton / g.ton.sum()
print("Modelo de bloques MR2024 por código RT:\n", g.round(2).to_string(index=False))

# 2) tabla de WSC lámina 12 (extraída a caracterizacion_muestras.csv)
cm = pd.read_csv(R / "extraido" / "caracterizacion_muestras.csv", low_memory=False)
l12 = cm[cm.astype(str).apply(lambda r: r.str.contains("lámina 12|lamina 12|L12", case=False).any(), axis=1)]
cols = [c for c in l12.columns if l12[c].notna().any()]
print("\nFilas de WSC lámina 12 en la extracción:", len(l12)); print(l12[cols].head(40).to_string())

# 3) sondajes: ROCKCODE → ROCKCODE_NUMEQ, Lithology, Geologia_2024
sj = pd.read_csv(D / "Merged_Table_Assay_lito_12JUNIO2025_ult.csv", low_memory=False,
                 usecols=lambda c: c in {"ROCKCODE", "ROCKCODE_NUMEQ", "Lithology", "Geologia_2024", "RT_UCS", "UCS_MPa", "from", "to"})
sj["m"] = sj["to"] - sj["from"]
t = sj.groupby(["ROCKCODE", "ROCKCODE_NUMEQ"], dropna=False).agg(metros=("m", "sum"), lith=("Lithology", lambda x: x.mode().iat[0] if x.notna().any() else ""),
                                                                 geo=("Geologia_2024", lambda x: x.mode().iat[0] if x.notna().any() else "")).reset_index()
t = t.sort_values("metros", ascending=False)
print("\nSondajes: ROCKCODE → NUMEQ, litología textual y grupo:\n", t.round(0).to_string(index=False))
print("\nGeologia_2024 por NUMEQ:\n", sj.groupby("ROCKCODE_NUMEQ").Geologia_2024.agg(lambda x: x.value_counts().head(3).to_dict()).to_string())
g.to_csv(R / "base" / "modelo_bloques_por_RT.csv", index=False); t.to_csv(R / "base" / "sondajes_rockcode.csv", index=False)

