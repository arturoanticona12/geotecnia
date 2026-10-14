import pymupdf, sys
d = pymupdf.open(sys.argv[1]); p = d[0]
for w in p.get_text("words"):
    x0, y0, x1, y1, t = w[:5]
    if x0 > 630 and t.replace('.', '').replace('%', '').isdigit():
        print(t.rjust(6), "cx=%.1f cy=%.1f" % ((x0 + x1) / 2, (y0 + y1) / 2))
