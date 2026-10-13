import pymupdf as fitz, math
pdf=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
doc=fitz.open(pdf)
for pno in [6,7]:
    pg=doc[pno-1]
    txt=[(sp['text'].strip(),sp['bbox']) for b in pg.get_text('dict')['blocks'] for l in b.get('lines',[]) for sp in l['spans'] if sp['text'].strip() in ('10000','1000','100','10','1','0.1','0','50','100')]
    print(pno,[(t,round((b[0]+b[2])/2,1),round((b[1]+b[3])/2,1)) for t,b in txt])
    cols={}
    for dr in pg.get_drawings():
        r=dr['rect']; c=dr.get('fill')
        if c and 2<r.width<7 and 2<r.height<7:
            cols.setdefault(tuple(round(v,2) for v in c),[]).append((round((r.x0+r.x1)/2,2),round((r.y0+r.y1)/2,2)))
    for k,v in cols.items(): print(' ',k,len(v),sorted(v)[:25])
