"""Figuras del informe: rango de esfuerzos, caída de φ'1 a alta presión, envolventes, rotura y presión de poros."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
AQUI = Path(__file__).parent
sys.path.insert(0, str(AQUI))
from common import load_db, within_set, PA  # noqa: E402

FIG = AQUI.parent / "figuras"; FIG.mkdir(exist_ok=True)
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
INK, INK2, MUTED, GRID, AXIS, SURF = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
BAND = "#f0efec"
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2,
                     "xtick.color": MUTED, "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID,
                     "grid.linewidth": 0.6, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False,
                     "savefig.dpi": 220, "savefig.bbox": "tight"})
df = load_db()
A = 3.72  # °/década, ajustado en analisis2.py


def fmt_log(ax, axis="x"):
    t = [0.01, 0.03, 0.1, 0.3, 1, 3, 10, 30]
    (ax.set_xticks if axis == "x" else ax.set_yticks)(t)
    (ax.set_xticklabels if axis == "x" else ax.set_yticklabels)([f"{v:g}" for v in t])


# --- Figura 1: cobertura de esfuerzos
fig, ax = plt.subplots(figsize=(6.5, 3.2))
bins = np.logspace(-2.5, np.log10(20), 36)
ax.hist(df.sn, bins=bins, color=C1, edgecolor=SURF, linewidth=1.0, zorder=3)
ax.set_xscale("log"); fmt_log(ax)
ymax = ax.get_ylim()[1] * 1.25; ax.set_ylim(0, ymax)
ax.axvspan(1.9, 4.6, color=BAND, zorder=1)
ax.axvspan(4.6, 6.5, color="#e1e0d9", zorder=1)
ax.axvline(df.sn.max(), color=INK2, lw=1, ls="--", zorder=4)
ax.axvline(14.7, color=INK, lw=1.2, zorder=4)
ax.text(np.sqrt(1.9 * 4.6), ymax * 0.93, "Superficie circular\ncrítica", ha="center", va="top", color=INK2, fontsize=8)
ax.text(np.sqrt(4.6 * 6.5), ymax * 0.70, "Mecanismo\nbasal", ha="center", va="top", color=INK2, fontsize=8)
ax.text(df.sn.max() * 1.05, ymax * 0.45, f"Máximo de la base\nde datos: {df.sn.max():.1f} MPa", color=INK2, fontsize=8, va="top")
ax.text(14.7 * 1.08, ymax * 0.97, "σv en la\nbase de\n700 m:\n14.7 MPa", color=INK, fontsize=8, va="top", ha="left")
ax.set_xlim(right=60)
ax.set_xlabel("Esfuerzo normal efectivo en el plano de falla, σ′n (MPa)")
ax.set_ylabel("Número de ensayos")
fig.savefig(FIG / "fig1_cobertura_esfuerzos.png"); plt.close(fig)

# --- Figura 2: (a) caída de φ'1 dentro de cada set; (b) sesgo de extrapolación según m
w = within_set(df)
bm = pd.read_csv(AQUI / "barrido_m.csv")
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={"width_ratios": [1.35, 1]})
ax.scatter(w.sn, w.dphi1, s=7, color=C1, alpha=0.3, linewidths=0, zorder=3, label="Ensayo individual")
edges = np.array([0.1, 0.3, 0.6, 1, 2, 3, 4, 5, 8])
mid, med, q1, q3 = [], [], [], []
for lo, hi in zip(edges[:-1], edges[1:]):
    g = w[(w.sn > lo) & (w.sn <= hi)].dphi1
    mid.append(np.sqrt(lo * hi)); med.append(g.median()); q1.append(g.quantile(0.25)); q3.append(g.quantile(0.75))
mid, med = np.array(mid), np.array(med)
ax.errorbar(mid, med, yerr=[med - np.array(q1), np.array(q3) - med], fmt="o", ms=5, color=INK, ecolor=INK2,
            elinewidth=1, capsize=0, zorder=5, label="Mediana (barras: cuartiles)")
xs = np.logspace(-1, np.log10(15), 80)
from common import tau_leps, fit_set
sref = np.logspace(np.log10(0.3), np.log10(1.5), 7)
for mm, ls in [(0.87, "-"), (0.85, ":")]:
    # mismo procedimiento que los datos: referencia con m = 0.9 ajustada en 0.3–1.5 MPa sobre una envolvente con m = mm
    ref = fit_set(sref, tau_leps(sref, 41, mm), m=0.9)[0]
    dphi = np.degrees(np.arctan(tau_leps(xs, 41, mm) / ((10 * PA) ** 0.1 * xs ** 0.9))) - ref
    ax.plot(xs, dphi, color=C2, lw=2, ls=ls, zorder=4, label=f"Envolvente con m = {mm}")
ax.axhline(0, color=AXIS, lw=1, zorder=2)
ax.axvspan(df.sn.max(), 15, color=BAND, zorder=1)
ax.set_xscale("log"); fmt_log(ax); ax.set_xlim(0.1, 15); ax.set_ylim(-9, 7)
ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Δφ′1 respecto de la referencia del set (°)")
ax.set_title("(a)", loc="left", fontsize=9, color=INK)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=7.5)
bx.plot(bm.m, 100 * bm.sesgo, color=C1, lw=2, marker="o", ms=3.5, label="Sesgo medio, σ′n ≥ 2 MPa")
bx.plot(bm.m, 100 * bm.sesgo3, color=C3, lw=2, marker="o", ms=3.5, label="Sesgo medio, σ′n ≥ 3 MPa")
bx.plot(bm.m, 100 * bm.mae, color=INK2, lw=1.5, ls="--", label="Error absoluto medio, σ′n ≥ 2 MPa")
bx.axhline(0, color=AXIS, lw=1)
bx.axvspan(0.856, 0.875, color=BAND, zorder=0)
bx.axvline(0.9, color=MUTED, lw=1, ls=":")
bx.text(0.903, -19, "m = 0.9\n(Leps 2.0)", color=INK2, fontsize=7.5, va="bottom")
bx.set_xlim(0.78, 0.95); bx.set_ylim(-20, 15)
bx.set_xlabel("Exponente m usado al extrapolar"); bx.set_ylabel("Error en τ predicho (%)")
bx.set_title("(b)", loc="left", fontsize=9, color=INK)
bx.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1, fontsize=7.5)
fig.tight_layout(w_pad=2.0)
fig.savefig(FIG / "fig2_extrapolacion_m.png"); plt.close(fig)

# --- Figura 3: envolventes en ángulo secante
fig, ax = plt.subplots(figsize=(6.5, 3.6))
s = np.logspace(-1, np.log10(15), 200)
phs = lambda p1, mm: np.degrees(np.arctan(np.tan(np.radians(p1)) * (s / (10 * PA)) ** (mm - 1)))
hi = df[df.sn > 2]
ax.scatter(hi.sn, hi.phis, s=10, color=MUTED, alpha=0.5, linewidths=0, zorder=2, label="Ensayos de la base con σ′n > 2 MPa")
ax.axhspan(30, 40, xmin=0.62, xmax=1, color=BAND, zorder=1)
for p1, ls in [(41, "-"), (38, "--")]:
    ax.plot(s, phs(p1, 0.9), color=C1, lw=2, ls=ls, zorder=4, label=f"φ′1 = {p1}°, m = 0.9")
    ax.plot(s, phs(p1, 0.87), color=C2, lw=2, ls=ls, zorder=4, label=f"φ′1 = {p1}°, m = 0.87")
ax.axvline(df.sn.max(), color=INK2, lw=1, ls=":", zorder=3)
ax.set_xscale("log"); fmt_log(ax); ax.set_xlim(0.1, 15); ax.set_ylim(26, 56)
ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Ángulo de fricción secante, φ′s (°)")
from matplotlib.patches import Patch
h_, l_ = ax.get_legend_handles_labels()
h_.append(Patch(color=BAND)); l_.append("30–40° a alta presión (Ovalle et al., 2020)")
ax.legend(h_, l_, loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=8)
fig.savefig(FIG / "fig3_envolventes_secantes.png"); plt.close(fig)

# --- Figura 4: rotura Bg vs σn por clase de UCS
b = df.dropna(subset=["Bg", "UCS"])
fig, ax = plt.subplots(figsize=(6.5, 3.4))
cls = [((0, 80), "UCS ≤ 80 MPa", C2), ((80, 150), "UCS 80–150 MPa", C3), ((150, 400), "UCS > 150 MPa", C1)]
xs = np.logspace(-2, np.log10(8), 50)
for (lo, hi_), lab, c in cls:
    g = b[(b.UCS > lo) & (b.UCS <= hi_)]
    ax.scatter(g.sn, g.Bg, s=10, color=c, alpha=0.45, linewidths=0, zorder=3)
    sl, ic = np.polyfit(np.log10(g.sn), g.Bg, 1)
    ax.plot(xs, ic + sl * np.log10(xs), color=c, lw=2, zorder=4, label=f"{lab} (n = {len(g)})")
ax.set_xscale("log"); fmt_log(ax); ax.set_xlim(0.01, 10); ax.set_ylim(0, 120)
ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Índice de rotura de Marsal, Bg (%)")
ax.legend(loc="upper left", fontsize=8)
fig.savefig(FIG / "fig4_rotura_Bg.png"); plt.close(fig)

# --- Figura 5: exceso de presión de poros por consolidación
rows = pd.DataFrame(json.load(open(AQUI / "consol.json")))
fig, ax = plt.subplots(figsize=(6.5, 3.2))
for R, c in [(25, C1), (50, C2), (100, C3)]:
    g = rows[(rows.M == 50) & (rows.R == R)].sort_values("k")
    ax.plot(g.k, g.ru.clip(lower=1e-5), color=c, lw=2, marker="o", ms=5, label=f"Crecimiento {R} m/año")
ax.axhline(0.1, color=INK2, lw=1, ls="--")
ax.text(3e-6, 0.12, "Δu/σv = 0.1", color=INK2, fontsize=8)
ax.axvspan(1e-7, 1e-4, color=BAND, zorder=0)
ax.text(1.4e-6, 0.3, "Desmonte con matriz granular\n($k \\geq 10^{-7}$ m/s)", ha="center", color=INK2, fontsize=8)
ax.set_xscale("log"); ax.set_yscale("log"); ax.set_xlim(5e-10, 2e-5); ax.set_ylim(1e-5, 1)
ax.set_xlabel("Permeabilidad de la capa basal saturada, k (m/s)")
ax.set_ylabel("Exceso Δu/σv al final (base)")
ax.legend(loc="lower left", fontsize=8)
fig.savefig(FIG / "fig5_presion_poros_consolidacion.png"); plt.close(fig)

# --- Figura 6: Leps 3.0, envolvente central y de diseño frente a Leps 2.0 (φ'1 = 41°)
sys.path.insert(0, str(AQUI.parent / "leps3"))
import warnings as _w
import leps3 as L3
_w.filterwarnings("ignore")
fig, ax = plt.subplots(figsize=(6.5, 3.7))
s = np.logspace(np.log10(0.05), np.log10(15), 300)
sec = lambda t: np.degrees(np.arctan(t / s))
ax.fill_between(s, sec(L3.tau_diseno(s, 41, percentil=10)), sec(L3.tau(s, 41)), color=C2, alpha=0.15, lw=0, zorder=1)
ax.plot(s, sec(L3.tau(s, 41, 0.9)), color=C1, lw=2, label="Leps 2.0 (m = 0.9)")
ax.plot(s, sec(L3.tau(s, 41)), color=C2, lw=2, label="Leps 3.0, envolvente central (m = 0.87)")
ax.plot(s, sec(L3.tau_diseno(s, 41, percentil=20)), color=C2, lw=1.5, ls="--", label="Leps 3.0, diseño P20")
ax.plot(s, sec(L3.tau_diseno(s, 41, percentil=10)), color=C2, lw=1.5, ls=":", label="Leps 3.0, diseño P10")
ax.axvspan(L3.SN_MAX_DATOS, 15, color=BAND, zorder=0)
ax.text(10.9, 47.5, "Extrapolación\nsin datos", ha="center", color=INK2, fontsize=8)
ax.set_xscale("log"); fmt_log(ax); ax.set_xlim(0.05, 15); ax.set_ylim(28, 52)
ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Ángulo de fricción secante, φ′s (°)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=2, fontsize=8)
fig.savefig(FIG / "fig6_leps3_envolventes.png"); plt.close(fig)
print("figuras en", FIG)


