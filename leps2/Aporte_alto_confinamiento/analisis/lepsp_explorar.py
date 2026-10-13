"""Leps-P, paso 1: comparación de especificaciones (todas con REML de 3 niveles y heterocedasticidad)."""
import sys, json, warnings, time
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo, S0  # noqa: E402

d = preparar(load_db(), CLASE)
CL = ["good", "moderate", "low"]
dum = np.c_[[(d.clase == c).values.astype(float) for c in CL]].T
lnD = np.log(d.Dmax.fillna(d.Dmax.median()) / 100.0).values       # escala respecto de dmax 100 mm
lnU = np.log(d.UCS.fillna(d.UCS.median()) / 100.0).values
e, x = d.e.values, d.x.values
print(f"datos: {len(d)} ensayos, {d.Set.nunique()} sets, {d.pub.nunique()} publicaciones; Dmax faltante {d.Dmax.isna().sum()}, UCS faltante {d.UCS.isna().sum()}")

ESP = {
    "M0 Leps-P base (clase, e, x)": (np.c_[dum, e, x], CL + ["e", "x"]),
    "M1 + e·x (densidad sobre curvatura)": (np.c_[dum, e, x, e * x], CL + ["e", "x", "e·x"]),
    "M2 + x² (curvatura local que cambia)": (np.c_[dum, e, x, x ** 2], CL + ["e", "x", "x²"]),
    "M3 + ln(Dmax/100)": (np.c_[dum, e, x, lnD], CL + ["e", "x", "lnD"]),
    "M4 + ln(Dmax/100)·x": (np.c_[dum, e, x, lnD, lnD * x], CL + ["e", "x", "lnD", "lnD·x"]),
    "M5 UCS en vez de clase": (np.c_[np.ones(len(d)), lnU, e, x], ["c", "lnUCS", "e", "x"]),
    "M6 completo (clase, e, x, e·x, x², lnD)": (np.c_[dum, e, x, e * x, x ** 2, lnD], CL + ["e", "x", "e·x", "x²", "lnD"]),
}
R = {}
for nm, (X, nom) in ESP.items():
    t = time.time(); m = Modelo(d, X, nom).ajustar(); r = m.resumen()
    R[nm] = r; b, se = r["beta"], r["se"]
    print(f"\n{nm}   ll_REML = {r['ll']:.2f}   ({time.time()-t:.0f} s)")
    print("  β: " + ", ".join(f"{k} {b[k]:+.4f} ({se[k]:.4f})" for k in nom))
    print(f"  publicación: sdθ {r['pub'][0]:.4f} sdm {r['pub'][1]:.4f} ρ {r['pub'][2]:+.2f} | set: sdθ {r['set'][0]:.4f} sdm {r['set'][1]:.4f} ρ {r['set'][2]:+.2f}"
          f" | σε(x): exp({r['a'][0]:.3f} {r['a'][1]:+.3f}x) → {np.exp(r['a'][0]-r['a'][1]*1.5):.4f} a x=-1.5, {np.exp(r['a'][0]):.4f} a x=0, {np.exp(r['a'][0]+r['a'][1]*2):.4f} a x=2")
# modelo homocedástico de 2 niveles (referencia del manuscrito anterior) para comparar σε
X0, n0 = ESP["M0 Leps-P base (clase, e, x)"]
mh = Modelo(d, X0, n0, het=False).ajustar(); print("\nM0 homocedástico:", {k: (round(v[0], 4), round(v[1], 4), round(v[2], 2)) if isinstance(v, tuple) and len(v) == 3 else v for k, v in mh.resumen().items() if k in ("pub", "set")}, "σε", round(float(np.exp(mh.a[0])), 4), "ll", round(mh.ll, 2))
json.dump({k: {kk: (vv if not isinstance(vv, dict) else {a: float(b) for a, b in vv.items()}) for kk, vv in v.items()} for k, v in R.items()},
          open(AQUI / "lepsp_explorar.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
