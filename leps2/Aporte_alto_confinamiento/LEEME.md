# Aporte: resistencia del desmonte a grandes confinamientos (Leps 2.0 → Leps 3.0)

## Versión vigente: Leps-P, manuscrito en inglés para ASCE IJGM (2026-10-06)

**Manuscrito:** `manuscrito/LepsP_IJGM_manuscript.docx` y `.pdf`.
- Formato ASCE: doble espacio, numeración de líneas, ecuaciones OMML, leyendas de figuras al final y tablas tras las referencias.
- Extensión: 24 páginas más 6 figuras, total 30.
- Se genera con `manuscrito/build_lepsp_asce.py`. Las normas de ASCE están en `manuscrito/NORMAS_ASCE_IJGM.md`.

**Modelo:** 3 niveles (publicación → set → ensayo), σε(x) heterocedástica en la verosimilitud, REML propio y MCMC de los hiperparámetros.
- Código: `analisis/lepsp_modelo.py`, `lepsp_explorar.py`, `lepsp_final.py`, `lepsp_cv.py` y `lepsp_cv_metricas.py`.
- Efecto de escala dentro de materiales: `lepsp_escala.py`.

**Implementación de referencia:** `leps3/lepsp.py`, con 12 pruebas aprobadas y los parámetros en `lepsp_parametros.json`.
- Regla de actualización: se actualizan θ y m solo si la razón de σ′n es ≥ 3 y la prueba de conflicto da p ≥ 0.05; en otro caso se actualiza solo el nivel, con pivote en x̄.

**Sitio:** `analisis_antamina/a5_lepsp_sitio.py`. Estabilidad: `analisis/lepsp_estabilidad.py` y `consol_frente.py`.
- Lotes de Slide2: 60 (seis grupos) y 61 (base no drenada con límites de mecanismo global).
- Generador: `slide2/generar_yaml_lepsp.py`.

**Figuras:** `figuras/lepsp/`, generadas con `analisis/figuras_lepsp.py`.

**Literatura:** `literatura/MATRIZ_LITERATURA.md` (21 PDF leídos, en `literatura/pdf/`).

**Resultados clave:**

| Tema | Resultado |
|---|---|
| Modo A, sin ensayos | Cobertura del 83 %; CRPS igual al de la referencia; intervalos conservadores sobre 2.75 MPa |
| Modo B, con la regla | CRPS de 0.041 a 0.031; IC de la diferencia [+0.005, +0.016] |
| Varianza de θ entre materiales | 37 % explicada por laboratorios |
| Efecto de escala | Gradación paralela: κ = 0.24 ± 0.09. En general el signo cambia con la gradación |
| FS, 700 m, fundación horizontal | 1.65 (P50); 1.50 (P05); 1.28 con la litología más débil |
| FS, ladera de 10°, base con ru = 0.2 | 1.39 |
| FS, base no drenada | 0.65 con Su = 0.17σ′v; 0.39 con resistencia licuada |
| Frente de volteo (150 m en 3 meses) | Δu/σv = 0.11 con k = 1e-7 (capa de 30 m) |

**Pendientes:**
- Autores.
- DOI del repositorio.
- Año de la versión de Slide2.
- Autorización del propietario de los datos.
- Segunda ronda de revisores en curso.

## Versión anterior: Leps 3.0 probabilístico en español (2026-10-06, reemplazada)

Leps 3.0 es un criterio probabilístico: un modelo jerárquico en log–log donde φ′1 y m son aleatorios por material. No critica Leps 2.0; su mediana reproduce la tabla de Leps 2.0. El sitio está anonimizado como «un yacimiento de skarn polimetálico en los Andes».

- **Manuscrito:** `manuscrito/Manuscrito_Leps3_probabilistico.docx` y `.pdf` (16 p.). Se genera con `construir_leps3_prob.py`, que lee todos los números de `analisis/resumen_manuscrito.json`, `analisis/ejemplo_leps3.json` y los CSV de `analisis_antamina/`.
  - Verificaciones: citas 39/18 sin faltantes; risk words solo con las excepciones acordadas («ley de potencia», «Palabras clave»); ninguna mención a Antamina, LE2 ni a los consultores.
  - Paginación: 11 avisos, todos falsos positivos o no aplicables. Las «Fuente» de figuras están bajo su imagen, que el verificador no ve, y la regla de capítulos en hoja nueva es para informes, no para un artículo.
