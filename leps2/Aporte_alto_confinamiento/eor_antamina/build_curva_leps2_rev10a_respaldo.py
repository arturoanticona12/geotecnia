"""Memorándum técnico de Stantec para Antamina: curva de resistencia Leps 2.0 del desmonte y su incertidumbre a alto
confinamiento. Revisión 3 (2026-10-09), tras la segunda ronda de revisión (EoR Piteau, líder técnico de Stantec LE2, líder de
geotecnia de Antamina): margas y caliza con la resistencia del mármol, banda propia de la curva propuesta (curva media y total, con ω y e),
matriz de aplicación por zona, pares σ′n–τ por e y parámetros de Power Curve, Tabla 5 y sensibilidades recalculadas con la curva
vigente (lote 78, con control de convergencia), programa de ensayos con cantidades, riesgos y cláusulas revisadas (SMKC).
Curvas sin tope (decisión del usuario). Todos los números se leen de los resultados (analisis_antamina/a9–a15, drenados_utilizables.csv).
Revisión 9 (2026-10-12, comentarios de WA): curva ajustada con todos los ensayos con igual peso (control: producción por litología
del DDE, 44/56); sin resultados de Slide2 (curva nueva, sin recalcular); sin curva del mármol, de margas y caliza ni aplicación por
sector (el DDE trata el desmonte ROM como un solo material); anexo con todos los ensayos de resistencia y su uso (a27).
Revisión 10 (2026-10-12, WA): curva simple con m = 0.85 en todo el rango (a33; m sin sesgo en los ensayos mundiales de mayor
esfuerzo, a31), e0 con el Gs D854 de Golder (2010) en todos los ensayos (a8), triaxiales convertidos con m = 0.85; referencias de
fondo: Leps (1970) e Indraratna et al. (1993) con φ′1 = 33° sin dependencia de e (Cylwik et al. 2025, Tabla 1).
Escribe el .tex; compilar aparte con pdflatex dos veces (MiKTeX en %LOCALAPPDATA%\\Programs\\MiKTeX\\miktex\\bin\\x64)."""
import json, math, shutil, re, sys
from pathlib import Path
import numpy as np, pandas as pd

AQ = Path(__file__).parent; AA = AQ.parent / "analisis_antamina"; FIG = AA / "figuras_leps2"
(AQ / "figs").mkdir(exist_ok=True)
for f in ("Fig1_phi_sigma.pdf", "Fig2_tau_sigma.pdf", "Fig3_perfil_e.pdf", "Fig4_contraste.pdf", "Fig5_bg.pdf"):
    shutil.copy2(FIG / f, AQ / "figs" / f)
J = lambda n: json.load(open(AA / n, encoding="utf-8"))
R9, C, A12, PE = J("a9_leps2_antamina.json"), J("a10_leps2_curvatura.json"), J("a12_leps2_ponderada.json"), J("a13_perfil_e.json")
sys.path.insert(0, str(AA)); import a13_perfil_e as PEM  # noqa: E402  (e_A y eV_of_sv para los pares por perfil)
P = pd.read_csv(AA / "a10_puntos.csv"); D = pd.read_csv(AA / "drenados_utilizables.csv", low_memory=False)
S0, OM, EC = 1.013, 20.0, 0.45                    # e base 0.45 (γ del DDE; decisión del usuario, 2026-10-10); curvas sin tope
EB_TXT = f"{EC:.2f}"
EG = lambda gam, w: 2.75 * 9.81 * (1 + w) / gam - 1            # e con Gs 2.75 a partir del peso unitario total y la humedad
REPOSO = 37.0                                     # ángulo de reposo típico de caras de volteo (Hawley y Cunning 2017, §16.5): cruce y verificación de caras
CV = C["curvas"]; C2 = A12["curvas"]; OP2 = C2["Curva propuesta (mediana mundial)"]; MAR = A12["marmol"]["central"]; W = R9["mundial"]; MC = OP2["m"]
# revisión 10: curva simple (a33): m = 0.85, nivel con m = 0.85; desviación estándar del nivel por bootstrap de sets
A33 = J("a33_curva_propuesta.json"); A31 = J("a31_m_defendible.json"); NIV = A33["nivel"]
OP2 = dict(pe0=A33["parametros"]["pe0"], m=A33["parametros"]["m_a"], sd_pe0=NIV["m085"]["sd"]); MC = OP2["m"]
_S34 = pd.read_csv(AA / "a34_phi1_sets.csv")                                  # φ′1 por set con m = 0.85 y e0 media del set
_ml = _S34.groupby("litologia").phi_e0.mean()
OP2["pe0_dde"] = float(0.28 * _ml["Mármol"] + 0.28 * _ml["Hornfels"] + 0.44 * _ml["Intrusivo"])   # control DDE 44/56
_rng = np.random.default_rng(10); _nn = 200000                                 # σ de φ′1 con nivel, ω de 15 a 25° y e de 0.35 a 0.55
_ph = _rng.normal(_S34.phi1.mean(), OP2["sd_pe0"], _nn) + _rng.uniform(15, 25, _nn) * (_S34.e0.mean() - _rng.uniform(0.35, 0.55, _nn))
OP2["sd_phi1_total"] = float(np.std(_ph)); M_SB, M_IC = A31["m_sin_sesgo"]["mundo"], A31["m_sin_sesgo_mundo_ic90"]
M_MED = A31["estimadores"]["Mundo, todos los sets (mediana; P10–P90)"]["m"]
R18 = J("a18_m_jerarquico.json"); RM = R18["variantes"]["rango completo"]; RA = R18["antamina"]               # m de la base mundial (a18)
R19 = J("a19_m_covariables.json")                                                                                # covariables de m (a19)
FIS = (AQ / "flac" / "leps2_tangente.fis").read_text(encoding="utf-8")
FIS_TXT = FIS[FIS.index("fish define leps_tangente"):].rstrip()               # librería FISH completa para el memo
# c′ y φ′ tangentes de la curva propuesta (e base) a varios σ′3, para la tabla de verificación de FLAC2D
def tangente(s3, pe0=None, e=EC):
    pe0 = OP2["pe0"] if pe0 is None else pe0; a_ = math.tan(math.radians(pe0 - OM * e)) * S0 ** (1 - MC); lo_, hi_ = math.log(s3), math.log(40 * s3)
    for _ in range(80):
        mid = 0.5 * (lo_ + hi_); sn_ = math.exp(mid); t_ = a_ * sn_ ** MC; b_ = 0.5 * math.atan(MC * t_ / sn_) + math.pi / 4
        lo_, hi_ = (lo_, mid) if sn_ - t_ / math.tan(b_) - s3 > 0 else (mid, hi_)
    sn_ = math.exp(0.5 * (lo_ + hi_)); t_ = a_ * sn_ ** MC; tf = MC * t_ / sn_
    return sn_, t_, math.degrees(math.atan(tf)), (1 - MC) * t_
filas_flac = []
for s3_ in (0.1, 0.5, 1.0, 2.0, 5.0):
    sn_, t_, ft_, ct_ = tangente(s3_)
    q_ = 2 * t_ / math.cos(math.radians(ft_))                                  # σ′1 − σ′3 = 2R, R = τ/cos φ′t
    filas_flac.append(f"{s3_:.1f} & {sn_:.3f} & {t_ * 1000:.1f} & {ft_:.1f} & {ct_ * 1000:.1f} & {q_:.3f}" + r" \\")
SNW = R19["base_sn_max"]                                                                                         # σ′n máximo de la base mundial de Leps 2.0
# cota inferior de Indraratna et al. (1993) en la forma de Leps 2.0 (Cylwik et al. 2025, Tabla 1, p. 3): Ec. 9, φ′1 = 33°, m = 0.9, sin e
LB = lambda s, e=None: math.degrees(math.atan(math.tan(math.radians(33.0)) * (s / S0) ** (0.9 - 1)))
L70 = lambda s, p1: math.degrees(math.atan(math.tan(math.radians(p1)) * (s / S0) ** (0.9 - 1)))   # Leps (1970): 36, 41 y 46° (Cylwik p. 2)
PMG = MAR["pe0"] - A12["dclase"]                  # margas y caliza dominantes, provisional: una clase Leps 2.0 bajo el mármol
tau_l = lambda sn, pe0, m, e=EC: math.tan(math.radians(pe0 - OM * e)) * S0 ** (1 - m) * sn ** m
phis = lambda sn, pe0, m, e=EC: math.degrees(math.atan(tau_l(sn, pe0, m, e) / sn))
tau = lambda sn, pe0, m, e=EC: tau_l(sn, pe0, m, e)
s_cruce = lambda pe0, e=EC:  S0 * (math.tan(math.radians(pe0 - OM * e)) / math.tan(math.radians(REPOSO))) ** (1 / (1 - MC))
_SNA = np.log(np.array(A33["sn"]))                                            # banda de a33: nivel P5–P95 con m de 0.834 a 0.862
lo = lambda sn: float(np.interp(math.log(sn), _SNA, A33["phi_lo"])); hi = lambda sn: float(np.interp(math.log(sn), _SNA, A33["phi_hi"]))
SNF = np.log(np.array(A12["sn_fino"])); T05 = np.min([v["phi_t05"] for v in C2.values()], 0); T95 = np.max([v["phi_t95"] for v in C2.values()], 0)
lot = lambda sn: float(np.interp(math.log(sn), SNF, T05)); hit = lambda sn: float(np.interp(math.log(sn), SNF, T95))   # curva propuesta, total
HC = lambda s: math.degrees(math.atan(1.446 * (s * 1000) ** 0.898 / (s * 1000)))
d0 = pd.read_csv(AA / "ensayos_ajuste.csv", low_memory=False)                 # revisión 5: TX y corte directo (a8_ensayos_ajuste.py)
assert len(d0) == len(P) and np.allclose(d0.s3.values, P.s3.values, equal_nan=True)
# revisión 10: puntos con la e0 del D854 (a8) y los triaxiales convertidos a σ′n–τ con m = 0.85 (Ec. 16 de Leps 2.0)
_tx = (d0.tipo == "TX").values; _sn = d0.sn_ds.values.astype(float).copy(); _ta = d0.tau_ds.values.astype(float).copy()
_D, _S = (d0.s1 - d0.s3).values[_tx], (d0.s1 + d0.s3).values[_tx]
_sp = (np.sqrt(4 * MC * (MC - 1) * _D ** 2 + _S ** 2) - _S) / (2 * (MC - 1) * _D)
_sn[_tx] = _S / 2 - _D / 2 * _sp; _ta[_tx] = _D / 2 * np.sqrt(1 - _sp ** 2)
P["sn"] = _sn; P["phis"] = np.degrees(np.arctan(_ta / _sn)); P["e"] = d0.e0_adoptado.values; P["phis_e065"] = P.phis - OM * (EC - P.e)
TXD = d0[d0.tipo == "TX"]; DSD = d0[d0.tipo == "DS"]; PTX = P[P.tipo == "TX"]; PDS = P[P.tipo == "DS"]
SNX, S3X = float(PTX.sn.max()), float(PTX.s3.max())
n_ciclo = int(sum(("carga-descarga" in str(r.tipo_ensayo).lower()) or ("CICL" in str(r.notas).upper()) for _, r in TXD.iterrows()))
n_contr = int((TXD.eps_vol_falla_pct < 0).sum()); n_eps = int(TXD.eps_vol_falla_pct.notna().sum())
C_DS = R9["datos"]["c_ds"]; GSD = DSD.groupby("litologia").Gs_adoptado.first()
P["cota"] = [LB(s) for s in P.sn]; PBAJO = P[P.phis_e065 < P.cota]; PBAJO_MN = PBAJO[(PBAJO.litologia == "Mármol") & (PBAJO.tipo == "DS")]
LOWP = P[P.sn < 0.5].copy(); LOWP["curva"] = [phis(s, OP2["pe0"], MC) for s in LOWP.sn]; LOWP["dif"] = LOWP.phis_e065 - LOWP.curva
# auditoría independiente (2026-10-10): frases calculadas en vez de escritas a mano
PMN = P[P.litologia == "Mármol"].copy(); PMN["curva"] = [phis(s, OP2["pe0"], MC) for s in PMN.sn]
n_mn_bajo_curva = int((PMN.phis_e065 < PMN.curva).sum())
N_HF = int((P.litologia == "Hornfels").sum()); N_HF_TX = int((PTX.litologia == "Hornfels").sum())
BGT = pd.read_csv(AA / "a16_bg.csv"); BG12 = BGT[BGT.s3 >= 0.9]
_lsds = pd.read_csv(AA.parent / "datos_antamina" / "verificacion_ocr" / "anddes2024_lsds.csv")
DS_FIN = _lsds[_lsds.desplaz_pico_cm_lectura_grafico.astype(str).str.contains("(fin", regex=False)]
assert len(DS_FIN) == 3, DS_FIN                                                # ruma 02 a 1.2 MPa y pilas 01 y 02 a 0.6 MPa   # pico al final del ensayo (lectura de las curvas): cota inferior
DS_DUD = _lsds[_lsds.desplaz_pico_cm_lectura_grafico.astype(str).str.contains("ilegible")]  # τ pico de la tabla no visible en la curva
f1 = lambda v: f"{v:.1f}"; f2 = lambda v: f"{v:.2f}"; sg = lambda v, d=1: f"{v:+.{d}f}".replace("-", "$-$")
LITN = {"Mármol": "mármol", "Hornfels": "hornfels", "Intrusivo": "intrusivo", "Mezcla": "mezcla"}
# auditoría 2026-10-10: las dos mezclas no son iguales. G2021 (G21-DESM-COMP) es un compuesto 0.35 tipo A (intrusivo) : 0.15 tipo B
# (mármol y hornfels) : 0.50 tipo C (hornfels) (Golder 2021, p. 6); solo la pila 01 de Anddes es mármol + hornfels.
LITS = lambda fuente, lit: ("compuesto" if fuente == "G2021" else "mármol--hornfels") if lit == "Mezcla" else LITN[lit]
P["phi1"] = np.degrees(np.arctan(np.tan(np.radians(P.phis_e065)) * (P.sn / S0) ** (1 - MC))); LITM = P.groupby("litologia").phi1.mean()
p2, pm = OP2["pe0"] - OM * EC, MAR["pe0"] - OM * EC
ML = R9["m_libre"]; ES = R9["esc"]
A25 = J("a25_alta_tension.json"); A27 = pd.read_csv(AA / "a27_ensayos_todos.csv")          # esfuerzos altos y tabla completa
_W = 'Base mundial (Cylwik et al. 2025) | 4.6–7.9 MPa'; _A = 'Antamina (ajuste) | 3–7.9 MPa'
# revisión 10: contraste a grandes esfuerzos recalculado con la curva simple, cada ensayo a su propia e
sys.path.insert(0, str(AA.parent / "analisis")); from lepsp_r6 import datos as _datos  # noqa: E402
_WD = _datos(); _WD = _WD[~_WD.cens] if "cens" in _WD else _WD; _kw = (_WD.sn > SNX) & (_WD.sn <= SNW)
_dw = np.degrees(np.arctan(_WD.tau[_kw] / _WD.sn[_kw])) - np.array([phis(s_, OP2["pe0"], MC, e_) for s_, e_ in zip(_WD.sn[_kw], _WD.e[_kw])])
_ka = P.sn > 3; _da = P.phis_e065[_ka] - np.array([phis(s_, OP2["pe0"], MC) for s_ in P.sn[_ka]])
A25 = {"ensayos": {_W: dict(n=int(_kw.sum()), bajo_curva=int((_dw < 0).sum()), dphi_mediana=float(np.median(_dw))),
                   _A: dict(n=int(_ka.sum()), bajo_curva=int((_da < 0).sum()), dphi_mediana=float(np.median(_da)))}}
# sesgo de la curva frente a los ensayos de Antamina por rango (medido − curva, a e = 0.45)
_res = P.phis_e065 - np.array([phis(s_, OP2["pe0"], MC) for s_ in P.sn])
SESGO = [(a_, b_, float(_res[(P.sn > a_) & (P.sn <= b_)].mean()), int(((P.sn > a_) & (P.sn <= b_)).sum())) for a_, b_ in ((0, 0.5), (0.5, 2), (2, SNX + 0.01))]
# posición frente a Leps (1970) a e = 0.45 y con el perfil A (0 = inferior, 1 = media)
_pos = lambda s_, f_: (f_ - L70(s_, 36)) / (L70(s_, 41) - L70(s_, 36))
def _cruce(p1, e_=EC):
    a_, b_ = 0.01, 200.0
    for _ in range(80):
        c_ = math.sqrt(a_ * b_); a_, b_ = (c_, b_) if phis(c_, OP2["pe0"], MC, e_) - L70(c_, p1) > 0 else (a_, c_)
    return math.sqrt(a_ * b_)
