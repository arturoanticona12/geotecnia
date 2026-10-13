import fitz, sys, re, json
doc=fitz.open(sys.argv[1])
res={}
for p in [161,162,163,167,168,169,173,174,175,179,180,181]:
    t=doc[p-1].get_text()
    if len(t.strip())<50:
        print(p,'SIN TEXTO'); continue
    nums=re.findall(r'-?\d+,\d+|-?\d+ \d{2}(?=\s)',t)
    # cabecera
    hdr=t[:t.find('Esf. Desv')]
    print('=== p',p, 'muestra', re.search(r'Nº de muestra\s*\n(.*)',t).group(1))
    print(' cabecera nums:', re.findall(r'\d+,\d+|\b\d{3,4}\b',hdr)[:30])
    # filas
    after=t[t.find('kPa\nkPa\nkPa\nkPa\nkPa\nkPa'):]
    vals=[float(x.replace(',','.')) for x in re.findall(r'-?\d+,\d+',after)]
    rows=[];
    i=0
    while i+9<=len(vals):
        r=vals[i:i+9]; rows.append(r); i+=9
    # dedup by eps keeping first
    seen={};clean=[]
    for r in rows:
        if r[0] in seen: continue
        seen[r[0]]=1; clean.append(r)
    ok=all(abs(r[4]-r[3]-r[1])<0.05 for r in clean)
    print(' nfilas',len(clean),'check s1-s3=desv',ok)
    for r in clean: 
        if abs(r[4]-r[3]-r[1])>=0.05: print('  BAD',r)
    res[p]=clean
json.dump(res,open(sys.argv[2],'w'))
