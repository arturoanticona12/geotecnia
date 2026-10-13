
Notas a la tabla:

- Golder (filas 0-44): el estado de falla es el impreso con el criterio «Esfuerzo Desv. Máximo». La hoja no tabula la curva, así que la máxima oblicuidad queda «no informado». Leer valores en los gráficos sería suponer, y no se hizo.
- Vector (filas 45-56): las columnas principales conservan el «pico de esfuerzo desviador», que es el criterio de Vector. Las curvas MN, HG e INT salen de la capa de texto; un script comprobó en cada fila que σ′1 − σ′3 = Δσ y que σ′3c − σ′3 = u. Las de exoskarn (p.179-181) no tienen texto y se transcribieron de la imagen, con la misma comprobación.
- **EXO 125 kPa (fila 56)**: la curva no tiene pico. El desviador crece hasta 496.8 kPa al 14 %. Vector marcó el punto de εa = 1.0 %, lo que se confirmó en la trayectoria de p.183. Se conserva solo por trazabilidad; para análisis conviene usar `maxdev_*` o `maxobl_*`.
- **HG 250 y 125 kPa, y EXO 500 y 250 kPa (filas 49, 50, 54, 55)**: el «pico» de Vector es un máximo local temprano. El máximo absoluto se da al 14 %.
- **INT 500 kPa (fila 51)**: el máximo numérico es a εa = 1.75 %, pero el círculo «pico» de la trayectoria (p.177) está en εa ≈ 2.5 %. Se mantuvo 1.75 %.

## 3. Golder 2010: discrepancias del resumen extraído (`Golder_2010_ROM_resumen.md`)

| # | Ítem | Valor anterior | Valor correcto | Página | Razón |
|---|---|---|---|---|---|
| R1 | Granulometría de terreno, D10/D30/D60 | Interpolados por el extractor, por ejemplo MN-A 2.5/61/256, HG-A 20.7/80/207 e INT-A 8.0/56/185 mm | Valores de la hoja: MN-A 3.0/60.0/265.0; HG-A 20.0/78.0/205.0; INT-A 9.0/55.0/183.0; EXO-A 0.8/8.5/33.0; MN-B 0.1/11.2/50.5; HG-B 6.8/23.8/63.0; INT-B 0.1/8.5/57.5; EXO-B 0.2/5.1/18.9 | 27-34 | Las hojas sí informan D60, D30, D10, Cu y Cc. El resumen decía que no se habían transcrito |
| R2 | Cu/Cc «del informe» | Tomados de las Figuras 1-4: INT-A 30.3/1.8; MN-B 485.3/26.6; HG-B 7.9/1.0; INT-B 400/10; EXO-B 76.2/6.4 | Hojas: INT-A 20.3/1.8; MN-B 476.4/23.4; HG-B 9.3/1.3; INT-B 410.7/9.0; EXO-B 84.0/6.0. En la Fase A, MN, HG y EXO coinciden | 12-15; 27-34 | Las figuras redondean o copian mal; 183/9.0 = 20.3 |
| R3 | «Tabla 4 coincide con las hojas» | Coincidencia total | En Vector, el φ total de la Tabla 4 para HG (26°) e INT (12°) es el φ total al 12 % de deformación (26° y 12.4°), no el de pico (22.8° y 15.3°) | 10; 171; 177 | Contradicción en la Tabla 4 |
| R4 | Plantilla copiada en Vector | «los valores finales difieren» | En MN e INT coinciden también las humedades finales (8.50/8.84/9.56 %). Solo difieren Hf, Df y γd final | 161-163; 173-175 | Revisión de la cabecera |
| R5 | Origen y clase de la Fase A | «Fase A = material original del tajo → ROM. Muestreo julio–agosto 2009» | Todas las muestras, A y B, se tomaron en el «Acopio parte baja de chancadora secundaria». Las hojas de densidad in situ de la Fase A (02-09-2009) dicen «LIFT: Material Chancado Fase A». La clase ROM se apoya solo en el texto de p.1 | 19-34; 35-38; 1 | Debe quedar explícito |
| R6 | σc por carga puntual, INT-B | 78.06 MPa (Tabla 2) sin observación | Promedio de la hoja: 784.9 kg/cm² = 76.97 MPa. La Tabla 2 y la Fig. 4 dan 78.06 MPa | 80; 8 | No coincide |
| R7 | Densidad de montaje EXO-A 4" | «mínima 2.180» | La hoja dice 2.180, pero la γd mínima de laboratorio es 2.175 (p.43). Las probetas 2 y 3 se armaron a 2.056 y 2.046, más sueltas que la mínima: e0 de 0.695 y 0.703, mayor que emáx = 0.602 | 112; 43 | Probetas más sueltas que la densidad mínima |

