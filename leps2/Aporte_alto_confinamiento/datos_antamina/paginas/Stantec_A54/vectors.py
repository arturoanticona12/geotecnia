import pymupdf, sys
d = pymupdf.open(sys.argv[1]); p=d[0]
for i,dr in enumerate(p.get_drawings()):
    r = dr["rect"]
    pts=[]
    for it in dr["items"]:
        for q in it[1:]:
            if isinstance(q, pymupdf.Point): pts.append((round(q.x,1),round(q.y,1)))
    col = tuple(round(c,2) for c in dr["color"]) if dr.get("color") else None
    fill = tuple(round(c,2) for c in dr["fill"]) if dr.get("fill") else None
    if len(pts)>=2 and r.width>20 and not (col and all(c>0.8 for c in col)):
        print(i, dr["type"], "col",col,"fill",fill,"w",dr.get("width"),"dash",dr.get("dashes"), "rect",[round(v) for v in r], "n",len(pts))
