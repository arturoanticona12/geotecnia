"""¿Es representativa la validación plug-in de la predictiva que entrega la librería? Con todos los datos se compara, para
material nuevo (sin ensayos), la predictiva plug-in de la forma acotada (óptimo de la cresta, ψ y β puntuales: la que se
validó fuera de muestra) con la de lepsp.previa (mezcla del MCMC, cresta y truncamiento de pendiente), en mediana y DE de
ln τ por ensayo (puntual=True). Escribe lepsp_desplegada.json."""
import sys, json, math
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent / "leps3"))
import lepsp as L  # noqa: E402
from lepsp_acotada2 import media2  # noqa: E402

F = L._P["formas"]["acotada"]; G2 = lambda p: np.array([[math.exp(2 * p[0]), math.tanh(p[2]) * math.exp(p[0] + p[1])], [math.tanh(p[2]) * math.exp(p[0] + p[1]), math.exp(2 * p[1])]])
psi = np.array(F["psi"]); G = G2(psi[0:3]) + G2(psi[3:6]); C = np.array(F["cov_beta"])
CL = {"buena": "good", "moderada": "moderate", "baja": "low"}; SN = [0.3, 1.0, 3.0, 5.0, 7.9]; filas = []
for cal in CL:
    for e in (0.3, 0.45, 0.65):
        mat = L.previa(cal, e, n=60000, seed=4); x = np.log(np.array(SN) / L.S0)
        yl = L._media(mat, x) + np.random.default_rng(5).normal(size=(len(mat.th), len(x))) * L.sigma_eps(x, mat)
        dd = pd.DataFrame(dict(clase=[CL[cal]] * len(x), e=[e] * len(x), x=x))
        f, Jm, Z = media2(np.array(F["beta"]), dd, math.tan(math.radians(F["phi_cs"])), F["zeta"])
        sd = np.sqrt(np.einsum("ij,jk,ik->i", Z, G, Z) + np.einsum("ij,jk,ik->i", Jm, C, Jm) + np.exp(2 * (psi[6] + psi[7] * x)))
        for k, s in enumerate(SN):
            filas.append(dict(cal=cal, e=e, sn=s, dmed=float(np.median(yl[:, k]) - f[k]), ratio_sd=float(np.std(yl[:, k]) / sd[k]), sd_plugin=float(sd[k])))
T = pd.DataFrame(filas)
print(T.groupby("sn")[["dmed", "ratio_sd"]].agg(["min", "max"]).round(3).to_string())
out = dict(dmed_abs_max=float(T.dmed.abs().max()), dmed_rel_sd_max=float((T.dmed.abs() / T.sd_plugin).max()),
           ratio_sd_min=float(T.ratio_sd.min()), ratio_sd_max=float(T.ratio_sd.max()), por_sn=T.groupby("sn")[["dmed", "ratio_sd"]].mean().to_dict())
print(out)
json.dump(out, open(AQ / "lepsp_desplegada.json", "w", encoding="utf-8"), indent=1)
