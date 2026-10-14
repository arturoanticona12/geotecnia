"""Tabla de diseño de Leps-P (forma acotada): mediana y P05 de φ′s de la envolvente media de un material nuevo (sin
ensayos), por calidad de roca, relación de vacíos y σ′n; escala de laboratorio (sin efecto de tamaño).
Además: diagnóstico de clase del set de la litología A del sitio (p del conflicto para cada calidad) y validación externa
de la forma con los ensayos del sitio (lepsp_acotada_sitio). Escribe lepsp_tabla_diseno.json."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "leps3"))
import lepsp as L  # noqa: E402

SN = [0.5, 1.0, 3.0, 5.0, 8.0]; D_TAB = 100.0; D_CAMPO = 1000.0       # ronda 6: Dmax de laboratorio declarado; campo 1 m
out = dict(sn=SN, D_lab_mm=D_TAB, D_campo_mm=D_CAMPO, tabla={}, tabla_campo={})
for cal in ("buena", "moderada", "baja"):
    for e in (0.30, 0.45, 0.65):
        mt = L.previa(cal, e, n=60000, seed=3, D=D_TAB)
        q = L.percentiles(SN, mt, (5, 50), puntual=False)
        out["tabla"][f"{cal}|{e}"] = dict(P50=[round(float(v), 1) for v in q[50]], P05=[round(float(v), 1) for v in q[5]])
        qc = L.percentiles(SN, L.escala(mt, D_TAB, D_CAMPO), (5, 50), puntual=False)
        out["tabla_campo"][f"{cal}|{e}"] = dict(P50=[round(float(v), 1) for v in qc[50]], P05=[round(float(v), 1) for v in qc[5]])
        print(f"{cal:9s} e={e:.2f}  lab " + "  ".join(f"{s:g}: {a:.1f}/{b:.1f}" for s, a, b in zip(SN, q[50], q[5]))
              + "  | campo P05 " + " ".join(f"{b:.1f}" for b in qc[5]))
# diagnóstico de clase de la litología A (un set) con la previa de cada calidad
D = pd.read_csv(AQ.parent / "analisis_antamina" / "drenados_utilizables.csv", low_memory=False)
D = D[D.escala.isin(["0.6 m", "1.0 m"]) & (D.relave_pct_masa_total.fillna(0) == 0) & (D.litologia == "Mármol")]; D["e_use"] = D.e0_adoptado.fillna(D.e0)
out["clase_A"] = {}
for cal in ("baja", "moderada", "buena"):
    _, dg = L.actualizar_sitio([dict(calidad=cal, e=float(D.e_use.iloc[0]), D=float(D.Dmax_mm.iloc[0]), s3=D.s3.values, s1=D.s1.values)], n=4000, seed=1)
    out["clase_A"][cal] = dg[0]["p_conflicto"]
print("clase de la litología A, p del conflicto:", out["clase_A"])
json.dump(out, open(AQ / "lepsp_tabla_diseno.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
