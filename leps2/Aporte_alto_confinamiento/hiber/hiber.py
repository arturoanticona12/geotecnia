"""HiBER (Hierarchical Bounded Envelopes for Rockfill): criterio probabilístico de resistencia al corte drenada de enrocados y desmonte de mina.
Implementación de referencia. Unidades: MPa y grados.

Modelo jerárquico de tres niveles (publicación → material → ensayo), calibrado con la base de Arrieta (2025).
x = ln(σ′n/σ0), y = ln(τ/σ0), σ0 = 10 pa; (b0, b1) = b_publicación + b_material; ln σε(x) = a0 + a1·x.
Formas de la envolvente media de la población:
  «acotada» (central): tan φ′s = T + (tan φ′1 − T)·exp(−ζx), T = tan φ′∞, ln tan φ′1 = η = β[calidad] + βe·e
                        y = x + ln[T + (e^η − T)·e^(−ζx)] + b0 + b1·x + ε
                        φ′∞ es el ángulo asintótico de la ley de decaimiento: un parámetro de ajuste, NO un ángulo de
                        estado crítico. (φ′∞, ζ) se muestrean sobre la cresta de verosimilitud (no se identifican por
                        separado). En el archivo de parámetros se guarda con la clave histórica «phi_cs».
  «x2»:                 y = θ + m·x + c2·x² + ε,  θ = β[calidad] + βe·e + b0,  m = βx + b1
  «potencia»:           «x2» con c2 = 0.
En la forma acotada, `th` y `m` guardan las desviaciones de nivel y de pendiente (b0 + desplazamientos de nivel, b1);
la parte poblacional no lineal se guarda en `eta`, `T` y `zeta`. Las distribuciones se representan con muestras que
propagan la incertidumbre de los hiperparámetros (MCMC), de los efectos fijos y de los efectos aleatorios. La
envolvente se restringe a pendiente local ≤ 1 (no convexa) en el rango de uso.

Uso recomendado (impone el orden de operaciones y el dominio de validez):
    r = envolvente_diseno("moderate", e_lab=0.45, e_campo=0.65, D_lab=150, D_campo=1000,
                          ensayos=dict(s3=[0.5, 1.0, 2.0], s1=[2.6, 4.9, 9.1]))
    r.tabla; r.p_conflicto; r.avisos

Uso por pasos (el orden importa: actualizar SIEMPRE a la e de laboratorio y desplazar después):
    mat = previa("moderada", e=0.45)                         # material nuevo, laboratorio nuevo, e de las probetas
    mat, dg = actualizar(mat, s3=[0.5, 1.0], s1=[2.6, 4.9])  # ensayos triaxiales drenados del sitio
    mat = densidad(mat, de=+0.20)                            # de la probeta a la densidad de colocación
    mat = escala(mat, d_lab=150, d_campo=1000)               # de la probeta al desmonte de campo
    percentiles([1, 5], mat)                                 # φ′s por percentil (envolvente media)

Dominio de validez: σ′n ≤ 8 MPa (σ′n máx. de la base ≈ 7.9 MPa); por encima de 3 MPa, solo e ≤ 0.55; e de la base
0.15–0.89; por debajo de σ′n ≈ 0.05–0.1 MPa, usar con un tope (tope_reposo). Fuera de él la biblioteca avisa o falla.
Clases: «buena»/«moderada»/«baja» o «good»/«moderate»/«low».
"""
from __future__ import annotations
import json, math, warnings
from dataclasses import dataclass, field
from pathlib import Path
import numpy as np
from scipy.stats import chi2

_P = json.load(open(Path(__file__).with_name("hiber_parameters.json")))
S0 = _P["S0"]
SN_MAX_BASE = _P["n"]["sn_max"]
# nombre de clase → columna de β en el archivo de parámetros; se aceptan los nombres en español y en inglés
CALIDAD = {"buena": "good", "moderada": "moderate", "baja": "low", "good": "good", "moderate": "moderate", "low": "low"}
SN_USO_MAX = 20.0          # σ′n hasta el que se exige pendiente local ≤ 1 (MPa)
FORMA = "acotada" if "acotada" in _P["formas"] else "x2"
_XS = np.log(np.geomspace(0.05, SN_USO_MAX, 13) / S0)

# Dominio de validez (artículo, sección de limitaciones)
SN_DISENO_MAX = 8.0        # σ′n máximo de uso (MPa); el máximo de la base es SN_MAX_BASE ≈ 7.9 MPa
SN_DISENO_MIN = 0.05       # por debajo, solo con un tope (tope_reposo)
SN_TOPE = 0.1              # σ′n por debajo del cual actúa tope_reposo (MPa)
SN_E_ALTA = 3.0            # por encima de esta σ′n la base solo tiene e ≤ E_ALTA_MAX
E_ALTA_MAX = 0.55
E_BASE = (0.15, 0.89)      # rango de e de la base de calibración


def _clase(cal: str) -> str:
    """Normaliza el nombre de clase («buena»/«good», «moderada»/«moderate», «baja»/«low»; sin distinguir mayúsculas)."""
    c = str(cal).strip().lower()
    if c not in CALIDAD:
        raise ValueError(f"Clase desconocida {cal!r}; use una de {sorted(CALIDAD)}.")
    return c


def _chequear_e(e, que="e"):
    if e is not None and not (E_BASE[0] <= e <= E_BASE[1]):
        warnings.warn(f"{que} = {e:.3f} fuera del rango de la base de calibración ({E_BASE[0]}–{E_BASE[1]}): extrapolación.",
                      stacklevel=3)


def _G(p):
    s0, s1, r = math.exp(p[0]), math.exp(p[1]), math.tanh(p[2])
    return np.array([[s0 * s0, r * s0 * s1], [r * s0 * s1, s1 * s1]])


