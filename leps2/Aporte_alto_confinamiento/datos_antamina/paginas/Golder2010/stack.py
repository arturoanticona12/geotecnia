"""Uso: stack.py <pdf> <salida.png> <dpi> <x0> <y0> <x1> <y1> <pag1> [pag2 ...]
Recorta la misma región (fracciones de página visible) de varias páginas y las apila verticalmente."""
import sys
import pymupdf

pdf, out, dpi = sys.argv[1], sys.argv[2], int(sys.argv[3])
x0, y0, x1, y1 = map(float, sys.argv[4:8])
pages = [int(s) for s in sys.argv[8:]]
doc = pymupdf.open(pdf)
subs = []
for n in pages:
    pix = doc[n - 1].get_pixmap(dpi=dpi)
    W, H = pix.width, pix.height
    ir = pymupdf.IRect(int(x0 * W), int(y0 * H), int(x1 * W), int(y1 * H))
    s = pymupdf.Pixmap(pix.colorspace, ir, pix.alpha)
    s.copy(pix, ir)
    s.set_origin(0, 0)
    subs.append(s)
w = max(s.width for s in subs)
h = sum(s.height for s in subs) + 6 * len(subs)
big = pymupdf.Pixmap(subs[0].colorspace, pymupdf.IRect(0, 0, w, h), False)
big.clear_with(200)
y = 0
for s in subs:
    s.set_origin(0, y)
    big.copy(s, s.irect)
    y += s.height + 6
big.save(out)
print("ok", out, w, h)
