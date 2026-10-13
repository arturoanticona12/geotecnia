"""Construye la base de datos de desmonte de Antamina a partir de los CSV verificados (datos_antamina/verificado).
Salidas en datos_antamina/base/: antamina_base.xlsx (una hoja por tabla + diccionario + calidad) y CSV por tabla."""
import sys, re, json
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
R = Path(__file__).parent; V = R / "verificado"; X = R / "extraido"; OUT = R / "base"; OUT.mkdir(exist_ok=True)

# ------------------------------------------------------------------ fuentes
FUENTES = [
    ("G2010", "Golder Associates", 2010, "Caracterización ROM IPCC", "primaria", "Golder_2010_ROM_verificado.csv"),
    ("G2012", "Golder Associates / IDIEM", 2012, "Triaxiales gran escala en mármol negro (Doc. 446; IDIEM 708.397-A)", "primaria", "Golder_2012_marmol_verificado.csv"),
    ("G2021", "Golder Associates", 2021, "Ensayos de laboratorio commingling", "primaria", "Golder_2021_commingling_verificado.csv"),
    ("W2022", "WSP / IDIEM / Golder / USC", 2022, "Pruebas de enrocado 3B a gran escala, hornfels (deformación)", "primaria", "WSP_2022_hornfels3B_verificado.csv"),
    ("W2024", "WSP / IDIEM", 2024, "Ensayos gran escala mezcla co-disposición (Fase 1)", "primaria", "WSP_2024_codisposicion_verificado.csv"),
    ("I2025", "IDIEM (para WSP)", 2025, "Triaxiales gran escala Codisposal 100 % intrusivo (Fases 2–3)", "primaria", "IDIEM_2025_verificado.csv"),
    ("A2024", "Anddes Geolab", 2024, "Triaxial CU 6 in (solicitud EPE-23.10.141)", "primaria", "ensayos_triaxial_CU_verificado.csv"),
    ("A2024DS", "Anddes Geolab", 2024, "Corte directo de gran escala LSDS", "primaria", "ensayos_corte_directo_verificado.csv"),
    ("LE2", "Antamina", 2025, "Resultados parámetros geotécnicos LE2 (03-09-2025), núcleos por RMU", "primaria (roca)", "indices_roca_LE2.csv"),
    ("FRAG", "Antamina", 2025, "Fragmentación desmonte 2025 (análisis por fotos)", "primaria (campo)", "fragmentacion.csv"),
    ("MR24", "Antamina", 2024, "Modelo de bloques MR2024 y sondajes LE2 (proporción y propiedades por litología)", "primaria (modelo)", "litologias_proporcion.csv"),
    ("S2023", "Stantec", 2023, "Láminas A.5.4 y A.5.5: interpretación antigua", "histórica (no se usa)", "—"),
    ("OV2020", "Ovalle et al.", 2020, "Compilación de triaxiales grandes (Zenodo 3625778), no Antamina", "externa", "Ovalle_2020.csv"),
]
fuentes = pd.DataFrame(FUENTES, columns=["fuente_id", "autor", "anio", "titulo", "tipo", "archivo"])

# ------------------------------------------------------------------ ensayos de resistencia
ARCH = {r[0]: r[5] for r in FUENTES[:8]}
partes = []
for fid, a in ARCH.items():
    d = pd.read_csv(V / a, low_memory=False); d.insert(0, "fuente_id", fid); partes.append(d)
E = pd.concat(partes, ignore_index=True, sort=False)
num = lambda c: pd.to_numeric(E[c], errors="coerce") if c in E else pd.Series(np.nan, index=E.index)


def tipo_std(t):
    t = str(t).lower()
    if "edóm" in t or "odóm" in t or "edom" in t: return "Edómetro"
    if "permeab" in t: return "Permeabilidad"
    if "corte directo" in t: return "Corte directo CD"
    if "cíclico" in t or "ciclico" in t: return "Triaxial cíclico + monótono post-cíclico"
    if "cu" in t.split() or t.startswith("cu") or "ciu" in t: return "Triaxial CU"
    if "carga-descarga" in t: return "Triaxial CD carga-descarga"
    if "cid" in t: return "Triaxial CD"
    return t


