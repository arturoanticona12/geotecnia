"""Curva propuesta compuesta (2026-10-12) y su incertidumbre. Usa a32 (nivel con m de Antamina, e0 con D854) y leps_compuesta.
Banda: nivel (φ′e=0, P5–P95 por bootstrap de sets: media de φ′1_set + 20·e0_set con la m de cada hipótesis) combinado con la
curvatura entre dos hipótesis: «curvatura desde 1 MPa» (m = 0.85 en todo el rango, nivel reajustado) y «sin curvatura» (m = 1).
Contraste con los ensayos mundiales de σ_a a 7.9 MPa, cada uno a su e. Escribe a33_curva_propuesta.json y figuras_leps2/Fig_compuesta.png."""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis")); sys.path.insert(0, str(AQ))
from modelos import sigma1, tau_leps2  # noqa: E402
from lepsp_r6 import datos  # noqa: E402
import leps_compuesta as LC  # noqa: E402
A32 = json.load(open(AQ / "a32_curva_compuesta.json", encoding="utf-8"))
C_DS = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8"))["datos"]["c_ds"]
A = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
A["set"] = A.fuente_id + "|" + A.set_id.astype(str); A["e"] = A.e0_adoptado; A["tx"] = A.tipo == "TX"
SA = list(dict.fromkeys(A.set)); E_SET = np.array([A[A.set == s].e.mean() for s in SA]); EB, OM = 0.45, 20.0


def phi1_sets(m):
    ph = []
    for s in SA:
        g = A[A.set == s]; tx = g.tx.values
        def r(p):
            rr = np.empty(len(g))
            if tx.any():
                s3 = g.s3.values[tx]; rr[tx] = np.log(sigma1(tau_leps2, s3, p[0], m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
            if (~tx).any():
                rr[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], p[0], m)) - np.log(g.tau_ds.values[~tx]))
            return rr
        ph.append(least_squares(r, [40.0], bounds=([15], [70])).x[0])
    return np.array(ph)


P = dict(LC.PAR_DEF, pe0=A32["pe0_antamina"], m_a=A32["m_antamina"])
rng = np.random.default_rng(33); HIP = {"compuesta": 1.0, "m085": 0.85}
niv = {}
for k, m in HIP.items():
    v = phi1_sets(m) + OM * E_SET
    b = [v[rng.integers(0, len(v), len(v))].mean() for _ in range(4000)]
    niv[k] = dict(pe0=float(v.mean()), p5=float(np.percentile(b, 5)), p95=float(np.percentile(b, 95)), sd=float(np.std(b, ddof=1)))
print("nivel φ′e0 (P5–P95):", {k: f"{v['pe0']:.2f} ({v['p5']:.2f}–{v['p95']:.2f})" for k, v in niv.items()})
SN = np.unique(np.round(np.concatenate([np.geomspace(0.01, 15, 120), [0.5, 1, 2, 3, 4.6, 7.86, 10, 15]]), 4))
lin = lambda pe0: dict(P, pe0=pe0, m_a=1.0, m_h=1.0)
m85 = lambda pe0: dict(P, pe0=pe0, m_a=0.85, m_h=0.85)
cen = LC.phis(SN, EB, P)
lo = np.minimum(LC.phis(SN, EB, dict(P, pe0=niv["compuesta"]["p5"])), LC.phis(SN, EB, m85(niv["m085"]["p5"])))
hi = np.maximum(LC.phis(SN, EB, dict(P, pe0=niv["compuesta"]["p95"])), LC.phis(SN, EB, lin(niv["compuesta"]["p95"])))
W = datos(); W = W[~W.cens] if "cens" in W else W; k = (W.sn > P["s_a"]) & (W.sn <= 7.9)
d = np.degrees(np.arctan(W.tau[k] / W.sn[k])) - LC.phis(W.sn[k].values, W.e[k].values, P)
out = dict(parametros=P, nivel=niv, sn=SN.tolist(), phi=cen.tolist(), phi_lo=lo.tolist(), phi_hi=hi.tolist(),
           mundo_46_786=dict(n=int(k.sum()), bajo=int((d < 0).sum()), mediana=float(np.median(d))),
           hipotesis=dict(m085=m85(niv["m085"]["pe0"]), lineal=lin(niv["compuesta"]["pe0"])))
json.dump(out, open(AQ / "a33_curva_propuesta.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
for s in (0.3, 1, 2, 4.23, 7.86, 10, 15):
    j = int(np.argmin(np.abs(SN - s))); print(f"  σ′n {s:5.2f} MPa: φ′s {cen[j]:.1f}°  banda {lo[j]:.1f}–{hi[j]:.1f}°")
print(f"ensayos mundiales {P['s_a']:.2f}–7.9 MPa frente a la curva: {out['mundo_46_786']['bajo']} de {out['mundo_46_786']['n']} bajo ella, mediana {out['mundo_46_786']['mediana']:+.1f}°")
