"""Leps-P, MCMC de hiperparámetros (ronda 3).
- Formas: «acotada» (central), «x2» y «potencia».
- Acotada: (φ′cs, ζ) no identificados por separado (cresta): perfil ML en grilla fina con ψ fija → pesos ∝ exp(ML) con
  previa plana en la grilla; los puntos que acumulan el 99.5 % del peso se reajustan por completo (ψ y β). Las muestras
  de hiperparámetros se toman del MCMC en el óptimo y se trasladan a cada punto de la cresta (ψ − ψ_opt + ψ_g).
- Previas: DE ~ Half-Normal(s) con s = 0.25 (base; sensibilidad 0.1 y 0.5); ρ ~ U(−1, 1); a0 ~ N(−3.3, 1); a1 ~ N(0, 1).
- 4 cadenas con inicios sobredispersos; R̂ normalizado por rangos y ESS bulk/tail (Vehtari et al. 2021, arviz).
Escribe en lepsp_parametros.json las formas (conserva las demás claves) y el diagnóstico en lepsp_mcmc3.json."""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
import arviz as az
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_acotada import d, ModeloNL, beta_inicial, disenio_m2  # noqa: E402
from lepsp_modelo import Modelo  # noqa: E402

CL = ["good", "moderate", "low"]
dum = np.c_[[(d.clase == c).values.astype(float) for c in CL]].T


def logprior(p, s=0.25):
    lp = 0.0
    for i in (0, 1, 3, 4):
        v = np.exp(p[i]); lp += -0.5 * (v / s) ** 2 + p[i]
    for i in (2, 5):
        lp += np.log(1 - np.tanh(p[i]) ** 2 + 1e-300)
    return lp - 0.5 * (p[6] + 3.3) ** 2 - 0.5 * p[7] ** 2


def cadena(mod, p0, n, burn, rng, S, s):
    p = p0.copy(); lp = mod.reml(p) + logprior(p, s); k = len(p); out = []; acc = 0
    for i in range(n + burn):
        q = rng.multivariate_normal(p, S); lq = mod.reml(q) + logprior(q, s)
        if np.log(rng.random()) < lq - lp:
            p, lp = q, lq; acc += 1
        out.append(p.copy())
        if 300 <= i < burn and i % 150 == 0:
            S = np.cov(np.array(out[-300:]).T) * 2.38 ** 2 / k + np.eye(k) * 1e-7
    return np.array(out[burn:]), acc / (n + burn)


def mcmc(mod, n, burn, s=0.25, nc=4, seed=7):
    f = lambda p: mod.reml(p) + logprior(p, s); p0 = mod.psi; h = 1e-3; k = len(p0); Hm = np.zeros((k, k))
    for i in range(k):
        for j in range(i, k):
            ei = np.eye(k)[i] * h; ej = np.eye(k)[j] * h
            Hm[i, j] = Hm[j, i] = (f(p0 + ei + ej) - f(p0 + ei - ej) - f(p0 - ei + ej) + f(p0 - ei - ej)) / (4 * h * h)
    Cov = np.linalg.inv(-Hm); Cov = (Cov + Cov.T) / 2
    rng = np.random.default_rng(seed); cads = []
    for c in range(nc):
        start = rng.multivariate_normal(p0, 9 * Cov)
        ch, acc = cadena(mod, start, n, burn, np.random.default_rng(seed * 100 + c), Cov * 2.38 ** 2 / k, s); cads.append(ch)
    ch = np.array(cads)
    idata = az.convert_to_dataset({f"p{j}": ch[:, :, j] for j in range(k)})
    rh = np.array([float(az.rhat(idata, method="rank")[f"p{j}"]) for j in range(k)])
    eb = np.array([float(az.ess(idata, method="bulk")[f"p{j}"]) for j in range(k)])
    et = np.array([float(az.ess(idata, method="tail")[f"p{j}"]) for j in range(k)])
    return ch, dict(rhat=rh.tolist(), ess_bulk=eb.tolist(), ess_tail=et.tolist())


def hiper_nat(ch):
    """Medianas e IC 90 % en escala natural: sdθp, sdmp, ρp, sdθs, sdms, ρs, σε(0), a1."""
    t = ch.reshape(-1, ch.shape[-1]); H = np.c_[np.exp(t[:, 0]), np.exp(t[:, 1]), np.tanh(t[:, 2]), np.exp(t[:, 3]), np.exp(t[:, 4]), np.tanh(t[:, 5]), np.exp(t[:, 6]), t[:, 7]]
    return [[float(np.median(H[:, i])), float(np.percentile(H[:, i], 5)), float(np.percentile(H[:, i], 95))] for i in range(8)]


