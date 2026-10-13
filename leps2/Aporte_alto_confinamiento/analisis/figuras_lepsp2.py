"""Figures for the Leps-P manuscript, round 2 (English; ASCE: legible in black and white; mathtext subscripts; 600 dpi)."""
import sys, json, warnings, re
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.stats import norm
warnings.filterwarnings("ignore")
AQ = Path(__file__).parent; R = AQ.parent; OUT = R / "figuras" / "lepsp2"; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(R / "leps3"))
import lepsp as L  # noqa: E402
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar  # noqa: E402

INK, INK2, MUTED, GRID, AXIS, BAND = "#0b0b0b", "#52514e", "#8a8984", "#e1e0d9", "#c3c2b7", "#bfbebb"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False, "savefig.dpi": 600, "savefig.bbox": "tight",
                     "hatch.color": "#9a9994", "hatch.linewidth": 0.5})
W1, W2 = 3.5, 7.0
SN_ = r"$\sigma'_n$"; PHI_ = r"$\phi'_s$"


def xlog(ax, t=(0.1, 0.3, 1, 3, 10)):
    ax.set_xscale("log"); ax.set_xticks(t); ax.set_xticklabels([f"{v:g}" for v in t])


def guardar(fig, nm):
    fig.savefig(OUT / f"{nm}.png"); fig.savefig(OUT / f"{nm}.tif", pil_kwargs={"compression": "tiff_lzw"}); plt.close(fig)


d = preparar(load_db(), CLASE); SNMAX = d.sn.max()
EST = json.load(open(AQ / "lepsp_estabilidad2.json", encoding="utf-8"))
# ---------- Fig. 1
fig, ax = plt.subplots(figsize=(W2, 2.4))
ax.hist(d.sn, bins=np.logspace(np.log10(0.05), np.log10(40), 34), color=MUTED, edgecolor="white", lw=0.8, label=f"Calibration tests (n = {len(d)})")
snc = EST["det"]["e=0.65|700|model"]["P50"]["snmax"]
for v, t, ls in [(snc, f"Largest {SN_} on the critical surface, 700 m dump, level foundation ({snc:.1f} MPa)", ":"),
                 (SNMAX, f"Largest {SN_} in the calibration database ({SNMAX:.1f} MPa)", "--"),
                 (700 * 0.021, r"Total vertical stress $\sigma_v$ at the base of a 700 m dump (14.7 MPa; upper bound of $\sigma'_n$)", "-")]:
    ax.axvline(v, color=INK, lw=1.1, ls=ls, label=t)
xlog(ax, (0.1, 0.3, 1, 3, 10, 30)); ax.set_xlim(0.05, 40); ax.set_xlabel(f"Effective normal stress on the failure plane, {SN_} (MPa)"); ax.set_ylabel("Number of tests")
ax.grid(axis="x", visible=False); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), fontsize=6.5, ncol=1)
guardar(fig, "Fig01_stress_coverage")
# ---------- Fig. 2
sn = np.logspace(-1, np.log10(15), 120)
fig, ax = plt.subplots(figsize=(W1, 3.0))
for forma, ls, lab in [("x2", "-", "quadratic form"), ("potencia", "--", "power form")]:
    mat = L.previa("moderada", 0.45, forma, n=40000); q = L.percentiles(sn, mat, (10, 50, 90))
    if forma == "x2":
        ax.fill_between(sn, q[10], q[90], facecolor="none", edgecolor="#9a9994", hatch="////", lw=0, label="80% interval, quadratic form")
    ax.plot(sn, q[50], color=INK, lw=1.4, ls=ls, label=f"Median, {lab}"); ax.plot(sn, q[10], color=INK2, lw=0.8, ls=ls, label=f"10th percentile, {lab}")
ax.axvspan(SNMAX, 15, color="#ecebe8", zorder=0); ax.text(10.9, 55, "No data", ha="center", fontsize=7, color=INK2)
xlog(ax); ax.set_xlim(0.1, 15); ax.set_ylim(24, 58); ax.set_xlabel(f"{SN_} (MPa)"); ax.set_ylabel(f"Secant friction angle, {PHI_} (°)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), fontsize=6.5, ncol=2)
guardar(fig, "Fig02_predictive_band")
# ---------- Fig. 3
A = pd.read_csv(AQ / "lepsp_cv_A.csv"); A = A[(A.agrup == "pub") & (A.esp == "M2")]
bins = [-np.inf, -1, 0, 1, np.inf]; lab = ["<0.37", "0.37–1.0", "1.0–2.75", "≥2.75"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 2.4))
for k, (mu, sd, mk, nm) in enumerate([("mu", "sd", "o", "Leps-P"), ("mu0", "sd0", "s", "Leps 2.0 with constant dispersion")]):
    cov, bel = [], []
    for a, b in zip(bins[:-1], bins[1:]):
        dd = A[(A.x >= a) & (A.x < b)]; z = (dd.y - dd[mu]) / dd[sd]; cov.append(100 * np.mean(np.abs(z) <= 1.2816)); bel.append(100 * np.mean(z < -1.2816))
    xs = np.arange(4) + (k - 0.5) * 0.18
    for a_, v_ in ((a1, cov), (a2, bel)):
        a_.plot(xs, v_, mk, color=INK if k == 0 else INK2, ms=5, mfc=INK if k == 0 else "white", label=nm)
