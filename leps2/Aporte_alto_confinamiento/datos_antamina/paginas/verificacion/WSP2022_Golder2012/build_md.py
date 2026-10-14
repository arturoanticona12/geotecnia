import pandas as pd, os
V=os.path.dirname(os.path.abspath(__file__))
OUT=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Aporte_alto_confinamiento\datos_antamina\verificado\verificacion_WSP2022_Golder2012.md"
body=open(os.path.join(V,'verif_cuerpo.md'),encoding='utf-8').read()
d=pd.read_csv(os.path.join(V,'discrepancias_filas.csv'),dtype=str).fillna('')
esc=lambda s: s.replace('|','\\|').replace('\n',' ')
lines=['','| Archivo | Fila CSV | ensayo_id | Columna | Valor anterior | Valor correcto | Página | Razón |','|---|---|---|---|---|---|---|---|']
for _,r in d.iterrows():
    lines.append('| '+' | '.join(esc(str(r[c])) for c in ['archivo','fila_csv','ensayo_id','columna','valor_anterior','valor_correcto','pagina','razon'])+' |')
open(OUT,'w',encoding='utf-8').write(body+'\n'.join(lines)+'\n')
print(len(d),'filas en anexo')
