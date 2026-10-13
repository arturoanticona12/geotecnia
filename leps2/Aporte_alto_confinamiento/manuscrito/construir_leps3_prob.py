"""Manuscrito «Leps 3.0» probabilístico (artículo completo, español). El texto está aquí; los números se leen de los
resultados de analisis/ y analisis_antamina/. Uso: python construir_leps3_prob.py"""
import json, math, re
from pathlib import Path
import pandas as pd
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, Cm

AQUI = Path(__file__).parent; RAIZ = AQUI.parent; FIG = RAIZ / "figuras"; FIGA = RAIZ / "analisis_antamina" / "figuras"
AN = RAIZ / "analisis"; AA = RAIZ / "analisis_antamina"
RS = json.load(open(AN / "resumen_manuscrito.json", encoding="utf-8"))
EJ = json.load(open(AN / "ejemplo_leps3.json", encoding="utf-8"))
COB = pd.read_csv(AN / "prob_cobertura_tabla.csv")
LP = pd.read_csv(AA / "litologia_posterior.csv").set_index("litologia")
LE = pd.read_csv(AA / "litologia_envolventes.csv", index_col=[0, 1])
BE = pd.read_csv(AA / "botadero_envolvente.csv").set_index("sn")

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(11)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.space_after = Pt(6); st.paragraph_format.line_spacing = 1.15
for s in doc.sections:
    s.top_margin = s.bottom_margin = Cm(2.5); s.left_margin = s.right_margin = Cm(2.5)


def runs(p, texto):
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


def par(texto, sangria=True, just=True):
    p = doc.add_paragraph()
    if just:
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    if sangria:
        p.paragraph_format.first_line_indent = Cm(0.6)
    return runs(p, texto)


def vineta(texto):
    p = doc.add_paragraph(style="List Bullet"); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    return runs(p, texto)


def titulo(texto, nivel=1):
    p = doc.add_paragraph(); r = p.add_run(texto); r.bold = True
    r.font.size = Pt(12 if nivel == 1 else 11); r.italic = nivel == 2
    p.paragraph_format.space_before = Pt(12 if nivel == 1 else 8); p.paragraph_format.keep_with_next = True


def ecuacion(texto, n):
    p = doc.add_paragraph(); pf = p.paragraph_format
    pf.tab_stops.add_tab_stop(Cm(8), alignment=1); pf.tab_stops.add_tab_stop(Cm(16), alignment=2)
    p.add_run("\t"); runs(p, texto); p.add_run(f"\t({n})")


def rotulo(tipo, n, texto):
    p = doc.add_paragraph(); p.paragraph_format.keep_with_next = True; p.paragraph_format.space_before = Pt(8)
    p.add_run(f"{tipo} {n}").bold = True
    p2 = doc.add_paragraph(); p2.paragraph_format.keep_with_next = True; runs(p2, f"*{texto}*")


def fuente(texto):
    p = doc.add_paragraph(); runs(p, texto); p.paragraph_format.space_after = Pt(10)
    for r in p.runs:
        r.font.size = Pt(9)


def figura(n, ruta, texto, fte, ancho=15.0):
    rotulo("Figura", n, texto)
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(ruta), width=Cm(ancho)); fuente(fte)


def bordes(c, arriba=None, abajo=None):
    tcPr = c._tc.get_or_add_tcPr(); b = OxmlElement("w:tcBorders")
    for lado, v in (("top", arriba), ("bottom", abajo)):
        if v:
            e = OxmlElement(f"w:{lado}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(v)); b.append(e)
    tcPr.append(b)


def tabla(n, texto, enc, filas, anchos, fte, nota=None):
    rotulo("Tabla", n, texto)
    t = doc.add_table(rows=1 + len(filas), cols=len(enc)); t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for j, h in enumerate(enc):
        c = t.rows[0].cells[j]; c.text = ""; runs(c.paragraphs[0], h)
        for r in c.paragraphs[0].runs:
            r.bold = True
        bordes(c, 8, 6)
    for i, f in enumerate(filas, 1):
        for j, v in enumerate(f):
            c = t.rows[i].cells[j]; c.text = ""; runs(c.paragraphs[0], str(v))
            if i == len(filas):
                bordes(c, abajo=8)
    for row in t.rows:
        trPr = row._tr.get_or_add_trPr(); trPr.append(OxmlElement("w:cantSplit"))
        for j, c in enumerate(row.cells):
            c.width = Cm(anchos[j])
            for p in c.paragraphs:
                p.paragraph_format.space_after = Pt(1); p.paragraph_format.keep_with_next = True
                for r in p.runs:
                    r.font.size = Pt(9)
    if nota:
        p = doc.add_paragraph(); runs(p, nota); p.paragraph_format.space_before = Pt(3); p.paragraph_format.keep_with_next = True
        for r in p.runs:
            r.font.size = Pt(9)
    fuente(fte)


pc = lambda v: f"{100 * v:.0f} %"
menos = lambda v, d: f"{v:.{d}f}".replace("-", "−")              # signo menos tipográfico
f1 = lambda v: f"{v:.1f}"
f2 = lambda v: f"{v:.2f}"
grad = lambda th: math.degrees(math.atan(math.exp(th)))
fe = RS["fe"]; A = RS["A_total"]; A0 = RS["A0_total"]; B = RS["B"]; AH = RS["A_en_B"]; P1 = RS["P1"]; P3 = RS["P3"]
w_var = RS["sd_theta"] ** 2 / (RS["sd_theta"] ** 2 + RS["sx"][2] ** 2)          # fracción de la varianza a σ0 entre materiales
omega = -fe["e"] * math.sin(math.radians(41)) * math.cos(math.radians(41)) * 180 / math.pi
FS = {k: v["F"] for k, v in EJ.items()}
dmax_tab = max(abs(v[0] - v[1]) for c in RS["tabla_phi1"].values() for v in c.values())
le = lambda lit, p, s: LE.loc[(lit, p), s]

# ============================================================== portada y resumen
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Leps 3.0: un criterio probabilístico de resistencia al corte de enrocados y desmonte de mina para "
              "botaderos de gran altura")
r.bold = True; r.font.size = Pt(14)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, "[[Autor(es) y afiliaciones por confirmar]]")
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, "Borrador del manuscrito. Formato de artículo de investigación.")

