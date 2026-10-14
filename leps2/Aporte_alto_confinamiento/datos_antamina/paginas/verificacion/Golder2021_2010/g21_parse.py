import fitz, sys, re, json
doc=fitz.open(sys.argv[1])
pages=[108,109,110,115,116,117,122,123,124,129,130,131,136,137,138,143,144,145,150,151,152,157,158,159,164,165,166,171,172,173]
out={}
num=r'-?\d+\.\d+|-?\d+'
for p in pages:
    t=doc[p-1].get_text()
    g=lambda pat: (re.search(pat,t,re.S).group(1) if re.search(pat,t,re.S) else None)
    h={}
    h['informe']=g(r'Nº Informe\s*:\s*(\S+)')
    h['B']=g(r'Parámetro B:\s*\n?\s*([\d.]+)')
    h['celda']=g(r'Presión de Celda:\s*\n?\s*([\d.]+)')
    h['contra']=g(r'Contrapresión:\s*\n?\s*([\d.]+)')
    h['s3c']=g(r'Inicial \(s3\):\s*([\d.]+)')
    h['obs']=g(r'Observaciones:\s*(.*?)\n')
    ini=re.search(r'INICIAL\s*\n'+r'\s*\n'.join([r'\s*('+num+')']*7),t)
    h['ini']=ini.groups() if ini else None
    fins=re.findall(r'FINAL\s*\n'+r'\s*\n'.join([r'\s*('+num+')']*7),t)
    h['final_consol']=fins[0] if fins else None
    h['final_corte']=fins[1] if len(fins)>1 else None
    h['rate']=g(r'Deformación \(%/min\):\s*\n?\s*([\d.]+)')
    h['eps_f']=g(r'Axial en la Falla \(%\):\s*\n?\s*([\d.]+)')
    cf=re.search(r'Criterios de Falla:\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)\s*\n\s*([\d.]+)',t)
    h['crit_s1_s1p_s3']=cf.groups() if cf else None
    gs=re.search(r'G\. Específica\s*\n\s*([\d.]+)',t); h['Gs']=gs.group(1) if gs else None
    # tabla
    a=t.find('(kPa)\n',t.find('q/p'))
    seg=t[t.find('(%) \n(kPa) \n(%) \n(kPa) \n(kPa) \n(kPa) \n(kPa)'):]
    seg=seg[:seg.find('LAB-PER')]
    vals=[float(x) for x in re.findall(num,seg.split('(kPa)',7)[-1])]
    rows=[vals[i:i+8] for i in range(0,len(vals)-7,8)]
    bad=[r for r in rows if abs(r[4]-r[3]-r[1])>0.06]
    h['nrows']=len(rows); h['bad']=bad[:3]
    out[p]={'h':h,'rows':rows}
    print(p,h['informe'],h['s3c'],h['Gs'],h['B'],h['ini'],h['rate'],h['eps_f'],h['crit_s1_s1p_s3'],'n',len(rows),'bad',len(bad))
json.dump(out,open(sys.argv[2],'w'),ensure_ascii=False)