E["tipo_ensayo_std"] = E.tipo_ensayo.map(tipo_std)
# esfuerzos en la falla (efectivos), criterio homogéneo:
#   CD: máximo desviador (coincide con máxima oblicuidad);
#   CU: máxima oblicuidad σ′1/σ′3 si la fuente la permite; si no, máximo desviador (marcado).
E["sigma3c_kPa"] = num("sigma3c_kPa").fillna(num("sigma3_kPa"))
s3f = num("sigma3f_kPa").fillna(num("sigma3_kPa")); s1f = num("sigma1f_kPa").fillna(num("sigma1_kPa"))
crit = pd.Series(np.where(E.tipo_ensayo_std.str.startswith("Triaxial CU"), "CU: máximo desviador (la fuente no permite máxima oblicuidad)",
                          "CD: máximo desviador"), index=E.index)
for s3c, s1c in [("sigma3f_oblmax_kPa", "sigma1f_oblmax_kPa"), ("maxobl_sigma3f_kPa", "maxobl_sigma1f_kPa")]:
    if s3c in E:
        m = E.tipo_ensayo_std.str.startswith("Triaxial CU") & num(s3c).notna() & num(s1c).notna()
        s3f = s3f.where(~m, num(s3c)); s1f = s1f.where(~m, num(s1c)); crit[m] = "CU: máxima oblicuidad σ′1/σ′3"
# Anddes (A2024) sin estado de oblicuidad: no usar el 15 % mezclado con σ′3c
m = (E.fuente_id == "A2024") & (crit != "CU: máxima oblicuidad σ′1/σ′3")
s3f[m] = np.nan; s1f[m] = np.nan
E["criterio_falla_std"] = np.where(E.tipo_ensayo_std.str.startswith("Triaxial"), crit, np.where(E.tipo_ensayo_std.eq("Corte directo CD"), "CD: τ pico", ""))
E["sigma3f_kPa_std"] = s3f; E["sigma1f_kPa_std"] = s1f; E["q_kPa_std"] = s1f - s3f
tx = E.tipo_ensayo_std.str.startswith("Triaxial")
E["phi_sec_deg_std"] = np.where(tx, np.degrees(np.arcsin((s1f - s3f) / (s1f + s3f))), np.nan)
ds = E.tipo_ensayo_std.eq("Corte directo CD")
E.loc[ds, "phi_sec_deg_std"] = np.degrees(np.arctan(num("tau_kPa") / num("sigma_n_kPa")))[ds]
# σ'n y τ en el plano de falla (aprox. lineal en cada ensayo, para referencia)
ph = np.radians(E.phi_sec_deg_std)
E["sigma_n_falla_kPa"] = np.where(tx, (s1f + s3f) / 2 - (s1f - s3f) / 2 * np.sin(ph), num("sigma_n_kPa"))
E["tau_falla_kPa"] = np.where(tx, (s1f - s3f) / 2 * np.cos(ph), num("tau_kPa"))
# escala
D = num("diametro_mm").fillna(num("caja_mm"))
E["escala"] = pd.cut(D, [0, 120, 200, 400, 800, 2000], labels=["pequeña (<120 mm)", "6 in (≈150 mm)", "media (240–305 mm)", "0.6 m", "1.0 m"]).astype(str)
E["D_sobre_Dmax"] = D / num("Dmax_mm")


