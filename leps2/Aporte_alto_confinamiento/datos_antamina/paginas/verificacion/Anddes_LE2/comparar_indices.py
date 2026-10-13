import pandas as pd, pathlib, math
ext=pathlib.Path(__file__).parents[3]/"extraido"
sv=[75,50,37.5,25,19,9.5,4.75,2.0,0.85,0.425,0.25,0.15,0.106,0.075]
# transcrito de imagenes SUCS p1 (SUCS_M_p1.png, crop_SUCS_*_p1*.png)
G={"M":[100,85,75,63,56,44,35,27,22,18,15,13,12,10],
   "H":[100,91,83,68,59,43,32,26,21,18,16,14,13,11],
   "I":[100,90,84,73,65,49,37,24,18,15,13,11,9,8],
   "P1":[100,93,87,78,70,53,41,32,26,22,19,16,13,11],
   "P2":[100,93,89,81,73,55,43,32,26,22,18,15,12,9]}
REP={"M":dict(bol=None,gr=65,ar=25,fi=10,D10=1.54,D30=2.76,D60=22.04,Cu=14.29,Cc=0.22,LL="NP",SUCS="GP-GM",gdmax=23.780,wopt=6.8,gdc=25.754,wc=3.9,gsb=2.94,wb=0.1,gs=3.06,wn=3,wcalc=710/24174*100,met="Fuera de método"),
     "H":dict(bol=None,gr=68,ar=21,fi=11,D10=1.54,D30=3.55,D60=19.45,Cu=12.61,Cc=0.42,LL=16,SUCS="GP-GM",gdmax=22.876,wopt=7.7,gdc=24.533,wc=4.7,gsb=2.80,wb=0.3,gs=2.94,wn=3,wcalc=757/23114*100,met="Fuera de método"),
     "I":dict(bol=None,gr=63,ar=29,fi=8,D10=0.13,D30=3.03,D60=15.35,Cu=121.26,Cc=4.74,LL=17,SUCS="GP-GM",gdmax=20.930,wopt=9.8,gdc=22.230,wc=6.7,gsb=2.56,wb=1.0,gs=2.75,wn=5,wcalc=1211/23683*100,met="Fuera de método"),
     "P1":dict(bol=0,gr=59,ar=30,fi=11,D10=1.54,D30=1.47,D60=12.51,Cu=8.11,Cc=0.11,LL="NP",SUCS="GP-GM",gdmax=22.819,wopt=7.4,gdc=24.012,wc=5.4,gsb=2.79,wb=0.8,gs=2.90,wn=3,wcalc=216/7696*100,met="Método C"),
     "P2":dict(bol=1,gr=57,ar=34,fi=9,D10=0.08,D30=1.45,D60=11.49,Cu=138.86,Cc=2.21,LL="NP",SUCS="GW-GM",gdmax=19.951,wopt=11.1,gdc=20.797,wc=8.6,gsb=2.39,wb=2.0,gs=2.74,wn=6,wcalc=542/9822*100,met="Método C")}
# Proctor points (w, gd) from table
PT={"M":[(3.6,23.1),(5.8,23.7),(7.7,23.7),(9.5,23.1)],"H":[(4.4,21.9),(6.1,22.6),(8.1,22.9),(10.1,21.9)],"I":[(5.0,19.2),(7.3,19.9),(9.0,20.8),(11.1,20.3)],
    "P1":[(3.4,21.9),(5.0,22.3),(7.1,22.8),(9.0,22.4)],"P2":[(7.1,19.4),(9.3,19.7),(11.0,20.0),(13.0,19.5)]}
def Dx(p,x):
    for i in range(len(sv)-1):
        if p[i]>=x>=p[i+1]:
            if p[i]==p[i+1]: return sv[i+1]
            return math.exp(math.log(sv[i+1])+(x-p[i+1])/(p[i]-p[i+1])*(math.log(sv[i])-math.log(sv[i+1])))
    return None
df=pd.read_csv(ext/"ensayos_indices.csv")
m={"Marmol":"M","HORNFELS":"H","Intrusivo":"I","Pila 01":"P1","Pila 02":"P2"}
for _,r in df.iterrows():
    k=[v for kk,v in m.items() if r.fuente.startswith(kk)][0]; R=REP[k]; p=G[k]
    gstr="; ".join(f"{s:g} mm:{q}" for s,q in zip(sv,p))
    d10,d30,d50,d60=[Dx(p,x) for x in (10,30,50,60)]
    print(f"--- {k}: gran OK={gstr.replace(' ','')==str(r.granulometria_pct_pasa).replace(' ','')}", f"sum={R['gr']+R['ar']+R['fi']}")
    print("   interp D10=%s D30=%.2f D50=%.2f D60=%.2f"%(None if d10 is None else round(d10,3),d30,d50,d60), "| CSV interp",r.D10_interp_mm,r.D30_interp_mm,r.D50_mm,r.D60_interp_mm)
    if d10: print("   Cu=%.1f Cc=%.2f"%(d60/d10,d30**2/(d10*d60)), "| CSV",r.Cu_interp,r.Cc_interp)
    # reported Cu Cc consistency
    print("   Cu_rep calc from rep D: %.2f Cc %.3f"%(R['D60']/R['D10'],R['D30']**2/(R['D10']*R['D60'])))
    # oversize fraction from correction (ASTM D4718)
    gw=9.81
    Pc=(1/R['gdmax']-1/R['gdc'])/(1/R['gdmax']-1/(R['gsb']*gw))
    wcc=(1-Pc)*R['wopt']+Pc*R['wb']
    print("   Pc sobretamaño=%.1f%% (ret. 3/4in=%d%%) w_corr calc=%.2f rep=%s"%(Pc*100,100-p[4],wcc,R['wc']))
    # Gs min for Sr<=1
    gsmin=max(g/(gw-w/100*g) for w,g in PT[k])
    print("   Gs_min(Sr<=1) Proctor=%.3f ; Gs rotulado %.2f ; Sr punto opt con Gs rot=%.2f"%(gsmin,R['gs'], R['wopt']/100*R['gs']/(R['gs']*gw/R['gdmax']-1)))
    cmp={"D10_mm":R['D10'],"D30_mm":R['D30'],"D60_mm":R['D60'],"Cu":R['Cu'],"Cc":R['Cc'],"grava_pct":R['gr'],"arena_pct":R['ar'],"finos_pct":R['fi'],"gamma_d_max_kNm3":R['gdmax'],"w_opt_pct":R['wopt'],
         "gamma_d_max_corr_kNm3":R['gdc'],"w_opt_corr_pct":R['wc'],"Gs_bulk_sobretamano":R['gsb'],"w_sobretamano_pct":R['wb'],"Gs":R['gs'],"w_natural_pct":R['wn'],"w_natural_calc_pct":round(R['wcalc'],2)}
    bad=[(c,r[c],v) for c,v in cmp.items() if pd.isna(r[c]) or abs(float(r[c])-v)>0.006]
    print("   diffs:",bad, "| LL",r.LL,"SUCS",r.SUCS,"bol",r.bolones_pct, "rho",r.rho_d_max_gcm3, "met",r.proctor_metodo)
