"""Sensibilidad del diagnóstico de conflicto previa–sitio al criterio de falla (ronda 3).
Criterios: máximo desviador (el de la base de calibración), q a εa = 15 % y q a εa = 10 % (rama de carga virgen),
leídos de las curvas tabuladas de los informes (curvas_sitio/curvas_sitio.csv). Para cada set: p del conflicto, razón
de esfuerzos y pendiente local libre (ajuste log–log). Escribe a7_criterio_falla.json."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; sys.path.insert(0, str(AQ.parent / "leps3"))
import lepsp as L  # noqa: E402

C = pd.read_csv(AQ / "curvas_sitio" / "curvas_sitio.csv")
D = pd.read_csv(AQ / "drenados_utilizables.csv", low_memory=False)
D = D[D.escala.isin(["0.6 m", "1.0 m"]) & (D.relave_pct_masa_total.fillna(0) == 0)].copy(); D["e_use"] = D.e0_adoptado.fillna(D.e0)
CAL = {"Mármol": "baja", "Hornfels": "moderada", "Intrusivo": "baja"}
out = {}
for crit, col in (("qmax", "qmax"), ("q15", "q15"), ("q10", "q10")):
    sets, nom = [], []
    for sid, g in C.groupby("set_a", sort=False):
        dd = D[D.set_a == sid]; lit = dd.litologia.iloc[0]
        s3 = g.s3_MPa.values; s1 = s3 + g[col].values
        sets.append(dict(calidad=CAL[lit], e=float(dd.e_use.iloc[0]), s3=s3, s1=s1, usar=True)); nom.append(sid)
    _, dg = L.actualizar_sitio(sets, n=4000, seed=1)
    res = {}
    for sid, s, dg_ in zip(nom, sets, dg):
        sn, tau = L._a_sn_tau(s["s3"], s["s1"], 0.86)
        m_libre = float(np.polyfit(np.log(sn), np.log(tau), 1)[0])
        phis = np.degrees(np.arctan(tau / sn))
        res[sid] = dict(p=float(dg_["p_conflicto"]), m_libre=m_libre, phis=[round(float(v), 1) for v in phis])
    out[crit] = res
    print(f"\n[{crit}]")
    for sid, r in res.items():
        print(f"  {sid:38s} p = {r['p']:.4f} {'(conflicto)' if r['p'] < 0.05 else '':12s} m libre = {r['m_libre']:.3f}  φ′s = {r['phis']}")
json.dump(out, open(AQ / "a7_criterio_falla.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
