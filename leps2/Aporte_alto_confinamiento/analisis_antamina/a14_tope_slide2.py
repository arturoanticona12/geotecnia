"""Lee el lote 73 (efecto del tope de 37° en Slide2, Morgenstern–Price) y escribe a14_tope_slide2.json con el FS por altura,
opción y tope, y la extensión de la superficie crítica (x de entrada y salida) para distinguir el modo global del superficial."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
R = json.load(open(r"H:\Mi unidad\slide2-bench-intercambio\resultados\73-tope-reposo\fs_por_escenario.json", encoding="utf-8"))
out = {}
for mod, v in R.items():
    H = mod.split("_H")[1]
    for k, fs in v["fs"].items():
        out[f"{H}|{k.split('/')[-1].strip()}"] = fs["gle/morgenstern-price"]
for k in sorted(out):
    print(k, round(out[k], 3))
json.dump(out, open(Path(__file__).with_name("a14_tope_slide2.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
