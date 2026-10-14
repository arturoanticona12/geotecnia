"""Lee los resultados de Slide2 (Morgenstern–Price, GLE con medio seno) de la ronda 4 y arma lepsp_estabilidad_slide2.json.
- Determinístico (lote 64): FS por altura, caso (densidad/escala/forma) y escenario de correlación, envolventes P50 y P05.
- Monte Carlo (lotes 65+): FS de cada realización (búsqueda propia de la superficie crítica) → Pf condicional (solo
  resistencia) con IC de Clopper–Pearson, P50 y P05 del FS e índice de confiabilidad lognormal.
Uso: python lepsp_estabilidad_slide2.py <lote_det> [<lote_mc> ...]"""
import sys, json, re
from pathlib import Path
import numpy as np
from scipy.stats import beta as betad
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; RES = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados"); SL = AQ.parent / "slide2"
MET = "gle/morgenstern-price"
CLAVE = json.load(open(SL / "det5" / "claves.json", encoding="utf-8"))           # ronda 5 (det4b en la ronda 4)


def leer(lote):
    """{(modelo, escenario): FS}; los modelos con error no traen 'fs' y se informan."""
    out = {}
    for mod, v in json.load(open(RES / lote / "fs_por_escenario.json", encoding="utf-8")).items():
        if "fs" not in v:
            print(f"  AVISO: {lote} / {mod} sin resultados ({v.get('estado')})")
        for k, fs in v.get("fs", {}).items():
            out[(mod, k.split("/")[-1].strip())] = fs.get(MET, float("nan"))
    return out


def cp(k, n):
    return [0.0 if k == 0 else float(betad.ppf(0.025, k, n - k + 1)), float(betad.ppf(0.975, k + 1, n - k)) if k < n else 1.0]


OUT = dict(metodo="Morgenstern–Price (Slide2 9.043, GLE con función medio seno)", det={}, mc={}, conv={})
for lote in sys.argv[1].split(","):
    for (mod, esc), f in leer(lote).items():
        H = re.search(r"_H(\d+)_", mod).group(1); caso, escn, q = CLAVE[esc].split("|")
        if mod.endswith("_conv"):                     # control de convergencia: búsqueda circular Auto Refine
            OUT["conv"][q] = f; print(f"  control circular {caso}|{escn}|{H}|{q}: FS = {f:.3f}"); continue
        OUT["det"][f"{caso}|{escn}|{H}|{q}"] = f
for k in sorted(OUT["det"]):
    print(f"  {k:55s} FS = {OUT['det'][k]:.3f}")
mc = {}
for lote in sys.argv[2:]:
    for (mod, esc), f in leer(lote).items():
        mc.setdefault(esc.split()[0], []).append(f)
for caso, v in mc.items():
    F = np.array([x for x in v if np.isfinite(x)]); n = len(F); nf = int((F < 1).sum()); p50, p05 = np.median(F), np.percentile(F, 5)
    sl = (np.log(p50) - np.log(p05)) / 1.645
    OUT["mc"][caso] = dict(n=n, fallas=nf, pf=nf / n, pf_ic95=cp(nf, n), FS_P50=float(p50), FS_P05=float(p05), FS_min=float(F.min()), beta_ln=float(np.log(p50) / sl))
    print(f"  MC {caso}: n={n} fallas {nf} Pf {nf / n:.4f} IC {np.round(cp(nf, n), 4)} FS P50 {p50:.3f} P05 {p05:.3f} mín {F.min():.3f} β_LN {np.log(p50) / sl:.2f}")
json.dump(OUT, open(AQ / "lepsp_estabilidad_slide2.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("escrito lepsp_estabilidad_slide2.json")
