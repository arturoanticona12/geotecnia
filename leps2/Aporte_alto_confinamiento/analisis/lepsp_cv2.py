"""Leps-P, validación (ronda 2): ajusta M2 una vez por publicación excluida (guarda lepsp_folds.pkl) y evalúa:
(1) Modo B por rama de la regla (conjunta / solo nivel) y sensibilidad a los umbrales (razón 2, 3, 4; p 0.01, 0.05, 0.10);
(2) líneas base ingenuas: φ′1 ajustado a los ensayos del sitio con m fijo (0.86 y 0.90), σ predictiva por RMSE fuera de muestra;
(3) validación específica de la rama conjunta: sets con ≥ 4 ensayos; se actualiza con la mitad inferior en σ′n y se predice
    la superior, solo si la mitad inferior abarca una razón ≥ 3;
(4) Modo A con clase desconocida (previa de mezcla de las tres clases, pesos = frecuencia en el entrenamiento).
Salida: lepsp_cv2_B.csv, lepsp_cv2_J.csv, lepsp_cv2_Amix.csv."""
import sys, pickle, time, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.stats import chi2, norm
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar, Modelo  # noqa: E402

d = preparar(load_db(), CLASE); CL = ["good", "moderate", "low"]


def X_(dd, clase=None):
    c = dd.clase.values if clase is None else np.full(len(dd), clase)
    dum = np.c_[[(c == k).astype(float) for k in CL]].T
    return np.c_[dum, dd.e.values, dd.x.values, dd.x.values ** 2]


PK = AQUI / "lepsp_folds.pkl"
if PK.exists():
    FOLDS = pickle.load(open(PK, "rb"))
else:
    FOLDS = {}; t0 = time.time()
    for g in d.pub.unique():
        tr = d[d.pub != g].reset_index(drop=True); m = Modelo(tr, X_(tr), [f"b{i}" for i in range(6)]).ajustar()
        FOLDS[g] = dict(beta=m.beta, cov_beta=m.cov_beta, Gp=m.Gp, Gs=m.Gs, a=m.a, freq={k: float((tr.clase == k).mean()) for k in CL},
                        rmse={})
        print(f"pliegue {g}: {time.time()-t0:.0f} s", flush=True)
    pickle.dump(FOLDS, open(PK, "wb"))
se = lambda F, x: np.exp(F["a"][0] + F["a"][1] * np.asarray(x))


def actualizar(F, Xl, xl, yl, modo):
    """Devuelve (bp, Cp, pval, rama) para modo en {'conjunta', 'nivel', ('regla', razon_min, p_min)}."""
    G = F["Gp"] + F["Gs"]; Zl = np.c_[np.ones_like(xl), xl]; R = np.diag(se(F, xl) ** 2); rl = yl - Xl @ F["beta"]
    V = Zl @ G @ Zl.T + Xl @ F["cov_beta"] @ Xl.T + R; pval = 1 - chi2.cdf(float(rl @ np.linalg.solve(V, rl)), len(xl))
    razon = np.exp(xl.max() - xl.min())
    if isinstance(modo, tuple):
        modo = "conjunta" if (razon >= modo[1] and pval >= modo[2]) else "nivel"
    if modo == "conjunta":
        Cp = np.linalg.inv(np.linalg.inv(G) + Zl.T @ np.linalg.solve(R, Zl)); bp = Cp @ Zl.T @ np.linalg.solve(R, rl)
    else:
        xb = float(np.mean(xl)); T = np.array([[1.0, xb], [0.0, 1.0]]); Gq = T @ G @ T.T; g0 = Gq[0, 0]; z1 = np.ones((len(xl), 1))
        c = 1 / (1 / g0 + (z1.T @ np.linalg.solve(R, z1)).item()); q0 = c * (z1.T @ np.linalg.solve(R, rl)).item()
        q1 = Gq[1, 0] / g0 * q0; v11 = Gq[1, 1] - Gq[1, 0] ** 2 / g0 + (Gq[1, 0] / g0) ** 2 * c
        Cq = np.array([[c, Gq[1, 0] / g0 * c], [Gq[1, 0] / g0 * c, v11]]); Ti = np.linalg.inv(T); bp = Ti @ np.array([q0, q1]); Cp = Ti @ Cq @ Ti.T
    return bp, Cp, pval, modo, razon


def predecir(F, Xh, xh, bp, Cp):
    Zh = np.c_[np.ones_like(xh), xh]
    mu = Xh @ F["beta"] + Zh @ bp
    v = np.einsum("ij,jk,ik->i", Zh, Cp, Zh) + np.einsum("ij,jk,ik->i", Xh, F["cov_beta"], Xh) + se(F, xh) ** 2
    return mu, np.sqrt(v)


