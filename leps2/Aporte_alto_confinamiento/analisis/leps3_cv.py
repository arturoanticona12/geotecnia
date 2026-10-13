"""Leps 3.0 frente a Leps 2.0: ajuste en esfuerzos principales y validación cruzada dejando fuera cada publicación.
Modo A (predictivo): φ'1 = φ'e=0[calidad] − ω·e. Modo B (extrapolación): φ'1 por set con σ'n ≤ 1.5 MPa, predicción σ'n ≥ 2 MPa."""
import sys, json, warnings, time
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore")
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE, sigma1, tau_leps2, tau_leps3, PA  # noqa: E402

df = load_db()
df = df[(df["Lab Test"] == "TRX") & (df.s3 > 0) & df.s1.notna() & df.e.notna()].copy()
df["clase"] = df["Material Type"].map(CLASE)
df["ci"] = df.clase.map({"good": 0, "moderate": 1, "low": 2})
df["q"] = df.s1 - df.s3
df["pub"] = df.Reference
print(f"ensayos {len(df)}, sets {df.Set.nunique()}, publicaciones {df.pub.nunique()}")
S3, Q, E, CI = df.s3.values, df.q.values, df.e.values, df.ci.values

# ------------------------------------------------------------------ modelos del modo A
def pred_A(nombre, p, idx):
    s3, e, ci = S3[idx], E[idx], CI[idx]
    if nombre == "L2pub":
        phi1 = np.array([53, 50, 47.0])[ci] - 20 * e
        return sigma1(tau_leps2, s3, phi1, 0.9)[0] - s3
    if nombre == "L2fit":
        phi1 = p[:3][ci] - p[3] * e
        return sigma1(tau_leps2, s3, phi1, p[4])[0] - s3
    if nombre == "L3fit":
        phi1 = p[:3][ci] - p[3] * e
        return sigma1(tau_leps3, s3, phi1, p[4], np.exp(p[5]))[0] - s3


X0 = {"L2pub": None, "L2fit": [53, 50, 47, 20, 0.9], "L3fit": [53, 50, 47, 20, 34, np.log(10.0)]}
LB = {"L2fit": [35, 35, 35, 0, 0.6], "L3fit": [35, 35, 35, 0, 20, np.log(0.5)]}
UB = {"L2fit": [70, 70, 70, 45, 1.0], "L3fit": [70, 70, 70, 45, 42, np.log(2000)]}


def ajustar_A(nombre, idx):
    if nombre == "L2pub":
        return None
    f = lambda p: np.log(np.maximum(pred_A(nombre, np.array(p), idx), 1e-6) / Q[idx])
    return least_squares(f, X0[nombre], bounds=(LB[nombre], UB[nombre]), x_scale="jac").x


def resumen(err, s3, etiqueta):
    out = {}
    for lo, hi, k in [(0, 0.06, "<0.06"), (0.06, 0.6, "0.06–0.6"), (0.6, 2, "0.6–2"), (2, 5, "≥2")]:
        mk = (s3 >= lo) & (s3 < hi)
        out[k] = (100 * err[mk].mean(), 100 * np.abs(err[mk]).mean(), int(mk.sum()))
    print(f"  {etiqueta:7s} " + " | ".join(f"σ3 {k}: sesgo {b:+5.1f} % EAM {a:4.1f} % (n={n})" for k, (b, a, n) in out.items()))
    return out


# ------------------------------------------------------------------ 1. ajuste con todos los datos
t0 = time.time()
todo = np.arange(len(df)); PAR = {}
for nm in ["L2fit", "L3fit"]:
    PAR[nm] = ajustar_A(nm, todo)
print("\nParámetros con todos los datos:")
print("  Leps 2.0 reajustado: φe0 (buena, moderada, baja) = %.1f, %.1f, %.1f ; ω = %.1f ; m = %.3f" % tuple(PAR["L2fit"]))
p3 = PAR["L3fit"]
print("  Leps 3.0:            φe0 = %.1f, %.1f, %.1f ; ω = %.1f ; φcs = %.1f° ; σcr = %.1f MPa" % (*p3[:5], np.exp(p3[5])))
print("\nModo A, ajuste y evaluación con todos los datos (error en q = σ1 − σ3):")
for nm in ["L2pub", "L2fit", "L3fit"]:
    qp = pred_A(nm, PAR.get(nm), todo); resumen(qp / Q - 1, S3, nm)

# ------------------------------------------------------------------ 2. LOPO modo A
print("\nModo A, validación dejando fuera cada publicación:")
pubs = df.pub.unique(); ERR = {nm: np.full(len(df), np.nan) for nm in ["L2pub", "L2fit", "L3fit"]}; FOLD = {}
for pb in pubs:
    te = np.where(df.pub.values == pb)[0]; tr = np.where(df.pub.values != pb)[0]
    for nm in ERR:
        p = ajustar_A(nm, tr); FOLD[(pb, nm)] = p
        ERR[nm][te] = pred_A(nm, p, te) / Q[te] - 1
for nm in ERR:
    resumen(ERR[nm], S3, nm)
print(f"  (tiempo {time.time() - t0:.0f} s)")