X_MED, X_INF = _cruce(41), _cruce(36)
POS_A = [_pos(s_, phis(s_, OP2["pe0"], MC, float(PEM.e_A(s_)))) for s_ in (1, 4, 10, 15)]
_dlb = [phis(s_, OP2["pe0"], MC) - LB(s_) for s_ in np.geomspace(0.5, 15, 60)]; LB_SOBRE = min(_dlb) > 0   # sobre Indraratna hasta 15 MPa
PB = P.loc[P.sn.idxmin()]; ROWB = d0.loc[P.sn.idxmin()]                       # ensayo de menor σ′n (mezcla G2021)
EPS4 = TXD[TXD.eps_axial_falla_pct < 6]
# auditoría 2026-10-10: conteos calculados (ensayos frente a la banda y a las cotas)
P["lo"] = [lo(s) for s in P.sn]; P["hi"] = [hi(s) for s in P.sn]
N_SOBRE_B, N_BAJO_B = int((P.phis_e065 > P.hi).sum()), int((P.phis_e065 < P.lo).sum())
N_SOBRE_HC = int((P.phis_e065 > [HC(s) for s in P.sn]).sum())
N_BAJO_LB_06 = int((PBAJO.sn <= 0.6).sum())
_dhc = [phis(s, OP2['pe0'], MC) - HC(s) for s in (1, 3, 8)]
HC_POS = "sobre" if min(_dhc) > 0 else ("bajo" if max(_dhc) < 0 else "a ambos lados de")
P_CP = P                                                                       # ensayos de la curva propuesta (con las mezclas desde el 2026-10-12)
_g = lambda s: phis(s, OP2["pe0"], MC) - LB(s); _a, _b = 0.5, 15.0            # cruce de la curva propuesta con la cota de Indraratna
for _ in range(60):
    _c = 0.5 * (_a + _b); _a, _b = (_c, _b) if _g(_c) > 0 else (_a, _c)
S_LB = 0.5 * (_a + _b)
# ---- efecto del tamaño de partícula (Frossard et al. 2012): τ_campo(σ) = λ^(1−m)·τ_lab(σ), λ = (D_lab/D_campo)^(3/m_w)
DLABS, DCAMPO = tuple(sorted(d0.Dmax_mm.unique(), reverse=True)), 1000.0          # 178 mm (1 m), 102 mm (0.6 m) y 25 mm (6 in y corte directo)
TAM = []
for dl_ in DLABS:
    for mw_ in (4.0, 3 / 0.45, 10.0):
        k_ = ((dl_ / DCAMPO) ** (3 / mw_)) ** (1 - MC)
        TAM.append((dl_, mw_, k_, math.degrees(math.atan(k_ * math.tan(math.radians(p2))))))
filas_tam = [f"{dl_:.0f} & {mw_:.1f}" + (r" (ISRM)" if abs(mw_ - 3 / 0.45) < 0.01 else "") + f" & {k_:.3f} & {f1_:.1f} & {sg(f1_ - p2, 1)}" + r" \\" for dl_, mw_, k_, f1_ in TAM]
TAMC = {round(dl_): (k_, f1_ - p2) for dl_, mw_, k_, f1_ in TAM if abs(mw_ - 3 / 0.45) < 0.01}
# ---- revisión 4: inventario, campo, contraste y Bg (a16; extracciones verificadas contra los PDF, 2026-10-10)
A16 = J("a16_resultados.json")
CIT = {"G2012": r"\citet{g2012}", "G2021": r"\citet{g2021}", "W2022": r"\citet{w2022}", "W2024": r"\citet{w2024}", "I2025": r"\citet{i2025}",
       "A2024DS": r"\citet{anddes2024}, corte directo"}
AMB = TXD.set_id.isin(["HF-0.15m-Golder", "MN-0.15m-Golder"])                 # signo de εv dudoso (leyenda Golder Burnaby)
n_contr_seg = int(((TXD.eps_vol_falla_pct < 0) & ~AMB).sum())
EIN = A16["e_in_situ_G2010"]; FR = A16["frag"]; BG = A16["bg"]
ein_A = [v["e"] for k, v in EIN.items() if k.startswith("A|")]
RC = {k: v for k, v in A16.items() if k.startswith(("CU", "Corte"))}
rc = lambda pre: next(v for k, v in RC.items() if k.startswith(pre))
INV = [
    (r"\citet{g2010}, fase A (ROM)", "Triaxial CU", "2.8 y 4~in (9.5--15.9~mm)", "Mármol, hornfels, intrusivo, skarn", "21", r"Contraste (sección~\ref{sec:contraste})"),
    (r"\citet{g2010}, fase B (ROM chancado)", "Triaxial CU", "2.8, 4 y 6~in (9.5--25.4~mm)", "Mármol, hornfels, intrusivo, skarn", "36", "No usado: material chancado"),
    (r"\citet{g2010}", "Índices de roca y densidad in situ", "--", "Mármol, hornfels, intrusivo, skarn", "--", r"$G_s$; la $e$ in situ no se usa (sección~\ref{sec:datos})"),
    (r"\citet{g2012}", "Triaxial CD (3 con carga y descarga)", "1~m (178~mm)", "Mármol", "5", "Ajuste"),
    (r"\citet{g2012}", "Edómetro", "0.95~m", "Mármol", "1", r"Rango de compresibilidad (Tabla~\ref{tab:edo})"),
    (r"\citet{g2021}", "Triaxial CD, desmonte compuesto", "6~in (25~mm)", r"Intrusivo, hornfels, mármol (35/50/15~\%)", "3", "Ajuste"),
    (r"\citet{w2022}", "Triaxial CD (3 con carga y descarga)", "1~m (178~mm)", "Hornfels", "6", "Ajuste"),
    (r"\citet{w2022}", "Triaxial CD con carga y descarga", "6~in (25~mm)", "Hornfels, mármol", "2", "Ajuste (pares de escala)"),
    (r"\citet{w2022}", r"Triaxial CD y edómetro (copias de \citealp{g2012})", "1~m", "Mármol", "5 y 1", "Duplicados; se usa el original"),
    (r"\citet{w2022}", "Triaxial cíclico (15 ciclos) y luego monótono", "0.10--0.15~m", "Hornfels, mármol", "6", "No usado: carga cíclica previa; 3 detenidos por la capacidad del equipo"),
    (r"\citet{w2022}", "Edómetro", "1~m (2) y 0.24~m (4)", "Hornfels, mármol", "6", r"Perfil A (mármol suelto, 0.24~m) y rango de compresibilidad (Tabla~\ref{tab:edo})"),
    (r"\citet{w2024}, set C4", "Triaxial CD", "0.6~m (102~mm)", "Intrusivo", "3", "Ajuste"),
    (r"\citet{w2024}, set C4", "Edómetro", "0.6~m (102~mm)", "Intrusivo", "1", r"Rango de compresibilidad (Tabla~\ref{tab:edo})"),
    (r"\citet{i2025}", "Triaxial CD", "1~m (178~mm)", "Intrusivo", "3", "Ajuste"),
    (r"\citet{anddes2024}", "Triaxial CU", "6~in ($D_{max}$ no informado)", "Mármol, hornfels, intrusivo, mármol--hornfels", "15", "Contraste"),
    (r"\citet{anddes2024}", "Corte directo de gran escala", "30.5~cm (1~in)", "Mármol, hornfels, intrusivo, mármol--hornfels", "15", "Ajuste"),
    (r"\citet{anddes2024}", "Granulometría, límites, Proctor, humedad", "--", "Mármol, hornfels, intrusivo, mármol--hornfels", "5", "Caracterización"),
    (r"\citet{stantec2023}", r"Puntos $\tau$--$\sigma'_n$ de terceros", "--", "--", "--", "No usado"),
    (r"\citet{antamina2025frag}", "Fragmentación por análisis de fotos", "Campo", "Desmonte ROM", f"{FR['n']}", "$D_{max}$ de campo"),
]
filas_inv = [" & ".join(r) + r" \\" for r in INV]
# edómetros verificados (a17_edometros.py)
EDO = J("a17_edometros.json")
for r in EDO:
    r["perfil"] = {str(k): v for k, v in (r["perfil"] or {}).items()}
EDO_S = [r for r in EDO if r["e0"] and r["e0"] >= 0.42]; EDO_D = [r for r in EDO if r["e0"] and r["e0"] < 0.42]
NOM_EDO = {"INT-edo-0.6m-C4 (IDIEM/WSP)": ("Intrusivo, set C4", ""), "HF-edo-1.0m (IDIEM)": ("Hornfels", "s"), "MN-edo-1.0m-2021 (IDIEM)": ("Mármol, 2021", "s"),
           "MN-edo-1.0m-2011 (IDIEM 708.397-A)": ("Mármol, 2011", ""), "MN-edo-0.24m-1.86 (Golder Test 1)": ("Mármol, 1.86~t/m³ (perfil A)", ""),
           "HF-edo-0.24m-2.1 (Golder)": ("Hornfels, 2.1~t/m³", "g"), "HF-edo-0.24m-1.8 (Golder)": ("Hornfels, 1.8~t/m³", "g"), "MN-edo-0.24m-2.3 (Golder)": ("Mármol, 2.3~t/m³", "g")}
filas_edo = [f"{NOM_EDO[r['ensayo']][0]}" + (f"$^{{{NOM_EDO[r['ensayo']][1]}}}$" if NOM_EDO[r['ensayo']][1] else "") + f" & {r['diametro_mm'] / 1000:.2f}~m & {r['e0']:.3f} & {r['Cc1']:.3f} & {r['Cc2']:.3f} & {r['perfil']['300']:.2f} & {r['perfil']['700']:.2f}" + r" \\"
             for r in sorted(EDO, key=lambda r: -r["e0"])]
# ---- tablas
filas_t1 = []; _fu = None
for i, r in d0.iterrows():
    p = P.iloc[i]; sid = str(r.set_id).replace("Codisposal 1 (100% Intrusivo)", "Intrusivo 100~\\%").replace(" (100% Intrusivo)", "").replace("_", r"\_")
    cic = r"$^{c}$" if (("carga-descarga" in str(r.tipo_ensayo).lower()) or ("CICL" in str(r.notas).upper())) else ""
    if r.fuente_id != _fu:                                     # fila de encabezado por informe (APA 7)
        filas_t1.append((r"\midrule " if _fu else "") + r"\multicolumn{10}{l}{\textit{" + CIT[r.fuente_id] + r"}} \\"); _fu = r.fuente_id
    if r.tipo == "DS":                                          # corte directo: caja de 30.5 cm, σ′n y τ medidos
        filas_t1.append(f"{sid}$^{{d}}$ & {LITS(r.fuente_id, r.litologia)} & 0.31 & {r.Dmax_mm:.0f} & {r.e0_adoptado:.3f} & -- & -- & {p.sn:.2f} & {p.phis:.1f} & --" + r" \\")
        continue
    filas_t1.append(f"{sid}{cic} & {LITS(r.fuente_id, r.litologia)} & {r.diametro_mm / 1000:.2f} & {r.Dmax_mm:.0f} & {r.e0_adoptado:.3f} & "
                    f"{r.s3:.2f} & {r.s1:.2f} & {p.sn:.2f} & {p.phis:.1f} & " + (f"{p.eps_a:.1f}" if np.isfinite(p.eps_a) else "--") + r" \\")
NOMS = {"S1": "Todos, con ajuste de escala", "S2": "Solo gran escala", "S3": "Todos, sin ajuste (base)"}
filas_t2 = [f"{NOMS[k]} & {ES[k]['n']} & {ES[k]['sets']} & {ES[k]['pe0_m09']:.2f} & {ES[k]['phi1_col_m09']:.2f} & {min(ES[k]['m_libre'], 1.0):.2f}" + r" \\" for k in ("S1", "S2", "S3")]
SNT = [1, 2, 3, SNX, 8, 15]
HIPT = [("$m$ alto (IC 90~\\%)", "m0862"), ("Curva propuesta", "m085"), ("$m$ bajo (IC 90~\\%)", "m0834"), ("Antamina sola$^{s}$", "lineal")]
filas_t3 = [f"{nm_} & {A33['hipotesis'][k_]['m_a']:.3f} & {A33['hipotesis'][k_]['pe0']:.2f} & " + " & ".join(f1(phis(s, A33['hipotesis'][k_]['pe0'], A33['hipotesis'][k_]['m_a'])) for s in SNT) + r" \\" for nm_, k_ in HIPT]
filas_t3 += [r"\midrule Banda, límite inferior & & & " + " & ".join(f1(lo(s)) for s in SNT) + r" \\",
             "Banda, límite superior & & & " + " & ".join(f1(hi(s)) for s in SNT) + r" \\"
             ]
SN4 = [0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15]
ext = lambda s: r"$^{a,w}$" if s > SNW else (r"$^{a}$" if s > SNX else "")
filas_t4 = [r"0 & 0.0 & 0.0 & 0.0 & -- \\"]
filas_t4 += [f"{s*1000:.0f}{ext(s)} & {tau(s, OP2['pe0'], MC)*1000:.1f} & "
             f"{s*1000*math.tan(math.radians(lo(s))):.1f} & {s*1000*math.tan(math.radians(hi(s))):.1f} & {phis(s, OP2['pe0'], MC):.1f}" + r" \\" for s in SN4]
EPAR = [("0.45", lambda s: 0.45), ("0.55", lambda s: 0.55), ("0.65", lambda s: 0.65), ("A", lambda s: float(PEM.e_A(s))), ("V", lambda s: float(PEM.eV_of_sv(s)))]
filas_t5 = [r"0 & " + " & ".join("0.0" for _ in EPAR) + r" & 0.0 \\"]
filas_t5 += [f"{s*1000:.0f}{ext(s)} & " + " & ".join(f"{tau(s, OP2['pe0'], MC, fe(s))*1000:.1f}" if math.isfinite(fe(s)) else "--" for _, fe in EPAR)
             + f" & {s*1000*math.tan(math.radians(REPOSO)):.1f}" + r" \\" for s in SN4]
A_PC = lambda pe0, e: math.tan(math.radians(pe0 - OM * e)) * 1013.0 ** (1 - MC)
PCV = [("Curva propuesta", OP2["pe0"], 0.45), ("Curva propuesta", OP2["pe0"], 0.55), ("Curva propuesta", OP2["pe0"], 0.65)]
filas_pc = [f"{nm} & {pe0:.2f} & {e:.2f} & {pe0 - OM * e:.2f} & {A_PC(pe0, e):.4f} & {MC:.4f} & 0 & 0" + r" \\" for nm, pe0, e in PCV]
filas_esc = [f"{LITN[r['litologia']]} & {r['s3']:.2f} & {r['pe0_grande']:.2f} & {r['m']:.2f} & {r['pe0_chico']:.2f} & {sg(r['dif'], 2)}" + r" \\" for r in R9["escala"]["pares"]]
zz_ = np.array(PE["z"]); filas_ez = []
for zq in (0, 50, 100, 200, 300, 400, 500, 600, 700):
    j = int(np.argmin(np.abs(zz_ - zq))); ev = PE["e_V"][j]
    filas_ez.append(f"{zq} & {PE['sv_A'][j]:.2f} & {PE['e_A'][j]:.3f} & " + (f"{PE['sv_V'][j]:.2f} & {ev:.3f}" if ev is not None else "-- & --") + r" \\")
SNE = [0.5, 1, 2, 3, 5, 8, 15]; snP = list(PE["sn"])
ROTE = {"e = 0.45": "0.45 constante (base)", "e = 0.55": "0.55 constante", "e = 0.65": "0.65 constante", "Perfil A (edómetro Antamina)": "Perfil A, compresibilidad de Antamina",
        "Perfil V (Valenzuela et al. 2008)": r"Perfil V, Valenzuela et al. (2008)$^{c}$"}
