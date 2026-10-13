import re,sys,json
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'=== PÁGINA (\d+) ===',t)
pages={int(parts[i]):parts[i+1] for i in range(1,len(parts),2)}
num=re.compile(r'^-?\d+(\.\d{3})*(,\d+)?$')
def f(x): return float(x.replace('.','').replace(',','.'))
tests={}
for p in range(102,296):
    body=pages[p]
    m=re.search(r'Probeta\s*\n\s*(PROBETA \d+)',body) or re.search(r'Muestra\s*\n\s*(Probeta \d[^\n]*)',body)
    if not m: continue
    rep='E' if p<229 else ('B.2' if p<252 else '708.397-A'); key=rep+'|'+m.group(1).strip()
    hdr={}
    for lab,pat in [('H','Altura[^\n]*\n[^\n]*\n\s*([\d,\.]+)'),('D','Di[aá]metro[^\n]*\n[^\n]*\n\s*([\d,\.]+)'),('dV','Variaci[oó]n Volumen[^\n]*\n[^\n]*\n\s*([\d,\.]+)'),('gd','Densidad Seca[^\n]*\n[^\n]*\n\s*([\d,\.]+)'),('w','Humedad[^\n]*\n[^\n]*\n\s*([\d,\.]+)'),('bp','Contrapresi[oó]n[^\n]*\n[^\n]*\n\s*([\d,\.]+)'),('cell','C[aá]mara Total[^\n]*\n[^\n]*\n\s*([\d,\.]+)')]:
        mm=re.search(pat,body)
        if mm: hdr[lab]=mm.group(1)
    toks=[l.strip() for l in body.splitlines() if num.match(l.strip())]
    # find start: data quads after header values; take tokens after the last header token
    rows=[]
    # brute: slide over tokens; accept quads where |(p-q) - const| small
    vals=[f(x) for x in toks]
    i=0
    while i+3<len(vals):
        ea,ev,pp,q=vals[i:i+4]
        if abs(pp-q - round(pp-q))<0.06 and pp>=q and abs(ea)<40 and abs(ev)<30 and pp-q>=2:
            rows.append((ea,ev,pp,q,p)); i+=4
        else: i+=1
    T=tests.setdefault(key,{'hdr':{},'rows':[],'pages':[]})
    if hdr and not T['hdr']: T['hdr']=hdr
    T['rows']+=rows; T['pages'].append(p)
for k,T in tests.items():
    h=T['hdr']; s3e=f(h.get('cell','0'))-f(h.get('bp','0'))
    r=[x for x in T['rows'] if abs(x[2]-x[3]-s3e)<0.06]; T['rows']=r
    if not r: print(k,T['pages'][:3],'NO ROWS');continue
    s3=sorted(set(round(x[2]-x[3],1) for x in r))
    mx=max(r,key=lambda x:x[3])
    last=r[-1]
    print(k,'pages',T['pages'][0],'-',T['pages'][-1],'n',len(r),'hdr',T['hdr'],'s3set',s3[:5])
    print('   max t',mx,' last',last, ' min ev',min(x[1] for x in r))

json.dump({k:v for k,v in tests.items()},open(sys.argv[2],'w'))

