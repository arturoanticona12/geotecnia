# Verificación de ensayos edométricos de desmonte (Antamina)

Fecha: 2026-10-10. Archivo de datos: `edometros_verificados.csv` (278 filas, 8 ensayos, una fila por escalón).

## 1. Método

1. **Índice de páginas por texto.** Usé los `.txt` de `datos_antamina/texto/`, que tienen marcas `=== PÁGINA n ===` alineadas con la numeración del PDF, y busqué *edom|consolidaci|odóm|One-Dimensional|Codisposal 4*. Con eso no tuve que leer los PDF completos (366 y 396 páginas).
2. **Tablas.** Transcribí los valores de la capa de texto vectorial del PDF y los confirmé contra el render de la página (pypdfium2, escala 2) en las páginas W2024 p121 y W2022 p295, p324 y p359. Además comprobé la aritmética:
   - C4: εv = asiento (mm, p122) / 300 mm.
   - MN 2011: e recalculado desde H.
   - En todas las filas tabuladas, e ≈ e0 − εv(1+e0) con |Δ| ≤ 0.0015. No hay excepciones.
3. **Gráficos.** Los ensayos Golder de 0.24 m sin hoja de laboratorio se leyeron de los vértices de las polilíneas y de los centros de los marcadores vectoriales del PDF (pdfplumber). La calibración se hizo con las líneas de grilla y los rótulos de los ejes. Están marcados como «lectura de gráfico». Para cada punto crucé εv (Fig. 33/34) con e (Fig. 31/32) mediante e = e0 − εv(1+e0), y el error quedó por debajo de 0.0015 en e.
4. **Unidades y signos.**
   - σ′v [kPa] = kg/cm² × 98.0665.
   - En el C4, IDIEM usa signo negativo para la compresión; en el CSV va positiva.
   - En MN 2011, εv = (90 − H)/90 con H tabulada (cálculo propio, 3 decimales).
5. Scripts en `scratchpad/ocr_edo/`: `idx.py`, `pg.py`, `render.py`, `poly.py`, `digit.py`, `markers.py`, `build.py` y `compare.py`.

## 2. Índice de páginas (página del PDF)

**2024_WSP_Ensayos gran escala mezcla co-disposicion.pdf**

| Contenido | Pág. |
|---|---|
| Programa de mezclas; C4 = 100 % intrusivo | 8–9 |
| Granulometría, scalping a 4″ | 10 |
| Gs aparente del intrusivo (ASTM C127, Tabla 3) | 11 |
| Gs global por mezcla (Tabla 5) | 12 |
| Tabla 11 (programa edométrico), Tabla 12 (e0, ρd, εv final), Figs. 16–17 | 29–32 |
| Bg del edómetro C4 = 9.2 % | 36 |
| Granulometría inicial del «Desmonte de Mina (Intrusivo)», IDIEM 1.914.482-A | 93 |
| **Informe IDIEM 1.914.482-B (Codisposal 4):** portada | 101 |
| Tabla 1 | 104 |
| Metodología | 108–109 |
| Gs < #4 = 2.80 | 110 |
| **Hoja de consolidación** | **121** |
| Lecturas tiempo-asiento | 122 |
| Gráfico e–log σ | 123 |
| Granulometría post-edómetro | 129 |
| Resumen (Tabla 6, deformación en mm y k) | 132 |
| Tabla 7 | 133 |

Los informes C, D y E (pp. 135–347) son de los sets C1–C3, con relave, y no se extrajeron.

**2022_WSP_Pruebas de enrocado 3B a Gran Escala Hornfels para Deformacion.pdf**

| Contenido | Pág. |
|---|---|
| Programa de ensayos; material < 7″ (IDIEM) y < 1″ (Golder) | 4, 6 |
| Tabla 4 (programa edométrico) y §5.1–5.3 | 31–32 |
| Fig. 31: e–log σ, hornfels | 33 |
| Fig. 32: e–log σ, mármol | 34 |
| Fig. 33: εv–σ, hornfels | 35 |
| Fig. 34: εv–σ, mármol | 36 |
| Tabla 7 (Bg) | 41 |
| Granulometrías IDIEM inicial/post: MN 2021 | 61 |
| Granulometrías IDIEM inicial/post: HF | 62 |
| Granulometrías IDIEM 708.397-A (2011): inicial | 66 |
| Granulometrías IDIEM 708.397-A (2011): «Probeta 6 Odómetro» | 67 |
| **MN 2011, hoja 708.397-A** | **295** |
| **HF 1.0 m, IDIEM 1.555.677-B.1** | **300–302** |
| **MN 2021 1.0 m, IDIEM 1.555.677-A REV2** | **324** |
| Lecturas tiempo-altura | 325 |
| Golder Test 1, gráficos | 358 |
| **Golder Test 1, mármol 0.24 m, tabla** | **359** |
| Anexo C (pp. 350–357): son triaxiales CID de 6″, no edómetros | — |

