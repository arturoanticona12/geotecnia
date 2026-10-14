"""Compara fuera de muestra (LOPO, modo A) la envolvente acotada por el estado crítico, el modelo cuadrático M2 y la
referencia Leps 2.0 (m = 0.9, dispersión constante). Mismos ensayos y pliegues. Bootstrap pareado por publicación.
Escribe lepsp_acotada_metricas.json."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; S0 = 1.013
A = pd.read_csv(AQ / "lepsp_acotada_A.csv")
C = pd.read_csv(AQ / "lepsp_cv_A.csv"); C = C[(C.agrup == "pub") & (C.esp == "M2")]
M = A.merge(C[["pub", "Set", "x", "y", "mu", "sd", "mu0", "sd0"]], on=["pub", "Set", "x", "y"], suffixes=("_b", "_q"))
assert len(M) == len(A), (len(M), len(A))
Z90 = norm.ppf(0.9)


def met(y, mu, sd):
    z = (y - mu) / sd
    crps = sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))
    q10 = mu - Z90 * sd; pin = np.where(y < q10, 0.9 * (q10 - y), 0.1 * (y - q10))
    return dict(crps=crps, cob80=(np.abs(z) < Z90).astype(float), bajo10=(z < -Z90).astype(float), pin10=pin, z=z, pit=norm.cdf(z))


MOD = {"acotada": ("mu_b", "sd_b"), "cuadratica": ("mu_q", "sd_q"), "leps2_ref": ("mu0", "sd0")}
rng = np.random.default_rng(0); out = {}
for banda, sel in (("todo", np.ones(len(M), bool)), ("sn>2.75", (S0 * np.exp(M.x) > 2.75).values), ("sn<0.5", (S0 * np.exp(M.x) < 0.5).values)):
    D = M[sel].reset_index(drop=True); R = {k: met(D.y.values, D[a].values, D[b].values) for k, (a, b) in MOD.items()}
    pubs = D.pub.values; up = np.unique(pubs); idx = [np.where(pubs == p)[0] for p in up]
    res = dict(n=len(D), n_pub=len(up))
    for k, r in R.items():
        res[k] = dict(crps=float(r["crps"].mean()), cob80=float(r["cob80"].mean()), bajo10=float(r["bajo10"].mean()), pin10=float(r["pin10"].mean()),
                      z_medio=float(r["z"].mean()), sd_z=float(r["z"].std()), pit_quintiles=np.histogram(r["pit"], bins=5, range=(0, 1))[0].tolist())
    for a, b in (("acotada", "cuadratica"), ("acotada", "leps2_ref"), ("cuadratica", "leps2_ref")):
        for mt in ("crps", "pin10"):
            dif = R[a][mt] - R[b][mt]; bs = []
            for _ in range(4000):
                s = np.concatenate([idx[i] for i in rng.integers(0, len(up), len(up))]); bs.append(dif[s].mean())
            res[f"{a}-{b}|{mt}"] = [float(dif.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]
    out[banda] = res
    print(f"\n[{banda}] n = {res['n']} ({res['n_pub']} publicaciones)")
    for k in MOD:
        r = res[k]; print(f"  {k:11s} CRPS {r['crps']:.4f}  cob80 {r['cob80']:.3f}  bajo P10 {r['bajo10']:.3f}  pin10 {r['pin10']:.4f}  z̄ {r['z_medio']:+.2f}  sd(z) {r['sd_z']:.2f}  PIT {r['pit_quintiles']}")
    for k, v in res.items():
        if "|" in k:
            print(f"  Δ {k:32s} {v[0]:+.4f} [{v[1]:+.4f}, {v[2]:+.4f}]")
out["phi_cs_por_pliegue"] = A.groupby("pub").phi_cs.first().value_counts().to_dict()
out["lam_por_pliegue"] = A.groupby("pub").lam.first().value_counts().to_dict()
print("\nφcs elegido por pliegue:", out["phi_cs_por_pliegue"], "| λ:", out["lam_por_pliegue"])
json.dump(out, open(AQ / "lepsp_acotada_metricas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
