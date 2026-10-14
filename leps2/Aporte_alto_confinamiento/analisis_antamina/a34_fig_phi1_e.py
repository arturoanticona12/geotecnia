"""Figura φ′1–e de la curva propuesta (simple, m = 0.85; 2026-10-12), como la Fig. 10 de Cylwik et al. (2025): φ′1 de cada set de Antamina
con la m de la curva (Ec. 8), frente a la e0 media del set (D854 de Golder 2010, a8), y la recta
φ′1 = φ′e0 − 20°·e de la curva (nivel de a33). Rectas de referencia de las clases de Leps 2.0 en gris. Escribe figuras_leps2/Fig_phi1_e.png
y .pdf, y a34_phi1_sets.csv."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt  # noqa: E401,E402
from matplotlib.lines import Line2D  # noqa: E402
from a33_curva_propuesta import A, SA, E_SET, phi1_sets  # noqa: E402

A33 = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8")); P = A33["parametros"]
PHI1 = phi1_sets(P["m_a"])
LIT = [A[A.set == s].litologia.iloc[0] for s in SA]; DS = [bool((A[A.set == s].tipo != "TX").all()) for s in SA]
pd.DataFrame(dict(set=SA, litologia=LIT, corte_directo=DS, e0=E_SET, phi1=PHI1, phi_e0=PHI1 + P["omega"] * E_SET)).to_csv(
    AQ / "a34_phi1_sets.csv", index=False, encoding="utf-8-sig")
print(f"{len(SA)} sets; media φ′1 + 20·e0 = {np.mean(PHI1 + P['omega'] * E_SET):.2f}° (curva: {P['pe0']:.2f}°)")

INK2, MUTED, VIO = "#52514e", "#8a8984", "#4a3aa7"
LITC = {"Mármol": ("#2a78d6", "o"), "Hornfels": ("#eb6834", "s"), "Intrusivo": ("#1baf7a", "^")}
MEZ = ("#eda100", "D")
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.edgecolor": MUTED, "xtick.color": INK2, "ytick.color": INK2, "savefig.dpi": 300})
fig, ax = plt.subplots(figsize=(6.5, 4.8)); ee = np.linspace(0, 0.8, 50)
# fondo (WA 2026-10-12): Leps (1970) como φ′1 = 46/41/36° (Cylwik et al. 2025, p. 2, Ec. 9; no dependen de e) y la cota inferior de
# Indraratna et al. (1993) en la forma de Cylwik et al. (2025, Tabla 1, p. 3): φ′1 = 33°, sin dependencia de e
REF = ((lambda e: np.full_like(e, 46.0), (0, (6, 2, 1, 2)), "Leps (1970), envolvente superior (φ′1 = 46°)"),
       (lambda e: np.full_like(e, 41.0), (0, (4, 2)), "Leps (1970), envolvente media (φ′1 = 41°)"),
       (lambda e: np.full_like(e, 36.0), (0, (1, 1.5)), "Leps (1970), envolvente inferior (φ′1 = 36°)"),
       (lambda e: np.full_like(e, 33.0), "-", "Cota inferior de Indraratna et al. (1993) (φ′1 = 33°)"))
for f_, ls, _ in REF:
    ax.plot(ee, f_(ee), color=MUTED, lw=1.0, ls=ls)
ax.plot(ee, P["pe0"] - P["omega"] * ee, color=VIO, lw=2.2)
for i in range(len(SA)):
    c_, mk = LITC.get(LIT[i], MEZ)
    ax.scatter(E_SET[i], PHI1[i], s=46, marker=mk, zorder=4, facecolor="white" if DS[i] else c_, edgecolor=c_, lw=1.6)
ax.set_xlim(0.2, 0.55); ax.set_ylim(32, 50)
ax.set_xlabel("Relación de vacíos inicial del ensayo, e0 (media del set)")
ax.set_ylabel("φ′1 del set (°), ángulo secante a σ′n = 10pa")
ax.grid(True, color="#e6e5e1", lw=0.6); ax.set_axisbelow(True)
h1 = [Line2D([], [], color=VIO, lw=2.2, label=f"Curva propuesta: φ′1 = {P['pe0']:.1f}° − {P['omega']:.0f}°·e")] + \
     [Line2D([], [], color=MUTED, lw=1.0, ls=ls, label=n_) for _, ls, n_ in REF]
h2 = [Line2D([], [], ls="", marker=mk, color=c_, ms=7, label=l_) for l_, (c_, mk) in LITC.items()] + \
     [Line2D([], [], ls="", marker=MEZ[1], color=MEZ[0], ms=7, label="Mezclas"),
      Line2D([], [], ls="", marker="o", color="#52514e", ms=7, label="Lleno: triaxial"),
      Line2D([], [], ls="", marker="o", mfc="white", mec="#52514e", mew=1.6, ms=7, label="Vacío: corte directo")]
l1 = fig.legend(handles=h1, loc="upper left", bbox_to_anchor=(0.02, 0.0), frameon=False, fontsize=7.5, title="Curva y referencias",
                title_fontsize=8, alignment="left")
fig.legend(handles=h2, loc="upper left", bbox_to_anchor=(0.56, 0.0), frameon=False, fontsize=7.5, ncol=2,
           title=f"Sets de ensayos de Antamina (m = {P['m_a']:.2f})", title_fontsize=8, alignment="left")
fig.tight_layout()
for ext in ("png", "pdf"):
    fig.savefig(AQ / "figuras_leps2" / f"Fig_phi1_e.{ext}", bbox_inches="tight")
plt.close(fig); print("escrito figuras_leps2/Fig_phi1_e.png/.pdf y a34_phi1_sets.csv")
