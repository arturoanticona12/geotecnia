# Golder (2012): triaxiales de gran escala en mármol negro (resumen de extracción)

**Fuente:** `2012_Golder_Triaxiales Gran Escala en Marmol Negro.pdf` (79 págs.).
- Págs. 1–24: Technical Memorandum Golder Associates Perú, Doc. No. 446, del 7 de febrero de 2012, *Summary of results from laboratory testing program for black marble rockfill from Antamina*. Proyecto 1014270482C/1194155017P, dirigido a R. Manrique (CMA).
- Págs. 25–79: anexo IDIEM (Universidad de Chile), Informe de ensayo Nº 708.397-A, *Material de enrocamiento presa Antamina, Perú*, emitido el 05-sep-2011; ensayos del 02-abr-2011 al 22-ago-2011.

Las páginas citadas son las del PDF.

## Objetivo y material

- **Objetivo:** caracterizar la resistencia y la deformabilidad del enrocado de mármol negro con el que se construye la presa de relaves de Antamina, dentro del *Dam Deformation Study*. Los resultados sirven para calibrar modelos sísmicos (pág. 1 y 3).
- **Material:** enrocado de mármol negro, «Type C rockfill» según Antamina, de la Fase 5, polígono 12022607, cota 4478. El informe lo describe como «angular run-of-the-mine material». Se usaron unos 16 000 kg (págs. 1–2).
- **Clasificación:**
  - `litologia` = Mármol; `litologia_detalle` = mármol negro.
  - `tipo_material` = **Enrocado**, porque es material para la presa. El origen es ROM angular; queda anotado en `notas`.
  - `clase_desmonte` = C.
- **Escalamiento:** truncado (scalping) a 178 mm. La macro-granulometría de terreno llega a un Dmax de 558.8 mm, con Cu = 35.0 y Cc = 2.5. La granulometría de laboratorio tiene Dmax 177.8 mm, Cu = 34.4 y Cc = 4.1 (Fig. 1, pág. 2).

## Ensayos extraídos (CSV `Golder_2012_marmol.csv`: 6 filas)

Se extrajeron **5 triaxiales CID** sobre probetas de 1.0 m × 1.8 m, que forman un solo set (misma granulometría y densidad), más **1 edómetro** de gran escala.

| Probeta | Tipo de carga | σ′c (kg/cm²) | σ′3 (kPa) | q pico (kPa) | σ′1 (kPa) | εa (%) | εv (%) | φ′sec (°) | Bg (%) | Finos post (%) |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Monotónica | 5 | 490.3 | 1780.9 | 2271.2 | 17.27 | −5.65 | 40.2 | 26.8 | 8.2 |
| 2 | Carga-descarga | 5 | 490.3 | 1702.4 | 2192.8 | 18.26 | −6.95 | 39.4 | 28.6 | 8.0 |
| 3 | Carga-descarga | 10 | 980.7 | 2916.5 | 3897.2 | 18.00 | −8.17 | 36.7 | 40.8 | 8.5 |
| 4 | Monotónica | 20 | 1961.3 | 5817.3 | 7778.6 | 19.59 | −7.69 | 36.7 | 50.2 | 10.7 |
| 5 | Carga-descarga | 20 | 1961.3 | 6329.2 | 8290.5 | 17.78 | −9.67 | 38.1 | 55.4 | 11.4 |

Cómo se obtuvo la tabla:

- **Origen de los valores:** son el máximo de q = (σ1−σ3)/2 en las tablas IDIEM, que están en kg/cm² (págs. 29, 40, 52, 55 y 70). Se verificaron en la imagen de cada página.
- **φ′sec:** se calculó como asin(t/p) y coincide con la Fig. 5 (pág. 10). El informe resume el ángulo pico entre 40° (σ′c = 5 kg/cm²) y 36° (20 kg/cm²).
- **Comportamiento:** todas las probetas fueron contractivas. La falla se tomó en el máximo desviador, alcanzado entre 17 y 20 % de εa; no hubo un pico marcado.
- **Convención de εv:** negativo = compresión.
- **Condiciones comunes:**
  - γd de confección 2.10 t/m³ (20.60 kN/m³) y w = 0.09 %.
  - e0 = 0.286, con Gs = 2.7 **supuesto** (el Gs de la roca no se determinó; pág. 3 y 7).
  - Después de la consolidación, e = 0.256, 0.250, 0.227, 0.200 y 0.179 (Tabla 3, pág. 7).
  - Contrapresión 2 kg/cm² y B > 0.95.
- **Ensayos de carga-descarga:** tienen ciclos irregulares (Fig. 2, pág. 8). Sirven de base para estudiar la compactación cíclica (sección 6, pág. 22).

