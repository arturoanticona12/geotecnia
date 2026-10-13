import json, pathlib, pandas as pd
out=pathlib.Path(__file__).parent
ext=out.parents[2]/"extraido"
df=pd.read_csv(ext/"ensayos_triaxial_CU.csv")
C={c["key"]:c for c in json.load(open(out/"tx_criterios.json"))}
R=json.load(open(out/"tx_verif.json"))
m={"Marmol":"M","HORNFELS":"H","Intrusivo":"I","Pila 01":"P1","Pila 02":"P2"}
cols=["diametro_mm","altura_mm","rho_d_gcm3","w_pct","B","contrapresion_kPa","presion_celda_kPa","altura_consol_mm","diametro_consol_mm","rho_d_consol_gcm3","w_final_pct","sigma3_kPa","sigma1_kPa","q_kPa","eps_axial_falla_pct","u_falla_kPa","p_falla_kPa","q_falla_und_kPa","ratio_s1s3_falla","Su_kPa","q_dev_max_kPa","eps_q_dev_max_pct","u_q_dev_max_kPa","p_q_dev_max_kPa","ratio_s1s3_max","eps_ratio_max_pct","Gs","e0","gamma_d_kNm3","pagina"]
for _,r in df.iterrows():
    k=[v for kk,v in m.items() if r.fuente.startswith(kk)][0]
    s=r.ensayo_id.split(" kPa")[0]
    key=f"{k}_{s} kPa"; c=C[key]; d=R[key]
    mine=dict(diametro_mm=d["D"][0]*10,altura_mm=d["H"][0]*10,rho_d_gcm3=d["rho"][0],w_pct=d["w"][0],B=d["B"][0],contrapresion_kPa=d["bp"][0],presion_celda_kPa=d["cell"][0],
      altura_consol_mm=d["H"][1]*10,diametro_consol_mm=d["D"][1]*10,rho_d_consol_gcm3=d["rho"][1],w_final_pct=d["w"][1],sigma3_kPa=c["s3c"],
      sigma1_kPa=c["e15"]["s1f"],q_kPa=c["e15"]["q"],eps_axial_falla_pct=15.0,u_falla_kPa=c["e15"]["u"],p_falla_kPa=c["e15"]["pp"],q_falla_und_kPa=c["e15"]["qq"],
      ratio_s1s3_falla=round(c["e15"]["ratio"],2),Su_kPa=round(c["e15"]["qq"]),q_dev_max_kPa=c["qmax"]["q"],eps_q_dev_max_pct=c["qmax"]["eps"],u_q_dev_max_kPa=c["qmax"]["u"],p_q_dev_max_kPa=c["qmax"]["pp"],
      ratio_s1s3_max=round(c["obl"]["ratio"],2),eps_ratio_max_pct=c["obl"]["eps"],pagina=d["page"])
    diffs=[]
    for col,val in mine.items():
        old=r[col]
        if col=="pagina":
            if str(old).split(";")[0]!=str(val): diffs.append((col,old,val))
            continue
        if pd.isna(old) or abs(float(old)-float(val))>0.006: diffs.append((col,old,val))
    print(key, "OK" if not diffs else diffs, "| Gs",r.Gs,"e0",r.e0,"gd",r.gamma_d_kNm3, "| sigma1 old col meaning check")

