import pymupdf, re
pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2021_Golder_Ensayos de Laboratorio Commingling.pdf"
doc = pymupdf.open(pdf)
for s in range(10):
    p0=108+7*s
    for pg in range(p0,p0+3):
        page=doc[pg-1]
        # find word 'Promedio' or 'Específica' and number below it
        ws=page.get_text("words")
        cand=[w for w in ws if re.fullmatch(r"[23]\.\d{2,3}",w[4]) and w[0]>450 and 180<w[1]<330]
        print(pg, [(w[4],round(w[0]),round(w[1])) for w in cand][:6])
    # summary page c, phi
    for pg in range(p0+3,p0+7):
        t=doc[pg-1].get_text()
        if "COHESI" in t:
            print("  resumen", pg, re.findall(r"EFECTIVO\s*\n(\S+)\s*\n(\S+)", t), re.findall(r"\n(\d+)\nPARAMETROS", t), re.findall(r"Sondaje\s*\n?:?\s*([^\n]+)",t)[:1], re.findall(r"(\d+% Relave[^\n]*)",t)[:1])
