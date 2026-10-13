"""UCS de referencia por litología: compresión uniaxial directa (Core_UCS) frente a carga puntual convertida (Core_PLT)
y frente al modelo de bloques. Sondajes LE2 (Merged_Table) y RMU LE2 (indices_roca_LE2)."""
import sys
from pathlib import Path
import pandas as pd, numpy as np
sys.stdout.reconfigure(encoding="utf-8"); pd.set_option("display.width", 220)
D = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\250903 Waste Charact")
R = Path(__file__).parent
LEY = {1: "Intrusivo", 10: "Caliza y margas (sedimentario)", 13: "Hornfels", 14: "Hornfels diópsido", 16: "Mármol", 19: "Mármol diópsido"}
sj = pd.read_csv(D / "Merged_Table_Assay_lito_12JUNIO2025_ult.csv", low_memory=False, usecols=["ROCKCODE_NUMEQ", "Fuente", "UCS_MPa", "RT_UCS"])
sj = sj.dropna(subset=["UCS_MPa"])
print("Fuente de UCS:", sj.Fuente.value_counts().to_dict())
t = sj.groupby(["ROCKCODE_NUMEQ", "Fuente"]).UCS_MPa.agg(["size", "median", "mean"]).unstack("Fuente")
t.columns = [f"{a}_{b}" for a, b in t.columns]
for c in [c for c in t.columns if c.startswith("median")]:
    pass
med = t.filter(like="median")
if med.shape[1] == 2:
    a, b = med.columns
    t["razon_PLT_sobre_UCS"] = t[[c for c in med.columns if "PLT" in c][0]] / t[[c for c in med.columns if "UCS" in c and "PLT" not in c][0]]
t.insert(0, "litologia", [LEY.get(int(i), "?") for i in t.index])
print(t.round(2).to_string())
bm = pd.read_csv(R / "base" / "modelo_bloques_por_RT.csv")
print("\nModelo de bloques (MR24_UCS) mediana por RT:\n", bm[["MR24_RT", "UCS_mediana", "n_bloques"]].to_string(index=False))
t.to_csv(R / "base" / "ucs_directa_vs_plt.csv")
