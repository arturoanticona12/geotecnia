"""Figuras del memorándum (revisión 6, 2026-10-10). Regla del usuario: en color solo la data usada y el resultado que la figura
muestra; en grises las referencias y lo no usado; una figura, una pregunta.
Fig. 1: ensayos del ajuste (color por litología; lleno triaxial, vacío corte directo) y la curva recomendada (opción 2, m = 0.90)
        con su banda de incertidumbre (nivel, curvatura y margas y caliza). Sin opción 1 ni líneas de curvatura (van en tablas).
Fig. 1b: zona de mármol: ensayos de mármol en color y su curva; el resto de los ensayos y la opción 2 en gris.
Fig. 2: τ–σ′n de la opción 2 con su banda y los ensayos; clases de Leps 2.0 y cota de Hawley y Cunning (2017) en gris.
Fig. 3: perfiles de e y su efecto en la opción 2: base (e = 0.65) y perfiles A y V en color; e = 0.45 y 0.55 en gris.
Paleta validada (dataviz, modo claro): litologías #2a78d6, #eb6834, #1baf7a, #eda100 y curva propuesta #4a3aa7 (PASS; contraste
< 3:1 en verde y amarillo: la identidad la llevan también la forma del marcador y la Tabla 2)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.ticker
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; OUT = AQ / "figuras_leps2"; OUT.mkdir(exist_ok=True)
C = json.load(open(AQ / "a10_leps2_curvatura.json", encoding="utf-8")); P = pd.read_csv(AQ / "a10_puntos.csv")
A12 = json.load(open(AQ / "a12_leps2_ponderada.json", encoding="utf-8")); C2 = A12["curvas"]
EC = json.load(open(AQ / "a13_perfil_e.json", encoding="utf-8"))["e_top"]       # e base de colocación (0.45 desde el 2026-10-10)
INK, INK2, MUTED, GRID, SURF, GRIS = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb", "#b9b8b2"
VIO, VIO_B = "#4a3aa7", "#e3e0f3"                                # curva propuesta y su banda
LIT = {"Mármol": ("#2a78d6", "o"), "Hornfels": ("#eb6834", "s"), "Intrusivo": ("#1baf7a", "^"), "Mezcla": ("#eda100", "D")}
LIT_TXT = {"Mármol": "Mármol", "Hornfels": "Hornfels", "Intrusivo": "Intrusivo", "Mezcla": "Mezclas (Golder Associates Perú, 2021; Anddes Geolab, 2024)"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
# 2026-10-12: curva propuesta simple, m = 0.85 (leps_compuesta con m_a = m_h, a33). Puntos: e0 con D854 (a8); triaxiales a σ′n–τ con
# la m de la curva (Ec. 16); normalización a e base: φ′s − 20·(0.45 − e0) (Ec. 27 sobre φ′1)
sys.path.insert(0, str(AQ)); import leps_compuesta as LC  # noqa: E402
A33 = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8")); PC = A33["parametros"]
_d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False); _tx = _d.tipo == "TX"
_sn = _d.sn_ds.values.copy(); _tau = _d.tau_ds.values.copy()
_D, _S = (_d.s1 - _d.s3).values[_tx], (_d.s1 + _d.s3).values[_tx]; _m = PC["m_a"]
_sp = _D / _S if abs(_m - 1) < 1e-9 else (np.sqrt(4 * _m * (_m - 1) * _D ** 2 + _S ** 2) - _S) / (2 * (_m - 1) * _D)
_sn[_tx] = _S / 2 - _D / 2 * _sp; _tau[_tx] = _D / 2 * np.sqrt(1 - _sp ** 2)
P = pd.DataFrame(dict(litologia=_d.litologia.values, tipo=_d.tipo.values, sn=_sn, e=_d.e0_adoptado.values,
                      phis=np.degrees(np.arctan(_tau / _sn))))
P["phis_e065"] = P.phis - 20.0 * (EC - P.e)          # nombre histórico: φ′s a la e base
sn = np.array(A33["sn"]); SNX = float(P[P.tipo == "TX"].sn.max())
SNW = json.load(open(AQ / "a19_m_covariables.json", encoding="utf-8"))["base_sn_max"]   # σ′n máximo de la base mundial de Leps 2.0
XMAX = 15.0


def zonas(ax, log=True, rotulos=True):
    """Zonas de respaldo de datos: sobre SNX sin ensayos de Antamina; sobre SNW fuera de la base mundial."""
    ax.axvspan(SNX, SNW, color="#efeee9", lw=0, zorder=0)
    ax.axvspan(SNW, XMAX, facecolor="none", edgecolor="#d2d1cb", hatch="///", lw=0, zorder=0)
    if rotulos:
        y = ax.get_ylim()[1]
        ax.text((SNX * SNW) ** 0.5 if log else (SNX + SNW) / 2, y, "Sin ensayos\nde Antamina", fontsize=6.5, color=INK2, ha="center", va="top")
        ax.text((SNW * XMAX) ** 0.5 if log else (SNW + XMAX) / 2, y, "Fuera de la\nbase mundial", fontsize=6.5, color=INK2, ha="center", va="top")
OP2 = dict(phi=A33["phi"]); MAR = A12["marmol"]["central"]; MC = PC["m_a"]
lo = np.array(A33["phi_lo"]); hi = np.array(A33["phi_hi"])
# cota inferior de Indraratna et al. (1993) en la forma de Cylwik et al. (2025, Tabla 1, p. 3): Ec. 9 con φ′1 = 33° y m = 0.9; no depende de e
# (corregido 2026-10-12: antes se desplazaba con ω desde e = 0.6 a la e base, y a e = 0.45 coincidía con Leps inferior; era un error)
cota_inf = lambda s: np.degrees(np.arctan(np.tan(np.radians(33.0)) * (np.asarray(s, float) / 1.013) ** (0.9 - 1)))
# Referencias de fondo (WA 2026-10-12: solo Leps 1970 e Indraratna): envolventes de Leps (1970) en la forma de Cylwik et al. (2025,
# p. 2, Ec. 9, m = 0.9): φ′1 = 46° (superior), 41° (media) y 36° (inferior); no dependen de e
leps70 = lambda s, p1: np.degrees(np.arctan(np.tan(np.radians(p1)) * (np.asarray(s, float) / 1.013) ** (0.9 - 1)))
FONDO = [("Leps (1970), envolvente superior", lambda s: leps70(s, 46.0), (0, (6, 2, 1, 2))),
         ("Leps (1970), envolvente media", lambda s: leps70(s, 41.0), (0, (4, 2))),
         ("Leps (1970), envolvente inferior", lambda s: leps70(s, 36.0), (0, (1, 1.5))),
         ("Cota inferior de Indraratna et al. (1993)", cota_inf, "-")]


# base mundial de Leps 2.0 (Cylwik et al. 2025): cada ensayo llevado a la e base con ω = 20°, como los de Antamina (WA 2026-10-12)
sys.path.insert(0, str(AQ.parent / "analisis")); from lepsp_r6 import datos as _datos  # noqa: E402
WB = _datos(); WB = WB[~WB.cens] if "cens" in WB else WB
WB = WB[(WB.sn > 0) & (WB.tau > 0)].copy(); WB["phis_eb"] = np.degrees(np.arctan(WB.tau / WB.sn)) - 20.0 * (EC - WB.e)
GRIS_M = "#c9c8c2"


def mundo(ax, tau=False):
    ax.scatter(WB.sn, WB.sn * np.tan(np.radians(WB.phis_eb)) if tau else WB.phis_eb, s=7, marker="o", facecolor=GRIS_M, edgecolor="none",
               zorder=2, rasterized=True)


H_MUNDO = Line2D([], [], ls="", marker="o", markerfacecolor=GRIS_M, markeredgecolor="none", markersize=4,
                 label="Base mundial de Leps 2.0 (Cylwik et al., 2025), llevada a e = %.2f" % EC)


def fondo(ax, x, tau=False):
    for _, f_, ls in FONDO:
        ax.plot(x, x * np.tan(np.radians(f_(x))) if tau else f_(x), color=MUTED, lw=1.1, ls=ls, zorder=3)


def h_fondo():
    return [Line2D([], [], color=MUTED, lw=1.1, ls=ls, label=nm) for nm, _, ls in FONDO]


def ensayos(ax, campo, solo=None, gris=False):
    for lit, (col, mk) in LIT.items():
        for tipo, lleno in (("TX", True), ("DS", False)):
            q = P[(P.litologia == lit) & (P.tipo == tipo)]
            if solo is not None:
                q = q[q.litologia == solo] if not gris else q[q.litologia != solo]
            if len(q) == 0:
                continue
            c = GRIS if gris else col
            ax.scatter(q.sn, campo(q), s=30 if gris else 36, marker=mk, facecolor=c if lleno else "none", edgecolor=SURF if lleno else c,
                       linewidth=1.0 if lleno else 1.3, zorder=3 if gris else 5)


def leyenda_ensayos(lits=None):
    """Ensayos de Antamina: color y forma por litología; lleno, triaxial drenado; vacío, corte directo (comentario WA 2026-10-12)."""
    h = [Line2D([], [], ls="", marker=LIT[l][1], color=LIT[l][0], markersize=6, label=LIT_TXT[l]) for l in (lits or LIT)]
    h += [Line2D([], [], ls="", marker="o", markerfacecolor=INK2, markeredgecolor=INK2, markersize=6, label="Lleno: triaxial drenado (0.6–1 m y 6 in)"),
          Line2D([], [], ls="", marker="o", markerfacecolor="none", markeredgecolor=INK2, markersize=6, label="Vacío: corte directo (caja de 30.5 cm)")]
    return h


def leyendas(fig, ax, curvas, y=-0.15):
    """Dos leyendas con título, una bajo la otra, para que ningún rótulo se corte."""
    l1 = ax.legend(handles=curvas, title="Curva y referencias", loc="upper left", bbox_to_anchor=(-0.1, y), fontsize=7.0,
                   title_fontsize=7.4, frameon=False, ncol=1, alignment="left")
    ax.add_artist(l1)
    ax.legend(handles=leyenda_ensayos(), title="Ensayos de Antamina, llevados a e = %.2f" % EC, loc="upper left", bbox_to_anchor=(0.50, y),
              fontsize=7.0, title_fontsize=7.4, frameon=False, ncol=1, alignment="left")


def eje_log(ax, ylim):
    ax.set_xscale("log"); ax.set_xlim(0.1, XMAX); ax.set_ylim(*ylim)
    ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 5, 8, 15]); ax.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "5", "8", "15"])
    ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
    ax.set_xlabel("Esfuerzo normal efectivo en el plano de falla, σ′n (MPa)"); ax.set_ylabel(f"Ángulo de fricción secante, φ′s (°), a e = {EC:.2f}")
    ax.grid(True, which="major", color=GRID, lw=0.6); ax.set_axisbelow(True)
    zonas(ax)


# ---------------------------------------------------------------- Fig. 1: curva recomendada y ensayos del ajuste
fig, ax = plt.subplots(figsize=(6.5, 5.0))
ax.fill_between(sn, lo, hi, color=VIO_B, lw=0, zorder=1)
TOPE = 40.0                                         # revisión 11: tope del ángulo secante a bajo confinamiento
_phi = np.array(OP2["phi"]); _top = _phi > TOPE
ax.plot(sn, np.minimum(_phi, TOPE), color=VIO, lw=2.4, zorder=4)
ax.plot(np.where(_top, sn, np.nan), np.where(_top, _phi, np.nan), color=VIO, lw=1.2, ls=":", zorder=4)
mundo(ax); fondo(ax, sn)
ensayos(ax, lambda q: q.phis_e065)
eje_log(ax, (22, 56))
h = [Line2D([], [], color=VIO, lw=2.4, label=f"Curva propuesta (m = {PC['m_a']:.2f}), con tope de {TOPE:.0f}°"),
     Line2D([], [], color=VIO, lw=1.2, ls=":", label="Curva sin tope"), Patch(color=VIO_B, label="Incertidumbre de la curva"),
     Patch(facecolor="#efeee9", label=f"{SNX:.2f}–{SNW:.2f} MPa: sin ensayos de Antamina"),
     Patch(facecolor="none", edgecolor="#d2d1cb", hatch="///", label=f"Sobre {SNW:.2f} MPa: extrapolación")] + h_fondo() + [H_MUNDO]
leyendas(fig, ax, h)
fig.set_size_inches(6.5, 6.0); fig.subplots_adjust(left=0.12, right=0.97, top=0.97, bottom=0.40)
fig.savefig(OUT / "Fig1_phi_sigma.png"); fig.savefig(OUT / "Fig1_phi_sigma.pdf"); plt.close(fig)

# ---------------------------------------------------------------- Fig. 2: τ–σ′n
S0 = 1.013; sl = np.linspace(0.01, XMAX, 400)
tau_of = lambda phi_curve: np.interp(np.log(sl), np.log(sn), np.tan(np.radians(phi_curve))) * sl
fig, ax = plt.subplots(figsize=(6.5, 4.6))
ax.fill_between(sl, tau_of(lo), tau_of(hi), color=VIO_B, lw=0, zorder=1)
REF = [(nm, (lambda g: lambda s: s * np.tan(np.radians(g(s))))(f_), ls) for nm, f_, ls in FONDO]
mundo(ax, tau=True); fondo(ax, sl, tau=True)
ax.plot(sl, tau_of(np.minimum(np.array(OP2["phi"]), TOPE)), color=VIO, lw=2.4, zorder=4)
ensayos(ax, lambda q: q.sn * np.tan(np.radians(q.phis_e065)))
ax.set_xlim(0, XMAX); ax.set_ylim(0, 10.5); zonas(ax, log=False); ax.set_xlabel("Esfuerzo normal efectivo en el plano de falla, σ′n (MPa)"); ax.set_ylabel("Resistencia al corte, τ (MPa)")
ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
h = [Line2D([], [], color=VIO, lw=2.4, label=f"Curva propuesta, e = {EC:.2f}, con tope de {TOPE:.0f}°"), Patch(color=VIO_B, label="Incertidumbre de la curva")]
h += h_fondo() + [H_MUNDO]
leyendas(fig, ax, h, y=-0.16)
fig.set_size_inches(6.5, 5.6); fig.subplots_adjust(left=0.1, right=0.97, top=0.97, bottom=0.38)
fig.savefig(OUT / "Fig2_tau_sigma.png"); fig.savefig(OUT / "Fig2_tau_sigma.pdf"); plt.close(fig)
for s_ in (1, 3, 5, 8):
    j = int(np.argmin(np.abs(sl - s_)))
    print(f"σ′n {s_} MPa: curva propuesta φs {np.degrees(np.arctan(tau_of(OP2['phi'])[j] / sl[j])):.1f}°  " +
          "  ".join(f"{nm[:28]} {np.degrees(np.arctan(f(sl[j]) / sl[j])):.1f}°" for nm, f, _ in REF))

# ---------------------------------------------------------------- Fig. 3: relación de vacíos con la profundidad y su efecto
PE = json.load(open(AQ / "a13_perfil_e.json", encoding="utf-8")); import a13_perfil_e as PEM  # noqa: E402
COLP = {"Perfil A (edómetro Antamina)": "#e87ba4", "Perfil V (Valenzuela et al. 2008)": "#008300"}   # no son colores de litología
NOMP = {"Perfil A (edómetro Antamina)": "Perfil A, compresibilidad de Antamina", "Perfil V (Valenzuela et al. 2008)": "Perfil V, Valenzuela et al. (2008)"}
fig, (a1, a2) = plt.subplots(1, 2, figsize=(6.5, 3.9), gridspec_kw=dict(width_ratios=[1, 1.45], wspace=0.32))
zz = np.array(PE["z"]); eA = np.array(PE["e_A"]); eV = np.array([np.nan if v is None else v for v in PE["e_V"]])
EST = {0.45: (0, (1, 1.5)), 0.55: (0, (4, 2)), 0.65: (0, (6, 2, 1, 2))}
a1.axvline(EC, color=VIO, lw=2.0)
a1.plot(eA, zz, color=COLP["Perfil A (edómetro Antamina)"], lw=2); a1.plot(eV, zz, color=COLP["Perfil V (Valenzuela et al. 2008)"], lw=2)
a1.text(eA[-1] - 0.008, 690, "A", color=INK, fontsize=8, ha="right", va="bottom"); a1.text(np.nanmin(eV) - 0.005, 600, "V", color=INK, fontsize=8, ha="right", va="center")
a1.set_ylim(700, 0); a1.set_xlim(0.08, 0.70); a1.set_xlabel("Relación de vacíos, e"); a1.set_ylabel("Profundidad bajo la superficie (m)")
a1.grid(True, color=GRID, lw=0.6); a1.set_axisbelow(True); a1.set_title("(a) Relación de vacíos", loc="left", fontsize=8.5, color=INK)
snp = np.geomspace(0.1, XMAX, 200)
fondo(a2, snp)
for k in PE["curvas"]:
    _e = (float(k[4:]) if k.startswith("e = ") else (PEM.e_A(snp) if k.startswith("Perfil A") else PEM.eV_of_sv(snp)))
    f = LC.phis(snp, _e, PC)
    if k.startswith("e = "):
        e_ = float(k[4:])
        if abs(e_ - EC) < 1e-9:
            a2.plot(snp, f, color=VIO, lw=2.2, label=f"e = {EC:.2f} constante (base)")
    else:
        a2.plot(snp, f, color=COLP[k], lw=2.0, label=NOMP[k])
a2.set_xscale("log"); a2.set_xlim(0.1, XMAX); a2.set_ylim(22, 58); a2.set_xticks([0.1, 0.2, 0.5, 1, 2, 5, 15]); a2.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "5", "15"])
zonas(a2, rotulos=False)
a2.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
a2.set_xlabel("σ′n (MPa)"); a2.set_ylabel("φ′s (°), curva propuesta"); a2.grid(True, color=GRID, lw=0.6); a2.set_axisbelow(True)
a2.set_title("(b) Ángulo de fricción secante", loc="left", fontsize=8.5, color=INK)
fig.legend(handles=a2.get_legend_handles_labels()[0] + h_fondo(), loc="lower center", bbox_to_anchor=(0.5, 0.0), fontsize=6.6,
           frameon=False, ncol=2)
fig.set_size_inches(6.5, 4.6); fig.subplots_adjust(bottom=0.36, left=0.1, right=0.98)
fig.savefig(OUT / "Fig3_perfil_e.png"); fig.savefig(OUT / "Fig3_perfil_e.pdf"); plt.close(fig)
print("figuras en", OUT)
