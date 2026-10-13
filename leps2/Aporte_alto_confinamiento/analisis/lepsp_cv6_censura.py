"""Validación por laboratorio con los ensayos censurados incluidos de forma honesta: su resistencia real es ≥ y_obs, así
que un censurado cuenta «bajo P05» solo si y_obs < P05 y aun así es ambiguo. Se dan cotas inferior (ninguno de los
ambiguos bajo el cuantil) y superior (todos). Escribe lepsp_cv6_censura.json."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent
A = pd.read_csv(AQ / "lepsp_cv6_A.csv"); A["sn"] = 1.013 * np.exp(A.x); A = A.rename(columns={"mu0": "mu_leps2_ref", "sd0": "sd_leps2_ref"})
Z = {"P05": norm.ppf(0.95), "P10": norm.ppf(0.90)}; OUT = {}
for banda, sel in (("todo", A.sn > 0), ("sn>=2", A.sn >= 2), ("sn>=3", A.sn >= 3)):
    D = A[sel.values]; c = D.cens.values; y = D.y.values; o = dict(n=int(len(D)), censurados=int(c.sum()), n_lab=int(D.lab.nunique()))
    print(f"[{banda}] n={len(D)} (censurados {int(c.sum())}, {D.lab.nunique()} laboratorios)")
    for f in ("acotada", "cuadratica", "potencia", "leps2_jer", "leps2_ref"):
        mu, sd = D[f"mu_{f}"].values, D[f"sd_{f}"].values; r = {}
        for nm, zq in Z.items():
            q = mu - zq * sd; bu = (~c) & (y < q); amb = c & (y < q)
            r[nm] = [float(bu.sum() / len(D)), float((bu.sum() + amb.sum()) / len(D))]
        z = (y - mu) / sd; r["z_no_cens"] = float(z[~c].mean()); r["z_cens_cota"] = float(z[c].mean()) if c.any() else None
        o[f] = r
        print(f"  {f:11s} bajo P05 {100*r['P05'][0]:4.1f}–{100*r['P05'][1]:4.1f} % | bajo P10 {100*r['P10'][0]:4.1f}–{100*r['P10'][1]:4.1f} %"
              f" | z̄ no censurados {r['z_no_cens']:+.2f}" + (f", censurados (cota inferior) {r['z_cens_cota']:+.2f}" if c.any() else ""))
    OUT[banda] = o
json.dump(OUT, open(AQ / "lepsp_cv6_censura.json", "w", encoding="utf-8"), indent=1)
