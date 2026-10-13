# Ronda 6: seis revisores independientes e insesgados (2026-10-07)

Revisores: estadística (E), geomecánica (G), confiabilidad y estabilidad (R), práctica de botaderos (P), auditoría de datos (D), editor asociado (N).
Ninguno leyó planes ni revisiones anteriores; todos leyeron el manuscrito completo y verificaron contra datos y código.
Veredictos: 5 revisión mayor, 1 menor-moderada (auditoría). Los números se reproducen: conteos, Tablas 1–3, S1, ΔML, metaanálisis, varianza, FS y MC.

## Brechas consolidadas (sin duplicados)

### A. Integridad de datos y validación (cerrar ahora; cambia todos los números → una sola cascada)
| ID | Brecha | Revisores | Cierre |
|---|---|---|---|
| A1 | 16 puntos digitalizados de curvas (σ′3 vacío) y duplicados (Ho-dd/ee, 19D, UC13, recycled) | D3, E10 | Exigir σ′3 informado, quitar duplicados (≈741/220/36) y relanzar perfil, MCMC y cv4 |
| A2 | La unidad independiente es el laboratorio, no la publicación (36 → 23 laboratorios; >3 MPa: 8 → 5) | D1, E2 | LOPO por laboratorio, sign-flip por laboratorio, metaanálisis por laboratorio |
| A3 | El umbral de 2.75 MPa decide la significancia (>2 MPa: Leps 2.0 mejor en P10, Holm ≈ 0.01) | D2 | Banda ≥ 2 MPa como en el Modo B; informar 2/2.75/3 MPa en el suplemento |
| A4 | La Tabla 2 omite la forma de potencia (ya evaluada: la acotada es mejor sobre 2.75 MPa en 7 de 9 publicaciones) y Leps 2.0 mezcla envolvente y dispersión | D4 | Filas: potencia, y Leps 2.0 reajustado por pliegue con dispersión jerárquica |
| A5 | Sign-flip pondera igual publicaciones de 1 y 69 ensayos; falta el efecto mínimo detectable | E12, D7 | Sign-flip ponderado; coberturas con IC por clúster |

### B. Forma del modelo y física (decisión del autor; cambia el titular)
| ID | Brecha | Revisores | Cierre |
|---|---|---|---|
| B1 | ΔML = 9.7 confunde media, covarianza y aproximación FO; no prueba la curvatura | E1, N1 | Laplace/AGHQ o NUTS; ajustes cruzados (media acotada con efectos aditivos y viceversa); log score conjunto LOPO |
| B2 | Máximo desviador censurado por deformación (71 % sobre 5 MPa con εa ≥ 15 %; 29 % en el límite del equipo) | G2 | Verosimilitud censurada (Tobit) para εa ≥ 19 % o máximo en el último punto; re-perfilar φ′∞ |
| B3 | Asíntota 24° por debajo de los ángulos de estado crítico plausibles; la Fig. 3b llega a 20 MPa | G1, N3 | Prior o piso en φ′∞ (≈ 33°) como sensibilidad; cortar figuras a 8 MPa; cota inferior tangente para modelos numéricos |
| B4 | La clase «low» mezcla forma, origen y resistencia (UCS 200 MPa, gravas redondeadas) y decae menos | G3 | ζ0 por clase; covariables de angularidad/origen, ln UCS y ln Cu×x; LOPO en el subconjunto angular volado |
| B5 | Mala calibración a σ alta (z̄ +0.21; p de conflicto acumulados cerca de 1, KS p = 0.04); época confundida con tensión | E5 | Chequeo predictivo de pendientes por banda; perfil omitiendo las publicaciones dominantes a σ alta |
| B6 | El efecto de e que se desvanece con la tensión no está identificado (lo impone la forma) | G5 | Variante con efecto de e persistente en las Tablas 3 y 4 |

