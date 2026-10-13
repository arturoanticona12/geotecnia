import re,sys,json
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'=== PÁGINA (\d+) ===',t)
pages={int(parts[i]):parts[i+1] for i in range(1,len(parts),2)}
num=re.compile(r'^-?\d+(\.\d{3})*(,\d+)?$')
def f(x): return float(x.replace('.','').replace(',','.'))
out={}
for name,pp in [('HF',[300,301,302]),('MN21',[324]),('MN11',[295])]:
    rows=[]
    for p in pp:
        body=pages[p]
        i=body.find('de Vac')
        if i<0: i=body.find('Relación de Vac')
        seg=body[i:]
        toks=[l.strip() for l in seg.splitlines() if num.match(l.strip())]
        vals=[f(x) for x in toks]
        k=0
        while k+2<len(vals):
            s,e,ev=vals[k:k+3]
            if 0<=s<=100 and 0<=e<30 and 0.05<ev<0.6:
                rows.append((s,e,ev,p));k+=3
            else: k+=1
    out[name]=rows
    print(name,len(rows))
    for r in rows: print('  ',r)
json.dump(out,open(sys.argv[2],'w'))
