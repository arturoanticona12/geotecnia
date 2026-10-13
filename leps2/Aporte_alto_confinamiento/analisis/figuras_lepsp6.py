"""Figures for the HiBER manuscript, round 6 (cleaned data, extended model, validation by laboratory). Round 5 (main: Fig01 design envelopes, Fig02 validation, Fig03 site; supplement: S1 coverage, S2 volumetric/breakage from lepsp_diag_alta.py, S3 profile likelihood, S4 size effect, S5 variance). Round 4 header: (English; ASCE: legible in black and white, ≥ 8 pt at final width; 600 dpi;
RGB TIFF). Main: Fig01 design envelopes · Fig02 likelihood ridge · Fig03 validation · Fig04 site envelopes.
Supplement: FigS1 stress coverage · FigS2 volumetric strain and breakage (lepsp_diag_alta.py) · FigS3 variance · FigS4 size effect."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from scipy.stats import norm
from PIL import Image
warnings.filterwarnings("ignore")
AQ = Path(__file__).parent; R = AQ.parent; OUT = R / "figuras" / "lepsp6"; OUT.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(AQ)); sys.path.insert(0, str(R / "leps3"))
import lepsp as L  # noqa: E402
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar  # noqa: E402
from lepsp_r6 import datos  # noqa: E402

INK, INK2, MUTED, GRID, AXIS = "#0b0b0b", "#52514e", "#8a8984", "#e1e0d9", "#c3c2b7"
plt.rcParams.update({"font.family": "Arial", "font.size": 8, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": INK2, "ytick.color": INK2,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.5, "axes.spines.top": False, "axes.spines.right": False,
                     "figure.facecolor": "white", "axes.facecolor": "white", "legend.frameon": False, "savefig.dpi": 600, "savefig.bbox": "tight",
                     "hatch.color": "#7d7c78", "hatch.linewidth": 0.6, "legend.fontsize": 8})
W2 = 7.0; SN_ = r"$\sigma'_n$"; PHI_ = r"$\phi'_s$"; S0 = L.S0
cr = lambda mu, s, y: s * ((y - mu) / s * (2 * norm.cdf((y - mu) / s) - 1) + 2 * norm.pdf((y - mu) / s) - 1 / np.sqrt(np.pi))


def xlog(ax, t=(0.1, 0.3, 1, 3, 10)):
    ax.set_xscale("log"); ax.set_xticks(t); ax.set_xticklabels([f"{v:g}" for v in t]); ax.minorticks_off()


def guardar(fig, nm):
    fig.savefig(OUT / f"{nm}.png"); fig.savefig(OUT / f"{nm}_rgba.tif"); plt.close(fig)
    Image.open(OUT / f"{nm}_rgba.tif").convert("RGB").save(OUT / f"{nm}.tif", compression="tiff_lzw"); (OUT / f"{nm}_rgba.tif").unlink()


d = datos(); SNMAX = d.sn.max()
# ---------- Fig. 1: design envelopes (median thick, 5th percentile thin), bounded form
sn = np.logspace(-1, np.log10(15), 100); ES = {0.30: "-", 0.45: "--", 0.65: ":"}
fig, axs = plt.subplots(1, 3, figsize=(W2, 3.0), sharey=True)
for ax, (cal, nom) in zip(axs, (("buena", "Good"), ("moderada", "Moderate"), ("baja", "Low"))):
    for e, ls in ES.items():
        q = L.percentiles(sn, L.previa(cal, e, n=40000, seed=1), (5, 50), puntual=False)
        ax.plot(sn, q[50], color=INK, lw=1.8, ls=ls); ax.plot(sn, q[5], color=INK2, lw=0.8, ls=ls)
    xlog(ax); ax.set_xlim(0.1, 8.0)          # límite de uso (revisores B3, E7)
    ax.set_title(f"({'abc'[['Good', 'Moderate', 'Low'].index(nom)]}) {nom} rock quality", loc="left", fontsize=8, color=INK); ax.set_xlabel(f"{SN_} (MPa)")
axs[0].set_ylabel(f"Secant friction angle, {PHI_} (°)"); axs[0].set_ylim(22, 60)
hs = [Line2D([], [], color=MUTED, ls=ls, lw=1.2, label=f"e = {e:.2f}") for e, ls in ES.items()] + \
     [Line2D([], [], color=INK, lw=1.8, label="Median (thick)"), Line2D([], [], color=INK2, lw=0.8, label="5th percentile (thin)")]
fig.legend(handles=hs, loc="upper center", bbox_to_anchor=(0.5, 0.0), ncol=5)
guardar(fig, "Fig01_design_envelopes")
# ---------- Fig. S3: true profile likelihood of the asymptote (ML, ζ0 and ψ refitted)
PRf = json.load(open(AQ / "lepsp_perfil6.json", encoding="utf-8")); pp = sorted(PRf["perfil"], key=lambda r: r["phi"])
ph_ = np.array([r["phi"] for r in pp]); dm_ = np.array([r["ml"] for r in pp]) - PRf["ml_max"]
fig, ax = plt.subplots(figsize=(3.5, 2.6))
ax.plot(ph_, dm_, "o-", color=INK, ms=3.5, lw=1.2); ax.axhline(-1.92, color=INK2, lw=0.8, ls="--"); ax.text(1, -1.6, "−1.92 (95%)", color=INK2, fontsize=8)
ax.axhline(-3, color=INK2, lw=0.8, ls=":"); ax.text(1, -4.1, "−3", color=INK2, fontsize=8)
ax.set_xlabel(r"Asymptotic angle, $\phi'_\infty$ (°)"); ax.set_ylabel("Profile log-likelihood relative to maximum"); ax.set_ylim(-20, 1)
guardar(fig, "FigS3_profile_likelihood")
# ---------- Fig. 3: validation (a) 80% coverage by stress band (Mode A); (b) Mode B procedures
M = pd.read_csv(AQ / "lepsp_cv6_A.csv"); M = M[~M.cens].reset_index(drop=True)          # censurados: cota inferior, no se puntúan
bins = np.log(np.array([1e-9, 0.5, 1.0, 2.0, 1e9]) / S0); lab = ["<0.5", "0.5–1.0", "1.0–2.0", "≥2.0"]        # bandas fijadas de antemano (revisor D2)
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 2.9), gridspec_kw=dict(width_ratios=[1, 1.1], wspace=1.0))
for k, (mu, sd, mk, nm) in enumerate([("mu_acotada", "sd_acotada", "o", "HiBER, bounded form"), ("mu_cuadratica", "sd_cuadratica", "^", "HiBER, quadratic form"), ("mu0", "sd0", "s", "Leps 2.0 envelope, constant dispersion")]):
    cov = []
    for a, b in zip(bins[:-1], bins[1:]):
        dd = M[(M.x >= a) & (M.x < b)]; z = (dd.y - dd[mu]) / dd[sd]; cov.append(100 * np.mean(np.abs(z) <= 1.2816))
    a1.plot(np.arange(4) + (k - 1) * 0.17, cov, mk, color=INK if k == 0 else INK2, mfc=INK if k == 0 else "white", ms=5, label=nm)
a1.axhline(80, color=INK2, lw=0.8, ls="--"); a1.set_xticks(range(4)); a1.set_xticklabels(lab); a1.set_xlabel(f"{SN_} range (MPa)")
a1.set_ylim(60, 100); a1.set_ylabel("Coverage of the 80% interval (%)"); a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22))
a1.set_title("(a) No site tests (Mode A)", loc="left", fontsize=8, color=INK)
Bv = pd.read_csv(AQ / "lepsp_cv6_B.csv"); rng = np.random.default_rng(3)
filas = [("Prior, no site tests", "previa"), ("Fit of $\\phi'_1$, $m$ = 0.90", "ingenuo_m090"), ("Fit of $\\phi'_1$, $m$ from training data", "ingenuo_mtr"),
         ("Joint update of both effects", "conjunta"), ("Level update of each set (design procedure)", "nivel"), ("Flagged sets discarded, shared laboratory", "sitio")]
for i, (nm, v) in enumerate(filas):
    b = Bv[Bv.variante == v].copy(); b["c"] = cr(b.mu, b.sd, b.y); g = b.groupby("lab").c; pubs = b.lab.unique()
    bs = [np.concatenate([g.get_group(p).values for p in rng.choice(pubs, len(pubs))]).mean() for _ in range(2000)]
    m = b.c.mean(); lo, hi = np.percentile(bs, [2.5, 97.5])
    a2.errorbar(m, i, xerr=[[m - lo], [hi - m]], fmt="o", color=INK, mfc=INK if v == "nivel" else "white", ms=5, capsize=2, lw=0.9)
a2.set_yticks(range(len(filas))); a2.set_yticklabels([f[0] for f in filas]); a2.invert_yaxis(); a2.grid(axis="y", visible=False)
a2.set_xlabel(r"Mean CRPS of ln $\tau$ ($\sigma'_n \geq$ 2 MPa)"); a2.set_title("(b) Site tests at low stress (Mode B)", loc="left", fontsize=8, color=INK)
guardar(fig, "Fig02_validation")
# ---------- Fig. 4: site envelopes
S = json.load(open(R / "analisis_antamina" / "lepsp_sitio6.json", encoding="utf-8")); SNs = np.array(S["sn"])
EST_ = {"A": ("o", "-"), "B": ("s", "--"), "C": ("^", "-."), "D": ("v", ":"), "E": ("D", ":")}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(W2, 3.1), sharey=True)
lab_ = S["escenarios"]["e=lab|ninguno"]["litologias"]
for k in "ABC":
    mk, ls = EST_[k]; a1.plot(SNs, lab_[k]["P50"], color=INK, ls=ls, lw=1.4, label=f"Rock type {k}, median"); a1.plot(SNs, lab_[k]["P05"], color=INK2, ls=ls, lw=0.6)
a1.plot([], [], color=INK2, lw=0.6, label="5th percentiles (thin)")
for t in S["ensayos"]:
    a1.plot(t["sn"], t["phis"], EST_[t["lit"]][0], color=INK, mfc=INK if t["usado"] else "white", ms=4.5, ls="")
for k in "ABC":
    a1.plot([], [], EST_[k][0], color=INK, mfc="white" if k == "B" else INK, ms=4.5, ls="", label=f"Tests, rock type {k}")
a1.plot([], [], "o", color=INK, mfc="white", ms=4.5, ls="", label="Open symbols: flagged, not used")
fld = S["escenarios"]["e=0.65|general"]
for k in EST_:
    mk, ls = EST_[k]
    a2.plot(SNs, fld["litologias"][k]["P50"], color=INK2, ls=ls, lw=0.9, marker=mk if k in "DE" else None, markevery=8, ms=4, mfc="white",
            label=f"Rock type {k}{' (untested, e = 0.80)' if k == 'E' else (' (untested)' if k == 'D' else '')}, median")
bm = fld["botadero"]["model"]
a2.fill_between(SNs, bm["P05"], bm["P50"], facecolor="#ecebe8", edgecolor="none", label="Dump average, 5th–50th percentile")
a2.plot(SNs, bm["P50"], color=INK, lw=1.8, label="Dump average, median"); a2.plot(SNs, bm["P05"], color=INK, lw=0.8)
for a_, t in ((a1, "(a) Laboratory specimens"), (a2, "(b) Placed waste rock (e = 0.65, $D_{max}$ = 1 m)")):
    xlog(a_); a_.set_xlim(0.1, 8.0); a_.set_xlabel(f"{SN_} (MPa)"); a_.set_title(t, loc="left", fontsize=8, color=INK); a_.axvline(4.6, color=MUTED, lw=0.8, ls=(0, (2, 2)))
a1.set_ylabel(f"{PHI_} (°)"); a1.set_ylim(20, 56)
a1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1); a2.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
guardar(fig, "Fig03_site_envelopes")
# ---------- Fig. S1: stress coverage
fig, ax = plt.subplots(figsize=(W2, 2.4))
ax.hist(d.sn, bins=np.logspace(np.log10(0.05), np.log10(40), 34), color=MUTED, edgecolor="white", lw=0.8, label=f"Calibration tests (n = {len(d)})")
for v, t, ls in [(SNMAX, f"Largest {SN_} in the calibration database ({SNMAX:.1f} MPa)", "--"),
                 (700 * 0.0172, r"Vertical stress at the base of a 700 m dump, $\gamma$ = 17.2 kN/m$^3$ (12 MPa)", "-")]:
    ax.axvline(v, color=INK, lw=1.1, ls=ls, label=t)
xlog(ax, (0.1, 0.3, 1, 3, 10, 30)); ax.set_xlim(0.05, 40); ax.set_xlabel(f"Effective normal stress on the failure plane, {SN_} (MPa)"); ax.set_ylabel("Number of tests")
ax.grid(axis="x", visible=False); ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.25), ncol=1)
guardar(fig, "FigS1_stress_coverage")
# ---------- Fig. S3: variance decomposition
V = json.load(open(AQ / "lepsp_varianza6.json", encoding="utf-8"))
comp = [("escala_campo", "Specimen size to field scale", "////"), ("material", "Material (between sets)", "...."), ("publicacion", "Publication or laboratory", "xxx"),
        ("cresta", r"Asymptote and decay ($\phi'_\infty$, $\zeta_0$)", ""), ("efectos_fijos", "Fixed effects", "")]
fig, ax = plt.subplots(figsize=(3.5, 2.6)); keys = [k for k in V if k.startswith("low") and k.endswith("D=100 mm")]
for i, k in enumerate(keys):
    left = 0; tot = V[k]["total"]
    for c, nm, h in comp:
        w = 100 * V[k]["comp"][c] / tot
        ax.barh(i, w, left=left, color="white" if h else (MUTED if c == "cresta" else INK2), edgecolor=INK, hatch=h, lw=0.6, height=0.6, label=nm if i == 0 else None); left += w
ax.set_yticks(range(len(keys))); ax.set_yticklabels([f"{SN_} = {k.split('σ′n=')[1].split(' ')[0]} MPa" for k in keys]); ax.invert_yaxis(); ax.set_xlim(0, 100)
ax.set_xlabel(r"Share of the variance of ln $\tau$ (%)"); ax.grid(axis="y", visible=False); ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.25), ncol=1)
guardar(fig, "FigS5_variance")
# ---------- Fig. S4: specimen-size effect
E = pd.read_csv(AQ / "lepsp_escala6.csv").sort_values("bD").reset_index(drop=True); ES3 = json.load(open(AQ / "lepsp_escala6.json", encoding="utf-8"))
fig, ax = plt.subplots(figsize=(W2 * 0.8, 4.4))
for i, r in E.iterrows():
    ax.errorbar(np.clip(r.bD, -0.3, 0.3), i, xerr=1.96 * r.se_bD, fmt="o" if r.R >= 2 else "s", color=INK if r.R >= 2 else INK2, mfc=INK if r.R >= 2 else "white", ms=4, lw=0.8, capsize=2)
c = ES3["laboratorios R ≥ 2"]["ci"][0]; ax.axvspan(c[0], c[1], facecolor="none", edgecolor="#7d7c78", hatch="////", lw=0); ax.axvline(0, color=INK2, lw=0.8)
for i, r in E.iterrows():
    if r.bD < -0.3:
        ax.annotate(f"{r.bD:.2f}".replace("-", "−"), xy=(-0.3, i), xytext=(-0.22, i - 0.3), fontsize=8, color=INK2, arrowprops=dict(arrowstyle="->", color=INK2, lw=0.6))
ax.set_yticks(range(len(E))); ax.set_yticklabels([f"{p.strip().replace(' & ', ' and ')}, {m.lower()}" for p, m in zip(E.pub, E.material)], fontsize=8)
ax.set_xlabel(r"$\beta_D$, change in ln $\tau$ per unit ln $D_{max}$"); ax.set_xlim(-0.3, 0.3); ax.grid(axis="y", visible=False); ax.invert_yaxis()
ax.legend(handles=[Line2D([], [], marker="o", color=INK, ls="", ms=4, label="Size ratio ≥ 2"), Line2D([], [], marker="s", color=INK2, mfc="white", ls="", ms=4, label="Size ratio < 2"),
                   Patch(facecolor="none", edgecolor="#7d7c78", hatch="////", label="95% CI of mean across laboratories")], loc="upper center", bbox_to_anchor=(0.3, -0.09))
guardar(fig, "FigS4_size_effect")
print("figures in", OUT)
