import sys, openpyxl, pandas as pd, numpy as np
f=sys.argv[1]
wb = openpyxl.load_workbook(f, data_only=True)
print([ (w.title, w.max_row, w.max_column) for w in wb.worksheets])
ws=wb['Resumen']
for row in ws.iter_rows():
    v=[(c.coordinate,c.value) for c in row if c.value is not None]
    if v: print(v)
# formulas in Resumen
wbf = openpyxl.load_workbook(f, data_only=False)
print("FORMULAS Resumen C7..K10:", [(c.coordinate,c.value) for r in wbf['Resumen']['C7:K10'] for c in r])
print("UCS G2..J2:", [c.value for c in wbf['UCS'][2][6:10]])
print("UCS_rev E2..G3:", [c.value for c in wbf['UCS_rev'][2][4:7]])
print("Corte H2..O2:", [c.value for c in wbf['Corte'][2][7:15]])
print("RMR K2..W2:", [c.value for c in wbf['RMR_RQD_FF'][2][10:23]])
# columns beyond in each sheet: any header with litología?
for w in wbf.worksheets:
    print(w.title, [c.value for c in w[1]])
