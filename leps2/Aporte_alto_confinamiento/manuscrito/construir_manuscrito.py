"""Construye el manuscrito (artículo corto, español) en Word. El contenido está aquí; los FS de Slide2 se leen de los
resultados del banco. Uso: python construir_manuscrito.py"""
import json, re
from pathlib import Path
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm, RGBColor

AQUI = Path(__file__).parent
RAIZ = AQUI.parent
FIG = RAIZ / "figuras"
RES = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados")
S50 = json.load(open(RES / "50-botadero700" / "fs_por_escenario.json", encoding="utf-8"))["botadero_700m"]["fs"]
S51 = json.load(open(RES / "51-botadero700-m087" / "fs_por_escenario.json", encoding="utf-8"))["botadero_700m"]["fs"]
PY = json.load(open(RAIZ / "analisis" / "slope_results.json", encoding="utf-8"))
WG = json.load(open(RAIZ / "analisis" / "wedge_global.json", encoding="utf-8"))

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.15
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2.5); s.left_margin = s.right_margin = Cm(2.5)


def runs(p, texto):
    """*cursiva*, ^superíndice^, _subíndice_ y [[resaltado]] (dato por confirmar)."""
    for tok in re.split(r"(\*[^*]+\*|\^[^^]+\^|_\{[^}]+\}|\[\[[^\]]+\]\])", texto):
        if not tok:
            continue
        if tok.startswith("*"):
            r = p.add_run(tok[1:-1]); r.italic = True
        elif tok.startswith("^"):
            r = p.add_run(tok[1:-1]); r.font.superscript = True
        elif tok.startswith("_{"):
            r = p.add_run(tok[2:-1]); r.font.subscript = True
        elif tok.startswith("[["):
            r = p.add_run(tok[2:-2]); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            p.add_run(tok)
    return p


def par(texto, just=True, sangria=False, estilo=None):
    p = doc.add_paragraph(style=estilo) if estilo else doc.add_paragraph()
    if just:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if sangria:
        p.paragraph_format.first_line_indent = Cm(0.6)
    return runs(p, texto)


def titulo(texto, nivel=1):
    p = doc.add_paragraph(); r = p.add_run(texto); r.bold = True
    r.font.size = Pt(12 if nivel == 1 else 11); r.italic = nivel == 2
    p.paragraph_format.space_before = Pt(12 if nivel == 1 else 8); p.paragraph_format.keep_with_next = True
    return p


def ecuacion(texto, n):
    p = doc.add_paragraph(); p.paragraph_format.tab_stops.add_tab_stop(Cm(8), alignment=1)
    p.paragraph_format.tab_stops.add_tab_stop(Cm(16), alignment=2)
    p.add_run("\t"); runs(p, texto); p.add_run(f"\t({n})")


def rotulo(tipo, n, texto):
    p = doc.add_paragraph(); p.paragraph_format.keep_with_next = True; p.paragraph_format.space_before = Pt(8)
    r = p.add_run(f"{tipo} {n}"); r.bold = True
    p2 = doc.add_paragraph(); p2.paragraph_format.keep_with_next = True
    runs(p2, f"*{texto}*")


def fuente(texto):
    p = doc.add_paragraph(); r = p.add_run(texto); r.font.size = Pt(9)
    p.paragraph_format.space_after = Pt(10)


def figura(n, archivo, texto, fte, ancho=15.5):
    rotulo("Figura", n, texto)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(FIG / archivo), width=Cm(ancho))
    fuente(fte)


def bordes(celda, arriba=None, abajo=None):
    tcPr = celda._tc.get_or_add_tcPr(); b = OxmlElement("w:tcBorders")
    for lado, val in (("top", arriba), ("bottom", abajo)):
        if val:
            e = OxmlElement(f"w:{lado}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(val)); b.append(e)
    tcPr.append(b)


def tabla(n, texto, encabezado, filas, anchos, fte, notas=None):
    rotulo("Tabla", n, texto)
    t = doc.add_table(rows=1 + len(filas), cols=len(encabezado)); t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for j, h in enumerate(encabezado):
        c = t.rows[0].cells[j]; c.text = ""; runs(c.paragraphs[0], h); c.paragraphs[0].runs[0].bold = True
        bordes(c, arriba=8, abajo=6)
    for i, f in enumerate(filas, start=1):
        for j, v in enumerate(f):
            c = t.rows[i].cells[j]; c.text = ""; runs(c.paragraphs[0], str(v))
            if i == len(filas):
                bordes(c, abajo=8)
    for row in t.rows:
        tr = row._tr; trPr = tr.get_or_add_trPr(); cs = OxmlElement("w:cantSplit"); trPr.append(cs)
        for j, c in enumerate(row.cells):
            c.width = Cm(anchos[j])
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(1); p.paragraph_format.keep_with_next = True
                for r in p.runs:
                    r.font.size = Pt(9)
    if notas:
        p = doc.add_paragraph(); runs(p, notas); [setattr(r.font, "size", Pt(9)) for r in p.runs]
        p.paragraph_format.space_before = Pt(3)
    fuente(fte)


f3 = lambda x: f"{x:.2f}"

# ------------------------------------------------------------------ portada
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Extrapolación de la envolvente Leps 2.0 a grandes confinamientos: sesgo del exponente de curvatura "
              "e implicancias para botaderos de desmonte de 700 m"); r.bold = True; r.font.size = Pt(14)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, "[[Autor(es) y afiliaciones por confirmar]]")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, "Borrador del manuscrito. Formato de artículo corto.")

