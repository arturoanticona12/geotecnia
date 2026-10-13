"""Extrae del texto las hojas resumen de CU Golder (págs. 82-156) para luego verificar en imagen."""
import re, sys, json
from pathlib import Path

txt = Path(sys.argv[1]).read_text(encoding="utf-8")
parts = re.split(r"=== PÁGINA (\d+) ===", txt)
pg = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}

out = []
for p in range(82, 185):
    t = pg.get(p, "")
    if "DATOS CONSOLIDACI" in t and "DATOS DE CORTE" in t:
        d = {"pag": p}
        m = re.search(r"Sondaje\s*\n?:?\s*(IPCC - Fase [AB])", t) or re.search(r"(IPCC - Fase [AB])", t)
        d["fase"] = m.group(1) if m else None
        m = re.search(r"Remoldeado[^\n]*", t); d["obs"] = m.group(0) if m else None
        m = re.search(r"Se usó material[^\n]*", t); d["mat"] = m.group(0) if m else None
        d["s3"] = re.findall(r"Esfuerzo Efectivo Inicial \(σ3\)\s*\n?\s*(\d+) kPa", t)
        d["ini"] = re.findall(r"INICIAL\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)", t)
        d["fin"] = re.findall(r"FINAL\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)\n([\d.]+)", t)
        d["eps"] = re.findall(r"Deformación Axial en la Falla \(%\):\n([\d.]+)", t)
        d["fail"] = re.findall(r"Criterios de falla:\n(\d+)\n(\d+)\n(\d+)", t)
        d["s3p"] = re.findall(r"σ3'\n(\d+)", t)
        d["gs"] = re.findall(r"\n(\d\.\d{3})\n", t)
        for name in ["Marmol Negro", "Mármol Negro", "Hornfels", "Intrusivo", "Exoskarn"]:
            if name in t:
                d["mat_name"] = name
        out.append(d)
for d in out:
    print(json.dumps(d, ensure_ascii=False))
