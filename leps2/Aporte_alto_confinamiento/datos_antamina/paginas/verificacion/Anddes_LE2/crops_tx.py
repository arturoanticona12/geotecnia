import fitz, pathlib
base = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos\Triaxial CU 6 in")
out = pathlib.Path(__file__).parent
names={"M":"Marmol","H":"HORNFELS","I":"Intrusivo","P1":"Pila 01","P2":"Pila 02"}
for k,n in names.items():
    pdf=[p for p in base.glob("*.pdf") if p.name.startswith(n)][0]
    doc=fitz.open(pdf)
    for i in (2,3,4):
        pg=doc[i]
        clip=fitz.Rect(95,205,500,672)
        pg.get_pixmap(dpi=135,clip=clip).save(out/f"crop_TX_{k}_p{i+1}.png")
    # p1 header + top
    doc[0].get_pixmap(dpi=110,clip=fitz.Rect(60,45,535,250)).save(out/f"crop_TX_{k}_p1_head.png")
    doc[6].get_pixmap(dpi=110,clip=fitz.Rect(60,200,535,620)).save(out/f"crop_TX_{k}_p7.png")
    # find hidden 2.70
    for w in doc[3].get_text("dict")["blocks"]:
        for l in w.get("lines",[]):
            for s in l["spans"]:
                if s["text"].strip() in ("2.70","2,70"): print(k, s["text"], s["bbox"], hex(s["color"]), s["size"])

