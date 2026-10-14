import pymupdf, pathlib, re, json
src = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos\Triaxial CU 6 in")
d = pathlib.Path(__file__).parent
NUM = re.compile(r"^-?\d+([.,]\d+)?$")
def key(n):
    n=n.lower()
    return "M" if n.startswith("marmol") else "I" if n.startswith("intrusivo") else "H" if n.startswith("hornfels") else "P1" if "pila 01" in n else "P2"
def rowvals(words, y, x0, tol=3):
    return [float(w[4].replace(",",".")) for w in sorted(words,key=lambda w:w[0]) if abs((w[1]+w[3])/2-y)<tol and w[0]>x0 and NUM.match(w[4])]
res={}
for f in sorted(src.glob("*.pdf")):
    k=key(f.name); doc=pymupdf.open(f); out=[]
    for pi,p in enumerate(doc):
        W=p.get_text("words")
        txt=p.get_text()
        if "Etapa de consolidación" not in txt: continue
        def lab(s):
            c=[w for w in W if w[4]==s]
            return c
        info={}
        for name,first in [("Altura","Altura"),("Diametro","Diámetro"),("w","Contenido"),("rho","Densidad"),("B",'Parámetro'),("vel","Velocidad"),("cell","Presión"),("bp","Contra")]:
            c=lab(first)
            if name=="cell": c=[w for w in c if any(v[4]=="celda" and abs(v[1]-w[1])<3 for v in W)]
            if name=="w": c=[w for w in c if w[1]>250]
            if not c: info[name]=None; continue
            w0=c[0]; y=(w0[1]+w0[3])/2
            info[name]=rowvals(W,y,w0[2]+30)
        s3=[w for w in W if w[4]=="kPa" and w[1]<300 and w[0]>450]
        s3v=[ww[4] for ww in W if abs(ww[1]-s3[0][1])<3 and NUM.match(ww[4])] if s3 else None
        # table rows: lines with 9 numbers below header 'Deform.'
        hdr=[w for w in W if w[4].startswith("Deform")][0]
        ys=sorted(set(round((w[1]+w[3])/2,1) for w in W if w[1]>hdr[3]+5 and NUM.match(w[4])))
        rows=[]; seen=set()
        for y in ys:
            if any(abs(y-s)<2 for s in seen): continue
            r=rowvals(W,y,0,2.5)
            if len(r)==9: rows.append(r); seen.add(y)
        out.append(dict(page=pi+1, s3=s3v, **info, rows=rows))
    res[k]=out
    for o in out:
        r=o["rows"]; qmax=max(r,key=lambda x:x[1])
        print(k,o["page"],"s3",o["s3"],"H",o["Altura"],"D",o["Diametro"],"w",o["w"],"rho",o["rho"],"B",o["B"],"v",o["vel"],"cell",o["cell"],"bp",o["bp"],"n",len(r))
        print("   last",r[-1]," qmax",qmax)
(d/"tx_parsed.json").write_text(json.dumps(res,indent=1),encoding="utf-8")
