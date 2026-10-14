"""Leps-P, estabilidad drenada (ronda 2): botaderos de 150, 400 y 700 m (2H:1V, fundación horizontal competente, seco),
Bishop con envolvente no lineal tabulada. Envolventes del desmonte del sitio a escala de campo (escala 'general') y con
densidad de campo e = 0.65 (escenario base) y de laboratorio; supuestos de correlación entre litologías: modelo,
comonotónico y litología más débil. Monte Carlo por supuesto con familia de círculos alrededor de los críticos;
Pf reportada como frecuencia observada y cota superior del 95 % (regla de tres: 3/n si no hay fallas).
Escribe lepsp_estabilidad2.json y lepsp_funciones_slide2.json."""
import sys, json, warnings, time
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent; sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(RAIZ / "leps3"))
import lepsp as L  # noqa: E402
from slope import search, bishop  # noqa: E402

BETA = 26.57; NMC = 600


def env_tau(sn, tau):
    lt = np.log(tau)
    t = lambda s: np.exp(np.interp(np.log(np.maximum(s, 1e-6)), np.log(sn), lt)) * np.where(s < sn[0], np.maximum(s, 1e-6) / sn[0], 1)
    dt = lambda s: (t(np.maximum(s, 1e-6) * 1.001) - t(np.maximum(s, 1e-6) * 0.999)) / (0.002 * np.maximum(s, 1e-6))
    return t, dt


def escenarios(npz):
    Z = np.load(npz); tau = Z["tau"]; w = Z["pesos"]; sn = Z["sn"]; nom = list(Z["nombres"])
    phi = lambda t: np.degrees(np.arctan(t / sn))
    medianas = [np.median(phi(t)[:, -1]) for t in tau]
    i_d = int(np.argmin(medianas)); i_dt = int(np.argmin([m if "untested" not in n else 99 for m, n in zip(medianas, nom)]))
    return sn, {"model": np.tensordot(w, tau, 1), "comonotonic": np.tensordot(w, np.sort(tau, axis=1), 1),
                f"weakest tested ({nom[i_dt]})": tau[i_dt], f"weakest ({nom[i_d]})": tau[i_d]}


out = dict(det={}, mc={})
fun = {}
for etq, archivo in (("e=0.65", "lepsp_sitio2_muestras_e065.npz"), ("e=lab", "lepsp_sitio2_muestras_lab.npz")):
    sn, ESC = escenarios(RAIZ / "analisis_antamina" / archivo)
    for H in (150.0, 400.0, 700.0):
        Lh = H / np.tan(np.radians(BETA))
        for nm, T in ESC.items():
            res = {}
            for q in (50, 5):
                tq = np.percentile(T, q, axis=0); r = search(H, BETA, env_tau(sn, tq))
                res[f"P{q:02d}"] = dict(F=float(r["F"]), snmax=float(r["sn"].max()), circ=[float(r["xc"]), float(r["yc"]), float(r["R"])])
                if H == 700 and nm == "model":
                    fun[f"{etq} P{q:02d}"] = [[0.0, 0.0]] + [[round(float(s) * 1000, 3), round(float(t) * 1000, 3)] for s, t in zip(sn[::2], tq[::2])]
            out["det"][f"{etq}|{H:.0f}|{nm}"] = res
            print(f"{etq} H={H:4.0f} {nm:42s} FS P50 env {res['P50']['F']:.3f} | P05 env {res['P05']['F']:.3f} | σ′n máx {res['P50']['snmax']:.2f}", flush=True)
            if H != 700.0:
                continue
            # Monte Carlo (familia de 54 círculos alrededor de los críticos P50 y P05), solo para 700 m
            fam = []
            for c in ("P50", "P05"):
                xc, yc, R = res[c]["circ"]
                for dx in (-0.06, 0, 0.06):
                    for dy in (-0.06, 0, 0.06):
                        for dR in (-0.03, 0, 0.03):
                            fam.append((xc + dx * Lh, yc + dy * Lh, R + dR * Lh))
            rng = np.random.default_rng(int(H)); idx = rng.choice(T.shape[0], NMC, replace=False); Fs = []
            for j in idx:
                e = env_tau(sn, T[j]); fm = np.inf
                for xc, yc, R in fam:
                    r = bishop(xc, yc, R, H, BETA, e)
                    if r is not None and (r["x1"] - r["x0"]) >= 0.3 * Lh:
                        fm = min(fm, r["F"])
                Fs.append(fm)
            Fs = np.array(Fs); nf = int((Fs < 1).sum())
            out["mc"][f"{etq}|{H:.0f}|{nm}"] = dict(n=NMC, FS_P50=float(np.median(Fs)), FS_P10=float(np.percentile(Fs, 10)), FS_P05=float(np.percentile(Fs, 5)),
                                                     FS_min=float(Fs.min()), cov=float(Fs.std() / Fs.mean()), fallas=nf,
                                                     pf_sup95=float(3 / NMC) if nf == 0 else float(np.mean(Fs < 1)))
            print(f"{etq} H={H:4.0f} {nm:42s} FS P50 env {res['P50']['F']:.3f} | P05 env {res['P05']['F']:.3f} | MC: P50 {np.median(Fs):.3f} P05 {np.percentile(Fs, 5):.3f} mín {Fs.min():.3f} fallas {nf}/{NMC}", flush=True)
json.dump(out, open(AQUI / "lepsp_estabilidad2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
json.dump(fun, open(AQUI / "lepsp_funciones_slide2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("escrito lepsp_estabilidad2.json y lepsp_funciones_slide2.json")
