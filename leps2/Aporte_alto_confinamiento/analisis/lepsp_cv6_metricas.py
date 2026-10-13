"""Métricas de la validación de la ronda 6 (lepsp_cv6_{A,B,S}.csv): clúster = programa de laboratorio (auditoría D1).
- Bandas fijadas de antemano: todo, σ′n ≥ 2 MPa (como el modo B; revisor D2), < 0.5 MPa; 2.75 y 3 MPa como sensibilidad.
- Ensayos censurados excluidos de la puntuación (su y es una cota inferior); sensibilidad incluyéndolos.
- Pruebas exactas de signo invertido sobre las medias por laboratorio (sin ponderar y ponderadas por número de ensayos,
  revisor E12), Holm por modo; bootstrap por laboratorio solo descriptivo.
- Cuantil de diseño: fracción bajo P05 y pérdida pinball en P05 (revisor E3); validación a nivel de set de la
  envolvente media (excedencia del P05, z̄, DE de z) y distribución de los p del chequeo de conflicto (KS frente a la
  uniforme; revisor E6). Escribe lepsp_cv6_metricas.json."""
import sys, json, itertools
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm, kstest
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; S0 = 1.013; Z90 = norm.ppf(0.9); Z95 = norm.ppf(0.95); rng = np.random.default_rng(0)
FORMAS = ["acotada", "cuadratica", "potencia", "leps2_jer", "leps2_ref"]


def met(y, mu, sd):
    z = (y - mu) / sd; crps = sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))
    q10 = mu - Z90 * sd; q05 = mu - Z95 * sd
    pin10 = np.where(y < q10, 0.9 * (q10 - y), 0.1 * (y - q10)); pin05 = np.where(y < q05, 0.95 * (q05 - y), 0.05 * (y - q05))
    return dict(crps=crps, cob80=(np.abs(z) < Z90).astype(float), bajo10=(z < -Z90).astype(float), bajo05=(z < -Z95).astype(float),
                pin10=pin10, pin05=pin05, z=z)


def resumen(r):
    z = r["z"]
    return dict(n=len(z), crps=float(r["crps"].mean()), cob80=float(r["cob80"].mean()), bajo10=float(r["bajo10"].mean()), bajo05=float(r["bajo05"].mean()),
                pin10=float(r["pin10"].mean()), pin05=float(r["pin05"].mean()), z_medio=float(z.mean()), sd_z=float(z.std()))


def signflip(pm, w=None):
    n = len(pm); w = np.ones(n) if w is None else w / w.mean(); obs = abs(np.mean(w * pm))
    sig = np.array(list(itertools.product((-1, 1), repeat=n))) if n <= 20 else rng.choice((-1, 1), size=(200000, n))
    return float(np.mean(np.abs((sig * (w * pm)).mean(1)) >= obs - 1e-15))


def comparar(dif, cl):
    up = np.unique(cl); idx = [np.where(cl == c)[0] for c in up]; pm = np.array([dif[i].mean() for i in idx]); nn = np.array([len(i) for i in idx], float)
    bs = [dif[np.concatenate([idx[i] for i in rng.integers(0, len(up), len(up))])].mean() for _ in range(4000)]
    return dict(media=float(dif.mean()), ic95_boot=[float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))], n_lab=len(up),
                labs_a_mejor=int((pm < 0).sum()), p_signflip=signflip(pm), p_signflip_pond=signflip(pm, nn))


def holm(fam, clave="p_signflip"):
    ks = sorted(fam, key=lambda k: fam[k][clave]); m = len(ks); acc = 0
    for i, k in enumerate(ks):
        acc = max(acc, min(1.0, (m - i) * fam[k][clave])); fam[k][clave + "_holm"] = acc


OUT = {}
A = pd.read_csv(AQ / "lepsp_cv6_A.csv"); A["sn"] = S0 * np.exp(A.x)
A = A.rename(columns={"mu0": "mu_leps2_ref", "sd0": "sd_leps2_ref"})
famA = {}
for incl in (False, True):
    D0 = A if incl else A[~A.cens]
    for banda, sel in (("todo", D0.sn > 0), ("sn>=2", D0.sn >= 2), ("sn<0.5", D0.sn < 0.5), ("sn>2.75", D0.sn > 2.75), ("sn>3", D0.sn > 3)):
        D = D0[sel.values]; R = {f: met(D.y.values, D[f"mu_{f}"].values, D[f"sd_{f}"].values) for f in FORMAS}
        o = {f: resumen(R[f]) for f in FORMAS}; o.update(n=len(D), n_lab=int(D.lab.nunique()), n_pub=int(D.pub.nunique()))
        for b in FORMAS[1:]:
            for mt in ("crps", "pin10", "pin05"):
                o[f"acotada-{b}|{mt}"] = comparar(R["acotada"][mt] - R[b][mt], D.lab.values)
                if not incl and banda in ("todo", "sn>=2", "sn<0.5"):
                    famA[(banda, b, mt)] = o[f"acotada-{b}|{mt}"]
        OUT[f"A|{banda}" + ("|con_censurados" if incl else "")] = o
