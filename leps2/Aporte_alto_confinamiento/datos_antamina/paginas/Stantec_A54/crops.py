import pymupdf, sys, os
d = pymupdf.open(sys.argv[1]); p=d[0]; out=sys.argv[2]
print("images:", [(i[0], i[2], i[3], p.get_image_rects(i[0])) for i in p.get_images()])
print("drawings:", len(p.get_drawings()))
print("words:", len(p.get_text("words")))
crops = {"tabla": (405,205,630,295), "corte": (640,60,1065,460), "indices": (50,470,640,715), "densidad": (640,470,1065,725), "gsd": (50,60,640,470)}
for k,(x0,y0,x1,y1) in crops.items():
    p.get_pixmap(dpi=int(sys.argv[3]), clip=pymupdf.Rect(x0,y0,x1,y1)).save(os.path.join(out, f"crop_{k}.png"))
