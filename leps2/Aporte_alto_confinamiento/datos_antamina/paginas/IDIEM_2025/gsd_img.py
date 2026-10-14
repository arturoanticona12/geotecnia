import pymupdf, sys
d = pymupdf.open(sys.argv[1])
pix = pymupdf.Pixmap(d, 109)
print(pix.width, pix.height, pix.n)
if pix.n>3: pix = pymupdf.Pixmap(pymupdf.csRGB, pix)
pix.save(sys.argv[2])