titulo("Resumen")
par("Las envolventes de Leps (1970) y su actualización como Leps 2.0 (Cylwik et al., 2025) son la referencia empírica para "
    "estimar la resistencia al corte de enrocados y desmonte de mina sin ensayos del sitio. La nueva generación de "
    "botaderos, de 500–700 m de altura, lleva esa estimación a esfuerzos que la base de datos no cubre y la usa en "
    "diseños por confiabilidad, que necesitan una distribución de la resistencia y no solo un valor central. Este trabajo "
    "propone Leps 3.0, un criterio probabilístico que conserva la forma y la tabla de Leps 2.0 y las convierte en un modelo "
    "jerárquico: el ángulo de referencia φ′_{1} y el exponente de curvatura m son variables aleatorias de cada material, "
    "con medias que dependen de la calidad de la roca y de la relación de vacíos, y la dispersión dentro de cada material "
    f"depende del esfuerzo. El modelo se calibró con {RS['n_ensayos']} ensayos de {RS['n_sets']} materiales y "
    f"{RS['n_pub']} publicaciones, y se evaluó fuera de muestra, dejando fuera cada publicación. Sin ensayos del sitio, el intervalo "
    f"predictivo de 80 % contiene el {pc(A['cob80'])} de los ensayos y el {pc(A['bajo10'])} queda bajo su percentil 10. "
    "Con ensayos del sitio de baja presión, la actualización bayesiana conjugada reduce a la mitad el ancho del "
    f"intervalo a σ′_{{n}} ≥ 2 MPa ({f2(AH['ancho80'])} a {f2(B['ancho80'])} en ln τ) sin perder la calibración. La mediana de φ′_{{1}} reproduce la "
    f"tabla de Leps 2.0 con diferencias de {f1(dmax_tab)}° o menos. El {pc(w_var)} de la varianza corresponde a "
    "diferencias entre materiales y no a la dispersión de los ensayos, de modo que la incertidumbre no se reduce al "
    "promediar a lo largo de una superficie de falla, sino con ensayos del material. La aplicación al desmonte de un "
    "yacimiento de skarn polimetálico en los Andes muestra cómo se integran los ensayos de gran escala por litología y cómo "
    "la mezcla de litologías del botadero estrecha la envolvente de diseño.", sangria=False)
par("*Palabras clave:* enrocado; desmonte de mina; resistencia al corte; envolvente no lineal; modelo jerárquico; "
    "actualización bayesiana; botaderos de gran altura; diseño por confiabilidad.", sangria=False, just=False)

# ============================================================== 1
titulo("1. Introducción")
par("Leps (1970) reunió 109 ensayos triaxiales de gran escala y propuso tres envolventes no lineales para enrocados. "
    "Durante cinco décadas esas curvas se usaron en presas y botaderos cuando no había ensayos del sitio. Cylwik et al. "
    "(2025) las actualizaron con 938 ensayos de 40 publicaciones (Arrieta, 2025), propusieron un criterio basado en una ley de potencia con "
    "un solo parámetro de ajuste, el ángulo secante φ′_{1} a σ′_{n} = 10 p_{a}, y un modelo empírico que estima φ′_{1} a "
    "partir de la calidad de la roca y la relación de vacíos. Llamaron al conjunto Leps 2.0.")
par("Dos cambios en la práctica minera piden un paso más. El primero es la escala: los botaderos de 500–700 m "
    "(Valenzuela et al., 2008) imponen en su base esfuerzos normales de 10–15 MPa, en un material que se tritura, pierde "
    "dilatancia y reduce su permeabilidad (Linero et al., 2007; Ovalle et al., 2020), mientras que la base de datos llega a "
    f"σ′_{{n}} = {f1(RS['sn_max'])} MPa. El segundo es el método de diseño: los análisis por confiabilidad y los criterios de "
    "aceptación por probabilidad de falla necesitan la distribución de la resistencia y su dependencia del esfuerzo, no "
    "un valor central con un factor de seguridad global. Leps 2.0 ya informa la dispersión de φ′_{1} entre ensayos; falta "
    "un modelo que la organice por fuentes, la propague al esfuerzo de diseño, la reduzca con ensayos del sitio y diga "
    "cuánto crece al extrapolar.")
par("Este trabajo propone Leps 3.0 con ese fin. Leps 3.0 no cambia la forma funcional ni la tabla de φ′_{1} de Leps 2.0: "
    "las adopta como la media de un modelo jerárquico calibrado con la misma base de datos. Sus aportes son cuatro: (a) "
    "una distribución predictiva de la resistencia de un material nuevo, con su dependencia del esfuerzo; (b) una "
    "regla analítica para actualizarla con ensayos del sitio; (c) la verificación de ambas fuera de muestra, dejando fuera "
    "cada publicación; y (d) una implementación abierta que permite recalibrar el criterio cuando existan ensayos a mayor "
    "presión. La sección 5 lo aplica al desmonte de un yacimiento de skarn polimetálico en los Andes, con ensayos de "
    "gran escala por litología, para un botadero de 700 m.")

# ============================================================== 2
titulo("2. Formulación")
titulo("2.1 De la ley de potencia al modelo jerárquico", 2)
par("El criterio de Leps 2.0 (Cylwik et al., 2025) es una ley de potencia anclada en σ_{0} = 10 p_{a}, con "
    "p_{a} = 0.1013 MPa:")
ecuacion("τ = tan φ′_{1} σ_{0}^1−m^ σ′_{n}^m^", 1)
par("En variables logarítmicas, x = ln(σ′_{n}/σ_{0}) e y = ln(τ/σ_{0}), la Ecuación 1 es una recta con ordenada "
    "θ = ln tan φ′_{1} y pendiente m. Leps 3.0 trata cada material ensayado (un set de ensayos con la misma "
    "granulometría, densidad y litología) como una realización de una población:")