@dataclass
class Material:
    """Muestras de los parámetros del material (una fila por realización)."""
    th: np.ndarray            # x2/potencia: θ = ln tan φ′1; acotada: desviación de nivel (b0 + desplazamientos)
    m: np.ndarray             # x2/potencia: pendiente; acotada: desviación de pendiente b1
    c2: np.ndarray            # término cuadrático (x2)
    a0: np.ndarray            # ln σε(0)
    a1: np.ndarray
    k: np.ndarray             # índice de la muestra de hiperparámetros
    forma: str
    sn_max_ensayado: float | None = None
    notas: list = field(default_factory=list)
    be: np.ndarray | None = None      # βe por muestra (para densidad())
    eta: np.ndarray | None = None     # acotada: ln tan φ′1 del material (efectos fijos + aleatorio, en «eta_zeta»)
    T: np.ndarray | None = None       # acotada: tan φ′∞ (ángulo asintótico de decaimiento, no de estado crítico)
    zeta: np.ndarray | None = None    # acotada: tasa de decaimiento del material
    vb: np.ndarray | None = None      # varianza de η por los efectos fijos (para la ganancia de la actualización)
    efectos: str = "lineal"           # «eta_zeta»: efectos aleatorios en (η, ζ); «lineal»: en (nivel, pendiente) log–log
    e: float | None = None            # relación de vacíos actual (solo para los chequeos de dominio)

    def sel(self, ok):
        f = lambda a: None if a is None else a[ok]
        return Material(self.th[ok], self.m[ok], self.c2[ok], self.a0[ok], self.a1[ok], self.k[ok], self.forma,
                        self.sn_max_ensayado, list(self.notas), f(self.be), f(self.eta), f(self.T), f(self.zeta), f(self.vb), self.efectos,
                        self.e)

    def copia(self):
        return self.sel(np.ones(len(self.th), bool))


def _media(mat: Material, x) -> np.ndarray:
    """ŷ = E[ln(τ/σ0) | parámetros del material] por muestra (filas) y por x (columnas), sin la dispersión de ensayo."""
    x = np.atleast_1d(np.asarray(x, float))[None, :]
    lin = mat.th[:, None] + mat.m[:, None] * x
    if mat.eta is not None:
        T = mat.T[:, None]; g = np.maximum(T + (np.exp(mat.eta)[:, None] - T) * np.exp(-mat.zeta[:, None] * x), 1e-9)
        return x + np.log(g) + lin
    return lin + mat.c2[:, None] * x ** 2


def _pendiente(mat: Material, x) -> np.ndarray:
    """Pendiente local dy/dx por muestra y por x."""
    h = 1e-4
    return (_media(mat, np.asarray(x) + h) - _media(mat, np.asarray(x) - h)) / (2 * h)


def _hiper(forma):
    F = _P["formas"][forma]; ix = F["nombres"].index
    H = []
    for s in F["muestras"]:
        p = np.array(s["psi"])
        H.append(dict(Gp=_G(p[0:3]), Gs=_G(p[3:6]), G=_G(p[0:3]) + _G(p[3:6]), a=p[6:8], beta=np.array(s["beta"]),
                      # «phi_cs» es la clave histórica de φ′∞ (ángulo asintótico de decaimiento, no de estado crítico)
                      C=np.array(s["cov_beta"]), T=math.tan(math.radians(s.get("phi_cs", 0.0))), zeta=s.get("zeta", 0.0)))
    return F, ix, H


D_REF = 100.0     # mm: Dmax de referencia del término ln(Dmax/D_REF) de la ronda 6 (solo si «lnD» está en los parámetros)


def _lnD(D):
    return math.log(float(D) / D_REF) if D is not None else 0.0


def _fijos(forma, F, ix, bet, cal, e, D=None):
    """Parte fija por muestra: (nivel, pendiente, c2, eta) — nivel y pendiente lineales para x2; eta para acotada.
    Ronda 6: si los parámetros traen «lnD», η suma β_D·ln(Dmax/100 mm) con el Dmax de laboratorio del material (dentro del
    rango de la base; la extrapolación a tamaño de campo la hace escala())."""
    n = len(bet); cero = np.zeros(n); be = bet[:, ix("e")]
    if forma.startswith("acotada"):
        eta = bet[:, ix(CALIDAD[cal])] + be * e
        if "lnD" in F["nombres"]:
            eta = eta + bet[:, ix("lnD")] * _lnD(D)
        return cero, cero, cero, eta, be
    c2 = bet[:, ix("x2")] if "x2" in F["nombres"] else cero
    return bet[:, ix(CALIDAD[cal])] + be * e, bet[:, ix("x")], c2, None, be


def _efectos(forma):
    return _P["formas"][forma].get("efectos", "lineal")


def _vacio(n, forma):
    o = dict(th=np.zeros(n), m=np.zeros(n), c2=np.zeros(n), a=np.zeros((n, 2)), be=np.zeros(n), vb=np.zeros(n))
    if forma.startswith("acotada"):
        o.update(eta=np.zeros(n), T=np.zeros(n), zeta=np.zeros(n))
    return o


def _material(o, k, forma, notas=None):
    return Material(o["th"], o["m"], o["c2"], o["a"][:, 0], o["a"][:, 1], k, forma, notas=list(notas or []), be=o["be"],
                    eta=o.get("eta"), T=o.get("T"), zeta=o.get("zeta"), vb=o["vb"], efectos=_efectos(forma))


