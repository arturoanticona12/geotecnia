# Stantec 2023, Apéndice A.5.5: propiedades índice del desmonte ROM

**Fuente:** `2023_Stantec_A.5.5_Propiedades Desmonte ROM.pdf` (1 lámina A3, L-01, fecha 9/14/2023)
**Proyecto:** Ingeniería de Prefactibilidad Gate 2A del depósito de Relaves Site 3 y Depósito de desmonte EE4BE-S3 (Stantec).
**Tipo de material:** ROM.
**CSV de ensayos:** no se generó. La lámina no presenta ensayos individuales identificables. Es una compilación de puntos de Golder (2010, 2011, 2012 y 2022), de «Puntos Histórico 1 y 2» y de Hawley y Cunning (2017).

## Contenido y objetivo

La lámina resume las propiedades índice y de resistencia que sirven de base al diseño del desmonte ROM. Contiene:

1. Granulometrías de terreno por litología (Golder, 2010) y las granulometrías de los triaxiales monótonos y de carga-descarga de Golder 2012 y 2022, con diámetros de 6" y 40". Incluye además las bandas A, B y C de Golder (1987).
2. La tabla «% de Material Presente».
3. El gráfico de resistencia τ–σn con tres envolventes.
4. Gs, UCS, abrasión y durabilidad por litología.
5. La densidad seca vs p′ con la envolvente propuesta y su ecuación.

## Clasificación litológica (tipo_material = ROM)

| litologia_informe | litologia | litologia_detalle | alteracion | Datos de la lámina para esta litología |
|---|---|---|---|---|
| Mármol Negro | Mármol | mármol negro | no indicada | granulometría de terreno, tabla de %, Gs, UCS, abrasión, durabilidad |
| Hornfels Gris | Hornfels | hornfels gris | no indicada | ídem; pared flexible Golder (2010): w 4 %, k 3,3×10⁻⁶ m/s |
| Intrusivo | Intrusivo | (no indicado) | no indicada | ídem; pared flexible Golder (2010): w 9 %, k 2,5×10⁻⁶ m/s |
| Exoskarn Diposido / Diopsido (escrito así en la leyenda y en la tabla) | Skarn | exoskarn diopsídico | no indicada | ídem |
| Enrocado Mármol (Golder 2012, 2022) | Mármol | (no indicado) | no indicada | solo puntos τ–σn |
| Enrocado Hornfels (Golder 2022) | Hornfels | (no indicado) | no indicada | solo puntos τ–σn |

La lámina no describe la mineralogía ni el origen (tajo, banco o fase), y no da carga puntual ni absorción. No hay mezclas de litologías. Los puntos «Enrocado Mármol» y «Enrocado Hornfels» aparecen en la lámina del ROM aunque su nombre corresponde a la clase Enrocado.

## Envolventes de resistencia (gráfico superior derecho)

- Leyenda:
  - Envolventes: «Moderada a buena calidad (Antamina)» (celeste continua), «Buena calidad (Piteau, 2013)» (morada continua), «Función Golder» (roja segmentada) y «Leps (1970)» (grises segmentadas).
  - Puntos: Puntos Histórico 1 y 2, (Golder, 2011), Enrocado Mármol (Golder, 2012), IPCC Study (Golder, 2010), Enrocado Mármol (Golder 2022) y Enrocado Hornfels (Golder, 2022).
- La lámina **no da parámetros numéricos**. Los valores se extrajeron de las polilíneas vectoriales del PDF, calibradas con las etiquetas de los ejes (±15 kPa).

| σn (kPa) | 100 | 250 | 500 | 1000 | 1500 | 2000 | 2500 | 3000 | 3500 | 4000 | 4500 | 5000 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| τ «Moderada a buena calidad (Antamina)» | 88 | 213 | 417 | 797 | 1187 | 1563 | 1891 | 2228 | 2582 | 2927 | 3236 | 3527 |
| φ_sec (°) | 41,4 | 40,4 | 39,8 | 38,6 | 38,4 | 38,0 | 37,1 | 36,6 | 36,4 | 36,2 | 35,7 | 35,2 |
| τ «Buena calidad (Piteau, 2013)» | 88 | 213 | 417 | 797 | 1191 | 1578 | 1951 | 2314 | 2672 | 3028 | 3394 | 3764 |
| φ_sec (°) | 41,4 | 40,4 | 39,8 | 38,6 | 38,5 | 38,3 | 38,0 | 37,6 | 37,4 | 37,1 | 37,0 | 37,0 |
| τ «Función Golder» (aprox.) | ~99 | ~269 | ~502 | 856 | 1213 | 1568 | 1904 | 2230 | 2574 | 2946 | 3251 | 3522 |

