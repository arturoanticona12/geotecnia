"""Pruebas de la implementación de referencia de HiBER (pytest)."""
import math, warnings
import numpy as np
import pytest
import lepsp as L

warnings.simplefilter("ignore")


@pytest.mark.parametrize("cal,e,leps2", [("buena", 0.30, 47.0), ("moderada", 0.45, 41.0), ("baja", 0.60, 35.0)])
def test_mediana_cercana_a_leps2(cal, e, leps2):
    # la mediana de φ′1 queda a menos de 2° de la tabla de Leps 2.0 (φe0 − 20e) en el rango usual de e. Ronda 6: Leps 2.0
    # se ajustó a los tamaños típicos de la base (Dmax mediano ≈ 38 mm); con el término ln Dmax la comparación justa es a
    # ese tamaño (a 100 mm, la referencia de la Tabla 3, la clase baja con e = 0.6 queda 2.4° por encima).
    assert abs(L.phi1_mediana(L.previa(cal, e, n=20000, D=38.0)) - leps2) < 2.0


def test_restriccion_pendiente_local():
    mat = L.previa("baja", 0.3, n=20000)
    xs = np.log(np.geomspace(0.05, L.SN_USO_MAX, 13) / L.S0)
    assert np.all(L._pendiente(mat, xs) <= 1.0 + 1e-9)


def test_percentiles_ordenados_y_envolvente_media_mas_estrecha():
    mat = L.previa("moderada", 0.45, n=20000)
    # puntual=True explícito: desde que el defecto de percentiles() es la envolvente media, q y qm serían idénticos
    q = L.percentiles([1.0, 5.0], mat, (10, 50, 90), puntual=True); qm = L.percentiles([1.0, 5.0], mat, (10, 90), puntual=False)
    assert np.all(q[10] < q[50]) and np.all(q[50] < q[90])
    assert np.all((qm[90] - qm[10]) <= (q[90] - q[10]) + 1e-9)


def _sintetico(th, m, s3):
    sn = np.logspace(-1.5, 1.2, 400); tau = L.S0 * np.exp(th + m * np.log(sn / L.S0))
    b = np.arctan(m * tau / sn) / 2 + np.pi / 4
    s3c, s1c = sn - tau / np.tan(b), sn + tau * np.tan(b)
    return np.interp(s3, s3c, s1c)


def test_actualizacion_recupera_y_reduce_incertidumbre():
    th, m = math.log(math.tan(math.radians(44))), 0.88
    s3 = np.array([0.2, 0.5, 1.0, 2.0]); s1 = _sintetico(th, m, s3)
    pr = L.previa("moderada", 0.45, n=20000)
    po, dg = L.actualizar(pr, s3, s1)                                 # regla por defecto: solo nivel
    assert dg["modo"] == "solo nivel" and not dg["conflicto"]
    assert abs(L.phi1_mediana(po) - 44.0) < 1.0
    sd0 = lambda mt: np.std(L._media(mt, [0.0])[:, 0])                  # dispersión de la envolvente en σ0
    assert sd0(po) < 0.5 * sd0(pr)
    pc, dc = L.actualizar(pr, s3, s1, conjunta=True)                  # opcional: actualización conjunta
    assert dc["modo"] == "nivel y pendiente" and abs(np.median(L._pendiente(pc, [math.log(0.7 / L.S0)])) - 0.88) < 0.05


def test_rango_estrecho_actualiza_solo_theta():
    th, m = math.log(math.tan(math.radians(43))), 0.87
    s3 = np.array([0.8, 1.0, 1.2]); s1 = _sintetico(th, m, s3)
    po, dg = L.actualizar(L.previa("moderada", 0.45, n=20000), s3, s1)
    assert dg["modo"] == "solo nivel"


def test_conflicto_detectado():
    th, m = math.log(math.tan(math.radians(60))), 0.86      # material muy distinto de su clase
    s3 = np.array([0.3, 1.0, 3.0]); s1 = _sintetico(th, m, s3)
    with pytest.warns(UserWarning):
        _, dg = L.actualizar(L.previa("baja", 0.6, n=20000), s3, s1)
    assert dg["conflicto"]


