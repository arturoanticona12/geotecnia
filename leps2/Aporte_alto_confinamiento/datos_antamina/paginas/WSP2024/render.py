import sys, fitz
from pathlib import Path
here = Path(__file__).resolve().parent
pdf = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2024_WSP_Ensayos gran escala mezcla co-disposicion.pdf")
doc = fitz.open(pdf)
dpi = int(sys.argv[1])
for a in sys.argv[2:]:
    if "-" in a:
        x, y = map(int, a.split("-")); ps = range(x, y + 1)
    else:
        ps = [int(a)]
    for p in ps:
        out = here / f"p{p:03d}.png"
        if not out.exists():
            doc[p - 1].get_pixmap(dpi=dpi).save(out)
        print(out.name, doc[p - 1].rect)
