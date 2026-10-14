# Esquema de extracción de ensayos (común a todos los informes)

Un archivo CSV por informe, en UTF-8 con coma como separador y punto decimal. **Una fila por probeta ensayada**: por ejemplo, un triaxial a un σ3 dado, o un corte directo a un σn dado. Si un dato no aparece en el informe, la celda queda vacía; nunca se supone.

| Columna | Contenido |
|---|---|
| fuente | Nombre del archivo PDF |
| anio | Año del informe |
| autor_informe | Empresa o laboratorio (Golder, WSP, IDIEM, Stantec…) y código del informe si existe |
| laboratorio | Laboratorio que ejecutó el ensayo |
| set_id | Identificador del material o serie (misma granulometría, densidad y litología, a distintos σ3) |
| ensayo_id | Identificador de la probeta tal como aparece en el informe |
| litologia_informe | Litología tal como la nombra el informe (sin cambios) |
| litologia | Litología normalizada: **Intrusivo**, **Hornfels**, **Mármol**, **Skarn**, **Caliza** u **Otra** (indicar cuál). Si el informe distingue subtipos, se conservan en `litologia_detalle`. Si es una mezcla, se escribe «Mezcla» y se usa `litologia_proporcion` |
| litologia_detalle | Subtipo, si se indica: mármol blanco, mármol negro, endoskarn, exoskarn, monzonita cuarcífera, pórfido, hornfels calcáreo, etc. |
| litologia_proporcion | En mezclas: proporciones por litología (p. ej. «Mármol 50 %; Hornfels 50 %») |
| alteracion | Alteración o grado de meteorización, si se indica |
| tipo_material | Clase de desmonte de Antamina: **ROM** (run of mine, transportado en camiones), **Chancado** (para faja transportadora) o **Enrocado** (seleccionado para presa). En mezclas con relave: «Mezcla co-disposición: <clase> + X % relave» |
| clase_desmonte | Clasificación de desmonte de Antamina si aparece (A, B, C u otra) |
| tipo_ensayo | CID, CIU, CU, CD, UU, corte directo, edómetro, etc. |
| saturado | sí / no / no indicado |
| diametro_mm | Diámetro de la probeta |
| altura_mm | Altura de la probeta |
| Dmax_mm | Tamaño máximo de partícula ensayado |
| D10_mm, D30_mm, D50_mm, D60_mm | Diámetros característicos antes del ensayo |
| Cu, Cc | Coeficientes de uniformidad y curvatura |
| grava_pct, arena_pct, finos_pct | Porcentajes antes del ensayo |
| escalamiento | Paralelo, truncado (scalping) o ninguno, y Dmax de terreno si se indica |
| Gs | Gravedad específica |
| gamma_d_kNm3 | Peso unitario seco de la probeta (convertir desde g/cm³ o t/m³: × 9.81) |
| e0 | Relación de vacíos inicial. Si no viene, calcular e0 = Gs·γw/γd − 1 y anotarlo en `e0_origen` |
| e0_origen | «informe» o «calculado» |
| Dr_pct | Densidad relativa, si se indica |
| w_pct | Humedad |
| UCS_MPa | Resistencia a la compresión uniaxial de la roca, si se indica (o carga puntual, en `notas`) |
| sigma3_kPa | Presión de confinamiento efectiva |
| sigma1_kPa | σ′1 en la falla |
| q_kPa | Desviador en la falla (σ1 − σ3) |
| criterio_falla | Peak, máximo desviador, deformación límite (p. ej. 15 %), etc. |
| phi_sec_deg | Ángulo secante informado para esa probeta, si existe |
| eps_axial_falla_pct | Deformación axial en la falla |
| eps_vol_falla_pct | Deformación volumétrica en la falla, **con la convención del informe** (indicarla en `notas`) |
| u_falla_kPa | Presión de poros en la falla (no drenados) |
| p_falla_kPa, q_falla_und_kPa | Trayectoria no drenada: p′ y q en la falla o en estado estable |
| Su_kPa | Resistencia no drenada, si se informa |
| Bg_pct | Índice de rotura de Marsal |
| Br | Índice de rotura de Hardin u otro (indicar cuál en `notas`) |
| finos_post_pct | Finos después del ensayo, si se informan |
| sigma_n_kPa, tau_kPa | Solo para corte directo |
| pagina | Página del PDF de donde salió cada dato principal (σ3, σ1/q y granulometría; varias separadas por «;») |
| verificado_imagen | sí / no: si el valor se comprobó en la imagen de la página |
| notas | Lo que haga falta para interpretar la fila |

Además de los ensayos, cada informe debe tener un archivo `<informe>_resumen.md` con:

- objetivo del informe y materiales;
- envolventes ajustadas por el propio informe (c, φ, Leps, potencia…) con su página;
- ensayos índice (UCS, Los Ángeles, durabilidad), granulometrías de terreno y de ensayo, permeabilidad, edómetros, ensayos no drenados;
- dudas y datos ilegibles.
