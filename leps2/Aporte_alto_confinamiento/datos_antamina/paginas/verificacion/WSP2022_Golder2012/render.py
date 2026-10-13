import sys, fitz, os
D=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina"
F={'G':"2012_Golder_Triaxiales Gran Escala en Marmol Negro.pdf",'W':"2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"}
OUT=os.path.dirname(os.path.abspath(__file__))
key=sys.argv[1]; zoom=float(sys.argv[2]); pages=[int(p) for p in sys.argv[3].split(',')]
clip=None
if len(sys.argv)>4: clip=[float(a) for a in sys.argv[4].split(',')]  # fractions x0,y0,x1,y1
doc=fitz.open(os.path.join(D,F[key]))
for p in pages:
    pg=doc[p-1]; r=pg.rect
    c=None
    if clip: c=fitz.Rect(r.x0+clip[0]*r.width, r.y0+clip[1]*r.height, r.x0+clip[2]*r.width, r.y0+clip[3]*r.height)
    pix=pg.get_pixmap(matrix=fitz.Matrix(zoom,zoom),clip=c)
    suf='' if not clip else '_c'+'_'.join(str(int(a*100)) for a in clip)
    fn=os.path.join(OUT,f"{key}_p{p:03d}{suf}.png"); pix.save(fn); print(fn, pix.width,pix.height)
