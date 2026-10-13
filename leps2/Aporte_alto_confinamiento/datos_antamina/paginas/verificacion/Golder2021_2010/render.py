# uso: render.py <pdf> <prefijo> <dpi> <paginas p.ej. 7,8,9-12> [clip x0,y0,x1,y1 en fraccion]
import fitz, sys, os
pdf, pre, dpi, pages = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
clip = [float(x) for x in sys.argv[5].split(',')] if len(sys.argv) > 5 else None
out = os.path.dirname(os.path.abspath(__file__))
doc = fitz.open(pdf)
ps = []
for t in pages.split(','):
    if '-' in t:
        a, b = map(int, t.split('-')); ps += range(a, b + 1)
    else:
        ps.append(int(t))
for p in ps:
    pg = doc[p - 1]
    r = pg.rect
    c = None
    if clip:
        c = fitz.Rect(r.x0 + clip[0]*r.width, r.y0 + clip[1]*r.height, r.x0 + clip[2]*r.width, r.y0 + clip[3]*r.height)
    pix = pg.get_pixmap(dpi=dpi, clip=c)
    suf = '' if not clip else '_c' + '_'.join(str(int(x*100)) for x in clip)
    fn = os.path.join(out, f'{pre}_p{p:03d}{suf}.png')
    pix.save(fn); print(fn, pix.width, pix.height, 'rot', pg.rotation)