a1.axhline(80, color=INK2, lw=0.8, ls="--"); a2.axhline(10, color=INK2, lw=0.8, ls="--")
for a_, yl, t in [(a1, (60, 100), "(a) Coverage of the 80% interval (%)"), (a2, (0, 20), "(b) Tests below the 10th percentile (%)")]:
    a_.set_xticks(range(4)); a_.set_xticklabels(lab); a_.set_xlabel(f"{SN_} range (MPa)"); a_.set_ylim(*yl); a_.set_ylabel(t)
a1.legend(loc="lower right", fontsize=6.5)
guardar(fig, "Fig03_calibration")
# ---------- Fig. 4: Mode B, CRPS with 95% CI (bootstrap of publications)
B = pd.read_csv(AQ / "lepsp_cv2_B.csv"); rng = np.random.default_rng(3)
crps = lambda mu, s, y: s * ((y - mu) / s * (2 * norm.cdf((y - mu) / s) - 1) + 2 * norm.pdf((y - mu) / s) - 1 / np.sqrt(np.pi))
for v in ("ingenuo m=0.86", "ingenuo m=0.9"):
    b = B[B.variante == v]; B.loc[b.index, "sd"] = b.pub.map({p: np.sqrt(np.mean((b[b.pub != p].y - b[b.pub != p].mu) ** 2)) for p in b.pub.unique()})
filas = [("Prior (no site tests)", "conjunta", "prior"), ("Fit of φ′1, m = 0.90", "ingenuo m=0.9", "c"), ("Fit of φ′1, m = 0.86", "ingenuo m=0.86", "c"),
         ("Leps-P, joint update of θ and m", "conjunta", "c"), ("Leps-P, level-only update", "nivel", "c")]
fig, ax = plt.subplots(figsize=(W1, 2.4))
for i, (nm, v, col) in enumerate(filas):
    b = B[B.variante == v].copy(); b["c"] = crps(b.mu, b.sd, b.y) if col == "c" else crps(b.muA, b.sdA, b.y)
    g = b.groupby("pub").c; pubs = b.pub.unique(); m = b.c.mean()
    bs = [np.concatenate([g.get_group(p).values for p in rng.choice(pubs, len(pubs))]).mean() for _ in range(2000)]
    lo, hi = np.percentile(bs, [2.5, 97.5])
    ax.errorbar(m, i, xerr=[[m - lo], [hi - m]], fmt="o" if "Leps-P" in nm else "s", color=INK, mfc=INK if "level" in nm else "white", ms=5, capsize=2, lw=0.9)
ax.set_yticks(range(len(filas))); ax.set_yticklabels([f[0].replace("φ′1", r"$\phi'_1$") for f in filas]); ax.invert_yaxis()
ax.set_xlabel(r"Mean CRPS of ln $\tau$, held-out tests at $\sigma'_n \geq$ 2 MPa"); ax.grid(axis="y", visible=False)
guardar(fig, "Fig04_site_updating")
# ---------- Fig. 5: specimen-size effect, all groups
E = pd.read_csv(AQ / "lepsp_escala2.csv"); ES = json.load(open(AQ / "lepsp_escala2.json"))
E["similar"] = (E.dlnCu.abs() <= np.log(1.5)) & (E.de.abs() <= 0.05)
E = E.sort_values(["similar", "bD"], ascending=[False, True]).reset_index(drop=True)


def etiqueta(pub, mat):
    m = re.match(r"(.*?)\s*\(?(\d{4})\)?$", pub.strip()); a, y = (m.group(1), m.group(2)) if m else (pub, "")
    a = a.replace(" et al", " et al.").replace("et al..", "et al.").replace(" & ", " and ").strip()
    return f"{a} ({y}), {mat.lower()}"


fig, ax = plt.subplots(figsize=(W1, 4.2))
for i, r in E.iterrows():
    ax.errorbar(np.clip(r.bD, -0.3, 0.3), i, xerr=1.96 * r.se_bD, fmt="o" if r.similar else "s", color=INK if r.similar else INK2,
                mfc=INK if r.similar else "white", ms=4, lw=0.8, capsize=2)
