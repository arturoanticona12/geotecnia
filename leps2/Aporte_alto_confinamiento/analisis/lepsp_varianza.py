"""Descomposición de la varianza de ln τ de la envolvente media de un material nuevo (forma acotada), a 1, 3 y 10 MPa:
efectos fijos (J C_β Jᵀ en el óptimo), cresta (φ′cs, ζ) entre muestras, publicación (zᵀG_p z), material (zᵀG_s z),
escala a campo (ln(D_f/D_l)²·(EE² + τ²)) y, como referencia, la dispersión de ensayo σε². Escribe lepsp_varianza.json."""
import sys, json, math
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada2 import media2  # noqa: E402

P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8")); F = P["formas"]["acotada"]; S0 = P["S0"]
G2 = lambda p: np.array([[math.exp(2 * p[0]), math.tanh(p[2]) * math.exp(p[0] + p[1])], [math.tanh(p[2]) * math.exp(p[0] + p[1]), math.exp(2 * p[1])]])
psi = np.median(np.array([s["psi"] for s in F["muestras"]]), axis=0); Gp, Gs = G2(psi[0:3]), G2(psi[3:6])
SUPV = "tau_r3" if "--tau-r3" in sys.argv else "general"; E = P["escala"][SUPV]; RAZ = math.log(1000 / 177.8)
out = {}
for cal, e in (("low", 0.65), ("moderate", 0.45)):
    for sn in (1.0, 3.0, 10.0):
        x = math.log(sn / S0); dd = pd.DataFrame(dict(clase=[cal], e=[e], x=[x]))
        f, J, Zr = media2(np.array(F["beta"]), dd, math.tan(math.radians(F["phi_cs"])), F["zeta"]); z = Zr[0]   # gradiente respecto de (η, ζ)
        fs = [media2(np.array(s["beta"]), dd, math.tan(math.radians(s["phi_cs"])), s["zeta"])[0][0] for s in F["muestras"]]
        comp = dict(efectos_fijos=float(J[0] @ np.array(F["cov_beta"]) @ J[0]), cresta=float(np.var(fs)),
                    publicacion=float(z @ Gp @ z), material=float(z @ Gs @ z), escala_campo=RAZ ** 2 * (E["se_hk"] ** 2 + E["tau"] ** 2))
        tot = sum(comp.values()); phi = math.degrees(math.atan(math.exp(f[0] - x)))
        k = f"{cal} e={e} σ′n={sn:g}"; out[k] = dict(comp=comp, total=tot, phi_mediana=phi, ensayo=float(math.exp(2 * (psi[6] + psi[7] * x))))
        # en grados: dφ ≈ sen φ cos φ · d ln τ
        sg = lambda v: math.degrees(math.sqrt(v) * math.sin(math.radians(phi)) * math.cos(math.radians(phi)))
        print(f"{k:28s} φ̃ {phi:4.1f}°  " + "  ".join(f"{n} {100 * v / tot:4.0f} % ({sg(v):.1f}°)" for n, v in comp.items()) + f"  | total DE {sg(tot):.1f}°")
json.dump(out, open(AQ / ("lepsp_varianza_taur3.json" if SUPV == "tau_r3" else "lepsp_varianza.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
