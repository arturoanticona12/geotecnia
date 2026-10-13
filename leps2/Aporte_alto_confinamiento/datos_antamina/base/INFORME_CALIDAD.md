# Base de datos de desmonte de Antamina: informe de calidad

Generado por `informe_calidad.py` desde `base/`. Los valores provienen de los CSV verificados (`verificado/`), auditados contra las páginas originales por un revisor independiente del extractor.

## 1. Inventario

- Ensayos registrados: **175**; de resistencia: **162**; utilizables en envolventes: **154**.
- Materiales (sets): **66**.

| fuente_id | tipo_ensayo_std | n |
|---|---|---|
| A2024 | Triaxial CU | 15 |
| A2024DS | Corte directo CD | 15 |
| G2010 | Triaxial CU | 57 |
| G2012 | Edómetro | 1 |
| G2012 | Triaxial CD | 5 |
| G2021 | Permeabilidad | 6 |
| G2021 | Triaxial CD | 30 |
| I2025 | Triaxial CD | 3 |
| W2022 | Edómetro | 6 |
| W2022 | Triaxial CD | 5 |
| W2022 | Triaxial CD carga-descarga | 8 |
| W2022 | Triaxial cíclico + monótono post-cíclico | 6 |
| W2024 | Triaxial CD | 12 |
| W2024 | Triaxial CD carga-descarga | 6 |

## 2. Cobertura de los ensayos utilizables

### Por litología y clase de desmonte

| litologia | clase_desmonte_std | (0, 300] | (1000, 1500] | (1500, 2000] | (2000, 2500] | (300, 600] | (600, 1000] | nan |
|---|---|---|---|---|---|---|---|---|
| Hornfels | Chancado | 2 | 0 | 1 | 0 | 4 | 2 | 0 |
| Hornfels | Enrocado | 0 | 0 | 2 | 2 | 1 | 3 | 0 |
| Hornfels | ROM | 0 | 0 | 2 | 0 | 4 | 3 | 3 |
| Intrusivo | Chancado | 2 | 0 | 1 | 0 | 4 | 2 | 0 |
| Intrusivo | Mezcla co-disposición (desmonte ROM + relave) | 0 | 0 | 5 | 0 | 5 | 5 | 0 |
| Intrusivo | ROM | 0 | 0 | 5 | 0 | 7 | 6 | 6 |
| Mezcla | Mezcla co-disposición (desmonte ROM + relave) | 9 | 9 | 0 | 0 | 9 | 0 | 0 |
| Mezcla | ROM | 1 | 1 | 1 | 0 | 2 | 1 | 3 |
| Mármol | Chancado | 2 | 0 | 1 | 0 | 4 | 2 | 0 |
| Mármol | Enrocado | 0 | 0 | 2 | 0 | 4 | 2 | 0 |
| Mármol | ROM | 0 | 0 | 2 | 0 | 2 | 2 | 3 |
| Skarn | Chancado | 2 | 0 | 1 | 0 | 4 | 2 | 0 |
| Skarn | ROM | 0 | 0 | 1 | 0 | 3 | 2 | 0 |

### Por litología y escala de probeta

| litologia | 0.6 m | 1.0 m | 6 in (≈150 mm) | media (240–305 mm) | pequeña (<120 mm) |
|---|---|---|---|---|---|
| Hornfels | 0 | 6 | 8 | 3 | 12 |
| Intrusivo | 18 | 3 | 9 | 6 | 12 |
| Mezcla | 0 | 0 | 33 | 3 | 0 |
| Mármol | 0 | 5 | 9 | 3 | 9 |
| Skarn | 0 | 0 | 3 | 0 | 12 |

### Ensayos de gran escala (0.6–1.0 m), los más representativos del desmonte

