"""Validación externa de la forma con los ensayos del sitio (no usados en la calibración): para cada set, actualización
de solo nivel con los ensayos de σ′n ≤ 1.5 MPa y predicción de los de σ′n ≥ 2 MPa con la cuadrática y con la acotada
(ambas ajustadas con toda la base; la acotada en el óptimo de la cresta). Conversión a (σ′n, τ) con m = 0.86."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent / "leps3"))
from lepsp_acotada import d, ModeloNL, disenio_m2, media  # noqa: E402
from lepsp_acotada_B import predB  # noqa: E402
from lepsp_modelo import Modelo, S0  # noqa: E402
import lepsp as L  # noqa: E402

G = json.load(open(AQ / "lepsp_acotada_grilla.json", encoding="utf-8"))
mq = Modelo(d, disenio_m2(d), ["g", "m", "l", "e", "x", "x2"]).ajustar()
mb = ModeloNL(d, np.tan(np.radians(G["opt"][0])), G["opt"][1], G["beta_opt"]).ajustar_nl(mq.psi)
S = pd.read_csv(AQ.parent / "analisis_antamina" / "drenados_utilizables.csv", low_memory=False)
S = S[S.escala.isin(["0.6 m", "1.0 m"]) & (S.relave_pct_masa_total.fillna(0) == 0)].copy(); S["e_use"] = S.e0_adoptado.fillna(S.e0)
CAL = {"Mármol": "low", "Hornfels": "moderate", "Intrusivo": "low"}
filas = []
for sid, g in S.groupby("set_a"):
    sn, tau = L._a_sn_tau(g.s3.values, g.s1.values, 0.86)
    te = pd.DataFrame(dict(sn=sn, x=np.log(sn / S0), y=np.log(tau / S0), e=float(g.e_use.iloc[0]), clase=CAL[g.litologia.iloc[0]]))
    # por rango: el laboratorio del sitio usó σ3 = 0.49, 0.98, 1.96 (y 2.45) MPa; se actualiza con los ensayos de las
    # tensiones inferiores y se predicen los del σ3 más alto del set
    s3 = g.s3.values; hi = np.where(s3 == s3.max())[0]; lo = np.where(s3 < s3.max())[0]
    if len(lo) < 2:
        continue
    Xq = disenio_m2(te); fb, Jb = media(mb.beta_nl, te, mb.T, mb.lam)
    muq, sdq = predB(Xq[lo] @ mq.beta, Xq[hi] @ mq.beta, Xq[lo], Xq[hi], mq.cov_beta, mq, te, lo, hi)
    mub, sdb = predB(fb[lo], fb[hi], Jb[lo], Jb[hi], mb.cov_beta, mb, te, lo, hi)
    for k, i in enumerate(hi):
        filas.append(dict(set=sid, lit=g.litologia.iloc[0], sn=te.sn[i], y=te.y[i], mu_q=muq[k], sd_q=sdq[k], mu_b=mub[k], sd_b=sdb[k]))
R = pd.DataFrame(filas)
for nm, a, b in (("cuadrática", "mu_q", "sd_q"), ("acotada", "mu_b", "sd_b")):
    z = (R.y - R[a]) / R[b]; c = R[b] * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi))
    R[f"crps_{a[-1]}"] = c
    print(f"{nm:11s} n={len(R)}  CRPS {c.mean():.4f}  sesgo ln τ {(R.y - R[a]).mean():+.4f}  z̄ {z.mean():+.2f}")
S_ = R.groupby("set")[["crps_q", "crps_b"]].mean()
print(S_.round(4).to_string())
json.dump(dict(n=len(R), sets=len(S_), crps_q=float(R.crps_q.mean()), crps_b=float(R.crps_b.mean()), sets_mejora=int((S_.crps_b < S_.crps_q).sum()),
               sesgo_q=float((R.y - R.mu_q).mean()), sesgo_b=float((R.y - R.mu_b).mean())),
          open(AQ / "lepsp_acotada_sitio.json", "w", encoding="utf-8"), indent=1)
