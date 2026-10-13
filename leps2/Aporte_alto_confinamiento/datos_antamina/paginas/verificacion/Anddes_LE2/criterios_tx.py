import json, pathlib
out=pathlib.Path(__file__).parent
R=json.load(open(out/"tx_verif.json"))
Gs={"M":3.06,"H":2.94,"I":2.75,"P1":2.90,"P2":2.74}
crit=[]
for key,d in R.items():
    s3c=d["cell"][0]-d["bp"][0]
    rows=d["rows"]
    chk=0
    for e,dv,u,p,q,pp,qq,r1,r2 in rows:
        s3=s3c-u; s1=s3+dv
        if abs(p-(s3c+dv/2))>0.15 or abs(q-dv/2)>0.15 or abs(pp-(p-u))>0.15 or abs(qq-q)>0.15: chk+=1
        if s3>0 and abs(r2-s1/s3)>0.011: chk+=1
    def st(r):
        e,dv,u=r[0],r[1],r[2]; s3=s3c-u; s1=s3+dv
        return dict(eps=e,q=dv,u=u,s3f=round(s3,1),s1f=round(s1,1),ratio=round(s1/s3,3),pp=r[5],qq=r[6])
    imax=max(range(len(rows)),key=lambda i:rows[i][1])
    iobl=max(range(len(rows)),key=lambda i:(s3c-rows[i][2]+rows[i][1])/(s3c-rows[i][2]))
    i15=len(rows)-1
    H0,Hf=d["H"];D0,Df=d["D"];r0,rf=d["rho"];w0,wf=d["w"]
    rf_calc=r0*H0*D0**2/(Hf*Df**2)
    gs_imp=1/(1/rf-wf/100)
    g=Gs[d["set"]]
    e0=g/r0-1; ec=g/rf-1
    Sr0=w0/100*g/e0; Srf=wf/100*g/ec
    Sr0_270=w0/100*2.70/(2.70/r0-1)
    crit.append(dict(key=key,set=d["set"],s3c=s3c,checks_fail=chk,nrows=len(rows),
        qmax=st(rows[imax]),obl=st(rows[iobl]),e15=st(rows[i15]),
        rho_f_rep=rf,rho_f_calc=round(rf_calc,3),Gs_imp_Sr1=round(gs_imp,2),e0=round(e0,3),e_c=round(ec,3),Sr0=round(Sr0,2),Sr_f=round(Srf,2),Sr0_Gs270=round(Sr0_270,2),
        dV_cons_pct=round((1-Hf*Df**2/(H0*D0**2))*100,1), dH_pct=round((1-Hf/H0)*100,2), dD_pct=round((1-Df/D0)*100,2), B=d["B"][0], w=d["w"]))
for c in crit:
    print(c["key"],c["s3c"],"fail",c["checks_fail"],"| qmax",c["qmax"],"| obl",c["obl"],"| 15",c["e15"])
for c in crit:
    print(c["key"],"rho_f rep/calc",c["rho_f_rep"],c["rho_f_calc"],"Gs_imp",c["Gs_imp_Sr1"],"e0",c["e0"],"ec",c["e_c"],"Sr0",c["Sr0"],"Srf",c["Sr_f"],"dV%",c["dV_cons_pct"],"dH",c["dH_pct"],"dD",c["dD_pct"],"w",c["w"])
json.dump(crit,open(out/"tx_criterios.json","w"),indent=1)