# clase de desmonte normalizada y confianza
def clase(row):
    t = str(row.get("tipo_material", "")).lower()
    sin_relave = bool(re.search(r"\+\s*0\s*%\s*relave", t)) or "sin relave" in t
    if ("mezcla" in t or "relave" in t) and not sin_relave: c = "Mezcla co-disposición"
    elif t.startswith("rom"): c = "ROM"
    elif t.startswith("chancado"): c = "Chancado"
    elif t.startswith("enrocado"): c = "Enrocado"
    else: c = "No indicada"
    conf = "textual" if c in ("ROM", "Chancado", "Enrocado") else "—"
    if row["fuente_id"] == "G2010": conf = "dudosa: muestras del acopio de la chancadora secundaria; hojas de Fase A dicen «Material Chancado»"
    if row["fuente_id"] == "G2012": conf = "asignada: material para presa; el texto lo llama run-of-the-mine"
    if row["fuente_id"] in ("A2024", "A2024DS"): conf = "no indicada; inferencia ROM (rumas del Botadero Este) no confirmada"
    return pd.Series({"clase_desmonte_std": c, "clase_confianza": conf})


E = pd.concat([E, E.apply(clase, axis=1)], axis=1)
# relave en masa seca total
REL = {("W2024", "Codisposal 1"): 13.1, ("W2024", "Codisposal 2"): 10.7, ("W2024", "Codisposal 3"): 9.0, ("W2024", "Codisposal 4"): 0.0}


def relave(row):
    for (f, k), v in REL.items():
        if row.fuente_id == f and k.lower() in str(row.set_id).lower():
            return v
    if row.fuente_id == "W2024":
        return np.nan
    m = re.search(r"\+\s*(\d+)\s*%\s*relave", str(row.tipo_material))
    if m: return float(m.group(1))
    return 0.0 if row.clase_desmonte_std != "Mezcla co-disposición" else np.nan


E["relave_pct_masa_total"] = E.apply(relave, axis=1)
# duplicados, exclusiones y calidad
notas = E.notas.fillna("")
E["duplicado_de"] = np.where(notas.str.contains("DUPLICADO", case=False), "G2012 (registro primario)", "")
excl = {"USC HR-CTX1": "detenido antes de la falla (εa 1.68 %): q es cota inferior",
        "USC HR-CTX4": "detenido antes de la falla (εa 7.37 %): q es cota inferior",
        "USC MN-CTX3": "detenido antes de la falla (εa 4.89 %): q es cota inferior"}
E["excluir_envolvente"] = ""
for k, v in excl.items():
    E.loc[E.ensayo_id.astype(str).str.startswith(k), "excluir_envolvente"] = v
E.loc[E.duplicado_de != "", "excluir_envolvente"] = "duplicado (usar registro primario G2012)"
E.loc[E.tipo_ensayo_std.isin(["Edómetro", "Permeabilidad"]), "excluir_envolvente"] = "no es ensayo de resistencia"
grafico = notas.str.contains("leído de gráfico|leido de grafico|digitaliz", case=False, regex=True)
E["calidad"] = np.where(E.verificado_imagen.astype(str).str.lower().str.startswith("s") & ~grafico, "A", np.where(grafico, "B", "C"))
# e0 adoptado: corrige los e0 calculados con Gs incompatibles (WSP 2022, edómetros IDIEM con Gs 2.60)
E["e0_adoptado"] = num("e0")
E["e0_nota"] = ""
m = (E.fuente_id == "W2022") & E.ensayo_id.astype(str).str.contains("1.555.677-B.1", regex=False)
E.loc[m, ["e0_adoptado", "e0_nota"]] = [0.310, "recalculado con Gs 2.75 (2.60 del informe es incompatible con la densidad de núcleos)"]
m = (E.fuente_id == "W2022") & E.ensayo_id.astype(str).str.contains("REG 41061", regex=False)
E.loc[m, ["e0_adoptado", "e0_nota"]] = [0.286, "recalculado con Gs 2.70 (2.60 incompatible); con Gs 2.75 sería 0.310"]
# ------------------------------------------------------------------ decisiones de criterio experto (ver DECISIONES.md)
# Clase de desmonte donde el informe no la indica
CLASE_EXP = {"W2024": ("ROM", "criterio experto: desmonte del tajo recibido con Dmax 10 in, escalado; programa de co-disposición de desmonte de camión"),
             "I2025": ("ROM", "criterio experto: mismo programa Codisposal que W2024; intrusivo del tajo"),
             "G2021": ("ROM", "criterio experto: compuesto de desmonte por tipos geoquímicos A/B/C para co-disposición en botadero"),
             "A2024": ("ROM", "criterio experto: rumas perforadas en el Botadero Este (desmonte depositado por camión) y pilas experimentales"),
             "A2024DS": ("ROM", "criterio experto: rumas perforadas en el Botadero Este (desmonte depositado por camión) y pilas experimentales")}
