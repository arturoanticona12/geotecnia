"""Tensión normal efectiva movilizada en las superficies críticas de Slide2 (ronda 5): para cada escenario del lote
determinístico, σ′n ≈ γ·h·cos²α en la base de cada dovela (h = altura de la columna, α = inclinación de la base;
aproximación de dovela simple). Media ponderada por longitud de base, P90 y máximo. Escribe lepsp_sn_movilizada.json."""
import sys, json, re
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "slide2" / "scripts"))
import resultados as R  # noqa: E402

RES = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados"); CLAVE = json.load(open(AQ.parent / "slide2" / "det5" / "claves.json", encoding="utf-8"))
LOTES = sys.argv[1].split(",") if len(sys.argv) > 1 else ["64-lepsp4-det-mp", "64c-lepsp4-det-c1"]
MET = "gle/morgenstern-price"; out = {}


def dovelas(s01):
    L = Path(s01).read_text(encoding="latin-1").splitlines()
    i = next(k for k, l in enumerate(L) if l.startswith("* minimum slice info") and l.endswith(f"method={MET}"))
    D = []
    for l in L[i + 1:]:
        if l.startswith("*"):
            break
        t = l.split()
        if len(t) >= 5:
            D.append([float(v) for v in t[:5]])
    return np.array(D)


for lote in LOTES:
    for caso in sorted((RES / lote).iterdir()):
        if not caso.is_dir() or caso.name.endswith("_conv"):
            continue
        slmd = next(caso.rglob("*.slmd"), None)
        if slmd is None:
            continue
        nombres = R.escenarios(slmd)
        H = int(re.search(r"_H(\d+)_", caso.name).group(1))
        for s01 in caso.rglob("*.s01"):
            nm = nombres.get(s01.stem)
            if nm is None:
                continue
            nm = nm.split("/")[-1].strip()
            caso_, esc, q = CLAVE[nm].split("|"); gam = 15.74 if esc == "weakest E" else (21.0 if caso_.startswith("lab") else 17.17)
            D = dovelas(s01)
            if len(D) < 3:
                continue
            xb, yt, yb = D[:, 0], D[:, 2], D[:, 3]
            dx = np.diff(xb); dyb = np.diff(yb); hm = 0.5 * ((yt - yb)[1:] + (yt - yb)[:-1]); al = np.arctan2(dyb, dx); lb = np.hypot(dx, dyb)
            sn = gam * hm * np.cos(al) ** 2 / 1000.0                    # MPa
            out[f"{caso_}|{esc}|{H}|{q}"] = dict(media=float((sn * lb).sum() / lb.sum()), p90=float(np.percentile(sn, 90)), max=float(sn.max()),
                                                 prof_max=float((yt - yb).max()), x=[float(xb.min()), float(xb.max())])
for k in sorted(out):
    v = out[k]; print(f"  {k:48s} σ′n media {v['media']:.2f}  P90 {v['p90']:.2f}  máx {v['max']:.2f} MPa  (profundidad máx {v['prof_max']:.0f} m)")
json.dump(out, open(AQ / "lepsp_sn_movilizada.json", "w", encoding="utf-8"), indent=1)
