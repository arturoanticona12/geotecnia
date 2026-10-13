"""Tabla completa de ensayos de resistencia de desmonte de Antamina con su uso en el memo (comentario WA 2026-10-12: «una tabla
así [la de ensayos del ajuste] con toda la data usada, no usada, contraste»). Mismo universo que el inventario (Tabla 1): no
entran las mezclas con relave (fuera del alcance de Leps 2.0; decisión del usuario de no mencionarlas), los edómetros (tienen
su tabla) ni los ensayos de permeabilidad. Esfuerzos efectivos de falla con el criterio homogéneo de la base (CD: máximo
desviador; CU: máxima oblicuidad, o máximo desviador si la fuente no permite otra cosa; corte directo: τ pico); σ′n y φ′s de los
triaxiales con la conversión de Leps 2.0 y la m de la curva propuesta, como en la Tabla 2. Control: los ensayos del ajuste deben
reproducir a10_puntos.csv. Escribe a27_ensayos_todos.csv."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent
E = pd.read_csv(AQ.parent / "datos_antamina" / "base" / "ensayos.csv", low_memory=False)
A = pd.read_csv(AQ / "ensayos_ajuste.csv", low_memory=False)
# revisión 10 (2026-10-12): m de la curva simple (a33) y puntos del ajuste calculados aquí (e0 con D854, conversión con esa m)
MC = json.load(open(AQ / "a33_curva_propuesta.json", encoding="utf-8"))["parametros"]["m_a"]


def a_tau_sn(s3, s1, m):                                  # conversión de Leps 2.0 (Ecs. 13–16), la de a9 y a16
    D, Sm = s1 - s3, s1 + s3
    sp = D / Sm if abs(m - 1) < 1e-6 else (np.sqrt(4 * m * (m - 1) * D ** 2 + Sm ** 2) - Sm) / (2 * (m - 1) * D)
    return Sm / 2 - D / 2 * sp, D / 2 * np.sqrt(1 - sp ** 2)


AJ = set(zip(A.fuente_id, A.set_id, A.ensayo_id))


def uso(r):
    k = (r.fuente_id, r.set_id, r.ensayo_id)
    if k in AJ:
        return "Ajuste de la curva propuesta", ""
    if r.fuente_id == "A2024":
        return "Contraste", "triaxial no drenado (CU), máxima oblicuidad"
    if r.fuente_id == "G2010":
        return ("Contraste", "triaxial no drenado (CU), máximo desviador") if str(r.set_id).startswith("G2010-A") else \
               ("No usado", "material chancado (fase B)")
    if isinstance(r.duplicado_de, str) and r.duplicado_de:
        return "No usado", "duplicado de Golder Associates Perú (2012); se usa el original"
    if "cíclico" in str(r.tipo_ensayo_std):
        return "No usado", "carga cíclica (compresión y extensión) previa a la carga monótona"
    return None, None


filas = []
# ensayos del ajuste: los mismos valores de la Tabla 2 (ensayos_ajuste.csv y a10_puntos.csv, en el mismo orden)
for _, r in A.iterrows():
    ds = r.tipo == "DS"
    sn_, tau_ = (r.sn_ds, r.tau_ds) if ds else a_tau_sn(r.s3, r.s1, MC); p = pd.Series(dict(sn=sn_, phis=np.degrees(np.arctan(tau_ / sn_))))
    filas.append(dict(fuente_id=r.fuente_id, set_id=r.set_id, ensayo_id=r.ensayo_id, litologia=r.litologia,
                      ensayo="Corte directo CD" if ds else str(r.tipo_ensayo_std), D_m=0.31 if ds else r.diametro_mm / 1000,
                      Dmax_mm=r.Dmax_mm, e0=r.e0_adoptado, s3=np.nan if ds else r.s3, s1=np.nan if ds else r.s1, sn=p.sn,
                      tau=p.sn * np.tan(np.radians(p.phis)), phis=p.phis, eps_a=np.nan if ds else r.eps_axial_falla_pct,
                      criterio="CD: τ pico" if ds else "CD: máximo desviador",
                      uso="Ajuste de la curva propuesta",              # con las mezclas desde el 2026-10-12
                      motivo="", pagina=r.get("pagina", "")))
for _, r in E.iterrows():
    if "Edómetro" in str(r.tipo_ensayo_std) or "Permeabilidad" in str(r.tipo_ensayo_std):
        continue
    if (r.fuente_id, r.set_id, r.ensayo_id) in AJ or r.fuente_id == "A2024DS":   # ya incluidos arriba (los 15 cortes directos)
        continue
    u, mot = uso(r)
    if u is None:                                       # mezclas con relave: fuera del universo del inventario
        continue
    ds = str(r.tipo_ensayo_std).startswith("Corte directo")
    if ds:
        sn, tau = r.sigma_n_falla_kPa / 1000, r.tau_falla_kPa / 1000; s3 = s1 = np.nan; D = 0.31
    else:
        s3, s1 = r.sigma3f_kPa_std / 1000, r.sigma1f_kPa_std / 1000; sn, tau = a_tau_sn(s3, s1, MC); D = r.diametro_mm / 1000
    filas.append(dict(fuente_id=r.fuente_id, set_id=r.set_id, ensayo_id=r.ensayo_id, litologia=r.litologia, ensayo=r.tipo_ensayo_std,
                      D_m=D, Dmax_mm=r.Dmax_mm, e0=r.e0_adoptado, s3=s3, s1=s1, sn=sn, tau=tau, phis=np.degrees(np.arctan(tau / sn)),
                      eps_a=r.eps_axial_falla_pct, criterio=r.criterio_falla_std, uso=u, motivo=mot, pagina=r.pagina))
T = pd.DataFrame(filas)
# e0 de los CU de Anddes (2024): la de cada probeta CU (ρd inicial y Gs D854 de Golder 2010), igual que la Fig. 4 (a16), no la de las rumas
_C = pd.read_csv(AQ / "a16_contraste.csv"); _C = _C[_C.grupo.str.startswith("CU Anddes")]
_mp = {str(k)[:7]: v for k, v in _C.groupby("set").e.first().items()}                                 # una e por set (ρd inicial del set)
_k = (T.fuente_id == "A2024") & (T.uso == "Contraste")
_new = [_mp.get(str(r.set_id)[:7]) for _, r in T[_k].iterrows()]   # «Pila 01», «Ruma 02»...
assert all(v is not None for v in _new), "CU de Anddes sin pareja en a16"
T.loc[_k, "e0"] = _new
print(f"m de la conversión: {MC:.3f}; ensayos del ajuste: {len(A)}")
T.to_csv(AQ / "a27_ensayos_todos.csv", index=False)
print(T.groupby(["uso", "motivo"]).size().to_string())
print("total", len(T))
