"""Montaje de recortes (encabezado Muestra/Probeta + tabla de datos) de las páginas de pico para verificación visual."""
import sys, fitz
from pathlib import Path
here = Path(__file__).resolve().parent
pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2024_WSP_Ensayos gran escala mezcla co-disposicion.pdf"
doc = fitz.open(pdf)
name = sys.argv[1]; pages = list(map(int, sys.argv[2:]))
# coordenadas en puntos PDF (595x842)
hdr = fitz.Rect(55, 170, 510, 310)
tab = fitz.Rect(270, 315, 510, 660)
W = 245 * len(pages); H = 140 + 350
out = fitz.open(); pg = out.new_page(width=W, height=H)
for i, p in enumerate(pages):
    src = doc[p - 1]
    x0 = 245 * i
    pg.show_pdf_page(fitz.Rect(x0, 0, x0 + 245, 140 * 245 / 455), doc, p - 1, clip=hdr)
    pg.show_pdf_page(fitz.Rect(x0, 80, x0 + 245, 80 + 345 * 245 / 240), doc, p - 1, clip=tab)
    pg.insert_text((x0 + 5, H - 5), f"p{p}", fontsize=10, color=(1, 0, 0))
out[0].get_pixmap(dpi=170).save(here / f"{name}.png")
print(name)
