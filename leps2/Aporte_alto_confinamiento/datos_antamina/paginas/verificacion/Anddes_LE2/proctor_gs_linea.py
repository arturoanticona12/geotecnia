import pymupdf as fitz, pathlib, re, statistics as st
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos\Proctor estándar")
out=pathlib.Path(__file__).parent
for pdf in sorted(root.glob("*.pdf")):
    doc=fitz.open(pdf); pg=doc[0]
    words=pg.get_text("words")
    yt=[(float(w[4].replace(",",".")),(w[1]+w[3])/2) for w in words if re.fullmatch(r"\d{2},\d{3}",w[4]) and 280<w[1]<600]
    xt=[(float(w[4]),(w[0]+w[2])/2) for w in words if re.fullmatch(r"\d{1,2}",w[4]) and 555<w[1]<585 and 180<w[0]<450]
    # linear fits
    def fit(pairs):
        n=len(pairs); mx=sum(p[1] for p in pairs)/n; my=sum(p[0] for p in pairs)/n
        b=sum((p[1]-mx)*(p[0]-my) for p in pairs)/sum((p[1]-mx)**2 for p in pairs); return lambda z: my+b*(z-mx)
    fy=fit(yt); fx=fit(xt)
    segs=None; pts=[]
    for d in pg.get_drawings():
        if d.get("color")==(0.0,0.41200000047683716,0.6669999957084656) and abs((d.get("width") or 0)-0.93)<0.01 and len(d["items"])>10:
            for it in d["items"]:
                pts.append(it[1]); pts.append(it[2])
    gs=[]
    for p in pts:
        w=fx(p.x)/100; g=fy(p.y)
        gs.append(g/(9.81-w*g))
    # also compaction points (markers): blue small squares
    mk=[]
    for d in pg.get_drawings():
        if d.get("color")==(0.0,0.41200000047683716,0.6669999957084656) and len(d["items"])==4:
            r=d["rect"]; mk.append((round(fx((r.x0+r.x1)/2),2),round(fy((r.y0+r.y1)/2),3)))
    print(pdf.name[:22], "Gs linea: min %.3f max %.3f media %.3f n=%d"%(min(gs),max(gs),st.mean(gs),len(gs)), "| puntos (w,gd):",mk)
    # zoom crop of label
    doc[0].get_pixmap(dpi=200,clip=fitz.Rect(250,330,420,520)).save(out/f"zoom_PR_linea_{pdf.name.split()[0]}_{pdf.name.split()[1]}.png")
