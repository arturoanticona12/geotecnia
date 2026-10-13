"""Leps-P, ronda 5: verosimilitud perfilada verdadera (ML completa) de la asíntota φ′∞.
Para cada φ′∞ de la lista se maximiza la log-verosimilitud ML respecto de ζ0 (continuo), de los efectos fijos (Gauss–
Newton) y de los parámetros de varianza ψ (reajustados, no fijos). También se ajustan por ML completa la forma
cuadrática y la de potencia (log–log), para comparar estructuras de media distintas. Uso:
  python lepsp_perfil.py <parte> <φ1,φ2,...>   → lepsp_perfil_<parte>.json
  python lepsp_perfil.py unir                  → lepsp_perfil.json"""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
from scipy.optimize import minimize, minimize_scalar
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada2 import d, ModeloNL2, BETA0, PSI0, CL  # noqa: E402
from lepsp_modelo import Modelo  # noqa: E402


def ml_de(mod, psi):
    r = mod.reml(psi, devolver=True)
    if not isinstance(r, tuple):
        return -1e12
    ll, b, C = r
    return ll - 0.5 * np.linalg.slogdet(C)[1]          # ML = REML + ½ log|XᵀV⁻¹X|


def fit_ml_nl(T, z, psi0):
    m = ModeloNL2(d, T, z, BETA0); psi = np.array(psi0, float)
    for _ in range(3):
        m.gn(psi)
        r = minimize(lambda p: -ml_de(m, p), psi, method="Nelder-Mead", options=dict(maxiter=4000, xatol=1e-4, fatol=1e-5)); psi = r.x
    m.gn(psi); return ml_de(m, psi), psi, m


def perfil_phi(ph, psi0):
    T = np.tan(np.radians(ph)); cache = {}

    def f(z):
        mlv, psi, _ = fit_ml_nl(T, z, cache.get("psi", psi0)); cache["psi"] = psi; cache[z] = (mlv, psi); return -mlv
    r = minimize_scalar(f, bounds=(0.08, 0.70), method="bounded", options=dict(xatol=0.004))
    mlv, psi = cache[r.x]
    return dict(phi=ph, zeta=float(r.x), ml=float(mlv), psi=psi.tolist())


def fit_ml_lineal(X, nom):
    m = Modelo(d, X, nom).ajustar()
    r = minimize(lambda p: -ml_de(m, p), m.psi, method="Nelder-Mead", options=dict(maxiter=6000, xatol=1e-4, fatol=1e-5))
    return float(-r.fun)


if __name__ == "__main__":
    t0 = time.time()
    if sys.argv[1] == "unir":
        P = []
        for f in sorted(AQ.glob("lepsp_perfil_*.json")):
            if f.name != "lepsp_perfil.json":
                P += json.load(open(f, encoding="utf-8"))["perfil"]
        U = {}                                                  # un punto por φ′∞ (partes repetidas: el de mayor ML)
        for r in P:
            if r["phi"] not in U or r["ml"] > U[r["phi"]]["ml"]:
                U[r["phi"]] = r
        P = sorted(U.values(), key=lambda r: r["phi"]); out = dict(perfil=P)
        dum = np.c_[[(d.clase == c).values.astype(float) for c in CL]].T
        out["ml_cuadratica"] = fit_ml_lineal(np.c_[dum, d.e.values, d.x.values, d.x.values ** 2], CL + ["e", "x", "x2"])
        out["ml_potencia"] = fit_ml_lineal(np.c_[dum, d.e.values, d.x.values], CL + ["e", "x"])
        mx = max(r["ml"] for r in P); out["ml_max"] = mx
        for r in P:
            print(f"  φ′∞ {r['phi']:5.1f}°  ζ0 {r['zeta']:.3f}  ΔML {r['ml'] - mx:+7.2f}")
        print(f"ML máx acotada {mx:.2f} | cuadrática {out['ml_cuadratica']:.2f} | potencia {out['ml_potencia']:.2f} ({time.time()-t0:.0f} s)")
        json.dump(out, open(AQ / "lepsp_perfil.json", "w", encoding="utf-8"), indent=1); sys.exit()
    parte = sys.argv[1]; PH = [float(v) for v in sys.argv[2].split(",")]
    m0 = ModeloNL2(d, np.tan(np.radians(24.0)), 0.30, BETA0).ajustar_nl(PSI0); res = []
    for ph in PH:
        r = perfil_phi(ph, m0.psi); res.append(r)
        print(f"  φ′∞ {ph:5.1f}°  ζ0 {r['zeta']:.3f}  ML {r['ml']:.2f} ({time.time()-t0:.0f} s)", flush=True)
        json.dump(dict(perfil=res), open(AQ / f"lepsp_perfil_{parte}.json", "w", encoding="utf-8"), indent=1)