- **Implementación de referencia:** `leps3/leps3.py` con API probabilística: `previa`, `actualizar`, `muestras` (m ≤ 1 truncado exacto), `percentiles` y `tabla_slide2`. Tiene 9 pruebas en `test_leps3.py`, todas aprobadas.
- **Calibración y figuras:**
  - `analisis/prob_cv.py`: LOPO, modos A y B. Escribe `leps3_prob_parametros.json`.
  - `analisis/figuras_leps3_prob.py`: figuras P0 a P3.
  - `analisis/resumen_manuscrito.py`: números del manuscrito.
  - `analisis/ejemplo_leps3.py`: FS del botadero de 700 m por percentil.
- **Resultados clave:**
  - **Modo A, sin ensayos:** cobertura del intervalo de 80 % de 81 %, con 11 % bajo el P10, en 767 ensayos.
  - **Modo B, con ensayos del sitio:** en los mismos 64 ensayos, el ancho del intervalo baja de 0.26 a 0.14 en ln τ. La cobertura pasa de 94 % a 77 % y la fracción bajo el P10 de 3 % a 8 %. El CRPS es igual (0.043), así que se gana precisión, no exactitud de la mediana.
  - **Varianza:** el 92 % es entre materiales.
  - **FS del botadero de 700 m (Bishop):**

    | Material | P50 | P10 de la envolvente media | P10 puntual |
    |---|---|---|---|
    | Genérico | 1.71 | 1.51 | 1.50 |
    | Skarn | 1.65 | 1.53 (promedio entre litologías) | 1.37 |
- **Correcciones de esta etapa:**
  - `a4_envolventes.py` y la figura A3 no aplicaban m ≤ 1. Se corrigió: hasta 0.4° en el botadero y 1.5° en el P50 del hornfels a 15 MPa.
  - La comparación de los modos A y B usaba conjuntos de ensayos distintos. Ahora usa los mismos 64.
  - `figuras.py` (fig. 1 a 6 del manuscrito anterior) usa la API determinística antigua y ya no corre. Sus figuras se conservan solo por trazabilidad.
- El manuscrito determinístico anterior (`Manuscrito_Leps3.docx`, m = 0.87) queda reemplazado. Contenía la errata de la Ec. 23 y la crítica a m = 0.9, que se dejaron fuera por decisión del usuario.
- **Análisis de Leps 3.0** (todos con LOPO = dejando fuera una publicación):
  - `verificar_ecuaciones.py` y `ec23_error.py`: errata de la Ec. 23.
  - `leps3_cv.py` y `leps3_formas.py`: formas con piso y comparación (descartadas).
  - `leps3_mvariable.py`: m dependiente de φ′1 (descartado).
  - `leps3_final.py`: modo A y bandas de diseño.
  - `leps3_bayes.py`: previa de m y actualización.
  - `ejemplo_leps3.py`: botadero de 700 m.
- **Slide2:** el lote 52 verifica la envolvente de diseño. Bishop en Slide2 frente a Python: 1.507 frente a 1.515 y 1.353 frente a 1.359.
- **Pendientes:**
  - autores;
  - repositorio público del código (resaltado en el manuscrito);
  - traducción;
  - revista.
- Lo que sigue más abajo describe la etapa anterior (artículo corto con m = 0.87); se conserva por trazabilidad.

Uso interno. Resume qué hay en esta carpeta, los resultados, los controles hechos y lo pendiente.

## Hallazgos

