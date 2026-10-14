"""Bishop simplificado con envolvente no lineal: botadero genérico de 700 m (ilustrativo)."""
import sys, numpy as np, json
sys.stdout.reconfigure(encoding="utf-8")
PA = 0.1013
GW = 9.81e-3  # MN/m3
GAM = 21e-3   # MN/m3


def env_leps(phi1, m=0.9):
    t1 = np.tan(np.radians(phi1)); k = (10 * PA) ** (1 - m)
    tau = lambda s: t1 * k * np.maximum(s, 1e-6) ** m
    dtau = lambda s: t1 * k * m * np.maximum(s, 1e-6) ** (m - 1)
    return tau, dtau


def env_corr(phi1, a=3.72, phi_floor=None):
    """Leps 2.0 (m=0.9) con caída adicional de φ'1 = a·log10(σn/10pa) para σn>10pa; piso opcional de φs."""
    def tau(s):
        s = np.maximum(s, 1e-6)
        ph = phi1 - a * np.maximum(np.log10(s / (10 * PA)), 0)
        t = np.tan(np.radians(ph)) * (10 * PA) ** 0.1 * s ** 0.9
        if phi_floor is not None:
            t = np.maximum(t, s * np.tan(np.radians(phi_floor)))
        return t
    dtau = lambda s: (tau(s * 1.001) - tau(s * 0.999)) / (0.002 * np.maximum(s, 1e-6))
    return tau, dtau


ROCK = (lambda s: 1.0 + s * np.tan(np.radians(45)), lambda s: np.tan(np.radians(45)) + 0 * s)


def ground(x, H, beta):
    L = H / np.tan(np.radians(beta))
    return np.clip(x * np.tan(np.radians(beta)), 0, H)


def bishop(xc, yc, R, H, beta, env, hw=0.0, ru_ex=0.0, nsl=120):
    # intersections of lower arc with ground: sample
    xs = np.linspace(xc - R + 1e-6, xc + R - 1e-6, 4000)
    yarc = yc - np.sqrt(R ** 2 - (xs - xc) ** 2)
    inside = yarc < ground(xs, H, beta) - 1e-6
    if inside.sum() < 10:
        return None
    idx = np.where(inside)[0]
    x0, x1 = xs[idx[0]], xs[idx[-1]]
    if x1 - x0 < 20:
        return None
    xb = np.linspace(x0, x1, nsl + 1); xm = 0.5 * (xb[1:] + xb[:-1]); b = np.diff(xb)
    yb = yc - np.sqrt(R ** 2 - (xm - xc) ** 2)
    yt = ground(xm, H, beta)
    h = np.maximum(yt - yb, 0)
    W = GAM * h * b
    alpha = np.arcsin((xm - xc) / R)  # positive where base rises toward +x? base slope dy/dx = (x-xc)/sqrt(...)
    # slope sliding toward -x (toe at x=0, crest at +x): driving = W sin(alpha) with alpha = atan(dy/dx)
    alpha = np.arctan((xm - xc) / np.sqrt(R ** 2 - (xm - xc) ** 2))
    sv = GAM * h
    hwx = np.minimum(hw, yt)
    u = GW * np.maximum(hwx - yb, 0) + ru_ex * sv * (yb < hwx)
    inrock = yb < 0
    l = b / np.cos(alpha)
    sn = np.maximum(sv * np.cos(alpha) ** 2 - u, 1e-3)
    F = 1.5
    for _ in range(200):
        tau_f = np.where(inrock, ROCK[0](sn), env[0](sn)); tphi = np.where(inrock, ROCK[1](sn), env[1](sn))
        ct = tau_f - sn * tphi
        drive = np.sum(W * np.sin(alpha))
        if drive <= 0:
            return None
        ma = np.cos(alpha) * (1 + np.tan(alpha) * tphi / F)
        ma = np.maximum(ma, 0.2)
        Fn = np.sum((ct * b + (W - u * b) * tphi) / ma) / drive
        Np = (W - u * b - ct * b * np.tan(alpha) / Fn) / ma
        sn_new = np.maximum(Np / l, 1e-3)
        if abs(Fn - F) < 1e-5 and np.max(np.abs(sn_new - sn) / (sn + 0.01)) < 1e-3:
            F = Fn; sn = sn_new; break
        F = Fn; sn = 0.5 * sn + 0.5 * sn_new
    return dict(F=F, sn=sn, l=l, xm=xm, yb=yb, tau=np.where(inrock, ROCK[0](sn), env[0](sn)), x0=x0, x1=x1)