if __name__ == "__main__":
    t0 = time.time(); P = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8")); diag = {}
    N_IT, BURN = 6000, 2000
    # ------------------------------------------------ acotada: cresta de (φ′cs, ζ)
    m2 = Modelo(d, disenio_m2(d), CL + ["e", "x", "x2"]).ajustar()
    PH = np.arange(12.0, 32.01, 1.0); ZE = np.round(np.arange(0.15, 0.475, 0.025), 4)
    ML = np.full((len(PH), len(ZE)), -np.inf)
    for i, ph in enumerate(PH):
        for j, z in enumerate(ZE):
            ML[i, j], _ = ModeloNL(d, np.tan(np.radians(ph)), z, beta_inicial(d)).gn(m2.psi)
    w = np.exp(ML - ML.max()); w /= w.sum(); orden = np.argsort(w.ravel())[::-1]
    keep = orden[: int(np.searchsorted(np.cumsum(w.ravel()[orden]), 0.995)) + 1]
    print(f"cresta: {len(keep)} puntos con el 99.5 % del peso ({time.time()-t0:.0f} s)", flush=True)
    pts = []
    for q in keep:
        i, j = np.unravel_index(q, ML.shape)
        mg = ModeloNL(d, np.tan(np.radians(PH[i])), ZE[j], beta_inicial(d)).ajustar_nl(m2.psi)
        mlg, _ = mg.gn(mg.psi); pts.append(dict(phi_cs=float(PH[i]), zeta=float(ZE[j]), ml=float(mlg), mod=mg))
    mls = np.array([p["ml"] for p in pts]); wg = np.exp(mls - mls.max()); wg /= wg.sum()
    iopt = int(np.argmax(mls)); mopt = pts[iopt]["mod"]
    pm = float(np.sum(wg * [p["phi_cs"] for p in pts])); zm = float(np.sum(wg * [p["zeta"] for p in pts]))
    print(f"óptimo φcs = {pts[iopt]['phi_cs']}°, ζ = {pts[iopt]['zeta']}; media ponderada φcs = {pm:.1f}°, ζ = {zm:.3f} ({time.time()-t0:.0f} s)", flush=True)
    ch, dg = mcmc(mopt, N_IT, BURN); diag["acotada"] = dg
    print(f"acotada: R̂ máx {max(dg['rhat']):.3f}; ESS bulk mín {min(dg['ess_bulk']):.0f}; ESS tail mín {min(dg['ess_tail']):.0f} ({time.time()-t0:.0f} s)", flush=True)
    todas = ch.reshape(-1, 8); rng = np.random.default_rng(11); idx = rng.choice(len(todas), 800, replace=False)
    gsel = rng.choice(len(pts), 800, p=wg); mues = []
    for p, g in zip(todas[idx], gsel):
        pg = p - mopt.psi + pts[g]["mod"].psi; mg = pts[g]["mod"]
        mg.relinealizar(); _, _, Cb = mg.reml(pg, devolver=True)
        mues.append(dict(psi=pg.tolist(), beta=mg.beta_nl.tolist(), cov_beta=Cb.tolist(), phi_cs=pts[g]["phi_cs"], zeta=pts[g]["zeta"]))
    P["formas"]["acotada"] = dict(nombres=CL + ["e"], psi=mopt.psi.tolist(), beta=mopt.beta_nl.tolist(), cov_beta=mopt.cov_beta.tolist(),
                                  phi_cs=pts[iopt]["phi_cs"], zeta=pts[iopt]["zeta"], muestras=mues,
                                  cresta=[dict(phi_cs=p["phi_cs"], zeta=p["zeta"], ml=p["ml"], peso=float(x)) for p, x in zip(pts, wg)],
                                  ml=float(mls.max()), hiper=hiper_nat(ch))
    diag["acotada_cresta"] = dict(grilla_phi=PH.tolist(), grilla_zeta=ZE.tolist(), ml=ML.tolist(), phi_media=pm, zeta_media=zm)
    diag["ml"] = dict(acotada=float(mls.max()), x2=float(m2.ll - 0.5 * np.linalg.slogdet(m2.cov_beta)[1]))
    # sensibilidad a la previa (acotada, cadenas más cortas)
    for s in (0.1, 0.5):
        chs, dgs = mcmc(mopt, 3000, 1500, s=s, seed=21); diag[f"acotada_previa_{s}"] = dict(hiper=hiper_nat(chs), rhat_max=max(dgs["rhat"]))
        print(f"previa half-normal({s}): sdθ_pub {hiper_nat(chs)[0][0]:.4f}, sdm_pub {hiper_nat(chs)[1][0]:.4f} ({time.time()-t0:.0f} s)", flush=True)
    diag["acotada_previa_0.25"] = dict(hiper=hiper_nat(ch))
    # ------------------------------------------------ x2 y potencia (cadenas más largas; potencia el doble)
    for forma, X, NOM, nit in (("x2", disenio_m2(d), CL + ["e", "x", "x2"], N_IT), ("potencia", np.c_[dum, d.e.values, d.x.values], CL + ["e", "x"], 2 * N_IT)):
        m = Modelo(d, X, NOM).ajustar(); ch, dg = mcmc(m, nit, BURN); diag[forma] = dg
        print(f"{forma}: R̂ máx {max(dg['rhat']):.3f}; ESS bulk mín {min(dg['ess_bulk']):.0f}; ESS tail mín {min(dg['ess_tail']):.0f} ({time.time()-t0:.0f} s)", flush=True)
        todas = ch.reshape(-1, 8); idx = np.linspace(0, len(todas) - 1, 800).astype(int); mues = []
        for p in todas[idx]:
            _, b, Cb = m.reml(p, devolver=True); mues.append(dict(psi=p.tolist(), beta=b.tolist(), cov_beta=Cb.tolist()))
        P["formas"][forma] = dict(nombres=NOM, psi=m.psi.tolist(), beta=m.beta.tolist(), cov_beta=m.cov_beta.tolist(), muestras=mues, hiper=hiper_nat(ch))
    json.dump(P, open(AQ / "lepsp_parametros.json", "w", encoding="utf-8"), indent=0)
    json.dump(diag, open(AQ / "lepsp_mcmc3.json", "w", encoding="utf-8"), indent=1)
    print(f"escrito lepsp_parametros.json y lepsp_mcmc3.json ({time.time()-t0:.0f} s)")
