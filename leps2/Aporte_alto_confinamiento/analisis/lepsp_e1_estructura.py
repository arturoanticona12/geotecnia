"""Leps-P, crítica E1: ¿la ventaja de verosimilitud de la envolvente acotada sobre la cuadrática viene de la media,
de la estructura de covarianza o de la aproximación de primer orden (FO)?

Datos: datos() de lepsp_r6 (741 ensayos), sin censura ni truncamiento. Todos los modelos: clase (3), e, lnD.
Log-verosimilitud ML gaussiana exacta por bloques de publicación (con constantes): ll = Σ_b log N(y_b | f_b, V_b),
V_b = Z G_p Zᵀ + (S ∘ Z G_s Zᵀ) + diag σε²(x),  ln σε = a0 + a1 x.
  M1  media acotada, Z = ∂f/∂(η, ζ) en u = 0 (FO), máx. sobre β, ψ, ζ0 y φ′∞ ∈ grilla
  M2  media acotada, Z = [1, x] (exacta), máx. sobre β, ψ, ζ0 y φ′∞ ∈ grilla
  M3  media cuadrática, Z = [1, x] (exacta);  M3b  cuadrática por clase (+ clase×x)
  M4  media cuadrática, Z = Z de M1 en su óptimo (fija; exacta dado Z);  M4b  ídem por clase
  M5  Laplace (modo condicional, Hessiano de Gauss–Newton) para el modelo no lineal de M1; en el óptimo de M1 y reoptimizado.
Además: contribución por publicación y log score fuera de muestra (dejar fuera una publicación, ψ fija).
Salida: lepsp_e1_estructura.json"""
import sys, json, time, warnings
from pathlib import Path
import numpy as np
from scipy.linalg import solve_triangular, cho_factor, cho_solve
from scipy.optimize import minimize
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ))
from lepsp_r6 import datos, media3, CL, NOMBRES, BETA0, PSI0, ModeloR6  # noqa: E402

T0 = time.time()
LOG2PI = np.log(2 * np.pi)
PHIS = [20.0, 22.0, 24.0, 25.0, 26.0, 28.0]      # grilla del encargo (tabla principal)
PHIS_EXT = [16.0, 18.0]                           # extensión de sensibilidad (M2 queda en el borde de 20°)
LAPLACE_MAX_S = 45 * 60          # tope de cómputo para la reoptimización por Laplace

d = datos()
n = len(d)
y = d.y_obs.values.astype(float)
x = d.x.values; e = d.e.values; lD = d.lnD.values
dum = np.c_[[(d.clase == c).values.astype(float) for c in CL]].T
ZADD = np.c_[np.ones(n), x]
X_Q = np.c_[dum, e, lD, x, x ** 2]
NOM_Q = CL + ["e", "lnD", "x", "x2"]
X_QB = np.c_[X_Q, dum[:, 1] * x, dum[:, 2] * x]
NOM_QB = NOM_Q + ["moderate:x", "low:x"]

PUBS = sorted(d.pub.unique())
B = []
for p in PUBS:
    ip = np.where(d.pub.values == p)[0]
    sets = d.Set.values[ip]; u, cod = np.unique(sets, return_inverse=True)
    B.append(dict(pub=p, ip=ip, S=(cod[:, None] == cod[None, :]).astype(float), cod=cod, ns=len(u)))


def log(msg):
    print(f"[{time.time() - T0:7.0f} s] {msg}", flush=True)


def G2(p):
    s0, s1, r = np.exp(p[0]), np.exp(p[1]), np.tanh(np.clip(p[2], -6, 6))
    return np.array([[s0 * s0, r * s0 * s1], [r * s0 * s1, s1 * s1]])


def unpack(psi):
    return G2(psi[0:3]), G2(psi[3:6]), psi[6:8]


def Vb(b, Z, Gp, Gs, a):
    ip = b["ip"]; Zb = Z[ip]
    V = Zb @ Gp @ Zb.T + b["S"] * (Zb @ Gs @ Zb.T)
    V[np.diag_indices_from(V)] += np.exp(2 * (a[0] + a[1] * x[ip]))
    return V


