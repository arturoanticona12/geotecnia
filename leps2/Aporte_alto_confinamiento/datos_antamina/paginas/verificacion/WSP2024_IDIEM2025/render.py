import sys, fitz, os
# uso: render.py <pdf> <outdir> <prefijo> <dpi> <pag1,pag2,...> [clip x0,y0,x1,y1 en fracción]
pdf, out, pre, dpi, pags = sys.argv[1:6]
clip = None
if len(sys.argv) > 6:
    clip = [float(x) for x in sys.argv[6].split(',')]
doc = fitz.open(pdf)
for p in pags.split(','):
    pg = doc[int(p)-1]
    r = pg.rect
    kw = {}
    suf = ''
    if clip:
        kw['clip'] = fitz.Rect(r.x0 + clip[0]*r.width, r.y0 + clip[1]*r.height, r.x0 + clip[2]*r.width, r.y0 + clip[3]*r.height)
        suf = '_c' + '_'.join(str(int(c*100)) for c in clip)
    pix = pg.get_pixmap(dpi=int(dpi), **kw)
    fn = os.path.join(out, f"{pre}_p{int(p):03d}{suf}.png")
    pix.save(fn)
    print(fn, pix.width, pix.height)
