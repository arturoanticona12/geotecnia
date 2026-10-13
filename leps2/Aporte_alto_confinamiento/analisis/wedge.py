"""Mecanismo compuesto (basal) en botadero de ladera, Janbu simplificado (sin f0) con envolvente no lineal. Ilustrativo."""
import sys, json, numpy as np
sys.path.insert(0, sys.argv[1])
from slope import env_leps, env_corr, GW, GAM
sys.stdout.reconfigure(encoding="utf-8")

H, BETA, THETA = 700.0, 26.57, 10.0       # altura pie-cresta, talud global, pendiente de la ladera de fundación
tb, tt = np.tan(np.radians(BETA)), np.tan(np.radians(THETA))
XC = H / tb                                  # cresta
XE = H / tt                                  # fin de la plataforma (contacto con ladera)
top = lambda x: np.clip(np.minimum(x * tb, H), 0, None)
fnd = lambda x: x * tt


def janbu(xb, env, basal_env=None, hw=0.0, ru_ex=0.0, scarp=60.0, nsl=300):
    """Superficie: contacto de fundación (x de 0 a xb) + escarpe a 'scarp' grados hasta la superficie."""
    ts = np.tan(np.radians(scarp))
    # escarpe: y = fnd(xb) + (x-xb)*ts hasta cortar la superficie
    xs = np.linspace(xb, xb + H / ts * 1.5, 2000)
    k = np.argmax(fnd(xb) + (xs - xb) * ts >= top(xs))
    xtop = xs[k]
    xbnd = np.r_[np.linspace(0, xb, int(nsl * 0.85) + 1), np.linspace(xb, xtop, int(nsl * 0.15) + 1)[1:]]
    xm = 0.5 * (xbnd[1:] + xbnd[:-1]); b = np.diff(xbnd)
    yb = np.where(xm <= xb, fnd(xm), fnd(xb) + (xm - xb) * ts)
    alpha = np.where(xm <= xb, np.arctan(tt), np.arctan(ts))
    h = np.maximum(top(xm) - yb, 0); W = GAM * h * b; sv = GAM * h
    basal = xm <= xb
    u = np.where(basal, GW * np.minimum(hw, h) + ru_ex * sv * (hw > 0), 0.0)
    l = b / np.cos(alpha)
    sn = np.maximum(sv * np.cos(alpha) ** 2 - u, 1e-3)
    sv0 = np.maximum(sv - GW * np.minimum(hw, h), 1e-3)  # σ'v antes de exceso (para Su)
    F = 1.5
    for _ in range(300):
        if basal_env == "undrained":
            su = 0.28 * sv0
            tau_f = np.where(basal, su, env[0](sn)); tphi = np.where(basal, 0.0, env[1](sn))
        else:
            tau_f = env[0](sn); tphi = env[1](sn)
        ct = tau_f - sn * tphi
        ma = np.maximum(np.cos(alpha) * (1 + np.tan(alpha) * tphi / F), 0.2)
        num = np.sum((ct * b + (W - u * b) * tphi) / (np.cos(alpha) * ma))
        den = np.sum(W * np.tan(alpha))
        Fn = num / den
        Np = (W - u * b - ct * b * np.tan(alpha) / Fn) / ma
        sn_new = np.maximum(Np / l, 1e-3)
        if abs(Fn - F) < 1e-6:
            F = Fn; break
        F = Fn; sn = 0.5 * sn + 0.5 * sn_new
    return dict(F=F, sn=sn, l=l, basal=basal, xb=xb)


if __name__ == "__main__":
    print(f"Geometría: H={H} m, talud global {BETA}°, ladera {THETA}°, cresta x={XC:.0f} m, espesor en cresta={H - fnd(XC):.0f} m")
    cases = [("Leps 2.0 φ'1=41° m=0.9", env_leps(41), None),
             ("Leps 2.0 φ'1=41° m=0.87", env_leps(41, 0.87), None),
             ("Leps 2.0 φ'1=38° m=0.9", env_leps(38), None),
             ("Leps 2.0 φ'1=38° m=0.87", env_leps(38, 0.87), None),
             ("Base no drenada Su/σ'v=0.28 (resto φ'1=41° m=0.87)", env_leps(41, 0.87), "undrained")]
    out = {}
    XMIN = float(sys.argv[3]) if len(sys.argv) > 3 else 0.04
    for name, env, be in cases:
        for hw, ru in [(0, 0), (30, 0), (30, 0.1), (30, 0.2)]:
            if be == "undrained" and hw == 0:
                continue
            best = None
            for xb in np.linspace(XMIN * XC, 1.6 * XC, 60):
                for sc in [50, 60, 70]:
                    r = janbu(xb, env, be, hw, ru, sc)
                    if best is None or r["F"] < best["F"]:
                        best = r
            sn, l, bs = best["sn"], best["l"], best["basal"]
            f45 = l[bs & (sn > 4.48)].sum() / l.sum(); f79 = l[bs & (sn > 7.86)].sum() / l.sum()
            print(f"{name:52s} hw={hw:2d} ru_ex={ru:.1f}  FS(Janbu s/f0)={best['F']:.3f}  xb={best['xb']:.0f} m  σn,max={sn.max():5.2f}  L(σn>4.5)={f45:4.0%}  L(σn>7.9)={f79:4.0%}")
            out[f"{name}|hw={hw}|ru={ru}"] = dict(F=best["F"], xb=best["xb"], snmax=float(sn.max()), f45=f45, f79=f79)
    json.dump(out, open(sys.argv[2], "w", encoding="utf-8"), indent=1, ensure_ascii=False)



