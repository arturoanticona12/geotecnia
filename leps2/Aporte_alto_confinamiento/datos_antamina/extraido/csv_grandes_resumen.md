# CSV grandes de Waste Characterization (Antamina, carpeta 250903 Waste Charact)

Scripts y salidas completas en `datos_antamina\paginas\csv_grandes\` (`01_perfil.py`,
`02_relaciones.py`, `03_extraer.py` y sus `*_salida.txt`). Ambos archivos se leen en UTF-8 con separador coma.

## 1. SIMULACIONES_MR2024_V3.csv (23 MB)

- **Qué es:** exportación de Leapfrog Geo (primera línea `# Exported from Leapfrog Geo`) de un modelo de bloques.
  **Una fila = un bloque.** 310 102 bloques, 12 columnas, sin coordenadas XYZ duplicadas.
- **Geometría:** grilla rotada 45° respecto de X/Y. En coordenadas rotadas u = (X+Y)/√2 y v = (Y−X)/√2,
  el espaciamiento es 20 m en ambos ejes, y en Z es 15 m (cotas 3255,5 a 4830,5). Por eso se asumió un
  **bloque de 20 × 20 × 15 m = 6000 m³**. Es una inferencia a partir del espaciamiento de los centroides;
  conviene confirmarla con la definición del modelo.
- **Todos los bloques tienen código de período de desmonte (`XLE2WST_AMIN`, sin nulos).** El archivo
  parece contener solo el desmonte asignado a LE2. No trae bloques de mineral ni columnas de destino
  ni de clase de desmonte (ROM, Chancado, Enrocado).
- **Total:** 1861 Mm³ y 4988 Mt (con 6000 m³ × MR24_BD).

| Columna | Tipo | Contenido observado |
|---|---|---|
| X, Y, Z | float | Centroide del bloque (coordenadas mina) |
| MR24_ABRA | float | Abrasión (12,5 a 66,9; mediana 26,6). Unidad no declarada |
| MR24_AXB | float | Parámetro A×b (30 a 305; mediana 70). Unidad no declarada |
| MR24_BD | float | Densidad (2,17 a 3,46; media 2,68), probablemente t/m³ |
| MR24_BWI | float | Índice de Bond (6,7 a 22,6; mediana 10,2), probablemente kWh/t |
| MR24_RT | int | Código de tipo de roca: 1, 2, 10, 11, 13, 14, 16, 19 y 53 |
| MR24_UCS | float | UCS en MPa (16,8 a 226; mediana 74) |
| LOM25_AMIN_LE2 | float | Año de minado del plan LOM25 (2025 a 2049); 9355 bloques nulos |
| LOM25_FASES_LE2 | texto | Fase del plan LOM25: 8, 9A, 9B, 9C, 9D, 10A, 10B, 11, 1201, 1202, 13, 14 (9355 nulos) |
| XLE2WST_AMIN | int | Período de desmonte LE2: 2025 a 2035 anual, y luego 203637, 203839, 204041, 204245 y 204649 |

Notas:
- `XLE2WST_AMIN` y `LOM25_AMIN_LE2` no coinciden bloque a bloque (la tabla cruzada muestra dispersión
  de ±1 a 3 años). Parecen ser dos programaciones distintas. Los códigos de 6 dígitos parecen tramos
  bienales o trienales (por ejemplo 203637 = 2036-2037), pero falta confirmarlo.
- Las variables MR24_* son **valores de modelo**, no ensayos. Por eso varios bloques de un mismo RT repiten
  exactamente el mismo valor: por ejemplo, el 72 % de los bloques RT 16 tiene AXB = 93,82 y el 61 % de los RT 11
  tiene BWI = 18,00. El nombre "SIMULACIONES" sugiere una realización o un promedio de simulación
  geoestadística, pero falta confirmarlo.

## 2. Merged_Table_Assay_lito_12JUNIO2025_ult.csv (39 MB)

- **Qué es:** tabla de **intervalos de sondaje** (una fila = un intervalo `holeid/from/to`). Tiene 248 620 filas,
  35 columnas y 1873 sondajes; los intervalos no se duplican ni se solapan. El largo de intervalo tiene una mediana de 1,0 m
  (rango 0,001 a 36,6 m), con un total de 258 421 m. Las leyes químicas (BESTEL) están unidas a la litología y a datos geotécnicos
  puntuales.
- **Todos los intervalos tienen `GM_LE2WASTE_Output`** (los mismos 16 códigos de período que `XLE2WST_AMIN`).
  Es decir, se trata de los sondajes que caen dentro del desmonte LE2 programado. Así se cruza con el modelo de bloques,
  por período o espacialmente con mid_x/mid_y/mid_z frente a X/Y/Z.

