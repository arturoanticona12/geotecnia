"""Revisión 4 del memorándum (comentarios del 2026-10-10): inventario completo de los ensayos de desmonte de Antamina (sin las
mezclas con relave), contraste de los ensayos no usados en el ajuste con la curva propuesta, rotura de partículas (Bg de Marsal)
y condiciones de campo (Dmax de la fragmentación 2025, e in situ de Golder 2010). Todos los valores de ensayo se leen de las
extracciones verificadas contra los PDF (datos_antamina/verificacion_ocr/, 2026-10-10).
  - Contraste: CU de Anddes (2024) en esfuerzos efectivos a máxima oblicuidad; CU de Golder (2010), solo fase A (ROM; la fase B es
    ROM chancado y no se usa), en esfuerzos efectivos al máximo desviador (único criterio informado); corte directo de gran escala
    de Anddes (2024), τ pico. Los CU se convierten a σ′n–τ con la misma conversión de Leps 2.0 (m = 0.9) que los drenados y todos
    se llevan a e = 0.65 con ω = 20°.
  - Bg: triaxiales drenados sin relave con Bg informado o recalculado (Golder 2012: el informe da 2·Bg; se usa el recalculado).
Escribe a16_resultados.json, a16_contraste.csv, a16_bg.csv y figuras_leps2/Fig4_contraste.pdf/png y Fig5_bg.pdf/png."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; V = AQ.parent / "datos_antamina" / "verificacion_ocr"; B = AQ.parent / "datos_antamina" / "base"; OUT = AQ / "figuras_leps2"
OM, EC, S0 = 20.0, 0.45, 1.013   # e base 0.45 (2026-10-10)
# 2026-10-12: curva propuesta simple, m = 0.85 (leps_compuesta, a33); conversión de los triaxiales con la m de la curva
sys.path.insert(0, str(AQ)); import leps_compuesta as LC  # noqa: E402
A33 = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8")); PC = A33["parametros"]; M = PC["m_a"]
phis_c = lambda sn: LC.phis(np.asarray(sn, float), EC, PC)


def a_tau_sn(s3, s1, m=M):                     # misma conversión que a9 (Ecs. 13–16 de Leps 2.0)
    D, Sm = s1 - s3, s1 + s3
    sp = D / Sm if abs(m - 1) < 1e-9 else (np.sqrt(4 * m * (m - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (m - 1) * D)
    return Sm / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


LIT = {"Mármol": "Mármol", "Mármol Negro": "Mármol", "Hornfels": "Hornfels", "Hornfels Gris": "Hornfels", "Intrusivo": "Intrusivo",
       "Skarn": "Skarn", "Exoskarn Diópsido": "Skarn", "Mezcla": "Mezcla"}
# ---------------------------------------------------------------- contraste
cu = pd.read_csv(V / "anddes2024_cu.csv"); g10 = pd.read_csv(V / "golder2010_cu.csv"); ds = pd.read_csv(V / "anddes2024_lsds.csv")
e_ = pd.read_csv(B / "ensayos.csv", low_memory=False)
lit_and = e_[e_.fuente_id == "A2024"].groupby("set_id").litologia.first()
def lit_anddes(s):
    s = str(s)
    for k, v in (("M-1", "Mármol"), ("H-1", "Hornfels"), ("I-1", "Intrusivo"), ("Pila 01", "Mezcla"), ("Pila 02", "Intrusivo"), ("MP1", "Mezcla"), ("MP2", "Intrusivo")):
        if k in s:
            return v
    return "?"
filas = []
for _, r in cu.iterrows():
    s3, s1 = r.maxobl_s3f_ef_calc_kPa / 1000, r.maxobl_s1f_ef_calc_kPa / 1000
    filas.append(dict(grupo="CU Anddes (2024), 6 in, máxima oblicuidad", fuente="Anddes Geolab (2024)", tipo="Triaxial CU", set=r.set, litologia=lit_anddes(r.set),
                      e=r.e0, s3=s3, s1=s1, pagina=r.pagina_pdf))
for _, r in g10[g10.campana == "A"].iterrows():
    s3, s1 = r.maxdev_sigma3ef_kPa / 1000, r.maxdev_sigma1ef_kPa / 1000
    filas.append(dict(grupo="CU Golder (2010), fase A, 2.8 y 4 in, máximo desviador", fuente="Golder Associates (2010)", tipo="Triaxial CU", set=r.set_id,
                      litologia=LIT.get(r.litologia, r.litologia), e=r.e0, s3=s3, s1=s1, pagina=r.pagina_pdf))
C = pd.DataFrame(filas)
# Anddes no informa Gs: e con el Gs de sólidos (D854) de Golder (2010), promedio de las fases A y B, igual que su corte directo
# en el ajuste (a8_ensayos_ajuste.py; revisión 5). Antes se usaba el rótulo del Proctor (3.06 en el mármol).
GSD = {"Mármol": (2.763 + 2.747) / 2, "Hornfels": (2.791 + 2.802) / 2, "Intrusivo": (2.674 + 2.742) / 2}; GSD["Mezcla"] = (GSD["Mármol"] + GSD["Hornfels"]) / 2
EA = cu.groupby("set").rho_d_ini_gcm3.first().astype(float); EA = pd.Series({s: GSD[lit_anddes(s)] / v - 1 for s, v in EA.items()})
C["e"] = C.e.astype(object)   # pandas 3: la columna puede quedar como texto
C.loc[C.fuente == "Anddes Geolab (2024)", "e"] = C.loc[C.fuente == "Anddes Geolab (2024)", "set"].map(EA)
C["e"] = pd.to_numeric(C.e, errors="raise")
C["sn"], C["tau"] = a_tau_sn(C.s3.values, C.s1.values)
# revisión 5: el corte directo de Anddes (2024) entra en el ajuste (a8_ensayos_ajuste.py); ya no es contraste
C["phis"] = np.degrees(np.arctan(C.tau / C.sn)); C["phis_e065"] = C.phis - OM * (EC - C.e); C["resid"] = C.phis_e065 - phis_c(C.sn)
_d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False); _tx = (_d.tipo == "TX").values
_sn = _d.sn_ds.values.copy(); _tau = _d.tau_ds.values.copy(); _sn[_tx], _tau[_tx] = a_tau_sn(_d.s3.values[_tx], _d.s1.values[_tx])
P = pd.DataFrame(dict(sn=_sn, e=_d.e0_adoptado.values, phis=np.degrees(np.arctan(_tau / _sn)))); P["phis_e065"] = P.phis - OM * (EC - P.e)
P["resid"] = P.phis_e065 - phis_c(P.sn)
C.to_csv(AQ / "a16_contraste.csv", index=False)
res = {"ajuste (triaxiales y corte directo)": dict(n=len(P), sn=[float(P.sn.min()), float(P.sn.max())], resid_media=float(P.resid.mean()), e=[float(P.e.min()), float(P.e.max())])}
for g, q in C.groupby("grupo", sort=False):
    res[g] = dict(n=len(q), sn=[float(q.sn.min()), float(q.sn.max())], resid_media=float(q.resid.mean()), resid_min=float(q.resid.min()),
                  resid_max=float(q.resid.max()), e=[float(q.e.min()), float(q.e.max())])
for k, v in res.items():
    print(f"{k:58s} n {v['n']:2d}  σ′n {v['sn'][0]:.2f}–{v['sn'][1]:.2f} MPa  e {v['e'][0]:.3f}–{v['e'][1]:.3f}  Δφ′ media {v['resid_media']:+.1f}°")
# ---------------------------------------------------------------- Bg (drenados sin relave)
bg = pd.read_csv(V / "rotura_bg.csv")
sel = [("G2012", "G2012-MN-C", "calculado", "Mármol", "1.0 m"), ("W2022", "HF-1.0m-IDIEM-mono", "informado", "Hornfels", "1.0 m"),
       ("W2022", "HF-1.0m-IDIEM-cd", "informado", "Hornfels", "1.0 m"), ("W2022", "HF-0.15m-Golder", "informado", "Hornfels", "6 in"),
       ("W2022", "MN-0.15m-Golder", "informado", "Mármol", "6 in"), ("W2024", "WSP24_C4_MON", "informado", "Intrusivo", "0.6 m")]
G = []
for f, s, o, l, esc in sel:
    q = bg[(bg.fuente_id == f) & (bg.set_id == s) & bg.origen.str.startswith(o)]
    for _, r in q.iterrows():
        if "edómetro" in str(r.probeta):
            continue
        G.append(dict(fuente=f, set=s, litologia=l, escala=esc, s3=float(r.sigma3_kPa) / 1000, Bg=float(r.Bg_pct), origen=r.origen, pagina=r.pagina_pdf))
G = pd.DataFrame(G); G.to_csv(AQ / "a16_bg.csv", index=False)
co = np.polyfit(G.s3, G.Bg, 1); rbg = float(np.corrcoef(G.s3, G.Bg)[0, 1])
res["bg"] = dict(n=len(G), rango=[float(G.Bg.min()), float(G.Bg.max())], s3=[float(G.s3.min()), float(G.s3.max())], pendiente=float(co[0]), ordenada=float(co[1]), r=rbg,
                 por_lit={l: [float(q.Bg.min()), float(q.Bg.max()), int(len(q))] for l, q in G.groupby("litologia")})
print(f"Bg: n {len(G)}, {G.Bg.min():.1f}–{G.Bg.max():.1f} %, σ′3 {G.s3.min():.2f}–{G.s3.max():.2f} MPa, Bg ≈ {co[1]:.1f} + {co[0]:.1f}·σ′3 (r {rbg:.2f})")
print(G.groupby("litologia").Bg.describe().round(1).to_string())
# ---------------------------------------------------------------- campo: Dmax (fragmentación 2025) y e in situ (Golder 2010, plataformas de prueba)
fr = pd.read_csv(B / "fragmentacion.csv", low_memory=False)
res["frag"] = dict(n=len(fr), D50=float(fr.D50_mm.median()), D80=float(fr.D80_mm.median()), Dmax=float(fr.Dmax_mm.median()),
                   Dmax_p10=float(fr.Dmax_mm.quantile(0.1)), Dmax_p90=float(fr.Dmax_mm.quantile(0.9)))
gi = pd.read_csv(V / "golder2010_indices.csv")
ein = {}
for (c, l), q in gi[gi.ensayo.str.contains("Tabla 2", na=False)].groupby(["campana", "litologia"]):
    rd = q[q.propiedad == "densidad_seca_in_situ_gcm3"].valor; gs = q[q.propiedad == "Gs_mat_grueso"].valor
    if len(rd) and len(gs):
        ein[f"{c}|{LIT.get(l, l)}"] = dict(rho_d=float(rd.iloc[0]), Gs=float(gs.iloc[0]), e=float(gs.iloc[0]) / float(rd.iloc[0]) - 1, pagina=8)
res["e_in_situ_G2010"] = ein
print("e in situ (plataformas de prueba, Golder 2010):", {k: round(v["e"], 3) for k, v in ein.items()})
json.dump(res, open(AQ / "a16_resultados.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
# ---------------------------------------------------------------- figuras (paleta validada de a11; dataviz)
INK, INK2, MUTED, GRID, SURF = "#0b0b0b", "#52514e", "#8a8984", "#e6e5e1", "#fcfcfb"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": MUTED, "axes.labelcolor": INK, "xtick.color": INK2,
                     "ytick.color": INK2, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
sn = np.array(A33["sn"]); lo = np.array(A33["phi_lo"]); hi = np.array(A33["phi_hi"])
fig, ax = plt.subplots(figsize=(6.5, 5.4))
ax.fill_between(sn, lo, hi, color="#e3e0f3", lw=0, zorder=1, label="Incertidumbre de la curva")
from tope import TOPE  # noqa: E402
_pc = phis_c(sn); _tp = _pc > TOPE
ax.plot(sn, np.minimum(_pc, TOPE), color="#4a3aa7", lw=2.2, zorder=4, label=f"Curva propuesta (m = {M:.2f}), con tope de {TOPE:.0f}°")
ax.plot(np.where(_tp, sn, np.nan), np.where(_tp, _pc, np.nan), color="#4a3aa7", lw=1.1, ls=":", zorder=4, label="Curva sin tope")
# fondo (WA 2026-10-12): Leps (1970) en la forma de Cylwik et al. (2025, p. 2, Ec. 9, m = 0.9) y cota inferior de Indraratna et al. (1993)
_l70 = lambda s, p1: np.degrees(np.arctan(np.tan(np.radians(p1)) * (s / S0) ** (0.9 - 1)))
for _nm, _p1, _ls in (("Leps (1970), envolvente superior", 46.0, (0, (6, 2, 1, 2))), ("Leps (1970), envolvente media", 41.0, (0, (4, 2))),
                      ("Leps (1970), envolvente inferior", 36.0, (0, (1, 1.5))),
                      ("Cota inferior de Indraratna et al. (1993)", 33.0, "-")):   # Cylwik et al. (2025, Tabla 1): φ′1 = 33°, sin e
    ax.plot(sn, _l70(sn, _p1), color=MUTED, lw=1.1, ls=_ls, zorder=3, label=_nm)
ax.scatter(P.sn, P.phis_e065, s=26, marker="o", facecolor=INK2, edgecolor=SURF, lw=0.8, zorder=5, label=f"Ensayos del ajuste ({len(P)}: triaxial CD y corte directo)")
EST = {"CU Anddes (2024), 6 in, máxima oblicuidad": ("#e87ba4", "s", "Triaxiales CU, Anddes (2024), 6 in"),   # colores fuera de las litologías
       "CU Golder (2010), fase A, 2.8 y 4 in, máximo desviador": ("#008300", "^", "Triaxiales CU, Golder (2010), fase A")}
for g, (col, mk, lab) in EST.items():
    q = C[C.grupo == g]
    ax.scatter(q.sn, q.phis_e065, s=30, marker=mk, facecolor="none", edgecolor=col, lw=1.3, zorder=6, label=f"{lab} ({len(q)})")
ax.set_xscale("log"); ax.set_xlim(0.1, 8); ax.set_ylim(15, 60)
ax.set_xticks([0.1, 0.2, 0.5, 1, 2, 5, 8]); ax.set_xticklabels(["0.1", "0.2", "0.5", "1", "2", "5", "8"]); ax.xaxis.set_minor_formatter(matplotlib.ticker.NullFormatter())
ax.set_xlabel("Esfuerzo normal efectivo en el plano de falla, σ′n (MPa)"); ax.set_ylabel(f"Ángulo de fricción secante, φ′s (°), a e = {EC:.2f}")
ax.grid(True, which="major", color=GRID, lw=0.6); ax.set_axisbelow(True)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), fontsize=7, frameon=False, ncol=2)
fig.subplots_adjust(left=0.12, right=0.97, bottom=0.36); fig.savefig(OUT / "Fig4_contraste.png"); fig.savefig(OUT / "Fig4_contraste.pdf"); plt.close(fig)
COL = {"Mármol": "#2a78d6", "Hornfels": "#eb6834", "Intrusivo": "#1baf7a"}
fig, ax = plt.subplots(figsize=(6.5, 3.8))
for (l, esc), q in G.groupby(["litologia", "escala"]):
    big = esc != "6 in"
    ax.scatter(q.s3, q.Bg, s=40, marker={"Mármol": "o", "Hornfels": "s", "Intrusivo": "^"}[l], facecolor=COL[l] if big else "none", edgecolor=COL[l], lw=1.3, zorder=5,
               label=f"{l.lower() if l != 'Hornfels' else 'hornfels'}, probeta de {esc}".capitalize())
xs = np.linspace(0, 2.6, 10); ax.plot(xs, np.polyval(co, xs), color=INK2, lw=1.0, ls=(0, (4, 2)), zorder=3, label=f"Tendencia lineal (r = {rbg:.2f})")
ax.set_xlim(0, 2.7); ax.set_ylim(0, 45); ax.set_xlabel("Esfuerzo efectivo de confinamiento, σ′3 (MPa)"); ax.set_ylabel("Índice de rotura de Marsal, Bg (%)")
ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True); ax.legend(loc="upper left", fontsize=7, frameon=False)
fig.subplots_adjust(left=0.1, right=0.97, bottom=0.13); fig.savefig(OUT / "Fig5_bg.png"); fig.savefig(OUT / "Fig5_bg.pdf"); plt.close(fig)
print("figuras 4 y 5 escritas")
