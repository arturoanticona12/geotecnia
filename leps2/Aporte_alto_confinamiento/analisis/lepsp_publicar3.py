"""Publica los parámetros de la ronda 3 en leps3/: formas (lepsp_mcmc3.py) y efecto de escala (lepsp_escala3.py).
Escala: el metaanálisis por publicación (R ≥ 2) no detecta un efecto sistemático (media positiva, IC con cero). Para
diseño se adopta media cero ('general') con la heterogeneidad entre materiales y el error de la media como incertidumbre;
'datos' conserva la media estimada como sensibilidad. Se elimina el supuesto 'paralela' (sin respaldo en la ronda 3)."""
import json, shutil
from pathlib import Path
AQ = Path(__file__).parent
P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8")); E = json.load(open(AQ / "lepsp_escala3.json", encoding="utf-8"))
pub = E["publicaciones R ≥ 2"]
P["escala"] = dict(general=dict(b=0.0, se_hk=pub["se_kh"][0], tau=pub["tau"], nota="media cero; incertidumbre = heterogeneidad ⊕ EE"),
                   datos=dict(b=pub["b"][0], se_hk=pub["se_kh"][0], tau=pub["tau"], nota="media estimada (sensibilidad)"),
                   k_publicaciones=pub["k"])
json.dump(P, open(AQ / "lepsp_parametros.json", "w", encoding="utf-8"), indent=0)
shutil.copy(AQ / "lepsp_parametros.json", AQ.parent / "leps3" / "lepsp_parametros.json")
print("formas:", list(P["formas"]), "| escala:", {k: v for k, v in P["escala"].items() if k != "k_publicaciones"})
