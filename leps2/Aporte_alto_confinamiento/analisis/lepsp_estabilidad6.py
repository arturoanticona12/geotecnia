"""Ronda 6: lee los resultados de Slide2 (Morgenstern–Price) y arma lepsp_estabilidad6.json.
- det: lote determinístico (det6; claves en slide2/det6/claves.json), con el control circular («conv»).
- alto: mecanismos de alto confinamiento (alto6; claves en slide2/alto6/claves.json) con la σ′n movilizada en la base de las
  dovelas (γ·h·cos²α; aproximación) de cada superficie crítica.
- mc: Monte Carlo (mc6), Pf con IC de Clopper–Pearson (bilateral y cota unilateral al 95 %), índice lognormal.
- sustituto (revisores R1, R2, R9): ln FS = a + b·ln tan φ′s(σ′rep) ajustado a las 600 realizaciones del caso «modelo»
  (σ′rep elegido por máxima correlación); Pf con todas las muestras de la envolvente; Pf integrada sobre la incertidumbre de
  τ_D (lognormal ajustada al IC Q-profile) y con colas t (ν = 4) en el desplazamiento de escala.
Uso: python lepsp_estabilidad6.py <lote_det> <lote_alto> <lote_mc>"""
import sys, json, re
from pathlib import Path
import numpy as np
from scipy.stats import beta as betad, norm, t as tdist
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; RES = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados"); SL = AQ.parent / "slide2"; AA = AQ.parent / "analisis_antamina"
MET = "gle/morgenstern-price"
sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "slide2" / "scripts"))
import resultados as R  # noqa: E402


def leer(lote):
    out = {}
    for mod, v in json.load(open(RES / lote / "fs_por_escenario.json", encoding="utf-8")).items():
        if "fs" not in v:
            print(f"  AVISO: {lote} / {mod} sin resultados ({v.get('estado')})")
        for k, fs in v.get("fs", {}).items():
            out[(mod, k.split("/")[-1].strip())] = fs.get(MET, float("nan"))
    return out


def cp(k, n):
    return [0.0 if k == 0 else float(betad.ppf(0.025, k, n - k + 1)), float(betad.ppf(0.975, k + 1, n - k)) if k < n else 1.0]


def sn_mov(lote, clave, con_H=False, alto=False):
    """σ′n movilizada (media ponderada por longitud de base, P90, máx.) de cada escenario: γ·h·cos²α en la base de la dovela."""
    out = {}
    for caso in sorted((RES / lote).iterdir()):
        if not caso.is_dir() or caso.name.endswith("_conv"):
            continue
        slmd = next(caso.rglob("*.slmd"), None)
        if slmd is None:
            continue
        nombres = R.escenarios(slmd)
        for s01 in caso.rglob("*.s01"):
            nm = nombres.get(s01.stem)
            if nm is None:
                continue
            nm = nm.split("/")[-1].strip()
            if nm not in clave:
                continue
            L = Path(s01).read_text(encoding="latin-1").splitlines()
            try:
                i = next(k for k, l in enumerate(L) if l.startswith("* minimum slice info") and l.endswith(f"method={MET}"))
            except StopIteration:
                continue
            D = []
            for l in L[i + 1:]:
                if l.startswith("*"):
                    break
                t = l.split()
                if len(t) >= 5:
                    D.append([float(v) for v in t[:5]])
            D = np.array(D)
            if len(D) < 3:
                continue
            gam = 15.74 if "weakest E" in clave[nm] else (21.0 if clave[nm].startswith("lab") else 17.17)
            xb, yt, yb = D[:, 0], D[:, 2], D[:, 3]; dx = np.diff(xb); dyb = np.diff(yb); hm = 0.5 * ((yt - yb)[1:] + (yt - yb)[:-1])
            al = np.arctan2(dyb, dx); lb = np.hypot(dx, dyb); sn = gam * hm * np.cos(al) ** 2 / 1000.0
            if clave[nm].startswith("agua100"):         # Hu = 1 bajo el freático basal (generar_yaml_lepsp6.py: 0 en el pie, 100 m a x = 200 m)
                xm, ym = 0.5 * (xb[1:] + xb[:-1]), 0.5 * (yb[1:] + yb[:-1])
                sn = np.maximum(sn - 9.81 * np.maximum(np.interp(xm, [-1e5, 0.0, 200.0, 1e5], [0.0, 0.0, 100.0, 100.0]) - ym, 0.0) / 1000.0, 0.0)
            k_ = clave[nm]
            if alto:
                t_, H_ = re.match(r"alto_(\w+?)_H(\d+)", caso.name).groups(); k_ = f"{t_}|{H_}|{k_.split('|')[2]}"
            if con_H:
                c_, e_, q_ = k_.split("|"); k_ = f"{c_}|{e_}|{re.search(r'_H(\d+)', caso.name).group(1)}|{q_}"
            out[k_] = dict(media=float((sn * lb).sum() / lb.sum()), p90=float(np.percentile(sn, 90)), max=float(sn.max()), prof_max=float((yt - yb).max()))
    return out


