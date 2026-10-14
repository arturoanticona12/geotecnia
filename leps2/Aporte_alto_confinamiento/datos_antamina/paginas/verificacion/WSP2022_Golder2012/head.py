import pymupdf as fitz, os, sys
D=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina"
doc=fitz.open(os.path.join(D,"2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"))
for p in [int(x) for x in sys.argv[1].split(',')]:
    t=doc[p-1].get_text()
    lines=[l.strip() for l in t.splitlines() if l.strip()]
    print('==',p, ' | '.join(lines[:60]))