def _llenar(o, i, forma, F, ix, h, bet, cal, e, b, D=None):
    lv, sl, c2, eta, be = _fijos(forma, F, ix, bet, cal, e, D)
    o["a"][i] = h["a"]; o["be"][i] = be; o["c2"][i] = c2
    dv = np.zeros(len(F["nombres"])); dv[ix(CALIDAD[cal])] = 1.0; dv[ix("e")] = e
    if "lnD" in F["nombres"]:
        dv[ix("lnD")] = _lnD(D)
    o["vb"][i] = float(dv @ h["C"] @ dv)
    if F.get("efectos") == "eta_zeta":                 # efectos aleatorios en (η, ζ) de cada material
        dz = bet[:, ix("dz_" + CALIDAD[cal])] if ("dz_" + CALIDAD[cal]) in F["nombres"] else 0.0   # ronda 6: ζ por clase
        o["th"][i] = 0.0; o["m"][i] = 0.0; o["eta"][i] = eta + b[:, 0]; o["zeta"][i] = h["zeta"] + dz + b[:, 1]; o["T"][i] = h["T"]
        return
    o["th"][i] = lv + b[:, 0]; o["m"][i] = sl + b[:, 1]
    if forma.startswith("acotada"):
        o["eta"][i] = eta; o["T"][i] = h["T"]; o["zeta"][i] = h["zeta"]


def _Z(mat: Material, x) -> np.ndarray:
    """Gradiente de ŷ respecto de los efectos aleatorios del material, por muestra: (n, len(x), 2)."""
    x = np.atleast_1d(np.asarray(x, float))[None, :]
    if mat.efectos == "eta_zeta":
        T = mat.T[:, None]; E = np.exp(mat.eta)[:, None]; q = np.exp(-mat.zeta[:, None] * x); g = np.maximum(T + (E - T) * q, 1e-9)
        return np.stack([E * q / g, -x * (E - T) * q / g], axis=-1)
    return np.stack([np.ones((len(mat.th), x.shape[1])), np.broadcast_to(x, (len(mat.th), x.shape[1]))], axis=-1)


def _aplicar(mat: Material, i, du):
    """Suma desplazamientos de los efectos aleatorios (n_i, 2) a las muestras i."""
    if mat.efectos == "eta_zeta":
        mat.eta[i] += du[:, 0]; mat.zeta[i] += du[:, 1]
    else:
        mat.th[i] += du[:, 0]; mat.m[i] += du[:, 1]


def _ok_pendiente(mat, xs=_XS):
    return np.all(_pendiente(mat, xs) <= 1.0, axis=1)


def _restringir(mat, rng=None):
    """Condiciona a pendiente local ≤ 1 en el rango de uso (muestreo por rechazo)."""
    ok = _ok_pendiente(mat)
    if ok.mean() < 0.02:
        warnings.warn("La restricción de pendiente ≤ 1 descarta más del 98 % de las muestras: conflicto entre el modelo y los datos.", stacklevel=3)
    return mat.sel(ok)


def previa(calidad: str, e: float, forma: str = FORMA, n: int = 40000, seed: int = 0, D: float | None = None) -> Material:
    """Material nuevo de calidad «buena», «moderada» o «baja» (Tabla 5 de Cylwik et al., 2025) con relación de vacíos e,
    ensayado por un laboratorio nuevo. forma: «acotada» (central), «x2» o «potencia».
    También se aceptan «good», «moderate» y «low». Avisa si e está fuera del rango de la base (0.15–0.89)."""
    calidad = _clase(calidad); _chequear_e(e)
    rng = np.random.default_rng(seed); F, ix, H = _hiper(forma)
    k = rng.integers(len(H), size=n); o = _vacio(n, forma)
    for j in np.unique(k):
        i = np.where(k == j)[0]; h = H[j]
        bet = rng.multivariate_normal(h["beta"], h["C"], len(i)); b = rng.multivariate_normal([0, 0], h["G"], len(i))
        _llenar(o, i, forma, F, ix, h, bet, calidad, e, b, D)
    mat = _material(o, k, forma, [f"previa {calidad}, e = {e}"]); mat.e = float(e)
    return _restringir(mat, rng)


def previa_conjunta(materiales, forma: str = FORMA, mismo_laboratorio=False, n: int = 40000, seed: int = 0):
    """Varios materiales de un mismo sitio, muestreados con las mismas realizaciones de hiperparámetros y de efectos
    fijos (incertidumbre sistemática común). Los efectos de material son independientes; el de laboratorio es común si
    mismo_laboratorio=True. materiales: lista de (calidad, e). Devuelve una lista de Material alineados por fila
    (sin aplicar la restricción de pendiente; usar restringir_conjunto al final)."""
    materiales = [(_clase(m_[0]), m_[1], (m_[2] if len(m_) > 2 else None)) for m_ in materiales]   # (calidad, e[, Dmax mm])
    for _, e, _D in materiales:
        _chequear_e(e)
    rng = np.random.default_rng(seed); F, ix, H = _hiper(forma)
    k = rng.integers(len(H), size=n); out = [_vacio(n, forma) for _ in materiales]
    for j in np.unique(k):
        i = np.where(k == j)[0]; h = H[j]
        bet = rng.multivariate_normal(h["beta"], h["C"], len(i)); bpub = rng.multivariate_normal([0, 0], h["Gp"], len(i))
        for o, (cal, e, Dm) in zip(out, materiales):
            b = (bpub if mismo_laboratorio else rng.multivariate_normal([0, 0], h["Gp"], len(i))) + rng.multivariate_normal([0, 0], h["Gs"], len(i))
            _llenar(o, i, forma, F, ix, h, bet, cal, e, b, Dm)
    mats = [_material(o, k, forma, [f"previa {c}, e = {e}"]) for o, (c, e, _D) in zip(out, materiales)]
    for mt, (_, e, _D) in zip(mats, materiales):
        mt.e = float(e)
    return mats


def restringir_conjunto(mats):
    """Aplica la restricción de pendiente ≤ 1 a todos los materiales a la vez (conserva el alineamiento por fila)."""
    ok = np.all([_ok_pendiente(mt) for mt in mats], axis=0)
    return [mt.sel(ok) for mt in mats]