ecuacion("y_{ij} = θ_{j} + m_{j} x_{ij} + ε_{ij},   ε_{ij} ~ N(0, σ_{ε}(x_{ij})^2^)", 2)
ecuacion("θ_{j} = β_{c(j)} + β_{e} e_{j} + b_{0j},   m_{j} = μ_{m} + b_{1j},   (b_{0j}, b_{1j}) ~ N(0, Σ)", 3)
par("donde i indica el ensayo y j el material; β_{c} es la ordenada de la calidad de roca c (buena, moderada o baja, "
    "según la Tabla 5 de Cylwik et al., 2025), β_{e} el efecto de la relación de vacíos inicial e, μ_{m} la curvatura "
    "media y Σ la covarianza entre materiales de (θ, m). El término ε corresponde a la dispersión de los ensayos de un mismo "
    "material, que incluye la variabilidad entre probetas y el error de medición, y su desviación σ_{ε} se estima por "
    "rango de esfuerzo. Es un modelo lineal mixto (Laird y Ware, 1982). Con β_{e} y β_{c}, la mediana de "
    "φ′_{1} reproduce la relación φ′_{1} = φ′_{e=0} − ω e de Leps 2.0; con Σ y σ_{ε} = 0, la Ecuación 2 es la Ecuación 1.")

titulo("2.2 Distribución predictiva", 2)
par("Para un material nuevo de calidad c y relación de vacíos e, sin ensayos, el par (θ, m) tiene distribución normal "
    "con media (β_{c} + β_{e} e, μ_{m}) y covarianza Σ. La resistencia en un punto a un esfuerzo σ′_{n} tiene entonces:")
ecuacion("E[y] = β_{c} + β_{e} e + μ_{m} x,   Var[y] = z^T^ Σ z + σ_{ε}(x)^2^,   z = (1, x)", 4)
par("La varianza crece con x^2^: la incertidumbre es mínima cerca de σ_{0} y aumenta al alejarse, en particular al "
    "extrapolar hacia los esfuerzos de la base de un botadero alto. El primer término es la incertidumbre de la "
    "envolvente media del material; el segundo, la dispersión de un ensayo en torno a ella. La distinción importa en el "
    "diseño: la resistencia movilizada por una superficie de falla extensa promedia el segundo término, pero no el "
    "primero (Vanmarcke, 1977).")

titulo("2.3 Actualización con ensayos del sitio", 2)
par("Si se dispone de n ensayos del material, con pares (x_{i}, y_{i}), la distribución de (θ, m) se actualiza con la "
    "posterior gaussiana analítica del modelo lineal con previa conocida:")
ecuacion("C_{post} = (Σ^−1^ + Z^T^ R^−1^ Z)^−1^,   μ_{post} = C_{post} (Σ^−1^ μ_{0} + Z^T^ R^−1^ y)", 5)
par("con Z la matriz de filas (1, x_{i}), R = diag(σ_{ε}(x_{i})^2^) y μ_{0} la media previa. Con uno o dos ensayos, el "
    "material se acerca a la previa; con ensayos en un rango amplio de esfuerzos, dominan los datos. Los triaxiales se "
    "convierten a pares (σ′_{n}, τ) con las Ecuaciones 13, 14 y 16 de Cylwik et al. (2025), que dependen de m; la "
    "conversión se itera con el m posterior.")

titulo("2.4 Restricción de forma", 2)
par("Una envolvente con ley de potencia y m > 1 es convexa y su ángulo secante crece sin límite con el esfuerzo, lo que no "
    "tiene respaldo físico en materiales granulares. Leps 3.0 condiciona la distribución de (θ, m) a m ≤ 1: m se muestrea "
    "de su marginal normal truncada y θ de su distribución condicional dado m. La restricción casi no actúa en la previa "
    f"(P[m > 1] = {RS['P_m_gt1_previa']:.1%}), pero es necesaria tras actualizar con materiales cuya resistencia secante no "
    "disminuye en el rango ensayado, como el del ejemplo de la sección 4.4.")

titulo("2.5 Dominio", 2)
par("Leps 3.0 hereda el dominio de aplicación de Leps 2.0 (D_{50} > 2 mm y finos < 25 %) y lo extiende con dos avisos "
    f"que forman parte del criterio: sobre σ′_{{n}} = {f1(RS['sn_max'])} MPa no hay datos en la base, y sobre tres veces "
    "el σ′_{n} máximo ensayado en el sitio los intervalos actualizados no han sido verificados. En ambos casos la "
    "envolvente se extrapola con el mismo modelo y su banda crece según la Ecuación 4, pero la cobertura de esa banda no "
    "tiene contraste empírico.")

# ============================================================== 3
titulo("3. Datos y métodos")
titulo("3.1 Base de datos", 2)
par(f"Se usó la base de datos publicada con Leps 2.0 (Arrieta, 2025). Se retuvieron {RS['n_ensayos']} ensayos de "
    f"{RS['n_sets']} sets y {RS['n_pub']} publicaciones que cumplen tres condiciones: σ′_{{3}} ≥ 60 kPa en los triaxiales, "
    "relación de vacíos inicial informada y al menos dos ensayos por set. El límite de 60 kPa sigue la guía 60-600 de "
    "Cylwik et al. (2025), que reconoce el mayor error de los ensayos a muy bajo confinamiento. Los sets se identificaron "
    "por publicación y código, y la calidad de roca se asignó según la Tabla 5 de Cylwik et al. (2025). La Figura 1 "
    f"muestra la distribución de σ′_{{n}}: {RS['n_sn_gt3']} ensayos superan 3 MPa y provienen de {RS['n_pub_sn_gt3']} "
    "publicaciones.")
figura(1, FIG / "figP0_esfuerzos_base.png", "Distribución de σ′n en la base de calibración y esfuerzos de un botadero de 700 m",
       "Fuente: elaboración propia con datos de Arrieta (2025). La superficie crítica es la del ejemplo de la sección 5.4.")

titulo("3.2 Estimación", 2)
par("Los efectos fijos (β_{c}, β_{e}, μ_{m}) y la covarianza Σ se estimaron por máxima verosimilitud restringida "
    "(Seabold y Perktold, 2010). La dispersión dentro de cada material, σ_{ε}, se estimó con los residuos condicionales "
    "en cuatro rangos de x, con límites en σ′_{n} = 0.37, 1.0 y 2.75 MPa, y se interpola linealmente entre los centros "
    "de los rangos para evitar saltos en la banda.")

titulo("3.3 Evaluación fuera de muestra", 2)
par("Se repitió la estimación dejando fuera cada publicación y se predijeron sus ensayos, de modo que cada predicción "
    "corresponde a un laboratorio, un material y un procedimiento que el modelo no vio. Se evaluaron dos modos de uso:")
