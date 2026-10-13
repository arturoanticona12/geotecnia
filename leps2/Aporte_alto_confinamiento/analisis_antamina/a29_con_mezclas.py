"""Pregunta de WA (2026-10-12): ¿por qué no entran las dos mezclas en el ajuste? Con la opción B (desmonte como un solo material,
todos los ensayos con igual peso) ya no hay razón para excluirlas. Este script compara la curva sin y con las mezclas (m mundial
y P10/P90), con bootstrap por sets, y su posición frente a las cotas y a los ensayos altos."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from modelos import sigma1, tau_leps2  # noqa: E402
OM, EB, S0 = 20.0, 0.45, 1.013
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
d["set"] = d.fuente_id + "|" + d.set_id.astype(str); d["e"] = d.e0_adoptado; d["tx"] = d.tipo == "TX"
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]
C2 = json.load(open(AQ / "a12_leps2_ponderada.json", encoding="utf-8"))["curvas"]


def resid(g, pe0, m):
    e = g.e.values; tx = g.tx.values; r = np.empty(len(g))
    if tx.any():
        s3 = g.s3.values[tx]; r[tx] = np.log(sigma1(tau_leps2, s3, pe0 - OM * e[tx], m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
    if (~tx).any():
        r[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], pe0 - OM * e[~tx], m)) - np.log(g.tau_ds.values[~tx]))
    return r


aj = lambda g, m: float(least_squares(lambda p: resid(g, p[0], m), [49], bounds=([30], [70])).x[0])
phis = lambda s, pe0, m: np.degrees(np.arctan(np.tan(np.radians(pe0 - OM * EB)) * (s / S0) ** (m - 1)))
rng = np.random.default_rng(12); out = {}
for nm, g in (("sin mezclas (actual)", d[d.litologia != "Mezcla"]), ("con mezclas", d)):
    sets = g.set.unique()
    for k in ("Curva propuesta (mediana mundial)", "Mundial P10", "Mundial P90"):
        m = C2[k]["m"]; pe0 = aj(g, m)
        b = [aj(pd.concat([g[g.set == s] for s in rng.choice(sets, len(sets))]), m) for _ in range(300)] if k.startswith("Curva") else []
        out[f"{nm} | {k}"] = dict(n=len(g), sets=len(sets), m=m, pe0=pe0, phi1=pe0 - OM * EB,
                                 b90=[float(np.percentile(b, 5)), float(np.percentile(b, 95))] if b else None,
                                 phis={s: float(phis(s, pe0, m)) for s in (0.3, 1, 4.6, 10, 15)})
        o = out[f"{nm} | {k}"]
        print(f"{nm:22s} {k:35s} n {o['n']} sets {o['sets']} | φ′e0 {pe0:.2f} φ′1 {o['phi1']:.2f}" + (f" (90 %: {o['b90'][0]:.2f}–{o['b90'][1]:.2f})" if b else "")
              + " | φ′s " + " ".join(f"{s}:{v:.1f}" for s, v in o["phis"].items()))
json.dump(out, open(AQ / "a29_con_mezclas.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