_fe = lambda k_, sv: float(k_[4:]) if k_.startswith("e = ") else float(PEM.e_A(sv) if k_.startswith("Perfil A") else PEM.eV_of_sv(sv))   # revisión 10: curva simple
filas_et = [ROTE[k_] + " & " + " & ".join(f"{phis(sv, OP2['pe0'], MC, _fe(k_, sv)):.1f}" if math.isfinite(_fe(k_, sv)) else "--" for sv in SNE) + r" \\" for k_ in PE["curvas"]]
REF_S = r"""\bibitem[Anddes Geolab(2024)]{anddes2024} Anddes Geolab (2024). \emph{Ensayos de laboratorio en desmonte (rumas M-1 a M-13, H-1 a H-12, I-1 a I-12 y pilas 01 y 02): triaxial CU de 6~in, corte directo de gran escala, clasificación SUCS, Proctor estándar y contenido de agua} [informes de ensayo para Compañía Minera Antamina; solicitud EPE-23.10.141].
\bibitem[WSP Perú(2023)]{wsp2023tsf} WSP Perú (2023). \emph{Ingeniería de detalle para recrecimiento de depósito de relaves a la cota 4165 m, Presa de Relaves Antamina: Informe final} [Informe 104-22155-MTE00420-IFF-430-G-0001, Rev.~0, 28 de diciembre de 2023, para Compañía Minera Antamina].
\bibitem[Stantec(2025)]{stantec2025sda} Stantec (2025). \emph{Seismic deformation analysis report: 24213EXB-115 Depósito de Desmonte Este, extensiones E1, E2, E9 y E10} [Informe 102-24213-CW18321-INF-115-R-0005, Rev.~B, 31 de octubre de 2025, para Compañía Minera Antamina].
\bibitem[Stantec(2026a)]{stantec2026dde} Stantec (2026a). \emph{Informe de diseño geotécnico: 24213EXB-115 Depósito de Desmonte Este, extensiones E1, E2, E9 y E10} [Informe 102-24213-CW18321-INF-115-R-0004, Rev.~0, 13 de febrero de 2026, para Compañía Minera Antamina].
\bibitem[Stantec(2026b)]{stantec2026iff} Stantec (2026b). \emph{Informe final de estudio: Depósito de Desmonte Este (DDE), Life Extension 2 Program, ingeniería de prefactibilidad Gate 2B} [Informe 102-24213-CW18321-IFF-115-G-0001, Rev.~B, 6 de abril de 2026, para Compañía Minera Antamina].
\bibitem[Compañía Minera Antamina(2025)]{antamina2025frag} Compañía Minera Antamina (2025). \emph{Fragmentación del desmonte 2025} [base de datos de análisis de fotos post-voladura].
\bibitem[Golder Associates Perú(2010)]{g2010} Golder Associates Perú (2010). \emph{Caracterización material de ROM -- Proyecto IPCC} [Memorando técnico para Compañía Minera Antamina, proyecto 099-4151017, 25 de marzo de 2010].
\bibitem[Golder Associates Perú(2012)]{g2012} Golder Associates Perú (2012). \emph{Summary of results from laboratory testing program for black marble rockfill} [Technical memorandum Doc.~No.~446, proyectos 1014270482C/1194155017P, 7 de febrero de 2012; anexo IDIEM, Informe 708.397-A].
\bibitem[Golder Associates Perú(2021)]{g2021} Golder Associates Perú (2021). \emph{Estudio conceptual almacenamiento eco-estable de desmonte y relaves: Informe de interpretación de ensayos de laboratorio} [Informe 101-20110-LTE01220-INF-420-G-0013, Rev.~0, 28 de abril de 2021].
\bibitem[Golder Associates Perú(2022)]{w2022} Golder Associates Perú (2022). \emph{Pruebas de enrocado 3B a gran escala material tipo hornfels y de alta presión para el modelamiento de deformación} [Memorando técnico 105-18028-MTE00420-MEM-430-G-0007, 8 de septiembre de 2022; anexos IDIEM, Informes 1.555.677-A a~E].
\bibitem[WSP Perú(2024)]{w2024} WSP Perú (2024). \emph{Ensayos geotécnicos a gran escala para mezclas de co-disposición de desmonte y relave} [Informe final 101-20110-LTE01220-IFF-420-G-0003, Fase~1, 30 de octubre de 2024; anexos IDIEM 1.914.482-A a~G].
\bibitem[IDIEM(2025)]{i2025} IDIEM (2025). \emph{Ensayos triaxiales a gran escala -- Fase 2 y 3} [Informe de Ensayo Especial 1.966.314-B, Rev.~01, 24 de enero de 2025, para WSP Perú y Compañía Minera Antamina]."""
PC = r"\colorbox{yellow}"
FECHA = "12 de octubre de 2026"
TXT_OBJ_ESCALA = r"El efecto del tamaño de partícula, entre los ensayos ($D_{max}$ de 25 a 178~mm) y el desmonte ROM (tamaño máximo de 1~m; \citealp[Tabla~3-1]{stantec2026iff}), se estimó aparte como sensibilidad (sección~\ref{sec:tamano})."

