"""Parsea las hojas 'INFORME ENSAYO TRIAXIAL CID' (IDIEM) del texto extraído del informe WSP 2024.
Agrupa por (informe, muestra, probeta, tipo) y entrega máximo q=(s1-s3)/2, con eps_a y eps_v en ese punto.
"""
import re, json, sys
from pathlib import Path

base = Path(__file__).resolve().parents[2]
txt = (base / "texto" / "2024_WSP_Ensayos gran escala mezcla co-disposicion.txt").read_text(encoding="utf-8")
parts = re.split(r"=== PÁGINA (\d+) ===", txt)
pages = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}

num = r"-?\d+,\d+"
row_re = re.compile(rf"^\s*({num})\s*\|?\s*$")

def fnum(s):
    return float(s.replace(",", "."))

def hdr(t, key):
    m = re.search(re.escape(key) + r"[^\n]*\n\s*\[[^\]]*\]=\s*\|?\s*\n?\s*([\d,\.]+)", t)
    return m.group(1) if m else None

tests = {}
order = []
for p in sorted(pages):
    t = pages[p]
    if "INFORME ENSAYO TRIAXIAL CID" not in t:
        continue
    rep = re.search(r"Informe Ensayo Nº (1\.914\.482-[A-F])", t).group(1)
    mu = re.search(r"(Codisposal \d[^\n|]*)", t.split("PROBETA")[0][-400:])
    mu = re.findall(r"(Codisposal \d \([^\n]*\))", t)
    prob = re.findall(r"PROBETA\s*(\d)", t)
    lines = [l.strip().rstrip("|").strip() for l in t.split("\n")]
    # números sueltos tras el encabezado de columnas
    try:
        start = max(i for i, l in enumerate(lines) if l.startswith("[kg/cm²]"))
    except ValueError:
        start = 0
    vals = []
    for l in lines[start + 1:]:
        if re.fullmatch(num, l):
            vals.append(fnum(l))
        elif re.match(rf"^{num}\s", l):
            # '0,01 ' seguido de texto
            vals.append(fnum(l.split()[0]))
    rows = [vals[i:i + 4] for i in range(0, len(vals) - len(vals) % 4, 4)]
    head = dict(
        vol_cons=hdr(t, "Variación Volumen drenado"),
        dens=hdr(t, "Densidad Seca de Confección"),
        w=hdr(t, "Humedad de Confección"),
        bp=hdr(t, "Contrapresión"),
        cell=hdr(t, "Presión de Cámara Total"),
        H=hdr(t, "Altura   Inicial"),
        D=hdr(t, "Diámetro Inicial"),
    )
    key = (rep, mu[-1] if mu else "?", prob[-1] if prob else "?", head["vol_cons"])
    if key not in tests:
        tests[key] = dict(pages=[], rows=[], head=head)
        order.append(key)
    tests[key]["pages"].append(p)
    tests[key]["rows"].extend(rows); tests[key].setdefault("rp", []).extend([p]*len(rows))

out = []
for k in order:
    d = tests[k]
    rows = d["rows"]
    # chequeo de consistencia: p - q debe ser constante (= sigma3')
    s3 = [round(r[2] - r[3], 2) for r in rows]
    bad = [i for i, x in enumerate(s3) if abs(x - s3[0]) > 0.03]
    imax = max(range(len(rows)), key=lambda i: rows[i][3])
    r = rows[imax]
    last = rows[-1]
    out.append(dict(rep=k[0], muestra=k[1], probeta=k[2], pages=f"{d['pages'][0]}-{d['pages'][-1]}", n=len(rows),
                    head=d["head"], s3=s3[0], n_bad=len(bad), bad_ex=[rows[i] for i in bad[:3]],
                    qmax=r[3], pmax=r[2], ea=r[0], ev=r[1], last=last,
                    page_peak=d["rp"][imax], row_idx_in_page=imax - d["rp"].index(d["rp"][imax])))
for o in out:
    print(json.dumps(o, ensure_ascii=False))


