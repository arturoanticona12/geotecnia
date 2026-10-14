"""Inspección rápida de Fragmentación Desmonte 2025.xlsx (¿clase ROM/Chancado/Enrocado?)."""
from pathlib import Path
import pandas as pd
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 40)
F = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura"
         r"\Leps 2.0\Data Antamina\250903 Waste Charact\Fragmentación Desmonte 2025.xlsx")
for name, df in pd.read_excel(F, sheet_name=None, header=None).items():
    print("=" * 80, "\nHOJA:", name, df.shape)
    print(df.head(40).to_string())
