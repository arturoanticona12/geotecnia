import pymupdf as fitz, json
pdf=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
doc=fitz.open(pdf); pg=doc[34]
# gridlines: collect long horizontal/vertical lines to calibrate
lines=[]
for dr in pg.get_drawings():
    for it in dr['items']:
        if it[0]=='l':
            p1,p2=it[1],it[2]
            lines.append((round(p1.x,2),round(p1.y,2),round(p2.x,2),round(p2.y,2)))
def panel(x0,x1,y0,y1):
    vx=sorted(set(l[0] for l in lines if abs(l[0]-l[2])<0.01 and x0<=l[0]<=x1 and y0<=min(l[1],l[3])<=y1 and abs(l[1]-l[3])>50))
    hy=sorted(set(l[1] for l in lines if abs(l[1]-l[3])<0.01 and y0<=l[1]<=y1 and x0-5<=min(l[0],l[2])<=x1 and abs(l[0]-l[2])>50))
    return vx,hy
print('c',panel(340,545,165,310))
print('d',panel(340,545,355,520))
pts={}
for dr in pg.get_drawings():
    r=dr['rect']; col=dr.get('fill')
    if col and 2<r.width<8 and 2<r.height<8:
        c=tuple(round(v,2) for v in col)
        cx,cy=(r.x0+r.x1)/2,(r.y0+r.y1)/2
        pts.setdefault(c,[]).append((round(cx,2),round(cy,2)))
json.dump({str(k):v for k,v in pts.items()},open('pts35.json','w'))
for k,v in pts.items():
    print(k,len(v),[p for p in v if p[0]>340][:60])
