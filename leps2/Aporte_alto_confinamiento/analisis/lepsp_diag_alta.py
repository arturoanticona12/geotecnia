"""Diagnóstico mecánico a alta tensión (ronda 4): deformación volumétrica en la falla (evol) y rotura (Bg de Marsal)
frente a σ′n en la base de calibración, y relación de los residuos de la forma acotada (ajuste con todos los datos) con
Bg sobre 2.75 MPa. Bg es un resultado del ensayo: se usa como diagnóstico, no como covariable predictiva.
Escribe lepsp_diag_alta.json y figuras/lepsp4/FigS2_volumetric_breakage.(png|tif)."""
import sys, json, math
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import spearmanr
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; OUT = AQ.parent / "figuras" / "lepsp5"; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(AQ))
from lepsp_acotada2 import d, media2  # noqa: E402

P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8"))["formas"]["acotada"]
N_BG_MAL = int((d.Bg > 100).sum())                  # Bg de Marsal ≤ 100 % por definición: valores mayores son errores de la base
d.loc[d.Bg > 100, "Bg"] = np.nan
f, _, _ = media2(np.array(P["beta"]), d, math.tan(math.radians(P["phi_cs"])), P["zeta"]); d["res"] = d.y.values - f
bandas = [(0, 0.5), (0.5, 1.5), (1.5, 3.0), (3.0, 99)]; out = {"bandas": [], "bg_excluidos_mayor_100": N_BG_MAL}
for a, b in bandas:
    g = d[(d.sn >= a) & (d.sn < b)]; ev = g.evol.dropna(); bg = g.Bg.dropna()
    out["bandas"].append(dict(sn=[a, b], n_evol=len(ev), evol_mediana=float(ev.median()) if len(ev) else None, frac_contractiva=float((ev < 0).mean()) if len(ev) else None,
                              n_bg=len(bg), bg_mediana=float(bg.median()) if len(bg) else None))
    print(f"σ′n {a}–{b} MPa: evol n={len(ev)} mediana {ev.median():+.2f} (fracción < 0: {(ev < 0).mean():.2f}); Bg n={len(bg)} mediana {bg.median():.1f}")
# ¿disminuye con la tensión la dispersión entre sets? DE de las medias por set de los residuos (envolvente poblacional)
out["sd_entre_sets"] = {}
for a, b in ((0, 1.0), (1.0, 3.0), (3.0, 99)):
    g = d[(d.sn >= a) & (d.sn < b)]; ms = g.groupby("Set").res.mean(); ns = g.groupby("Set").res.size()
    out["sd_entre_sets"][f"{a}-{b}"] = dict(n_sets=int(len(ms)), n_pub=int(g.pub.nunique()), sd=float(ms.std()), sd_ponderada=float(np.sqrt(np.average((ms - np.average(ms, weights=ns)) ** 2, weights=ns))))
    print(f"σ′n {a}–{b} MPa: {len(ms)} sets ({g.pub.nunique()} publicaciones), DE entre sets del residuo medio {ms.std():.3f}")
h = d[(d.sn > 2.75) & d.Bg.notna()]; rho, p = spearmanr(h.Bg, h.res)
out["res_vs_bg_alta"] = dict(n=len(h), spearman=float(rho), p=float(p), n_pub=int(h.pub.nunique()))
print(f"residuo vs Bg sobre 2.75 MPa: n={len(h)} ({h.pub.nunique()} publicaciones), Spearman {rho:+.2f} (p = {p:.3f})")
hs = d[d.sn > 5]; out["phis_sobre_5"] = [float(np.percentile(np.degrees(np.arctan(hs.tau / hs.sn)), q)) for q in (5, 50, 95)]; out["n_sobre_5"] = len(hs)
print("φ′s sobre 5 MPa (P5/P50/P95):", np.round(out["phis_sobre_5"], 1), "n =", len(hs))
json.dump(out, open(AQ / "lepsp_diag_alta.json", "w", encoding="utf-8"), indent=1)
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#8a8984", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 600, "savefig.bbox": "tight"})
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.0, 2.7))
for ax, col, lab in ((a1, "evol", "Volumetric strain at failure (%)"), (a2, "Bg", "Breakage index, $B_g$ (%)")):
    g = d[d[col].notna()]; ax.plot(g.sn, g[col], "o", ms=3, mfc="white", mec=INK2, mew=0.6, ls="")
    ax.set_xscale("log"); ax.set_xticks([0.1, 0.3, 1, 3, 10]); ax.set_xticklabels(["0.1", "0.3", "1", "3", "10"]); ax.minorticks_off()
    ax.set_xlabel(r"$\sigma'_n$ (MPa)"); ax.set_ylabel(lab); ax.axvspan(2.75, 12, color="#ecebe8", zorder=0)
a1.axhline(0, color=INK, lw=0.8); a1.set_title("(a) Negative: contraction", loc="left", fontsize=8, color=INK); a2.set_title("(b) Particle breakage", loc="left", fontsize=8, color=INK)
fig.savefig(OUT / "FigS2_volumetric_breakage.png"); fig.savefig(OUT / "FigS2_volumetric_breakage.tif", pil_kwargs={"compression": "tiff_lzw"})
