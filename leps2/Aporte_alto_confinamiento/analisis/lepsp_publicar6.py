"""Publica los parámetros de la ronda 6 en leps3/: forma «acotada» del modelo extendido (lepsp_mcmc6.py: datos
depurados, ln Dmax, ζ por clase, truncamiento, censura) y efecto de escala por programa de laboratorio
(lepsp_escala6.json): 'general' = media cero (diseño), 'datos' = media estimada, 'weibull' = β_D = −0.05 (sensibilidad)."""
import json, shutil
from pathlib import Path
AQ = Path(__file__).parent
P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8"))
E = json.load(open(AQ / "lepsp_escala6.json", encoding="utf-8"))
L = E["laboratorios R ≥ 2"]
P["escala"] = dict(E["libreria"], k_laboratorios=L["k"], prediccion95=L.get("prediccion95"), rango_razon_tamanos=E["rango_razon_tamanos"],
                   rango_Dmax_mm=E["rango_Dmax_mm"])
assert "lnD" in P["formas"]["acotada"]["nombres"], "lepsp_parametros.json no es de la ronda 6 (correr lepsp_mcmc6.py)"
json.dump(P, open(AQ / "lepsp_parametros.json", "w", encoding="utf-8"), indent=0)
shutil.copy(AQ / "lepsp_parametros.json", AQ.parent / "leps3" / "lepsp_parametros.json")
shutil.copy(AQ / "lepsp_parametros.json", AQ.parent / "hiber" / "hiber_parameters.json")   # biblioteca pública HiBER
print("formas:", list(P["formas"]), "| nombres acotada:", P["formas"]["acotada"]["nombres"], "| escala general:", P["escala"]["general"])
