# Verificación independiente: WSP 2024 (co-disposición, Fase 1) e IDIEM 2025 (Codisposal 1, 100 % intrusivo)

Fecha: 2026-10-06. Revisor distinto del extractor. Cada cifra se comprobó en la imagen de la página (PNG en `paginas/verificacion/WSP2024_IDIEM2025/`). Los máximos de las tablas triaxiales se recalcularon con un parser propio (`parse_wsp24_tx.py`, `parse_idiem25.py`), independiente del usado en la extracción.

Páginas citadas = página del PDF (no la numeración interna del anexo).

## 1. Resumen

| Fuente | Filas | Valores de ensayo (σ′3, σ1, q, εa, εv, Bg, finos post) | Discrepancias en el CSV | Celdas corregidas |
|---|---|---|---|---|
| WSP 2024 | 18 | Todos correctos (18/18) | 5 | tipo_material 15, litologia_proporcion 18, escalamiento 18, notas 18 |
| IDIEM 2025 | 3 | Todos correctos (3/3) | 2 menores, en notas | notas 3 |

Ningún valor numérico de resistencia, deformación, densidad, Gs ni e0 del CSV estaba equivocado. Las correcciones afectan la descripción del material (contenido real de relave), el origen del Dmax de 10″ y una cifra de las notas (rango de UCS).

**Autocorrección:** en la primera pasada mi parser dio otros máximos para C2 carga-descarga a 490 y 980 kPa (2263,4 y 3677,5 kPa). La causa era un error de mi parser, que descartaba las filas superiores de las páginas de continuación. Ya corregido, reproduce exactamente los valores del extractor (2267,3 y 3703,0 kPa), y la p.169 confirma el máximo q = 11,56 kgf/cm² en εa = 7,93 %.

## 2. Discrepancias

### WSP 2024: `WSP_2024_codisposicion.csv`

| # | Columna (filas) | Valor anterior | Valor correcto | Página | Razón |
|---|---|---|---|---|---|
| 1 | `tipo_material` (C1, C2, C3; 15 filas) | «… + 22 % / 18 % / 15 % relave» | «… + 13,1 % / 10,7 % / 9,0 % relave en masa seca total (nominal 22/18/15 % aplicado solo a la fracción < 3/4″)» | 267-268, 142-143, 231-232, 108; 93, 355; 12; 221-222, 257, 344 | Ver §3(a). IDIEM indica «agregar un X % de Relave integral … se trabaja el material integral bajo ¾″». La curva de montaje coincide con el desmonte sobre 3/4″. |
| 2 | `litologia_proporcion` (18) | «Desmonte intrusivo 78 %; relave 22 % (nominal en masa)…» | Nominal y efectivo por separado (C1: desmonte 86,9 %, relave 13,1 %; C2: 89,3/10,7; C3: 91,0/9,0). La fracción tonalita/caliza se indica como conteo de 38 fragmentos, no como masa. | ídem; 356-362 | La proporción nominal no corresponde a la masa total de la probeta. |
| 3 | `escalamiento` (18) | «truncado (scalping) a 4″; Dmax de terreno 10″» | «truncado a 4″; Dmax de la muestra recibida en laboratorio 10″; granulometría de terreno no informada» | 89, 93 | Los 10″ son el Dmax de los 5 maxisacos que recibió IDIEM, no una granulometría de terreno. |
| 4 | `notas` (18) | «UCS … rango 64.0–143.1 MPa, Tabla 6 p.12» | «rango 61.1–143.1 MPa» | 12 | La Tabla 6 tiene 7 valores: 100,6; 143,1; 64,0; 117,8; 76,0; 103,6; **61,1**. El texto del informe dice «desde 64.0», lo que es un error del propio informe. La media de 95,2 MPa es correcta. |
| 5 | `notas` (C1-C3; 15) | «… (≈13.1 % de la masa total); duda abierta» | Duda resuelta, con las evidencias | ver #1 | §3(a). |

Además, en las 18 filas se añadió a `notas` el origen exacto del Gs, la advertencia de que UCS, Los Ángeles y Gs > N°4 son de muestras distintas del lote de IDIEM, y la convención de εv declarada por IDIEM. Son complementos, no correcciones.

### IDIEM 2025: `IDIEM_2025.csv`