| fuente_id | litologia | clase_desmonte_std | n | s3_min | s3_max | phi_min | phi_max | Bg_max |
|---|---|---|---|---|---|---|---|---|
| G2012 | Mármol | Enrocado | 5 | 490.3 | 1961.3 | 36.7 | 40.2 | 27.7 |
| I2025 | Intrusivo | ROM | 3 | 490.3 | 1961.3 | 39.2 | 39.6 |  |
| W2022 | Hornfels | Enrocado | 6 | 981.0 | 2452.0 | 41.4 | 46.5 | 39.0 |
| W2024 | Intrusivo | Mezcla co-disposición (desmonte ROM + relave) | 15 | 490.3 | 1961.3 | 38.8 | 44.3 | 19.4 |
| W2024 | Intrusivo | ROM | 3 | 490.3 | 1961.3 | 38.7 | 39.9 | 17.6 |

## 3. Criterio de falla homogéneo

- Ensayos drenados: máximo desviador (en CD coincide con la máxima oblicuidad).
- Ensayos no drenados: máxima oblicuidad σ′1/σ′3 cuando la fuente lo permite; si no, máximo desviador (marcado en `criterio_falla_std`).
- Corte directo: τ pico.

| criterio_falla_std | count |
|---|---|
| CD: máximo desviador | 75 |
| CU: máximo desviador (la fuente no permite máxima oblicuidad) | 45 |
| CU: máxima oblicuidad σ′1/σ′3 | 27 |
| CD: τ pico | 15 |
| — | 13 |

## 4. Exclusiones de envolventes

| excluir_envolvente | count |
|---|---|
| no es ensayo de resistencia | 13 |
| duplicado (usar registro primario G2012) | 5 |
| detenido antes de la falla (εa 1.68 %): q es cota inferior | 1 |
| detenido antes de la falla (εa 7.37 %): q es cota inferior | 1 |
| detenido antes de la falla (εa 4.89 %): q es cota inferior | 1 |

## 5. Correcciones principales de la verificación

- **Golder 2012:** Bg informado al doble (sumaba diferencias positivas y negativas); se usa la mitad (13.4–27.7 %).
- **WSP 2022:** 5 triaxiales y 1 edómetro de mármol 2011 duplican a Golder 2012 (registro primario). Tres cíclicos USC detenidos antes de la falla. Gs 2.60 de los edómetros IDIEM es incompatible con la densidad de los núcleos; e0 recalculado. Bg = 45 % del edómetro de mármol 2021 se recalcula en 37.8 %.
- **WSP 2024:** el relave efectivo es 13.1/10.7/9.0 % de la masa total (no 22/18/15 %). UCS 61.1–143.1 MPa (no 64.0).
- **IDIEM 2025:** lote distinto de WSP 2024 (139 t, probetas de 1 m, Dmax 7 in); sin Gs propio (e0 condicional 0.357).
- **Golder 2010:** CU con σ′3c y estados en la falla separados (57 filas); c y c′ de la Tabla 3 en kg/cm²; la clase ROM de la Fase A es dudosa.
- **Anddes 2024:** D10 de 1.54 mm es un artefacto (Cu y Cc no utilizables); Gs leído de la curva Proctor (3.06 en mármol, atípico); probetas al 90 % del Proctor sobre la fracción < 19 mm; saturación del corte directo no demostrada.
- **LE2 2025:** P35 de UCS de XDP corregido de 2021 a 70.8 MPa.

Detalle completo en `verificado/verificacion_*.md`.

## 6. Origen del Gs y de e0

