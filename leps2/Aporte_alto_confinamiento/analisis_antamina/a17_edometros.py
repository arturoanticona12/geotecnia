"""Edómetros de desmonte de Antamina verificados contra los PDF (verificacion_ocr/edometros_verificados.csv, 2026-10-10):
compresibilidad Cc (pendiente de e frente a log σ′v) en la rama de carga, en los mismos rangos que el perfil A de a13
(0.2–0.8 MPa y 1.2–4.8 MPa), y e a 300 y 700 m de profundidad con la ley de a13 (e = 0.65 en superficie, γ con Gs 2.75 y w 5 %)
usando el par de Cc de cada edómetro. Escribe a17_edometros.json."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; V = AQ.parent / "datos_antamina" / "verificacion_ocr"
E = pd.read_csv(V / "edometros_verificados.csv")
GS, W, GW, ETOP, SA = 2.75, 0.05, 9.81, 0.45, 0.05   # e base 0.45 (2026-10-10)
gam = lambda e: GS * GW * (1 + W) / (1 + e) / 1000.0


def cc(q, lo, hi):
    s = q[(q.sigma_v_kPa >= lo) & (q.sigma_v_kPa <= hi)]
    return float(-np.polyfit(np.log10(s.sigma_v_kPa), s.e, 1)[0]) if len(s) >= 2 and s.sigma_v_kPa.max() / s.sigma_v_kPa.min() > 1.5 else None


def perfil(c1, c2, zs=(300, 700)):
    e_ = lambda sv: ETOP - c1 * np.log10(max(sv, SA) / SA) if sv <= 1.0 else ETOP - c1 * np.log10(1.0 / SA) - c2 * np.log10(sv / 1.0)
    z = np.linspace(0, max(zs), 1401); sv = 0.0; e = ETOP; out = {}
    for i in range(1, len(z)):
        sv += gam(e) * (z[i] - z[i - 1]); e = e_(sv)
        if int(round(z[i])) in zs and abs(z[i] - round(z[i])) < 1e-9:
            out[int(round(z[i]))] = float(e)
    return out


res = []
for k, q in E.groupby("ensayo_id", sort=False):
    q = q[q.rama.astype(str).str.startswith("carga")].sort_values("sigma_v_kPa")
    q = q[pd.to_numeric(q.e, errors="coerce").notna()].copy(); q["e"] = q.e.astype(float)
    c1, c2 = cc(q, 200, 800), cc(q, 1200, 4800)
    r0 = E[E.ensayo_id == k].iloc[0]
    res.append(dict(ensayo=k, fuente=r0.fuente_id, litologia=r0.litologia, diametro_mm=r0.diametro_mm, Dmax_mm=r0.Dmax_mm, Gs=r0.Gs, Gs_origen=r0.Gs_origen,
                    e0=float(r0.e0) if pd.notna(pd.to_numeric(r0.e0, errors="coerce")) else None, e0_origen=r0.e0_origen,
                    sv_max=float(q.sigma_v_kPa.max()), Cc1=c1, Cc2=c2, perfil=perfil(c1, c2) if (c1 and c2) else None))
for r in res:
    print(f"{r['ensayo'][:42]:42s} {str(r['litologia'])[:10]:10s} D {r['diametro_mm']} e0 {r['e0']}  Cc {r['Cc1']}/{r['Cc2']}  σv máx {r['sv_max']:.0f}  e(300,700) {r['perfil']}")
json.dump(res, open(AQ / "a17_edometros.json", "w", encoding="utf-8"), indent=1, ensure_ascii=False, default=str)
