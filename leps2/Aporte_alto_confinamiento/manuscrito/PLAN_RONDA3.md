# Tercera ronda de revisores (2026-10-06): síntesis y plan

## Estado al 2026-10-07
**Decisiones del usuario:**
- envolvente acotada como modelo central si ganaba fuera de muestra;
- presión de poros en un artículo complementario;
- anonimización genérica (tipos de roca A–E, «mina a cielo abierto alojada en carbonatos»).

**Hecho, con resultados en archivos:**
- **Forma acotada** (`analisis/lepsp_acotada*.py`, `lepsp_mcmc3.py`, `lepsp_cv3*.py`).
  - Cresta (φ′cs, ζ) promediada.
  - LR frente a la ley de potencia sin piso: p ≈ 10⁻⁴.
  - Modo A frente a la cuadrática: significativo (Wilcoxon p = 0.039).
  - Prueba de forma: 10/13 publicaciones, p = 0.027.
  - Modo B preregistrado: la regla de solo nivel supera al ajuste ingenuo con m del entrenamiento (p = 0.040).
- **MCMC:** R̂ normalizado por rangos, ESS bulk y de colas, cadenas más largas en potencia y sensibilidad a las previas.
- **Escala** (`lepsp_escala3.py`): con R ≥ 2, ajuste por e, varianza entre sets y agrupamiento por publicación, el efecto es nulo. Para diseño se usa media cero; el supuesto «paralela» se elimina.
- **Grilla de la mezcla de clases corregida:** CRPS 0.0852.
- **Librería** `leps3/lepsp.py`:
  - forma acotada por defecto y función `densidad()`;
  - actualización descrita como «de corte»;
  - 15 de 15 pruebas pasan.
- **Sitio** (`a8_lepsp_sitio.py`): forma acotada; sensibilidad con la forma x2.
- **Curvas tensión–deformación del sitio** (`curvas_sitio/`) y sensibilidad al criterio de falla (`a7`): el hornfels mantiene m > 1 con todos los criterios.
- **Descomposición de varianza** (`lepsp_varianza.py`): la escala aporta 35–48 % y la asíntota ≤ 4 %.
- **Tabla de diseño** por clase, e y σ′n (`lepsp_tabla_diseno.py`).
- **Diagnóstico de clase de la litología A:** p = 0.16 (baja), 0.11 (moderada), 0.025 (buena).
- **Estabilidad** (`lepsp_estabilidad3.py`): γ coherente con e, nueva búsqueda en Monte Carlo cuando FS < 1.3 e IC de Clopper–Pearson.
- **Manuscrito:** `build_lepsp_asce3.py`, sin la sección de presión de poros.
- **Figuras:** `figuras_lepsp3.py`; el efecto de escala queda en material suplementario (Fig. S1).

**Pendiente:**
- validación de la predictiva desplegada (mezcla MCMC frente a la aproximación plug-in);
- tabla S1 del material suplementario;
- depurar el repositorio de nombres identificatorios;
- datos del usuario: autores, año de Slide2 (ya no se cita), DOI del código, agradecimientos y consentimiento;
- cuarta ronda de revisores.

Los cinco revisores recomiendan **revisión mayor**. Ninguno recomienda rechazo. Los números que revisaron contra los archivos coinciden, salvo dos errores de reporte (§1).

