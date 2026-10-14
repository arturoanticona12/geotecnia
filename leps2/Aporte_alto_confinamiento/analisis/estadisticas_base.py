"""Estadísticas descriptivas de la base usadas en el manuscrito."""
import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from common import load_db
df = load_db()
print("ensayos", len(df), "| sets", df.Set.nunique(), "| publicaciones", df.Reference.nunique(), "| triaxiales", (df["Lab Test"] == "TRX").sum())
print("σ3 max %.2f MPa | σn max %.2f MPa" % (df.s3.max(), df.sn.max()))
for t in [2, 3, 4.48]:
    s = df[df.s3 >= t]; print(f"σ3 ≥ {t}: {len(s)} ensayos, {s.Set.nunique()} sets, {s.Reference.nunique()} publicaciones: {sorted(s.Reference.unique())}")
for t in [3, 5]:
    print(f"σn ≥ {t}: {(df.sn >= t).sum()} ensayos ({100*(df.sn >= t).mean():.1f} %)")
print("sets con ≥3 ensayos:", (df.groupby('Set').size() >= 3).sum())
b = df.dropna(subset=["Bg"])
for lo, hi in [(0.1, 0.3), (1, 2), (2, 4), (4, 8)]:
    g = b[(b.sn > lo) & (b.sn <= hi)].Bg; print(f"Bg mediana σn {lo}-{hi}: {g.median():.1f} % (n={len(g)})")
v = df.dropna(subset=["evol"])
for lo, hi in [(0, 0.1), (0.3, 1), (1, 3), (3, 5)]:
    g = v[(v.s3 > lo) & (v.s3 <= hi)].evol; print(f"evol σ3 {lo}-{hi}: media {g.mean():.1f} %, n={len(g)}, >0: {(g>0).sum()}")
print("n evol", len(v), "| n Bg", len(b))
