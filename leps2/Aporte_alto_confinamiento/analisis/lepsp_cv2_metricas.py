"""Métricas de lepsp_cv2: ramas de la regla, sensibilidad de umbrales, líneas base ingenuas (IC pareado por publicación),
validación de la rama conjunta y modo A con clase desconocida. Bootstrap de publicaciones (2000). Escribe lepsp_cv2_metricas.json."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; RNG = np.random.default_rng(3); NB = 2000
B = pd.read_csv(AQ / "lepsp_cv2_B.csv"); J = pd.read_csv(AQ / "lepsp_cv2_J.csv"); M = pd.read_json(AQ / "lepsp_cv2_Amix.json")
crps = lambda mu, sd, y: sd * ((y - mu) / sd * (2 * norm.cdf((y - mu) / sd) - 1) + 2 * norm.pdf((y - mu) / sd) - 1 / np.sqrt(np.pi))


def met(df, mu="mu", sd="sd"):
    z = (df.y - df[mu]) / df[sd]
    return dict(n=len(df), cob80=float(np.mean(np.abs(z) <= 1.2816)), bajo10=float(np.mean(z < -1.2816)), sdz=float(np.std(z)),
                mae=float(np.mean(np.abs(df.y - df[mu]))), crps=float(np.mean(crps(df[mu], df[sd], df.y))))


def boot_diff(a, b, col_a, col_b):
    """IC de la diferencia pareada de CRPS (a − b) remuestreando publicaciones."""
    ga = a.groupby("pub"); gb = b.groupby("pub"); pubs = a.pub.unique(); vals = []
    for _ in range(NB):
        s = RNG.choice(pubs, len(pubs)); xa = np.concatenate([ga.get_group(p)[col_a].values for p in s]); xb = np.concatenate([gb.get_group(p)[col_b].values for p in s])
        vals.append(xa.mean() - xb.mean())
    return np.percentile(vals, [2.5, 97.5]).tolist()


R = {}
base = B[B.variante == "conjunta"].copy(); base["c_prev"] = crps(base.muA, base.sdA, base.y)
# sigma de las líneas base ingenuas: RMSE fuera de muestra de cada variante (dejando fuera la publicación)
for v in ("ingenuo m=0.86", "ingenuo m=0.9"):
    b = B[B.variante == v].copy(); sds = []
    for p in b.pub.unique():
        r = b[b.pub != p]; sds.append((p, np.sqrt(np.mean((r.y - r.mu) ** 2))))
    b["sd"] = b.pub.map(dict(sds)); B.loc[b.index, "sd"] = b.sd
for v in B.variante.unique():
    b = B[B.variante == v].copy().reset_index(drop=True); b["c"] = crps(b.mu, b.sd, b.y); b["c_prev"] = crps(b.muA, b.sdA, b.y)
    m = met(b); m["mejora_vs_previa"] = [float(b.c_prev.mean() - b.c.mean())] + boot_diff(b, b, "c_prev", "c")
    m["ramas"] = b.groupby("Set").rama.first().value_counts().to_dict(); R[f"B|{v}"] = m
    print(f"{v:22s} n={m['n']} cob80 {m['cob80']:.2f} bajo10 {m['bajo10']:.2f} sd(z) {m['sdz']:.2f} MAE {m['mae']:.4f} CRPS {m['crps']:.4f} "
          f"| mejora vs previa {m['mejora_vs_previa'][0]:+.4f} [{m['mejora_vs_previa'][1]:+.4f},{m['mejora_vs_previa'][2]:+.4f}] | ramas {m['ramas']}")
# comparación pareada regla publicada vs ingenuo m=0.86
rg = B[B.variante == "regla r3 p0.05"].copy().reset_index(drop=True); rg["c"] = crps(rg.mu, rg.sd, rg.y)
ig = B[B.variante == "ingenuo m=0.86"].copy().reset_index(drop=True); ig["c"] = crps(ig.mu, ig.sd, ig.y)
R["regla_vs_ingenuo086"] = [float(ig.c.mean() - rg.c.mean())] + boot_diff(ig, rg, "c", "c")
print(f"\nCRPS ingenuo(0.86) − regla: {R['regla_vs_ingenuo086'][0]:+.4f} [{R['regla_vs_ingenuo086'][1]:+.4f}, {R['regla_vs_ingenuo086'][2]:+.4f}]")
# por rama dentro de la regla publicada
for rama in ("conjunta", "nivel"):
    s = rg[rg.rama == rama]
    if len(s):
        s = s.copy(); s["c_prev"] = crps(s.muA, s.sdA, s.y); m = met(s); m["crps_prev"] = float(s.c_prev.mean()); m["sets"] = int(s.Set.nunique())
        R[f"regla|rama {rama}"] = m; print(f"regla r3 p0.05, rama {rama:9s}: sets {m['sets']} n {m['n']} CRPS {m['crps']:.4f} (previa {m['crps_prev']:.4f}) sd(z) {m['sdz']:.2f} cob80 {m['cob80']:.2f}")
# validación de la rama conjunta (mitad inferior → superior)
print()
for v in J.variante.unique():
    j = J[J.variante == v].copy().reset_index(drop=True)
    if v.startswith("ingenuo"):
        sds = {p: np.sqrt(np.mean((j[j.pub != p].y - j[j.pub != p].mu) ** 2)) for p in j.pub.unique()}; j["sd"] = j.pub.map(sds)
    j["c"] = crps(j.mu, j.sd, j.y); j["c_prev"] = crps(j.muA, j.sdA, j.y); m = met(j); m["sets"] = int(j.Set.nunique()); m["pubs"] = int(j.pub.nunique())
    m["mejora_vs_previa"] = [float(j.c_prev.mean() - j.c.mean())] + boot_diff(j, j, "c_prev", "c"); R[f"J|{v}"] = m
    print(f"rama conjunta, {v:15s}: sets {m['sets']} pubs {m['pubs']} n {m['n']} cob80 {m['cob80']:.2f} bajo10 {m['bajo10']:.2f} sd(z) {m['sdz']:.2f} CRPS {m['crps']:.4f} "
          f"| mejora vs previa {m['mejora_vs_previa'][0]:+.4f} [{m['mejora_vs_previa'][1]:+.4f},{m['mejora_vs_previa'][2]:+.4f}]")
# modo A con clase desconocida (mezcla): CDF de mezcla para cobertura y CRPS por integración numérica
yy = np.linspace(-4.0, 4.0, 8001)                     # ronda 3: la grilla anterior (−2.5 a 1.5) truncaba 70 ensayos con y > 1.5
cov, bel, cr = [], [], []
for _, r in M.iterrows():
    mus, sds, ws = map(np.array, (r.mus, r.sds, r.ws)); Fm = (ws[None, :] * norm.cdf((yy[:, None] - mus[None, :]) / sds[None, :])).sum(1)
    q10, q90 = np.interp([0.1, 0.9], Fm, yy); cov.append(q10 <= r.y <= q90); bel.append(r.y < q10)
    cr.append(np.trapezoid((Fm - (yy >= r.y)) ** 2, yy))
R["A|clase desconocida"] = dict(n=len(M), cob80=float(np.mean(cov)), bajo10=float(np.mean(bel)), crps=float(np.mean(cr)))
print(f"\nModo A con clase desconocida (mezcla): n {len(M)} cob80 {np.mean(cov):.3f} bajo10 {np.mean(bel):.3f} CRPS {np.mean(cr):.4f}")
json.dump(R, open(AQ / "lepsp_cv2_metricas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