| Grupo | Columnas | Comentario |
|---|---|---|
| Identificación | holeid, from, to, SAMPLEID, SAMPLETYPE (25 tipos: HHQ, HNQ, DCD, DT, CORE, …), MODEL (RM_2000 a RM_2024-LE2-2A) | MODEL parece ser la campaña o el modelo de origen |
| Plan | GM_LE2WASTE_Output (período desmonte), GM_YEAR_LE2_Output, plp_GM_YEAR_LE2_Output (incluye "OTROS"), plp_GM_FASES_LE2_Output (8, 9BN, 9BS, 9C, 10AN, 10AS, 10B, 11A a 11D, 12A1, 12A2, 12B, 13A, 13B1, 13B2, 13C, 14, 15, OTROS) | plp_GM_YEAR coincide casi 1:1 con GM_LE2WASTE; GM_YEAR_LE2 es otra programación (el 47 % de las filas = 2030) |
| Leyes | Ag_ppm, As_ppm, BI_PPM, Cu_pct, CuAC, CuCN, Mo_pct, Zn_pct, ZnAC (sufijo BESTEL) | No sirven para la resistencia al corte |
| Litología | ROCKCODE (39 códigos), ROCKCODE_NUMEQ (1, 10, 13, 14, 16, 19), sin nulos | Todos los intervalos tienen litología; es la base para la proporción por metros |
| Geotecnia | Fuente (Core_PLT 12 652 / Core_UCS 2258), Geologia_2024, Lithology (66 textos), RT_UCS, UCS_MPa (14 910 datos), RT_RQD, RQD_pc (199 076 datos), RT_Abrasion, ABRASION_pc (1960 datos) | RT_UCS/RT_RQD = "código RT_ZD" o "código RT_No_ZD" |
| Densidad | ROCA (código RT), DTADJ (14 521 datos, 1,95 a 3,53) | Base de densidad distinta de la de UCS (casi no se superponen) |
| Coordenadas | mid_x, mid_y, mid_z | Punto medio del intervalo |

## 3. Leyenda que se puede deducir de los propios datos

La columna `Geologia_2024` trae etiquetas del tipo `Metamorfico_16`. De ahí sale el **grupo** de cada código RT
(sin interpretar más allá de la etiqueta):

| RT | Grupo (según Geologia_2024) |
|---|---|
| 1, 2 | Intrusivo |
| 10, 11 | Sedimentario |
| 13, 14, 16, 19 | Metamorfico |
| 20, 22, 23 | Endoskarn |
| 31, 32, 34, 35, 36, 37 | Exoskarn |
| 50 | Brechas |
| 51, 52, 53 | sin etiqueta en los datos (53 aparece en el modelo de bloques: 403 bloques) |

`ROCKCODE` agrupa en `ROCKCODE_NUMEQ` sin ambigüedad: 1 = IPPA, IPPAO, IPPAMO, IPPEO, IPHPE, DI, BCIPPA, BCIPPAO, BCIPPEO, BMIPPA;
10 = CG, CGS, CA, CN, C, CBMN, CF, CM; 13 = HG, HGS, HC, BCHG, BMHG; 14 = HBV, HGV, HCB, HDP, HMGV, HV;
16 = MC, MG, MGS, MPA, MCGB, MCB, M, MDL, BCM; 19 = MDP. **No hay leyenda de qué roca es cada sigla.**

Atención: `ROCKCODE_NUMEQ` **no equivale exactamente** al código RT de las columnas geotécnicas. Al cruzar RT_RQD con
NUMEQ, el RT 11 cae casi siempre en NUMEQ 10; el RT 14 cae mayormente en NUMEQ 19; y NUMEQ no tiene 2 ni 11.
La equivalencia entre ambos sistemas falta confirmarla.

## 4. Proporción de litologías del desmonte (archivo `litologias_proporcion.csv`)

Formato largo con estas columnas: archivo, base_medida, agrupacion (total, período, año LOM25, fase), clave, codigo_tipo,
litologia_codigo, grupo_geologia_2024, n_registros, volumen_m3, toneladas, metros y pct.

**Modelo de bloques, desmonte LE2 total (4988 Mt), en % de toneladas:**

| RT | Grupo | Mt | % |
|---|---|---|---|
| 16 | Metamorfico | 1801 | 36,1 |
| 11 | Sedimentario | 945 | 18,9 |
| 13 | Metamorfico | 788 | 15,8 |
| 1 | Intrusivo | 691 | 13,9 |
| 10 | Sedimentario | 397 | 8,0 |
| 14 | Metamorfico | 171 | 3,4 |
| 19 | Metamorfico | 137 | 2,7 |
| 2 | Intrusivo | 51 | 1,0 |
| 53 | sin leyenda | 6 | 0,1 |

