"""Figures for the Leps-P manuscript, round 3 (English; ASCE: legible in black and white, ≥ 7 pt at final size; 600 dpi).
Fig01 stress coverage · Fig02 design envelopes by class and void ratio (bounded form) · Fig03 evidence for bounded
curvature (likelihood ridge; within-material shape test) · Fig04 calibration by stress band and Mode B procedures ·
Fig05 variance decomposition · Fig06 site envelopes · FigS1 specimen-size effect (supplemental)."""
import sys, json, warnings, re
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.stats import norm
warnings.filterwarnings("ignore")
AQ = Path(__file__).parent; R = AQ.parent; OUT = R / "figuras" / "lepsp3"; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(R / "leps3"))
import lepsp as L  # noqa: E402
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar  # noqa: E402

INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#8a8984", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False, "savefig.dpi": 600, "savefig.bbox": "tight",
                     "hatch.color": "#7d7c78", "hatch.linewidth": 0.6, "legend.fontsize": 7})
W1, W2 = 3.5, 7.0; SN_ = r"$\sigma'_n$"; PHI_ = r"$\phi'_s$"; S0 = L.S0


def xlog(ax, t=(0.1, 0.3, 1, 3, 10)):
    ax.set_xscale("log"); ax.set_xticks(t); ax.set_xticklabels([f"{v:g}" for v in t]); ax.minorticks_off()


def guardar(fig, nm):
    fig.savefig(OUT / f"{nm}.png"); fig.savefig(OUT / f"{nm}.tif", pil_kwargs={"compression": "tiff_lzw"}); plt.close(fig)


d = preparar(load_db(), CLASE); SNMAX = d.sn.max()
EST = json.load(open(AQ / "lepsp_estabilidad3.json", encoding="utf-8"))
# ---------- Fig. 1
fig, ax = plt.subplots(figsize=(W2, 2.4))
ax.hist(d.sn, bins=np.logspace(np.log10(0.05), np.log10(40), 34), color=MUTED, edgecolor="white", lw=0.8, label=f"Calibration tests (n = {len(d)})")
snc = EST["acotada e=0.65 γ17|700|model"]["det"]["P50"]["snmax"]
for v, t, ls in [(snc, f"Largest {SN_} on the critical surface, 700 m dump on a level foundation ({snc:.1f} MPa)", ":"),
                 (SNMAX, f"Largest {SN_} in the calibration database ({SNMAX:.1f} MPa)", "--"),
                 (700 * 0.0171, r"Vertical stress at the base of a 700 m dump, $\gamma$ = 17 kN/m$^3$ (12 MPa)", "-")]:
    ax.axvline(v, color=INK, lw=1.1, ls=ls, label=t)
xlog(ax, (0.1, 0.3, 1, 3, 10, 30)); ax.set_xlim(0.05, 40); ax.set_xlabel(f"Effective normal stress on the failure plane, {SN_} (MPa)"); ax.set_ylabel("Number of tests")
ax.grid(axis="x", visible=False); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=1)
guardar(fig, "Fig01_stress_coverage")
# ---------- Fig. 2: design envelopes (median and 5th percentile of the mean envelope), bounded form
sn = np.logspace(-1, np.log10(15), 100); ES = {0.30: "-", 0.45: "--", 0.65: ":"}
fig, axs = plt.subplots(1, 3, figsize=(W2, 2.9), sharey=True); TAB = []
for ax, (cal, nom) in zip(axs, (("buena", "Good"), ("moderada", "Moderate"), ("baja", "Low"))):
    for e, ls in ES.items():
        q = L.percentiles(sn, L.previa(cal, e, n=40000, seed=1), (5, 50), puntual=False)
        ax.plot(sn, q[50], color=INK, lw=1.4, ls=ls); ax.plot(sn, q[5], color=INK2, lw=0.8, ls=ls)
    ax.axvspan(SNMAX, 15, color="#ecebe8", zorder=0); xlog(ax, (0.1, 0.3, 1, 3, 10)); ax.set_xlim(0.1, 15)
    ax.set_title(f"({'abc'[['Good', 'Moderate', 'Low'].index(nom)]}) {nom} rock quality", loc="left", fontsize=8, color=INK); ax.set_xlabel(f"{SN_} (MPa)")
