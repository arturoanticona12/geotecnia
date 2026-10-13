import fitz, pathlib, sys
src = pathlib.Path(r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\ensayos")
out = pathlib.Path(__file__).parent
abbr = {"Triaxial CU 6 in":"TX","Corte directo":"DS","Proctor estándar":"PR","Contenido de agua":"CA","Clasificación de suelos SUCS":"SU"}
def key(n):
    n=n.lower()
    if n.startswith("marmol"): return "M"
    if n.startswith("intrusivo"): return "I"
    if n.startswith("hornfels"): return "H"
    if "pila 01" in n: return "P1"
    if "pila 02" in n: return "P2"
for sub,a in abbr.items():
    for f in sorted((src/sub).glob("*.pdf")):
        doc=fitz.open(f); k=key(f.name)
        txt=[]
        for i,p in enumerate(doc):
            txt.append(f"=== PAGE {i+1} === size {p.rect}\n"+p.get_text())
            p.get_pixmap(dpi=int(sys.argv[1]) if len(sys.argv)>1 else 150).save(out/f"{a}_{k}_p{i+1}.png")
        (out/f"{a}_{k}.txt").write_text("\n".join(txt),encoding="utf-8")
        print(a,k,len(doc),doc.metadata.get("creationDate"))
