import pandas as pd, pathlib
ext=pathlib.Path(__file__).parents[3]/"extraido"
df=pd.read_csv(ext/"parametros_RMU.csv")
print(df.columns.tolist()); print(len(df))
print(df.iloc[:3].T.to_string())
print(df.groupby(["fuente"]).size() if "fuente" in df else "")
for c in ["parametro","estadistico","base","rmu","RMU"]:
    if c in df: print(c, df[c].unique()[:60])
