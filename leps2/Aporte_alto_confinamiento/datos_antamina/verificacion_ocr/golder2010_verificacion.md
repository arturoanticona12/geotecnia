# Verificación de Golder (2010), «Caracterización material de ROM – Proyecto IPCC»

Fuente: `Data Antamina/2010_Golder_Caracterizacion ROM IPCC.pdf` (232 páginas). Es un memorando técnico de Golder Associates Perú (proyecto 099-4151017, 25-mar-2010) con sus anexos.
Fecha de la verificación: 2026-10-10. Las páginas citadas son las del visor del PDF (1 a 232), no la numeración impresa.

## 1. Método

1. **Capa de texto.** El PDF es digital (salida de Excel/Word), no escaneado. Todas las páginas útiles tienen capa de texto, que extraje con `pdfplumber` (`dedupe_chars()` elimina los caracteres duplicados de las celdas en negrita).
2. **Lectura en imagen.** Rendericé las páginas con `pypdfium2` (escala 2 a 3) y las leí visualmente:
   - Tablas 2, 3 y 4 (p. 8–10) y Tabla 1 (p. 7).
   - Las 15 hojas resumen CU de Golder (p. 82, 87, …, 152).
   - Hojas Vector p. 161, 168 y 179 (tablas de la curva) y las 4 hojas de envolventes Vector (p. 165, 171, 177 y 183).
   - Índices p. 48, 49, 66 y 81.
   - En todas ellas el texto extraído coincidió con la imagen dígito a dígito.
3. **Envolventes Vector.** Los recuadros de las p. 165, 171, 177 y 183 tienen texto fragmentado, así que los transcribí desde la imagen.
4. **Valores calculados.** Se marcan con el sufijo `_calc`: u = σ3 − σ′3, q = σ′1 − σ′3, p′ = (σ′1 + 2σ′3)/3, γd = ρd·9.81 y la relación σ′1/σ′3. Los números que no llevan `_calc` son impresos.
5. **Contraste.** Comparé con `base/ensayos.csv` (57 filas G2010) campo por campo, con tolerancia de medio dígito del valor de la base. Hice 1596 comparaciones. También contrasté con `indices_roca.csv` (238 filas G2010) y `materiales.csv` (19 filas).

Scripts en el scratchpad de la sesión (`ocr_g2010/`): `txt.py`, `parse.py`, `build.py`, `compare.py`, `indices.py` y `cmp_idx.py`.

### Entregables (esta carpeta)

| Archivo | Contenido |
|---|---|
| `golder2010_cu.csv` | Una fila por probeta (57). Estados de máximo desviador (`maxdev_*`) y máxima oblicuidad (`maxobl_*`, solo Vector). Para Vector añade el «pico» que usa el laboratorio (`vpico_*`). Incluye las envolventes de la hoja, las de 12 % (Vector) y las de las Tablas 3 y 4, con columnas de página. |
| `golder2010_vector_curvas.csv` | Las 12 curvas Vector completas (324 filas): εa, q, u, σ′3, σ′1, p, t, t/p y oblicuidad, con página. |
| `golder2010_indices.csv` | 732 filas en formato largo: Tabla 2 completa, granulometría de campo de la Tabla 1, densidad in situ, densidades mínima y máxima, C127, D854, Los Ángeles, sulfato, UCS y carga puntual por probeta, y permeabilidad. Cada fila lleva su página. |

## 2. Índice de páginas

