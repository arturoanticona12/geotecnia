"""Verificación independiente: parseo de todas las hojas 'INFORME ENSAYO TRIAXIAL CID' del PDF WSP 2024.
Agrupa páginas consecutivas con el mismo encabezado y extrae máximo q (MIT), fila final, ev, etc.
Uso: python parse_wsp24_tx.py <pdf> [salida.json]"""
import sys, re, math, json, pymupdf

doc = pymupdf.open(sys.argv[1])
num = re.compile(r'^-?\d+,\d+$')
KEYS = ['Altura', 'Diámetro', 'Variación Volumen', 'Densidad Seca', 'Humedad',
        'Contrapresión', 'Presión de Cámara', 'Velocidad']
tests = []
for i in range(len(doc)):
    pg = doc[i]
    t = pg.get_text()
    if 'INFORME ENSAYO TRIAXIAL' not in t:
        continue
    hdr, lab = {}, {}
    for b in pg.get_text('blocks'):
        s = b[4]
        if b[0] > 150 and 125 < b[1] < 215:
            lab[round(b[1])] = s.strip().replace('\n', ' ')
        for key in KEYS:
            if s.strip().startswith(key):
                hdr[key] = s.strip().split('\n')[-1].strip()
    labs = [lab[k] for k in sorted(lab)]
    ws = sorted([w for w in pg.get_text('words') if num.match(w[4]) and w[1] > 200 and w[0] > 190], key=lambda w: (w[1] + w[3]) / 2)
    clusters = []
    for w in ws:
        yc = (w[1] + w[3]) / 2
        if clusters and abs(yc - clusters[-1][0]) < 2.0:
            clusters[-1][1].append(w)
        else:
            clusters.append([yc, [w]])
    data = []
    nskip = 0
    for yc, cw in clusters:
        r = [float(w[4].replace(',', '.')) for w in sorted(cw, key=lambda w: w[0])]
        if len(r) == 4:
            data.append((i + 1, *r))
        else:
            nskip += 1
    if nskip > 12: print('  filas no-4 en pag', i + 1, nskip)
    sig = json.dumps([labs, sorted(hdr.items())], ensure_ascii=False)
    if not tests or tests[-1]['sig'] != sig or tests[-1]['pages'][-1] != i:
        tests.append({'sig': sig, 'hdr': hdr, 'labs': labs, 'data': [], 'pages': []})
    tests[-1]['data'] += data
    tests[-1]['pages'].append(i + 1)

res = []
for T in tests:
    rs = T['data']
    h = T['hdr']
    if not rs:
        print('SIN DATOS', T['labs'], T['pages'])
        continue
    s3 = rs[0][3] - rs[0][4]
    bad = [r for r in rs if abs((r[3] - r[4]) - s3) > 0.015]
    j = max(range(len(rs)), key=lambda j: rs[j][4])
    r = rs[j]
    nmax = sum(1 for x in rs if x[4] == r[4])
    d = dict(labs=T['labs'], pages=f"{T['pages'][0]}-{T['pages'][-1]}", hdr=h, n=len(rs), s3=round(s3, 3),
             n_bad=len(bad), qmax=r[4], qmax_page=r[0], ea=r[1], ev=r[2], p=r[3], nmax=nmax,
             dev_kPa=round(2 * r[4] * 98.0665, 1), s1_kPa=round((r[3] + r[4]) * 98.0665, 1),
             phi=round(math.degrees(math.asin(r[4] / r[3])), 2),
             ea_final=rs[-1][1], q_final=rs[-1][4], ev_final=rs[-1][2],
             ev_min=min(x[2] for x in rs), ev_max=max(x[2] for x in rs))
    res.append(d)
    print(' / '.join(T['labs']), '|', d['pages'], '|',
          ' '.join(f"{k[:6]}={v}" for k, v in h.items()))
    print(f"    n={d['n']} s3={d['s3']} bad={d['n_bad']} qmax={d['qmax']} (x{nmax}) p{d['qmax_page']} ea={d['ea']} ev={d['ev']} "
          f"p={d['p']} dev={d['dev_kPa']} s1={d['s1_kPa']} phi={d['phi']} | fin ea={d['ea_final']} q={d['q_final']} ev={d['ev_final']} | evmin={d['ev_min']} evmax={d['ev_max']}")
if len(sys.argv) > 2:
    json.dump(res, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