for f, (c, why) in CLASE_EXP.items():
    m = (E.fuente_id == f)
    base = np.where(E.loc[m, "clase_desmonte_std"].eq("Mezcla co-disposición"), "Mezcla co-disposición (desmonte ROM + relave)", c)
    E.loc[m, "clase_desmonte_std"] = base
    E.loc[m, "clase_confianza"] = why
# Gs adoptado: medido sobre el mismo material o lote; si no, Gs de sólidos (ASTM D854) por litología de Golder (2010)
GS_LITO = {"Mármol": 2.755, "Hornfels": 2.797, "Intrusivo": 2.708, "Skarn": 3.41}
E["Gs_adoptado"] = num("Gs"); E["Gs_adoptado_origen"] = "informe o verificación"
m = E.fuente_id.eq("I2025")
E.loc[m, ["Gs_adoptado", "Gs_adoptado_origen"]] = [2.85, "WSP 2024 Codisposal 4 (mismo programa y litología)"]
m = E.fuente_id.eq("G2012") | (E.fuente_id.eq("W2022") & E.duplicado_de.ne(""))
E.loc[m, ["Gs_adoptado", "Gs_adoptado_origen"]] = [GS_LITO["Mármol"], "Gs de sólidos del mármol negro (Golder 2010, ASTM D854); 2.70 del informe era supuesto"]
m = E.fuente_id.isin(["A2024", "A2024DS"])
gl = E.loc[m, "litologia"].map(GS_LITO)
E.loc[m & gl.notna(), "Gs_adoptado"] = gl[gl.notna()]
E.loc[m & gl.notna(), "Gs_adoptado_origen"] = "Gs de sólidos por litología (Golder 2010); el Gs rotulado en el Proctor (2.74–3.06) no fue ensayado"
# Edómetros IDIEM de WSP 2022 con Gs 2.60 (incompatible con la densidad de los núcleos del lote)
m = E.fuente_id.eq("W2022") & gs_inf.sub(2.60).abs().lt(0.005) if (gs_inf := num("Gs")) is not None else None
E.loc[m & E.litologia.eq("Hornfels"), ["Gs_adoptado", "Gs_adoptado_origen"]] = [2.75, "Gs del lote (Golder Burnaby); 2.60 del informe es incompatible"]
E.loc[m & E.litologia.eq("Mármol"), ["Gs_adoptado", "Gs_adoptado_origen"]] = [GS_LITO["Mármol"], "Gs de sólidos del mármol (Golder 2010); 2.60 del informe es incompatible"]
# e0 adoptado coherente con el Gs adoptado: e0 = Gs·(1+e0_inf)/Gs_inf − 1 (misma densidad seca)
gs_inf = num("Gs"); e_inf = num("e0")
rec = E.Gs_adoptado.notna() & gs_inf.notna() & e_inf.notna() & (E.Gs_adoptado - gs_inf).abs().gt(0.005)
E.loc[rec, "e0_adoptado"] = (E.Gs_adoptado * (1 + e_inf) / gs_inf - 1)[rec]
E.loc[rec, "e0_nota"] = "recalculado con Gs adoptado"
m = E.fuente_id.eq("I2025") & E.e0_adoptado.isna()
E.loc[m, ["e0_adoptado", "e0_nota"]] = [0.357, "con Gs 2.85 de WSP 2024 y ρd 2.10 g/cm³"]
E["id_probeta"] = [f"{f}-{i:03d}" for i, f in enumerate(E.fuente_id)]
E["id_material"] = E.fuente_id + "|" + E.set_id.astype(str)

