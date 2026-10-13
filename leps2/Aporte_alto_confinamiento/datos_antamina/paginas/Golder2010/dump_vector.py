import re, sys
from pathlib import Path
txt = Path(sys.argv[1]).read_text(encoding="utf-8")
parts = re.split(r"=== PÁGINA (\d+) ===", txt)
pg = {int(parts[i]): parts[i + 1] for i in range(1, len(parts), 2)}
num = re.compile(r"^-?\d+,\d+$")
for p in [167,168,169,173,174,175]:
    vals=[float(l.strip().replace(",",".")) for l in pg[p].splitlines() if num.match(l.strip())]
    k=next(j for j in range(len(vals)-2) if vals[j]==0 and vals[j+1]==0 and vals[j+2]==0)
    rows=[vals[j:j+9] for j in range(k,len(vals)-8,9)]
    seen=set(); print("p",p)
    for r in rows:
        if r[0] in seen: continue
        seen.add(r[0]); print("  eps=%5.2f dev=%7.2f u=%7.2f s3'=%7.2f s1'=%7.2f p'=%7.2f t=%7.2f" % tuple(r[:7]))
