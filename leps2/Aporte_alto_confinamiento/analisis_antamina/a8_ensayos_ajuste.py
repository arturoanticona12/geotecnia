"""Ensayos del ajuste de Leps 2.0 (revisión 5 del memorándum, 2026-10-10; el usuario aprobó incluir el corte directo):
  - 22 triaxiales drenados (CD) sin relave de drenados_utilizables.csv (verificados contra los PDF: verificacion_ocr/drenados_verificados.csv);
  - 15 cortes directos de gran escala de Anddes Geolab (2024), caja de 30.5 cm, Dmax 1 in (verificacion_ocr/anddes2024_lsds.csv),
    con τ pico y σ′n. Leps 2.0 admite corte directo (Cylwik et al. 2025: «triaxial or direct shear tests»).
e de los cortes directos: Anddes no informa Gs; se usa el Gs de sólidos (ASTM D854) de Golder (2010, p. 49), promedio de las fases A y B,
el mismo criterio con que la base recalculó el e0 de Golder (2012) (2.755 para el mármol): mármol 2.755, hornfels 2.7965, intrusivo
2.708; la pila 01 (mármol + hornfels, proporción no informada) usa el promedio de ambos, 2.776. e = Gs/ρd − 1 con ρd inicial del ensayo.
Escribe ensayos_ajuste.csv (columna «tipo»: TX o DS)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
AQ = Path(__file__).parent; V = AQ.parent / "datos_antamina" / "verificacion_ocr"
GS_D854 = {"Mármol": (2.763 + 2.747) / 2, "Hornfels": (2.791 + 2.802) / 2, "Intrusivo": (2.674 + 2.742) / 2}   # Golder (2010), p. 49
GS_D854["Mezcla"] = (GS_D854["Mármol"] + GS_D854["Hornfels"]) / 2
tx = pd.read_csv(AQ / "drenados_utilizables.csv", low_memory=False)
tx = tx[tx.relave_pct_masa_total.fillna(0) == 0].copy(); tx["tipo"] = "TX"; tx["sn_ds"] = np.nan; tx["tau_ds"] = np.nan
ds = pd.read_csv(V / "anddes2024_lsds.csv")
LIT = [("Ruma 01", "Mármol"), ("Ruma 02", "Hornfels"), ("Ruma 03", "Intrusivo"), ("Pila 01", "Mezcla"), ("Pila 02", "Intrusivo")]
lit = lambda s: next(v for k, v in LIT if str(s).startswith(k))
rows = []
for _, r in ds.iterrows():
    L = lit(r.set); gs = GS_D854[L]; e = gs / float(r.rho_d_ini_gcm3) - 1
    rows.append(dict(fuente_id="A2024DS", set_id=str(r.set).replace(" (I-1 al I-12)", "").replace(" (H-1 al H-12)", "").replace(" (M-1 al M-13)", ""),
                     ensayo_id=f"LSDS {r.set} σn={r.sigma_n_kPa:.0f}", litologia=L, tipo="DS", tipo_ensayo="Corte directo de gran escala (LSDS)",
                     escala="Corte directo 30.5 cm", diametro_mm=305.0, Dmax_mm=25.4, e0_adoptado=e, Gs_adoptado=gs,
                     Gs_adoptado_origen="Golder (2010) D854, promedio fases A y B", s3=np.nan, s1=np.nan,
                     sn_ds=float(r.sigma_n_kPa) / 1000, tau_ds=float(r.tau_pico_kPa) / 1000, eps_axial_falla_pct=np.nan,
                     eps_vol_falla_pct=np.nan, relave_pct_masa_total=0.0, notas=f"Anddes Geolab (2024), p. {r.pagina_pdf}; ρd {r.rho_d_ini_gcm3}"))
# 2026-10-12 (decisión de WA): un solo criterio de Gs en todos los ensayos, el D854 de sólidos de Golder (2010) por litología.
# Antes los triaxiales usaban el Gs de cada informe o de otro cercano: 2.70 supuesto (Golder 2012, ya recalculado a 2.755),
# 2.75 «calculated» (hojas Golder 6 in, también usado en IDIEM 2022), 2.85 (WSP 2024: Gs aparente C127 de gruesos con D854 de
# finos; también usado en IDIEM 2025), 2.762 (Golder 2021, sin rastrear). e0 = Gs·γw/γd − 1 con la γd inicial verificada.
GS_G21 = 1 / (0.35 / GS_D854["Intrusivo"] + 0.15 / GS_D854["Mezcla"] + 0.50 / GS_D854["Hornfels"])   # compuesto (Golder 2021, p. 6)
def gs_tx(r):
    if r.litologia == "Mezcla":
        return GS_G21, "Golder (2010) D854 ponderado por la composición del compuesto (35 % intrusivo, 15 % mármol y hornfels, 50 % hornfels); Golder (2021) midió 2.77 (D854, p. 73)"
    return GS_D854[r.litologia], "Golder (2010) D854, promedio fases A y B"
tx["e0_informe_o_previo"] = tx.e0_adoptado; tx["Gs_previo"] = tx.Gs_adoptado
for i, r in tx.iterrows():
    gs, org = gs_tx(r)
    tx.loc[i, ["Gs_adoptado", "Gs_adoptado_origen", "e0_adoptado"]] = [gs, org, gs * 9.81 / float(r.gamma_d_kNm3) - 1]
print(tx[["fuente_id", "set_id", "litologia", "gamma_d_kNm3", "Gs_previo", "e0_informe_o_previo", "Gs_adoptado", "e0_adoptado"]]
      .drop_duplicates(["fuente_id", "set_id", "gamma_d_kNm3"]).round(3).to_string())
D = pd.concat([tx, pd.DataFrame(rows)], ignore_index=True)
D.to_csv(AQ / "ensayos_ajuste.csv", index=False)
print(f"TX {int((D.tipo == 'TX').sum())}, DS {int((D.tipo == 'DS').sum())}, sets {D.groupby(['fuente_id', 'set_id']).ngroups}")
print(D[D.tipo == "DS"][["set_id", "litologia", "sn_ds", "tau_ds", "e0_adoptado", "Gs_adoptado"]].round(3).to_string())
