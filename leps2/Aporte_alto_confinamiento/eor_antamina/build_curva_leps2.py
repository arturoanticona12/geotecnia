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
for f in ("Fig1_phi_sigma.pdf", "Fig2_tau_sigma.pdf", "Fig3_perfil_e.pdf", "Fig4_contraste.pdf", "Fig5_bg.pdf", "Fig_phi1_e.pdf"):
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
# revisión 11 (revisión independiente, 2026-10-13): sensibilidad del nivel a la composición del desmonte de LE2 (modelo de bloques
# MR2024, períodos 2035 en adelante, fracción en masa: mármol 37.8 %, hornfels 15.5 %, intrusivo 17.0 %, caliza y margas 29.6 %, sin
# ensayos y asimiladas al mármol) y al mármol solo. La curva propuesta sigue siendo la media de los sets (decisión del usuario).
W_LE2 = {"Mármol": 37.8, "Hornfels": 15.5, "Intrusivo": 17.0, "Caliza y margas": 29.6}
OP2["pe0_le2"] = float(((W_LE2["Mármol"] + W_LE2["Caliza y margas"]) * _ml["Mármol"] + W_LE2["Hornfels"] * _ml["Hornfels"]
                        + W_LE2["Intrusivo"] * _ml["Intrusivo"]) / sum(W_LE2.values()))   # fracciones de MR2024 normalizadas (suman 99.9 %)
OP2["pe0_mar"] = float(_ml["Mármol"]); OP2["pe0_hor"] = float(_ml["Hornfels"]); OP2["pe0_int"] = float(_ml["Intrusivo"])
from tope import TOPE                              # tope del ángulo secante a bajo confinamiento (decisión del usuario, revisión 12: 42°)
EV = 0.55                                         # e de verificación del diseño (decisión del usuario, revisión 11)
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
s_tope = lambda pe0, e=EC:  S0 * (math.tan(math.radians(pe0 - OM * e)) / math.tan(math.radians(TOPE))) ** (1 / (1 - MC))
tauT = lambda sn, pe0, m, e=EC: min(tau_l(sn, pe0, m, e), sn * math.tan(math.radians(TOPE)))   # curva con tope
phisT = lambda sn, pe0, m, e=EC: min(phis(sn, pe0, m, e), TOPE)
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
A25 = J("a25_alta_tension.json"); A27 = pd.read_csv(AA / "a27_ensayos_todos.csv")
A30 = J("a30_dos_pasos.json")                                    # ajuste en dos pasos pedido por WA (revisión 11: e0 adoptadas)          # esfuerzos altos y tabla completa
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
SESGO = [(a_, b_, float(_res[(P.sn > a_) & (P.sn <= b_)].median()), int(((P.sn > a_) & (P.sn <= b_)).sum())) for a_, b_ in ((0, 0.5), (0.5, 2), (2, SNX + 0.01))]
# posición frente a Leps (1970) a e = 0.45 y con el perfil A (0 = inferior, 1 = media)
_pos = lambda s_, f_: (f_ - L70(s_, 36)) / (L70(s_, 41) - L70(s_, 36))
def _cruce(p1, e_=EC):
    a_, b_ = 0.01, 200.0
    for _ in range(80):
        c_ = math.sqrt(a_ * b_); a_, b_ = (c_, b_) if phis(c_, OP2["pe0"], MC, e_) - L70(c_, p1) > 0 else (a_, c_)
    return math.sqrt(a_ * b_)
X_MED, X_INF = _cruce(41), _cruce(36)
def _cruce_lb(e_):
    a_, b_ = 0.3, 300.0
    if phis(b_, OP2["pe0"], MC, e_) - LB(b_) > 0:
        return float("inf")
    for _ in range(80):
        c_ = math.sqrt(a_ * b_); a_, b_ = (c_, b_) if phis(c_, OP2["pe0"], MC, e_) - LB(c_) > 0 else (a_, c_)
    return math.sqrt(a_ * b_)
S_LB06 = _cruce_lb(0.6)                           # la curva evaluada a e = 0.6 frente a la cota (normalizada a e = 0.6 por Cylwik)
POS_A = [_pos(s_, phis(s_, OP2["pe0"], MC, float(PEM.e_A(s_)))) for s_ in (1, 4, 10, 15)]
# revisión 10b: comprobaciones (cada ensayo frente a la curva evaluada a su propia e)
_dA = np.asarray(P.phis) - np.array([phis(s_, OP2["pe0"], MC, e_) for s_, e_ in zip(P.sn, P.e)]); _dW = np.asarray(_dw)
CMP = []; _fmt = lambda v: f"{v:.2f}".rstrip("0").rstrip(".")
for a_, b_ in ((0, 0.5), (0.5, 2), (2, SNX + 0.01)):
    k_ = ((P.sn > a_) & (P.sn <= b_)).values
    CMP.append((f"Antamina, {_fmt(a_)} a {_fmt(min(b_, SNX))}~MPa", int(k_.sum()), float(np.median(_dA[k_])), int((_dA[k_] < 0).sum())))
_cl = _WD.clase[_kw].values; CLW = {}
for c_, nm_ in (("good", "buena"), ("moderate", "moderada"), ("low", "baja")):
    k_ = _cl == c_
    if k_.sum():
        CLW[c_] = (int(k_.sum()), float(np.median(_dW[k_])), int((_dW[k_] < 0).sum()))
        CMP.append((f"Base mundial, roca de calidad {nm_}, {f2(SNX)} a {f2(SNW)}~MPa", *CLW[c_]))
filas_cmp = [f"{a} & {n} & {sg(m_)} & {b}" + r" \\" for a, n, m_, b in CMP]
N_SUBE = N_BAJA = N_TEND = 0                                                   # sets cuyo φ′s sube o baja con σ′n (más de 0.5° por unidad de ln σ′n)
for _, g_ in P.groupby("set"):
    if g_.sn.nunique() < 2:
        continue
    N_TEND += 1; sl_ = np.polyfit(np.log(g_.sn), g_.phis, 1)[0]; N_SUBE += int(sl_ > 0.5); N_BAJA += int(sl_ < -0.5)
PH1_10 = phis(10, A33["hipotesis"]["lineal"]["pe0"], 1.0)
# procedencia de las e0 por set (verificada contra las hojas de laboratorio, 2026-10-12)
GSINF = {"G2012-MN-C": "2.70 (supuesto)", "G21-DESM-COMP": "2.77 (D854)", "HF-1.0m-IDIEM-mono": "2.75$^{h}$", "HF-1.0m-IDIEM-cd": "2.75$^{h}$",
         "HF-0.15m-Golder": "2.75 (calculado)", "MN-0.15m-Golder": "2.70 (calculado)", "WSP24_C4_MON": "2.85", "Codisposal 1 (100% Intrusivo)": "2.85$^{i}$"}
CITP = {"G2012": r"Golder (2012)", "G2021": r"Golder (2021)", "W2022": r"Golder (2022)", "W2024": r"WSP (2024)", "I2025": r"IDIEM (2025)", "A2024DS": r"Anddes (2024)"}
filas_e0 = []
for (fu_, si_), g_ in d0.groupby(["fuente_id", "set_id"], sort=False):
    r_ = g_.iloc[0]; ead_ = float(g_.e0_adoptado.mean())
    rho_ = float(r_.gamma_d_kNm3) / 9.81 if pd.notna(r_.gamma_d_kNm3) else float(r_.Gs_adoptado) / (1 + ead_)
    nm_ = str(si_).replace("Codisposal 1 (100% Intrusivo)", "Intrusivo 100~\\%").replace("WSP24_C4_MON", "C4, monótono").replace("_", r"\_")
    einf_ = f"{float(r_.e0):.3f}" if pd.notna(r_.e0) else "--"
    filas_e0.append(f"{CITP[fu_]} & {nm_} & {LITS(fu_, r_.litologia)} & {rho_:.2f}" + (r"$^{d}$" if fu_ == "A2024DS" else "")
                    + f" & {GSINF.get(si_, 'no informa')} & {einf_} & {float(r_.Gs_adoptado):.3f} & {ead_:.3f}" + r" \\")
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
    (r"\citet{g2010}", "Granulometría, índices de roca, densidad in situ, permeabilidad y carga directa en plataforma", "--", "Mármol, hornfels, intrusivo, skarn (fases A y B)", "125", r"$G_s$; la $e$ in situ no se usa; resto, caracterización (Tablas~\ref{tab:b_g10gran} y~\ref{tab:b_g10ind})"),
    (r"\citet{g2012}", "Triaxial CD (3 con carga y descarga)", "1~m (178~mm)", "Mármol", "5", "Ajuste"),
    (r"\citet{g2012}", "Edómetro", "0.95~m", "Mármol", "1", r"Rango de compresibilidad (Tabla~\ref{tab:edo})"),
    (r"\citet{g2012}", "Permeabilidad en el edómetro", "0.95~m", "Mármol", "6", r"Caracterización (Tabla~\ref{tab:caract})"),
    (r"\citet{g2021}", "Triaxial CD, desmonte compuesto", "6~in (25~mm)", r"Intrusivo, hornfels, mármol (35/50/15~\%)", "3", "Ajuste"),
    (r"\citet{g2021}", r"Granulometría, $G_s$, absorción, límites y Proctor", "--", "Intrusivo, mármol--hornfels, hornfels, compuesto y mezclas con relave", "13", r"Caracterización (Tabla~\ref{tab:caract})"),
    (r"\citet{g2021}", "Permeabilidad, pared flexible", "--", "Mezclas de desmonte y relave", "6", "No usado: mezcla con relave"),
    (r"\citet{w2022}", "Triaxial CD (3 con carga y descarga)", "1~m (178~mm)", "Hornfels", "6", "Ajuste"),
    (r"\citet{w2022}", "Triaxial CD con carga y descarga", "6~in (25~mm)", "Hornfels, mármol", "2", "Ajuste (pares de escala)"),
    (r"\citet{w2022}", r"Triaxial CD y edómetro (copias de \citealp{g2012})", "1~m", "Mármol", "5 y 1", "Duplicados; se usa el original"),
    (r"\citet{w2022}", "Triaxial cíclico (15 ciclos) y luego monótono", "0.10--0.15~m", "Hornfels, mármol", "6", "No usado: carga cíclica previa; 3 detenidos por la capacidad del equipo"),
    (r"\citet{w2022}", "Edómetro", "1~m (2) y 0.24~m (4)", "Hornfels, mármol", "6", r"Perfil A (mármol suelto, 0.24~m) y rango de compresibilidad (Tabla~\ref{tab:edo})"),
    (r"\citet{w2022}", "Permeabilidad, UCS, Los Ángeles, densidad máxima y mínima, granulometría de terreno", "--", "Hornfels, mármol", "28", r"Caracterización (Tabla~\ref{tab:caract})"),
    (r"\citet{w2024}, set C4", "Triaxial CD", "0.6~m (102~mm)", "Intrusivo", "3", "Ajuste"),
    (r"\citet{w2024}, set C4", "Edómetro", "0.6~m (102~mm)", "Intrusivo", "1", r"Rango de compresibilidad (Tabla~\ref{tab:edo})"),
    (r"\citet{w2024}", r"$G_s$, absorción, UCS, Los Ángeles, carga puntual, densidad máxima y mínima, granulometría de terreno, permeabilidad", "--", "Intrusivo y mezclas con relave", "36", r"Caracterización (Tabla~\ref{tab:caract})"),
    (r"\citet{w2024}, sets C1--C3", "Edómetro", "0.6~m", "Mezclas de intrusivo y relave", "3", "No usado: mezcla con relave"),
    (r"\citet{i2025}", "Triaxial CD", "1~m (178~mm)", "Intrusivo", "3", "Ajuste"),
    (r"\citet{anddes2024}", "Triaxial CU", "6~in ($D_{max}$ no informado)", "Mármol, hornfels, intrusivo, mármol--hornfels", "15", "Contraste"),
    (r"\citet{anddes2024}", "Corte directo de gran escala", "30.5~cm (1~in)", "Mármol, hornfels, intrusivo, mármol--hornfels", "15", "Ajuste"),
    (r"\citet{anddes2024}", "Granulometría, límites, Proctor, humedad", "--", "Mármol, hornfels, intrusivo, mármol--hornfels", "5", r"Caracterización (Tabla~\ref{tab:caract})"),
    (r"\citet{stantec2023}", r"Puntos $\tau$--$\sigma'_n$ de terceros", "--", "--", "--", "No usado"),
    (r"\citet{antamina2025frag}", "Fragmentación por análisis de fotos", "Campo", "Desmonte ROM", f"{FR['n']}", "$D_{max}$ de campo"),
    (r"\citet{antamina2025le2}", "UCS, carga puntual, tracción, corte directo, RMR, RQD y FF en roca", "--", "Seis unidades geotécnicas de roca", r"23\,860", r"Caracterización (Tabla~\ref{tab:b_rmu})"),
    (r"\citet{antamina2025wsc}", "UCS, índices de chancado y abrasión", "--", "Desmonte Waste-C/Std, Waste-Fine y Waste-Hard", "3", r"Caracterización (Tabla~\ref{tab:b_wsc})"),
    (r"\citet{antamina2024mr}", "Modelo de bloques: UCS y densidad", "--", "Nueve litologías del desmonte del LOM25 (LE1 y LE2)", r"310\,102", r"Caracterización (Tabla~\ref{tab:b_mr})"),
]
filas_inv = [" & ".join(r) + r" \\" for r in INV]

