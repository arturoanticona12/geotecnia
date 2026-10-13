"""Fig. 7 del manuscrito Leps-P (ronda 2): FS del botadero de 700 m sobre ladera con capa basal saturada frente a la
permeabilidad de la capa, por velocidad de carga (Slide2, lote 63, Morgenstern–Price). Monocromo (ASCE)."""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; OUT = AQ.parent / "figuras" / "lepsp2"
RES = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados\63-lepsp-presion-poros-capa\fs_por_escenario.json")
INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#8a8984", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
                     "legend.frameon": False, "savefig.dpi": 600, "savefig.bbox": "tight"})
FS = {}
for v in json.load(open(RES, encoding="utf-8")).values():
    FS.update(v["fs"])
KS = (1e-6, 1e-7, 1e-8, 1e-9); RS = (25, 100, 300, 600)
EST = {25: (INK, "o", "-"), 100: (INK, "s", "--"), 300: (INK2, "^", "-."), 600: (INK2, "D", ":")}
fig, axs = plt.subplots(1, 2, figsize=(7.0, 2.8), sharey=True)
tabla = {}
for ax, esc, tit in zip(axs, ("P50", "P05"), ("(a) Median envelope", "(b) 5th-percentile envelope")):
    for R in RS:
        f = [FS[f"R{R} k{k:.0e} / {esc}"]["gle/morgenstern-price"] for k in KS]; tabla[(esc, R)] = f
        c, mk, ls = EST[R]
        ax.plot(KS, f, color=c, marker=mk, ls=ls, lw=1.2, ms=4.5, mfc="white", mew=1.0, label=f"{R} m/year")
    for y, t in ((1.0, "FS = 1.0"), (1.3, "FS = 1.3")):
        ax.axhline(y, color=MUTED, lw=0.8, ls=(0, (4, 2)))
        ax.text(1.2e-6, y - 0.02, t, color=INK2, fontsize=6.5, ha="left", va="top")
    ax.set_xscale("log"); ax.set_xlim(1.3e-6, 0.7e-9); ax.set_xticks(KS); ax.set_xticklabels([r"$10^{-6}$", r"$10^{-7}$", r"$10^{-8}$", r"$10^{-9}$"])
    ax.minorticks_off(); ax.set_xlabel("Permeability of the basal layer, $k$ (m/s)"); ax.set_title(tit, fontsize=8, color=INK, loc="left")
axs[0].set_ylabel("Factor of safety (Morgenstern–Price)")
axs[0].set_ylim(bottom=0)
h, l = axs[0].get_legend_handles_labels()
fig.legend(h, l, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=4, fontsize=7, title="Loading rate of the dump over the layer", title_fontsize=7)
fig.savefig(OUT / "Fig07_pore_pressure.png"); fig.savefig(OUT / "Fig07_pore_pressure.tif", pil_kwargs={"compression": "tiff_lzw"})
for (esc, R), f in tabla.items():
    print(esc, R, " ".join(f"{v:.3f}" for v in f))