### C. Colas y valores de diseño (cerrar ahora; riesgo no conservador)
| ID | Brecha | Revisores | Cierre |
|---|---|---|---|
| C1 | Cola truncada en φ′1 ≥ 31°: el P05 de diseño (31.1°) cae en el truncamiento | N4, G4, E7 | Verosimilitud truncada en η; nota en la Tabla 3 cuando P05 < 33° |
| C2 | La cantidad de diseño (P05 de la envolvente media) no se valida; el «recomendado» deja 9.4 % bajo P05 | E3 | Validación a nivel de set: excedencia de P05, PIT, pinball en P05 |
| C3 | Tres procedimientos distintos según la sección; «Recommended» puntúa peor | N2, D5, E4, P8 | Un único procedimiento en resumen, Design Format, Tabla 2, Fig. 2b y aplicación; regla asimétrica: no descartar sets más débiles |
| C4 | Con 1–3 ensayos la envolvente actualizada es la de la muestra, no la del tipo de roca (+8° con un ensayo favorable) | P1 | Valor característico = set nuevo del mismo laboratorio (reponer G_s); exigir ≥ 2 sets por tipo |
| C5 | Chequeo de conflicto: tamaño 9 % frente a 5 %, potencia baja, sin Holm en el sitio (con Holm, C no queda marcado) | E6 | Distribución LOPO de p, curva de potencia, Holm entre sets de un sitio; la clase no se elige por el chequeo |
| C6 | 83 % de cobertura del Modo B es optimista (selección entre 7 procedimientos) | E4, D6 | Calibración del update por simulación; IC por publicación/laboratorio |

### D. Efecto de escala
| ID | Brecha | Revisores | Cierre |
|---|---|---|---|
| D1s | Doble conteo: Dmax no está en el modelo y G_s ya absorbe la variación de tamaño; razón real ≈ 26, no 5.6 | E2 | ln Dmax como covariable con pendiente aleatoria; recalcular la descomposición (cambia «52–62 %») |
| D2s | Técnica de escalamiento (escalpado/paralela) no codificada; efecto dependiente de la tensión (ln D×x < 0) | G7, N5 | Codificar la técnica en los 16 materiales; meta-regresión β_D + β_Dx·x; sensibilidad Weibull β_D = −0.05 |
| D3s | «Conservative given the positive estimate» no se sostiene (por material o laboratorio el IC incluye 0) | G7, E2, D1 | Retirar la frase; Conclusión 4 coherente con +0.041 (IC −0.001 a +0.084) |

### E. Estabilidad y confiabilidad
| ID | Brecha | Revisores | Cierre |
|---|---|---|---|
| E1s | β = 3.3 condicionado a τ_D puntual (β de 2.0 a 4.4 en el IC; integrado ≈ 2.8) | R1 | Pf y β integradas sobre τ_D; curva β(τ_D); colas t |
| E2s | «P05 del FS = FS del P05» es tautológico con un material (ln FS lineal, r = 0.999) | R2 | Reformular; usar el sustituto como método y los 600 Slide2 como verificación |
| E3s | El ejemplo no prueba la contribución: fundación con c = 1 MPa limita σ′n a unos 2 MPa | R3 | Slide2: capa débil, fundación inclinada, zona basal, con acotada/cuadrática/Leps 2.0/extremos de φ′∞ (≈ 60 escenarios) |
| E4s | Fundación no declarada; sin agua; e y γ constantes con la profundidad | R4, R6, G11, P6 | Declarar; freático basal; perfil e(z) y γ(z) |
| E5s | Promediado espacial y zonificación no tratados | R5, R7, P10 | Separar sistemático/espacial (Vanmarcke); botadero por fases |
| E6s | «Doble conteo» de EC7 depende de la β objetivo; 0.6 % es bilateral (unilateral 0.50 %) | R8, E12 | Relación β–FS_car–γ_M frente a EN 1990 y criterios mineros |
| E7s | Funciones tabuladas hasta 14.7 MPa pese a «no usar sobre 8 MPa»; φ′s 47° a 0.05 MPa | R10, P3, P4 | Truncar a 8 MPa; tope por ángulo de reposo bajo 0.1 MPa |

### F. Usabilidad para el diseñador
| ID | Brecha | Revisores | Cierre |
|---|---|---|---|
| F1 | Orden de operaciones no protegido (≈ 9° inseguro si se invierte) | P2 | Función única `envolvente_diseno(...)`; diagrama de flujo; fijar *m* de conversión |
| F2 | El código contradice el dominio (16 MPa, avisos apagados, `puntual=True`) | P3 | `sn_max = 8` con error; chequeo (e, σ′n); `puntual=False` |
| F3 | Clase de calidad, e de colocación y D_f no operativizados | P5, P6, P7 | Tabla de criterios de clase; guía de e por método; D_f = Dmax del 90–95 % de la masa |
| F4 | Sin guía de cuántos ensayos ni a qué σ′3 | P9 | ≥ 3 ensayos por set, ≥ 2 sets por tipo; σ′3 ≈ 0.55–0.6 σ′n de diseño |
| F5 | Hoja de cálculo imposible sin C_β, G_p, G_s; falta ejemplo trabajado | P14, N | Publicar matrices; ejemplo de principio a fin en el suplemento; planilla verificada |
| F6 | Sin comparación con Leps 1970, Leps 2.0 y Barton–Kjærnsli | P13 | Tabla 3 casos × 3 métodos |
| F7 | Paquete sin README, requirements ni DOI; nombres en español; φ′cs en docstrings | P16 | API en inglés o alias, README, versión con DOI (Zenodo) |

