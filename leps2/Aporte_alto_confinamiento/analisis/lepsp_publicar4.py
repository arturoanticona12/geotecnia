"""Publica los parámetros de la ronda 4 en leps3/: forma «acotada» con efectos en (η, ζ) (lepsp_mcmc4.py) y efecto de
escala sin la varianza entre sets añadida (τ conservador, lepsp_escala3.json); 'general' = media cero (diseño),
'datos' = media estimada, 'tau_r3' = τ de la ronda 3 (sensibilidad)."""
import json, shutil
from pathlib import Path
AQ = Path(__file__).parent
P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8"))
E0 = json.load(open(AQ / "lepsp_escala3.json", encoding="utf-8"))["publicaciones R ≥ 2"]
E1 = json.load(open(AQ / "lepsp_escala3_f1.json", encoding="utf-8"))["publicaciones R ≥ 2"]
P["escala"] = dict(general=dict(b=0.0, se_hk=E0["se_kh"][0], tau=E0["tau"], tau_ci=E0.get("tau_ci"), nota="media cero; τ sin varianza entre sets (conservador)"),
                   datos=dict(b=E0["b"][0], se_hk=E0["se_kh"][0], tau=E0["tau"], nota="media estimada (sensibilidad)"),
                   tau_r3=dict(b=0.0, se_hk=E1["se_kh"][0], tau=E1["tau"], nota="τ con varianza entre sets (ronda 3; sensibilidad)"),
                   k_publicaciones=E0["k"])
json.dump(P, open(AQ / "lepsp_parametros.json", "w", encoding="utf-8"), indent=0)
shutil.copy(AQ / "lepsp_parametros.json", AQ.parent / "leps3" / "lepsp_parametros.json")
print("formas:", list(P["formas"]), "| efectos acotada:", P["formas"]["acotada"].get("efectos"), "| escala general:", P["escala"]["general"])
