import pandas as pd, pathlib
ext=pathlib.Path(__file__).parents[3]/"extraido"
df=pd.read_csv(ext/"ensayos_triaxial_CU.csv")
print(df[["set_id","ensayo_id","saturado","Dmax_mm","escalamiento","w_pct","Su_kPa","c_ef_serie_kPa","phi_ef_serie_deg","a_ef_serie_kPa","alfa_ef_serie_deg","c_tot_serie_kPa","phi_tot_serie_deg","envolvente_total_criterio","pagina","clase_desmonte","tipo_material","litologia_proporcion"]].to_string())
print(df.notas.iloc[3]); print(df.notas.iloc[6]); print(df.notas.iloc[9]);print(df.notas.iloc[14])