vineta("Modo A, sin ensayos del sitio: distribución predictiva de la Ecuación 4 con la calidad de roca y e.")
vineta("Modo B, con ensayos del sitio: en cada set con al menos dos ensayos de σ′_{n} ≤ 1.5 MPa y uno de σ′_{n} ≥ 2 MPa, "
       "se actualizó con los primeros (Ecuación 5) y se predijeron los segundos.")
par("Las métricas son la cobertura de los intervalos centrales de 80 % y 90 %, la fracción de ensayos bajo el percentil "
    "10, que debe ser cercana a 10 % para que una envolvente de diseño P10 signifique lo que dice, el ancho del intervalo "
    "y el puntaje de probabilidad continua CRPS (Gneiting y Raftery, 2007), que premia a la vez la calibración y la "
    "precisión. Como referencia se usó la práctica habitual de asignar a la envolvente central una dispersión constante "
    "en ln τ, estimada en el mismo pliegue de entrenamiento.")

# ============================================================== 4
titulo("4. Resultados")
titulo("4.1 Parámetros y relación con Leps 2.0", 2)
par("La Tabla 1 resume los parámetros. La curvatura media es μ_{m} = "
    f"{fe['x']:.3f} y la desviación entre materiales es {RS['sd_m']:.3f} en m y {RS['sd_theta']:.3f} en θ, con una "
    f"correlación de {menos(RS['rho'], 2)}: los materiales más resistentes a σ_{{0}} tienden a ser algo más curvos, como predice "
    "la relación entre dilatancia y esfuerzo de Bolton (1986). El efecto de la relación de vacíos equivale a "
    f"{omega:.0f}° por unidad de e a φ′_{{1}} ≈ 41°, del orden de los 20° de Leps 2.0.")
filas = [["β_{c}, calidad buena", f"{fe['C(clase)[good]']:.3f}", f"φ′_{{e=0}} = {f1(grad(fe['C(clase)[good]']))}°"],
         ["β_{c}, calidad moderada", f"{fe['C(clase)[moderate]']:.3f}", f"φ′_{{e=0}} = {f1(grad(fe['C(clase)[moderate]']))}°"],
         ["β_{c}, calidad baja", f"{fe['C(clase)[low]']:.3f}", f"φ′_{{e=0}} = {f1(grad(fe['C(clase)[low]']))}°"],
         ["β_{e}", menos(fe['e'], 3), f"≈ {omega:.0f}° por unidad de e a φ′_{{1}} ≈ 41°"],
         ["μ_{m}", f"{fe['x']:.3f}", "Curvatura media"],
         ["Desviación de θ entre materiales", f"{RS['sd_theta']:.3f}", f"≈ ±{f1(math.degrees(RS['sd_theta']) * 0.49)}° en φ′_{{1}}"],
         ["Desviación de m entre materiales", f"{RS['sd_m']:.3f}", ""],
         ["Correlación de θ y m", menos(RS['rho'], 2), ""],
         ["σ_{ε} por rango de σ′_{n} (MPa)", " / ".join(f"{v:.3f}" for v in RS["sx"]), "< 0.37; 0.37–1.0; 1.0–2.75; > 2.75"]]
tabla(1, "Parámetros de Leps 3.0", ["Parámetro", "Valor", "Interpretación"], filas, [5.4, 4.2, 6.0],
      f"Fuente: elaboración propia con datos de Arrieta (2025); {RS['n_ensayos']} ensayos, {RS['n_sets']} sets.")
par("La Tabla 2 compara la mediana de φ′_{1} de la previa con la tabla de Leps 2.0. Las diferencias son de "
    f"{f1(dmax_tab)}° o menos: el modelo jerárquico, estimado de forma independiente y con la curvatura libre, llega a "
    "la misma tabla. Esto confirma la tabla de Leps 2.0 y permite usarla como la media de Leps 3.0 sin recalibrarla.")
filas = []
for c, nm in (("buena", "Buena"), ("moderada", "Moderada"), ("baja", "Baja")):
    filas.append([nm] + [f"{v[0]:.1f}° / {v[1]:.0f}°" for v in RS["tabla_phi1"][c].values()])
tabla(2, "Mediana de φ′1 en Leps 3.0 frente a Leps 2.0", ["Calidad de roca", "e = 0.30", "e = 0.45", "e = 0.60"],
      filas, [3.6, 3.6, 3.6, 3.6], "Fuente: elaboración propia; Leps 2.0 según Cylwik et al. (2025).",
      "Nota: cada celda indica Leps 3.0 / Leps 2.0 (φ′e=0 − 20e).")

titulo("4.2 Banda predictiva", 2)
par("La Figura 2 muestra la distribución predictiva del ángulo secante para un material nuevo de calidad moderada con "
    f"e = 0.45. La mediana baja de {P1['1']['50']}° a 1 MPa a {P1['10']['50']}° a 10 MPa. El intervalo de 80 % mide "
    f"{f1(P1['1']['90'] - P1['1']['10'])}° a 1 MPa y {f1(P1['10']['90'] - P1['10']['10'])}° a 10 MPa, y el percentil 10 "
    f"a 10 MPa es {P1['10']['10']}°. Sobre {f1(RS['sn_max'])} MPa la banda es una extrapolación del modelo.")
figura(2, FIG / "figP1_banda_predictiva.png", "Distribución predictiva del ángulo secante de un material nuevo de calidad moderada, e = 0.45",
       "Fuente: elaboración propia con datos de Arrieta (2025).")

titulo("4.3 Calibración fuera de muestra", 2)
par(f"Sin ensayos del sitio (modo A), el intervalo de 80 % contiene el {pc(A['cob80'])} de los {A['n']} ensayos y el de "
    f"90 %, el {pc(A['cob90'])}; el {pc(A['bajo10'])} de los ensayos queda bajo el percentil 10. La calibración se "
    "mantiene por rango de esfuerzo (Tabla 3 y Figura 3), con una tendencia a intervalos más anchos que lo necesario "
    "sobre 2.75 MPa, donde la fracción bajo el percentil 10 es menor que la nominal. La referencia con dispersión "
    "constante tiene una cobertura global parecida, pero es demasiado estrecha a bajo esfuerzo y demasiado ancha a alto "
    "esfuerzo, porque no modela el crecimiento de la incertidumbre con la distancia al anclaje ni su reducción en el "
    f"rango con más ensayos. Su CRPS es {A0['crps']:.4f}, frente a {A['crps']:.4f} de Leps 3.0.")