## 1. Errores propios que se corrigen sí o sí
- La diferencia «+0.0058 (−0.0016 a +0.0190)» compara m = 0.86 contra la **regla mixta**, no contra la actualización de solo nivel (0.0363 − 0.0298 = 0.0065). [R2]
- En la prueba de 18 sets, el ajuste con m = 0.86 fue el mejor (0.0359 frente a 0.0372 de solo nivel), y se omitió. [R1, R2]
- «Conservative intervals» sobre 2.75 MPa es falso. El PIT [0.04, 0.09, 0.23, 0.42, 0.22] muestra la mediana **sesgada hacia abajo**; la pérdida al 10 % es peor que la referencia, y su CRPS es 0.0468 frente a 0.0446 de Leps 2.0. [R1, R2]
- Las proporciones de varianza 38 % y 61 % son cocientes de medianas; sus intervalos son 23–55 % y 43–79 %. «Most of the curvature» no se sostiene. [R2]
- El efecto de escala «compatible con Weibull» depende de un solo criterio de similitud, y 3 materiales tienen razón de tamaños < 2. Sale de las conclusiones y del resumen. [R1, R2, R4]
- La CRPS de la mezcla se calculó en una grilla truncada: 0.0840 pasa a 0.0852. [R2]
- La restricción de pendiente de `previa`/`actualizar` trunca hasta 20 MPa, no hasta 7.9. [R2]
- Leyenda de la Fig. 5: κ = 0.41 frente a 0.25 en el texto. [R5]
- La Fig. 2 se cita fuera de orden. [R5]
- La Fig. 5 cita publicaciones que no están en la lista de referencias. [R5]
- Las Pf deben llevar intervalos exactos: 2/600 = 0.04–1.2 %; 37/600 = 4.4–8.4 %. [R3, R4]
- «Laboratory density» de la Tabla 4 incluye el cambio de escala, a diferencia de la Tabla 3. [R4]
- «Several degrees» corresponde en realidad a 0.5° y 2.8°. [R4]

## 2. Validación (estadística)
- Validar la **predictiva desplegada**, con mezcla del MCMC y truncamiento, o declarar que se validó la aproximación plug-in. [R2]
- **Validación cruzada anidada** para elegir la regla. Reportar la regla preespecificada (r3 p0.05: 0.0305) y todas las variantes en material suplementario. [R2]
- Validar el procedimiento completo: diagnóstico → descarte → solo nivel, y la actualización con laboratorio común. La actualización es de «corte», no un «posterior exacto». [R2]
- R̂ normalizado por rangos, ESS de bulk y de colas, cadenas más largas para la forma potencia y sensibilidad a las previas. [R2]
- Validar la envolvente media a nivel de set, porque el valor característico es el P05 de la envolvente media. [R2]

### Preregistro del modo B de la forma acotada (2026-10-07, antes de correrlo)
- **Regla principal, fijada antes de ver resultados de la acotada:** actualización de solo nivel en x̄ con todos los sets
  (sin descartar los que el diagnóstico marca), igual que la regla vigente de la ronda 2.
- **Comparaciones secundarias**, todas reportadas en el material suplementario: previa sin actualizar; actualización
  conjunta; procedimiento completo (diagnóstico → descartar si p < 0.05 → solo nivel); ajustes ingenuos de φ′1 con m = 0.86
  y m = 0.90, con m estimado solo en el entrenamiento.
- **Métricas:** CRPS, cobertura del 80 %, fracción bajo el P10, sd(z) y PIT; bootstrap por publicación y Wilcoxon sobre las
  medias por publicación. No se elige ninguna variante a partir de estos resultados.

## 3. Mecánica (oportunidad principal del artículo)
- **Envolvente acotada por el estado crítico:** φ′s = φ′cs + Δφ(σ′n/σ0)^−λ, puntuada fuera de muestra sobre 2.75 MPa. Si gana, corrige el sesgo a alta tensión, y ese es el aporte central para botaderos altos. [R1]
- **Rotura (Bg) como covariable de la curvatura:** Bg existe en 524 de 767 ensayos y en 84 de 90 sobre 3 MPa. [R1]
- **Interacción e·x** (+0.016 ± 0.028, ya estimada): el efecto de la densidad debería disminuir con la tensión. Sensibilidad. [R1]
- c2 está mal respaldado por las citas de Charles y Watts e Indraratna; vincularlo a la supresión de la dilatancia. [R1]
- Efecto de escala con razón de tamaños ≥ 2, agrupamiento por publicación y ajuste por e en vez de filtrar; reportarlo nulo si sale nulo. [R1, R2]
- Literatura: Marsal (1967), Hardin (1985), Lade et al. (1996), Yamamuro y Lade (1996), McDowell y Bolton (1998), Einav (2007), Oldecop y Alonso (2001), Alonso et al. (2012). Verificar los DOI antes de citarlas.

