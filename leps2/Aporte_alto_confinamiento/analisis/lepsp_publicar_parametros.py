"""Incorpora los supuestos de escala (lepsp_escala2.json) a lepsp_parametros.json y lo copia a leps3/."""
import json, shutil
from pathlib import Path
AQUI = Path(__file__).parent
P = json.load(open(AQUI / "lepsp_parametros.json")); E = json.load(open(AQUI / "lepsp_escala2.json"))
sim = E["similares Cu≤1.5 Δe≤0.05"]; tod = E["todos"]
P["escala"] = {"general": dict(b=tod["b"], se_hk=tod["se_hk"], tau=tod["tau"], k=tod["n"]),
               "paralela": dict(b=sim["b"], se_hk=sim["se_hk"], tau=sim["tau"], k=sim["n"], kappa=sim["kappa"], kappa_ci_hk=sim["kappa_ci_hk"])}
json.dump(P, open(AQUI / "lepsp_parametros.json", "w"), indent=0)
shutil.copy(AQUI / "lepsp_parametros.json", AQUI.parent / "leps3" / "lepsp_parametros.json")
print("escala:", {k: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in v.items()} for k, v in P["escala"].items()})