# ------------------------------------------------------------------ materiales (sets) con condiciones verificadas
cond = []
for f, a in [("G2010", "condiciones_Golder2010.csv"), ("G2012", "condiciones_Golder2012.csv"), ("G2021", "condiciones_Golder2021.csv"),
             ("W2022", "condiciones_WSP2022.csv"), ("W2024", "condiciones_WSP2024.csv"), ("I2025", "condiciones_IDIEM2025.csv"),
             ("A2024", "condiciones_Anddes2024.csv")]:
    c = pd.read_csv(V / a, low_memory=False); c.insert(0, "fuente_id", f); cond.append(c)
C = pd.concat(cond, ignore_index=True, sort=False)
C["id_material"] = C.fuente_id + "|" + C.set_id.astype(str)
agg = E.groupby("id_material").agg(fuente_id=("fuente_id", "first"), set_id=("set_id", "first"),
                                   litologia=("litologia", "first"), litologia_detalle=("litologia_detalle", "first"),
                                   litologia_proporcion=("litologia_proporcion", "first"),
                                   clase_desmonte_std=("clase_desmonte_std", "first"), clase_confianza=("clase_confianza", "first"),
                                   relave_pct_masa_total=("relave_pct_masa_total", "first"), escala=("escala", "first"),
                                   n_probetas=("id_probeta", "size"), tipos_ensayo=("tipo_ensayo_std", lambda x: "; ".join(sorted(set(x)))),
                                   sigma3_min_kPa=("sigma3c_kPa", "min"), sigma3_max_kPa=("sigma3c_kPa", "max"),
                                   Dmax_mm=("Dmax_mm", "first"), D50_mm=("D50_mm", "first"), Cu=("Cu", "first"), finos_pct=("finos_pct", "first"),
                                   Gs=("Gs", "first"), e0_adoptado=("e0_adoptado", "median"), UCS_MPa=("UCS_MPa", "first")).reset_index()
M = agg.merge(C.drop(columns=[c for c in ["fuente_id", "set_id", "litologia", "litologia_detalle", "litologia_proporcion"] if c in C]),
              on="id_material", how="left", suffixes=("", "_cond"))

# ------------------------------------------------------------------ otras tablas
edo = pd.read_csv(X / "WSP_2022_edometro.csv"); edo.insert(0, "fuente_id", "W2022")
idx = []
g10 = pd.read_csv(V / "indices_roca_Golder2010.csv"); g10.insert(0, "fuente_id", "G2010"); idx.append(g10)
le2 = pd.read_csv(V / "indices_roca_LE2.csv"); le2.insert(0, "fuente_id", "LE2"); idx.append(le2)
IR = pd.concat(idx, ignore_index=True, sort=False)
ind = pd.read_csv(V / "ensayos_indices_verificado.csv"); ind.insert(0, "fuente_id", "A2024")
frag = pd.read_csv(X / "fragmentacion.csv"); frag.insert(0, "fuente_id", "FRAG")
lito = pd.read_csv(X / "litologias_proporcion.csv"); lito.insert(0, "fuente_id", "MR24")
prop = pd.read_csv(X / "propiedades_roca_por_litologia.csv"); prop.insert(0, "fuente_id", "MR24")
ov = pd.read_csv(X / "Ovalle_2020.csv"); ov.insert(0, "fuente_id", "OV2020")
# leyenda de litologías (reconstruida: coincidencia exacta de n de bloques y UCS con WSC lámina 12)
bmrt = pd.read_csv(OUT / "modelo_bloques_por_RT.csv")
LEYENDA = {1: ("Intrusivo", "Intrusivo", "Intrusivo_1"), 2: ("Intrus-Estruct-Tab", "Intrusivo", "Intrusivo_2"),
           53: ("Brechas-Intrus", "Intrusivo", "sin etiqueta"), 13: ("Horfels", "Hornfels", "Metamorfico_13"),
           14: ("Horfel Diopsida", "Hornfels", "Metamorfico_14"), 16: ("Marmol", "Mármol", "Metamorfico_16"),
           19: ("Marmol Diopsida", "Mármol", "Metamorfico_19"), 10: ("Caliza", "Caliza", "Sedimentario_10"),
           11: ("Margas-Limonitas", "Marga-Limolita", "Sedimentario_11")}
