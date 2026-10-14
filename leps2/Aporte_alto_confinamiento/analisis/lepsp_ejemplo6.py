"""Ejemplo trabajado del suplemento (ronda 6, revisores P14 y N): actualización de corte (Ec. 8) con las matrices publicadas,
en el punto de máxima verosimilitud de la cresta (plug-in), paso a paso, y contraste con la biblioteca (envolvente_diseno,
que promedia sobre la cresta y las muestras de los hiperparámetros).
Material: calidad baja, e de probeta 0.35, Dmax de probeta 178 mm; tres ensayos sintéticos (σ′3 = 0.3, 0.7, 1.2 MPa) de una
envolvente de potencia con φ′1 = 42° y m = 0.86; colocación e = 0.65 y Dmax de campo 1 m. Escribe lepsp_ejemplo6.json."""
import sys, json, math, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import chi2, norm
sys.stdout.reconfigure(encoding="utf-8"); warnings.simplefilter("ignore")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent / "leps3"))
from lepsp_r6 import media3, D_REF  # noqa: E402
import lepsp as L  # noqa: E402

P_ = json.load(open(AQ.parent / "hiber" / "hiber_parameters.json", encoding="utf-8")); F = P_["formas"]["acotada"]; S0 = P_["S0"]
B = np.array(F["beta"]); CB = np.array(F["cov_beta"]); psi = np.array(F["psi"]); T = math.tan(math.radians(F["phi_cs"])); Z0 = F["zeta"]
G2 = lambda p: np.array([[math.exp(2 * p[0]), math.tanh(p[2]) * math.exp(p[0] + p[1])], [math.tanh(p[2]) * math.exp(p[0] + p[1]), math.exp(2 * p[1])]])
GP, GS = G2(psi[0:3]), G2(psi[3:6]); se2 = lambda x: np.exp(2 * (psi[6] + psi[7] * np.asarray(x)))
ESC = P_["escala"]["general"]; CAL, E_LAB, D_LAB, E_C, D_C = "low", 0.35, 177.8, 0.65, 1000.0
deg = lambda y, x: np.degrees(np.arctan(np.exp(np.asarray(y) - np.asarray(x))))


def fz(x, e=E_LAB, D=D_LAB):
    dd = pd.DataFrame(dict(clase=[CAL] * len(np.atleast_1d(x)), e=e, x=np.atleast_1d(x), lnD=math.log(D / D_REF)))
    return media3(B, dd, T, Z0, True)          # f, J (7), Z (2)


# 1. ensayos → (σ′n, τ) con la conversión de la biblioteca (m de la previa a 1 MPa)
s3 = np.array([0.3, 0.7, 1.2]); th, m = math.log(math.tan(math.radians(42))), 0.86
snc = np.logspace(-1.5, 1.2, 400); tc = S0 * np.exp(th + m * np.log(snc / S0)); bb = np.arctan(m * tc / snc) / 2 + np.pi / 4
s1 = np.interp(s3, snc - tc / np.tan(bb), snc + tc * np.tan(bb))
m_c = L._m_conversion(L.previa(CAL, E_LAB, n=20000, D=D_LAB)); sn, tau = L._a_sn_tau(s3, s1, m_c)
x = np.log(sn / S0); y = np.log(tau / S0)
# 2. previa en los ensayos y chequeo de conflicto (Ec. 7)
f, Jm, Zm = fz(x); r = y - f; S = np.diag(se2(x))
V = Zm @ (GP + GS) @ Zm.T + Jm @ CB @ Jm.T + S; D2 = float(r @ np.linalg.solve(V, r)); p = float(1 - chi2.cdf(D2, len(x)))
# 3. actualización de corte en x̄ (Ec. 8): v = (u_lab [2], u_set [2], δβ [7]); P = diag(G_p, G_s, C_β)
xb = float(x.mean()); fb, Jb, Zb = fz([xb]); a = np.r_[Zb[0], Zb[0], Jb[0]]
Pm = np.zeros((11, 11)); Pm[:2, :2] = GP; Pm[2:4, 2:4] = GS; Pm[4:, 4:] = CB
g0 = float(a @ Pm @ a); w = 1 / se2(x); vq = 1 / (1 / g0 + w.sum()); q0 = float(vq * (r * w).sum())
Pa = Pm @ a; v = Pa * q0 / g0; Ppost = Pm - np.outer(Pa, Pa) / g0 * (1 - vq / g0)
# 4. tipo de roca = set nuevo del mismo laboratorio: se conserva lo aprendido del laboratorio y de β; el set vuelve a G_s
idx = np.r_[0, 1, 4:11]; vt = v[idx]; Pt = Ppost[np.ix_(idx, idx)]


