# Verificación por página de los triaxiales drenados (CD) del desmonte de Antamina

Fecha: 2026-10-10. Entregables en esta carpeta:
- `drenados_verificados.csv`: 28 filas. Son los 22 ensayos de `drenados_utilizables.csv` más los 6 ensayos cíclicos USC (W2022), que se clasifican en la §6.
- `rotura_bg.csv`: Bg de Marsal, informado y calculado, con su página.

Las páginas citadas son siempre la página del PDF (1 = primera página del archivo), no la numeración interna del informe.

## 1. Método

1. **Índice de páginas.** Se extrajo el texto de cada página con pypdfium2. El número de páginas coincide con los caché `datos_antamina/texto/*.txt`.
   - Todos los PDF son nativos (texto vectorial), no escaneos. Las pocas páginas sin texto son fotos: G2012 1, G2021 18, W2024 1.
   - Por eso no fue necesario hacer OCR de los números.
2. **Ubicación de las tablas.** Se localizaron con búsquedas por palabra clave (Tabla 3/7/8/9/15, Probeta, Marsal, Post TX, Failure, etc.).
3. **Máximo desviador.**
   - Las tablas IDIEM (columnas εa, εv, p, q con q = (σ1−σ3)/2 en kg/cm²) se leyeron completas desde el texto, para encontrar el máximo de q y el último punto.
   - Ese máximo se **confirmó visualmente**: se renderizó la página (escala 2–2.5) y se abrió como imagen.
   - Desviador = 2·q_MIT·98.0665 kPa; σ′3 = p − q de la primera fila (constante en todas las filas).
