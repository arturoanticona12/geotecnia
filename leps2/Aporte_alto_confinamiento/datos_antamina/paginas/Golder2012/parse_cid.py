"""Parsea las tablas eps, ev, p, q (kg/cm2, q=(s1-s3)/2) del anexo IDIEM 708.397-A
del texto extraído y reporta el máximo q por probeta (para luego verificar en imagen)."""
import re, sys
from pathlib import Path

txt = Path(sys.argv[1]).read_text(encoding="utf-8")
pages = re.split(r"=== PÁGINA (\d+) ===", txt)
pg = {int(pages[i]): pages[i + 1] for i in range(1, len(pages), 2)}

probetas = {1: [29], 2: list(range(31, 41)), 3: list(range(42, 53)),
            4: [54, 55], 5: list(range(57, 71))}
num = re.compile(r"^-?\d+,\d+$")
for k, plist in probetas.items():
    rows = []
    for p in plist:
        t = pg[p]
        # header info
        if p == plist[0]:
            for key in ["Volumen drenado etapa consolidación", "Densidad Seca de Confección",
                        "Humedad de Confección", "Contrapresión", "Presión de Cámara Total",
                        "Fecha de Inicio", "Fecha de Término"]:
                m = re.search(re.escape(key) + r".*?\n(?:\[.*?\]=\n)?([\d,\-]+)", t)
                print(f"P{k} {key}: {m.group(1) if m else None}")
        idx = t.find("[kg/cm²]\n[kg/cm²]")
        body = t[idx:]
        vals = [float(l.strip().replace(",", ".")) for l in body.splitlines() if num.match(l.strip())]
        for i in range(0, len(vals) - 3, 4):
            rows.append((p, *vals[i:i + 4]))
    # sanity: p - q should be ~ s3 (constant)
    bad = [r for r in rows if abs((r[3] - r[4]) - rows[0][3] + rows[0][4]) > 0.1]
    imax = max(range(len(rows)), key=lambda i: rows[i][4])
    r = rows[imax]
    print(f"P{k}: n={len(rows)}, filas con p-q != s3: {len(bad)}; max q={r[4]} en pag {r[0]}: "
          f"ea={r[1]} ev={r[2]} p={r[3]} q={r[4]}; ultima fila {rows[-1]}")
    if bad[:3]:
        print("   ejemplos malos:", bad[:3])
