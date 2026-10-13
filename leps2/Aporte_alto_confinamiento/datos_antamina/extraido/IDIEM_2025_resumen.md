# IDIEM 2025: triaxiales a gran escala, Codisposal 1 (100 % Intrusivo)

**Fuente:** `2025_IDIEM_Triaxiales Gran Escala Codisposal 100 Intrusivo.pdf` (32 páginas: 31 del informe y 1 de repositorio)
**Informe:** IDIEM, Informe de Ensayo Especial N°1.966.314-B, Rev. 01, «Ensayos triaxiales a gran escala – Fase 2 y 3». Referencia DGL.PRE.2341.2024-0012r2. Elaborado el 23-01-2025 y aprobado el 24-01-2025.
**Cliente:** WSP Perú S.A. para Compañía Minera Antamina S.A.
**Laboratorio:** IDIEM, División Geotecnia Laboratorio (Santiago, Chile).
**CSV:** `IDIEM_2025.csv` (3 probetas, 1 set).

## Objetivo y materiales

- El proyecto completo (Tabla 1, pp. 3-5) contempla triaxiales CID de 100 × 180 cm sobre cinco mezclas de co-disposición. Codisposal 1 es 100 % Intrusivo; Codisposal 2 es 67 % Intrusivo y 33 % Relave; Codisposal 3 es 80/20; Codisposal 4 es 86/14; Codisposal 5 es 89/11. Todas se ensayan a 5, 10 y 20 kgf/cm² con densidad seca de 2,1 g/cm³.
- El proyecto también incluye 6 CID de carga y descarga («por definir»), 5 ensayos de consolidación + permeabilidad en celda de 100 cm y granulometrías post-ensayo.
- **Este informe solo presenta la serie Codisposal 1 (100 % Intrusivo).** El resto figura como pendiente («---»). Las granulometrías iniciales de Intrusivo y Relave se entregaron en el informe 1.966.314-A, que no está en este set.
- Muestras recibidas el 12, 14 y 16 de agosto de 2024 (Tabla 2, p. 6): Intrusivo 139 184 kg y Relave 64 864 kg, ambas perturbadas (P) y en maxisacos.
- **Clase de desmonte (ROM, Chancado o Enrocado): el informe no la indica.** Solo dice «Intrusivo». En el CSV queda como «Mezcla co-disposición: clase de desmonte no indicada + 0 % relave».

## Clasificación litológica

| Muestra / set | litologia_informe | litologia | litologia_detalle | litologia_proporcion | alteracion | tipo_material |
|---|---|---|---|---|---|---|
| Codisposal 1 (probetas 1-3) | Intrusivo | Intrusivo | (no indicado) | (no es mezcla de litologías; 0 % relave) | (no indicada) | Mezcla co-disposición con 0 % relave; clase ROM, Chancado o Enrocado no indicada |
| Relave (para Codisposal 2-5, no ensayado aquí) | Relave | (no es desmonte) | — | — | — | — |

El informe no describe la mineralogía, el subtipo (monzonita, pórfido, etc.), la alteración ni el origen de la muestra (tajo, banco o fase): la Tabla 2 deja calicata y cota en «---». Tampoco da propiedades de la roca (UCS, carga puntual, Los Ángeles, absorción ni Gs).

## Metodología (p. 8)

- El cliente define la densidad seca de montaje, las presiones efectivas de confinamiento y la banda granulométrica. El material se corta en **7"** (escalamiento por truncado).
- Montaje por capas en molde rígido con geomembrana. Saturación con B ≥ 0,95. Consolidación hasta que la deformación volumétrica se estabiliza. Corte **a carga controlada** con escalones de esfuerzo vertical. La velocidad de deformación no se informa.
- Las tablas dan ε_a, ε_v, p = (σ1+σ3)/2 y q = (σ1−σ3)/2 en kgf/cm² (**notación MIT**). En el CSV, q_kPa es el desviador σ1−σ3 = 2·q_MIT.

## Resultados (pp. 10-28; resumen en Tabla 4, p. 29)

