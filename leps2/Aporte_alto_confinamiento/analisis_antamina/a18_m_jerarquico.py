"""Calibración del exponente m de Leps 2.0 para Antamina con toda la data (pedido del usuario, 2026-10-10).
Modelo jerárquico normal–normal (empírico):
  1. Base mundial de Leps 2.0 (lepsp_r6.datos, 741 ensayos): en cada set con ≥ 3 ensayos y σ′n máx/mín ≥ 2, m_i = pendiente de
     ln τ frente a ln σ′n (en Leps 2.0, ln(τ/σ0) = ln tan φ′1 + m·ln(σ′n/σ0)), con su error estándar s_i.
  2. Distribución de m entre materiales: media μ y varianza entre sets τ² por Paule–Mandel, descontando s_i².
  3. Antamina: m con un nivel propio por set (igual que la pendiente dentro de set de la base mundial), triaxiales (residuo en ln q)
     y cortes directos (residuo en ln τ, con el factor de a9); error estándar por bootstrap de sets.
  4. Posterior de m de Antamina: normal con precisión 1/τ² + 1/s_A², truncada en m ≤ 1 (límite de Leps 2.0).
También se informa la variante con solo los ensayos a σ′n ≥ 1 MPa (curvatura a alto confinamiento).
Escribe a18_m_jerarquico.json."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
from scipy.optimize import least_squares
from scipy.stats import norm, truncnorm
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "analisis"))
from lepsp_r6 import datos  # noqa: E402
from modelos import sigma1, tau_leps2  # noqa: E402
OM, S0 = 20.0, 1.013
R9 = json.load(open(AQ / "a9_leps2_antamina.json", encoding="utf-8")); C_DS = R9["datos"]["c_ds"]


def pendientes(W, snmin=0.0):
    out = []
    for s, g in W.groupby("Set"):
        g = g[(g.sn >= snmin) & (g.sn > 0) & (g.tau > 0)]
        if len(g) >= 3 and g.sn.max() / g.sn.min() >= 2:
            x, y = np.log(g.sn.values / S0), np.log(g.tau.values / S0)
            X = np.c_[np.ones(len(x)), x]; b, res, *_ = np.linalg.lstsq(X, y, rcond=None)
            r = y - X @ b; s2 = (r @ r) / (len(x) - 2) if len(x) > 2 else np.nan
            se = np.sqrt(s2 * np.linalg.inv(X.T @ X)[1, 1])
            out.append(dict(set=s, m=b[1], se=max(se, 1e-3), n=len(g), lab=g.lab.iloc[0], clase=g.clase.iloc[0]))
    return pd.DataFrame(out)


def paule_mandel(m, se):
    """τ² tal que la Q generalizada iguala k − 1 (Paule–Mandel). DerSimonian–Laird daba τ = 0.085, mayor que la desviación
    estándar bruta de las pendientes (0.064): 18 sets con s_i ≤ 0.005 dominan los pesos 1/s_i² (auditoría 2026-10-10)."""
    from scipy.optimize import brentq
    k = len(m)
    def q(t2):
        ws = 1 / (se ** 2 + t2); mu = np.sum(ws * m) / ws.sum(); return np.sum(ws * (m - mu) ** 2) - (k - 1)
    t2 = brentq(q, 0.0, 1.0) if q(0.0) > 0 else 0.0
    ws = 1 / (se ** 2 + t2); mu = np.sum(ws * m) / ws.sum()
    return float(mu), float(np.sqrt(t2)), float(np.sqrt(1 / ws.sum()))


# ---- Antamina: m común con nivel propio por set
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
d["set"] = d.fuente_id + "|" + d.set_id.astype(str); d["tx"] = d.tipo == "TX"; d["e"] = d.e0_adoptado
SETS = list(d.set.unique())


def resid(g, pe0s, m):
    idx = g.set.map({s: i for i, s in enumerate(SETS)}).values; pe = pe0s[idx]; e = g.e.values; tx = g.tx.values; r = np.empty(len(g))
    if tx.any():
        s3 = g.s3.values[tx]; r[tx] = np.log(sigma1(tau_leps2, s3, pe[tx] - OM * e[tx], m)[0] - s3) - np.log((g.s1 - g.s3).values[tx])
    if (~tx).any():
        r[~tx] = C_DS * (np.log(tau_leps2(g.sn_ds.values[~tx], pe[~tx] - OM * e[~tx], m)) - np.log(g.tau_ds.values[~tx]))
    return r


def m_antamina(g):
    p0 = np.r_[np.full(len(SETS), 48.0), 0.9]
    r = least_squares(lambda p: resid(g, p[:-1], p[-1]), p0, bounds=(np.r_[np.full(len(SETS), 30.0), 0.5], np.r_[np.full(len(SETS), 70.0), 1.5]))
    return float(r.x[-1])


mA = m_antamina(d); rng = np.random.default_rng(18); boot = []
for _ in range(400):
    sel = rng.choice(SETS, len(SETS)); gb = pd.concat([d[d.set == s].assign(set=s) for s in sel])
    try:
        boot.append(m_antamina(gb))
    except Exception:
        pass
seA = float(np.std(boot, ddof=1))
print(f"Antamina (nivel por set, {len(SETS)} sets, {len(d)} ensayos): m = {mA:.3f}, error estándar (bootstrap por sets) {seA:.3f}")
# ---- base mundial y posterior
W = datos(); out = dict(antamina=dict(m=mA, se=seA, n_sets=len(SETS), boot=[float(np.percentile(boot, q)) for q in (5, 50, 95)]), variantes={})
for nm, snmin in (("rango completo", 0.0), ("σ′n ≥ 1 MPa", 1.0)):
    T = pendientes(W, snmin); mu, tau, se_mu = paule_mandel(T.m.values, T.se.values)
    prec = 1 / tau ** 2 + 1 / seA ** 2; mpost = (mu / tau ** 2 + mA / seA ** 2) / prec; spost = np.sqrt(1 / prec)
    a = (-np.inf); b = (1.0 - mpost) / spost; dist = truncnorm(a, b, loc=mpost, scale=spost)
    q = {p: float(dist.ppf(p / 100)) for p in (5, 10, 50, 90, 95)}
    out["variantes"][nm] = dict(n_sets=len(T), mu=mu, tau=tau, se_mu=se_mu, m_P10_sets=float(T.m.quantile(0.1)), m_P50_sets=float(T.m.median()),
                                m_P90_sets=float(T.m.quantile(0.9)), post_media_sin_truncar=float(mpost), post_sd_sin_truncar=float(spost), post=q,
                                peso_antamina=float((1 / seA ** 2) / prec))
    print(f"[{nm}] sets {len(T)}: μ = {mu:.3f} (±{se_mu:.3f}), dispersión entre materiales τ = {tau:.3f}; P10–P90 de los sets {T.m.quantile(0.1):.3f}–{T.m.quantile(0.9):.3f}")
    print(f"     posterior Antamina: P5 {q[5]:.3f}  P50 {q[50]:.3f}  P95 {q[95]:.3f}  (peso de Antamina {100 * (1 / seA ** 2) / prec:.0f} %)")
json.dump(out, open(AQ / "a18_m_jerarquico.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
