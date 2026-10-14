"""Uso: crop.py <pdf> <out_dir> <dpi> <pag> <x0> <y0> <x1> <y1> <sufijo>
Coordenadas como fracción (0-1) de la página tal como se ve (con rotación aplicada).
Renderiza la página completa y recorta el pixmap (evita problemas de rotación)."""
import sys
import pymupdf

pdf, out, dpi, pag = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
x0, y0, x1, y1 = map(float, sys.argv[5:9])
suf = sys.argv[9]
doc = pymupdf.open(pdf)
pix = doc[pag - 1].get_pixmap(dpi=dpi)
W, H = pix.width, pix.height
ir = pymupdf.IRect(int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))
sub = pymupdf.Pixmap(pix.colorspace, ir, pix.alpha)
sub.copy(pix, ir)
sub.set_origin(0, 0)
fn = f"{out}/p{pag:03d}_{suf}.png"
sub.save(fn)
print("ok", fn, sub.width, sub.height)