filas = []
for rg in COB.rango.unique():
    a = COB[(COB.rango == rg) & (COB.modelo == "Leps 3.0")].iloc[0]
    b = COB[(COB.rango == rg) & (COB.modelo != "Leps 3.0")].iloc[0]
    filas.append([rg, int(a.n), pc(a.cob80), pc(a.bajo10), pc(b.cob80), pc(b.bajo10)])
filas.append(["Total", A["n"], pc(A["cob80"]), pc(A["bajo10"]), pc(A0["cob80"]), pc(A0["bajo10"])])
tabla(3, "Calibración de los intervalos sin ensayos del sitio (evaluación dejando fuera cada publicación)",
      ["σ′_{n} (MPa)", "Ensayos", "Leps 3.0: cobertura 80 %", "Leps 3.0: bajo P10", "Dispersión constante: cobertura 80 %",
       "Dispersión constante: bajo P10"], filas, [2.4, 1.7, 2.9, 2.4, 3.2, 2.9],
      "Fuente: elaboración propia con datos de Arrieta (2025).",
      "Nota: valores nominales de 80 % y 10 %. La referencia usa la envolvente central de Leps 2.0 con una dispersión "
      "constante en ln τ.")
figura(3, FIG / "figP2_cobertura.png", "Calibración de los intervalos por rango de esfuerzo, sin ensayos del sitio",
       "Fuente: elaboración propia con datos de Arrieta (2025). Las líneas discontinuas son los valores nominales.")

titulo("4.4 Actualización con ensayos del sitio", 2)
par(f"En el modo B ({RS['B_sets']} sets, {RS['B_pub']} publicaciones, {B['n']} ensayos de σ′_{{n}} ≥ 2 MPa), se "
    "compararon las predicciones de los mismos ensayos sin y con los ensayos del sitio de σ′_{n} ≤ 1.5 MPa. Sin ellos, "
    f"el intervalo de 80 % contiene el {pc(AH['cob80'])} de esos ensayos y el {pc(AH['bajo10'])} queda bajo el percentil "
    f"10: para esos materiales, la previa es más ancha que lo necesario. Con la actualización, el ancho medio del "
    f"intervalo baja de {f2(AH['ancho80'])} a {f2(B['ancho80'])} en ln τ, es decir, a la mitad, con una cobertura de "
    f"{pc(B['cob80'])} y un {pc(B['bajo10'])} bajo el percentil 10, más cerca de los valores nominales. El CRPS es el "
    f"mismo en ambos casos ({AH['crps']:.3f} y {B['crps']:.3f}): los ensayos de baja presión no mejoran en promedio la "
    "mediana extrapolada, pero permiten usar una banda de la mitad del ancho sin perder la calibración.")
par("La Figura 4 muestra un caso del yacimiento de la sección 5: tres triaxiales drenados en probetas de 1 m de "
    f"diámetro de hornfels, con σ′_{{3}} de {P3['s3'][0]:.2f} a {P3['s3'][-1]:.2f} MPa. La previa, de calidad moderada y "
    f"e = 0.31, tiene φ′_{{1}} = {P3['phi1_previa']}° y una mediana que baja a {P3['previa']['10'][1]}° a 10 MPa. Los "
    "ensayos muestran un ángulo secante que no baja con el esfuerzo. La posterior sin restricción tiene "
    f"m = {P3['m_post']:.2f}; con m ≤ 1, la envolvente queda casi lineal, con mediana de {P3['post']['10'][1]}° e "
    f"intervalo de 80 % de {P3['post']['10'][0]}–{P3['post']['10'][2]}° a 10 MPa, frente a "
    f"{P3['previa']['10'][0]}–{P3['previa']['10'][2]}° de la previa. Ese intervalo estrecho supone que la curvatura "
    "observada hasta 4.3 MPa se mantiene más allá; a 10 MPa se está a más del doble del esfuerzo ensayado, y sobre "
    "13 MPa, fuera del dominio verificado (sección 2.5).")
figura(4, FIG / "figP3_actualizacion.png", "Actualización con tres ensayos de gran escala de hornfels del yacimiento de skarn",
       "Fuente: elaboración propia. Pares (σ′n, τ) de los ensayos calculados con m = 1.")

# ============================================================== 5
titulo("5. Aplicación al desmonte de un yacimiento de skarn")
titulo("5.1 Datos del sitio", 2)
par("El yacimiento es un skarn polimetálico en los Andes, con desmonte de mármol, hornfels, intrusivo, caliza y margas. "
    "Según el plan de minado, la composición en masa del desmonte es 39 % mármol, 19 % hornfels, 19 % margas y "
    "limolitas, 15 % intrusivo y 8 % caliza. Se compilaron y verificaron contra los informes originales los ensayos de "
    "laboratorio de 2010–2025: 64 triaxiales drenados utilizables en 22 sets, 32 en probetas de 0.6–1.0 m de diámetro y "
    "32 en probetas de 152 mm, con σ′_{3} de hasta 2.45 MPa. Se excluyeron ensayos repetidos entre informes, ensayos "
    "detenidos antes de la falla, ensayos cíclicos y ensayos no drenados. La falla se definió en el máximo desviador. La "
    "resistencia a compresión uniaxial de referencia se tomó de ensayos directos sobre testigos; el mármol es la "
    "litología más débil, con 48 MPa.")
titulo("5.2 Resultados de los ensayos", 2)
par("La Figura 5 compara el ángulo secante de los ensayos del sitio con la base de calibración. En probetas de gran "
    "escala, el exponente ajustado por set va de 0.88 a 1.0 entre 0.5 y 2.5 MPa, en la parte alta de la distribución poblacional "
    f"(media {fe['x']:.2f}). En el hornfels, el ángulo secante aumenta de 41.4° a 1 MPa a 46.5° a 2.45 MPa. Para "
    "σ′_{n} de 3–6 MPa, la mediana del sitio es 39.9° (percentil 10: 38.3°), frente a 37.8° (35.2°) de la base de "
    "calibración. El efecto de escala entre probetas de 152 mm y de 1 m es del orden de 1° en el hornfels.")
figura(5, FIGA / "figA1_phi_vs_s3.png", "Ángulo secante de los ensayos del yacimiento por litología y escala, sobre la base de calibración",
       "Fuente: elaboración propia con ensayos del yacimiento y datos de Arrieta (2025).")