ley = bmrt.assign(litologia_lamina12=bmrt.MR24_RT.map(lambda r: LEYENDA[r][0]), litologia_normalizada=bmrt.MR24_RT.map(lambda r: LEYENDA[r][1]),
                  grupo_Geologia_2024=bmrt.MR24_RT.map(lambda r: LEYENDA[r][2]),
                  evidencia="n de bloques y mediana de UCS idénticos a WSC lámina 12; % de tonelaje coherente con WSC lámina 17")
comp = ley.groupby("litologia_normalizada").pct_ton.sum().sort_values(ascending=False).reset_index().rename(columns={"pct_ton": "pct_tonelaje_LE2"})
ucsr = pd.read_csv(OUT / "ucs_directa_vs_plt.csv")

# ------------------------------------------------------------------ diccionario
DIC = [
    ("ensayos", "id_probeta", "Identificador único de la probeta en esta base"),
    ("ensayos", "id_material", "fuente_id|set_id; enlaza con la tabla materiales"),
    ("ensayos", "tipo_ensayo_std", "Triaxial CD, CD carga-descarga, CU, cíclico + monótono, corte directo CD, edómetro o permeabilidad"),
    ("ensayos", "sigma3c_kPa", "σ′3 de consolidación"),
    ("ensayos", "sigma3f_kPa_std / sigma1f_kPa_std", "Esfuerzos efectivos en la falla (en CD, σ′3f = σ′3c)"),
    ("ensayos", "q_kPa_std", "Desviador en la falla = σ′1f − σ′3f (se corrigió la notación MIT de las hojas IDIEM)"),
    ("ensayos", "phi_sec_deg_std", "Ángulo secante: asin(q/(σ′1+σ′3)) en triaxial; atan(τ/σn) en corte directo"),
    ("ensayos", "sigma_n_falla_kPa, tau_falla_kPa", "Punto de tangencia aproximado (círculo de Mohr con φ secante); referencia"),
    ("ensayos", "eps_vol_falla_pct", "Deformación volumétrica en la falla; compresión negativa"),
    ("ensayos", "Bg_pct", "Índice de rotura de Marsal = suma de diferencias positivas (Golder 2012 corregido a la mitad)"),
    ("ensayos", "escala", "Clase de diámetro de probeta"),
    ("ensayos", "clase_desmonte_std, clase_confianza", "ROM, Chancado, Enrocado, Mezcla co-disposición o No indicada; con el respaldo de la asignación"),
    ("ensayos", "relave_pct_masa_total", "Relave en masa seca total (WSP 2024 corregido: 13.1/10.7/9.0 % en vez de 22/18/15 % nominal)"),
    ("ensayos", "e0_adoptado, e0_nota", "e0 verificado; corregido cuando el Gs del informe es físicamente incompatible"),
    ("ensayos", "excluir_envolvente", "Motivo para no usar el ensayo en envolventes (duplicado, falla no alcanzada, no es de resistencia)"),
    ("ensayos", "calidad", "A: tabla verificada en imagen; B: leído o digitalizado de gráfico; C: otro"),
    ("materiales", "—", "Una fila por set (material ensayado) con condiciones de campo y laboratorio verificadas"),
    ("indices_roca", "—", "UCS, carga puntual, Los Ángeles, durabilidad, absorción y Gs por litología: Golder 2010 (por fase) y LE2 2025 (por RMU)"),
    ("fragmentacion", "—", "319 análisis de fragmentación por fotos del ROM recién volado (fases 8, 9 y 10)"),
    ("litologia_plan", "—", "Proporción de litologías del desmonte LE2 (modelo de bloques MR2024) por período y fase; códigos pendientes de leyenda"),
    ("externos_ovalle2020", "—", "158 triaxiales de gran escala (Ovalle et al., 2020); no Antamina; posibles duplicados con otras fuentes chilenas"),
]
dic = pd.DataFrame(DIC, columns=["tabla", "columna", "descripcion"])

