import sys, openpyxl, pandas as pd, numpy as np
sys.stdout.reconfigure(encoding="utf-8")
f=sys.argv[1]
wbf = openpyxl.load_workbook(f, data_only=False)
# formulas of summary cols per RMU block
for sh, cols in []: # [('UCS','GHIJ'),('PLTA','GHIJ'),('PLTD','GHIJ'),('Brazilian','GHIJ'),('Corte','HIJKLMNO')]:
    ws=wbf[sh]
    for r in range(1, ws.max_row+1):
        v=ws[f'{cols[0]}{r}'].value
        if isinstance(v,str) and v.startswith('='):
            print(sh, r, [ws[f'{c}{r}'].value for c in cols])
spec = {'UCS':(0,'RMU','Resist. Comp Simple (MPa)','Año'),'PLTA':(0,'RMU','Is(50)','Año'),'PLTD':(0,'RMU','Is(50)','Año'),
        'Brazilian':(0,'Unidad Geotécnica','Resistencia a la  tracción  (MPa)','Año'),'Corte':(0,'Unidad Geotécnica','Angulo de Fricción (°)','Año'),
        'RMR_RQD_FF':(0,'UG','RMR',None)}
for sh,(h,u,v,y) in spec.items():
    df=pd.read_excel(f, sheet_name=sh)
    df=df[df[u].notna()]; df[v]=pd.to_numeric(df[v],errors="coerce")
    print("\n##",sh, len(df), df[u].value_counts().to_dict())
    if y: print(" years", df[y].min(), df[y].max(), df[y].value_counts().sort_index().to_dict())
    print(" non-numeric vals:", df[pd.to_numeric(df[v],errors='coerce').isna()][v].unique()[:10])
    g=df.groupby(u)[v]
    print(pd.DataFrame({'n':g.count(),'mean':g.mean(),'std':g.std(),'min':g.min(),'p16':g.quantile(.16),'p35':g.quantile(.35),'p50':g.median(),'p84':g.quantile(.84),'max':g.max()}).round(3).to_string())
    print(" dup rows:", df.duplicated(subset=[c for c in df.columns[:7]]).sum())
    if sh=='Corte':
        df['Cohesión en (Mpa)']=pd.to_numeric(df['Cohesión en (Mpa)'],errors='coerce'); g=df.groupby(u)['Cohesión en (Mpa)']
        print(pd.DataFrame({'n':g.count(),'mean':g.mean(),'p35':g.quantile(.35),'p50':g.median(),'max':g.max()}).round(3).to_string())
        d2=df.drop_duplicates(subset=[df.columns[3],df.columns[4],df.columns[5],df.columns[6]])
        print(" unique (UG,phi,c,year) combos:", len(d2), d2[u].value_counts().to_dict())
    if sh=='RMR_RQD_FF':
        for c in ['RQD Corregido','Nro_Total_Estructuras/ Por metro (FF)']:
            df[c]=pd.to_numeric(df[c],errors='coerce')
            g=df.groupby(u)[c]; print(c); print(pd.DataFrame({'n':g.count(),'mean':g.mean(),'p35':g.quantile(.35),'p50':g.median()}).round(2).to_string())
