import pandas as pd,sys
b=sys.argv[1]
o=pd.read_csv(b+'/extraido/Golder_2010_ROM.csv'); n=pd.read_csv(b+'/verificado/Golder_2010_ROM_verificado.csv')
print('| Fila | Set | σ′3c | sigma3_kPa ant. → σ′3f | sigma1_kPa (σ′1f) | q ant. → q = σ′1f−σ′3f | Δu ant. → nuevo | máx. desviador (εa %, q) | máx. oblicuidad (εa %, σ′1/σ′3) | Pág. |')
print('|---|---|---|---|---|---|---|---|---|---|')
for i in range(len(n)):
    md = f"{n.maxdev_eps_pct[i]}, {n.maxdev_q_kPa[i]}"
    mo = 'no informado' if str(n.maxobl_ratio[i])=='no informado' else f"{n.maxobl_eps_pct[i]}, {n.maxobl_ratio[i]}"
    print(f"| {i} | {n.set_id[i]} | {n.sigma3c_kPa[i]:g} | {o.sigma3_kPa[i]:g} → {n.sigma3_kPa[i]:g} | {n.sigma1_kPa[i]:g} | {o.q_kPa[i]:g} → {n.q_kPa[i]:g} | {o.u_falla_kPa[i]:g} → {n.u_falla_kPa[i]:g} | {md} | {mo} | {str(n.pagina[i]).split(';')[0]} |")
