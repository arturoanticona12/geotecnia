import pymupdf as fitz, os, sys, re, pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse_idiem import rows, D, F
W=fitz.open(os.path.join(D,F['W']))
B=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Aporte_alto_confinamiento\datos_antamina\extraido"
E=pd.read_csv(B+r"\WSP_2022_edometro.csv")
def tab3(pages):
    out=[]
    for p in pages:
        for x0,r in rows(W,p):
            if len(r)==3 and x0>200: out.append(r)
    return out
K=98.0665
for name,pages in [('HF-edo-1.0m (IDIEM)',[300,301,302]),('MN-edo-1.0m-2021 (IDIEM)',[324])]:
    t=tab3(pages); c=E[E.ensayo_id==name]
    print(name,'filas pdf',len(t),'csv',len(c))
    bad=0
    for (s,ev,e),(_,r) in zip(t,c.iterrows()):
        if abs(s*K-r.sigma_v_kPa)>0.1 or abs(ev-r.eps_v_pct)>1e-6 or abs(e-r.e)>1e-6: bad+=1; print('  dif',s,ev,e,'|',r.sigma_v_kPa,r.eps_v_pct,r.e)
    print('  filas distintas:',bad, ' max sigma pdf',max(x[0] for x in t),'eps final',t[-1][1])
# 2011: tension, asent, H, dens, e (+obs) -> filas con >=5 numeros
t=[]
for x0,r in rows(W,295):
    if len(r)>=5: t.append(r)
c=E[E.ensayo_id.str.startswith('MN-edo-1.0m-2011')]
print('2011 filas pdf',len(t),'csv',len(c))
bad=0
for r1,(_,r) in zip(t,c.iterrows()):
    s,a,H,dd,e=r1[:5]; eps=(90-H)/90*100
    if abs(s*K-r.sigma_v_kPa)>0.15 or abs(round(eps,2)-r.eps_v_pct)>0.011 or abs(e-r.e)>1e-6: bad+=1; print('  dif',r1[:5],round(eps,3),'|',r.sigma_v_kPa,r.eps_v_pct,r.e)
print('  filas distintas',bad)
# Golder MN test1 p359: filas Load#, stress, dH, d, eps, H-Hs, e ...
G=[r for x0,r in rows(W,359)]
print('p359 sample rows', G[:3])
c=E[E.ensayo_id.str.startswith('MN-edo-0.24m')]
print(c[['sigma_v_kPa','eps_v_pct','e']].to_string())