### G. Editorial y ASCE
| ID | Brecha | Revisores | Cierre |
|---|---|---|---|
| G1e | Título de 104 caracteres (máximo 100) y encuadre que sobreafirma | N1 | Título nuevo; la curvatura como extrapolación acotada, no como mejora de exactitud |
| G2e | Dominio de validez inconsistente entre resumen, PA, Tabla 3 y figuras | N3, D8 | Una sola frase, repetida igual |
| G3e | Literatura faltante: Bozorgzadeh et al. 2019; Ching & Phoon 2020; Ovalle & Dano 2020; Girumugisha et al. 2026; Ventini et al. 2021; Xiao et al. 2014 I-II; Indraratna et al. 1993; Bard et al. 2011 | N8 | DOI verificados en Crossref por el editor |
| G4e | Resumen con símbolos matemáticos; `\hline\hline`; leyenda de la Fig. 3b (E con e = 0.80); Fig. 1; figuras en TIFF/PDF | N10 | Corregir |
| G5e | Placeholders: afiliación, DOI del repositorio, agradecimientos, declaración de IA, año de Slide2 | N10 | Pendientes del autor |
| G6e | Espacio: 30 páginas exactas | N | Quitar Notation (opcional en ASCE, ≈ −1.5 p.), mover detalles al suplemento |

### H. Solo con ensayos nuevos (protocolo en la Discusión)
σ′3 de 5–10 MPa con e > 0.55 hasta εa de 25 % con εv local; un mismo material a dos tamaños con gradación paralela documentada; densidad in situ a gran escala y compresión 1D hasta 12 MPa; durabilidad (slake, Los Ángeles, húmedo–seco) y triaxiales saturados del material degradado; validación externa con publicaciones posteriores a la base.

## Notas propias
- D8 dice que p = 0.17 debería ser 0.18: 0.17 viene del ajuste conjunto del sitio (`lepsp_sitio3.json`, 0.1712) y 0.18 de la tabla de diseño (0.1797). Se usa el primero a propósito; aclararlo en el texto.
- G (geomecánica) se corrigió a sí mismo sobre e×x: con pendiente aleatoria el desvanecimiento del efecto de e no está identificado.

## Estado al pausar (2026-10-07, a pedido del usuario: batería baja)

Hecho:
- Módulo `analisis/lepsp_r6.py`: datos depurados (741 ensayos, 220 sets, 36 publicaciones, 23 laboratorios; 55 censurados con εa ≥ 19 %), modelo con ln Dmax, ζ por clase, truncamiento y censura; `ll_obs` (verosimilitud de los datos observados).
- Diagnóstico en (25°, 0.30): lnD +2.5 (β_D = +0.019); ζ por clase +2.0 (2 parámetros, débil); truncamiento casi nulo; censura cambia el nivel.
- Metaanálisis de escala por laboratorio (`lepsp_escala6.py/json`): β_D = +0.028 (IC −0.034 a +0.089), τ_D = 0.064 (0.039–0.140), predicción −0.15 a +0.20; β_Dx = −0.010 (no significativo).
- Biblioteca `leps3/`: `envolvente_diseno`, dominio aplicado, avisos, README, 30 pruebas; soporte de lnD y ζ por clase; `residuo_medio` en el diagnóstico.
- Scripts listos sin correr: `lepsp_mcmc6.py`, `lepsp_publicar6.py`, `analisis_antamina/a8_lepsp_sitio6.py`, `lepsp6_envolventes_alto.py`, `lepsp_tabla_diseno.py` (D = 100 mm y campo), `slide2/generar_yaml_lepsp6.py` (alto confinamiento; geometrías verificadas en alto6_prueba) y `generar_yaml_lepsp6det.py`.

Perfil r6 (`lepsp_perfil6_{b,c,d,e}.json`; ll_obs): 5° 783.92 · 10° 786.00 · 14° 788.04 · 17° 789.84 · 18° 790.50 · 19° 791.19 · 21° 792.65 · 22° 793.42 · 23° 794.19 · 25° 795.72 · 26° 796.42 · 27° 797.00 · 28° 797.40 · 29° 797.48 · 30° 797.06 · 31° 795.83 · 34° 781.07 · 36° 748.27. Máximo ≈ 28–29° (r5: 25°).
Faltan: 0° (se atascó > 1 h en la parte «a»), 16°, 20°, 24°, 32°.