T = r"""\documentclass[11pt,letterpaper]{article}
\usepackage[utf8]{inputenc}\usepackage[T1]{fontenc}\usepackage{lmodern}
\usepackage[spanish,es-noshorthands,es-tabla]{babel}\decimalpoint
\usepackage[margin=2.5cm]{geometry}\usepackage{booktabs,longtable,graphicx,amsmath,array,caption,xcolor,float,needspace}\usepackage[section]{placeins}\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\usepackage{upquote}
\usepackage[colorlinks=true,linkcolor=black,citecolor=black,urlcolor=blue]{hyperref}
\usepackage[round]{natbib}\captionsetup{font=small,labelfont=bf}
\setlength{\parskip}{4pt}
\begin{document}
\begin{center}{\Large\textbf{Envolvente de resistencia del desmonte ROM de Antamina con Leps 2.0}}\\[3pt]{\large Propuesta de curva e incertidumbre a alto confinamiento}\end{center}
\vspace{4pt}
\noindent\begin{tabular}{@{}p{3.2cm}p{12.6cm}@{}}\toprule
Para: & Compañía Minera Antamina\\
De: & Stantec\\
Fecha: & """ + FECHA + r"""\\\bottomrule
\end{tabular}

\section{Objetivo y alcance}\label{sec:obj}
Este memorándum propone, para la revisión del EoR, una curva de resistencia al corte drenada para el desmonte ROM de Antamina. Stantec ajustó el criterio Leps 2.0 \citep{cylwik}, que actualiza las envolventes de \citet{leps} con una base de unos 900 ensayos de gran escala, a los triaxiales drenados (de gran escala y de 6~in) y a los cortes directos de gran escala disponibles, y estimó la incertidumbre de la curva por nivel, curvatura y relación de vacíos, en particular por encima del máximo esfuerzo ensayado. """ + TXT_OBJ_ESCALA + r""" La curva corresponde a desmonte colocado por volteo descendente con relación de vacíos $e = 0.45$, con alternativas de $e$ y perfiles de densificación por profundidad (sección~\ref{sec:e}).

La curva trata el desmonte ROM como un solo material, como el diseño geotécnico del Depósito de Desmonte Este (DDE), que no zonifica el botadero por litología \citep[Tabla~3-1]{stantec2026iff}: se ajustó con todos los ensayos con igual peso, sin ponderar por litología. Como control, ponderar los ensayos con la producción de desmonte por litología desde 2021 que el DDE incluye en sus bases de diseño da prácticamente la misma curva (sección~\ref{sec:curva}). El documento no incluye análisis de estabilidad ni propone criterios de aceptación. Las limitaciones de uso están en la sección~\ref{sec:uso}.

\section{Datos}\label{sec:datos}
\subsection{Ensayos disponibles y uso}
La Tabla~\ref{tab:inventario} lista todos los ensayos de desmonte de Antamina disponibles para este memorándum y el uso que se dio a cada grupo. Stantec verificó los valores de la base de datos contra las hojas de laboratorio de cada informe o, donde no hay hoja, contra sus gráficos. Los triaxiales usados en el ajuste coinciden con los informes dentro del redondeo en $\sigma'_3$, desviador, $\varepsilon_a$ y $\varepsilon_v$ en el máximo desviador. El Anexo~\ref{sec:anexo} da, ensayo por ensayo, los """ + f"{len(A27)}" + r""" ensayos de resistencia de la Tabla~\ref{tab:inventario} con su uso (ajuste, contraste o no usado, con el motivo) y sus esfuerzos en la falla.

\begin{footnotesize}\setlength{\tabcolsep}{3pt}
\begin{longtable}{L{3.0cm}L{3.0cm}L{2.2cm}L{2.6cm}rL{3.0cm}}
\caption{Ensayos de desmonte disponibles y su uso en este memorándum. Escala: diámetro de la probeta o lado de la caja (entre paréntesis, tamaño máximo de partícula ensayado).}\label{tab:inventario}\\
\toprule Fuente & Ensayo & Escala & Litologías & $n$ & Uso\\\midrule\endfirsthead
\toprule Fuente & Ensayo & Escala & Litologías & $n$ & Uso\\\midrule\endhead
""" + "\n".join(filas_inv) + r"""
\bottomrule
\end{longtable}\end{footnotesize}

El ajuste usa los ensayos drenados de material del tajo: los triaxiales drenados (CD) y los cortes directos de gran escala. Leps 2.0 admite ambos tipos de ensayo: \citet{cylwik} definen sus sets como series de triaxiales o de cortes directos (p.~5) y dan una guía de esfuerzos para cada tipo (p.~11), aunque su base es casi toda triaxial (934 triaxiales y 4 cortes directos, p.~4). Quedan """ + f"{len(P)} ensayos en {P.set.nunique()} sets" + r""" (Tabla~\ref{tab:datos}): """ + f"{len(PTX)}" + r""" triaxiales (""" + f"{int((~PTX.escala.str.startswith('6 in')).sum())}" + r""" en probetas de 0.6--1.0~m y """ + f"{int(PTX.escala.str.startswith('6 in').sum())}" + r""" de 6~in) y """ + f"{len(PDS)}" + r""" cortes directos en caja de 30.5~cm, de mármol, hornfels, intrusivo (tonalita) y dos mezclas: el desmonte compuesto de \citet{g2021}, con 35~\% de intrusivo, 15~\% de mármol y hornfels y 50~\% de hornfels en masa seca (tipos A, B y C de Antamina; p.~6), y la pila 01 de mármol y hornfels de \citet{anddes2024}. Las dos mezclas también entran en la curva propuesta, que trata el desmonte como un solo material (sección~\ref{sec:curva}). El máximo $\sigma'_3$ de los triaxiales es """ + f2(S3X) + r"""~MPa, que con la conversión de Leps 2.0 ($m = """ + f"{MC:.2f}" + r"""$) corresponde a $\sigma'_n = """ + f2(SNX) + r"""$~MPa en el plano de falla; los cortes directos llegan a """ + f"{PDS.sn.max():.1f}" + r"""~MPa. Los triaxiales no drenados (CU) se usan como contraste (sección~\ref{sec:contraste}). Los CU de la fase B de \citet{g2010} no se usan porque son de material chancado: según el propio informe, la fase A corresponde al «material original procedente del tajo» y la fase B al «material chancado» (p.~1).

Por origen, el intrusivo \citep{w2024,i2025}, el compuesto de \citet{g2021} y las muestras de \citet{anddes2024} son desmonte del tajo; los informes no dicen si es ROM, chancado o enrocado, de modo que se clasificaron como ROM por su procedencia. Los tipos A, B y C con que Antamina designa el desmonte son una clasificación geoquímica por potencial de generación de acidez \citep[pp.~6 y~27]{g2021}, no de gradación. El mármol de \citet{g2012} es enrocado para la presa de relaves, obtenido de material \emph{run-of-the-mine} del tajo («Type C rockfill», pp.~1--2), y el hornfels de \citet{w2022} es enrocado 3B de la presa (pp.~3 y~7).

\subsection{Diferencias entre los ensayos y el campo}
Los ensayos no reproducen el desmonte del botadero en dos aspectos, y ambos deben tenerse presentes al usar la curva:
\begin{itemize}
\item \textbf{Tamaño de partícula.} El desmonte ROM de Antamina tiene $D_{max}$ de """ + f"{FR['Dmax']:.0f}" + r"""~mm en mediana (""" + f"{FR['Dmax_p10']:.0f}--{FR['Dmax_p90']:.0f}" + r"""~mm entre los percentiles 10 y 90), $D_{50}$ de """ + f"{FR['D50']:.0f}" + r"""~mm y $D_{80}$ de """ + f"{FR['D80']:.0f}" + r"""~mm, según """ + f"{FR['n']}" + r""" análisis de fragmentación por fotos en el frente de carguío \citep{antamina2025frag}. Los ensayos del ajuste se hicieron con $D_{max}$ de 25 a 178~mm, es decir, con la gradación cortada (escalpada) a entre 1/""" + f"{FR['Dmax'] / max(DLABS):.0f} y 1/{FR['Dmax'] / min(DLABS):.0f}" + r""" del $D_{max}$ mediano de campo. El efecto del tamaño se trata en la sección~\ref{sec:tamano}.
\item \textbf{Densidad.} Las probetas se compactaron, con $e_0$ de """ + f"{P.e.min():.3f} a {P.e.max():.3f}" + r""", y se densificaron más al consolidar: en \citet{g2012}, la $e$ bajó entre 0.03 y 0.11 según el informe. La curva se lleva a la $e$ de colocación del botadero, 0.45, con la corrección por densidad de Leps 2.0 (sección~\ref{sec:e}). Las únicas densidades in situ de desmonte disponibles para este memorándum son las de \citet[Tabla~2]{g2010}, por reemplazo de agua (ASTM D5030), un ensayo por litología. En la fase A dan $e$ de """ + f"{min(ein_A):.2f} a {max(ein_A):.2f}" + r""" con el $G_s$ del material grueso de cada litología (más altas con el $G_s$ de sólidos, ASTM D854). Las hojas ubican el ensayo en la «parte baja chancadora secundaria» (pp.~35--38) y el informe no describe cómo se colocó ese material, de modo que nada indica que represente desmonte volteado desde gran altura. Por eso no se usan como $e$ de colocación.
\end{itemize}

\subsection{Aspectos de los ensayos del ajuste}
Seis aspectos condicionan la interpretación:
\begin{enumerate}
\item """ + str(n_ciclo) + r""" ensayos tuvieron ciclos de carga y descarga antes del máximo desviador (en \citealp{g2012}, a partir de cerca del 50~\% de la resistencia última estimada, p.~7) y luego carga monótona hasta la falla. Son triaxiales drenados comparables a un CD, porque el máximo desviador se alcanza en la carga monótona, pero los ciclos pueden haber densificado la probeta. Son distintos de los seis ensayos cíclicos de \citet{w2022}, con ciclos de compresión y extensión, que no se usan.
\item Los ensayos se programaron hasta cerca de 20~\% de deformación axial, y ningún informe indica que se detuvieran por límite del equipo (dos de \citealp{i2025} terminaron en 15.0 y 16.7~\% sin explicación del laboratorio). La mayoría alcanzó el máximo desviador entre 11 y 21~\% de deformación axial, y en cuatro el máximo coincidió con el último punto: en esos casos el desviador podía seguir creciendo y el valor usado es una cota inferior. Dos ensayos llegaron al máximo con cerca de 4~\%: """ + "; ".join(f"{CIT[r.fuente_id]}, {LITS(r.fuente_id, r.litologia)}, $\\sigma'_3 = {r.s3:.2f}$~MPa" for _, r in EPS4.iterrows()) + r""".
\item Los """ + f"{n_eps}" + r""" ensayos tienen registro de volumen. En """ + f"{n_contr_seg}" + r""" la deformación volumétrica acumulada en el máximo desviador era de contracción: la probeta no había llegado a dilatar, de modo que la resistencia última puede ser algo mayor, en particular en el hornfels. En los dos ensayos de 6~in de \citet{w2022} el signo de $\varepsilon_v$ es dudoso, porque la leyenda de las hojas indica que el valor negativo es dilatación.
\item En el hornfels de 6~in de \citet{w2022}, la hoja informa un desviador máximo de 4100~kPa a 11.4~\% de deformación, pero su curva sigue subiendo hasta unos 4600~kPa cerca de 17.5~\% (lectura del gráfico). Se usa el valor de la hoja, del lado conservador.
\item Los cortes directos de \citet{anddes2024} se hicieron en una caja de 30.5~cm con la muestra cortada a 1~in (relación caja/partícula de 12; para probetas densas, \citealp[p.~297]{ovalle2023} recomiendan una relación de 12 a 24 para que la resistencia crítica sea representativa, y su resultado no se refiere a la resistencia pico), con $\sigma'_n$ de 0.3 a 1.2~MPa (1.0~MPa en la pila 01, que no cumple en sentido estricto la recomendación de Leps 2.0 de tener al menos un ensayo de corte directo sobre 1~MPa). Se usa el $\tau$ pico. Los ensayos terminaron a unos 66~mm de desplazamiento en las rumas y 64~mm en las pilas. Según la lectura de las curvas, en """ + f"{len(DS_FIN)}" + r""" ensayos el pico se alcanzó al final del ensayo (en dos de ellos $\tau$ seguía creciendo), así que el valor es una cota inferior; y en """ + f"{len(DS_DUD)}" + r""" (pila 02 a 0.3~MPa) la curva no muestra el $\tau$ pico de la tabla del laboratorio (353.9~kPa; unos 349~kPa al final), un dato dudoso que se mantiene tal como fue informado. El laboratorio no informa $G_s$, de modo que la $e$ se calculó con la densidad seca inicial y el $G_s$ de sólidos (ASTM D854) de \citet[p.~49]{g2010}, promedio de las fases A y B, el mismo criterio que se usó para el mármol de \citet{g2012}: """ + ", ".join(f"{LITN[l]} {v:.3f}" for l, v in GSD.items()) + r""". Con el $G_s$ del rótulo del ensayo Proctor (hasta 3.06 en el mármol), las $e$ serían mayores y la resistencia corregida a $e = 0.45$, más alta.
\item La $e_0$ es la inicial de la probeta, antes de consolidar, como en la base de Leps 2.0 \citep[p.~4 y Tabla~2]{cylwik}. En \citet{g2012} se recalculó con $G_s = 2.755$ \citep{g2010}, por lo que difiere de la del informe (0.286); \citet{i2025} no informa $G_s$ y se usó el de \citet{w2024} (2.85). El $G_s$ no es uniforme entre campañas: en el mármol, la probeta de 0.15~m usa 2.70 y la de 1~m, 2.755 (unos 0.03 en $e$ y 0.5° en $\phi'_1$); en el intrusivo, los cortes directos usan 2.708 (ASTM D854, \citealp{g2010}) y los triaxiales, 2.85 (unos 0.07 en $e$ y 1.4° en $\phi'_1$); y el hornfels de \citet{w2022} usa 2.75, frente a 2.797 del ASTM D854.
\end{enumerate}

\begin{footnotesize}\setlength{\tabcolsep}{2.5pt}
\begin{longtable}{lllrrrrrrr}
\caption{Ensayos usados en el ajuste. En los triaxiales, $\sigma'_n$ y $\phi'_s$ con la conversión de Leps 2.0 ($m = """ + f"{MC:.2f}" + r"""$, Ecs.~13--16 de \citealp{cylwik}); $D$: diámetro de la probeta o lado de la caja; $\varepsilon_a$: deformación axial en el máximo desviador; $^{c}$con ciclos de carga y descarga; $^{d}$corte directo: $\sigma'_n$ y $\tau$ pico medidos. Compuesto: desmonte compuesto de \citet{g2021}, con 35~\% de intrusivo, 15~\% de mármol y hornfels y 50~\% de hornfels.}\label{tab:datos}\\
\toprule Set & Litología & $D$ & $D_{max}$ & $e_0$ & $\sigma'_3$ & $\sigma'_1$ & $\sigma'_n$ & $\phi'_s$ & $\varepsilon_a$\\
 & & (m) & (mm) & & (MPa) & (MPa) & (MPa) & (°) & (\%)\\\midrule\endfirsthead
\toprule Set & Litología & $D$ & $D_{max}$ & $e_0$ & $\sigma'_3$ & $\sigma'_1$ & $\sigma'_n$ & $\phi'_s$ & $\varepsilon_a$\\\midrule\endhead
""" + "\n".join(filas_t1) + r"""
\bottomrule
\end{longtable}\end{footnotesize}

\section{Método}\label{sec:metodo}
Leps 2.0 expresa la resistencia como
\begin{equation}
\tau = \tan\!\left(\phi'_{e=0} - \omega\, e\right)\,(10p_a)^{1-m}\,\sigma_n'^{\,m}
\end{equation}
(Ec.~26 de \citealp{cylwik}), donde:
\begin{itemize}
\item $\tau$ es la resistencia al corte en el plano de falla y $\sigma'_n$ el esfuerzo normal efectivo en ese plano;
\item $p_a = 0.1013$~MPa es la presión atmosférica, de modo que $10p_a \approx 1$~MPa es el esfuerzo de referencia;
\item $e$ es la relación de vacíos del material cuya resistencia se calcula (ver abajo);
\item $\phi'_{e=0}$ es el ángulo de fricción secante a $10p_a$ extrapolado a $e = 0$, el parámetro que representa la litología;
\item $\omega$ es la pérdida de ángulo de fricción por unidad de relación de vacíos;
\item $\phi'_1 = \phi'_{e=0} - \omega e$ es el ángulo de fricción secante a $\sigma'_n = 10p_a$ para la $e$ considerada;
\item $m \le 1$ es el exponente de curvatura: con $m = 1$ la envolvente es una recta por el origen, y con $m < 1$ el ángulo secante baja al subir $\sigma'_n$.
\end{itemize}
En este memorándum aparecen tres relaciones de vacíos, y conviene no confundirlas:
\begin{itemize}
\item \textbf{$e_0$, de la probeta, inicial} (antes de consolidar). Es la que usa la base de Leps 2.0 («void ratio at start of test», \citealp[Tabla~2]{cylwik}) y con la que cada ensayo se lleva a la curva (Tabla~\ref{tab:datos}).
\item \textbf{$e$ de la probeta después de consolidar.} Solo se cita para mostrar cuánto se densifican las probetas (sección~\ref{sec:datos}); no entra en la curva.
\item \textbf{$e$ del desmonte en el botadero (in situ).} Es la de colocación, con valor base 0.45, y su variación con la profundidad, $e(z)$ (sección~\ref{sec:e}). Con ella se aplica la curva al botadero.
\end{itemize}
En la Ec.~(1), $e$ es $e_0$ al ajustar los ensayos y la $e$ in situ al aplicar la curva. El modelo simplificado de Leps 2.0 usa $m = 0.9$ (Ec.~9) y $\omega = 20°$ (Ec.~25). La corrección por densidad de la Ec.~27, $\Delta\phi' = -20°\,(e_{objetivo} - e)$, es ese mismo término $\omega e$ de la Ec.~(1): llevar un ensayo de su $e$ a la $e$ de colocación cambia $\phi'_1$ en $-\omega\,\Delta e$. Como el rango de $e$ de los ensayos es estrecho, Stantec fijó $\omega$ en 20° y ajustó $\phi'_{e=0}$ (y $m$, donde se indica) en esfuerzos principales: para cada ensayo se calcula el $\sigma'_1$ del círculo que pasa por $\sigma'_3$ y es tangente a la envolvente, y se minimiza el error en $\ln(\sigma'_1 - \sigma'_3)$. En el corte directo, que mide $\tau$ y $\sigma'_n$ en el plano de falla, se minimiza el error en $\ln\tau$, multiplicado por """ + f"{C_DS:.2f}" + r""" para que un grado de error en el ángulo de fricción pese lo mismo en los dos tipos de ensayo (la razón entre las sensibilidades de $\ln(\sigma'_1 - \sigma'_3)$ y de $\ln\tau$ al ángulo de fricción, con los ángulos medidos). La incertidumbre del nivel de la curva media se estimó por \emph{bootstrap} remuestreando sets completos, porque los ensayos de un mismo set no son independientes; con solo """ + str(P_CP.set.nunique()) + r""" sets en la curva propuesta, ese intervalo es aproximado. Como $\omega$ se fijó, su incertidumbre (15--25°) se incluye aparte, junto con la de la $e$ de colocación (sección~\ref{sec:alto}).

Con ese ajuste se construye la curva propuesta (sección~\ref{sec:curva}), con todos los ensayos de las litologías ensayadas con igual peso. Su exponente $m$ se toma de la base mundial de Leps 2.0 y no de los ensayos de Antamina (sección~\ref{sec:alto}).

Se compararon tres escenarios de datos (Tabla~\ref{tab:esc}): todos los ensayos con un ajuste de escala para las probetas de 6~in, solo gran escala, y todos sin ajuste. El ajuste de escala se midió con los dos pares de probetas de 0.15~m y 1~m de la misma litología (Tabla~\ref{tab:escala}): el hornfels dio """ + sg(R9['escala']['pares'][0]['dif'], 2) + r"""° y el mármol """ + sg(R9['escala']['pares'][1]['dif'], 2) + r"""° (el par de mármol combina dos campañas con $G_s$ distinto). Con dos pares de un ensayo cada uno y signos opuestos, los datos no permiten afirmar ni descartar un efecto de escala, de modo que la curva propuesta usa todos los ensayos sin ajuste.

\begin{table}[htbp]\centering\small\caption{Pares de escala: $\phi'_{e=0}$ que reproduce el ensayo de 0.15~m con la curva de 1~m de la misma litología.}\label{tab:escala}
\begin{tabular}{lrrrrr}\toprule Litología & $\sigma'_3$ (MPa) & $\phi'_{e=0}$, 1~m (°) & $m$, 1~m & $\phi'_{e=0}$, 0.15~m (°) & Diferencia (°)\\\midrule
""" + "\n".join(filas_esc) + r"""
\bottomrule\end{tabular}\end{table}

\section{Resultados}\label{sec:res}
\subsection{Ajuste a los ensayos de Antamina}
Con $m = 0.90$ y todos los ensayos sin ponderar, solo para comparar los escenarios de datos, los tres dan $\phi'_{e=0}$ entre """ + f"{min(ES[k]['pe0_m09'] for k in ES):.2f}° y {max(ES[k]['pe0_m09'] for k in ES):.2f}°" + r""" (Tabla~\ref{tab:esc}); el escenario de solo gran escala, que excluye las probetas de 6~in y el corte directo, es el más alto. En Leps 2.0 el exponente no puede ser mayor que 1. Si se ajusta $m$ junto con el nivel, los ensayos de Antamina llevan el ajuste a ese límite, $m = 1$: hasta $\sigma'_n \approx """ + f1(SNX) + r"""$~MPa la envolvente es prácticamente lineal, sin la curvatura que muestra la base mundial. Por litología, el hornfels y el mármol también llegan al límite, el intrusivo da $m = """ + f2(min(ML['intrusivo'], 1.0)) + r"""$ y el conjunto sin hornfels, $m = """ + f2(min(ML['sin hornfels'], 1.0)) + r"""$. La linealidad está influida por el hornfels, cuyo ángulo secante crece con el esfuerzo (de unos 41° a 46° entre 1.7 y 4.6~MPa, antes de la corrección por densidad); sus seis ensayos de gran escala tenían contracción volumétrica en el máximo desviador. Los ensayos de Antamina dan $m \approx 1$, en el límite de Leps 2.0, pero ese valor no se adopta por su representatividad (sección~\ref{sec:alto}). La curva propuesta toma $m = """ + f"{MC:.2f}" + r"""$ de la base mundial (sección~\ref{sec:alto}).

\begin{table}[htbp]\centering\small\caption{Ajuste de Leps 2.0 ($\omega = 20°$, $m = 0.90$) por escenario de datos, con $\phi'_1$ a $e = 0.45$, y exponente ajustado con el límite de Leps 2.0 ($m \le 1$). Todos los ensayos, sin ponderar por litología.}\label{tab:esc}
\begin{tabular}{lrrrrr}\toprule Escenario & Ensayos & Sets & $\phi'_{e=0}$ (°) & $\phi'_1$ (°) & $m$ ajustado\\\midrule
""" + "\n".join(filas_t2) + r"""
\bottomrule\end{tabular}\end{table}

\subsection{Rango de esfuerzos con respaldo de datos}\label{sec:rango}
Las figuras y tablas de este memorándum llegan hasta $\sigma'_n = 15$~MPa, pero el respaldo de los datos no es el mismo en todo ese rango. Hay tres zonas:
\begin{itemize}
\item \textbf{Hasta """ + f2(SNX) + r"""~MPa}, el máximo de los ensayos de Antamina (triaxial de hornfels con $\sigma'_3 = """ + f2(S3X) + r"""$~MPa, convertido con $m = """ + f"{MC:.2f}" + r"""$). El nivel de la curva se apoya en los ensayos de Antamina y su curvatura, en la base mundial.
\item \textbf{De """ + f2(SNX) + r""" a """ + f2(SNW) + r"""~MPa}, el máximo de la base mundial de Leps 2.0, donde solo """ + f"{R19['base_n_sobre_5']} ensayos, de {R19['base_sets_sobre_5']} sets," + r""" superan 5~MPa. No hay ensayos de Antamina; la curvatura sigue apoyada en la base mundial y el nivel es el de los ensayos de Antamina a menor esfuerzo.
\item \textbf{Sobre """ + f2(SNW) + r"""~MPa}. No hay ensayos en ninguna de las dos fuentes: la curva es una extrapolación de la ley de potencia de Leps 2.0, y la banda se abre en consecuencia.
\end{itemize}
Las figuras marcan estas zonas: gris claro, sin ensayos de Antamina; rayado, fuera de la base mundial. Los valores se extienden hasta 15~MPa porque en un botadero de 700~m el esfuerzo vertical efectivo en la base llega a unos """ + f"{PE['sv_A'][-1]:.1f}" + r"""~MPa con el perfil A (Tabla~\ref{tab:ez}), y una superficie de falla profunda, por ejemplo con fundación débil o compuesta a lo largo de la base, podría movilizar $\sigma'_n$ de ese orden. Fuera de la base mundial, los valores de la curva deben usarse solo como sensibilidad y con la banda completa.

\subsection{Incertidumbre a alto confinamiento}\label{sec:alto}
La linealidad de Antamina no autoriza a extrapolarla. Su causa no está identificada: puede influir la densificación de las probetas durante la consolidación y los ciclos de carga, pero en la base mundial $m$ casi no se correlaciona con la relación de vacíos ni con el tamaño (ver abajo), de modo que esas propiedades no la explican por sí solas. La decisión de no usar el $m$ de Antamina se basa en no extrapolar fuera de su rango un resultado de """ + str(P.set.nunique()) + r""" sets de un solo sitio, no en una causa demostrada. Por eso el exponente de la curva propuesta se toma de la base mundial de Leps 2.0. En sus """ + f"{RM['n_sets']}" + r""" sets triaxiales con $\sigma'_3 \ge 0.06$~MPa (la guía 60--600 de \citealp[p.~11]{cylwik}), al menos tres ensayos y $\sigma'_n$ máximo de al menos el doble del mínimo, la pendiente de $\ln\tau$ frente a $\ln\sigma'_n$ (que en Leps 2.0 es $m$) tiene mediana """ + f"{RM['m_P50_sets']:.2f}" + r""", P10 de """ + f"{RM['m_P10_sets']:.2f}" + r""" y P90 de """ + f"{RM['m_P90_sets']:.2f}" + r""". La curvatura se atribuye a la rotura de partículas, que crece con el confinamiento y reduce la dilatancia \citep{marsal1967,indraratna1993}. Para elegir el exponente se buscó el que mejor predice los ensayos mundiales de mayor esfuerzo, que es donde se usará la curva: en cada set con ensayos sobre 4.6~MPa, el nivel se fijó con sus ensayos de menor esfuerzo y se predijeron los de mayor esfuerzo con un $m$ común. El $m$ con residuo mediano nulo es """ + f"{M_SB:.3f}" + r""" (intervalo al 90~\% de """ + f"{M_IC[0]:.3f} a {M_IC[1]:.3f}" + r"""), y la curva propuesta usa $m = """ + f"{MC:.2f}" + r"""$; la mediana de los sets es """ + f"{M_MED:.2f}" + r""". La banda cubre ese intervalo de $m$. La desviación estándar de las pendientes es """ + f"{R19['m_sd_sets']:.3f}" + r"""; descontado el error de ajuste de cada set, la dispersión entre materiales es """ + f"{RM['tau']:.3f}" + r""" (estimador de Paule--Mandel). Las propiedades de los materiales la explican poco: en esos sets, la correlación de Spearman de $m$ con la relación de vacíos, el tamaño máximo, la resistencia de la roca y la rotura es como máximo de """ + f"{R19['max_abs_spearman']:.2f}" + r""" en valor absoluto, y agregar la relación de vacíos, el tamaño y la clase de roca la reduce poco (""" + f"{R19['tau_sin_covariables']:.3f} a {R19['tau_con_e_lnD_clase']:.3f}" + r"""). \citet[Tabla~4]{cylwik}, con el coeficiente de Pearson en sus 249 sets, informan correlaciones algo mayores de $m$ con el contenido de grava ($-0.32$) y el $D_{50}$ ($-0.24$), que siguen siendo débiles. Los pares $\sigma'_n$--$\tau$ de la base son los de \citet{cylwik}, que convirtieron los triaxiales con un procedimiento iterativo que considera la curvatura de cada set. Con la información disponible, la incertidumbre de $m$ para Antamina no puede bajar de esa dispersión sin ensayos representativos del campo a alto confinamiento (ítem~4 de la sección~\ref{sec:ensayos}). La base excluyó los ensayos con $\phi'_1 < 31°$ \citep[p.~4]{cylwik}, de modo que su distribución de $m$ puede estar sesgada.

Los ensayos de Antamina no se usan para la curvatura. Ajustados con un nivel propio por set, dan $m = """ + f"{RA['m']:.2f} \\pm {RA['se']:.2f}" + r"""$; en una calibración jerárquica con la base mundial, ese resultado pesaría un """ + f"{100 * RM['peso_antamina']:.0f}" + r"""~\% y llevaría $m$ a """ + f"{RM['post']['50'] if '50' in RM['post'] else RM['post'][50]:.2f}" + r""". Ese peso refleja solo la dispersión entre ensayos, no su representatividad del botadero.

La incertidumbre de la curva propuesta (sección~\ref{sec:curva}) se representa con una sola banda (Tabla~\ref{tab:hip}, Fig.~\ref{fig:phi}), que reúne dos fuentes:
\begin{itemize}
\item \emph{Curvatura.} $m$ entre """ + f"{M_IC[0]:.3f} y {M_IC[1]:.3f}" + r""", el intervalo al 90~\% de la prueba con los ensayos mundiales de mayor esfuerzo. Para cada $m$ se reajustó el nivel con los ensayos de Antamina. Las hipótesis no se dibujan una por una: la banda es su envolvente, y sus valores están en la Tabla~\ref{tab:hip}.
\item \emph{Nivel.} El intervalo del nivel al 90~\% (\emph{bootstrap} por sets, estratificado por litología).
\end{itemize}
La hipótesis $m = 1$, que es lo que dan los ensayos de Antamina solos, queda fuera de la banda y se informa como sensibilidad (Tabla~\ref{tab:hip}): daría un ángulo secante constante de """ + f1(phis(1, A33['hipotesis']['lineal']['pe0'], 1.0)) + r"""° a $e = 0.45$. Con $m = """ + f"{MC:.2f}" + r"""$, los ensayos de Antamina quedan en promedio """ + "; ".join(f"{sg(v_)}° entre {a_:g} y {f2(b_ if b_ < SNX else SNX)}~MPa ({n_} ensayos)" for a_, b_, v_, n_ in SESGO) + r""" respecto de la curva (medido menos curva): la curva queda sobre ellos a bajo esfuerzo y bajo ellos sobre 2~MPa, el costo de no extrapolar la linealidad de Antamina.

La incertidumbre de la relación de vacíos de colocación no entra en la banda porque se trata explícitamente con las alternativas de $e$ de la sección~\ref{sec:e}; tampoco la de $\omega$ (15--25°), que entra solo en la desviación estándar total de $\phi'_1$ indicada abajo. La banda representa la incertidumbre de la curva media, no la dispersión entre ensayos ni entre litologías: """ + f"{N_SOBRE_B + N_BAJO_B} de los {len(P)} ensayos quedan fuera de ella, {N_SOBRE_B} por encima (sobre todo hornfels e intrusivo) y {N_BAJO_B} por debajo" + r""". La banda va de """ + f"{f1(lo(1))}° a {f1(hi(1))}° a 1~MPa, de {f1(lo(2))}° a {f1(hi(2))}° a 2~MPa, de {f1(lo(SNX))}° a {f1(hi(SNX))}° a {f2(SNX)}~MPa y de {f1(lo(8))}° a {f1(hi(8))}° a 8~MPa, y de {f1(lo(15))}° a {f1(hi(15))}° a 15~MPa, ya fuera de la base mundial" + r""".

Para análisis probabilísticos, la desviación estándar de $\phi'_{e=0}$ de la curva media es """ + f2(OP2['sd_pe0']) + r"""° (nivel; $m = """ + f"{MC:.2f}" + r"""$), y la de $\phi'_1$, sumando además $\omega$ entre 15° y 25° y $e$ entre 0.35 y 0.55 (distribuciones uniformes), es """ + f2(OP2['sd_phi1_total']) + r"""°. Ninguna incluye la variabilidad espacial del botadero.

\begin{table}[htbp]\centering\small\caption{Ángulo de fricción secante $\phi'_s$ (°) de la curva propuesta a $e = 0.45$ según la hipótesis de curvatura, con el nivel ajustado a los ensayos, y límites de la banda de incertidumbre.}\label{tab:hip}
\setlength{\tabcolsep}{4.5pt}\begin{tabular}{lrrrrrrrr}\toprule Hipótesis & $m$ & $\phi'_{e=0}$ (°) & 1~MPa & 2~MPa & 3~MPa & """ + f2(SNX) + r"""~MPa & 8~MPa$^{w}$ & 15~MPa$^{w}$\\\midrule
""" + "\n".join(filas_t3) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{s}$Sensibilidad: el exponente de los ensayos de Antamina solos; no entra en la banda. $^{w}$Sobre el máximo de la base mundial de Leps 2.0 (""" + f2(SNW) + r"""~MPa): extrapolación fuera de toda la data (sección~\ref{sec:rango}).\end{table}

