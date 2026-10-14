"""Figuras del análisis estadístico de la base de Antamina."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent; FIG = AQUI / "figuras"; FIG.mkdir(exist_ok=True)
sys.path.insert(0, str(RAIZ / "analisis"))
from common import load_db  # noqa: E402
INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb", "#f0efec"
COL = {"Hornfels": "#2a78d6", "Mármol": "#eb6834", "Intrusivo": "#1baf7a", "Caliza y margas": "#eda100", "Mezcla": "#e87ba4"}
MK = {"Hornfels": "o", "Mármol": "s", "Intrusivo": "^", "Caliza y margas": "D", "Mezcla": "v"}
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False,
                     "savefig.dpi": 220, "savefig.bbox": "tight"})
d = pd.read_csv(AQUI / "drenados_utilizables.csv", low_memory=False)
W = load_db(); PA = 0.1013; S0 = 10 * PA


def ticks(ax):
    t = [0.1, 0.3, 1, 3, 10]; ax.set_xticks(t); ax.set_xticklabels([f"{v:g}" for v in t])


# Figura A1: φ secante vs σ′3, Antamina por litología y escala, sobre la base mundial
fig, ax = plt.subplots(figsize=(6.5, 3.8))
ax.scatter(W.s3, W.phis.where(W.s3 > 0), s=6, color=MUTED, alpha=0.25, linewidths=0, label="Base mundial (Cylwik et al., 2025)")
for lit in ["Hornfels", "Mármol", "Intrusivo", "Mezcla"]:
    g = d[d.litologia == lit]
    big = g.escala.isin(["0.6 m", "1.0 m"])
    nombre = "Intrusivo (con y sin relave)" if lit == "Intrusivo" else lit
    if big.any():
        ax.scatter(g.s3[big], g.phi_sec_deg_std[big], s=34, marker=MK[lit], color=COL[lit], edgecolor=SURF, linewidth=0.8, zorder=4,
                   label=f"{nombre}, gran escala (n = {big.sum()})")
    if (~big).any():
        ax.scatter(g.s3[~big], g.phi_sec_deg_std[~big], s=22, marker=MK[lit], facecolor="none", edgecolor=COL[lit], linewidth=1.1, zorder=3,
                   label=f"{lit}, 6 in (n = {(~big).sum()})")
ax.set_xscale("log"); ticks(ax); ax.set_xlim(0.08, 5); ax.set_ylim(30, 56)
ax.set_xlabel("σ′3 (MPa)"); ax.set_ylabel("Ángulo de fricción secante, φ′ps (°)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=7.5)
fig.savefig(FIG / "figA1_phi_vs_s3.png"); plt.close(fig)

# Figura A2: Bg vs σ′3
fig, ax = plt.subplots(figsize=(6.5, 3.4))
Wb = W.dropna(subset=["Bg"]); Wb = Wb[Wb.s3 > 0]
ax.scatter(Wb.s3, Wb.Bg, s=6, color=MUTED, alpha=0.25, linewidths=0, label=f"Base mundial (n = {len(Wb)})")
xs = np.logspace(-1.2, np.log10(4), 50); cw = np.polyfit(np.log10(Wb.s3), Wb.Bg, 1)
ax.plot(xs, np.polyval(cw, np.log10(xs)), color=INK2, lw=1.5, ls="--", label="Ajuste base mundial")
b = d.dropna(subset=["Bg_pct"])
for lit in ["Hornfels", "Mármol", "Intrusivo"]:
    g = b[b.litologia == lit]
    ax.scatter(g.s3, g.Bg_pct, s=34, marker=MK[lit], color=COL[lit], edgecolor=SURF, linewidth=0.8, zorder=4, label=f"{lit} (n = {len(g)})")
ax.set_xscale("log"); ticks(ax); ax.set_xlim(0.06, 5); ax.set_ylim(0, 80)
ax.set_xlabel("σ′3 (MPa)"); ax.set_ylabel("Índice de rotura de Marsal, Bg (%)")
ax.legend(loc="upper left", fontsize=7.5)
fig.savefig(FIG / "figA2_Bg.png"); plt.close(fig)

# Figura A3: envolventes por litología (P50 y P10) con extrapolación
R = pd.read_csv(AQUI / "litologia_posterior.csv"); import json
import sys; sys.path.insert(0, str(RAIZ / "leps3")); import leps3 as L  # noqa: E402
sn = np.logspace(np.log10(0.2), np.log10(15), 120)
fig, ax = plt.subplots(figsize=(6.5, 3.8))
for nm, lit in [("Hornfels", "Hornfels"), ("Mármol", "Mármol"), ("Intrusivo", "Intrusivo"), ("Caliza y margas", "Caliza")]:
    r = R[R.litologia == lit].iloc[0]
    est = L.Estado(np.array([r.theta, r.m]), np.array(json.loads(r.covar)) + L.SIGMA)   # material nuevo, m ≤ 1
    q = L.percentiles(sn, est, (50, 10), n=100000, rng=np.random.default_rng(5)); p50, p10 = q[50], q[10]
    lab = {"Caliza y margas": "Caliza y margas (sin ensayos; previa mundial)"}.get(nm, nm)
    ax.plot(sn, p50, color=COL[nm], lw=2, label=f"{lab}, P50")
    ax.plot(sn, p10, color=COL[nm], lw=1.2, ls=":", label=f"{nm}, P10")
ax.axvspan(2.45 * 1.7, 15, color=BAND, zorder=0)
ax.text(9.5, 51, "Sin ensayos\ndel sitio", ha="center", color=INK2, fontsize=8)
ax.set_xscale("log"); ticks(ax); ax.set_xlim(0.2, 15); ax.set_ylim(20, 54)
ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Ángulo de fricción secante, φ′s (°)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=7.5)
fig.savefig(FIG / "figA3_envolventes_litologia.png"); plt.close(fig)

# Figura A4: efecto del relave
S = pd.read_csv(AQUI / "sets_ajuste.csv")
fig, ax = plt.subplots(figsize=(6.0, 3.2))
g21 = S[S.set_a.str.contains("ALT")]; w24 = S[S.set_a.str.startswith("W2024")]
ax.scatter(g21.relave, g21.phi1_m086, s=34, marker="o", color="#2a78d6", edgecolor=SURF, label="Golder 2021: < 1 in, probeta 6 in, suelto (78 % Proctor)")
ax.scatter(w24.relave, w24.phi1_m086, s=40, marker="s", color="#eb6834", edgecolor=SURF, label="WSP 2024: probeta 0.6 m, intrusivo")
ax.set_xlabel("Relave en masa seca total (%)"); ax.set_ylabel("φ′1 del set (°), m = 0.86")
ax.set_xlim(-3, 55); ax.set_ylim(35, 46); ax.legend(loc="lower left", fontsize=7.5)
fig.savefig(FIG / "figA4_relave.png"); plt.close(fig)
print("figuras en", FIG)
