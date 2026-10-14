"""¿Qué m usar para extrapolar? Calibrar φ'1 con ensayos de σn ≤ 1.5 MPa y un m fijo, predecir σn ≥ 2 MPa.
Barrido de m y selección con validación cruzada dejando fuera una publicación (LORO)."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path(__file__).parent))
from common import load_db, tau_leps, fit_set  # noqa: E402

df = load_db()
MS = np.round(np.arange(0.78, 0.951, 0.01), 2)
rows = []
for s, g in df.groupby("Set"):
    tr = g[g.sn <= 1.5]; te = g[g.sn >= 2]
    if len(tr) < 2 or len(te) < 1:
        continue
    for m in MS:
        phi1 = fit_set(tr.sn.values, tr.tau.values, m=m)[0]
        for _, r in te.iterrows():
            rows.append(dict(Set=s, ref=r.Reference, sn=r.sn, m=m, err=(tau_leps(r.sn, phi1, m) - r.tau) / r.tau,
                             UCS=r.UCS))
R = pd.DataFrame(rows)
print(f"sets = {R.Set.nunique()}, publicaciones = {R.ref.nunique()}, ensayos = {R[R.m == 0.9].shape[0]}")
print("\nBarrido de m (σn ≥ 2 MPa | σn ≥ 3 MPa): sesgo medio y error absoluto medio de τ")
tab = []
for m in MS:
    a = R[R.m == m]; b = a[a.sn >= 3]
    # promedio por set primero (cada set pesa igual)
    ps = a.groupby("Set").err.mean()
    tab.append(dict(m=m, sesgo=a.err.mean(), mae=a.err.abs().mean(), sesgo_set=ps.mean(), sesgo3=b.err.mean(), mae3=b.err.abs().mean(),
                    frac_sobre=(a.err > 0).mean()))
tab = pd.DataFrame(tab)
print(tab.round(3).to_string(index=False))

# m sin sesgo (interpolado, ponderación por set)
m0 = np.interp(0, tab.sesgo_set.values, tab.m.values)
print(f"\nm con sesgo medio por set nulo: {m0:.3f} ; sesgo global nulo: {np.interp(0, tab.sesgo.values, tab.m.values):.3f} ; σn≥3: {np.interp(0, tab.sesgo3.values, tab.m.values):.3f}")

# LORO: elegir m con las demás publicaciones, evaluar en la excluida
out = []
for ref in R.ref.unique():
    tr = R[R.ref != ref]
    sb = tr.groupby("m").apply(lambda d: d.groupby("Set").err.mean().mean())
    m_sel = sb.abs().idxmin()
    te = R[(R.ref == ref)]
    out.append(dict(ref=ref, m_sel=m_sel, n=len(te[te.m == 0.9]),
                    err_sel=te[te.m == m_sel].err.mean(), err_09=te[te.m == 0.9].err.mean()))
out = pd.DataFrame(out)
print("\nValidación dejando fuera una publicación:")
print(out.round(3).to_string(index=False))
w = out.n / out.n.sum()
print(f"sesgo ponderado: m=0.9 → {np.sum(w * out.err_09):+.3f} ; m elegido → {np.sum(w * out.err_sel):+.3f} ; m elegido: {out.m_sel.min()}–{out.m_sel.max()}")

# bootstrap por set del m sin sesgo
rng = np.random.default_rng(7); sets = R.Set.unique(); bs = []
piv = R.groupby(["Set", "m"]).err.mean().unstack()
for _ in range(2000):
    smp = piv.loc[rng.choice(sets, len(sets))].mean()
    bs.append(np.interp(0, smp.values, smp.index.values))
print(f"m sin sesgo, bootstrap por set: mediana {np.median(bs):.3f}, IC 90 % [{np.percentile(bs, 5):.3f}, {np.percentile(bs, 95):.3f}]")
# por clase de UCS
for lo, hi in [(0, 80), (80, 150), (150, 400)]:
    sub = R[(R.UCS > lo) & (R.UCS <= hi)]
    if sub.empty: continue
    t = sub.groupby("m").apply(lambda d: d.groupby("Set").err.mean().mean())
    print(f"UCS {lo}-{hi}: sets = {sub.Set.nunique()}, m sin sesgo ≈ {np.interp(0, t.values, t.index.values):.3f}, sesgo con m=0.9: {t.loc[0.9]:+.3f}")
tab.to_csv(Path(__file__).with_name("barrido_m.csv"), index=False)
R.to_csv(Path(__file__).with_name("barrido_m_detalle.csv"), index=False)

