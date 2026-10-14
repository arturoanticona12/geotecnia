import pandas as pd, sys
pd.set_option('display.width',250); pd.set_option('display.max_columns',100); pd.set_option('display.max_colwidth',60)
B=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Aporte_alto_confinamiento\datos_antamina\extraido"
d=pd.read_csv(B+r"\WSP_2022_hornfels3B.csv")
print(d.shape)
cols=[c for c in d.columns if c not in('fuente','anio','autor_informe','notas')]
for i,r in d.iterrows():
    print('-----',i)
    for c in cols:
        if pd.notna(r[c]): print(f"  {c}: {r[c]}")
