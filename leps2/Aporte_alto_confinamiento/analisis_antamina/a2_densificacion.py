"""Hipótesis: la densificación durante la consolidación aplana la envolvente a alta presión.
Prueba: dentro de cada set, ¿la variación del φ′1 implícito (marco m = 0.86) sigue a la relación de vacíos al inicio del
corte (e_c) con una pendiente ω cercana a la de Cylwik et al. (2025), 20° por unidad de e?"""
import sys, re, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8"); pd.set_option("display.width", 220)
AQUI = Path(__file__).parent
d = pd.read_csv(AQUI / "drenados_utilizables.csv", low_memory=False)
PA = 0.1013; S0 = 10 * PA
Gs = d.Gs_adoptado.astype(float)


def e_c(row):
    n = str(row.notas)
    if pd.notna(row.get("e_post_consol")):                       # G2010 y G2021: columna (con el Gs del informe)
        return float(row.e_post_consol) * row.Gs_adoptado / row.Gs if pd.notna(row.Gs) and row.Gs > 0 else float(row.e_post_consol)
    m = re.search(r"Tras consolidaci[oó]n:\s*gd=(\d+(?:\.\d+)?)\s*t/m3", n)          # G2012
    if m: return row.Gs_adoptado / float(m.group(1)) - 1
    m = re.search(r"e al inicio del corte\s*≈\s*(\d+(?:\.\d+)?)", n)                  # W2022 (Gs 2.75)
    if m: return float(m.group(1)) * row.Gs_adoptado / 2.75
    m = re.search(r"post-?consolidaci[oó]n[^0-9]{0,40}([12][.,]\d{2,3})\s*g/cm", n, re.I)   # IDIEM, WSP 2024
    if m: return row.Gs_adoptado / float(m.group(1).replace(",", ".")) - 1
    return np.nan


d["e_c"] = d.apply(e_c, axis=1)
print("e_c disponible:", d.groupby("fuente_id").e_c.apply(lambda s: f"{s.notna().sum()}/{len(s)}").to_dict())
# φ′1 implícito con m = 0.86, a partir del φ secante en principales (conversión lineal aproximada para el marco)
s3, s1 = d.s3, d.s1
phi = np.arcsin((s1 - s3) / (s1 + s3)); sn = (s1 + s3) / 2 - (s1 - s3) / 2 * np.sin(phi); tau = (s1 - s3) / 2 * np.cos(phi)
d["phi1_t"] = np.degrees(np.arctan(tau / (S0 ** 0.14 * sn ** 0.86)))
d["de"] = d.e_c - d.e0_adoptado
print(d.dropna(subset=["e_c"]).groupby("set_a").agg(n=("e_c", "size"), e0=("e0_adoptado", "first"), ec_min=("e_c", "min"), ec_max=("e_c", "max"),
                                                    phi1_min=("phi1_t", "min"), phi1_max=("phi1_t", "max")).round(3).to_string())
# regresión con efectos fijos por set: φ1_t − media(set) ~ ω·(e_c − media(set))  y alternativa con ln σ3
v = d.dropna(subset=["e_c"]).copy()
v = v[v.groupby("set_a").e_c.transform("size") >= 2]
v["y"] = v.phi1_t - v.groupby("set_a").phi1_t.transform("mean"); v["xe"] = v.e_c - v.groupby("set_a").e_c.transform("mean")
v["xs"] = np.log(v.s3) - v.groupby("set_a").s3.transform(lambda s: np.log(s).mean())


def ajuste(cols):
    X = v[cols].values; b, *_ = np.linalg.lstsq(X, v.y.values, rcond=None)
    r = v.y.values - X @ b; return b, 1 - np.sum(r ** 2) / np.sum(v.y.values ** 2)


be, r2e = ajuste(["xe"]); bs, r2s = ajuste(["xs"]); bb, r2b = ajuste(["xe", "xs"])
rng = np.random.default_rng(5); sets = v.set_a.unique(); boot = []
for _ in range(2000):
    vv = pd.concat([v[v.set_a == s] for s in rng.choice(sets, len(sets))])
    boot.append(np.linalg.lstsq(vv[["xe"]].values, vv.y.values, rcond=None)[0][0])
print(f"\nDentro de sets ({v.set_a.nunique()} sets, {len(v)} ensayos):")
print(f"  φ′1 ~ e_c:            ω = {-be[0]:.1f}°/unidad de e (IC 90 % {-np.percentile(boot, 95):.1f} a {-np.percentile(boot, 5):.1f}), R² = {r2e:.2f}")
print(f"  φ′1 ~ ln σ′3:         pendiente {bs[0]:+.2f}°/unidad ln, R² = {r2s:.2f}")
print(f"  φ′1 ~ e_c + ln σ′3:   ω = {-bb[0]:.1f}, pendiente ln σ′3 {bb[1]:+.2f}, R² = {r2b:.2f}")
print(f"  referencia Cylwik et al. (2025): ω = 20° (rango 15–25°)")
v.to_csv(AQUI / "densificacion.csv", index=False)

