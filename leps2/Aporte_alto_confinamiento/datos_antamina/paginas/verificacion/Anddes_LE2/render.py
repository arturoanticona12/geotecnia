import fitz, pathlib, sys, json
base = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos")
out = pathlib.Path(__file__).parent
short = {"Clasificación de suelos SUCS":"SUCS","Contenido de agua":"CA","Corte directo":"LSDS","Proctor estándar":"PR","Triaxial CU 6 in":"TX"}
def key(name):
    n=name.lower()
    if n.startswith("marmol"): return "M"
    if n.startswith("hornfels"): return "H"
    if n.startswith("intrusivo"): return "I"
    if "pila 01" in n: return "P1"
    if "pila 02" in n: return "P2"
txt=open(out/"texto_todo.txt","w",encoding="utf8")
for pdf in sorted(base.rglob("*.pdf")):
    t=short[pdf.parent.name]; k=key(pdf.name)
    doc=fitz.open(pdf)
    for i,p in enumerate(doc):
        fn=out/f"{t}_{k}_p{i+1}.png"
        p.get_pixmap(dpi=170).save(fn)
        txt.write(f"\n===== {t}_{k}_p{i+1} | {pdf.name} | rot={p.rotation} size={p.rect}\n")
        txt.write(p.get_text())
    print(t,k,len(doc))
