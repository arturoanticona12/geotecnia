import pymupdf as fitz, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_idiem import rows, D, F
G=fitz.open(os.path.join(D,F['G'])); W=fitz.open(os.path.join(D,F['W']))
def tab(doc,a,b,n=4):
    out=[]
    for p in range(a,b+1):
        for x0,r in rows(doc,p):
            if len(r)==n and x0>250: out.append(tuple(r))
    return out
pairs={'P1':((29,29),(252,253)),'P2':((31,40),(254,263)),'P3':((42,52),(265,275)),'P4':((54,55),(277,278)),'P5':((57,70),(280,293))}
for k,(g,w) in pairs.items():
    a=tab(G,*g); b=tab(W,*w)
    print(k,len(a),len(b),'identicas' if a==b else 'DIFIEREN', sum(1 for x,y in zip(a,b) if x!=y))
# edometro: todas las filas numericas de la pagina
def allnums(doc,p):
    return [r for x0,r in rows(doc,p)]
a=allnums(G,72); b=allnums(W,295)
print('edo filas',len(a),len(b), 'identicas' if a==b else 'DIFIEREN')
for x,y in zip(a,b):
    if x!=y: print(' G',x,'| W',y)
