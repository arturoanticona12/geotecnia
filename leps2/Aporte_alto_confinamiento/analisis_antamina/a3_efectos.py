"""Análisis 4–5: efectos de relave, escala y rotura; Antamina frente a la base mundial (Cylwik/Arrieta) a igual σ′n."""
import sys, json, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore"); sys.stdout.reconfigure(encoding="utf-8"); pd.set_option("display.width", 220)
AQUI = Path(__file__).parent; RAIZ = AQUI.parent
sys.path.insert(0, str(RAIZ / "analisis"))
from common import load_db  # noqa: E402
PA = 0.1013; S0 = 10 * PA
E = pd.read_csv(RAIZ / "datos_antamina" / "base" / "ensayos.csv", low_memory=False)
S = pd.read_csv(AQUI / "sets_ajuste.csv")
d = pd.read_csv(AQUI / "drenados_utilizables.csv", low_memory=False)
# relave efectivo por set (corrige la correspondencia de WSP 2024)
REL = {"WSP24_C1": 13.1, "WSP24_C2": 10.7, "WSP24_C3": 9.0, "WSP24_C4": 0.0}
for k, v in REL.items():
    S.loc[S.set_a.str.contains(k), "relave"] = v; d.loc[d.set_a.str.contains(k), "relave_pct_masa_total"] = v

# ---------------- relave
print("== Efecto del relave (φ′1 con m = 0.86 por set)")
r = S[S.set_a.str.startswith(("G2021", "W2024"))][["set_a", "relave", "e0", "phi1_m086", "m"]].sort_values(["set_a"])
print(r.round(2).to_string(index=False))
g21 = S[S.set_a.str.startswith("G2021")].copy()
b = np.polyfit(g21.relave, g21.phi1_m086, 1)
print(f"Golder 2021 (< 1 in, 6 in): φ′1 = {b[1]:.1f} {b[0]:+.3f}·relave(%)  → −{-b[0]*10:.2f}° por cada 10 % de relave")
w24 = S[S.set_a.str.startswith("W2024")]
print(f"WSP 2024 (0.6 m): φ′1 con 0 % = {w24[w24.relave == 0].phi1_m086.mean():.1f}°; con 9–13 % = {w24[w24.relave > 0].phi1_m086.mean():.1f}° "
      f"(rango {w24[w24.relave > 0].phi1_m086.min():.1f}–{w24[w24.relave > 0].phi1_m086.max():.1f})")

# ---------------- escala: mismo material ensayado en 1 m y en 6 in a σ′3 ≈ 1 MPa (WSP 2022)
print("\n== Efecto de escala (WSP 2022, σ′3 ≈ 1 MPa)")
e22 = d[(d.fuente_id == "W2022") & d.s3.between(0.9, 1.05)][["set_a", "escala", "litologia", "s3", "phi_sec_deg_std", "Bg_pct"]]
print(e22.round(2).to_string(index=False))

# ---------------- rotura
print("\n== Rotura (Bg Marsal) en ensayos drenados de Antamina")
bg = d.dropna(subset=["Bg_pct"])
print(bg.groupby(["litologia", "escala"]).agg(n=("Bg_pct", "size"), s3_max=("s3", "max"), Bg_med=("Bg_pct", "median"), Bg_max=("Bg_pct", "max")).round(1).to_string())
cb = np.polyfit(np.log10(bg.s3), bg.Bg_pct, 1)
print(f"Antamina: Bg = {cb[1]:.1f} + {cb[0]:.1f}·log10(σ′3, MPa)")
W = load_db().dropna(subset=["Bg"]); W = W[W.s3 > 0]
cw = np.polyfit(np.log10(W.s3), W.Bg, 1)
print(f"Base mundial: Bg = {cw[1]:.1f} + {cw[0]:.1f}·log10(σ′3, MPa)  (n = {len(W)})")
for s3 in (0.5, 1.0, 2.0):
    print(f"  σ′3 = {s3} MPa: Antamina {np.polyval(cb, np.log10(s3)):.1f} % | mundial {np.polyval(cw, np.log10(s3)):.1f} %")
# Bg frente a la caída de φ (por litología a gran escala)
print("\n== φ secante frente a Bg (gran escala)")
gg = bg[bg.escala.isin(["0.6 m", "1.0 m"])]
print(gg[["set_a", "litologia", "s3", "phi_sec_deg_std", "Bg_pct"]].sort_values(["litologia", "s3"]).round(2).to_string(index=False))

# ---------------- Antamina frente a la base mundial a igual σ′n (ángulo secante en el plano)
print("\n== φ′s de Antamina (gran escala) frente a la base mundial en el mismo rango de σ′n")
phi = np.arcsin((d.s1 - d.s3) / (d.s1 + d.s3)); d["sn"] = (d.s1 + d.s3) / 2 - (d.s1 - d.s3) / 2 * np.sin(phi)
d["phis"] = np.degrees(np.arctan((d.s1 - d.s3) / 2 * np.cos(phi) / d.sn))
Wd = load_db()
for lo, hi in [(0.5, 1.5), (1.5, 3.0), (3.0, 6.0)]:
    a = d[(d.sn >= lo) & (d.sn < hi) & d.escala.isin(["0.6 m", "1.0 m"])]; w = Wd[(Wd.sn >= lo) & (Wd.sn < hi)]
    print(f"  σ′n {lo}–{hi} MPa: Antamina n={len(a):2d} mediana {a.phis.median():.1f}° (P10 {a.phis.quantile(.1):.1f}) | "
          f"mundial n={len(w):3d} mediana {w.phis.median():.1f}° (P10 {w.phis.quantile(.1):.1f})")
S.to_csv(AQUI / "sets_ajuste.csv", index=False); d.to_csv(AQUI / "drenados_utilizables.csv", index=False)
