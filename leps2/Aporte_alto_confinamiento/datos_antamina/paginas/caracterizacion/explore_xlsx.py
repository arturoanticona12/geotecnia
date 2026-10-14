import sys, openpyxl
wb = openpyxl.load_workbook(sys.argv[1], data_only=True, read_only=False)
for ws in wb.worksheets:
    print(f"\n### SHEET '{ws.title}' dims={ws.dimensions} max_row={ws.max_row} max_col={ws.max_column} state={ws.sheet_state}")
    print("  images:", len(getattr(ws,'_images',[])), "charts:", len(getattr(ws,'_charts',[])), "merged:", len(ws.merged_cells.ranges))
    n = int(sys.argv[2]) if len(sys.argv)>2 else 15
    for r in ws.iter_rows(min_row=1, max_row=min(ws.max_row, n)):
        vals = [(c.coordinate, c.value) for c in r if c.value is not None]
        if vals: print("  ", vals[:30])