def actualizar_sitio(sets, nuevos=(), forma: str = FORMA, n: int = 40000, seed: int = 0, solo_nivel: bool = True,
                     lab_comun_nuevos: bool = True):
    """Actualización conjunta de todos los ensayos de un sitio ensayados por un mismo laboratorio.
    solo_nivel=True: los ensayos de cada set informan el nivel de la envolvente en su centroide x̄ (actualización de
    corte: cada residuo se trata como medición de b0 + b1·x̄); la pendiente conserva su distribución previa condicional.
    False: actualización conjunta de (b0, b1).
    Modelo: b_set_j = b_lab + b_mat_j, con b_lab ~ N(0, G_p) común a todo el sitio y b_mat_j ~ N(0, G_s) por set.
    sets: lista de dict(calidad, e, s3, s1, usar=True); los sets con usar=False no informan la actualización y se devuelven
    como material nuevo de su calidad que comparte el efecto de laboratorio actualizado. nuevos: lista de (calidad, e);
    lab_comun_nuevos=False les asigna un efecto de laboratorio independiente (sensibilidad).
    En la forma con efectos en (η, ζ), las filas de la actualización son el gradiente de la envolvente respecto de (η, ζ)
    en x̄ (linealización en la media del grupo de hiperparámetros) y la incertidumbre de los efectos fijos se suma a la
    previa del efecto de laboratorio en η.
    Conversión σ′3, σ′1 → σ′n, τ: la misma que en actualizar() (ver _m_conversion), con la previa de la clase y e de
    cada set. Avisa si un set usado tiene menos de 2 ensayos y si hay conflicto (p < 0.05) entre la previa y un set.
    Devuelve (lista de Material para sets y nuevos, alineados por fila; diagnósticos por set)."""
    sets = [dict(s, calidad=_clase(s["calidad"])) for s in sets]; nuevos = [(_clase(m_[0]), m_[1], (m_[2] if len(m_) > 2 else None)) for m_ in nuevos]
    rng = np.random.default_rng(seed); F, ix, H = _hiper(forma); nS = len(sets); nN = len(nuevos)
    conv, previas = [], []
    for s in sets:
        s3, s1 = np.asarray(s["s3"], float), np.asarray(s["s1"], float)
        if np.any(s1 <= s3) or np.any(s3 <= 0):
            raise ValueError("Se requiere σ′1 > σ′3 > 0")
        if s.get("usar", True) and len(s3) < 2:
            warnings.warn(f"Set de clase «{s['calidad']}» con {len(s3)} ensayo: la actualización con menos de 2 ensayos "
                          "no separa el material de la dispersión de ensayo; se recomiendan ≥ 3 por set.", stacklevel=2)
        pr = previa(s["calidad"], s["e"], forma, n=20000, seed=seed + 7, D=s.get("D")); previas.append(pr)
        # antes se usaba m = 0.86 fijo; ahora la misma regla que actualizar() (la pendiente previa a 1 MPa es ≈ 0.86)
        sn, tau = _a_sn_tau(s3, s1, _m_conversion(pr)); conv.append((np.log(sn / S0), np.log(tau / S0), sn))
    k = rng.integers(len(H), size=n); outs = [_vacio(n, forma) for _ in range(nS + nN)]
    usar = [s.get("usar", True) for s in sets]
    for j in np.unique(k):
        idx = np.where(k == j)[0]; h = H[j]; Gp, Gs, a = h["Gp"], h["Gs"], h["a"]
        bet = rng.multivariate_normal(h["beta"], h["C"], len(idx))
        D = 2 * (1 + nS); P0 = np.zeros((D, D)); P0[:2, :2] = Gp
        for i in range(nS):
            P0[2 + 2 * i:4 + 2 * i, 2 + 2 * i:4 + 2 * i] = Gs
        rows, Rv, yres, vbs = [], [], [], []
        for i, (x, y, _) in enumerate(conv):
            if not usar[i]:
                continue
            tmp = _vacio(len(idx), forma); _llenar(tmp, np.arange(len(idx)), forma, F, ix, h, bet, sets[i]["calidad"], sets[i]["e"], np.zeros((len(idx), 2)), sets[i].get("D"))
            mt0 = _material(tmp, k[idx], forma); xc = float(np.mean(x)); vbs.append(float(np.mean(mt0.vb)))
            for xx in x:
                zz = _Z(mt0, [xc if solo_nivel else xx]).mean(0)[0]
                r_ = np.zeros(D); r_[0:2] = zz; r_[2 + 2 * i:4 + 2 * i] = zz; rows.append(r_); Rv.append(np.exp(2 * (a[0] + a[1] * xx)))
            yres.append(y[None, :] - _media(mt0, x))
        # la incertidumbre de los efectos fijos (que entra por η) va en la ganancia, no en la previa de los efectos
        # aleatorios: las muestras ya la llevan al sortear β (ronda 5: antes se contaba dos veces)
        P0g = P0.copy()
        if vbs and F.get("efectos") == "eta_zeta":
            P0g[0, 0] += float(np.mean(vbs))
        Bdraw = rng.multivariate_normal(np.zeros(D), P0, len(idx))
        if rows:
            Zm = np.array(rows); R = np.diag(Rv); K = P0g @ Zm.T @ np.linalg.inv(Zm @ P0g @ Zm.T + R)
            Yr = np.hstack(yres); pert = rng.normal(size=Yr.shape) * np.sqrt(np.array(Rv))[None, :]
            Bdraw = Bdraw + (Yr + pert - Bdraw @ Zm.T) @ K.T
        for i, s in enumerate(sets):
            bm = Bdraw[:, 2 + 2 * i:4 + 2 * i] if usar[i] else rng.multivariate_normal([0, 0], Gs, len(idx))
            _llenar(outs[i], idx, forma, F, ix, h, bet, s["calidad"], s["e"], Bdraw[:, :2] + bm, s.get("D"))
        for q, (cal, e, Dm) in enumerate(nuevos):
            bm = rng.multivariate_normal([0, 0], Gs, len(idx))
            lab = Bdraw[:, :2] if lab_comun_nuevos else rng.multivariate_normal([0, 0], Gp, len(idx))
            _llenar(outs[nS + q], idx, forma, F, ix, h, bet, cal, e, lab + bm, Dm)
    mats = [_material(o, k, forma) for o in outs]
    sn_lab = max([float(conv[i][2].max()) for i in range(nS) if usar[i]], default=None)
    for i, s in enumerate(sets):
        mats[i].e = float(s["e"]); mats[i].sn_max_ensayado = float(conv[i][2].max()) if usar[i] else sn_lab
        mats[i].notas.append(f"sitio: set {s['calidad']}, e = {s['e']}" + (f", {len(conv[i][0])} ensayos" if usar[i] else ", no usado"))
    for q, (cal, e, _D) in enumerate(nuevos):
        mats[nS + q].e = float(e); mats[nS + q].sn_max_ensayado = sn_lab
        mats[nS + q].notas.append(f"sitio: set nuevo {cal}, e = {e}")
    diags = []
    for i, s in enumerate(sets):
        x, y, sn = conv[i]; pr = previas[i]
        pred = _media(pr, x) + rng.normal(size=(len(pr.th), len(x))) * sigma_eps(x, pr)
        mu, V = pred.mean(0), np.cov(pred.T).reshape(len(x), len(x)); D2 = float((y - mu) @ np.linalg.solve(V, y - mu))
        p = float(1 - chi2.cdf(D2, len(x)))
        diags.append(dict(p_conflicto=p, rango_sn=float(sn.max() / sn.min()), sn_max=float(sn.max()), usado=bool(usar[i]),
                          m_conversion=_m_conversion(pr), residuo_medio=float(np.mean(y - mu))))   # > 0: set más resistente que la previa
        if p < 0.05:
            warnings.warn(f"Conflicto entre la previa y el set {i} (p = {p:.3f}). "
                          "Revise el ensayo, la clase de roca o la definición de falla.", stacklevel=2)
    return mats, diags


