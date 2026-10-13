import pymupdf, re
pdf = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2021_Golder_Ensayos de Laboratorio Commingling.pdf"
doc = pymupdf.open(pdf)
for pg in range(72, 96):
    t = doc[pg-1].get_text()
    mu = re.search(r"Muestra\s*\n([^\n]+)", t)
    idm = re.search(r"ID\. Muestra:\s*([^\n]+)", t)
    ab = re.search(r"Absorci.n\s*\n%\s*\n([\d.]+)\s*\n([\d.]+)\s*\n([\d.]+)", t)
    gsf = re.search(r"(?i)gravedad espec.fica[^\n]*\n?[^\n]*(D854|C127)", t)
    std = "C127" if "C127" in t else ("D854" if "D854" in t else "?")
    nums = re.findall(r"\n(\d\.\d{2,3})\s*\n", t)
    print(pg, std, mu.group(1).strip() if mu else None, idm.group(1).strip() if idm else None, "abs", ab.groups() if ab else None, "nums", nums[:12])