titulo("Resumen")
par("Los botaderos de desmonte de mina que se proyectan con alturas de hasta 700 m imponen esfuerzos verticales de unos "
    "15 MPa en su base, mientras que los criterios empíricos de resistencia para enrocados se calibraron con ensayos "
    "triaxiales de gran escala que rara vez superan σ′_{3} = 3 MPa. Este trabajo evalúa la extrapolación del criterio "
    "Leps 2.0 (Cylwik et al., 2025) con la base de datos pública que lo sustenta (938 ensayos, 289 sets, 40 "
    "publicaciones). Mediante un análisis dentro de cada set y validación cruzada, se muestra que cuando φ′_{1} se calibra "
    "con ensayos de σ′_{n} ≤ 1.5 MPa y se mantiene el exponente típico m = 0.9, la resistencia a σ′_{n} ≥ 2 MPa se "
    "sobreestima en 4.9 % en promedio y en el 81 % de los ensayos. El exponente que anula el sesgo es m = 0.87 (intervalo "
    "de 90 %: 0.86–0.88), y se mantiene al excluir cada publicación y al restringir la muestra al rango de aplicación del "
    "criterio. El índice de rotura de Marsal crece de 6 % a 36 % entre σ′_{n} de 0.1–0.3 MPa y de 2–4 MPa, y los 347 "
    "ensayos con registro volumétrico muestran compresión neta en la falla. En un botadero genérico de 700 m, verificado en Slide2, las superficies "
    "críticas drenadas alcanzan σ′_{n} de 3–6 MPa y el cambio de m reduce el factor de seguridad en 2–4 %. En cambio, una "
    "base saturada con respuesta no drenada (S_{u}/σ′_{v} = 0.28) lo lleva por debajo de 1.0. En botaderos muy altos, la "
    "incertidumbre de la resistencia drenada a alta presión pesa menos que la condición de drenaje de la base.")
par("*Palabras clave:* enrocado; desmonte de mina; resistencia al corte; envolvente no lineal; rotura de partículas; "
    "presión de poros; botaderos de gran altura.", just=False)

# ------------------------------------------------------------------ 1
titulo("1. Introducción")
par("Los botaderos de desmonte de la gran minería a cielo abierto han pasado de 200–300 m a 400–500 m de altura, y se "
    "evalúan diseños de 700 m o más (Valenzuela et al., 2008). Su estabilidad depende de la resistencia al corte del "
    "desmonte bajo esfuerzos efectivos para los que casi no hay ensayos. Un botadero de 700 m con peso unitario de "
    "21 kN/m^3^ impone cerca de 14.7 MPa de esfuerzo vertical en su base.", sangria=True)
par("Leps (1970) agrupó 109 ensayos triaxiales de gran escala en tres envolventes no lineales, de uso extendido en "
    "minería. Cylwik et al. (2025) las actualizaron con 938 ensayos y propusieron el criterio Leps 2.0, de un solo "
    "parámetro de ajuste, el ángulo secante φ′_{1} a σ′_{n} = 10 p_{a} (≈ 1 MPa), con un exponente de curvatura típico "
    "m = 0.9. Los mismos autores proponen calibrarlo con al menos un ensayo con σ′_{3} > 600 kPa, advierten que las "
    "condiciones no drenadas o con presión de poros no se abordaron y recomiendan ensayos específicos en proyectos de "
    "alta consecuencia.", sangria=True)
par("La pregunta práctica es qué error se comete al extrapolar Leps 2.0 desde los esfuerzos habituales de laboratorio "
    "hasta los de la base de un botadero muy alto. La rotura de partículas, que aumenta con el esfuerzo y genera arena y "
    "finos (Linero et al., 2007; Valenzuela et al., 2008), suprime la dilatancia y curva la envolvente, pero también "
    "reduce la permeabilidad y vuelve el material contractivo, lo que abre la posibilidad de presiones de poros en exceso "
    "y de respuestas no drenadas como las observadas en botaderos de carbón (Dawson et al., 1998; Hungr et al., 2002). "
    "Este trabajo cuantifica el primer efecto con la base de datos de Cylwik et al. (2025) y evalúa en un botadero "
    "genérico de 700 m el peso relativo de ambos.", sangria=True)

