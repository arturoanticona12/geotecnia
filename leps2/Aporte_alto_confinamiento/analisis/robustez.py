"""Robustez de la caída de φ'1 a alta presión: efectos mixtos, ventana de referencia, rango de aplicación,
exclusión por publicación y validación cruzada por set (leave-one-set-out)."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from common import load_db, within_set, tau_leps, fit_set, PA  # noqa: E402

df = load_db()


def slope_A(w):
    h = w[w.sn >= 10 * PA].copy(); h["L"] = np.log10(h.sn / (10 * PA))
    a = np.linalg.lstsq(h[["L"]].values, h.dphi1.values, rcond=None)[0][0]
    return a, len(h), h.Set.nunique()


def report(tag, w):
    a, n, ns = slope_A(w)
    print(f"{tag:58s} a = {a:6.2f} °/déc  (n = {n}, sets = {ns})")


print("== 1. Ventana de referencia")
for lo, hi in [(0.2, 1.0), (0.3, 1.5), (0.5, 2.0), (0.3, 1.0)]:
    report(f"ref {lo}–{hi} MPa", within_set(df, lo, hi))

print("\n== 2. Rango de aplicación de Cylwik et al. (2025) y guía 60-600")
app = df[(df.D50 > 2) & (df.fines.fillna(0) < 25)]
report("D50 > 2 mm y finos < 25 %", within_set(app))
g606 = df[df.s3 >= 0.06]
report("σ3 ≥ 60 kPa", within_set(g606))
both = app[app.s3 >= 0.06]
report("ambos", within_set(both))

print("\n== 3. Efectos mixtos (intercepto y pendiente aleatorios por set), σn ≥ 1 MPa")
w = within_set(df)
h = w[w.sn >= 10 * PA].copy(); h["L"] = np.log10(h.sn / (10 * PA))
h["phi1t"] = h.dphi1 + h.phi1_ref
m1 = smf.mixedlm("phi1t ~ L", h, groups=h["Set"], re_formula="~L").fit(method="lbfgs")
print(m1.summary().tables[1])
# directamente sobre φ'1-test, sin la referencia de baja presión (todas las presiones ≥ 0.1 MPa, quiebre en 1 MPa)
d = df[df.sn >= 0.1].copy(); d["Lp"] = np.maximum(np.log10(d.sn / (10 * PA)), 0); d["Lm"] = np.minimum(np.log10(d.sn / (10 * PA)), 0)
cnt = d.groupby("Set").sn.transform("size"); d = d[cnt >= 3]
m2 = smf.mixedlm("phi1_test ~ Lm + Lp", d, groups=d["Set"]).fit(method="lbfgs")
print("\nModelo por tramos sin referencia (φ'1-test ~ Lm + Lp, intercepto aleatorio por set):")
print(m2.summary().tables[1])

print("\n== 4. Exclusión de una publicación a la vez (fuentes con datos σn ≥ 3 MPa)")
refs = w[w.sn >= 3].ref.value_counts()
print(refs.to_string())
for r in refs.index:
    a, n, ns = slope_A(w[w.ref != r])
    print(f"  sin {r:30s} a = {a:6.2f}  (n = {n}, sets = {ns})")

print("\n== 5. Validación cruzada por set: entrenar σn ≤ 1.5 MPa, predecir σn ≥ 2 MPa")
rows = []
sets = [s for s, g in df.groupby("Set") if (g.sn <= 1.5).sum() >= 2 and (g.sn >= 2).sum() >= 1]
for s in sets:
    a_s, _, _ = slope_A(w[w.Set != s])          # pendiente sin el set evaluado
    g = df[df.Set == s]; tr = g[g.sn <= 1.5]; te = g[g.sn >= 2]
    phi1 = fit_set(tr.sn.values, tr.tau.values, m=0.9)[0]
    for _, r in te.iterrows():
        t09 = tau_leps(r.sn, phi1, 0.9)
        ph = phi1 - a_s * max(np.log10(r.sn / (10 * PA)), 0) if a_s < 0 else phi1 + a_s * max(np.log10(r.sn / (10 * PA)), 0)
        ph = phi1 + a_s * max(np.log10(r.sn / (10 * PA)), 0)
        tc = tau_leps(r.sn, ph, 0.9)
        rows.append(dict(Set=s, sn=r.sn, e09=(t09 - r.tau) / r.tau, ecorr=(tc - r.tau) / r.tau))
cv = pd.DataFrame(rows)
print(f"sets = {cv.Set.nunique()}, ensayos = {len(cv)}")
for c in ["e09", "ecorr"]:
    print(f"  {c}: sesgo medio {cv[c].mean():+.3f}  mediana {cv[c].median():+.3f}  error abs. medio {cv[c].abs().mean():.3f}  fracción sobreestimada {np.mean(cv[c] > 0):.2f}")
hi3 = cv[cv.sn >= 3]
for c in ["e09", "ecorr"]:
    print(f"  σn ≥ 3 MPa {c}: sesgo {hi3[c].mean():+.3f}  abs {hi3[c].abs().mean():.3f}  n = {len(hi3)}")

print("\n== 6. m ajustado por set (todos los ensayos) — sets que llegan a σn ≥ 4 MPa")
ps = []
for s, g in df.groupby("Set"):
    if len(g) >= 3:
        p1, m = fit_set(g.sn.values, g.tau.values)
        ps.append(dict(Set=s, m=m, snmax=g.sn.max()))
ps = pd.DataFrame(ps)
print(f"todos: mediana m = {ps.m.median():.3f}, media {ps.m.mean():.3f}, n = {len(ps)}")
print(f"σn,max ≥ 4: mediana m = {ps[ps.snmax >= 4].m.median():.3f}, n = {(ps.snmax >= 4).sum()}")
cv.to_csv(Path(__file__).with_name("validacion_cruzada.csv"), index=False)
