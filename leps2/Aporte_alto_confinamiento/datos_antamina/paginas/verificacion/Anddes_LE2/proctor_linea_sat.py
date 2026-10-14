import pymupdf as fitz, pathlib, re
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos\Proctor estándar")
for pdf in sorted(root.glob("*.pdf")):
    pg=fitz.open(pdf)[0]
    words=pg.get_text("words")
    print("=====",pdf.name)
    for w in words:
        if "Gs" in w[4] or "satur" in w[4].lower() or "Curva" in w[4]: print("  label",w[4],[round(x,1) for x in w[:4]])
    # axis tick labels
    ticks=[(w[4],round(w[0],1),round(w[1],1),round(w[2],1),round(w[3],1)) for w in words if re.fullmatch(r"\d{1,2}(,\d{3})?",w[4]) and 280<w[1]<600]
    print("  ticks",ticks)
    for d in pg.get_drawings():
        for it in d["items"]:
            if it[0]=="l":
                p1,p2=it[1],it[2]
                if abs(p1.x-p2.x)>5 and abs(p1.y-p2.y)>5 and 150<p1.x<450 and 250<p1.y<600:
                    print("  line",round(p1.x,1),round(p1.y,1),round(p2.x,1),round(p2.y,1),d.get("color"),d.get("width"))