def restringir_conjunto_rango(mats, sn_max=None):
    """Restricción de pendiente local ≤ 1 solo en el rango calibrado (por defecto, σ′n ≤ σ′n máx. de la base).
    Devuelve (materiales filtrados, fracción conservada por material y conjunta)."""
    sn_max = SN_MAX_BASE if sn_max is None else sn_max; xs = np.log(np.geomspace(0.05, sn_max, 13) / S0)
    oks = [_ok_pendiente(mt, xs) for mt in mats]; ok = np.all(oks, axis=0)
    return [mt.sel(ok) for mt in mats], dict(por_material=[float(o.mean()) for o in oks], conjunta=float(ok.mean()))


def sigma_eps(x, mat: Material):
    return np.exp(mat.a0[:, None] + mat.a1[:, None] * np.atleast_1d(x)[None, :])


def _a_sn_tau(s3, s1, m):
    """Ecs. 13, 14 y 16 de Cylwik et al. (2025)."""
    D, S = s1 - s3, s1 + s3
    sp = D / S if abs(m - 1) < 1e-6 else (np.sqrt(4 * m * (m - 1) * D ** 2 + S ** 2) - S) / (2 * (m - 1) * D)
    return S / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


def _m_conversion(mat: Material) -> float:
    """m de la conversión σ′3, σ′1 → σ′n, τ (Ecs. 13–16 de Cylwik et al., 2025): mediana de la pendiente local
    d ln τ / d ln σ′n de la envolvente media del material a σ′n = 1 MPa, acotada a [0.5, 1.0]. Es la misma regla en
    actualizar() y en actualizar_sitio() (en este último, con la previa de la clase y e de cada set)."""
    return float(np.clip(np.median(_pendiente(mat, [math.log(1.0 / S0)])), 0.5, 1.0))