# ------------------------------------------------------------------ 2
titulo("2. Datos y métodos")
titulo("2.1 Base de datos y criterio de resistencia", 2)
par("Se usó la base de datos publicada junto con Leps 2.0 (Arrieta, 2025): 938 ensayos (934 triaxiales y 4 de corte "
    "directo) de 40 publicaciones, con muestras de 51–1 130 mm de diámetro y D_{max} de 4.8–200 mm. Los pares "
    "(σ′_{n}, τ) de la base ya incorporan la conversión no lineal de Cylwik et al. (2025). Los sets se identificaron por "
    "publicación y código de set, porque dos códigos se repiten entre publicaciones distintas. El criterio es:", sangria=True)
ecuacion("τ = tan φ′_{1} (10 p_{a})^1−m^ σ′_{n}^m^", 1)
par("donde p_{a} = 0.1013 MPa. Para cada ensayo se calculó el φ′_{1} implícito con m = 0.9 (Ecuación 31 de Cylwik "
    "et al., 2025):", sangria=False)
ecuacion("φ′_{1,ens} = arctan[τ / ((10 p_{a})^0.1^ σ′_{n}^0.9^)]", 2)
par("Si m = 0.9 describiera bien cada material, φ′_{1,ens} no variaría con σ′_{n} dentro de un mismo set.")

titulo("2.2 Análisis dentro de cada set", 2)
par("Para separar el efecto del esfuerzo de la variabilidad entre materiales, en cada set con al menos tres ensayos se "
    "ajustó un φ′_{1,ref} con m = 0.9 por mínimos cuadrados en ln τ, usando solo los ensayos con 0.3 ≤ σ′_{n} ≤ 1.5 MPa, "
    "y se calculó Δφ′_{1} = φ′_{1,ens} − φ′_{1,ref}. Como contraste independiente de la ventana de referencia, se ajustó "
    "un modelo de efectos mixtos por tramos, con φ′_{1,ens} como respuesta, pendientes en log_{10}(σ′_{n}/10 p_{a}) "
    "distintas por debajo y por encima de 1 MPa e intercepto aleatorio por set (Seabold y Perktold, 2010).", sangria=True)

titulo("2.3 Validación cruzada de la extrapolación", 2)
par("La prueba reproduce el uso práctico del criterio. En los sets con al menos dos ensayos con σ′_{n} ≤ 1.5 MPa y al "
    "menos uno con σ′_{n} ≥ 2 MPa (47 sets, 67 ensayos de evaluación, 13 publicaciones) se calibró φ′_{1} con los ensayos "
    "de esfuerzo bajo para un m fijo entre 0.78 y 0.95, y se predijo τ en los ensayos de esfuerzo alto. El error relativo "
    "es ε = (τ_{pred} − τ)/τ, como en Cylwik et al. (2025); ε > 0 indica sobreestimación. El exponente sin sesgo m* se "
    "definió como el que anula el sesgo medio por set. Su incertidumbre se estimó con 2 000 remuestreos por set, y su "
    "estabilidad, con una validación dejando fuera cada publicación: se eligió m con las demás y se evaluó en la excluida.",
    sangria=True)

titulo("2.4 Análisis de estabilidad y de presión de poros", 2)
par("Se analizó un botadero genérico de 700 m de altura con taludes globales de 2H:1V (26.6°) y 2.5H:1V (21.8°), "
    "γ = 21 kN/m^3^ y fundación de roca competente (c′ = 1 MPa, φ′ = 45°), horizontal o inclinada 10°. Se implementó en "
    "Python el método de Bishop (1955) con la envolvente no lineal, linealizada en la tangente al σ′_{n} de cada dovela "
    "e iterada hasta converger. La implementación reproduce la solución de talud infinito (1.566 frente a 1.562) y los "
    "FS de Slide2 9.043 (Rocscience, s. f.) con diferencias de 0.007 o menos. En la fundación inclinada se usó en Slide2 una "
    "búsqueda no circular por recocido simulado con los métodos de Spencer (1967) y GLE. Para el mecanismo basal con "
    "agua se usó el método simplificado de Janbu sin factor de corrección, que tiende a dar FS menores.", sangria=True)
par("Se consideraron una capa basal saturada de 30–50 m con razón de exceso de presión de poros r_{u} = 0.1–0.2 y, como "
    "escenario de tamizaje, una respuesta no drenada del contacto basal con S_{u} = 0.28 σ′_{v0}, a partir de la razón "
    "S_{u}/σ′_{3c} = 0.28–0.29 que Valenzuela et al. (2008) midieron en desmonte de cobre. La presión de poros por "
    "consolidación se estimó con la ecuación de Terzaghi con carga creciente, resuelta por diferencias finitas "
    "implícitas en una capa basal saturada de 30 m, drenada arriba e impermeable abajo:", sangria=True)
