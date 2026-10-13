import pymupdf, re
pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2021_Golder_Ensayos de Laboratorio Commingling.pdf"
doc = pymupdf.open(pdf)
for pg in range(42,56):
    t = doc[pg-1].get_text()
    src = re.search(r"Source of Sample:\s*([^\n]+)", t); sn = re.search(r"Sample Number:\s*([^\n]+)", t)
    m = re.search(r"NP\s*\nNP\s*\nNP\s*\n((?:[\d.]+\s*\n){5,9})(G[A-Z\-]+|S[A-Z\-]+)", t)
    vals = m.group(1).split() if m else None
    print(pg, src.group(1).strip() if src else None, sn.group(1).strip() if sn else None, vals, m.group(2) if m else None)