# ---- ensayos de caracterización (no de resistencia del desmonte); valores tal como los informan los reportes,
#      verificados en la imagen o la capa de texto de la página citada de cada informe (2026-10-13)
E = lambda m, x: f"${m}\\times10^{{{x}}}$"
CAR = [
    ("Granulometría y clasificación", [
        ("Granulometría de terreno", r"\citet[Tablas~1 y~2]{g2010}", "Mármol, hornfels, intrusivo y skarn; fases A y B", "8", r"A: TM 19--35~in, finos 0.88--2.8~\%; B: finos 2.7--7.2~\%$^{k}$", r"Caracterización (Tabla~\ref{tab:b_g10gran})"),
        ("Granulometría de terreno", r"\citet[pp.~47 y~52]{w2022}", "Hornfels y mármol (muestras M-001)", "2", r"TM 36~in; finos: hornfels 2.49~\% (GW-GM$^{a}$), mármol 4.07~\% (GP-GM$^{a}$)", r"Caracterización (Tabla~\ref{tab:b_gran})"),
        ("Granulometría de terreno", r"\citet[p.~93]{w2024}", "Intrusivo", "1", r"TM 10~in; finos 6.6~\%", r"Caracterización (Tabla~\ref{tab:b_gran})"),
        ("Granulometría y SUCS (ASTM D6913 y D2487)", r"\citet{anddes2024}", r"Mármol, hornfels, intrusivo y mármol--hornfels; $D_{max}$ 75~mm", "5", r"Grava 57--68~\%, arena 21--34~\%, finos 8--11~\%; GP-GM (4) y GW-GM (1)", r"Caracterización (Tabla~\ref{tab:b_gran})"),
        ("Granulometría y SUCS (ASTM D422 y D7928)", r"\citet[Tabla~4]{g2021}", "Tipos A, B y C y desmonte compuesto", "4", r"$D_{50}$ 3.6--9.5~mm; finos 7.2--13.5~\%; GM (3) y GP-GM (1)", r"Caracterización (Tabla~\ref{tab:b_gran})"),
        ("Límites de Atterberg", r"\citet{anddes2024}", "Mismas muestras", "5", "LL: NP (3), 16 y 17; IP: NP", r"Caracterización (Tabla~\ref{tab:b_gran})"),
        ("Límites de Atterberg", r"\citet[p.~14 y pp.~58--60]{g2021}", "Tipos A, B y C, compuesto y mezclas", "--", "NP", r"Caracterización (Tabla~\ref{tab:b_gran})"),
    ]),
    ("Peso específico y absorción", [
        (r"$G_s$ de sólidos (ASTM D854)", r"\citet[Tabla~2]{g2010}", "Mármol, hornfels, intrusivo y skarn; fases A y B", "8", "A: 2.674--3.484; B: 2.742--3.338", r"$e_0$ (Tabla~\ref{tab:e0})"),
        (r"$G_s$ y absorción del grueso (ASTM C127)", r"\citet[p.~48]{g2010}", "Mismas muestras", "8", r"A: $G_s$ bulk 2.461--3.212$^{b}$, absorción 0.24--1.66~\%; B: 2.647--3.102 y 0.12--2.17~\%", r"Caracterización (Tabla~\ref{tab:b_g10ind})"),
        (r"$G_s$ y absorción del grueso (ASTM C127)", r"\citet[Tabla~5 y pp.~83--86]{g2021}", "Tipos A, B y C y desmonte compuesto", "4", r"$G_s$ bulk 2.44--2.87; absorción 0.54--3.39~\%; $G_s$ de finos del compuesto 2.77", r"Caracterización (Tabla~\ref{tab:b_gs})"),
        (r"$G_s$ y absorción del grueso (ASTM C127)", r"\citet[Tabla~3]{w2024}", "Intrusivo", "8", r"$G_s$ aparente 2.83--2.93; base seca 2.71--2.86; absorción 0.8--1.6~\%", r"Caracterización (Tabla~\ref{tab:b_gs})"),
    ]),
    ("Densidad y humedad", [
        ("Densidad in situ (reemplazo de agua) y humedad natural", r"\citet[Tabla~2]{g2010}", "Desmonte en el tajo (A) y chancado (B)", "8", r"A: $\gamma_d$ 1.865--2.273~g/cm³, $w$ 2.2--3.8~\%; B: 2.019--2.357~g/cm³, 2.3--3~\%", r"No usado (sección~\ref{sec:datos})"),
        ("Densidad mínima y máxima (ASTM D4254 y D4253)", r"\citet[pp.~43--47]{g2010}", "Skarn (A); mármol, hornfels, intrusivo y skarn (B); fracción menor que 5/8~in", "5", r"Mínima 1.821--2.175; máxima 2.236--2.647~g/cm³", r"Caracterización (Tabla~\ref{tab:b_dens})"),
        ("Densidad mínima y máxima (ASTM D4254 y D4253)", r"\citet[pp.~85--86]{w2022}", "Hornfels y mármol", "2", r"Mínima 1.852 y 1.905; máxima seca 2.232 y 2.297~g/cm³", r"Caracterización (Tabla~\ref{tab:b_dens})"),
        ("Densidad mínima y máxima (ASTM D4254 y D4253)", r"\citet[Tabla~8]{w2024}", r"Intrusivo (C4) y mezclas con relave (C1--C3); fracción menor que 3~in", "4", r"Mínima 1.825--1.945; máxima 2.158--2.212~g/cm³", r"Caracterización (Tabla~\ref{tab:b_dens})"),
        ("Proctor estándar (ASTM D698)", r"\citet{anddes2024}", "Mismas muestras", "5", r"$\gamma_{d,max}$ 19.95--23.78~kN/m³; $w_{opt}$ 6.8--11.1~\%$^{c}$", r"Caracterización (Tabla~\ref{tab:b_gran})"),
        ("Proctor estándar (ASTM D698)", r"\citet[Tabla~6]{g2021}", "Desmonte compuesto y 9 mezclas con relave", "10", r"Compuesto: 22.7~kN/m³ y 6.5~\%; mezclas: 22.0--23.0~kN/m³ y 5.6--7.5~\%", r"Caracterización (Tabla~\ref{tab:b_gran})"),
        ("Contenido de agua", r"\citet{anddes2024}", "Mismas muestras", "5", r"3--6~\%", r"Caracterización (Tabla~\ref{tab:b_gran})"),
    ]),
    ("Compresibilidad, carga en plataforma y permeabilidad", [
        ("Edómetro de gran escala", r"\citet{g2012,w2022,w2024}", "Mármol, hornfels e intrusivo; 0.24--1.0~m", "8", r"$C_c$ y $e$ con la profundidad en la Tabla~\ref{tab:edo}", "Perfil A y rango de compresibilidad"),
        ("Edómetro de gran escala", r"\citet[Tabla~12]{w2024}", "Mezclas de intrusivo y relave (C1--C3); 0.6~m", "3", r"$\varepsilon_v$ final 8.2--11.1~\% a 5880~kPa", r"Caracterización (Tabla~\ref{tab:b_perm})"),
        ("Carga directa en plataforma", r"\citet[Tabla~2 y pp.~185--226]{g2010}", "Material chancado (fase B); placas de 0.30 a 0.60~m", "4", r"Asentamiento máximo 3.6--5.6~cm, con carga de hasta 6.0~kg/cm²", r"Caracterización (Tabla~\ref{tab:b_perm})"),
        ("Permeabilidad, pared flexible (ASTM D5084)", r"\citet[Tabla~2 y pp.~157--160]{g2010}", r"Hornfels e intrusivo (A y B); fracción menor que 5/8~in, $\sigma'$ de 20~kPa", "4", r"$k_{20}$ " + E("2.2", "-6") + "--" + E("3.2", "-6") + r"~m/s", r"Caracterización (Tabla~\ref{tab:b_perm})"),
        ("Permeabilidad, carga constante en el edómetro", r"\citet[Tabla~4]{g2012}", "Mármol; 0.95~m", "1 (6 escalones)", E("8.2", "-4") + "--" + E("1.4", "-3") + r"~m/s$^{d}$, con $\sigma'_v$ de 6 a 60~kg/cm²", r"Caracterización (Tabla~\ref{tab:b_perm})"),
        ("Permeabilidad, carga constante en el edómetro", r"\citet[Tablas~5 y~6]{w2022}", "Hornfels y mármol (2021); 1.0~m", "2 (14 escalones)", "Hornfels, de " + E("3.5", "-4") + " a " + E("3.5", "-5") + "; mármol, de " + E("1.2", "-4") + " a " + E("2.7", "-5") + r"~m/s$^{d}$, de 588 a 6865~kPa", r"Caracterización (Tabla~\ref{tab:b_perm})"),
        ("Permeabilidad, carga constante en el edómetro", r"\citet[Tabla~14]{w2024}", "Intrusivo (C4) y mezclas con relave (C1--C3); 0.6~m", "4 (20 escalones)", E("2.0", "-4") + "--" + E("1.3", "-3") + r"~m/s, de 392 a 5880~kPa$^{e}$", r"Caracterización (Tabla~\ref{tab:b_perm})"),
        ("Permeabilidad, pared flexible (ASTM D5084)", r"\citet[Tabla~9]{g2021}", "Mezclas de desmonte y relave 9:1 y 1:1", "6", E("1.4", "-6") + "--" + E("8.9", "-6") + r"~m/s$^{f}$", "No usado: mezcla con relave"),
    ]),
    ("Degradabilidad", [
        ("Abrasión Los Ángeles (ASTM C535)", r"\citet[Tabla~2]{g2010}", "Mármol, hornfels, intrusivo y skarn; fases A y B", "8", r"A: pérdida 23.7--62.1~\%; B: 20.3--62.4~\%", r"Caracterización (Tabla~\ref{tab:b_g10ind})"),
        ("Abrasión Los Ángeles (ASTM C535)", r"\citet[pp.~48--55]{w2022}", "Hornfels y mármol (muestras M-001 y M-002)", "4", r"Hornfels 15.5 y 17.3~\%; mármol 55.8 y 45.2~\%$^{g}$", r"Caracterización (Tabla~\ref{tab:b_part})"),
        ("Abrasión Los Ángeles", r"\citet[p.~17]{g2012}", "Mármol", "2", r"44 y 41~\%", r"Caracterización (Tabla~\ref{tab:b_part})"),
        ("Abrasión Los Ángeles (ASTM C535$^{n}$)", r"\citet[Tabla~7]{w2024}", "Intrusivo", "8", r"Pérdida 21.2--39.9~\% (promedio 30.4~\%)", r"Caracterización (Tabla~\ref{tab:b_part})"),
        ("Durabilidad en sulfato", r"\citet[Tabla~2]{g2010}", "Mármol, hornfels, intrusivo y skarn; fases A y B", "8", r"Pérdida corregida A: 0.7--43.4~\%; B: 0.6--49.8~\%$^{h}$", r"Caracterización (Tabla~\ref{tab:b_g10ind})"),
        ("Índice de abrasión de Bond, abrasividad Macon, CWI, crushability y DWT", r"\citet[lámina~2]{antamina2025wsc}", r"Desmonte Waste-C/Std, Waste-Fine y Waste-Hard$^{o}$", "3 materiales", r"Bond Ai 0.0202--0.4810; abrasividad Macon 39.4--778.0~g/t; CWI 12.6--17.1~kWh/t; crushability 25.02--36.50~\%; A$\times$b 35.6--43.9", r"Caracterización (Tabla~\ref{tab:b_wsc})"),
    ]),
    ("Resistencia de la roca", [
        ("Compresión uniaxial (ASTM D2938)", r"\citet[Tabla~2 y pp.~66--73]{g2010}", "Mármol, hornfels, intrusivo y skarn; fases A y B", "16 probetas", r"Promedio por litología A: 44.7--73.3~MPa; B: 49.6--97.4~MPa", r"Caracterización (Tabla~\ref{tab:b_g10ind})"),
        ("Carga puntual (ASTM D5731)", r"\citet[Tabla~2 y pp.~74--81]{g2010}", "Mismas litologías", "48 probetas", r"$\sigma_c$ estimada por el laboratorio a partir de $I_{s(50)}$, promedio por litología A: 32.24--80.56~MPa; B: 24.56--124.78~MPa", r"Caracterización (Tabla~\ref{tab:b_g10ind})"),
        ("Compresión uniaxial", r"\citet[Tablas~1 y~2 y pp.~72--83]{w2022}", "Hornfels y mármol", "18 probetas", r"Hornfels, 64 y 65~MPa (Tabla~1) y 24.5--40.8~MPa (IDIEM, 3); mármol, 42--136~MPa (2 de 2020, 8 de 2011 y 3 de IDIEM)$^{i}$", r"Caracterización (Tabla~\ref{tab:b_part})"),
        ("Compresión uniaxial (ASTM D7012)", r"\citet[Tabla~6]{w2024}", "Intrusivo", "7 probetas", r"61.1--143.1~MPa$^{j}$", r"Caracterización (Tabla~\ref{tab:b_part})"),
        ("Carga puntual", r"\citet[pp.~356--364]{w2024}", "Desmonte intrusivo: 31 colpas de tonalita y 7 de caliza", "4 sets", r"$I_{s(50)}$ por set 4.11--6.16~MPa", r"Caracterización (Tabla~\ref{tab:b_part})"),
        ("UCS de desmonte", r"\citet[lámina~2]{antamina2025wsc}", r"Desmonte Waste-C/Std, Waste-Fine y Waste-Hard$^{o}$", "3 materiales", r"54, 83 y 155~MPa", r"Caracterización (Tabla~\ref{tab:b_wsc})"),
        ("UCS, carga puntual, tracción brasileña, corte directo, RMR, RQD y FF", r"\citet{antamina2025le2}", "Roca de seis unidades geotécnicas (END, EXO, HRN, INT, LMH y XDP) del tajo LE2", r"23\,860$^{l}$", r"Medianas por unidad: UCS 28.1--98.0~MPa; $I_{s(50)}$ axial 2.0--6.8 y diametral 2.6--7.2~MPa; tracción 3.4--9.7~MPa; $\phi$ 28.2--33.4°", r"Caracterización (Tabla~\ref{tab:b_rmu})"),
        ("UCS del modelo de bloques", r"\citet[lámina~12]{antamina2025wsc}; \citet{antamina2024mr}", "Desmonte del LOM25, 2025--2049 (LE1 y LE2), nueve litologías", r"310\,102 bloques$^{m}$", r"Media por litología 57.37--116.96~MPa", r"Caracterización (Tabla~\ref{tab:b_mr})"),
    ]),
    ("Fragmentación de campo", [
        ("Fragmentación por análisis de fotos", r"\citet{antamina2025frag}", "Desmonte de voladura, clases A, B, C y C1; fases 8 a 10", "319 análisis", r"Mediana de $X_{max}$ 66.7--91.9~cm según la clase; máximo 270.9~cm$^{p}$", r"$D_{max}$ de campo (Tabla~\ref{tab:b_frag})"),
    ]),
]
filas_car = []
for gr_, fs_ in CAR:
    filas_car.append((r"\midrule " if filas_car else "") + r"\multicolumn{6}{l}{\textit{" + gr_ + r"}} \\")
    filas_car += [" & ".join(f) + r" \\" for f in fs_]
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
HIPT = [("$m$ P90 entre materiales", "m_p90"), ("$m$ alto (IC 90~\\%)", "m0862"), ("Curva propuesta", "m085"), ("$m$ bajo (IC 90~\\%)", "m0834"),
        ("$m$ P10 entre materiales", "m_p10"), ("Antamina sola$^{s}$", "lineal")]
filas_t3 = [f"{nm_} & {A33['hipotesis'][k_]['m_a']:.3f} & {A33['hipotesis'][k_]['pe0']:.2f} & " + " & ".join(f1(phis(s, A33['hipotesis'][k_]['pe0'], A33['hipotesis'][k_]['m_a'])) for s in SNT) + r" \\" for nm_, k_ in HIPT]
filas_t3 += [r"\midrule Banda, límite inferior & & & " + " & ".join(f1(lo(s)) for s in SNT) + r" \\",
             "Banda, límite superior & & & " + " & ".join(f1(hi(s)) for s in SNT) + r" \\"
             ]
filas_t3 += [r"\midrule Composición de LE2$^{l}$ & " + f"{MC:.3f} & {OP2['pe0_le2']:.2f} & " + " & ".join(f1(phis(s, OP2['pe0_le2'], MC)) for s in SNT) + r" \\",
             r"Mármol solo & " + f"{MC:.3f} & {OP2['pe0_mar']:.2f} & " + " & ".join(f1(phis(s, OP2['pe0_mar'], MC)) for s in SNT) + r" \\",
             r"Propuesta, $e = 0.55$ & " + f"{MC:.3f} & {OP2['pe0']:.2f} & " + " & ".join(f1(phis(s, OP2['pe0'], MC, EV)) for s in SNT) + r" \\"]
SN4 = [0.01, 0.02, 0.03, 0.05, 0.1, 0.2, 0.5, 1, 1.5, 2, 3, 4, 5, 6, 8, 10, 12, 15]
ext = lambda s: r"$^{a,w}$" if s > SNW else (r"$^{a}$" if s > SNX else "")
filas_t4 = [r"0 & 0.0 & 0.0 & 0.0 & -- \\"]
_tp = lambda s: r"$^{t}$" if phis(s, OP2['pe0'], MC) > TOPE else ""
filas_t4 += [f"{s*1000:.0f}{ext(s)}{_tp(s)} & {tauT(s, OP2['pe0'], MC)*1000:.1f} & "
             f"{s*1000*math.tan(math.radians(min(lo(s), TOPE))):.1f} & {s*1000*math.tan(math.radians(min(hi(s), TOPE))):.1f} & {phisT(s, OP2['pe0'], MC):.1f}" + r" \\" for s in SN4]
