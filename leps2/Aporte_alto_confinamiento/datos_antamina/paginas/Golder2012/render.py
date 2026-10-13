"""Uso: render.py <pdf> <carpeta_salida> <dpi> <pag1> [pag2 ...]  (páginas 1-based)"""
import sys
import fitz

pdf, out, dpi = sys.argv[1], sys.argv[2], int(sys.argv[3])
doc = fitz.open(pdf)
for s in sys.argv[4:]:
    n = int(s)
    pix = doc[n - 1].get_pixmap(dpi=dpi)
    pix.save(f"{out}/p{n:03d}.png")
    print("ok", n, pix.width, pix.height)