| # | Columna (filas) | Valor anterior | Valor correcto | Página | Razón |
|---|---|---|---|---|---|
| 6 | `notas` (probeta 1) | «q_MIT cae de 8,57 a ~6,0 kgf/cm² tras ea ≈ 8 %» | «cae de 8,57 (εa 3,98 %) a 6,72 en εa = 8,05 % y a 5,80 al final (εa = 19,09 %)» | 14 | En εa = 8 % el valor es 6,72; recién llega a ≈6,0 en εa = 16,15 %. |
| 7 | `notas` (3) | «Humedad de confección 0,00 % (montaje seco, luego saturado…)» | «0,00 % según hoja (el informe no describe si el montaje fue seco)» | 8, 10 | «Montaje seco» es una interpretación; el informe no lo dice. |

En las 3 filas se añadió a `notas` el Gs no informado, el e0 condicional, la relación con WSP 2024 y la convención de εv.

### Observaciones sobre los `_resumen.md` del extractor (no son CSV; no se modificaron)

- WSP, §2: «UCS de 64.0 a 143.1 MPa» debe decir **61,1–143,1 MPa**.
- WSP, §2: los cuatro Is50 (5,48 / 4,36 / 4,11 / 6,16 MPa) no son «por set». Son cuatro hojas de la muestra «100% Intrusivo» (IDIEM 1.914.482-G, ensayada del 08 al 11-04-2024).
- WSP, §5, Tabla 12: e0 = 0,418 para C1 es el valor de WSP. La hoja IDIEM del edómetro C1 (p.328) da **0,413**, y para C3 da 0,407 frente al 0,408 de WSP. Es una inconsistencia interna del informe y no afecta los triaxiales.
- WSP: Gs < N°4 = 2,97 (C2) y 2,94 (C3) aparecen solo en la Tabla 5 de WSP (p.12). En el anexo IDIEM esos ensayos figuran «pendientes» (p.264) y no tienen hoja.
- IDIEM 2025, §Granulometría: los tamices 0,106 / 0,425 / 0,85 mm son aproximaciones. IDIEM usa 0,110 / 0,42 / 0,84 mm, y la diferencia no altera D10–D60.

## 3. Puntos abiertos

### (a) Contenido real de relave: resuelto, ≈13,1 / 10,7 / 9,0 % de la masa seca total

Cinco evidencias independientes:

1. **Metodología IDIEM** (p.108, 142, 231, 267): «el cliente ha decidido cortar el material Desmonte de Mina (Intrusivo) en 4″ y agregar un 18 % de Relave integral … cabe destacar que se trabaja el material integral bajo ¾″». En C4 el texto es el mismo, sin relave.
2. **Curva de montaje (Gráfico 1, imagen ampliada).** Sobre 3/4″ la curva roja «TEÓRICA» es idéntica a la del desmonte (59,7 % pasa 3/4″). El cálculo exacto (desmonte p.93 truncado a 4″ + relave p.355) separa las dos hipótesis:

   | Mezcla | Pasa N°4 leído | Hipótesis B (relave solo < 3/4″) | Hipótesis A (relave en masa total) | Pasa N°60, C1: leído / B / A |
   |---|---|---|---|---|
   | C1 | 33,9 | 34,0 | 42,8 | 15,9 / 16,0 / 21,1 |
   | C2 | 32,8 | 32,6 | 39,9 | |
   | C3 | 31,4 | 31,6 | 37,7 | |

   A 3/4″ la hipótesis A daría 68,5 % para C1, y el gráfico muestra 59,7 %.
3. **Gs global de WSP (Tabla 5).** Recalculado con la fórmula del propio informe, la hipótesis B da 2,935 / 2,902 / 2,892, y el informe dice 2,93 / 2,90 / 2,89. La hipótesis A daría 2,952 / 2,909 / 2,896.
4. **Granulometrías post-ensayo** (p.344, 221-222, 257). C1 tiene 33,6 % (C/D a 490 kPa), 36,0 % (C/D a 980 kPa) y 37,1 % (monótona a 490 kPa) pasante N°4 después del ensayo. Con la hipótesis A el inicial sería 42,8 % y la rotura habría *reducido* el pasante, lo que es imposible. Los finos post de C1 C/D a 490 kPa (6,9 %) también son menores que el inicial de la hipótesis A (8,1 %), y compatibles con el de la hipótesis B (7,0 %).
5. **Gs < N°4 medido** (3,07 / 2,97 / 2,94). Implica una fracción de relave en el pasante N°4 de 0,46 / 0,30 / 0,25. La hipótesis B predice 0,39 / 0,33 / 0,28 y la A 0,51 / 0,45 / 0,40. C2 y C3 coinciden con B; C1 queda entre ambas. Es el indicador más débil de los cinco.

