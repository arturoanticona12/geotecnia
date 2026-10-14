"""Leps-P, estabilidad drenada (ronda 4): botaderos de 150, 400 y 700 m (2H:1V, fundación horizontal competente y drenada),
Bishop con envolvente no lineal tabulada (slope.py), envolventes de a8_lepsp_sitio.py (forma acotada con efectos en η y ζ).
- γ coherente con e (Gs 2.75, w 5 %): 17.2 kN/m³ para e = 0.65, 15.7 para el tipo de roca E (e = 0.80), 21 en laboratorio.
- Monte Carlo (600) con familia de círculos y búsqueda completa si FS < 1.3; Pf condicional (solo resistencia) con IC de
  Clopper–Pearson e índice de confiabilidad lognormal β = ln(FS50)/σ_lnFS, σ_lnFS = (ln FS50 − ln FS05)/1.645.
- Casos para separar efectos: densidad y escala; solo densidad; solo escala; ninguno; escala con media estimada.
Partes en paralelo: '1' (e = 0.65 con escala, cuatro correlaciones) · '2' (demás casos, MC solo del modelo) · 'unir'."""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; R = AQ.parent; sys.path.insert(0, str(AQ))
import slope  # noqa: E402
from lepsp_estabilidad3 import env_tau, escenarios, cp, GAM_E  # noqa: E402

BETA = 26.57; NMC = 600


def correr(etq, archivo, gam, Hs=(150.0, 400.0, 700.0), mc=True, mc_solo=None, gam_E=None):
    out = {}; sn, ESC = escenarios(R / "analisis_antamina" / archivo)
    for H in Hs:
        Lh = H / np.tan(np.radians(BETA))
        for nm, T in ESC.items():
            slope.GAM = gam_E if (gam_E is not None and nm.startswith("weakest (E")) else gam
            res = {}
            for q in (50, 5):
                tq = np.percentile(T, q, axis=0); r = slope.search(H, BETA, env_tau(sn, tq))
                res[f"P{q:02d}"] = dict(F=float(r["F"]), snmax=float(r["sn"].max()), circ=[float(r["xc"]), float(r["yc"]), float(r["R"])])
            clave = f"{etq}|{H:.0f}|{nm}"; out[clave] = dict(det=res, gam=slope.GAM * 1000)
            if not (mc and H == 700.0) or (mc_solo is not None and nm not in mc_solo):
                print(f"{clave:58s} FS P50 {res['P50']['F']:.3f} | P05 {res['P05']['F']:.3f}", flush=True); continue
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
            Fs = np.array(Fs); nf = int((Fs < 1).sum()); p50, p05 = np.median(Fs), np.percentile(Fs, 5)
            sl = (np.log(p50) - np.log(p05)) / 1.645
            out[clave]["mc"] = dict(n=NMC, FS_P50=float(p50), FS_P05=float(p05), FS_min=float(Fs.min()), fallas=nf, pf=nf / NMC,
                                    pf_ic95=cp(nf, NMC), busquedas_completas=nbus, beta_ln=float(np.log(p50) / sl) if sl > 0 else None)
            print(f"{clave:58s} FS P50 {res['P50']['F']:.3f} | P05 {res['P05']['F']:.3f} | MC P50 {p50:.3f} P05 {p05:.3f} fallas {nf}/{NMC} "
                  f"IC {np.round(cp(nf, NMC), 4)} β_LN {np.log(p50) / sl:.2f} (búsquedas {nbus})", flush=True)
    return out


if __name__ == "__main__":
    parte = sys.argv[1] if len(sys.argv) > 1 else "1"; t0 = time.time()
    if parte == "unir":
        OUT = dict(gam_base=GAM_E(0.65) * 1000, gam_E=GAM_E(0.80) * 1000, gam_lab=21.0)
        for p in ("1", "2"):
            OUT.update(json.load(open(AQ / f"lepsp_estabilidad4_p{p}.json", encoding="utf-8")))
        json.dump(OUT, open(AQ / "lepsp_estabilidad4.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1); print("escrito lepsp_estabilidad4.json"); sys.exit()
    OUT = {}
    if parte == "1":
        OUT.update(correr("e=0.65 escala", "lepsp_sitio3_muestras_e065_general.npz", GAM_E(0.65), gam_E=GAM_E(0.80)))
    if parte == "2":
        OUT.update(correr("lab sin escala", "lepsp_sitio3_muestras_lab_ninguno.npz", 21e-3, Hs=(700.0,), mc_solo={"model"}))
        OUT.update(correr("e=0.65 sin escala", "lepsp_sitio3_muestras_e065_ninguno.npz", GAM_E(0.65), Hs=(700.0,), mc_solo={"model"}))
        OUT.update(correr("lab escala", "lepsp_sitio3_muestras_lab_general.npz", 21e-3, Hs=(700.0,), mc_solo={"model"}))
        OUT.update(correr("e=0.65 escala datos", "lepsp_sitio3_muestras_e065_datos.npz", GAM_E(0.65), Hs=(700.0,), mc_solo={"model"}))
        OUT.update(correr("e=0.65 escala γ21", "lepsp_sitio3_muestras_e065_general.npz", 21e-3, Hs=(700.0,), mc=False))
        OUT.update(correr("x2 e=0.65 escala", "lepsp_sitio3_muestras_e065_general_x2.npz", GAM_E(0.65), Hs=(700.0,), mc_solo={"model"}))
    json.dump(OUT, open(AQ / f"lepsp_estabilidad4_p{parte}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"escrito lepsp_estabilidad4_p{parte}.json ({time.time()-t0:.0f} s)")
