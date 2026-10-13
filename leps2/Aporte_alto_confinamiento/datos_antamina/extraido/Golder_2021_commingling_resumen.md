# Golder 2021: ensayos de laboratorio en mezclas commingling (desmonte + relave)

**Fuente:** `2021_Golder_Ensayos de Laboratorio Commingling.pdf` (205 páginas).
**Informe:** Golder Associates Perú (miembro de WSP), *Estudio Conceptual Almacenamiento Eco-Estable de Desmonte y Relaves. Informe de interpretación de ensayos de laboratorio*, 101-20110-LTE01220-INF-420-G-0013, Rev. 0, 28/04/2021. Las páginas 1–32 son el cuerpo del informe y las páginas 33–205 son los anexos A a H.
**Laboratorio:** Golder Lima (todos los ensayos geotécnicos) y BIZALab Lima (DRX).
**Datos:** `Golder_2021_commingling.csv` tiene 36 filas: 30 probetas triaxiales CID y 6 ensayos de permeabilidad.

Las 16 páginas sin texto (33, 41, 56, 71, 96, 178, 185 y 196–205) son carátulas de anexo o la contraportada. No contienen datos.

## Objetivo y materiales

El informe caracteriza mezclas de desmonte y relave para las Alternativas 1, 2 y 4 del estudio conceptual de co-disposición en los depósitos Yanacancha y Valle C (ES1DDE, ES2DDE, EE3DDE y EE4DDE).

- **Desmonte:** muestras Tipo A, Tipo B y Tipo C, recibidas el 11/08/2020. El compuesto se armó con 0.35 A : 0.15 B : 0.50 C en masa seca, según el LOM EVA1/EVA3A. Todo el desmonte se truncó a menos de 1" (25.4 mm) por las limitaciones del equipo (p. 6 y 9).
- **Relave:** compuesto 1/3 M1 : 1/3 M2A : 1/3 M4B, preparado con el segundo lote. El primer lote no era representativo (p. 9).
  - Alternativa 1: relave filtrado, con ~86 % de sólidos.
  - Alternativa 2: relave en pasta, con ~80 % de sólidos.
  - Alternativa 4: relave cicloneado, con ~86 % de sólidos y 80 % de gruesos / 20 % de finos.
- **Mezclas:** desmonte:relave 9:1, 4:1 y 1:1 en masa seca, es decir 10, 20 y 50 % de relave.
- **Clase de desmonte (ROM / Chancado / Enrocado):** el informe no la indica. Por eso `tipo_material` dice «clase no indicada». Las letras A, B y C son una tipificación geoquímica por potencial de generación de acidez, no una clase de manejo. El propio informe recomienda volver a muestrear según la fuente geológica (p. 27 y 29).
- **Origen:** el informe no da tajo, banco ni fase.
- **Alteración:** no se indica para ninguna muestra.

## Litología: clasificación y propiedades por litología

| Muestra (ID) | Litología del informe | Litología normalizada | Gs bulk / SSS / aparente (ASTM C127) | Absorción % | Gs finos | D50 / D85 mm | Grava / arena / finos % | SUCS | Páginas |
|---|---|---|---|---|---|---|---|---|---|
| Tipo A (II0336) | intrusivo | Intrusivo | 2.44 / 2.53 / 2.67 | 3.39 | – | 3.6 / 17.9 | 45.3 / 41.2 / 13.5 | GM | 6, 11, 14, 43, 83 |
| Tipo B (II0337) | mármol y hornfels | Mezcla (Mármol + Hornfels, reparto no indicado) | 2.87 / 2.90 / 2.97 | 1.22 | – | 3.9 / 15.4 | 46.2 / 40.9 / 12.9 | GM | 6, 11, 14, 44, 84 |
| Tipo C (II0338) | hornfels | Hornfels | 2.70 / 2.72 / 2.75 | 0.61 | – | 9.5 / 18.7 | 68.2 / 24.6 / 7.2 | GM (hoja de laboratorio: GP-GM) | 6, 11, 14, 45, 85 |
| Compuesto de desmonte (II0471) | Tipo A, B, C | Mezcla: Intrusivo 35 %; Mármol + Hornfels 15 %; Hornfels 50 % | 2.71 / 2.72 / 2.75 | 0.54 | 2.77 | 7.4 / 18.2 | 59.5 / 30.8 / 9.7 | GP-GM | 11, 15, 46, 73, 86 |
| Compuesto de relave (II0498) | relave M1, M2A, M4B | Otra (relave) | – | – | 3.31 | 0.1 / 0.3 | 0.2 / 59.8 / 40.0 | SM | 11, 15, 42, 72 |

Notas sobre la tabla:

