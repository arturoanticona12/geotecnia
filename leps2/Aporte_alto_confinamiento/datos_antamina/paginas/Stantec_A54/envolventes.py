"""Extrae polilíneas vectoriales de envolventes (tau-sigma_n) y línea de densidad de las láminas Stantec A.5.4/A.5.5.
Uso: python envolventes.py <pdf> <A54|A55>"""
import pymupdf, sys, math
import numpy as np

pdf, hoja = sys.argv[1], sys.argv[2]
p = pymupdf.open(pdf)[0]
dr = p.get_drawings()

if hoja == "A54":
    cal = dict(x0=670.3, x5=1057.1, y0=429.7, y5=70.2)       # corte: 0 y 5000 kPa
    dcal = dict(x0=674.2, x70=1055.8, y17=702.7, y27=478.5)  # densidad
    curvas = {49: "Baja Calidad (Piteau, 2019) - azul continua"}
    dens = 106
else:
    cal = dict(x0=672.7, x5=1057.4, y0=427.6, y5=72.6)
    dcal = dict(x0=672.9, x70=1057.9, y17=699.3, y27=476.2)
    curvas = {124: "Moderada a buena calidad (Antamina) - celeste continua",
              125: "Buena calidad (Piteau, 2013) - morada continua",
              126: "Funcion Golder - roja segmentada (relleno)"}
    dens = 34

def pts_of(i):
    out = []
    for it in dr[i]["items"]:
        for q in it[1:]:
            if isinstance(q, pymupdf.Point):
                out.append((q.x, q.y))
    return out

def to_tau(x, y):
    s = (x - cal["x0"]) / (cal["x5"] - cal["x0"]) * 5000
    t = (cal["y0"] - y) / (cal["y0"] - cal["y5"]) * 5000
    return s, t

for i, name in curvas.items():
    pts = sorted(set((round(a, 2), round(b, 2)) for a, b in pts_of(i)))
    st = np.array([to_tau(a, b) for a, b in pts])
    if i == 126:  # relleno de segmentos: usar línea media por x
        xs = np.round(st[:, 0], -1)
        st = np.array([(x, st[xs == x, 1].mean()) for x in np.unique(xs)])
    st = st[np.argsort(st[:, 0])]
    print("==", name, "n=", len(st))
    for sn in [100, 250, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]:
        tau = np.interp(sn, st[:, 0], st[:, 1])
        print(f"  sn={sn:5d}  tau={tau:7.0f}  phi_sec={math.degrees(math.atan(tau / sn)):5.1f}")
    m = (st[:, 0] > 50) & (st[:, 1] > 5)
    b, la = np.polyfit(np.log(st[m, 0]), np.log(st[m, 1]), 1)
    print(f"  ajuste potencia tau = {math.exp(la):.3f} * sn^{b:.4f}  (kPa)")
    print("  primeros/ultimos:", np.round(st[:3], 0).tolist(), np.round(st[-3:], 0).tolist())

pts = sorted(pts_of(dens))
print("== Envolvente densidad (roja)")
for x, y in pts[::4] + [pts[-1]]:
    pp = (x - dcal["x0"]) / (dcal["x70"] - dcal["x0"]) * 70
    rho = 1.7 + (dcal["y17"] - y) / (dcal["y17"] - dcal["y27"]) * 1.0
    print(f"  p'={pp:5.1f} (x0.1 MPa)  rho_d={rho:.3f} t/m3  exp={2.0425*math.exp(0.0035*pp):.3f}")
