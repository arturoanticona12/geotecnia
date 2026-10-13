"""Aplicación de Leps-P al desmonte del yacimiento de skarn: envolventes por litología con ensayos de gran escala
(≥ 0.6 m, sin relave, réplicas agrupadas), escala de laboratorio a campo, y envolvente del botadero con tres supuestos
de correlación entre litologías. Escribe lepsp_sitio.json y lepsp_sitio_muestras.npz (para la estabilidad)."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent; sys.path.insert(0, str(RAIZ / "leps3"))
import lepsp as L  # noqa: E402

d = pd.read_csv(AQUI / "drenados_utilizables.csv", low_memory=False)
g = d[d.escala.isin(["0.6 m", "1.0 m"]) & (d.relave_pct_masa_total.fillna(0) == 0)].copy()
g["e_use"] = g.e0_adoptado.fillna(g.e0)
LIT = {"Carbonato metamórfico (mármol)": ("Mármol", "baja"), "Hornfels": ("Hornfels", "moderada"),
       "Intrusivo": ("Intrusivo", "baja"), "Sedimentaria carbonatada (caliza y margas)": (None, "baja")}
PESO = {"Carbonato metamórfico (mármol)": 0.40, "Hornfels": 0.20, "Intrusivo": 0.15, "Sedimentaria carbonatada (caliza y margas)": 0.25}
E_REF = float(g.groupby("set_a").e_use.first().median())
D_LAB = float(g.Dmax_mm.median()); D_CAMPO = 1000.0
print(f"ensayos de gran escala sin relave: {len(g)} en {g.set_a.nunique()} sets; e de referencia (mediana por set) = {E_REF:.3f}; dmax de laboratorio = {D_LAB:.0f} mm")
specs, datos = [], []
for nm, (lit, cal) in LIT.items():
    gi = g[g.litologia == lit] if lit else g.iloc[0:0]
    e = float(gi.e_use.median()) if len(gi) else E_REF
    specs.append((cal, e)); datos.append(gi)
    print(f"  {nm:45s} clase {cal:8s} e = {e:.3f}  ensayos {len(gi)}  sets {gi.set_a.nunique() if len(gi) else 0}  σ′3 {gi.s3.min() if len(gi) else float('nan'):.2f}–{gi.s3.max() if len(gi) else float('nan'):.2f} MPa")
N = 60000
mats = L.previa_conjunta(specs, n=N, seed=11)
diags = {}
for i, (nm, gi) in enumerate(zip(LIT, datos)):
    if len(gi):
        mats[i], dg = L.actualizar(mats[i], gi.s3.values, gi.s1.values, seed=20 + i, restringir=False)
        diags[nm] = {k: (float(v) if not isinstance(v, (str, np.ndarray)) else (v if isinstance(v, str) else v.round(3).tolist())) for k, v in dg.items()}
        print(f"  actualización {nm}: modo {dg['modo']}, p de conflicto {dg['p_conflicto']:.3f}, razón de σ′n {dg['rango_sn']:.2f}")
mats_lab = L.restringir_conjunto(mats)
E = json.load(open(RAIZ / "leps3" / "lepsp_parametros.json"))["escala"]
bD = np.random.default_rng(5).normal(E["bD"], np.hypot(E["se"], E["tau"]), N)                  # escala común al sitio
mats_c = L.restringir_conjunto([L.escala(mt, D_LAB, D_CAMPO, bD=bD) for mt in mats])
SN = np.array([0.5, 1, 3, 6, 10, 15])
res = dict(e_ref=E_REF, d_lab=D_LAB, d_campo=D_CAMPO, pesos=PESO, diag=diags, litologias={}, botadero={})
for nm, ml, mc in zip(LIT, mats_lab, mats_c):
    ql = L.percentiles(SN, ml, (10, 50), puntual=False); qc = L.percentiles(SN, mc, (5, 10, 50), puntual=False)
    res["litologias"][nm] = dict(phi1=L.phi1_mediana(ml), m=float(np.median(ml.m)), lab_P50=ql[50].tolist(), lab_P10=ql[10].tolist(),
                                 campo_P50=qc[50].tolist(), campo_P10=qc[10].tolist(), campo_P05=qc[5].tolist())
    print(f"\n{nm}: φ′1 {L.phi1_mediana(ml):.1f}°, m {np.median(ml.m):.3f}")
    print("   σ′n:      " + "  ".join(f"{s:>9g}" for s in SN))
    print("   lab  P50/P10: " + "  ".join(f"{a:4.1f}/{b:4.1f}" for a, b in zip(ql[50], ql[10])))
    print("   campo P50/P10:" + "  ".join(f"{a:4.1f}/{b:4.1f}" for a, b in zip(qc[50], qc[10])))
# envolvente media del botadero: τ = Σ w_k τ_k
w = np.array([PESO[k] for k in LIT]); x = np.log(SN / L.S0)
tau = np.array([L.S0 * np.exp(mt.th[:, None] + mt.m[:, None] * x + mt.c2[:, None] * x ** 2) for mt in mats_c])   # (lit, n, sn)
phi = lambda t: np.degrees(np.arctan(t / SN[None, :]))
esc = {"Modelo (sistemático común, materiales independientes)": np.tensordot(w, tau, 1),
       "Correlación total entre litologías": np.tensordot(w, np.sort(tau, axis=1), 1),
       "Segregación: litología más débil": tau[int(np.argmin([np.median(t[:, -1]) for t in tau]))]}
for k, t in esc.items():
    p = {q: np.percentile(phi(t), q, axis=0) for q in (5, 10, 50)}
    res["botadero"][k] = {f"P{q:02d}": p[q].tolist() for q in (5, 10, 50)}
    print(f"\nBotadero — {k}\n   P50/P10/P05: " + "  ".join(f"{a:4.1f}/{b:4.1f}/{c:4.1f}" for a, b, c in zip(p[50], p[10], p[5])))
res["sn"] = SN.tolist()
json.dump(res, open(AQUI / "lepsp_sitio.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
np.savez_compressed(AQUI / "lepsp_sitio_muestras.npz", **{f"lit{i}_{c}": getattr(mt, c) for i, mt in enumerate(mats_c) for c in ("th", "m", "c2")}, pesos=w)
print("\nescrito lepsp_sitio.json y lepsp_sitio_muestras.npz")