Por grupo: Metamorfico 58,1 %, Sedimentario 26,9 %, Intrusivo 14,9 %. El modelo no incluye skarn ni brechas, salvo el RT 53.
La proporción varía mucho entre períodos: por ejemplo, el RT 16 va del 16 % (2040-41) al 65 % (2027), y el período 2046-49
tiene 59 % de RT 1. La variación por fase LOM25 está en el mismo CSV.

**Sondajes (metros dentro del desmonte LE2), por ROCKCODE_NUMEQ:** 16 = 33,9 %, 1 = 29,3 %, 19 = 12,8 %, 13 = 11,9 %,
10 = 10,2 %, 14 = 1,8 %. Las siglas principales son IPPA 16,3 %, MC 14,3 %, MDP 12,8 %, IPPAO 10,5 %, HG 7,0 %, CG 5,4 %, MPA 5,2 %
y MG 4,8 %. Los sondajes sobrerrepresentan el intrusivo respecto del modelo (29 % frente a 15 %), algo esperable porque se perfora más donde
hay mineral. **Para la proporción del desmonte conviene usar el modelo de bloques.**

## 5. Propiedades por litología (archivo `propiedades_roca_por_litologia.csv`)

Para cada combinación de variable y código, el archivo trae n, media, desviación estándar, CV, mínimo, p05 a p95, máximo y, en el caso del RQD,
la media ponderada por largo de intervalo.

- Modelo (por MR24_RT): BD, UCS, ABRA, AXB y BWI. Medianas de UCS: RT 1 = 63, 10 = 83, 11 = 69, 13 = 105, 14 = 115, 16 = 74,
  19 = 95 y 2 = 103 MPa. Medianas de BD: RT 1 = 2,45, RT 14 = 2,87, RT 19 = 2,85 y el resto ≈ 2,70 t/m³.
- Sondajes: UCS_MPa por RT_UCS (con y sin separar por Fuente) y por Lithology; RQD por RT_RQD y por ROCKCODE;
  ABRASION por RT_Abrasion; DTADJ por ROCA. El UCS de Core_PLT (carga puntual convertida) es sistemáticamente mayor que el de
  Core_UCS: la mediana global es 83 MPa frente a 57 MPa, y en el RT 13 es 103 MPa frente a 63 MPa. Hay que decidir qué fuente usar.
- El RQD es alto en casi todo (mediana de 100 %, media ponderada de 93 a 97 %). Las excepciones son el RT 1 (≈ 80 %) y los códigos 20, 50, 52 y 53,
  con 23 a 57 % y pocos datos.
- No hay datos de alteración (como variable), GSI, ángulo de fricción, granulometría ni durabilidad.

## 5b. Litología normalizada (Intrusivo / Hornfels / Mármol / Skarn / Caliza / Otra)

`05_litologia_normalizada.py` agrega a ambos CSV las columnas `litologia_normalizada`, `subtipo`,
`criterio_asignacion` y `litologia_tentativa`. El código original se conserva en `litologia_codigo`.
También agrega filas agregadas con `codigo_tipo` = `litologia_normalizada` o `litologia_tentativa`, para el total y para cada período y fase.

- **`litologia_normalizada`** solo asigna lo que el dato dice explícitamente:
  - RT 1, 2 y ROCKCODE_NUMEQ 1 (siglas IPP*, DI) → Intrusivo.
  - RT 20, 22 y 23 → Skarn, subtipo Endoskarn.
  - RT 31 a 37 → Skarn, subtipo Exoskarn.
  - RT 50 → Otra, subtipo Brechas.
  - Lithology "Marble" → Mármol y "Diop. Hornfels" → Hornfels.

  Todo lo demás queda **«sin asignar»**. Eso incluye los RT 10 y 11 (etiquetados solo como "Sedimentario"), los RT 13, 14, 16 y 19
  (solo "Metamorfico"), los RT 51 a 53 y las siglas sin leyenda.
- **`litologia_tentativa`** es una **hipótesis, no una leyenda**: se basa en la inicial de las siglas ROCKCODE que agrupa cada código
  (H* → Hornfels, M* → Mármol, C* → Caliza). La apoyan dos coincidencias: Lithology "Diop. Hornfels" ≈ ROCKCODE HGV (NUMEQ 14) y "Marble" ≈ MCGB (NUMEQ 16).

Resultado para el desmonte LE2 (modelo, % de toneladas):
- Con asignación segura: Intrusivo 14,9 % y **sin asignar 85,1 %**.
- Con la hipótesis tentativa: Mármol 38,9 % (RT 16 = 36,1 y RT 19 = 2,7), Caliza 26,9 % (RT 11 = 18,9 y RT 10 = 8,0),
  Hornfels 19,2 % (RT 13 = 15,8 y RT 14 = 3,4), Intrusivo 14,9 % y RT 53 0,1 %. El modelo no tiene skarn.
- Sondajes por metros (tentativa): Mármol 46,7 %, Intrusivo 29,3 %, Hornfels 13,7 % y Caliza 10,2 %.

