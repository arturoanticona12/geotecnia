"""Ronda 6: descomposición de la varianza de ln τ de la envolvente media de un material nuevo con el modelo extendido
(ln Dmax, ζ por clase), a 1, 3 y 10 MPa. Componentes: efectos fijos (J C_β Jᵀ), cresta (φ′∞, ζ0) entre muestras,
publicación (zᵀG_p z), material (zᵀG_s z) y escala a campo (ln(D_f/D_l)²·(EE² + τ_D²), τ_D por laboratorio). Como G_s ya
no absorbe el tamaño (ln Dmax está en el modelo; revisor E2), no hay doble conteo. Razones de tamaño: de 100 mm (referencia
de la Tabla 3) y de 178 mm (laboratorio del ejemplo) a 1 m. Escribe lepsp_varianza6.json."""
import sys, json, math
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_r6 import media3, D_REF  # noqa: E402

P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8")); F = P["formas"]["acotada"]; S0 = P["S0"]
G2 = lambda p: np.array([[math.exp(2 * p[0]), math.tanh(p[2]) * math.exp(p[0] + p[1])], [math.tanh(p[2]) * math.exp(p[0] + p[1]), math.exp(2 * p[1])]])
psi = np.median(np.array([s["psi"] for s in F["muestras"]]), axis=0); Gp, Gs = G2(psi[0:3]), G2(psi[3:6]); E = P["escala"]["general"]
out = dict(tau_D=E["tau"], se_hk=E["se_hk"])
for Dl, etq in ((D_REF, "100 mm"), (177.8, "178 mm")):
    RAZ = math.log(1000.0 / Dl)
    for cal, e in (("low", 0.65), ("moderate", 0.45)):
        for sn in (1.0, 3.0, 10.0):
            x = math.log(sn / S0); dd = pd.DataFrame(dict(clase=[cal], e=[e], x=[x], lnD=[math.log(Dl / D_REF)]))
            T = math.tan(math.radians(F["phi_cs"]))
            f, J, Zr = media3(np.array(F["beta"]), dd, T, F["zeta"], True); z = Zr[0]
            fs = [media3(np.array(s["beta"]), dd, math.tan(math.radians(s["phi_cs"])), s["zeta"], True)[0][0] for s in F["muestras"]]
            comp = dict(efectos_fijos=float(J[0] @ np.array(F["cov_beta"]) @ J[0]), cresta=float(np.var(fs)),
                        publicacion=float(z @ Gp @ z), material=float(z @ Gs @ z), escala_campo=RAZ ** 2 * (E["se_hk"] ** 2 + E["tau"] ** 2))
            tot = sum(comp.values()); phi = math.degrees(math.atan(math.exp(f[0] - x)))
            k = f"{cal} e={e} σ′n={sn:g} D={etq}"; out[k] = dict(comp=comp, total=tot, phi_mediana=phi, ensayo=float(math.exp(2 * (psi[6] + psi[7] * x))), razon=1000.0 / Dl)
            sg = lambda v: math.degrees(math.sqrt(v) * math.sin(math.radians(phi)) * math.cos(math.radians(phi)))
            print(f"{k:36s} φ̃ {phi:4.1f}°  " + "  ".join(f"{n} {100 * v / tot:4.0f} % ({sg(v):.1f}°)" for n, v in comp.items()) + f"  | total DE {sg(tot):.1f}°")
json.dump(out, open(AQ / "lepsp_varianza6.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
