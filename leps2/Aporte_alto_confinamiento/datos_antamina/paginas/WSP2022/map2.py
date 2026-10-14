import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'=== PÁGINA (\d+) ===',t)
kw=re.compile(r'(ANEXO|Informe N|INFORME|Ensayo [A-ZÁa-z]+|ENSAYO|Triaxial|TRIAXIAL|Edom|EDOM|Granulom|GRANULOM|Permeab|PERMEAB|Densidad|Gravedad|Probeta|PROBETA|Muestra|Report|Test|TEST|Gs|Specific|Consolid|Cyclic|CYCLIC|Oedometer|Gradation|Proctor)')
for i in range(1,len(parts),2):
    p=int(parts[i])
    if p<46: continue
    body=parts[i+1]
    lines=[l.strip() for l in body.splitlines() if l.strip() and not l.startswith('La reproducción') and not l.startswith('Nota') and 'IDIEM' not in l[:5]]
    hits=[l for l in lines if kw.search(l)][:5]
    print(p,len(body),' | '.join(hits)[:230])
