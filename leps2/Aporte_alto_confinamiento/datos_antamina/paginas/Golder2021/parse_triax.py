import pymupdf, re, json, os
pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2021_Golder_Ensayos de Laboratorio Commingling.pdf"
out = os.path.dirname(os.path.abspath(__file__))
doc = pymupdf.open(pdf)
num = r"(-?\d+(?:\.\d+)?)"
res = []
for s in range(10):
    p0 = 108 + 7*s
    for k in range(3):
        pg = p0 + k
        t = doc[pg-1].get_text()
        r = {"pagina": pg, "set": s+1, "esp": k+1}
        def g(pat, cast=float):
            m = re.search(pat, t)
            return cast(m.group(1)) if m else None
        r["B"] = g(r"Par.metro B:\s*"+num)
        r["celda"] = g(r"Presi.n de Celda:\s*"+num)
        r["contra"] = g(r"Contrapresi.n:\s*"+num)
        r["s3"] = g(r"Inicial \(s3\):\s*"+num)
        r["t90"] = g(r"t90 \(minutos\):\s*"+num)
        r["eps_f"] = g(r"en la Falla \(%\):\s*"+num)
        m = re.search(r"Criterios de Falla:\s*"+r"\s+".join([num]*3), t)
        r["fall_s1"], r["fall_s1p"], r["fall_s3"] = (float(x) for x in m.groups()) if m else (None,)*3
        m = re.search(r"INICIAL\s+"+r"\s+".join([num]*7), t); r["ini"] = [float(x) for x in m.groups()] if m else None
        fins = re.findall(r"FINAL(?: \(corte\))?\s+"+r"\s+".join([num]*7), t)
        r["fin"] = [[float(x) for x in f] for f in fins]
        m = re.search(r"Observaciones:([^\n]*)", t); r["obs"] = m.group(1).strip() if m else None
        m = re.search(r"Sondaje\s*\n?:\s*([^\n]+)", t); r["sondaje"] = m.group(1).strip() if m else None
        m = re.search(r"Muestra\s*\n?:\s*([^\n]+)", t); r["muestra"] = m.group(1).strip() if m else None
        m = re.search(r"N. Informe\s*\n?:\s*([^\n]+)", t); r["informe"] = m.group(1).strip() if m else None
        m = re.search(r"Clasificaci.n SUCS:?\s*\n?\s*([A-Z]{2}(?:-[A-Z]{2})?)", t); r["sucs"]=m.group(1) if m else None
        # data table: tokens after the header '(kPa)' sequence
        lines = [l.strip() for l in t.split("\n")]
        idx = None
        for i in range(len(lines)-6):
            if lines[i].startswith("(%)") and lines[i+1].startswith("(kPa)") and lines[i+2].startswith("(%)"):
                idx = i; break
        rows=[]
        if idx is not None:
            j = idx
            while j < len(lines) and not re.fullmatch(num, lines[j]): j += 1
            toks=[]
            while j < len(lines) and re.fullmatch(num, lines[j]):
                toks.append(float(lines[j])); j+=1
            rows = [toks[i:i+8] for i in range(0, len(toks)-len(toks)%8, 8)]
            r["ntok"]=len(toks)
        r["rows"]=rows
        res.append(r)
json.dump(res, open(os.path.join(out,"triax_parse.json"),"w"), indent=0)
for r in res:
    rows=r["rows"]
    bad = [x for x in rows if abs((x[4]-x[3])-x[1])>1.0 or abs((x[4]+x[3])/2-x[5])>1.0]
    im = max(range(len(rows)), key=lambda i: rows[i][1]) if rows else None
    mx = rows[im] if rows else None
    print(r["pagina"], r["set"], r["esp"], r["informe"], r["sondaje"], r["muestra"], r["sucs"], "B",r["B"], "s3",r["s3"], "eps_f",r["eps_f"], "falla",r["fall_s1"],r["fall_s1p"],r["fall_s3"], "ini",r["ini"], "fin",r["fin"], "nrows",len(rows), "ntok", r.get("ntok"), "bad",len(bad), "max",mx, "last", rows[-1] if rows else None)
    print("   obs:", r["obs"])
