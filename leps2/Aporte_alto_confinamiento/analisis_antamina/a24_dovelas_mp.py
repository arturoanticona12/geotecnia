"""Datos completos de las dovelas de la superficie crítica de Slide2 (2026-10-11). El .s01 estándar de Slide2 guarda la geometría
de las dovelas de la superficie mínima, el par (λ, FS) de Morgenstern–Price y los totales (área, momentos y fuerzas), pero no
las fuerzas de cada dovela. Este script resuelve Morgenstern–Price (GLE, función media onda seno) sobre esas mismas dovelas, con
la geometría, los materiales, el agua y la función τ–σ′n del modelo (.yaml), y obtiene por dovela: peso, presión de poros,
fuerza normal efectiva N′, σ′n = N′/l, τ disponible y movilizado, y fuerzas entre dovelas E y X.
Validación: el FS, la λ y el área total deben reproducir los de Slide2 (se imprime la diferencia de cada caso).
Convenciones: el talud mira a −x (falla de derecha a izquierda); base con pendiente α = atan(dyb/dx) > 0 subiendo hacia la cresta;
E positivo en compresión; X = λ f(x) E; momentos respecto del centro (xc, yc) de la superficie de Slide2."""
import sys, json, math
from pathlib import Path
import numpy as np, yaml
from shapely.geometry import Polygon, LineString
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "slide2" / "scripts")); import resultados as R  # noqa: E402
AQ = Path(__file__).parent; S2 = AQ.parent / "slide2"; BASE = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados")
MET = "gle/morgenstern-price"; GW = 9.81
HU1 = "--hu-cos2" not in sys.argv     # Hu = 1: reproduce a Slide2 («hu: auto») en ladera (ΔFS ≤ 0.0007); con cos²β del NF, 0.002–0.006
LOTES = [("88-profundas-720", "profundas"), ("89-profundas-roca", "profundas_roca"), ("90-profundas-entradas", "profundas_entradas"),
         ("91-profundas-largas", "profundas_entradas_largas")]


def leer_s01(p):
    L = p.read_text(encoding="latin-1").splitlines()
    k = next(i for i, l in enumerate(L) if l.startswith("* minimum slice info") and l.endswith(MET))
    D = []
    for l in L[k + 1:]:
        if l.startswith("*"):
            break
        v = l.split()
        if len(v) >= 5:
            D.append([float(a) for a in v[:5]])
    k = next(i for i, l in enumerate(L) if l.startswith("* Global Minimum FS"))
    v = L[k + 1].split(); xc, yc, fs = float(v[0]), float(v[1]), float(v[7])
    k = next(i for i, l in enumerate(L) if l.startswith("Force Lambda Data") and l.endswith(MET))
    n = int(L[k + 1]); lam = [tuple(map(float, L[k + 2 + j].split())) for j in range(n)]
    k = next(i for i, l in enumerate(L) if l.startswith("Moment Lambda Data") and l.endswith(MET))
    lamm = [tuple(map(float, L[k + 2 + j].split())) for j in range(n)]
    k = next(i for i, l in enumerate(L) if l.startswith("* Global Minimum Text"))
    txt = {a.split("=")[0]: float(a.split("=")[1].split()[0]) for a in L[k + 2:k + 2 + int(L[k + 1])]}
    return np.array(D), xc, yc, fs, lam, lamm, txt


