"""Análisis 1–3: ajuste por set (φ′1, m) en esfuerzos principales y posterior jerárquico de Leps 3.0 por set y litología.
Solo ensayos triaxiales drenados utilizables (CD y CD carga-descarga; cíclicos post-monótonos con su σ′3 de 350 kPa)."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
pd.set_option("display.width", 250); pd.set_option("display.max_rows", 200); pd.set_option("display.max_colwidth", 45)
AQUI = Path(__file__).parent; RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "analisis"))
from modelos import sigma1, tau_leps2  # noqa: E402
PA = 0.1013; S0 = 10 * PA
E = pd.read_csv(RAIZ / "datos_antamina" / "base" / "ensayos.csv", low_memory=False)
P = json.load(open(RAIZ / "analisis" / "leps3_prob_parametros.json"))

d = E[E.tipo_ensayo_std.str.startswith("Triaxial C", na=False) & ~E.tipo_ensayo_std.str.contains("CU", na=False)
      & E.excluir_envolvente.isna()].copy()
d["s3"] = d.sigma3f_kPa_std / 1000; d["s1"] = d.sigma1f_kPa_std / 1000; d["q"] = d.s1 - d.s3
d = d[(d.s3 > 0) & (d.q > 0)]
# set analítico: material y escala (las probetas de 1 m y de 6 in del mismo informe son sets distintos)
d["set_a"] = d.fuente_id + "|" + d.set_id.astype(str)
print(f"Ensayos drenados utilizables: {len(d)} en {d.set_a.nunique()} sets")

# ---------------------------------------------------------------- 2. ajuste por set en q
filas = []
for s, g in d.groupby("set_a"):
    s3, q = g.s3.values, g.q.values
    f1 = lambda p, m: np.log(sigma1(tau_leps2, s3, np.full(len(s3), p), m)[0] - s3) - np.log(q)
    r9 = least_squares(lambda p: f1(p[0], 0.86), [41], bounds=([15], [70]))
    fila = dict(set_a=s, fuente=g.fuente_id.iat[0], litologia=g.litologia.iat[0], clase=g.clase_desmonte_std.iat[0],
                escala=g.escala.iat[0], n=len(g), s3_min=s3.min(), s3_max=s3.max(), e0=g.e0_adoptado.median(),
                relave=g.relave_pct_masa_total.iat[0], Bg_max=g.Bg_pct.max(), phi1_m086=r9.x[0], m=np.nan, phi1=np.nan)
    if len(g) >= 3 and s3.max() / s3.min() >= 2:
        r = least_squares(lambda p: f1(p[0], p[1]), [41, 0.86], bounds=([15, 0.5], [70, 1.0]))
        fila.update(phi1=r.x[0], m=r.x[1])
    filas.append(fila)
S = pd.DataFrame(filas)
print("\nAjuste por set (φ′1 con m libre si hay ≥3 ensayos con razón σ3 ≥ 2; φ′1 con m = 0.86 siempre):")
print(S.round(3).to_string(index=False))


# ---------------------------------------------------------------- 3. posterior jerárquico (en ln τ–ln σn)
def a_tau_sn(s3, s1, m):
    """Conversión de Cylwik et al. (2025), Ecs. 13, 14 y 16, con el m del set."""
    D, Sm = s1 - s3, s1 + s3
    if abs(m - 1) < 1e-6:
        sp = D / Sm
    else:
        sp = (np.sqrt(4 * m * (m - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (m - 1) * D)
    return Sm / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


XB = np.array([-1.0, 0.0, 1.0]); SX = np.array(P["sx"]); Sig = np.array(P["Sig"]); fe = P["fe"]
CLASE_LEPS = {"Mármol": "low", "Hornfels": "moderate", "Intrusivo": "low", "Skarn": "moderate", "Mezcla": "moderate"}
post = []
for s, g in d.groupby("set_a"):
    srow = S[S.set_a == s].iloc[0]
    m_conv = srow.m if np.isfinite(srow.m) else 0.86
    sn, tau = a_tau_sn(g.s3.values, g.s1.values, m_conv)
    x = np.log(sn / S0); y = np.log(tau / S0)
    cl = CLASE_LEPS.get(srow.litologia, "moderate"); e0 = srow.e0 if np.isfinite(srow.e0) else 0.40
    m0 = np.array([fe[f"C(clase)[{cl}]"] + fe["e"] * e0, fe["x"]])
    Z = np.c_[np.ones(len(x)), x]; Rinv = np.diag(1 / SX[np.clip(np.digitize(x, XB), 0, 3)] ** 2)
    Si = np.linalg.inv(Sig); Pc = np.linalg.inv(Si + Z.T @ Rinv @ Z); mc = Pc @ (Si @ m0 + Z.T @ Rinv @ y)
    sd = np.sqrt(np.diag(Pc))
    post.append(dict(set_a=s, litologia=srow.litologia, clase_leps_previa=cl, e0=e0,
                     phi1_previa=np.degrees(np.arctan(np.exp(m0[0]))), phi1_post=np.degrees(np.arctan(np.exp(mc[0]))),
                     phi1_post_sd=np.degrees(sd[0] * np.exp(mc[0]) / (1 + np.exp(2 * mc[0]))), m_post=mc[1], m_post_sd=sd[1],
                     theta=mc[0], cov=json.dumps(Pc.tolist()), n=len(g), s3_max=g.s3.max()))
Q = pd.DataFrame(post)
Q["dif_post_previa"] = Q.phi1_post - Q.phi1_previa
print("\nPosterior por set (previa: modelo jerárquico mundial con la clase de Cylwik asignada y e0):")
print(Q.drop(columns=["cov", "theta"]).round(2).to_string(index=False))
print("\nResumen por litología (media de sets; diferencia posterior − previa):")
print(Q.groupby("litologia").agg(sets=("set_a", "size"), phi1_previa=("phi1_previa", "mean"), phi1_post=("phi1_post", "mean"),
                                 dif=("dif_post_previa", "mean"), m_post=("m_post", "mean")).round(2).to_string())
S.to_csv(AQUI / "sets_ajuste.csv", index=False); Q.to_csv(AQUI / "sets_posterior.csv", index=False)
d.to_csv(AQUI / "drenados_utilizables.csv", index=False)
