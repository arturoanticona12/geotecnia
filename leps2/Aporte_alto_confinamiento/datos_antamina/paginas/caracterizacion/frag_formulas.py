import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], data_only=False)
ws = wb.worksheets[0]
for r in (6,7,200,324):
    print(r, [(c.coordinate,c.value) for c in ws[r] if c.value is not None and c.column>=18][:60])
print([ws.title for ws in wb.worksheets], wb.defined_names if hasattr(wb,'defined_names') else '')
# last nonempty row
last=max(r for r in range(1,400) if ws.cell(r,1).value is not None); print('last row', last)