# ------------------------------------------------------------------ calidad y cobertura
res = E[E.tipo_ensayo_std.str.startswith(("Triaxial", "Corte"))]
uso = res[res.excluir_envolvente == ""]
cob = uso.assign(rango_s3=pd.cut(uso.sigma3c_kPa, [0, 300, 600, 1000, 1500, 2000, 2500], right=True).astype(str)) \
         .pivot_table(index=["litologia", "clase_desmonte_std"], columns="rango_s3", values="id_probeta", aggfunc="count", fill_value=0)
cob["total"] = cob.sum(axis=1)
esc = uso.pivot_table(index=["litologia"], columns="escala", values="id_probeta", aggfunc="count", fill_value=0)
gs = M[["id_material", "Gs", "Gs_origen"]] if "Gs_origen" in M else M[["id_material", "Gs"]]

with pd.ExcelWriter(OUT / "antamina_base.xlsx", engine="openpyxl") as w:
    fuentes.to_excel(w, "fuentes", index=False)
    M.to_excel(w, "materiales", index=False)
    E.to_excel(w, "ensayos", index=False)
    edo.to_excel(w, "edometros", index=False)
    IR.to_excel(w, "indices_roca", index=False)
    ind.to_excel(w, "indices_suelo_Anddes", index=False)
    frag.to_excel(w, "fragmentacion", index=False)
    lito.to_excel(w, "litologia_plan", index=False)
    prop.to_excel(w, "propiedades_modelo", index=False)
    ov.to_excel(w, "externos_ovalle2020", index=False)
    ley.to_excel(w, "leyenda_litologia", index=False)
    comp.to_excel(w, "composicion_desmonte_LE2", index=False)
    ucsr.to_excel(w, "UCS_directa_vs_PLT", index=False)
    dic.to_excel(w, "diccionario", index=False)
    cob.to_excel(w, "cobertura_litologia_s3")
    esc.to_excel(w, "cobertura_escala")
for nm, t in [("fuentes", fuentes), ("materiales", M), ("ensayos", E), ("edometros", edo), ("indices_roca", IR),
              ("fragmentacion", frag), ("diccionario", dic)]:
    t.to_csv(OUT / f"{nm}.csv", index=False, encoding="utf-8-sig")

print("ensayos:", len(E), "| de resistencia:", len(res), "| usables en envolventes:", len(uso), "| materiales:", len(M))
print(E.groupby(["fuente_id", "tipo_ensayo_std"]).size().to_string())
print("\nexcluidos:", E[E.excluir_envolvente != ""].excluir_envolvente.value_counts().to_string())
print("\ncalidad:", E.calidad.value_counts().to_dict())
print("\nCobertura (ensayos usables) por litología y clase vs σ′3c (kPa):\n", cob.to_string())
print("\nPor escala:\n", esc.to_string())
dif = (E.q_kPa_std - num("q_kPa")).abs()
print("\ncriterio de falla:", E.criterio_falla_std.value_counts().to_dict())
print("control q_std vs q informado (|dif|>2 kPa) en CD:", int((dif[E.criterio_falla_std.str.startswith("CD: máximo")] > 2).sum()))
print("q_std no positivo o vacío en triaxiales:", int(((E.q_kPa_std <= 0) | E.q_kPa_std.isna())[E.tipo_ensayo_std.str.startswith("Triaxial")].sum()))
print("φ secante std (triaxial y corte), resumen por fuente:")
print(E.groupby("fuente_id").phi_sec_deg_std.describe()[["count", "min", "50%", "max"]].round(1).to_string())
