"""Leps-P, ronda 4: parámetros de la forma acotada con efectos aleatorios en (η, ζ) de cada material (lepsp_acotada2).
- Cresta de (φ′∞, ζ0): perfil ML en grilla fina con ψ fija; los puntos con el 99.5 % del peso (previa plana en grados)
  se reajustan por completo; pesos finales ∝ exp(ML). Sensibilidad: previa uniforme en tan φ′∞ (peso × sec² φ′∞).
- MCMC de ψ en el óptimo (previas de lepsp_mcmc3: half-normal 0.25; sensibilidad 0.1 y 0.5), 4 cadenas, R̂ y ESS
  normalizados por rangos (arviz). Las muestras se trasladan a cada punto de la cresta (ψ − ψ_opt + ψ_g).
Escribe la forma «acotada» en lepsp_parametros.json (la de la ronda 3 queda como «acotada_r3») y lepsp_mcmc4.json."""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada2 import d, ModeloNL2, BETA0, PSI0, CL  # noqa: E402
from lepsp_mcmc3 import mcmc, hiper_nat  # noqa: E402

if __name__ == "__main__":
    t0 = time.time(); P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8")); diag = {}
    if "acotada_r3" not in P["formas"]:
        P["formas"]["acotada_r3"] = P["formas"]["acotada"]
    m0 = ModeloNL2(d, np.tan(np.radians(24.0)), 0.30, BETA0).ajustar_nl(PSI0)
    PH = np.arange(14.0, 32.01, 1.0); ZE = np.round(np.arange(0.175, 0.476, 0.025), 4)
    ML = np.full((len(PH), len(ZE)), -np.inf)
    for i, ph in enumerate(PH):
        for j, z in enumerate(ZE):
            ML[i, j], _ = ModeloNL2(d, np.tan(np.radians(ph)), z, BETA0).gn(m0.psi)
    w = np.exp(ML - ML.max()); w /= w.sum(); orden = np.argsort(w.ravel())[::-1]
    keep = orden[: int(np.searchsorted(np.cumsum(w.ravel()[orden]), 0.995)) + 1]
    print(f"cresta: {len(keep)} puntos con el 99.5 % del peso ({time.time()-t0:.0f} s)", flush=True)
    pts = []
    for q in keep:
        i, j = np.unravel_index(q, ML.shape)
        mg = ModeloNL2(d, np.tan(np.radians(PH[i])), ZE[j], BETA0).ajustar_nl(m0.psi)
        mlg, _ = mg.gn(mg.psi); pts.append(dict(phi=float(PH[i]), zeta=float(ZE[j]), ml=float(mlg), mod=mg))
    mls = np.array([p["ml"] for p in pts]); wg = np.exp(mls - mls.max()); wg /= wg.sum()
    wt = wg / np.cos(np.radians([p["phi"] for p in pts])) ** 2; wt /= wt.sum()           # previa uniforme en tan φ′∞
    iopt = int(np.argmax(mls)); mopt = pts[iopt]["mod"]
    med = lambda ww, k: float(np.sum(ww * [p[k] for p in pts]))
    print(f"óptimo φ′∞ = {pts[iopt]['phi']}°, ζ0 = {pts[iopt]['zeta']}, ML {mls.max():.2f}; media φ′∞ {med(wg, 'phi'):.1f}° (tan: {med(wt, 'phi'):.1f}°), "
          f"ζ0 {med(wg, 'zeta'):.3f} ({time.time()-t0:.0f} s)", flush=True)
    ch, dg = mcmc(mopt, 6000, 2000); diag["acotada"] = dg
    print(f"MCMC: R̂ máx {max(dg['rhat']):.3f}; ESS bulk mín {min(dg['ess_bulk']):.0f}; tail mín {min(dg['ess_tail']):.0f} ({time.time()-t0:.0f} s)", flush=True)
    for s in (0.1, 0.5):
        chs, dgs = mcmc(mopt, 3000, 1500, s=s, seed=21); diag[f"previa_{s}"] = dict(hiper=hiper_nat(chs), rhat_max=max(dgs["rhat"]))
    diag["previa_0.25"] = dict(hiper=hiper_nat(ch))
    todas = ch.reshape(-1, 8); rng = np.random.default_rng(11); idx = rng.choice(len(todas), 800, replace=False)
    gsel = rng.choice(len(pts), 800, p=wg); mues = []
    for p, g in zip(todas[idx], gsel):
        pg = p - mopt.psi + pts[g]["mod"].psi; mg = pts[g]["mod"]; mg.relinealizar(); _, _, Cb = mg.reml(pg, devolver=True)
        mues.append(dict(psi=pg.tolist(), beta=mg.beta_nl.tolist(), cov_beta=Cb.tolist(), phi_cs=pts[g]["phi"], zeta=pts[g]["zeta"]))
    P["formas"]["acotada"] = dict(nombres=CL + ["e"], efectos="eta_zeta", psi=mopt.psi.tolist(), beta=mopt.beta_nl.tolist(), cov_beta=mopt.cov_beta.tolist(),
                                  phi_cs=pts[iopt]["phi"], zeta=pts[iopt]["zeta"], muestras=mues, ml=float(mls.max()), hiper=hiper_nat(ch),
                                  cresta=[dict(phi_cs=p["phi"], zeta=p["zeta"], ml=p["ml"], peso=float(x), peso_tan=float(y)) for p, x, y in zip(pts, wg, wt)])
    diag["cresta"] = dict(grilla_phi=PH.tolist(), grilla_zeta=ZE.tolist(), ml=ML.tolist(), phi_media=med(wg, "phi"), zeta_media=med(wg, "zeta"),
                          phi_media_tan=med(wt, "phi"), ml_opt=float(mls.max()))
    json.dump(P, open(AQ / "lepsp_parametros.json", "w", encoding="utf-8"), indent=0)
    json.dump(diag, open(AQ / "lepsp_mcmc4.json", "w", encoding="utf-8"), indent=1)
    print(f"escrito lepsp_parametros.json y lepsp_mcmc4.json ({time.time()-t0:.0f} s)")
