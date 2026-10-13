"""Leps-P, ronda 6: validación fuera de muestra dejando fuera cada PROGRAMA DE LABORATORIO (auditoría D1: varias
publicaciones comparten laboratorio y a veces material). Datos depurados de lepsp_r6.datos().
Modo A (material nuevo de un laboratorio nuevo), predictores reajustados en cada pliegue:
  acotada  — modelo de la ronda 6 (ln Dmax, ζ por clase, truncamiento, censura); (φ′∞, ζ0) elegidos en el entrenamiento
             por la log-verosimilitud observada (grilla con ψ del ajuste inicial del pliegue);
  cuadratica, potencia — log–log con efectos aleatorios (θ, m) de publicación y set (y = Xβ + Z(u_p + u_s) + ε);
  leps2_jer — envolvente de Leps 2.0 (m = 0.9 fijo) con la misma dispersión jerárquica y heterocedástica (D4);
  leps2_ref — Leps 2.0 publicado con dispersión constante del entrenamiento (como en la ronda 5).
Los ensayos censurados (εa ≥ 19 %) se predicen pero se puntúan aparte (su y es una cota inferior).
Modo B: igual que la ronda 5 (sets con ≥ 2 ensayos a σ′n ≤ 1.5 MPa y ≥ 1 a σ′n ≥ 2 MPa).
Además: p del chequeo de conflicto de todos los sets retenidos (E6) y validación a nivel de set de la envolvente media
(excedencia del P05; E3). Uso: python lepsp_cv6.py <k> <K>  (pliegues k, k+K, ...) → lepsp_cv6_{A,B,S}_<k>.csv;
python lepsp_cv6.py unir → lepsp_cv6_{A,B,S}.csv"""
import sys, time, json
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import chi2
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_r6 import datos, ModeloR6, media3, BETA0, PSI0, CL  # noqa: E402
from lepsp_modelo import Modelo  # noqa: E402
from lepsp_cv3 import casos_B, m_dentro, rmse_ingenuo  # noqa: E402

PH = np.arange(18.0, 32.01, 2.0); ZE = np.round(np.arange(0.20, 0.501, 0.05), 3)
d = datos()


def corte(P, A_lo, s2, r, A_hi):
    a = A_lo; g0 = float(a @ P @ a); c = 1 / (1 / g0 + np.sum(1 / s2)); q = c * np.sum(r / s2); k = A_hi @ P @ a / g0
    return k * q, np.einsum("ij,jk,ik->i", A_hi, P, A_hi) - k ** 2 * g0 + k ** 2 * c


def X_lin(dd, forma):
    dum = np.c_[[(dd.clase == c).values.astype(float) for c in CL]].T; e, x, lD = dd.e.values, dd.x.values, dd.lnD.values
    return {"cuadratica": np.c_[dum, e, lD, x, x ** 2], "potencia": np.c_[dum, e, lD, x], "leps2_jer": np.c_[dum, e, lD]}[forma]


def ajustar_lineal(tr, forma):
    tt = tr.copy()
    if forma == "leps2_jer":
        tt["y"] = tt.y.values - 0.9 * tt.x.values
    X = X_lin(tt, forma); return Modelo(tt, X, [f"b{i}" for i in range(X.shape[1])]).ajustar()


def pred_lineal(m, te, forma):
    X = X_lin(te, forma); x = te.x.values; Z = np.c_[np.ones_like(x), x]
    mu = X @ m.beta + (0.9 * x if forma == "leps2_jer" else 0.0)
    vm = np.einsum("ij,jk,ik->i", Z, m.Gp + m.Gs, Z) + np.einsum("ij,jk,ik->i", X, m.cov_beta, X)
    return mu, np.sqrt(vm + m.sigma_eps(x) ** 2), np.sqrt(vm), m.sigma_eps(x)


def leps2_ref(tr, te):
    f = lambda dd: np.log(np.tan(np.radians(dd.clase.map({"good": 53, "moderate": 50, "low": 47}).values - 20 * dd.e.values))) + 0.9 * dd.x.values
    trn = tr[~tr.cens]; s = np.std(trn.y_obs.values - f(trn)); return f(te), np.full(len(te), s)


def ajustar_acotada(tr):
    m0 = ModeloR6(tr, np.tan(np.radians(25.0)), 0.30, BETA0).ajustar_nl(PSI0, it_cens=4)
    ti = m0.dd.copy(); mejor = None
    for ph in PH:
        for z in ZE:
            mm = ModeloR6(ti, np.tan(np.radians(ph)), z, m0.beta_nl)
            try:
                mm.gn(m0.psi); ll = mm.ll_obs(m0.psi)
            except Exception:
                continue
            if mejor is None or ll > mejor[0]:
                mejor = (ll, ph, z, mm.beta_nl.copy())
    _, ph, z, b0 = mejor
    mb = ModeloR6(ti, np.tan(np.radians(ph)), z, b0).ajustar_nl(m0.psi, it_cens=4)
    return mb, ph, z