holm(famA); holm(famA, "p_signflip_pond")
for banda in ("todo", "sn>=2", "sn<0.5"):
    o = OUT[f"A|{banda}"]; print(f"\n[modo A, {banda}] n = {o['n']} ({o['n_lab']} laboratorios, {o['n_pub']} publicaciones)")
    for f in FORMAS:
        r = o[f]; print(f"  {f:11s} CRPS {r['crps']:.4f} cob80 {r['cob80']:.3f} bajoP10 {r['bajo10']:.3f} bajoP05 {r['bajo05']:.3f} z̄ {r['z_medio']:+.2f} sd(z) {r['sd_z']:.2f}")
    for k, v in o.items():
        if "|" in k and "crps" in k:
            print(f"  Δ {k:30s} {v['media']:+.4f}  mejor en {v['labs_a_mejor']}/{v['n_lab']} lab.  p {v['p_signflip']:.3f} (Holm {v.get('p_signflip_holm', float('nan')):.3f}); pond. {v['p_signflip_pond']:.3f}")
# ---- modo B
B = pd.read_csv(AQ / "lepsp_cv6_B.csv"); famB = {}
if len(B):
    ref = B[B.variante == "nivel"].reset_index(drop=True); rr = met(ref.y.values, ref.mu.values, ref.sd.values)
    for v in ["nivel", "sitio", "descarte", "conjunta", "previa", "ingenuo_m090", "ingenuo_mtr"]:
        D = B[B.variante == v].reset_index(drop=True); r = met(D.y.values, D.mu.values, D.sd.values); o = resumen(r)
        if v != "nivel":
            o["vs_nivel"] = comparar(r["crps"] - rr["crps"], D.lab.values); famB[v] = o["vs_nivel"]
        OUT[f"B|{v}"] = o
    holm(famB); holm(famB, "p_signflip_pond")
    OUT["B|n"] = dict(ensayos=len(ref), sets=int(ref.Set.nunique()), labs=int(ref.lab.nunique()), pubs=int(ref.pub.nunique()))
    print(f"\n[modo B] {OUT['B|n']}")
    for v in ["nivel", "sitio", "descarte", "conjunta", "previa", "ingenuo_m090", "ingenuo_mtr"]:
        o = OUT[f"B|{v}"]; print(f"  {v:13s} CRPS {o['crps']:.4f} cob80 {o['cob80']:.3f} bajoP05 {o['bajo05']:.3f} sd(z) {o['sd_z']:.2f}"
                                  + (f"  Δ vs nivel {o['vs_nivel']['media']:+.4f} p {o['vs_nivel']['p_signflip']:.3f} Holm {o['vs_nivel']['p_signflip_holm']:.3f}" if "vs_nivel" in o else ""))
# ---- nivel de set: envolvente media y chequeo de conflicto
S = pd.read_csv(AQ / "lepsp_cv6_S.csv")
OUT["S"] = {f: dict(n_sets=int(S[f"z_{f}"].notna().sum()), bajo05=float((S[f"z_{f}"] < -Z95).mean()), z_medio=float(S[f"z_{f}"].mean()), sd_z=float(S[f"z_{f}"].std()))
            for f in ("acotada", "cuadratica", "potencia", "leps2_jer")}
ks = kstest(S.pval.values, "uniform")
OUT["S"]["conflicto"] = dict(n=int(len(S)), frac_p05=float((S.pval < 0.05).mean()), ks_p=float(ks.pvalue),
                             hist=np.histogram(S.pval, bins=10, range=(0, 1))[0].tolist())
print("\n[nivel de set]", json.dumps(OUT["S"], ensure_ascii=False))
OUT["phi_pliegues"] = A.groupby("lab").phi_cs.first().value_counts().to_dict(); OUT["zeta_pliegues"] = A.groupby("lab").zeta.first().value_counts().to_dict()
json.dump(OUT, open(AQ / "lepsp_cv6_metricas.json", "w", encoding="utf-8"), indent=1, default=float)
print("escrito lepsp_cv6_metricas.json")
