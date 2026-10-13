"""Figura del anexo (2026-10-10): superficies profundas en el desmonte de un botadero de 720 m sobre roca horizontal (lotes 89–91,
a24_dovelas_mp.json). Arriba, la sección a escala real con la superficie crítica y las de entrada forzada cada vez más atrás de
la cresta; abajo, la σ′n estimada en la base de cada dovela. Regla del usuario: color para el resultado (superficies, una sola
gama de violeta de la curva propuesta, de claro a oscuro con la profundidad), grises para la sección y las zonas de respaldo."""
import json, sys
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; OUT = AQ / "figuras_leps2"
D = json.load(open(AQ / "a24_dovelas_mp.json", encoding="utf-8"))   # σ′n por Morgenstern–Price en cada dovela
SNX, SNW = 4.60, json.load(open(AQ / "a19_m_covariables.json", encoding="utf-8"))["base_sn_max"]
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#8a8984"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
SEL = [("R0 roca horizontal|Seco, global", "crítica"), ("R0 roca horizontal|Seco, entrada a 1H", "1H"),
       ("R0 roca horizontal|Seco, entrada a 2H", "2H"), ("R0 roca horizontal|Seco, entrada a 3H", "3H"),
       ("R0 roca horizontal|Seco, entrada a 5H", "5H")]
cm = LinearSegmentedColormap.from_list("vio", ["#a99be3", "#2a1f73"]); COL = [cm(i / (len(SEL) - 1)) for i in range(len(SEL))]
# perfil de bancos (generar_yaml_profundas.bancos): 12 bancos de 60 m, caras 1.333H:1V, bermas de 50 m
px, py, x, y = [-400.0, 0.0], [0.0, 0.0], 0.0, 0.0
for i in range(12):
    x += 60 * 1.333; y += 60; px.append(x); py.append(y)
    if i < 11:
        x += 50; px.append(x); py.append(y)
XR = 5300; px.append(XR); py.append(720)
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.5, 5.6), gridspec_kw=dict(height_ratios=[1.0, 1.55], hspace=0.32))
a1.fill_between(px, py, 0, color="#f1f0ec", lw=0); a1.plot(px, py, color=INK2, lw=0.9)
a1.fill_between([-400, XR], -120, 0, color="#dcdbd5", lw=0); a1.text(-350, -95, "Roca", color=INK2, fontsize=8)
a1.text(4900, 120, "Desmonte ROM", color=INK2, fontsize=8, ha="right")
for (k, et), c in zip(SEL, COL):
    s = D[k]["superficie"]; a1.plot(s["x"], s["yb"], color=c, lw=1.6)
    a1.annotate(f"{et}\nFS {D[k]['fs_slide2']:.2f}", (s["x"][-1], 720), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                fontsize=7, color=INK)
a1.set_xlim(-400, XR); a1.set_ylim(-120, 900); a1.set_aspect("equal"); a1.set_yticks([0, 360, 720])
a1.set_xlabel("Distancia desde el pie (m)"); a1.set_ylabel("Cota (m)")
a1.text(0.0, 1.26, "a) Sección de 720 m sobre roca horizontal: superficie crítica y superficies con entrada forzada", transform=a1.transAxes,
        fontsize=8.5, color=INK, va="bottom")
a2.axhspan(SNX, SNW, color="#efeee9", lw=0, zorder=0)
a2.axhspan(SNW, 15, facecolor="none", edgecolor="#d2d1cb", hatch="///", lw=0, zorder=0)
for v in (SNX, SNW):
    a2.axhline(v, color=MUTED, lw=0.7, ls="--", zorder=1)
a2.text(XR - 30, SNX + 0.12, f"{SNX:.2f} MPa", ha="right", va="bottom", fontsize=7, color=INK2)
a2.text(XR - 30, SNW + 0.12, f"{SNW:.2f} MPa", ha="right", va="bottom", fontsize=7, color=INK2)
for (k, et), c in zip(SEL, COL):
    d = D[k]["dovelas"]; xm, sn = np.array(d["xm"]), np.array(d["sn"]); ok = np.array(d["mat"]) == "Desmonte ROM"
    a2.plot(xm[ok], sn[ok], color=c, lw=1.6, zorder=3)
    i = int(np.argmax(sn)); a2.annotate(f"{et}: {sn[i]:.1f}", (xm[i], sn[i]), xytext=(0, 4), textcoords="offset points", ha="center",
                                        va="bottom", fontsize=7, color=INK)
a2.set_xlim(-400, XR); a2.set_ylim(0, 13); a2.set_xlabel("Distancia desde el pie (m)"); a2.set_ylabel("σ′n en la base de la dovela (MPa)")
a2.text(0.0, 1.03, "b) Esfuerzo normal efectivo en la base de cada dovela (Morgenstern–Price)", transform=a2.transAxes,
        fontsize=8.5, color=INK, va="bottom")
fig.subplots_adjust(left=0.1, right=0.98, top=0.93, bottom=0.08)
fig.savefig(OUT / "FigA1_profundas.png"); fig.savefig(OUT / "FigA1_profundas.pdf"); plt.close(fig)
print("ok", OUT / "FigA1_profundas.png")
