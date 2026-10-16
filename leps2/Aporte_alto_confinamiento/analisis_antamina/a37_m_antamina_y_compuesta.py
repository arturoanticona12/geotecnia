"""(1) ¿Sigue Antamina con m ≈ 1 con toda la data, incluidos los cortes directos? (pedido del usuario, 2026-10-13)
    Mismo estimador que a18 (m común, nivel propio por set, m libre en [0.5, 1.5], sin el límite m ≤ 1 de Leps 2.0), con variantes:
    todos; solo triaxiales; solo cortes directos; cortes directos con peso 1 en vez de c_ds; sin la mezcla de Golder (2021)
    a 0.10 MPa; sin los sets de Pila 01 y 02. Intervalo al 90 % por bootstrap de sets.
(2) Curva compuesta como alternativa (leps_compuesta.py): m = 1 hasta σ_a = 4.23 MPa (máximo σ′n de Antamina convertido con m = 1),
    transición lineal en ln σ′n hasta m = 0.85 en σ_b = 7.86 MPa; nivel de los sets con m = 1 (a33 «lineal»).
    Se compara con la curva propuesta: residuos de Antamina, φ′s a e = 0.45 y prueba de extrapolación con la base mundial
    (nivel con σ′n ≤ 2 MPa, predicción de los ensayos sobre 4.62 MPa), como a31.
Escribe a37_resultados.json."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy import stats
from scipy.optimize import least_squares
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis")); sys.path.insert(0, str(AQ))
from modelos import sigma1, tau_leps2  # noqa: E402
from lepsp_r6 import datos  # noqa: E402
import leps_compuesta as LC  # noqa: E402
from tope import TOPE  # noqa: E402
S0, OM, EB = 1.013, 20.0, 0.45
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]
A33 = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8")); A30 = json.load(open(AQ / "a30_dos_pasos.json", encoding="utf-8"))
SNX = A30["snx"]
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
d["set"] = d.fuente_id + "|" + d.set_id.astype(str); d["tx"] = d.tipo == "TX"; d["e"] = d.e0_adoptado


def ajuste_m(g, c_ds=C_DS):
    sets = list(g.set.unique()); idx = g.set.map({s: i for i, s in enumerate(sets)}).values; tx = g.tx.values; e = g.e.values

    def res(p):
        pe = p[:-1][idx]; m = p[-1]; r = np.empty(len(g))
        if tx.any():
            s3 = g.s3.values[tx]; r[tx] = np.log(sigma1(tau_leps2, s3, pe[tx] - OM * e[tx], m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
        if (~tx).any():
            r[~tx] = c_ds * (np.log(tau_leps2(g.sn_ds.values[~tx], pe[~tx] - OM * e[~tx], m)) - np.log(g.tau_ds.values[~tx]))
        return r
    p0 = np.r_[np.full(len(sets), 48.0), 0.9]
    r = least_squares(res, p0, bounds=(np.r_[np.full(len(sets), 25.0), 0.5], np.r_[np.full(len(sets), 75.0), 1.5]))
    return float(r.x[-1])


def con_boot(g, nb=300, seed=37, **kw):
    m = ajuste_m(g, **kw); sets = list(g.set.unique()); rng = np.random.default_rng(seed); b = []
    for _ in range(nb):
        sel = rng.choice(sets, len(sets))
        gb = pd.concat([g[g.set == s].assign(set=f"{s}#{i}") for i, s in enumerate(sel)])   # cada copia, un set propio
        try:
            b.append(ajuste_m(gb, **kw))
        except Exception:
            pass
    return dict(m=m, p5=float(np.percentile(b, 5)), p95=float(np.percentile(b, 95)), n=int(len(g)), sets=int(g.set.nunique()))


PILAS = d.set.str.contains("Pila")
VAR = {"Todos (37 ensayos)": (d, {}), "Solo triaxiales": (d[d.tx], {}), "Solo cortes directos": (d[~d.tx], {}),
       "Todos, cortes directos con peso 1": (d, dict(c_ds=1.0)),
       "Sin la mezcla de Golder (2021)": (d[~d.set.str.contains("G21-DESM")], {}), "Sin las pilas 01 y 02 (corte directo)": (d[~PILAS], {})}
out = {"m_antamina": {}}
for k, (g, kw) in VAR.items():
    out["m_antamina"][k] = r = con_boot(g, **kw)
    print(f"{k:40s} n {r['n']:2d} sets {r['sets']:2d}  m = {r['m']:.3f}  (IC 90 % {r['p5']:.3f}–{r['p95']:.3f})")
# pendientes dentro de cada set de corte directo (ln τ sobre ln σ′n = m local del set)
out["ds_por_set"] = {s: float(stats.linregress(np.log(q.sn_ds), np.log(q.tau_ds)).slope) for s, q in d[~d.tx].groupby("set")}
print("m por set de corte directo (pendiente de ln τ sobre ln σ′n):", {k.split("|")[1]: round(v, 3) for k, v in out["ds_por_set"].items()})

# ---------------------------------------------------------------- (2) curva compuesta
PC = dict(LC.PAR_DEF, pe0=A33["nivel"]["lineal"]["pe0"], m_a=1.0, m_h=0.85)
PS = dict(LC.PAR_DEF, pe0=A33["parametros"]["pe0"], m_a=0.85, m_h=0.85)
SNT = [0.5, 1.0, 2.0, SNX, 7.86, 10.0, 15.0]
out["compuesta"] = dict(param=PC, phis={f"{s:g}": [float(min(LC.phis(s, EB, PS), TOPE)), float(min(LC.phis(s, EB, PC), TOPE))] for s in SNT})
print("\nφ′s a e = 0.45 (propuesta | compuesta):", {k: [round(v, 1) for v in x] for k, x in out["compuesta"]["phis"].items()})
# residuos de Antamina (a35: σ′n y φ′s de cada ensayo, triaxiales convertidos con m = 0.85)
P = pd.read_csv(AQ / "a35_residuos.csv")
rc = P.phis - np.minimum(LC.phis(P.sn.values, P.e.values, PC), TOPE)
lr = stats.linregress(np.log(P.sn), rc)
out["compuesta"]["residuos"] = dict(media=float(rc.mean()), mae=float(np.abs(rc).mean()), pendiente=float(lr.slope), r=float(lr.rvalue), p=float(lr.pvalue),
                                    rangos={f"{a}-{b}": float(rc[(P.sn >= a) & (P.sn < b)].mean()) for a, b in ((0.1, 0.5), (0.5, 1), (1, 2), (2, 5))})
print("residuos de Antamina con la compuesta:", {k: (round(v, 3) if isinstance(v, float) else {a: round(b, 2) for a, b in v.items()}) for k, v in out["compuesta"]["residuos"].items()})
# prueba de extrapolación con la base mundial
W = datos(); W = W[~W.cens] if "cens" in W else W


def extrap(p):
    err = []
    for s, g in W.groupby("Set"):
        lo, hi = g[g.sn <= 2.0], g[g.sn > SNX]
        if len(lo) and len(hi):
            I = lambda x: LC.integral_m(x, p["m_a"], p["m_h"], p["s_a"], p["s_b"])
            lt = np.mean(np.log(lo.tau.values) - np.log(S0) - I(lo.sn.values))
            tp = np.exp(lt) * S0 * np.exp(I(hi.sn.values))
            err += list(np.degrees(np.arctan(tp / hi.sn.values)) - np.degrees(np.arctan(hi.tau.values / hi.sn.values)))
    err = np.array(err); return dict(sesgo=float(err.mean()), mae=float(np.abs(err).mean()), n=int(len(err)))


out["extrapolacion_mundo"] = {"Propuesta (m = 0.85)": extrap(PS), "Compuesta (m = 1 → 0.85)": extrap(PC),
                              "m = 1": extrap(dict(PS, m_a=1.0, m_h=1.0))}
print("prueba de extrapolación, base mundial (predicción − medido, °):", {k: {a: round(b, 2) for a, b in v.items()} for k, v in out["extrapolacion_mundo"].items()})
json.dump(out, open(AQ / "a37_resultados.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print("escrito a37_resultados.json")
