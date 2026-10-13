import pymupdf as fitz, pathlib
from PIL import Image
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos")
out = pathlib.Path(__file__).parent
names={"H":"HORNFELS","I":"Intrusivo","P1":"Pila 01","P2":"Pila 02"}
ims=[]
for k,n in names.items():
    pdf=[p for p in (root/"Clasificación de suelos SUCS").glob("*.pdf") if p.name.startswith(n)][0]
    doc=fitz.open(pdf)
    pm=doc[0].get_pixmap(dpi=95,clip=fitz.Rect(140,320,580,540))
    pm.save(out/f"crop_SUCS_{k}_p1_tabla.png"); ims.append(Image.open(out/f"crop_SUCS_{k}_p1_tabla.png"))
W=max(i.width for i in ims); H=sum(i.height for i in ims)
c=Image.new("RGB",(W,H),"white"); y=0
for i in ims: c.paste(i,(0,y)); y+=i.height
c.save(out/"crop_SUCS_HIP1P2_tablas.png")