def resolver(D, desc, grupo, xc, yc, lam_s01):
    mats = {m["nombre"]: m for m in desc["materiales"]}; fun = {k: np.array(v) for k, v in desc.get("funciones", {}).items()}
    regs = [(Polygon(r["poligono"]), mats[r["material"]]) for r in grupo["geometria"]["regiones"]]
    agua = grupo.get("agua"); wt = LineString(agua["nivel_freatico"]) if agua else None
    def ywt(x):                                                     # cota del nivel freático y su pendiente en x
        if wt is None:
            return None, 0.0
        P = np.array(wt.coords)
        if x <= P[0, 0] or x >= P[-1, 0]:
            return None, 0.0
        i = np.searchsorted(P[:, 0], x) - 1; (x0, y0), (x1, y1) = P[i], P[i + 1]
        return y0 + (y1 - y0) * (x - x0) / (x1 - x0), math.atan2(y1 - y0, x1 - x0)
    def tau(m, sn):                                                 # kPa
        if m["modelo"] == "funcion":
            F = fun[m["funcion"]]; return float(np.interp(sn, F[:, 0], F[:, 1], right=F[-1, 1] + (sn - F[-1, 0]) * (F[-1, 1] - F[-2, 1]) / (F[-1, 0] - F[-2, 0])))
        return m.get("c", 0) + max(sn, 0) * math.tan(math.radians(m["phi"]))
    xb, yb = D[:, 0], D[:, 3]; n = len(xb) - 1
    W = np.zeros(n); xg = np.zeros(n); U = np.zeros(n); area = 0.0; matb = []
    for i in range(n):
        col = Polygon([(xb[i], yb[i]), (xb[i + 1], yb[i + 1]), (xb[i + 1], 1e4), (xb[i], 1e4)])
        xm = 0.5 * (xb[i] + xb[i + 1]); ym = 0.5 * (yb[i] + yb[i + 1]); yw, bw = ywt(xm)
        mom = 0.0
        for pg, m in regs:
            it = col.intersection(pg)
            if it.is_empty or it.area < 1e-9:
                continue
            g = m["gamma"]
            if yw is not None and m.get("agua") == "nf" and "gamma_sat" in m:       # γ saturado bajo el nivel freático
                below = it.intersection(Polygon([(xb[i], -1e4), (xb[i + 1], -1e4), (xb[i + 1], yw), (xb[i], yw)]))
                w = g * it.area + (m["gamma_sat"] - g) * below.area
                mom += g * it.area * it.centroid.x + (m["gamma_sat"] - g) * below.area * (below.centroid.x if below.area > 0 else 0)
            else:
                w = g * it.area; mom += w * it.centroid.x
            W[i] += w; area += it.area
        xg[i] = mom / W[i] if W[i] > 0 else xm
        # material de la base: el de la región que contiene un punto 1 cm sobre el centro de la base
        from shapely.geometry import Point
        mb = next(m for pg, m in regs if pg.buffer(1e-9).contains(Point(xm, ym + 0.01)))
        matb.append(mb)
        U[i] = GW * max(yw - ym, 0) * (1.0 if HU1 else math.cos(bw) ** 2) if (yw is not None and mb.get("agua") == "nf") else 0.0   # Hu automático
    dx = np.diff(xb); al = np.arctan2(np.diff(yb), dx); l = dx / np.cos(al); xm = 0.5 * (xb[1:] + xb[:-1]); ym = 0.5 * (yb[1:] + yb[:-1])
    ub = U * l                                                      # fuerza de poros en la base
    f = np.sin(np.pi * (xb - xb[0]) / (xb[-1] - xb[0]))            # media onda seno en los bordes
    def ciclo(lmb, F, X):
        """N′ de cada dovela con X dado (equilibrio vertical, resistencia no lineal) y E por equilibrio horizontal."""
        Np = np.zeros(n); T = np.zeros(n)
        for i in range(n):
            rhs = W[i] - (X[i] - X[i + 1]) - ub[i] * math.cos(al[i])   # X[i] cara izquierda (hacia arriba), X[i+1] derecha (hacia abajo)
            g = lambda N: N * math.cos(al[i]) + tau(matb[i], N / l[i]) * l[i] / F * math.sin(al[i]) - rhs
            a, b = 0.0, max(rhs / max(math.cos(al[i]), 0.05), 1.0) * 2 + 1
            if g(a) > 0:
                Np[i] = 0.0
            else:
                while g(b) < 0:
                    b *= 2
                for _ in range(60):
                    c = 0.5 * (a + b); a, b = (c, b) if g(c) < 0 else (a, c)
                Np[i] = 0.5 * (a + b)
            T[i] = tau(matb[i], Np[i] / l[i]) * l[i]
        Ntot = Np + ub
        E = np.zeros(n + 1)
        for i in range(n):
            E[i + 1] = E[i] - Ntot[i] * math.sin(al[i]) + T[i] / F * math.cos(al[i])
        return Np, T, E
    def momento(Np, T):
        Ntot = Np + ub
        rN = (xm - xc) * (Ntot * np.cos(al)) - (ym - yc) * (-Ntot * np.sin(al))
        rS = (xm - xc) * (T * np.sin(al)) - (ym - yc) * (T * np.cos(al))
        Mw = ((xg - xc) * (-W)).sum()
        return -rS.sum() / (Mw + rN.sum()), Mw                      # Σ M(W) + Σ M(N) + Σ M(T)/F = 0
    def iterar(lmb, cual, F0=1.5):
        """GLE: cada factor se itera con su propio F en la expresión de N (Fredlund y Krahn 1977)."""
        F, X = F0, np.zeros(n + 1)
        for _ in range(300):
            Np, T, E = ciclo(lmb, F, X)
            Ff = (T * np.cos(al)).sum() / ((Np + ub) * np.sin(al)).sum()
            Fm, Mw = momento(Np, T)
            Fn = Ff if cual == "f" else Fm
            Xn = lmb * f * E; Xn[0] = Xn[-1] = 0.0
            if abs(Fn - F) < 1e-7 and np.abs(Xn - X).max() < 1e-3:
                F = Fn; break
            F, X = Fn, 0.5 * X + 0.5 * Xn
        return F, Np, T, E, X, Mw
    def factores(lmb):
        a = iterar(lmb, "f"); b = iterar(lmb, "m", a[0])
        return a[0], b[0], a[1], a[2], a[3], a[4], a[5], None
    # λ en que Ff = Fm (secante sobre λ, partiendo de la λ de Slide2 para acelerar)
    l0, l1 = 0.0, max(lam_s01, 0.1)
    d0 = (lambda r: r[0] - r[1])(factores(l0)); d1 = (lambda r: r[0] - r[1])(factores(l1))
    for _ in range(30):
        if abs(d1 - d0) < 1e-12:
            break
        l2 = l1 - d1 * (l1 - l0) / (d1 - d0); l0, d0 = l1, d1; l1 = l2; d1 = (lambda r: r[0] - r[1])(factores(l1))
        if abs(d1) < 1e-6:
            break
    Ff, Fm, Np, T, E, X, Mw, MS = factores(l1)
    r0 = factores(0.0)
    return dict(lam=l1, Ff=Ff, Fm=Fm, Ff0=r0[0], Fm0=r0[1], area=area, xm=xm, ym=ym, al=al, l=l, W=W, U=U, Np=Np, T=T, E=E, X=X,
                mat=[m["nombre"] for m in matb], sn=Np / l / 1000, tau_disp=T / l / 1000, tau_mov=T / l / 1000 / Ff, Mw=Mw)


