"""Exporta a CSV los datos de cada dovela de las superficies críticas (a24_dovelas_mp.json): una tabla por caso en dovelas_mp/."""
import json, re
from pathlib import Path
import pandas as pd
AQ = Path(__file__).parent; OUT = AQ / "dovelas_mp"; OUT.mkdir(exist_ok=True)
D = json.load(open(AQ / "a24_dovelas_mp.json", encoding="utf-8"))
COL = {"xm": "x_centro_base_m", "ym": "y_centro_base_m", "al": "alfa_base_rad", "l": "largo_base_m", "W": "peso_kN_m", "U": "u_kPa",
       "Np": "N_efectiva_kN_m", "T": "resistencia_disponible_kN_m", "sn": "sigma_n_efectivo_MPa", "tau_disp": "tau_disponible_MPa",
       "tau_mov": "tau_movilizado_MPa", "mat": "material_base"}
for k, v in D.items():
    d = v["dovelas"]; t = pd.DataFrame({COL[c]: d[c] for c in COL})
    t.insert(0, "dovela", range(1, len(t) + 1))
    t["E_izq_kN_m"] = d["E"][:-1]; t["E_der_kN_m"] = d["E"][1:]; t["X_izq_kN_m"] = d["X"][:-1]; t["X_der_kN_m"] = d["X"][1:]
    nombre = re.sub(r"[^\w.-]+", "_", k).strip("_")
    with open(OUT / f"{nombre}.csv", "w", encoding="utf-8", newline="") as fh:
        fh.write(f"# {k}: FS Morgenstern-Price propio {v['fs']:.4f} (Slide2 {v['fs_slide2']:.4f}), lambda {v['lam']:.3f}; Hu = 1\n")
        t.to_csv(fh, index=False, float_format="%.4f")
print(len(D), "CSV en", OUT)