**Resultado:** relave efectivo = r_nominal × 59,7 %, es decir 13,1 / 10,7 / 9,0 % en masa seca. La relación intrusivo:relave real es ≈6,6:1 / 8,3:1 / 10,2:1, no 3,5 / 4,5 / 5,5:1. Ni WSP ni IDIEM lo explican, y WSP sigue llamando a las mezclas «3.5 : 1» en todo el informe.

Las granulometrías de C1-C3 del CSV (digitalizadas) coinciden con el cálculo exacto dentro de ±0,2 % de pasante:

| Mezcla | D30 CSV / exacto (mm) | Cc CSV / exacto |
|---|---|---|
| C1 | 2,13 / 2,15 | 1,84 / 1,87 |
| C2 | 2,82 / 2,88 | 3,1 / 3,2 |
| C3 | 3,43 / 3,51 | 4,46 / 4,64 |

Se mantienen los valores del CSV.

### (b) Gs de IDIEM 2025, y si repite o complementa a WSP 2024

- **IDIEM 2025 no informa Gs.** Revisé las 32 páginas; tampoco trae UCS, carga puntual ni Los Ángeles. Las granulometrías iniciales están en el informe 1.966.314-A, que no está en el set.
- **No es el mismo material de WSP 2024.**

  | | WSP 2024 (Fase 1) | IDIEM 2025 (Fase 2-3) |
  |---|---|---|
  | Informes | IDIEM 1.914.482-A…G | IDIEM 1.966.314-B |
  | Lote | 46 191 kg de desmonte, recibido el 15-11-2023 (p.89) | 139 184 kg de intrusivo + 64 864 kg de relave, recibidos el 12-16-08-2024 (p.6) |
  | Probeta | 60×120 cm | 100×180 cm |
  | Dmax | 4″ | 7″ |
  | ρd de montaje | 2,00 g/cm³ | 2,10 g/cm³ |
  | w de montaje | 3 % | 0 % |
  | D50 | 13,3 mm | 53,9 mm |
  | Pasa N°4 | 26,7 % | 21,2 % |

  La curva de IDIEM 2025 tampoco es la del desmonte de Fase 1 truncada en 7″: con ese corte pasaría 96,8 % por 4″, y la curva de 2025 pasa 84,9 %.
- **La numeración cambia.** En WSP 2024, «Codisposal 4» es el 100 % intrusivo. En IDIEM 2025, «Codisposal 1» es el 100 % intrusivo, y las mezclas de Fase 2-3 son 67/33, 80/20, 86/14 y 89/11 (p.3).
- **IDIEM 2025 complementa a WSP 2024; no lo repite.** WSP 2024 lo anticipa en p.41: «se encuentra en proceso de ejecución la Fase 2 y 3».
- **Gs:** solo hay una referencia externa, el Gs global de WSP 2024 C4 = 2,85, que es de otro lote y otra curva. Reponderado con el pasante N°4 de 2025 da 2,855. Por eso e0 de IDIEM 2025 es **condicional**: 2,85/2,10 − 1 = **0,357** (0,344 / 0,301 / 0,234 después de la consolidación). En el CSV verificado, `Gs` y `e0` siguen vacíos y el condicional queda solo en `notas`.

### (c) Composición litológica: tonalita dominante con caliza

- **Recuento verificado en pp.356-362:** 38 fragmentos de carga puntual en 4 hojas, 31 de tonalita (82 %) y 7 de caliza (18 %). Por hoja: 8T+2C, 6T+2C, 9T+1C y 8T+2C.
- **Is50 de los fragmentos válidos:** tonalita 5,01 MPa (n = 26, rango 1,1–8,8); caliza 5,27 MPa (n = 7, rango 4,3–6,6).
- **Método:** es descripción visual del laboratorio sobre fragmentos de ≈37-58 mm. No hay petrografía ni conteo en masa, así que el 82/18 es un **porcentaje en número de fragmentos**, no en masa.
- **Lo que no dicen los informes:** el cuerpo de WSP 2024 nunca menciona tonalita ni caliza, e IDIEM 2025 no tiene ninguna descripción litológica.
- Las alteraciones del CSV están confirmadas: sericitización, cloritización y, localmente, epidotización, oxidación, arcillas y zeolitización. La caliza no presenta alteración.