\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]{figs/Fig1_phi_sigma.pdf}
\caption{Curva propuesta ($m = """ + f"{MC:.2f}" + r"""$) y su banda de incertidumbre, con los ensayos del ajuste llevados a $e = 0.45$ (Ec.~27 de Leps 2.0), y en gris claro los ensayos de la base mundial de Leps 2.0 \citep{cylwik}, llevados a la misma $e$. Color y forma por litología; marcador lleno: triaxial drenado (probetas de 0.6--1~m y de 6~in); vacío: corte directo de gran escala (caja de 30.5~cm). En gris, como referencia, las envolventes superior, media e inferior de \citet{leps} ($\phi'_1$ = 46°, 41° y 36°) y la cota inferior de \citet{indraratna1993} ($\phi'_1 = 33°$), todas en la forma de la Ec.~9 de Leps 2.0 ($m = 0.9$; \citealp[p.~2 y Tabla~1]{cylwik}), que no depende de $e$. Zona gris: entre el máximo $\sigma'_n$ de los ensayos de Antamina (""" + f2(SNX) + r"""~MPa) y el de la base mundial (""" + f2(SNW) + r"""~MPa); rayado: fuera de la base mundial (sección~\ref{sec:rango}).}\label{fig:phi}\end{figure}

\subsection{Contraste con los ensayos no usados en el ajuste}\label{sec:contraste}
La Fig.~\ref{fig:contraste} compara la curva con los triaxiales no drenados (CU) de desmonte ROM, que no entran en el ajuste (los de la fase A de \citealp{g2010} y los de \citealp{anddes2024}), llevados a $e = 0.45$ con la misma corrección por densidad. Se convirtieron a $\sigma'_n$--$\tau$ con los esfuerzos efectivos en la falla y la misma conversión de Leps 2.0 que los drenados. Respecto de la curva propuesta, la diferencia media de $\phi'_s$ es:
\begin{itemize}
\item triaxiales CU de 6~in de \citet{anddes2024}, a máxima oblicuidad (""" + f"{rc('CU Anddes')['n']}" + r""" ensayos): """ + sg(rc('CU Anddes')['resid_media']) + r"""°;
\item triaxiales CU de 2.8 y 4~in de la fase A de \citet{g2010}, al máximo desviador, único criterio que informa el laboratorio (""" + f"{rc('CU Golder')['n']}" + r""" ensayos): """ + sg(rc('CU Golder')['resid_media']) + r"""°.
\end{itemize}
Los CU quedan a ambos lados de la curva y no son comparables con el ajuste. Su resistencia depende de la presión de poros y del criterio de falla: el laboratorio de \citet{anddes2024} toma la falla al 15~\% de deformación, y en 12 de sus 15 probetas el desviador seguía creciendo. Además, los de \citet{g2010} son probetas pequeñas, con la gradación cortada a 9.5--15.9~mm, y parte se remoldeó a la densidad mínima ($e$ de 0.49 a 0.54) y el resto a una compacidad mayor ($e$ de 0.27 a 0.45; \citealp[p.~4]{g2010}). La $e$ de los CU de \citet{anddes2024} se calculó igual que la de sus cortes directos, con el $G_s$ de \citet{g2010}.

\begin{figure}[H]\centering\includegraphics[width=\linewidth]{figs/Fig4_contraste.pdf}
\caption{Contraste de la curva propuesta con los triaxiales CU de desmonte ROM no usados en el ajuste, llevados a $e = 0.45$: \citet{anddes2024} y fase A de \citet{g2010}. Puntos grises: ensayos del ajuste (triaxiales drenados y cortes directos).}\label{fig:contraste}\end{figure}

\subsection{Rotura de partículas}\label{sec:rotura}
""" + f"{BG['n']}" + r""" de los triaxiales drenados del ajuste tienen el índice de rotura de \citet{marsal1967}, $B_g$, informado o recalculado de las granulometrías antes y después del ensayo (Fig.~\ref{fig:bg}). En \citet{g2012} se usa el valor recalculado, porque la Tabla~5 del informe da la suma de las diferencias absolutas, que es el doble de $B_g$. $B_g$ va de """ + f"{BG['rango'][0]:.0f} a {BG['rango'][1]:.0f}" + r"""~\% con $\sigma'_3$ de """ + f"{BG['s3'][0]:.2f} a {BG['s3'][1]:.2f}" + r"""~MPa y crece con el confinamiento ($B_g \approx """ + f"{BG['ordenada']:.1f} + {BG['pendiente']:.0f}" + r"""\,\sigma'_3$, con $\sigma'_3$ en MPa; $r = """ + f"{BG['r']:.2f}" + r"""$). Es mayor en el hornfels (""" + f"{BG['por_lit']['Hornfels'][0]:.0f}--{BG['por_lit']['Hornfels'][1]:.0f}" + r"""~\%) y el mármol (""" + f"{BG['por_lit']['Mármol'][0]:.0f}--{BG['por_lit']['Mármol'][1]:.0f}" + r"""~\%) que en el intrusivo (""" + f"{BG['por_lit']['Intrusivo'][0]:.0f}--{BG['por_lit']['Intrusivo'][1]:.0f}" + r"""~\%).

La rotura ya es importante a 1--2.5~MPa: con $\sigma'_3$ de """ + f"{BG12.s3.min():.2f} a {BG12.s3.max():.2f}" + r"""~MPa, $B_g$ va de """ + f"{BG12.Bg.min():.1f} a {BG12.Bg.max():.0f}" + r"""~\%, y en el hornfels y el mármol de gran escala, de """ + f"{BG12[BG12.escala != '6 in'][BG12.litologia.isin(['Hornfels', 'Mármol'])].Bg.min():.0f} a {BG12[BG12.escala != '6 in'][BG12.litologia.isin(['Hornfels', 'Mármol'])].Bg.max():.0f}" + r"""~\%: una parte apreciable de las partículas se fragmenta durante el ensayo. En la literatura, la rotura es el mecanismo al que se atribuye la curvatura de la envolvente a alto confinamiento \citep{marsal1967,indraratna1993}. En la base de Leps 2.0, sin embargo, $B_g$ apenas se correlaciona con $m$ (sección~\ref{sec:alto}), y en los ensayos de Antamina una rotura de hasta 39~\% no curvó la envolvente hasta """ + f2(SNX) + r"""~MPa. La rotura no justifica por sí sola la curvatura sobre ese esfuerzo; la justificación es la base mundial. La rotura también aumenta con el tamaño de partícula, lo que se trata en la sección~\ref{sec:tamano}. Con un solo valor de $B_g$ por ensayo, y sin ensayos sobre 2.45~MPa, los datos no permiten cuantificar la curvatura a partir de la rotura.

\begin{figure}[H]\centering\includegraphics[width=0.9\linewidth]{figs/Fig5_bg.pdf}
\caption{Índice de rotura de \citet{marsal1967} en los triaxiales drenados del ajuste, según el esfuerzo efectivo de confinamiento. Símbolos llenos: probetas de 0.6 y 1~m; vacíos: probetas de 6~in.}\label{fig:bg}\end{figure}

\section{Curva propuesta}\label{sec:curva}
Stantec propone una curva de Leps 2.0 para el desmonte ROM, con el nivel anclado a los ensayos de Antamina y la curvatura de la base mundial ($m = """ + f"{MC:.2f}" + r"""$). La curva trata el desmonte como un solo material, como el diseño del DDE \citep[Tabla~3-1]{stantec2026iff}: se ajustó con los """ + str(len(P_CP)) + r""" ensayos de Antamina con igual peso: los de mármol, hornfels e intrusivo y las dos mezclas (el compuesto de \citealp{g2021}, triaxial de 6~in, y la pila 01 de mármol y hornfels de \citealp{anddes2024}, corte directo), que representan desmonte mezclado:
\begin{equation}
\tau = \tan\!\left(""" + f"{OP2['pe0']:.2f}" + r"""° - 20°\,e\right)\,(10p_a)^{""" + f"{1 - MC:.3f}" + r"""}\,\sigma_n'^{\,""" + f"{MC:.3f}" + r"""},\qquad \phi'_1(e = 0.45) = """ + f2(p2) + r"""°
\end{equation}
Como control, el DDE incluye en sus bases de diseño la producción de desmonte por litología desde 2021: intrusivo y exoskarn, 44~\%, y hornfels y mármol, 56~\% \citep[Tabla~3-1]{stantec2026iff}. Ponderar los ensayos de las tres litologías con esas fracciones (con el 56~\% repartido por igual entre hornfels y mármol, que el DDE no separa, y el 44~\% asignado al intrusivo, porque no hay ensayos de exoskarn) da $\phi'_{e=0} = """ + f2(OP2['pe0_dde']) + r"""°$, prácticamente la misma curva. El mármol es la litología ensayada más débil (sección~\ref{sec:vacios}). Comparada con la cota inferior de \citet{hc2017} para construcción descendente de botaderos de peligro muy alto o alto ($\tau = 1.446\,\sigma^{0.898}$ en kPa, Tabla~5.9, propuesta para enrocado de calidad alta y moderada), la curva propuesta queda """ + sg(phis(1, OP2['pe0'], MC) - HC(1), 2) + "° a 1~MPa, " + sg(phis(3, OP2['pe0'], MC) - HC(3), 2) + "° a 3~MPa y " + sg(phis(8, OP2['pe0'], MC) - HC(8), 2) + r"""° a 8~MPa. Con $e = 0.45$, la curva propuesta queda """ + HC_POS + r""" esa cota genérica, y """ + f"{N_SOBRE_HC} de los {len(P)}" + r""" ensayos llevados a esa $e$ quedan sobre ella; la diferencia depende principalmente de la $e$ de colocación (sección~\ref{sec:e}).

\citet[Fig.~13, p.~49]{indraratna1993} propusieron un límite inferior para la resistencia de enrocados, 3° bajo el límite inferior que \citet{leps} había dado para enrocado de baja densidad, trazado entre unos 7~kPa y 3.5~MPa. \citet[p.~13]{cylwik} lo compararon con los ensayos de enrocados de calidad baja de su base ($e > 0.45$), normalizados a $e = 0.6$, encontraron que captura el borde inferior de esos datos y lo reproducen con su Ec.~9, $m = 0.9$ y $\phi'_1 = 33°$. Esos ensayos llegan a $\sigma'_n \approx 0.75$~MPa \citep[Fig.~19]{cylwik}, de modo que sobre ese esfuerzo la forma con $m = 0.9$ es una extrapolación. No es un ángulo mínimo constante: su ángulo secante también baja con el esfuerzo. En esa forma no depende de $e$ \citep[Tabla~1]{cylwik} y queda 3° bajo la envolvente inferior de \citet{leps}; da """ + f"{LB(1):.1f}° a 1~MPa, {LB(SNX):.1f}° a {f2(SNX)}~MPa y {LB(8):.1f}° a 8~MPa" + r""" (Figs.~\ref{fig:phi} y~\ref{fig:tau}). La curva propuesta queda """ + f"{sg(phis(1, OP2['pe0'], MC) - LB(1), 1)}° sobre esa forma a 1~MPa, {sg(phis(SNX, OP2['pe0'], MC) - LB(SNX), 1)}° a {f2(SNX)}~MPa, {sg(phis(8, OP2['pe0'], MC) - LB(8), 1)}° a 8~MPa y {sg(phis(15, OP2['pe0'], MC) - LB(15), 2)}° a 15~MPa" + (r""", y sobre ella en todo el rango hasta 15~MPa""" if LB_SOBRE else f", y la cruza a unos {S_LB:.1f}~MPa") + r""". Sobre """ + f2(SNX) + r"""~MPa las dos son extrapolaciones: la curva propuesta, de los ensayos de Antamina (sección~\ref{sec:rango}), y la cota, de ensayos que llegan a unos 0.75~MPa. La cota no se usa para acotar la banda, porque """ + f"{len(PBAJO)} de los {len(P)}" + r""" ensayos de Antamina quedan por debajo de ella, """ + f"{N_BAJO_LB_06}" + r""" con $\sigma'_n \le 0.6$~MPa; los más alejados son la mezcla triaxial de 6~in de \citet{g2021} a """ + f"{f2(PB.sn)}~MPa ({abs(PB.phis_e065 - LB(PB.sn)):.1f}°" + r""" por debajo) y los cortes directos de la ruma de mármol ROM (hasta """ + f"{abs((PBAJO_MN.phis_e065 - PBAJO_MN.cota).min()):.1f}" + r"""° por debajo). \citet{cylwik} advierten, además, que su base no tiene rocas con resistencia a la compresión menor que 25~MPa y que materiales más débiles pueden quedar bajo sus predicciones.

\textbf{A grandes esfuerzos.} Sobre """ + f2(SNX) + r"""~MPa la curva no tiene ensayos de Antamina, así que conviene contrastarla con los ensayos más altos disponibles, cada uno con la curva evaluada a su propia $e$. Entre """ + f2(SNX) + r""" y """ + f2(SNW) + r"""~MPa, """ + f"{A25['ensayos'][_W]['n'] - A25['ensayos'][_W]['bajo_curva']} de los {A25['ensayos'][_W]['n']}" + r""" ensayos de la base mundial quedan sobre la curva, con una mediana de """ + sg(A25['ensayos'][_W]['dphi_mediana']) + r"""° en $\phi'_s$, y de los """ + f"{A25['ensayos'][_A]['n']}" + r""" ensayos de Antamina con $\sigma'_n$ sobre 3~MPa, """ + f"{A25['ensayos'][_A]['n'] - A25['ensayos'][_A]['bajo_curva']}" + r""" quedan sobre ella (mediana """ + sg(A25['ensayos'][_A]['dphi_mediana']) + r"""°): la curva queda del lado conservador a grandes esfuerzos. A 10~MPa da """ + f"{phis(10, OP2['pe0'], MC):.1f}" + r"""°, sobre la cota de \citet{indraratna1993} (""" + f"{LB(10):.1f}" + r"""°) y la de \citet{hc2017} (""" + f"{HC(10):.1f}" + r"""°), y bajo los 33° que el DDE usó como sensibilidad entre 5 y 10~MPa de esfuerzo vertical efectivo, con 30° por encima \citep[§3.5.3.6, Tabla~3-24, nota~4]{stantec2026iff}; en la base de una dovela, $\sigma'_n \le \sigma'_v$.

El exponente $m = """ + f"{MC:.2f}" + r"""$ es el que predice sin sesgo los ensayos mundiales de mayor esfuerzo (sección~\ref{sec:alto}), algo menor que el valor estándar del modelo simplificado (0.9). Las hipótesis de curvatura, incluida $m = 1$, están en la Tabla~\ref{tab:hip}.

\textbf{Posición frente a \citet{leps}.} Las envolventes de \citet{leps}, en la forma de Leps 2.0 ($\phi'_1$ = 36°, 41° y 46° con $m = 0.9$; \citealp[p.~2]{cylwik}), no dependen de $e$: la densidad está en la clase (baja densidad, promedio, alta densidad). Por eso la posición de la curva propuesta frente a ellas depende de la $e$ con que se la evalúe. Con $e = 0.45$ constante, la curva cruza la envolvente media a """ + f2(X_MED) + r"""~MPa, queda entre la media y la inferior sobre ese esfuerzo y alcanza la inferior a unos """ + f1(X_INF) + r"""~MPa, porque su $m$ es menor que 0.9. Con la $e$ del perfil A, que baja con la profundidad (sección~\ref{sec:e}), la curva sigue a la envolvente media: en una escala en que 0 es la envolvente inferior y 1 la media, su posición es """ + ", ".join(f"{v_:.2f}" for v_ in POS_A) + r""" a 1, 4, 10 y 15~MPa. Para comparar con \citet{leps}, la $e$ de colocación pesa tanto como la curva misma.

\subsection*{Comportamiento a bajo confinamiento}
Las curvas se entregan sin tope. Con $m < 1$, el ángulo secante de Leps 2.0 crece al bajar $\sigma'_n$ y supera el ángulo de reposo de las caras de volteo de Antamina (típicamente 37° en caras de volteo; \citealp[§16.5]{hc2017}) bajo $\sigma'_n$ = """ + f"{s_cruce(OP2['pe0']):.2f}" + r"""~MPa con $e = 0.45$. \citet{cylwik} indican que bajo 0.1~MPa el criterio tiende a subestimar la resistencia medida. Para el desmonte suelto de la cara, en cambio, la resistencia movilizable está cerca del ángulo de reposo. Con $\sigma'_n$ menor que 0.5~MPa hay """ + f"{len(LOWP)}" + r""" ensayos: la mezcla triaxial de \citet{g2021} (6~in, $\sigma'_3 = """ + f2(ROWB.s3) + r"""$~MPa, máximo desviador con """ + f1(ROWB.eps_axial_falla_pct) + r"""~\% de deformación axial) y los cortes directos a 0.3~MPa. Llevados a $e = 0.45$, sus ángulos van de """ + f"{LOWP.phis_e065.min():.1f}° a {LOWP.phis_e065.max():.1f}°" + r""", frente a unos """ + f"{LOWP.curva.mean():.0f}" + r"""° de la curva: """ + f"{int((LOWP.dif < 0).sum())} quedan bajo la curva y {int((LOWP.dif >= 0).sum())} sobre ella" + r""". A bajo confinamiento los ensayos son pocos y muy dispersos, y no respaldan la curva de forma consistente.

Por eso, la curva sin tope se entrega con una condición de aplicación: los mecanismos de cara y de banco, con $\sigma'_n$ menor que el cruce con 37° (""" + f"{s_cruce(OP2['pe0']):.1f}" + r"""~MPa), se verifican además con $\phi' = 37°$. \citet[§8.4.1.1]{hc2017} indican que el peligro de inestabilidad superficial de las caras a ángulo de reposo se maneja normalmente con procedimientos operacionales, y que analizarlo no suele aportar, porque su factor de seguridad es 1 por definición. Por eso la verificación con 37° tiene sentido en caras y bancos más tendidos que el ángulo de reposo.

\section{Valores para los modelos de equilibrio límite}\label{sec:valores}
La Tabla~\ref{tab:slide} da los pares $\sigma'_n$--$\tau$ de la curva propuesta a $e = 0.45$ y de los límites de su incertidumbre, y la Tabla~\ref{tab:slide_e}, los de la curva propuesta para cada supuesto de $e$. Ambas incluyen el origen y puntos desde 10~kPa, para definir la curva cerca del origen. Las curvas con $e$ constante también pueden cargarse como función de potencia (\emph{Power Curve} de Slide2, $\tau = a(\sigma'_n + d)^b + c$), con los parámetros de la Tabla~\ref{tab:power}. Los perfiles $e(z)$ no son una función de potencia y se cargan como pares. La Fig.~\ref{fig:tau} compara la curva propuesta con las envolventes de \citet{leps} y la cota inferior de \citet{indraratna1993}.