def ll_exact(f, Z, psi, por_bloque=False, bl=None):
    Gp, Gs, a = unpack(psi); out = []
    for b in (B if bl is None else bl):
        try:
            L = np.linalg.cholesky(Vb(b, Z, Gp, Gs, a))
        except np.linalg.LinAlgError:
            return -1e12 if not por_bloque else None
        z = solve_triangular(L, y[b["ip"]] - f[b["ip"]], lower=True)
        out.append(-0.5 * z @ z - np.log(np.diag(L)).sum() - 0.5 * len(b["ip"]) * LOG2PI)
    return np.array(out) if por_bloque else float(np.sum(out))


def gls(X, Z, psi, bl=None):
    """β̂ por mínimos cuadrados generalizados y log-verosimilitud ML perfilada exacta."""
    Gp, Gs, a = unpack(psi); k = X.shape[1]; A = np.zeros((k, k)); g = np.zeros(k); ld = 0.0; yy = 0.0; m = 0
    for b in (B if bl is None else bl):
        ip = b["ip"]
        try:
            L = np.linalg.cholesky(Vb(b, Z, Gp, Gs, a))
        except np.linalg.LinAlgError:
            return None, None, -1e12
        Xi = solve_triangular(L, X[ip], lower=True); yi = solve_triangular(L, y[ip], lower=True)
        A += Xi.T @ Xi; g += Xi.T @ yi; yy += yi @ yi; ld += 2 * np.log(np.diag(L)).sum(); m += len(ip)
    try:
        beta = np.linalg.solve(A, g)
    except np.linalg.LinAlgError:
        return None, None, -1e12
    return beta, np.linalg.inv(A), float(-0.5 * (ld + yy - beta @ g + m * LOG2PI))


def opt(fun, p0, bounds=None, nm=True, maxiter=5000):
    p = np.asarray(p0, float)
    if nm:
        p = minimize(fun, p, method="Nelder-Mead", options=dict(maxiter=maxiter, maxfev=maxiter, xatol=1e-6, fatol=1e-8)).x
    best = None
    for _ in range(3):
        r = minimize(fun, p, method="L-BFGS-B", bounds=bounds, options=dict(maxiter=maxiter, maxfun=50 * maxiter, ftol=1e-13, gtol=1e-7))
        if best is not None and best.fun - r.fun < 1e-7:
            best = r if r.fun < best.fun else best; break
        best = r; p = r.x
    return best


# ---------------------------------------------------------------- modelos lineales en β (M3, M3b, M4, M4b)
def fit_lineal(X, Z, nombre):
    f = lambda p: -gls(X, Z, p)[2]
    mejores = [opt(f, s) for s in (PSI0, np.array([np.log(0.1), np.log(0.05), 0.0, np.log(0.05), np.log(0.03), 0.0, np.log(0.05), 0.0]))]
    r = min(mejores, key=lambda r: r.fun); psi = r.x
    beta, C, ll = gls(X, Z, psi)
    log(f"{nombre}: ML {ll:.3f} (arranques: {[round(-m.fun, 3) for m in mejores]})")
    return dict(ll=ll, psi=psi, beta=beta, C=C, X=X, Z=Z, k=X.shape[1] + 8)


# ---------------------------------------------------------------- media acotada (M1, M2)
def fb(beta, T, z0):
    return media3(beta, d, T, z0, clase_z=True)


def ll_b(beta, psi, T, z0, cov, por_bloque=False):
    f, J, Zd = fb(beta, T, z0)
    return ll_exact(f, Zd if cov == "dec" else ZADD, psi, por_bloque)


