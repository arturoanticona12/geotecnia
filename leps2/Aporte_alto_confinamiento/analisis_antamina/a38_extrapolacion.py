"""Figura de la prueba de extrapolación (pedido del usuario, 2026-10-13: «esto debe estar clarito y bien mostrado en figuras»).
Misma prueba que a31: en cada set, el nivel (φ′1) se fija con sus ensayos de menor esfuerzo y se predicen los de mayor esfuerzo con
un m dado; error = φ′s predicho − φ′s medido (positivo: la curva sobreestima la resistencia).
  Base mundial: sets con algún ensayo sobre σ′n = 4.62 MPa; nivel con σ′n ≤ 2 MPa; predicción de los ensayos sobre 4.62 MPa.
  Antamina: sets triaxiales con 3 o más σ′3; nivel con los dos menores; predicción del mayor (σ′n y τ convertidos con cada m).
Paneles: (a) un set mundial de ejemplo; (b) predicho contra medido, base mundial, m = 0.85 y m = 1; (c) lo mismo, Antamina;
(d) sesgo medio según m (a31) y rango de esfuerzos de cada población. Escribe a38_extrapolacion.json, a38_casos.csv y
figuras_leps2/Fig_extrapolacion.pdf/png."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.ticker
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis")); sys.path.insert(0, str(AQ))
from lepsp_r6 import datos  # noqa: E402
S0 = 1.013
A30 = json.load(open(AQ / "a30_dos_pasos.json", encoding="utf-8")); A31 = json.load(open(AQ / "a31_m_defendible.json", encoding="utf-8"))
SNX = A30["snx"]
W = datos(); W = W[~W.cens] if "cens" in W else W
A = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False); A["set"] = A.fuente_id + "|" + A.set_id.astype(str)
phis = lambda sn, tau: np.degrees(np.arctan(tau / sn))


def a_tau_sn(s3, s1, m):
    D, Sm = s1 - s3, s1 + s3
    sp = D / Sm if abs(m - 1) < 1e-6 else (np.sqrt(4 * m * (m - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (m - 1) * D)
    return Sm / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


def nivel(sn, tau, m):
    return float(np.mean(np.log(tau) - np.log(S0 ** (1 - m) * sn ** m)))   # ln tan φ′1


filas = []
for s, g in W.groupby("Set"):
    lo, hi = g[g.sn <= 2.0], g[g.sn > SNX]
    if len(lo) and len(hi):
        for m in (0.85, 1.0):
            lt = nivel(lo.sn.values, lo.tau.values, m)
            for sn, tau in zip(hi.sn.values, hi.tau.values):
                tp = np.exp(lt) * S0 ** (1 - m) * sn ** m
                filas.append(dict(pob="Base mundial", set=s, m=m, sn=sn, med=phis(sn, tau), pred=phis(sn, tp)))
for s, g in A[A.tipo == "TX"].groupby("set"):
    if g.s3.nunique() < 3:
        continue
    g = g.sort_values("s3"); k = g.s3.values < g.s3.values.max()
    for m in (0.85, 1.0):
        sn, tau = a_tau_sn(g.s3.values, g.s1.values, m); lt = nivel(sn[k], tau[k], m)
        for sn_, tau_ in zip(sn[~k], tau[~k]):
            tp = np.exp(lt) * S0 ** (1 - m) * sn_ ** m
            filas.append(dict(pob="Antamina", set=s, m=m, sn=sn_, med=phis(sn_, tau_), pred=phis(sn_, tp)))
C = pd.DataFrame(filas); C["err"] = C.pred - C.med
C.to_csv(AQ / "a38_casos.csv", index=False, encoding="utf-8-sig")
RES = {f"{p}|{m}": dict(n=int(len(q)), sets=int(q.set.nunique()), sesgo=float(q.err.mean()), mae=float(q.err.abs().mean()),
                         sobre=int((q.err > 0).sum()), sn=[float(q.sn.min()), float(q.sn.max())])
       for (p, m), q in C.groupby(["pob", "m"])}
# ejemplo: set mundial con error de m = 1 más cercano a la mediana, con al menos 2 ensayos bajos y 2 altos
cand = []
for s, g in W.groupby("Set"):
    lo, hi = g[g.sn <= 2.0], g[g.sn > SNX]
    if len(lo) >= 2 and len(hi) >= 2:
        e1 = C[(C.pob == "Base mundial") & (C.m == 1.0) & (C.set == s)].err.mean(); cand.append((abs(e1 - C[(C.pob == "Base mundial") & (C.m == 1.0)].err.median()), s))
EJ = sorted(cand)[0][1]
out = dict(resumen=RES, ejemplo=EJ, snx=SNX, barrido=[dict(m=r["m"], mundo=r["mundo_sesgo"], antamina=r["antamina_sesgo"]) for r in A31["extrapolacion"]],
           sn_mundo_max=float(W.sn.max()))
json.dump(out, open(AQ / "a38_extrapolacion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- figura
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"
VIO, NAR, ROSA, GRIS_M = "#4a3aa7", "#d55e00", "#e87ba4", "#c9c8c2"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
fig, axs = plt.subplots(2, 2, figsize=(6.5, 7.6), gridspec_kw=dict(hspace=0.48, wspace=0.34))
# (a) ejemplo
ax = axs[0, 0]; g = W[W.Set == EJ]; lo, hi = g[g.sn <= 2.0], g[g.sn > SNX]; xs = np.geomspace(0.1, 12, 100)
ax.axvspan(SNX, 12, color="#efeee9", lw=0, zorder=0)
for m, c, ls in ((0.85, VIO, "-"), (1.0, NAR, (0, (5, 2)))):
    lt = nivel(lo.sn.values, lo.tau.values, m); ax.plot(xs, phis(xs, np.exp(lt) * S0 ** (1 - m) * xs ** m), color=c, lw=2, ls=ls, zorder=3)
ax.scatter(g[(g.sn > 2.0) & (g.sn <= SNX)].sn, phis(g[(g.sn > 2.0) & (g.sn <= SNX)].sn, g[(g.sn > 2.0) & (g.sn <= SNX)].tau), s=22, color=GRIS_M, zorder=4)
ax.scatter(lo.sn, phis(lo.sn, lo.tau), s=34, marker="o", facecolor=INK2, edgecolor=SURF, zorder=5)
ax.scatter(hi.sn, phis(hi.sn, hi.tau), s=40, marker="s", facecolor="white", edgecolor=INK, lw=1.4, zorder=5)
ax.set_xscale("log"); ax.set_xlim(0.1, 12); ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 5, 10]); ax.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "5", "10"])
ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("φ′s (°)")
ax.set_ylim(34, 56); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.set_title("(a) Ejemplo: " + " · ".join(x.strip() for x in EJ.split("|")), loc="left", fontsize=8.0, color=INK)
ax.text(0.97, 0.95, f"Sobre {SNX:.2f} MPa:\nse predice", transform=ax.transAxes, ha="right", va="top", fontsize=6.8, color=INK2)
# (b) y (c) predicho contra medido
for ax, pob, tit in ((axs[0, 1], "Base mundial", f"(b) Base mundial: ensayos sobre {SNX:.2f} MPa"), (axs[1, 0], "Antamina", "(c) Antamina: ensayo de mayor σ′3 de cada set")):
    q = C[C.pob == pob]; lim = (min(q.med.min(), q.pred.min()) - 2, max(q.med.max(), q.pred.max()) + 2)
    ax.plot((20, 60), (20, 60), color=INK2, lw=0.9, zorder=2)
    for m, c, mk in ((0.85, VIO, "o"), (1.0, NAR, "s")):
        qq = q[q.m == m]; r = RES[f"{pob}|{m}"]
        ax.scatter(qq.med, qq.pred, s=24, marker=mk, facecolor=c if m == 0.85 else "none", edgecolor=SURF if m == 0.85 else c, lw=0.8 if m == 0.85 else 1.3, zorder=4,
                   label=f"m = {m:.2f}: sesgo {r['sesgo']:+.1f}°, {r['sobre']} de {r['n']} sobreestimados".replace("-", "−"))
    EJES_BC = {"Base mundial": ((32, 52), (32, 56)), "Antamina": ((28, 50), (28, 56))}[pob]
    ax.set_xlim(*EJES_BC[0]); ax.set_ylim(*EJES_BC[1])
    ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(4)); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(4))
    ax.set_xlabel("φ′s medido (°)"); ax.set_ylabel("φ′s predicho (°)"); ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
    ax.set_title(tit, loc="left", fontsize=8.0, color=INK); ax.legend(loc="upper left", fontsize=6.4, frameon=False, handletextpad=0.3)
    ax.text(0.97, 0.04, "Sobre la recta:\nla curva sobreestima", transform=ax.transAxes, ha="right", va="bottom", fontsize=6.6, color=INK2)
# (d) barrido de m
ax = axs[1, 1]; B = pd.DataFrame(out["barrido"])
ax.axhline(0, color=INK2, lw=0.9)
ax.plot(B.m, B.mundo, color=VIO, lw=2, label=f"Base mundial ({SNX:.2f}–{W.sn.max():.2f} MPa)")
ax.plot(B.m, B.antamina, color=ROSA, lw=2, label=f"Antamina (hasta {SNX:.2f} MPa)")
for m, c in ((0.85, VIO), (1.0, NAR)):
    ax.axvline(m, color=c, lw=0.9, ls=(0, (2, 2)))
y85 = float(np.interp(0.85, B.m, B.mundo)); y1 = float(np.interp(1.0, B.m, B.mundo))
ax.annotate(f"m = 1: {y1:+.1f}°", (1.0, y1), xytext=(1.005, 4.6), fontsize=7, color=NAR, arrowprops=dict(arrowstyle="-", color=NAR, lw=0.8))
ax.annotate(f"m = 0.85: {y85:+.1f}°", (0.85, y85), xytext=(0.79, 3.0), fontsize=7, color=VIO, arrowprops=dict(arrowstyle="-", color=VIO, lw=0.8))
ax.set_xlim(0.75, 1.05); ax.xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(0.05)); ax.set_ylim(-9, 9); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(3)); ax.set_xlabel("Exponente de curvatura, m"); ax.set_ylabel("Sesgo medio de la predicción (°)")
ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(loc="lower right", fontsize=6.6, frameon=False)
ax.set_title("(d) Sesgo según m: ningún m anula los dos", loc="left", fontsize=8.0, color=INK)
h = [Line2D([], [], color=VIO, lw=2, label="m = 0.85 (curva propuesta)"), Line2D([], [], color=NAR, lw=2, ls=(0, (5, 2)), label="m = 1 (lineal, como Antamina)"),
     Line2D([], [], ls="", marker="o", mfc=INK2, mec=INK2, ms=5, label="(a) Ensayos con σ′n ≤ 2 MPa: fijan el nivel"),
     Line2D([], [], ls="", marker="s", mfc="white", mec=INK, ms=5, label=f"(a) Ensayos sobre {SNX:.2f} MPa: se predicen")]
fig.legend(handles=h, loc="lower center", ncol=2, fontsize=6.9, frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.subplots_adjust(left=0.1, right=0.98, top=0.96, bottom=0.11)
out["ejes"] = {k: dict(x=list(map(float, ax_.get_xlim())), y=list(map(float, ax_.get_ylim()))) for k, ax_ in (("a", axs[0, 0]), ("b", axs[0, 1]), ("c", axs[1, 0]), ("d", axs[1, 1]))}
json.dump(out, open(AQ / "a38_extrapolacion.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for ext in ("png", "pdf"):
    fig.savefig(AQ / "figuras_leps2" / f"Fig_extrapolacion.{ext}")
plt.close(fig)
for k, v in RES.items():
    print(k, {a: (round(b, 2) if isinstance(b, float) else b) for a, b in v.items()})
print("ejemplo:", EJ); print("escrito a38_extrapolacion.json, a38_casos.csv y figuras_leps2/Fig_extrapolacion.png/.pdf")
