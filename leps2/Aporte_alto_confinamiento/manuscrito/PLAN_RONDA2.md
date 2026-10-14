# Plan de corrección tras la segunda ronda de revisores (2026-10-06)

Decisiones del usuario:
- **Sitio:** se mantiene, rehecho y más anónimo, con consentimiento escrito antes del envío.
- **Estabilidad:** se rehace completa.

Estado: `[ ]` pendiente · `[x]` hecho · `[~]` parcial. Actualizado el 2026-10-06 (manuscrito `LepsP_IJGM_manuscript_r2`).

## 1. Modelo y validación
- [x] **MCMC:** 4 cadenas sobredispersas, previas half-normal(0.25) en las DE, uniforme en ρ; split-R̂ máx 1.009 y ESS mín 452 (forma x2). Forma potencia: 1.017 / 360, algo corta.
- [x] **Modo B:**
  - [x] métricas por rama con IC;
  - [x] sensibilidad del umbral (r 2–4, p 0.01–0.10): CRPS 0.029–0.031;
  - [x] línea base ingenua (m = 0.86 y 0.9) con IC pareado;
  - [x] validación específica de la rama conjunta (18 sets, 7 publicaciones).
- [x] **Fuga por la clase:** mezcla de clases, CRPS 0.0688 → 0.0840.
- [~] **Restricción de pendiente** solo en el rango calibrado; fracción conservada reportada (0.92 conjunta). Falta mostrar la sensibilidad sin restricción.
- [x] **Truncamiento de la base** (φ′1 < 31°) declarado.
- [ ] **Validación del procedimiento desplegado** (modo A con MCMC y restricción en una submuestra de pliegues) o declarar la diferencia.

## 2. Efecto de escala
- [x] Hartung–Knapp, intercepto por set y sensibilidad al criterio de similitud.
- [~] Dirección de ΔCu y Δe por grupo y meta-regresión (Δln Cu, angularidad). Falta el origen (aluvial o de voladura).
- [~] 19 grupos en la Fig. 5 con Goto anotado. Faltan en las referencias todas las publicaciones de la Fig. 5.
- [~] Tratado como exploratorio; Varadarajan et al. (2003) discutido. Falta la condición de baja rotura de Ovalle et al. (2014).

## 3. Sitio
- [x] Sets por separado con efecto de laboratorio común.
- [x] Hornfels en conflicto: discusión de densificación; para diseño se usa la previa.
- [x] Densidad de campo e = 0.55 y 0.65.
- [x] Caliza y marga separadas; degradación de la marga Δe = +0.15.
- [x] Sensibilidad de la clase del mármol: con clase buena el set queda en conflicto (p = 0.042); +2.1°/+1.6° en P50/P05 a 3 MPa.
- [~] **Anonimizar:** pesos ilustrativos y sin Dmax ni deformaciones en el texto. Falta depurar el repositorio (carpeta `analisis_antamina`, nombres de sets con laboratorio y años).
- [x] Ensayos del sitio en la Fig. 6.

## 4. Estabilidad y presión de poros
- [x] Capa basal desde x = 150 m sin aflorar; Su = r·σ′v efectivo coherente con u.
- [x] Malla de presiones de consolidación en Slide2 (lote 63, asignada solo a la capa basal; el lote 62 la aplicaba a todo el modelo y dio FS = 0 espurios).
- [x] Barrido FS frente a k y R; umbrales FS < 1.3 (P50) y < 1.0 (P05); Fig. 7 y Tabla 5.
- [~] Búsqueda SA sin restricción y mínimo con entrada en la plataforma (no drenado). Faltan varias semillas, `verificar_superficies.py` y la figura de geometría con superficies.
- [x] Monte Carlo con tres supuestos de correlación y Pf con cota 3/n.
- [x] Concordancia Python–Slide2 corregida (0.7 %).
- [x] Formato de diseño paso a paso.

## 5. Manuscrito
- [x] Sobreafirmaciones corregidas («conservative», efecto de publicación, escala compatible con Weibull, no drenado como sensibilidad).
- [x] Números leídos de archivos (incluida la fila de la previa del modo B en la Tabla 2).
- [x] Posicionamiento y aclaración de no afiliación.
- [x] Notación definida; sección Notation de ASCE.
- [x] Figuras de la ronda 2 en `figuras/lepsp2/` (Fig. 7 nueva: presión de poros). No enviar `figuras/lepsp/Fig07_fs_height`.
- [~] **Referencias:** Varadarajan, Marachi, Marsal (1973), Bandini y Coop, Coop, Phoon y Kulhawy, EN 1997-1, Hungr et al. (2002), Arrieta (versión). Faltan el año de Slide2 y el DOI del código.
- [x] Data Availability Statement con redacción de ASCE (repositorio y datos confidenciales).
- [x] Metadatos del docx limpios.
- [~] **Extensión:** 26 páginas de texto y tablas más 7 figuras; cerca del límite de 30.
- [ ] Autores, agradecimientos, declaración de uso de IA y consentimiento escrito del dueño de los datos.

## 6. Verificación
- [x] Pruebas de la librería (13/13), verificador de citas y búsqueda de términos identificatorios.
- [ ] Tercera ronda de revisores (en curso).
