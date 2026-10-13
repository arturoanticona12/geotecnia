"""Convierte posiciones de marcadores (px, 300 dpi) a % pasante con calibración por marcadores azules
(Desmonte bajo 4" = pasante p.93 / 96.2). Luego calcula D10, D30, D50, D60, Cu, Cc por interpolación log-lineal."""
import numpy as np
sieves = {101.6: 96.2, 76.2: 93.2, 63.5: 89.6, 50.8: 84.2, 38.1: 77.0, 25.4: 67.0, 19.0: 57.4, 9.52: 39.3,
          4.76: 25.7, 2.0: 20.4, 0.84: 15.6, 0.42: 12.4, 0.25: 10.4, 0.11: 7.5, 0.074: 6.6}
D = np.array(list(sieves)); P4 = 100 * np.array(list(sieves.values())) / 96.2

data = {
 # pagina: (azules [(x,y)], rojos [(x,y)])  -- de gran_digit.py
 "C1_p268": ([(1171, 1109), (1261, 1240), (1362, 1290), (1467, 1335), (1549, 1365), (1613, 1386)],
             [(884, 567), (919, 595), (941, 628), (968, 680), (1052, 846), (1088, 936), (1171, 1071), (1255, 1172),
              (1361, 1212), (1465, 1251), (1549, 1293), (1612, 1338), (1712, 1406), (1759, 1419)]),
 "C2_p143": ([(1172, 1098), (1261, 1226), (1363, 1273), (1471, 1318), (1556, 1348), (1622, 1367)],
             [(915, 595), (937, 626), (965, 678), (1001, 746), (1050, 838), (1085, 928), (1173, 1066), (1256, 1170),
              (1364, 1212), (1470, 1252), (1556, 1289), (1621, 1329), (1721, 1389), (1770, 1400)]),
 "C3_p232": ([(1190, 913), (1330, 1041), (1409, 1073), (1471, 1096), (1519, 1109)],
             [(1002, 546), (1019, 569), (1039, 606), (1065, 656), (1101, 723), (1127, 788), (1191, 894), (1252, 972),
              (1330, 1003), (1408, 1033), (1470, 1059), (1518, 1087), (1591, 1125), (1626, 1133)]),
}
blue_D = [9.52, 4.76, 2.0, 0.84, 0.42, 0.25]

def chars(Ds, Ps):
    o = np.argsort(Ps); Ps = np.array(Ps)[o]; Ds = np.array(Ds)[o]
    f = lambda p: float(10 ** np.interp(p, Ps, np.log10(Ds))) if Ps[0] <= p <= Ps[-1] else None
    d10, d30, d50, d60 = f(10), f(30), f(50), f(60)
    cu = d60 / d10 if d10 and d60 else None
    cc = d30 ** 2 / (d10 * d60) if d10 and d60 and d30 else None
    return d10, d30, d50, d60, cu, cc

for k, (bl, rd) in data.items():
    bD = blue_D[-len(bl):] if k.startswith("C3") else blue_D
    if k.startswith("C3"):
        bD = [9.52, 2.0, 0.84, 0.42, 0.25]  # en p232 el azul de #4 queda tapado por el rojo; se verifican abajo
    bx = np.array([b[0] for b in bl]); by = np.array([b[1] for b in bl])
    bP = np.array([P4[list(D).index(d)] for d in bD])
    ax, bxc = np.polyfit(np.log10(bD), bx, 1)
    ay, byc = np.polyfit(bP, by, 1)
    resx = bx - (ax * np.log10(bD) + bxc); resy = by - (ay * bP + byc)
    Ds = [10 ** ((x - bxc) / ax) for x, _ in rd]
    Ps = [(y - byc) / ay for _, y in rd]
    print(f"\n{k}: residuos calib x={np.round(resx,1)} y={np.round(resy,1)}")
    for d, p in zip(Ds, Ps):
        near = min(D, key=lambda s: abs(np.log10(s / d)))
        print(f"  D={d:7.3f} (malla {near:7.3f})  P={p:6.1f}")
    # usar tamaños nominales
    Dn = [min(D, key=lambda s: abs(np.log10(s / d))) for d in Ds]
    d10, d30, d50, d60, cu, cc = chars(Dn, Ps)
    P4m = Ps[Dn.index(4.76)]; P200 = Ps[Dn.index(0.074)]
    print(f"  D10={d10:.3f} D30={d30:.2f} D50={d50:.2f} D60={d60:.2f} Cu={cu:.0f} Cc={cc:.2f} grava={100-P4m:.1f} arena={P4m-P200:.1f} finos={P200:.1f}")

# Codisposal 4: calculado exacto desde la tabla p.93 (escalado bajo 4")
d10, d30, d50, d60, cu, cc = chars(list(D), list(P4))
print(f"\nC4 (calc p93/96.2): P#4={P4[8]:.1f} P#200={P4[-1]:.1f} D10={d10:.3f} D30={d30:.2f} D50={d50:.2f} D60={d60:.2f} Cu={cu:.0f} Cc={cc:.2f}")
