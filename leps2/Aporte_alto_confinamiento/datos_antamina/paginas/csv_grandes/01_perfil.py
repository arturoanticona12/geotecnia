"""Perfilado de los dos CSV grandes de Waste Characterization (Antamina)."""
from pathlib import Path
import pandas as pd

pd.set_option("display.width", 250)
pd.set_option("display.max_columns", 60)
pd.set_option("display.max_rows", 400)

BASE = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3"
            r"\Revisión de literatura\Leps 2.0\Data Antamina\250903 Waste Charact")
SIM = BASE / "SIMULACIONES_MR2024_V3.csv"
ASY = BASE / "Merged_Table_Assay_lito_12JUNIO2025_ult.csv"


def perfil(df, nombre, max_uni=60):
    print("=" * 100)
    print(nombre, "filas:", len(df), "columnas:", df.shape[1])
    print(df.dtypes.to_string())
    print("\n-- nulos por columna --")
    print(df.isna().sum().to_string())
    print("\n-- n únicos --")
    print(df.nunique().to_string())
    num = df.select_dtypes("number")
    print("\n-- describe numéricas --")
    print(num.describe(percentiles=[.05, .25, .5, .75, .95]).T.to_string())
    for c in df.columns:
        nu = df[c].nunique()
        if df[c].dtype == object or nu <= max_uni:
            vc = df[c].value_counts(dropna=False)
            print(f"\n-- value_counts {c} (n únicos={nu}) --")
            print(vc.head(max_uni).to_string())


sim = pd.read_csv(SIM, skiprows=1, encoding="utf-8")
perfil(sim, "SIMULACIONES_MR2024_V3")
# espaciamiento de la grilla
for c in "XYZ":
    u = sorted(sim[c].unique())
    d = pd.Series(u).diff().round(3).value_counts().head(5)
    print(f"\n{c}: min {u[0]} max {u[-1]} n {len(u)}; diffs más comunes:\n{d.to_string()}")

for enc in ("utf-8", "latin-1"):
    try:
        asy = pd.read_csv(ASY, encoding=enc, low_memory=False)
        print("\nASSAY leído con", enc)
        break
    except UnicodeDecodeError as e:
        print(enc, "falla:", e)
perfil(asy, "Merged_Table_Assay_lito")
asy["len"] = asy["to"] - asy["from"]
print("\nlongitud de intervalo:\n", asy["len"].describe().to_string())
print("n sondajes:", asy["holeid"].nunique())