# ------------------------------------------------------------------ 3. modo B: extrapolación por set
print("\nModo B: φ'1 de cada set con σ'n ≤ 1.5 MPa, predicción de σ'n ≥ 2 MPa (globales del pliegue sin esa publicación)")
rows = []
for s, g in df.groupby("Set"):
    lo = g[g.sn <= 1.5]; hi = g[g.sn >= 2]
    if len(lo) < 2 or len(hi) < 1:
        continue
    pb = g.pub.iloc[0]; p2 = FOLD[(pb, "L2fit")]; p3_ = FOLD[(pb, "L3fit")]
    cands = {"m=0.9": (tau_leps2, lambda f: (f, 0.9)), "m=0.87": (tau_leps2, lambda f: (f, 0.87)),
             "L2 m ajust.": (tau_leps2, lambda f: (f, p2[4])),
             "Leps 3.0": (tau_leps3, lambda f: (f, p3_[4], np.exp(p3_[5])))}
    for nm, (fn, par) in cands.items():
        fobj = lambda x: np.log(np.maximum(sigma1(fn, lo.s3.values, np.full(len(lo), x[0]), *par(np.full(len(lo), x[0]))[1:])[0] - lo.s3.values, 1e-6) / lo.q.values)
        phi1 = least_squares(fobj, [41.0], bounds=([15], [70])).x[0]
        qp = sigma1(fn, hi.s3.values, np.full(len(hi), phi1), *par(np.full(len(hi), phi1))[1:])[0] - hi.s3.values
        for k in range(len(hi)):
            rows.append(dict(Set=s, pub=pb, modelo=nm, sn=hi.sn.values[k], err=qp[k] / hi.q.values[k] - 1))
B = pd.DataFrame(rows)
print(f"  sets {B.Set.nunique()}, ensayos {B[B.modelo == 'm=0.9'].shape[0]}, publicaciones {B.pub.nunique()}")
for nm in ["m=0.9", "m=0.87", "L2 m ajust.", "Leps 3.0"]:
    b = B[B.modelo == nm]; b3 = b[b.sn >= 3]
    ps = b.groupby("Set").err.mean()
    print(f"  {nm:12s} σn≥2: sesgo {100*b.err.mean():+5.1f} % (por set {100*ps.mean():+5.1f} %) EAM {100*b.err.abs().mean():4.1f} % | "
          f"σn≥3: sesgo {100*b3.err.mean():+5.1f} % EAM {100*b3.err.abs().mean():4.1f} % (n={len(b3)})")

# ------------------------------------------------------------------ 4. interacción densidad × esfuerzo en los datos
from common import within_set  # noqa: E402
w = within_set(load_db()); h = w[w.sn >= 10 * PA].copy(); h["L"] = np.log10(h.sn / (10 * PA)); h["d"] = h.phi1_ref - 41
X = np.c_[h.L, h.L * h.d]; c = np.linalg.lstsq(X, h.dphi1, rcond=None)[0]
rng = np.random.default_rng(3); sets = h.Set.unique(); bs = []
for _ in range(1000):
    dd = pd.concat([h[h.Set == k] for k in rng.choice(sets, len(sets))])
    bs.append(np.linalg.lstsq(np.c_[dd.L, dd.L * dd.d], dd.dphi1, rcond=None)[0][1])
print(f"\nInteracción en los datos: Δφ1 = L·({c[0]:.2f} {c[1]:+.3f}·(φ1,ref − 41°)); IC 90 % del término de interacción "
      f"[{np.percentile(bs, 5):+.3f}, {np.percentile(bs, 95):+.3f}] (negativo: los sets más resistentes pierden más con el esfuerzo)")

# ------------------------------------------------------------------ 5. estabilidad de φcs y σcr entre pliegues, y extrapolación
pc = np.array([FOLD[(pb, "L3fit")] for pb in pubs])
print(f"\nLeps 3.0 entre pliegues: φcs {pc[:, 4].min():.1f}–{pc[:, 4].max():.1f}° ; σcr {np.exp(pc[:, 5]).min():.1f}–{np.exp(pc[:, 5]).max():.1f} MPa")
for sn_ in [1.013, 3, 5, 8, 10, 15]:
    l2 = np.degrees(np.arctan(tau_leps2(sn_, 41, 0.9) / sn_)); l287 = np.degrees(np.arctan(tau_leps2(sn_, 41, 0.87) / sn_))
    l3 = np.degrees(np.arctan(tau_leps3(sn_, 41, p3[4], np.exp(p3[5])) / sn_))
    print(f"  φ'1 = 41°, σ'n = {sn_:5.2f} MPa: φ's  Leps 2.0 m=0.9 {l2:4.1f}° | m=0.87 {l287:4.1f}° | Leps 3.0 {l3:4.1f}°")
json.dump({"L2fit": PAR["L2fit"].tolist(), "L3fit": PAR["L3fit"].tolist(),
           "folds": {f"{k[0]}|{k[1]}": (v.tolist() if v is not None else None) for k, v in FOLD.items()}},
          open(AQUI / "leps3_parametros.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
B.to_csv(AQUI / "leps3_modoB.csv", index=False)
pd.DataFrame({k: v for k, v in ERR.items()} | {"s3": S3, "pub": df.pub.values, "Set": df.Set.values}).to_csv(AQUI / "leps3_modoA.csv", index=False)
