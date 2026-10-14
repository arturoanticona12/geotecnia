"""Inventario de los PDF de Data Antamina: páginas, texto extraíble y páginas con indicios de resultados triaxiales."""
import sys, re, json
from pathlib import Path
import fitz
sys.stdout.reconfigure(encoding="utf-8")
SRC = Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina")
OUT = Path(__file__).parent / "texto"; OUT.mkdir(exist_ok=True)
CLAVES = re.compile(r"(σ3|sigma 3|σ'3|confin|presi[oó]n de c[aá]mara|desviador|triaxial|CID|CIU|ϕ|φ|fricci[oó]n|Marsal|Bg|densidad|granulom|D50|UCS|resistencia)", re.I)
inv = {}
for pdf in sorted(SRC.glob("*.pdf")):
    d = fitz.open(pdf); n = len(d); txt_pag = []; hits = []
    with open(OUT / (pdf.stem + ".txt"), "w", encoding="utf-8") as f:
        for i, pg in enumerate(d):
            t = pg.get_text()
            f.write(f"\n=== PÁGINA {i + 1} ===\n{t}")
            txt_pag.append(len(t.strip()))
            k = len(CLAVES.findall(t))
            if k >= 3:
                hits.append(i + 1)
    vacias = sum(1 for x in txt_pag if x < 50)
    inv[pdf.name] = dict(paginas=n, sin_texto=vacias, paginas_con_indicios=hits[:60])
    print(f"{pdf.name}\n   páginas {n} | sin texto (escaneadas) {vacias} | con indicios de ensayos: {len(hits)} → {hits[:40]}")
json.dump(inv, open(Path(__file__).parent / "inventario.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
