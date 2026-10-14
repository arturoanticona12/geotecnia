import re, sys
from pathlib import Path
txt = Path(sys.argv[1]).read_text(encoding="utf-8")
parts = re.split(r"=== PÁGINA (\d+) ===", txt)
pg = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
for p in range(66, 74):
    t = pg[p]; fase = re.search(r"Fase ([AB])", t)
    rows = re.findall(r"\n([A-Za-zÁ-úñ ]+)\n-\n(\d\.\d\d)\n(\d\.\d\d)\n(\d\.\d\d)\n(\d\.\d\d)\n(\d+)\n(\d+\.\d)", t)
    print("UCS p", p, fase.group(1) if fase else "?", rows)
for p in range(74, 82):
    t = pg[p]; fase = re.search(r"Fase ([AB])", t)
    rows = re.findall(r"\n(M-\d|[A-Z]+-\d)\n-\n([LI]+)\n(\d+\.\d\d)\n(\d+\.\d\d)\n(\d\.\d\d)\n(\d+)\n(\d+)\n(\d+\.\d)\n(\d+\.\d)\n(\d+)", t)
    name = re.search(r"\n(Mármol|Marmol|Hornfels|Intrusivo|Exoskarn)[^\n]*", t)
    print("PL p", p, fase.group(1) if fase else "?", name.group(0).strip() if name else "?", rows)
for p in range(50, 66):
    t = pg[p]; m = re.search(r"Muestra\s*\n?:\s*([^\n]+)", t); fase = re.search(r"Fase ([AB])", t)
    print("p", p, m.group(1).strip() if m else "?", fase.group(1) if fase else "?")