## 4. Sitio
- El aumento del ángulo secante con la tensión aparece en todos los sets, así que es un patrón del laboratorio, no una anomalía del hornfels. Las fallas a 17–19 % de deformación sin pico están limitadas por la deformación. [R1, R4]
- Opciones: volver a reducir los ensayos con un criterio único (máxima razón de tensiones o q a deformación fija), o estimar un efecto de pendiente común del laboratorio en vez de descartar sets. [R1]
- El efecto de publicación cumple dos papeles (medición y resistencia): declararlo y mostrar la sensibilidad sin el posterior del laboratorio. [R4]
- Clase del mármol: probabilidades a posteriori de cada clase y promedio de modelos. [R4]
- Descomposición de varianza a 3 MPa, en la que domina el efecto de escala; matriz de escenarios e × escala × correlación. [R1, R4]
- Anonimización más fuerte: «a carbonate-hosted deposit», sin «Andes». [R5]

## 5. Estabilidad y presión de poros
- La capa basal tiene resistencia de enrocado con permeabilidad de arcilla: hay que definirla (desmonte triturado rico en finos o suelo de fundación) con su propia resistencia. [R3, R1]
- No reportar FS < 0.5 como valores; reportar la **altura o velocidad crítica** a la que el FS llega a 1.0 o 1.3. [R3]
- R mal definida (600 m/año vertical no es creíble); columnas evaluadas en tiempos distintos; cv constante. Análisis por etapas. [R3]
- γ = 21 kN/m³ es incoherente con e = 0.65 (≈ 16.3 seco). [R3]
- Monte Carlo con una familia fija de círculos subestima la Pf: buscar de nuevo la superficie crítica si FS < 1.3; rotular «condicional, solo resistencia». [R3, R4]
- Las comparaciones mezclan geometría, método y código (Bishop sobre fundación horizontal frente a M–P sobre ladera). [R3]
- Tabla FS(P05) ↔ Pf frente a las clases de consecuencia de Hawley y Cunning. [R3, R4]
- Reconocer: sismo, efectos 3D, confinamiento del pie, licuación estática y degradación. [R3]

## 6. Presentación (ASCE)
- Extensión ≈ 33 páginas con las figuras, sobre el límite de 30: quitar la Tabla 5, unir las Figs. 3 y 4, y pasar la Fig. 5 y la meta-regresión al material suplementario. [R5]
- Fuentes de las figuras de 8 pt o más; usar el mismo percentil por contexto (P10 para validación, P05 para diseño). [R5]
- Ecuación de la actualización de solo nivel en forma cerrada; definir la «regla mixta», la pérdida de cuantil y las conversiones. [R5]
- Notación completa y ordenada; Hungr en orden alfabético; referencia propia del código en Zenodo. [R5]
- Título más corto y centrado en el resultado; no llamar a Leps 2.0 «the standard». [R5, R1]

## 7. Lo que pediría un artículo de referencia (coincidencia entre revisores)
- Figura central: P50, P05 y P10 de φ′s frente a σ′n por clase y relación de vacíos, sucesora probabilística del gráfico de Leps.
- Tabla de diseño por clase, e y σ′n, y una regla de actualización en forma cerrada para planilla.
- Herramienta abierta archivada en Zenodo.
- Dominio de validez declarado: σ′n ≤ 8 MPa y e ≤ 0.6 sobre 3 MPa.

## No afirmar
«The standard»; efecto de escala compatible con Weibull; percentiles predictivos sobre 7.9 MPa; «validated» sin la validación del §2; Pf absolutas o anuales; que la envolvente P05 da en general el P05 del FS; generalizar el resultado de presión de poros.