def ingenuo(lo, hi, m):
    """φ′1 por mínimos cuadrados en ln τ con m fijo (práctica habitual con Leps 2.0)."""
    th = float(np.mean(lo.y.values - m * lo.x.values)); return th + m * hi.x.values


filasB, filasJ, filasM = [], [], []
VARIANTES = [("conjunta", "conjunta"), ("nivel", "nivel")] + [(f"regla r{r} p{p}", ("regla", r, p)) for r in (2, 3, 4) for p in (0.01, 0.05, 0.10)]
for g in d.pub.unique():
    F = FOLDS[g]; te = d[d.pub == g].reset_index(drop=True)
    # (4) modo A con clase desconocida: mezcla de las tres clases
    for k in range(len(te)):
        r = te.iloc[[k]]; mus, vs, ws = [], [], []
        for c in CL:
            Xc = X_(r, c); z = np.c_[1.0, r.x.values[0]]
            mus.append(float(Xc @ F["beta"])); ws.append(F["freq"][c])
            vs.append(float(z @ (F["Gp"] + F["Gs"]) @ z.T + Xc @ F["cov_beta"] @ Xc.T + se(F, r.x.values) ** 2))
        ws = np.array(ws) / sum(ws); mus = np.array(mus); vs = np.array(vs)
        filasM.append(dict(pub=g, x=r.x.values[0], y=r.y.values[0], mus=mus.tolist(), sds=np.sqrt(vs).tolist(), ws=ws.tolist()))
    for s, gi in te.groupby("Set"):
        # ---- (1)+(2) modo B estándar
        lo = gi[gi.sn <= 1.5]; hi = gi[gi.sn >= 2]
        if len(lo) >= 2 and len(hi) >= 1:
            Xl, Xh = X_(lo), X_(hi); xl, xh = lo.x.values, hi.x.values; muA, sdA = predecir(F, Xh, xh, np.zeros(2), F["Gp"] + F["Gs"])
            for nm, modo in VARIANTES:
                bp, Cp, pval, rama, razon = actualizar(F, Xl, xl, lo.y.values, modo); mu, sd = predecir(F, Xh, xh, bp, Cp)
                for k in range(len(hi)):
                    filasB.append(dict(variante=nm, rama=rama, pub=g, Set=s, x=xh[k], y=hi.y.values[k], mu=mu[k], sd=sd[k], muA=muA[k], sdA=sdA[k], pval=pval, razon=razon))
            for m0 in (0.86, 0.90):
                mu = ingenuo(lo, hi, m0)
                for k in range(len(hi)):
                    filasB.append(dict(variante=f"ingenuo m={m0}", rama="—", pub=g, Set=s, x=xh[k], y=hi.y.values[k], mu=mu[k], sd=np.nan, muA=muA[k], sdA=sdA[k], pval=np.nan, razon=np.nan))
        # ---- (3) rama conjunta: mitad inferior → mitad superior
        if len(gi) >= 4:
            gs = gi.sort_values("sn"); h = len(gs) // 2; lo, hi = gs.iloc[:h], gs.iloc[h:]
            if np.exp(lo.x.max() - lo.x.min()) >= 3 or (len(lo) >= 2 and np.exp(lo.x.max() - lo.x.min()) >= 3):
                Xl, Xh = X_(lo), X_(hi); xl, xh = lo.x.values, hi.x.values; muA, sdA = predecir(F, Xh, xh, np.zeros(2), F["Gp"] + F["Gs"])
                for nm in ("conjunta", "nivel"):
                    bp, Cp, pval, rama, razon = actualizar(F, Xl, xl, lo.y.values, nm); mu, sd = predecir(F, Xh, xh, bp, Cp)
                    for k in range(len(hi)):
                        filasJ.append(dict(variante=nm, pub=g, Set=s, x=xh[k], y=hi.y.values[k], mu=mu[k], sd=sd[k], muA=muA[k], sdA=sdA[k], pval=pval,
                                           razon_ext=np.exp(xh.max() - xl.max())))
                mu = ingenuo(lo, hi, 0.86)
                for k in range(len(hi)):
                    filasJ.append(dict(variante="ingenuo m=0.86", pub=g, Set=s, x=xh[k], y=hi.y.values[k], mu=mu[k], sd=np.nan, muA=muA[k], sdA=sdA[k], pval=np.nan, razon_ext=np.nan))
pd.DataFrame(filasB).to_csv(AQUI / "lepsp_cv2_B.csv", index=False); pd.DataFrame(filasJ).to_csv(AQUI / "lepsp_cv2_J.csv", index=False)
pd.DataFrame(filasM).to_json(AQUI / "lepsp_cv2_Amix.json", orient="records")
print("escrito lepsp_cv2_B.csv, lepsp_cv2_J.csv, lepsp_cv2_Amix.json")