ecuacion("∂u/∂t = c_{v} ∂^2^u/∂z^2^ + dσ_{v}/dt ,   c_{v} = k M / γ_{w}", 3)
par("con velocidades de crecimiento de 25–100 m/año hasta 700 m, módulo edométrico M = 50–150 MPa y k = 10^−9^–10^−5^ "
    "m/s. La solución numérica coincide con la estacionaria, u_{base} = (dσ_{v}/dt) H^2^/(2 c_{v}) (147 kPa en ambos "
    "casos para k = 10^−8^ m/s y M = 100 MPa).")

# ------------------------------------------------------------------ 3
titulo("3. Resultados")
titulo("3.1 Cobertura de esfuerzos", 2)
par("La base cubre bien el rango de 0.1–3 MPa, pero solo el 9.6 % de los ensayos supera σ′_{n} = 3 MPa y el 3.6 % "
    "supera 5 MPa (Figura 1). Los ensayos con σ′_{3} ≥ 3 MPa provienen de cuatro publicaciones (Al-Hussaini, 1983; "
    "Donaghe y Cohen, 1978; Hall y Gordon, 1963; Marachi et al., 1972), y el máximo, σ′_{3} = 4.48 MPa (σ′_{n} = 7.9 MPa), "
    "de una sola. Con γ = 21 kN/m^3^, ese máximo equivale al esfuerzo vertical a unos 375 m de profundidad. La base no "
    "contiene ensayos con los esfuerzos de la mitad inferior de un botadero de 700 m.", sangria=True)
figura(1, "fig1_cobertura_esfuerzos.png",
       "Distribución de σ′n en la base de datos y rangos de esfuerzo de un botadero de 700 m",
       "Fuente: elaboración propia con datos de Arrieta (2025). Las bandas indican el rango de σ′n en las superficies "
       "críticas calculadas en la sección 4.")

titulo("3.2 Sesgo de la extrapolación con m = 0.9", 2)
par("Dentro de cada set, φ′_{1,ens} cae de forma sistemática con el esfuerzo (Figura 2a). Respecto de la referencia de "
    "0.3–1.5 MPa, la mediana de Δφ′_{1} es −0.8° entre 1 y 2 MPa, −1.4° entre 2 y 3 MPa y −2.2° a −3.1° entre 3 y 8 MPa. "
    "Las medianas quedan entre las curvas de envolventes con m = 0.85 y m = 0.87 procesadas con el mismo procedimiento. "
    "El modelo de efectos mixtos, que no depende de la ventana de referencia, da una caída de φ′_{1,ens} de 3.2° por "
    "década de σ′_{n} por debajo de 1 MPa (IC 95 %: 2.6–3.8°) y de 2.2° por década por encima (IC 95 %: 1.5–3.0°). La "
    "envolvente real es más curva que m = 0.9 en el rango ensayado, y ese exceso de curvatura disminuye a alta presión.",
    sangria=True)
par("En la validación cruzada, calibrar con m = 0.9 y extrapolar a σ′_{n} ≥ 2 MPa sobreestima τ en 4.9 % en promedio "
    "(mediana 5.0 %, error absoluto medio 6.7 %), y el 81 % de los ensayos queda sobreestimado (Figura 2b). El sesgo medio "
    "por set se anula con m* = 0.866 (IC 90 %: 0.856–0.875); con m = 0.87 el error absoluto medio baja a 4.3 %. En los "
    "ensayos con σ′_{n} ≥ 3 MPa el exponente sin sesgo sube a 0.886, lo que concuerda con una curvatura más baja a alta "
    "presión. La Tabla 1 resume la estabilidad del resultado. Al excluir cada publicación, el m elegido con las demás "
    "queda en 0.86–0.87 y el sesgo ponderado en la excluida pasa de +4.9 % a −0.7 %.", sangria=True)
figura(2, "fig2_extrapolacion_m.png",
       "(a) Caída de φ′1 dentro de cada set respecto de la referencia de 0.3–1.5 MPa. (b) Error de τ al calibrar con "
       "σ′n ≤ 1.5 MPa y extrapolar a σ′n ≥ 2 MPa, según el exponente m",
       "Fuente: elaboración propia con datos de Arrieta (2025). En (b), la banda gris es el intervalo de 90 % de m*.")
tabla(1, "Estabilidad del exponente de extrapolación y del sesgo con m = 0.9",
      ["Prueba", "Muestra", "Resultado"],
      [["Sesgo con m = 0.9, σ′_{n} ≥ 2 MPa", "47 sets, 67 ensayos", "+4.9 % (81 % sobreestimados)"],
       ["Sesgo con m = 0.9, σ′_{n} ≥ 3 MPa", "26 ensayos", "+3.0 %"],
       ["m* (sesgo medio por set nulo)", "47 sets", "0.866 (IC 90 %: 0.856–0.875)"],
       ["m elegido dejando fuera cada publicación", "13 publicaciones", "0.86–0.87; sesgo de +4.9 % a −0.7 %"],
       ["Δφ′_{1} por década sobre 1 MPa, ref. 0.3–1.5 MPa", "137 sets", "−3.7°"],
       ["Ídem, con D_{50} > 2 mm y finos < 25 %", "96 sets", "−3.8°"],
       ["Ídem, sin ensayos con σ′_{3} < 60 kPa", "136 sets", "−3.7°"],
       ["Ídem, excluyendo una publicación a la vez", "123–133 sets", "−3.2° a −4.1°"],
       ["Ídem, otras ventanas de referencia", "136–139 sets", "−2.0° (0.5–2 MPa) a −4.3° (0.2–1 MPa)"],
       ["Efectos mixtos, pendiente sobre 1 MPa", "209 sets", "−2.2° (IC 95 %: −3.0° a −1.5°)"]],
      [6.6, 3.4, 6.0],
      "Fuente: elaboración propia con datos de Arrieta (2025).",
      "Nota: las pendientes en grados por década de σ′n están expresadas en el marco de m = 0.9; una pendiente nula "
      "equivale a m = 0.9.")