### (d) Notación MIT en las hojas IDIEM: confirmada

- **Definición explícita:** todas las hojas dicen «q = (σ1−σ3)/2; p = (σ1+σ3)/2» (WSP 2024 p.111 y siguientes; IDIEM 2025 p.10 y siguientes), con p y q en kgf/cm².
- **Valores efectivos:** la primera fila tiene p = σ′3 (5,00 / 10,00 / 20,00) y q = 0, y p − q = σ′3 en todas las filas de las 24 probetas (0 excepciones). Por lo tanto son esfuerzos efectivos.
- **Desviador:** en ambos CSV, `q_kPa` = 2·q_MIT·98,0665 es el desviador, lo que es correcto.
- **Contradicción menor de WSP:** la nota (1) de la Tabla 9 (p.15) define «q = (σ′1−σ′3)» para los ciclos, mientras que p.19 usa τ = (σ′1−σ′3)/2.

## 4. Gs y e0 definitivos por set

| Set | ρd de montaje (g/cm³) | Gs (origen) | e0 = Gs/ρd − 1 | e después de consolidar (490/980/1960 kPa) |
|---|---|---|---|---|
| WSP24_C1 (MON y C/D) | 2,07 | 2,93 (Tabla 5 p.12) | **0,415** | MON 0,369/0,338/0,285 · C/D 0,382/0,369/0,326 |
| WSP24_C2 (MON y C/D) | 2,03 | 2,90 | **0,429** | MON 0,394/0,362/0,336 · C/D 0,388/0,355/0,318 |
| WSP24_C3 | 2,05 | 2,89 | **0,410** | 0,370/0,350/0,302 |
| WSP24_C4 | 2,00 | 2,85 | **0,425** | 0,411/0,351/0,332 |
| IDIEM25 Codisposal 1 | 2,10 | no informado | **no definitivo**; condicional 0,357 con Gs 2,85 de WSP 2024 | 0,344/0,301/0,234 (condicional) |

**Origen del Gs de WSP:** es el Gs global ponderado de la Tabla 5 (las hojas IDIEM lo describen como «Peso específico ponderado proporcionado por el cliente»). Combina:

- Gs **aparente** > N°4 = 2,87, promedio de 8 muestras de WSP Lima según ASTM C127. Esas muestras las tomó Antamina en feb-mar de 2024, no son el lote de IDIEM.
- Gs < N°4 medido por IDIEM según ASTM D854: 3,07 (C1, p.271), 2,80 (C4, p.110). Para C2 (2,97) y C3 (2,94) solo existe el valor de la Tabla 5.

Con el Gs **base seca** (media 2,78), más apropiado para relación de vacíos de enrocado con absorción del 1,1 %, el e0 sería ≈0,02-0,03 menor. Los e0 de la tabla son los que corresponden al Gs del informe; la propia WSP los calcula igual en los edómetros (p.30).

Los ρd después de consolidar del informe (Tablas IDIEM pp.130, 217, 219, 255, 339, 341; IDIEM 2025 p.29) se reproducen con ΔV/V0 dentro de ±0,005 g/cm³.

## 5. Confirmado como correcto (visto en imagen)

### WSP 2024

- **Montaje (hojas IDIEM, primera página de cada probeta):**
  - 60×120 cm; ρd 2,07 / 2,03 / 2,05 / 2,00; w = 3,0 %; contrapresión 1,0 kgf/cm²; cámara 6 / 11 / 21 kgf/cm².
  - Velocidad «--», es decir no informada; el corte es a carga controlada.
  - ΔV de consolidación de las 18 probetas igual a las notas del CSV.
- **σ′3 y valores en falla:**
  - σ′3 = 490,3 / 980,7 / 1961,3 kPa.
  - Máximo q, σ1, εa y εv de las 18 probetas, idénticos al CSV en su segundo decimal.
  - El máximo de oblicuidad coincide con el máximo desviador (σ′3 constante).
- **Deformación final:** entre 19,45 y 20,98 %.
- **Saturación y consolidación:** CO2 + agua y B > 95 % (p.17); consolidación isotrópica por incrementos continuos.
- **Tabla 9 (p.15) y ciclos de la Tabla 10 (p.18).**
- **Ángulos de fricción:** los φ′ del CSV reproducen la Fig. 13 (p.27). Ojo: el informe los da solo en gráfico; el valor numérico del CSV es calculado.
- **Rotura y finos:**
  - Bg de la Tabla 15 (pp.35-36): los 18 valores son correctos. Método de Marsal (1967).
  - Finos post-ensayo (pp.132, 221-222, 257, 344): los 18 valores son correctos.