def gn(beta, psi, T, z0, cov, bl=None, it=60):
    """Gauss–Newton para β con ψ fija (para «dec», Z se recalcula en cada iteración: esquema FO usual)."""
    Gp, Gs, a = unpack(psi); bl = B if bl is None else bl; beta = beta.copy(); A = None
    for _ in range(it):
        f, J, Zd = fb(beta, T, z0); Z = Zd if cov == "dec" else ZADD
        A = np.zeros((7, 7)); g = np.zeros(7); Ls = []
        for b in bl:
            ip = b["ip"]; L = np.linalg.cholesky(Vb(b, Z, Gp, Gs, a)); Ls.append(L)
            Ji = solve_triangular(L, J[ip], lower=True); ri = solve_triangular(L, y[ip] - f[ip], lower=True)
            A += Ji.T @ Ji; g += Ji.T @ ri
        step = np.linalg.solve(A, g)
        obj0 = sum((solve_triangular(L, y[b["ip"]] - f[b["ip"]], lower=True) ** 2).sum() for L, b in zip(Ls, bl))
        t = 1.0
        for _h in range(30):
            fn = fb(beta + t * step, T, z0)[0]
            obj = sum((solve_triangular(L, y[b["ip"]] - fn[b["ip"]], lower=True) ** 2).sum() for L, b in zip(Ls, bl))
            if obj <= obj0 + 1e-12:
                break
            t *= 0.5
        beta = beta + t * step
        if np.max(np.abs(t * step)) < 1e-9:
            break
    return beta, np.linalg.inv(A)


def fit_acotada(T, cov, start):
    beta, psi, z0 = [np.array(v, float) if np.ndim(v) else float(v) for v in start]
    # barrido grueso de ζ0 (β por GN, ψ fija) para el arranque
    cand = []
    for zz in sorted({round(z0, 3), 0.12, 0.2, 0.3, 0.45, 0.65}):
        try:
            bb, _ = gn(beta, psi, T, zz, cov)
            cand.append((ll_b(bb, psi, T, zz, cov), zz, bb))
        except np.linalg.LinAlgError:
            pass
    _, z0, beta = max(cand, key=lambda c: c[0])
    for _ in range(2):                                     # alternancia β | ψ
        psi = opt(lambda p: -ll_b(beta, p, T, z0, cov), psi, nm=True, maxiter=3000).x
        beta, _ = gn(beta, psi, T, z0, cov)
    th0 = np.r_[beta, psi, z0]
    bnds = [(None, None)] * 15 + [(0.01, 3.0)]
    r = opt(lambda t: -ll_b(t[:7], t[7:15], T, t[15], cov), th0, bounds=bnds, nm=False, maxiter=4000)
    th = r.x
    return dict(ll=-float(r.fun), beta=th[:7], psi=th[7:15], z0=float(th[15]), T=T)


def perfil(cov, nombre):
    res = []; start = (BETA0, PSI0, 0.30)
    for ph in PHIS:
        r = fit_acotada(np.tan(np.radians(ph)), cov, start); r["phi"] = ph; res.append(r)
        start = (r["beta"], r["psi"], r["z0"])
        log(f"{nombre} φ′∞ = {ph:4.1f}°: ML {r['ll']:.3f}  ζ0 {r['z0']:.3f}")
    s0 = (res[0]["beta"], res[0]["psi"], res[0]["z0"])
    for ph in sorted(PHIS_EXT, reverse=True):              # extensión hacia φ′∞ bajos (no entra en la tabla principal)
        r = fit_acotada(np.tan(np.radians(ph)), cov, s0); r["phi"] = ph; r["ext"] = True; res.append(r)
        s0 = (r["beta"], r["psi"], r["z0"])
        log(f"{nombre} (ext.) φ′∞ = {ph:4.1f}°: ML {r['ll']:.3f}  ζ0 {r['z0']:.3f}")
    res_ext = res; res = [r for r in res if not r.get("ext")]
    best = max(res, key=lambda r: r["ll"])
    # re-arranque del mejor φ desde el valor por defecto (control de óptimos locales)
    r2 = fit_acotada(best["T"], cov, (BETA0, PSI0, 0.30))
    log(f"{nombre} control de arranque en φ′∞ = {best['phi']}: ML {r2['ll']:.3f} (vs {best['ll']:.3f})")
    if r2["ll"] > best["ll"] + 1e-6:
        r2["phi"] = best["phi"]; res_ext[[r["phi"] for r in res_ext].index(best["phi"])] = r2; best = r2
    best = dict(best); best["k"] = 7 + 1 + 1 + 8
    return best, res_ext