- Los valores de Gs, absorción y granulometría de A, B, C y del compuesto se verificaron en las imágenes de las páginas 11, 14, 46 y 83–86. Los D60/D10 de A, B y C (p. 43–45) vienen solo del texto. A y B no tienen hidrómetro, así que su «finos» incluye limo y arcilla.
- La hoja de Gs del Tipo B (p. 84) lleva el ID II0336 en lugar de II0337. Parece un error de copia.
- **UCS, carga puntual, Los Ángeles y durabilidad:** no se ensayaron.
- **Mineralogía:** solo hay DRX de los relaves del primer lote, que no se usó en las mezclas (p. 24–25).
  - M1: cuarzo 34 %, feldespato K 25 %, plagioclasa 16 %, granate 14 %.
  - M2A: granate 36 %, feldespato K 15 %, calcita 10 %, cuarzo 9 %.
  - M4B: granate 32 %, calcita 16 %, diópsido 12 %, cuarzo 10 %, pirita 5 %.
  - No hay arcillas por encima del límite de detección.
  - El texto de la p. 24 cita «granate 32 % y cuarzo 34 %» como los mayores porcentajes, pero esas cifras vienen de muestras distintas.
- **Gs de los gruesos en las mezclas (C127, bulk):** entre 2.67 y 2.71, con absorción de 0.57 a 0.90 % (p. 87–95).
- **Gs de los finos en las mezclas (D854):** 2.86–2.87 para 9:1, 2.94–2.96 para 4:1 y 3.12–3.13 para 1:1 (p. 15 y 74–82).

## Programa de ensayos

| Tipo de ensayo | Sets | Probetas | Notas |
|---|---|---|---|
| Triaxial CID (ASTM D7181), saturado | 10 | 30 | 1 compuesto de desmonte + 9 mezclas (Alt. 1, 2 y 4 × 9:1, 4:1 y 1:1); σ3' ≈ 100, 400 y 1200 kPa |
| Permeabilidad, pared flexible (ASTM D5084) | 6 | 6 | Mezclas 9:1 y 1:1 de cada alternativa, a σ' = 399 kPa |
| No drenados (CU/CIU) | 0 | 0 | No hay. El informe los recomienda para una etapa posterior (p. 28 y 30) |
| Corte directo, edómetro | 0 | 0 | No hay |
| Proctor estándar (ASTM D698) | 10 | – | Solo en el resumen (abajo) |
| Límites de Atterberg | – | – | Todas las muestras son NP |

**Detalles de las probetas triaxiales:**

- Probetas de 152.4 mm × 305 mm, con Dmax = 25.4 mm. La relación D/Dmax es 6, en el límite inferior habitual.
- Densidad seca de remoldeo:
  - Compuesto de desmonte: ρd ≈ 2.09 g/cm³ (γd = 20.5 kN/m³), w = 2 %.
  - Mezclas: ρd = 1.802 g/cm³ (γd = 17.7 kN/m³), «según solicitud del cliente», con w entre 1.6 y 8.5 %.
- Relación de vacíos inicial: e0 = 0.32 en el compuesto y entre 0.55 y 0.67 en las mezclas.
- Saturación con B entre 0.95 y 1.0. Velocidad de 0.111 %/min. El ensayo llega hasta εa ≈ 20 %.
- **Rango de σ3':** de 96 a 1206 kPa. No hay confinamientos mayores a 1.2 MPa.

## Envolventes ajustadas por el informe (Mohr-Coulomb, efectivas)

| Material | Tabla 7 (p. 19): c kPa / φ° | Hoja de laboratorio (página): c / φ |
|---|---|---|
| Compuesto de desmonte | 0 / 40 | 0 / 41 (p. 112) |
| Alt. 1 – 9:1 | 84 / 40 | 83 / 40 (p. 119) |
| Alt. 1 – 4:1 | 59 / 40 | 58 / 40 (p. 126) |
| Alt. 1 – 1:1 | 24 / 38 | 22 / 38 (p. 133) |
| Alt. 2 – 9:1 | 53 / 40 | 53 / 40 (p. 140) |
| Alt. 2 – 4:1 | 41 / 40 | 41 / 40 (p. 147) |
| Alt. 2 – 1:1 | 29 / 39 | 29 / 39 (p. 154) |
| Alt. 4 – 9:1 | 62 / 40 | 62 / 40 (p. 161) |
| Alt. 4 – 4:1 | 66 / 39 | 66 / 39 (p. 168) |
| Alt. 4 – 1:1 | 51 / 37 | 51 / 37 (p. 175) |

El informe atribuye la cohesión aparente a la trabazón de partículas angulares (p. 29). No se ajustaron envolventes de Leps ni de potencia.

En el CSV, la columna `notas` trae el φsec calculado (c = 0) de cada probeta a partir de q de la Tabla 8:

- A σ3' ≈ 100 kPa, el φsec va de 36.2° (compuesto denso, en el pico) a 49.0°.
- A σ3' ≈ 400 kPa, va de 38.8° a 45.4°.
- A σ3' ≈ 1200 kPa, va de 37.5° a 41.3°.

## Proctor estándar (Tabla 6, p. 18)

γd,máx varía entre 22.0 y 23.0 kN/m³ y la wópt entre 5.6 y 7.5 %.

- Compuesto de desmonte: 22.7 kN/m³ y wópt 6.5 %.
- Las probetas triaxiales de las mezclas (17.7 kN/m³) quedaron a cerca del **78 % del Proctor estándar**, es decir, sueltas.
- Para la Alt. 1 – 1:1, la Tabla 6 da wópt = 6.3 % y el texto de la p. 15 da 6.0 %.