out = {}
for lote, carp in LOTES:
    RES = BASE / lote
    for caso in sorted(c for c in RES.iterdir() if c.is_dir()):
        y = S2 / carp / f"{caso.name}.yaml"
        y = y if y.exists() else next((S2 / carp).glob("*.yaml"))
        desc = yaml.safe_load(open(y, encoding="utf-8")); grupo = desc["grupos"][0]
        nom = R.escenarios(next(caso.rglob("*.slmd")))
        for s01 in sorted(caso.rglob("*.s01")):
            nm = nom.get(s01.stem, "").split("/")[-1].strip()
            if not nm:
                continue
            D, xc, yc, fs, lam, lamm, txt = leer_s01(s01)
            r = resolver(D, desc, grupo, xc, yc, lam[-2][0])
            d = r["mat"]; ds = np.array([m == "Desmonte ROM" for m in d]); ld = r["l"][ds].sum()
            k = f"{grupo['nombre']}|{nm}"
            out[k] = dict(fs_slide2=fs, lam_slide2=lam[-2][0], fs=r["Ff"], fm=r["Fm"], lam=r["lam"], ff0=r["Ff0"], fm0=r["Fm0"],
                          ff0_slide2=lam[0][1], fm0_slide2=lamm[0][1], area=r["area"], area_slide2=txt.get("Total Slice Area"),
                          sn_max_desmonte=float(r["sn"][ds].max()) if ds.any() else 0.0,
                          sn_media_desmonte=float((r["sn"][ds] * r["l"][ds]).sum() / ld) if ld else 0.0,
                          frac_desmonte_sobre=[float(r["l"][ds & (r["sn"] > s)].sum() / ld) if ld else 0.0 for s in (4.60, 7.86)],
                          dovelas={c: [round(float(v), 4) for v in r[c]] for c in ("xm", "ym", "al", "l", "W", "U", "Np", "T", "sn", "tau_disp", "tau_mov")}
                          | dict(E=[round(float(v), 1) for v in r["E"]], X=[round(float(v), 1) for v in r["X"]], mat=d))
            o = out[k]; o["superficie"] = dict(x=[round(float(v), 1) for v in D[:, 0]], yb=[round(float(v), 1) for v in D[:, 3]])
            o["prof"] = float((D[:, 2] - D[:, 3]).max())
            o["frac_long"] = {m: float(r["l"][np.array(d) == m].sum() / r["l"].sum()) for m in ("Desmonte ROM", "Morrena", "Roca")}
            print(f"{k:42s} FS Slide2 {fs:.4f} propio {o['fs']:.4f}/{o['fm']:.4f} | λ {o['lam_slide2']:.3f}/{o['lam']:.3f} | λ=0: Ff {o['ff0_slide2']:.4f}/{o['ff0']:.4f} "
                  f"Fm {o['fm0_slide2']:.4f}/{o['fm0']:.4f} | área {o['area_slide2']:.0f}/{o['area']:.0f} | σ′n desmonte máx {o['sn_max_desmonte']:.2f} MPa")
if HU1:
    json.dump(out, open(AQ / "a24_dovelas_mp.json", "w", encoding="utf-8"), ensure_ascii=False)