# ---------------------------------------------------------------- Laplace (FOCE) para el modelo no lineal
def eta_zeta(beta, z0):
    return dum @ beta[:3] + beta[3] * e + beta[4] * lD, z0 + beta[5] * dum[:, 1] + beta[6] * dum[:, 2]


UCACHE = {}


def laplace(beta, psi, T, z0, aditivo=False, por_bloque=False, cache_key="m"):
    """log p(y) ≈ log p(y|û) + log p(û) + (q/2) log 2π − ½ log|H|,  H = JᵤᵀR⁻¹Jᵤ + Ω⁻¹."""
    Gp, Gs, a = unpack(psi)
    try:
        Gpi = np.linalg.inv(Gp); Gsi = np.linalg.inv(Gs)
        ldGp = np.linalg.slogdet(Gp)[1]; ldGs = np.linalg.slogdet(Gs)[1]
    except np.linalg.LinAlgError:
        return -1e12
    if not (np.isfinite(ldGp) and np.isfinite(ldGs)):
        return -1e12
    eta0, zeta0 = eta_zeta(beta, z0); f0 = fb(beta, T, z0)[0] if aditivo else None
    s2all = np.exp(2 * (a[0] + a[1] * x)); out = []
    for ib, b in enumerate(B):
        ip, cod, ns = b["ip"], b["cod"], b["ns"]; m = len(ip); q = 2 + 2 * ns; xb = x[ip]; s2 = s2all[ip]; yb = y[ip]
        Oi = np.zeros((q, q)); Oi[:2, :2] = Gpi
        for s in range(ns):
            Oi[2 + 2 * s:4 + 2 * s, 2 + 2 * s:4 + 2 * s] = Gsi
        ldO = ldGp + ns * ldGs

        def cond(u):
            ue = u[0] + u[2 + 2 * cod]; uz = u[1] + u[3 + 2 * cod]
            if aditivo:
                return f0[ip] + ue + uz * xb, np.ones(m), xb
            E = np.exp(eta0[ip] + ue); qq = np.exp(-(zeta0[ip] + uz) * xb)
            g = T + (E - T) * qq
            if np.any(g <= 1e-12):
                return None, None, None
            return xb + np.log(g), E * qq / g, -xb * (E - T) * qq / g

        def obj(u):
            fu, _, _ = cond(u)
            if fu is None:
                return np.inf
            return 0.5 * np.sum((yb - fu) ** 2 / s2) + 0.5 * u @ Oi @ u

        u = UCACHE.get((cache_key, ib), np.zeros(q)).copy()
        if obj(u) == np.inf:
            u = np.zeros(q)
        o = obj(u); rows = np.arange(m)
        for _ in range(200):
            fu, w, dz = cond(u)
            Jf = np.zeros((m, q)); Jf[:, 0] = w; Jf[:, 1] = dz; Jf[rows, 2 + 2 * cod] = w; Jf[rows, 3 + 2 * cod] = dz
            H = Jf.T @ (Jf / s2[:, None]) + Oi; g = Jf.T @ ((yb - fu) / s2) - Oi @ u
            step = np.linalg.solve(H, g); t = 1.0
            while t > 1e-10:
                on = obj(u + t * step)
                if on <= o + 1e-14:
                    break
                t *= 0.5
            u = u + t * step; dif = o - on; o = on
            if np.max(np.abs(t * step)) < 1e-11 or dif < 1e-15:
                break
        UCACHE[(cache_key, ib)] = u
        fu, w, dz = cond(u)
        Jf = np.zeros((m, q)); Jf[:, 0] = w; Jf[:, 1] = dz; Jf[rows, 2 + 2 * cod] = w; Jf[rows, 3 + 2 * cod] = dz
        H = Jf.T @ (Jf / s2[:, None]) + Oi
        lly = float(np.sum(-0.5 * (yb - fu) ** 2 / s2 - 0.5 * np.log(2 * np.pi * s2)))
        out.append(lly - 0.5 * u @ Oi @ u - 0.5 * ldO - 0.5 * np.linalg.slogdet(H)[1])
    return np.array(out) if por_bloque else float(np.sum(out))


