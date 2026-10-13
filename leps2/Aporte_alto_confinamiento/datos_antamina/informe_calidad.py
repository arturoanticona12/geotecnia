"""Genera base/INFORME_CALIDAD.md con inventario, cobertura y estado de la base de Antamina."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
sys.stdout.reconfigure(encoding="utf-8")
B = Path(__file__).parent / "base"
E = pd.read_csv(B / "ensayos.csv", low_memory=False); M = pd.read_csv(B / "materiales.csv", low_memory=False)
F = pd.read_csv(B / "fuentes.csv")
res = E[E.tipo_ensayo_std.str.startswith(("Triaxial", "Corte"), na=False)]
uso = res[res.excluir_envolvente.isna()]


def md(df):
    df = df.copy(); df.columns = [str(c) for c in df.columns]
    head = "| " + " | ".join(df.columns) + " |\n|" + "---|" * len(df.columns) + "\n"
    return head + "\n".join("| " + " | ".join("" if pd.isna(v) else (f"{v:.1f}" if isinstance(v, float) else str(v)) for v in r) + " |" for r in df.itertuples(index=False))


L = ["# Base de datos de desmonte de Antamina: informe de calidad", "",
     "Generado por `informe_calidad.py` desde `base/`. Los valores provienen de los CSV verificados (`verificado/`), "
     "auditados contra las páginas originales por un revisor independiente del extractor.", "",
     "## 1. Inventario", "",
     f"- Ensayos registrados: **{len(E)}**; de resistencia: **{len(res)}**; utilizables en envolventes: **{len(uso)}**.",
     f"- Materiales (sets): **{len(M)}**.", "", md(E.groupby(["fuente_id", "tipo_ensayo_std"]).size().reset_index(name="n")), "",
     "## 2. Cobertura de los ensayos utilizables", "",
     "### Por litología y clase de desmonte", "",
     md(uso.pivot_table(index=["litologia", "clase_desmonte_std"], columns=pd.cut(uso.sigma3c_kPa, [0, 300, 600, 1000, 1500, 2000, 2500]).astype(str),
                        values="id_probeta", aggfunc="count", fill_value=0).reset_index()), "",
     "### Por litología y escala de probeta", "",
     md(uso.pivot_table(index="litologia", columns="escala", values="id_probeta", aggfunc="count", fill_value=0).reset_index()), "",
     "### Ensayos de gran escala (0.6–1.0 m), los más representativos del desmonte", "",
     md(uso[uso.escala.isin(["0.6 m", "1.0 m"])].groupby(["fuente_id", "litologia", "clase_desmonte_std"])
        .agg(n=("id_probeta", "size"), s3_min=("sigma3c_kPa", "min"), s3_max=("sigma3c_kPa", "max"),
             phi_min=("phi_sec_deg_std", "min"), phi_max=("phi_sec_deg_std", "max"), Bg_max=("Bg_pct", "max")).reset_index()), "",
     "## 3. Criterio de falla homogéneo", "",
     "- Ensayos drenados: máximo desviador (en CD coincide con la máxima oblicuidad).",
     "- Ensayos no drenados: máxima oblicuidad σ′1/σ′3 cuando la fuente lo permite; si no, máximo desviador (marcado en `criterio_falla_std`).",
     "- Corte directo: τ pico.", "", md(E.criterio_falla_std.fillna("—").value_counts().reset_index()), "",
     "## 4. Exclusiones de envolventes", "", md(E.excluir_envolvente.dropna().value_counts().reset_index()), "",
     "## 5. Correcciones principales de la verificación", "",
     "- **Golder 2012:** Bg informado al doble (sumaba diferencias positivas y negativas); se usa la mitad (13.4–27.7 %).",
     "- **WSP 2022:** 5 triaxiales y 1 edómetro de mármol 2011 duplican a Golder 2012 (registro primario). Tres cíclicos USC detenidos antes de la falla. "
     "Gs 2.60 de los edómetros IDIEM es incompatible con la densidad de los núcleos; e0 recalculado. Bg = 45 % del edómetro de mármol 2021 se recalcula en 37.8 %.",
     "- **WSP 2024:** el relave efectivo es 13.1/10.7/9.0 % de la masa total (no 22/18/15 %). UCS 61.1–143.1 MPa (no 64.0).",
     "- **IDIEM 2025:** lote distinto de WSP 2024 (139 t, probetas de 1 m, Dmax 7 in); sin Gs propio (e0 condicional 0.357).",
     "- **Golder 2010:** CU con σ′3c y estados en la falla separados (57 filas); c y c′ de la Tabla 3 en kg/cm²; la clase ROM de la Fase A es dudosa.",
     "- **Anddes 2024:** D10 de 1.54 mm es un artefacto (Cu y Cc no utilizables); Gs leído de la curva Proctor (3.06 en mármol, atípico); "
     "probetas al 90 % del Proctor sobre la fracción < 19 mm; saturación del corte directo no demostrada.",
     "- **LE2 2025:** P35 de UCS de XDP corregido de 2021 a 70.8 MPa.", "",
     "Detalle completo en `verificado/verificacion_*.md`.", "",
     "## 6. Origen del Gs y de e0", "",
     md(M[["id_material", "litologia", "Gs", "Gs_origen", "e0_adoptado"]].dropna(subset=["Gs_origen"]).head(40)) if "Gs_origen" in M else "",
     "", "## 7. Decisiones de criterio experto (detalle y evidencia en DECISIONES.md)", "",
     "- **Leyenda de litologías** reconstruida con coincidencia exacta frente a WSC lámina 12 (tabla `leyenda_litologia`).",
     "- **Composición del desmonte LE2** (tabla `composicion_desmonte_LE2`): Mármol 38.9 %, Hornfels 19.2 %, Marga-Limolita 18.9 %, Intrusivo 15.0 %, Caliza 8.0 %.",
     "- **UCS de referencia**: compresión uniaxial directa; la carga puntual convertida sobreestima 1.5–1.75× en mármol y hornfels (tabla `UCS_directa_vs_PLT`).",
     "- **Clase de desmonte** asignada por criterio cuando el informe no la da; el respaldo queda en `clase_confianza`.",
     "- **Gs adoptado** por material o por litología (Golder 2010, ASTM D854) y e0 recalculado (`Gs_adoptado`, `e0_adoptado`).", "",
     "## 8. Vacíos que la base no puede cubrir", "",
     "1. **Margas y limolitas (19 % del desmonte LE2)** no tienen ningún ensayo de resistencia, de índice ni de durabilidad.",
     "2. **Mármol**: la litología dominante (39 %) y la más débil (UCS directa 48 MPa) solo tiene ensayos de gran escala como enrocado seleccionado, no como ROM.",
     "3. No hay ensayos de resistencia con σ′3 > 2.45 MPa ni ensayos no drenados de gran escala.",
     "4. El Gs de los lotes de 1 m (WSP 2022, IDIEM 2025) y de las muestras Anddes no se ensayó.",
     "5. El archivo «Resultados de Laboratorio.zip» del RFI 115-G-0047 (lixiviación ácida) no está en la carpeta.", ""]
(B / "INFORME_CALIDAD.md").write_text("\n".join(L), encoding="utf-8")
print("escrito", B / "INFORME_CALIDAD.md")