par("La Figura 3 compara las envolventes resultantes. Con φ′_{1} = 41°, el ángulo secante a 10 MPa es 34.6° con "
    "m = 0.9 y 32.6° con m = 0.87. Ambas curvas quedan dentro del rango de 30–40° que Ovalle et al. (2020) reportan para "
    "enrocados triturables a alta presión.", sangria=True)
figura(3, "fig3_envolventes_secantes.png", "Ángulo de fricción secante según Leps 2.0 con m = 0.9 y m = 0.87",
       "Fuente: elaboración propia con datos de Arrieta (2025) y el rango de Ovalle et al. (2020). La línea punteada "
       "vertical marca el máximo σ′n de la base.")

titulo("3.3 Rotura de partículas y cambio volumétrico", 2)
par("El índice de rotura de Marsal (B_{g}), disponible en 627 ensayos, tiene una mediana de 5.7 % para σ′_{n} de "
    "0.1–0.3 MPa, 24.4 % para 1–2 MPa y 36.0 % para 2–4 MPa (Figura 4). Por encima de 4 MPa la mediana es 27.6 %, pero esa "
    "muestra está dominada por pocos materiales y no permite concluir si la rotura se estabiliza. La pendiente de B_{g} "
    "con el esfuerzo no ordena los materiales por su UCS de forma consistente, y la muestra con UCS conocida a alta "
    "presión es pequeña. La deformación volumétrica neta en la falla, disponible en 347 ensayos, es de compresión en "
    "los 347 ensayos y aumenta de −1.9 % en promedio para σ′_{3} ≤ 0.1 MPa a −7.1 % para σ′_{3} de 3–5 MPa (valores negativos "
    "indican compresión, según la tendencia con σ′_{3} y lo observado por Valenzuela et al., 2008).", sangria=True)
figura(4, "fig4_rotura_Bg.png", "Índice de rotura de Marsal en función de σ′n, por clase de resistencia de la roca",
       "Fuente: elaboración propia con datos de Arrieta (2025). Se omiten 2 ensayos con Bg > 120 %.")

# ------------------------------------------------------------------ 4
titulo("4. Implicancias para un botadero de 700 m")
titulo("4.1 Esfuerzos en las superficies críticas y factor de seguridad", 2)
k = lambda b, n_, hw=0, ru=0.0: PY[f"{b}|{n_}|hw={hw}|ru={ru:g}"]
c41, c41b = k("26.6", "Leps 2.0 φ'1=41° m=0.9"), k("26.6", "Leps 2.0 φ'1=41° m=0.87")
par(f"Sobre fundación horizontal, el círculo crítico de Bishop alcanza {c41['depth']:.0f}–{c41b['depth']:.0f} m de "
    f"profundidad y un σ′_{{n}} máximo de {c41['snmax']:.1f}–{c41b['snmax']:.1f} MPa (Tabla 2). Con el talud de 2.5H:1V y una "
    "capa basal con presión de poros, el círculo baja y hasta el 17 % de su longitud supera σ′_{n} = 4.5 MPa, "
    "nivel que solo alcanza el 4.6 % de los ensayos de la base. En el mecanismo basal sobre la ladera de 10°, el σ′_{n} máximo llega a 6.4 MPa y el 18 % de la superficie "
    "supera 4.5 MPa. Pese a la altura, las superficies críticas drenadas trabajan en su mayor parte dentro del rango de "
    "la base de datos, porque cortan el botadero bajo el talud y no bajo la plataforma.", sangria=True)


def fs(S, g, esc, met):
    return S[f"{g} / {esc}"][met]