| Páginas | Contenido |
|---|---|
| 1–5 | Memorando: ensayos y normas (p. 2), discusión, cuadro de diámetro de probeta frente a Dmax (p. 3: 2.8″ → 3/8″, 4″ → 5/8″, 6″ → 1″) y rangos de c′ y φ′ (p. 4–5) |
| 6–10 | Tablas. **Tabla 1** (p. 7): humedad natural y granulometría de campo de las fases A y B. **Tabla 2** (p. 8): resumen de índices. **Tabla 3** (p. 9): c y φ de la fase A. **Tabla 4** (p. 10): c y φ de la fase B |
| 11–17 | Figuras 1–4 (granulometrías A frente a B), 5–6 (τ′ relativo para σ′v = 1000 kPa) y 7 (e frente a ρd). Son solo gráficos |
| 18–34 | Anexos: humedad D2216 (p. 19–26) y granulometrías D422/D1140 (p. 27–34) |
| 35–42 | Densidad in situ por reemplazo de agua, D5030 (fases A y B, 4 litologías) |
| 43–47 | Densidades mínima y máxima, D4253/D4254: Exoskarn fase A y las 4 litologías de fase B (material < 5/8″) |
| 48 | Gs y absorción del agregado grueso, C127 |
| 49 | Gs de sólidos, D854 |
| 50–57 | Abrasión Los Ángeles, C535 (1000 revoluciones) |
| 58–65 | Inalterabilidad en sulfato de magnesio, C88 |
| 66–73 | Compresión uniaxial, D2938 (2 probetas por litología y fase) |
| 74–81 | Carga puntual, D5731 (4 probetas por litología en fase A y 8 en fase B) |
| 82–156 | **Triaxiales CU de Golder**: 15 juegos de 5 páginas cada uno. Por juego: hoja resumen, curvas q–εa y u–εa, círculos de Mohr con c y φ, diagrama p′–q y fotos. Hojas resumen en p. 82, 87, …, 152 |
| 157–160 | Permeabilidad de pared flexible, D5084 (Intrusivo y Hornfels 4″, fases A y B) |
| 161–184 | **Triaxiales CU de Vector** (6″, fase B, informe VP-209-09E): 4 juegos de 6 páginas cada uno. Por juego: 3 tablas de curva, gráficos, envolventes y fotos |
| 185–232 | CISMID: ensayos de carga directa in situ (D1194). No son ensayos de laboratorio de corte |

## 3. Qué representan exactamente los esfuerzos

### Hojas Golder (2.8″ y 4″; 45 probetas)

- **Datos de consolidación.** Cada probeta da el «Esfuerzo Efectivo Inicial (σ3)», que es σ′3 de consolidación.
- **Datos de corte.** Dan εa en la falla, el criterio «Esfuerzo Desv. Máximo» y cuatro esfuerzos principales en la falla: σ1, σ1′, σ3 y σ3′.
- **El σ3 «total» impreso es siempre igual a σ′3c.** Ocurre en las 45 de 45 probetas. Es la presión de celda menos la contrapresión (esfuerzo neto); no es el esfuerzo total absoluto. Ni la presión de celda ni la contrapresión ni B están informadas.
- σ1 − σ3 = σ1′ − σ3′, con diferencias de ±1 kPa por redondeo.
- σ3 − σ3′ es el **exceso de presión de poros Δu** en la falla. Es negativo en el mármol negro denso (dilatancia).
- **Criterio de falla.** Solo se informa el máximo desviador. No hay tabla de la curva, de modo que la máxima oblicuidad es «no informado».

**Conclusión para la base.** En las filas de 2.8″ y 4″, `sigma3_kPa` = `maxdev_sigma3f_kPa` = σ′3 efectivo en la falla en el estado de máximo desviador. No es el esfuerzo de consolidación (ese está en `sigma3c_kPa`) ni el total. Que coincidan es correcto, no un error. `sigma1_kPa` y `maxdev_sigma1f_kPa` son σ′1 en la falla, y `u_falla_kPa` es Δu. La base deja la máxima oblicuidad como «no informado», y está bien.

### Hojas Vector (6″; 12 probetas)

- Cada hoja da la presión de celda, la contrapresión, B (0.86–0.93, por debajo de 0.95) y σ′3c (500, 250 o 125 kPa; σ′3c = celda − contrapresión).
- La tabla completa de la curva da εa, Δσ, u (exceso), s̄3 y s̄1 (efectivos, con barra), p̄ = (σ′1 + σ′3)/2, q̄ = (σ′1 − σ′3)/2 y la oblicuidad.
- Comprobé las identidades en todas las filas (diferencia ≤ 0.01): s̄3 = σ′3c − u, Δσ = s̄1 − s̄3, p̄ y q̄.
- Vector traza dos envolventes:
  - una «a valores pico de esfuerzo desviador» (un punto marcado por probeta);
  - otra «al 12 % de deformación».
- En la base, `sigma3_kPa` y `sigma1_kPa` de 6″ son el punto «pico» de Vector, el primer máximo local. `maxdev_*` es el máximo absoluto de la curva y `maxobl_*` la máxima oblicuidad.
- **El primer máximo local y el máximo absoluto difieren en 4 probetas:** HG 125, HG 250, EXO 250 y EXO 500 (en las cuatro el máximo absoluto está al 14 %). En **EXO 125** la curva crece de forma monótona; Vector marca εa = 1.0 % (σ′3 = 64.57; p, q ≈ 127.6, 63.0 en la p. 183) y la base lo recoge así, con la nota «la curva no tiene pico».

