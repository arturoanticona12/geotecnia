import sys; sys.path.insert(0, sys.argv[1]); sys.stdout.reconfigure(encoding="utf-8")
from common import load_db
df = load_db()
g = df.groupby("Set").Reference.nunique()
print("sets totales:", df.Set.nunique(), "| ids repetidos entre publicaciones:", (g > 1).sum())
print(g[g > 1].head(20).to_string())
print("pares (Reference, Set):", df.groupby(["Reference", "Set"]).ngroups)