Lo que sí se confirmó del resumen 2010:

- Tablas 1 a 4 transcritas bien, salvo lo indicado arriba.
- Durabilidad con sulfato de **magnesio** en las 8 hojas (p.58-65), frente a «sulfato de sodio» en el texto de p.2. Solo se ensayó la gradación 2 (1½"-¾").
- c y c′ de la Tabla 3 (Fase A, 2.8") en kg/cm² aunque el rótulo dice kPa: 871 → 9, 259 → 3, 149 → 2, 33 → 0, 313 → 3, 103 → 1, 80 → 1. Los 4" de la Tabla 3 y toda la Tabla 4 sí están en kPa.
- Tamaño máximo de la Fase B: 9-12" según el texto de p.2. La Tabla 1 da 100 % pasante 12" en las cuatro litologías, mientras que la Tabla 2 repite el TM de la Fase A (35/35/30/19").
- Valores B de Vector: 0.86-0.93 (MN 0.88/0.87/0.89; HG 0.90/0.91/0.93; INT 0.87/0.88/0.86; EXO 0.89/0.88/0.90).
- Gs grueso: Tabla 2 frente a la hoja C127 en la Fase A (2.696/2.733/2.451/3.172 en la tabla; 2.717/2.737/2.461/3.212 en la hoja). En la Fase B coinciden.
- Envolventes de las 15 hojas Mohr Golder y de las 4 de Vector.
- UCS: 16 probetas. Los Ángeles: 8. Densidad máxima y mínima: 5. Absorción: 8. Permeabilidad: 4.

## 4. Golder 2010: errores y contradicciones del propio informe (no se «corrigen», se documentan)

| # | Dónde | Contradicción | Páginas |
|---|---|---|---|
| I1 | Durabilidad | El texto dice sulfato de sodio; las hojas, sulfato de magnesio | 2; 58-65 |
| I2 | Tabla 3, 2.8" Fase A | c y c′ en kg/cm² con rótulo kPa | 9; 84-99 |
| I3 | Tabla 2, TM Fase B | Repite el TM de la Fase A (35/35/30/19"); la Tabla 1 y el texto dan 12" (9-12") | 8; 7; 2 |
| I4 | Tabla 2, Gs grueso Fase A | No es igual a ningún Gs de la hoja C127 (bulk, SSS ni aparente) | 8; 48 |
| I5 | Tabla 2, σc carga puntual INT-B | 78.06 MPa frente a 76.97 MPa del promedio de la hoja | 8; 80 |
| I6 | Tabla 2, k HG-A | 3.20E-06 m/s frente a 3.3E-06 en la hoja | 8; 158 |
| I7 | Tabla 2, unidad de k Fase B | Dice «cm/s»; las hojas, m/s | 8; 159-160 |
| I8 | Tabla 4, Vector, φ total de HG e INT | Corresponden al 12 %, no al pico | 10; 171; 177 |
| I9 | Tabla 4, γd de MN-B 4" | 1.722 es solo la probeta 3 (las probetas 1 y 2 tienen 1.825 y 1.824); INT-B 4" da 1.833 y el promedio es 1.836 | 10; 137; 147 |
| I10 | Figuras 1-4 | Cu/Cc distintos de las hojas (Fig. 4 da Cu 30.3 y la hoja 20.3); la Fig. 3 da γd MN-B 2.157 y la hoja 2.151; la Fig. 1 da σc 72.96 y la Tabla 2 72.99 | 12-15 |
| I11 | Densidad in situ Fase A | Rotulada «Material Chancado Fase A», en la parte baja de la chancadora secundaria; contradice la definición de p.1 | 35-38; 1 |
| I12 | Durabilidad Fase B | Hojas fechadas 10.09.09, antes del muestreo de la Fase B (22-23/09/09) | 62-65; 23-26 |
| I13 | Montaje EXO-A 4" y EXO-B | EXO-A 4", probetas 2 y 3: más sueltas que la γd mínima. EXO-B: saturación final de 100.2 a 105.2 %, lo que indica que el Gs 3.338 o la γd no son consistentes | 112; 43; 132; 152 |
| I14 | Fecha de la hoja EXO-B 4" | «07 de Enero de 2009» (probablemente 2010) | 152 |
| I15 | 16 hojas CU Golder | σ1 − σ3 total ≠ σ′1 − σ′3 en 1 kPa (redondeo) | ver tabla 2.2 |
| I16 | Vector INT 500 y EXO 125 | El marcador «pico» no está en el máximo, o la curva no tiene pico | 177; 183 |
| I17 | Texto p.2 | TM de la Fase A «19" a 36"», pero el tamiz mayor de la Tabla 1 es 35" | 2; 7 |

## 5. Golder 2010: Gs y e0 definitivos por set

El laboratorio (Golder) calculó e0 con el **Gs D854** de la misma litología y fase (p.49), impreso como «G. Específica Promedio» en cada hoja CU. Vector no informa Gs ni e0; se usó el mismo Gs D854. El e0 recalculado como Gs/γd − 1 coincide con el de la hoja (±0.001). El Gs grueso (C127) es menor, sobre todo en el intrusivo y el exoskarn. Con él, el e0 bajaría: por ejemplo, de 0.532 a 0.413 en EXO-A con Gs bulk 3.212. Se adopta el Gs D854 porque es el que usó el laboratorio, y se marca como incierto en EXO-B, donde la saturación final supera el 100 %.

| Set | Gs adoptado (D854) | Gs grueso C127 bulk | e0 por probeta |
|---|---|---|---|
| A-MN 2.8" | 2.763 | 2.717 | 0.290/0.295/0.290 |
| A-HG 2.8" / 4" | 2.791 | 2.737 | 0.377 (×3) / 0.377/0.381/0.377 |
| A-INT 2.8" / 4" | 2.674 | 2.461 | 0.434 (×3) / 0.435 (×3) |
| A-EXO 2.8" / 4" | 3.484 | 3.212 | 0.532/0.531/0.532 / 0.598/0.695/0.703 |
| B-MN 2.8" / 4" / 6" | 2.747 | 2.725 | 0.278/0.273/0.273 / 0.505/0.506/0.595 / 0.355/0.357/0.357* |
| B-HG 2.8" / 4" / 6" | 2.802 | 2.740 | 0.312/0.312/0.311 / 0.502/0.501/0.503 / 0.312/0.310/0.310* |
| B-INT 2.8" / 4" / 6" | 2.742 | 2.647 | 0.358 (×3) / 0.492/0.498/0.492 / 0.353/0.354/0.355* |
| B-EXO 2.8" / 4" / 6" | 3.338 | 3.102 | 0.417/0.416/0.416 / 0.539/0.534/0.538 / 0.419/0.418/0.431* |

\* Calculado aquí, porque Vector no lo informa.

## 6. Golder 2021: verificación

### 6.1 Confirmado en imagen, sin cambios numéricos

- **30 probetas CID.** σ′3, q de la Tabla 8, w0, ρd0 y e0 coinciden con la Tabla 8 (p.20-22). εa y εv en el máximo coinciden con la hoja. Gs coincide con la «G. Específica (Promedio)» de cada hoja. Las granulometrías D10/D30/D50/D60/Cu/Cc y el porcentaje de grava, arena y finos coinciden con p.46-55.
- **6 permeabilidades.** k20 de la hoja: 5.6E-06, 8.9E-07, 8.1E-06, 1.4E-06, 6.7E-06 y 2.5E-06 m/s (p.179-184). La ρd final de cada ensayo es igual a la ρd «antes del corte» de la probeta de ≈400 kPa en la Tabla 8. Las condiciones son σ′ = 399 kPa, celda 661 kPa y contrapresión 262 kPa.
- **Composición del desmonte compuesto:**
  - 0.35 Tipo A : 0.15 Tipo B : 0.50 Tipo C en masa seca, «de acuerdo con información proporcionada por Antamina» (LOM EVA1 y EVA3A) (p.6 y p.9).
  - Tipo A = intrusivo, Tipo B = mármol y hornfels, Tipo C = hornfels (p.6 y p.27).
  - La tipificación A/B/C es geoquímica: p.6 dice «cuya tipificación obedece a consideraciones geoquímicas de potencial de generación de acidez». No hay petrografía ni conteo de fragmentos, y el reparto mármol/hornfels del Tipo B no se informa.
  - **La clase ROM / Chancado / Enrocado no se indica.**
- **Escala.** La p.9 dice: «Las muestras primigenias de desmonte Tipo A, Tipo B y Tipo C fueron limitadas a partículas menores a una pulgada, debido a las limitaciones inherentes a los equipos de laboratorio». Es un truncado anterior a la mezcla, sin escalamiento paralelo. Dmax = 25.4 mm y D/Dmax = 6.0. El Dmax de terreno no se informa. La p.29 reconoce que los resultados no representan el material a escala real.
- **Densidades de montaje:**
  - Compuesto: «remoldeado a la densidad seca de 2.084 g/cm³ y 2.0 %» (hojas p.108-110). Valores reales 2.09/2.09/2.087 g/cm³ (Tabla 8: 2.089/2.089/2.087) = 20.49/20.49/20.47 kN/m³. Es el 90 % del Proctor estándar corregido por sobretamaño (22.72 kN/m³, D698 + D4718 con 12.3 % > ¾", p.97) o el 92 % del no corregido (22.26 kN/m³).
  - Mezclas: «a la DS 1.8 g/cm³ … según solicitud del cliente». Valores reales 1.802 g/cm³ (1.801 en una probeta) = 17.68 kN/m³, entre el 77 y el 80 % del Proctor de la Tabla 6.
- **e0 y Gs:**
  - Golder calculó e0 con la «G. Específica Promedio» de las hojas: 2.762 en el compuesto; 2.793/2.846/3.000 en Alt. 1; 2.789/2.851/3.006 en Alt. 2; 2.793/2.846/3.003 en Alt. 4.
  - Ese Gs no es el de finos (Tabla 5: 2.77; mezclas 2.86-3.13) ni el de gruesos (2.71; 2.67-2.71). El informe no dice cómo se obtuvo.
  - e0 recalculado: 0.322 en el compuesto; 0.550/0.579/0.665 en Alt. 1; 0.548/0.582/0.668 en Alt. 2; 0.550/0.579/0.666 en Alt. 4. Coincide con la Tabla 8, salvo la errata indicada abajo.
- **Saturación.** B = 0.95-1.00 por probeta (columna `B_valor`); contrapresión de 260 a 268 kPa; velocidad 0.111 %/min; ensayo hasta εa ≈ 20 % (13.85 % en Alt. 2 4:1 a 1200 kPa).

### 6.2 Columnas añadidas (`Golder_2021_commingling_verificado.csv`)

Se añadieron estas columnas, sin modificar los valores existentes:

- `sigma3c_kPa`, `sigma3f_kPa`, `sigma1f_kPa`.
- `hoja_maxdev_*`: máximo de la tabla de la hoja.
- `maxobl_*`: máxima oblicuidad.
- `eps_final_pct`, `q_final_kPa`, `hay_pico`.
- `B_valor`, `celda_kPa`, `contrapresion_kPa`, `velocidad_pct_min`.
- `gamma_d_post_consol_kNm3`, `e_post_consol`.
- `Gs_origen`, `e0_recalculado`, `verificacion_2026`.

Como el ensayo es drenado, σ′3f = σ′3c (nominal de la Tabla 8).

### 6.3 Discrepancias del resumen extraído 2021

| # | Ítem | Antes | Correcto | Páginas | Razón |
|---|---|---|---|---|---|
| S1 | «Solo la probeta densa del compuesto a 98 kPa muestra un pico» | Un solo pico | Hay 5 probetas cuyo desviador cae más de un 2 % después del máximo: compuesto 98 kPa (3.9 %, con dilatación) y compuesto 1200 kPa (3.5 %); Alt. 1 9:1 1203 kPa (7.0 %), Alt. 1 4:1 1202 kPa (2.9 %) y Alt. 2 9:1 1203 kPa (3.3 %). En estas cuatro el máximo está en εa ≈ 12 % y siguen contrayendo (no hay dilatación) | 110; 117; 124; 138 | Ablandamiento a gran deformación, no pico dilatante |

Lo demás del resumen 2021 se confirmó:

- Tablas 4-9.
- Permeabilidad de Alt. 1 1:1: 8.9E-07 en la hoja frente a 8.90E-06 en la Tabla 9.
- e0 de Alt. 4 4:1 a 1204 kPa.
- ρd de Alt. 1 9:1 a 101 kPa.
- Criterio de las hojas: σ1 impreso a εa ≈ 16 %.
- 18 de 30 probetas con el máximo en la última lectura.

### 6.4 Errores y contradicciones del propio informe 2021

| # | Dónde | Contradicción | Páginas |
|---|---|---|---|
| J1 | Tabla 9, Fig. 11 y texto p.23 | Alt. 1 1:1: 8.90E-06 m/s; la hoja da 8.9E-07. La conclusión de p.29 (k crece con el relave en la Alt. 1) depende de ese valor | 23; 180; 29 |
| J2 | Tabla 8 | e0 de Alt. 4 4:1 a 1204 kPa = 0.23 (es 0.58) | 22; 166 |
| J3 | Tabla 8 | Alt. 1 9:1 101 kPa: ρd antes del corte 2.163 = ρd final | 20; 115 |
| J4 | Hojas CID | «Criterio: Esfuerzo Desv. Máximo», pero el σ1 impreso corresponde a εa ≈ 16 % (20 % en el compuesto) | 108-173 |
| J5 | Tabla 8 frente a las hojas | Máximo desviador de la Alt. 1 y del compuesto: diferencias de −10.1 a +20.9 kPa (máximo 0.75 %) | 20; 108-131 |
| J6 | Texto p.19 | «humedad inicial entre 1.6 % y 8.1 %»; la Tabla 8 llega a 8.5 % | 19; 21 |
| J7 | Texto p.11 y p.27 | «D85 … 15.3 mm a 187 mm» (debe ser 18.7); p.27 «14.4 mm a 0.39 mm» | 11; 27 |
| J8 | Gs de las hojas triaxiales | «G. Específica Promedio» distinta de la Tabla 5, sin explicación | 108-173; 15 |
| J9 | Texto p.9 | Dice «las muestras de desmonte fueron mezcladas en 0.33 M1 …» cuando se refiere al relave | 9 |

## 7. Condiciones clave (detalle en `condiciones_*.csv`)

- **Golder 2010.**
  - Ensayos CU de pequeña escala sobre la matriz truncada: < 3/8" en probetas de 2.8" (D/Dmax = 7.5), < 5/8" en 4" (6.3-6.4) y < 1" en las de 6" de Vector (6.0). El material de terreno tiene TM de 19-35" en la Fase A y 12" en la Fase B.
  - Granulometría de la fracción ensayada: no informada.
  - Montaje a la «densidad de campo» medida por reemplazo de agua o a la densidad mínima ASTM D4253/4254 (< 5/8"), con la humedad pedida por el cliente.
  - Golder no informa B ni contrapresión; las probetas terminan con S ≈ 100 %. Vector informa B = 0.86-0.93 y contrapresión de 205-207 kPa.
  - σ′3c de 125 a 1577 kPa.
  - Velocidad: 0.083-0.167 %/min (Golder) y 0.082 %/min (Vector).
  - Solo Vector tabula la curva.
- **Golder 2021.** CID en probetas de 6" × 12" sobre desmonte truncado a 1" (sin escalamiento paralelo). σ′3 de 96 a 1206 kPa. Compuesto denso (≈90 % del Proctor) y mezclas sueltas (≈78 % del Proctor). Curva tabulada en todas las probetas. Sin UCS, carga puntual, Los Ángeles ni durabilidad.