def actualizar(mat: Material, s3, s1, seed: int = 1, restringir=True, conjunta: bool = False):
    """Actualiza con triaxiales drenados del mismo material (σ′3 y σ′1 en la falla, MPa).
    Regla por defecto: se actualiza el nivel de la envolvente en el centroide de los ensayos (actualización de corte) y la
    pendiente conserva su distribución condicional. conjunta=True actualiza nivel y pendiente solo si la razón de σ′n ≥ 3
    y no hay conflicto (p ≥ 0.05). El diagnóstico de conflicto se informa siempre. Devuelve (Material, diagnóstico).
    `mat` debe estar a la e de las probetas y sin escalar: actualizar después de densidad() o escala() devuelve la
    envolvente a la resistencia de laboratorio (lado inseguro) y emite un aviso. La posterior es la del material
    ensayado; para un tipo de roca (set nuevo del mismo laboratorio) use actualizar_sitio(..., nuevos=...) o
    envolvente_diseno(..., representa="tipo"). Conversión σ′3, σ′1 → σ′n, τ con m = _m_conversion(mat)."""
    s3, s1 = np.asarray(s3, float), np.asarray(s1, float)
    if np.any(s1 <= s3) or np.any(s3 <= 0):
        raise ValueError("Se requiere σ′1 > σ′3 > 0")
    if any(nt.startswith(("Δe", "escala")) for nt in mat.notas):
        warnings.warn("Orden de operaciones: se actualiza un material ya desplazado por densidad() o escala(). Actualice a "
                      "la e de laboratorio y desplace después (o use envolvente_diseno); al revés el resultado queda del "
                      "lado inseguro.", stacklevel=2)
    if len(s3) < 2:
        warnings.warn(f"Actualización con {len(s3)} ensayo: no separa el material de la dispersión de ensayo; se "
                      "recomiendan ≥ 3 ensayos por set.", stacklevel=2)
    rng = np.random.default_rng(seed); _, _, H = _hiper(mat.forma)
    m_c = _m_conversion(mat)                                         # conversión con la pendiente previa a 1 MPa
    sn, tau = _a_sn_tau(s3, s1, m_c); x = np.log(sn / S0); y = np.log(tau / S0)
    pred = _media(mat, x) + rng.normal(size=(len(mat.th), len(x))) * sigma_eps(x, mat)
    mu, V = pred.mean(0), np.cov(pred.T).reshape(len(x), len(x))
    D2 = float((y - mu) @ np.linalg.solve(V, y - mu)); pval = float(1 - chi2.cdf(D2, len(x)))
    rango = float(sn.max() / sn.min()); completo = conjunta and rango >= 3 and pval >= 0.05
    nuevo = mat.copia(); yhat = _media(mat, x); xb = float(np.mean(x))
    for j in np.unique(mat.k):
        i = np.where(mat.k == j)[0]; G = H[j]["G"]; s2 = np.exp(2 * (H[j]["a"][0] + H[j]["a"][1] * x))
        sub = mat.sel(i); r = y[None, :] - yhat[i] + rng.normal(size=(len(i), len(x))) * np.sqrt(s2)[None, :]
        # previa de los efectos aleatorios con la incertidumbre de los efectos fijos (que solo entran por η)
        Gs_ = np.repeat(G[None], len(i), 0)
        if mat.efectos == "eta_zeta":
            Gs_[:, 0, 0] += mat.vb[i]
        if completo:
            Zm = _Z(sub, x).mean(0); R = np.diag(s2)                          # linealización en la media del grupo
            Gm = Gs_.mean(0); K = Gm @ Zm.T @ np.linalg.inv(Zm @ Gm @ Zm.T + R); du = r @ K.T
        else:
            # actualización de corte: los residuos informan q = zᵀu en x̄; u se desplaza por regresión sobre q
            zb = _Z(sub, [xb])[:, 0, :]; Gz = np.einsum("nij,nj->ni", Gs_, zb); g0 = np.einsum("ni,ni->n", zb, Gz)
            c = 1 / (1 / g0 + np.sum(1 / s2)); dq = c * (r / s2[None, :]).sum(1)
            du = Gz * (dq / g0)[:, None]
        _aplicar(nuevo, i, du)
    nuevo.sn_max_ensayado = float(sn.max()) if mat.sn_max_ensayado is None else max(mat.sn_max_ensayado, float(sn.max()))
    nuevo.notas.append(f"actualizado con {len(x)} ensayos ({'nivel y pendiente' if completo else 'solo nivel'})")
    diag = dict(p_conflicto=pval, conflicto=pval < 0.05, rango_sn=rango, modo="nivel y pendiente" if completo else "solo nivel", sn=sn, tau=tau)
    if pval < 0.05:
        warnings.warn(f"Conflicto entre la previa y los ensayos del sitio (p = {pval:.3f}). "
                      "Revise el ensayo, la clase de roca o la definición de falla.", stacklevel=2)
    return (_restringir(nuevo, rng) if restringir else nuevo), diag


def densidad(mat: Material, de: float) -> Material:
    """Cambio de relación de vacíos Δe (p. ej., de la probeta a la colocación). En la forma acotada actúa sobre la parte
    dilatante (η), de modo que su efecto disminuye con la tensión; en x2/potencia desplaza el nivel.
    Avisa si la e resultante (si se conoce la e del material) queda fuera del rango de la base (0.15–0.89)."""
    nuevo = mat.copia()
    if mat.eta is not None:
        nuevo.eta = mat.eta + mat.be * de
    else:
        nuevo.th = mat.th + mat.be * de
    if mat.e is not None:
        nuevo.e = mat.e + de; _chequear_e(nuevo.e, f"e + Δe = {mat.e:.3f} {de:+.3f}")
    nuevo.notas.append(f"Δe = {de:+.3f}"); return nuevo


def muestras_bD(n, supuesto="general", seed=2):
    """βD por realización. 'general': todos los grupos de la base; 'paralela': grupos con gradación casi paralela y
    densidad similar. Media ± (EE de Hartung–Knapp ⊕ τ)."""
    E = _P["escala"][supuesto]; return np.random.default_rng(seed).normal(E["b"], math.hypot(E["se_hk"], E["tau"]), n)


def escala(mat: Material, d_lab: float, d_campo: float, seed: int = 2, bD=None, supuesto="general") -> Material:
    """Efecto de tamaño de la probeta (dmax d_lab) al desmonte de campo (dmax d_campo): Δ nivel = βD·ln(d_campo/d_lab).
    bD: muestras dadas (para compartirlas entre materiales de un mismo sitio); si no, se generan con muestras_bD."""
    if d_campo / d_lab > 15:
        warnings.warn("Razón de tamaños > 15: fuera del rango recomendado por Frossard et al. (2012).", stacklevel=2)
    if bD is None:
        bD = muestras_bD(len(mat.th), supuesto, seed)
    nuevo = mat.copia(); nuevo.th = mat.th + bD * math.log(d_campo / d_lab)
    nuevo.notas.append(f"escala {d_lab:g} → {d_campo:g} mm"); return nuevo


def _dominio(sn, mat):
    """Avisos de dominio de validez para las σ′n pedidas y la e actual del material."""
    sn = np.atleast_1d(sn)
    if np.any(sn > SN_DISENO_MAX):
        warnings.warn(f"σ′n > {SN_DISENO_MAX:.0f} MPa (máx. de la base {SN_MAX_BASE:.1f} MPa): fuera del rango de la base "
                      "de calibración; extrapolación.", stacklevel=3)
    if mat.e is not None and mat.e > E_ALTA_MAX and np.any(sn > SN_E_ALTA):
        warnings.warn(f"e = {mat.e:.3f} > {E_ALTA_MAX} con σ′n > {SN_E_ALTA:.0f} MPa: la base no tiene ensayos de "
                      "material suelto a esa tensión; extrapolación.", stacklevel=3)
    if mat.sn_max_ensayado and np.any(sn > 3 * mat.sn_max_ensayado):
        warnings.warn("σ′n > 3 veces el máximo ensayado en el sitio: intervalos no verificados en ese rango.", stacklevel=3)


