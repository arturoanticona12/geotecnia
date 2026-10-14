import pymupdf as fitz, pathlib
root = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos")
out = pathlib.Path(__file__).parent
names={"M":"Marmol","H":"HORNFELS","I":"Intrusivo","P1":"Pila 01","P2":"Pila 02"}
for folder,tag in [("Corte directo","LSDS")]:
    for k,n in names.items():
        pdf=[p for p in (root/folder).glob("*.pdf") if p.name.startswith(n)][0]
        doc=fitz.open(pdf)
        doc[0].get_pixmap(dpi=105,clip=fitz.Rect(70,110,535,700)).save(out/f"crop_{tag}_{k}_p1.png")
        doc[1].get_pixmap(dpi=105,clip=fitz.Rect(70,110,535,760)).save(out/f"crop_{tag}_{k}_p2.png")