EPAR = [("0.45", lambda s: 0.45), ("0.55", lambda s: 0.55), ("0.65", lambda s: 0.65), ("A", lambda s: float(PEM.e_A(s))), ("V", lambda s: float(PEM.eV_of_sv(s)))]
filas_t5 = [r"0 & " + " & ".join("0.0" for _ in EPAR) + r" & 0.0 \\"]
filas_t5 += [f"{s*1000:.0f}{ext(s)} & " + " & ".join(f"{tauT(s, OP2['pe0'], MC, fe(s))*1000:.1f}" if math.isfinite(fe(s)) else "--" for _, fe in EPAR)
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
\bibitem[Compañía Minera Antamina(2025a)]{antamina2025frag} Compañía Minera Antamina (2025a). \emph{Fragmentación del desmonte 2025} [planilla de análisis de fragmentación por fotos post-voladura, enero a agosto de 2025, archivo «Fragmentación Desmonte 2025»].
\bibitem[Compañía Minera Antamina(2025b)]{antamina2025le2} Compañía Minera Antamina (2025b). \emph{Ensayos geotécnicos LE2} [presentación de Geotecnia e Hidrogeología PDN «Parametros Geotecnicos Vs RMU LE2 03092025» y planilla «Resultados Parametros Geotecnicos LE2 (03092025)», 3 de septiembre de 2025; confidencial].
\bibitem[Compañía Minera Antamina(2025c)]{antamina2025wsc} Compañía Minera Antamina (2025c). \emph{LE2 waste characterization: LE2 Program estudios} [presentación, archivo «Waste Sample Characterization Rev C», 29 de agosto de 2025].
\bibitem[Compañía Minera Antamina(2024)]{antamina2024mr} Compañía Minera Antamina (2024). \emph{Modelo de bloques MR2024 del desmonte del plan LOM25} [exportación de Leapfrog Geo, archivo SIMULACIONES\_MR2024\_V3].
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

\section*{Resumen}
Stantec propone para el desmonte ROM de Antamina la curva de Leps 2.0
\begin{equation*}
\tau = \tan\!\left(""" + f"{OP2['pe0']:.2f}" + r"""^{\circ} - 20^{\circ}\,e\right)\,(10p_a)^{""" + f"{1 - MC:.2f}" + r"""}\,\sigma_n'^{\,""" + f"{MC:.2f}" + r"""},
\end{equation*}
donde $e$ es la relación de vacíos del desmonte colocado, con valor base 0.45. Es la curva media de los ensayos de Antamina, no una curva característica: el Ingeniero de Registro elige el percentil o la reducción que corresponda al diseño. Se aplica con un tope de """ + f"{TOPE:.0f}" + r"""° en el ángulo secante, que gobierna bajo $\sigma'_n$ = """ + f"{s_tope(OP2['pe0']):.2f}" + r"""~MPa, y el diseño se verifica también con $e = """ + f"{EV:.2f}" + r"""$. Con $e = 0.45$, el ángulo de fricción secante es """ + f"{f1(phis(1, OP2['pe0'], MC))}° a 1~MPa, {f1(phis(SNX, OP2['pe0'], MC))}° a {f2(SNX)}~MPa (el máximo ensayado en Antamina), {f1(phis(10, OP2['pe0'], MC))}° a 10~MPa y {f1(phis(15, OP2['pe0'], MC))}° a 15~MPa" + r""". La banda de incertidumbre de la curva va de """ + f"{f1(lo(1))}° a {f1(hi(1))}° a 1~MPa y de {f1(lo(10))}° a {f1(hi(10))}° a 10~MPa" + r""".

La curva resulta de tres decisiones, cada una con su evidencia (sección~\ref{sec:decisiones}):
\begin{enumerate}
\item \textbf{El nivel sale de los ensayos de Antamina.} Los """ + f"{len(P)} ensayos ({P.set.nunique()} sets)" + r""" de mármol, hornfels, intrusivo y mezclas dan $\phi'_{e=0} = """ + f"{OP2['pe0']:.2f}" + r"""°$ (P5--P95 de """ + f"{NIV['m085']['p5']:.1f} a {NIV['m085']['p95']:.1f}" + r"""°), entre las clases de calidad baja (47°) y moderada (50°) de Leps 2.0. Por litología, el nivel es """ + f"{OP2['pe0_mar']:.1f}° en el mármol, {OP2['pe0_int']:.1f}° en el intrusivo y {OP2['pe0_hor']:.1f}° en el hornfels" + r""". Ponderar con la producción de desmonte del DDE da """ + f2(OP2['pe0_dde']) + r"""°; con la composición del desmonte de LE2 del modelo de bloques, que tiene 30~\% de caliza y margas sin ensayos (asimiladas aquí al mármol), da """ + f2(OP2['pe0_le2']) + r"""°, unos """ + f"{OP2['pe0'] - OP2['pe0_le2']:.1f}" + r"""° menos.
\item \textbf{La forma sale de la base mundial.} $m = """ + f"{MC:.2f}" + r"""$ es el exponente con residuo mediano nulo en los ensayos mundiales de mayor esfuerzo (intervalo al 90~\% de """ + f"{M_IC[0]:.3f} a {M_IC[1]:.3f}" + r"""); entre materiales, $m$ varía entre """ + f"{A31['estimadores']['Mundo, todos los sets (mediana; P10–P90)']['p10']:.2f} y {A31['estimadores']['Mundo, todos los sets (mediana; P10–P90)']['p90']:.2f}" + r""" (P10--P90), y la banda de la curva incluye ese rango. Los ensayos de Antamina solos dan $m = 1$, un ángulo secante constante, porque en """ + f"{N_SUBE} de sus {N_TEND}" + r""" sets con varios esfuerzos el ángulo secante sube con el esfuerzo, algo que no es esperable en un enrocado. Extrapolar esa linealidad daría """ + f1(PH1_10) + r"""° a 10~MPa, en vez de """ + f1(phis(10, OP2['pe0'], MC)) + r"""°.
\item \textbf{La relación de vacíos es la de colocación y no baja con la profundidad.} $e = 0.45$ está en el extremo suelto del ROM de Antamina y es el valor de la literatura para botaderos altos de volteo; como los pesos unitarios de Antamina incluyen densificación, el diseño se verifica también con $e = """ + f"{EV:.2f}" + r"""$, que baja $\phi'_s$ unos 2°. No se reduce con la profundidad porque Leps 2.0 se calibró con la $e$ inicial de las probetas, antes de consolidar: la densificación por carga ya está dentro de $m$, y bajar además la $e$ la contaría dos veces. Los perfiles de densificación se entregan como sensibilidad.
\end{enumerate}

\textbf{Comprobaciones.} Con esa curva, los ensayos de Antamina quedan en mediana """ + "; ".join(f"{sg(m_)}° entre {a_.split(', ')[1].replace(' a ', ' y ')}" for a_, n_, m_, b_ in CMP[:3]) + r""" (medido menos curva, cada ensayo a su $e$): la curva queda sobre ellos a bajo esfuerzo y bajo ellos sobre 2~MPa. Entre """ + f"{f2(SNX)} y {f2(SNW)}" + r"""~MPa, donde no hay ensayos de Antamina, los ensayos mundiales de roca de calidad buena y moderada quedan sobre la curva (mediana """ + f"{sg(CLW['good'][1])}° y {sg(CLW['moderate'][1])}°" + r"""), y los de calidad baja, los comparables al desmonte de Antamina, quedan cerca de ella (""" + f"{CLW['low'][0]} ensayos, mediana {sg(CLW['low'][1])}°" + r"""). Frente a las envolventes de \citet{leps}, con $e = 0.45$ la curva queda entre la media y la inferior sobre """ + f2(X_MED) + r"""~MPa y alcanza la inferior a unos """ + f1(X_INF) + r"""~MPa; con la densificación del perfil A seguiría a la media. Queda sobre la cota inferior de \citet{indraratna1993} en la forma de Leps 2.0, que no depende de $e$, hasta 15~MPa; si la cota se lee como normalizada a $e = 0.6$, como la trazaron \citet[p.~13]{cylwik}, la curva evaluada a esa $e$ la cruza a unos """ + (f"{S_LB06:.0f}" if math.isfinite(S_LB06) else "más de 300") + r"""~MPa (sección~\ref{sec:curva}).

\textbf{Lo que no está respaldado.} No hay ensayos de Antamina sobre """ + f2(SNX) + r"""~MPa, y sobre """ + f2(SNW) + r"""~MPa no hay ensayos en ninguna fuente: ahí la curva es una extrapolación. No hay densidad in situ de desmonte volteado ni medición de su compresibilidad. La caliza y las margas, el 30~\% del desmonte de LE2, no tienen ensayos de resistencia, y el mármol, la litología ensayada más débil, es el 38~\%. El efecto del tamaño de partícula, del ensayo al campo, se estimó como sensibilidad y no se aplica a la curva: bajaría $\phi'_1$ entre """ + f"{abs(TAMC[round(DLABS[0])][1]):.1f}" + r""" y """ + f"{abs(TAMC[round(DLABS[2])][1]):.1f}" + r"""° (sección~\ref{sec:tamano}). La curva se apoya en """ + f"{P.set.nunique()}" + r""" sets de un solo sitio y la banda no incluye la variabilidad espacial del botadero. Los ensayos que más reducirían la incertidumbre son la densidad in situ y triaxiales de gran escala a alto confinamiento (sección~\ref{sec:ensayos}).

\section{Objetivo y alcance}\label{sec:obj}
Este memorándum propone, para la revisión del EoR, una curva de resistencia al corte drenada para el desmonte ROM de Antamina. Stantec ajustó el criterio Leps 2.0 \citep{cylwik}, que actualiza las envolventes de \citet{leps} con una base de unos 900 ensayos de gran escala, a los triaxiales drenados (de gran escala y de 6~in) y a los cortes directos de gran escala disponibles, y estimó la incertidumbre de la curva por nivel, curvatura y relación de vacíos, en particular por encima del máximo esfuerzo ensayado. """ + TXT_OBJ_ESCALA + r""" La curva corresponde a desmonte colocado por volteo descendente con relación de vacíos $e = 0.45$, con alternativas de $e$ y perfiles de densificación por profundidad (sección~\ref{sec:e}).

La curva trata el desmonte ROM como un solo material, como el diseño geotécnico del Depósito de Desmonte Este (DDE), que no zonifica el botadero por litología \citep[Tabla~3-1]{stantec2026iff}: se ajustó con todos los ensayos con igual peso, sin ponderar por litología. Como control, ponderar los ensayos con la producción de desmonte por litología desde 2021 que el DDE incluye en sus bases de diseño da prácticamente la misma curva (sección~\ref{sec:curva}). El documento no incluye análisis de estabilidad ni propone criterios de aceptación. Las limitaciones de uso están en la sección~\ref{sec:uso}.

\section{Datos}\label{sec:datos}
\subsection{Ensayos disponibles y uso}
La Tabla~\ref{tab:inventario} lista los ensayos de desmonte de Antamina disponibles para este memorándum y el uso que se dio a cada grupo. Stantec verificó los valores de la base de datos contra las hojas de laboratorio de cada informe o, donde no hay hoja, contra sus gráficos. Los triaxiales usados en el ajuste coinciden con los informes dentro del redondeo en $\sigma'_3$, desviador, $\varepsilon_a$ y $\varepsilon_v$ en el máximo desviador. El Anexo~\ref{sec:anexo} da, ensayo por ensayo, los """ + f"{len(A27)}" + r""" ensayos de resistencia de la Tabla~\ref{tab:inventario} con su uso (ajuste, contraste o no usado, con el motivo) y sus esfuerzos en la falla.

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

\subsection{Ensayos de caracterización}\label{sec:caract}
La Tabla~\ref{tab:cobertura} muestra cuánta información hay por tipo de ensayo y por litología, y la Tabla~\ref{tab:caract} resume sus resultados: granulometría y clasificación, peso específico y absorción, densidad, compresibilidad, carga en plataforma, permeabilidad, degradabilidad, resistencia de la roca y fragmentación de campo. Los valores son los que informa cada fuente, contrastados con la página del informe, la lámina o la planilla citada; cuando la fuente da un valor por litología o por muestra, la tabla da el rango entre esos valores. Stantec calculó solo lo que se indica en las notas: las estadísticas de fragmentación por clase, la densidad y la fracción en masa del modelo de bloques y un percentil de la planilla de roca. De \citet{g2010} se incluyen las dos fases: la A, de material del tajo, y la B, del mismo material chancado. El Anexo~\ref{sec:anexob} da los valores de cada tipo de desmonte (litología, clase de desmonte o unidad geotécnica) y de cada muestra, con la tabla o página de origen. De estos datos, el memorándum usa el $G_s$ de sólidos de \citet{g2010} para calcular la $e_0$ (Tabla~\ref{tab:e0}), los edómetros para los perfiles de $e$ (Tabla~\ref{tab:edo}) y la fragmentación para el $D_{max}$ de campo (sección~\ref{sec:tamano}); los demás caracterizan el material y no entran en el ajuste de la curva.

La cobertura es desigual. La caliza y las margas-limonitas, que suman el 30~\% del desmonte de LE2 en el modelo de bloques, no tienen ensayos de laboratorio sobre desmonte; solo hay ensayos de roca de la unidad LMH y 7 colpas de caliza en la carga puntual de \citet{w2024}. El skarn tiene ensayos índice solo de \citet{g2010}, con una muestra por fase, y ningún ensayo de resistencia drenado. El mármol, la litología más abundante (38~\%), es la más degradable de las ensayadas \citep[p.~3]{g2010}: pérdida en Los Ángeles de 41 a 62~\%, frente al límite de 60~\% de la especificación de enrocado 3B, y pérdida en sulfato de 43.4 y 49.8~\%, frente a la pérdida máxima de 18~\% que citan las hojas para agregado grueso; el intrusivo da 33.4 y 18.6~\% (notas $g$ y $h$ de la Tabla~\ref{tab:caract}). No hay ensayos de durabilidad por humedecimiento y secado, por congelamiento y deshielo, ni de desmonte degradado.

\begin{table}[!htbp]\centering\scriptsize\setlength{\tabcolsep}{2.5pt}\caption{Cantidad de datos por tipo de ensayo y litología. Cada celda da el número de muestras, probetas o ensayos según la columna Unidad; --: sin datos.}\label{tab:cobertura}
\begin{tabular}{L{3.0cm}L{1.45cm}>{\raggedleft\arraybackslash}p{1.15cm}>{\raggedleft\arraybackslash}p{1.15cm}>{\raggedleft\arraybackslash}p{1.15cm}>{\raggedleft\arraybackslash}p{1.15cm}>{\raggedleft\arraybackslash}p{1.15cm}>{\raggedleft\arraybackslash}p{1.15cm}>{\raggedleft\arraybackslash}p{1.15cm}>{\raggedleft\arraybackslash}p{1.15cm}}\toprule
Ensayo & Unidad & Mármol & Hornfels & Intrusivo & Skarn & Caliza y margas & \hspace{0pt}Mezcla de litologías & Con relave & Total\\\midrule
\multicolumn{10}{l}{\textit{Fracción en masa del desmonte de LE2, 2035--2049 \citep{antamina2024mr}, en \%}} \\
Modelo de bloques MR2024 & \% & 37.8 & 15.5 & 17.0 & -- & 29.6 & -- & -- & 99.9\\\midrule
\multicolumn{10}{l}{\textit{Resistencia del desmonte (Anexo~\ref{sec:anexo} y Tabla~\ref{tab:edo})}} \\
Triaxial drenado, incluye carga y descarga & Probetas & 6 (11) & 7 & 6 & -- & -- & 3 & -- & 22 (27)\\
Corte directo de gran escala & Probetas & 3 & 3 & 6 & -- & -- & 3 & -- & 15\\
Triaxial no drenado (CU) & Probetas & 15 & 18 & 21 & 15 & -- & 3 & -- & 72\\
Triaxial cíclico y monótono & Probetas & 3 & 3 & -- & -- & -- & -- & -- & 6\\
Edómetro de gran escala & Probetas & 4 & 3 & 1 & -- & -- & -- & 3 & 11\\
Carga directa en plataforma (chancado) & Ensayos & 1 & 1 & 1 & 1 & -- & -- & -- & 4\\\midrule
\multicolumn{10}{l}{\textit{Ensayos índice del desmonte (Tabla~\ref{tab:caract} y Anexo~\ref{sec:anexob})}} \\
Granulometría (terreno o laboratorio) & Muestras & 5 & 5 & 6 & 2 & -- & 3 & 9 & 30\\
Límites de Atterberg & Muestras & 1 & 2 & 3 & -- & -- & 3 & -- & 9\\
$G_s$ y absorción & Muestras & 3 & 4 & 13 & 2 & -- & 3 & -- & 25\\
Densidad in situ y humedad natural & Muestras & 2 & 2 & 2 & 2 & -- & -- & -- & 8\\
Humedad natural (Anddes) & Muestras & 1 & 1 & 2 & -- & -- & 1 & -- & 5\\
Densidad mínima y máxima & Muestras & 2 & 2 & 2 & 2 & -- & -- & 3 & 11\\
Proctor estándar & Muestras & 1 & 1 & 2 & -- & -- & 2 & 9 & 15\\
Permeabilidad & Probetas (escalones) & 2 (13) & 3 (9) & 3 (7) & -- & -- & -- & 9 (21) & 17 (50)\\
Los Ángeles & Muestras & 6 & 4 & 10 & 2 & -- & -- & -- & 22\\
Durabilidad en sulfato & Muestras & 2 & 2 & 2 & 2 & -- & -- & -- & 8\\
UCS de partículas & Probetas & 17 & 9 & 11 & 4 & -- & -- & -- & 41\\
Carga puntual de partículas & Probetas o colpas & 12 & 12 & 43 & 12 & 7 & -- & -- & 86\\\midrule
\multicolumn{10}{l}{\textit{Roca del tajo LE2 por unidad geotécnica \citep{antamina2025le2}}} \\
UCS & Ensayos & -- & 275 & 379 & 699 & 1111 & -- & -- & 2464\\
Carga puntual axial y diametral & Ensayos & -- & 1648 & 2563 & 4529 & 9878 & -- & -- & 18\,618\\
Tracción brasileña & Ensayos & -- & 304 & 206 & 528 & 834 & -- & -- & 1872\\
Corte directo & Ensayos & -- & 113 & 66 & 204 & 507 & -- & -- & 890\\
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize Mármol incluye mármol diópsida; hornfels, hornfels diópsida; intrusivo, Intrus-Estruct-Tab y brechas; skarn, las unidades END, EXO y XDP de LE2 y el exoskarn diópsido de \citet{g2010}; caliza y margas, la unidad LMH y las litologías Caliza y Margas-Limonitas del modelo. El modelo de bloques no distingue skarn. Mezcla de litologías: desmonte compuesto y tipo B de \citet{g2021} y pila 01 de \citet{anddes2024}. Con relave: mezclas de desmonte y relave de \citet{g2021} y \citet{w2024}. Triaxial drenado de mármol: entre paréntesis, con las 5 copias de \citet{g2012} que trae \citet{w2022}. Los totales de roca excluyen 16 registros sin unidad asignada. Fragmentación de campo: 319 análisis por clase de desmonte (Tabla~\ref{tab:b_frag}).\end{table}

\clearpage
\begin{footnotesize}\setlength{\tabcolsep}{3pt}
\begin{longtable}{L{2.3cm}L{2.1cm}L{2.4cm}>{\raggedleft\arraybackslash}p{1.55cm}L{4.0cm}L{2.25cm}}
\caption{Ensayos de caracterización de desmonte y de roca de Antamina, con los valores informados por cada fuente. TM: tamaño máximo; finos: pasante del tamiz N.º~200; NP: no plástico.}\label{tab:caract}\\
\toprule Ensayo & Fuente & Material & $n$ & Resultado & Uso\\\midrule\endfirsthead
\toprule Ensayo & Fuente & Material & $n$ & Resultado & Uso\\\midrule\endhead
""" + "\n".join(filas_car) + r"""
\bottomrule
\end{longtable}\end{footnotesize}
\vspace{-6pt}{\footnotesize $^{a}$Clasificación calculada por el laboratorio con el material menor que 3~in. $^{b}$La Tabla~2 del informe da 2.451--3.172 para el mismo ensayo; el valor de la tabla es el de las hojas de laboratorio. $^{c}$Informes marcados «fuera de método». $^{d}$Convertido de cm/s. $^{e}$El informe no los considera indicativos de la permeabilidad del material: la conductividad del equipo es del orden de $10^{-4}$~m/s y el flujo pudo ir por las paredes del molde. $^{f}$Tabla~9 del informe; la hoja de laboratorio de la mezcla 1:1 de la alternativa~1 da $8.9\times10^{-7}$~m/s. $^{g}$Hojas ASTM C535 del anexo; el texto del informe (p.~38) resume 17~\% para el hornfels y 43~\% (2011) y 45--50~\% (2021) para el mármol, y cita la especificación de enrocado 3B: pérdida menor que 60~\% y UCS de 40~MPa como mínimo. $^{h}$Sulfato de magnesio según las hojas de laboratorio, que citan una pérdida máxima especificada de 18~\% para agregado grueso (ASTM C33); el texto del informe indica sulfato de sodio (ASTM C88). $^{i}$Las hojas de IDIEM de la muestra REG~41061 indican «Tipo de Roca: Marmol». $^{j}$Valores de la Tabla~6; el texto del informe da 64.0--143.1~MPa. $^{k}$La Tabla~2 del informe repite en la fase B el TM de la fase A; la Tabla~1 indica 12~in después del chancado. $^{l}$Ensayos de las hojas de la planilla, de 1997 a 2024: 2470 de UCS, 4657 de carga puntual axial, 13\,971 de carga puntual diametral, 1872 de tracción y 890 de corte directo (261 combinaciones distintas); además, 42\,500 tramos de logueo con RMR, RQD y FF. La fuente indica que incluye solo ensayos desde la configuración del plan minero 2036 hacia abajo. $^{m}$Bloques del modelo, no ensayos. $^{n}$Las fichas y la Tabla~2 del informe indican ASTM C535; el texto, C131. $^{o}$Categorías del estudio Mine-to-mill 2007/2009 que cita la lámina; no son las clases A, B, C y C1 de Antamina. $^{p}$Clase A. La clase y la fase están asociadas: 26 de los 27 análisis de la clase C1 son de la fase 10 y 27 de los 30 de la clase B, de la fase 9.\par}

\subsection{Diferencias entre los ensayos y el campo}
Los ensayos no reproducen el desmonte del botadero en dos aspectos, y ambos deben tenerse presentes al usar la curva:
\begin{itemize}
\item \textbf{Tamaño de partícula.} El desmonte ROM de Antamina tiene $D_{max}$ de """ + f"{FR['Dmax']:.0f}" + r"""~mm en mediana (""" + f"{FR['Dmax_p10']:.0f}--{FR['Dmax_p90']:.0f}" + r"""~mm entre los percentiles 10 y 90), $D_{50}$ de """ + f"{FR['D50']:.0f}" + r"""~mm y $D_{80}$ de """ + f"{FR['D80']:.0f}" + r"""~mm, según """ + f"{FR['n']}" + r""" análisis de fragmentación por fotos en el frente de carguío \citep{antamina2025frag}. Los ensayos del ajuste se hicieron con $D_{max}$ de 25 a 178~mm, es decir, con la gradación cortada (escalpada) a entre 1/""" + f"{FR['Dmax'] / max(DLABS):.0f} y 1/{FR['Dmax'] / min(DLABS):.0f}" + r""" del $D_{max}$ mediano de campo. El efecto del tamaño se trata en la sección~\ref{sec:tamano}.
\item \textbf{Densidad.} Las probetas se compactaron, con $e_0$ de """ + f"{P.e.min():.3f} a {P.e.max():.3f}" + r""", y se densificaron más al consolidar: en \citet{g2012}, la $e$ bajó entre 0.03 y 0.11 según el informe. La curva se lleva a la $e$ de colocación del botadero, 0.45, con la corrección por densidad de Leps 2.0 (sección~\ref{sec:e}). Las únicas densidades in situ de desmonte disponibles para este memorándum son las de \citet[Tabla~2]{g2010}, por reemplazo de agua (ASTM D5030), un ensayo por litología. En la fase A dan $e$ de """ + f"{min(ein_A):.2f} a {max(ein_A):.2f}" + r""" con el $G_s$ del material grueso de cada litología (más altas con el $G_s$ de sólidos, ASTM D854). Las hojas ubican el ensayo en la «parte baja chancadora secundaria» (pp.~35--38) y el informe no describe cómo se colocó ese material, de modo que nada indica que represente desmonte volteado desde gran altura. Por eso no se usan como $e$ de colocación.
\end{itemize}

La Tabla~\ref{tab:e0} muestra de dónde sale la $e_0$ de cada set. Los informes usan $G_s$ distintos, y algunos no lo informan. Para que todas las $e_0$ sean comparables se recalcularon con la densidad seca del informe y el $G_s$ de sólidos (ASTM D854) de \citet[p.~49]{g2010} por litología, promedio de las fases A y B: mármol 2.755, hornfels 2.797 e intrusivo 2.708, ponderados por la composición en las mezclas.

\begin{table}[H]\centering\footnotesize\setlength{\tabcolsep}{3pt}\caption{Relación de vacíos inicial por set: densidad seca del informe, $G_s$ y $e_0$ informados, y $e_0$ adoptada con el $G_s$ de sólidos (ASTM D854) de \citet{g2010}.}\label{tab:e0}
\begin{tabular}{L{2.2cm}L{2.7cm}L{1.6cm}rL{2.0cm}rrr}\toprule Informe$^{r}$ & Set & Litología & $\rho_d$ (t/m³) & $G_s$ informado & $e_0$ inf. & $G_s$ adopt. & $e_0$ adopt.\\\midrule
""" + "\n".join(filas_e0) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{h}$Tomado por el laboratorio de la hoja de los ensayos de 6~in de Golder. $^{i}$El informe no da $G_s$; el valor es el de \citet{w2024}. $^{d}$Corte directo: densidad seca de la probeta, con la que se calculó la $e_0$. $^{r}$Referencias completas: \citet{g2012}, \citet{g2021}, \citet{w2022}, \citet{w2024}, \citet{i2025} y \citet{anddes2024}.\end{table}

\subsection{Aspectos de los ensayos del ajuste}
Seis aspectos condicionan la interpretación:
\begin{enumerate}
\item """ + str(n_ciclo) + r""" ensayos tuvieron ciclos de carga y descarga antes del máximo desviador (en \citealp{g2012}, a partir de cerca del 50~\% de la resistencia última estimada, p.~7) y luego carga monótona hasta la falla. Son triaxiales drenados comparables a un CD, porque el máximo desviador se alcanza en la carga monótona, pero los ciclos pueden haber densificado la probeta. Son distintos de los seis ensayos cíclicos de \citet{w2022}, con ciclos de compresión y extensión, que no se usan.
\item Los ensayos se programaron hasta cerca de 20~\% de deformación axial, y ningún informe indica que se detuvieran por límite del equipo (dos de \citealp{i2025} terminaron en 15.0 y 16.7~\% sin explicación del laboratorio). La mayoría alcanzó el máximo desviador entre 11 y 21~\% de deformación axial, y en cuatro el máximo coincidió con el último punto: en esos casos el desviador podía seguir creciendo y el valor usado es una cota inferior. Dos ensayos llegaron al máximo con cerca de 4~\%: """ + "; ".join(f"{CIT[r.fuente_id]}, {LITS(r.fuente_id, r.litologia)}, $\\sigma'_3 = {r.s3:.2f}$~MPa" for _, r in EPS4.iterrows()) + r""".
\item Los """ + f"{n_eps}" + r""" ensayos tienen registro de volumen. En """ + f"{n_contr_seg}" + r""" la deformación volumétrica acumulada en el máximo desviador era de contracción: la probeta no había llegado a dilatar, de modo que la resistencia última puede ser algo mayor, en particular en el hornfels. En los dos ensayos de 6~in de \citet{w2022} el signo de $\varepsilon_v$ es dudoso, porque la leyenda de las hojas indica que el valor negativo es dilatación.
\item En el hornfels de 6~in de \citet{w2022}, la hoja informa un desviador máximo de 4100~kPa a 11.4~\% de deformación, pero su curva sigue subiendo hasta unos 4600~kPa cerca de 17.5~\% (lectura del gráfico). Se usa el valor de la hoja, del lado conservador.
\item Los cortes directos de \citet{anddes2024} se hicieron en una caja de 30.5~cm con la muestra cortada a 1~in (relación caja/partícula de 12; para probetas densas, \citealp[p.~297]{ovalle2023} recomiendan una relación de 12 a 24 para que la resistencia crítica sea representativa, y su resultado no se refiere a la resistencia pico), con $\sigma'_n$ de 0.3 a 1.2~MPa (1.0~MPa en la pila 01, que no cumple en sentido estricto la recomendación de Leps 2.0 de tener al menos un ensayo de corte directo sobre 1~MPa). Se usa el $\tau$ pico. Los ensayos terminaron a unos 66~mm de desplazamiento en las rumas y 64~mm en las pilas. Según la lectura de las curvas, en """ + f"{len(DS_FIN)}" + r""" ensayos el pico se alcanzó al final del ensayo (en dos de ellos $\tau$ seguía creciendo), así que el valor es una cota inferior; y en """ + f"{len(DS_DUD)}" + r""" (pila 02 a 0.3~MPa) la curva no muestra el $\tau$ pico de la tabla del laboratorio (353.9~kPa; unos 349~kPa al final), un dato dudoso que se mantiene tal como fue informado. El laboratorio no informa $G_s$, de modo que la $e$ se calculó con la densidad seca inicial y el $G_s$ de sólidos (ASTM D854) de \citet[p.~49]{g2010}, promedio de las fases A y B, el mismo criterio que se usó para el mármol de \citet{g2012}: """ + ", ".join(f"{LITN[l]} {v:.3f}" for l, v in GSD.items()) + r""". Con el $G_s$ del rótulo del ensayo Proctor (hasta 3.06 en el mármol), las $e$ serían mayores y la resistencia corregida a $e = 0.45$, más alta.
\item La $e_0$ es la inicial de la probeta, antes de consolidar, como en la base de Leps 2.0 \citep[p.~4 y Tabla~2]{cylwik}. En \citet{g2012} se recalculó con $G_s = 2.755$ \citep{g2010}, por lo que difiere de la del informe (0.286); \citet{i2025} no informa $G_s$. Para homogeneizar, la $e_0$ adoptada se calcula con el $G_s$ de sólidos (ASTM D854) de \citet{g2010} de cada litología: 2.755 en el mármol, 2.797 en el hornfels y 2.708 en el intrusivo (Tabla~\ref{tab:e0}). Los informes usan valores distintos: en el mármol, 2.70 (unos 0.02 en $e$); en el intrusivo, 2.85 en los triaxiales de \citet{w2024} (unos 0.07 en $e$ y 1.4° en $\phi'_1$); y en el hornfels de \citet{w2022}, 2.75.
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

\needspace{18\baselineskip}\section{Método}\label{sec:metodo}
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

\section{Cómo se construyó la curva}\label{sec:decisiones}
La Ec.~(1) tiene tres parámetros, $\phi'_{e=0}$, $\omega$ y $m$, y se aplica con una relación de vacíos $e$. $\omega$ se fijó en 20°, el valor de Leps 2.0, porque el rango de $e_0$ de los ensayos de Antamina es demasiado estrecho para ajustarlo. Las otras tres cantidades se decidieron como sigue; los detalles están en las secciones que se indican.

\subsection{Nivel: los ensayos de Antamina}
Para cada set se calculó $\phi'_1$ con el $m$ de la curva (Ec.~8 de \citealp{cylwik}), y con su $e_0$ (Tabla~\ref{tab:e0}), $\phi'_{e=0} = \phi'_1 + 20°\,e_0$ (Ec.~25). El nivel de la curva es la media de los """ + f"{P.set.nunique()}" + r""" sets, todos con igual peso, porque el DDE trata el desmonte como un solo material. Los $\phi'_1$ de los sets van de """ + f"{_S34.phi1.min():.1f}° a {_S34.phi1.max():.1f}°" + r""" (Fig.~\ref{fig:phi1e}): el hornfels queda arriba y el mármol y los cortes directos, abajo. El resultado, $\phi'_{e=0} = """ + f"{OP2['pe0']:.2f}" + r"""°$, cae entre las clases de calidad baja (47°) y moderada (50°) de Leps 2.0 \citep[Ec.~25]{cylwik}, lo que es coherente con la Tabla~5 de \citet{cylwik}, que clasifica la caliza como de calidad baja. Se prefirió el nivel de los ensayos al de una clase genérica porque los ensayos son del material de Antamina.

\textbf{Ajuste en dos pasos.} Como control, se ajustaron por separado la curvatura y la pendiente $\omega$. En el primer paso, una $m$ común y un $\phi'_1$ por set, con los """ + f"{P.set.nunique()}" + r""" sets de Antamina y los """ + f"{A30['n_sets_mundo']}" + r""" sets mundiales con ensayos sobre """ + f"{A30['snx']:.2f}" + r"""~MPa, que aportan solo la curvatura y pesan lo mismo que Antamina: resulta $m = """ + f"{A30['paso1']['0.5']['m']:.2f}" + r"""$ (""" + f"{A30['paso1']['0.0']['m']:.2f}" + r""" con Antamina sola). Esa $m$ combina la linealidad de Antamina con la curvatura mundial en todo el rango de esfuerzos y queda cerca del límite superior de la banda (""" + f"{A33['hipotesis']['m_p90']['m_a']:.2f}" + r"""); la curva usa $m = """ + f"{MC:.2f}" + r"""$ porque es la que mejor predice los ensayos de mayor esfuerzo, que es donde se usará (sección~\ref{sec:alto}). En el segundo paso, la recta $\phi'_1 = \phi'_{e=0} - \omega\,e$ con los """ + f"{P.set.nunique()}" + r""" sets da $\omega = """ + f"{A30['criterio_omega']['omega']:.0f}" + r"""°$, con intervalo al 90~\% (\emph{bootstrap} por sets) de """ + f"${A30['criterio_omega']['ic90'][0]:.0f}$ a ${A30['criterio_omega']['ic90'][1]:.0f}$" + r"""°: la $e_0$ de los sets varía poco (""" + f"{min(A30['e0_set']):.2f} a {max(A30['e0_set']):.2f}" + r""") y la litología pesa más que la densidad, de modo que $\omega$ no se puede identificar con estos ensayos. Con la base mundial (sets por clase de roca), $\omega = """ + f"{A30['omega_mundo']['omega']:.1f}" + r"""°$, una regresión entre materiales que mezcla la clase de roca con la densidad; dentro de un mismo tipo de roca, \citet[Tabla~7]{cylwik} obtienen 14 a 17°. Por eso la curva mantiene $\omega = 20°$, el valor de Leps 2.0. Con $e = 0.45$ su efecto es pequeño: como la $e_0$ media de los sets es """ + f"{np.mean(A30['e0_set']):.2f}" + r""", $\omega$ de 15 a 25° cambia $\phi'_1$ en $\pm$""" + f"{5 * (0.45 - np.mean(A30['e0_set'])):.1f}" + r"""°.

\begin{figure}[htbp]\centering\includegraphics[width=0.85\linewidth]{figs/Fig_phi1_e.pdf}
\caption{$\phi'_1$ de cada set de Antamina (con $m = """ + f"{MC:.2f}" + r"""$) frente a su $e_0$ media, y la recta de la curva propuesta, $\phi'_1 = """ + f"{OP2['pe0']:.1f}" + r"""° - 20°\,e$. En gris, las envolventes de \citet{leps} y la cota inferior de \citet{indraratna1993}, que no dependen de $e$ \citep[p.~2 y Tabla~1]{cylwik}.}\label{fig:phi1e}\end{figure}

\subsection{Forma: el exponente de la base mundial}
Ajustados solos, los ensayos de Antamina llevan $m$ al límite de Leps 2.0, $m = 1$: el ángulo secante no baja con el esfuerzo. En """ + f"{N_SUBE} de los {N_TEND}" + r""" sets con varios esfuerzos el ángulo secante sube con el esfuerzo, y baja en """ + f"{N_BAJA}" + r""". Que el ángulo secante de un enrocado suba con el esfuerzo no es esperable, y su causa no está identificada (sección~\ref{sec:alto}). En la mayoría de los triaxiales el máximo desviador llega al final de la carrera, sin pico (sección~\ref{sec:datos}); eso subestima la resistencia, sobre todo a $\sigma'_3$ alto, de modo que no explica la linealidad. No se pueden corregir los ensayos con los datos disponibles: todas las probetas de un set tienen la misma $e_0$, y la $e$ después de consolidar solo está en \citet{g2021}. Por eso el exponente se toma de la base mundial de Leps 2.0, con el criterio de que prediga bien los ensayos de mayor esfuerzo, que es donde se usará: $m = """ + f"{MC:.2f}" + r"""$ (sección~\ref{sec:alto}). La hipótesis $m = 1$ se informa como sensibilidad (Tabla~\ref{tab:hip}).

\subsection{Relación de vacíos: la de colocación, sin densificación}
La curva se aplica con la $e$ del desmonte al colocarse. El valor base, 0.45, está en el extremo suelto del ROM de Antamina y coincide con la literatura de botaderos altos de volteo (sección~\ref{sec:e}). Las $e_0$ de los ensayos, de """ + f"{P.e.min():.2f} a {P.e.max():.2f}" + r""", corresponden a probetas compactadas, no a ROM volteado. La $e$ no se reduce con la profundidad, porque Leps 2.0 se calibró con la $e$ inicial de las probetas: las que se ensayaron a mayor confinamiento también se densificaron al consolidar, y ese efecto ya está en $m$. La densificación con la profundidad se trata como sensibilidad con los perfiles $e(z)$ (sección~\ref{sec:e}), hasta contar con densidad in situ representativa.

\subsection{Comprobaciones}
La Tabla~\ref{tab:cmp} compara la curva con los ensayos, cada uno con la curva evaluada a su propia $e$. Con los ensayos de Antamina, el sesgo por rango es el costo de no extrapolar su linealidad. Con la base mundial, la diferencia depende de la calidad de la roca: los materiales de calidad buena y moderada son más resistentes que el desmonte de Antamina, y los de calidad baja quedan cerca de la curva. Sobre """ + f2(SNX) + r"""~MPa, la curva queda por debajo de la base mundial por la diferencia de material, no por su curvatura, que se verificó con el nivel de cada set.

\begin{table}[htbp]\centering\small\caption{Ensayos frente a la curva propuesta, cada uno a su $e$: diferencia de $\phi'_s$ (medido menos curva).}\label{tab:cmp}
\begin{tabular}{L{8.6cm}rrr}\toprule Grupo & Ensayos & Mediana (°) & Bajo la curva\\\midrule
""" + "\n".join(filas_cmp) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize Calidad de la roca según la clasificación de la base mundial \citep[Tabla~5]{cylwik}.\end{table}

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
La linealidad de Antamina no autoriza a extrapolarla. Su causa no está identificada: puede influir la densificación de las probetas durante la consolidación y los ciclos de carga, pero en la base mundial $m$ casi no se correlaciona con la relación de vacíos ni con el tamaño (ver abajo), de modo que esas propiedades no la explican por sí solas. La decisión de no usar el $m$ de Antamina se basa en no extrapolar fuera de su rango un resultado de """ + str(P.set.nunique()) + r""" sets de un solo sitio, no en una causa demostrada. Por eso el exponente de la curva propuesta se toma de la base mundial de Leps 2.0. En sus """ + f"{RM['n_sets']}" + r""" sets triaxiales con $\sigma'_3 \ge 0.06$~MPa (la guía 60--600 de \citealp[p.~11]{cylwik}), al menos tres ensayos y $\sigma'_n$ máximo de al menos el doble del mínimo, la pendiente de $\ln\tau$ frente a $\ln\sigma'_n$ (que en Leps 2.0 es $m$) tiene mediana """ + f"{RM['m_P50_sets']:.2f}" + r""", P10 de """ + f"{RM['m_P10_sets']:.2f}" + r""" y P90 de """ + f"{RM['m_P90_sets']:.2f}" + r""". La curvatura se atribuye a la rotura de partículas, que crece con el confinamiento y reduce la dilatancia \citep{marsal1967,indraratna1993}. Para elegir el exponente se buscó el que mejor predice los ensayos mundiales de mayor esfuerzo, que es donde se usará la curva: en cada set con ensayos sobre 4.6~MPa, el nivel se fijó con sus ensayos de menor esfuerzo y se predijeron los de mayor esfuerzo con un $m$ común. El $m$ con residuo mediano nulo es """ + f"{M_SB:.3f}" + r""" (intervalo al 90~\% de """ + f"{M_IC[0]:.3f} a {M_IC[1]:.3f}" + r"""), y la curva propuesta usa $m = """ + f"{MC:.2f}" + r"""$; la mediana de los sets es """ + f"{M_MED:.2f}" + r""". Ese intervalo es el de la $m$ mediana de la base, no el de un material nuevo; por eso la banda cubre además la dispersión entre materiales. La desviación estándar de las pendientes es """ + f"{R19['m_sd_sets']:.3f}" + r"""; descontado el error de ajuste de cada set, la dispersión entre materiales es """ + f"{RM['tau']:.3f}" + r""" (estimador de Paule--Mandel). Las propiedades de los materiales la explican poco: en esos sets, la correlación de Spearman de $m$ con la relación de vacíos, el tamaño máximo, la resistencia de la roca y la rotura es como máximo de """ + f"{R19['max_abs_spearman']:.2f}" + r""" en valor absoluto, y agregar la relación de vacíos, el tamaño y la clase de roca la reduce poco (""" + f"{R19['tau_sin_covariables']:.3f} a {R19['tau_con_e_lnD_clase']:.3f}" + r"""). \citet[Tabla~4]{cylwik}, con el coeficiente de Pearson en sus 249 sets, informan correlaciones algo mayores de $m$ con el contenido de grava ($-0.32$) y el $D_{50}$ ($-0.24$), que siguen siendo débiles. Los pares $\sigma'_n$--$\tau$ de la base son los de \citet{cylwik}, que convirtieron los triaxiales con un procedimiento iterativo que considera la curvatura de cada set. Con la información disponible, la incertidumbre de $m$ para Antamina no puede bajar de esa dispersión sin ensayos representativos del campo a alto confinamiento (ítem~4 de la sección~\ref{sec:ensayos}). La base excluyó los ensayos con $\phi'_1 < 31°$ \citep[p.~4]{cylwik}, de modo que su distribución de $m$ puede estar sesgada.

Los ensayos de Antamina no se usan para la curvatura. Ajustados con un nivel propio por set, dan $m = """ + f"{RA['m']:.2f} \\pm {RA['se']:.2f}" + r"""$; en una calibración jerárquica con la base mundial, ese resultado pesaría un """ + f"{100 * RM['peso_antamina']:.0f}" + r"""~\% y llevaría $m$ a """ + f"{RM['post']['50'] if '50' in RM['post'] else RM['post'][50]:.2f}" + r""". Ese peso refleja solo la dispersión entre ensayos, no su representatividad del botadero.

La incertidumbre de la curva propuesta (sección~\ref{sec:curva}) se representa con una sola banda (Tabla~\ref{tab:hip}, Fig.~\ref{fig:phi}), que reúne dos fuentes:
\begin{itemize}
\item \emph{Curvatura.} $m$ entre """ + f"{A33['hipotesis']['m_p10']['m_a']:.3f} y {A33['hipotesis']['m_p90']['m_a']:.3f}" + r""", el P10--P90 de la $m$ entre materiales de la base mundial, que contiene el intervalo al 90~\% de la $m$ mediana (""" + f"{M_IC[0]:.3f} a {M_IC[1]:.3f}" + r"""). Los """ + f"{A25['ensayos'][_W]['n']}" + r""" ensayos mundiales sobre """ + f2(SNX) + r"""~MPa provienen de pocas publicaciones y no incluyen rocas carbonatadas, de modo que ese rango puede quedarse corto para el mármol y la caliza. Para cada $m$ se reajustó el nivel con los ensayos de Antamina. Las hipótesis no se dibujan una por una: la banda es su envolvente, y sus valores están en la Tabla~\ref{tab:hip}.
\item \emph{Nivel.} El intervalo del nivel al 90~\% (\emph{bootstrap} por sets, estratificado por litología).
\end{itemize}
La hipótesis $m = 1$, que es lo que dan los ensayos de Antamina solos, queda fuera de la banda y se informa como sensibilidad (Tabla~\ref{tab:hip}): daría un ángulo secante constante de """ + f1(phis(1, A33['hipotesis']['lineal']['pe0'], 1.0)) + r"""° a $e = 0.45$. Con $m = """ + f"{MC:.2f}" + r"""$, los ensayos de Antamina quedan en mediana """ + "; ".join(f"{sg(v_)}° entre {a_:g} y {f2(b_ if b_ < SNX else SNX)}~MPa ({n_} ensayos)" for a_, b_, v_, n_ in SESGO) + r""" respecto de la curva (medianas, medido menos curva): la curva queda sobre ellos a bajo esfuerzo y bajo ellos sobre 2~MPa, el costo de no extrapolar la linealidad de Antamina.

La incertidumbre de la relación de vacíos de colocación no entra en la banda porque se trata explícitamente con las alternativas de $e$ de la sección~\ref{sec:e}; tampoco la de $\omega$ (15--25°), que entra solo en la desviación estándar total de $\phi'_1$ indicada abajo. La banda representa la incertidumbre de la curva media, no la dispersión entre ensayos ni entre litologías: """ + f"{N_SOBRE_B + N_BAJO_B} de los {len(P)} ensayos quedan fuera de ella, {N_SOBRE_B} por encima (sobre todo hornfels e intrusivo) y {N_BAJO_B} por debajo" + r""". La banda va de """ + f"{f1(lo(1))}° a {f1(hi(1))}° a 1~MPa, de {f1(lo(2))}° a {f1(hi(2))}° a 2~MPa, de {f1(lo(SNX))}° a {f1(hi(SNX))}° a {f2(SNX)}~MPa y de {f1(lo(8))}° a {f1(hi(8))}° a 8~MPa, y de {f1(lo(15))}° a {f1(hi(15))}° a 15~MPa, ya fuera de la base mundial" + r""".

Para análisis probabilísticos, la desviación estándar de $\phi'_{e=0}$ de la curva media es """ + f2(OP2['sd_pe0']) + r"""° (nivel; $m = """ + f"{MC:.2f}" + r"""$), y la de $\phi'_1$, sumando además $\omega$ entre 15° y 25° y $e$ entre 0.35 y 0.55 (distribuciones uniformes), es """ + f2(OP2['sd_phi1_total']) + r"""°. Ninguna incluye la variabilidad espacial del botadero.

\begin{table}[htbp]\centering\small\caption{Ángulo de fricción secante $\phi'_s$ (°) de la curva propuesta a $e = 0.45$ según la hipótesis de curvatura, con el nivel ajustado a los ensayos, límites de la banda de incertidumbre y sensibilidades del nivel y de la relación de vacíos. Sin el tope de """ + f"{TOPE:.0f}" + r"""°.}\label{tab:hip}
\setlength{\tabcolsep}{4.5pt}\begin{tabular}{lrrrrrrrr}\toprule Hipótesis & $m$ & $\phi'_{e=0}$ (°) & 1~MPa & 2~MPa & 3~MPa & """ + f2(SNX) + r"""~MPa & 8~MPa$^{w}$ & 15~MPa$^{w}$\\\midrule
""" + "\n".join(filas_t3) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{s}$Sensibilidad: el exponente de los ensayos de Antamina solos; no entra en la banda. $^{l}$Fracciones en masa del desmonte de LE2 del modelo de bloques, con la caliza y las margas asimiladas al mármol (sección~\ref{sec:curva}). $^{w}$Sobre el máximo de la base mundial de Leps 2.0 (""" + f2(SNW) + r"""~MPa): extrapolación fuera de toda la data (sección~\ref{sec:rango}).\end{table}

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
\tau = \tan\!\left(""" + f"{OP2['pe0']:.2f}" + r"""^{\circ} - 20^{\circ}\,e\right)\,(10p_a)^{""" + f"{1 - MC:.3f}" + r"""}\,\sigma_n'^{\,""" + f"{MC:.3f}" + r"""},\qquad \phi'_1(e = 0.45) = """ + f2(p2) + r"""°
\end{equation}
Como control, el DDE incluye en sus bases de diseño la producción de desmonte por litología desde 2021: intrusivo y exoskarn, 44~\%, y hornfels y mármol, 56~\% \citep[Tabla~3-1]{stantec2026iff}. Ponderar los ensayos de las tres litologías con esas fracciones (con el 56~\% repartido por igual entre hornfels y mármol, que el DDE no separa, y el 44~\% asignado al intrusivo, porque no hay ensayos de exoskarn) da $\phi'_{e=0} = """ + f2(OP2['pe0_dde']) + r"""°$, prácticamente la misma curva. Esa proporción no es la del desmonte de LE2. Con el modelo de bloques MR2024 (períodos de 2035 en adelante; Tabla~\ref{tab:cobertura}), el desmonte de LE2 tiene 37.8~\% de mármol, 15.5~\% de hornfels, 17.0~\% de intrusivo y 29.6~\% de caliza y margas, que no tienen ensayos de resistencia. Con los niveles por litología (mármol """ + f2(OP2['pe0_mar']) + r"""°, hornfels """ + f2(OP2['pe0_hor']) + r"""° e intrusivo """ + f2(OP2['pe0_int']) + r"""°) y la caliza y las margas asimiladas al mármol, el nivel es """ + f2(OP2['pe0_le2']) + r"""°: $\phi'_s$ baja unos """ + f"{phis(1, OP2['pe0'], MC) - phis(1, OP2['pe0_le2'], MC):.1f}" + r"""° en todo el rango. Con el mármol solo, el nivel es """ + f2(OP2['pe0_mar']) + r"""° (""" + f"{phis(1, OP2['pe0'], MC) - phis(1, OP2['pe0_mar'], MC):.1f}" + r"""° menos). Estas sensibilidades están en la Tabla~\ref{tab:hip}. La curva propuesta es la media de los sets ensayados, en los que el hornfels, la litología más resistente, pesa más que en el desmonte de LE2; si el EoR adopta una curva característica, estas sensibilidades indican su orden de magnitud. El mármol es la litología ensayada más débil y la más degradable (Tabla~\ref{tab:caract} y sección~\ref{sec:vacios}). Comparada con la cota inferior de \citet{hc2017} para construcción descendente de botaderos de peligro muy alto o alto ($\tau = 1.446\,\sigma^{0.898}$ en kPa, Tabla~5.9, propuesta para enrocado de calidad alta y moderada), la curva propuesta queda """ + sg(phis(1, OP2['pe0'], MC) - HC(1), 2) + "° a 1~MPa, " + sg(phis(3, OP2['pe0'], MC) - HC(3), 2) + "° a 3~MPa y " + sg(phis(8, OP2['pe0'], MC) - HC(8), 2) + r"""° a 8~MPa. Con $e = 0.45$, la curva propuesta queda """ + HC_POS + r""" esa cota genérica, y """ + f"{N_SOBRE_HC} de los {len(P)}" + r""" ensayos llevados a esa $e$ quedan sobre ella; la diferencia depende principalmente de la $e$ de colocación (sección~\ref{sec:e}).

\citet[Fig.~13, p.~49]{indraratna1993} propusieron un límite inferior para la resistencia de enrocados, 3° bajo el límite inferior que \citet{leps} había dado para enrocado de baja densidad, trazado entre unos 7~kPa y 3.5~MPa. \citet[p.~13]{cylwik} lo compararon con los ensayos de enrocados de calidad baja de su base ($e > 0.45$), normalizados a $e = 0.6$, encontraron que captura el borde inferior de esos datos y lo reproducen con su Ec.~9, $m = 0.9$ y $\phi'_1 = 33°$. Esos ensayos llegan a $\sigma'_n \approx 0.75$~MPa \citep[Fig.~19]{cylwik}, de modo que sobre ese esfuerzo la forma con $m = 0.9$ es una extrapolación. No es un ángulo mínimo constante: su ángulo secante también baja con el esfuerzo. En esa forma no depende de $e$ \citep[Tabla~1]{cylwik} y queda 3° bajo la envolvente inferior de \citet{leps}; da """ + f"{LB(1):.1f}° a 1~MPa, {LB(SNX):.1f}° a {f2(SNX)}~MPa y {LB(8):.1f}° a 8~MPa" + r""" (Figs.~\ref{fig:phi} y~\ref{fig:tau}). La curva propuesta queda """ + f"{sg(phis(1, OP2['pe0'], MC) - LB(1), 1)}° sobre esa forma a 1~MPa, {sg(phis(SNX, OP2['pe0'], MC) - LB(SNX), 1)}° a {f2(SNX)}~MPa, {sg(phis(8, OP2['pe0'], MC) - LB(8), 1)}° a 8~MPa y {sg(phis(15, OP2['pe0'], MC) - LB(15), 2)}° a 15~MPa" + (r""", y sobre ella en todo el rango hasta 15~MPa""" if LB_SOBRE else f", y la cruza a unos {S_LB:.1f}~MPa") + r""". Hay otra lectura: como \citet[p.~13]{cylwik} trazaron la cota con datos normalizados a $e = 0.6$, puede compararse con la curva evaluada a esa $e$; así, el margen es de """ + f"{sg(phis(1, OP2['pe0'], MC, 0.6) - LB(1), 1)}° a 1~MPa y {sg(phis(10, OP2['pe0'], MC, 0.6) - LB(10), 1)}° a 10~MPa" + r""", y la curva cruza la cota a unos """ + (f"{S_LB06:.0f}" if math.isfinite(S_LB06) else "más de 300") + r"""~MPa. Sobre """ + f2(SNX) + r"""~MPa las dos son extrapolaciones: la curva propuesta, de los ensayos de Antamina (sección~\ref{sec:rango}), y la cota, de ensayos que llegan a unos 0.75~MPa. La cota no se usa para acotar la banda, porque """ + f"{len(PBAJO)} de los {len(P)}" + r""" ensayos de Antamina quedan por debajo de ella, """ + f"{N_BAJO_LB_06}" + r""" con $\sigma'_n \le 0.6$~MPa; los más alejados son la mezcla triaxial de 6~in de \citet{g2021} a """ + f"{f2(PB.sn)}~MPa ({abs(PB.phis_e065 - LB(PB.sn)):.1f}°" + r""" por debajo) y los cortes directos de la ruma de mármol ROM (hasta """ + f"{abs((PBAJO_MN.phis_e065 - PBAJO_MN.cota).min()):.1f}" + r"""° por debajo). \citet{cylwik} advierten, además, que su base no tiene rocas con resistencia a la compresión menor que 25~MPa y que materiales más débiles pueden quedar bajo sus predicciones.

\textbf{A grandes esfuerzos.} Sobre """ + f2(SNX) + r"""~MPa la curva no tiene ensayos de Antamina, así que conviene contrastarla con los ensayos más altos disponibles, cada uno con la curva evaluada a su propia $e$. Entre """ + f2(SNX) + r""" y """ + f2(SNW) + r"""~MPa, """ + f"{A25['ensayos'][_W]['n'] - A25['ensayos'][_W]['bajo_curva']} de los {A25['ensayos'][_W]['n']}" + r""" ensayos de la base mundial quedan sobre la curva, con una mediana de """ + sg(A25['ensayos'][_W]['dphi_mediana']) + r"""° en $\phi'_s$, y de los """ + f"{A25['ensayos'][_A]['n']}" + r""" ensayos de Antamina con $\sigma'_n$ sobre 3~MPa, """ + f"{A25['ensayos'][_A]['n'] - A25['ensayos'][_A]['bajo_curva']}" + r""" quedan sobre ella (mediana """ + sg(A25['ensayos'][_A]['dphi_mediana']) + r"""°): sobre 3~MPa la curva queda bajo la mayoría de los ensayos disponibles. Los ensayos mundiales de ese rango son sobre todo de roca de calidad buena y moderada, y solo """ + f"{CLW['low'][0]}" + r""" de calidad baja. A 10~MPa da """ + f"{phis(10, OP2['pe0'], MC):.1f}" + r"""°, sobre la cota de \citet{indraratna1993} (""" + f"{LB(10):.1f}" + r"""°) y la de \citet{hc2017} (""" + f"{HC(10):.1f}" + r"""°), y bajo los 33° que el DDE usó como sensibilidad entre 5 y 10~MPa de esfuerzo vertical efectivo, con 30° por encima \citep[§3.5.3.6, Tabla~3-24, nota~4]{stantec2026iff}; en la base de una dovela, $\sigma'_n \le \sigma'_v$.

El exponente $m = """ + f"{MC:.2f}" + r"""$ es el de residuo mediano nulo en los ensayos mundiales de mayor esfuerzo (sección~\ref{sec:alto}), algo menor que el valor estándar del modelo simplificado (0.9). Las hipótesis de curvatura, incluida $m = 1$, están en la Tabla~\ref{tab:hip}.

\textbf{Posición frente a \citet{leps}.} Las envolventes de \citet{leps}, en la forma de Leps 2.0 ($\phi'_1$ = 36°, 41° y 46° con $m = 0.9$; \citealp[p.~2]{cylwik}), no dependen de $e$: la densidad está en la clase (baja densidad, promedio, alta densidad). Por eso la posición de la curva propuesta frente a ellas depende de la $e$ con que se la evalúe. Con $e = 0.45$ constante, la curva cruza la envolvente media a """ + f2(X_MED) + r"""~MPa, queda entre la media y la inferior sobre ese esfuerzo y alcanza la inferior a unos """ + f1(X_INF) + r"""~MPa, porque su $m$ es menor que 0.9. Con la $e$ del perfil A, que baja con la profundidad (sección~\ref{sec:e}), la curva sigue a la envolvente media: en una escala en que 0 es la envolvente inferior y 1 la media, su posición es """ + ", ".join(f"{v_:.2f}" for v_ in POS_A) + r""" a 1, 4, 10 y 15~MPa. Para comparar con \citet{leps}, la $e$ de colocación pesa tanto como la curva misma.

\subsection*{Comportamiento a bajo confinamiento}
La curva se entrega con un tope de """ + f"{TOPE:.0f}" + r"""° en el ángulo secante, que gobierna bajo $\sigma'_n$ = """ + f"{s_tope(OP2['pe0']):.2f}" + r"""~MPa con $e = 0.45$ (""" + f"{s_tope(OP2['pe0'], EV):.2f}" + r"""~MPa con $e = """ + f"{EV:.2f}" + r"""$); los pares de las Tablas~\ref{tab:slide} y~\ref{tab:slide_e} lo incluyen. Con $m < 1$, el ángulo secante de Leps 2.0 crece al bajar $\sigma'_n$ y supera el ángulo de reposo de las caras de volteo de Antamina (típicamente 37° en caras de volteo; \citealp[§16.5]{hc2017}) bajo $\sigma'_n$ = """ + f"{s_cruce(OP2['pe0']):.2f}" + r"""~MPa con $e = 0.45$. \citet{cylwik} indican que bajo 0.1~MPa el criterio tiende a subestimar la resistencia medida. Para el desmonte suelto de la cara, en cambio, la resistencia movilizable está cerca del ángulo de reposo. Con $\sigma'_n$ menor que 0.5~MPa hay """ + f"{len(LOWP)}" + r""" ensayos: la mezcla triaxial de \citet{g2021} (6~in, $\sigma'_3 = """ + f2(ROWB.s3) + r"""$~MPa, máximo desviador con """ + f1(ROWB.eps_axial_falla_pct) + r"""~\% de deformación axial) y los cortes directos a 0.3~MPa. Llevados a $e = 0.45$, sus ángulos van de """ + f"{LOWP.phis_e065.min():.1f}° a {LOWP.phis_e065.max():.1f}°" + r""", frente a unos """ + f"{LOWP.curva.mean():.0f}" + r"""° de la curva: """ + f"{int((LOWP.dif < 0).sum())} quedan bajo la curva y {int((LOWP.dif >= 0).sum())} sobre ella" + r""". A bajo confinamiento los ensayos son pocos y muy dispersos, y no respaldan la curva sin tope: a 0.3~MPa daría """ + f"{phis(0.3, OP2['pe0'], MC):.1f}" + r"""°, y """ + f"{int((LOWP.dif < 0).sum())}" + r""" de los """ + f"{len(LOWP)}" + r""" ensayos quedan bajo ese valor. El tope de """ + f"{TOPE:.0f}" + r"""° deja la curva cerca de la mediana de esos ensayos sin bajar del ángulo de reposo.

Además, los mecanismos de cara y de banco, con $\sigma'_n$ menor que el cruce con 37° (""" + f"{s_cruce(OP2['pe0']):.1f}" + r"""~MPa), se verifican además con $\phi' = 37°$. \citet[§8.4.1.1]{hc2017} indican que el peligro de inestabilidad superficial de las caras a ángulo de reposo se maneja normalmente con procedimientos operacionales, y que analizarlo no suele aportar, porque su factor de seguridad es 1 por definición. Por eso la verificación con 37° tiene sentido en caras y bancos más tendidos que el ángulo de reposo.

\section{Valores para los modelos de equilibrio límite}\label{sec:valores}
La Tabla~\ref{tab:slide} da los pares $\sigma'_n$--$\tau$ de la curva propuesta a $e = 0.45$ y de los límites de su incertidumbre, y la Tabla~\ref{tab:slide_e}, los de la curva propuesta para cada supuesto de $e$. Ambas incluyen el origen y puntos desde 10~kPa, para definir la curva cerca del origen. Las curvas con $e$ constante también pueden cargarse como función de potencia (\emph{Power Curve} de Slide2, $\tau = a(\sigma'_n + d)^b + c$), con los parámetros de la Tabla~\ref{tab:power}. Los perfiles $e(z)$ no son una función de potencia y se cargan como pares. La Fig.~\ref{fig:tau} compara la curva propuesta con las envolventes de \citet{leps} y la cota inferior de \citet{indraratna1993}.

\begin{table}[htbp]\centering\small\caption{Pares $\sigma'_n$--$\tau$ a $e = 0.45$: curva propuesta y límites de su incertidumbre.}\label{tab:slide}
\begin{tabular}{rrrrr}\toprule $\sigma'_n$ & $\tau$ curva propuesta & $\tau$ límite inferior$^{b}$ & $\tau$ límite superior$^{b}$ & $\phi'_s$ curva propuesta\\
(kPa) & (kPa) & (kPa) & (kPa) & (°)\\\midrule
""" + "\n".join(filas_t4) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{a}$Sobre el máximo $\sigma'_n$ de los ensayos de Antamina (""" + f2(SNX) + r"""~MPa). $^{w}$Sobre el máximo de la base mundial de Leps 2.0 (""" + f2(SNW) + r"""~MPa): extrapolación fuera de toda la data (sección~\ref{sec:rango}). $^{b}$Límites de la banda de incertidumbre de la curva media (sección~\ref{sec:alto}). $^{t}$Con el tope de """ + f"{TOPE:.0f}" + r"""° en el ángulo secante (sección~\ref{sec:curva}); bajo 0.5~MPa hay pocos ensayos y muy dispersos.\end{table}

\begin{table}[htbp]\centering\small\caption{Pares $\sigma'_n$--$\tau$ (kPa) de la curva propuesta según la relación de vacíos y de la recta de 37° para verificar caras y bancos.}\label{tab:slide_e}
\setlength{\tabcolsep}{4pt}\begin{tabular}{rrrrrrr}\toprule $\sigma'_n$ & $e = 0.45$ & $e = 0.55$ & $e = 0.65$ & Perfil A & Perfil V & $\phi' = 37°$\\
(kPa) & (base) & & & & & \\\midrule
""" + "\n".join(filas_t5) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{a}$Sobre el máximo $\sigma'_n$ de los ensayos de Antamina (""" + f2(SNX) + r"""~MPa). $^{w}$Sobre el máximo de la base mundial (""" + f2(SNW) + r"""~MPa): extrapolación fuera de toda la data. Perfil V: sin valores sobre $\sigma'_v \approx """ + f"{max(s for s, e_ in zip(PE['sv_V'], PE['e_V']) if e_ is not None):.1f}" + r"""$~MPa, donde termina la curva de Valenzuela et al.\ (600~m de altura). Todas las columnas de Leps 2.0 incluyen el tope de """ + f"{TOPE:.0f}" + r"""°. La columna $e = """ + f"{EV:.2f}" + r"""$ es la verificación del diseño (sección~\ref{sec:e}); los perfiles A y V son sensibilidades y no se usan en el diseño, porque $m$ ya incluye la densificación por carga.\end{table}

\begin{table}[htbp]\centering\small\caption{Parámetros de \emph{Power Curve} de Slide2 ($\tau = a(\sigma'_n + d)^b + c$, con $\sigma'_n$ y $\tau$ en kPa), equivalentes a Leps 2.0 con $e$ constante: $a = \tan\phi'_1 \cdot 1013^{1-m}$, $b = m$. La función no incluye el tope de """ + f"{TOPE:.0f}" + r"""°: para aplicarlo se usan los pares de las Tablas~\ref{tab:slide} y~\ref{tab:slide_e}.}\label{tab:power}
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
La $e$ in situ del ROM no se ha medido directamente, pero los pesos unitarios que miden y adoptan los estudios de Antamina permiten calcularla (Tabla~\ref{tab:ebase}). Para el ROM dan $e$ de 0.25 a 0.45, con el valor más bajo medido en la superficie de un botadero; la literatura da 0.25 a 0.9, con 0.45 a 0.49 en botaderos altos de volteo. El valor base, """ + EB_TXT + r""", está en el extremo suelto del rango de Antamina y en el de la literatura, y es el valor central adoptado. Los pesos unitarios con que se calculó incluyen la densificación por carga y por tránsito de los botaderos en operación, y \citet{hc2017} dan $e$ de 0.4 a 0.9 para material volteado, de modo que la $e$ de volteo puede ser mayor. Por eso el diseño se verifica también con $e = """ + f"{EV:.2f}" + r"""$ (Tabla~\ref{tab:slide_e}), hasta contar con densidad in situ del desmonte volteado. El chancado y el enrocado dan $e$ de 0.25 a 0.28, claramente más densos; por eso los ensayos de enrocado compactado ($e_0$ de 0.30 a 0.34) se llevan a la $e$ del ROM con la regla de densidad de Leps 2.0 antes de ajustar la curva. El valor base está dentro del rango de los ensayos ($e_0$ = """ + f"{P.e.min():.3f}" + r"""--""" + f"{P.e.max():.3f}" + r"""), así que esa corrección no extrapola la regla. Con 0.65, más suelto que toda la evidencia y que la categoría «suelta» de Leps 2.0, la curva representaría el material más suelto de la cara de volteo; 0.65 se entrega como sensibilidad conservadora.

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
$e = 0.45$ no medida (cada 0.05 de $e$ cambia $\phi'_1$ en 1°) & Coherente con el $\gamma$ del DDE y con la literatura (Tabla~\ref{tab:ebase}); verificación con $e = 0.55$ (Tablas~\ref{tab:hip} y~\ref{tab:slide_e}); alternativa 0.65 y perfiles $e(z)$ & Densidad in situ (ítem~1)\\
Mármol, la litología ensayada más débil: un set triaxial de gran escala (enrocado de presa, 3 de 5 ensayos con carga y descarga), uno de 6~in y un corte directo ROM & Curva de un solo material, como el DDE; no cubre sectores con predominio de mármol & Triaxiales de mármol ROM (ítem~2)\\
Composición de LE2: caliza y margas, 30~\% en masa, sin ensayos de resistencia; mármol 38~\% & Sensibilidad de nivel: composición de LE2 y mármol solo (Tabla~\ref{tab:hip}) & Triaxiales de caliza y margas ROM\\
""" + f"{n_contr_seg} de {n_eps}" + r""" triaxiales con contracción volumétrica en el máximo desviador (""" + f"{n_contr}" + r""" si se cuentan los de signo dudoso) & Del lado conservador: el máximo desviador puede subestimar la resistencia última & Ensayos hasta 25~\% de deformación (ítem~2)\\
Curvatura sobre """ + f2(SNX) + r"""~MPa & Hipótesis P10--P90 en la banda; sensibilidad con $m = """ + f"{RM['m_P10_sets']:.2f}" + r"""$ & Triaxiales a alta presión (ítem~4)\\
Segregación por volteo & No cubierta: curva de un solo material, como el DDE & Modelo de bloques y plan de colocación, si el EoR lo requiere\\
Bajo confinamiento: pocos ensayos y dispersos; la curva sin tope da ángulos altos bajo 1~MPa & Tope de """ + f"{TOPE:.0f}" + r"""° en el ángulo secante y verificación de caras y bancos con 37° & --\\
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
La librería pasa la revisión estática de sintaxis de FLAC2D 9.0, pero no se ha corrido en FLAC: se entrega como prototipo sin verificar, y sus resultados no deben usarse antes de las tres comprobaciones anteriores. Tampoco aplica el tope de """ + f"{TOPE:.0f}" + r"""° (sección~\ref{sec:curva}); en las zonas con $\sigma'_n$ menor que """ + f"{s_tope(OP2['pe0']):.2f}" + r"""~MPa hay que limitar el ángulo de fricción a ese valor, sin cohesión.

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

# ---- Anexo B: caracterización por tipo de desmonte, con los valores de cada informe tal como fueron informados
#      (verificados en la página, lámina o planilla citada; 2026-10-13)
TB = lambda rows: "\n".join(" & ".join(r) + r" \\" for r in rows)
TBG = lambda grupos, nc: "\n".join((r"\midrule " if i else "") + r"\multicolumn{" + str(nc) + r"}{l}{\textit{" + g + r"}} \\" + "\n" + TB(rr) for i, (g, rr) in enumerate(grupos))
B_G10GRAN = [
    ("Fase A, material del tajo", [
        ("Mármol negro", "35", "35.1", "30.2", "23.6", "8.3", "2.8", "71.4", "22.8", "5.8", "2.185", "2.2", "2.135"),
        ("Hornfels gris", "35", "22.1", "49.3", "24.9", "2.82", "0.88", "86.2", "11.2", "2.6", "2.055", "2.4", "2.026"),
        ("Intrusivo", "30", "21.8", "38.8", "31.4", "6.4", "1.6", "80.4", "16.3", "3.3", "1.931", "3.8", "1.865"),
        ("Exoskarn diópsido", "19", "4.6", "15.6", "58", "19.1", "2.7", "76.5", "20.9", "2.6", "2.35", "3.1", "2.273")]),
    ("Fase B, material chancado", [
        ("Mármol negro", "35$^{a}$", "--", "34", "43.4", "15.4", "7.2", "68.9", "23.6", "7.5", "2.2", "2.9", "2.151"),
        ("Hornfels gris", "35$^{a}$", "--", "35.6", "56.3", "5.4", "2.7", "85.6", "10.8", "3.6", "2.162", "2.3", "2.137"),
        ("Intrusivo", "30$^{a}$", "--", "34.7", "40.7", "17.6", "7", "67.4", "25.4", "7.2", "2.06", "2.7", "2.019"),
        ("Exoskarn diópsido", "19$^{a}$", "--", "10.7", "60.9", "23", "5.4", "72.5", "23.1", "4.4", "2.418", "3", "2.357")]),
]
B_G10IND = [
    ("Fase A, material del tajo", [
        ("Mármol negro", "2.763", "2.717", "0.34", "43.4", "62.1", "32.24", "44.7 (41.0; 48.3)", "--", "--"),
        ("Hornfels gris", "2.791", "2.737", "0.24", "0.7", "23.7", "72.99", "49.2 (46.8; 51.6)", r"$3.20\times10^{-6}$", "--"),
        ("Intrusivo", "2.674", "2.461", "1.66", "33.4", "49.8", "80.56", "46.8 (48.4; 45.1)", r"$2.50\times10^{-6}$", "--"),
        ("Exoskarn diópsido", "3.484", "3.212", "1.44", "5.9", "37", "67.79", "73.3 (79.3; 67.3)", "--", "--")]),
    ("Fase B, material chancado", [
        ("Mármol negro", "2.747", "2.725", "0.33", "49.8", "62.4", "24.56", "49.6 (41.5; 57.7)", "--", "4.8"),
        ("Hornfels gris", "2.802", "2.740", "0.12", "0.6", "20.3", "100.42", "65.5 (62.6; 68.3)", r"$2.60\times10^{-6}$$^{c}$", "5.6"),
        ("Intrusivo", "2.742", "2.647", "2.17", "18.6", "32.2", "78.06", "54 (56.1; 51.8)", r"$2.20\times10^{-6}$$^{c}$", "3.6"),
        ("Exoskarn diópsido", "3.338", "3.102", "1.30", "6.7", "27.6", "124.78", "97.4 (101.7; 93.1)", "--", "5.1")]),
]
B_GRAN = [
    (r"\citet{anddes2024}: muestras de perforación, patio de servicios y Botadero Este, 40--90~m", [
        ("Ruma 01 (M-1 a M-13)", "Mármol", "75~mm", "65", "25", "10", "GP-GM", "NP / NP", "23.780 (25.754)", "6.8 (3.9)", "3"),
        ("Ruma 02 (H-1 a H-12)", "Hornfels", "75~mm", "68", "21", "11", "GP-GM", "16 / NP", "22.876 (24.533)", "7.7 (4.7)", "3"),
        ("Ruma 03 (I-1 a I-12)", "Intrusivo", "75~mm", "63", "29", "8", "GP-GM", "17 / NP", "20.930 (22.230)", "9.8 (6.7)", "5"),
        ("Pila 01", "Mármol y hornfels", "75~mm", "59", "30", "11", "GP-GM", "NP / NP", "22.819 (24.012)", "7.4 (5.4)", "3"),
        ("Pila 02", "Intrusivo", "75~mm", "57", "34", "9", "GW-GM", "NP / NP", "19.951 (20.797)", "11.1 (8.6)", "6")]),
    (r"\citet[Tablas~4 y~6, p.~14]{g2021}: muestras truncadas en 1~in", [
        ("Tipo A", "Intrusivo", r"$D_{50}$ 3.6~mm", "45.3", "41.2", "13.5$^{e}$", "GM", "NP", "--", "--", "--"),
        ("Tipo B", "Mármol y hornfels", r"$D_{50}$ 3.9~mm", "46.2", "40.9", "12.9$^{e}$", "GM", "NP", "--", "--", "--"),
        ("Tipo C", "Hornfels", r"$D_{50}$ 9.5~mm", "68.2", "24.6", "7.2$^{e}$", "GM$^{h}$", "NP", "--", "--", "--"),
        (r"Compuesto (35/15/50~\%)", "Intrusivo, mármol--hornfels y hornfels", r"$D_{50}$ 7.4~mm", "59.5", "30.8", "9.7$^{f}$", "GP-GM", "NP", "22.7", "6.5", "--")]),
    ("Granulometría de terreno y de probeta", [
        (r"M-001 \citep[p.~47]{w2022}", "Hornfels", "36~in", "--", "--", "2.49", "GW-GM$^{g}$", "NP", "--", "--", "--"),
        (r"M-001 \citep[p.~52]{w2022}", "Mármol", "36~in", "--", "--", "4.07", "GP-GM$^{g}$", "--", "--", "--", "--"),
        (r"Desmonte de mina \citep[p.~93]{w2024}", "Intrusivo", "10~in", "--", "--", "6.6", "--", "--", "--", "--", "--"),
        (r"Probeta de 1~m \citep[anexo, p.~3]{g2012}", "Mármol", "178~mm", "--", "--", "4.9", "--", "--", "--", "--", "--")]),
]
B_GS = [
    (r"\citet[Tabla~5 y pp.~83--86]{g2021}", [
        ("Tipo A", "Intrusivo", "2.44", "2.53", "2.67", "3.39", "--"),
        ("Tipo B", "Mármol y hornfels", "2.87", "2.90", "2.97", "1.22", "--"),
        ("Tipo C", "Hornfels", "2.70", "2.72", "2.75", "0.61", "--"),
        ("Compuesto", "Mezcla", "2.71", "2.72", "2.75", "0.54", "2.77")]),
    (r"\citet[Tabla~3]{w2024}, desmonte tipo intrusivo", [
        ("M-1", "Intrusivo", "2.79", "2.82", "2.87", "1.0", "--"), ("M-2", "Intrusivo", "2.79", "2.82", "2.87", "1.0", "--"),
        ("M-3", "Intrusivo", "2.80", "2.83", "2.90", "1.2", "--"), ("M-4", "Intrusivo", "2.80", "2.83", "2.87", "0.8", "--"),
        ("M-5", "Intrusivo", "2.75", "2.79", "2.85", "1.3", "--"), ("M-6", "Intrusivo", "2.86", "2.88", "2.93", "0.8", "--"),
        ("M-7", "Intrusivo", "2.71", "2.76", "2.83", "1.6", "--"), ("M-8", "Intrusivo", "2.76", "2.79", "2.84", "1.0", "--")]),
    (r"\citet{anddes2024}, fracción sobretamaño del Proctor", [
        ("Ruma 01", "Mármol", "2.94", "--", "--", "--", "--"), ("Ruma 02", "Hornfels", "2.80", "--", "--", "--", "--"),
        ("Ruma 03", "Intrusivo", "2.56", "--", "--", "--", "--"), ("Pila 01", "Mármol y hornfels", "2.79", "--", "--", "--", "--"),
        ("Pila 02", "Intrusivo", "2.39", "--", "--", "--", "--")]),
]
B_DENS = [
    (r"\citet[pp.~43--47]{g2010}, fracción menor que 5/8~in", [("Exoskarn diópsido, fase A", "2.175", "2.621", "--"), ("Mármol negro, fase B", "1.821", "2.236", "--"),
        ("Hornfels gris, fase B", "1.861", "2.308", "--"), ("Intrusivo, fase B", "1.833", "2.237", "--"), ("Exoskarn diópsido, fase B", "2.161", "2.647", "--")]),
    (r"\citet[pp.~85--86]{w2022}", [("Hornfels (HR)", "1.852", "2.232", "2.308"), ("Mármol (MR)", "1.905", "2.297", "2.398")]),
    (r"\citet[Tabla~8]{w2024}, fracción menor que 3~in", [("Codisposal 4, intrusivo", "1.825", "2.212", "--"),
        ("Codisposal 1, intrusivo y relave 3.5:1", "1.945", "2.169", "--"), ("Codisposal 2, intrusivo y relave 4.5:1", "1.914", "2.158", "--"),
        ("Codisposal 3, intrusivo y relave 5.5:1", "1.865", "2.187", "--")]),
]
B_PART = [
    ("Compresión uniaxial (MPa)", [
        (r"\citet[Tabla~1]{w2022}", "Hornfels gris (M-1 y M-2)", "2", "65; 64"),
        (r"\citet[Tabla~2]{w2022}", "Mármol negro (M-001 y M-002)", "2", "44; 42"),
        (r"\citet[Tabla~2]{w2022}, de \citet{g2012}", "Mármol negro (M1-1 a M4-2)", "8", "53; 108; 106; 129; 54; 61; 136; 132"),
        (r"\citet[anexo IDIEM, pp.~72--77]{w2022}", "H6 hornfels gris", "3", "26.3; 40.8; 24.5"),
        (r"\citet[anexo IDIEM, pp.~78--83]{w2022}", "Mármol (muestra REG~41061)", "3", "96.6; 66.9; 103.5"),
        (r"\citet[Tabla~6]{w2024}", "Intrusivo (M-1 y M-2)", "7", "100.6; 143.1; 64.0; 117.8; 76.0; 103.6; 61.1")]),
    ("Abrasión Los Ángeles (\\% de pérdida)", [
        (r"\citet[pp.~48--55, ASTM C535]{w2022}", "Hornfels (M-001, dos ensayos); mármol (M-001 y M-002)", "4", r"15.5; 17.3; 55.8; 45.2$^{i}$"),
        (r"\citet[p.~17]{g2012}", "Mármol negro", "2", "44; 41"),
        (r"\citet[Tabla~7]{w2024}", r"Intrusivo (M-1 a M-8)$^{j}$", "8", "29.1; 39.9; 21.2; 32.2; 27.1; 32.3; 29.0; 32.6")]),
    ("Carga puntual, $I_{s(50)}$ (MPa)", [
        (r"\citet[Tabla~6 del informe IDIEM 1.914.482-F, p.~364]{w2024}", "Desmonte intrusivo: 4 sets con 31 colpas de tonalita y 7 de caliza", "4", "5.48; 4.36; 4.11; 6.16")]),
]
B_PERM = [
    ("Permeabilidad (m/s salvo indicación)", [
        (r"\citet[Tabla~2 y pp.~157--160]{g2010}", "Hornfels gris, A y B; intrusivo, A y B (fracción < 5/8~in, probeta de 4~in)", r"$\sigma'$ = 20~kPa", r"$3.20\times10^{-6}$; $2.60\times10^{-6}$; $2.50\times10^{-6}$; $2.20\times10^{-6}$$^{c}$"),
        (r"\citet[Tabla~4]{g2012}", "Mármol negro, 0.95~m (cm/s)", "6, 10, 20, 40, 50 y 60~kg/cm²", r"$1.4\times10^{-1}$; $1.1\times10^{-1}$; $1.0\times10^{-1}$; $1.1\times10^{-1}$; $8.6\times10^{-2}$; $8.2\times10^{-2}$"),
        (r"\citet[Tabla~5]{w2022}", "Hornfels, 1.0~m (cm/s)", "588, 981, 1961, 3923, 4903, 5884 y 6865~kPa", r"$3.5\times10^{-2}$; $1.7\times10^{-2}$; $9.7\times10^{-3}$; $6.8\times10^{-3}$; $5.6\times10^{-3}$; $4.2\times10^{-3}$; $3.5\times10^{-3}$"),
        (r"\citet[Tabla~6]{w2022}", "Mármol negro 2021, 1.0~m (cm/s)", "Mismos esfuerzos", r"$1.2\times10^{-2}$; $9.5\times10^{-3}$; $7.7\times10^{-3}$; $5.0\times10^{-3}$; $4.1\times10^{-3}$; $3.0\times10^{-3}$; $2.7\times10^{-3}$"),
        (r"\citet[Tabla~14]{w2024}", "Codisposal 4, intrusivo, 0.6~m$^{j}$", "392, 784, 1568, 3136 y 5880~kPa", r"$2.9\times10^{-4}$; $2.8\times10^{-4}$; $2.3\times10^{-4}$; $2.3\times10^{-4}$; $2.0\times10^{-4}$"),
        (r"\citet[Tabla~14]{w2024}", "Codisposal 1, intrusivo y relave 3.5:1$^{j}$", "Mismos esfuerzos", r"$1.3\times10^{-3}$; $1.0\times10^{-3}$; $8.4\times10^{-4}$; $7.6\times10^{-4}$; $6.6\times10^{-4}$"),
        (r"\citet[Tabla~14]{w2024}", "Codisposal 2, intrusivo y relave 4.5:1$^{j}$", "Mismos esfuerzos", r"$4.7\times10^{-4}$; $3.8\times10^{-4}$; $3.2\times10^{-4}$; $2.7\times10^{-4}$; $2.5\times10^{-4}$"),
        (r"\citet[Tabla~14]{w2024}", "Codisposal 3, intrusivo y relave 5.5:1$^{j}$", "Mismos esfuerzos", r"$7.0\times10^{-4}$; $6.2\times10^{-4}$; $5.8\times10^{-4}$; $4.5\times10^{-4}$; $4.2\times10^{-4}$"),
        (r"\citet[Tabla~9]{g2021}", "Mezclas de desmonte y relave, alternativas 1, 2 y 4, 9:1 y 1:1", "399~kPa", r"$5.60\times10^{-6}$ y $8.90\times10^{-6}$$^{k}$; $8.10\times10^{-6}$ y $1.40\times10^{-6}$; $6.70\times10^{-6}$ y $2.50\times10^{-6}$")]),
    ("Edómetros de mezclas, 0.6~m: $e_0$; $\\rho_d$ (g/cm³); $\\varepsilon_v$ final a 5880~kPa (\\%)", [
        (r"\citet[Tabla~12]{w2024}", "Codisposal 1, 2 y 3 (intrusivo y relave)", "--", "0.418, 2.07, 8.2; 0.431, 2.03, 10.4; 0.408, 2.05, 11.1"),
        (r"\citet[Tabla~12]{w2024}", r"Codisposal 4, intrusivo (también en la Tabla~\ref{tab:edo})", "--", "0.425, 2.00, 17.4")]),
    ("Carga directa en plataforma de material chancado (asentamiento máximo, cm)", [
        (r"\citet[Tabla~2 y pp.~185--226]{g2010}", "Mármol negro; hornfels gris; intrusivo; exoskarn diópsido", "Hasta 6.0~kg/cm², placas de 0.30, 0.45 y 0.60~m", "4.8; 5.6; 3.6; 5.1")]),
]
B_RMU = [
    ("END", "Promedio", "39.3", "2.8", "3.9", "4.2", "30.7", "0.3", "60.7", "78.0", "2.6"), ("", "P50", "28.1", "2.0", "2.6", "3.4", "31.4", "0.1", "65.0", "98.2", "0.4"), ("", "P35", "22.0", "1.5", "1.7", "2.4", "27.9", "0.0", "58.0", "85.7", "0.3"),
    ("EXO", "Promedio", "72.7", "5.1", "6.5", "7.7", "33.8", "0.4", "62.5", "81.6", "1.8"), ("", "P50", "66.7", "4.7", "5.9", "7.2", "31.6", "0.1", "66.5", "100.0", "0.5"), ("", "P35", "49.6", "3.4", "4.6", "6.0", "29.7", "0.0", "60.0", "93.3", "0.3"),
    ("HRN", "Promedio", "96.8", "5.4", "5.6", "9.8", "29.1", "0.4", "69.2", "96.5", "1.2"), ("", "P50", "75.2", "4.9", "5.0", "9.7", "28.2", "0.0", "72.0", "100.0", "0.7"), ("", "P35", "58.2", "4.3", "4.3", "8.7", "27.4", "0.0", "67.0", "100.0", "0.3"),
    ("INT", "Promedio", "57.7", "4.0", "5.7", "7.4", "31.1", "0.5", "67.9", "91.7", "1.3"), ("", "P50", "50.6", "3.5", "4.9", "7.3", "33.4", "0.1", "71.0", "100.0", "0.3"), ("", "P35", "39.5", "2.1", "3.7", "5.9", "30.3", "0.0", "65.0", "100.0", "0.0"),
    ("LMH", "Promedio", "68.0", "3.7", "3.8", "6.6", "31.0", "0.2", "68.3", "96.0", "0.9"), ("", "P50", "56.3", "3.5", "3.5", "6.4", "28.7", "0.1", "70.0", "100.0", "0.6"), ("", "P35", "44.3", "2.8", "2.9", "5.5", "28.0", "0.1", "65.0", "100.0", "0.3"),
    ("XDP", "Promedio", "98.7", "7.3", "7.8", "8.9", "33.7", "0.2", "67.0", "91.7", "0.9"), ("", "P50", "98.0", "6.8", "7.2", "8.5", "32.6", "0.0", "68.0", "100.0", "0.6"), ("", "P35", "2021.0$^{l}$", "4.9", "5.7", "7.1", "27.7", "0.0", "64.0", "97.5", "0.3"),
]
B_MR = [  # lámina 12 (n, media, desviación, mínimo, P25, P50, P75, máximo); densidad media y fracción en masa recalculadas del modelo
    ("Intrusivo", "1", "46\\,813", "63.27", "14.16", "16.81", "54.08", "63.18", "71.39", "153.34", "2.46", "13.9", "15.8"),
    ("Intrus-Estruct-Tab", "2", "3137", "104.47", "19.33", "46.51", "92.40", "103.30", "113.28", "196.41", "2.69", "1.0", "1.1"),
    ("Caliza", "10", "24\\,434", "81.32", "5.50", "51.35", "77.37", "82.54", "82.97", "123.98", "2.71", "8.0", "8.9"),
    ("Margas-Limonitas", "11", "58\\,104", "70.03", "7.89", "28.10", "68.32", "69.24", "72.17", "121.52", "2.71", "18.9", "20.7"),
    ("Hornfels", "13", "48\\,510", "105.85", "16.57", "28.85", "97.20", "104.93", "115.31", "200.24", "2.71", "15.8", "13.3"),
    ("Hornfels diópsida", "14", "9983", "116.96", "18.00", "57.13", "105.91", "114.95", "130.48", "225.95", "2.86", "3.4", "2.2"),
    ("Mármol", "16", "110\\,698", "74.03", "13.87", "26.58", "65.84", "74.14", "80.91", "174.86", "2.71", "36.1", "35.8"),
    ("Mármol diópsida", "19", "8020", "94.91", "11.10", "39.93", "89.48", "94.66", "102.08", "153.71", "2.85", "2.7", "2.0"),
    ("Brechas-Intrus", "53", "403", "57.37", "7.06", "40.11", "53.27", "56.68", "60.86", "96.93", "2.66", "0.1", "0.1"),
]
B_WSC = [
    ("Waste-C/Std", "54", "12.6", "36.50", "--", "39.4", "0.0261", "43.9"),
    ("Waste-Fine", "83", "17.1", "28.72", "--", "50.0", "0.0202", "35.6"),
    ("Waste-Hard", "155", "16.0", "25.02", "--", "778.0", "0.4810", "38.8"),
]
B_FRAG = [  # recalculado de la planilla (clasificación «Desmonte»); percentiles con interpolación lineal
    ("A", "147", "8, 9 y 10", "10.1", "23.4", "86.0", "48.4--127.7"),
    ("B", "30", "9 y 10", "11.45", "27.0", "91.9", "65.9--149.9"),
    ("C", "115", "9 y 10", "10.0", "24.5", "86.1", "60.9--141.1"),
    ("C1", "27", "9 y 10", "7.7", "18.1", "66.7", "49.7--98.1"),
    (r"\midrule Todas", "319", "8, 9 y 10", "9.8", "23.4", "85.3", "54.1--134.0"),
]
ANXB = r"""
\clearpage
\renewcommand{\thetable}{B\arabic{table}}\setcounter{table}{0}
\section{Caracterización por tipo de desmonte}\label{sec:anexob}
Este anexo da, para cada tipo de desmonte (litología, clase de desmonte de Antamina o unidad geotécnica), los valores de caracterización disponibles, con la tabla, página o lámina de origen. Los valores son los informados por cada fuente, verificados en la página del informe, la lámina o la planilla, sin recalcular; las excepciones, que Stantec calculó a partir de la base de origen, se indican en la nota de cada tabla. Los ensayos de resistencia del desmonte están en el Anexo~\ref{sec:anexo} y los edómetros, en la Tabla~\ref{tab:edo}. El orden es: granulometría, densidad e índices de \citet{g2010} por litología y fase (Tablas~\ref{tab:b_g10gran} y~\ref{tab:b_g10ind}); granulometría, clasificación y compactación de las demás fuentes (Tabla~\ref{tab:b_gran}); peso específico y absorción (Tabla~\ref{tab:b_gs}); densidades mínima y máxima (Tabla~\ref{tab:b_dens}); resistencia de partículas (Tabla~\ref{tab:b_part}); permeabilidad, edómetros de mezclas y carga en plataforma (Tabla~\ref{tab:b_perm}); roca por unidad geotécnica (Tabla~\ref{tab:b_rmu}); modelo de bloques por litología (Tabla~\ref{tab:b_mr}); caracterización para chancado (Tabla~\ref{tab:b_wsc}); y fragmentación por clase de desmonte (Tabla~\ref{tab:b_frag}).

Las clases A, B y C de Antamina son una clasificación geoquímica por potencial de generación de acidez \citep[pp.~6 y~27]{g2021}. Las muestras de tipo A, B y C de \citet{g2021} fueron de intrusivo, de mármol y hornfels, y de hornfels, respectivamente; esa correspondencia describe esas muestras, no la definición de las clases. La planilla de fragmentación \citep{antamina2025frag} usa las letras A, B, C y C1 sin definirlas.

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{2.5pt}\caption{Granulometría de terreno, densidad in situ y humedad natural por litología y fase \citep[Tabla~2]{g2010}. Porcentajes en masa de la muestra global y de la matriz menor que 3~in.}\label{tab:b_g10gran}
\begin{tabular}{L{2.4cm}rrrrrrrrrrrr}\toprule
 & & \multicolumn{5}{c}{Muestra global (\%)} & \multicolumn{3}{c}{Matriz (\%)} & $\gamma$ in situ & $w$ & $\gamma_d$\\\cmidrule(lr){3-7}\cmidrule(lr){8-10}
Litología & TM (in) & 12--36~in & 3--12~in & Grava & Arena & Finos & Grava & Arena & Finos & (g/cm³) & (\%) & (g/cm³)\\\midrule
""" + TBG(B_G10GRAN, 13) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{a}$TM repetido de la fase A en la Tabla~2 del informe; la Tabla~1 indica 12~in después del chancado. Densidad in situ por reemplazo de agua (pp.~35--42).\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{2.5pt}\caption{Peso específico, absorción, degradabilidad, resistencia, permeabilidad y carga en plataforma por litología y fase \citep{g2010}.}\label{tab:b_g10ind}
\begin{tabular}{L{1.9cm}>{\centering\arraybackslash}p{1.25cm}>{\centering\arraybackslash}p{1.25cm}>{\centering\arraybackslash}p{1.25cm}>{\centering\arraybackslash}p{1.25cm}>{\centering\arraybackslash}p{1.25cm}>{\centering\arraybackslash}p{1.25cm}L{2.1cm}>{\centering\arraybackslash}p{1.75cm}>{\centering\arraybackslash}p{1.2cm}}\toprule
Litología & $G_s$ fino (D854) & $G_s$ bulk (C127)$^{b}$ & \hspace{0pt}Absorción (\%) & \hspace{0pt}Durabilidad (\%)$^{d}$ & Los Ángeles (\%) & $\sigma_c$ carga puntual (MPa) & UCS promedio (probetas) (MPa) & $k$ (m/s) & \hspace{0pt}Asentamiento máximo (cm)\\\midrule
""" + TBG(B_G10IND, 10) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize Fuentes: Tabla~2 (p.~8), hojas de C127 (p.~48), compresión uniaxial (pp.~66--73), carga puntual (pp.~74--81, 4 probetas por litología en la fase A y 8 en la B), permeabilidad en pared flexible con fracción menor que 5/8~in (pp.~157--160) y carga directa en plataformas con placas de hasta 0.60~m y 6.0~kg/cm² (pp.~185--226). $^{b}$Hojas de laboratorio; en la fase A, la Tabla~2 del informe da 2.696, 2.733, 2.451 y 3.172. $^{c}$La Tabla~2 rotula la fase B en cm/s; las hojas de laboratorio dan m/s. $^{d}$Sulfato de magnesio según las hojas; el texto del informe indica sulfato de sodio.\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{2.5pt}\caption{Granulometría, clasificación, límites, Proctor estándar y humedad natural por muestra. Entre paréntesis, Proctor corregido por sobretamaño.}\label{tab:b_gran}
\begin{tabular}{L{2.8cm}L{1.8cm}L{1.3cm}rrrlL{1.35cm}rrr}\toprule
 & & TM o & Grava & Arena & Finos & SUCS & LL / IP & $\gamma_{d,max}$ & $w_{opt}$ & $w$\\
Muestra & Litología & $D_{50}$ & (\%) & (\%) & (\%) & & & (kN/m³) & (\%) & (\%)\\\midrule
""" + TBG(B_GRAN, 11) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize \citet{anddes2024}: ASTM D6913, D2487 y D698 (informes marcados «fuera de método») y contenido de agua. $^{e}$Pasante del tamiz N.º~200, limo y arcilla (sin hidrómetro). $^{f}$9.2~\% de limo y 0.5~\% de arcilla. $^{g}$Calculada por el laboratorio con el material menor que 3~in; en esa fracción, 5.7~\% de finos en el hornfels y 7.0~\% en el mármol. $^{h}$La hoja de límites (p.~60) clasifica el tipo C como GP-GM. Límites de \citet{g2021}: pp.~58--60.\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\caption{Peso específico y absorción por muestra.}\label{tab:b_gs}
\begin{tabular}{L{2.4cm}L{2.4cm}rrrrr}\toprule
Muestra & Litología & $G_s$ bulk o base seca & $G_s$ SSS & $G_s$ aparente & Absorción (\%) & $G_s$ de finos\\\midrule
""" + TBG(B_GS, 7) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize ASTM C127 en el grueso y D854 en los finos. Las muestras de \citet{g2010} están en la Tabla~\ref{tab:b_g10ind}.\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\caption{Densidades mínima y máxima (ASTM D4254 y D4253), en g/cm³.}\label{tab:b_dens}
\begin{tabular}{L{6.0cm}rrr}\toprule
Material & Mínima & Máxima (seca) & Máxima (húmeda)\\\midrule
""" + TBG(B_DENS, 4) + r"""
\bottomrule\end{tabular}\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\caption{Resistencia de partículas: valores individuales informados.}\label{tab:b_part}
\begin{tabular}{L{4.2cm}L{3.6cm}rL{5.4cm}}\toprule
Fuente & Material & $n$ & Valores\\\midrule
""" + TBG(B_PART, 4) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize $^{i}$El texto del informe (p.~38) resume 17~\% para el hornfels y 43~\% (2011) y 45--50~\% (2021) para el mármol. $^{j}$Las fichas indican ASTM C535; el texto, C131. Las de \citet{g2010} están en la Tabla~\ref{tab:b_g10ind}. En \citet{w2024}, el texto da UCS de 64.0 a 143.1~MPa, pero la Tabla~6 incluye una probeta de 61.1~MPa.\end{table}

\begin{footnotesize}\setlength{\tabcolsep}{3pt}
\begin{longtable}{L{3.0cm}L{3.6cm}L{2.6cm}L{6.0cm}}
\caption{Permeabilidad por nivel de esfuerzo, edómetros de mezclas y carga directa en plataforma.}\label{tab:b_perm}\\
\toprule Fuente & Material & Esfuerzo & Valores\\\midrule\endfirsthead
\toprule Fuente & Material & Esfuerzo & Valores\\\midrule\endhead
""" + TBG(B_PERM, 4) + r"""
\bottomrule
\end{longtable}\end{footnotesize}
\vspace{-6pt}{\footnotesize $^{j}$El informe no los considera indicativos de la permeabilidad del material: la conductividad del equipo es del orden de $10^{-4}$~m/s y el flujo pudo ir por las paredes del molde. Los ensayos de 1.0~m de \citet{w2022} dan para el mármol de 2011 una permeabilidad de uno a dos órdenes de magnitud mayor que la del mármol de 2021 (p.~37). $^{k}$Tabla~9; la hoja de laboratorio da $8.9\times10^{-7}$~m/s.\par}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\caption{Parámetros de roca por unidad geotécnica (RMU) del tajo LE2 \citep[lámina~4 y planilla]{antamina2025le2}.}\label{tab:b_rmu}
\begin{tabular}{llrrrrrrrrr}\toprule
 & & UCS & $I_{s(50)}$ axial & $I_{s(50)}$ diam. & Tracción & \multicolumn{2}{c}{Corte directo} & & & \\\cmidrule(lr){7-8}
RMU & Estadístico & (MPa) & (MPa) & (MPa) & (MPa) & $\phi$ (°) & $c$ (MPa) & RMR & RQD & FF\\\midrule
""" + TB(B_RMU) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize Ensayos de 1997 a 2024: 2470 de UCS, 4657 de carga puntual axial, 13\,971 de carga puntual diametral, 1872 de tracción y 890 de corte directo; RMR, RQD y FF de 42\,500 tramos de logueo. Según la fuente, LMH corresponde a «calizas desmonte (limestone hornfels)» y XDP, a «exoskarn mayor desmonte» \citep[lámina~12]{antamina2025wsc}. UCS por unidad: END 312, EXO 309, HRN 275, INT 379, LMH 1111 y XDP 78 ensayos. Corte directo: 890 registros (261 combinaciones distintas); la planilla no indica si es sobre discontinuidades. La fuente incluye solo ensayos desde la configuración del plan minero 2036 hacia abajo (lámina~2). $^{l}$Valor de la fuente: la fórmula de la planilla toma una columna errada. El percentil 35 de los 78 UCS de XDP de la planilla, calculado por Stantec, es 70.8~MPa.\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{2.5pt}\caption{UCS y densidad del modelo de bloques del desmonte del LOM25 (2025--2049, LE1 y LE2) por litología, y fracción en masa en LE2 (2035--2049). UCS: \citet[lámina~12]{antamina2025wsc}; densidad y fracciones: \citet{antamina2024mr}.}\label{tab:b_mr}
\begin{tabular}{L{2.2cm}rrrrrrrrrrrr}\toprule
 & & & \multicolumn{7}{c}{UCS del modelo (MPa)} & Densidad & \multicolumn{2}{c}{Fracción en masa (\%)}\\\cmidrule(lr){4-10}\cmidrule(lr){12-13}
Litología & RT & Bloques & Media & Desv. & Mín. & P25 & P50 & P75 & Máx. & (t/m³) & LOM25 & LE2\\\midrule
""" + TB(B_MR) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize Los valores son del modelo, no ensayos. UCS según la lámina~12, con los 310\,102 bloques del desmonte del LOM25 (2025--2049, LE1 y LE2). La densidad media y las fracciones en masa las calculó Stantec del modelo, suponiendo bloques de igual volumen; LE2 corresponde a los 175\,437 bloques con período de desmonte de 2035 en adelante, como en la lámina~7. Nombres de litología del modelo: Horfels, Horfel Diopsida, Marmol y Marmol Diopsida. La correspondencia entre el código RT y la litología coincide con el número de bloques de la lámina.\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\caption{Caracterización del desmonte para chancado \citep[lámina~2]{antamina2025wsc}.}\label{tab:b_wsc}
\begin{tabular}{l>{\centering\arraybackslash}p{1.8cm}>{\centering\arraybackslash}p{1.8cm}>{\centering\arraybackslash}p{1.8cm}>{\centering\arraybackslash}p{1.8cm}>{\centering\arraybackslash}p{1.8cm}>{\centering\arraybackslash}p{1.8cm}>{\centering\arraybackslash}p{1.8cm}}\toprule
Material & UCS (MPa) & Bond CWI (kWh/t) & Crushability (\%) & Bond BWI (kWh/t) & Abrasividad Macon (g/t) & Bond Ai & DWT A$\times$b\\\midrule
""" + TB(B_WSC) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize La lámina atribuye los datos al estudio Mine-to-mill 2007/2009, fase~3; no indica cuántos ensayos hay por material. Waste-C/Std, Waste-Fine y Waste-Hard son categorías de ese estudio, no las clases A, B, C y C1 de Antamina. Según la lámina, Waste-Hard es el desmonte de mayor resistencia a la voladura y el más abrasivo.\end{table}

\begin{table}[H]\centering\scriptsize\setlength{\tabcolsep}{3pt}\caption{Fragmentación del desmonte por clase de Antamina, en el frente de carguío \citep{antamina2025frag}.}\label{tab:b_frag}
\begin{tabular}{lrlrrrr}\toprule
Clase & Análisis & Fases & P50 (cm) & P80 (cm) & $X_{max}$ (cm) & $X_{max}$, P10--P90 (cm)\\\midrule
""" + TB(B_FRAG) + r"""
\bottomrule\end{tabular}\par\vspace{3pt}\footnotesize Medianas de los análisis por fotos de enero a agosto de 2025 (columna «Tipo de material» de la planilla); P10--P90: percentiles 10 y 90 de $X_{max}$ entre análisis. Estadísticos calculados por Stantec de la planilla. P50 y P80: tamaños del análisis por fotos que pasan el 50 y el 80~\%. El $X_{max}$ máximo es 270.9~cm (clase A). La clase y la fase están asociadas (26 de 27 análisis de la clase C1 en la fase 10 y 27 de 30 de la clase B en la fase 9); las fases 8 a 10 no son las fases de LE2 del modelo de bloques.\end{table}
"""
_bib = [b.strip() for b in T[_i:_j].split("\\bibitem") if b.strip()]
_bib.sort(key=lambda b: b.split("]", 1)[1].split("}", 1)[1].strip().lower().replace("á", "a").replace("é", "e"))
T = T[:_i] + "\n".join("\\bibitem" + b for b in _bib) + "\n" + T[_j:]
T = T.replace("\\end{document}", ANX + ANXB + "\\end{document}")
_grado = lambda m: m.group(0).replace("°", "^{" + chr(92) + "circ}")
T = re.sub(r"\$[^$]*\$", _grado, T)
T = re.sub(r"begin\{equation\}.*?end\{equation\}", _grado, T, flags=re.S)
(AQ / "curva_leps2_antamina.tex").write_text(T, encoding="utf-8")
print(f"escrito | curva propuesta φ′e0 {OP2['pe0']:.2f}° m {MC:.3f} φ′1 {p2:.2f}° (control DDE {OP2['pe0_dde']:.2f}°) | ciclos {n_ciclo} | "
      f"contractivos {n_contr}/{n_eps} | anexo {len(A27)} ensayos | sobre Indraratna hasta 15 MPa: {LB_SOBRE}")

# ---- documento aparte con los anexos (A y B); referencias al cuerpo del memo con xr-hyper (compilar antes el memo)
_pre = T[:T.index("\\begin{document}")].replace("\\usepackage[colorlinks", "\\usepackage{xr-hyper}\\usepackage[colorlinks", 1)
_pre += "\\externaldocument[M-]{curva_leps2_antamina}\n"
_pre += "\\hypersetup{filecolor=black}\n"
_anx = T[T.index("\\clearpage\n\\appendix"):T.index("\\end{document}")].replace("\\clearpage\n\\appendix", "\\appendix", 1)
_lab = set(re.findall(r"\\label\{([^}]+)\}", _anx))
def _ext(m_):
    pre_, k_ = m_.group(1), m_.group(2)
    if k_ in _lab:
        return m_.group(0)
    return pre_ + "\\ref{M-" + k_ + "}" + (" del memorándum" if pre_ else "")
_anx = re.sub(r"((?:Tabla|Tablas|sección|Figura|Fig\.)~)?\\ref\{([^}]+)\}", _ext, _anx)
_cit = set(k for g in re.findall(r"\\cite[tp]?\*?(?:\[[^\]]*\])*\{([^}]+)\}", _anx) for k in g.split(","))
_b0 = T.index("\\begin{thebibliography}"); _b1 = T.index("\\end{thebibliography}") + len("\\end{thebibliography}")
_bib_items = [b for b in T[_b0:_b1].split("\\bibitem")[1:]]
_bib_keep = [b.replace("\\end{thebibliography}", "").rstrip() for b in _bib_items if re.match(r"\[[^\]]*\]\{([^}]+)\}", b).group(1) in _cit]
ANXDOC = (_pre + "\\begin{document}\n"
          + _anx.replace("\\appendix\n", "\\appendix\n", 1)
          + "\n\\begin{thebibliography}{20}\\small\n" + "\n".join("\\bibitem" + b for b in _bib_keep) + "\n\\end{thebibliography}\n\\end{document}\n")
(AQ / "curva_leps2_antamina_anexos.tex").write_text(ANXDOC, encoding="utf-8")
print(f"anexos: {len(_bib_keep)} referencias, {len(_lab)} etiquetas propias")