# ---------------------------------------------------------------- fuera de muestra: dejar fuera una publicación
def lopo(mod, tipo):
    """ψ (y φ′∞, ζ0) fijos del ajuste completo; efectos fijos reajustados sin la publicación; log N(y_pub | f, V_pub + J C Jᵀ)."""
    psi = mod["psi"]; Gp, Gs, a = unpack(psi); out = []
    for k, b in enumerate(B):
        tr = [bb for j, bb in enumerate(B) if j != k]; ip = b["ip"]
        if tipo == "lineal":
            beta, C, _ = gls(mod["X"], mod["Z"], psi, tr)
            f = mod["X"] @ beta; J = mod["X"]; Z = mod["Z"]
        else:
            beta, C = gn(mod["beta"], psi, mod["T"], mod["z0"], tipo, tr)
            f, J, Zd = fb(beta, mod["T"], mod["z0"]); Z = Zd if tipo == "dec" else ZADD
        V = Vb(b, Z, Gp, Gs, a) + J[ip] @ C @ J[ip].T
        L = np.linalg.cholesky(V); z = solve_triangular(L, y[ip] - f[ip], lower=True)
        out.append(float(-0.5 * z @ z - np.log(np.diag(L)).sum() - 0.5 * len(ip) * LOG2PI))
    return np.array(out)


def sdpsi(psi):
    Gp, Gs, a = unpack(psi)
    f = lambda G: [float(np.sqrt(G[0, 0])), float(np.sqrt(G[1, 1])), float(G[0, 1] / np.sqrt(G[0, 0] * G[1, 1]))]
    return dict(pub=f(Gp), set=f(Gs), a=[float(a[0]), float(a[1])])


