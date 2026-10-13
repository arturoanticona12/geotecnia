import pandas as pd
f=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\250903 Waste Charact\SIMULACIONES_MR2024_V3.csv"
df=pd.read_csv(f,skiprows=1)
print(len(df))
g=df.groupby("MR24_RT").agg(n=("MR24_UCS","count"),ucs_mean=("MR24_UCS","mean"),ucs_p50=("MR24_UCS","median"),ucs_std=("MR24_UCS","std"),bd_n=("MR24_BD","count"),bd_p50=("MR24_BD","median"),bd_mean=("MR24_BD","mean"),bd_p16=("MR24_BD",lambda s:s.quantile(.16)),bd_p84=("MR24_BD",lambda s:s.quantile(.84)),bd_min=("MR24_BD","min"),bd_max=("MR24_BD","max"))
print(g.round(3).to_string())
