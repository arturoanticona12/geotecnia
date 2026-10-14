import pymupdf, re
pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2021_Golder_Ensayos de Laboratorio Commingling.pdf"
doc = pymupdf.open(pdf)
for pg in range(42,56):
    t = doc[pg-1].get_text()
    L=[l.strip() for l in t.split("\n") if l.strip()]
    # sieve labels then values
    i = L.index("#200") if "#200" in L else None
    # find first numeric run of 100.0 after sieves
    j = next(k for k in range(len(L)) if L[k]=="100.0")
    vals=[]
    k=j
    while re.fullmatch(r"\d+\.\d", L[k]): vals.append(float(L[k])); k+=1
    # percents block after 'Clay'
    c = max(k for k in range(len(L)) if L[k]=="Clay")
    parts = L[c+1:c+9]
    print(pg, "pasa:", vals[:14], "parts(+3,Gc,Gf,Sc,Sm,Sf,silt,clay):", parts)
