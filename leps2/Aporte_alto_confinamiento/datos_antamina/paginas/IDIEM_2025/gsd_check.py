import pymupdf, sys
d = pymupdf.open(sys.argv[1]); p=d[7]
print("images:", [(i[0], p.get_image_rects(i[0])) for i in p.get_images()])
dr = p.get_drawings(); print("drawings:", len(dr))
