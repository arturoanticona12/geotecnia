# Valores transcritos de las imagenes (crop_LSDS_*_p1/p2.png y LSDS_M_p1/p2.png)
import pandas as pd, pathlib, math
ext=pathlib.Path(__file__).parents[3]/"extraido"
V={ # set: (sn list, tau pico, sec pico, tau66, sec66, c_p, phi_p, mu_p, c66, phi66, mu66, Hf(cm) list, wi, wf list, rhoi, rhof list)
"M":([300,600,1200],[219.5,469.5,984.3],[36,38,39],[208.0,469.2,973.5],[35,38,39],0.0,39.0,0.68,0.0,38.7,0.67,[16.7,16.2,15.8],6.80,[9.90,9.60,9.00],2.183,[2.322,2.396,2.456]),
"H":([300,600,1200],[255.7,476.1,998.1],[40,38,40],[250.8,473.9,998.1],[40,38,40],0.0,39.5,0.69,0.0,39.5,0.69,[16.8,16.3,15.9],7.70,[10.60,9.70,8.90],2.100,[2.227,2.293,2.350]),
"I":([300,600,1200],[228.1,468.1,945.1],[37,38,38],[218.3,451.8,885.6],[36,37,36],0.0,38.1,0.67,0.0,36.5,0.64,[17.0,16.9,16.3],9.80,[11.90,11.40,11.00],1.921,[2.006,2.026,2.091]),
"P1":([300,600,1000],[356.3,625.3,947.3],[50,46,43],[340.0,625.3,931.2],[49,46,43],109.6,40.1,0.70,100.0,40.0,0.70,[17.0,16.6,16.3],7.40,[8.50,8.00,7.40],2.094,[2.191,2.248,2.290]),
"P2":([300,600,1200],[353.9,633.7,1019.2],[50,47,40],[349.1,631.7,991.5],[49,46,40],161.1,36.0,0.63,169.2,34.9,0.61,[17.1,16.8,16.3],11.10,[11.70,11.40,10.90],1.831,[1.907,1.941,1.995]),
}
Gs={"M":3.06,"H":2.94,"I":2.75,"P1":2.90,"P2":2.74}
df=pd.read_csv(ext/"ensayos_corte_directo.csv")
m={"Marmol":"M","HORNFELS":"H","Intrusivo":"I","Pila 01":"P1","Pila 02":"P2"}
cnt={}
for idx,r in df.iterrows():
    k=[v for kk,v in m.items() if r.fuente.startswith(kk)][0]
    i=cnt.get(k,0); cnt[k]=i+1
    sn,tp,sp,t6,s6,cp,pp,mp,c6,p6,m6,Hf,wi,wf,ri,rf=V[k]
    mine=dict(sigma_n_kPa=sn[i],tau_kPa=tp[i],phi_sec_deg=sp[i],tau_66mm_kPa=t6[i],phi_sec_66mm_deg=s6[i],c_pico_serie_kPa=cp,phi_pico_serie_deg=pp,coef_friccion_pico=mp,
      c_66mm_serie_kPa=c6,phi_66mm_serie_deg=p6,coef_friccion_66mm=m6,altura_final_mm=Hf[i]*10,w_pct=wi,w_final_pct=wf[i],rho_d_gcm3=ri,rho_d_final_gcm3=rf[i],Gs=Gs[k],gamma_d_kNm3=round(ri*9.81,2),e0=round(Gs[k]/ri-1,3))
    d=[(c,r[c],v) for c,v in mine.items() if pd.isna(r[c]) or abs(float(r[c])-v)>0.006]
    ef=Gs[k]/rf[i]-1; Sr=wf[i]/100*Gs[k]/ef
    print(k,sn[i],"OK" if not d else d,"| Sr_final(Gs rot.)=%.2f"%Sr, "| atan check pico %.1f 6.6 %.1f"%(math.degrees(math.atan(tp[i]/sn[i])),math.degrees(math.atan(t6[i]/sn[i]))))
print(df[["fuente","Dmax_mm","saturado","caja_mm","criterio_falla","tau_residual_kPa","pagina"]].drop_duplicates("fuente").to_string())
print(df.notas.iloc[9])
