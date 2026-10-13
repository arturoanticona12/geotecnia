import pymupdf as fitz, pathlib
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos")
out = pathlib.Path(__file__).parent
names={"M":"Marmol","H":"HORNFELS","I":"Intrusivo","P1":"Pila 01","P2":"Pila 02"}
for k,n in names.items():
    pdf=[p for p in (root/"Clasificación de suelos SUCS").glob("*.pdf") if p.name.startswith(n)][0]
    doc=fitz.open(pdf)
    doc[0].get_pixmap(dpi=100,clip=fitz.Rect(70,110,540,385)).save(out/f"crop_SUCS_{k}_p1.png")
    doc[1].get_pixmap(dpi=80,clip=fitz.Rect(70,220,540,520)).save(out/f"crop_SUCS_{k}_p2.png")
    for folder,tag in [("Proctor estándar","PR"),("Contenido de agua","CA")]:
        pdf=[p for p in (root/folder).glob("*.pdf") if p.name.startswith(n)][0]
        doc=fitz.open(pdf)
        doc[0].get_pixmap(dpi=100).save(out/f"full_{tag}_{k}.png")
