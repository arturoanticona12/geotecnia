"""Métricas de la validación de la ronda 3 (preregistro en PLAN_RONDA3.md).
Modo A: acotada (lepsp_cv3_A) frente a cuadrática M2 y Leps 2.0 con dispersión constante (lepsp_cv_A, mismos pliegues).
Modo B: variantes de lepsp_cv3_B frente a la regla principal (nivel). Bootstrap pareado por publicación (5000) y prueba
de Wilcoxon sobre las medias por publicación. Escribe lepsp_cv3_metricas.json."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm, wilcoxon
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; S0 = 1.013; Z90 = norm.ppf(0.9); rng = np.random.default_rng(0)


def met(y, mu, sd):
    z = (y - mu) / sd
    crps = sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))
    q10 = mu - Z90 * sd; pin = np.where(y < q10, 0.9 * (q10 - y), 0.1 * (y - q10))
    return dict(crps=np.asarray(crps), cob80=np.asarray(np.abs(z) < Z90, float), bajo10=np.asarray(z < -Z90, float), pin10=np.asarray(pin), z=np.asarray(z))


def resumen(r):
    z = r["z"]
    return dict(crps=float(r["crps"].mean()), cob80=float(r["cob80"].mean()), bajo10=float(r["bajo10"].mean()), pin10=float(r["pin10"].mean()),
                z_medio=float(z.mean()), sd_z=float(z.std()), pit=np.histogram(norm.cdf(z), bins=5, range=(0, 1))[0].tolist())


def comparar(dif, pubs, n=5000):
    up = np.unique(pubs); idx = [np.where(pubs == p)[0] for p in up]
    bs = [dif[np.concatenate([idx[i] for i in rng.integers(0, len(up), len(up))])].mean() for _ in range(n)]
    pm = np.array([dif[i].mean() for i in idx])
    try:
        pw = float(wilcoxon(pm).pvalue)
    except ValueError:
        pw = float("nan")
    return dict(media=float(dif.mean()), ic95=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], n_pub=len(up),
                pubs_mejora=int((pm < 0).sum()), wilcoxon_p=pw)


OUT = {}
A = pd.read_csv(AQ / "lepsp_cv3_A.csv"); C = pd.read_csv(AQ / "lepsp_cv_A.csv"); C = C[(C.agrup == "pub") & (C.esp == "M2")]
M = A.merge(C[["pub", "Set", "x", "y", "mu", "sd", "mu0", "sd0"]], on=["pub", "Set", "x", "y"], suffixes=("", "_q"))
assert len(M) == len(A)
for banda, sel in (("todo", M.x > -99), ("sn>2.75", S0 * np.exp(M.x) > 2.75), ("sn<0.5", S0 * np.exp(M.x) < 0.5)):
    D = M[sel.values]; R = {"acotada": met(D.y.values, D.mu.values, D.sd.values), "cuadratica": met(D.y.values, D.mu_q.values, D.sd_q.values),
                            "leps2_ref": met(D.y.values, D.mu0.values, D.sd0.values)}
    o = {k: resumen(v) for k, v in R.items()}; o["n"] = len(D); o["n_pub"] = int(D.pub.nunique())
    for a, b in (("acotada", "cuadratica"), ("acotada", "leps2_ref")):
        for mt in ("crps", "pin10"):
            o[f"{a}-{b}|{mt}"] = comparar(R[a][mt] - R[b][mt], D.pub.values)
    OUT[f"A|{banda}"] = o
    print(f"\n[modo A, {banda}] n = {len(D)} ({o['n_pub']} publicaciones)")
    for k in R:
        r = o[k]; print(f"  {k:11s} CRPS {r['crps']:.4f} cob80 {r['cob80']:.3f} bajoP10 {r['bajo10']:.3f} z̄ {r['z_medio']:+.2f} sd(z) {r['sd_z']:.2f} PIT {r['pit']}")
    for k, v in o.items():
        if "|" in k:
            print(f"  Δ {k:28s} {v['media']:+.4f} [{v['ic95'][0]:+.4f}, {v['ic95'][1]:+.4f}]  mejora en {v['pubs_mejora']}/{v['n_pub']}  Wilcoxon p = {v['wilcoxon_p']:.3f}")
B = pd.read_csv(AQ / "lepsp_cv3_B.csv"); ref = B[B.variante == "nivel"].reset_index(drop=True)
rr = met(ref.y.values, ref.mu.values, ref.sd.values)
print(f"\n[modo B] n = {len(ref)} ensayos, {ref.Set.nunique()} sets, {ref.pub.nunique()} publicaciones; m del entrenamiento (mediana) {B.m_tr.median():.3f}")
for v in ["nivel", "previa", "conjunta", "procedimiento", "ingenuo_m090", "ingenuo_mtr"]:
    D = B[B.variante == v].reset_index(drop=True); r = met(D.y.values, D.mu.values, D.sd.values); o = resumen(r)
    if v != "nivel":
        o["vs_nivel"] = comparar(r["crps"] - rr["crps"], D.pub.values)
    OUT[f"B|{v}"] = o
    extra = f"  Δ vs nivel {o['vs_nivel']['media']:+.4f} [{o['vs_nivel']['ic95'][0]:+.4f}, {o['vs_nivel']['ic95'][1]:+.4f}] Wilcoxon p {o['vs_nivel']['wilcoxon_p']:.3f}" if v != "nivel" else ""
    print(f"  {v:14s} CRPS {o['crps']:.4f} cob80 {o['cob80']:.3f} bajoP10 {o['bajo10']:.3f} z̄ {o['z_medio']:+.2f} sd(z) {o['sd_z']:.2f}{extra}")
OUT["B|conflicto_frac"] = float((ref.groupby("Set").pval.first() < 0.05).mean())
OUT["A|phi_cs_pliegues"] = A.groupby("pub").phi_cs.first().value_counts().to_dict(); OUT["A|zeta_pliegues"] = A.groupby("pub").zeta.first().value_counts().to_dict()
print("fracción de sets en conflicto (modo B):", round(OUT["B|conflicto_frac"], 3), "| φcs por pliegue:", OUT["A|phi_cs_pliegues"])
json.dump(OUT, open(AQ / "lepsp_cv3_metricas.json", "w", encoding="utf-8"), indent=1, default=float)
