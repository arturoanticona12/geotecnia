import fitz,os
pdf=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
out=os.path.dirname(os.path.abspath(__file__))
doc=fitz.open(pdf)
pg=doc[34]
r=pg.rect
# crop lower half bottom figures (c and d)
for name,clip in [('p035_c',fitz.Rect(r.x0,r.y0+r.height*0.45,r.x0+r.width*0.55,r.y0+r.height*0.80)),('p035_d',fitz.Rect(r.x0+r.width*0.45,r.y0+r.height*0.45,r.x1,r.y0+r.height*0.80))]:
    pg.get_pixmap(dpi=200,clip=clip).save(os.path.join(out,name+'.png'))
# list drawings? try vector paths
paths=pg.get_drawings()
print(len(paths))