axs[0].set_ylabel(f"Secant friction angle, {PHI_} (°)"); axs[0].set_ylim(18, 60)
axs[2].text(10.5, 57, "Beyond\ndata", ha="center", va="top", fontsize=7, color=INK2)
hs = [Line2D([], [], color=INK, ls=ls, lw=1.4, label=f"e = {e:.2f}") for e, ls in ES.items()] + \
     [Line2D([], [], color=INK, lw=1.4, label="Median"), Line2D([], [], color=INK2, lw=0.8, label="5th percentile (characteristic value)")]
fig.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=5)
guardar(fig, "Fig02_design_envelopes")
# ---------- Fig. 3: (a) likelihood ridge; (b) within-material shape test by publication
M3 = json.load(open(AQ / "lepsp_mcmc3.json", encoding="utf-8")); C = M3["acotada_cresta"]
PH, ZE, ML = np.array(C["grilla_phi"]), np.array(C["grilla_zeta"]), np.array(C["ml"]); dML = ML - ML.max()
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 2.8), gridspec_kw=dict(width_ratios=[1, 1.15]))
cs = a1.contour(ZE, PH, dML, levels=[-6, -3], colors=[INK2, INK], linewidths=[0.9, 1.2], linestyles=["--", "-"])
a1.clabel(cs, fmt={-6: "−6", -3: "−3"}, fontsize=7)
i, j = np.unravel_index(np.argmax(ML), ML.shape); a1.plot(ZE[j], PH[i], "o", color=INK, ms=5)
a1.set_xlabel(r"Decay rate, $\zeta$"); a1.set_ylabel(r"Asymptotic angle, $\phi'_{cs}$ (°)"); a1.set_title("(a) Profile log-likelihood relative to maximum", loc="left", fontsize=8, color=INK)
B = pd.read_csv(AQ / "lepsp_acotada_B.csv")
cr = lambda mu, s, y: s * ((y - mu) / s * (2 * norm.cdf((y - mu) / s) - 1) + 2 * norm.pdf((y - mu) / s) - 1 / np.sqrt(np.pi))
B["d"] = cr(B.mu_b, B.sd_b, B.y) - cr(B.mu_q, B.sd_q, B.y)
P = B.groupby("pub").agg(d=("d", "mean"), n=("d", "size")).sort_values("d").reset_index()
for k, r in P.iterrows():
    a2.plot(r.d * 1000, k, "o", color=INK if r.d < 0 else INK2, mfc=INK if r.d < 0 else "white", ms=3 + 0.6 * np.sqrt(r.n))
a2.axvline(0, color=INK2, lw=0.8)
a2.set_yticks(range(len(P))); a2.set_yticklabels([re.sub(r"([A-Za-z])\(", r"\1 (", re.sub(r"\s+", " ", p)) for p in P.pub], fontsize=7); a2.grid(axis="y", visible=False)
a2.set_xlabel(r"$\Delta$CRPS (×10$^{-3}$), bounded − quadratic"); a2.set_title("(b) Within-material extrapolation, by publication", loc="left", fontsize=8, color=INK)
guardar(fig, "Fig03_bounded_evidence")
# ---------- Fig. 4: (a) 80% coverage by stress band; (b) Mode B procedures, CRPS with 95% CI
A3 = pd.read_csv(AQ / "lepsp_cv3_A.csv"); A2 = pd.read_csv(AQ / "lepsp_cv_A.csv"); A2 = A2[(A2.agrup == "pub") & (A2.esp == "M2")]
M = A3.merge(A2[["pub", "Set", "x", "y", "mu", "sd", "mu0", "sd0"]], on=["pub", "Set", "x", "y"], suffixes=("", "_q"))
bins = np.log(np.array([1e-9, 0.37, 1.0, 2.75, 1e9]) / S0); lab = ["<0.37", "0.37–1.0", "1.0–2.75", "≥2.75"]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 2.7), gridspec_kw=dict(width_ratios=[1, 1.1], wspace=1.05))
for k, (mu, sd, mk, nm) in enumerate([("mu", "sd", "o", "Leps-P, bounded form"), ("mu_q", "sd_q", "^", "Leps-P, quadratic form"), ("mu0", "sd0", "s", "Leps 2.0, constant dispersion")]):
    cov = []
    for a, b in zip(bins[:-1], bins[1:]):
        dd = M[(M.x >= a) & (M.x < b)]; z = (dd.y - dd[mu]) / dd[sd]; cov.append(100 * np.mean(np.abs(z) <= 1.2816))
    a1.plot(np.arange(4) + (k - 1) * 0.17, cov, mk, color=INK if k == 0 else INK2, mfc=INK if k == 0 else "white", ms=5, label=nm)