for key, hatch in (("todos", "...."), ("similares Cu≤1.5 Δe≤0.05", "////")):
    c = ES[key]["ci_hk"]; ax.axvspan(c[0], c[1], facecolor="none", edgecolor="#9a9994", hatch=hatch, lw=0)
ax.axvline(0, color=INK2, lw=0.8); ax.axvline(-0.41 * (1 - ES["similares Cu≤1.5 Δe≤0.05"]["m_bar"]), color=INK, lw=0.9, ls=":")
for i, r in E.iterrows():
    if r.bD < -0.3:
        ax.annotate(f"{r.bD:.2f}", xy=(-0.3, i), xytext=(-0.24, i - 0.35), fontsize=5.5, color=INK2, arrowprops=dict(arrowstyle="->", color=INK2, lw=0.6))
ax.set_yticks(range(len(E))); ax.set_yticklabels([etiqueta(p, m) for p, m in zip(E.pub, E.material)], fontsize=5.5)
ax.set_xlabel(r"$\beta_D$, change in ln $\tau$ per unit ln $D_{max}$"); ax.set_xlim(-0.3, 0.3); ax.grid(axis="y", visible=False); ax.invert_yaxis()
ax.legend(handles=[Line2D([], [], marker="o", color=INK, ls="", ms=4, label="Nearly parallel grading, similar density"),
                   Line2D([], [], marker="s", color=INK2, mfc="white", ls="", ms=4, label="Grading or density changes with size"),
                   Patch(facecolor="none", edgecolor="#9a9994", hatch="////", label="95% CI of mean, parallel grading (Hartung–Knapp)"),
                   Patch(facecolor="none", edgecolor="#9a9994", hatch="....", label="95% CI of mean, all groups (Hartung–Knapp)"),
                   Line2D([], [], color=INK, ls=":", label=r"Weibull scaling with $\kappa$ = 0.41")],
          loc="upper center", bbox_to_anchor=(0.3, -0.09), ncol=1, fontsize=6)
guardar(fig, "Fig05_size_effect")
# ---------- Fig. 6: site — (a) laboratory scale with site tests; (b) field scale, dump-average envelope
S = json.load(open(R / "analisis_antamina" / "lepsp_sitio2.json", encoding="utf-8")); SNs = np.array(S["sn"])
EST_ = {"Metamorphic carbonate": ("o", "-"), "Hornfels": ("s", "--"), "Intrusive": ("^", "-."), "Limestone (untested)": ("v", ":"), "Marl (untested)": ("D", (0, (1, 3)))}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 2.9), sharey=True)
lab_ = S["escenarios"]["e=lab|ninguno"]["litologias"]
for k in ("Metamorphic carbonate", "Hornfels", "Intrusive"):
    mk, ls = EST_[k]; a1.plot(SNs, lab_[k]["P50"], color=INK, ls=ls, lw=1.1, marker=mk, markevery=[0], ms=4, mfc="white", label=f"{k}: median; tests ({mk})".replace(f" ({mk})", ""))
    a1.plot(SNs, lab_[k]["P10"], color=INK2, ls=ls, lw=0.6)
for t in S["ensayos"]:
    mk = EST_[t["lit"]][0]; a1.plot(t["sn"], t["phis"], mk, color=INK, mfc=INK if t["usado"] else "white", ms=4, ls="")
a1.plot([], [], "o", color=INK, ms=4, label="Site tests used in updating"); a1.plot([], [], "o", color=INK, mfc="white", ms=4, label="Site tests in conflict (not used)")
a1.plot([], [], color=INK2, lw=0.6, label="Thin lines: 10th percentile")
fld = S["escenarios"]["e=0.65|general"]
for k in EST_:
    mk, ls = EST_[k]; a2.plot(SNs, fld["litologias"][k]["P50"], color=INK2, ls=ls, lw=0.9, label=f"{k}, median")
bm = fld["botadero"]["model"]
a2.fill_between(SNs, bm["P05"], bm["P50"], facecolor="none", edgecolor="#9a9994", hatch="////", lw=0, label="Dump average, 5th–50th percentile")
a2.plot(SNs, bm["P50"], color=INK, lw=1.6, label="Dump average, median")
for a_, t in ((a1, "(a) Laboratory specimens"), (a2, "(b) Placed waste rock (e = 0.65, $D_{max}$ = 1 m)")):
    xlog(a_, (0.1, 0.3, 1, 3, 10)); a_.set_xlim(0.1, 20); a_.set_xlabel(f"{SN_} (MPa)"); a_.set_title(t, loc="left", fontsize=8, color=INK)
    a_.axvspan(4.6, 20, color="#ecebe8", zorder=0)
a1.set_ylabel(f"{PHI_} (°)"); a1.set_ylim(18, 56)
a1.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1); a2.legend(fontsize=5.5, loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
guardar(fig, "Fig06_site_envelopes")
print("figures in", OUT)