par("La rotura de partículas, medida con el índice de Marsal (1967), es menor que en la base de calibración a igual "
    "σ′_{3}: 17 % frente a 29 % a 1 MPa (Figura 6). Su efecto depende de la litología. Con una densificación parecida "
    "durante la consolidación, el mármol pierde resistencia con la rotura (de 40° a 37°) y el hornfels la gana, lo que "
    "apunta a la mineralogía: el clivaje de la calcita frente a los silicatos angulosos del hornfels. Dentro de cada set, "
    "la relación de vacíos al inicio del corte explica parte del aplanamiento de la envolvente, pero es colineal con "
    "σ′_{3} y los datos no permiten separar ambos efectos. En mezclas de intrusivo con 9–13 % de relaves en "
    "co-disposición, φ′_{1} es 1.8° mayor que sin relaves; en material suelto de menos de 25 mm, la caída se concentra "
    "sobre 20 % de relaves.")
figura(6, FIGA / "figA2_Bg.png", "Índice de rotura de Marsal de los ensayos del yacimiento y de la base de calibración",
       "Fuente: elaboración propia con ensayos del yacimiento y datos de Arrieta (2025).")

titulo("5.3 Envolventes por litología", 2)
par("Para cada litología se combinó la previa de su calidad de roca, con e = 0.42 (mediana de los ensayos de gran escala "
    "del sitio), con las posteriores de sus sets sin relaves, cada una con su incertidumbre más la variabilidad entre "
    "materiales Σ. La caliza y las margas no tienen ensayos y conservan la previa. La Tabla 4 y la Figura 7 dan la "
    "envolvente de un material nuevo de cada litología, con m ≤ 1.")
filas = []
SNt = ["1.0", "3.0", "6.0", "10.0", "15.0"]
for lit, nm, pct in (("Hornfels", "Hornfels", 19), ("Intrusivo", "Intrusivo", 15), ("Mármol", "Mármol", 39),
                     ("Caliza", "Caliza y margas (sin ensayos)", 27)):
    r_ = LP.loc[lit]
    filas.append([nm, f"{pct} %", int(r_.n_sets), f"{grad(r_.theta):.1f}° / {r_.m:.2f}"] +
                 [f"{le(lit, 'P50', s):.1f} / {le(lit, 'P10', s):.1f}" for s in SNt])
filas.append(["Botadero (mezcla por masa)", "100 %", "", ""] + [f"{BE.loc[float(s), 'P50']:.1f} / {BE.loc[float(s), 'P10']:.1f}" for s in SNt])
tabla(4, "Ángulo secante φ′s (°) de un material nuevo de cada litología, P50 / P10",
      ["Litología", "Masa", "Sets", "φ′_{1} / m", "1 MPa", "3 MPa", "6 MPa", "10 MPa", "15 MPa"], filas,
      [2.7, 1.4, 1.1, 2.0, 1.75, 1.75, 1.75, 1.75, 1.75],
      "Fuente: elaboración propia con ensayos del yacimiento y datos de Arrieta (2025).",
      "Nota: φ′1 y m son las medias posteriores de la litología. Sobre σ′n ≈ 4 MPa no hay ensayos del sitio.")
figura(7, FIGA / "figA3_envolventes_litologia.png", "Envolventes P50 y P10 por litología del desmonte del yacimiento",
       "Fuente: elaboración propia con ensayos del yacimiento y datos de Arrieta (2025).")
par("El hornfels y el intrusivo, con exponentes posteriores de "
    f"{LP.loc['Hornfels', 'm']:.2f} y {LP.loc['Intrusivo', 'm']:.2f}, mantienen la resistencia a alta presión. El mármol, "
    f"con m = {LP.loc['Mármol', 'm']:.2f}, es la litología dominante y la que más la pierde. La caliza y las margas, sin "
    "ensayos, tienen la banda más ancha y son la mayor fuente de incertidumbre del botadero.")

titulo("5.4 Estabilidad de un botadero de 700 m", 2)
par("Se analizó un botadero genérico de 700 m con talud global 2H:1V, γ = 21 kN/m^3^ y fundación de roca competente "
    "horizontal, con el método de Bishop (1955) y la envolvente no lineal linealizada en la tangente al σ′_{n} de cada "
    "dovela. La implementación en Python reproduce los factores de seguridad de Slide2 9.043 (Rocscience, s. f.) con "
    "diferencias de 0.008 o menos. Se usaron tres envolventes para cada material (Tabla 5): la mediana; el percentil 10 "
    "de la envolvente media, que corresponde a la escala de la superficie de falla; y el percentil 10 puntual, que "
    "incluye la dispersión de un ensayo. Para el desmonte del yacimiento, la envolvente media del botadero promedia τ "
    "entre litologías ponderadas por masa, cada una con su incertidumbre, y trata la caliza y las margas como un solo "
    "material porque comparten la previa.")
filas = [["Material genérico, calidad moderada, e = 0.45", f2(FS["Genérico|P50"]), f2(FS["Genérico|P10 envolvente media"]),
          f2(FS["Genérico|P10 puntual"])],
         ["Desmonte del yacimiento (mezcla de litologías)", f2(FS["Skarn|P50 envolvente media del botadero"]),
          f2(FS["Skarn|P10 envolvente media del botadero"]), f2(FS["Skarn|P10 puntual"])]]
tabla(5, "Factor de seguridad del botadero de 700 m sobre fundación horizontal, método de Bishop",
      ["Material", "P50", "P10 de la envolvente media", "P10 puntual"], filas, [7.0, 2.0, 3.6, 2.6],
      "Fuente: elaboración propia.",
      f"Nota: σ′n máximo en la superficie crítica de {min(v['snmax'] for v in EJ.values()):.1f}–"
      f"{max(v['snmax'] for v in EJ.values()):.1f} MPa.")
