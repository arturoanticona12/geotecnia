import json
P=json.load(open('pts35.json'))
X=lambda x:(x-342.93)/(530.22-342.93)*6000
out={}
for key,y0,y1,ymax,name in [('(0.0, 0.69, 0.31)',172.87,299.49,6.0,'HF_P2_024'),('(0.75, 0.0, 0.0)',363.72,511.49,18.0,'HF_P3_024')]:
    pts=[p for p in P[key] if p[0]>340 and not (395<p[0]<406 and (p[1]<190 or 370<p[1]<380))]
    rows=[(round(X(x)),round((y-y0)/(y1-y0)*ymax,2)) for x,y in pts]
    out[name]=rows; print(name,rows)
json.dump(out,open('edo024_hf.json','w'))