4. **Encabezados.** Se leyeron en imagen las hojas Golder (Lima y Burnaby), USC y los encabezados IDIEM (D, H, ρd, w, contrapresión, cámara, ΔV).
5. **Bg de Marsal.** Bg = Σ de las diferencias positivas del % retenido por fracción (incluye el fondo, < #200), usando las granulometrías tabuladas antes y después del ensayo.
6. **Comparación con la base.** Se comparó con `analisis_antamina/drenados_utilizables.csv`, filas 0–7, 35–42, 58–63. Las tolerancias equivalen al redondeo: 0.6 kPa, 0.005 %, 0.0025 en e y 0.015 kN/m³.
7. **Lo que no se puede leer.** Se marca como «no informado» o «gráfico, aprox.». Ningún valor se interpoló entre puntos tabulados.

## 2. Índice de páginas por informe

| Informe (páginas) | Contenido verificado | Páginas PDF |
|---|---|---|
| G2012, Golder Doc. 446 + IDIEM 708.397-A (79) | Granulometría de terreno y de laboratorio (gráfico) y scalping a 178 mm | 2 |
| | UCS / Los Ángeles | 3 |
| | Saturación, Tabla 3 (ρd, e0, e tras consolidar) y programa de carga-descarga | 7 |
| | φ pico | 10 |
| | Tabla 5 (Bg) | 17 |
| | Granulometrías IDIEM antes y después | 27–28 |
| | Tablas CID: P1 p29; P2 p31–40; P3 p42–52; P4 p54–55; P5 p57–70 | 29–70 |
| G2021, Golder Commingling (205) | Escalamiento a < 1" | 9, 29 |
| | Tabla 8 (resumen CD) | 20 |
| | Granulometría de II0471 | 46 |
| | Hojas CD II0471 E1/E2/E3 | 108/109/110 |
| | Curvas | 111 |
| | Sin Bg ni granulometrías post-ensayo | — |
| W2022, WSP/Golder enrocado 3B (396) | Tabla 3 (programa CID) | 10 |
| | Procedimientos (carga-descarga, cíclicos) | 13–15 |
| | Resultados cíclicos | 28–30 |
| | Tabla 7 (Bg) | 41 |
| | Macro-granulometría de hornfels M-001 | 47 |
| | Granulometrías IDIEM inicial y post (1.555.677-C) | 62–63 |
| | IDIEM E (carga-descarga): P1 106–117, P2 119–167, P3 169–227 | 106–227 |
| | IDIEM B.2 (monótono): P1 233–236, P2 238–243, P3 245–250 | 233–250 |
| | Golder 6" HR | 350–351 |
| | Golder 6" MR | 354–355 |
| | USC: HR-CTX1 361–366; HR-CTX4 367–372; HR-LCTX2 373–378; MN-CTX3 379–384; MN-LCTX1 385–390; MN-LCTX2 391–396 | 361–396 |
| W2024, WSP co-disposición (366) | Tabla 5 (Gs) | 12 |
| | Tabla 9 (programa) | 15 |
| | Procedimiento carga-descarga | 18 |
| | Tabla 15 y curvas (Bg) | 35–36 |
| | Granulometría del desmonte recibido (Dmax 10") | 93 |
| | Metodología de corte a 4" | 108 |
| | C4: P1 111–112, P2 114–115, P3 117–118 | 111–118 |
| | Granulometrías post-TX de C4 | 120 |
| | Resumen y ρd post-consolidación | 130 |
| | Finos post | 132 |
| | Post-TX C2 | 214–215 |
| | Post-TX C1 | 336–337 |
| I2025, IDIEM 1.966.314-B (32) | Programa; la granulometría post-TX figura «---», no ejecutada | 3–5 |
| | Corte en 7" y granulometría de montaje (solo gráfico) | 8 |
| | P1 | 10–15 |
| | P2 | 16–21 |
| | P3 | 22–28 |
| | Tabla 4 (ρd post-consolidación) | 29 |
| RFI 102-24213-…-0047 (3) | Solicitud de información de Stantec (25-03-2026) sobre desmonte degradado. No contiene ensayos | 1–3 |
| Stantec A.5.4 / A.5.5 (1 + 1) | Láminas resumen con gráficos τ–σn, granulometrías y UCS. No tienen tablas de ensayos | 1 |

## 3. Diferencias con la base (22 ensayos)

**Resultado general.** En los 22 ensayos, σ′3, q, εa en el máximo y εv en el máximo coinciden con el PDF dentro del redondeo. La excepción es G2021, con diferencias menores entre la hoja y la Tabla 8. Las e0 que trae la base también coinciden, salvo II0471-E3.

| Ensayo | Campo | Base | PDF | Página | Comentario |
|---|---|---|---|---|---|
| G2021 II0471-E1 | σ′1 (kPa) | 381 | 382.29 (fila del máximo); 98 + 283 = 381 según Tabla 8 | 108; 20 | Redondeo |
| G2021 II0471-E2 | σ′1 | 1917 | 1916.18 | 109 | Redondeo |
| G2021 II0471-E3 | e0 | 0.320 | 0.324 (hoja); 0.32 (Tabla 8) | 110; 20 | Menor |
| G2021 II0471-E3 | q (kPa) | 4647 | 4644.80 (máximo de la tabla); 4,647 (Tabla 8) | 110; 20 | Menor; la base usa la Tabla 8 |
| G2021 II0471-E3 | σ′1 | 5847 | 5842.87 | 110 | Menor |
| G2012 T1–T5 | e tras consolidar | vacío | 0.256 / 0.250 / 0.227 / 0.200 / 0.179 | 7 | Falta en la base |
| W2022 Golder 6" HR / MR | e tras consolidar | vacío | 0.25 / 0.23 | 350 / 354 | Falta en la base |
| W2024 C4 P1–P3 | e tras consolidar | vacío | 0.411 / 0.351 / 0.332, calculados con Gs 2.85 y ρd post 2.02 / 2.11 / 2.14 | 12; 130 | Calculado |
| G2012, W2022 B.2, I2025 | γd (kN/m³) | 20.60 | 2.10 g/cm³ × 9.807 = 20.59 | 7; 233; 10 | Redondeo |
| W2022 IDIEM E | γd | 20.21 | 2.06 × 9.807 = 20.20 | 106 | Redondeo |
| W2024 C4 | γd | 19.62 | 2.00 × 9.807 = 19.61 | 111 | Redondeo |

**Alertas de contenido.** Los números de la base coinciden con lo que la hoja dice, pero hay contradicciones dentro del propio PDF:

1. **W2022, Golder 6" hornfels (p350–351).**
   - La hoja informa «Failure at maximum deviator stress» = 4100 kPa a εa 11.44 %.
   - Su curva sigue subiendo hasta ≈4600 kPa a εa ≈17.5 % (lectura gráfica aproximada) y luego cae bruscamente.
   - Por lo tanto, el q de la base (4100) **no es el máximo de la curva**.
   - Además, el gráfico de εv de las hojas Golder Burnaby (p351, p355) dice «−ve = dilation, +ve = contraction». Si fuera literal, εv = −5.31 y −6.51 serían dilatación. El ΔVc de consolidación también es negativo (−386 y −193 cc), lo que sugiere que el negativo es compresión. **No se puede resolver con el PDF.**
2. **G2021 (p108–110).**
   - El encabezado «Esfuerzo principal en la falla» de cada hoja no corresponde al máximo de la tabla:
     - E1: εa 20.03 %, σ1′ 368 (q ≈ 268), frente al máximo de 282.53 a 3.99 %.
     - E3: σ1 5691 a 20.0 %, frente al máximo de 4644.80 a 12.09 %.
   - La Tabla 8 y la base usan el máximo de la tabla. Esa elección es correcta.
3. **G2021 E1.** εv en el máximo es +0.32. La convención de signo no está declarada. Por la curva (p111), negativo parece compresión, así que +0.32 sería dilatación a 98 kPa.
4. **I2025.**
   - Gs y e0 son **no informados**; la base también los deja vacíos.
   - P2 y P3 terminan a εa 15.02 % y 16.70 %. El informe no dice por qué.
5. **W2022, IDIEM.** Gs no lo informa IDIEM. El e0 = 0.310 / 0.335 es calculado con Gs 2.75, tomado de la hoja Golder 6" del mismo lote.

### ¿Se detuvieron por límite del equipo?

- **En los 22 ensayos de la base: no.** Ningún informe lo declara. Todos terminan por programa en εa ≈ 20 % (G2012 p7; W2022 p13; W2024 p18; G2021 en ≈20 %). I2025 P2 y P3 terminan antes, sin explicación.
- **Desviador aún creciente o en su máximo en el último punto** (q_max = último punto):
  - W2022 B.2 P2 (19.04 %) y E P1 (19.15 %).
  - G2021 E2 (20.21 %).
  - W2024 C4 P2 (20.70 %).
  - G2012 T4 queda en meseta: 29.66 a 19.59 % y 29.50 al final.
  - En estos casos el q informado es el máximo **alcanzado**, no un pico de falla.
- **Límite de equipo explícito: solo en 3 ensayos cíclicos USC** (HR-CTX1, HR-CTX4, MN-CTX3). Ver §6.

## 4. Ensayos drenados faltantes o fuera de la base

- **En los cinco informes no hay ningún triaxial drenado de desmonte sin relave que no esté en `ensayos.csv`.**
  - Los 6 cíclicos USC y los duplicados de mármol 2011 en W2022 están en la base, pero no en los 22.
  - Los de W2024 C1–C3 y G2021 ALT contienen relave.
- **W2024.** No existen C3 ni C4 de carga-descarga (Tabla 9, p15). Esa ausencia es correcta en la base.
- **W2024, en la base.** `relave_pct_masa_total` está vacío para C1/C2 CD y debería reflejar el relave (≈13.1 / 10.7 % efectivo, según la verificación previa).
- **Stantec A.5.4 y A.5.5.** Grafican puntos τ–σn de fuentes que **no están en la base**:
  - «WSP, 2023» (mármol negro escalado).
  - «Golder, 2011».
  - «Puntos Histórico 1» y «Puntos Histórico 2».
  - «Piteau 2013 / 2019» (envolventes).
  - Solo hay gráficos; no se pueden extraer valores ni saber si son drenados. Habría que pedir los informes originales.
- **RFI-0047.** No contiene ensayos. Pide resultados de desmonte degradado, que hoy no están disponibles.

## 5. Rotura de partículas (Bg de Marsal)

`rotura_bg.csv` tiene 68 filas: 50 con Bg informado, 16 con Bg calculado y 2 «no informado» (G2021 e I2025).

**Bg calculados con granulometrías tabuladas (16)**

| Set | Bg calculado | Comparación con el informe |
|---|---|---|
| G2012, 5 triaxiales + edómetro | 13.4 / 14.3 / 20.4 / 25.1 / 27.7 / 14.4 | La Tabla 5 (p17) informa 26.8 / 28.6 / 40.8 / 50.2 / 55.4 / 28.8, que es **exactamente Σ\|ΔW\| = 2·Bg**. El texto define Bg como la suma de las diferencias positivas, así que los valores de la Tabla 5 están al doble |
| W2022 hornfels 1.0 m, 6 triaxiales + edómetro | 20.3 / 29.3 / 36.5 / 24.2 / 35.5 / 38.9 y 23.0 | Reproducen la Tabla 7 (p41) |
| W2024 C4, 3 triaxiales | 8.3 / 8.5 / 17.6 | Iguales a la Tabla 15 (p36) |

- **W2022, asignación de columnas.** En p63, las dos columnas «20 kgf/cm²» no dicen cuál es la monótona y cuál la ciclada. Se asignaron por coincidencia con la Tabla 7.
- **W2024 C4, curva inicial.** La curva inicial de montaje solo está en gráfico (p108). Se calculó como el desmonte de p93 truncado a 4" y renormalizado (supuesto).

**Bg solo informados**
- W2022 Tabla 7: Golder 6" hornfels 15 y mármol 30; cíclicos 8 y 6 (un solo valor por grupo); edómetros 12, 8, 14, 45, «-», 21.
- W2024 Tabla 15 (C1–C3 con relave, más edómetros): 9.6 / 18.3 / 16.9 / 6.0 / 11.8 / 16.9 / 10.5; 7.8 / 8.6 / 13.5 / 13.0 / 15.8 / 15.2 / 8.3; 6.3 / 15.2 / 19.4 / 7.7; edómetro C4 9.2.

**Sin Bg**
- G2021: no tiene granulometrías post-ensayo.
- I2025: las granulometrías post-TX están programadas, pero no ejecutadas en este informe (p4).

**Granulometría y Dmax de campo**
- G2012: Dmax 558.8 mm, Cu 35.0 y Cc 2.5; solo gráfico (p2).
- W2022 hornfels M-001: tabulada (p47). 36" 100 %; 16" 88.21; 10" 76.98; 6" 58.34; 3" 43.65; 1" 31.49; #4 13.14; #200 2.49.
- W2024: solo la del material recibido en laboratorio (Dmax 10", p93), no la de terreno.
- G2021 e I2025: no informada.

## 6. Clasificación de ensayos cíclicos y de carga-descarga

| Ensayo (base) | ¿Drenado? | Tipo real de carga | ¿Máximo monótono hasta la falla legible? | ¿Desmonte sin relave? | ¿Utilizable como CD? | Páginas |
|---|---|---|---|---|---|---|
| G2012 T2, T3, T5 («CICLICO») | Sí | **Carga-descarga dentro de un ensayo monótono**: 1 ciclo a ≈33 % τu, ciclos parciales y luego 4 (T2) o 15 (T3, T5) ciclos a ≈50 % τu; después, carga monótona hasta ≈20 % | Sí: σ′3, q, εa, εv tabulados; e0 en Tabla 3 | Sí (mármol) | **Sí** (ya están en los 22) | 7; 31–70 |
| W2022 IDIEM E P1–P3 («CICLEADO») | Sí | Igual: 4 etapas con 15 ciclos a ≈50 % τu y carga final hasta ≈20 % | Sí (e0 calculado) | Sí (hornfels) | **Sí** (en los 22) | 13; 106–227 |
| W2022 Golder 6" HR y MR | Sí | Carga-descarga: 1 ciclo y un paquete de ciclos a εa ≈2–3 %; luego monótono | Sí en la hoja; en HR, la hoja contradice su curva (§3) | Sí | **Sí**; HR con alerta | 350–355 |
| W2022 mármol 2011, P3–P5 | Sí | Duplicados de G2012 T2, T3, T5 | Sí | Sí | Usar el registro primario G2012 | 252–295 |
| W2024 C1_CD, C2_CD | Sí | Carga-descarga: ciclos a εa 2 %, 5 % (15 ciclos) y 8 %; luego monótono hasta 20 % | Sí (tablas IDIEM) | **No** (contienen relave) | Como CD sí; **no como desmonte sin relave** | 18; 148–204; 283–326 |
| **W2022 USC HR-LCTX2, 6"** | Sí («Cyclic Drained» y luego «Monotonic Drained») | **Cíclico verdadero**: 15 ciclos de amplitud constante en compresión-extensión (CSR 0.38), σ′c 350 kPa; luego monótono drenado a 5 %/h | q_max 1420.40 kPa = valor a εa 20.00 % (meseta). εv solo gráfico (≈−3.2 %). e0 0.238 calculado (Gs 2.71 estimado); e tras consolidar 0.19 | Sí (hornfels) | **Con reservas** (probeta pre-ciclada, σ′3 350 kPa) | 373, 377 |
| **W2022 USC MN-LCTX1, 6"** | Sí | Cíclico verdadero (CSR 0.19) + monótono | q_max 1575.90 kPa a εa ≈5 % (gráfico); al final, 1392.7 a 20 %. εv ≈−1.0 % (gráfico). e0 0.204 calculado; e tras consolidar 0.21 (incoherente) | Sí (mármol) | **Con reservas** | 385, 389 |
| **W2022 USC MN-LCTX2, 6"** | Sí | Cíclico verdadero (CSR 0.38) + monótono | q_max 1550.50 kPa a εa ≈8 % (gráfico); al final, 1414.8. εv ≈−1.1 % (gráfico). e tras consolidar 0.25 (incoherente) | Sí (mármol) | **Con reservas** | 391, 395 |
| W2022 USC HR-CTX1, 4" | Sí | Cíclico verdadero (CSR 0.33) + monótono | **No**: detenido a εa 1.68 % porque «Reach the maximum capacity of actuator at 10 kN» | Sí | **No** (q 1280 es cota inferior) | 361, 363, 365 |
| W2022 USC HR-CTX4, 4" | Sí | Cíclico verdadero (CSR 0.20) + monótono | **No**: límite del actuador a 7.37 % | Sí | **No** (q 1210.54 es cota inferior) | 367, 371 |
| W2022 USC MN-CTX3, 4" | Sí | Cíclico verdadero (CSR 0.25) + monótono | **No**: límite del actuador a 4.89 % | Sí | **No** (q 1245.3 es cota inferior) | 379, 383 |

**Conclusión de la clasificación**

- **Ensayos de «carga-descarga» (G2012 «CICLICO», IDIEM «CICLEADO», Golder 6", W2024 C/D).** Los ciclos se aplican por debajo del ≈50 % de τu dentro de un ensayo monótono que continúa hasta εa ≈20 %. Son comparables a un CD.
- **Ensayos USC.** Son carga cíclica verdadera: 15 ciclos de compresión-extensión con amplitud constante, cuyo objetivo es la respuesta cíclica (W2022 p15 y p28–30). La fase post-cíclica es monótona y drenada.
  - HR-LCTX2, MN-LCTX1 y MN-LCTX2 llegan a εa 20 % con un máximo definido. Son utilizables solo con reservas: la probeta está pre-ciclada, σ′3 es bajo (350 kPa), D/Dmax = 5.8, εa y εv en el máximo solo se pueden leer en el gráfico, y la hoja es «DRAFT».
  - Los otros tres se detuvieron por la **capacidad del actuador de 10 kN**: su q es solo una cota inferior.
- **Diferencias con la base en los USC.**
  - εa en el máximo de MN-LCTX1 y MN-LCTX2 está vacío en la base. En el gráfico se lee ≈5 % y ≈8 %.
  - El CSR de las hojas no coincide con la Tabla 3 (p10).
    - Hornfels: hojas 0.38 / 0.33 / 0.20 frente a 0.50 / 0.40 / 0.33 en la tabla.
    - Mármol: hojas 0.25 / 0.19 / 0.38 frente a 0.25 / 0.20 / 0.40 en la tabla.

## 7. Dudas abiertas

1. **Golder 6" hornfels.** ¿4100 kPa a 11.44 % (hoja) o ≈4600 kPa a ≈17.5 % (curva)? Hace falta la planilla «6in Triaxial Report HR.xlsx», que se cita en la hoja.
2. **Signo de εv en las hojas Golder Burnaby.** La leyenda dice «−ve = dilation».
3. **I2025.** No se sabe por qué P2 y P3 terminan antes del 20 %. Tampoco hay Gs (e0 no calculable sin supuesto) ni granulometrías post-TX (informe 1.966.314-A o posterior).
4. **W2022 p63.** No se puede confirmar desde el PDF qué columna de 20 kgf/cm² es la monótona y cuál la ciclada.
5. **W2024 C4.** Hay fechas de ensayo anteriores a la recepción del material (p111, p118).
6. **Stantec A.5.4/A.5.5.** Las fuentes «WSP 2023», «Golder 2011», «Puntos Histórico» y Piteau no están disponibles en tabla.
