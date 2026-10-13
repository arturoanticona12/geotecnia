import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
parts=re.split(r'=== PÁGINA (\d+) ===',t)
pages={int(parts[i]):parts[i+1] for i in range(1,len(parts),2)}
for p in [72,74,76,78,80,82]:
    b=pages[p]
    L=[l.strip() for l in b.splitlines() if l.strip()]
    def after(k,n=1):
        for i,l in enumerate(L):
            if l.startswith(k): return L[i+1:i+1+n]
    print(p,'Muestra',after('Muestra'),'Tipo',after('Tipo de Roca'),'Fract',after('Fracturas'),'Alt',after('Alteraciones'))
    print('   ', [l for l in L if re.match(r'^\d+,\d+$',l)][:12])
    m=re.search(r'Resistencia M[aá]x\. D50[^\n]*\n(.*\n){0,6}',b); 
    print('   D50 block:',re.findall(r'Resistencia M[aá]x[^\n]*',b), re.findall(r'falla por[^\n]*\n?[^\n]*',b))
