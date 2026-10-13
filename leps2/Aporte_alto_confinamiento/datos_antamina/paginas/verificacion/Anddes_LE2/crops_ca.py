import pymupdf as fitz, pathlib
from PIL import Image
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos\Contenido de agua")
out = pathlib.Path(__file__).parent
ims=[]
for n in ["HORNFELS","Intrusivo","Pila 01","Pila 02"]:
    pdf=[p for p in root.glob("*.pdf") if p.name.startswith(n)][0]
    pg=fitz.open(pdf)[0]
    for clip in (fitz.Rect(70,140,540,265),fitz.Rect(120,300,500,560)):
        fn=out/"_t.png"; pg.get_pixmap(dpi=70,clip=clip).save(fn); ims.append(Image.open(fn).copy())
W=max(i.width for i in ims); H=sum(i.height for i in ims)
c=Image.new("RGB",(W,H),"white"); y=0
for i in ims: c.paste(i,(0,y)); y+=i.height
c.save(out/"crop_CA_HIP1P2.png"); (out/"_t.png").unlink()