if __name__ == "__main__":
    ldet, lalto, lmc = sys.argv[1], sys.argv[2], sys.argv[3]
    OUT = dict(metodo="Morgenstern–Price (Slide2 9.043, GLE con función medio seno)", det={}, conv={}, alto={}, mc={})
    CL = json.load(open(SL / "det6" / "claves.json", encoding="utf-8"))
    for (mod, esc), f in leer(ldet).items():
        H = re.search(r"_H(\d+)_", mod).group(1); caso, escn, q = CL[esc].split("|")
        if mod.endswith("_conv"):
            OUT["conv"][q] = f; continue
        OUT["det"][f"{caso}|{escn}|{H}|{q}"] = f
    OUT["sn_det"] = sn_mov(ldet, CL, con_H=True)
    CA = json.load(open(SL / "alto6" / "claves.json", encoding="utf-8"))
    # las claves de alto6 se repiten entre modelos (deb700 para debil25 y debil30; inc700 para inc10 e inc20): tipo y H salen
    # del nombre del modelo (alto_<tipo>_H<H>) y de la clave solo la envolvente
    for (mod, esc), f in leer(lalto).items():
        if esc in CA:
            t_, H_ = re.match(r"alto_(\w+?)_H(\d+)", mod).groups(); OUT["alto"][f"{t_}|{H_}|{CA[esc].split('|')[2]}"] = f
    OUT["sn_alto"] = sn_mov(lalto, CA, alto=True)
    for k in sorted(OUT["alto"]):
        s = OUT["sn_alto"].get(k, {})
        print(f"  alto {k:28s} FS {OUT['alto'][k]:.3f}  σ′n media {s.get('media', float('nan')):.2f} máx {s.get('max', float('nan')):.2f} MPa  prof {s.get('prof_max', float('nan')):.0f} m")
    mc = {}
    for (mod, esc), f in leer(lmc).items():
        mc.setdefault(esc.split()[0], []).append((int(esc.split()[1][1:]), f))
    for caso, v in mc.items():
        v = sorted(v); F = np.array([x for _, x in v if np.isfinite(x)]); n = len(F); nf = int((F < 1).sum()); p50, p05 = np.median(F), np.percentile(F, 5)
        sl = (np.log(p50) - np.log(p05)) / 1.645
        OUT["mc"][caso] = dict(n=n, fallas=nf, pf=nf / n, pf_ic95=cp(nf, n), pf_unilateral95=float(betad.ppf(0.95, nf + 1, n - nf)), FS_P50=float(p50),
                               FS_P05=float(p05), FS_min=float(F.min()), beta_ln=float(np.log(p50) / sl), beta_normal=float((F.mean() - 1) / F.std()))
        print(f"  MC {caso}: n={n} fallas {nf} IC {np.round(cp(nf, n), 4)} unilat. {OUT['mc'][caso]['pf_unilateral95']:.4f} FS P50 {p50:.3f} P05 {p05:.3f} β_LN {np.log(p50) / sl:.2f}")
    # ---- sustituto lineal y Pf integrada sobre τ_D
    Z = np.load(AA / "lepsp_sitio6_muestras_e065_general.npz"); sn = Z["sn"]; T = np.tensordot(Z["pesos"], Z["tau"].astype(float), 1)
    idx = np.load(SL / "mc6" / "indices_modelo.npy"); Fm = np.array([x for _, x in sorted(mc["modelo"])]); Tm = T[idx[:len(Fm)]]
    best = None
    for j in range(len(sn)):
        X = np.log(Tm[:, j] / sn[j]); r = np.corrcoef(X, np.log(Fm))[0, 1]
        if best is None or r > best[0]:
            best = (r, j)
    r, j = best; X = np.log(Tm[:, j] / sn[j]); b, a = np.polyfit(X, np.log(Fm), 1)
    Xall = np.log(T[:, j] / sn[j]); lnF = a + b * Xall
    sus = dict(sigma_rep=float(sn[j]), r=float(r), a=float(a), b=float(b), n_muestras=int(len(Xall)), pf=float(np.mean(lnF < 0)),
               beta=float(lnF.mean() / lnF.std()), FS_P05=float(np.exp(np.percentile(lnF, 5))))
    # sin escala: misma envolvente sin el desplazamiento de tamaño → componente no atribuible al tamaño
    Z0 = np.load(AA / "lepsp_sitio6_muestras_e065_ninguno.npz"); T0 = np.tensordot(Z0["pesos"], Z0["tau"].astype(float), 1); X0 = np.log(T0[:, j] / sn[j])
    E = json.load(open(AQ / "lepsp_parametros.json", encoding="utf-8"))["escala"]["general"]; RAZ = np.log(1000.0 / 177.8)
    rng = np.random.default_rng(6); nn = 400000; x0 = rng.choice(X0, nn)
    def pf_tau(tau, colas=None):
        s = np.hypot(E["se_hk"], tau) * RAZ
        dlt = (rng.standard_t(colas, nn) * s * np.sqrt((colas - 2) / colas)) if colas else rng.normal(0, s, nn)
        l = a + b * (x0 + dlt); return float(np.mean(l < 0)), float(l.mean() / l.std())
    tau_med = E["tau"]; lo, hi = E["tau_ci"]; s_ln = (np.log(hi) - np.log(lo)) / (2 * 1.96)
    curva = [dict(tau=float(t), pf=pf_tau(t)[0], beta=pf_tau(t)[1]) for t in (lo, 0.05, tau_med, 0.08, 0.10, hi)]
    taus = np.exp(rng.normal(np.log(tau_med), s_ln, 60)); pfs = [pf_tau(t)[0] for t in taus]
    sus.update(curva_tau=curva, pf_integrada=float(np.mean(pfs)), beta_integrado=float(-norm.ppf(np.mean(pfs))),
               pf_t4=pf_tau(tau_med, 4)[0], beta_t4=float(-norm.ppf(max(pf_tau(tau_med, 4)[0], 1e-12))))
    OUT["sustituto"] = sus
    print(f"  sustituto: σ′rep {sn[j]:.2f} MPa r = {r:.4f}; Pf {sus['pf']:.2e} β {sus['beta']:.2f}; integrada sobre τ_D Pf {sus['pf_integrada']:.2e} (β {sus['beta_integrado']:.2f}); "
          f"colas t4 Pf {sus['pf_t4']:.2e}")
    for c in curva:
        print(f"    τ_D {c['tau']:.3f}: Pf {c['pf']:.2e}  β {c['beta']:.2f}")
    json.dump(OUT, open(AQ / "lepsp_estabilidad6.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("escrito lepsp_estabilidad6.json")