def pred(sn_, e=E_LAB, D=D_LAB, act=True, campo=False):
    x_ = np.log(np.asarray(sn_) / S0); f_, J_, Z_ = fz(x_, e, D); A_ = np.c_[Z_, J_]
    if act:
        mu = f_ + A_ @ vt; var = np.einsum("ij,jk,ik->i", A_, Pt, A_) + np.einsum("ij,jk,ik->i", Z_, GS, Z_)
    else:
        mu = f_; var = np.einsum("ij,jk,ik->i", Z_, GP + GS, Z_) + np.einsum("ij,jk,ik->i", J_, CB, J_)
    if campo:
        var = var + math.log(D_C / D_LAB) ** 2 * (ESC["se_hk"] ** 2 + ESC["tau"] ** 2)
    sd = np.sqrt(var)
    return dict(P50=deg(mu, x_).tolist(), P05=deg(mu - 1.645 * sd, x_).tolist(), mu=mu.tolist(), sd=sd.tolist())


SN = [0.5, 1.0, 3.0, 5.0]
out = dict(material=dict(clase=CAL, e_lab=E_LAB, D_lab_mm=D_LAB, e_campo=E_C, D_campo_mm=D_C),
           ensayos=dict(s3=s3.tolist(), s1=s1.tolist(), m_conversion=m_c, sn=sn.tolist(), tau=tau.tolist(), x=x.tolist(), y=y.tolist()),
           previa_en_ensayos=dict(f=f.tolist(), r=r.tolist(), sigma_eps=np.sqrt(np.diag(S)).tolist(), z=Zm.tolist(), D2=D2, p=p),
           corte=dict(x_bar=xb, a=a.tolist(), g0=g0, q0=q0, var_q0=vq, desplaz_eta_lab=float(v[0]), desplaz_zeta_lab=float(v[1]),
                      desplaz_eta_set=float(v[2]), desplaz_beta=v[4:].tolist()),
           matrices=dict(beta=B.tolist(), C_beta=CB.tolist(), G_p=GP.tolist(), G_s=GS.tolist(), a0=float(psi[6]), a1=float(psi[7]),
                         phi_inf=F["phi_cs"], zeta0=Z0, nombres=F["nombres"]),
           sn=SN, previa_lab=pred(SN, act=False), actualizada_lab=pred(SN), actualizada_campo=pred(SN, E_C, D_LAB, True, True),
           previa_campo=pred(SN, E_C, D_LAB, False, True), sn_max_ensayos=float(sn.max()))
dis = np.minimum(np.array(out["actualizada_campo"]["P05"]), np.array(out["previa_campo"]["P05"]))
out["diseno_P05"] = np.where(np.array(SN) > sn.max(), dis, out["actualizada_campo"]["P05"]).tolist()
lib = L.envolvente_diseno(CAL, E_LAB, E_C, D_LAB, D_C, ensayos=dict(s3=s3, s1=s1), sn=SN, n=40000)
out["biblioteca"] = dict(P50=lib.tabla.phi_P50.tolist(), P05=lib.tabla.phi_P05.tolist(), p=lib.p_conflicto)
json.dump(out, open(AQ / "lepsp_ejemplo6.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(f"ensayos: σ′n {np.round(sn, 3)} MPa, φ′s {np.round(deg(y, x), 1)}°, m de conversión {m_c:.3f}")
print(f"chequeo: D² = {D2:.2f}, p = {p:.3f}; residuos {np.round(r, 3)}; σε {np.round(np.sqrt(np.diag(S)), 3)}")
print(f"corte: x̄ = {xb:.3f}, g0 = {g0:.4f}, q̂0 = {q0:.4f}, Var(q0) = {vq:.5f}; Δη lab {v[0]:+.4f}, Δη set {v[2]:+.4f}")
for k in ("previa_lab", "actualizada_lab", "previa_campo", "actualizada_campo"):
    o = out[k]; print(f"  {k:18s} " + "  ".join(f"{s:g} MPa {a_:.1f}/{b_:.1f}" for s, a_, b_ in zip(SN, o["P50"], o["P05"])))
print("  diseño P05        " + "  ".join(f"{s:g} MPa {v_:.1f}" for s, v_ in zip(SN, out["diseno_P05"])))
print("  biblioteca        " + "  ".join(f"{s:g} MPa {a_:.1f}/{b_:.1f}" for s, a_, b_ in zip(SN, out["biblioteca"]["P50"], out["biblioteca"]["P05"])) + f"  p = {lib.p_conflicto:.3f}")
