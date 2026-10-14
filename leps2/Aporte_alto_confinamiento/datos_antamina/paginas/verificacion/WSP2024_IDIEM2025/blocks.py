import sys, pymupdf
doc = pymupdf.open(sys.argv[1])
pg = doc[int(sys.argv[2])-1]
for b in pg.get_text('blocks'):
    if b[1] < 330: print([round(x) for x in b[:4]], repr(b[4][:150]))