def _validar_sn_max(sn_max, permitir_extrapolacion):
    """Error si se pide σ′n por encima del dominio, salvo extrapolación explícita (que _dominio avisa)."""
    if sn_max > SN_DISENO_MAX and not permitir_extrapolacion:
        raise ValueError(f"σ′n máx. = {sn_max:g} MPa > {SN_DISENO_MAX:g} MPa (dominio de validez; máx. de la base "
                         f"{SN_MAX_BASE:.1f} MPa). Use permitir_extrapolacion=True para extrapolar bajo su responsabilidad.")


def _aviso_baja_tension(sn_min, tope_reposo):
    if sn_min < SN_DISENO_MIN and tope_reposo is None:
        warnings.warn(f"σ′n = {sn_min:g} MPa < {SN_DISENO_MIN:g} MPa sin tope: φ′s crece sin límite al bajar la tensión; "
                      "use tope_reposo (p. ej., 38°).", stacklevel=3)


def _con_tope(sn, phi, tope_reposo):
    """φ′s ≤ tope_reposo (°) para σ′n < SN_TOPE (0.1 MPa); sin cambio si tope_reposo es None."""
    if tope_reposo is None:
        return phi
    return np.where(np.asarray(sn) < SN_TOPE, np.minimum(phi, tope_reposo), phi)


def muestras_phi(sn, mat: Material, puntual=True, seed=3):
    """Ángulo secante φ′s (°) por muestra y por σ′n. puntual=True incluye la dispersión de ensayo (resistencia de un
    punto); False da la incertidumbre de la envolvente media del material (escala de la superficie de falla)."""
    sn = np.atleast_1d(np.asarray(sn, float)); _dominio(sn, mat); x = np.log(sn / S0)
    y = _media(mat, x)
    if puntual:
        y = y + np.random.default_rng(seed).normal(size=(len(mat.th), 1)) * sigma_eps(x, mat)
    return np.degrees(np.arctan(S0 * np.exp(y) / sn[None, :]))


def percentiles(sn, mat: Material, ps=(10, 50, 90), puntual=False):
    """Percentiles de φ′s (°) por σ′n. Por defecto (puntual=False) son los de la envolvente MEDIA del material, que es
    lo que se usa en diseño (falla global). puntual=True incluye la dispersión de ensayo (resistencia de un punto)."""
    ph = muestras_phi(sn, mat, puntual)
    return {p: np.percentile(ph, p, axis=0) for p in ps}


def phi1_mediana(mat: Material) -> float:
    """Mediana de φ′1 (ángulo secante en σ′n = σ0) de la envolvente media del material."""
    return float(np.degrees(np.arctan(np.exp(np.median(_media(mat, [0.0])[:, 0])))))


def tau_percentil(sn, mat: Material, p=10, puntual=False):
    sn = np.atleast_1d(np.asarray(sn, float))
    return sn * np.tan(np.radians(percentiles(sn, mat, (p,), puntual)[p]))


def caracteristico(sn, mat: Material):
    """Valor característico para falla global (estimación prudente de la media, en sentido bayesiano): P05 de la
    envolvente media del material."""
    return tau_percentil(sn, mat, 5, puntual=False)


def tabla_slide2(mat: Material, p=50, sn_max=SN_DISENO_MAX, n_pts=30, unidades="kPa", puntual=False,
                 sn_min=SN_DISENO_MIN, permitir_extrapolacion=False, tope_reposo=None):
    """Pares (σ′n, τ) del percentil p para un material de tipo función (p. ej., Slide2), con (0, 0) al inicio.
    σ′n en [sn_min, sn_max] con espaciado logarítmico (por defecto 0.05–8 MPa, el dominio de validez).
    sn_max > 8 MPa: ValueError, salvo permitir_extrapolacion=True (entonces se emite un aviso, no se silencia).
    sn_min < 0.05 MPa sin tope: aviso. tope_reposo (°, p. ej. 38): φ′s ≤ tope para σ′n < 0.1 MPa; None = sin tope.
    Los avisos de dominio (e > 0.55 con σ′n > 3 MPa, etc.) se emiten, no se silencian."""
    _validar_sn_max(sn_max, permitir_extrapolacion); _aviso_baja_tension(sn_min, tope_reposo)
    f = 1000.0 if unidades == "kPa" else 1.0
    sn = np.logspace(math.log10(sn_min), math.log10(sn_max), n_pts)
    phi = _con_tope(sn, percentiles(sn, mat, (p,), puntual)[p], tope_reposo)
    t = sn * np.tan(np.radians(phi))
    return [(0.0, 0.0)] + [(round(float(a) * f, 3), round(float(b) * f, 3)) for a, b in zip(sn, t)]


SN_TABLA = (0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 3.0, 5.0, 8.0)   # σ′n por defecto de envolvente_diseno (MPa)


@dataclass
class Diseno:
    """Resultado de envolvente_diseno. tabla: DataFrame con sn_MPa, phi_P50, phi_P05 (°), tau_P50, tau_P05 (MPa) de
    la envolvente media. p_conflicto: p del chequeo previa–ensayos (None sin ensayos). avisos: textos de los avisos
    emitidos. material: Material final (a e_campo y D_campo), p. ej. para tabla_slide2. También admite r["tabla"]."""
    tabla: object
    p_conflicto: float | None
    avisos: list
    material: Material
    diagnostico: dict | None = None
    tope_reposo: float | None = None

    def __getitem__(self, k):
        return getattr(self, k)

    def a_slide2(self, p=5, **kw):
        """tabla_slide2 del material final con el mismo tope_reposo (por defecto P05, en kPa)."""
        kw.setdefault("tope_reposo", self.tope_reposo)
        return tabla_slide2(self.material, p=p, **kw)


def _leer_ensayos(ensayos):
    try:
        s3, s1 = np.asarray(ensayos["s3"], float).ravel(), np.asarray(ensayos["s1"], float).ravel()
    except (TypeError, KeyError, IndexError):
        raise TypeError("ensayos debe ser un dict (o DataFrame) con claves 's3' y 's1' (σ′3 y σ′1 en la falla, MPa).")
    if len(s3) != len(s1) or len(s3) == 0:
        raise ValueError("ensayos: 's3' y 's1' deben tener la misma longitud (≥ 1).")
    return s3, s1


