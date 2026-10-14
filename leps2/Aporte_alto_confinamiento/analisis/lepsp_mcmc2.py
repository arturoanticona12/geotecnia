"""Leps-P, MCMC de hiperparámetros (ronda 2): previas propias, 4 cadenas con inicios sobredispersos, split-R̂ y ESS.
Previas (en la escala natural): DE ~ Half-Normal(0.25); ρ ~ U(−1, 1); a0 ~ N(−3.3, 1); a1 ~ N(0, 1).
Reescribe lepsp_parametros.json (formas x2 y potencia) y deja el diagnóstico en lepsp_mcmc2.json."""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo, S0  # noqa: E402

d = preparar(load_db(), CLASE); CL = ["good", "moderate", "low"]
dum = np.c_[[(d.clase == c).values.astype(float) for c in CL]].T


def logprior(p):
    lp = 0.0
    for i in (0, 1, 3, 4):                         # ln σ: Half-Normal(0.25) + Jacobiano
        s = np.exp(p[i]); lp += -0.5 * (s / 0.25) ** 2 + p[i]
    for i in (2, 5):                               # atanh ρ: U(−1,1) + Jacobiano
        lp += np.log(1 - np.tanh(p[i]) ** 2 + 1e-300)
    lp += -0.5 * ((p[6] + 3.3) / 1.0) ** 2 - 0.5 * p[7] ** 2
    return lp


def cadena(mod, p0, n, burn, rng, S0_):
    p = p0.copy(); lp = mod.reml(p) + logprior(p); k = len(p); S = S0_.copy(); out = []; acc = 0
    for i in range(n + burn):
        q = rng.multivariate_normal(p, S); lq = mod.reml(q) + logprior(q)
        if np.log(rng.random()) < lq - lp:
            p, lp = q, lq; acc += 1
        out.append(p.copy())
        if 300 <= i < burn and i % 150 == 0:
            S = np.cov(np.array(out[-300:]).T) * 2.38 ** 2 / k + np.eye(k) * 1e-7
    return np.array(out[burn:]), acc / (n + burn)


def split_rhat_ess(ch):
    """ch: (cadenas, n, k). Split-R̂ (Gelman et al. 2013) y ESS por autocorrelación (Geyer)."""
    c, n, k = ch.shape; h = n // 2; sp = np.concatenate([ch[:, :h], ch[:, h:2 * h]], 0)
    W = sp.var(1, ddof=1).mean(0); B = h * sp.mean(1).var(0, ddof=1); rh = np.sqrt(((h - 1) / h * W + B / h) / W)
    ess = []
    for j in range(k):
        x = ch[:, :, j]; xm = x - x.mean(1, keepdims=True); acf = np.zeros(n)
        for t in range(n):
            acf[t] = np.mean([np.dot(xm[i, :n - t], xm[i, t:]) / ((n - t) * xm[i].var() + 1e-300) for i in range(c)])
            if t > 1 and acf[t] + acf[t - 1] < 0:
                break
        ess.append(c * n / (1 + 2 * acf[1:t].sum()))
    return rh, np.array(ess)


FORMAS = {"x2": (np.c_[dum, d.e.values, d.x.values, d.x.values ** 2], CL + ["e", "x", "x2"]),
          "potencia": (np.c_[dum, d.e.values, d.x.values], CL + ["e", "x"])}
ESC = json.load(open(AQUI / "lepsp_escala.json"))
out = dict(clases=CL, S0=S0, n=dict(ensayos=len(d), sets=int(d.Set.nunique()), pub=int(d.pub.nunique()), sn_max=float(d.sn.max())), formas={})
diag = {}
for forma, (X, NOM) in FORMAS.items():
    t = time.time(); m = Modelo(d, X, NOM).ajustar()
    # matriz de pasos inicial: inversa del hessiano numérico del log-posterior en el modo
    f = lambda p: m.reml(p) + logprior(p); p0 = m.psi; h = 1e-3; k = len(p0); Hm = np.zeros((k, k))
    for i in range(k):
        for j in range(i, k):
            ei = np.eye(k)[i] * h; ej = np.eye(k)[j] * h
            Hm[i, j] = Hm[j, i] = (f(p0 + ei + ej) - f(p0 + ei - ej) - f(p0 - ei + ej) + f(p0 - ei - ej)) / (4 * h * h)
    Cov = np.linalg.inv(-Hm); Cov = (Cov + Cov.T) / 2
    rng = np.random.default_rng(7); cads = []
    for c in range(4):
        start = rng.multivariate_normal(p0, 9 * Cov)            # ±3 DE: inicios sobredispersos
        ch, acc = cadena(m, start, 5000, 2000, np.random.default_rng(100 + c), Cov * 2.38 ** 2 / k); cads.append(ch)
        print(f"  {forma} cadena {c}: aceptación {acc:.2f} ({time.time()-t:.0f} s)", flush=True)
    ch = np.array(cads); rh, ess = split_rhat_ess(ch)
    print(f"{forma}: split-R̂ máx {rh.max():.3f}; ESS mín {ess.min():.0f} (por parámetro: {np.round(ess).astype(int).tolist()})")
    diag[forma] = dict(rhat=rh.tolist(), ess=ess.tolist())
    todas = ch.reshape(-1, k); idx = np.linspace(0, len(todas) - 1, 800).astype(int); mues = []
    for p in todas[idx]:
        _, b, Cb = m.reml(p, devolver=True); mues.append(dict(psi=p.tolist(), beta=b.tolist(), cov_beta=Cb.tolist()))
    out["formas"][forma] = dict(nombres=NOM, psi=m.psi.tolist(), beta=m.beta.tolist(), cov_beta=m.cov_beta.tolist(), muestras=mues)
out["escala"] = dict(bD=ESC["similares"]["b"], se=ESC["similares"]["se"], tau=ESC["similares"]["tau"], kappa=ESC["similares"]["kappa"], grupos=ESC["similares"]["n"])
json.dump(out, open(AQUI / "lepsp_parametros.json", "w"), indent=0); json.dump(diag, open(AQUI / "lepsp_mcmc2.json", "w"), indent=1)
print("escrito lepsp_parametros.json y lepsp_mcmc2.json")
