"""Leps-P: efecto de escala de la probeta dentro de un mismo material (misma publicación y tipo de roca, distinto Dmax).
Por grupo: MCO de y = c + m x + βD ln(Dmax) + βe e. Predicción de Frossard et al. (2012): βD = −κ(1 − m), κ ≈ 0.41."""
import sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from common import load_db  # noqa: E402
from modelos import CLASE  # noqa: E402
from lepsp_modelo import preparar  # noqa: E402

d = preparar(load_db(), CLASE); d = d[d.Dmax.notna()].copy()
d["Cu-BT"] = pd.to_numeric(d["Cu-BT"], errors="coerce")
filas = []
for (ref, mat), g in d.groupby(["pub", "Material Type"]):
    if g.Dmax.nunique() < 2 or len(g) < 6:
        continue
    lnD = np.log(g.Dmax.values)
    cols = [np.ones(len(g)), g.x.values, lnD]; nom = ["c", "m", "bD"]
    if g.e.std() > 0.01 and np.corrcoef(g.e, lnD)[0, 1] ** 2 < 0.9:
        cols.append(g.e.values); nom.append("be")
    X = np.c_[tuple(cols)]; b, *_ = np.linalg.lstsq(X, g.y.values, rcond=None)
    r = g.y.values - X @ b; s2 = r @ r / max(len(g) - X.shape[1], 1); se = np.sqrt(np.diag(s2 * np.linalg.inv(X.T @ X)))
    i = nom.index("bD")
    cu = g.groupby("Dmax")["Cu-BT"].mean(); ee = g.groupby("Dmax").e.mean()
    similar = bool(cu.notna().all() and cu.max() / cu.min() < 1.25 and ee.max() - ee.min() < 0.05)
    filas.append(dict(pub=ref, material=mat, n=len(g), Dmax=f"{g.Dmax.min():g}–{g.Dmax.max():g}", R=g.Dmax.max() / g.Dmax.min(),
                      Cu_ratio=cu.max() / cu.min() if cu.notna().all() else np.nan, de=ee.max() - ee.min(), similar=similar,
                      m=b[1], bD=b[i], se_bD=se[i], frossard=-0.41 * (1 - b[1]),
                      dphi_R=np.degrees(np.arctan(np.tan(np.radians(40)) * (g.Dmax.max() / g.Dmax.min()) ** b[i])) - 40))
T = pd.DataFrame(filas).sort_values("R", ascending=False)
print(T.round(3).to_string(index=False))


def meta(T, etq):
    w = 1 / T.se_bD ** 2; bm = (w * T.bD).sum() / w.sum(); sem = np.sqrt(1 / w.sum())
    Q = (w * (T.bD - bm) ** 2).sum(); tau2 = max(0, (Q - (len(T) - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    wr = 1 / (T.se_bD ** 2 + tau2); bre = (wr * T.bD).sum() / wr.sum(); sere = np.sqrt(1 / wr.sum())
    k = -bre / (1 - T.m.mean())
    print(f"\n{etq} ({len(T)} grupos): efectos fijos {bm:+.4f} ± {sem:.4f}; efectos aleatorios {bre:+.4f} ± {sere:.4f} (τ = {np.sqrt(tau2):.4f})"
          f" | κ implícito {k:.2f} ± {sere / (1 - T.m.mean()):.2f} | Δφ′ a 40° por duplicar Dmax {np.degrees(np.arctan(np.tan(np.radians(40)) * 2 ** bre)) - 40:+.2f}°")
    return dict(b=bre, se=sere, tau=np.sqrt(tau2), kappa=k, n=len(T))


R = dict(todos=meta(T, "Todos los grupos"), similares=meta(T[T.similar], "Gradación paralela y misma densidad (Cu ±25 %, Δe < 0.05)"),
         no_similares=meta(T[~T.similar], "Gradación o densidad cambian con Dmax"))
print(f"Frossard con κ = 0.41 y m = 0.86: {-0.41 * 0.14:+.4f}")
import json; json.dump(R, open(AQUI / "lepsp_escala.json", "w"), indent=1, default=float)
T.to_csv(AQUI / "lepsp_escala.csv", index=False)