filas = []
for g, nom, mets in [("Fundacion horizontal", "Fundación horizontal, 2H:1V", ("bishop simplified", "spencer")),
                     ("Ladera 10 grados", "Ladera de 10°, 2H:1V", ("gle/morgenstern-price", "spencer"))]:
    for p1 in (41, 38):
        a = fs(S50, g, f"Leps 2.0 phi1 {p1}", mets[0]); b = fs(S51, g, f"m 0.87 phi1 {p1}", mets[0])
        a2 = fs(S50, g, f"Leps 2.0 phi1 {p1}", mets[1]); b2 = fs(S51, g, f"m 0.87 phi1 {p1}", mets[1])
        pyA = PY[f"26.6|Leps 2.0 φ'1={p1}° m=0.9|hw=0|ru=0"]["F"] if g.startswith("Fund") else None
        pyB = PY[f"26.6|Leps 2.0 φ'1={p1}° m=0.87|hw=0|ru=0"]["F"] if g.startswith("Fund") else None
        filas.append([nom, f"{p1}°", f"{f3(a)} / {f3(a2)}", f"{f3(b)} / {f3(b2)}", f"{100 * (b / a - 1):+.1f} %".replace("-", "−"),
                      f"{f3(pyA)} / {f3(pyB)}" if pyA else "n. a."])
wg = lambda n_, hw, ru: WG[f"{n_}|hw={hw}|ru={ru:g}"]["F"]
filas.append(["Mecanismo basal, ladera de 10°, seco", "41°", f3(wg("Leps 2.0 φ'1=41° m=0.9", 0, 0)),
              f3(wg("Leps 2.0 φ'1=41° m=0.87", 0, 0)),
              f"{100 * (wg('Leps 2.0 φ' + chr(39) + '1=41° m=0.87', 0, 0) / wg('Leps 2.0 φ' + chr(39) + '1=41° m=0.9', 0, 0) - 1):+.1f} %".replace("-", "−"), "Janbu"])
for ru in (0.1, 0.2):
    filas.append([f"Ídem, base saturada de 30 m, r_{{u}} = {ru}", "41°", f3(wg("Leps 2.0 φ'1=41° m=0.9", 30, ru)),
                  f3(wg("Leps 2.0 φ'1=41° m=0.87", 30, ru)), "n. a.", "Janbu"])
filas.append(["Ídem, contacto basal no drenado, S_{u} = 0.28 σ′_{v0}", "41°", "n. a.",
              f3(wg("Base no drenada Su/σ'v=0.28 (resto φ'1=41° m=0.87)", 30, 0.0)), "n. a.", "Janbu"])
tabla(2, "Factores de seguridad del botadero genérico de 700 m",
      ["Caso", "φ′_{1}", "FS con m = 0.9", "FS con m = 0.87", "Cambio", "Bishop en Python"],
      filas, [5.6, 1.0, 2.5, 2.5, 1.5, 2.8],
      "Fuente: elaboración propia. Slide2 9.043 (Rocscience) para las cuatro primeras filas; Python para las demás.",
      "Nota: en las cuatro primeras filas el par de valores corresponde a Bishop y Spencer (fundación horizontal) o a GLE "
      "y Spencer (ladera), calculados en Slide2; la última columna da el FS de Bishop en Python con m = 0.9 y m = 0.87. "
      "n. a.: no aplica. Janbu: método simplificado sin factor de corrección, con superficie basal impuesta; en seco Slide2 encontró una "
      "superficie casi circular con FS menor.")
par("El cambio de m = 0.9 a m = 0.87 reduce el FS en 2–4 % en los casos drenados analizados. En la ladera de 10°, la búsqueda "
    "no circular de Slide2 no favorece el deslizamiento por el contacto basal en condición seca: la superficie crítica "
    "es casi circular y su FS (1.72 con φ′_{1} = 41°) es menor que el del mecanismo basal impuesto (1.80). El agua cambia "
    "esa jerarquía. Una capa basal saturada de 30 m con r_{u} = 0.2 baja el FS del mecanismo basal en 18 %, y un contacto "
    "basal con respuesta no drenada lo deja en 0.97. Ese valor es probablemente optimista, porque S_{u}/σ′_{3c} medido en "
    "consolidación isótropa equivale a una razón menor referida a σ′_{v} en condición K_{0}.", sangria=True)

titulo("4.2 Presión de poros por consolidación", 2)
par("Con desmonte de matriz granular (k ≥ 10^−7^ m/s), el exceso de presión de poros por consolidación en una capa basal "
    "saturada de 30 m no supera 0.4 % de σ_{v} al final de la construcción, aun con crecimientos de 100 m/año "
    "(Figura 5). Para llegar a Δu/σ_{v} = 0.1 se necesita k ≈ 10^−9^ m/s, propio de una matriz arcillosa. Como u_{base} "
    "crece con el cuadrado del espesor drenante, una zona saturada de 100 m multiplica esos valores por 11, y el umbral "
    "se desplaza hacia k ≈ 10^−8^ m/s. La rotura bajo alta presión produce principalmente arena y, en menor medida, finos "
    "(Valenzuela et al., 2008), y con la carga sola es difícil alcanzar esas permeabilidades; la meteorización y la "
    "lixiviación, que concentran finos, sí podrían hacerlo (Valenzuela et al., 2008). El mecanismo de presión de poros "
    "que más preocupa no es la consolidación, sino la saturación de la base por infiltración, sumada a la respuesta "
    "contractiva del desmonte, que a estos esfuerzos no muestra dilatación neta en la falla (sección 3.3).", sangria=True)
