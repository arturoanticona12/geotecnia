"""Conteo de fragmentos por tipo de roca y validez en las hojas de carga puntual IDIEM 1.914.482-G (dentro del F), WSP 2024 pp.356-363."""
import sys, re, pymupdf
from collections import Counter

doc = pymupdf.open(sys.argv[1])
rx = re.compile(r'\n([A-Z])\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n([\d,]+)\n(.*?)(?=\n[A-Z]\n[\d,]+\n|\nResultados)', re.S)
tot = Counter(); allf = []
for p in range(355, 364):
    t = doc[p - 1].get_text()
    if 'CARGA PUNTUAL' not in t:
        continue
    hum = re.search(r'Humedad \[%\]\s*\n\s*([\d,]+)', t)
    is50 = re.search(r'"Is \(50\)" \[MPa\]\s*\n\s*([\d,]+)', t)
    frs = []
    for m in rx.finditer(t):
        rest = ' '.join(x.strip() for x in m.group(10).split('\n') if x.strip())
        roca = rest.split(' ')[0]
        valida = 'no válida' not in rest.lower() and 'no valida' not in rest.lower()
        is50f = float(m.group(9).replace(',', '.'))
        frs.append((m.group(1), roca, is50f, valida, rest))
    c = Counter(f[1] for f in frs)
    tot.update(c)
    allf += frs
    print(f'p{p}: n={len(frs)} {dict(c)} w={hum.group(1) if hum else None} Is50 hoja={is50.group(1) if is50 else None}'
          f' | media válidos={sum(f[2] for f in frs if f[3]) / max(1, sum(f[3] for f in frs)):.2f} (n={sum(f[3] for f in frs)})'
          f' | media todos={sum(f[2] for f in frs) / max(1, len(frs)):.2f}')
    for f in frs:
        if not f[3]:
            print('    no válida:', f[0], f[1], f[2], f[4][:80])
print('TOTAL', dict(tot), 'n =', len(allf))
for roca in tot:
    v = [f[2] for f in allf if f[1] == roca and f[3]]
    print(roca, 'válidos', len(v), 'media %.2f' % (sum(v) / len(v)), 'rango', min(v), max(v))
