import sys, pymupdf as fitz, os, re
D=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina"
F={'G':"2012_Golder_Triaxiales Gran Escala en Marmol Negro.pdf",'W':"2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"}
num=re.compile(r'^-?\d+,\d+$')
def rows(doc,p):
    ws=doc[p-1].get_text('words')
    ws=[w for w in ws if num.match(w[4])]
    R={}
    for w in ws:
        k=round((w[1]+w[3])/2/3)
        R.setdefault(k,[]).append(w)
    out=[]
    for k in sorted(R):
        r=sorted(R[k],key=lambda w:w[0])
        out.append((r[0][0],[float(w[4].replace(',','.')) for w in r]))
    return out
if __name__=='__main__':
    key=sys.argv[1]; groups=sys.argv[2:]  # name:pages e.g. P1:29 P2:31-40
    doc=fitz.open(os.path.join(D,F[key]))
    for g in groups:
        name,pr=g.split(':'); a,b=(pr.split('-')+[pr])[:2]; a=int(a); b=int(b)
        data=[]
        for p in range(a,b+1):
            for x0,r in rows(doc,p):
                if len(r)==4 and x0>250: data.append((p,)+tuple(r))
        if not data: print(name,'sin datos'); continue
        m=max(data,key=lambda d:d[4]); last=data[-1]
        print(f"{name}: n={len(data)} max t={m[4]} p={m[3]} ea={m[1]} ev={m[2]} (pag {m[0]}) | fin ea={last[1]} ev={last[2]} t={last[4]} | sigma3=p-t: {sorted(set(round(d[3]-d[4],2) for d in data))[:6]}")
