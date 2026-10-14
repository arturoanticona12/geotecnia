import sys, warnings, numpy as np, pandas as pd
from scipy.optimize import least_squares
from scipy import stats
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 400)
exec(open(__import__("pathlib").Path(__file__).with_name("common.py"), encoding="utf-8").read())

ho = pd.read_csv(SP + r"\holdout.csv")
h = ho.dropna(subset=["UCS"])
print("holdout err09 vs UCS: r=%.2f n=%d ; vs log(sn/UCS): r=%.2f" % (np.corrcoef(h.err09, h.UCS)[0, 1], len(h), np.corrcoef(h.err09, np.log10(h.sn / h.UCS))[0, 1]))
print(h.groupby(pd.cut(h.UCS, [0, 80, 150, 400])).err09.agg(["size", "mean", "median"]).round(3))

w = within_set(df)
hi = w[(w.sn >= 1.013)].dropna(subset=["UCS"]).copy()
hi["L"] = np.log10(hi.sn / (10 * PA))
hi["LU"] = np.log10(hi.sn / hi.UCS)
# model A: dphi1 = a*L (through origin at anchor)
a = np.linalg.lstsq(hi[["L"]].values, hi.dphi1.values, rcond=None)[0][0]
resA = hi.dphi1 - a * hi.L
print("\nModel A Δφ1 = a·log10(σn/10pa): a=%.2f °/decade, RMSE=%.2f, n=%d" % (a, np.sqrt((resA ** 2).mean()), len(hi)))
# model B: dphi1 = a*L + b*L*log10(100/UCS)  (stress effect scaled by particle strength)
X = np.c_[hi.L, hi.L * np.log10(100 / hi.UCS)]
cb = np.linalg.lstsq(X, hi.dphi1.values, rcond=None)[0]
resB = hi.dphi1 - X @ cb
print("Model B Δφ1 = L·(%.2f + %.2f·log10(100/UCS)), RMSE=%.2f" % (cb[0], cb[1], np.sqrt((resB ** 2).mean())))
# significance of b via bootstrap over sets
rng = np.random.default_rng(1); sets = hi.Set.unique(); bs = []
for _ in range(2000):
    s = rng.choice(sets, len(sets)); d = pd.concat([hi[hi.Set == k] for k in s])
    Xb = np.c_[d.L, d.L * np.log10(100 / d.UCS)]
    bs.append(np.linalg.lstsq(Xb, d.dphi1.values, rcond=None)[0])
bs = np.array(bs)
print("bootstrap 90%% CI a: [%.2f, %.2f]  b: [%.2f, %.2f]" % (*np.percentile(bs[:, 0], [5, 95]), *np.percentile(bs[:, 1], [5, 95])))
bsA = []
for _ in range(2000):
    s = rng.choice(sets, len(sets)); d = pd.concat([hi[hi.Set == k] for k in s])
    bsA.append(np.linalg.lstsq(d[["L"]].values, d.dphi1.values, rcond=None)[0][0])
print("bootstrap 90%% CI a (model A): [%.2f, %.2f]" % tuple(np.percentile(bsA, [5, 95])))
print(hi.groupby(pd.cut(hi.UCS, [0, 80, 150, 400])).apply(lambda g: pd.Series(dict(n=len(g), sets=g.Set.nunique(), slope=np.linalg.lstsq(g[["L"]].values, g.dphi1.values, rcond=None)[0][0]))).round(2))

# equivalent m: phi1 drop a per decade above anchor ⇔ tan φs ∝ σn^(m-1) with m=0.9 plus extra
# compute effective m over 1–8 MPa matching model A for φ1=41
for phi1 in [38, 41, 44]:
    sn = np.array([1.013, 8.0])
    tau_true = np.tan(np.radians(phi1 + a * np.log10(sn / 1.013))) * (10 * PA) ** 0.1 * sn ** 0.9
    meff = np.polyfit(np.log(sn), np.log(tau_true), 1)[0]
    print("φ1=%d: effective m over 1–8 MPa = %.3f" % (phi1, meff))

# Bg vs log(σn) by UCS class (median breakage) for later chart
b = df.dropna(subset=["Bg", "UCS"]).copy()
for lo, hi_ in [(0, 80), (80, 150), (150, 400)]:
    g = b[(b.UCS > lo) & (b.UCS <= hi_)]
    sl, ic, r, pv, se = stats.linregress(np.log10(g.sn), g.Bg)
    print(f"UCS {lo}-{hi_}: n={len(g)} Bg = {ic:.1f} + {sl:.1f} log10σn  r={r:.2f}")

# fraction of tests with net dilation at failure
v = df.dropna(subset=["evol"])
print(v.groupby(pd.cut(v.s3, [0, 0.1, 0.3, 0.6, 1, 2, 5])).evol.apply(lambda s: (s > 0).mean()).round(2))