def pred_acotada(mb, te):
    f, J, Z = media3(mb.beta_nl, te, mb.T, mb.z0, True); x = te.x.values
    vm = np.einsum("ij,jk,ik->i", Z, mb.Gp + mb.Gs, Z) + np.einsum("ij,jk,ik->i", J, mb.cov_beta, J)
    return f, np.sqrt(vm + mb.sigma_eps(x) ** 2), np.sqrt(vm), mb.sigma_eps(x), J, Z


def pliegue(g):
    tr = d[d.lab != g].reset_index(drop=True); te = d[d.lab == g].reset_index(drop=True)
    FA, FB, FS = [], [], []
    mb, ph, z = ajustar_acotada(tr)
    P = {"acotada": pred_acotada(mb, te)}
    for forma in ("cuadratica", "potencia", "leps2_jer"):
        P[forma] = pred_lineal(ajustar_lineal(tr[~tr.cens].reset_index(drop=True), forma), te, forma)
    mu0, sd0 = leps2_ref(tr, te)
    for k in range(len(te)):
        row = dict(lab=g, pub=te.pub[k], Set=te.Set[k], x=te.x[k], y=te.y_obs[k], cens=bool(te.cens[k]), phi_cs=ph, zeta=z, mu0=mu0[k], sd0=sd0[k])
        for nm, p in P.items():
            row[f"mu_{nm}"] = p[0][k]; row[f"sd_{nm}"] = p[1][k]
        FA.append(row)
    # validación a nivel de set de la envolvente media (sin censurados) y p del chequeo de conflicto (todos los sets)
    f, sd, sdm, se, J, Zg = P["acotada"]; Gp, Gs = mb.Gp, mb.Gs; G = Gp + Gs
    for s, gi in te.groupby("Set"):
        ii = gi.index.values; ok = ii[~te.cens.values[ii]]
        if len(ok) == 0:
            continue
        r = te.y_obs.values[ok] - f[ok]; A = Zg[ok]; Jj = J[ok]
        V = A @ G @ A.T + Jj @ mb.cov_beta @ Jj.T + np.diag(se[ok] ** 2)
        D2 = float(r @ np.linalg.solve(V, r)); pval = 1 - chi2.cdf(D2, len(ok))
        w = np.ones(len(ok)) / len(ok); vbar = float(w @ V @ w); zset = float(r.mean() / np.sqrt(vbar))
        row = dict(lab=g, pub=te.pub[ii[0]], Set=s, n=len(ok), xbar=float(te.x.values[ok].mean()), pval=pval, z_acotada=zset)
        for nm in ("cuadratica", "potencia", "leps2_jer"):
            mu_, _, sdm_, se_ = P[nm]; rr = te.y_obs.values[ok] - mu_[ok]
            row[f"z_{nm}"] = float(rr.mean() / np.sqrt(np.mean(sdm_[ok] ** 2) + np.mean(se_[ok] ** 2) / len(ok)))
        FS.append(row)
    # ---- modo B (sin censurados entre los ensayos de actualización y de prueba)
    tn = te[~te.cens].reset_index(drop=True); cB = casos_B(tn)
    if cB:
        trn = tr[~tr.cens].reset_index(drop=True); mtr = m_dentro(trn); s090 = rmse_ingenuo(trn, 0.90); s_tr = rmse_ingenuo(trn, mtr)
        f, sdA, sdmA, seA, J, Zg = pred_acotada(mb, tn); x = tn.x.values; nb = J.shape[1]
        P1 = np.zeros((2 + nb, 2 + nb)); P1[:2, :2] = G; P1[2:, 2:] = mb.cov_beta
        Af = lambda ii, xx=None: (lambda r_: np.c_[r_[2], r_[1]])(media3(mb.beta_nl, tn.iloc[ii].assign(x=xx if xx is not None else tn.x.values[ii]), mb.T, mb.z0, True))
        pinfo = {}
        for s, lo, hi in cB:
            xl, xh = x[lo], x[hi]; s2 = mb.sigma_eps(xl) ** 2; rl = tn.y_obs.values[lo] - f[lo]
            Al = Af(lo); Ah = Af(hi); xb = float(np.mean(xl)); Ab = Af(lo[:1], np.array([xb]))[0]
            Vp = Al @ P1 @ Al.T + np.diag(s2); pval = 1 - chi2.cdf(float(rl @ np.linalg.solve(Vp, rl)), len(lo)); pinfo[s] = pval
            se_h = mb.sigma_eps(xh) ** 2; dn, vn = corte(P1, Ab, s2, rl, Ah)
            K = P1 @ Al.T @ np.linalg.inv(Vp); Pp = P1 - K @ Al @ P1; mj = K @ rl
            var = {"nivel": (f[hi] + dn, np.sqrt(vn + se_h)), "previa": (f[hi], sdA[hi]),
                   "conjunta": (f[hi] + Ah @ mj, np.sqrt(np.einsum("ij,jk,ik->i", Ah, Pp, Ah) + se_h))}
            var["descarte"] = var["previa"] if pval < 0.05 else var["nivel"]
            for nm, m_, sv in (("ingenuo_m090", 0.90, s090), ("ingenuo_mtr", mtr, s_tr)):
                th = np.mean(tn.y_obs.values[lo] - m_ * xl); var[nm] = (th + m_ * xh, np.full(len(hi), sv))
            for nm, (mu, sd_) in var.items():
                for k, ii in enumerate(hi):
                    FB.append(dict(variante=nm, lab=g, pub=tn.pub[ii], Set=s, x=x[ii], y=tn.y_obs[ii], mu=mu[k], sd=sd_[k], pval=pval))
        # procedimiento usado en la aplicación: sets marcados descartados y actualización conjunta con laboratorio común
        nS = len(cB); Dd = 2 + 2 * nS + nb; Pq = np.zeros((Dd, Dd)); Pq[:2, :2] = Gp; Pq[-nb:, -nb:] = mb.cov_beta
        for j in range(nS):
            Pq[2 + 2 * j:4 + 2 * j, 2 + 2 * j:4 + 2 * j] = Gs
        rows, rv, ys = [], [], []
        for j, (s, lo, hi) in enumerate(cB):
            if pinfo[s] < 0.05:
                continue
            ab = Af(lo[:1], np.array([float(np.mean(x[lo]))]))[0]
            for ii in lo:
                rw = np.zeros(Dd); rw[:2] = ab[:2]; rw[2 + 2 * j:4 + 2 * j] = ab[:2]; rw[-nb:] = ab[2:]
                rows.append(rw); rv.append(mb.sigma_eps(np.array([x[ii]]))[0] ** 2); ys.append(tn.y_obs.values[ii] - f[ii])
        m_post, P_post = np.zeros(Dd), Pq
        if rows:
            Rm = np.array(rows); S = Rm @ Pq @ Rm.T + np.diag(rv); K = Pq @ Rm.T @ np.linalg.inv(S); m_post = K @ np.array(ys); P_post = Pq - K @ Rm @ Pq
        for j, (s, lo, hi) in enumerate(cB):
            Ah = Af(hi); H = np.zeros((len(hi), Dd)); H[:, :2] = Ah[:, :2]; H[:, 2 + 2 * j:4 + 2 * j] = Ah[:, :2]; H[:, -nb:] = Ah[:, 2:]
            mu = f[hi] + H @ m_post; sd_ = np.sqrt(np.einsum("ij,jk,ik->i", H, P_post, H) + mb.sigma_eps(x[hi]) ** 2)
            for k, ii in enumerate(hi):
                FB.append(dict(variante="sitio", lab=g, pub=tn.pub[ii], Set=s, x=x[ii], y=tn.y_obs[ii], mu=mu[k], sd=sd_[k], pval=pinfo[s]))
    return FA, FB, FS, ph, z