if __name__ == "__main__":
    R = dict(n=n, n_pub=len(B), n_set=int(d.Set.nunique()), phis=PHIS)
    log(f"datos: {n} ensayos, {len(B)} publicaciones, {R['n_set']} sets (sin censura ni truncamiento)")

    # verificación: ll_exact (Z de FO) = ModeloR6.ll_obs sin censura ni truncamiento
    Tc = np.tan(np.radians(25.0)); bc = BETA0.copy(); bc[5:] = [0.02, -0.03]
    mr = ModeloR6(d, Tc, 0.3, bc, trunc=False, cens=False)
    chk = (ll_b(bc, PSI0, Tc, 0.3, "dec"), mr.ll_obs(PSI0, bc))
    log(f"verificación ll FO propia vs ModeloR6.ll_obs: {chk[0]:.6f} vs {chk[1]:.6f}")
    R["verif_ll_vs_r6"] = list(chk)

    # ---- M1 y M2
    M1, P1 = perfil("dec", "M1"); M2, P2 = perfil("add", "M2")
    R["perfil_M1"] = [dict(phi=r["phi"], ll=r["ll"], z0=r["z0"], ext=bool(r.get("ext"))) for r in P1]
    R["perfil_M2"] = [dict(phi=r["phi"], ll=r["ll"], z0=r["z0"], ext=bool(r.get("ext"))) for r in P2]
    R["optimo_con_extension"] = {k: dict(phi=max(P, key=lambda r: r["ll"])["phi"], ll=max(r["ll"] for r in P)) for k, P in (("M1", P1), ("M2", P2))}

    # ---- M3, M3b, M4, M4b
    ZD1 = fb(M1["beta"], M1["T"], M1["z0"])[2]
    M3 = fit_lineal(X_Q, ZADD, "M3 cuadrática, Z=[1,x]")
    M3b = fit_lineal(X_QB, ZADD, "M3b cuadrática por clase, Z=[1,x]")
    M4 = fit_lineal(X_Q, ZD1, "M4 cuadrática, Z de M1")
    M4b = fit_lineal(X_QB, ZD1, "M4b cuadrática por clase, Z de M1")
    MOD = dict(M1=M1, M2=M2, M3=M3, M3b=M3b, M4=M4, M4b=M4b)

    # verificación de Laplace: con efectos aditivos (lineales en u) debe coincidir con la ll exacta de M2
    lap_add = laplace(M2["beta"], M2["psi"], M2["T"], M2["z0"], aditivo=True, cache_key="add")
    log(f"verificación Laplace (efectos aditivos) vs exacta M2: {lap_add:.6f} vs {M2['ll']:.6f}")
    R["verif_laplace_aditivo"] = [lap_add, M2["ll"]]

    # ---- M5: Laplace en los parámetros de M1, por φ′∞
    lap_phi = []
    for r in P1:
        lp = laplace(r["beta"], r["psi"], r["T"], r["z0"], cache_key=f"phi{r['phi']}")
        lap_phi.append(dict(phi=r["phi"], ll_fo=r["ll"], ll_laplace=lp, fo_menos_laplace=r["ll"] - lp))
        log(f"Laplace en óptimo FO φ′∞ = {r['phi']}: FO {r['ll']:.3f}  Laplace {lp:.3f}  FO−Lap {r['ll'] - lp:+.3f}")
    R["laplace_en_FO"] = lap_phi
    lap1_bl = laplace(M1["beta"], M1["psi"], M1["T"], M1["z0"], por_bloque=True, cache_key="m")

    # ---- M5 reoptimizado (β, ψ, ζ0) con Laplace, perfil en φ′∞ (arranque: óptimo FO de cada φ′∞; tope de tiempo global)
    t_glob = time.time()

    class Tope(Exception):
        pass

    def reopt_laplace(r):
        t_ini = time.time(); estado = dict(best=-np.inf, th=None, nfev=0); key = f"opt{r['phi']}"

        def nlap(th):
            estado["nfev"] += 1
            v = laplace(th[:7], th[7:15], r["T"], th[15], cache_key=key)
            if v > estado["best"]:
                estado["best"], estado["th"] = v, th.copy()
            if time.time() - t_glob > LAPLACE_MAX_S:
                raise Tope()
            return -v
        completo = True; th = np.r_[r["beta"], r["psi"], r["z0"]]
        try:
            for _ in range(2):                                  # reinicio de L-BFGS-B
                rr = minimize(nlap, th, method="L-BFGS-B", bounds=[(None, None)] * 15 + [(0.01, 3.0)],
                              options=dict(maxiter=500, ftol=1e-13, gtol=1e-7))
                th = estado["th"]; completo = bool(rr.success)
        except Tope:
            completo = False
        th = estado["th"]
        out = dict(ll=float(estado["best"]), beta=th[:7], psi=th[7:15], z0=float(th[15]), T=r["T"], phi=r["phi"], k=17,
                   convergido=completo, nfev=estado["nfev"], seg=time.time() - t_ini, ext=bool(r.get("ext")))
        out["ll_FO_en_params_Laplace"] = ll_b(out["beta"], out["psi"], out["T"], out["z0"], "dec")
        log(f"M5 Laplace reoptimizado φ′∞ = {r['phi']}: {out['ll']:.3f} (FO opt {r['ll']:.3f}; convergió {completo}, "
            f"{out['nfev']} evals, {out['seg']:.0f} s); ζ0 {out['z0']:.3f}; FO en esos parámetros {out['ll_FO_en_params_Laplace']:.3f}")
        return out
    P5 = []
    for r in sorted(P1, key=lambda r: abs(r["phi"] - M1["phi"])):          # del óptimo FO hacia afuera
        if time.time() - t_glob > LAPLACE_MAX_S:
            log(f"tope de tiempo: Laplace no reoptimizado en φ′∞ = {r['phi']}"); continue
        P5.append(reopt_laplace(r))
    P5.sort(key=lambda r: r["phi"])
    R["perfil_M5_laplace"] = [dict(phi=r["phi"], ll=r["ll"], z0=r["z0"], convergido=r["convergido"], ext=r["ext"],
                                   ll_FO_mismos_params=r["ll_FO_en_params_Laplace"]) for r in P5]
    M5 = max([r for r in P5 if not r["ext"]], key=lambda r: r["ll"])
    M5ext = max(P5, key=lambda r: r["ll"])
    log(f"M5 (grilla del encargo): φ′∞ = {M5['phi']}, ll {M5['ll']:.3f}; con extensión: φ′∞ = {M5ext['phi']}, ll {M5ext['ll']:.3f}")

    # ---- tabla 2×2 y descomposición
    t22 = {"acotada|decreciente": "M1", "acotada|aditiva": "M2", "cuadratica|decreciente": "M4", "cuadratica|aditiva": "M3",
           "cuadratica_clase|decreciente": "M4b", "cuadratica_clase|aditiva": "M3b"}
    R["modelos"] = {}
    for k, m in MOD.items():
        R["modelos"][k] = dict(ll=m["ll"], k=m["k"], AIC=-2 * m["ll"] + 2 * m["k"], var=sdpsi(m["psi"]),
                               beta=[float(v) for v in m["beta"]], phi=m.get("phi"), z0=m.get("z0"))
    R["modelos"]["M5_laplace"] = dict(ll=M5["ll"], k=17, phi=M5["phi"], convergido=M5["convergido"], nfev=M5["nfev"], seg=M5["seg"], z0=M5["z0"],
                                      beta=[float(v) for v in M5["beta"]], var=sdpsi(M5["psi"]), ll_FO_mismos_params=M5["ll_FO_en_params_Laplace"])
    R["tabla_2x2"] = {c: dict(modelo=m, ll=MOD[m]["ll"], k=MOD[m]["k"]) for c, m in t22.items()}
    L = {k: m["ll"] for k, m in MOD.items()}
    R["descomposicion"] = dict(
        total_M1_M3=L["M1"] - L["M3"], total_M1_M3b=L["M1"] - L["M3b"],
        media_con_cov_decreciente_M1_M4=L["M1"] - L["M4"], media_con_cov_aditiva_M2_M3=L["M2"] - L["M3"],
        cov_con_media_acotada_M1_M2=L["M1"] - L["M2"], cov_con_media_cuadratica_M4_M3=L["M4"] - L["M3"],
        media_clase_cov_decr_M1_M4b=L["M1"] - L["M4b"], media_clase_cov_adit_M2_M3b=L["M2"] - L["M3b"],
        cov_con_media_cuad_clase_M4b_M3b=L["M4b"] - L["M3b"],
        aproximacion_FO_menos_Laplace_en_M1=M1["ll"] - laplace(M1["beta"], M1["psi"], M1["T"], M1["z0"], cache_key="m"),
        aproximacion_FO_opt_menos_Laplace_opt=M1["ll"] - M5["ll"], laplace_opt_menos_M3=M5["ll"] - L["M3"],
        laplace_opt_menos_M4=M5["ll"] - L["M4"], laplace_opt_menos_M2=M5["ll"] - L["M2"],
        laplace_opt_menos_M3b=M5["ll"] - L["M3b"], laplace_opt_menos_M4b=M5["ll"] - L["M4b"],
        ext_laplace_opt_menos_M2ext=M5ext["ll"] - R["optimo_con_extension"]["M2"]["ll"])
    for k, v in R["descomposicion"].items():
        log(f"  {k:42s} {v:+8.3f}")

    # ---- contribución por publicación (en muestra)
    pb = {"M1": ll_b(M1["beta"], M1["psi"], M1["T"], M1["z0"], "dec", True), "M2": ll_b(M2["beta"], M2["psi"], M2["T"], M2["z0"], "add", True)}
    for k in ("M3", "M3b", "M4", "M4b"):
        m = MOD[k]; pb[k] = ll_exact(m["X"] @ m["beta"], m["Z"], m["psi"], True)
    pb["M1_laplace"] = lap1_bl
    pb["M5"] = laplace(M5["beta"], M5["psi"], M5["T"], M5["z0"], por_bloque=True, cache_key=f"opt{M5['phi']}")

    def contrib(a, b):
        dlt = pb[a] - pb[b]; o = np.argsort(-dlt); tot = dlt.sum()
        return dict(total=float(tot), por_pub={B[i]["pub"]: float(dlt[i]) for i in o},
                    n_ensayos={B[i]["pub"]: int(len(B[i]["ip"])) for i in o},
                    top3_suma=float(dlt[o[:3]].sum()), sin_top1=float(tot - dlt[o[0]]), sin_top3=float(tot - dlt[o[:3]].sum()),
                    n_pub_positivas=int((dlt > 0).sum()), n_pub_mayor_1=int((dlt > 1).sum()), n_pub_menor_m1=int((dlt < -1).sum()))
    R["por_publicacion"] = {f"{a}-{b}": contrib(a, b) for a, b in (("M1", "M3"), ("M1", "M4"), ("M4", "M3"), ("M2", "M3"), ("M1", "M2"), ("M1", "M3b"),
                                                                       ("M5", "M3"), ("M5", "M2"), ("M1", "M5"), ("M5", "M3b"))}
    for kk in ("M1-M3", "M1-M4", "M4-M3", "M5-M3", "M5-M2", "M1-M5"):
        c = R["por_publicacion"][kk]; top = list(c["por_pub"].items())[:4]
        log(f"ΔLL {kk}: total {c['total']:+.2f}, top-3 {c['top3_suma']:+.2f}, sin top-3 {c['sin_top3']:+.2f}; "
            f"pubs >0: {c['n_pub_positivas']}/36; mayores: {[(p, round(v, 2)) for p, v in top]}")

    # ---- log score fuera de muestra (LOPO, ψ fija)
    ls = {"M1": lopo(M1, "dec"), "M2": lopo(M2, "add")}
    for k in ("M3", "M3b", "M4", "M4b"):
        ls[k] = lopo(MOD[k], "lineal")
    R["lopo"] = dict(total={k: float(v.sum()) for k, v in ls.items()},
                     por_pub={k: {B[i]["pub"]: float(v[i]) for i in range(len(B))} for k, v in ls.items()})
    dif = {}
    for a_, b_ in (("M1", "M3"), ("M1", "M4"), ("M4", "M3"), ("M2", "M3"), ("M1", "M2"), ("M1", "M3b"), ("M4b", "M3b")):
        dd_ = ls[a_] - ls[b_]; o = np.argsort(-dd_)
        dif[f"{a_}-{b_}"] = dict(total=float(dd_.sum()), ee_total=float(dd_.std(ddof=1) * np.sqrt(len(dd_))),
                                 top3=[(B[i]["pub"], float(dd_[i])) for i in o[:3]], sin_top3=float(dd_.sum() - dd_[o[:3]].sum()),
                                 n_pub_positivas=int((dd_ > 0).sum()))
        log(f"LOPO {a_}-{b_}: {dd_.sum():+.2f} (ee {dif[f'{a_}-{b_}']['ee_total']:.2f}), sin top-3 {dif[f'{a_}-{b_}']['sin_top3']:+.2f}")
    R["lopo"]["diferencias"] = dif
    log("LOPO totales: " + ", ".join(f"{k} {v:.2f}" for k, v in R["lopo"]["total"].items()))

    R["seg_total"] = time.time() - T0
    json.dump(R, open(AQ / "lepsp_e1_estructura.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False,
              default=lambda o: o.tolist() if isinstance(o, np.ndarray) else float(o))
    log("listo → lepsp_e1_estructura.json")
