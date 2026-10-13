import sys, openpyxl, pandas as pd
f=sys.argv[1]
wb = openpyxl.load_workbook(f, data_only=True)
ws = wb.worksheets[0]
for r in (2,3,4,5):
    print(r, [(c.coordinate,c.value) for c in ws[r] if c.value is not None])
print("merged", ws.merged_cells.ranges)
# formulas?
wbf = openpyxl.load_workbook(f, data_only=False); wsf=wbf.worksheets[0]
print("formulas row6:", [(c.coordinate,c.value) for c in wsf[6] if isinstance(c.value,str) and c.value.startswith('=')][:20])
df = pd.read_excel(f, header=4)
df = df.dropna(how='all')
print(df.shape); print(df.columns.tolist())
for c in ['Año','Mes','Equipo','Fase','Tipo de material','Target (cm)','Clasificación','Zona','COMPARATIVO','TIPO DE EXPLOSIVO']:
    if c in df: print(c, df[c].value_counts(dropna=False).head(30).to_dict())
print(df.describe().T.to_string())
print(df.tail(3).T.to_string())
