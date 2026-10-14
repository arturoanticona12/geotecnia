import pymupdf as fitz, collections
pdf=r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0\Data Antamina\2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf"
doc=fitz.open(pdf); pg=doc[34]
print(pg.rect)
for b in pg.get_text('dict')['blocks']:
    for l in b.get('lines',[]):
        for sp in l['spans']:
            t=sp['text'].strip()
            if t and (t.replace('.','').replace(',','').isdigit() or len(t)<40): print('T',round(sp['bbox'][0]),round(sp['bbox'][1]),round(sp['bbox'][2]),round(sp['bbox'][3]),repr(t))
cnt=collections.Counter()
for dr in pg.get_drawings():
    r=dr['rect']; col=dr.get('fill') or dr.get('color')
    if 2<r.width<8 and 2<r.height<8:
        cnt[(tuple(round(c,2) for c in col) if col else None)]+=1
print(cnt)
