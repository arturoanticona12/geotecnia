"""Leps-P, estabilidad: botaderos de 150, 400 y 700 m (talud global 2H:1V, fundación horizontal competente, seco),
método de Bishop con envolvente no lineal. (1) FS con envolventes por percentil; (2) probabilidad de falla por Monte
Carlo sobre las muestras de la envolvente del botadero (familia de superficies alrededor de las críticas).
Escribe lepsp_estabilidad.json y lepsp_funciones_slide2.json."""
import sys, json, warnings, time
from pathlib import Path
import numpy as np
from scipy.stats import norm
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; RAIZ = AQUI.parent
sys.path.insert(0, str(AQUI)); sys.path.insert(0, str(RAIZ / "leps3"))
import lepsp as L  # noqa: E402
from slope import search, bishop  # noqa: E402

BETA = 26.57
SNG = np.logspace(-3, np.log10(25), 80); XG = np.log(SNG / L.S0)


def env_phi(phis):
    """Envolvente (τ, dτ/dσ) desde φ′s en la grilla SNG (interpolación en log σ′n)."""
    lt = np.log(SNG * np.tan(np.radians(phis)))
    t = lambda s: np.exp(np.interp(np.log(np.maximum(s, 1e-6)), np.log(SNG), lt)) * np.where(s < SNG[0], np.maximum(s, 1e-6) / SNG[0], 1)
    dt = lambda s: (t(np.maximum(s, 1e-6) * 1.001) - t(np.maximum(s, 1e-6) * 0.999)) / (0.002 * np.maximum(s, 1e-6))
    return t, dt


def env_muestra(TH, M, C2, w):
    """Envolvente media del botadero de una realización: τ = Σ w_k σ0 exp(θ_k + m_k x + c2 x²)."""
    def t(s):
        s = np.maximum(s, 1e-6); x = np.log(s / L.S0)
        return np.sum([wk * L.S0 * np.exp(th + m * x + c2 * x * x) for wk, th, m, c2 in zip(w, TH, M, C2)], axis=0)
    dt = lambda s: (t(np.maximum(s, 1e-6) * 1.001) - t(np.maximum(s, 1e-6) * 0.999)) / (0.002 * np.maximum(s, 1e-6))
    return t, dt


# ---- muestras del sitio (alineadas por fila; ya incluyen escala a campo)
Z = np.load(RAIZ / "analisis_antamina" / "lepsp_sitio_muestras.npz"); w = Z["pesos"]; nl = len(w)
TH = np.array([Z[f"lit{i}_th"] for i in range(nl)]); MM = np.array([Z[f"lit{i}_m"] for i in range(nl)]); C2 = np.array([Z[f"lit{i}_c2"] for i in range(nl)])
tau_g = np.tensordot(w, L.S0 * np.exp(TH[:, :, None] + MM[:, :, None] * XG + C2[:, :, None] * XG ** 2), 1)       # (n, grilla)
phi_g = np.degrees(np.arctan(tau_g / SNG))
S = json.load(open(RAIZ / "analisis_antamina" / "lepsp_sitio.json", encoding="utf-8"))
debil = list(S["litologias"])[int(np.argmin([S["litologias"][k]["campo_P50"][-1] for k in S["litologias"]]))]
i_d = list(S["litologias"]).index(debil)
phi_d = np.degrees(np.arctan(L.S0 * np.exp(TH[i_d][:, None] + MM[i_d][:, None] * XG + C2[i_d][:, None] * XG ** 2) / SNG))
gen = L.escala(L.previa("moderada", 0.45, n=40000), 150, 1000)
phi_gen = L.muestras_phi(SNG, gen, puntual=False)
ENV = {"Desmonte del sitio, P50": np.percentile(phi_g, 50, 0),
       "Desmonte del sitio, P05 (característico)": np.percentile(phi_g, 5, 0),
       "Desmonte del sitio, segregación (litología más débil), P05": np.percentile(phi_d, 5, 0),
       "Material genérico moderado e = 0.45, P50": np.percentile(phi_gen, 50, 0),
       "Material genérico moderado e = 0.45, P05 (característico)": np.percentile(phi_gen, 5, 0)}
