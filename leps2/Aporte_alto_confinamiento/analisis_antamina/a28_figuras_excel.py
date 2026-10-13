"""Figuras del memo como gráficos nativos de Excel (revisión 12, pedido del usuario 2026-10-13: «que replique tal cual las figuras
del informe»). Lo llama a28_hoja_calculo.py. Escribe dos hojas:
  Datos_figuras: los datos de cada figura. Curvas, banda y ensayos con fórmulas ligadas a Parametros, Ensayos y Base_mundial;
                 φ′1 por set (a34), contraste CU (a16), Bg (a16) y perfil V como valores, con su fuente en la fila 1.
  Figuras: las seis figuras del memo con la misma numeración, series, colores, marcadores, tipos de línea, escalas y leyendas que
           a11, a16 y a34 (matplotlib). Excel no tiene relleno entre curvas en un gráfico de dispersión: la banda y la zona gris
           se dibujan con segmentos verticales anchos y el rayado con segmentos diagonales."""
import math
import numpy as np, pandas as pd
from openpyxl.chart import Reference, ScatterChart, Series
from openpyxl.chart.axis import ChartLines
from openpyxl.chart.legend import LegendEntry
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.chart.text import RichText
from openpyxl.drawing.line import LineProperties
from openpyxl.drawing.text import CharacterProperties, Paragraph, ParagraphProperties
from openpyxl.styles import Font

# paleta de a11 (dataviz)
INK2, MUTED, GRID, SURF = "52514E", "8A8984", "E6E5E1", "FCFCFB"
VIO, VIO_B, ZONA, RAYA, GRIS_M = "4A3AA7", "E3E0F3", "EFEEE9", "D2D1CB", "C9C8C2"
LIT = {"Mármol": ("2A78D6", "circle"), "Hornfels": ("EB6834", "square"), "Intrusivo": ("1BAF7A", "triangle"), "Mezcla": ("EDA100", "diamond")}
LIT_TXT = {"Mármol": "Mármol", "Hornfels": "Hornfels", "Intrusivo": "Intrusivo",
           "Mezcla": "Mezclas (Golder Associates Perú, 2021; Anddes Geolab, 2024)"}
# Leps (1970) e Indraratna et al. (1993) en la forma de la Ec. 9 de Leps 2.0 (m = 0.9); estilos de a11
FONDO = [("Leps (1970), envolvente superior", 46.0, "dashDot"), ("Leps (1970), envolvente media", 41.0, "dash"),
         ("Leps (1970), envolvente inferior", 36.0, "sysDot"), ("Cota inferior de Indraratna et al. (1993)", 33.0, "solid")]
NEG = Font(bold=True)


def _txt(sz):
    cp = CharacterProperties(sz=int(sz * 100))
    return RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), endParaRPr=cp)])


def _ln(color, w_pt, dash="solid"):
    return LineProperties(solidFill=color, w=int(w_pt * 12700), prstDash=dash)


