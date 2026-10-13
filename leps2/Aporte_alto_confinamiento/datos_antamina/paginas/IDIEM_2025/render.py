import fitz, sys, os
src, out, dpi = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = fitz.open(src)
for i, p in enumerate(d):
    print(i+1, p.rect)
    p.get_pixmap(dpi=dpi).save(os.path.join(out, f"p{i+1:02d}.png"))