\begin{table}[htbp]\centering\small\caption{Pares $\sigma'_n$--$\tau$ a $e = 0.45$: curva propuesta y límites de su incertidumbre.}\label{tab:slide}
\begin{tabular}{rrrrr}\toprule $\sigma'_n$ & $\tau$ curva propuesta & $\tau$ límite inferior$^{b}$ & $\tau$ límite superior$^{b}$ & $\phi'_s$ curva propuesta\\
(kPa) & (kPa) & (kPa) & (kPa) & (°)\\\midrule
""" + "\n".join(filas_t4) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{a}$Sobre el máximo $\sigma'_n$ de los ensayos de Antamina (""" + f2(SNX) + r"""~MPa). $^{w}$Sobre el máximo de la base mundial de Leps 2.0 (""" + f2(SNW) + r"""~MPa): extrapolación fuera de toda la data (sección~\ref{sec:rango}). $^{b}$Límites de incertidumbre para sensibilidad; no son valores de diseño. Bajo 0.5~MPa hay pocos ensayos y muy dispersos.\end{table}

\begin{table}[htbp]\centering\small\caption{Pares $\sigma'_n$--$\tau$ (kPa) de la curva propuesta según la relación de vacíos y de la recta de 37° para verificar caras y bancos.}\label{tab:slide_e}
\setlength{\tabcolsep}{4pt}\begin{tabular}{rrrrrrr}\toprule $\sigma'_n$ & $e = 0.45$ & $e = 0.55$ & $e = 0.65$ & Perfil A & Perfil V & $\phi' = 37°$\\
(kPa) & (base) & & & & & \\\midrule
""" + "\n".join(filas_t5) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{a}$Sobre el máximo $\sigma'_n$ de los ensayos de Antamina (""" + f2(SNX) + r"""~MPa). $^{w}$Sobre el máximo de la base mundial (""" + f2(SNW) + r"""~MPa): extrapolación fuera de toda la data. Perfil V: sin valores sobre $\sigma'_v \approx """ + f"{max(s for s, e_ in zip(PE['sv_V'], PE['e_V']) if e_ is not None):.1f}" + r"""$~MPa, donde termina la curva de Valenzuela et al.\ (600~m de altura).\end{table}

\begin{table}[htbp]\centering\small\caption{Parámetros de \emph{Power Curve} de Slide2 ($\tau = a(\sigma'_n + d)^b + c$, con $\sigma'_n$ y $\tau$ en kPa), equivalentes a Leps 2.0 con $e$ constante: $a = \tan\phi'_1 \cdot 1013^{1-m}$, $b = m$.}\label{tab:power}
\begin{tabular}{lrrrrrrr}\toprule Curva & $\phi'_{e=0}$ (°) & $e$ & $\phi'_1$ (°) & $a$ & $b$ & $c$ (kPa) & $d$ (kPa)\\\midrule
""" + "\n".join(filas_pc) + r"""
\bottomrule\end{tabular}\end{table}

\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]{figs/Fig2_tau_sigma.pdf}
\caption{Curva propuesta y su banda de incertidumbre en $\tau$--$\sigma'_n$, con los ensayos drenados llevados a $e = 0.45$ (incluidas las dos mezclas) y, en gris claro, la base mundial de Leps 2.0 llevada a la misma $e$. En gris, como referencia: las envolventes superior, media e inferior de \citet{leps} y la cota inferior de \citet{indraratna1993}, en la forma de la Ec.~9 de Leps 2.0 ($m = 0.9$; \citealp[p.~2 y Tabla~1]{cylwik}).}\label{fig:tau}\end{figure}

\section{Relación de vacíos de colocación}\label{sec:e}
La $e$ de colocación es el supuesto que más mueve la curva: cada 0.05 de $e$ cambia $\phi'_1$ en 1°. La $e$ depende de cómo se coloca el material, y en Antamina hay tres materiales de desmonte con colocación distinta:
\begin{itemize}
\item \textbf{Desmonte ROM}, descargado de camiones y volteado sin compactar, con tamaño máximo de partícula del orden de 1~m \citep[Tabla~3-1]{stantec2026iff}: es el más suelto. Es el material de esta curva.
\item \textbf{Desmonte chancado}, más fino y mejor gradado, colocado con fajas sin compactar: es más denso que el ROM.
\item \textbf{Enrocado 3B} de la presa de relaves, colocado en capas y compactado con rodillo: es el más denso. Parte de los ensayos del ajuste son de este material (sección~\ref{sec:datos}).
\end{itemize}
La $e$ in situ del ROM no se ha medido directamente, pero los pesos unitarios que miden y adoptan los estudios de Antamina permiten calcularla (Tabla~\ref{tab:ebase}). Para el ROM dan $e$ de 0.25 a 0.45, con el valor más bajo medido en la superficie de un botadero; la literatura da 0.25 a 0.9, con 0.45 a 0.49 en botaderos altos de volteo. El valor base, """ + EB_TXT + r""", está en el extremo suelto del rango de Antamina y en el de la literatura: es representativo del ROM volteado y queda del lado conservador. El chancado y el enrocado dan $e$ de 0.25 a 0.28, claramente más densos; por eso los ensayos de enrocado compactado ($e_0$ de 0.30 a 0.34) se llevan a la $e$ del ROM con la regla de densidad de Leps 2.0 antes de ajustar la curva. El valor base está dentro del rango de los ensayos ($e_0$ = """ + f"{P.e.min():.3f}" + r"""--""" + f"{P.e.max():.3f}" + r"""), así que esa corrección no extrapola la regla. Con 0.65, más suelto que toda la evidencia y que la categoría «suelta» de Leps 2.0, la curva representaría el material más suelto de la cara de volteo; 0.55 y 0.65 se entregan como sensibilidad conservadora.

\begin{table}[!htbp]\centering\small\caption{Relación de vacíos de colocación del desmonte de Antamina según el material, calculada con los pesos unitarios de los estudios de Antamina, y valores de la literatura.}\label{tab:ebase}
\begin{tabular}{L{2.0cm}L{8.4cm}r>{\raggedleft\arraybackslash}p{2.1cm}}\toprule Material & Fuente & $\gamma$ (kN/m³) & $e$\\\midrule
ROM & Pesos unitarios totales medidos in situ en Antamina, con dispersión de 19 a 24~kN/m³; valor adoptado \citep[pp.~12--14, Fig.~4 y Tabla~3]{stantec2025sda} & 20.0 & """ + f"{EG(20.0, 0.029):.2f}" + r"""\\
ROM & Diseño geotécnico del DDE \citep[Tabla~9-3]{stantec2026dde} & 19.6 & """ + f"{EG(19.6, 0.029):.2f}" + r"""\\
ROM & Densidad del desmonte para el tonelaje del plan, 1.95~t/m³ \citep[Tabla~4-1]{stantec2026dde} & -- & """ + f"{2.75 / 1.95 - 1:.2f}--{2.75 * 1.029 / 1.95 - 1:.2f}" + r"""$^{a}$\\
ROM & Densidad por reemplazo de agua en la superficie del Botadero Tucush, junto al sondaje BH19-BT-01; probablemente compactada por el tránsito \citep[Anexo~C, Tabla~3]{wsp2023tsf} & -- & """ + f"{2.75 / 2.200 - 1:.2f}" + r"""$^{b}$\\
ROM & Peso unitario total promedio de \citet{g2010}, citado en \citet[p.~59]{stantec2026dde} & 20.75 & """ + f"{EG(20.75, 0.029):.2f}" + r"""\\
Chancado & \citet{g2010}, citado en \citet[p.~59]{stantec2026dde} & 21.66 & """ + f"{EG(21.66, 0.028):.2f}" + r"""\\
Chancado & Valor adoptado \citep[Tabla~3]{stantec2025sda} & 22.0 & """ + f"{EG(22.0, 0.028):.2f}" + r"""\\
Enrocado 3B & Diseño geotécnico del DDE \citep[Tabla~9-3]{stantec2026dde} y \citet[Tabla~3]{stantec2025sda} & 22.0 & """ + f"{EG(22.0, 0.029):.2f}" + r"""\\
\midrule
Literatura & \citet[Fig.~10]{valenzuela2008}, envolvente propuesta, en superficie ($\gamma_d \approx 1.84$~t/m³) & -- & 0.49\\
Literatura & \citet[§5.5.1.6]{hc2017}: botaderos (Dawson et al. 1998), Andina (Linero et al. 2006) y medidos en terreno (Golder Associates 1987) & -- & 0.4--0.9; 0.46; 0.25--0.3\\
Literatura & Leps 2.0 \citep[Tabla~6]{cylwik}: densa, media y suelta & -- & 0.30; 0.45; 0.60\\
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $e = G_s\,\gamma_w\,(1 + w)/\gamma - 1$, con $G_s$ = 2.75, $\gamma_w$ = 9.81~kN/m³ y la humedad informada en \citet[Tabla~3]{stantec2025sda} (2.9~\% en el ROM y 2.8~\% en el chancado). $^{a}$Densidad seca o húmeda: el informe no lo indica. $^{b}$Densidad seca medida de 2.200~t/m³.\end{table}

La $e$ de la curva es constante y no baja con el esfuerzo, aunque el desmonte se comprime con la profundidad. Hay dos razones. Primero, Leps 2.0 se calibró con la $e$ inicial de cada probeta, antes de consolidar: en su base, las probetas ensayadas a mayor confinamiento también se densificaron al consolidar, y ese efecto ya está dentro de la curvatura $m$. Bajar además la $e$ con la profundidad contaría dos veces la densificación. Segundo, la compresibilidad del ROM suelto en el botadero no se ha medido en Antamina. La densificación con la profundidad se evalúa aparte, como sensibilidad, con los perfiles $e(z)$ de esta sección.
 La $e$ de un botadero alto, además, no es constante: el desmonte se comprime y rompe con la carga, y \citet[Fig.~10]{valenzuela2008} propusieron, a partir de triaxiales y edómetros de gran escala, una envolvente de densidad seca que crece de unos 1.84 a 2.37~t/m³ entre la superficie y 600~m de altura ($e$ de 0.49 a 0.16 con $G_s = 2.75$; la figura está reproducida en \citealp[Fig.~5.6]{hc2017}). La evolución que adoptaron para el diseño de un botadero alto es escalonada y más conservadora, de 1.86 a 2.25~t/m³.

Por eso se entregan, para la curva propuesta (Fig.~\ref{fig:e}, Tablas~\ref{tab:ez}, \ref{tab:etau} y~\ref{tab:slide_e}):
\begin{itemize}
\item \textbf{$e$ constante de 0.45, 0.55 y 0.65}, para asignar por sectores o como sensibilidad.
\item \textbf{Perfiles $e(z)$ con densificación}, partiendo de $e = 0.45$ en superficie. El perfil A usa la compresibilidad de la rama de carga del edómetro de mármol más suelto de Antamina (probeta de 0.24~m, $e_0 = 0.455$ con $G_s = 2.70$ supuesto; \citealp{w2022}): $C_c$ = """ + f"{PE['Cc1']:.3f}" + r""" entre 0.2 y 0.8~MPa y """ + f"{PE['Cc2']:.3f}" + r""" entre 1.2 y 4.8~MPa, extrapolado fuera de ese rango. El perfil V usa la forma de la envolvente propuesta por \citet{valenzuela2008}, leída de la figura y desplazada para partir de $e = 0.45$; no es su curva de diseño, que es escalonada. Se usa la envolvente porque resume la tendencia de los ensayos de gran escala y es continua. Con la curva de diseño, desplazada de la misma manera, la $e$ a 600~m sería """ + f"{EC + 2.75 / 2.25 - 2.75 / 1.86:.2f}" + r""" en vez de """ + f"{[e_ for e_ in PE['e_V'] if e_ is not None][-1]:.2f}" + r""": el perfil V es, por eso, la más favorable de las alternativas de densificación, y se entrega como sensibilidad. A cada $\sigma'_n$ se le asigna la $e$ de la profundidad donde $\sigma'_v = \sigma'_n$; como en la base de una dovela $\sigma'_n \le \sigma'_v$, eso usa una $e$ algo más suelta que la real.
\end{itemize}
El perfil A llega a $e \approx """ + f"{PE['e_A'][-1]:.2f}" + r"""$ a 700~m y el V a $e \approx """ + f"{min(v for v in PE['e_V'] if v is not None):.2f}" + r"""$ a 600~m. A 8~MPa dan """ + f"{phis(8, OP2['pe0'], MC, _fe('Perfil A', 8)):.1f}° (A) y {phis(8, OP2['pe0'], MC, _fe('Perfil V', 8)):.1f}° (V)" + r""", frente a """ + f"{phis(8, OP2['pe0'], MC):.1f}" + r"""° con $e = 0.45$ constante: con densificación, la envolvente se acerca a la linealidad de los ensayos de Antamina, cuyas probetas también se densificaron.

Hay dos advertencias. Primero, aplicar la regla de Leps 2.0 ($-20°$ por unidad de $e$) a la densificación por carga es un supuesto, porque la regla se calibró con probetas compactadas y en el botadero la densificación viene con rotura de partículas. Segundo, la compresibilidad del desmonte suelto en botadero no se ha medido en Antamina: los edómetros son de probetas compactadas, con la gradación cortada. La Tabla~\ref{tab:edo} muestra los """ + f"{len(EDO)}" + r""" edómetros disponibles y la $e$ que daría cada uno con la ley del perfil A. Los más sueltos ($e_0 \ge 0.42$) dan $e$ de """ + f"{min(r['perfil']['700'] for r in EDO_S):.2f} a {max(r['perfil']['700'] for r in EDO_S):.2f}" + r""" a 700~m, y los densos, de """ + f"{min(r['perfil']['700'] for r in EDO_D):.2f} a {max(r['perfil']['700'] for r in EDO_D):.2f}" + r""". El perfil A está dentro del rango de los sueltos; los densos, ya compactados, se comprimen menos y darían un perfil menos favorable. Por eso los perfiles son una sensibilidad del lado no conservador y no una curva de diseño, hasta contar con densidad in situ representativa del desmonte volteado (sección~\ref{sec:datos}).

\begin{table}[!htbp]\centering\small\caption{Edómetros de desmonte de Antamina: compresibilidad en la rama de carga y $e$ que resulta con la ley del perfil A ($e = 0.45$ en superficie). $C_c$: pendiente de $e$ frente a $\log\sigma'_v$, entre 0.2 y 0.8~MPa ($C_{c1}$) y entre 1.2 y 4.8~MPa ($C_{c2}$).}\label{tab:edo}
\begin{tabular}{L{4.2cm}lrrrrr}\toprule Edómetro & Probeta & $e_0$ & $C_{c1}$ & $C_{c2}$ & $e$ a 300~m & $e$ a 700~m\\\midrule
""" + "\n".join(filas_edo) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{g}$$e$ leída de los gráficos del informe (sin hoja de laboratorio). $^{s}$$G_s = 2.60$ estimado por el laboratorio, no ensayado; con el $G_s$ de sólidos (ASTM D854, \citealp{g2010}) la $e_0$ sería mayor (0.33 en el hornfels). Fuentes: \citet{w2022} y \citet{w2024}; el mármol de 1~m de 2011 es el de \citet{g2012}.\end{table}

\begin{table}[htbp]\centering\small\caption{Relación de vacíos y esfuerzo vertical efectivo con la profundidad (sin presión de poros, $G_s = 2.75$, $w = 5$~\%).}\label{tab:ez}
\begin{tabular}{rrrrr}\toprule Profundidad (m) & $\sigma'_v$, perfil A (MPa) & $e$, perfil A & $\sigma'_v$, perfil V (MPa) & $e$, perfil V\\\midrule
""" + "\n".join(filas_ez) + r"""
\bottomrule\end{tabular}\end{table}

\begin{table}[htbp]\centering\small\caption{Ángulo de fricción secante $\phi'_s$ (°) de la curva propuesta según la relación de vacíos.}\label{tab:etau}
\setlength{\tabcolsep}{3pt}\begin{tabular}{l""" + "r" * len(SNE) + r"""}\toprule $e$ & """ + " & ".join(f"{s:g}~MPa" + ext(s) for s in SNE) + r"""\\\midrule
""" + "\n".join(filas_et) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize Las curvas con $e$ constante siguen la Ec.~(2) con la $e$ indicada; los pares $\sigma'_n$--$\tau$ están en la Tabla~\ref{tab:slide_e}. $^{a}$Sobre el máximo $\sigma'_n$ de los ensayos de Antamina (""" + f2(SNX) + r"""~MPa). $^{w}$Sobre el máximo de la base mundial (""" + f2(SNW) + r"""~MPa): extrapolación fuera de toda la data (sección~\ref{sec:rango}). $^{c}$La envolvente de Valenzuela et al.\ llega a 600~m de altura ($\sigma'_v \approx """ + f"{max(s for s, e_ in zip(PE['sv_V'], PE['e_V']) if e_ is not None):.1f}" + r"""$~MPa con el peso unitario de este memorándum); sobre ese esfuerzo no se extrapola.\end{table}

\begin{figure}[htbp]\centering\includegraphics[width=\linewidth]{figs/Fig3_perfil_e.pdf}
\caption{(a) Relación de vacíos con la profundidad: valores constantes y perfiles con densificación desde $e = 0.45$ (A, compresibilidad del edómetro de Antamina; V, forma de la envolvente propuesta por \citealp{valenzuela2008}). (b) Ángulo de fricción secante de la curva propuesta con cada supuesto; zona gris y rayado como en la Fig.~\ref{fig:phi}.}\label{fig:e}\end{figure}

\section{Sensibilidades y vacíos}\label{sec:vacios}
\begin{itemize}
\item \textbf{Litologías.} Con $m = """ + f"{MC:.2f}" + r"""$, el $\phi'_1$ medio a $e = 0.45$ es """ + f"{LITM['Mármol']:.1f}° en mármol, {LITM['Intrusivo']:.1f}° en intrusivo y {LITM['Hornfels']:.1f}° en hornfels" + r""". La curva trata el desmonte como un solo material, como el diseño del DDE; donde el volteo concentre mármol, la litología ensayada más débil, la resistencia sería menor: de los """ + f"{len(PMN)}" + r""" ensayos de mármol, """ + f"{n_mn_bajo_curva}" + r""" quedan bajo la curva propuesta. El mármol descansa en un solo set triaxial de gran escala, con 3 de sus 5 ensayos con ciclos de carga y descarga, en un set de 6~in y en el corte directo de la ruma de mármol ROM de \citet{anddes2024}, y tiene desgaste Los Ángeles de 41--44~\% (nota de \citealp{g2012}), lo que sugiere susceptibilidad a la rotura.
\item \textbf{Condiciones no cubiertas.} La curva es drenada y de máximo desviador. No cubre presiones de poros en capas basales saturadas, colapso por humedecimiento, degradación en el tiempo, condición sísmica ni post-sísmica.
\end{itemize}

\subsection{Efecto del tamaño de partícula}\label{sec:tamano}
Leps 2.0 no tiene un término de tamaño: en su base mundial, el tamaño medio de partícula ($D_{50}$) no mostró una correlación fuerte con la resistencia, y sus efectos pueden haber quedado bajo el ruido de los datos \citep[Tabla~4]{cylwik}. Los dos pares de escala de Antamina tampoco permiten estimarlo (sección~\ref{sec:metodo}). La teoría de \citet{frossard2012}, en cambio, predice que un material más grueso de la misma roca resiste menos, porque las partículas grandes rompen con menor esfuerzo. Para gradaciones paralelas, la envolvente del material grueso es la del fino con los esfuerzos escalados por $\lambda = (D_{lab}/D_{campo})^{3/m_w}$, donde $m_w$ es el módulo de Weibull de la resistencia de las partículas. Con la envolvente de Leps 2.0, eso equivale a multiplicar $\tau$ por $\lambda^{1-m}$ en todo el rango.

Como no hay ensayos de resistencia de partículas por tamaño en Antamina, Stantec tomó como valor central el exponente de la corrección por tamaño del ensayo de carga puntual, 0.45 \citep{isrm1985}, que equivale a $m_w = 6.7$, y un rango de 4 a 10. Los ensayos del ajuste tienen tres tamaños de partícula: $D_{max} = """ + f"{DLABS[0]:.0f}" + r"""$~mm en los triaxiales de 1~m, """ + f"{DLABS[1]:.0f}" + r"""~mm en los de 0.6~m y """ + f"{DLABS[2]:.0f}" + r"""~mm en las probetas de 6~in y el corte directo. Con $D_{campo} = 1000$~mm, entre la mediana (""" + f"{FR['Dmax']:.0f}" + r"""~mm) y el percentil 90 (""" + f"{FR['Dmax_p90']:.0f}" + r"""~mm) de la fragmentación, resulta la Tabla~\ref{tab:tamano}: con el valor central, $\phi'_1$ bajaría """ + f"{abs(TAMC[round(DLABS[0])][1]):.1f}" + r"""° si el ensayo representativo es el de """ + f"{DLABS[0]:.0f}" + r"""~mm y """ + f"{abs(TAMC[round(DLABS[2])][1]):.1f}" + r"""° si es el de """ + f"{DLABS[2]:.0f}" + r"""~mm. \citet{frossard2012} recomiendan limitar la razón de escalamiento a 15: de """ + f"{DLABS[0]:.0f}" + r"""~mm a 1000~mm es """ + f"{DCAMPO / DLABS[0]:.1f}" + r""", pero de """ + f"{DLABS[2]:.0f}" + r"""~mm es """ + f"{DCAMPO / DLABS[2]:.0f}" + r""", fuera de ese límite. Los dos pares de escala de Antamina no muestran una diferencia sistemática entre esos tamaños (sección~\ref{sec:metodo}), lo que no es coherente con el efecto teórico entre 25 y 178~mm. El método supone gradaciones paralelas, lo que no se cumple con las gradaciones escalpadas de los ensayos, y no se ha verificado en desmonte de Antamina. Por eso el efecto se informa como sensibilidad y no se aplica a la curva propuesta.

\begin{table}[H]\centering\small\caption{Sensibilidad al tamaño de partícula, del ensayo al desmonte con $D_{campo} = 1000$~mm \citep{frossard2012}: factor sobre $\tau$ y $\phi'_1$ de la curva propuesta a $e = 0.45$.}\label{tab:tamano}
\begin{tabular}{rlrrr}\toprule $D_{lab}$ (mm) & $m_w$ & Factor sobre $\tau$ & $\phi'_1$ (°) & Diferencia (°)\\\midrule
""" + "\n".join(filas_tam) + r"""
\bottomrule\end{tabular}\end{table}

\subsection*{Riesgos de la curva y cómo se cubren}
La Tabla~\ref{tab:riesgos} resume qué riesgos se cubren hoy con margen o con la forma de aplicar la curva, y cuáles requieren ensayos.
\begin{table}[!htbp]\centering\small\caption{Riesgos principales de la curva propuesta.}\label{tab:riesgos}
\begin{tabular}{L{5.0cm}L{5.6cm}L{4.6cm}}\toprule Riesgo & Cobertura en esta revisión & Qué lo cierra\\\midrule
$e = 0.45$ no medida (cada 0.05 de $e$ cambia $\phi'_1$ en 1°) & Coherente con el $\gamma$ del DDE y con la literatura (Tabla~\ref{tab:ebase}); alternativas 0.55 y 0.65 y perfiles $e(z)$ & Densidad in situ (ítem~1)\\
Mármol, la litología ensayada más débil: un set triaxial de gran escala (enrocado de presa, 3 de 5 ensayos con carga y descarga), uno de 6~in y un corte directo ROM & Curva de un solo material, como el DDE; no cubre sectores con predominio de mármol & Triaxiales de mármol ROM (ítem~2)\\
""" + f"{n_contr_seg} de {n_eps}" + r""" triaxiales con contracción volumétrica en el máximo desviador (""" + f"{n_contr}" + r""" si se cuentan los de signo dudoso) & Del lado conservador: el máximo desviador puede subestimar la resistencia última & Ensayos hasta 25~\% de deformación (ítem~2)\\
Curvatura sobre """ + f2(SNX) + r"""~MPa & Hipótesis P10--P90 en la banda; sensibilidad con $m = """ + f"{RM['m_P10_sets']:.2f}" + r"""$ & Triaxiales a alta presión (ítem~4)\\
Segregación por volteo & No cubierta: curva de un solo material, como el DDE & Modelo de bloques y plan de colocación, si el EoR lo requiere\\
Bajo confinamiento: pocos ensayos y dispersos & Verificación de caras y bancos con 37° & --\\
Efecto del tamaño de partícula & Sensibilidad (Tabla~\ref{tab:tamano}); no aplicado a la curva & Ensayos de resistencia de partículas por tamaño (carga puntual o compresión de partículas)\\
\bottomrule\end{tabular}\end{table}

\section{Ensayos que más reducirían la incertidumbre}\label{sec:ensayos}
La Tabla~\ref{tab:ensayos} ordena los ensayos por el valor de la información para la curva. Las cantidades son mínimas. El costo, el plazo y el laboratorio quedan """ + PC + r"""{por confirmar}; para $\sigma'_3$ de 3 a 6~MPa en probetas de 1~m hay que confirmar primero que exista el equipo.

\begin{table}[H]\centering\small\caption{Programa de ensayos propuesto.}\label{tab:ensayos}
\begin{tabular}{L{0.4cm}L{3.0cm}L{6.4cm}L{5.0cm}}\toprule & Ensayo & Cantidad y condiciones & Decisión que informa\\\midrule
1 & Densidad in situ & Al menos 10 ensayos de reemplazo de agua en macrocalicatas en botaderos existentes, bajo la capa compactada por el tránsito o en material de cara volteado, repartidos por litología dominante; conciliación de toneladas transportadas contra volumen topográfico por botadero; registro de densidad en sondajes, donde existan, para la variación con la profundidad & $e$ de colocación (base 0.45) y perfil $e(z)$\\
2 & Triaxiales de mármol ROM & Un set de 4 probetas, diámetro de 1~m, $\sigma'_3$ = 0.5, 1.0, 1.5 y 2.0~MPa, $e \approx 0.6$, hasta 25~\% de deformación axial con medición de volumen & Resistencia de la litología ensayada más débil\\
3 & Edómetro de gran escala & Dos ensayos (mármol ROM y desmonte mezclado), diámetro mínimo de 0.6~m, desde $e \approx 0.65$ hasta $\sigma'_v$ de 5~MPa o el máximo del equipo & Compresibilidad del perfil $e(z)$\\
4 & Triaxiales a alta presión & Un set de 3 probetas de mármol, $\sigma'_3$ = 3, 4.5 y 6~MPa, con el mayor diámetro disponible; solo si un mecanismo lleva el diseño a esos esfuerzos & Curvatura $m$ sobre """ + f2(SNX) + r"""~MPa\\
\bottomrule\end{tabular}\end{table}

\section{Implementación en FLAC2D}\label{sec:flac}
FLAC2D (versión 9.0) no tiene un modelo constitutivo con la envolvente de potencia de Leps 2.0, pero la curva se puede usar con el modelo \texttt{mohr-coulomb}: en cada zona, la cohesión y la fricción se reemplazan por las de la recta tangente a la curva en el punto que corresponde al esfuerzo de la zona. El criterio de falla sigue siendo Mohr--Coulomb; lo que cambia de zona a zona son $c'$ y $\phi'$. Los parámetros elásticos no son parte de esta propuesta.

El procedimiento, que una función FISH aplica a todas las zonas del desmonte, es:
\begin{enumerate}
\item Con el $\sigma'_3$ de la zona, $-(\texttt{zone.stress.max} + \texttt{zone.pp})$ porque FLAC usa compresión negativa, se busca el $\sigma'_n$ del punto de tangencia del círculo de falla con la envolvente. Es el mismo cálculo con que este memorándum convierte los triaxiales (Ecs.~10--12 de \citealp{cylwik}).
\item En ese punto, $\tan\phi'_t = m\,\tau/\sigma'_n$ y $c'_t = (1-m)\,\tau$, que se asignan como \texttt{friction} (°) y \texttt{cohesion} (Pa).
\item Como la tangente depende del esfuerzo, la actualización y \texttt{model solve} se alternan hasta que las propiedades dejen de cambiar. Un piso de $\sigma'_3$ (10~kPa) evita que la cohesión se anule en la superficie.
\end{enumerate}
La Tabla~\ref{tab:flac} da los valores tangentes de la curva propuesta ($e = 0.45$) a varios $\sigma'_3$, para comprobar la implementación. La curva es cóncava, así que la recta tangente queda por encima de ella lejos del punto de tangencia: si los esfuerzos cambian después de la última actualización, la resistencia queda sobrestimada. Por eso la actualización se repite hasta converger. El procedimiento admite $e$ variable con la profundidad: basta guardar la $e$ de cada zona en una variable extra (\texttt{zone.extra}) y usarla en $\phi'_1$.

\begin{table}[!htbp]\centering\small\caption{Mohr--Coulomb tangente a la curva propuesta ($e = 0.45$) según el esfuerzo principal menor de la zona, para verificar la implementación en FLAC2D.}\label{tab:flac}
\begin{tabular}{rrrrrr}\toprule $\sigma'_3$ (MPa) & $\sigma'_n$ (MPa) & $\tau$ (kPa) & $\phi'_t$ (°) & $c'_t$ (kPa) & $\sigma'_1 - \sigma'_3$ (MPa)\\\midrule
""" + "\n".join(filas_flac) + r"""
\bottomrule\end{tabular}\end{table}

{\sloppy La librería \texttt{leps2\_tangente.fis}, que acompaña este memorándum, implementa los tres pasos. Se carga con \texttt{program call} después de asignar \texttt{mohr-coulomb} al grupo \texttt{desmonte}; en cada etapa, la función \texttt{leps\_equilibrar} reemplaza al \texttt{model solve}:\par}
{\footnotesize
\begin{verbatim}
""" + FIS_TXT + r"""
\end{verbatim}}

\noindent\textbf{Factor de seguridad.} \texttt{model factor-of-safety} reduce $c'$ y $\tan\phi'$ de cada zona por el mismo factor, lo que equivale a dividir la curva por ese factor en el punto de tangencia, pero deja fijas las tangentes mientras la reducción redistribuye los esfuerzos. Sirve como primera estimación. El valor consistente con la curva se obtiene con una reducción propia: para un factor de prueba $F$ se divide la curva por $F$ (variable \texttt{leps\_fos}), se repiten la actualización y el equilibrio desde el mismo estado guardado (\texttt{model save} y \texttt{model restore}), y se busca por bisección el $F$ con que el modelo deja de converger. En pruebas de Stantec con FLAC2D 9.0, \texttt{model factor-of-safety} no terminó en un talud de arena con cohesión nula; el piso de $\sigma'_3$ deja una cohesión tangente pequeña en la superficie, pero conviene verificar que el cálculo termine.

Antes de usar los resultados se recomienda:
\begin{enumerate}
\item Simular en FLAC triaxiales de una zona a los $\sigma'_3$ de la Tabla~\ref{tab:flac} y comparar el desviador; la diferencia debería ser de pocos por ciento.
\item Leer las propiedades asignadas (\texttt{zone.prop}) en algunas zonas y compararlas con la Tabla~\ref{tab:flac}.
\item Comparar el factor de seguridad de un caso simple con el de un programa de equilibrio límite (por ejemplo, Slide2 con Morgenstern--Price), con la misma geometría y la misma curva, y repetir con la malla de la mitad del tamaño.
\end{enumerate}
La librería pasa la revisión estática de sintaxis de FLAC2D 9.0, pero no se ha corrido en FLAC.

\section{Limitaciones y uso de este documento}\label{sec:uso}
Este memorándum es un borrador técnico para la revisión del Ingeniero de Registro (EoR) de los botaderos de Antamina, y la curva es una propuesta para esa revisión. La curva propuesta se basa en """ + str(len(P_CP)) + r""" ensayos de """ + str(P_CP.set.nunique()) + r""" sets, incluidas las dos mezclas, en el criterio Leps 2.0 y en supuestos declarados en el texto ($m$ de la base mundial, $e = 0.45$ y desmonte tratado como un solo material). Su aplicación a un diseño específico requiere la verificación del EoR con los datos del sitio, la geometría, las condiciones de agua y sismo y los criterios de aceptación que correspondan. El documento no incluye análisis de estabilidad.

Stantec usó los resultados de laboratorio de los informes de terceros listados en las referencias (Golder Associates, WSP, IDIEM y Anddes Geolab) tal como fueron informados. Stantec verificó que los valores de la base de datos coincidan con las hojas de laboratorio de cada informe o, donde no hay hoja, con sus gráficos, pero no repitió ni validó los ensayos. Los valores recalculados o leídos de gráficos se indican en el texto y en las notas de las tablas; entre ellos, la $e_0$ y el $B_g$ de \citet{g2012}, la $e$ de los ensayos de \citet{anddes2024} y de \citet{i2025}, las $e_0$ de los edómetros y los $\sigma'_n$ y $\phi'_s$ de los triaxiales, convertidos con Leps 2.0. Stantec preparó esta propuesta con la habilidad y diligencia razonables para el alcance descrito; su uso fuera de ese alcance y de las condiciones aquí descritas es responsabilidad de quien la aplique.

\vspace{6pt}\noindent\begin{tabular}{@{}lll@{}}
Preparado por: & """ + PC + r"""{XX} & Stantec\\
Revisado por: & """ + PC + r"""{XX} & Stantec\\
Aprobado por: & """ + PC + r"""{XX} & Stantec\\
\end{tabular}

\begin{thebibliography}{20}\small
\bibitem[Cylwik et al.(2025)]{cylwik} Cylwik, S.~D., Arrieta, M., Cunning, J.~C., y Hawley, P.~M. (2025). Update to the Leps strength envelopes for rockfill based on 900 large-scale triaxial tests. \emph{International Journal of Geomechanics}, 25(12), 04025285. \url{https://doi.org/10.1061/IJGNAI.GMENG-12050}
\bibitem[Frossard et al.(2012)]{frossard2012} Frossard, E., Hu, W., Dano, C., y Hicher, P.-Y. (2012). Rockfill shear strength evaluation: A rational method based on size effects. \emph{Géotechnique}, 62(5), 415--427. \url{https://doi.org/10.1680/geot.10.P.079}
\bibitem[Hawley y Cunning(2017)]{hc2017} Hawley, P.~M., y Cunning, J. (Eds.). (2017). \emph{Guidelines for mine waste dump and stockpile design}. CSIRO Publishing.
\bibitem[Indraratna et al.(1993)]{indraratna1993} Indraratna, B., Wijewardena, L.~S.~S., y Balasubramaniam, A.~S. (1993). Large-scale triaxial testing of greywacke rockfill. \emph{Géotechnique}, 43(1), 37--51. \url{https://doi.org/10.1680/geot.1993.43.1.37}
\bibitem[ISRM(1985)]{isrm1985} International Society for Rock Mechanics. (1985). Suggested method for determining point load strength. \emph{International Journal of Rock Mechanics and Mining Sciences \& Geomechanics Abstracts}, 22(2), 51--60.
\bibitem[Leps(1970)]{leps} Leps, T.~M. (1970). Review of shearing strength of rockfill. \emph{Journal of the Soil Mechanics and Foundations Division}, 96(SM4), 1159--1170.
\bibitem[Marsal(1967)]{marsal1967} Marsal, R.~J. (1967). Large scale testing of rockfill materials. \emph{Journal of the Soil Mechanics and Foundations Division}, 93(SM2), 27--43.
\bibitem[Ovalle et al.(2023)]{ovalle2023} Ovalle, C., Girumugisha, G., Cantor, D., y Ouellet, S. (2023). Size effects assessment of mine waste-rock shear strength combining numerical, laboratory and in situ approaches. En P.~M. Dight (Ed.), \emph{SSIM 2023} (pp.~291--300). Australian Centre for Geomechanics. \url{https://doi.org/10.36487/ACG_repo/2335_16}
\bibitem[Stantec(2023)]{stantec2023} Stantec (2023). \emph{Láminas A.5.4 y A.5.5: propiedades del desmonte chancado y ROM} [láminas de interpretación para Compañía Minera Antamina].
\bibitem[Valenzuela et al.(2008)]{valenzuela2008} Valenzuela, L., Bard, E., Campaña, J., y Anabalón, M.~E. (2008). High waste rock dumps: Challenges and developments. En A.~B. Fourie (Ed.), \emph{Rock Dumps 2008: Proceedings of the First International Seminar on the Management of Rock Dumps, Stockpiles and Heap Leach Pads} (pp.~65--78). Australian Centre for Geomechanics. \url{https://doi.org/10.36487/ACG_repo/802_6}
""" + REF_S + r"""
\end{thebibliography}
\end{document}
"""
T = re.sub(r"(?<!\}\n)\\(sub)?section\{", lambda m_: "\\needspace{10\\baselineskip}" + m_.group(0), T)
T = T.replace("Leps 2.0 expresa la resistencia como", "\\needspace{12\\baselineskip}Leps 2.0 expresa la resistencia como")
T = T.replace("\\begin{table}[H]", "\\begin{table}[!htbp]").replace("\\begin{table}[htbp]", "\\begin{table}[!htbp]").replace("\\begin{figure}[htbp]", "\\begin{figure}[!htbp]").replace("\\begin{figure}[H]", "\\begin{figure}[!htbp]")
# referencias en orden alfabético (APA 7)
_i, _j = T.index("\\begin{thebibliography}{20}\\small\n") + len("\\begin{thebibliography}{20}\\small\n"), T.index("\\end{thebibliography}")
# ---- Anexo A: todos los ensayos de resistencia y su uso (a27_tabla_completa.py; comentario WA 2026-10-12)
CITA = {"G2010": r"\citet{g2010}", "G2012": r"\citet{g2012}", "G2021": r"\citet{g2021}", "W2022": r"\citet{w2022}", "W2024": r"\citet{w2024}",
        "I2025": r"\citet{i2025}", "A2024": r"\citet{anddes2024}", "A2024DS": r"\citet{anddes2024}"}
LIT_A = lambda r: LITS(r.fuente_id, r.litologia) if r.litologia in LITN else str(r.litologia).lower()
num = lambda v, d: (lambda x: "--" if pd.isna(x) else f"{x:.{d}f}")(pd.to_numeric(v, errors="coerce"))   # texto («no informado») → --
GRUPOS = [("Ajuste de la curva propuesta", None, "Ajuste de la curva propuesta"),
          ("Contraste", None, "Contraste (sección~\\ref{sec:contraste})"),
          ("No usado", None, "No usado")]
ORDEN_F = ["G2012", "G2021", "W2022", "W2024", "I2025", "A2024DS", "A2024", "G2010"]
filas_anx = []
for uso_, _, tit_ in GRUPOS:
    g_ = A27[A27.uso == uso_]
    if g_.empty:
        continue
    filas_anx.append(r"\midrule\multicolumn{10}{p{14.2cm}}{\textbf{" + tit_ + r"}} \\")
    for (fu_, mot_), h_ in sorted(g_.groupby(["fuente_id", "motivo"], dropna=False), key=lambda kv: ORDEN_F.index(kv[0][0])):
        tipo_ = h_.ensayo.iloc[0]
        tipo_ = "corte directo" if str(tipo_).startswith("Corte") else ("triaxial CU" if "CU" in str(tipo_) else ("triaxial cíclico y monótono" if "cíclico" in str(tipo_) else "triaxial CD"))
        filas_anx.append(r"\multicolumn{10}{p{14.2cm}}{\textit{" + CITA[fu_] + ", " + tipo_ + (f": {mot_}" if isinstance(mot_, str) and mot_ else "") + r"}} \\")
        for _, r_ in h_.iterrows():
            sid_ = str(r_.set_id).replace("Codisposal 1 (100% Intrusivo)", "Intrusivo 100 %").replace("_", r"\_").replace("%", r"~\%")
            filas_anx.append(f"{sid_} & {LIT_A(r_)} & {num(r_.D_m, 2)} & {num(r_.Dmax_mm, 0)} & {num(r_.e0, 3)} & {num(r_.s3, 2)} & {num(r_.s1, 2)} & "
                             f"{num(r_.sn, 2)} & {num(r_.phis, 1)} & {num(r_.eps_a, 1)}" + r" \\")
CNT = A27.groupby("uso").size()
ANX = r"""
\clearpage
\appendix
\renewcommand{\thetable}{A\arabic{table}}\setcounter{table}{0}
\section{Ensayos de resistencia disponibles y su uso}\label{sec:anexo}
La Tabla~\ref{tab:anx_todos} da, ensayo por ensayo, los """ + f"{len(A27)}" + r""" ensayos de resistencia de desmonte de la Tabla~\ref{tab:inventario}, agrupados por su uso en este memorándum: """ + f"{CNT.get('Ajuste de la curva propuesta', 0)}" + r""" en el ajuste de la curva propuesta (incluidas las dos mezclas), """ + f"{CNT.get('Contraste', 0)}" + r""" de contraste y """ + f"{CNT.get('No usado', 0)}" + r""" no usados, con el motivo. Los esfuerzos son efectivos, en la falla: en los triaxiales drenados, en el máximo desviador; en los no drenados, en la máxima oblicuidad o, donde el informe no lo permite \citep{g2010}, en el máximo desviador; en el corte directo, $\tau$ pico y $\sigma'_n$ medidos. En los triaxiales, $\sigma'_n$ y $\phi'_s$ se calcularon con la conversión de Leps 2.0 con $m = """ + f"{MC:.2f}" + r"""$, como en la Tabla~\ref{tab:datos}, y $\phi'_s$ está a la $e_0$ de cada ensayo, sin corregir por densidad. Los edómetros están en la Tabla~\ref{tab:edo}.

\begin{footnotesize}\setlength{\tabcolsep}{2.5pt}
\begin{longtable}{L{3.6cm}L{2.2cm}rrrrrrrr}
\caption{Ensayos de resistencia de desmonte de Antamina y su uso. $D$: diámetro de la probeta o lado de la caja; $D_{max}$: tamaño máximo de partícula (--: no informado); $\varepsilon_a$: deformación axial en la falla.}\label{tab:anx_todos}\\
\toprule Set & Litología & $D$ & $D_{max}$ & $e_0$ & $\sigma'_3$ & $\sigma'_1$ & $\sigma'_n$ & $\phi'_s$ & $\varepsilon_a$\\
 & & (m) & (mm) & & (MPa) & (MPa) & (MPa) & (°) & (\%)\\\endfirsthead
\toprule Set & Litología & $D$ & $D_{max}$ & $e_0$ & $\sigma'_3$ & $\sigma'_1$ & $\sigma'_n$ & $\phi'_s$ & $\varepsilon_a$\\\midrule\endhead
""" + "\n".join(filas_anx) + r"""
\bottomrule
\end{longtable}\end{footnotesize}
"""
_bib = [b.strip() for b in T[_i:_j].split("\\bibitem") if b.strip()]
_bib.sort(key=lambda b: b.split("]", 1)[1].split("}", 1)[1].strip().lower().replace("á", "a").replace("é", "e"))
T = T[:_i] + "\n".join("\\bibitem" + b for b in _bib) + "\n" + T[_j:]
T = T.replace("\\end{document}", ANX + "\\end{document}")
_grado = lambda m: m.group(0).replace("°", "^{" + chr(92) + "circ}")
T = re.sub(r"\$[^$]*\$", _grado, T)
T = re.sub(r"begin\{equation\}.*?end\{equation\}", _grado, T, flags=re.S)
(AQ / "curva_leps2_antamina.tex").write_text(T, encoding="utf-8")
print(f"escrito | curva propuesta φ′e0 {OP2['pe0']:.2f}° m {MC:.3f} φ′1 {p2:.2f}° (control DDE {OP2['pe0_dde']:.2f}°) | ciclos {n_ciclo} | "
      f"contractivos {n_contr}/{n_eps} | anexo {len(A27)} ensayos | sobre Indraratna hasta 15 MPa: {LB_SOBRE}")
