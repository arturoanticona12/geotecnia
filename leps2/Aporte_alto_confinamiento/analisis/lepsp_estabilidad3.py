"""Leps-P, estabilidad drenada (ronda 3): botaderos de 150, 400 y 700 m (2H:1V, fundación horizontal competente y
drenada), Bishop con envolvente no lineal tabulada (slope.py). Cambios respecto de la ronda 2:
- envolventes del sitio con la forma acotada (a8_lepsp_sitio.py); sensibilidad con la forma x2;
- peso unitario coherente con e = 0.65: γ = Gs·γw·(1 + w)/(1 + e) ≈ 17 kN/m³ (Gs 2.75, w 5 %); sensibilidad 21 kN/m³;
- Monte Carlo: familia de círculos alrededor de los críticos y, si FS < 1.3, búsqueda completa de la superficie crítica
  para esa realización (la familia fija da una cota superior del FS);
- Pf con IC exacto de Clopper–Pearson; se reporta como Pf condicional, solo de resistencia.
Escribe lepsp_estabilidad3.json."""
import sys, json, warnings, time
from pathlib import Path
import numpy as np
from scipy.stats import beta as betad
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; R = AQ.parent; sys.path.insert(0, str(AQ))
import slope  # noqa: E402

BETA = 26.57; NMC = 600; GS, W = 2.75, 0.05
GAM_E = lambda e: GS * 9.81 * (1 + W) / (1 + e) / 1000       # MN/m³


def env_tau(sn, tau):
    lt = np.log(tau)
    t = lambda s: np.exp(np.interp(np.log(np.maximum(s, 1e-6)), np.log(sn), lt)) * np.where(s < sn[0], np.maximum(s, 1e-6) / sn[0], 1)
    dt = lambda s: (t(np.maximum(s, 1e-6) * 1.001) - t(np.maximum(s, 1e-6) * 0.999)) / (0.002 * np.maximum(s, 1e-6))
    return t, dt


def escenarios(npz):
    Z = np.load(npz); tau = Z["tau"]; w = Z["pesos"]; sn = Z["sn"]; nom = list(Z["nombres"])
    phi = lambda t: np.degrees(np.arctan(t / sn)); i3 = int(np.argmin(np.abs(sn - 3)))
    med = [np.median(phi(t)[:, i3]) for t in tau]
    i_d = int(np.argmin(med)); i_dt = int(np.argmin([m if n in "ABC" else 99 for m, n in zip(med, nom)]))
    return sn, {"model": np.tensordot(w, tau, 1), "comonotonic": np.tensordot(w, np.sort(tau, axis=1), 1),
                f"weakest tested ({nom[i_dt]})": tau[i_dt], f"weakest ({nom[i_d]})": tau[i_d]}


def cp(k, n):
    lo = 0.0 if k == 0 else float(betad.ppf(0.025, k, n - k + 1)); hi = float(betad.ppf(0.975, k + 1, n - k)) if k < n else 1.0
    return [lo, hi]


def correr(etq, archivo, gam, Hs=(150.0, 400.0, 700.0), mc=True, mc_solo=None):
    slope.GAM = gam; out = {}
    sn, ESC = escenarios(R / "analisis_antamina" / archivo)
    for H in Hs:
        Lh = H / np.tan(np.radians(BETA))
        for nm, T in ESC.items():
            res = {}
            for q in (50, 5):
                tq = np.percentile(T, q, axis=0); r = slope.search(H, BETA, env_tau(sn, tq))
                res[f"P{q:02d}"] = dict(F=float(r["F"]), snmax=float(r["sn"].max()), circ=[float(r["xc"]), float(r["yc"]), float(r["R"])])
            clave = f"{etq}|{H:.0f}|{nm}"; out[clave] = dict(det=res)
            if not (mc and H == 700.0) or (mc_solo is not None and nm not in mc_solo):
                print(f"{clave:55s} FS P50 {res['P50']['F']:.3f} | P05 {res['P05']['F']:.3f}", flush=True); continue
            fam = [(xc + dx * Lh, yc + dy * Lh, Rr + dR * Lh) for c in ("P50", "P05") for xc, yc, Rr in [res[c]["circ"]]
                   for dx in (-0.06, 0, 0.06) for dy in (-0.06, 0, 0.06) for dR in (-0.03, 0, 0.03)]
            idx = np.random.default_rng(int(H)).choice(T.shape[0], NMC, replace=False); Fs = []; nbus = 0
            for j in idx:
                e = env_tau(sn, T[j]); fm = np.inf
                for xc, yc, Rr in fam:
                    r = slope.bishop(xc, yc, Rr, H, BETA, e)
                    if r is not None and (r["x1"] - r["x0"]) >= 0.3 * Lh:
                        fm = min(fm, r["F"])
                if fm < 1.3:
                    fm = min(fm, float(slope.search(H, BETA, e)["F"])); nbus += 1
                Fs.append(fm)
            Fs = np.array(Fs); nf = int((Fs < 1).sum())
            out[clave]["mc"] = dict(n=NMC, FS_P50=float(np.median(Fs)), FS_P05=float(np.percentile(Fs, 5)), FS_min=float(Fs.min()),
                                    fallas=nf, pf=nf / NMC, pf_ic95=cp(nf, NMC), busquedas_completas=nbus)
            print(f"{clave:55s} FS P50 {res['P50']['F']:.3f} | P05 {res['P05']['F']:.3f} | MC P50 {np.median(Fs):.3f} P05 {np.percentile(Fs, 5):.3f} "
                  f"fallas {nf}/{NMC} IC {np.round(cp(nf, NMC), 4)} (búsquedas {nbus})", flush=True)
    return out


if __name__ == "__main__":
    # dos partes en paralelo ('1': e = 0.65 completo; '2': densidad de laboratorio, γ 21 y forma x2, MC solo del modelo);
    # 'unir' combina lepsp_estabilidad3_p1/p2.json en lepsp_estabilidad3.json
    parte = sys.argv[1] if len(sys.argv) > 1 else "todo"; t0 = time.time()
    if parte == "unir":
        OUT = dict(gam_base=GAM_E(0.65) * 1000, gam_sens=21.0)
        for p in ("1", "2"):
            OUT.update(json.load(open(AQ / f"lepsp_estabilidad3_p{p}.json", encoding="utf-8")))
        json.dump(OUT, open(AQ / "lepsp_estabilidad3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("escrito lepsp_estabilidad3.json"); sys.exit()
    OUT = {}
    if parte in ("1", "todo"):
        OUT.update(correr("acotada e=0.65 γ17", "lepsp_sitio3_muestras_e065.npz", GAM_E(0.65)))
    if parte in ("2", "todo"):
        OUT.update(correr("acotada e=lab γ21", "lepsp_sitio3_muestras_lab.npz", 21e-3, mc_solo={"model"}))
        OUT.update(correr("acotada e=0.65 γ21", "lepsp_sitio3_muestras_e065.npz", 21e-3, Hs=(700.0,), mc=False))
        OUT.update(correr("x2 e=0.65 γ17", "lepsp_sitio3_muestras_e065_x2.npz", GAM_E(0.65), Hs=(700.0,), mc_solo={"model"}))
    json.dump(OUT, open(AQ / f"lepsp_estabilidad3_p{parte}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"escrito lepsp_estabilidad3_p{parte}.json ({time.time()-t0:.0f} s)")
