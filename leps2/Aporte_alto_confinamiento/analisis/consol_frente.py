"""Exceso de presión de poros en la capa basal saturada: (a) crecimiento global del botadero (700 m a 25–100 m/año) y
(b) avance de un frente de volteo (150 m de carga en 3 meses, 600 m/año), con capas basales de 30 y 100 m.
Terzaghi 1D con carga creciente en rampa (consol.u_base). Escribe consol_frente.json."""
import sys, json
from pathlib import Path
AQUI = Path(__file__).parent; sys.path.insert(0, str(AQUI))
from consol import u_base  # noqa: E402
sys.stdout.reconfigure(encoding="utf-8")
filas = []
for caso, R, Hfin in [("global 25 m/año", 25, 700.0), ("global 100 m/año", 100, 700.0), ("frente 150 m en 3 meses", 600, 150.0)]:
    for Hs in (30.0, 100.0):
        for k in (1e-6, 1e-7, 1e-8, 1e-9):
            ub, sv, cv = u_base(k, 50, Hs, R, Hfin=Hfin)
            filas.append(dict(caso=caso, Hs=Hs, k=k, ru=ub / sv, u_kPa=ub))
            print(f"{caso:24s} capa {Hs:5.0f} m  k = {k:.0e} m/s  Δu/σv = {ub / sv:.3f}")
json.dump(filas, open(AQUI / "consol_frente.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
