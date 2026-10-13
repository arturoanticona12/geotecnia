"""Secciones típicas de botadero (anexo del memo, 2026-10-10): lee el lote 86 de Slide2 (modos de falla de Hawley y Cunning
2017, §8.4; slide2/generar_yaml_tipicas.py) y escribe a21_tipicas.json con el FS de Morgenstern–Price por sección, condición
de agua y búsqueda (libre, pie, global)."""
import json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
RES = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados\87-tipicas-hc2017-v3")   # lote 87: en ladera, agua bajo la huella
MET = "gle/morgenstern-price"
FS = json.load(open(RES / "fs_por_escenario.json", encoding="utf-8"))
out = {}
for modelo, v in FS.items():
    assert v["estado"] == "ok", (modelo, v["estado"])
    sec = modelo.split("_")[1]                                  # A, B, C, D
    sub = "morrena" if "morrena_5" in modelo else ("roca" if "A_roca" in modelo else "")
    clave = sec + (f" {sub}" if sub else "")
    for esc, f in v["fs"].items():
        cond, busq = [t.strip() for t in esc.split(",")]
        out.setdefault(clave, {}).setdefault("seco" if cond == "Seco" else "saturado", {})[busq] = f[MET]
for k in sorted(out):
    print(k, json.dumps(out[k]))
json.dump(out, open(Path(__file__).with_name("a21_tipicas.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
