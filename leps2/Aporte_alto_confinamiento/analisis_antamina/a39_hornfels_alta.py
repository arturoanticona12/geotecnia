"""Triaxiales de hornfels de 1 m a alta presión (WSP 2022, IDIEM; sets HF-1.0m mono y cd con σ′3 > 1.5 MPa): características y
sensibilidad de la curva sin ellos (pedido del usuario, 2026-10-13: «me hacen ruido estos ensayos»).
  - características: εa y εv en el máximo desviador, φ′s, φ′s a e = 0.45, residuo de la curva propuesta (con tope);
  - comparación con los demás triaxiales con máximo al final del ensayo (εa ≥ 17.5 %);
  - nivel de la curva sin esos 4 ensayos (cada set conserva su ensayo a 0.98 MPa) y m de Antamina sola sin ellos;
  - residuo medio de 2 a 4.62 MPa con y sin ellos; fracción de sets mundiales con φ′s creciente con σ′n (m > 1).
Escribe a39_hornfels_alta.json."""
import json, os, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ)); sys.path.insert(0, str(AQ.parent / "analisis"))
_so = sys.stdout; sys.stdout = open(os.devnull, "w", encoding="utf-8")
import a33_curva_propuesta as M  # noqa: E402
from lepsp_r6 import datos  # noqa: E402
sys.stdout = _so
S0, OM, EB = 1.013, 20.0, 0.45
A = M.A.copy(); MARCA = A.set.str.contains("HF-1.0m") & (A.s3 > 1.5)
d = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False); d["set"] = d.fuente_id + "|" + d.set_id.astype(str)
tx = d[d.tipo == "TX"].copy(); tx["marcado"] = tx.set.str.contains("HF-1.0m") & (tx.s3 > 1.5)
P = pd.read_csv(AQ / "a35_residuos.csv")
pm = P[P.set.str.contains("HF-1.0m") & (P.sn > 3)]
out = dict(ensayos=[dict(set=r.set, s3=float(r.s3), eps_a=float(r.eps_axial_falla_pct), eps_v=float(r.eps_vol_falla_pct)) for _, r in tx[tx.marcado].iterrows()],
           phis45=[float(v) for v in (pm.phis - OM * (EB - pm.e))], residuo=[float(v) for v in pm["Curva propuesta"]])
fin = tx[tx.eps_axial_falla_pct >= 17.5]
out["fin_de_ensayo"] = dict(n=int(len(fin)), n_tx=int(len(tx)), sets=sorted(fin.set.unique().tolist()), n_marcados=int(fin.marcado.sum()))
# nivel sin los 4 ensayos
full = M.phi1_sets(0.85) + OM * M.E_SET
M.A = A[~MARCA]; red = M.phi1_sets(0.85) + OM * M.E_SET; M.A = A
out["nivel"] = dict(con=float(full.mean()), sin=float(red.mean()),
                    sets={s: [float(a), float(b)] for s, a, b in zip(M.SA, full, red) if "HF-1.0m" in s})
ph = lambda s, p: float(np.degrees(np.arctan(np.tan(np.radians(p - OM * EB)) * (s / S0) ** (0.85 - 1))))
out["phis"] = {f"{s:g}": [ph(s, full.mean()), ph(s, red.mean())] for s in (1, 2, 3, 4.6, 8, 15)}
# residuo medio de 2 a 4.62 MPa
k = P.sn >= 2; hf = P.set.str.contains("HF-1.0m")
out["residuo_2_462"] = dict(con=float(P[k]["Curva propuesta"].mean()), sin=float(P[k & ~hf]["Curva propuesta"].mean()), n=int(k.sum()), n_sin=int((k & ~hf).sum()))
# base mundial: sets con φ′s creciente con σ′n
W = datos(); W = W[~W.cens] if "cens" in W else W
sl = np.array([np.polyfit(np.log(q.sn), np.log(q.tau), 1)[0] for _, q in W.groupby("Set") if q.sn.nunique() >= 3])
out["mundo_m_mayor_1"] = dict(n=int((sl > 1).sum()), sets=int(len(sl)))
# m de Antamina sola sin los 4 (estimador de a37, sin bootstrap)
g = {"__file__": str(AQ / "a37_m_antamina_y_compuesta.py"), "__name__": "x"}
sys.stdout = open(os.devnull, "w", encoding="utf-8"); exec(open(AQ / "a37_m_antamina_y_compuesta.py", encoding="utf-8").read().split("PILAS = ")[0], g); sys.stdout = _so
dd = g["d"]; out["m_antamina"] = dict(con=g["ajuste_m"](dd), sin=g["ajuste_m"](dd[~(dd.set.str.contains("HF-1.0m") & (dd.s3 > 1.5))]))
json.dump(out, open(AQ / "a39_hornfels_alta.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False)
print(json.dumps({k: v for k, v in out.items() if k not in ("ensayos",)}, ensure_ascii=False, indent=0)[:1500])