Para retomar:
1. Perfil: `python lepsp_perfil6.py f 16,20,24,32` y 0° aparte (revisar por qué se atasca); luego `python lepsp_perfil6.py unir`.
2. `lepsp_mcmc6.py` → `lepsp_escala6.py` → `lepsp_publicar6.py` → pytest en leps3.
3. Sitio: `a8_lepsp_sitio6.py` (base, --x2, --muestra, --lab-indep, --bD-indep, --weibull); `lepsp_tabla_diseno.py`; `lepsp6_envolventes_alto.py`.
4. Validación por laboratorio: relanzar `lepsp_cv6.py k K` desde cero (pliegues completados: 3 de 23; ~20 min por pliegue; máx. 3–4 procesos: la laptop tiene 7.7 GB de RAM) y luego `unir`; métricas (falta escribir `lepsp_cv6_metricas.py`).
5. Estudio E1 (`lepsp_e1_estructura.py`, escrito por un agente; se detuvo sin informe): revisar y correr.
6. Slide2: det6 + mc6 + alto6; varianza, Pf integrada sobre τ_D (sustituto lineal), figuras, manuscrito, suplemento, verificación.

## Avance al retomar (2026-10-07, tarde)

- Slide2: lote 69 (det6, 12 modelos, 90 escenarios) completo y «ok»; 70 (alto6) subiendo; 71 (mc6) corriendo en la laptop.
- `analisis/lepsp_estabilidad6.py` listo (det, conv, alto con claves por modelo —las claves de alto6 se repetían entre debil25/30 e inc10/20—,
  σ′n movilizada con u bajo el freático en agua100, MC con Clopper–Pearson y cota unilateral, sustituto ln FS–ln τ y Pf integrada sobre τ_D).
  `lepsp_estabilidad6.json` actual es PROVISIONAL (det real; alto y MC ficticios): regenerarlo con
  `python lepsp_estabilidad6.py 69-lepsp6-det 70-lepsp6-alto 71-lepsp6-mc`.
- Hallazgo del Modo B por laboratorio: la actualización de nivel deja 14 % bajo el P05 (sesgo de un laboratorio, z̄ = −1.04);
  regla nueva: sobre la σ′n máxima de los ensayos del sitio, el menor entre el percentil actualizado y el de la previa (4 % bajo P05).
  Implementada en `leps3/lepsp.py` (`envolvente_diseno`, paso 6; además pasa D_lab a la previa); 21 pruebas pasan.
- Ejemplo trabajado (`analisis/lepsp_ejemplo6.py`): plug-in y biblioteca coinciden a ≤ 0.1° (P05 de diseño a 1 MPa: 30.6°).
- Manuscrito r6 (`build_lepsp_asce6.py`): reescrito; 30 páginas, 0 problemas de compilación; Tabla 4 de r5 → Tabla S6.
  Resumen 236 palabras sin símbolos. Figs. 1 y 3 cortadas a 8 MPa. Notación sin consumir número de tabla.
- Suplemento r6 (`build_suplemento6.py`, solo LaTeX): Figs. S1–S5, Tablas S1–S6, ejemplo trabajado con matrices publicadas.
- Pendiente: resultados reales de 70/71 → regenerar JSON, revisar frases del resumen y de la sección de alto confinamiento
  contra los números, recompilar (vigilar 30 páginas), revisión visual final, memoria.
- 2026-10-07: el modelo se renombra **HiBER** (antes Leps-P) por decisión del usuario; título de 79 caracteres.
- 2026-10-07 (noche): lotes 70 (alto), 71 (MC, 48/48 ok) y 72 (bloques, 7/7 ok) incorporados; `lepsp_estabilidad6.json` ya es real
  (sin marca PROVISIONAL) y `analisis/lepsp_bloques6.json` guarda el lote 72. Hallazgo: la forma de la envolvente cambia el FS ≤ 0.04
  en todos los mecanismos secos; capas de 15–20° gobiernan por su propia resistencia (FS P05 1.05–1.15; desmonte ≤ 3.3 MPa); el
  freático que aflora en la cara da falla superficial (FS 0.65). Resumen, aplicaciones, discusión y conclusiones corregidos.
  MC: 0/600 fallas (β_LN 3.2); Pf por sustituto 1.1e-3 (β 3.1), integrada sobre τ_D 4.6e-3 (β 2.6). Manuscrito 30 páginas,
  resumen 245 palabras, 0 problemas; suplemento 8 páginas.