a1.axhline(80, color=INK2, lw=0.8, ls="--"); a1.set_xticks(range(4)); a1.set_xticklabels(lab); a1.set_xlabel(f"{SN_} range (MPa)")
a1.set_ylim(60, 100); a1.set_ylabel("Coverage of the 80% interval (%)"); a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22)); a1.set_title("(a) No site tests (Mode A)", loc="left", fontsize=8, color=INK)
Bv = pd.read_csv(AQ / "lepsp_cv3_B.csv"); rng = np.random.default_rng(3)
filas = [("Prior, no site tests", "previa"), ("Fit of φ′1, $m$ = 0.90", "ingenuo_m090"), ("Fit of φ′1, $m$ from training data", "ingenuo_mtr"),
         ("Joint update of level and slope", "conjunta"), ("Level-only update after conflict check", "procedimiento"), ("Level-only update (prespecified)", "nivel")]
for i, (nm, v) in enumerate(filas):
    b = Bv[Bv.variante == v].copy(); b["c"] = cr(b.mu, b.sd, b.y); g = b.groupby("pub").c; pubs = b.pub.unique()
    bs = [np.concatenate([g.get_group(p).values for p in rng.choice(pubs, len(pubs))]).mean() for _ in range(2000)]
    m = b.c.mean(); lo, hi = np.percentile(bs, [2.5, 97.5])
    a2.errorbar(m, i, xerr=[[m - lo], [hi - m]], fmt="o", color=INK, mfc=INK if v == "nivel" else "white", ms=5, capsize=2, lw=0.9)
a2.set_yticks(range(len(filas))); a2.set_yticklabels([f[0].replace("φ′1", r"$\phi'_1$") for f in filas], fontsize=7); a2.invert_yaxis(); a2.grid(axis="y", visible=False)
a2.set_xlabel(r"Mean CRPS of ln $\tau$ ($\sigma'_n \geq$ 2 MPa)"); a2.set_title("(b) With site tests at low stress (Mode B)", loc="left", fontsize=8, color=INK)
guardar(fig, "Fig04_validation")
# ---------- Fig. 5: variance decomposition (bounded form, field scale)
V = json.load(open(AQ / "lepsp_varianza.json", encoding="utf-8"))
comp = [("escala_campo", "Specimen size to field scale", "////"), ("material", "Material (between sets)", "...."), ("publicacion", "Publication or laboratory", "xxx"),
        ("cresta", r"Asymptote ($\phi'_{cs}$, $\zeta$)", ""), ("efectos_fijos", "Fixed effects", "")]
fig, ax = plt.subplots(figsize=(W1, 2.5)); keys = [k for k in V if k.startswith("low")]
for i, k in enumerate(keys):
    left = 0; tot = V[k]["total"]
    for c, nm, h in comp:
        w = 100 * V[k]["comp"][c] / tot
        ax.barh(i, w, left=left, color="white" if h else (MUTED if c == "cresta" else INK2), edgecolor=INK, hatch=h, lw=0.6, height=0.6, label=nm if i == 0 else None); left += w
ax.set_yticks(range(len(keys))); ax.set_yticklabels([f"{SN_} = {k.split('=')[-1]} MPa" for k in keys]); ax.invert_yaxis(); ax.set_xlim(0, 100)
ax.set_xlabel(r"Share of the variance of ln $\tau$ (%)"); ax.grid(axis="y", visible=False)
ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.25), ncol=2)
guardar(fig, "Fig05_variance")
# ---------- Fig. 6: site envelopes (bounded form)
S = json.load(open(R / "analisis_antamina" / "lepsp_sitio3.json", encoding="utf-8")); SNs = np.array(S["sn"])
EST_ = {"A": ("o", "-"), "B": ("s", "--"), "C": ("^", "-."), "D": ("v", ":"), "E": ("D", (0, (1, 3)))}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 3.0), sharey=True)
lab_ = S["escenarios"]["e=lab|ninguno"]["litologias"]
for k in "ABC":
    mk, ls = EST_[k]; a1.plot(SNs, lab_[k]["P50"], color=INK, ls=ls, lw=1.1, label=f"Rock type {k}, median"); a1.plot(SNs, lab_[k]["P05"], color=INK2, ls=ls, lw=0.6)
