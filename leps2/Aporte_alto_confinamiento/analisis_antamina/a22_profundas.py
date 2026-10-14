"""Fallas profundas en secciones típicas de 720 m (anexo del memo, 2026-10-10): lee el lote 88 de Slide2
(slide2/generar_yaml_profundas.py) y escribe a22_profundas.json con el FS de Morgenstern–Price por sección, condición y búsqueda,
y la σ′n movilizada en la base de cada dovela de la superficie crítica. Slide2 no exporta la σn de las dovelas en el .s01; se
estima como σv·cos²α − u, con σv de la columna por capas (desmonte, morrena, roca) y u hidrostática bajo el nivel freático
del modelo. Cada dovela se asigna al material de su base (desmonte, morrena o roca) y se resume la parte en el desmonte."""
import sys, json, math
from pathlib import Path
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, str(Path.home() / ".claude" / "skills" / "slide2" / "scripts")); import resultados as R  # noqa: E402
MET = "gle/morgenstern-price"; BASE = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados")
LOTES = [("88-profundas-720", "profundas"), ("89-profundas-roca", "profundas_roca"), ("90-profundas-entradas", "profundas_entradas"), ("91-profundas-largas", "profundas_entradas_largas")]   # 88: con morrena; 89: sobre roca; 90: entrada forzada
LIM = (4.60, 7.86)                                     # MPa: tope de los ensayos de Antamina y de la base mundial
out = {}
CASOS = []
for lote, carp in LOTES:
    RES = BASE / lote
    if not (RES / "fs_por_escenario.json").exists():
        print("sin resultados:", lote); continue
    GEO = json.load(open(Path(__file__).parents[1] / "slide2" / carp / "geometria.json", encoding="utf-8"))
    FSL = json.load(open(RES / "fs_por_escenario.json", encoding="utf-8"))
    CASOS += [(c, GEO, FSL) for c in sorted(c for c in RES.iterdir() if c.is_dir())]
GR, GW = 26.7, 9.81
for caso, GEO, FS in CASOS:
    GD, GM = GEO["gam"], GEO["gamma_morrena"]
    sec = next(k for k in GEO["secciones"] if k.split()[0] == caso.name.split("_")[1])
    g = GEO["secciones"][sec]; ta, t, xi = math.tan(math.radians(g["alfa"])), g["t"], g["xi"]; sat = caso.name.endswith("saturado")
    yfs = lambda x: np.where(x < 0, x * ta, np.minimum(x * ta, g["H"])) if ta else np.zeros_like(x)
    def ywt(x):                                        # nivel freático de generar_yaml_profundas.nf
        if ta == 0:
            return np.zeros_like(x)
        y = x * ta
        return np.where((x >= 0) & (x <= xi), y, y - (t - 0.2))
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
            v = l.split()
            if len(v) >= 5:
                D.append([float(a) for a in v[:5]])
        D = np.array(D); xb, yt, yb = D[:, 0], D[:, 2], D[:, 3]
        xm = 0.5 * (xb[1:] + xb[:-1]); ytm = 0.5 * (yt[1:] + yt[:-1]); ybm = 0.5 * (yb[1:] + yb[:-1])
        al = np.arctan2(np.diff(yb), np.diff(xb)); lb = np.hypot(np.diff(xb), np.diff(yb))
        yf = np.where(xm > xi, xm * ta, yfs(xm)) if ta else yfs(xm)    # techo de la fundación (bajo la plataforma, la ladera)
        hd = np.clip(ytm - np.maximum(ybm, yf), 0, None)                 # desmonte sobre la base
        hm = np.clip(np.minimum(ytm, yf) - np.maximum(ybm, yf - t), 0, None)
        hr = np.clip(np.minimum(ytm, yf - t) - ybm, 0, None)
        u = GW * np.clip(ywt(xm) - ybm, 0, None) if sat else 0 * xm
        sn = ((GD * hd + GM * hm + GR * hr) * np.cos(al) ** 2 - u) / 1000
        mat = np.where(ybm >= yf - 0.05, "desmonte", np.where(ybm >= yf - t - 0.05, "morrena", "roca"))
        d = mat == "desmonte"; ld = lb[d].sum()
        fs = [v[MET] for k, v in FS[caso.name]["fs"].items() if k.split("/")[-1].strip() == nm][0]
        out[f"{sec}|{nm}"] = dict(
            fs=fs, x=[float(xb.min()), float(xb.max())], prof=float((yt - yb).max()),
            sn_max_desmonte=float(sn[d].max()) if d.any() else 0.0,
            sn_media_desmonte=float((sn[d] * lb[d]).sum() / ld) if ld else 0.0,
            frac_long={m: float(lb[mat == m].sum() / lb.sum()) for m in ("desmonte", "morrena", "roca")},
            frac_desmonte_sobre=[float(lb[d & (sn > s)].sum() / ld) if ld else 0.0 for s in LIM],
            sn_max_fundacion=float(sn[~d].max()) if (~d).any() else 0.0,
            dovelas=dict(x=[round(float(v), 1) for v in xm], yb=[round(float(v), 1) for v in ybm], sn=[round(float(v), 3) for v in sn], mat=mat.tolist()),
            superficie=dict(x=[round(float(v), 1) for v in xb], yb=[round(float(v), 1) for v in yb]))
for k in sorted(out):
    o = out[k]; f = o["frac_long"]
    print(f"{k:34s} FS {o['fs']:.3f} | x {o['x'][0]:5.0f}–{o['x'][1]:5.0f} prof {o['prof']:4.0f} m | desmonte {f['desmonte']:.0%} "
          f"morrena {f['morrena']:.0%} roca {f['roca']:.0%} | σ′n desmonte media {o['sn_media_desmonte']:.2f} máx {o['sn_max_desmonte']:.2f} MPa"
          f" | >4.60: {o['frac_desmonte_sobre'][0]:.0%} >7.86: {o['frac_desmonte_sobre'][1]:.0%} | fund. máx {o['sn_max_fundacion']:.2f}")
json.dump(out, open(Path(__file__).with_name("a22_profundas.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
