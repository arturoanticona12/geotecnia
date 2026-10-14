import pymupdf, sys, re, json, math
d = pymupdf.open(sys.argv[1])
num = re.compile(r'^-?[\d\.]+,\d+$')
groups = {1: range(10,15), 2: range(16,21), 3: range(22,28)}
res = {}
for pr, pages in groups.items():
    rows = []
    for pg in pages:
        p = d[pg-1]
        ws = p.get_text("words")
        lines = {}
        for w in ws:
            x0,y0,x1,y1,t = w[:5]
            if x0 > 195 and num.match(t):
                key = round((y0+y1)/2,0)
                lines.setdefault(key, []).append((x0,t))
        hdr=[]
        for k in sorted(lines):
            v = [float(t.replace('.','').replace(',','.')) for x,t in sorted(lines[k])]
            if len(v)==4: rows.append(v+[pg])
            elif len(v)==1: hdr.append(v[0])
            else: print("irregular", pr, pg, k, v)
        if pg==pages[0]:
            print(pr, "header nums:", hdr)
            for w in ws:
                if 140<w[1]<215 and w[0]>140: print("   ", round(w[1]), w[4], end="")
            print()
    res[pr]=rows
    ea=[r[0] for r in rows]; ev=[r[1] for r in rows]; P=[r[2] for r in rows]; q=[r[3] for r in rows]
    i=max(range(len(q)), key=lambda j:q[j])
    s3=P[0]-q[0]
    print(f"Probeta {pr}: n={len(rows)} first={rows[0]} s3={s3} qmax={q[i]} ea={ea[i]} ev={ev[i]} p={P[i]} pag={rows[i][4]} phi={math.degrees(math.asin(q[i]/P[i])):.2f}")
    print("  ultimo", rows[-1], " min ev", min(ev), "at ea", ea[ev.index(min(ev))], "max ev", max(ev))
    # q at 15% axial (first row with ea>=15)
    for r in rows:
        if r[0]>=15: print("  primera fila ea>=15:", r); break
    # monotonic check ea
    bad=[j for j in range(1,len(ea)) if ea[j]<ea[j-1]]
    print("  descensos ea en filas:", bad[:10])
    # rows near peak
    for r in rows[max(0,i-3):i+4]: print("   ", r)
json.dump(res, open(sys.argv[2],'w'))