## 4. Diferencias contra `ensayos.csv`

**Resultado: 0 discrepancias en valores impresos.** De 1596 comparaciones, el script marcó 85:

- **45 son un artefacto del script.** El campo `maxobl_ratio` vale «no informado» tanto en la base como en el PDF, en las 45 probetas Golder.
- **40 son diferencias de procedencia o de criterio**, sin error de transcripción. Se detallan en las dos tablas siguientes.

### Valores calculados en la base que Vector no informa (p. 161–181)

Vector no da Gs ni e. La base usa el Gs de D854 de Golder (p. 49) y calcula e0 y e después de consolidar con ρd inicial y final. Comprobé el cálculo: por ejemplo, MN 500: 2.747/2.027 − 1 = 0.355. El orden de los valores es 500 / 250 / 125 kPa.

| set_id | Campo | Base | PDF | Página |
|---|---|---|---|---|
| G2010-B-MN-6in | Gs / e0 / e_post_consol | 2.747 / 0.355, 0.357, 0.357 / 0.333, 0.339, 0.345 | no informado (Vector) | 161–163 (Gs: p. 49) |
| G2010-B-HG-6in | Gs / e0 / e_post_consol | 2.802 / 0.312, 0.31, 0.31 / 0.272, 0.279, 0.282 | no informado | 167–169 |
| G2010-B-INT-6in | Gs / e0 / e_post_consol | 2.742 / 0.353, 0.354, 0.355 / 0.276, 0.304, 0.323 | no informado | 173–175 |
| G2010-B-EXO-6in | Gs / e0 / e_post_consol | 3.338 / 0.419, 0.418, 0.431 / 0.368, 0.386, 0.403 | no informado | 179–181 |

### Criterio de «falla» en EXO 125

| set_id | Campo | Base (punto marcado por Vector, εa = 1.0 %) | PDF (primer máximo local = máximo absoluto, εa = 14 %) | Página |
|---|---|---|---|---|
| G2010-B-EXO-6in σ′c = 125 | sigma3_kPa / sigma1_kPa / eps_axial_falla_pct / u_falla_kPa | 64.57 / 190.64 / 1.0 / 60.43 | 135.53 / 632.32 / 14.0 / −10.53 | 181 y 183 |

Las dos lecturas existen en el PDF. La base está documentada; solo conviene no tratar ese punto como «pico».

### Campos que coinciden

Coinciden todos los demás campos verificados: diámetro, altura, Dmax, Gs, γd, e0, w, σ′3c, εa, σ′3f, σ′1f, q y u en el máximo desviador, el estado completo de máxima oblicuidad (Vector), B, contrapresión, e y S tras consolidar y γd tras consolidar.

### `indices_roca.csv` y `materiales.csv`

- **`indices_roca.csv`.** Los 238 valores G2010 están respaldados por las hojas o por la Tabla 2. Solo quedan sin respaldo directo 8 promedios de Is50 que la base calcula (y declara como calculados).
- **`materiales.csv`.** Coinciden Dmax, diámetro y altura de probeta, Gs, w de montaje, velocidad (incluido B-HG-2.8 = 0.167/0.167/0.125 %/min), contrapresión de Vector, UCS, Is50, Los Ángeles, durabilidad y absorción.

## 5. Datos del PDF que faltan en la base

1. **Curvas Vector completas.** Son 27 puntos por probeta (p. 161–181) y la base solo guarda tres estados. Están ahora en `golder2010_vector_curvas.csv`.
2. **Envolventes Vector al 12 %** (p. 165, 171, 177 y 183). La base las anota parcialmente en `notas`. Valores (c, φ total; c′, φ′):
   - MN: 0/26; 10/38
   - HG: 0/26; 5/39.2
   - INT: 0/12.4; 0/38.1
   - EXO: 66/25.5; 0/42
