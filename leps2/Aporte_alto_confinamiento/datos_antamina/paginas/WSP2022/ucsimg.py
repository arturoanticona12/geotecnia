import pymupdf as fitz,os
pdf=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
doc=fitz.open(pdf)
from PIL import Image
ims=[]
for p in [74,76,78,80,82]:
    pg=doc[p-1]; r=pg.rect
    pix=pg.get_pixmap(dpi=110,clip=fitz.Rect(r.x0+80,r.y0+180,r.x1-60,r.y0+320))
    fn=f'ucs_{p}.png'; pix.save(fn); ims.append(Image.open(fn))
W=max(i.width for i in ims); H=sum(i.height for i in ims)
c=Image.new('RGB',(W,H),'white'); y=0
for i in ims: c.paste(i,(0,y)); y+=i.height
c.save('ucs_combo.png')