- **Gs y densidades de referencia:**
  - Tablas 3 y 4 (p.11): Gs aparente 2,83–2,93 (media 2,87), Gs base seca 2,71–2,86, absorción 0,8–1,6 % (media 1,08 %).
  - Gs del relave: 3,42–3,50 (media 3,46) según WSP; 3,48 según IDIEM (p.97).
  - Proctor del relave: 2,20 g/cm³ con w óptima de 12,1 % (p.97).
- **Densidades mínima y máxima (Tabla 8, p.13; material < 3″):** 1,945/2,169; 1,914/2,158; 1,865/2,187; 1,825/2,212.
- **Granulometrías:** del desmonte (p.93) y del relave (p.355); C4 calculado exacto (D10 0,20; D30 5,59; D50 13,3; D60 19,2; Cu 96; Cc 8,13; finos 6,9 %).
- **Ensayos índice:**
  - UCS: media 95,2 MPa (ASTM D7012, Método C).
  - Los Ángeles: 21,2–39,9 %, media 30,4 %. Las fichas dicen ASTM C535 gradación 1 (p.75) y el texto dice C131 (p.13).
  - Is50: 5,48 / 4,36 / 4,11 / 6,16 MPa (p.364).
- **Fechas anómalas:**
  - C4 probeta 1 está fechada 10-01-2023 a 12-01-2023 (p.111), antes de la recepción del 15-11-2023.
  - C2 C/D probeta 1 tiene inicio 06-05-2024 y término 08-04-2024 (p.169).

### IDIEM 2025

- **Montaje:** 100×180 cm, ρd 2,10, w 0,00 % (pp.10, 16, 22).
- **Contrapresión y cámara:** contrapresión 1 / 2 / 1 y cámara 6 / 12 / 21 kgf/cm², que dan σ′3 = 5 / 10 / 20.
- **Velocidad:** «---», no informada.
- **Valores en falla:**
  - q_MIT máx 8,57 / 17,58 / 34,29.
  - εa 3,98 / 12,97 / 11,18; εv −2,02 / −5,79 / −9,04.
  - Desviador 1680,9 / 3448,0 / 6725,4 kPa (pp.14, 20, 27).
- **Final del ensayo:** εa 19,09 / 15,02 / 16,70.
- **Consolidación (Tabla 4, p.29):** ΔV 16 200 / 57 500 / 131 400 cm³ y ρd post 2,12 / 2,19 / 2,31.
- **Errores del propio informe:** el título de la Tabla 4 es incorrecto, y el pie del Gráfico 4 dice «probeta 1» cuando corresponde a la probeta 3 (p.28).
- **Granulometría digitalizada:** coincide con el Gráfico 1 (p.8) dentro de ±0,5 %.
- **Convención de εv:** negativo = compresión. Lo respalda la nota de IDIEM en el edómetro de WSP 2024 (p.121): «deformación unitaria positiva indica hinchamiento».

## 6. Archivos

- `verificado/WSP_2024_codisposicion_verificado.csv` y `verificado/IDIEM_2025_verificado.csv`:
  - Contienen las correcciones; no se borró ninguna fila.
  - Columnas añadidas: `sigma3c_kPa`, `sigma3f_kPa`, `sigma1f_kPa` y `estado_max_oblicuidad`. En CID, σ3f = σ3c y no hay presión de poros en exceso; no hay ensayos no drenados.
- `verificado/condiciones_WSP2024.csv` (6 sets) y `verificado/condiciones_IDIEM2025.csv` (1 set).
- Scripts y páginas en `paginas/verificacion/WSP2024_IDIEM2025/`:

  | Script | Función |
  |---|---|
  | `render.py` | Renderiza páginas a PNG |
  | `parse_wsp24_tx.py` | Parser independiente de las hojas triaxiales de WSP 2024 |
  | `parse_idiem25.py` | Parser independiente de las tablas de IDIEM 2025 |
  | `check_notas.py` | Cruza las notas del CSV con los encabezados parseados |
  | `mezcla_relave.py` | Contenido de relave y granulometrías exactas de C1-C3 |
  | `carga_puntual.py` | Conteo de fragmentos de carga puntual |
  | `build_verificado.py` | Genera los entregables verificados |