par("Dos resultados orientan el diseño. En el material genérico, el FS con el percentil 10 de la envolvente media "
    f"({f2(FS['Genérico|P10 envolvente media'])}) casi coincide con el del percentil 10 puntual "
    f"({f2(FS['Genérico|P10 puntual'])}): la incertidumbre de un material sin ensayos está en cuál es su envolvente y no "
    "en la dispersión de sus ensayos, de modo que promediar a lo largo de la superficie no la reduce. En el desmonte del "
    f"yacimiento, en cambio, el promedio entre litologías sube el FS del percentil 10 de {f2(FS['Skarn|P10 puntual'])} a "
    f"{f2(FS['Skarn|P10 envolvente media del botadero'])}, porque los errores de litologías distintas son en parte "
    "independientes. La superficie crítica de este ejemplo llega a σ′_{n} ≈ 3 MPa, dentro del rango de la base; en un "
    "botadero sobre ladera o con debilidades en la fundación, el mecanismo puede bajar a esfuerzos de 6–15 MPa, donde la "
    "banda proviene de la extrapolación.")

titulo("5.5 Presión de poros", 2)
par("En la base de un botadero alto, el desmonte triturado tiene menor permeabilidad y puede responder de forma "
    "contractiva. La presión de poros por consolidación durante el crecimiento, calculada con la ecuación de Terzaghi con "
    "carga creciente, no supera 0.4 % de σ_{v} en una capa basal saturada de 30 m con k ≥ 10^−7^ m/s, aun con un "
    "crecimiento de 100 m/año; para llegar a Δu/σ_{v} = 0.1 se requiere k ≈ 10^−9^ m/s (Figura 8). El riesgo de presión "
    "de poros viene de la saturación de la base y de la respuesta no drenada de un material contractivo, como en los "
    "deslizamientos por licuación de botaderos de carbón (Dawson et al., 1998; Hungr et al., 2002), y no de la "
    "consolidación. Leps 3.0 describe la resistencia drenada; la no drenada requiere ensayos propios (sección 6).")
figura(8, FIG / "fig5_presion_poros_consolidacion.png",
       "Exceso de presión de poros por consolidación en la base de una capa saturada de 30 m al terminar un botadero de 700 m",
       "Fuente: elaboración propia. Módulo edométrico M = 50 MPa; con M = 150 MPa los valores se dividen por tres.")

# ============================================================== 6
titulo("6. Discusión")
titulo("6.1 Qué agrega un criterio probabilístico", 2)
par("Leps 3.0 no cambia la envolvente central de Leps 2.0; cambia lo que el criterio entrega. Para un material nuevo, "
    "entrega una distribución calibrada fuera de muestra, cuya banda crece con la distancia al anclaje y se puede "
    "leer en el percentil que pida el diseño. Con ensayos del sitio, entrega una regla analítica para combinarlos con la experiencia "
    "de la base mundial, que pesa más cuantos menos ensayos hay. Y para cada análisis, separa la incertidumbre de la "
    "envolvente media del material de la dispersión de un ensayo, una distinción que define qué percentil corresponde a "
    "una superficie de falla de gran tamaño.")
par(f"La descomposición de la varianza tiene una consecuencia práctica directa: a σ_{{0}}, el {pc(w_var)} de la "
    "varianza predictiva corresponde a diferencias entre materiales. Esa parte no se promedia en una superficie de falla "
    "dentro de un mismo material y solo se reduce con ensayos de ese material. El modo B muestra que unos pocos ensayos "
    "convencionales reducen el ancho de la banda a alta presión a la mitad. En términos de valor de información, el "
    "primer ensayo de gran escala de una litología sin ensayos vale más que repetir ensayos de una litología ya "
    "caracterizada; en el ejemplo, eso apunta a la caliza y las margas.")
titulo("6.2 Limitaciones", 2)
vineta(f"Los ensayos con σ′_{{n}} > 3 MPa provienen de {RS['n_pub_sn_gt3']} publicaciones, y no hay ensayos en la mitad "
       "inferior de un botadero de 700 m. Sobre 7.9 MPa, la forma y la banda son una extrapolación del modelo.")
vineta("La covarianza Σ se estimó con la base mundial. En un solo yacimiento, la variabilidad entre materiales de una "
       "misma litología es menor, de modo que la previa es conservadora para el sitio.")
vineta("El promedio entre litologías supone errores independientes entre ellas. Un sesgo común, como el de un "
       "laboratorio o un procedimiento de preparación, no se promedia; la variabilidad espacial dentro de la masa "
       "requiere un modelo de campo aleatorio (Vanmarcke, 1977; Phoon y Kulhawy, 1999).")
vineta("Las probetas usan granulometrías escalpadas o paralelas con D_{max} ≤ 200 mm, y su correspondencia con el "
       "material de campo depende de la razón entre el diámetro de la probeta y D_{max} (Girumugisha et al., 2024).")
vineta("Leps 3.0 describe la resistencia drenada. Para la base saturada de un botadero alto, la resistencia no drenada "
       "debe medirse en ensayos a alta presión sobre la granulometría triturada; mientras no existan, la razón "
       "S_{u}/σ′_{3c} = 0.28–0.29 de Valenzuela et al. (2008) sirve como valor de tamizaje.")
titulo("6.3 Un criterio que se actualiza", 2)
par("Leps 3.0 se define por sus parámetros poblacionales (β, μ_{m}, Σ y σ_{ε}) y por el procedimiento para estimarlos y "
    "evaluarlos, no por valores fijos. Cuando se publiquen ensayos drenados con σ′_{n} de 5–15 MPa, los parámetros se "
    "recalculan con el mismo programa, la evaluación dejando fuera cada publicación dirá si la ley de potencia sigue "
    "siendo suficiente o si conviene un término de estado crítico, y la cobertura de la banda extrapolada se podrá "
    "contrastar. La agenda que define la vigencia del criterio es concreta: triaxiales drenados de gran escala con "
    "σ′_{3} de 5–10 MPa en desmonte de distintas litologías, ensayos no drenados a alta presión sobre granulometrías "
    "trituradas, permeabilidad después de la rotura y monitoreo piezométrico en la base de botaderos altos.")

# ============================================================== 7
titulo("7. Conclusiones")
vineta("Leps 3.0 convierte el criterio de Leps 2.0 en un modelo jerárquico en el que φ′_{1} y m son variables aleatorias "
       "de cada material. Su mediana reproduce la tabla de Leps 2.0 con diferencias de "
       f"{f1(dmax_tab)}° o menos.")
vineta(f"Sin ensayos del sitio, el intervalo de 80 % contiene el {pc(A['cob80'])} de los ensayos de publicaciones no "
       f"usadas en la calibración, y el {pc(A['bajo10'])} queda bajo el percentil 10. La banda crece con la distancia "
       "al anclaje y cuantifica la incertidumbre de extrapolar a la base de botaderos altos.")
