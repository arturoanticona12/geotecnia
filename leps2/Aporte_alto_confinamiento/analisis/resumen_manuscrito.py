"""Números del manuscrito de Leps 3.0 probabilístico, leídos de los resultados (escribe resumen_manuscrito.json)."""
import sys, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import norm
sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent; sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(RAIZ / "leps3"))
from common import load_db, PA  # noqa: E402
from modelos import CLASE  # noqa: E402
import leps3 as L  # noqa: E402

S0 = 10 * PA
df = load_db()
df = df[(df.s3.isna() | (df.s3 >= 0.06)) & (df.sn > 0) & df.e.notna()].copy()
df["clase"] = df["Material Type"].map(CLASE)
df = df[df.groupby("Set").sn.transform("size") >= 2]
R = {"n_ensayos": len(df), "n_sets": df.Set.nunique(), "n_pub": df.Reference.nunique(),
     "sn_max": float(df.sn.max()), "n_sn_gt3": int((df.sn > 3).sum()), "n_pub_sn_gt3": int(df[df.sn > 3].Reference.nunique())}


def met(mu, sd, y):
    z = (y - mu) / sd
    return dict(n=int(len(y)), cob80=float(np.mean(np.abs(z) <= 1.2816)), cob90=float(np.mean(np.abs(z) <= 1.6449)),
                bajo10=float(np.mean(z < -1.2816)), ancho80=float(np.mean(2 * 1.2816 * sd)),
                crps=float(np.mean(sd * (z * (2 * norm.cdf(z) - 1) + 2 * norm.pdf(z) - 1 / np.sqrt(np.pi)))))


A = pd.read_csv(AQUI / "prob_cv_A.csv"); B = pd.read_csv(AQUI / "prob_cv_B.csv")
R["A_total"] = met(A.mu, A.sd, A.y); R["A0_total"] = met(A.mu0, A.sd0, A.y)
R["B"] = met(B.mu, B.sd, B.y); R["B_sets"] = int(B.Set.nunique()); R["B_pub"] = int(B.pub.nunique())
Ah = A[A.x >= np.log(2 / S0)]; R["A_sn_ge2"] = met(Ah.mu, Ah.sd, Ah.y)          # mismo rango que el modo B
# los mismos ensayos del modo B, predichos sin ensayos del sitio (modo A)
Am = B[["pub", "x", "y"]].round(10).merge(A.round(10), on=["pub", "x", "y"], how="left").drop_duplicates(["pub", "x", "y"])
R["A_en_B"] = met(Am.mu, Am.sd, Am.y); R["A_en_B"]["n_match"] = int(Am.mu.notna().sum())
# ancho del intervalo de 80 % en grados de φ′s, a σ′n = 3 MPa (aprox. lineal en ln τ)
P = json.load(open(AQUI / "leps3_prob_parametros.json"))
sd_ = np.sqrt(np.diag(P["Sig"])); R["sd_theta"] = float(sd_[0]); R["sd_m"] = float(sd_[1])
R["rho"] = float(P["Sig"][0][1] / sd_[0] / sd_[1]); R["fe"] = P["fe"]; R["sx"] = P["sx"]
# tabla φ′1 por calidad y e (previa) frente a Leps 2.0
R["tabla_phi1"] = {c: {f"{e:.2f}": [round(L.phi1_mediana(L.previa(c, e)), 1), {"buena": 53, "moderada": 50, "baja": 47}[c] - 20 * e]
                       for e in (0.3, 0.45, 0.6)} for c in ("buena", "moderada", "baja")}
# percentiles por σ′n para clase moderada e = 0.45 (Figura P1)
pr = L.previa("moderada", 0.45); sn = [0.3, 1, 3, 10, 15]
import warnings; warnings.simplefilter("ignore")
q = L.percentiles(sn, pr, (5, 10, 50, 90), n=200000)
R["P1"] = {f"{s:g}": {p: round(float(q[p][i]), 1) for p in q} for i, s in enumerate(sn)}
q2 = L.percentiles(sn, pr, (10, 50, 90), material_nuevo=False, n=200000)
R["P1_envolvente_media"] = {f"{s:g}": {p: round(float(q2[p][i]), 1) for p in q2} for i, s in enumerate(sn)}
# probabilidad de m > 1 en la previa
R["P_m_gt1_previa"] = float(1 - norm.cdf((1 - L.MU_M) / np.sqrt(L.SIGMA[1, 1])))
# ejemplo de actualización (hornfels 1 m del yacimiento)
d = pd.read_csv(RAIZ / "analisis_antamina" / "drenados_utilizables.csv")
g = d[d.set_a == "W2022|HF-1.0m-IDIEM-mono"].sort_values("s3")
po = L.actualizar(L.previa("moderada", 0.31), g.s3.values, g.s1.values)
qa = L.percentiles(sn, L.previa("moderada", 0.31), (10, 50, 90), n=200000); qb = L.percentiles(sn, po, (10, 50, 90), n=200000)
R["P3"] = {"s3": g.s3.round(3).tolist(), "s1": g.s1.round(3).tolist(), "phi1_previa": round(L.phi1_mediana(L.previa("moderada", 0.31)), 1),
           "phi1_post": round(L.phi1_mediana(po), 1), "m_post": round(float(po.media[1]), 3),
           "previa": {f"{s:g}": [round(float(qa[p][i]), 1) for p in (10, 50, 90)] for i, s in enumerate(sn)},
           "post": {f"{s:g}": [round(float(qb[p][i]), 1) for p in (10, 50, 90)] for i, s in enumerate(sn)}}
json.dump(R, open(AQUI / "resumen_manuscrito.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in R.items() if k not in ("fe", "sx")}, indent=1, ensure_ascii=False))
