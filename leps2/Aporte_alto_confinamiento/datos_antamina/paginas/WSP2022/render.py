import fitz,sys,os
pdf=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
out=os.path.dirname(os.path.abspath(__file__))
doc=fitz.open(pdf)
dpi=int(sys.argv[1])
pages=[]
for a in sys.argv[2:]:
    if '-' in a:
        x,y=map(int,a.split('-')); pages+=range(x,y+1)
    else: pages.append(int(a))
for p in pages:
    pg=doc[p-1]
    fn=os.path.join(out,f"p{p:03d}.png")
    pg.get_pixmap(dpi=dpi).save(fn)
    print(p, pg.rect.width, pg.rect.height, pg.rotation)