**Clase de desmonte y destino:** no se pueden desglosar. Ningún CSV trae ROM, Chancado, Enrocado ni mineral frente a desmonte.
Se revisó `Fragmentación Desmonte 2025.xlsx`, que tiene una sola hoja, "ANÁLISIS DE FRAGMENTACIÓN" (324 × 72): es un registro de voladuras
(fecha, pala, proyecto, malla, taladros, explosivo y fragmentación por fotos). No tiene clase por bloque ni por litología, y no se puede cruzar
con el modelo.

## 6. Qué sirve para el estudio de botaderos de hasta 700 m

1. **Proporción de litologías del desmonte por tonelaje:** modelo de bloques, por período y fase. Permite definir la mezcla
   litológica del botadero y su variación en el tiempo, que es lo que se depositaría en cada etapa de altura.
2. **UCS por litología** (modelo y ensayos): es el insumo para las envolventes de rotura de partículas y de resistencia al corte
   del enrocado bajo alto confinamiento (por ejemplo, en relaciones del tipo Leps o Barton-Kjaernsli que dependen de la resistencia de la roca intacta).
3. **Densidad por litología** (BD y DTADJ): sirve para el peso unitario de la partícula y para ponderar por tonelaje.
4. AXB, BWI y abrasión: son índices de conminución y desgaste. Pueden servir como indicadores de fragilidad o rompibilidad, pero no
   son parámetros de resistencia directos.

## 7. Limitaciones

- No hay destino (desmonte frente a mineral), ni clase de desmonte (ROM, Chancado o Enrocado), ni botadero de destino explícito.
  Solo hay códigos LE2 de período. Es posible que la clase de desmonte esté en `Fragmentación Desmonte 2025.xlsx`.
- El tamaño de bloque se infirió del espaciamiento (6000 m³). Si el modelo tiene subbloques o un porcentaje de bloque, el tonelaje cambia.
- Las MR24_* son estimaciones del modelo, con valores repetidos por RT, y no tienen unidades declaradas en el archivo.
- No se conoce la definición de "ZD" frente a "No_ZD" en RT_UCS y RT_RQD, por lo que no se interpretó.
- El UCS por carga puntual depende del factor de conversión usado, que no está en el archivo.
- Los códigos de skarn y brechas (20 a 53) tienen muy pocos ensayos.

## 8. Dudas para el cliente (leyendas pendientes)

1. Leyenda de **MR24_RT / ROCA / RT** (1, 2, 10, 11, 13, 14, 16, 19, 20, 22, 23, 31 a 37, 50 a 53): nombre de la roca y si 51 a 53 son brechas.
2. Leyenda de las siglas de **ROCKCODE** (IPPA, IPPAO, IPPAMO, IPPEO, IPHPE, DI, CG, CGS, CA, CN, C, CBMN, CF, CM, HG, HGS, HC,
   HBV, HGV, HCB, HDP, HMGV, HV, MC, MG, MGS, MPA, MCGB, MCB, M, MDL, MDP, y los prefijos BC y BM) y de la columna **Lithology**
   (incluye EXO, INT, LMH, XGRDW, XGVDP, XWGV, NGRDW y otras).
3. Por qué ROCKCODE_NUMEQ no coincide con el RT (11→10, 14→19) y cuál de los dos sistemas usar.
4. Significado de **ZD / No_ZD** y de **16_MN** en RT_Abrasion.
5. Significado de **XLE2WST_AMIN / GM_LE2WASTE_Output** (¿períodos 2036-37, …, 2046-49?), si "LE2" es un botadero
   y si el archivo contiene todo el desmonte o solo el que va a LE2.
6. Diferencia entre LOM25_AMIN_LE2, GM_YEAR_LE2_Output y plp_GM_YEAR_LE2_Output; códigos de fase (1201, 1202, 9BN, 10AN, …).
7. Tamaño de bloque, subbloques y si MR24_* corresponden a una realización o a la media de las simulaciones; unidades de ABRA, AXB y BWI.
8. Factor de conversión de PLT a UCS (Core_PLT) y significado de MODEL (RM_xxxx).
9. Dónde está la clasificación del desmonte en ROM, Chancado y Enrocado, que no aparece en estos CSV (ni en el Excel de fragmentación).
10. Confirmar la litología normalizada de cada RT: ¿10 y 11 = Caliza? ¿13 y 14 = Hornfels? ¿16 y 19 = Mármol? ¿53 = ?
    También confirmar las siglas Lithology sin hipótesis: EXO, INT, IQM, IPP4, LMH, MCD, MCG, MGCB, HDV, NC, NG, NGR3, NGRD,
    NGRDW, NPL, XBV, XGRD, XGRDP, XGRDW, XGVDP, XWGCV, XWGV y XWGVC.
