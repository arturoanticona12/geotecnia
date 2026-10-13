import sys, pymupdf, re
pdf = sys.argv[1]
doc = pymupdf.open(pdf)
num = re.compile(r'^-?\d+,\d+$')
cur = None; data = {}; hdr = {}
for i in range(9, 28):
    pg = doc[i]
    txt = pg.get_text()
    m = re.search(r'PROBETA\s*(\d)', txt)
    if m: cur = int(m.group(1)); data.setdefault(cur, []); hdr[cur] = []
    for key in ['Fecha de Inicio','Fecha de T','Contrapresi','Presi.n de C.mara','Densidad Seca','Humedad','Variaci.n Volumen','Velocidad']:
        pass
    words = pg.get_text('words')
    rows = {}
    for w in words:
        if num.match(w[4]) and w[0] > 190:
            rows.setdefault(round(w[1]/2), []).append((w[0], float(w[4].replace(',','.'))))
    for y in sorted(rows):
        r = [v for x, v in sorted(rows[y])]
        if len(r) == 4:
            data[cur].append((i+1, *r))
    print('pag', i+1, 'cur', cur, 'rows4', sum(1 for y in rows if len(rows[y])==4))
print({k: len(v) for k, v in data.items()})
for k, rs in data.items():
    if not rs: continue
    # chequeo p - q = sigma3
    s3 = rs[0][3]
    bad = [r for r in rs if abs((r[3]-r[4]) - s3) > 0.015]
    imax = max(range(len(rs)), key=lambda j: rs[j][4])
    r = rs[imax]
    p, q = r[3], r[4]
    import math
    print(f"Probeta {k}: n={len(rs)} s3={s3} filas p-q!=s3: {len(bad)}; max q={q} en pag {r[0]} ea={r[1]} ev={r[2]} p={p}; dev={2*q:.2f} kgf/cm2 = {2*q*98.0665:.1f} kPa; s1={(p+q)*98.0665:.1f} kPa; phi={math.degrees(math.asin(q/p)):.2f}; max s1/s3 = {max((rr[3]+rr[4])/(rr[3]-rr[4]) for rr in rs):.3f}")
    j = max(range(len(rs)), key=lambda j: (rs[j][3]+rs[j][4])/(rs[j][3]-rs[j][4]))
    print('   max oblicuidad fila', rs[j], ' final', rs[-1], ' min ev', min(rs, key=lambda r: r[2]))
    if bad: print('   ejemplos bad', bad[:5])



