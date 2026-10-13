import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'=== PÁGINA (\d+) ===',t)
for i in range(1,len(parts),2):
    p=int(parts[i]); body=parts[i+1].strip()
    lines=[l.strip() for l in body.splitlines() if l.strip()]
    print(p,len(body),' | '.join(lines[:4])[:150])
