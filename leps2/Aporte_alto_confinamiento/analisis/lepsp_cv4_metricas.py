"""Métricas de la validación de la ronda 4. Diferencias por publicación: prueba exacta de signo invertido (sign-flip)
sobre las medias por publicación (exacta si ≤ 20 publicaciones; si no, 200 000 permutaciones), bootstrap de
publicaciones (IC 95 %) y ajuste de Holm sobre la familia de comparaciones de cada modo. Se reportan todas las pruebas.
Modo A: acotada (cv4) frente a cuadrática M2 y Leps 2.0 con dispersión constante (cv_A, mismos pliegues).
Modo B: todas las variantes frente a «nivel». Escribe lepsp_cv4_metricas.json."""
import sys, json, itertools
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; S0 = 1.013; Z90 = norm.ppf(0.9); rng = np.random.default_rng(0)


def met(y, mu, sd):
    z = (y - mu) / sd; crps = sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))
    q10 = mu - Z90 * sd; pin = np.where(y < q10, 0.9 * (q10 - y), 0.1 * (y - q10))
    return dict(crps=np.asarray(crps), cob80=np.asarray(np.abs(z) < Z90, float), bajo10=np.asarray(z < -Z90, float), pin10=np.asarray(pin), z=np.asarray(z))


def resumen(r):
    z = r["z"]
    return dict(n=len(z), crps=float(r["crps"].mean()), cob80=float(r["cob80"].mean()), bajo10=float(r["bajo10"].mean()), pin10=float(r["pin10"].mean()),
                z_medio=float(z.mean()), sd_z=float(z.std()), pit=np.histogram(norm.cdf(z), bins=5, range=(0, 1))[0].tolist())


def signflip(pm):
    n = len(pm); obs = abs(pm.mean())
    if n <= 20:
        sig = np.array(list(itertools.product((-1, 1), repeat=n)))
    else:
        sig = rng.choice((-1, 1), size=(200000, n))
    return float(np.mean(np.abs((sig * pm).mean(1)) >= obs - 1e-15))


def comparar(dif, pubs):
    up = np.unique(pubs); idx = [np.where(pubs == p)[0] for p in up]; pm = np.array([dif[i].mean() for i in idx])
    bs = [dif[np.concatenate([idx[i] for i in rng.integers(0, len(up), len(up))])].mean() for _ in range(4000)]
    return dict(media=float(dif.mean()), ic95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], n_pub=len(up),
                pubs_a_mejor=int((pm < 0).sum()), p_signflip=signflip(pm))


def holm(fam):
    ks = sorted(fam, key=lambda k: fam[k]["p_signflip"]); m = len(ks); acc = 0
    for i, k in enumerate(ks):
        acc = max(acc, min(1.0, (m - i) * fam[k]["p_signflip"])); fam[k]["p_holm"] = acc


OUT = {}
A = pd.read_csv(AQ / "lepsp_cv4_A.csv"); C = pd.read_csv(AQ / "lepsp_cv_A.csv"); C = C[(C.agrup == "pub") & (C.esp == "M2")]
M = A.merge(C[["pub", "Set", "x", "y", "mu", "sd", "mu0", "sd0"]], on=["pub", "Set", "x", "y"], suffixes=("", "_q")); assert len(M) == len(A)
famA = {}
for banda, sel in (("todo", M.x > -99), ("sn>2.75", S0 * np.exp(M.x) > 2.75), ("sn<0.5", S0 * np.exp(M.x) < 0.5)):
    D = M[sel.values]; R = {"acotada": met(D.y.values, D.mu.values, D.sd.values), "cuadratica": met(D.y.values, D.mu_q.values, D.sd_q.values),
                            "leps2_ref": met(D.y.values, D.mu0.values, D.sd0.values)}
    o = {k: resumen(v) for k, v in R.items()}; o["n"] = len(D); o["n_pub"] = int(D.pub.nunique())
    for a, b in (("acotada", "cuadratica"), ("acotada", "leps2_ref")):
        for mt in ("crps", "pin10"):
            o[f"{a}-{b}|{mt}"] = comparar(R[a][mt] - R[b][mt], D.pub.values); famA[(banda, a, b, mt)] = o[f"{a}-{b}|{mt}"]
    OUT[f"A|{banda}"] = o
holm(famA)
for banda in ("todo", "sn>2.75", "sn<0.5"):
    o = OUT[f"A|{banda}"]; print(f"\n[modo A, {banda}] n = {o['n']} ({o['n_pub']} publicaciones)")
    for k in ("acotada", "cuadratica", "leps2_ref"):
        r = o[k]; print(f"  {k:11s} CRPS {r['crps']:.4f} cob80 {r['cob80']:.3f} bajoP10 {r['bajo10']:.3f} z̄ {r['z_medio']:+.2f} sd(z) {r['sd_z']:.2f} PIT {r['pit']}")
    for k, v in o.items():
        if "|" in k:
            print(f"  Δ {k:28s} {v['media']:+.4f} [{v['ic95'][0]:+.4f}, {v['ic95'][1]:+.4f}]  a mejor en {v['pubs_a_mejor']}/{v['n_pub']}  sign-flip p {v['p_signflip']:.3f}  Holm {v['p_holm']:.3f}")
B = pd.read_csv(AQ / "lepsp_cv4_B.csv"); ref = B[B.variante == "nivel"].reset_index(drop=True); rr = met(ref.y.values, ref.mu.values, ref.sd.values)
famB = {}
for v in ["nivel", "sitio", "descarte", "conjunta", "previa", "ingenuo_m090", "ingenuo_mtr"]:
    D = B[B.variante == v].reset_index(drop=True); r = met(D.y.values, D.mu.values, D.sd.values); o = resumen(r)
    if v != "nivel":
        o["vs_nivel"] = comparar(r["crps"] - rr["crps"], D.pub.values); famB[v] = o["vs_nivel"]
    OUT[f"B|{v}"] = o
holm(famB)
print(f"\n[modo B] {len(ref)} ensayos, {ref.Set.nunique()} sets, {ref.pub.nunique()} publicaciones")
for v in ["nivel", "sitio", "descarte", "conjunta", "previa", "ingenuo_m090", "ingenuo_mtr"]:
    o = OUT[f"B|{v}"]; ex = ""
    if "vs_nivel" in o:
        c = o["vs_nivel"]; ex = f"  Δ vs nivel {c['media']:+.4f} [{c['ic95'][0]:+.4f}, {c['ic95'][1]:+.4f}]  nivel mejor en {c['n_pub'] - c['pubs_a_mejor']}/{c['n_pub']}  p {c['p_signflip']:.3f} Holm {c['p_holm']:.3f}"
    print(f"  {v:13s} CRPS {o['crps']:.4f} cob80 {o['cob80']:.3f} bajoP10 {o['bajo10']:.3f} z̄ {o['z_medio']:+.2f} sd(z) {o['sd_z']:.2f} PIT {o['pit']}{ex}")
OUT["B|conflicto_frac"] = float((ref.groupby("Set").pval.first() < 0.05).mean())
OUT["A|phi_pliegues"] = A.groupby("pub").phi_cs.first().value_counts().to_dict(); OUT["A|zeta_pliegues"] = A.groupby("pub").zeta.first().value_counts().to_dict()
print("conflicto (modo B):", round(OUT["B|conflicto_frac"], 3), "| φ′∞ por pliegue:", OUT["A|phi_pliegues"], "| ζ0:", OUT["A|zeta_pliegues"])
json.dump(OUT, open(AQ / "lepsp_cv4_metricas.json", "w", encoding="utf-8"), indent=1, default=float)
