"""Exporta el manuscrito a PDF con Word."""
import sys, win32com.client as w
src, dst = sys.argv[1], sys.argv[2]
app = w.DispatchEx("Word.Application"); app.Visible = False
try:
    d = app.Documents.Open(src, ReadOnly=True); d.ExportAsFixedFormat(dst, 17); d.Close(False)
finally:
    app.Quit()
print("pdf:", dst)