if __name__ == "__main__":
    t0 = time.time()
    if sys.argv[1] == "unir":
        for t in "ABS":
            fs = sorted(AQ.glob(f"lepsp_cv6_{t}_*.csv")); pd.concat([pd.read_csv(f) for f in fs]).to_csv(AQ / f"lepsp_cv6_{t}.csv", index=False)
            print(t, len(fs), "partes")
        sys.exit()
    k, K = int(sys.argv[1]), int(sys.argv[2]); labs = sorted(d.lab.unique()); A, B, S = [], [], []
    hechos = set()
    for t, L_ in (("A", A), ("B", B), ("S", S)):                 # reanudar: conservar los pliegues ya calculados
        fp = AQ / f"lepsp_cv6_{t}_{k}.csv"
        if fp.exists() and fp.stat().st_size > 5:
            dfp = pd.read_csv(fp); L_ += dfp.to_dict("records")
            if t == "A":
                hechos = set(dfp.lab.unique())
    for g in [g_ for g_ in labs if g_ not in hechos][k::K] if hechos == set() else [g_ for g_ in labs[k::K] if g_ not in hechos]:
        fa, fb, fs, ph, z = pliegue(g); A += fa; B += fb; S += fs
        print(f"  lab {g[:38]:38s} n={sum(1 for r in fa):3d} sets B {len(set(r['Set'] for r in fb))}  φ′∞ {ph:.0f} ζ0 {z:.2f} ({time.time()-t0:.0f} s)", flush=True)
        pd.DataFrame(A).to_csv(AQ / f"lepsp_cv6_A_{k}.csv", index=False); pd.DataFrame(B).to_csv(AQ / f"lepsp_cv6_B_{k}.csv", index=False)
        pd.DataFrame(S).to_csv(AQ / f"lepsp_cv6_S_{k}.csv", index=False)
