import fitz, sys, os
pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2021_Golder_Ensayos de Laboratorio Commingling.pdf"
out = os.path.dirname(os.path.abspath(__file__))
doc = fitz.open(pdf)
for i, p in enumerate(doc, 1):
    t = p.get_text().strip()
    if len(t) < 60:
        print("pocas letras:", i, len(t), len(p.get_images()))
    pix = p.get_pixmap(dpi=150)
    pix.save(os.path.join(out, f"p{i:03d}.png"))
print(len(doc))