| id_material | litologia | Gs | Gs_origen | e0_adoptado |
|---|---|---|---|---|
| A2024|Pila 01 (MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B) | Mezcla | 2.9 | leído del rótulo «Curva 100% saturación (Gs=2.9)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.89 | 0.4 |
| A2024|Pila 01 (MP1-B-M-1, MP1-B-M2, MP1-B-M3, MP1-H-Material B) | Mezcla | 2.9 | leído del rótulo «Curva 100% saturación (Gs=2.9)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.89 | 0.4 |
| A2024|Pila 02 (MP2-A-M-1 a MP2-A-M-5, MP2-H-Material A) | Intrusivo | 2.7 | leído del rótulo «Curva 100% saturación (Gs=2.74)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.73 | 0.5 |
| A2024|Pila 02 (MP2-A-M-1 a MP2-A-M-5, MP2-H-Material A) | Intrusivo | 2.7 | leído del rótulo «Curva 100% saturación (Gs=2.74)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.73 | 0.5 |
| A2024|Ruma 01 (M-1 al M-13) | Mármol | 3.1 | leído del rótulo «Curva 100% saturación (Gs=3.06)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 3.05 | 0.3 |
| A2024|Ruma 01 (M-1 al M-13) | Mármol | 3.1 | leído del rótulo «Curva 100% saturación (Gs=3.06)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 3.05 | 0.3 |
| A2024|Ruma 02 (H-1 al H-12) | Hornfels | 2.9 | leído del rótulo «Curva 100% saturación (Gs=2.94)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.93 | 0.3 |
| A2024|Ruma 02 (H-1 al H-12) | Hornfels | 2.9 | leído del rótulo «Curva 100% saturación (Gs=2.94)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.93 | 0.3 |
| A2024|Ruma 03 / Fase 10 A (I-1 al I-12) | Intrusivo | 2.8 | leído del rótulo «Curva 100% saturación (Gs=2.75)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.74 | 0.4 |
| A2024|Ruma 03 / Fase 10 A (I-1 al I-12) | Intrusivo | 2.8 | leído del rótulo «Curva 100% saturación (Gs=2.75)» del gráfico Proctor (fracción < 19 mm); no hay ensayo de Gs. La geometría de la línea da Gs ≈ 2.74 | 0.4 |
| G2010|G2010-A-EXO-2.8in | Skarn | 3.5 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 3.212 (p.48); Tabla 2 da 3.172. Con Gs grueso e0 sería menor. | 0.5 |
| G2010|G2010-A-EXO-4in | Skarn | 3.5 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 3.212 (p.48); Tabla 2 da 3.172. Con Gs grueso e0 sería menor. | 0.7 |
| G2010|G2010-A-HG-2.8in | Hornfels | 2.8 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.737 (p.48); Tabla 2 da 2.733. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-A-HG-4in | Hornfels | 2.8 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.737 (p.48); Tabla 2 da 2.733. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-A-INT-2.8in | Intrusivo | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.461 (p.48); Tabla 2 da 2.451. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-A-INT-4in | Intrusivo | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.461 (p.48); Tabla 2 da 2.451. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-A-MN-2.8in | Mármol | 2.8 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.717 (p.48); Tabla 2 da 2.696. Con Gs grueso e0 sería menor. | 0.3 |
| G2010|G2010-B-EXO-2.8in | Skarn | 3.3 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 3.102 (p.48); Tabla 2 da 3.102. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-B-EXO-4in | Skarn | 3.3 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 3.102 (p.48); Tabla 2 da 3.102. Con Gs grueso e0 sería menor. | 0.5 |
| G2010|G2010-B-EXO-6in | Skarn | 3.3 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 3.102 (p.48); Tabla 2 da 3.102. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-B-HG-2.8in | Hornfels | 2.8 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.74 (p.48); Tabla 2 da 2.74. Con Gs grueso e0 sería menor. | 0.3 |
| G2010|G2010-B-HG-4in | Hornfels | 2.8 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.74 (p.48); Tabla 2 da 2.74. Con Gs grueso e0 sería menor. | 0.5 |
| G2010|G2010-B-HG-6in | Hornfels | 2.8 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.74 (p.48); Tabla 2 da 2.74. Con Gs grueso e0 sería menor. | 0.3 |
| G2010|G2010-B-INT-2.8in | Intrusivo | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.647 (p.48); Tabla 2 da 2.647. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-B-INT-4in | Intrusivo | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.647 (p.48); Tabla 2 da 2.647. Con Gs grueso e0 sería menor. | 0.5 |
| G2010|G2010-B-INT-6in | Intrusivo | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.647 (p.48); Tabla 2 da 2.647. Con Gs grueso e0 sería menor. | 0.4 |
| G2010|G2010-B-MN-2.8in | Mármol | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.725 (p.48); Tabla 2 da 2.725. Con Gs grueso e0 sería menor. | 0.3 |
| G2010|G2010-B-MN-4in | Mármol | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.725 (p.48); Tabla 2 da 2.725. Con Gs grueso e0 sería menor. | 0.5 |
| G2010|G2010-B-MN-6in | Mármol | 2.7 | ASTM D854 (p.49) sobre la misma litología y fase, impreso como «G. Específica Promedio» en la hoja CU; fracción ensayada en el picnómetro no especificada. Gs grueso C127 bulk = 2.725 (p.48); Tabla 2 da 2.725. Con Gs grueso e0 sería menor. | 0.4 |
| G2012|G2012-MN-C | Mármol | 2.7 | SUPUESTO: 'The specific gravity of this rock type was not determined' (p3); 'estimated assuming Gs=2.7' (p7); IDIEM 'Peso específico integral 2,700' (p72) | 0.3 |
| G2012|G2012-MN-C | Mármol | 2.7 | supuesto (p13) | 0.3 |
| G2021|G21-ALT1-1:1 | Mezcla | 3.0 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.129-131); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.7 |
| G2021|G21-ALT1-4:1 | Mezcla | 2.8 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.122-124); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.6 |
| G2021|G21-ALT1-9:1 | Mezcla | 2.8 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.115-117); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.6 |
| G2021|G21-ALT2-1:1 | Mezcla | 3.0 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.150-152); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.7 |
| G2021|G21-ALT2-4:1 | Mezcla | 2.9 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.143-145); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.6 |
| G2021|G21-ALT2-9:1 | Mezcla | 2.8 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.136-138); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.6 |
| G2021|G21-ALT4-1:1 | Mezcla | 3.0 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.171-173); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.7 |
| G2021|G21-ALT4-4:1 | Mezcla | 2.8 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.164-166); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.6 |
| G2021|G21-ALT4-9:1 | Mezcla | 2.8 | «G. Específica (Promedio)» impresa en las hojas triaxiales (p.157-159); no es el Gs de finos (D854) ni el de gruesos (C127) de la Tabla 5 y el informe no explica su cálculo. Golder calculó e0 con este valor | 0.6 |