def test_escala_general_sin_sesgo_y_ensancha():
    mat = L.previa("moderada", 0.45, n=20000)
    mg = L.escala(mat, 150, 1000, supuesto="general"); md = L.escala(mat, 150, 1000, supuesto="datos")
    assert abs(np.median(mg.th) - np.median(mat.th)) < 0.01            # ronda 3: media cero (efecto no detectado)
    assert np.std(mg.th) > np.std(mat.th) and np.median(md.th) > np.median(mg.th)


def test_acotada_efecto_densidad_decrece_con_tension():
    mat = L.previa("moderada", 0.35, "acotada", n=20000); suelto = L.densidad(mat, 0.30)
    p0 = L.percentiles([0.3, 15.0], mat, (50,), puntual=False)[50]; p1 = L.percentiles([0.3, 15.0], suelto, (50,), puntual=False)[50]
    caida = p0 - p1
    assert caida[0] > 0 and caida[1] > 0 and caida[1] < 0.6 * caida[0]


def test_acotada_mas_alta_que_cuadratica_a_alta_tension():
    a = L.percentiles([15.0], L.previa("moderada", 0.55, "acotada", n=20000), (50,), puntual=False)[50][0]
    b = L.percentiles([15.0], L.previa("moderada", 0.55, "x2", n=20000), (50,), puntual=False)[50][0]
    assert a > b


def test_sitio_laboratorio_comun_y_solo_nivel():
    th, m = math.log(math.tan(math.radians(42))), 0.86
    s3 = np.array([0.5, 1.0, 2.0]); s1 = _sintetico(th, m, s3)
    mats, dg = L.actualizar_sitio([dict(calidad="baja", e=0.35, s3=s3, s1=s1)], [("baja", 0.35)], n=20000)
    assert len(mats) == 2 and len(dg) == 1
    sd0 = lambda mt: np.std(L._media(mt, [0.0])[:, 0])
    assert sd0(mats[0]) < sd0(mats[1])                     # el set ensayado queda más acotado que el nuevo
    assert abs(L.phi1_mediana(mats[0]) - 42.0) < 1.5


def test_forma_potencia_mas_baja_a_alta_presion():
    a = L.percentiles([15.0], L.previa("moderada", 0.45, "x2", n=20000), (50,))[50][0]
    b = L.percentiles([15.0], L.previa("moderada", 0.45, "potencia", n=20000), (50,))[50][0]
    assert b < a


def test_aviso_extrapolacion():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always"); L.percentiles([12.0], L.previa("moderada", 0.45, n=5000))
    assert any("extrapolación" in str(x.message) for x in w)


def test_tabla_slide2_monotona():
    t = L.tabla_slide2(L.previa("moderada", 0.45, n=10000), p=10)
    assert t[0] == (0.0, 0.0) and all(b2 > b1 for (_, b1), (_, b2) in zip(t[1:-1], t[2:]))


# --- envolvente_diseno, dominio de validez y mal uso -------------------------------------------------------------

S3_EJ = np.array([0.3, 0.7, 1.2, 2.0])


def _ensayos_ej():
    return dict(s3=S3_EJ, s1=_sintetico(math.log(math.tan(math.radians(42))), 0.86, S3_EJ))


def test_envolvente_diseno_respeta_el_orden():
    ens, N, sn = _ensayos_ej(), 20000, np.array([0.1, 0.5, 1.0, 3.0, 6.0])
    r = L.envolvente_diseno("baja", 0.35, 0.65, 150, 1000, ensayos=ens, sn=sn, n=N, representa="tipo")
    # a mano, en el orden correcto: previa/actualización a e_lab → densidad → escala → envolvente media
    mats, dg = L.actualizar_sitio([dict(calidad="baja", e=0.35, s3=ens["s3"], s1=ens["s1"], D=150)], [("baja", 0.35, 150)], n=N)
    mt = L.escala(L.densidad(L._restringir(mats[1]), 0.30), 150, 1000)
    q = L.percentiles(sn, mt, (50, 5), puntual=False)
    # paso 6 (ronda 6): sobre la σ′n máxima de los ensayos, el menor entre actualizado y previa
    m0 = L.escala(L.densidad(L._restringir(L.previa("baja", 0.35, n=N, seed=11, D=150)), 0.30), 150, 1000)
    q0 = L.percentiles(sn, m0, (50, 5), puntual=False); sobre = sn > dg[0]["sn_max"]
    assert np.any(sobre)
    for k in (50, 5):
        q[k] = np.where(sobre, np.minimum(q[k], q0[k]), q[k])
    assert np.allclose(r.tabla["phi_P50"], q[50]) and np.allclose(r.tabla["phi_P05"], q[5])
    assert r.p_conflicto == pytest.approx(dg[0]["p_conflicto"])
    # orden invertido: desplazar a campo y actualizar después → vuelve a la resistencia de laboratorio (inseguro)
    mi = L.escala(L.densidad(L.previa("baja", 0.35, n=N), 0.30), 150, 1000)
    with pytest.warns(UserWarning, match="Orden de operaciones"):
        mi, _ = L.actualizar(mi, ens["s3"], ens["s1"])
    qi = L.percentiles(sn, mi, (5,), puntual=False)[5]
    assert np.all(qi > r.tabla["phi_P05"].to_numpy() + 2.0)