- Ajustes potenciales propios (no del informe):
  - Antamina: τ ≈ 1,119·σn^0,950.
  - Piteau 2013: τ ≈ 1,054·σn^0,961.
  - Golder: τ ≈ 2,00·σn^0,878.
- La «Función Golder» está dibujada como relleno de trazos segmentados. Por debajo de ~500 kPa la lectura es ruidosa (±20 kPa).
- La envolvente de Antamina coincide con la de Piteau 2013 hasta ~1000 kPa y queda por debajo a σn mayor. Por encima de ~2000 kPa casi se superpone con la Función Golder.

## Granulometría: tabla «% de Material Presente» (verificada en la imagen; cada fila suma 100 %)

| Tipo de desmonte | 12"–36" | 3"–12" | Gravas | Arenas | Finos | Matriz <3": Gravas | Arenas | Finos |
|---|---|---|---|---|---|---|---|---|
| Mármol Negro | 35,1 | 30,2 | 23,6 | 8,3 | 2,8 | 71,4 | 22,8 | 5,8 |
| Hornfels Gris | 22,1 | 49,3 | 24,9 | 2,82 | 0,88 | 86,2 | 11,2 | 2,6 |
| Intrusivo | 21,8 | 38,8 | 31,4 | 6,4 | 1,6 | 80,4 | 16,3 | 3,3 |
| Exoskarn Diópsido | 4,6 | 15,6 | 58 | 19,1 | 2,7 | 76,5 | 20,9 | 2,6 |

Fuente: Golder (2010). Las curvas de los triaxiales Golder 2012/2022 aparecen solo en el gráfico (segmentadas); no las digitalicé.

## Ensayos índice (leídos de gráfico raster, ±0,02 en Gs, ±2 MPa y ±1 %)

| Litología | Gs grueso | Gs fino | UCS mín / Q1 / mediana / Q3 / máx (MPa) | UCS promedio (MPa) | Abrasión (%) | Durabilidad (%) |
|---|---|---|---|---|---|---|
| Mármol Negro | 2,70 | 2,77 | 30 / 38 / 51 / 108 / 136 | 68 | 62 | 44 |
| Hornfels Gris | 2,73 | 2,80 | 47 / 51 / 69 / 75 / 82 | 65 | 24 | 1 |
| Intrusivo | 2,45 | 2,68 | 45 / 48 / 75 / 87 / 88 | 70 | 50 | 34 |
| Exoskarn Diópsido | 3,17 | 3,49 | 64 / 64 / 67 / 78 / 80 | 70 | 37 | 6 |

Estos valores son distintos de los de la lámina A.5.4, aunque las litologías son las mismas. Por ejemplo, el Gs grueso del Intrusivo es 2,45 aquí y 2,65 en A.5.4. Parecen bases de datos distintas, y el valor de 2,45 es anómalamente bajo para un intrusivo.

## Densidad seca vs p′

- La «Envolvente Propuesto» trae su ecuación en la lámina: **y = 2,0425·e^(0,0035·x)**, con y = ρd (t/m³) y x = p′ (×0,1 MPa). La comprobé contra el vector extraído y la diferencia es menor que 0,002 t/m³ entre 0 y 7 MPa.
- Ensayos de pared flexible de Golder (2010):
  - Intrusivo: w = 9 %, k = 2,5×10⁻⁶ m/s.
  - Hornfels: w = 4 %, k = 3,3×10⁻⁶ m/s.

## Edómetros y ensayos no drenados

La lámina no tiene recuadro de edómetro (a diferencia de A.5.4). No hay ensayos no drenados.

## Dudas

1. No hay parámetros numéricos de resistencia. Las tres envolventes se tabularon desde los vectores. Falta confirmar en el informe de diseño de Stantec cuál se adoptó para el ROM; por el nombre, sería probablemente la de «Moderada a buena calidad (Antamina)».
2. Los puntos τ–σn no tienen σ3 ni identificación. Hay que usar los informes originales de Golder 2010, 2011, 2012 y 2022.
3. Hay un Gs grueso de Intrusivo de 2,45, sospechosamente bajo, y diferencias de índices con A.5.4.
4. La lámina no define «Abrasión» ni «Durabilidad».