## 7. Decisiones de criterio experto (detalle y evidencia en DECISIONES.md)

- **Leyenda de litologías** reconstruida con coincidencia exacta frente a WSC lámina 12 (tabla `leyenda_litologia`).
- **Composición del desmonte LE2** (tabla `composicion_desmonte_LE2`): Mármol 38.9 %, Hornfels 19.2 %, Marga-Limolita 18.9 %, Intrusivo 15.0 %, Caliza 8.0 %.
- **UCS de referencia**: compresión uniaxial directa; la carga puntual convertida sobreestima 1.5–1.75× en mármol y hornfels (tabla `UCS_directa_vs_PLT`).
- **Clase de desmonte** asignada por criterio cuando el informe no la da; el respaldo queda en `clase_confianza`.
- **Gs adoptado** por material o por litología (Golder 2010, ASTM D854) y e0 recalculado (`Gs_adoptado`, `e0_adoptado`).

## 8. Vacíos que la base no puede cubrir

1. **Margas y limolitas (19 % del desmonte LE2)** no tienen ningún ensayo de resistencia, de índice ni de durabilidad.
2. **Mármol**: la litología dominante (39 %) y la más débil (UCS directa 48 MPa) solo tiene ensayos de gran escala como enrocado seleccionado, no como ROM.
3. No hay ensayos de resistencia con σ′3 > 2.45 MPa ni ensayos no drenados de gran escala.
4. El Gs de los lotes de 1 m (WSP 2022, IDIEM 2025) y de las muestras Anddes no se ensayó.
5. El archivo «Resultados de Laboratorio.zip» del RFI 115-G-0047 (lixiviación ácida) no está en la carpeta.