figura(5, "fig5_presion_poros_consolidacion.png",
       "Exceso de presión de poros por consolidación en la base de una capa saturada de 30 m al terminar un botadero de 700 m",
       "Fuente: elaboración propia. M = 50 MPa; con M = 150 MPa los valores se dividen por tres.")

# ------------------------------------------------------------------ 5
titulo("5. Discusión y limitaciones")
par("La sobreestimación con m = 0.9 coincide con el mecanismo descrito por Cylwik et al. (2025): la curvatura proviene "
    "de la supresión de la dilatancia y de la rotura. El aumento de m* a alta presión, de 0.866 a 0.886, y la pendiente más "
    "baja sobre 1 MPa en el modelo de efectos mixtos indican que la envolvente se aplana a medida que el material se "
    "acerca al estado crítico, como en arenas y carbonatos a muy alta presión (Coop et al., 2004; Yamamuro y Lade, 1996). "
    "La base no tiene datos sobre 7.9 MPa, de modo que ese aplanamiento no puede usarse para fijar un piso de resistencia "
    "en la base de un botadero de 700 m sin ensayos específicos. Mientras tanto, m = 0.87 entrega una extrapolación sin "
    "sesgo hasta el rango ensayado y es conservador si la envolvente se aplana más arriba.", sangria=True)
par("Con nuestro ajuste en ln τ, la mediana de m por set es 0.858 (209 sets con al menos tres ensayos), menor que el "
    "valor típico de 0.9 que adoptan Cylwik et al. (2025), quienes ajustaron en σ′_{1} con el solucionador GRG. La "
    "diferencia de m* respecto de 0.9 no depende de esa elección, porque la validación cruzada mide directamente el error "
    "de la predicción de τ.", sangria=True)
par("Las principales limitaciones son las siguientes. Los ensayos usan muestras escalpadas o de granulometría "
    "paralela, con D_{max} ≤ 200 mm. Su correspondencia con el material de campo depende de la razón entre el diámetro "
    "de la muestra y D_{max} (Girumugisha et al., 2024) y no se evaluó aquí. Las publicaciones con datos sobre 3 MPa son pocas y de los años sesenta a ochenta. El "
    "efecto de la resistencia de la partícula sobre el sesgo no es concluyente con esta muestra: la sobreestimación con "
    "m = 0.9 fue de +7.2 % en sets con UCS ≤ 80 MPa y de +4.9 % con UCS > 150 MPa, pero con solo 10 y 26 sets. La "
    "convención de signo de la deformación volumétrica se infirió de su tendencia. El botadero es genérico, sobre "
    "fundación competente y sin acción sísmica. El escenario no drenado es un tamizaje con el método de Janbu.",
    sangria=True)

# ------------------------------------------------------------------ 6
titulo("6. Conclusiones")
par("Calibrar Leps 2.0 con ensayos de σ′_{n} ≤ 1.5 MPa y extrapolar con m = 0.9 sobreestima la resistencia a "
    "σ′_{n} ≥ 2 MPa en cerca de 5 %. Con los datos disponibles, m = 0.87 reduce ese sesgo a −0.7 % en la prueba por publicación, con un intervalo de 90 % de "
    "0.86–0.88, estable al excluir publicaciones y al restringir la muestra al rango de aplicación del criterio.", sangria=True)
par("Para botaderos de gran altura se recomienda: (a) usar m = 0.87 cuando la calibración no incluya ensayos sobre "
    "1.5 MPa; (b) extender la guía 60-600 de Cylwik et al. (2025) con al menos un ensayo cuyo σ′_{3} se acerque al de "
    "las superficies críticas, que en este caso equivale a σ′_{3} de 1.8–3.8 MPa para σ′_{n} de 3–6 MPa; y (c) ensayar el material de la base "
    "con su granulometría triturada, en condición saturada y no drenada (CIU) a alta presión, y medir su permeabilidad.",
    sangria=True)
par("En el botadero analizado, el error de extrapolación de la resistencia drenada cambia el FS en 2–4 %, mientras que "
    "una base saturada con respuesta no drenada puede llevarlo por debajo de 1.0. Para botaderos de 700 m, el control "
    "del agua en la base y la verificación de su comportamiento no drenado pesan más en el diseño que la forma de "
    "la envolvente drenada a alta presión.", sangria=True)

titulo("Disponibilidad de datos")
par("La base de datos usada es pública (Arrieta, 2025). Los programas de análisis y el modelo de Slide2 están "
    "disponibles a solicitud de los autores.")

