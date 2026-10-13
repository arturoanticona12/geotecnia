"""Leps-P, ronda 6: parámetros de la forma acotada con el modelo extendido (datos depurados, ln Dmax, ζ por clase,
truncamiento y censura). Cresta del perfil de lepsp_perfil6.json (puntos con ΔML > −6 respecto del máximo, cada uno
reajustado en su ζ0 óptimo; pesos ∝ exp(ML)); MCMC de ψ en el óptimo (4 cadenas de 12 000 + 3 000; sensibilidad a la
previa 0.1 y 0.5 con 6 000 + 2 000). La forma «acotada» anterior queda como «acotada_r5».
Escribe lepsp_parametros.json (en analisis/) y lepsp_mcmc6.json."""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_r6 import datos, ModeloR6, NOMBRES, D_REF, ETA_T, EPS_CENS  # noqa: E402
from lepsp_mcmc3 import mcmc, hiper_nat  # noqa: E402

if __name__ == "__main__":
    t0 = time.time(); d = datos()
    P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8")); PR = json.load(open(AQ / "lepsp_perfil6.json", encoding="utf-8"))
    P["formas"]["acotada_r5"] = P["formas"]["acotada"]; diag = {}
    mx = PR["ml_max"]; sel = [r for r in PR["perfil"] if r["ml"] > mx - 6.0]; pts = []
    for r in sel:
        mg = ModeloR6(d, np.tan(np.radians(r["phi"])), r["zeta"], np.array(r["beta"])).ajustar_nl(np.array(r["psi"]), it_cens=6)
        pts.append(dict(phi=r["phi"], zeta=r["zeta"], ml=r["ml"], mod=mg))
        print(f"  cresta φ′∞ {r['phi']:.0f}°: reajustado ({time.time()-t0:.0f} s)", flush=True)
    ml = np.array([p["ml"] for p in pts]); wg = np.exp(ml - ml.max()); wg /= wg.sum()
    wt = wg / np.cos(np.radians([p["phi"] for p in pts])) ** 2; wt /= wt.sum()
    iopt = int(np.argmax(ml)); mopt = pts[iopt]["mod"]
    med = lambda ww, k: float(np.sum(ww * [p[k] for p in pts]))
    print(f"cresta: {len(pts)} puntos (φ′∞ {pts[0]['phi']:.0f}–{pts[-1]['phi']:.0f}°); óptimo {pts[iopt]['phi']}°, ζ0 {pts[iopt]['zeta']:.3f}; "
          f"media φ′∞ {med(wg, 'phi'):.1f}° (tan {med(wt, 'phi'):.1f}°) ({time.time()-t0:.0f} s)", flush=True)
    ch, dg = mcmc(mopt, 12000, 3000); diag["acotada"] = dg
    print(f"MCMC: R̂ máx {max(dg['rhat']):.3f}; ESS bulk mín {min(dg['ess_bulk']):.0f}; tail mín {min(dg['ess_tail']):.0f} ({time.time()-t0:.0f} s)", flush=True)
    for s in (0.1, 0.5):
        chs, dgs = mcmc(mopt, 6000, 2000, s=s, seed=21); diag[f"previa_{s}"] = dict(hiper=hiper_nat(chs), rhat_max=max(dgs["rhat"]))
        print(f"  previa {s}: R̂ máx {max(dgs['rhat']):.3f} ({time.time()-t0:.0f} s)", flush=True)
    diag["previa_0.25"] = dict(hiper=hiper_nat(ch))
    todas = ch.reshape(-1, 8); rng = np.random.default_rng(11); idx = rng.choice(len(todas), 800, replace=False)
    gsel = rng.choice(len(pts), 800, p=wg); mues = []
    for p, g in zip(todas[idx], gsel):
        pg = p - mopt.psi + pts[g]["mod"].psi; mg = pts[g]["mod"]; mg.relinealizar(); _, _, Cb = mg.reml(pg, devolver=True)
        mues.append(dict(psi=pg.tolist(), beta=mg.beta_nl.tolist(), cov_beta=Cb.tolist(), phi_cs=pts[g]["phi"], zeta=pts[g]["zeta"]))
    se = np.sqrt(np.clip(np.diag(mopt.cov_beta), 0, None))
    P["formas"]["acotada"] = dict(nombres=NOMBRES, efectos="eta_zeta", psi=mopt.psi.tolist(), beta=mopt.beta_nl.tolist(), cov_beta=mopt.cov_beta.tolist(),
                                  phi_cs=pts[iopt]["phi"], zeta=pts[iopt]["zeta"], muestras=mues, ml=float(ml.max()), hiper=hiper_nat(ch),
                                  D_ref_mm=D_REF, eta_trunc=ETA_T, eps_censura=EPS_CENS,
                                  cresta=[dict(phi_cs=p["phi"], zeta=p["zeta"], ml=p["ml"], peso=float(x), peso_tan=float(y)) for p, x, y in zip(pts, wg, wt)])
    P["n"] = dict(P.get("n", {}), ensayos=int(len(d)), sets=int(d.Set.nunique()), pub=int(d.pub.nunique()), labs=int(d.lab.nunique()),
                  censurados=int(d.cens.sum()), sn_max=float(d.sn.max()))
    diag["cresta"] = dict(phi_media=med(wg, "phi"), zeta_media=med(wg, "zeta"), phi_media_tan=med(wt, "phi"), ml_opt=float(ml.max()))
    diag["beta"] = dict(zip(NOMBRES, map(float, mopt.beta_nl))); diag["se"] = dict(zip(NOMBRES, map(float, se)))
    json.dump(P, open(AQ / "lepsp_parametros.json", "w", encoding="utf-8"), indent=0)
    json.dump(diag, open(AQ / "lepsp_mcmc6.json", "w", encoding="utf-8"), indent=1)
    print(f"escrito lepsp_parametros.json y lepsp_mcmc6.json ({time.time()-t0:.0f} s)")
