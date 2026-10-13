# Verificación independiente: propiedades índice y condiciones de campo y laboratorio

Esta revisión la hace un agente distinto del que extrajo los datos. Se lee el informe original, se comprueba cada número en la imagen de la página y se compara con el CSV ya extraído. **Ninguna cifra se acepta sin verla en la página.**

## A. Tabla de condiciones: `condiciones_<fuente>.csv` (una fila por set)

### Origen y condición de campo

| Columna | Contenido |
|---|---|
| fuente, set_id | Igual que en el CSV extraído |
| origen_muestra | Tajo, fase, banco, botadero, ruma, calicata o acopio; con fecha de muestreo si existe |
| clase_desmonte | ROM, Chancado, Enrocado o «no indicada». Decir textual en qué se basa |
| litologia, litologia_detalle, litologia_proporcion | Composición litológica y cómo se determinó (descripción visual, conteo de fragmentos, petrografía) |
| Dmax_campo_mm | Tamaño máximo de terreno |
| granulometria_campo | D10, D50, D80 y Dmax de terreno, o «no informada» |
| densidad_campo | Densidad in situ o de colocación, con método (reemplazo, nuclear, supuesta) |

### Preparación de la probeta

| Columna | Contenido |
|---|---|
| escalamiento_metodo | Paralelo, truncado (scalping), reemplazo u otro; texto del informe |
| Dmax_lab_mm, D_probeta_mm, H_probeta_mm, D_sobre_Dmax | Dimensiones y razón diámetro de probeta / tamaño máximo |
| granulometria_lab | D10, D30, D50, D60, Cu, Cc y % de finos de la curva de ensayo, y si se recalcularon |
| preparacion | Método de compactación (pisón, vibración, capas), número de capas y criterio de densidad: γd objetivo, % del Proctor o Dr. Indicar si es suelta, densa o de colocación |
| gamma_d_montaje_kNm3 | Peso unitario seco de montaje |
| w_montaje_pct | Humedad de montaje |
| Gs_valor | Valor de Gs usado |
| Gs_origen | Ensayado sobre el mismo material, de otro informe (cuál), supuesto, o leído de la curva de saturación del Proctor |
| e0_recalculado | Recalculado aquí con Gs_valor y γd, para comparar con el CSV |

### Condiciones del ensayo

| Columna | Contenido |
|---|---|
| saturacion | Método y valor de B |
| contrapresion_kPa | Contrapresión aplicada |
| consolidacion | Isotrópica o anisotrópica, σ′3c, duración |
| gamma_d_post_consolidacion_kNm3 | Si se informa |
| drenaje_corte | Drenado o no drenado |
| velocidad_pct_min | Velocidad de deformación |
| deformacion_final_pct | Deformación al terminar el ensayo |
| criterio_falla_informe | Criterio que usa el informe |
| hay_pico | Sí o no |
| hay_curva_tabulada | Si existe curva tabulada para recalcular otros criterios |

### Rotura y propiedades de la roca

| Columna | Contenido |
|---|---|
| Bg_metodo | Granulometría antes y después; tamices usados |
| UCS, Is50, LA_pct, durabilidad, absorcion_pct | Propiedades índice de la roca, con su origen exacto (probetas, número de ensayos, norma, informe) |

## B. Esfuerzos en ensayos no drenados

Corregir y separar las magnitudes en `<fuente>_verificado.csv`:

- `sigma3c_kPa`: σ′3 de consolidación.
- `sigma3f_kPa` y `sigma1f_kPa`: esfuerzos efectivos en la falla.
- `u_falla_kPa`: presión de poros en la falla.
- `q_kPa`: desviador, igual a σ1f − σ3f.

Registrar dos estados de falla cuando el informe permita calcularlos:

- máximo desviador;
- máxima oblicuidad σ′1/σ′3.

## C. Entregables

- `condiciones_<fuente>.csv`.
- `<fuente>_verificado.csv`: copia del CSV extraído con las correcciones aplicadas.
- `verificacion_<fuente>.md`: lista de discrepancias. Para cada una indicar columna, valor anterior, valor correcto, página y razón.

No se borran filas. Si un dato no existe en el informe, se escribe «no informado»; nunca se supone.
