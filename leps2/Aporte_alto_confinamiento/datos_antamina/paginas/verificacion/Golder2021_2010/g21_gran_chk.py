import fitz,sys,re,pandas as pd
doc=fitz.open(sys.argv[1]); df=pd.read_csv(sys.argv[2])
for p in range(46,56):
    t=doc[p-1].get_text()
    def g(k):
        m=re.search(k+r'\s*=\s*([\d.]+)',t); return float(m.group(1)) if m else None
    sn=re.search(r'Sample Number:\s*(\S+)',t); sn=sn.group(1) if sn else '?'
    m200=re.search(r'#200\s*\n?([\d.]+)',t)
    d=dict(D10=g('D10'),D30=g('D30'),D50=g('D50'),D60=g('D60'),Cu=g('Cu'),Cc=g('Cc'))
    sub=df[(df.pagina.astype(str).str.endswith(';'+str(p)))&(df.tipo_ensayo.str.startswith('CID'))]
    r=sub.iloc[0] if len(sub) else None
    print(p,sn,d,'| CSV',None if r is None else (r.D10_mm,r.D30_mm,r.D50_mm,r.D60_mm,r.Cu,r.Cc,r.grava_pct,r.arena_pct,r.finos_pct))