No hay hoja de laboratorio de los edómetros Golder de hornfels ni del mármol a 2.3 t/m³.

## 3. Ensayos extraídos

| ensayo_id | D × H (mm) | Dmax (mm) | Gs (origen) | ρd ini | e0 (origen) | w / S | σ′v máx (kPa) | Ramas |
|---|---|---|---|---|---|---|---|---|
| INT-edo-0.6m-C4 (IDIEM/WSP) **nuevo** | 600 × 300 (área 2827.43 cm²) | 101.6 (scalping bajo 4″) | 2.85: ponderado D854 de 2.80 (< #4, IDIEM p110) y 2.87 (> #4, C127 WSP p11); Tabla 5 p12 | 2.00 | 0.425, informado p121 (= 2.85/2.00 − 1) | 3.00 % / 20.12 % | 5884 (60 kg/cm²) | carga + descarga (32, 16, 4) |
| HF-edo-1.0m (IDIEM) | 1000 × 700 | 177.8 (< 7″; inicial p62) | 2.60, «estimado» por IDIEM (p300) | 2.100 | 0.238, informado | 1.69 % / – | 6865 (70) | carga 0→60, descarga →12, recarga →60, carga →70, descarga →0 |
| MN-edo-1.0m-2021 (IDIEM) | 1000 × 700 | 177.8 (inicial p61) | 2.60, «estimado» (p324) | 2.100 | 0.238, informado | 1.50 % / – | 6865 (70) | ídem |
| MN-edo-1.0m-2011 (IDIEM 708.397-A) | 949.7 × 900 | 178 (inicial p66) | 2.700, «Peso específico Integral» (p295) | 2.100 | 0.286, **calculado** (no tabulado) | 0.088 % / – | 5884 (60) | carga + descarga |
| MN-edo-0.24m-1.86 (Golder Test 1) | 241.0 × 202.0 | 25.4 (material < 1″) | 2.70, «Assumed» (p359) | 1.856 | 0.455, informado | 1.20 % / 7 % | 4799 | carga, descarga, recarga, descarga |
| HF-edo-0.24m-2.1 (Golder) | 240 × ≈200 (nominal p31–32) | 25.4 | no informado; implícito ≈ 2.77 | 2.1 (nominal) | 0.317, **lectura de gráfico** Fig. 31 | – | ≈4800 | carga, descarga, recarga, descarga |
| HF-edo-0.24m-1.8 (Golder) | 240 × ≈200 | 25.4 | no informado; implícito ≈ 2.76 | 1.8 (nominal) | 0.532, **lectura de gráfico** (vértice recortado fuera del eje) | – | ≈4800 | ídem |
| MN-edo-0.24m-2.3 (Golder) **nuevo** | 240 × ≈200 | 25.4 | no informado; implícito ≈ 2.71 | 2.3 (nominal) | 0.178, **lectura de gráfico** Fig. 32 | – | ≈4800 | solo carga graficada |

**Gradaciones.**

- **C4.** El intrusivo inicial pasa 96.2 % por 4″, 67.0 % por 1″, 25.7 % por #4 y 6.6 % por #200 (p93). El «cortado bajo 4″» solo aparece en gráfico (p108). Post-edómetro: 100 % por 4″, 30.8 % por #4 y 8.5 % por #200 (p129).
- **HF 1.0 m (p62).** Inicial: 100 % por 7″, 45.7 % por 1″, 12.7 % por #4 y 2.6 % por #200.
- **MN 2021 (p61).** 100 % por 7″, 51.9 % por 1″, 24.2 % por #4 y 10.9 % por #200.
- **MN 2011 (p66).** 100 % por 178 mm, 38.0 % por 1″, 14.7 % por #4 y 4.9 % por #200.
- **Golder 0.24 m.** La gradación de la probeta no está tabulada; solo se dice «material < 1″» y que la densidad se corrigió por tamaño según Dorador et al. (2018) (p32).

## 4. Diferencias con `base/edometros.csv`

| Ensayo | Campo | Base | PDF / esta verificación | Página |
|---|---|---|---|---|
| INT-edo-0.6m-C4 | todo | no existe | 10 escalones nuevos | W2024 p121 |
| MN-edo-0.24m-2.3 (Golder) | todo | no existe | 14 escalones nuevos (lectura de gráfico) | W2022 p36, p34 |
| HF-edo-0.24m-2.1 | e (26 filas) | vacío | 0.317 → 0.236, lectura de gráfico Fig. 31 | p33 |
| HF-edo-0.24m-2.1 | σ en el 1.er y último punto | 0.0 | ≈24 kPa (así está graficado; no es 0) | p35, p33 |
| HF-edo-0.24m-1.8 | e (25 filas) | vacío | 0.532 → 0.289, lectura de gráfico Fig. 31 | p33 |
| HF-edo-0.24m-1.8 | σ en el 1.er y último punto | 0.0 | ≈24 y ≈18 kPa | p35, p33 |
| HF-edo-0.24m-2.1 / 1.8 | σ, εv (resto) | — | coinciden: \|Δσ\| ≤ 1 kPa, \|Δεv\| ≤ 0.01 % | p35 |
| HF-edo-0.24m-* | página | 35 | 35;33 (εv de p35, e de p33) | — |
| MN-edo-1.0m-2011 | fila inicial | ausente | añadida: σ = 0, e0 = 0.286 calculado (no tabulado) | p295 |
| MN-edo-1.0m-2011 | εv | 2 decimales | 3 decimales; misma fórmula; \|Δ\| ≤ 0.004 % (redondeo) | p295 |
| HF-1.0m, MN-2021, MN-2011, MN Golder Test 1 | σ, εv, e, página | — | **sin diferencias** (69 + 69 + 38 + 26 filas) | 300–302, 324, 295, 359 |

## 5. Dudas e inconsistencias de las fuentes

1. **εv final del C4 según WSP.** WSP (Tabla 12 p30 y texto p31) da εv final = 17.4 % a 5880 kPa. La hoja IDIEM da 16.69 % a 60 kg/cm² y 16.27 % al final (4 kg/cm²). Leí la Fig. 17e de WSP (p32, vectorial) y da 4.3, 10.3, 12.1, 14.0, 15.8 y 17.9 % en carga, y 17.4 % en el último punto de descarga. Los puntos de la figura difieren de la tabla entre un 2 % y un 7 % relativo. No encontré la fórmula que lo explica. Usé la hoja IDIEM.
2. **Diámetro del edómetro C4.** La Tabla 1 del informe IDIEM (p104, y p227 del informe D) rotula la consolidación como «100 cm». La hoja (área 2827.43 cm²), el título «molde de 60 cm» y WSP (Tabla 11) indican 0.60 m. Usé 600 mm.
3. **Golder Test 1, mármol a 1.86 t/m³.**
   - La Fig. 34e (p36) grafica εv mayores que la hoja: 16.72 % frente a 15.63 % a 4800 kPa, y 13.51 % frente a 12.89 % al final.
   - La Fig. 32 (e) sí coincide con la hoja.
   - El texto (p33) cita «17 %».
   - La e final de fase de la hoja (0.220, altura LVDT 169.44 mm) no cuadra con la e de la última fila (0.267).
   - Usé la tabla.
4. **Rótulos de probetas del mármol.** El texto (p33) dice que la Probeta 3 es de 1.8 t/m³ y la 4 de 2.3 t/m³. La Tabla 4 (p31) y las leyendas de la Fig. 34 dicen lo contrario: P3 = 2.3 y P4 = 1.8. Además, la Tabla 7 (p41) rotula el hornfels de 0.24 m «2.3 t/m³», aunque se compactó a 2.1 (p31 nota 4; p32).
5. **Gs de los ensayos IDIEM 2021-22.** Usan Gs 2.60 «estimado», no medido. Ese valor fija e0 = 0.238 y todas las e. Si se usara un Gs medido en esas litologías, las e cambiarían.
6. **Ensayos Golder de 0.24 m sin hoja de laboratorio.**
   - El Gs y la ρd real se desconocen.
   - El e0 sale del gráfico y el Gs implícito se infiere suponiendo la ρd nominal.
   - El primer punto está graficado a ≈25 kPa, no a 0.
   - En el HF 1.8, ese punto (e = 0.532) queda fuera del eje y la figura lo recorta.
   - Del mármol a 2.3 t/m³ solo hay rama de carga, y su Bg figura como «-» (p41).
7. **Altura de los edómetros IDIEM de 1.0 m.** WSP da 0.9 m (p4) y 0.7 m (p32). Las hojas dan 70 cm (2021-22) y 90 cm con D = 94.97 cm (2011). Usé las hojas.
8. **Carga inicial.** WSP (p32) habla de 18 kPa iniciales. Eso solo aplica a 2011 (0.182 kg/cm²). En 2021-22 la saturación se hizo «a 0 kg/cm²» (p325). En el C4 fue a 0.10 kg/cm² (9.8 kPa).
