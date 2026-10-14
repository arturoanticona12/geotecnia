"""Lee los lotes 74–76 y 78 de Slide2 (sensibilidades del memorándum; el 78 es la revisión 3, la vigente) y escribe a15_eor2_slide2.json: FS (Morgenstern–Price)
por modelo y escenario, y σ′n movilizada en la superficie crítica (γ·h·cos²α en la base de cada dovela; media ponderada
por longitud y máximo) y la extensión horizontal de la superficie."""
import sys, json
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "slide2" / "scripts")); import resultados as R  # noqa: E402
RESS = [Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados") / l for l in ("74-eor-sensibilidades", "75-eor-global-sin-tope", "76-eor-sin-tope", "78-eor-rev3", "79-eor-rev5", "81-eor-rev7", "82-eor-e045")]; MET = "gle/morgenstern-price"
GAMS = {"82-eor-e045": 19.54}                     # γ del lote (e base 0.45); los anteriores, 17.17 (e = 0.65)
out = {}
for caso in [c for RES in RESS for c in sorted(RES.iterdir())]:
    FS = json.load(open(caso.parent / "fs_por_escenario.json", encoding="utf-8"))
    if not caso.is_dir():
        continue
    nom = R.escenarios(next(caso.rglob("*.slmd")))
    for s01 in caso.rglob("*.s01"):
        nm = nom.get(s01.stem, "").split("/")[-1].strip()
        if not nm:
            continue
        L = s01.read_text(encoding="latin-1").splitlines()
        i = next(k for k, l in enumerate(L) if l.startswith("* minimum slice info") and l.endswith(MET))
        D = []
        for l in L[i + 1:]:
            if l.startswith("*"):
                break
            t = l.split()
            if len(t) >= 5:
                D.append([float(v) for v in t[:5]])
        D = np.array(D); xb, yt, yb = D[:, 0], D[:, 2], D[:, 3]
        dx, dy = np.diff(xb), np.diff(yb); h = 0.5 * ((yt - yb)[1:] + (yt - yb)[:-1]); al = np.arctan2(dy, dx); lb = np.hypot(dx, dy)
        sn = GAMS.get(caso.parent.name, 17.17) * h * np.cos(al) ** 2 / 1000
        fs = [v[MET] for k, v in FS[caso.name]["fs"].items() if k.split("/")[-1].strip() == nm][0]
        out[f"{caso.name}|{nm}"] = dict(fs=fs, sn_media=float((sn * lb).sum() / lb.sum()), sn_max=float(sn.max()), x=[float(xb.min()), float(xb.max())],
                                        prof=float((yt - yb).max()))
for k in sorted(out):
    o = out[k]; print(f"{k:36s} FS {o['fs']:.3f}  σ′n media {o['sn_media']:.2f} máx {o['sn_max']:.2f} MPa  x {o['x'][0]:.0f}–{o['x'][1]:.0f}  prof {o['prof']:.0f} m")
json.dump(out, open(Path(__file__).with_name("a15_eor2_slide2.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
