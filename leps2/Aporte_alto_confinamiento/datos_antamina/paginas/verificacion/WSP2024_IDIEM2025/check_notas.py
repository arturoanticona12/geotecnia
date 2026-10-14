"""Cruza las notas del CSV extraído (vol. drenado, densidad post-consolidación, e_c) con los encabezados parseados del PDF."""
import sys, re, json, math
import pandas as pd

df = pd.read_csv(sys.argv[1])
tx = json.load(open(sys.argv[2], encoding='utf-8'))
tx = [t for t in tx if t['ea_final'] > 10]  # descarta primeras páginas partidas por el parser
V0 = math.pi * 30 ** 2 * 120
for i, r in df.iterrows():
    m = [t for t in tx if abs(t['dev_kPa'] - r.q_kPa) < 0.05 and abs(t['s3'] * 98.0665 - r.sigma3_kPa) < 1]
    t = m[0] if m else None
    dv = re.search(r'consolidación (\d+) cm', r.notas)
    rp = re.search(r'post-consolidación ([\d.]+) g/cm³ \(p\.(\d+)\) → e_c≈([\d.]+)', r.notas)
    dvh = float(t['hdr']['Variación Volumen'].replace(',', '.'))
    dens0 = float(t['hdr']['Densidad Seca'].replace(',', '.'))
    dpost = dens0 / (1 - dvh / V0)
    ec = r.Gs / dpost - 1
    print(r.set_id, r.sigma3_kPa, '| dV csv', dv.group(1) if dv else None, 'pdf', dvh,
          '| dpost csv', rp.group(1) if rp else None, 'p', rp.group(2) if rp else None, 'calc %.3f' % dpost,
          '| e_c csv', rp.group(3) if rp else None, 'calc %.3f' % ec,
          '| w', t['hdr']['Humedad'], 'BP', t['hdr']['Contrapresión'], 'Pc', t['hdr']['Presión de Cámara'],
          '| ea_fin', t['ea_final'], '| pags', t['pages'], '| e0', round(r.Gs / dens0 - 1, 4))
