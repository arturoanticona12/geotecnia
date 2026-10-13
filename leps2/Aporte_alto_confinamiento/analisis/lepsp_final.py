"""Leps-P, paso 3: ajuste final (M2: clase, e, x, x²; 3 niveles; σε(x)) con muestreo MCMC de los hiperparámetros y
banda de forma para la extrapolación. Escribe lepsp_parametros.json (punto + muestras de hiperparámetros)."""
import sys, json, warnings, time
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo, mcmc_hiper, S0  # noqa: E402

d = preparar(load_db(), CLASE)
CL = ["good", "moderate", "low"]
dum = np.c_[[(d.clase == c).values.astype(float) for c in CL]].T
FORMAS = {"x2": (np.c_[dum, d.e.values, d.x.values, d.x.values ** 2], CL + ["e", "x", "x2"]),
          "potencia": (np.c_[dum, d.e.values, d.x.values], CL + ["e", "x"])}
SAL = {}
for forma, (X, NOM) in FORMAS.items():
    print(f"\n=== forma {forma}")
    SAL[forma] = None
    t = time.time(); m = Modelo(d, X, NOM).ajustar(); print(f"REML en {time.time()-t:.0f} s:", {k: round(float(v), 4) for k, v in m.resumen()["beta"].items()})
    cads = [mcmc_hiper(m, n=2500, burn=1000, seed=s) for s in (1, 2)]
    cad = np.vstack([c for c, _ in cads]); print(f"MCMC 2 cadenas: aceptación {[round(a, 2) for _, a in cads]}, {time.time()-t:.0f} s")
    # Gelman–Rubin por parámetro
    W = np.mean([c.var(0, ddof=1) for c, _ in cads], 0); Bv = np.var([c.mean(0) for c, _ in cads], 0, ddof=1) * len(cads[0][0])
    n_ = len(cads[0][0]); rhat = np.sqrt(((n_ - 1) / n_ * W + Bv / n_) / W); print("R̂:", np.round(rhat, 3))
    SAL[forma] = (m, cad, NOM)
m, cad, NOM = SAL["x2"]
# resumen de hiperparámetros
def hp(p):
    Gp, Gs, a = m.desempacar(p)
    return [np.sqrt(Gp[0, 0]), np.sqrt(Gp[1, 1]), Gp[0, 1] / np.sqrt(Gp[0, 0] * Gp[1, 1]), np.sqrt(Gs[0, 0]), np.sqrt(Gs[1, 1]),
            Gs[0, 1] / np.sqrt(Gs[0, 0] * Gs[1, 1]), np.exp(a[0]), a[1]]
H = np.array([hp(p) for p in cad[::5]]); nh = ["sdθ_pub", "sdm_pub", "ρ_pub", "sdθ_set", "sdm_set", "ρ_set", "σε(0)", "a1"]
print("hiperparámetros: punto REML y mediana [IC 90 %] posterior")
for i, nmh in enumerate(nh):
    print(f"  {nmh:8s} {hp(m.psi)[i]:+.4f}  {np.median(H[:, i]):+.4f} [{np.percentile(H[:, i], 5):+.4f}, {np.percentile(H[:, i], 95):+.4f}]")
# para cada muestra de hiperparámetros: β | ψ ~ N(β̂ψ, Cψ)  → se guardan 400 pares (ψ, β̂, Cβ) por forma
ESC = json.load(open(AQUI / "lepsp_escala.json"))["similares"]
out = dict(clases=CL, S0=S0, n=dict(ensayos=len(d), sets=int(d.Set.nunique()), pub=int(d.pub.nunique()), sn_max=float(d.sn.max())),
           escala=dict(bD=ESC["b"], se=ESC["se"], tau=ESC["tau"], kappa=ESC["kappa"], grupos=ESC["n"]), formas={})
for forma, (mm, cc, nom) in SAL.items():
    mues = []
    for p in cc[::max(1, len(cc) // 400)][:400]:
        ll, b, Cb = mm.reml(p, devolver=True); mues.append(dict(psi=p.tolist(), beta=b.tolist(), cov_beta=Cb.tolist()))
    out["formas"][forma] = dict(nombres=nom, psi=mm.psi.tolist(), beta=mm.beta.tolist(), cov_beta=mm.cov_beta.tolist(), muestras=mues)
json.dump(out, open(AQUI / "lepsp_parametros.json", "w"), indent=0)
print("escrito lepsp_parametros.json")