def agregar(wb, *, HB, SNX, SNW, EB, TOPE, PE, PEM, A16BG, A16C, S34, N_AJ, NW, rbg, A36=None, P35=None, FIT=None, A38=None, WDF=None):
    wd = wb.create_sheet("Datos_figuras")
    wf = wb.create_sheet("Figuras", 1)
    col = [1]

    def bloque(titulo, cab, filas, ancho=11):
        c0 = col[0]
        wd.cell(1, c0, titulo).font = NEG
        for j, h in enumerate(cab):
            wd.cell(2, c0 + j, h).font = NEG
            wd.column_dimensions[wd.cell(2, c0 + j).column_letter].width = ancho
        for i, f in enumerate(filas):
            for j, v in enumerate(f):
                if v is not None and not (isinstance(v, float) and math.isnan(v)):
                    wd.cell(3 + i, c0 + j, v)
        col[0] += len(cab) + 1
        return c0, len(filas)

    L = lambda c, r: f"{wd.cell(r, c).column_letter}{r}"
    # fórmulas de la curva (nombres definidos de Parametros)
    phi_c = lambda x: f"DEGREES(ATAN(TAN(RADIANS(pe0-omega*e_base))*({x}/sref)^(m_-1)))"
    phi_e = lambda x, e: f"DEGREES(ATAN(TAN(RADIANS(pe0-omega*({e})))*({x}/sref)^(m_-1)))"
    lo_f = lambda x: "MIN(" + ",".join(f"DEGREES(ATAN(TAN(RADIANS(Parametros!$E${h}-omega*e_base))*({x}/sref)^(Parametros!$B${h}-1)))" for h in HB) + ")"
    hi_f = lambda x: "MAX(" + ",".join(f"DEGREES(ATAN(TAN(RADIANS(Parametros!$F${h}-omega*e_base))*({x}/sref)^(Parametros!$B${h}-1)))" for h in HB) + ")"
    l70 = lambda x, p1: f"DEGREES(ATAN(TAN(RADIANS({p1}))*({x}/sref)^(0.9-1)))"

    # ---------------------------------------------------------------- bloques de datos
    s_tope = 1.013 * (math.tan(math.radians(float(wb["Parametros"]["B2"].value) - 20 * EB)) / math.tan(math.radians(TOPE))) ** (1 / (1 - 0.85))
    xg = np.unique(np.round(np.concatenate([np.geomspace(0.01, 15, 110), [s_tope, SNX, SNW, 0.1, 1, 8]]), 5))
    filas = []
    for i, x in enumerate(xg):
        r = 3 + i; X = f"A{r}"   # se reubica abajo con el desplazamiento de columna
        filas.append([x])
    cG, nG = bloque("Curvas (fórmulas; a11, Figs. 2, 3 y 5)", ["σ′n (MPa)", "φ′s sin tope (°)", "φ′s curva con tope (°)", "φ′s sin tope, tramo sobre el tope (°)",
                    "Banda inf. (°)", "Banda sup. (°)"] + [nm for nm, _, _ in FONDO] + ["τ curva con tope (MPa)"] + [f"τ {nm}" for nm, _, _ in FONDO], filas)
    for i in range(nG):
        r = 3 + i; x = L(cG, r); ph = L(cG + 1, r)
        wd.cell(r, cG + 1, "=" + phi_c(x)); wd.cell(r, cG + 2, f"=MIN(tope,{ph})"); wd.cell(r, cG + 3, f"=IF({ph}>tope,{ph},NA())")
        wd.cell(r, cG + 4, "=" + lo_f(x)); wd.cell(r, cG + 5, "=" + hi_f(x))
        for j, (_, p1, _) in enumerate(FONDO):
            wd.cell(r, cG + 6 + j, "=" + l70(x, p1)); wd.cell(r, cG + 11 + j, f"={x}*TAN(RADIANS({L(cG + 6 + j, r)}))")
        wd.cell(r, cG + 10, f"={x}*TAN(RADIANS({L(cG + 2, r)}))")

    def banda_seg(titulo, xs, tau=False):
        """Segmentos verticales de la banda: (x, inf), (x, sup), vacío."""
        f = []
        for x in xs:
            f += [[x, None], [x, None], [None, None]]
        c0, n = bloque(titulo, ["σ′n (MPa)", "τ (MPa)" if tau else "φ′s (°)"], f)
        for i, x in enumerate(xs):
            for k, g in ((0, lo_f), (1, hi_f)):
                r = 3 + 3 * i + k; xc = L(c0, r)
                wd.cell(r, c0 + 1, f"={xc}*TAN(RADIANS({g(xc)}))" if tau else "=" + g(xc))
        return c0, n

    cB1, nB1 = banda_seg("Banda, segmentos (Figs. 2 y 3)", np.geomspace(0.1, 15, 130))
    cB2, nB2 = banda_seg("Banda τ, segmentos (Fig. 5)", np.linspace(0.02, 15, 170), tau=True)

    def zonas(titulo, y0, y1, log=True, xmax=15.0):
        """Zona gris (segmentos verticales entre SNX y SNW) y rayado (diagonales sobre SNW) en datos de la figura."""
        f = []
        for x in (np.geomspace(SNX, SNW, 26) if log else np.linspace(SNX, SNW, 26)):
            f += [[x, y0], [x, y1], [None, None]]
        # rayado ///: rectas a 45° en coordenadas de pantalla (eje x en décadas o MPa, eje y normalizado)
        u = (lambda x: math.log10(x)) if log else (lambda x: x)
        ui = (lambda v: 10 ** v) if log else (lambda v: v)
        a, b = u(SNW), u(xmax); paso = (b - a) / 7.0; k = (b - a) / 2.6   # pendiente de las rayas
        g = []
        v0 = a - k
        while v0 < b:
            pts = []
            for t in (0.0, 1.0):
                pts.append((v0 + k * t, t))
            (ua, ta), (ub, tb) = pts
            if ua < a:
                ta = ta + (a - ua) / k; ua = a
            if ub > b:
                tb = tb - (ub - b) / k; ub = b
            if ub > ua:
                g += [[None, None, ui(ua), y0 + ta * (y1 - y0)], [None, None, ui(ub), y0 + tb * (y1 - y0)], [None, None, None, None]]
            v0 += paso
        from itertools import zip_longest
        filas = [[*(fa or [None, None])[:2], *(gg or [None, None, None, None])[2:]] for fa, gg in zip_longest(f, g)]
        return bloque(titulo, ["Zona gris x", "Zona gris y", "Rayado x", "Rayado y"], filas)

    cZ1, nZ1 = zonas("Zonas Fig. 2 (valores)", 22, 56)
    cZ2, nZ2 = zonas("Zonas Fig. 5 (valores)", 0, 10.5, log=False)
    cZ3, nZ3 = zonas("Zonas Fig. 6b (valores)", 22, 58)

    # ensayos del ajuste (fórmulas ligadas a la hoja Ensayos, filas 2 a 1 + N_AJ)
    SER = [(l, tx) for l in LIT for tx in (True, False)]
    cE, nE = bloque("Ensayos del ajuste a e base (fórmulas; Ensayos!M y P)", ["σ′n (MPa)", "Todos φ′s (°)"] +
                    [f"{l} {'TX' if tx else 'DS'} φ′s" for l, tx in SER] + [f"{l} {'TX' if tx else 'DS'} τ" for l, tx in SER], [[None]] * N_AJ)
    for i in range(N_AJ):
        r = 3 + i; re_ = 2 + i
        wd.cell(r, cE, f"=Ensayos!M{re_}"); wd.cell(r, cE + 1, f"=Ensayos!P{re_}")
        for j, (l, tx) in enumerate(SER):
            cond = f'AND(Ensayos!$D{re_}="{l}",{"" if tx else "NOT("}LEFT(Ensayos!$E{re_},7)="Triaxia"{"" if tx else ")"})'
            wd.cell(r, cE + 2 + j, f"=IF({cond},Ensayos!P{re_},NA())")
            wd.cell(r, cE + 2 + len(SER) + j, f"=IF({cond},Ensayos!M{re_}*TAN(RADIANS(Ensayos!P{re_})),NA())")

    # base mundial llevada a e base (fórmulas ligadas a Base_mundial)
    cW, nW = bloque("Base mundial a e base (fórmulas; Base_mundial)", ["σ′n (MPa)", "φ′s a e base (°)", "τ a e base (MPa)"], [[None]] * NW)
    for i in range(NW):
        r = 3 + i; rb = 2 + i
        wd.cell(r, cW, f"=Base_mundial!C{rb}"); wd.cell(r, cW + 1, f"=Base_mundial!E{rb}-omega*(e_base-Base_mundial!B{rb})")
        wd.cell(r, cW + 2, f"={L(cW, r)}*TAN(RADIANS({L(cW + 1, r)}))")

    # Fig. 1: φ′1 por set (a34, valores) y rectas
    sets = [(l, ds) for l in LIT for ds in (False, True)]
    f = []
    for _, r in S34.iterrows():
        f.append([r.e0] + [r.phi1 if (r.litologia == l and bool(r.corte_directo) == ds) else None for l, ds in sets])
    cS, nS = bloque("Fig. 1: φ′1 por set (a34_phi1_sets.csv, m = 0.85)", ["e0 media"] + [f"{l} {'DS' if ds else 'TX'}" for l, ds in sets], f)
    cR, nR = bloque("Fig. 1: rectas (fórmulas)", ["e", "Curva propuesta"] + [nm for nm, _, _ in FONDO], [[0.0], [0.8]])
    for i in range(2):
        r = 3 + i
        wd.cell(r, cR + 1, f"=pe0-omega*{L(cR, r)}")
        for j, (_, p1, _) in enumerate(FONDO):
            wd.cell(r, cR + 2 + j, p1)

    # Fig. 6: perfiles de e
    zz = PE["z"]
    cP, nP = bloque("Fig. 6a: e con la profundidad (a13)", ["Profundidad (m)", "e perfil A", "e perfil V"],
                    [[z, a, v] for z, a, v in zip(zz, PE["e_A"], PE["e_V"])])
    cPb, _ = bloque("Fig. 6a: e base (fórmula)", ["Profundidad (m)", "e base"], [[0.0], [700.0]])
    wd.cell(3, cPb + 1, "=e_base"); wd.cell(4, cPb + 1, "=e_base")
    xs6 = np.geomspace(0.1, 15, 90)
    cQ, nQ = bloque("Fig. 6b: φ′s sin tope, como la Fig. 6 del memo (fórmulas; e perfil V como valor, a13)",
                    ["σ′n (MPa)", "e perfil A", "e perfil V", "φ′s e base (°)", "φ′s perfil A (°)", "φ′s perfil V (°)"],
                    [[x, None, (None if np.isnan(float(PEM.eV_of_sv(x))) else round(float(PEM.eV_of_sv(x)), 5))] for x in xs6])
    for i in range(nQ):
        r = 3 + i; x = L(cQ, r)
        wd.cell(r, cQ + 1, f"=IF(MAX({x},sv_piso)<=1,e_base-cc_bajo*LOG10(MAX({x},sv_piso)/sv_piso),e_base-cc_bajo*LOG10(1/sv_piso)-cc_alto*LOG10({x}))")
        wd.cell(r, cQ + 3, "=" + phi_e(x, 'e_base'))
        wd.cell(r, cQ + 4, "=" + phi_e(x, L(cQ + 1, r)))
        wd.cell(r, cQ + 5, f'=IF(ISNUMBER({L(cQ + 2, r)}),{phi_e(x, L(cQ + 2, r))},NA())')

    # Fig. 3: contraste CU (a16, valores)
    GRU = [("CU Anddes (2024), 6 in, máxima oblicuidad", "E87BA4", "square", "Triaxiales CU, Anddes (2024), 6 in"),
           ("CU Golder (2010), fase A, 2.8 y 4 in, máximo desviador", "008300", "triangle", "Triaxiales CU, Golder (2010), fase A")]
    f = []
    for _, r in A16C.iterrows():
        f.append([r.sn] + [r.phis_e065 if r.grupo == g else None for g, *_ in GRU])
    cC, nC = bloque("Fig. 3: triaxiales CU de contraste a e base (a16_contraste.csv)", ["σ′n (MPa)"] + [g[3] for g in GRU], f)

    # Fig. 4: Bg (a16, valores) y tendencia (fórmula)
    BGS = [(l, esc) for l in ("Hornfels", "Intrusivo", "Mármol") for esc in sorted(A16BG[A16BG.litologia == l].escala.unique())]
    f = []
    for _, r in A16BG.iterrows():
        f.append([r.s3, r.Bg] + [r.Bg if (r.litologia == l and r.escala == esc) else None for l, esc in BGS])
    cG4, nG4 = bloque("Fig. 4: Bg de Marsal (a16_bg.csv)", ["σ′3 (MPa)", "Bg (%)"] + [f"{l} {esc}" for l, esc in BGS], f)
    cT, nT = bloque("Fig. 4: tendencia lineal (fórmula)", ["σ′3 (MPa)", "Bg (%)"], [[0.0], [2.6]])
    xr = f"{L(cG4, 3)}:{L(cG4, 2 + nG4)}"; yr = f"{L(cG4 + 1, 3)}:{L(cG4 + 1, 2 + nG4)}"
    for i in range(2):
        wd.cell(3 + i, cT + 1, f"=INTERCEPT({yr},{xr})+SLOPE({yr},{xr})*{L(cT, 3 + i)}")

    # ---------------------------------------------------------------- gráficos
    def serie(ch, xc, yc, n, titulo, linea=None, marcador=None, msize=5, lleno=True, mcol=None, r0=3, leyenda=True):
        s = Series(Reference(wd, min_col=yc, min_row=r0, max_row=r0 + n - 1), Reference(wd, min_col=xc, min_row=r0, max_row=r0 + n - 1), title=titulo)
        s.smooth = False
        s.graphicalProperties = GraphicalProperties(ln=_ln(*linea) if linea else LineProperties(noFill=True))
        if marcador:
            s.marker.symbol = marcador; s.marker.size = msize
            s.marker.graphicalProperties = (GraphicalProperties(solidFill=mcol, ln=_ln(SURF if lleno and mcol != INK2 else mcol, 0.6)) if lleno
                                            else GraphicalProperties(noFill=True, ln=_ln(mcol, 1.2)))
        else:
            s.marker.symbol = "none"
        ch.series.append(s)
        if not leyenda:
            from openpyxl.chart.legend import Legend
            if ch.legend is None:
                ch.legend = Legend()
            ch.legend.legendEntry.append(LegendEntry(idx=len(ch.series) - 1, delete=True))
        return s

    def grafico(xt, yt, x0, x1, y0, y1, log=False, ymaj=None, w=17.0, h=15.0, invy=False):
        ch = ScatterChart(); ch.style = 13; ch.title = None; ch.scatterStyle = "lineMarker"
        ch.x_axis.title = xt; ch.y_axis.title = yt
        ch.x_axis.scaling.min, ch.x_axis.scaling.max = x0, x1
        ch.y_axis.scaling.min, ch.y_axis.scaling.max = y0, y1
        if log:
            ch.x_axis.scaling.logBase = 10
        if invy:
            ch.y_axis.scaling.orientation = "maxMin"; ch.x_axis.crosses = "max"
        else:
            ch.x_axis.crosses = "min"
        ch.y_axis.crosses = "min"
        if ymaj:
            ch.y_axis.majorUnit = ymaj
        for ax in (ch.x_axis, ch.y_axis):
            ax.delete = False
            ax.majorGridlines = ChartLines(spPr=GraphicalProperties(ln=_ln(GRID, 0.6)))
            ax.txPr = _txt(8); ax.number_format = "General"
            ax.spPr = GraphicalProperties(ln=_ln(MUTED, 0.75))
        ch.legend.position = "b"; ch.legend.txPr = _txt(7)
        ch.width, ch.height = w, h
        return ch

    def titulo(ch, texto):
        from openpyxl.chart.title import Title
        from openpyxl.chart.text import Text
        cp = CharacterProperties(sz=900, b=False)
        ch.title = Title(tx=Text(rich=RichText(p=[Paragraph(pPr=ParagraphProperties(defRPr=cp), r=[__import__("openpyxl").drawing.text.RegularTextRun(rPr=cp, t=texto)])])), overlay=False)

    def zonas_series(ch, cZ, nZ):
        serie(ch, cZ, cZ + 1, nZ, f"{SNX:.2f}–{SNW:.2f} MPa: sin ensayos de Antamina", linea=(ZONA, 4.5))
        serie(ch, cZ + 2, cZ + 3, nZ, f"Sobre {SNW:.2f} MPa: extrapolación", linea=(RAYA, 0.75))

    def fondo(ch, tau=False):
        for j, (nm, _, dash) in enumerate(FONDO):
            serie(ch, cG, cG + (11 if tau else 6) + j, nG, nm, linea=(MUTED, 1.1, dash))

    def ensayos(ch, tau=False):
        for j, (l, tx) in enumerate(SER):
            c_, mk = LIT[l]
            serie(ch, cE, cE + 2 + (len(SER) if tau else 0) + j, nE, f"{LIT_TXT[l]}, {'triaxial drenado' if tx else 'corte directo'}",
                  marcador=mk, msize=6, lleno=tx, mcol=c_)

    def mundo(ch, tau=False):
        serie(ch, cW, cW + (2 if tau else 1), nW, f"Base mundial de Leps 2.0 (Cylwik et al., 2025), llevada a e = {EB:.2f}",
              marcador="circle", msize=2, lleno=True, mcol=GRIS_M)

    XL = "Esfuerzo normal efectivo en el plano de falla, σ′n (MPa)"; YL = f"Ángulo de fricción secante, φ′s (°), a e = {EB:.2f}"
    figs = []
    # Fig. 1
    ch = grafico("Relación de vacíos inicial del ensayo, e0 (media del set)", "φ′1 del set (°), ángulo secante a σ′n = 10pa", 0.2, 0.55, 32, 50, ymaj=2, h=13)
    serie(ch, cR, cR + 1, 2, f"Curva propuesta: φ′1 = {float(wb['Parametros']['B2'].value):.1f}° − 20°·e", linea=(VIO, 2.2))
    for j, (nm, p1, dash) in enumerate(FONDO):
        serie(ch, cR, cR + 2 + j, 2, f"{nm} (φ′1 = {p1:.0f}°)", linea=(MUTED, 1.0, dash))
    for j, (l, ds) in enumerate(sets):
        if S34[(S34.litologia == l) & (S34.corte_directo == ds)].empty:
            continue
        c_, mk = LIT[l]
        serie(ch, cS, cS + 1 + j, nS, f"{'Mezclas' if l == 'Mezcla' else l}, {'corte directo' if ds else 'triaxial'}", marcador=mk, msize=7, lleno=not ds, mcol=c_)
    figs.append(("fig:phi1e", ch))
    # Fig. 2
    ch = grafico(XL, YL, 0.1, 15, 22, 56, log=True, ymaj=2)
    zonas_series(ch, cZ1, nZ1)
    serie(ch, cB1, cB1 + 1, nB1, "Incertidumbre de la curva", linea=(VIO_B, 4.0))
    mundo(ch); fondo(ch)
    serie(ch, cG, cG + 2, nG, f"Curva propuesta (m = 0.85), con tope de {TOPE:.0f}°", linea=(VIO, 2.4))
    serie(ch, cG, cG + 3, nG, "Curva sin tope", linea=(VIO, 1.2, "sysDot"))
    ensayos(ch)
    figs.append(("fig:phi", ch))
    # Fig. 3
    ch = grafico(XL, YL, 0.1, 8, 15, 60, log=True, ymaj=5, h=14)
    serie(ch, cB1, cB1 + 1, nB1, "Incertidumbre de la curva", linea=(VIO_B, 4.0))
    serie(ch, cG, cG + 1, nG, "Curva propuesta (m = 0.85)", linea=(VIO, 2.2))   # la Fig. 3 del memo (a16) no lleva tope
    fondo(ch)
    serie(ch, cE, cE + 1, nE, f"Ensayos del ajuste ({N_AJ}: triaxial CD y corte directo)", marcador="circle", msize=5, lleno=True, mcol=INK2)
    for j, (g, c_, mk, lab) in enumerate(GRU):
        serie(ch, cC, cC + 1 + j, nC, f"{lab} ({int((A16C.grupo == g).sum())})", marcador=mk, msize=6, lleno=False, mcol=c_)
    figs.append(("fig:contraste", ch))
    # Fig. 4
    ch = grafico("Esfuerzo efectivo de confinamiento, σ′3 (MPa)", "Índice de rotura de Marsal, Bg (%)", 0, 2.7, 0, 45, ymaj=5, h=11)
    COLB = {"Mármol": ("2A78D6", "circle"), "Hornfels": ("EB6834", "square"), "Intrusivo": ("1BAF7A", "triangle")}
    for j, (l, esc) in enumerate(BGS):
        c_, mk = COLB[l]
        serie(ch, cG4, cG4 + 2 + j, nG4, f"{l}, probeta de {esc}", marcador=mk, msize=7, lleno=esc != "6 in", mcol=c_)
    serie(ch, cT, cT + 1, 2, f"Tendencia lineal (r = {rbg:.2f})", linea=(INK2, 1.0, "dash"))
    ch.x_axis.majorUnit = 0.5
    figs.append(("fig:bg", ch))
    # Fig. 5
    ch = grafico(XL, "Resistencia al corte, τ (MPa)", 0, 15, 0, 10.5, ymaj=2, h=14)
    ch.x_axis.majorUnit = 2
    zonas_series(ch, cZ2, nZ2)
    serie(ch, cB2, cB2 + 1, nB2, "Incertidumbre de la curva", linea=(VIO_B, 3.0))
    mundo(ch, tau=True); fondo(ch, tau=True)
    serie(ch, cG, cG + 10, nG, f"Curva propuesta, e = {EB:.2f}, con tope de {TOPE:.0f}°", linea=(VIO, 2.4))
    ensayos(ch, tau=True)
    figs.append(("fig:tau", ch))
    # Fig. 6a y 6b
    cha = grafico("Relación de vacíos, e", "Profundidad bajo la superficie (m)", 0.08, 0.70, 0, 700, ymaj=100, w=8.5, h=12, invy=True)
    cha.x_axis.majorUnit = 0.04; cha.x_axis.number_format = "0.00"
    serie(cha, cPb + 1, cPb, 2, f"e = {EB:.2f} constante (base)", linea=(VIO, 2.0))
    serie(cha, cP + 1, cP, nP, "Perfil A, compresibilidad de Antamina", linea=("E87BA4", 2.0))
    serie(cha, cP + 2, cP, nP, "Perfil V, Valenzuela et al. (2008)", linea=("008300", 2.0))
    titulo(cha, "(a) Relación de vacíos")
    chb = grafico("σ′n (MPa)", "φ′s (°), curva propuesta", 0.1, 15, 22, 58, log=True, ymaj=4, w=12.5, h=12); titulo(chb, "(b) Ángulo de fricción secante")
    zonas_series(chb, cZ3, nZ3)
    fondo(chb)
    serie(chb, cQ, cQ + 3, nQ, f"e = {EB:.2f} constante (base)", linea=(VIO, 2.2))
    serie(chb, cQ, cQ + 4, nQ, "Perfil A, compresibilidad de Antamina", linea=("E87BA4", 2.0))
    serie(chb, cQ, cQ + 5, nQ, "Perfil V, Valenzuela et al. (2008)", linea=("008300", 2.0))
    figs.append(("fig:e", (cha, chb)))
    # ---------------------------------------------------------------- Fig. residuos (a36): datos con fórmulas ligadas a Ensayos
    if A36 is not None:
        from openpyxl.chart.error_bar import ErrorBars
        from openpyxl.chart.data_source import NumDataSource, NumRef
        # dispersión de la litología (d): la misma secuencia aleatoria que a36 (semilla 36), asignada a cada ensayo por (σ′n, e0)
        rng = np.random.default_rng(36); JIT = {}
        orden = ["Mármol", "Intrusivo", "Mezcla", "Hornfels"]
        for i, lit in enumerate(orden):
            for tipo in ("TX", "DS"):
                q = P35[(P35.litologia == lit) & (P35.tipo == tipo)]
                for (_, r), u in zip(q.iterrows(), rng.uniform(-0.18, 0.18, len(q))):
                    JIT[(round(r.sn, 5), round(r.e, 5))] = i + u
        cab = ["σ′n (MPa)", "ln σ′n", "Residuo curva propuesta, sin tope (°) = Ensayos!R", "Residuo m = 1 (°)", "x litología"] + \
              [f"{l} {'TX' if tx else 'DS'} (a)" for l, tx in SER] + [f"{l} {'TX' if tx else 'DS'} (b)" for l, tx in SER] + \
              [f"{l} {'TX' if tx else 'DS'} (d)" for l, tx in SER]
        cX, nX = bloque("Fig. residuos: residuo = φ′s medido − predicho, a σ′n y e0 del ensayo (fórmulas; Ensayos)", cab, [[None]] * N_AJ)
        for i in range(N_AJ):
            r = 3 + i; re_ = 2 + i; f_ = FIT.iloc[i]
            wd.cell(r, cX, f"=Ensayos!M{re_}"); wd.cell(r, cX + 1, f"=LN({L(cX, r)})")
            wd.cell(r, cX + 2, f"=Ensayos!R{re_}")   # Δφ′s ensayo − curva, sin tope (hoja Ensayos)
            wd.cell(r, cX + 3, f"=Ensayos!O{re_}-(Parametros!$C$17-omega*Ensayos!J{re_})")
            wd.cell(r, cX + 4, round(JIT[(round(f_.sn, 5), round(f_.e0, 5))], 6))
            for j, (l, tx) in enumerate(SER):
                cond = f'AND(Ensayos!$D{re_}="{l}",{"" if tx else "NOT("}LEFT(Ensayos!$E{re_},7)="Triaxia"{"" if tx else ")"})'
                for b, cc in enumerate((cX + 2, cX + 3, cX + 2)):
                    wd.cell(r, cX + 5 + b * len(SER) + j, f"=IF({cond},{L(cc, r)},NA())")
        R_ = lambda c: f"{L(c, 3)}:{L(c, 2 + nX)}"
        SN_, LN_ = R_(cX), R_(cX + 1)
        # medias por rango con IC 90 % (t de Student) y tendencia sobre ln σ′n
        BINS = [(0.1, 0.5), (0.5, 1.0), (1.0, 2.0), (2.0, 5.0)]
        cM, nM = bloque("Fig. residuos: medias por rango de σ′n (fórmulas)", ["Desde", "Hasta", "n", "σ′n media geom.", "Media (a)", "IC 90 % (a)",
                                                                              "Media (b)", "IC 90 % (b)"], [[a, b] for a, b in BINS])
        for i in range(len(BINS)):
            r = 3 + i; c1 = f'{SN_},">="&{L(cM, r)},{SN_},"<"&{L(cM + 1, r)}'
            wd.cell(r, cM + 2, f"=COUNTIFS({c1})"); wd.cell(r, cM + 3, f"=EXP(AVERAGEIFS({LN_},{c1}))")
            for k, cr in ((4, cX + 2), (6, cX + 3)):
                RR = R_(cr)
                wd.cell(r, cM + k, f"=AVERAGEIFS({RR},{c1})")
                wd.cell(r, cM + k + 1, f"=TINV(0.1,{L(cM + 2, r)}-1)*SQRT(SUMPRODUCT(({SN_}>={L(cM, r)})*({SN_}<{L(cM + 1, r)})*({RR}-{L(cM + k, r)})^2)/({L(cM + 2, r)}-1))/SQRT({L(cM + 2, r)})")
        cTr, nTr = bloque("Fig. residuos: tendencia sobre ln σ′n (fórmulas)", ["σ′n (MPa)", "Tendencia (a)", "Tendencia (b)", "", "Pendiente (a)", "r (a)", "Pendiente (b)", "r (b)"],
                          [[0.12], [4.8]])
        for k, cr in ((1, cX + 2), (2, cX + 3)):
            RR = R_(cr)
            for i in range(2):
                r = 3 + i
                wd.cell(r, cTr + k, f"=AVERAGE({RR})+SLOPE({RR},{LN_})*(LN({L(cTr, r)})-AVERAGE({LN_}))")
            wd.cell(3, cTr + 2 + 2 * k, f"=SLOPE({RR},{LN_})"); wd.cell(3, cTr + 3 + 2 * k, f"=CORREL({RR},{LN_})")
        # (c) medias por litología
        fl = []
        for i in range(4):
            fl += [[i - 0.3, None], [i + 0.3, None], [None, None]]
        cLm, nLm = bloque("Fig. residuos (d): media por litología (fórmulas)", ["x", "Media (°)"], fl)
        LITR = "Ensayos!$D$2:$D$" + str(1 + N_AJ)
        for i, lit in enumerate(orden):
            for k in range(2):
                wd.cell(3 + 3 * i + k, cLm + 1, f'=AVERAGEIF({LITR},"{lit}",{R_(cX + 2)})')
        cZ0, _ = bloque("Fig. residuos: línea cero", ["x (a, b)", "y", "x (d)", "y"], [[0.1, 0, -0.6, 0], [5.0, 0, 3.6, 0]])

        def err(s, cm, ce):
            cl = wd.cell(3, ce).column_letter; ref = f"'Datos_figuras'!${cl}$3:${cl}$6"
            s.errBars = ErrorBars(errDir="y", errBarType="both", errValType="cust", noEndCap=False,
                                  plus=NumDataSource(numRef=NumRef(f=ref)), minus=NumDataSource(numRef=NumRef(f=ref)),
                                  spPr=GraphicalProperties(ln=_ln(cm, 1.6)))

        def panel(titulo_y, b, col_med):
            ch = grafico("σ′n (MPa)", titulo_y, 0.1, 5, -16, 16, log=True, ymaj=4, w=12.5, h=11)
            serie(ch, cZ0, cZ0 + 1, 2, "Cero", linea=(INK2, 0.9), leyenda=False)
            for j, (l, tx) in enumerate(SER):
                c_, mk = LIT[l]
                serie(ch, cX, cX + 5 + b * len(SER) + j, nX, f"{'Mezclas' if l == 'Mezcla' else l}, {'triaxial drenado' if tx else 'corte directo'}",
                      marcador=mk, msize=5, lleno=tx, mcol=c_)
            s = serie(ch, cM + 3, cM + 4 + 2 * b, nM, "Media por rango de σ′n, IC 90 %", marcador="circle", msize=8, lleno=False, mcol=col_med)
            err(s, col_med, cM + 5 + 2 * b)
            serie(ch, cTr, cTr + 1 + b, 2, "Tendencia sobre ln σ′n", linea=(col_med, 1.2, "dash"))
            return ch

        cha = panel("Residuo: φ′s medido − predicho (°)", 0, VIO); titulo(cha, "(a) Curva propuesta (m = 0.85), sin tope")
        chb = panel("Residuo: φ′s medido − predicho (°)", 1, INK2); titulo(chb, "(b) Nivel reajustado con m = 1")
        chd = grafico("Litología", "Residuo de la curva propuesta (°)", -0.6, 3.6, -16, 16, ymaj=4, w=12.5, h=11)
        titulo(chd, "(c) Residuo por litología (raya: media)"); chd.x_axis.tickLblPos = "none"; chd.x_axis.number_format = ";;;"; chd.x_axis.majorGridlines = None
        from openpyxl.chart.label import DataLabelList
        cNm, _ = bloque("Fig. residuos (c): rótulos de litología", ["x", "y"], [[i, -15.4] for i in range(4)])
        for i, nm_ in enumerate(["Mármol", "Intrusivo", "Mezclas", "Hornfels"]):
            sl = serie(chd, cNm, cNm + 1, 1, nm_, r0=3 + i, leyenda=False)
            sl.dLbls = DataLabelList(showSerName=True, showVal=False, showCatName=False, showLegendKey=False, showPercent=False, dLblPos="ctr")
        chd.x_axis.majorUnit = 1
        serie(chd, cZ0 + 2, cZ0 + 3, 2, "Cero", linea=(INK2, 0.9), leyenda=False)
        for j, (l, tx) in enumerate(SER):
            c_, mk = LIT[l]
            s = Series(Reference(wd, min_col=cX + 5 + 2 * len(SER) + j, min_row=3, max_row=2 + nX), Reference(wd, min_col=cX + 4, min_row=3, max_row=2 + nX),
                       title=f"{'Mezclas' if l == 'Mezcla' else l}, {'triaxial drenado' if tx else 'corte directo'}")
            s.smooth = False; s.graphicalProperties = GraphicalProperties(ln=LineProperties(noFill=True))
            s.marker.symbol = mk; s.marker.size = 5
            s.marker.graphicalProperties = GraphicalProperties(solidFill=c_, ln=_ln(SURF, 0.6)) if tx else GraphicalProperties(noFill=True, ln=_ln(c_, 1.2))
            chd.series.append(s)
        serie(chd, cLm, cLm + 1, nLm, "Media por litología", linea=("0B0B0B", 2.0))
        figs.append(("fig:residuos", (cha, chb, chd)))
    # ---------------------------------------------------------------- Fig. prueba de extrapolación (a38)
    if A38 is not None:
        NAR, ROSA = "D55E00", "E87BA4"
        sx = A38["snx"]; EJ = A38["ejemplo"]
        # base mundial: sets con ensayos ≤ 2 MPa y > snx; filas ligadas a Base_mundial (mismo orden que la hoja)
        Wd = WDF.reset_index(drop=True); filas = []
        for s, g in Wd.groupby("Set"):
            lo, hi = g[g.sn <= 2.0], g[g.sn > sx]
            if len(lo) and len(hi):
                filas += [(i, "bajo") for i in lo.index] + [(i, "alto") for i in hi.index]
        filas.sort()
        cab = ["Set", "σ′n (MPa)", "τ (MPa)", "Rol", "φ′s medido (°)", "h m=0.85", "h m=1", "Nivel m=0.85", "Nivel m=1",
               "φ′s pred. m=0.85 (°)", "φ′s pred. m=1 (°)", "Error m=0.85 (°)", "Error m=1 (°)"]
        cWx, nWx = bloque(f"Fig. extrapolación (b): base mundial, nivel con σ′n ≤ 2 MPa, predicción sobre {sx:.2f} MPa (fórmulas; Base_mundial)", cab, [[None]] * len(filas))
        SETR, ROLR = None, None
        for j, (i, rol) in enumerate(filas):
            r = 3 + j; k = i + 2
            wd.cell(r, cWx, f"=Base_mundial!A{k}"); wd.cell(r, cWx + 1, f"=Base_mundial!C{k}"); wd.cell(r, cWx + 2, f"=Base_mundial!D{k}"); wd.cell(r, cWx + 3, rol)
            sn_, ta_ = L(cWx + 1, r), L(cWx + 2, r)
            wd.cell(r, cWx + 4, f"=DEGREES(ATAN({ta_}/{sn_}))")
            wd.cell(r, cWx + 5, f"=LN({ta_})-LN(sref^(1-0.85)*{sn_}^0.85)"); wd.cell(r, cWx + 6, f"=LN({ta_})-LN({sn_})")
        SETR, ROLR = R_ext = (f"{L(cWx, 3)}:{L(cWx, 2 + nWx)}", f"{L(cWx + 3, 3)}:{L(cWx + 3, 2 + nWx)}")
        for j in range(nWx):
            r = 3 + j; sn_ = L(cWx + 1, r)
            for b, m in enumerate((0.85, 1.0)):
                hR = f"{L(cWx + 5 + b, 3)}:{L(cWx + 5 + b, 2 + nWx)}"
                wd.cell(r, cWx + 7 + b, f'=AVERAGEIFS({hR},{SETR},{L(cWx, r)},{ROLR},"bajo")')
                wd.cell(r, cWx + 9 + b, f'=IF({L(cWx + 3, r)}="alto",DEGREES(ATAN(EXP({L(cWx + 7 + b, r)})*sref^(1-{m})*{sn_}^{m}/{sn_})),NA())')
                wd.cell(r, cWx + 11 + b, f'=IF({L(cWx + 3, r)}="alto",{L(cWx + 9 + b, r)}-{L(cWx + 4, r)},NA())')
        # Antamina: triaxiales de sets con 3 o más σ′3; nivel con los dos menores, se predice el mayor (σ′n y τ con cada m)
        tx = FIT[FIT.ensayo.str.startswith("Triaxial")].copy(); tx["key"] = tx.fuente_id + "|" + tx.set_id.astype(str)
        tx["fila"] = [FIT.index.get_loc(i) + 2 for i in tx.index]
        filasA = []
        for s, g in tx.groupby("key"):
            if g.s3.nunique() >= 3:
                mx = g.s3.max(); filasA += [(int(f), "alto" if s3 == mx else "bajo", s) for f, s3 in zip(g.fila, g.s3)]
        filasA.sort()
        cabA = ["Set", "σ′3 (MPa)", "σ′1 (MPa)", "Rol"] + [f"{t} m={m}" for m in ("0.85", "1") for t in ("sin φ", "σ′n", "τ", "φ′s medido", "h", "Nivel", "φ′s pred.", "Error")]
        cAx, nAx = bloque("Fig. extrapolación (c): Antamina, nivel con los dos menores σ′3, predicción del mayor (fórmulas; Ensayos)", cabA, [[None]] * len(filasA))
        SETA, ROLA = f"{L(cAx, 3)}:{L(cAx, 2 + nAx)}", f"{L(cAx + 3, 3)}:{L(cAx + 3, 2 + nAx)}"
        for j, (k, rol, s) in enumerate(filasA):
            r = 3 + j
            wd.cell(r, cAx, s); wd.cell(r, cAx + 1, f"=Ensayos!K{k}"); wd.cell(r, cAx + 2, f"=Ensayos!L{k}"); wd.cell(r, cAx + 3, rol)
            s3_, s1_ = L(cAx + 1, r), L(cAx + 2, r); D_, S_ = f"({s1_}-{s3_})", f"({s1_}+{s3_})"
            for b, m in enumerate((0.85, 1.0)):
                c0 = cAx + 4 + 8 * b
                wd.cell(r, c0, f"={D_}/{S_}" if m == 1.0 else f"=(SQRT(4*{m}*({m}-1)*{D_}^2+{S_}^2)-{S_})/(2*({m}-1)*{D_})")
                sp = L(c0, r)
                wd.cell(r, c0 + 1, f"={S_}/2-{D_}/2*{sp}"); wd.cell(r, c0 + 2, f"={D_}/2*SQRT(1-{sp}^2)")
                sn_, ta_ = L(c0 + 1, r), L(c0 + 2, r)
                wd.cell(r, c0 + 3, f"=DEGREES(ATAN({ta_}/{sn_}))")
                wd.cell(r, c0 + 4, f"=LN({ta_})-LN(sref^(1-{m})*{sn_}^{m})")
                hR = f"{L(c0 + 4, 3)}:{L(c0 + 4, 2 + nAx)}"
                wd.cell(r, c0 + 5, f'=AVERAGEIFS({hR},{SETA},{L(cAx, r)},{ROLA},"bajo")')
                wd.cell(r, c0 + 6, f'=IF({L(cAx + 3, r)}="alto",DEGREES(ATAN(EXP({L(c0 + 5, r)})*sref^(1-{m})*{sn_}^{m}/{sn_})),NA())')
                wd.cell(r, c0 + 7, f'=IF({L(cAx + 3, r)}="alto",{L(c0 + 6, r)}-{L(c0 + 3, r)},NA())')
        # resumen (sesgo y sobreestimados)
        cRs, _ = bloque("Fig. extrapolación: resumen (fórmulas)", ["Población", "m", "n", "Sesgo (°)", "Medio absoluto (°)", "Sobreestimados"],
                        [["Base mundial", 0.85], ["Base mundial", 1.0], ["Antamina", 0.85], ["Antamina", 1.0]])
        for i, (cE_, n_) in enumerate(((cWx + 11, nWx), (cWx + 12, nWx), (cAx + 11, nAx), (cAx + 19, nAx))):
            r = 3 + i; RR = f"{L(cE_, 3)}:{L(cE_, 2 + n_)}"
            wd.cell(r, cRs + 2, f"=COUNT({RR})"); wd.cell(r, cRs + 3, f"=AVERAGEIF({RR},\"<1E9\")")
            wd.cell(r, cRs + 4, f"=SUMPRODUCT(ISNUMBER({RR})*ABS(IFERROR({RR},0)))/COUNT({RR})"); wd.cell(r, cRs + 5, f'=COUNTIF({RR},">0")')
        RS = A38["resumen"]
        # (a) ejemplo
        ge = Wd[Wd.Set == EJ]
        cEj, nEj = bloque(f"Fig. extrapolación (a): ejemplo {EJ} (fórmulas)", ["σ′n bajo", "φ′s bajo", "σ′n alto", "φ′s alto", "σ′n otros", "φ′s otros"],
                          [[None]] * len(ge))
        for j, (i, rr) in enumerate(ge.iterrows()):
            r = 3 + j; k = i + 2; grupo = 0 if rr.sn <= 2.0 else (1 if rr.sn > sx else 2)
            wd.cell(r, cEj + 2 * grupo, f"=Base_mundial!C{k}"); wd.cell(r, cEj + 2 * grupo + 1, f"=DEGREES(ATAN(Base_mundial!D{k}/Base_mundial!C{k}))")
        xs_ = np.geomspace(0.1, 12, 40)
        cEc, nEc = bloque("Fig. extrapolación (a): curvas del ejemplo (fórmulas)", ["σ′n (MPa)", "m = 0.85", "m = 1"], [[x] for x in xs_])
        r_ej = 3 + [j for j, (i, _) in enumerate(filas) if Wd.Set[i] == EJ][0]
        for j in range(nEc):
            r = 3 + j; x = L(cEc, r)
            for b, m in enumerate((0.85, 1.0)):
                wd.cell(r, cEc + 1 + b, f"=DEGREES(ATAN(EXP(${L(cWx + 7 + b, r_ej).rstrip('0123456789')}${r_ej})*sref^(1-{m})*{x}^{m}/{x}))")
        fz = []
        for x in np.geomspace(sx, 12, 18):
            fz += [[x, 34], [x, 56], [None, None]]
        cZe, nZe = bloque("Fig. extrapolación (a): zona sobre el umbral (valores)", ["x", "y"], fz)
        cL1, _ = bloque("Fig. extrapolación (b, c): recta 1:1 y referencias de (d)", ["x", "y", "", "m", "y", "", "m", "y", "", "m", "y"],
                        [[20, 20, None, 0.85, -9, None, 1.0, -9, None, 0.75, 0], [60, 60, None, 0.85, 9, None, 1.0, 9, None, 1.05, 0]])
        BR = A38["barrido"]
        cBr, nBr = bloque("Fig. extrapolación (d): sesgo según m (a31_m_defendible.json)", ["m", "Base mundial (°)", "Antamina (°)"],
                          [[b_["m"], b_["mundo"], b_["antamina"]] for b_ in BR])
        E_ = A38["ejes"]
        cha = grafico("σ′n (MPa)", "φ′s (°)", 0.1, 12, 34, 56, log=True, ymaj=2, w=12.5, h=11); titulo(cha, "(a) Ejemplo: " + " · ".join(x.strip() for x in EJ.split("|")))
        serie(cha, cZe, cZe + 1, nZe, f"Sobre {sx:.2f} MPa: se predice", linea=(ZONA, 4.5))
        serie(cha, cEc, cEc + 1, nEc, "m = 0.85 (curva propuesta)", linea=(VIO, 2.0))
        serie(cha, cEc, cEc + 2, nEc, "m = 1 (lineal, como Antamina)", linea=(NAR, 2.0, "dash"))
        serie(cha, cEj + 4, cEj + 5, nEj, "Otros ensayos del set", marcador="circle", msize=4, mcol=GRIS_M)
        serie(cha, cEj, cEj + 1, nEj, "Ensayos con σ′n ≤ 2 MPa: fijan el nivel", marcador="circle", msize=6, mcol=INK2)
        serie(cha, cEj + 2, cEj + 3, nEj, f"Ensayos sobre {sx:.2f} MPa: se predicen", marcador="square", msize=7, lleno=False, mcol="0B0B0B")

        def unoauno(xr, yr, pob, cpob, npob, c85, c1):
            ch = grafico("φ′s medido (°)", "φ′s predicho (°)", xr[0], xr[1], yr[0], yr[1], ymaj=4, w=12.5, h=11)
            ch.x_axis.majorUnit = 4
            serie(ch, cL1, cL1 + 1, 2, "1:1", linea=(INK2, 0.9), leyenda=False)
            for m, cc, mk, ll in ((0.85, c85, "circle", True), (1.0, c1, "square", False)):
                r_ = RS[f"{pob}|{m}"]
                serie(ch, cpob[0], cpob[1 if m == 0.85 else 2], npob, f"m = {m:.2f}: sesgo {r_['sesgo']:+.1f}°, {r_['sobre']} de {r_['n']} sobreestimados".replace("-", "−"),
                      marcador=mk, msize=5, lleno=ll, mcol=cc)
            return ch
        chb = unoauno((32, 52), (32, 56), "Base mundial", (cWx + 4, cWx + 9, cWx + 10), nWx, VIO, NAR); titulo(chb, f"(b) Base mundial: ensayos sobre {sx:.2f} MPa")
        chc = unoauno((28, 50), (28, 56), "Antamina", (cAx + 7, cAx + 10, cAx + 10 + 8), nAx, VIO, NAR); titulo(chc, "(c) Antamina: ensayo de mayor σ′3 de cada set")
        # en (c) el φ′s medido depende de m (conversión): cada serie usa su propio medido
        chc.series[1].xVal.numRef.f = f"'Datos_figuras'!${L(cAx + 7, 3).rstrip('0123456789')}$3:${L(cAx + 7, 3).rstrip('0123456789')}${2 + nAx}"
        chc.series[2].xVal.numRef.f = f"'Datos_figuras'!${L(cAx + 15, 3).rstrip('0123456789')}$3:${L(cAx + 15, 3).rstrip('0123456789')}${2 + nAx}"
        chd = grafico("Exponente de curvatura, m", "Sesgo medio de la predicción (°)", 0.75, 1.05, -9, 9, ymaj=3, w=12.5, h=11); titulo(chd, "(d) Sesgo según m: ningún m anula los dos")
        chd.x_axis.majorUnit = 0.05; chd.x_axis.number_format = "0.00"
        serie(chd, cL1 + 9, cL1 + 10, 2, "Cero", linea=(INK2, 0.9), leyenda=False)
        serie(chd, cL1 + 3, cL1 + 4, 2, "m = 0.85", linea=(VIO, 0.9, "sysDash"), leyenda=False)
        serie(chd, cL1 + 6, cL1 + 7, 2, "m = 1", linea=(NAR, 0.9, "sysDash"), leyenda=False)
        serie(chd, cBr, cBr + 1, nBr, f"Base mundial ({sx:.2f}–{A38['sn_mundo_max']:.2f} MPa)", linea=(VIO, 2.0))
        serie(chd, cBr, cBr + 2, nBr, f"Antamina (hasta {sx:.2f} MPa)", linea=(ROSA, 2.0))
        from openpyxl.chart.label import DataLabelList
        y85 = float(np.interp(0.85, [b_["m"] for b_ in BR], [b_["mundo"] for b_ in BR])); y1 = float(np.interp(1.0, [b_["m"] for b_ in BR], [b_["mundo"] for b_ in BR]))
        cPt, _ = bloque("Fig. extrapolación (d): sesgo en m = 0.85 y m = 1 (base mundial)", ["m", "Sesgo (°)"], [[0.85, y85], [1.0, y1]])
        for i_, (cc_, pos_) in enumerate(((VIO, "t"), (NAR, "l"))):
            sp_ = serie(chd, cPt, cPt + 1, 1, f"m = {(0.85, 1.0)[i_]:g}", marcador="circle", msize=5, lleno=True, mcol=cc_, r0=3 + i_, leyenda=False)
            sp_.dLbls = DataLabelList(showSerName=True, showVal=True, showCatName=False, showLegendKey=False, showPercent=False, dLblPos=pos_, separator=": ")
            from openpyxl.chart.data_source import NumFmt
            sp_.dLbls.numFmt = None
            wd.cell(3 + i_, cPt + 1).number_format = '+0.0"°";-0.0"°"'
        figs.append(("fig:extrap", (cha, chb, chc, chd)))
    return wf, figs