vineta("La actualización bayesiana conjugada con ensayos del sitio de baja presión reduce a la mitad el ancho de la "
       "banda a alta presión y mantiene su calibración.")
vineta(f"El {pc(w_var)} de la varianza corresponde a diferencias entre materiales: la incertidumbre se reduce con "
       "ensayos del material, no al promediar a lo largo de una superficie de falla. El promedio entre litologías "
       "independientes sí estrecha la envolvente de diseño de un botadero mixto.")
vineta("En el desmonte del yacimiento de skarn, los ensayos de gran escala muestran envolventes casi lineales hasta "
       "2.5 MPa en hornfels e intrusivo y una pérdida de resistencia con la rotura en el mármol, la litología "
       "dominante. Las litologías sin ensayos son la mayor fuente de incertidumbre.")

titulo("Disponibilidad de datos y programas")
par("La base de datos de calibración es pública (Arrieta, 2025). La implementación de referencia de Leps 3.0 (módulo en "
    "Python con pruebas), los parámetros calibrados y los programas de evaluación están disponibles en "
    "[[repositorio público por definir]]. Los ensayos del yacimiento son confidenciales; los valores agregados usados "
    "en la sección 5 se informan en el texto y las tablas.", sangria=False)

# ============================================================== referencias
doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
titulo("Referencias")
REFS = [
    "Arrieta, M. (2025). *Rockfill test database* [Base de datos]. Zenodo. https://doi.org/10.5281/zenodo.14665504",
    "Bishop, A. W. (1955). The use of the slip circle in the stability analysis of slopes. *Géotechnique*, *5*(1), 7–17. https://doi.org/10.1680/geot.1955.5.1.7",
    "Bolton, M. D. (1986). The strength and dilatancy of sands. *Géotechnique*, *36*(1), 65–78. https://doi.org/10.1680/geot.1986.36.1.65",
    "Cylwik, S. D., Arrieta, M., Cunning, J. C. y Hawley, P. M. (2025). Update to the Leps strength envelopes for rockfill based on 900 large-scale triaxial tests. *International Journal of Geomechanics*, *25*(12), 04025285. https://doi.org/10.1061/IJGNAI.GMENG-12050",
    "Dawson, R. F., Morgenstern, N. R. y Stokes, A. W. (1998). Liquefaction flowslides in Rocky Mountain coal mine waste dumps. *Canadian Geotechnical Journal*, *35*(2), 328–343. https://doi.org/10.1139/t98-009",
    "Girumugisha, G., Ovalle, C. y Ouellet, S. (2024). Grading scalping and sample size effects on critical shear strength of mine waste rock through laboratory and in-situ testing. *International Journal of Rock Mechanics and Mining Sciences*, *183*, 105915. https://doi.org/10.1016/j.ijrmms.2024.105915",
    "Gneiting, T. y Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *Journal of the American Statistical Association*, *102*(477), 359–378. https://doi.org/10.1198/016214506000001437",
    "Hungr, O., Dawson, R. F., Kent, A., Campbell, D. y Morgenstern, N. R. (2002). Rapid flow slides of coal-mine waste in British Columbia, Canada. En S. G. Evans y J. V. DeGraff (Eds.), *Catastrophic landslides: Effects, occurrence, and mechanisms* (pp. 191–208). Geological Society of America. https://doi.org/10.1130/REG15-p191",
    "Laird, N. M. y Ware, J. H. (1982). Random-effects models for longitudinal data. *Biometrics*, *38*(4), 963–974. https://doi.org/10.2307/2529876",
    "Leps, T. M. (1970). Review of shearing strength of rockfill. *Journal of the Soil Mechanics and Foundations Division*, *96*(4), 1159–1170. https://doi.org/10.1061/JSFEAQ.0001433",
    "Linero, S., Palma, C. y Apablaza, R. (2007). Geotechnical characterisation of waste material in very high dumps with large scale triaxial testing. En *Proceedings of the 2007 International Symposium on Rock Slope Stability in Open Pit Mining and Civil Engineering* (pp. 59–75). Australian Centre for Geomechanics. https://doi.org/10.36487/ACG_repo/708_2",
    "Marsal, R. J. (1967). Large scale testing of rockfill materials. *Journal of the Soil Mechanics and Foundations Division*, *93*(2), 27–43. https://doi.org/10.1061/JSFEAQ.0000958",
    "Ovalle, C., Linero, S., Dano, C., Bard, E., Hicher, P.-Y. y Osses, R. (2020). Data compilation from large drained compression triaxial tests on coarse crushable rockfill materials. *Journal of Geotechnical and Geoenvironmental Engineering*, *146*(9), 06020013. https://doi.org/10.1061/(ASCE)GT.1943-5606.0002314",
    "Phoon, K.-K. y Kulhawy, F. H. (1999). Characterization of geotechnical variability. *Canadian Geotechnical Journal*, *36*(4), 612–624. https://doi.org/10.1139/t99-038",
    "Rocscience. (s. f.). *Slide2* (versión 9.043) [Programa de cómputo]. Rocscience Inc.",
    "Seabold, S. y Perktold, J. (2010). Statsmodels: Econometric and statistical modeling with Python. En *Proceedings of the 9th Python in Science Conference* (pp. 92–96). https://doi.org/10.25080/Majora-92bf1922-011",
    "Valenzuela, L., Bard, E., Campaña, J. y Anabalón, M. E. (2008). High waste rock dumps: Challenges and developments. En *Proceedings of the First International Seminar on the Management of Rock Dumps, Stockpiles and Heap Leach Pads* (pp. 65–78). Australian Centre for Geomechanics. https://doi.org/10.36487/ACG_repo/802_6",
    "Vanmarcke, E. H. (1977). Probabilistic modeling of soil profiles. *Journal of the Geotechnical Engineering Division*, *103*(11), 1227–1246. https://doi.org/10.1061/AJGEB6.0000517",
]
for ref in REFS:
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Cm(1.0); p.paragraph_format.first_line_indent = Cm(-1.0)
    runs(p, ref)
out = AQUI / "Manuscrito_Leps3_probabilistico.docx"
doc.save(str(out)); print("escrito", out)