def search(H, beta, env, hw=0.0, ru_ex=0.0, ngrid=22):
    L = H / np.tan(np.radians(beta))
    best = None
    for xc in np.linspace(-0.2 * L, 1.0 * L, ngrid):
        for yc in np.linspace(0.6 * H, 3.5 * H, ngrid):
            # radius such that circle exits near toe region: pass through points on/near toe
            for xe in [-0.15 * L, -0.05 * L, 0.0, 0.1 * L, 0.25 * L]:
                ye = ground(np.array([xe]), H, beta)[0]
                R = np.hypot(xc - xe, yc - ye)
                if yc - R < -0.15 * H:  # limit penetration into foundation
                    continue
                r = bishop(xc, yc, R, H, beta, env, hw, ru_ex)
                if r is None:
                    continue
                if (r["x1"] - r["x0"]) < 0.3 * L:  # interés en mecanismos globales
                    continue
                if best is None or r["F"] < best["F"]:
                    best = dict(r, xc=xc, yc=yc, R=R)
    # local refinement
    for it in range(3):
        d = 0.04 * L / (it + 1)
        cand = []
        for dx in [-d, 0, d]:
            for dy in [-d, 0, d]:
                for dR in [-d, 0, d]:
                    xc, yc, R = best["xc"] + dx, best["yc"] + dy, best["R"] + dR
                    if yc - R < -0.15 * H:
                        continue
                    r = bishop(xc, yc, R, H, beta, env, hw, ru_ex)
                    if r is None or (r["x1"] - r["x0"]) < 0.3 * L:
                        continue
                    if r["F"] < best["F"]:
                        best = dict(r, xc=xc, yc=yc, R=R)
    return best


if __name__ == "__main__":
    # verificación: Mohr-Coulomb lineal c=0, seco -> FS ≈ tanφ/tanβ (superficies someras)
    lin = (lambda s: s * np.tan(np.radians(38)), lambda s: np.tan(np.radians(38)) + 0 * s)
    bt = np.radians(26.57); mid = np.array([700, 350.0]); Rn = 2000.0
    cen = mid + Rn * np.array([-np.sin(bt), np.cos(bt)])
    r = bishop(xc=cen[0], yc=cen[1], R=Rn + 5.0, H=700, beta=26.57, env=lin, nsl=400)
    print("check talud infinito (círculo casi plano, 5 m prof.) F=%.3f ; tanφ/tanβ=%.3f" % (r["F"], np.tan(np.radians(38)) / np.tan(bt)))
    H = 700.0
    out = {}
    cases = [("Leps 2.0 φ'1=41° m=0.9", env_leps(41)),
             ("Leps 2.0 φ'1=38° m=0.9", env_leps(38)),
             ("Leps 2.0 φ'1=41° m=0.87", env_leps(41, 0.87)),
             ("Leps 2.0 φ'1=38° m=0.87", env_leps(38, 0.87))]
    for beta in [26.57, 21.8]:
        for name, env in cases:
            for hw, ru in [(0, 0), (50, 0), (50, 0.1), (50, 0.2)]:
                best = search(H, beta, env, hw, ru)
                sn, l = best["sn"], best["l"]
                frac45 = l[sn > 4.48].sum() / l.sum(); frac79 = l[sn > 7.86].sum() / l.sum()
                res_hi = (best["tau"] * l)[sn > 4.48].sum() / (best["tau"] * l).sum()
                key = f"{beta:.1f}|{name}|hw={hw}|ru={ru}"
                out[key] = dict(F=best["F"], snmax=float(sn.max()), snmean=float(np.average(sn, weights=l)),
                                frac_len_gt_4p5=frac45, frac_len_gt_7p9=frac79, frac_res_gt_4p5=res_hi,
                                depth=float((ground(best["xm"], H, beta) - best["yb"]).max()),
                                circle=[best["xc"], best["yc"], best["R"]])
                print(f"β={beta:5.2f} {name:42s} hw={hw:3d} ru_ex={ru:.1f}  FS={best['F']:.3f}  σn,max={sn.max():5.2f}  σn,med={np.average(sn, weights=l):4.2f}  L(σn>4.5)={frac45:4.0%}  L(σn>7.9)={frac79:4.0%}  R(σn>4.5)={res_hi:4.0%}  prof={out[key]['depth']:.0f} m")
    json.dump(out, open(sys.argv[1] if len(sys.argv) > 1 else "slope_results.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)



