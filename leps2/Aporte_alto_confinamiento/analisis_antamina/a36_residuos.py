"""Diagnóstico de los residuos del ajuste (pedido del usuario, 2026-10-13: «me parece un ajuste sesgado, evalúalo»).
Residuo = φ′s medido − φ′s de la curva, cada ensayo a su σ′n y su e0 (a35_residuos.csv; triaxiales convertidos con m = 0.85).
  (a) curva propuesta (m = 0.85, con tope) frente a σ′n: tendencia (regresión sobre ln σ′n) y medias por rango con IC 90 %;
  (b) la misma prueba con el nivel ajustado con m = 1 (Antamina sola, a33 «lineal»): si la tendencia desaparece, es de forma;
  (c) residuo de la curva propuesta por litología (nivel). La prueba de extrapolación va en su propia figura (a38).
Escribe a36_residuos.json y figuras_leps2/Fig_residuos.pdf/png."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.ticker
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from tope import TOPE  # noqa: E402
S0, OM = 1.013, 20.0
A33 = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8")); A31 = json.load(open(AQ / "a31_m_defendible.json", encoding="utf-8"))
PE0, PE1 = A33["parametros"]["pe0"], A33["nivel"]["lineal"]["pe0"]
P = pd.read_csv(AQ / "a35_residuos.csv")
ph = lambda s, pe0, e, m: np.degrees(np.arctan(np.tan(np.radians(pe0 - OM * e)) * (s / S0) ** (m - 1)))
P["r_prop"] = P["Curva propuesta"]                                   # m = 0.85, con tope (la curva entregada)
P["r_sintope"] = P.phis - ph(P.sn, PE0, P.e, 0.85)
P["r_m1"] = P.phis - ph(P.sn, PE1, P.e, 1.0)
BINS = [(0.1, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 5.0)]


def tendencia(r):
    lr = stats.linregress(np.log(P.sn), r)
    return dict(pendiente=float(lr.slope), r=float(lr.rvalue), p=float(lr.pvalue), media=float(np.mean(r)))


def por_rango(r):
    out = []
    for a, b in BINS:
        x = r[(P.sn >= a) & (P.sn < b)].values; n = len(x)
        h = float(stats.t.ppf(0.95, n - 1) * x.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan")
        out.append(dict(a=a, b=b, n=n, media=float(x.mean()), ic90=h, smed=float(np.exp(np.log(P.sn[(P.sn >= a) & (P.sn < b)]).mean()))))
    return out


R = {k: dict(tendencia=tendencia(P[k]), rangos=por_rango(P[k])) for k in ("r_prop", "r_sintope", "r_m1")}
# dentro de cada set (con 2 o más esfuerzos): pendiente del residuo sin tope sobre ln σ′n
SL = {s: float(stats.linregress(np.log(q.sn), q.r_sintope).slope) for s, q in P.groupby("set") if q.sn.nunique() >= 2}
R["dentro_sets"] = dict(n=len(SL), media=float(np.mean(list(SL.values()))), positivas=int(sum(v > 0 for v in SL.values())), por_set=SL)
R["pe0_m1"] = PE1
R["por_litologia"] = P.groupby("litologia").r_prop.agg(["mean", "count"]).rename(columns={"mean": "media", "count": "n"}).to_dict("index")
R["extrapolacion"] = [dict(m=r["m"], mundo=r["mundo_sesgo"], antamina=r["antamina_sesgo"], n_w=r["n_w"], n_a=r["n_a"]) for r in A31["extrapolacion"]]
lr_e = stats.linregress(P.e, P.r_sintope); R["frente_e"] = dict(pendiente=float(lr_e.slope), p=float(lr_e.pvalue))
json.dump(R, open(AQ / "a36_residuos.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ---------------------------------------------------------------- figura (paleta y estilo de a11)
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"
VIO = "#4a3aa7"; ROSA, VERDE = "#e87ba4", "#008300"
LIT = {"Mármol": ("#2a78d6", "o"), "Hornfels": ("#eb6834", "s"), "Intrusivo": ("#1baf7a", "^"), "Mezcla": ("#eda100", "D")}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8.5, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
fig, axs = plt.subplots(2, 2, figsize=(6.5, 7.4), gridspec_kw=dict(hspace=0.42, wspace=0.32))


def panel_res(ax, col, titulo, color_med):
    ax.axhline(0, color=INK2, lw=0.9)
    for lit, (c, mk) in LIT.items():
        for tipo, lleno in (("TX", True), ("DS", False)):
            q = P[(P.litologia == lit) & (P.tipo == tipo)]
            ax.scatter(q.sn, q[col], s=26, marker=mk, facecolor=c if lleno else "none", edgecolor=SURF if lleno else c, lw=0.9 if lleno else 1.2, zorder=4)
    rg = R[col]["rangos"]
    ax.errorbar([b["smed"] for b in rg], [b["media"] for b in rg], yerr=[b["ic90"] for b in rg], fmt="o", ms=6.5, color=color_med,
                mfc="white", mew=1.8, capsize=3, lw=1.6, zorder=6)
    t = R[col]["tendencia"]; xs = np.geomspace(0.12, 4.8, 50)
    ax.plot(xs, t["media"] + t["pendiente"] * (np.log(xs) - np.log(P.sn).mean()), color=color_med, lw=1.2, ls=(0, (4, 2)), zorder=5)
    ax.set_xscale("log"); ax.set_xlim(0.1, 5); ax.set_ylim(-16, 16)
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 5]); ax.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "5"]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Residuo: φ′s medido − predicho (°)")
    ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); ax.set_title(titulo, loc="left", fontsize=8.3, color=INK)
    _sup = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
    p_txt = (lambda mm, ee: f"{mm}×10{str(int(ee)).translate(_sup)}")(*f"{t['p']:.0e}".split("e")) if t["p"] < 0.01 else f"{t['p']:.2f}"
    ax.text(0.03, 0.04, f"Tendencia: {t['pendiente']:+.1f}° por unidad de ln σ′n\nr = {t['r']:.2f}, p = {p_txt}", transform=ax.transAxes, fontsize=7, color=INK2,
            va="bottom", bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=1.5))


panel_res(axs[0, 0], "r_prop", f"(a) Curva propuesta (m = 0.85, tope de {TOPE:.0f}°)", VIO)
panel_res(axs[0, 1], "r_m1", "(b) Nivel reajustado con m = 1", INK2)
ax = axs[1, 0]
rng = np.random.default_rng(36); orden = ["Mármol", "Intrusivo", "Mezcla", "Hornfels"]
ax.axhline(0, color=INK2, lw=0.9)
for i, lit in enumerate(orden):
    c, mk = LIT[lit]
    for tipo, lleno in (("TX", True), ("DS", False)):
        q = P[(P.litologia == lit) & (P.tipo == tipo)]
        ax.scatter(i + rng.uniform(-0.18, 0.18, len(q)), q.r_prop, s=24, marker=mk, facecolor=c if lleno else "none", edgecolor=SURF if lleno else c,
                   lw=0.9 if lleno else 1.2, zorder=4)
    m_ = P[P.litologia == lit].r_prop.mean(); ax.plot([i - 0.3, i + 0.3], [m_, m_], color=INK, lw=2.0, zorder=5)
ax.set_xticks(range(4)); ax.set_xticklabels(["Mármol", "Intrusivo", "Mezclas", "Hornfels"]); ax.set_xlim(-0.6, 3.6); ax.set_ylim(-16, 16)
ax.set_ylabel("Residuo de la curva propuesta (°)"); ax.grid(True, axis="y", color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.set_title("(c) Residuo por litología (raya: media)", loc="left", fontsize=8.3, color=INK)
h = [Line2D([], [], ls="", marker=LIT[l][1], color=LIT[l][0], ms=5.5, label=("Mezclas" if l == "Mezcla" else l)) for l in LIT]
h += [Line2D([], [], ls="", marker="o", mfc=INK2, mec=INK2, ms=5.5, label="Lleno: triaxial drenado"),
      Line2D([], [], ls="", marker="o", mfc="none", mec=INK2, ms=5.5, label="Vacío: corte directo"),
      Line2D([], [], ls="", marker="o", mfc="white", mec=VIO, mew=1.8, ms=6, label="Media por rango de σ′n, IC 90 %"),
      Line2D([], [], color=VIO, lw=1.2, ls=(0, (4, 2)), label="Tendencia sobre ln σ′n")]
axs[1, 1].axis("off")
axs[1, 1].legend(handles=h, loc="center left", fontsize=7.2, frameon=False, ncol=1)
fig.subplots_adjust(left=0.1, right=0.98, top=0.96, bottom=0.07)
for ext in ("png", "pdf"):
    fig.savefig(AQ / "figuras_leps2" / f"Fig_residuos.{ext}")
plt.close(fig)
for k in ("r_prop", "r_sintope", "r_m1"):
    t = R[k]["tendencia"]; print(k, {x: round(v, 3) for x, v in t.items()}, [(b["a"], b["n"], round(b["media"], 2), round(b["ic90"], 2)) for b in R[k]["rangos"]])
print("dentro de sets", R["dentro_sets"]["n"], round(R["dentro_sets"]["media"], 2), R["dentro_sets"]["positivas"], "| frente a e", R["frente_e"])
print("escrito a36_residuos.json y figuras_leps2/Fig_residuos.png/.pdf")
