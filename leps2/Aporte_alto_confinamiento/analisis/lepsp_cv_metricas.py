"""Leps-P: métricas de la validación fuera de muestra con IC 95 % por bootstrap de publicaciones completas."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent
A = pd.read_csv(AQUI / "lepsp_cv_A.csv"); B = pd.read_csv(AQUI / "lepsp_cv_B.csv")
X1 = np.log(2.75 / 1.013)
RNG = np.random.default_rng(7); NB = 2000


def crps(mu, sd, y):
    z = (y - mu) / sd
    return sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))


def pinball(mu, sd, y, q=0.10):
    p = mu + norm.ppf(q) * sd; u = y - p
    return np.where(u >= 0, q * u, (q - 1) * u)


def met(df, mu="mu", sd="sd"):
    z = (df.y - df[mu]) / df[sd]
    return dict(n=len(df), cob80=np.mean(np.abs(z) <= 1.2816), bajo10=np.mean(z < -1.2816), sdz=np.std(z),
                ancho80=np.mean(2 * 1.2816 * df[sd]), crps=np.mean(crps(df[mu], df[sd], df.y)), pin10=np.mean(pinball(df[mu], df[sd], df.y)))


def boot(df, f, grupo="pub"):
    g = df[grupo].unique(); idx = {k: v.values for k, v in df.groupby(grupo).groups.items()}; vals = []
    for _ in range(NB):
        s = RNG.choice(g, len(g)); ii = np.concatenate([idx[k] for k in s]); vals.append(f(df.loc[ii]))
    return np.percentile(vals, [2.5, 97.5])


out = {}
fmt = lambda v, ci: f"{v:.3f} [{ci[0]:.3f}, {ci[1]:.3f}]"
for (agr, esp), d in A.groupby(["agrup", "esp"]):
    d = d.reset_index(drop=True)
    for rango, dd in [("todo", d), ("σ′n>2.75", d[d.x >= X1].reset_index(drop=True))]:
        m = met(dd); m0 = met(dd, "mu0", "sd0")
        ci = {k: boot(dd, lambda q, k=k: met(q)[k], "grupo") for k in ("cob80", "bajo10", "crps", "pin10")}
        dcrps = boot(dd, lambda q: met(q, "mu0", "sd0")["crps"] - met(q)["crps"], "grupo")
        dpin = boot(dd, lambda q: met(q, "mu0", "sd0")["pin10"] - met(q)["pin10"], "grupo")
        clave = f"{agr}|{esp}|{rango}"
        out[clave] = dict(m=m, m0=m0, ci={k: list(v) for k, v in ci.items()}, dcrps=[m0["crps"] - m["crps"], *dcrps], dpin=[m0["pin10"] - m["pin10"], *dpin])
        print(f"{agr:13s} {esp} {rango:9s} n={m['n']:3d} | cob80 {fmt(m['cob80'], ci['cob80'])} | bajoP10 {fmt(m['bajo10'], ci['bajo10'])} | sd(z) {m['sdz']:.2f}"
              f" | CRPS {m['crps']:.4f} (ref {m0['crps']:.4f}; Δ {m0['crps']-m['crps']:+.4f} [{dcrps[0]:+.4f},{dcrps[1]:+.4f}])"
              f" | pinball10 Δ {m0['pin10']-m['pin10']:+.4f} [{dpin[0]:+.4f},{dpin[1]:+.4f}] | ref cob80 {m0['cob80']:.2f} bajo10 {m0['bajo10']:.2f}")
# PIT por rango (M0, LOPO)
d = A[(A.agrup == "pub") & (A.esp == "M0")]
for nm, dd in [("todo", d), ("σ′n>2.75", d[d.x >= X1])]:
    pit = norm.cdf((dd.y - dd.mu) / dd.sd); h = np.histogram(pit, bins=5, range=(0, 1))[0] / len(pit)
    print(f"PIT M0 {nm}: {np.round(h, 3)}"); out[f"PIT|{nm}"] = h.tolist()
print("\nMODO B (mismos ensayos: sin sitio → con sitio)")
for (esp, modo), b in B.groupby(["esp", "modo"]):
    b = b.reset_index(drop=True); mb = met(b); ma = met(b, "muA", "sdA")
    dc = boot(b, lambda q: met(q, "muA", "sdA")["crps"] - met(q)["crps"])
    print(f"{esp} {modo:24s} n={mb['n']} sets={b.Set.nunique()} conflicto={b.groupby('Set').conflicto.first().mean():.0%} | sin sitio: cob80 {ma['cob80']:.2f} bajo10 {ma['bajo10']:.2f} ancho {ma['ancho80']:.3f} CRPS {ma['crps']:.4f}"
          f" | con sitio: cob80 {mb['cob80']:.2f} bajo10 {mb['bajo10']:.2f} sd(z) {mb['sdz']:.2f} ancho {mb['ancho80']:.3f} CRPS {mb['crps']:.4f} | ΔCRPS {ma['crps']-mb['crps']:+.4f} [{dc[0]:+.4f},{dc[1]:+.4f}]")
    out[f"B|{esp}|{modo}"] = dict(sitio=mb, sin=ma, dcrps=[ma["crps"] - mb["crps"], *dc], sets=int(b.Set.nunique()), conflicto=float(b.groupby('Set').conflicto.first().mean()))
json.dump(out, open(AQUI / "lepsp_cv_metricas.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=float)
