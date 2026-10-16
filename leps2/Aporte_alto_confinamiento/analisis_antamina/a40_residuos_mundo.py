"""Residuos de la curva propuesta en Antamina y en la base mundial de Leps 2.0 (idea del usuario, 2026-10-13).
Residuo = φ′s medido − φ′s de la curva propuesta (con tope), cada ensayo a su σ′n y a su e0.
  (a) residuo frente a σ′n: Antamina (ensayos del ajuste) y base mundial (sin los censurados). Mide nivel y forma a la vez: los
      materiales mundiales más resistentes quedan sobre la curva. Medianas por clase de roca de Leps 2.0 entre 3 y 8 MPa.
  (b) residuo dentro de cada set (menos la media del set), con σ′n > 1 MPa y sets con dos o más esfuerzos en ese rango: quita el
      nivel de cada material y deja la forma. Tendencia sobre ln σ′n de cada población.
Escribe a40_residuos_mundo.json, a40_mundo.csv y figuras_leps2/Fig_residuos_mundo.pdf/png."""
import json, os, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.ticker
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent / "analisis"))
_so = sys.stdout; sys.stdout = open(os.devnull, "w", encoding="utf-8")
from lepsp_r6 import datos  # noqa: E402
sys.stdout = _so
from tope import TOPE  # noqa: E402
S0, OM, SMIN = 1.013, 20.0, 1.0
PE0 = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8"))["parametros"]["pe0"]
curva = lambda s, e: np.minimum(np.degrees(np.arctan(np.tan(np.radians(PE0 - OM * np.asarray(e))) * (np.asarray(s) / S0) ** (0.85 - 1))), TOPE)
W = datos(); W = W[~W.cens] if "cens" in W else W
W = W[(W.sn > 0) & (W.tau > 0)].reset_index(drop=True)
W["r"] = np.degrees(np.arctan(W.tau / W.sn)) - curva(W.sn, W.e)
P = pd.read_csv(AQ / "a35_residuos.csv"); P["r"] = P["Curva propuesta"]


def dentro(df, col_set):
    g = df[df.sn > SMIN].copy(); g = g[g.groupby(col_set).sn.transform("nunique") >= 2]
    g["rc"] = g.r - g.groupby(col_set).r.transform("mean"); lr = stats.linregress(np.log(g.sn), g.rc)
    return g, dict(pendiente=float(lr.slope), p=float(lr.pvalue), r=float(lr.rvalue), n=int(len(g)), sets=int(g[col_set].nunique()), intercepto=float(lr.intercept))


Gw, Tw = dentro(W, "Set"); Ga, Ta = dentro(P, "set")
CLS = [("good", "buena"), ("moderate", "moderada"), ("low", "baja")]
Tc = {c: dentro(W[W.clase == c], "Set")[1] for c, _ in CLS}          # tendencia dentro de los sets de cada clase
q = W[(W.sn > 3) & (W.sn <= 8)]
out = dict(definicion="residuo = φ′s medido − φ′s de la curva propuesta (con tope), a σ′n y e0 de cada ensayo",
           mundo_3_8=dict(n=int(len(q)), sets=int(q.Set.nunique()), mediana=float(q.r.median()), sobre=int((q.r > 0).sum()),
                          clases={c: dict(n=int(len(v)), mediana=float(v.r.median())) for c, v in q.groupby("clase")}),
           dentro_mundo=Tw, dentro_antamina=Ta, dentro_clase=Tc, n_clase={c: int((W.clase == c).sum()) for c, _ in CLS}, smin=SMIN, n_mundo=int(len(W)))
lo = []
for s, g in W.groupby("Set"):
    lo_, hi_ = g[g.sn <= 2], g[(g.sn > 3) & (g.sn <= 8)]
    if len(lo_) and len(hi_):
        t1 = np.mean(np.log(lo_.tau) - np.log(S0 ** 0.15 * lo_.sn ** 0.85)); lo.append(np.degrees(np.arctan(np.exp(t1))) + OM * lo_.e.mean())
out["mundo_3_8"]["pe0_mediana_sets"] = float(np.median(lo)); out["pe0_curva"] = PE0
W[["Set", "sn", "e", "r", "clase"]].assign(dentro=W.index.isin(Gw.index), rc=Gw.rc.reindex(W.index)).to_csv(AQ / "a40_mundo.csv", index=False, encoding="utf-8-sig")
json.dump(out, open(AQ / "a40_residuos_mundo.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- figura
INK, INK2, MUTED, GRID = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1"
ROJO, MUNDO = "#d55e00", "#3b3a37"
COLC = {"good": "#1f4e9e", "moderate": "#1b8a3a", "low": "#8c5a1e"}   # clases de roca de Leps 2.0 (distintos del rojo de Antamina)
MKC = {"good": "^", "moderate": "s", "low": "o"}; LLC = {"good": True, "moderate": True, "low": False}
GRIS_F = "#cfcec9"
BINS_A = [0.1, 0.2, 0.35, 0.6, 1.0, 1.7, 3.0, 5.0, 8.0]; BINS_B = [1.0, 1.5, 2.2, 3.2, 4.6, 8.0]


def medianas(q_, col, bins):
    """Mediana por rango de σ′n (con 3 o más ensayos); x = media geométrica de los σ′n del rango."""
    o = []
    for a, b in zip(bins[:-1], bins[1:]):
        v = q_[(q_.sn >= a) & (q_.sn < b)]
        if len(v) >= 3:
            o.append((float(np.exp(np.log(v.sn).mean())), float(v[col].median()), int(len(v)), a, b))
    return o


def mundo_sc(ax, q_, c, col, bins):
    m_ = medianas(q_, col, bins)
    ax.plot([x for x, *_ in m_], [y for _, y, *_ in m_], color=COLC[c], lw=1.6, marker=MKC[c], ms=6.5,
            mfc=COLC[c] if LLC[c] else "white", mec=COLC[c], mew=1.4, zorder=4)
    return m_
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
fig, (a1, a2) = plt.subplots(2, 1, figsize=(6.5, 8.3), gridspec_kw=dict(hspace=0.42))


def ejes(ax, y, titulo, x0=0.1):
    ax.axhline(0, color=INK2, lw=0.9, zorder=2)
    ax.set_xscale("log"); ax.set_xlim(x0, 10); ax.set_ylim(-y, y)
    tk = [t for t in (0.1, 0.2, 0.5, 1, 2, 3, 5, 10) if t >= x0 and (x0 < 1 or t != 0.5)]
    tk = [t for t in tk if not (x0 < 1 and t == 3)]
    ax.set_xticks(tk); ax.set_xticklabels([f"{t:g}" for t in tk])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter()); ax.yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(4))
    ax.set_xlabel("Esfuerzo normal efectivo en el plano de falla, σ′n (MPa)")
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); ax.set_title(titulo, loc="left", fontsize=8.6, color=INK)


