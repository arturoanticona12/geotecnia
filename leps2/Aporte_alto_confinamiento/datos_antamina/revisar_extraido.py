"""Revisión de consistencia de los CSV extraídos antes de unificarlos."""
import sys, glob, os
import pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 90); pd.set_option("display.max_rows", 200)
E = os.path.join(os.path.dirname(__file__), "extraido")
ARCH = ["Golder_2010_ROM", "Golder_2012_marmol", "Golder_2021_commingling", "IDIEM_2025", "WSP_2022_hornfels3B",
        "WSP_2024_codisposicion", "ensayos_triaxial_CU", "ensayos_corte_directo"]
d = pd.concat([pd.read_csv(os.path.join(E, a + ".csv")).assign(archivo=a) for a in ARCH], ignore_index=True)
print("filas", len(d))
print(d.groupby(["archivo", "tipo_ensayo"], dropna=False).size().to_string())
print("\n-- clase y litología")
print(d.groupby(["archivo", "tipo_material", "litologia"], dropna=False).size().to_string())
print("\n-- εv por archivo (min, max, n) y menciones de convención en notas")
for a, g in d.groupby("archivo"):
    ev = pd.to_numeric(g.eps_vol_falla_pct, errors="coerce")
    conv = g.notas.dropna().str.extract(r"((?:negativ|positiv|contracc|compres|dilat)[^.;]{0,80})", expand=False).dropna().unique()[:2]
    print(f"  {a:26s} εv min {ev.min()!s:>7} max {ev.max()!s:>7} n {ev.notna().sum():3d} | {list(conv)}")
print("\n-- criterio de falla")
print(d.groupby(["archivo", "criterio_falla"], dropna=False).size().to_string())
print("\n-- duplicados marcados y leídos de gráfico")
print("DUPLICADO:", d.notas.fillna("").str.contains("DUPLICADO", case=False).groupby(d.archivo).sum().to_dict())
print("gráfico:", d.notas.fillna("").str.contains("gráfico", case=False).groupby(d.archivo).sum().to_dict())
print("verificado:", d.verificado_imagen.value_counts(dropna=False).to_dict())
print("\n-- control q = σ1 − σ3 (|dif| > 1 kPa)")
q = pd.to_numeric(d.q_kPa, errors="coerce"); s1 = pd.to_numeric(d.sigma1_kPa, errors="coerce"); s3 = pd.to_numeric(d.sigma3_kPa, errors="coerce")
bad = d[(q - (s1 - s3)).abs() > 1]
print(len(bad), bad[["archivo", "ensayo_id", "sigma3_kPa", "sigma1_kPa", "q_kPa"]].head(10).to_string())
print("\n-- rango σ3 por archivo y diámetro")
print(d.assign(s3=s3).groupby("archivo").agg(s3_min=("s3", "min"), s3_max=("s3", "max"), D_mm=("diametro_mm", lambda x: sorted(pd.to_numeric(x, errors='coerce').dropna().unique().tolist()))).to_string())
