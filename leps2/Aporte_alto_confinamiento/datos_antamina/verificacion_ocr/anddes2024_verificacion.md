# Verificación de los ensayos Anddes Geolab (2024) contra `ensayos.csv`

Fecha: 2026-10-10. Fuente: 25 PDF en `Data Antamina\ensayos\` (solicitud EPE-23.10.141). Solo se leyeron; no se modificaron.

## 1. Cómo se extrajo

1. **Capa de texto.** Los 25 PDF tienen texto vectorial (no son escaneos). Se extrajo con `pdfplumber` y se interpretó con expresiones regulares. No hizo falta OCR.
2. **Lectura visual.** Cada página se renderizó a PNG con `pypdfium2` (escala 2,5; los recortes de gráficos y tablas, a escala 5) y se leyó a ojo para confirmar lo extraído:
   - TX: páginas 1, 3, 4 y 7 de Mármol; 1 y 7 de los cinco archivos; 3 de Pila 01.
   - LSDS: página 2 de Mármol, gráficos τ-δh de los cinco, página 1 de Pila 02.
   - SUCS: página 1 de Pila 01 y página 2 de los cinco.
   - Proctor: los cinco.

   En todos los casos la imagen coincide con la capa de texto.
3. **Solo en imagen.** Algunos datos no existen en la capa de texto y se tomaron de la imagen, con su página:
   - el rótulo «Gs=…» de la curva de 100 % de saturación del Proctor;
   - «(Fuera de método)» o «Método C» en el título del Proctor;
   - el desplazamiento en el pico de τ, leído en el gráfico τ-δh del LSDS (aprox. ±0,2 cm).
4. **Control interno de las tablas TX.** Las 420 filas (15 probetas × 28 escalones de 0 a 15 %) cumplen, a la precisión de redondeo, estas cinco relaciones:
   - p = σ′3c + σdesv/2
   - q = σdesv/2
   - p′ = p − μ
   - q′ = q
   - σ′1/σ′3 = (p′+q′)/(p′−q′)

   No hubo ninguna excepción. Por eso se descarta un error de lectura de dígitos.
5. **Valores derivados.** Las columnas con sufijo `_calc` no salen del PDF; son aritmética sobre valores del PDF:
   - σ′3f = p′ − q′ y σ′1f = p′ + q′;
   - e0 = Gs_rótulo/ρd − 1.
6. **Contraste con la base.** Se comparó automáticamente contra `ensayos.csv` (filas A2024 y A2024DS): 1245 comparaciones de campos.

Scripts en el scratchpad de la sesión: `ocr_anddes\build.py` y `compare.py`.

**Archivos entregados**

| Archivo | Contenido |
|---|---|
| `anddes2024_cu.csv` | 15 probetas CU (3 por material), 87 columnas |
| `anddes2024_cu_curvas.csv` | 420 filas: tabla completa εa–σdesv–μ–p–q–p′–q′–q′/p′–σ′1/σ′3 de cada probeta (págs. 3-5) |
| `anddes2024_lsds.csv` | 15 probetas LSDS (3 por material) |
| `anddes2024_indices.csv` | 5 muestras: granulometría completa, límites, SUCS, Proctor y contenido de agua |

## 2. Qué informan los CU sobre la falla

- **El laboratorio no informa σ′3f ni σ′1f como valores de falla.** Tabula, en cada escalón de εa de 0 a 15 %, los valores σdesv, μ (exceso de presión de poros), p, q, p′, q′, q′/p′ y σ′1/σ′3, todos en notación MIT (págs. 3, 4 y 5 = σ′3c de 2000, 1000 y 500 kPa).
- **Criterio del laboratorio:**
  - 15 % de deformación para la envolvente efectiva (p.1: a′, α′, c′, φ′) y para Su (p.1; Su = q′ a 15 %).
  - Envolvente «total» (p.7, «requerimiento explícito del solicitante»): al 2 % en las rumas M, H e I, y al 15 % en las pilas P01 y P02.
  - No identifica máximo desviador ni máxima oblicuidad.
- **Lo que extraje.** Para cada probeta, a partir de la tabla, cuatro estados:
  - máximo σdesv tabulado (`maxdev_*`);
  - máxima σ′1/σ′3 tabulada (`maxobl_*`);
  - 15 % (`e15_*`);
  - 2 % (`e2_*`).

  En cada estado: εa, σdesv, μ, p′, q′, σ′1/σ′3 y σ′3f/σ′1f calculados.
- **Comportamiento al final del ensayo (εa final = 15 % en las 15 probetas):**
  - El desviador seguía creciendo entre 14 y 15 % en 12 de las 15 probetas.
  - No crecía en I-2000, I-1000 y P01-2000.
  - En M-2000, H-500, P02-1000 y P02-2000 el máximo global del desviador está a 15 %, después de un primer pico a 1,75-3 % seguido de ablandamiento.
  - En P01-2000 el máximo está a 14 %.
  - La máxima oblicuidad está a 15 % en todas las probetas, salvo H-2000 (6,0 %; 6,09) y P01-2000 (empate 14-15 %; 5,47).

## 3. Diferencias contra `ensayos.csv`

**Resultado general.** En 1245 comparaciones de campos numéricos, los valores de la base coinciden con el PDF salvo las 4 diferencias de la tabla 3.1. Los campos comparados son:
- geometría inicial y tras consolidación, w, ρd, B, celda, contrapresión;
- σ′3c, máximo desviador, máxima oblicuidad y estado a 15 % (εa, q, u, p′, q′, σ′3f, σ′1f);
- Su y envolventes c′, φ′, a′, α′, c, φ;
- en LSDS: τ pico, τ a 6,6 cm, ángulos secantes, c, φ y μ de ambas envolventes, alturas, w y ρd;
- Dmax (TM 1 in), caja y Gs.

### 3.1 Diferencias en `ensayos.csv`

| id_probeta | Campo | Valor en la base | Valor en el PDF | Página | Comentario |
|---|---|---|---|---|---|
| A2024-149 (H, 1000 kPa) | ratio_oblmax, ratio_e15 | 11.349 | 11.34 | TX H p.4 | La base recalcula con (p′+q′)/(p′−q′); la tabla da 2 decimales. No es un error. |
| A2024-151 (I, 500 kPa) | ratio_oblmax, ratio_e15 | 6.853 | 6.86 | TX I p.5 | Ídem. El laboratorio redondea 6.86; con p′ = 482.1 y q′ = 359.4 el recálculo da 6.853. |

### 3.2 Diferencias en `materiales.csv` (texto `granulometria_campo`) contra la tabla de SUCS p.1

La base sustituyó los D informados por valores interpolados, y lo declara.

| Material | Campo | Base (interpolado) | PDF (informado) | Página |
|---|---|---|---|---|
| M | D10 / D30 / D60 / Cu / Cc | 0,075 / 2,77 / 22,2 / ≈296 / ≈4,6 | 1,54 / 2,76 / 22,04 / 14,29 / 0,22 | SUCS M p.1 |
| H | D10 / D30 / D60 | < 0,075 / 3,56 / 19,6 | 1,54 / 3,55 / 19,45 (Cu 12,61; Cc 0,42) | SUCS H p.1 |
| I | D10 / D30 / D60 / Cu / Cc | 0,126 / 2,98 / 15,3 / 121 / 4,7 | 0,13 / 3,03 / 15,35 / 121,26 / 4,74 | SUCS I p.1 |
| P01 | D10 / D30 / D60 | < 0,075 / 1,50 / 12,6 | 1,54 / 1,47 / 12,51 (Cu 8,11; Cc 0,11) | SUCS P01 p.1 |
| P02 | D10 / D30 / D60 / Cu / Cc | 0,084 / 1,50 / 11,5 / 137 / 2,3 | 0,08 / 1,45 / 11,49 / 138,86 / 2,21 | SUCS P02 p.1 |

Para M, H y P01, la corrección de la base es correcta: con 10-11 % que pasa el N° 200 (0,075 mm), un D10 = 1,54 mm es imposible. En P01, además, el D30 informado (1,47) es menor que el D10. Los Cu y Cc del laboratorio para M, H y P01 no son válidos.

### 3.3 Otros puntos de la base revisados y confirmados

- Gs = 3,06 / 2,94 / 2,75 / 2,90 / 2,74 (M/H/I/P01/P02) es el rótulo de la curva de 100 % de saturación del Proctor (imagen, p.1). No es un ensayo de Gs. Coincide con la base.
- e0 de la base (0,402 M; 0,400 H; 0,432 I; 0,385 P01; 0,496 P02) = Gs_rótulo/ρd − 1. Coincide.
- `w_montaje_vs_proctor`: el TX declara w óptimo de 6,0 % (H) y 8,0 % (I), pero el Proctor da 7,7 % y 9,8 %, y el LSDS usa 7,70 % y 9,80 %. Coincide con lo anotado en la base. En M, P01 y P02 el TX y el Proctor coinciden.

## 4. Lo que falta en la base

**Corrección a la premisa del encargo.** La base sí tiene esfuerzos efectivos en la falla de los CU A2024: `sigma3f_/sigma1f_` en los tres criterios (`qmax`, `oblmax`, `e15`) y `sigma3f_kPa_std/sigma1f_kPa_std` (máxima oblicuidad). Están calculados como σ′3c − u y σ′3f + q, igual que aquí, y coinciden con el PDF. Lo que está vacío son las columnas genéricas `sigma3f_kPa` y `sigma1f_kPa`, y también `eps_final_pct`, `q_final_kPa` y `hay_pico`. La información equivalente está en `e15_*` y `pico_local_previo`.

**Datos que no están en `ensayos.csv` (ni como columnas numéricas en `materiales.csv`):**
1. **Granulometría numérica.** D10, D30, D60, Cu, Cc, % grava/arena/finos y la curva completa están vacíos en `ensayos.csv`; solo aparecen como texto en `materiales.csv`. D50 no lo informa el laboratorio.
2. **Ensayos de índice (SUCS, Proctor, contenido de agua):** no hay filas.
   - γd máx: 22,876 / 20,930 / 23,780 / 22,819 / 19,951 kN/m³ (H/I/M/P01/P02).
   - w óptima: 7,7 / 9,8 / 6,8 / 7,4 / 11,1 %.
   - Valores corregidos por sobretamaño: 24,533 / 22,230 / 25,754 / 24,012 / 20,797 kN/m³ y 4,7 / 6,7 / 3,9 / 5,4 / 8,6 %.
   - Gs bulk del sobretamaño: 2,80 / 2,56 / 2,94 / 2,79 / 2,39; w del sobretamaño 0,3 / 1,0 / 0,1 / 0,8 / 2,0 %.
   - Límites: LL 16 (H), 17 (I), NP (M, P01, P02).
   - w natural informada: 3 / 5 / 3 / 3 / 6 % (enteros). Con las masas del informe da 3,28 / 5,11 / 2,94 / 2,81 / 5,52 % (cálculo propio).
3. **Envolvente total completa.** La base tiene c y φ, pero no a y α: H a = 69,4 kPa, α = 15,9°; I 156,9 / 15,6°; M 27,1 / 18,1°; P01 y P02 0,0 / 22,9° y 0,0 / 22,2° (p.7).
4. **Curvas tabuladas completas del CU** (28 puntos por probeta): ahora en `anddes2024_cu_curvas.csv`.
5. **LSDS:**
   - Desplazamiento en el pico (solo en gráfico, p.2; ver `desplaz_pico_cm_lectura_grafico`).
   - τ residual: no informado (no hay inversión de caja).
   - Desplazamiento final real de las curvas: ≈6,6 cm en M, H e I, pero ≈6,4 cm en P01 y P02, aunque la tabla dice «6,6 cm».

**Ensayos que no están en la base:** todos los ensayos de SUCS/granulometría, límites, Proctor y contenido de agua (5 de cada uno). Los 15 CU y los 15 LSDS sí están todos (A2024-145 a 159 y A2024DS-160 a 174).

## 5. Dudas, ilegibles y observaciones sobre los informes

1. **Texto oculto «2.70».** En la p.4 (1000 kPa) de los cinco TX hay un texto «2.70» (o «2,70») en blanco sobre fondo blanco, junto al recuadro SUCS. No se ve en la imagen. Probablemente es un Gs de plantilla. No se usó.
2. **Dmax y escalamiento de la probeta TX.** No se informan. El LSDS indica «TM: 1 in» (p.2). El CA indica «TM (visual) 3 in» de la muestra recibida, y la granulometría muestra 100 % pasando 3 in.
3. **Proctor de las rumas M, H e I.** Rotulado «(Fuera de método)»; los de P01 y P02 dicen «Método C». La base afirma que la MDS es de la fracción < 19 mm para todos. Eso solo está respaldado para las pilas (Método C). En las rumas el tamaño de corte del sobretamaño no se informa.
4. **Rótulo Gs de P02.** Se lee «Gs ≥2,74»: el «=» se superpone. Se interpreta como 2,74.
5. **LSDS P02, 300 kPa.** El τ pico tabulado, 353,9 kPa, no se ve en la curva: el máximo visible es ≈349 al final. El desplazamiento en el pico queda como ilegible.
6. **LSDS P02.** El número de informe termina en «_SUCS» (errata del laboratorio).
7. **LSDS P01.** El tercer σn es 1000 kPa, no 1200.
8. **Intrusivo.** El encabezado TX y los nombres de archivo dicen «I-1 al I-12», pero la lista de SUCS, Proctor, CA y LSDS es I-1 a I-11 (11 ítems).
9. **SUCS P02.** Informa 1 % de bolonería pese a que el 100 % pasa 3 in.
10. **Envolventes.** Los rótulos de p.7 usan prima (a′, c′, φ′) aunque son esfuerzos totales. En H, c total = c′ = 72,0 kPa. Es coherente con a y α: c = a/cos φ da 72,4 y 72,3.
11. **Su.** El laboratorio lo toma a 15 % de deformación («Duncan et al.»), no en el máximo desviador. En I traza dos rectas: Su/σ′3 = 0,72 (500 kPa) y 0,45.
12. **Saturación de los LSDS.** «Saturados durante el ensayo, salvo excepciones». No se indica si hubo excepciones.
