"""Figuras de Leps 3.0 probabilístico: (P1) banda predictiva por clase, (P2) cobertura de intervalos fuera de muestra,
(P3) actualización con ensayos del sitio (set de hornfels de 1 m)."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
warnings.filterwarnings("ignore")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent; FIG = RAIZ / "figuras"
P = json.load(open(AQUI / "leps3_prob_parametros.json")); fe = P["fe"]; Sig = np.array(P["Sig"]); SX = np.array(P["sx"])
PA = 0.1013; S0 = 10 * PA; XB = [-1, 0, 1]
INK, INK2, MUTED, GRID, AXIS, SURF, BAND = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb", "#f0efec"
C1, C2, C3 = "#2a78d6", "#eb6834", "#1baf7a"
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED,
                     "ytick.color": MUTED, "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "figure.facecolor": SURF, "axes.facecolor": SURF, "legend.frameon": False,
                     "savefig.dpi": 220, "savefig.bbox": "tight"})
XC = np.array([-1.5, -0.5, 0.5, 1.5])                     # centros de los tramos de x donde se estimó σε
sex = lambda x: np.interp(x, XC, SX)                       # dispersión dentro del material, interpolada sin escalones
RNG = np.random.default_rng(2026)
from scipy.stats import truncnorm


def muestra_truncada(m0, C, n):
    """(θ, m) ~ N(m0, C) condicionada a m ≤ 1: m de la marginal truncada y θ de la condicional θ | m (exacto)."""
    sm = np.sqrt(C[1, 1]); b = (1.0 - m0[1]) / sm
    m = truncnorm.rvs(-np.inf, b, loc=m0[1], scale=sm, size=n, random_state=RNG)
    th = m0[0] + C[0, 1] / C[1, 1] * (m - m0[1]) + RNG.normal(0, np.sqrt(C[0, 0] - C[0, 1] ** 2 / C[1, 1]), n)
    return th, m


def banda(sn, m0, C, extra_noise=True, n=20000):
    """Percentiles de φ′s por muestreo de (θ, m) ~ N(m0, C) con m ≤ 1 (envolvente no convexa) más el ruido dentro del material."""
    x = np.log(sn / S0)
    th, m = muestra_truncada(m0, C, n)
    y = th[:, None] + m[:, None] * x[None, :] + (RNG.normal(0, 1, (n, 1)) * sex(x)[None, :] if extra_noise else 0)
    ph = np.degrees(np.arctan(S0 * np.exp(y) / sn[None, :]))
    return np.median(ph, 0), np.percentile(ph, 10, 0), np.percentile(ph, 90, 0), np.percentile(ph, 5, 0)


def ticks(ax):
    t = [0.1, 0.3, 1, 3, 10]; ax.set_xticks(t); ax.set_xticklabels([f"{v:g}" for v in t])


# --- P0: esfuerzos de la base de calibración frente a los de un botadero de 700 m
sys.path.insert(0, str(AQUI)); from common import load_db  # noqa: E402
db = load_db(); db = db[(db.s3.isna() | (db.s3 >= 0.06)) & (db.sn > 0) & db.e.notna()]
db = db[db.groupby("Set").sn.transform("size") >= 2]
EJ = json.load(open(AQUI / "ejemplo_leps3.json", encoding="utf-8"))
sn_circ = max(v["snmax"] for v in EJ.values()); sv = 700 * 0.021
fig, ax = plt.subplots(figsize=(6.5, 3.2))
ax.hist(db.sn, bins=np.logspace(np.log10(0.03), np.log10(40), 34), color=C1, edgecolor=SURF, lw=1.5, label=f"Ensayos de la base ({len(db)})")
for v, t, ls, c in [(sn_circ, f"σ′n máximo en la superficie crítica del ejemplo ({sn_circ:.1f} MPa)", ":", INK2),
                    (db.sn.max(), f"Máximo de la base ({db.sn.max():.1f} MPa)", "--", INK2),
                    (sv, f"σv en la base de un botadero de 700 m ({sv:.1f} MPa)", "-", INK)]:
    ax.axvline(v, color=c, lw=1.4, ls=ls, label=t)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=7.5)
ax.set_xscale("log"); ticks(ax); ax.set_xticks([0.03, 0.1, 0.3, 1, 3, 10, 30]); ax.set_xticklabels(["0.03", "0.1", "0.3", "1", "3", "10", "30"])
ax.set_xlim(0.03, 40); ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Número de ensayos"); ax.grid(axis="x", visible=False)
fig.savefig(FIG / "figP0_esfuerzos_base.png"); plt.close(fig)
print("P0:", len(db), "ensayos; σn máx", round(db.sn.max(), 2), "| σn crítico ejemplo", round(sn_circ, 2))

# --- P1: banda predictiva de un material nuevo, clase moderada, e = 0.45
sn = np.logspace(-1, np.log10(15), 200)
m0 = np.array([fe["C(clase)[moderate]"] + fe["e"] * 0.45, fe["x"]])
p50, p10, p90, p05 = banda(sn, m0, Sig)
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.fill_between(sn, p10, p90, color=C1, alpha=0.15, lw=0, label="Intervalo de 80 % (P10–P90)")
ax.plot(sn, p50, color=C1, lw=2, label="Mediana (P50)")
ax.plot(sn, p05, color=C1, lw=1.2, ls=":", label="P05")
ax.axvspan(7.9, 15, color=BAND, zorder=0); ax.text(10.8, 54, "Extrapolación\n(sin datos)", ha="center", color=INK2, fontsize=8)
ax.set_xscale("log"); ticks(ax); ax.set_xlim(0.1, 15); ax.set_ylim(24, 58)
ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Ángulo de fricción secante, φ′s (°)")
ax.legend(loc="lower left", fontsize=8)
fig.savefig(FIG / "figP1_banda_predictiva.png"); plt.close(fig)

# --- P2: cobertura fuera de muestra (modo A) por rango de σ′n
A = pd.read_csv(AQUI / "prob_cv_A.csv")
bins = [-np.inf, -1, 0, 1, np.inf]; lab = ["< 0.37", "0.37–1.0", "1.0–2.75", "2.75–9"]
rows = []
for i, (a, b) in enumerate(zip(bins[:-1], bins[1:])):
    d = A[(A.x >= a) & (A.x < b)]
    for nm, mu, sd in [("Leps 3.0", d.mu, d.sd), ("Envolvente determinística con dispersión constante", d.mu0, d.sd0)]:
        z = (d.y - mu) / sd
        rows.append(dict(rango=lab[i], modelo=nm, cob80=np.mean(np.abs(z) <= 1.2816), bajo10=np.mean(z < -1.2816), n=len(d)))
R = pd.DataFrame(rows)
fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 3.2))
xs = np.arange(4)
for k, (nm, c, mk) in enumerate([("Leps 3.0", C1, "o"), ("Envolvente determinística con dispersión constante", MUTED, "s")]):
    r = R[R.modelo == nm]
    ax.plot(xs + (k - 0.5) * 0.12, 100 * r.cob80, marker=mk, ms=7, color=c, lw=0, label=nm)
    bx.plot(xs + (k - 0.5) * 0.12, 100 * r.bajo10, marker=mk, ms=7, color=c, lw=0, label=nm)
ax.axhline(80, color=INK2, lw=1, ls="--"); bx.axhline(10, color=INK2, lw=1, ls="--")
for a_, t, yl in [(ax, "(a) Cobertura del intervalo de 80 %", (60, 100)), (bx, "(b) Fracción bajo el P10", (0, 20))]:
    a_.set_xticks(xs); a_.set_xticklabels(lab, fontsize=8); a_.set_xlabel("σ′n (MPa)"); a_.set_ylim(*yl)
    a_.set_title(t, loc="left", fontsize=9, color=INK); a_.set_ylabel("%")
fig.tight_layout(w_pad=3, rect=(0, 0.1, 1, 1))
h, l = ax.get_legend_handles_labels(); fig.legend(h, l, loc="lower center", ncol=2, fontsize=8, frameon=False)
fig.savefig(FIG / "figP2_cobertura.png"); plt.close(fig)
R.to_csv(AQUI / "prob_cobertura_tabla.csv", index=False)

# --- P3: actualización con ensayos del sitio (hornfels, probetas de 1 m)
sys.path.insert(0, str(AQUI))
d = pd.read_csv(RAIZ / "analisis_antamina" / "drenados_utilizables.csv")
g = d[d.set_a == "W2022|HF-1.0m-IDIEM-mono"].sort_values("s3")
m_conv = 1.0
Dv, Sm = g.s1 - g.s3, g.s1 + g.s3
sp = Dv / Sm
snd = Sm / 2 - Dv / 2 * sp; taud = Dv / 2 * np.sqrt(1 - sp ** 2)
x = np.log(snd / S0).values; y = np.log(taud / S0).values
m_pr = np.array([fe["C(clase)[moderate]"] + fe["e"] * 0.31, fe["x"]])
Z = np.c_[np.ones_like(x), x]; Rinv = np.diag(1 / sex(x) ** 2); Si = np.linalg.inv(Sig)
# (la posterior se trunca en m ≤ 1 al predecir; ver banda())
Pc = np.linalg.inv(Si + Z.T @ Rinv @ Z); mc = Pc @ (Si @ m_pr + Z.T @ Rinv @ y)
sn = np.logspace(np.log10(0.3), np.log10(15), 200)
a50, a10, a90, _ = banda(sn, m_pr, Sig); b50, b10, b90, _ = banda(sn, mc, Pc)
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.fill_between(sn, a10, a90, color=MUTED, alpha=0.2, lw=0, label="Previa (clase y e): intervalo de 80 %")
ax.plot(sn, a50, color=INK2, lw=1.5, ls="--", label="Previa: mediana")
ax.fill_between(sn, b10, b90, color=C1, alpha=0.2, lw=0, label="Posterior con 3 ensayos del sitio: intervalo de 80 %")
ax.plot(sn, b50, color=C1, lw=2, label="Posterior: mediana")
ax.scatter(snd, np.degrees(np.arctan(taud / snd)), s=40, color=C2, edgecolor=SURF, zorder=5, label="Ensayos (probeta de 1 m)")
ax.set_xscale("log"); ticks(ax); ax.set_xlim(0.3, 15); ax.set_ylim(26, 52)
ax.set_xlabel("σ′n (MPa)"); ax.set_ylabel("Ángulo de fricción secante, φ′s (°)")
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, fontsize=7.5)
fig.savefig(FIG / "figP3_actualizacion.png"); plt.close(fig)
print(R.round(3).to_string(index=False))
print("posterior hornfels 1 m: φ1 =", round(np.degrees(np.arctan(np.exp(mc[0]))), 2), "m =", round(mc[1], 3), "| previa φ1 =", round(np.degrees(np.arctan(np.exp(m_pr[0]))), 2))
