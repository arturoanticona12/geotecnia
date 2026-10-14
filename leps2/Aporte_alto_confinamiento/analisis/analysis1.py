import sys, warnings, numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_columns", 60); pd.set_option("display.max_rows", 400)
PA = 0.1013
p = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0"
df = pd.read_excel(p + r"\Rockfill_Test_Database_v1.xlsx", sheet_name="Data", header=0)
df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
ren = {"σ3 (MPa)": "s3", "σ1 (MPa)": "s1", "σn (MPa)": "sn", "τ (MPa)": "tau", "ei": "e", "UCS (MPa)": "UCS",
       "Bg (%)": "Bg", "evol (%)": "evol", "eaxial (%)": "eax", "Fines-BT (%)": "fines", "D50-BT (mm)": "D50", "Dmax (mm)": "Dmax", "sat (%)": "sat"}
df = df.rename(columns=ren)
for c in ren.values():
    df[c] = pd.to_numeric(df[c], errors="coerce")
df = df[df["sn"] > 0].copy()
df["phis"] = np.degrees(np.arctan(df.tau / df.sn))
df["phi1_test"] = np.degrees(np.arctan(df.tau / ((10 * PA) ** 0.1 * df.sn ** 0.9)))  # Eq. 31

def tau_leps(sn, phi1, m):
    return np.tan(np.radians(phi1)) * (10 * PA) ** (1 - m) * sn ** m

def fit_set(sn, tau, m=None):
    if m is None:
        f = lambda x: np.log(tau_leps(sn, x[0], x[1])) - np.log(tau)
        r = least_squares(f, [41, 0.9], bounds=([15, 0.5], [70, 1.0]))
        return r.x
    f = lambda x: np.log(tau_leps(sn, x[0], m)) - np.log(tau)
    r = least_squares(f, [41], bounds=([15], [70]))
    return np.array([r.x[0], m])

# ---------- 1. Coverage
print("== Coverage of σn (MPa)")
for t in [1, 2, 3, 4, 5, 6, 7]:
    print(f"  σn>={t}: {int((df.sn>=t).sum())} tests")

# ---------- 2. Global trend of phi1_test vs σn (if m=0.9 holds, flat)
print("\n== φ'1-test (m=0.9 implied) by σn bin (all tests)")
bins = [0, 0.1, 0.3, 0.6, 1, 2, 3, 4, 5, 8]
df["bin"] = pd.cut(df.sn, bins)
print(df.groupby("bin").agg(n=("phi1_test", "size"), phi1_mean=("phi1_test", "mean"), phi1_sd=("phi1_test", "std"), phis_mean=("phis", "mean")).round(2))

# ---------- 3. Within-set normalisation: reference phi1 fitted with tests in 0.3<=σn<=1.5 (m=0.9)
rows = []
for s, g in df.groupby("Set"):
    ref = g[(g.sn >= 0.3) & (g.sn <= 1.5)]
    if len(ref) < 1 or len(g) < 3:
        continue
    phi1_ref, _ = fit_set(ref.sn.values, ref.tau.values, m=0.9)
    for _, r in g.iterrows():
        rows.append(dict(Set=s, sn=r.sn, dphi1=r.phi1_test - phi1_ref, phi1_ref=phi1_ref, UCS=r.UCS, Bg=r.Bg, mat=r["Material Type"]))
w = pd.DataFrame(rows)
w["bin"] = pd.cut(w.sn, bins)
print("\n== Within-set Δφ'1 (test − set reference fitted on 0.3–1.5 MPa, m=0.9) by σn bin")
print(w.groupby("bin").agg(n=("dphi1", "size"), sets=("Set", "nunique"), mean=("dphi1", "mean"), median=("dphi1", "median"), sd=("dphi1", "std")).round(2))

# ---------- 4. Hold-out extrapolation: sets with tests at σn<=1.5 (>=2) and σn>=3
print("\n== Hold-out extrapolation: train σn<=1.5 MPa, predict σn>=3 MPa")
ho = []
for s, g in df.groupby("Set"):
    tr = g[g.sn <= 1.5]; te = g[g.sn >= 3]
    if len(tr) < 2 or len(te) < 1:
        continue
    p09 = fit_set(tr.sn.values, tr.tau.values, m=0.9)
    pfree = fit_set(tr.sn.values, tr.tau.values) if len(tr) >= 3 else p09
    pall = fit_set(g.sn.values, g.tau.values)
    for _, r in te.iterrows():
        ho.append(dict(Set=s, mat=r["Material Type"], ref=r.Reference, sn=r.sn, UCS=r.UCS, Bg=r.Bg, e=r.e,
                       phis_test=r.phis,
                       err09=(tau_leps(r.sn, *p09) - r.tau) / r.tau,
                       errfree=(tau_leps(r.sn, *pfree) - r.tau) / r.tau,
                       m_train=pfree[1], m_all=pall[1], phi1_09=p09[0]))