1. **Cobertura.** La base de Cylwik et al. (2025) llega a σ′3 = 4.48 MPa (σ′n = 7.9 MPa). Solo 9.6 % de los ensayos supera σ′n = 3 MPa. La base de un botadero de 700 m tiene σv ≈ 14.7 MPa.
2. **Sesgo de m = 0.9.** Si se calibra φ′1 con σ′n ≤ 1.5 MPa y se extrapola a σ′n ≥ 2 MPa, τ se sobreestima +4.9 % en promedio y en 81 % de los ensayos (47 sets, 67 ensayos, 13 publicaciones).
3. **Exponente sin sesgo.** m* = 0.866, con IC 90 % de 0.856–0.875 (bootstrap por set). Dejando fuera una publicación a la vez se elige 0.86–0.87 y el sesgo queda en −0.7 %. Sobre 3 MPa, m* = 0.886: la envolvente se aplana.
4. **Rotura y volumen.** La mediana de Bg es 5.7 % a 0.1–0.3 MPa, 24 % a 1–2 MPa y 36 % a 2–4 MPa. Los 347 ensayos con εvol son contractivos netos en la falla.
5. **Botadero genérico de 700 m.**
   - Las superficies críticas drenadas tienen σ′n de 3–6 MPa.
   - Pasar de m = 0.9 a 0.87 reduce el FS en 2–4 %.
   - Con la base no drenada (Su = 0.28 σ′v0) el FS es 0.97.
   - La consolidación solo genera exceso de presión de poros relevante si k ≤ 10⁻⁹ m/s en una capa saturada de 30 m.

## Correcciones durante el trabajo (para trazabilidad)

- **Corrección por alta presión.** Primero se propuso una caída lineal de φ′1 en log(σn), de −3.7°/década. La validación cruzada mostró que sobrecorrige sobre 3 MPa (sesgo −5.2 %), así que se reemplazó por m = 0.87.
- **Mecanismo basal.** Se había supuesto que era crítico en seco. Slide2 (búsqueda no circular SA) encontró una superficie casi circular con FS menor; el mecanismo basal solo domina con agua en la base.
- **Clave de set.** Los códigos de set "A" y "C" se repetían entre publicaciones. La clave es ahora publicación + set; los resultados no cambiaron.

## Controles

| Control | Resultado |
|---|---|
| Bishop en Python frente a talud infinito | 1.566 frente a 1.562 |
| Bishop en Python frente a Slide2 9.043 (6 casos) | \|Δ\| ≤ 0.007 |
| Consolidación numérica frente a solución estacionaria | 147 frente a 147 kPa |
| Conversión (σn, τ) de la base | No lineal en el 97 % de los ensayos, como indica Cylwik et al. (2025) |
| DOI de las referencias | Verificados en Crossref y DataCite (`manuscrito/dois_crossref.json`) |
| `verificar_citas.py` | 39 citas, 19 referencias, 0 errores |
| `riskwords.py` | Quedan 6 avisos: «validación cruzada» (5), término estadístico, y «Palabras clave», sección de la revista. Se mantienen a propósito |
| `verificar_paginacion.py` | 6 avisos. Tres son «capítulo en hoja nueva», que no aplica a un manuscrito corrido. Tres son «Fuente» al inicio de página, que queda bajo su figura (el verificador no ve imágenes). Revisión visual sin defectos |

## Pendientes

- Autores y afiliaciones (resaltado en amarillo en el manuscrito).
- Elegir revista, ajustar el formato y traducir al inglés (Géotechnique Letters o Canadian Geotechnical Journal, nota técnica).
- Ensayos que pide el resultado:
  - triaxiales CID con σ′3 de 2–4 MPa sobre las litologías del proyecto;
  - triaxiales CIU a alta presión con la granulometría triturada;
  - permeabilidad después de la rotura.
- No analizado: la acción sísmica y el efecto de la UCS (la muestra es insuficiente).
- `figuras/fig2_caida_phi1.png` es una versión anterior que no usa el manuscrito. Se puede borrar.

## Estructura

- `analisis/`: scripts y salidas.
  - `common.py` carga la base.
  - `analysis1.py`, `analysis2.py`, `robustez.py` y `m_extrapolacion.py`: estadística.
  - `slope.py` (Bishop) y `wedge.py` (Janbu, mecanismo basal): estabilidad.
  - `consol.py`: consolidación.
  - `figuras.py`: figuras.
- `slide2/`: modelo de verificación (`generar_yaml.py` → `.yaml` → `.slmd`) y `resultados_Slide2/` (lotes 50 y 51 del banco).
- `figuras/`: figuras del manuscrito.
- `manuscrito/`: `construir_manuscrito.py` genera el docx; `exportar_pdf.py` genera el PDF con Word.