def test_tabla_slide2_sobre_8_mpa_falla():
    mat = L.previa("moderada", 0.45, n=5000)
    with pytest.raises(ValueError):
        L.tabla_slide2(mat, sn_max=12.0)
    with pytest.warns(UserWarning, match="extrapolación"):
        L.tabla_slide2(mat, sn_max=12.0, permitir_extrapolacion=True)
    with pytest.raises(ValueError):
        L.envolvente_diseno("moderada", 0.45, 0.45, 150, 150, sn=[1.0, 10.0], n=5000)


def test_aviso_un_solo_ensayo():
    ens = _ensayos_ej()
    with pytest.warns(UserWarning, match="1 ensayo"):
        L.actualizar(L.previa("baja", 0.35, n=5000), ens["s3"][:1], ens["s1"][:1])
    with pytest.warns(UserWarning, match="1 ensayo"):
        r = L.envolvente_diseno("low", 0.35, 0.35, 150, 150, ensayos=dict(s3=ens["s3"][:1], s1=ens["s1"][:1]), n=5000)
    assert any("1 ensayo" in a for a in r.avisos)


def test_nombres_de_clase_en_ingles():
    a, b = L.previa("low", 0.45, n=5000), L.previa("baja", 0.45, n=5000)
    assert L.phi1_mediana(a) == pytest.approx(L.phi1_mediana(b))
    assert L.envolvente_diseno("Low", 0.45, 0.45, 150, 150, n=5000).tabla.shape[0] == len(L.SN_TABLA)
    with pytest.raises(ValueError):
        L.previa("mala", 0.45)


def test_representa_tipo_mas_ancho_que_muestra():
    ens = _ensayos_ej()
    rt = L.envolvente_diseno("low", 0.35, 0.65, 150, 1000, ensayos=ens, representa="tipo", n=20000)
    t = rt.tabla; m = L.envolvente_diseno("low", 0.35, 0.65, 150, 1000, ensayos=ens, representa="muestra", n=20000).tabla
    dentro = (t["sn_MPa"] <= rt.diagnostico["sn_max"]).to_numpy()      # sobre el rango ensayado ambas pueden ser la previa
    assert dentro.sum() >= 3
    assert np.all(t["phi_P05"][dentro] < m["phi_P05"][dentro]) and np.all(t["phi_P05"] <= m["phi_P05"] + 1e-9)
    assert np.all((t["phi_P50"] - t["phi_P05"])[dentro] > (m["phi_P50"] - m["phi_P05"])[dentro])


def test_tope_reposo_y_aviso_e_suelta():
    mat = L.densidad(L.previa("baja", 0.35, n=5000), 0.30)            # e = 0.65 > 0.55
    t0 = L.tabla_slide2(mat, sn_min=0.05); t1 = L.tabla_slide2(mat, sn_min=0.05, tope_reposo=38.0)
    for (s, a), (_, b) in zip(t0[1:], t1[1:]):
        if s < 100.0:                                                 # kPa
            assert b <= s * math.tan(math.radians(38.0)) + 1e-3 and b <= a
        else:
            assert a == b
    with pytest.warns(UserWarning, match="0.55"):
        L.percentiles([5.0], mat)
