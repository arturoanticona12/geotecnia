"""Figures for the Leps-P manuscript (English, ASCE: readable in black and white, 600 dpi, no titles drawn)."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import norm
warnings.filterwarnings("ignore")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent; OUT = RAIZ / "figuras" / "lepsp"; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(RAIZ / "leps3"))
import lepsp as L  # noqa: E402
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar  # noqa: E402

INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7"
C1, C2, C3, C4 = "#2a78d6", "#eb6834", "#1baf7a", "#8e5cc7"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False,
                     "savefig.dpi": 600, "savefig.bbox": "tight"})
W1, W2 = 3.5, 7.0          # ancho de columna y de página (in)


def xlog(ax, t=(0.1, 0.3, 1, 3, 10)):
    ax.set_xscale("log"); ax.set_xticks(t); ax.set_xticklabels([f"{v:g}" for v in t])


def guardar(fig, nm):
    fig.savefig(OUT / f"{nm}.png"); fig.savefig(OUT / f"{nm}.tif", pil_kwargs={"compression": "tiff_lzw"}); plt.close(fig)


d = preparar(load_db(), CLASE)
SNMAX = d.sn.max()
# ---------- Fig. 1: stress coverage
EST = json.load(open(AQUI / "lepsp_estabilidad.json", encoding="utf-8"))
fig, ax = plt.subplots(figsize=(W2, 2.6))
ax.hist(d.sn, bins=np.logspace(np.log10(0.05), np.log10(40), 34), color=MUTED, edgecolor="white", lw=0.8, label=f"Calibration tests (n = {len(d)})")
for v, t, ls in [(EST["det"]["700|Desmonte del sitio, P50"]["snmax"], "Max. σ′n on critical surface, 700 m dump on level foundation", ":"),
                 (SNMAX, f"Max. σ′n in calibration database ({SNMAX:.1f} MPa)", "--"), (700 * 0.021, "σv at base of a 700 m dump (14.7 MPa)", "-")]:
    ax.axvline(v, color=INK, lw=1.1, ls=ls, label=t)
xlog(ax, (0.1, 0.3, 1, 3, 10, 30)); ax.set_xlim(0.05, 40); ax.set_xlabel("Effective normal stress on failure plane, σ′n (MPa)"); ax.set_ylabel("Number of tests")
ax.grid(axis="x", visible=False); ax.legend(loc="upper left", fontsize=7)
guardar(fig, "Fig01_stress_coverage")
# ---------- Fig. 2: predictive band of a new material (two forms)
sn = np.logspace(-1, np.log10(15), 120)
fig, ax = plt.subplots(figsize=(W1, 2.8))
for forma, ls, lab in [("x2", "-", "Quadratic form"), ("potencia", "--", "Power form")]:
    mat = L.previa("moderada", 0.45, forma, n=40000); q = L.percentiles(sn, mat, (10, 50, 90))
    if forma == "x2":
        ax.fill_between(sn, q[10], q[90], color=C1, alpha=0.18, lw=0, label="80% interval, quadratic form")
    ax.plot(sn, q[50], color=INK, lw=1.4, ls=ls, label=f"Median, {lab.lower()}")
    ax.plot(sn, q[10], color=INK2, lw=0.8, ls=ls)
ax.axvspan(SNMAX, 15, color="#f0efec", zorder=0); ax.text(10.9, 55, "No data", ha="center", fontsize=7, color=INK2)
xlog(ax); ax.set_xlim(0.1, 15); ax.set_ylim(24, 58); ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Secant friction angle, φ′s (°)")
ax.legend(loc="lower left", fontsize=6.5)
guardar(fig, "Fig02_predictive_band")
# ---------- Fig. 3: out-of-sample calibration (Mode A) by stress range + PIT
A = pd.read_csv(AQUI / "lepsp_cv_A.csv"); A = A[(A.agrup == "pub") & (A.esp == "M2")]
bins = [-np.inf, -1, 0, 1, np.inf]; lab = ["<0.37", "0.37–1.0", "1.0–2.75", ">2.75"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 2.5))
for k, (mu, sd, mk, nm) in enumerate([("mu", "sd", "o", "Leps-P"), ("mu0", "sd0", "s", "Constant dispersion (reference)")]):
    cov, bel = [], []
    for a, b in zip(bins[:-1], bins[1:]):
        dd = A[(A.x >= a) & (A.x < b)]; z = (dd.y - dd[mu]) / dd[sd]; cov.append(100 * np.mean(np.abs(z) <= 1.2816)); bel.append(100 * np.mean(z < -1.2816))
    xs = np.arange(4) + (k - 0.5) * 0.15
    a1.plot(xs, cov, mk, color=INK if k == 0 else MUTED, ms=5, label=nm, mfc="white" if k else INK)
    a2.plot(xs, bel, mk, color=INK if k == 0 else MUTED, ms=5, label=nm, mfc="white" if k else INK)
a1.axhline(80, color=INK2, lw=0.8, ls="--"); a2.axhline(10, color=INK2, lw=0.8, ls="--")
for a_, yl, t in [(a1, (60, 100), "(a) 80% interval coverage (%)"), (a2, (0, 20), "(b) Tests below the 10th percentile (%)")]:
    a_.set_xticks(range(4)); a_.set_xticklabels(lab); a_.set_xlabel("σ′n range (MPa)"); a_.set_ylim(*yl); a_.set_ylabel(t)
a1.legend(loc="lower right", fontsize=7)
guardar(fig, "Fig03_calibration")
# ---------- Fig. 4: site updating (Mode B) — CRPS and width, same 64 tests
B = pd.read_csv(AQUI / "lepsp_cv_B.csv"); B = B[(B.esp == "M2") & (B.modo == "solo_theta_si_conflicto")]
crps = lambda mu, sd, y: sd * ((y - mu) / sd * (2 * norm.cdf((y - mu) / sd) - 1) + 2 * norm.pdf((y - mu) / sd) - 1 / np.sqrt(np.pi))
fig, ax = plt.subplots(figsize=(W1, 2.6))
pa, pb = B.groupby("pub").apply(lambda g: crps(g.muA, g.sdA, g.y).mean()), B.groupby("pub").apply(lambda g: crps(g.mu, g.sd, g.y).mean())
for p in pa.index:
    ax.plot([0, 1], [pa[p], pb[p]], color=MUTED, lw=0.7, marker="o", ms=3)
ax.plot([0, 1], [crps(B.muA, B.sdA, B.y).mean(), crps(B.mu, B.sd, B.y).mean()], color=INK, lw=2, marker="s", ms=6, label="All 64 tests")
ax.set_xticks([0, 1]); ax.set_xticklabels(["Without site tests", "Updated with site tests\n(σ′n ≤ 1.5 MPa)"]); ax.set_xlim(-0.3, 1.3)
ax.set_ylabel("Mean CRPS of ln τ at σ′n ≥ 2 MPa"); ax.legend(loc="upper right", fontsize=7)
guardar(fig, "Fig04_site_updating")
# ---------- Fig. 5: specimen-size effect within materials (forest plot)
E = pd.read_csv(AQUI / "lepsp_escala.csv"); E = E[E.R >= 1.3].sort_values(["similar", "bD"]).reset_index(drop=True)
fig, ax = plt.subplots(figsize=(W1, 3.6))
for i, r in E.iterrows():
    ax.errorbar(r.bD, i, xerr=1.96 * r.se_bD, fmt="o" if r.similar else "s", color=INK if r.similar else MUTED, mfc=INK if r.similar else "white", ms=4, lw=0.8, capsize=2)
ES = json.load(open(AQUI / "lepsp_escala.json"))
ax.axvline(0, color=INK2, lw=0.8); ax.axvline(-0.41 * 0.14, color=INK2, lw=0.8, ls=":")
ax.axvspan(ES["similares"]["b"] - 1.96 * ES["similares"]["se"], ES["similares"]["b"] + 1.96 * ES["similares"]["se"], color=C1, alpha=0.15, lw=0)
ax.set_yticks(range(len(E))); ax.set_yticklabels([f"{p.split('(')[0].strip()} – {m}" for p, m in zip(E.pub, E.material)], fontsize=6)
ax.set_xlabel("βD, change in ln τ per unit ln(Dmax)"); ax.set_xlim(-0.25, 0.25); ax.grid(axis="y", visible=False)
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402
ax.legend(handles=[Line2D([], [], marker="o", color=INK, ls="", ms=4, label="Parallel grading, same density"),
                   Line2D([], [], marker="s", color=MUTED, mfc="white", ls="", ms=4, label="Grading or density changes with Dmax"),
                   Patch(color=C1, alpha=0.15, label="95% CI of mean, parallel grading"),
                   Line2D([], [], color=INK2, ls=":", label="Weibull scaling, κ = 0.41")],
          loc="upper center", bbox_to_anchor=(0.35, -0.12), ncol=2, fontsize=6)
guardar(fig, "Fig05_size_effect")
# ---------- Fig. 6: lithology envelopes at field scale
S = json.load(open(RAIZ / "analisis_antamina" / "lepsp_sitio.json", encoding="utf-8")); SN = np.array(S["sn"])
NOMEN = {"Carbonato metamórfico (mármol)": ("Metamorphic carbonate", "o", "-"), "Hornfels": ("Hornfels", "s", "--"),
         "Intrusivo": ("Intrusive", "^", "-."), "Sedimentaria carbonatada (caliza y margas)": ("Sedimentary carbonate (untested)", "v", ":")}
fig, ax = plt.subplots(figsize=(W1, 2.9))
for k, (nm, mk, ls) in NOMEN.items():
    r = S["litologias"][k]; ax.plot(SN, r["campo_P50"], color=INK, ls=ls, marker=mk, ms=4, lw=1.1, label=f"{nm}, P50")
    ax.plot(SN, r["campo_P10"], color=MUTED, ls=ls, marker=mk, ms=3, lw=0.7, mfc="white")
b = S["botadero"]["Modelo (sistemático común, materiales independientes)"]
ax.fill_between(SN, b["P05"], b["P50"], color=C1, alpha=0.18, lw=0, label="Dump-average envelope, P05–P50")
ax.axvspan(4.3, 15, color="#f0efec", zorder=0); ax.text(8, 49, "No site tests", ha="center", fontsize=6.5, color=INK2)
ax.plot([], [], color=MUTED, marker="o", mfc="white", ms=3, lw=0.7, label="Open symbols: P10")
xlog(ax, (0.5, 1, 3, 10)); ax.set_xlim(0.5, 15); ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("φ′s (°)")
ax.legend(fontsize=6, loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2)
guardar(fig, "Fig06_lithology_envelopes")
# ---------- Fig. 7: factor of safety vs height
fig, ax = plt.subplots(figsize=(W1, 2.7)); Hs = [150, 400, 700]
for nm, lab, mk, ls in [("Desmonte del sitio, P50", "Site waste rock, P50", "o", "-"), ("Desmonte del sitio, P05 (característico)", "Site waste rock, characteristic (P05)", "s", "--"),
                        ("Desmonte del sitio, segregación (litología más débil), P05", "Weakest lithology only, P05", "^", ":"),
                        ("Material genérico moderado e = 0.45, P05 (característico)", "Generic material without tests, P05", "D", "-.")]:
    ax.plot(Hs, [EST["det"][f"{h}|{nm}"]["F"] for h in Hs], color=INK, marker=mk, ls=ls, ms=4, lw=1, label=lab)
ax.set_xlabel("Dump height (m)"); ax.set_ylabel("Factor of safety (Bishop)"); ax.set_xticks(Hs); ax.legend(fontsize=6.5); ax.set_ylim(1.1, 2.0)
guardar(fig, "Fig07_fs_height")
print("figures in", OUT)