for t in S["ensayos"]:
    a1.plot(t["sn"], t["phis"], EST_[t["lit"]][0], color=INK, mfc=INK if t["usado"] else "white", ms=4.5, ls="")
for k in "ABC":
    a1.plot([], [], EST_[k][0], color=INK, ms=4.5, ls="", label=f"Tests, rock type {k} (open: flagged)")
fld = S["escenarios"]["e=0.65|general"]
for k in EST_:
    a2.plot(SNs, fld["litologias"][k]["P50"], color=INK2, ls=EST_[k][1], lw=0.9, label=f"Rock type {k}{' (untested)' if k in 'DE' else ''}, median")
bm = fld["botadero"]["model"]
a2.fill_between(SNs, bm["P05"], bm["P50"], facecolor="none", edgecolor="#7d7c78", hatch="////", lw=0, label="Dump average, 5th–50th percentile")
a2.plot(SNs, bm["P50"], color=INK, lw=1.6, label="Dump average, median")
for a_, t in ((a1, "(a) Laboratory specimens"), (a2, "(b) Placed waste rock (e = 0.65, $D_{max}$ = 1 m)")):
    xlog(a_); a_.set_xlim(0.1, 20); a_.set_xlabel(f"{SN_} (MPa)"); a_.set_title(t, loc="left", fontsize=8, color=INK); a_.axvspan(4.6, 20, color="#ecebe8", zorder=0)
a1.set_ylabel(f"{PHI_} (°)"); a1.set_ylim(18, 56)
a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1); a2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
guardar(fig, "Fig06_site_envelopes")
# ---------- Fig. S1: specimen-size effect (supplemental)
E = pd.read_csv(AQ / "lepsp_escala3.csv").sort_values("bD").reset_index(drop=True); ES3 = json.load(open(AQ / "lepsp_escala3.json", encoding="utf-8"))
fig, ax = plt.subplots(figsize=(W2 * 0.75, 4.2))
for i, r in E.iterrows():
    ax.errorbar(np.clip(r.bD, -0.3, 0.3), i, xerr=1.96 * r.se_bD, fmt="o" if r.R >= 2 else "s", color=INK if r.R >= 2 else INK2, mfc=INK if r.R >= 2 else "white", ms=4, lw=0.8, capsize=2)
c = ES3["publicaciones R ≥ 2"]["ci"][0]; ax.axvspan(c[0], c[1], facecolor="none", edgecolor="#7d7c78", hatch="////", lw=0); ax.axvline(0, color=INK2, lw=0.8)
for i, r in E.iterrows():
    if r.bD < -0.3:
        ax.annotate(f"{r.bD:.2f}", xy=(-0.3, i), xytext=(-0.22, i - 0.3), fontsize=7, color=INK2, arrowprops=dict(arrowstyle="->", color=INK2, lw=0.6))
ax.set_yticks(range(len(E))); ax.set_yticklabels([f"{p.strip()}, {m.lower()}" for p, m in zip(E.pub, E.material)], fontsize=7)
ax.set_xlabel(r"$\beta_D$, change in ln $\tau$ per unit ln $D_{max}$"); ax.set_xlim(-0.3, 0.3); ax.grid(axis="y", visible=False); ax.invert_yaxis()
ax.legend(handles=[Line2D([], [], marker="o", color=INK, ls="", ms=4, label="Size ratio ≥ 2"), Line2D([], [], marker="s", color=INK2, mfc="white", ls="", ms=4, label="Size ratio < 2"),
                   Patch(facecolor="none", edgecolor="#7d7c78", hatch="////", label="95% CI of mean across publications")], loc="upper center", bbox_to_anchor=(0.3, -0.09))
guardar(fig, "FigS1_size_effect")
print("figures in", OUT)