## Permeabilidad (Anexo G, p. 179–184; Tabla 9, p. 23)

Todos los ensayos se hicieron a σ' = 399 kPa con ρd inicial de 1.80 g/cm³.

| Mezcla | k20 en la hoja de laboratorio (m/s) | Tabla 9 (m/s) |
|---|---|---|
| Alt. 1 – 9:1 | 5.6E-06 | 5.60E-06 |
| Alt. 1 – 1:1 | **8.9E-07** | **8.90E-06**: no coincide |
| Alt. 2 – 9:1 | 8.1E-06 | 8.10E-06 |
| Alt. 2 – 1:1 | 1.4E-06 | 1.40E-06 |
| Alt. 4 – 9:1 | 6.7E-06 | 6.70E-06 |
| Alt. 4 – 1:1 | 2.5E-06 | 2.50E-06 |

La densidad seca final de cada ensayo de permeabilidad es igual a la de la probeta triaxial de 400 kPa tras consolidar. Todo indica que se midió sobre esas mismas probetas.

## Dudas, discrepancias y datos ilegibles

1. **Permeabilidad de Alt. 1 – 1:1.** La hoja da 8.9E-07 m/s y la Tabla 9 y la Figura 11 dan 8.90E-06 m/s. En el CSV se adoptó la hoja. Con el valor de la hoja desaparece la tendencia que el informe describe para la Alt. 1 (k que aumenta con el relave, p. 29); en las tres alternativas la k bajaría con más relave.
2. **e0 de Alt. 4 – 4:1 a 1204 kPa.** La Tabla 8 (p. 22) dice 0.23. La hoja (p. 166) y el cálculo con Gs/ρd dan 0.58, y se adoptó 0.58.
3. **Criterio de falla.**
   - Las hojas de laboratorio dicen «Esfuerzo Desv. Máximo», pero reportan σ1' a εa ≈ 16 % (o al final del ensayo en el compuesto), que no es el máximo de su propia tabla. Los círculos de Mohr del laboratorio usan esos valores.
   - El CSV usa el máximo desviador de la Tabla 8. En las Alt. 2 y 4 coincide con el máximo de la hoja. En la Alt. 1 y el compuesto difiere entre −0.8 y +0.7 %.
4. **Probetas sin pico.** En 18 de las 30 probetas el máximo desviador está en la última lectura (εa ≈ 20 %, o 13.85 % en una). Siguen endureciendo y contrayendo, así que q es «máximo hasta el fin del ensayo», no un pico. Solo la probeta densa del compuesto a 98 kPa muestra un pico (εa ≈ 4 %) con dilatación.
5. **Alt. 2 – 4:1 a 1200 kPa (p. 145).** El ensayo terminó a εa = 13.85 %; las filas finales repetidas están en rojo.
6. **Alt. 4 – 1:1 a 400 kPa (p. 172).** σ3' cayó a 383–396 kPa al final del corte.
7. **Columnas «Etapa final de corte» de la Tabla 8 en el compuesto de desmonte.** No coinciden con las hojas de laboratorio.
8. **Alt. 1 – 9:1 a 101 kPa en la Tabla 8.** El ρd antes del corte (2.163) es igual al ρd final de corte; probable error de copia.
9. **Granulometría (Tabla 4).** La columna «limos» de las mezclas es en realidad el pasante del tamiz #200 (limo + arcilla). En el compuesto sí es solo limo (9.2 + 0.5 de arcilla = 9.7 % de finos). El CSV usa el pasante #200 de las hojas del Anexo B (p. 46–55), y en algunas mezclas difiere ligeramente de la Tabla 4.
10. **Errores de texto del informe.** En la p. 11, «D85 entre 15.3 mm a 187 mm» debe ser 18.7 mm. La p. 28 invierte D85 y D50 del relave.
11. **Representatividad.** El informe advierte que los resultados de muestras truncadas a 1" no representan el material a escala real (p. 29). No hay escalamiento paralelo.
12. **Ausencia de ensayos.** No hay ensayos no drenados, edómetros, corte directo, UCS, Los Ángeles ni índices de rotura (Bg). Tampoco hay granulometría post-ensayo.

## Verificación

Se verificaron en imagen (150 dpi, en `paginas/Golder2021/`):

- Tablas 4, 6, 7, 8 y 9 (p. 11, 12, 18, 19, 20–23).
- Las 30 hojas triaxiales y las 10 hojas de envolvente.
- Las 10 granulometrías de los materiales ensayados (p. 46–55).
- Las 6 hojas de permeabilidad.
- Las hojas de Gs de los gruesos de A, B, C y del compuesto (p. 83–86).

Las tablas numéricas de cada hoja triaxial se extrajeron por texto y se controlaron internamente: σ1' − σ3' = desviador y p' = (σ1' + σ3')/2 en todas las filas usadas.

Scripts usados: `render.py`, `parse_triax.py`, `check.py`, `gran.py`, `gran2.py`, `gs_abs.py` y `build_csv.py`.
