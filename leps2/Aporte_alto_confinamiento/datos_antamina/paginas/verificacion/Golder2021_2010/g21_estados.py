import json,sys,re,fitz
d=json.load(open(sys.argv[1])); doc=fitz.open(sys.argv[2])
t8=[283,1518,4647,596,1977,4658,540,1780,4469,434,1356,3863,547,1714,4529,493,1700,4461,445,1470,4170,614,1818,4670,602,1736,4407,437,1415,3751]
res={}
for k,(p,v) in enumerate(d.items()):
    rows=[r for r in v['rows'] if abs(r[4]-r[3]-r[1])<=0.06 and r[3]>0]
    # dedupe by eps
    seen=set(); rr=[]
    for r in rows:
        if r[0] in seen: continue
        seen.add(r[0]); rr.append(r)
    md=max(rr,key=lambda r:r[1]); mo=max(rr,key=lambda r:r[4]/r[3]); last=rr[-1]
    t=doc[int(p)-1].get_text()
    gs=re.findall(r'\n\s*(2\.\d{2,3}|3\.\d{2,3})\s*\n',t[t.find('Específica')-400:t.find('Específica')+60]) if 'Específica' in t else []
    print(p,'n',len(rr),'maxq %.2f eps %.2f ev %.2f s3 %.2f s1 %.2f | T8 %d diff %.1f | maxobl %.3f eps %.2f s3 %.2f s1 %.2f q %.2f | last eps %.2f'%(md[1],md[0],md[2],md[3],md[4],t8[k],md[1]-t8[k],mo[4]/mo[3],mo[0],mo[3],mo[4],mo[1],last[0]),'Gs?',gs)
    res[p]={'maxq':md,'maxobl':mo,'last':last,'n':len(rr)}
json.dump(res,open(sys.argv[3],'w'))