# ------------------------------------------------------------------ referencias
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
titulo("Referencias")
REFS = [
    "Al-Hussaini, M. (1983). Effect of particle size and strain conditions on the strength of crushed basalt. *Canadian Geotechnical Journal*, *20*(4), 706–717. https://doi.org/10.1139/t83-077",
    "Arrieta, M. (2025). *Rockfill test database* [Base de datos]. Zenodo. https://doi.org/10.5281/zenodo.14665504",
    "Bishop, A. W. (1955). The use of the slip circle in the stability analysis of slopes. *Géotechnique*, *5*(1), 7–17. https://doi.org/10.1680/geot.1955.5.1.7",
    "Coop, M. R., Sørensen, K. K., Bodas Freitas, T. y Georgoutsos, G. (2004). Particle breakage during shearing of a carbonate sand. *Géotechnique*, *54*(3), 157–163. https://doi.org/10.1680/geot.2004.54.3.157",
    "Cylwik, S. D., Arrieta, M., Cunning, J. C. y Hawley, P. M. (2025). Update to the Leps strength envelopes for rockfill based on 900 large-scale triaxial tests. *International Journal of Geomechanics*, *25*(12), 04025285. https://doi.org/10.1061/IJGNAI.GMENG-12050",
    "Dawson, R. F., Morgenstern, N. R. y Stokes, A. W. (1998). Liquefaction flowslides in Rocky Mountain coal mine waste dumps. *Canadian Geotechnical Journal*, *35*(2), 328–343. https://doi.org/10.1139/t98-009",
    "Donaghe, R. T. y Cohen, M. W. (1978). *Strength and deformation properties of rock fill* (Informe técnico S-78-1). US Army Engineer Waterways Experiment Station.",
    "Girumugisha, G., Ovalle, C. y Ouellet, S. (2024). Grading scalping and sample size effects on critical shear strength of mine waste rock through laboratory and in-situ testing. *International Journal of Rock Mechanics and Mining Sciences*, *183*, 105915. https://doi.org/10.1016/j.ijrmms.2024.105915",
    "Hall, E. B. y Gordon, B. B. (1963). Triaxial testing with large-scale high pressure equipment. En *Laboratory shear testing of soils* (STP 361, pp. 315–328). ASTM.",
    "Hungr, O., Dawson, R. F., Kent, A., Campbell, D. y Morgenstern, N. R. (2002). Rapid flow slides of coal-mine waste in British Columbia, Canada. En S. G. Evans y J. V. DeGraff (Eds.), *Catastrophic landslides: Effects, occurrence, and mechanisms* (pp. 191–208). Geological Society of America. https://doi.org/10.1130/REG15-p191",
    "Leps, T. M. (1970). Review of shearing strength of rockfill. *Journal of the Soil Mechanics and Foundations Division*, *96*(4), 1159–1170. https://doi.org/10.1061/JSFEAQ.0001433",
    "Linero, S., Palma, C. y Apablaza, R. (2007). Geotechnical characterisation of waste material in very high dumps with large scale triaxial testing. En *Proceedings of the 2007 International Symposium on Rock Slope Stability in Open Pit Mining and Civil Engineering* (pp. 59–75). Australian Centre for Geomechanics. https://doi.org/10.36487/ACG_repo/708_2",
    "Marachi, N. D., Chan, C. K. y Seed, H. B. (1972). Evaluation of properties of rockfill materials. *Journal of the Soil Mechanics and Foundations Division*, *98*(1), 95–114. https://doi.org/10.1061/JSFEAQ.0001735",
    "Ovalle, C., Linero, S., Dano, C., Bard, E., Hicher, P.-Y. y Osses, R. (2020). Data compilation from large drained compression triaxial tests on coarse crushable rockfill materials. *Journal of Geotechnical and Geoenvironmental Engineering*, *146*(9), 06020013. https://doi.org/10.1061/(ASCE)GT.1943-5606.0002314",
    "Rocscience. (s. f.). *Slide2* (versión 9.043) [Programa de cómputo]. Rocscience Inc.",
    "Seabold, S. y Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. En *Proceedings of the 9th Python in Science Conference* (pp. 92–96). https://doi.org/10.25080/Majora-92bf1922-011",
    "Spencer, E. (1967). A method of analysis of the stability of embankments assuming parallel inter-slice forces. *Géotechnique*, *17*(1), 11–26. https://doi.org/10.1680/geot.1967.17.1.11",
    "Valenzuela, L., Bard, E., Campaña, J. y Anabalón, M. E. (2008). High waste rock dumps: Challenges and developments. En *Proceedings of the First International Seminar on the Management of Rock Dumps, Stockpiles and Heap Leach Pads* (pp. 65–78). Australian Centre for Geomechanics. https://doi.org/10.36487/ACG_repo/802_6",
    "Yamamuro, J. A. y Lade, P. V. (1996). Drained sand behavior in axisymmetric tests at high pressures. *Journal of Geotechnical Engineering*, *122*(2), 109–119. https://doi.org/10.1061/(ASCE)0733-9410(1996)122:2(109)",
]
for ref in REFS:
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(1.0); p.paragraph_format.first_line_indent = Cm(-1.0)
    runs(p, ref)

out = AQUI / "Manuscrito_Leps2_alto_confinamiento.docx"
doc.save(out)
print("escrito", out)