def envolvente_diseno(clase, e_lab, e_campo, D_lab, D_campo, ensayos=None, sn=None, representa="tipo",
                      tope_reposo=None, permitir_extrapolacion=False, forma=FORMA, n=40000, seed=0,
                      supuesto_escala="general"):
    """Envolvente de diseño con el orden de operaciones impuesto:
      1. previa de la clase a la relación de vacíos de LABORATORIO e_lab (la de las probetas);
      2. si hay ensayos: chequeo de conflicto y actualización con ellos (actualizar_sitio, un set a e_lab);
      3. densidad: Δe = e_campo − e_lab;
      4. escala: D_lab → D_campo (dmax, mm), βD con supuesto_escala;
      5. percentiles P50 y P05 de la envolvente MEDIA (puntual=False);
      6. sobre la σ′n máxima de los ensayos del sitio, el menor entre el percentil actualizado y el de la previa (ronda 6:
         en la validación por laboratorio, la actualización con ensayos a baja tensión dejó 14 % de los ensayos a σ′n ≥ 2 MPa
         bajo el P05; con esta regla, 4 %).
    Actualizar después de desplazar a campo devuelve la envolvente a la resistencia de laboratorio (lado inseguro).

    clase: «buena»/«moderada»/«baja» o «good»/«moderate»/«low». ensayos: dict o DataFrame con 's3' y 's1' (σ′3 y σ′1
    en la falla, MPa), triaxiales drenados del material a e_lab. La conversión σ′3, σ′1 → σ′n, τ (Ecs. 13–16 de
    Cylwik et al., 2025) usa m = mediana de la pendiente local d ln τ / d ln σ′n de la previa a σ′n = 1 MPa, acotada a
    [0.5, 1.0] (_m_conversion; la misma regla en actualizar y actualizar_sitio).
    representa: «tipo» (por defecto): la actualización representa el tipo de roca, no solo la muestra ensayada; se
    devuelve la envolvente de un set NUEVO del mismo laboratorio (efecto de laboratorio actualizado + varianza entre
    sets repuesta). «muestra»: posterior del set ensayado (más estrecha).
    sn: σ′n (MPa) de la tabla; por defecto SN_TABLA (0.05–8 MPa). σ′n > 8 MPa: ValueError salvo
    permitir_extrapolacion=True (con aviso). tope_reposo (°): φ′s ≤ tope para σ′n < 0.1 MPa (None = sin tope).
    Los avisos se emiten y además se devuelven en .avisos. Devuelve un Diseno."""
    import pandas as pd
    clase = _clase(clase)
    if representa not in ("tipo", "muestra"):
        raise ValueError("representa debe ser «tipo» o «muestra».")
    sn = np.atleast_1d(np.asarray(SN_TABLA if sn is None else sn, float))
    if np.any(sn <= 0):
        raise ValueError("σ′n debe ser > 0.")
    _validar_sn_max(float(sn.max()), permitir_extrapolacion)
    s3 = s1 = None
    if ensayos is not None:
        s3, s1 = _leer_ensayos(ensayos)
    with warnings.catch_warnings(record=True) as rec:
        warnings.simplefilter("always")
        _aviso_baja_tension(float(sn.min()), tope_reposo)
        diag = p = None
        if s3 is None:                                                    # 1. previa a e_lab
            warnings.warn("Sin ensayos del sitio: envolvente previa de la clase (laboratorio y material nuevos).", stacklevel=2)
            mat = previa(clase, e_lab, forma, n=n, seed=seed, D=D_lab)
        else:                                                             # 1–2. previa a e_lab + actualización
            mats, dgs = actualizar_sitio([dict(calidad=clase, e=e_lab, s3=s3, s1=s1, D=D_lab)], [(clase, e_lab, D_lab)], forma, n=n, seed=seed)
            mat = _restringir(mats[1] if representa == "tipo" else mats[0])
            diag = dgs[0]; p = diag["p_conflicto"]
        mat = densidad(mat, e_campo - e_lab)                              # 3. densidad
        mat = escala(mat, D_lab, D_campo, supuesto=supuesto_escala)       # 4. escala
        q = percentiles(sn, mat, (50, 5), puntual=False)                  # 5. envolvente media
        if s3 is not None:                                                # 6. sobre el rango ensayado manda la previa si es menor
            sobre = sn > diag["sn_max"]
            if np.any(sobre):
                m0 = escala(densidad(_restringir(previa(clase, e_lab, forma, n=n, seed=seed + 11, D=D_lab)), e_campo - e_lab),
                            D_lab, D_campo, supuesto=supuesto_escala)
                q0 = percentiles(sn, m0, (50, 5), puntual=False)
                for k_ in (50, 5):
                    q[k_] = np.where(sobre, np.minimum(q[k_], q0[k_]), q[k_])
                diag = dict(diag, previa_gobierna=[float(v) for v in sn[sobre & (q0[5] <= q[5])]])
    avisos = list(dict.fromkeys(str(w.message) for w in rec))
    for w in rec:                                                         # no se silencian: se re-emiten
        warnings.warn(w.message, w.category, stacklevel=2)
    mat.notas.append(f"envolvente_diseno: representa = {representa}")
    f50, f05 = _con_tope(sn, q[50], tope_reposo), _con_tope(sn, q[5], tope_reposo)
    tabla = pd.DataFrame(dict(sn_MPa=sn, phi_P50=f50, phi_P05=f05,
                              tau_P50=sn * np.tan(np.radians(f50)), tau_P05=sn * np.tan(np.radians(f05))))
    return Diseno(tabla, p, avisos, mat, diag, tope_reposo)


design_envelope = envolvente_diseno       # alias en inglés
