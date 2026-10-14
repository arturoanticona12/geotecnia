"""Leps 3.0 candidato: curvatura dependiente de la resistencia, m = m0 − k·(φ'1 − 41°).
Modo B (calibración ≤ 1.5 MPa, predicción ≥ 2 MPa) y modo A (predictivo con calidad y e), ambos con LOPO. Errores en q."""
import sys, json, warnings, itertools, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import minimize_scalar, least_squares
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import sigma1, tau_leps2, CLASE  # noqa: E402

df = load_db()
df = df[(df["Lab Test"] == "TRX") & (df.s3 > 0) & df.s1.notna() & df.e.notna()].copy()
df["q"] = df.s1 - df.s3; df["ci"] = df["Material Type"].map(CLASE).map({"good": 0, "moderate": 1, "low": 2})


def mfun(phi1, m0, k):
    return np.clip(m0 - k * (phi1 - 41.0), 0.6, 1.0)


def tau_mv(sn, phi1, m0, k):
    return tau_leps2(sn, phi1, mfun(phi1, m0, k))


# ------------------------------------------------------------------ modo B
sets = []
for s, g in df.groupby("Set"):
    lo = g[g.sn <= 1.5]; hi = g[g.sn >= 2]
    if len(lo) >= 2 and len(hi) >= 1:
        sets.append((s, g.Reference.iloc[0], lo.s3.values, lo.q.values, hi.s3.values, hi.q.values, hi.sn.values))
grilla = list(itertools.product(np.round(np.arange(0.84, 0.921, 0.01), 2), [0, 0.002, 0.004, 0.006, 0.008, 0.010, 0.013, 0.016, 0.020]))
t0 = time.time(); E = []; PHI = []
for m0, k in grilla:
    fila, ph = [], []
    for (s, pb, s3l, ql, s3h, qh, snh) in sets:
        obj = lambda f1: np.sum(np.log(np.maximum(sigma1(tau_mv, s3l, np.full(len(s3l), f1), m0, k)[0] - s3l, 1e-6) / ql) ** 2)
        f1 = minimize_scalar(obj, bounds=(15, 70), method="bounded", options={"xatol": 0.01}).x
        fila.append((sigma1(tau_mv, s3h, np.full(len(s3h), f1), m0, k)[0] - s3h) / qh - 1); ph.append(f1)
    E.append(fila); PHI.append(ph)
print(f"modo B: grilla {len(grilla)} ({time.time() - t0:.0f} s); sets {len(sets)}")
PB = [x[1] for x in sets]; SN = [x[6] for x in sets]; pubs = sorted(set(PB))


def lopo(Eg, gr, etiqueta):
    errs, sns, sel = [], [], []
    for pb in pubs:
        tr = [i for i in range(len(sets)) if PB[i] != pb]; te = [i for i in range(len(sets)) if PB[i] == pb]
        j = int(np.argmin([np.mean(np.concatenate([np.log1p(Eg[j][i]) ** 2 for i in tr])) for j in range(len(gr))]))
        sel.append(gr[j]); errs += [Eg[j][i] for i in te]; sns += [SN[i] for i in te]
    e, sn = np.concatenate(errs), np.concatenate(sns)
    jb = int(np.argmin([np.mean(np.concatenate([np.log1p(Eg[j][i]) ** 2 for i in range(len(sets))])) for j in range(len(gr))]))
    m2, m3 = sn >= 2, sn >= 3
    print(f"  {etiqueta:26s} todos: {tuple(map(float, gr[jb]))} | σn≥2 sesgo {100*e[m2].mean():+5.1f} % EAM {100*np.abs(e[m2]).mean():4.1f} % "
          f"| σn≥3 sesgo {100*e[m3].mean():+5.1f} % EAM {100*np.abs(e[m3]).mean():4.1f} % | elegidos k: {sorted({float(x[1]) for x in sel})}")
    return gr[jb], e, sn


print("LOPO modo B:")
sub = [j for j, g in enumerate(grilla) if g[1] == 0]
lopo([E[j] for j in sub], [grilla[j] for j in sub], "m fijo (k = 0)")
best_B, eB, snB = lopo(E, grilla, "m = m0 − k(φ1 − 41°)")

# ------------------------------------------------------------------ modo A (predictivo)
S3, Q, Ee, CI, PUB = df.s3.values, df.q.values, df.e.values, df.ci.values, df.Reference.values


def predA(p, idx, var):
    phi1 = p[:3][CI[idx]] - p[3] * Ee[idx]
    m0, k = (p[4], p[5]) if var else (p[4], 0.0)
    return sigma1(tau_mv, S3[idx], phi1, m0, k)[0] - S3[idx]


def fitA(idx, var):
    x0 = [53, 50, 47, 20, 0.88] + ([0.005] if var else [])
    lb = [35, 35, 35, 0, 0.6] + ([-0.03] if var else []); ub = [70, 70, 70, 45, 1.0] + ([0.05] if var else [])
    return least_squares(lambda p: np.log(np.maximum(predA(np.array(p), idx, var), 1e-6) / Q[idx]), x0, bounds=(lb, ub)).x


errA = {v: np.full(len(df), np.nan) for v in (False, True)}; parA = {}
for pb in np.unique(PUB):
    tr, te = np.where(PUB != pb)[0], np.where(PUB == pb)[0]
    for v in (False, True):
        errA[v][te] = predA(fitA(tr, v), te, v) / Q[te] - 1
for v in (False, True):
    parA[v] = fitA(np.arange(len(df)), v)
pub = (sigma1(tau_leps2, S3, np.array([53, 50, 47.0])[CI] - 20 * Ee, 0.9)[0] - S3) / Q - 1
print("\nLOPO modo A (predictivo, φ'1 = φe0[calidad] − ω·e):")
for et, e in [("Leps 2.0 publicado", pub), ("Leps 2.0 reajustado, m fijo", errA[False]), ("m = m0 − k(φ1 − 41°)", errA[True])]:
    out = []
    for lo_, hi_ in [(0, 0.06), (0.06, 0.6), (0.6, 2), (2, 5)]:
        mk = (S3 >= lo_) & (S3 < hi_); out.append(f"σ3 {lo_}–{hi_}: {100*e[mk].mean():+5.1f}/{100*np.abs(e[mk]).mean():4.1f}")
    print(f"  {et:28s} " + " | ".join(out) + "  (sesgo/EAM %)")
print("  parámetros (todos), m fijo: φe0 = %.1f/%.1f/%.1f ω = %.1f m = %.3f" % tuple(parA[False]))
print("  parámetros (todos), m variable: φe0 = %.1f/%.1f/%.1f ω = %.1f m0 = %.3f k = %.4f" % tuple(parA[True]))
json.dump(dict(modoB=list(map(float, best_B)), modoA_fijo=parA[False].tolist(), modoA_var=parA[True].tolist()),
          open(AQUI / "leps3_mvariable.json", "w"), indent=1)
pd.DataFrame(dict(err=eB, sn=snB)).to_csv(AQUI / "leps3_mvariable_modoB.csv", index=False)
pd.DataFrame(dict(s3=S3, pub=PUB, L2pub=pub, fijo=errA[False], var=errA[True])).to_csv(AQUI / "leps3_mvariable_modoA.csv", index=False)