3. **Envolventes «pico» de Vector con los parámetros a y α** (en `golder2010_cu.csv`).
4. **Granulometría de campo de la Tabla 1** (p. 7). Es la curva completa antes (fase A, de 35″ a #200) y después del chancado (fase B, de 12″ a #200) y es la única medida de rotura disponible (rotura por chancado, no en el triaxial). Ahora está en `golder2010_indices.csv`.
5. **Réplicas individuales de densidad mínima y máxima, y humedad de las hojas de densidad in situ.** Las humedades in situ difieren de la «humedad natural» de la Tabla 2. Por ejemplo, HG A: 1.44 % en la hoja (p. 36) frente a 2.4 % en la Tabla 2.
6. **Permeabilidad: B y condiciones de cada ensayo** (p. 157–160).
7. **Rotura de partículas en los triaxiales: no informado.** No hay granulometría después del ensayo ni Bg; solo fotos de las probetas (p. 86, 91, …, 156 y 166, 172, 178, 184).

## 6. Incoherencias del propio informe

1. **Tabla 3, fase A, 2.8″ (p. 9): c y c′ ≈ 1/98 de lo que dan las hojas.**
   - Hojas: MN 871/259, HG 149/33, INT 313/103, EXO 80/0 kPa.
   - Tabla 3: 9/3, 2/0, 3/1, 1/0.
   - Están en kg/cm² aunque el rótulo dice kPa; los ángulos coinciden.
2. **Tabla 4, 6″ (p. 10): mezcla de criterios.**
   - MN y EXO: c, φ totales y c′, φ′ corresponden a la envolvente pico (29.6 → 30 y 24.3 → 24).
   - HG: φ total = 26 sale de la envolvente al 12 % (la del pico es 22.8), y φ′ = 29.0 de la del pico (29.2).
   - INT: φ total = 12.0 sale de la del 12 % (12.4; la del pico es 15.3), y φ′ = 28.0 de la del pico (27.9).
3. **Tabla 4, B-MN-4″: ρd «promedio» = 1.722.** Es el valor de la probeta 3 sola; el promedio de las tres es 1.790 (p. 137). En B-INT-4″ la tabla da 1.833 frente a un promedio de 1.836.
4. **Tabla 2, Gs del material grueso de la fase A ≠ hoja C127 (p. 48).**
   - Tabla 2: MN 2.696, HG 2.733, INT 2.451, EXO 3.172.
   - Hoja C127 (Gs bulk): 2.717, 2.737, 2.461, 3.212.
   - En la fase B sí coinciden con el Gs bulk.
5. **Tabla 2, carga puntual de B-Intrusivo = 78.06 MPa.** La media de la hoja (p. 80) es 784.9 kg/cm² = 76.97 MPa. Las demás coinciden.
6. **Tabla 2, fase B: k rotulada en cm/s.** Las hojas (p. 159–160) la dan en m/s (2.2E-06 y 2.6E-06 m/s).
7. **Norma de durabilidad.** La p. 2 dice «sulfato de sodio» y las hojas, sulfato de magnesio.
8. **Saturación final por encima del 100 %** en B-EXO 2.8″ (105.2, 101.6 y 101.8 %, p. 132) y B-EXO 4″ (100.2–100.4 %). Viene del Gs usado.
9. **Cabeceras Vector con valores iniciales idénticos entre litologías** (por ejemplo, w = 4.50 % en MN e INT). La base ya lo señala como posible plantilla copiada.

## 7. Dudas abiertas

- **Fase A, ¿ROM o chancado?** El memo (p. 1) define la fase A como «material original procedente del tajo». Sin embargo, las hojas de densidad in situ de la fase A dicen «Material Chancado Fase A» (p. 35–38), y el muestreo de ambas fases se hizo en el «acopio parte baja de chancadora secundaria» (p. 19–34). La base ya lo marca como `clase_confianza = dudosa`.
- **Densidad de montaje.** Fase A 2.8″, fase A 4″ HG/INT y fase B 2.8″ se remoldearon a la «densidad de campo». Fase A 4″ EXO y fase B 4″ (las 4 litologías) se remoldearon a la «densidad mínima», según las observaciones de las hojas. Las de 6″ solo dicen «Remoldeado».
- **Golder no informa B ni contrapresión.** La saturación final es ≈ 100 %, pero no se puede verificar la calidad de la saturación.
- **Vector: B entre 0.86 y 0.93**, por debajo del 0.95 habitual. Los u medidos pueden estar subestimados.
- **σ′3c máximo = 1577 kPa** (Golder 2.8″). Con σ′3c ≈ 1570 kPa, Δu en la falla es positivo en las 8 probetas y σ′3 en la falla queda entre 401 y 1028 kPa (p. 82–132). El rango efectivo «en la falla» es, por tanto, menor que el de consolidación.

