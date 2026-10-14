"""Contenido real de relave en las mezclas WSP 2024 y granulometría de ensayo exacta.
Datos: desmonte IDIEM-A p.93 (Figura 3), relave IDIEM-F p.355. Gs: WSP Tabla 3-5 p.11-12; IDIEM p.97, 110, 271.
Hipótesis A: r nominal sobre la masa total (desmonte <4" + relave).
Hipótesis B: r aplicado solo a la fracción < 3/4" ("se trabaja el material integral bajo 3/4", IDIEM p.108/142/231/267),
             de modo que la curva sobre 3/4" queda igual a la del desmonte cortado en 4"."""
import math

sz = [101.6, 76.2, 63.5, 50.8, 38.1, 25.4, 19.0, 9.52, 4.76, 2.0, 0.84, 0.42, 0.25, 0.11, 0.074]
des = [96.2, 93.2, 89.6, 84.2, 77.0, 67.0, 57.4, 39.3, 25.7, 20.4, 15.6, 12.4, 10.4, 7.5, 6.6]
rel = {9.52: 100.0, 4.76: 99.9, 2.0: 99.7, 0.84: 96.2, 0.42: 81.8, 0.25: 57.5, 0.11: 18.7, 0.074: 12.4}
Pd = [p / 96.2 * 100 for p in des]               # desmonte cortado en 4"
Pt = [rel.get(s, 100.0) for s in sz]
i34 = sz.index(19.0)


def interpD(P, target):
    for k in range(len(sz) - 1):
        a, b = P[k], P[k + 1]
        if a >= target >= b:
            f = (target - b) / (a - b) if a != b else 0
            return math.exp(math.log(sz[k + 1]) + f * (math.log(sz[k]) - math.log(sz[k + 1])))
    return float('nan')


def params(P):
    D10, D30, D50, D60 = (interpD(P, t) for t in (10, 30, 50, 60))
    n4 = P[sz.index(4.76)]
    fin = P[-1]
    return dict(D10=D10, D30=D30, D50=D50, D60=D60, Cu=D60 / D10, Cc=D30 ** 2 / (D60 * D10),
                pasa_N4=n4, grava=100 - n4, arena=n4 - fin, finos=fin)


Gs_c, Gs_t, Gs_f_des = 2.87, 3.46, 2.80
print('Desmonte <4" (C4):', {k: round(v, 3) for k, v in params(Pd).items()})
for name, r, gs_lt4, gs_glob in [('C1', .22, 3.07, 2.93), ('C2', .18, 2.97, 2.90), ('C3', .15, 2.94, 2.89)]:
    A = [(1 - r) * pd + r * pt for pd, pt in zip(Pd, Pt)]
    B = [pd if k <= i34 else (1 - r) * pd + r * Pd[i34] * pt / 100 for k, (pd, pt) in enumerate(zip(Pd, Pt))]
    relB = r * Pd[i34]
    print(f'\n{name}: relave en masa total  A={r*100:.1f} %  B={relB:.2f} %  (relación intrusivo:relave B = {(100-relB)/relB:.2f}:1)')
    for lab, P in (('A', A), ('B', B)):
        pr = params(P)
        P4 = pr['pasa_N4'] / 100
        gsg = 1 / ((1 - P4) / Gs_c + P4 / gs_lt4)
        # fracción de relave dentro del pasante N°4 implícita
        des_lt4 = (1 - (r if lab == 'A' else relB / 100)) * 0  # no usado
        print(f'  {lab}: ' + ' '.join(f'{k}={v:.3g}' for k, v in pr.items()) + f' | Gs global recalculado={gsg:.3f} (informe {gs_glob})')
        print('     pasante por tamiz:', ' '.join(f'{s}:{p:.1f}' for s, p in zip(sz, P)))
    # relave dentro del pasante N4 según Gs medido (<N4) vs hipótesis
    ft_meas = (1 / Gs_f_des - 1 / gs_lt4) / (1 / Gs_f_des - 1 / Gs_t)
    k4 = sz.index(4.76)
    ftA = r * 99.9 / A_k4 if (A_k4 := (1 - r) * Pd[k4] + r * 99.9) else 0
    ftB = relB * 0.999 / ((1 - r) * Pd[k4] + relB * 0.999)
    print(f'  fracción de relave en el pasante N4: según Gs<N4 medido={ft_meas:.3f}; A={ftA:.3f}; B={ftB:.3f}')