ho = pd.DataFrame(ho)
print(ho.round(3).to_string())
print("\nSummary  err (pred−test)/test:  m=0.9 mean %.3f  median %.3f | m free mean %.3f median %.3f | n=%d sets=%d" % (
    ho.err09.mean(), ho.err09.median(), ho.errfree.mean(), ho.errfree.median(), len(ho), ho.Set.nunique()))

# ---------- 5. Local curvature: per set, m fitted on low half vs high half
print("\n== Local curvature m: low range (σn<=1) vs high range (σn>=1) within same set")
lc = []
for s, g in df.groupby("Set"):
    lo = g[g.sn <= 1.0]; hi = g[g.sn >= 1.0]
    if len(lo) >= 2 and len(hi) >= 2 and lo.sn.max() / lo.sn.min() > 2 and hi.sn.max() / hi.sn.min() > 1.5:
        mlo = fit_set(lo.sn.values, lo.tau.values)[1]; mhi = fit_set(hi.sn.values, hi.tau.values)[1]
        lc.append(dict(Set=s, mat=g["Material Type"].iloc[0], mlo=mlo, mhi=mhi, snmax=g.sn.max(), UCS=g.UCS.iloc[0]))
lc = pd.DataFrame(lc)
print(lc.round(3).to_string())
print("mean m_low=%.3f m_high=%.3f ; fraction m_high>m_low = %.2f (n=%d)" % (lc.mlo.mean(), lc.mhi.mean(), (lc.mhi > lc.mlo).mean(), len(lc)))

# ---------- 6. Per-set m vs UCS and stress range
print("\n== Per-set fitted (φ1, m) for sets with ≥3 tests; correlation with UCS, e, σn max")
ps = []
for s, g in df.groupby("Set"):
    if len(g) < 3: continue
    phi1, m = fit_set(g.sn.values, g.tau.values)
    ps.append(dict(Set=s, phi1=phi1, m=m, UCS=g.UCS.iloc[0], e=g.e.mean(), snmax=g.sn.max(), Bgmax=g.Bg.max(), mat=g["Material Type"].iloc[0]))
ps = pd.DataFrame(ps)
ps["log_snmax_UCS"] = np.log10(ps.snmax / ps.UCS)
print(ps[["phi1", "m", "UCS", "e", "snmax", "Bgmax", "log_snmax_UCS"]].corr().round(2))
print(ps.groupby(pd.cut(ps.snmax, [0, 1, 2, 4, 8])).agg(n=("m", "size"), m_mean=("m", "mean"), m_med=("m", "median")).round(3))

# ---------- 7. Breakage
print("\n== Breakage Bg vs normalised stress")
b = df[df.Bg.notna() & df.UCS.notna()].copy()
b["x"] = b.sn / b.UCS
print("corr(Bg, log σn)=%.2f  corr(Bg, log σn/UCS)=%.2f  corr(Bg, e)=%.2f corr(Bg,UCS)=%.2f n=%d" % (
    np.corrcoef(b.Bg, np.log(b.sn))[0, 1], np.corrcoef(b.Bg, np.log(b.x))[0, 1], b[["Bg", "e"]].dropna().corr().iloc[0, 1], np.corrcoef(b.Bg, b.UCS)[0, 1], len(b)))
print(b.groupby(pd.cut(b.sn, bins)).Bg.describe().round(1))
# Bg vs within-set strength drop
wb = w[w.Bg.notna()]
print("corr(Δφ1, Bg) within-set:", round(np.corrcoef(wb.dphi1, wb.Bg)[0, 1], 3), "n=", len(wb))
# phis vs Bg partial (control for σn): regress phis on log sn and Bg
bb = b.dropna(subset=["phis"])
X = np.c_[np.ones(len(bb)), np.log10(bb.sn), bb.Bg]
coef, *_ = np.linalg.lstsq(X, bb.phis, rcond=None)
print("φs = %.2f + %.2f log10σn + %.3f Bg" % tuple(coef))

# ---------- 8. Volumetric strain at failure
print("\n== Volumetric strain at failure vs σ3 (sign check)")
v = df[df.evol.notna()]
print(v.groupby(pd.cut(v.s3, [0, 0.1, 0.3, 0.6, 1, 2, 3, 5])).evol.describe().round(2))
print(v.groupby("Reference").agg(n=("evol", "size"), evmin=("evol", "min"), evmax=("evol", "max"), s3max=("s3", "max")).to_string())

ho.to_csv(str(__import__("pathlib").Path(__file__).with_name("holdout.csv")), index=False)

