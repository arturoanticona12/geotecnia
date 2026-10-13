"""Digitaliza las curvas 'Codisposal n' (marcadores rojos) de los Gráfico 1 de IDIEM.
Calibración: marcadores azules (Desmonte bajo 4") cuyos valores se conocen de la tabla de la p.93
(pasante/96.2*100), y tamaños de malla conocidos.
"""
import numpy as np, fitz, sys
from scipy import ndimage
from pathlib import Path

pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2024_WSP_Ensayos gran escala mezcla co-disposicion.pdf"
doc = fitz.open(pdf)
sieves = [101.6, 76.2, 63.5, 50.8, 38.1, 25.4, 19.0, 9.52, 4.76, 2.0, 0.84, 0.42, 0.25, 0.11, 0.074]
intr = [96.2, 93.2, 89.6, 84.2, 77.0, 67.0, 57.4, 39.3, 25.7, 20.4, 15.6, 12.4, 10.4, 7.5, 6.6]
des4 = [100 * v / 96.2 for v in intr]

def comps(mask, minpix):
    lab, n = ndimage.label(mask)
    out = []
    for i in range(1, n + 1):
        ys, xs = np.nonzero(lab == i)
        if len(ys) >= minpix:
            out.append((xs.mean(), ys.mean(), len(ys), np.ptp(xs) + 1, np.ptp(ys) + 1))
    return out

for pno in map(int, sys.argv[1:]):
    pix = doc[pno - 1].get_pixmap(dpi=300)
    img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)[:, :, :3].astype(int)
    R, G, B = img[..., 0], img[..., 1], img[..., 2]
    # restringir a la mitad superior (gráfico)
    red = (R > 200) & (G < 50) & (B < 50)
    blue = (B > 90) & (R < 60) & (G < 60)
    red = ndimage.binary_opening(red, structure=np.ones((9, 9)))   # elimina líneas finas
    blue = ndimage.binary_opening(blue, structure=np.ones((5, 5)))
    rc = sorted(comps(red, 40))
    bc = sorted(comps(blue, 15))
    print(f"--- p{pno}: {len(rc)} rojos, {len(bc)} azules")
    # calibración x por logD: usar marcadores azules (ordenados por x crec = D decreciente)
    # tomamos los últimos 15 azules (los de Codisposal 4 incluyen tamaños >4")
    bx = np.array([c[0] for c in bc]); by = np.array([c[1] for c in bc])
    print("azules x,y:", [(round(c[0]), round(c[1])) for c in bc])
    print("rojos  x,y:", [(round(c[0]), round(c[1])) for c in rc])

