import pymupdf as fitz, pathlib
from PIL import Image
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos")
out = pathlib.Path(__file__).parent
names={"H":"HORNFELS","I":"Intrusivo","P1":"Pila 01","P2":"Pila 02"}
ims=[]
for k,n in names.items():
    pdf=[p for p in (root/"Clasificación de suelos SUCS").glob("*.pdf") if p.name.startswith(n)][0]
    doc=fitz.open(pdf); pg=doc[1]
    a=pg.get_pixmap(dpi=85,clip=fitz.Rect(70,225,560,290)); b=pg.get_pixmap(dpi=85,clip=fitz.Rect(330,385,560,440)); c2=pg.get_pixmap(dpi=85,clip=fitz.Rect(330,530,560,600))
    for j,p in enumerate((a,b,c2)):
        fn=out/f"_tmp_{k}_{j}.png"; p.save(fn); ims.append(Image.open(fn))
W=max(i.width for i in ims); H=sum(i.height for i in ims)
c=Image.new("RGB",(W,H),"white"); y=0
for i in ims: c.paste(i,(0,y)); y+=i.height
c.save(out/"crop_SUCS_HIP1P2_p2.png")
for f in out.glob("_tmp_*.png"): f.unlink()