json.dump({k: [[0.0, 0.0]] + [[round(float(s) * 1000, 3), round(float(s * np.tan(np.radians(p))) * 1000, 3)] for s, p in zip(SNG[::3], v[::3])]
           for k, v in ENV.items()}, open(AQUI / "lepsp_funciones_slide2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
out = dict(det={}, pf={})
for H in (150.0, 400.0, 700.0):
    crit = {}
    for nm, ph in ENV.items():
        t0 = time.time(); r = search(H, BETA, env_phi(ph))
        sn, l = r["sn"], r["l"]
        out["det"][f"{H:.0f}|{nm}"] = dict(F=float(r["F"]), snmax=float(sn.max()), snmed=float(np.average(sn, weights=l)),
                                           f79=float(l[sn > 7.9].sum() / l.sum()), circ=[float(r["xc"]), float(r["yc"]), float(r["R"])])
        crit[nm] = (r["xc"], r["yc"], r["R"])
        print(f"H = {H:4.0f} m | {nm:58s} FS = {r['F']:.3f}  σ′n,máx = {sn.max():5.2f} MPa  σ′n,medio = {np.average(sn, weights=l):4.2f}  L(σ′n>7.9) = {l[sn > 7.9].sum() / l.sum():4.0%}  ({time.time()-t0:.0f} s)")
    # ---- Monte Carlo: familia de 45 círculos alrededor de los críticos del sitio
    Lh = H / np.tan(np.radians(BETA)); fam = []
    for nm in ("Desmonte del sitio, P50", "Desmonte del sitio, P05 (característico)"):
        xc, yc, R = crit[nm]
        for dx in (-0.06, 0, 0.06):
            for dy in (-0.06, 0, 0.06):
                for dR in (-0.03, 0, 0.03):
                    if dx == dy == 0 or dR == 0:
                        fam.append((xc + dx * Lh, yc + dy * Lh, R + dR * Lh))
    rng = np.random.default_rng(int(H)); idx = rng.choice(TH.shape[1], 400, replace=False); Fs = []
    t0 = time.time()
    for j in idx:
        e = env_muestra(TH[:, j], MM[:, j], C2[:, j], w); fmin = np.inf
        for xc, yc, R in fam:
            r = bishop(xc, yc, R, H, BETA, e)
            if r is not None and (r["x1"] - r["x0"]) >= 0.3 * Lh:
                fmin = min(fmin, r["F"])
        Fs.append(fmin)
    Fs = np.array(Fs); lnF = np.log(Fs)
    bl = lnF.mean() / lnF.std(); pf_ln = norm.cdf(-bl)
    out["pf"][f"{H:.0f}"] = dict(n=len(Fs), FS_P50=float(np.median(Fs)), FS_P10=float(np.percentile(Fs, 10)), FS_P05=float(np.percentile(Fs, 5)),
                                 FS_min=float(Fs.min()), beta_ln=float(bl), pf_ln=float(pf_ln), pf_emp=float(np.mean(Fs < 1)),
                                 cov=float(Fs.std() / Fs.mean()))
    print(f"   Monte Carlo ({len(Fs)} realizaciones, {time.time()-t0:.0f} s): FS P50 {np.median(Fs):.3f}, P10 {np.percentile(Fs, 10):.3f}, P05 {np.percentile(Fs, 5):.3f},"
          f" mín {Fs.min():.3f}; COV {Fs.std() / Fs.mean():.3f}; β (lognormal) {bl:.2f}; Pf ≈ {pf_ln:.1e}")
json.dump(out, open(AQUI / "lepsp_estabilidad.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("escrito lepsp_estabilidad.json y lepsp_funciones_slide2.json")