def colocar(wf, figs, rotulos):
    """Coloca las figuras en la hoja Figuras, una bajo la otra, con su número y título del memo."""
    fila = 1
    wf.column_dimensions["A"].width = 3
    wf.sheet_properties.pageSetUpPr.fitToPage = True; wf.page_setup.fitToWidth = 1; wf.page_setup.fitToHeight = 0
    wf.page_setup.orientation = "portrait"; wf.page_setup.paperSize = wf.PAPERSIZE_A4
    wf.cell(fila, 2, "Figuras del memorándum, recalculadas con las fórmulas de este libro (datos en Datos_figuras). "
                     "La banda y la zona gris se dibujan con segmentos verticales; el rayado, con segmentos diagonales.").font = Font(italic=True)
    fila += 2
    figs = sorted(figs, key=lambda f: int(rotulos.get(f[0], ("999", ""))[0] or 999))
    for lab, ch in figs:
        num, tit = rotulos.get(lab, ("", ""))
        wf.cell(fila, 2, f"Figura {num}. {tit}").font = NEG
        fila += 1
        if isinstance(ch, tuple) and len(ch) == 4:
            wf.add_chart(ch[0], f"B{fila}"); wf.add_chart(ch[1], f"N{fila}")
            fila += int(ch[0].height / 0.5) + 2
            wf.add_chart(ch[2], f"B{fila}"); wf.add_chart(ch[3], f"N{fila}"); h = ch[2].height
        elif isinstance(ch, tuple) and len(ch) == 3:
            wf.add_chart(ch[0], f"B{fila}"); wf.add_chart(ch[1], f"N{fila}")
            fila += int(ch[0].height / 0.5) + 2
            wf.add_chart(ch[2], f"B{fila}"); h = ch[2].height
        elif isinstance(ch, tuple):
            wf.add_chart(ch[0], f"B{fila}"); wf.add_chart(ch[1], f"J{fila}"); h = ch[0].height
        else:
            wf.add_chart(ch, f"B{fila}"); h = ch.height
        fila += int(h / 0.5) + 3
