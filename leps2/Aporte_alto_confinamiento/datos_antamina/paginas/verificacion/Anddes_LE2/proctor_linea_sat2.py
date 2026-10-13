import pymupdf as fitz, pathlib
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos\Proctor estándar")
pdf=[p for p in root.glob("*.pdf") if p.name.startswith("Marmol")][0]
pg=fitz.open(pdf)[0]
for d in pg.get_drawings():
    r=d["rect"]
    if 180<r.x0<460 and 300<r.y0<580 and d.get("color") not in (None,):
        pts=[]
        for it in d["items"]:
            for p in it[1:]:
                if hasattr(p,"x"): pts.append((round(p.x,1),round(p.y,1)))
        if len(pts)>=2 and (r.width>3 or r.height>3) and not (r.width<0.6 or r.height<0.6):
            print(d["color"],d.get("width"),[it[0] for it in d["items"]][:6],len(d["items"]),pts[:4],"...",pts[-2:])
print([ (round(b[0]),round(b[1]),round(b[2]),round(b[3])) for b in pg.get_images()])
for w in pg.get_text("words"):
    if 250<w[0]<400 and 300<w[1]<420: print(w)
