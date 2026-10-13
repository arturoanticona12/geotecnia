"""Leps-P, ronda 6: verosimilitud perfilada de φ′∞ con el modelo extendido (datos depurados, ln Dmax, ζ por clase,
truncamiento en φ′1 ≥ 31° y censura por deformación). Para cada φ′∞ se maximiza respecto de ζ0 (continuo); en cada ζ0 el
modelo se ajusta (EM de la censura + Gauss–Newton + REML de ψ) y se evalúa la log-verosimilitud de los datos
OBSERVADOS (ModeloR6.ll_obs), que es comparable entre puntos. Variante sin censura con «nocens».
Uso:  python lepsp_perfil6.py <parte> <φ1,φ2,...> [nocens]   → lepsp_perfil6[_nocens]_<parte>.json
      python lepsp_perfil6.py unir [nocens]                   → lepsp_perfil6[_nocens].json"""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
from scipy.optimize import minimize_scalar
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_r6 import datos, ModeloR6, BETA0, PSI0  # noqa: E402

CENS = "nocens" not in sys.argv
SUF = "" if CENS else "_nocens"
d = datos()


def ajuste(T, z, psi0, beta0, ycache):
    dd = d.copy()
    if CENS and ycache is not None:
        dd["y"] = ycache                                   # arranque del EM con la imputación anterior
    m = ModeloR6(dd, T, z, beta0, trunc=True, cens=CENS, clase_z=True, usar_D=True).ajustar_nl(psi0, it_cens=6)
    return m.ll_obs(), m


def perfil_phi(ph, psi0, beta0):
    T = np.tan(np.radians(ph)); cache = {"psi": psi0, "beta": beta0, "y": None}; res = {}

    def f(z):
        ll, m = ajuste(T, z, cache["psi"], cache["beta"], cache["y"])
        cache.update(psi=m.psi, beta=m.beta_nl, y=m.dd.y.values.copy()); res[z] = (ll, m); return -ll
    r = minimize_scalar(f, bounds=(0.10, 0.70), method="bounded", options=dict(xatol=0.006))
    ll, m = res[r.x]
    return dict(phi=ph, zeta=float(r.x), ml=ll, psi=m.psi.tolist(), beta=m.beta_nl.tolist()), m


if __name__ == "__main__":
    t0 = time.time()
    if sys.argv[1] == "unir":
        P = []
        for f in sorted(AQ.glob(f"lepsp_perfil6{SUF}_*.json")):
            P += json.load(open(f, encoding="utf-8"))["perfil"]
        U = {}
        for r in P:
            if r["phi"] not in U or r["ml"] > U[r["phi"]]["ml"]:
                U[r["phi"]] = r
        P = sorted(U.values(), key=lambda r: r["phi"]); mx = max(r["ml"] for r in P)
        for r in P:
            print(f"  φ′∞ {r['phi']:5.1f}°  ζ0 {r['zeta']:.3f}  ΔML {r['ml'] - mx:+7.2f}")
        json.dump(dict(perfil=P, ml_max=mx, censura=CENS, n=len(d), sets=int(d.Set.nunique()), pubs=int(d.pub.nunique()), labs=int(d.lab.nunique())),
                  open(AQ / f"lepsp_perfil6{SUF}.json", "w", encoding="utf-8"), indent=1)
        sys.exit()
    parte = sys.argv[1]; PH = [float(v) for v in sys.argv[2].split(",")]
    m0 = ModeloR6(d, np.tan(np.radians(25.0)), 0.30, BETA0, cens=CENS).ajustar_nl(PSI0)
    psi, beta = m0.psi, m0.beta_nl; res = []
    for ph in PH:
        r, m = perfil_phi(ph, psi, beta); res.append(r); psi, beta = m.psi, m.beta_nl
        print(f"  φ′∞ {ph:5.1f}°  ζ0 {r['zeta']:.3f}  ll_obs {r['ml']:.2f} ({time.time()-t0:.0f} s)", flush=True)
        json.dump(dict(perfil=res), open(AQ / f"lepsp_perfil6{SUF}_{parte}.json", "w", encoding="utf-8"), indent=1)