## Envolventes y conclusiones del propio informe

- **Ángulo pico:** de unos 40° a 5 kg/cm² a unos 36° a 20 kg/cm², decreciente con el confinamiento (Fig. 5, pág. 10; conclusiones, pág. 23).
- **Comparación con Leps (1970):** los puntos caen cerca de la línea de enrocado de calidad media (Fig. 6, pág. 10).
- **Ajuste c–φ:** el informe no ajusta c–φ ni una ley de potencia.
- **Módulos:** Ei1 y Ei2 frente a σ′c solo aparecen en gráficos (Fig. 7a–7b, págs. 11–12). No se digitalizaron.

## Ensayos índice y otros

- **UCS de la roca:** 8 probetas M1-1 a M4-2 del Informe 379 (Tabla 1, pág. 3). Valores: 540, 1110, 1080, 1310, 560, 620, 1380 y 1340 kg/cm², es decir 53 a 135 MPa, con promedio 97.3 MPa. Clasificación ISRM R4–R5.
- **Los Ángeles:** 44 % y 41 % (dos muestras, Informe 379; pág. 17).
- **Durabilidad y absorción:** no se informan.
- **Granulometría inicial de ensayo (IDIEM pág. 3, PDF 27), % que pasa:**

  | Abertura | 178 | 152 | 127 | 102 | 76 | 63.5 | 50.8 | 38.1 | 25.4 | 19 | 9.52 | 4.76 | 2.0 | 0.84 | 0.42 | 0.25 | 0.11 | 0.074 mm |
  |---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
  | % que pasa | 100 | 97.9 | 93.2 | 87.9 | 75.5 | 67.6 | 59.2 | 48.7 | 38.0 | 31.2 | 20.3 | 14.7 | 10.8 | 8.9 | 7.9 | 7.3 | 5.5 | 4.9 |

  - Valores calculados por interpolación: D10 ≈ 1.39, D30 ≈ 17.6, D50 ≈ 39.5 y D60 ≈ 51.9 mm.
  - Fracciones: grava 85.3 %, arena 9.8 % y finos 4.9 %.
- **Granulometrías post-ensayo:** probetas 1 a 5 y edómetro (págs. 27–28). Bg de Marsal según la Tabla 5 (pág. 17); el edómetro dio Bg = 28.8 a 60 kg/cm².
- **Edómetro de gran escala** (Ø 0.95 m × 0.90 m; págs. 13–15 y 72–73):
  - Estado inicial: γd = 2.10 g/cm³, e0 = 0.284.
  - A σ′v = 60 kg/cm²: e = 0.170.
  - Curva e–σ′v casi lineal hasta 40 kg/cm².
  - E ≈ 400 kg/cm² (σ′v < 40) y ≈ 800 kg/cm² (40 a 60).
  - Colapso por inundación: 0.09 %.
- **Permeabilidad** (carga constante, dentro del edómetro; Tabla 4, pág. 16):

  | σ′v (kg/cm²) | 6 | 10 | 20 | 40 | 50 | 60 |
  |---|---|---|---|---|---|---|
  | k (cm/s) | 1.4E-1 | 1.1E-1 | 1.0E-1 | 1.1E-1 | 8.6E-2 | 8.2E-2 |

- **Ensayos no drenados:** no hay.

## Dudas y datos ilegibles

1. **Gs = 2.7 supuesto.** Todas las e0 dependen de ese valor. El informe dice explícitamente que el Gs del mármol negro no se determinó.
2. **Origen de UCS y Los Ángeles.** Vienen del Informe 379 (Golder 2011, *Supervisión de ensayos y muestreo de roca*), que no está en este PDF. No se pudo comprobar que sean las mismas rocas ensayadas.
3. **Criterio de falla.** No hay pico: el máximo q aparece entre 17 y 20 % de εa, cerca del final del ensayo (≈20 %). Para las probetas 2, 3 y 5 (carga-descarga), el máximo corresponde a la carga monotónica final, después de los ciclos.
4. **Probeta 3** (carga-descarga, 10 kg/cm²): las tablas de las págs. 42–52 incluyen ciclos. El máximo de 14.87 kg/cm² está en la pág. 52 y se verificó.
5. **Diferencia de Cu.** Mi interpolación da Cu ≈ 37.4 y Cc ≈ 4.3, frente a 34.4 y 4.1 del informe. En el CSV se dejaron los del informe.
6. **Clase de desmonte.** Se registró como *Enrocado* por su uso en la presa, aunque el texto lo llama «run-of-the-mine» de Tipo C.
