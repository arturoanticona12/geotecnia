"""Pruebas de la implementación de referencia de Leps 3.0 probabilístico (pytest)."""
import math, warnings
import numpy as np
import pytest
import leps3 as L


@pytest.mark.parametrize("cal,e,leps2", [("buena", 0.30, 47.0), ("moderada", 0.45, 41.0), ("baja", 0.60, 35.0)])
def test_previa_reproduce_tabla(cal, e, leps2):
    # la mediana de φ′1 de la previa queda a menos de 1° de la tabla de Leps 2.0 (φe0 − 20e)
    assert L.phi1_mediana(L.previa(cal, e)) == pytest.approx(leps2, abs=1.0)


def test_anclaje_mediana():
    pr = L.previa("moderada", 0.45)
    p = L.percentiles([L.S0], pr, (50,), material_nuevo=False, n=200000)[50][0]
    assert p == pytest.approx(L.phi1_mediana(pr), abs=0.15)


def test_percentiles_ordenados_y_banda_crece():
    pr = L.previa("baja", 0.5)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        q = L.percentiles([1.0, 10.0], pr, (10, 50, 90))
    assert np.all(q[10] < q[50]) and np.all(q[50] < q[90])
    assert (q[90][1] - q[10][1]) > (q[90][0] - q[10][0])      # la incertidumbre crece lejos del anclaje


def test_m_no_supera_1():
    est = L.Estado(np.array([0.9, 1.05]), np.diag([0.01, 0.0009]))
    _, m = L.muestras(est, 50000)
    assert m.max() <= 1.0 + 1e-12


def test_actualizacion_recupera_parametros():
    # ensayos sintéticos de un material con φ′1 = 44°, m = 0.88: la posterior se acerca a los valores verdaderos
    th_v, m_v = math.log(math.tan(math.radians(44))), 0.88
    s3 = np.array([0.3, 0.6, 1.2, 2.4]); sn = np.logspace(math.log10(0.6), math.log10(5), 200)
    tau = L.S0 * np.exp(th_v + m_v * np.log(sn / L.S0))
    # círculo tangente: σ3 = σn − τ/tan β, σ1 = σn + τ tan β
    tphi = m_v * tau / sn; b = np.arctan(tphi) / 2 + np.pi / 4
    s3c, s1c = sn - tau / np.tan(b), sn + tau * np.tan(b)
    s1 = np.interp(s3, s3c, s1c)
    po = L.actualizar(L.previa("moderada", 0.45), s3, s1)
    assert L.phi1_mediana(po) == pytest.approx(44.0, abs=0.6) and po.media[1] == pytest.approx(0.88, abs=0.04)
    assert po.cov[0, 0] < L.SIGMA[0, 0] / 4                    # la incertidumbre baja con los ensayos


def test_aviso_extrapolacion():
    with pytest.warns(UserWarning):
        L.percentiles([12.0], L.previa("moderada", 0.45))


def test_tabla_slide2():
    t = L.tabla_slide2(L.previa("moderada", 0.45), p=50)
    assert t[0] == (0.0, 0.0) and all(b > a for (_, a), (_, b) in zip(t[1:-1], t[2:]))
