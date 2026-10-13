import pandas as pd, pathlib, json
here=pathlib.Path(__file__).parent
ext=here.parents[2]/"extraido"
df=pd.read_csv(ext/"parametros_RMU.csv")
S=json.load(open(here/"le2_stats.json"))
mp={"UCS":"UCS","Is50 axial":"PLTA","Is50 diametral":"PLTD","tracción brasileña":"Brazilian"}
ms={"media":"media","P50":"P50","P35":"P35","P16":"P16","P84":"P84","desv. estándar":"sd","mínimo":"min","máximo":"max"}
bad=0; tot=0
for i,r in df.iterrows():
    if r.parametro in mp and r.rmu in S[mp[r.parametro]]["stats"]:
        s=S[mp[r.parametro]]["stats"][r.rmu]; mine=s[ms[r.estadistico]]
        tot+=1
        rel=abs(r.valor_recalculado-mine)/max(abs(mine),1e-9)
        if rel>2e-3 or int(r.n)!=s["n"]:
            bad+=1; print("DIF",r.rmu,r.parametro,r.estadistico,"csv_recalc",r.valor_recalculado,"csv_inf",r.valor_informe,"mine",round(mine,4),"n",r.n,s["n"])
        if r.estadistico in ("media","P50","P35") and abs(float(r.valor_informe)-mine)/max(abs(mine),1e-9)>2e-3:
            print("INFORME≠recalc",r.rmu,r.parametro,r.estadistico,r.valor_informe,round(mine,4), "| nota:",str(r.notas)[:150])
print("filas comparadas",tot,"dif",bad)
print(df[df.rmu=="XDP"][df.parametro=="UCS"][["estadistico","valor_informe","valor_recalculado","n","notas"]].to_string())
print(df.drop_duplicates("rmu")[["rmu","litologia","litologia_detalle","correspondencia_rmu_litologias"]].to_string())
