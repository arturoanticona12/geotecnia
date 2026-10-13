"""Ajuste en dos pasos (pedido de WA, 2026-10-12; diseño en docs/2026-10-12-ajuste-dos-pasos-design.md).
Paso 1 (plano τ–σ′n): una m común y un φ′1 por set (Ec. 8 de Cylwik et al. 2025, φ′1 a la e₀ de cada set), con los 13 sets de
Antamina (37 ensayos) y los sets de la base mundial con algún ensayo sobre el máximo σ′n de Antamina; los sets mundiales tienen su
φ′1 libre (solo aportan la curvatura) y pesan, en conjunto, una fracción f del total (f = 0.5 base; 0, 0.25 y 0.75 sensibilidad).
Residuos de Antamina como a12 (ln q en triaxiales, tangencia de la Ec. 16; C_DS·ln τ en corte directo); mundo, ln τ.
Paso 2 (plano e–φ′1): φ′1 de cada set de Antamina contra su e₀ (e = «void ratio at start of test», Cylwik et al. 2025, p. 14),
regresión φ′1 = φ′e=0 − ω e (Ec. 25). Criterio: se adopta si 15° ≤ ω ≤ 25° y el intervalo del 90 % es más estrecho que ±10°; si
no, se evalúa la regresión conjunta con la base mundial (ω común, ordenada por clase y para Antamina, 50/50).
Bootstrap conjunto por sets (paso 1 y paso 2). Escribe a30_dos_pasos.json y figuras_leps2/Fig_phi1_e.png."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares, brentq
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from modelos import sigma1, tau_leps2  # noqa: E402
from lepsp_r6 import datos  # noqa: E402
S0, EB = 1.013, 0.45
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]
A = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
A["set"] = A.fuente_id + "|" + A.set_id.astype(str); A["e"] = A.e0_adoptado; A["tx"] = A.tipo == "TX"
SA = list(dict.fromkeys(A.set)); NA = len(A)
SNX = float(pd.read_csv(AQ / "a10_puntos.csv").query("tipo == 'TX'").sn.max())
W = datos(); W = W[~W.cens] if "cens" in W else W
SW_ALL = W.groupby("Set").sn.max(); SW = list(SW_ALL[SW_ALL > SNX].index)        # sets mundiales con algún ensayo sobre el máximo de Antamina
WH = W[W.Set.isin(SW)].copy()
print(f"Antamina: {len(SA)} sets, {NA} ensayos | mundo: {len(SW)} sets con σ′n > {SNX:.2f} MPa, {len(WH)} ensayos")


def resid_A(g, phi1, m):
    """Residuos de Antamina para el set g con su φ′1 (a la e₀ del set) y la m común."""
    tx = g.tx.values; r = np.empty(len(g))
    if tx.any():
        s3 = g.s3.values[tx]; r[tx] = np.log(sigma1(tau_leps2, s3, phi1, m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
    if (~tx).any():
        r[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], phi1, m)) - np.log(g.tau_ds.values[~tx]))
    return r


def paso1(sets_a, sets_w, f, m0=0.9):
    """m común y φ′1 por set. sets_a / sets_w: listas de sets (con repetición en el bootstrap). f: fracción del peso del mundo."""
    ga = [A[A.set == s] for s in sets_a]; gw = [WH[WH.Set == s] for s in sets_w] if f > 0 else []
    na = sum(len(g) for g in ga); nw = sum(len(g) for g in gw)
    ww = np.sqrt(f / (1 - f) * na / nw) if f > 0 else 0.0

    def res(p):
        m = p[0]; out = [resid_A(g, p[1 + i], m) for i, g in enumerate(ga)]
        out += [ww * (np.log(tau_leps2(g.sn.values, p[1 + len(ga) + j], m)) - np.log(g.tau.values)) for j, g in enumerate(gw)]
        return np.concatenate(out)
    p0 = [m0] + [40.0] * (len(ga) + len(gw))
    r = least_squares(res, p0, bounds=([0.5] + [15.0] * (len(p0) - 1), [1.0] + [70.0] * (len(p0) - 1)))
    return float(r.x[0]), np.array(r.x[1:1 + len(ga)])


def paso2(phi1, e):
    b, a = np.polyfit(e, phi1, 1)                             # φ′1 = a + b e  →  φ′e0 = a, ω = −b
    return float(a), float(-b)


E_SET = np.array([A[A.set == s].e.mean() for s in SA]); LIT = [A[A.set == s].litologia.iloc[0] for s in SA]
out = {"definiciones": "φ′1 a 10pa (Ec. 6); e = void ratio at start of test (p. 14); ω y φ′e=0 de la Ec. 25 (Cylwik et al. 2025)",
       "sets_antamina": SA, "e0_set": E_SET.tolist(), "litologia_set": LIT, "n_sets_mundo": len(SW), "snx": SNX, "paso1": {}}
for f in (0.0, 0.25, 0.5, 0.75):
    m, phi1 = paso1(SA, SW, f)
    pe0, om = paso2(phi1, E_SET)
    out["paso1"][str(f)] = dict(m=m, phi1=phi1.tolist(), pe0=pe0, omega=om)
    print(f"f = {f:.2f}: m = {m:.3f} | paso 2: φ′e0 = {pe0:.2f}°, ω = {om:.1f}°")
# bootstrap conjunto por sets (f = 0.5)
rng = np.random.default_rng(30); BM, BP, BO = [], [], []
for _ in range(150):
    ia = rng.integers(0, len(SA), len(SA)); iw = rng.integers(0, len(SW), len(SW))
    m_b, p_b = paso1([SA[i] for i in ia], [SW[i] for i in iw], 0.5)
    if np.ptp(E_SET[ia]) < 1e-6:
        continue
    pe_b, om_b = paso2(p_b, E_SET[ia]); BM.append(m_b); BP.append(pe_b); BO.append(om_b)
q = lambda v: [float(np.percentile(v, 5)), float(np.percentile(v, 50)), float(np.percentile(v, 95))]
out["bootstrap"] = dict(n=len(BM), m=q(BM), pe0=q(BP), omega=q(BO))
print(f"bootstrap ({len(BM)}): m P5–P50–P95 {q(BM)[0]:.3f}–{q(BM)[1]:.3f}–{q(BM)[2]:.3f} | ω {q(BO)[0]:.1f}–{q(BO)[1]:.1f}–{q(BO)[2]:.1f}° | "
      f"φ′e0 {q(BP)[0]:.2f}–{q(BP)[1]:.2f}–{q(BP)[2]:.2f}°")
B = out["paso1"]["0.5"]; M, PHI1 = B["m"], np.array(B["phi1"])
om_ok = 15 <= B["omega"] <= 25 and (q(BO)[2] - q(BO)[0]) / 2 < 10
out["criterio_omega"] = dict(adoptable=bool(om_ok), omega=B["omega"], ic90=[q(BO)[0], q(BO)[2]])
print("criterio de ω:", "se cumple" if om_ok else "NO se cumple", f"(ω = {B['omega']:.1f}°, IC 90 % {q(BO)[0]:.1f}–{q(BO)[2]:.1f}°)")
# diagnóstico: ordenada por litología, ω común
lits = sorted(set(LIT)); X = np.column_stack([[1.0 if l == L else 0.0 for l in LIT] for L in lits] + [-E_SET])
coef = np.linalg.lstsq(X, PHI1, rcond=None)[0]
out["diag_litologia"] = dict(omega=float(coef[-1]), ordenadas={L: float(c) for L, c in zip(lits, coef[:-1])})
print(f"diagnóstico, ordenada por litología: ω = {coef[-1]:.1f}° | " + ", ".join(f"{L} {c:.1f}°" for L, c in zip(lits, coef[:-1])))
# alternativa con la base mundial en e–φ′1: φ′1 de cada set mundial con la m común (nivel por set, forma cerrada en ln τ)
WS = W.groupby("Set").apply(lambda g: pd.Series(dict(e=g.e.mean(), clase=g.clase.iloc[0], n=len(g),
                                                     phi1=np.degrees(np.arctan(np.exp(np.mean(np.log(g.tau) - np.log(S0 ** (1 - M) * g.sn ** M)))))))).reset_index()
cl = ["low", "moderate", "good"]; nW = len(WS)
Xw = np.column_stack([[1.0 if c == C else 0.0 for c in WS.clase] for C in cl] + [np.zeros(nW)] + [-WS.e.values])
Xa = np.column_stack([np.zeros((len(SA), 3)), np.ones(len(SA)), -E_SET])
wa, ww_ = np.ones(len(SA)), np.full(nW, len(SA) / nW)          # 50/50
Xj = np.vstack([Xa * np.sqrt(wa)[:, None], Xw * np.sqrt(ww_)[:, None]]); yj = np.concatenate([PHI1 * np.sqrt(wa), WS.phi1.values * np.sqrt(ww_)])
cj = np.linalg.lstsq(Xj, yj, rcond=None)[0]
out["omega_mundo"] = dict(omega=float(cj[-1]), pe0_antamina=float(cj[3]), ordenadas_clase={C: float(c) for C, c in zip(cl, cj[:3])}, n_sets=nW)
print(f"alternativa con la base mundial ({nW} sets): ω = {cj[-1]:.1f}° | φ′e0 Antamina {cj[3]:.2f}° | clases " + ", ".join(f"{C} {c:.1f}°" for C, c in zip(cl, cj[:3])))
# comparación con la curva vigente
VIG = json.load(open(AQ / "a12_leps2_ponderada.json", encoding="utf-8"))["curvas"]["Curva propuesta (mediana mundial)"]
phis = lambda s, pe0, om, m: float(np.degrees(np.arctan(np.tan(np.radians(pe0 - om * EB)) * (s / S0) ** (m - 1))))
LB = lambda s: float(np.degrees(np.arctan(np.tan(np.radians(33.0)) * (s / S0) ** (0.9 - 1))))   # Indraratna: φ′1 = 33°, sin e (Cylwik Tabla 1)
HC = lambda s: float(np.degrees(np.arctan(1.446 * (s * 1000) ** 0.898 / (s * 1000))))
NUEVA = dict(pe0=B["pe0"], omega=B["omega"], m=M)
print("\nφ′s a e = 0.45 (°)      1 MPa   4.6    10     15   | cruza Indraratna / H&C")
for nm, c in (("vigente", dict(pe0=VIG["pe0"], omega=20.0, m=VIG["m"])), ("nueva (dos pasos)", NUEVA)):
    cr = []
    for f_ in (LB, HC):
        try:
            cr.append(f"{brentq(lambda s: phis(s, c['pe0'], c['omega'], c['m']) - f_(s), 0.3, 100):.1f}")
        except ValueError:
            cr.append("no cruza")
    print(f"  {nm:20s} " + " ".join(f"{phis(s, c['pe0'], c['omega'], c['m']):6.1f}" for s in (1, 4.6, 10, 15)) + f"   | {cr[0]} / {cr[1]} MPa")
    out.setdefault("comparacion", {})[nm] = dict(c, phis={s: phis(s, c["pe0"], c["omega"], c["m"]) for s in (1, 4.6, 10, 15)}, cruces=cr)
# ensayos altos frente a la curva nueva (cada uno a su e, como a25)
tauN = lambda s, e: np.tan(np.radians(NUEVA["pe0"] - NUEVA["omega"] * e)) * S0 ** (1 - M) * s ** M
k = (W.sn > SNX) & (W.sn <= 7.9); dphi = np.degrees(np.arctan(W.tau[k] / W.sn[k])) - np.degrees(np.arctan(tauN(W.sn[k], W.e[k]) / W.sn[k]))
out["mundo_altos"] = dict(n=int(k.sum()), bajo=int((dphi < 0).sum()), mediana=float(np.median(dphi)))
print(f"ensayos mundiales {SNX:.2f}–7.9 MPa frente a la curva nueva: {int((dphi < 0).sum())} de {int(k.sum())} bajo ella, mediana {np.median(dphi):+.1f}°")
json.dump(out, open(AQ / "a30_dos_pasos.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
# figura φ′1–e (como la Fig. 10 de Cylwik et al. 2025)
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt  # noqa: E401,E402
INK2, MUTED = "#52514e", "#8a8984"; LITC = {"Mármol": ("#2a78d6", "o"), "Hornfels": ("#eb6834", "s"), "Intrusivo": ("#1baf7a", "^"), "Mezcla": ("#eda100", "D")}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "savefig.dpi": 300})
fig, ax = plt.subplots(figsize=(6.5, 4.6)); ee = np.linspace(0, 0.8, 50)
for p_, ls in ((47, (0, (4, 2))), (50, (0, (1, 1.5))), (53, (0, (6, 2, 1, 2)))):
    ax.plot(ee, p_ - 20 * ee, color=MUTED, lw=1.0, ls=ls)
    ax.text(0.79, p_ - 20 * 0.79 + 0.4, f"{p_}° − 20°·e", fontsize=7, color=INK2, ha="right")
ax.plot(ee, B["pe0"] - B["omega"] * ee, color="#4a3aa7", lw=2.2, label=f"Antamina: φ′1 = {B['pe0']:.1f}° − {B['omega']:.1f}°·e")
for l_, (c_, mk) in LITC.items():
    sel = [i for i, l in enumerate(LIT) if l == l_]
    if sel:
        ax.scatter(E_SET[sel], PHI1[sel], color=c_, marker=mk, s=40, edgecolor="white", zorder=4, label=l_)
ax.set_xlim(0, 0.8); ax.set_ylim(20, 55); ax.set_xlabel("Relación de vacíos inicial de la probeta, e (Cylwik et al. 2025: «void ratio at start of test»)")
ax.set_ylabel("φ′1 del set (°), a σ′n = 10pa"); ax.grid(True, color="#e6e5e1", lw=0.6); ax.set_axisbelow(True)
ax.legend(fontsize=7, frameon=False, loc="lower left")
fig.tight_layout(); fig.savefig(AQ / "figuras_leps2" / "Fig_phi1_e.png"); plt.close(fig)
print("escrito a30_dos_pasos.json y figuras_leps2/Fig_phi1_e.png")
