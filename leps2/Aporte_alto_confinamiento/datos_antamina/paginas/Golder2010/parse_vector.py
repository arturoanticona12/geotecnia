"""Parsea hojas CU de VECTOR (págs. 161-184): cabecera y fila de desviador máximo."""
import re, sys
from pathlib import Path

txt = Path(sys.argv[1]).read_text(encoding="utf-8")
parts = re.split(r"=== PÁGINA (\d+) ===", txt)
pg = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
num = re.compile(r"^-?\d+,\d+$")
for p in range(161, 185):
    t = pg[p]
    mat = re.search(r"Nº de muestra\n([^\n]+)", t)
    fase = re.search(r'FASE "([AB])"', t)
    if "Esf. Desv." not in t:
        cph = re.findall(r"(COHESI[^\n]*|ngulo[^\n]*|c'?\s*=\s*[\d,.]+[^\n]*|φ[^\n]*)", t)
        print(f"p{p}: {mat.group(1) if mat else '?'} Fase {fase.group(1) if fase else '?'} [gráfico/otro] {cph[:6]}")
        continue
    lines = [l.strip() for l in t.splitlines()]
    # cabecera: buscar bloque tras 'Altura'
    hdr = {}
    i = lines.index("Altura") if "Altura" in lines else None
    m = re.search(r"Altura\s*\n\(cm\)\n([\d,]+)\n([\d,]+)\n([\d,]+)\nDiámetro\s*\n\(cm\)\n([\d,]+)\n([\d,]+)\nkPa\n(\d+)\nHumedad\s*\n\(%\)\n([\d,]+)\n([\d,]+)\nkPa\n(\d+)\n([\d,]+)\n([\d,]+)\nkPa\n(\d+)", t)
    if m:
        hdr = dict(H0=m.group(1), Hf=m.group(2), B=m.group(3), D0=m.group(4), Df=m.group(5), celda=m.group(6),
                   w0=m.group(7), wf=m.group(8), contrap=m.group(9), gd0=m.group(10), gdf=m.group(11), s3c=m.group(12))
    vals = [float(l.replace(",", ".")) for l in lines if num.match(l)]
    # filas de 9: eps, desv, u, s3', s1', p', q, q/p, s1/s3 ; empiezan con 0,00 0,00 0,00
    try:
        k = next(j for j in range(len(vals) - 2) if vals[j] == 0 and vals[j + 1] == 0 and vals[j + 2] == 0)
    except StopIteration:
        print(f"p{p}: sin tabla", hdr); continue
    rows = [vals[j:j + 9] for j in range(k, len(vals) - 8, 9)]
    # descartar filas incoherentes (s1'-s3' != desv)
    good = [r for r in rows if abs((r[4] - r[3]) - r[1]) < 0.5]
    best = max(good, key=lambda r: r[1])
    print(f"p{p}: {mat.group(1).strip() if mat else '?'} Fase {fase.group(1) if fase else '?'} {hdr} filas={len(rows)} ok={len(good)} "
          f"MAXDESV: eps={best[0]} q={best[1]} u={best[2]} s3'={best[3]} s1'={best[4]} p'={best[5]} t={best[6]} ; ultima={good[-1][:5]}")