| Probeta | σ3′ (kgf/cm²) | σ3′ (kPa) | q_MIT máx (kgf/cm²) | σ1−σ3 (kPa) | σ1′ (kPa) | ε_a falla (%) | ε_v falla (%) | φ_sec calc. (°) | ρd post-cons. (g/cm³) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | 5,0 | 490,3 | 8,57 | 1680,9 | 2171,2 | 3,98 | −2,02 | 39,2 | 2,12 |
| 2 | 10,0 | 980,7 | 17,58 | 3448,0 | 4428,7 | 12,97 | −5,79 | 39,6 | 2,19 |
| 3 | 20,0 | 1961,3 | 34,29 | 6725,4 | 8686,7 | 11,18 | −9,04 | 39,2 | 2,31 |

- Los valores en la falla se tomaron de las tablas numéricas (parseo por coordenadas de PyMuPDF) y se comprobaron en las imágenes de las pp. 14, 20 y 27 y en los gráficos de las pp. 15, 21 y 28. **No son lecturas de gráfico.**
- σ3′ = presión de cámara − contrapresión: 6−1, 12−2 y 21−1 kgf/cm².
- El informe **no da φ, c ni ninguna envolvente.** El φ_sec de la tabla lo calculé yo como asin(q/p); en el CSV va en `notas`, no en `phi_sec_deg`.
- Volumen drenado en consolidación: 16 200, 57 500 y 131 400 cm³ (ε_v,cons ≈ 1,15 %, 4,07 % y 9,29 %). Comprobé que concuerdan con las densidades post-consolidación de 2,12, 2,19 y 2,31 g/cm³.
- Comportamiento:
  - Probeta 1: pico frágil a ε_a ≈ 4 %. Luego q_MIT cae a ~5,8 kgf/cm² a ε_a = 19 %, con contracción máxima de −2,38 % y dilatancia posterior hasta −1,39 %.
  - Probetas 2 y 3: endurecimiento hasta una meseta a ε_a ≈ 11-13 %, con contracción sostenida (−5,8 % y −9,0 %). Los ensayos terminan en ε_a = 15,0 % y 16,7 %.
- Convención de ε_v: **negativo = contracción**. El informe no la declara; la inferí de la forma de las curvas.

## Granulometría de ensayo (Gráfico 1, p. 8)

Es una sola curva de montaje, presentada solo como gráfico (imagen raster). La digitalicé por detección de marcadores con un error de ±0,5 %. Valores en % que pasa:

| Tamiz (mm) | 0,075 | 0,106 | 0,25 | 0,425 | 0,85 | 2,0 | 4,75 | 9,5 | 19 | 25 | 37,5 | 50 | 63 | 75 | 100 | 125 | 150 | 177,8 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| % pasa | 5,5 | 6,7 | 10,7 | 12,6 | 14,9 | 17,7 | 21,2 | 24,4 | 30,8 | 35,1 | 42,3 | 47,0 | 56,3 | 65,2 | 84,9 | 95,1 | 98,2 | 100 |

Parámetros derivados por interpolación log-lineal: D10 ≈ 0,22 mm, D30 ≈ 17,4 mm, D50 ≈ 53,9 mm, D60 ≈ 67,7 mm, Cu ≈ 315 y Cc ≈ 20,8. Grava 78,8 %, arena 15,7 % y finos 5,5 %. Dmax = 7" (177,8 mm). El Cc alto indica una curva con déficit de tamaños intermedios (gap-graded).

## Ensayos índice, permeabilidad, edómetros y ensayos no drenados

- No se informan Gs, UCS, Los Ángeles, durabilidad ni límites. **Sin Gs no se puede calcular e0.**
- Los ensayos de consolidación + permeabilidad y las granulometrías post-ensayo (Bg) están pendientes. No hay ensayos no drenados.

## Dudas y datos ilegibles

1. Gs no se informa, así que e0 queda vacío. Sería útil buscarlo en el informe 1.966.314-A o en los informes de WSP.
2. No se sabe la clase de desmonte (ROM, Chancado o Enrocado) de la muestra «Intrusivo».
3. En la probeta 2 el máximo ocurre en la meseta final, y el ensayo termina en ε_a = 15 % sin caída clara. El pico podría estar algo subestimado.
4. El pie del Gráfico 4 (p. 28) dice «probeta 1», pero corresponde a la probeta 3 (σ3′ = 20 kgf/cm²).
5. La convención de signo de ε_v no está declarada (ver arriba).
6. La Tabla 4 se titula «Resumen resultado Granulometría Inicial», pero en realidad resume las densidades de consolidación. Parece un error de título.