ejes(a1, 16, "(a) Residuo de la curva propuesta, cada ensayo a su e0")
a1.scatter(W.sn, W.r, s=7, marker="o", color=GRIS_F, lw=0, zorder=2)
MED = {"a": {}, "b": {}}
for c, _ in CLS:
    MED["a"][c] = mundo_sc(a1, W[W.clase == c], c, "r", BINS_A)
a1.scatter(P.sn, P.r, s=38, marker="o", color=ROJO, edgecolor="#2b1a10", lw=0.8, zorder=5)
a1.set_ylabel("φ′s ensayado − predicho (°)")
cl = out["mundo_3_8"]["clases"]; nm = {"good": "buena", "moderate": "moderada", "low": "baja"}
a1.text(0.015, 0.03, "Base mundial, 3–8 MPa: mediana por clase de roca\n" + ", ".join(f"{nm[c]} {cl[c]['mediana']:+.1f}° ({cl[c]['n']})" for c in ("good", "moderate", "low") if c in cl),
        transform=a1.transAxes, fontsize=6.8, color=INK2, va="bottom", bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.5))
ejes(a2, 8, f"(b) Residuo dentro de cada set (menos la media del set), σ′n > {SMIN:g} MPa", x0=1.0)
a2.scatter(Gw.sn, Gw.rc, s=7, marker="o", color=GRIS_F, lw=0, zorder=2)
for c, _ in CLS:
    MED["b"][c] = mundo_sc(a2, Gw[Gw.clase == c], c, "rc", BINS_B)
a2.scatter(Ga.sn, Ga.rc, s=38, marker="o", color=ROJO, edgecolor="#2b1a10", lw=0.8, zorder=5)
xs = np.geomspace(1.0, 10, 30)
for g, t, c in ((Gw, Tw, MUNDO), (Ga, Ta, ROJO)):
    xg = np.geomspace(g.sn.min(), g.sn.max(), 30)
    a2.plot(xg, t["intercepto"] + t["pendiente"] * np.log(xg), color=c, lw=1.6, ls=(0, (5, 2)), zorder=5)
a2.set_ylabel("Residuo centrado en el set (°)")
pf = lambda p: "p < 0.001" if p < 0.001 else f"p = {p:.2f}"
h = [Line2D([], [], ls="", marker="o", mfc=ROJO, mec="#2b1a10", mew=0.8, ms=7, label=f"Antamina, ensayos del ajuste ({len(P)})"),
     Line2D([], [], ls="", marker="o", color=GRIS_F, ms=4, label=f"Base mundial de Leps 2.0, ensayos ({len(W)}; Cylwik et al., 2025)"),
     *[Line2D([], [], color=COLC[c], lw=1.6, marker=MKC[c], mfc=COLC[c] if LLC[c] else "white", mec=COLC[c], mew=1.4, ms=6, label=f"Mediana por rango de σ′n, clase {n_} ({out['n_clase'][c]} ensayos); (b) tendencia {Tc[c]['pendiente']:+.2f}°, {pf(Tc[c]['p'])}".replace("-", "−")) for c, n_ in CLS],
     Line2D([], [], color=ROJO, lw=1.6, ls=(0, (5, 2)), label=f"(b) Tendencia Antamina: {Ta['pendiente']:+.1f}° por unidad de ln σ′n, {pf(Ta['p'])} ({Ta['sets']} sets)".replace("-", "−")),
     Line2D([], [], color=MUNDO, lw=1.6, ls=(0, (5, 2)), label=f"(b) Tendencia base mundial, todas las clases: {Tw['pendiente']:+.2f}° por unidad de ln σ′n, {pf(Tw['p'])} ({Tw['sets']} sets)".replace("-", "−"))]
fig.legend(handles=h, loc="lower center", ncol=1, fontsize=7.2, frameon=False, bbox_to_anchor=(0.5, 0.0))
fig.subplots_adjust(left=0.1, right=0.98, top=0.96, bottom=0.215)
out["ejes"] = dict(a=list(a1.get_ylim()), b=list(a2.get_ylim())); out["medianas"] = MED; out["bins"] = dict(a=BINS_A, b=BINS_B)
json.dump(out, open(AQ / "a40_residuos_mundo.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for ext in ("png", "pdf"):
    fig.savefig(AQ / "figuras_leps2" / f"Fig_residuos_mundo.{ext}")
plt.close(fig)
print("fuera de ejes (a):", int((W.r.abs() > 16).sum()), "(b):", int((Gw.rc.abs() > 8).sum()))
print(json.dumps({k: v for k, v in out.items() if k != "definicion"}, ensure_ascii=False)[:900])
