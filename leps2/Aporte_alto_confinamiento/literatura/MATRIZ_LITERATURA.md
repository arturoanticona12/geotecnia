# Matriz de literatura: resistencia al corte de desmonte de mina y enrocados (Leps-P)

Fecha: 2026-10-06. Uso interno. Volumen, número y páginas de todas las referencias D están comprobados en Crossref. El DOI de Frossard et al. (2012) es 10.1680/geot.10.P.079 (resuelto). Hay dos fuentes:

- **Verificación adversarial** (deep-research `wf_bf30eda8-2d2`): 22 fuentes leídas, 88 afirmaciones extraídas, 25 verificadas (21 confirmadas y 4 refutadas).
- **Consultas propias a Crossref**, que confirman el DOI y los metadatos, pero no el contenido.

Nivel de verificación:

- **V**: contenido confirmado por verificación adversarial 3-0.
- **D**: DOI y metadatos confirmados en Crossref; contenido por leer.
- **L**: leído por nosotros en este proyecto.
- **S**: sin DOI (libro, tesis o guía); hay que conseguir el documento.

## 1. Matriz

### 1.1 Envolventes empíricas y bases de datos

| Referencia (APA 7) | Nivel | Hallazgo clave | Relevancia para Leps-P |
|---|---|---|---|
| Leps, T. M. (1970). Review of shearing strength of rockfill. *Journal of the Soil Mechanics and Foundations Division, 96*(4), 1159–1170. https://doi.org/10.1061/JSFEAQ.0001433 | D, L | Tres envolventes no lineales, a partir de 109 ensayos | Origen de la línea de trabajo |
| De Mello, V. F. B. (1977). Reflections on design decisions of practical significance to embankment dams. *Géotechnique, 27*(3), 281–355. https://doi.org/10.1680/geot.1977.27.3.281 | D | Ley de potencia τ = A σ′n^b para enrocados | Antecedente de la forma de potencia |
| Charles, J. A., y Watts, K. S. (1980). The influence of confining pressure on the shear strength of compacted rockfill. *Géotechnique, 30*(4), 353–367. https://doi.org/10.1680/geot.1980.30.4.353 | D, L | Ley de potencia y su uso en estabilidad | Antecedente; comparación de b con nuestro m |
| Barton, N., y Kjærnsli, B. (1981). Shear strength of rockfill. *Journal of the Geotechnical Engineering Division, 107*(7), 873–891. https://doi.org/10.1061/AJGEB6.0001167 | V (vía Barton 2016), D | τ = σ′n tan[R log(S/σ′n) + φb]; S depende de la UCS corregida por tamaño (exponente 0.2) | Alternativa de forma con significado físico (S, φb como piso); candidata para la incertidumbre de forma |
| Barton, N. (2016). Non-linear shear strength for rock, rock joints, rockfill and interfaces. *Innovative Infrastructure Solutions, 1*, Artículo 30. https://doi.org/10.1007/s41062-016-0011-1 | V, D, L | Juntas y enrocado comparten envolventes no lineales | Respaldo de la forma B&K |
| Barton, N. R. (2008). Shear strength of rockfill, interfaces and rock joints, and their points of contact in rock dump design. En *Rock Dumps 2008* (pp. 3–17). ACG. https://doi.org/10.36487/ACG_repo/802_1 | V | Con talud constante, el FS baja de la cresta a la base y del exterior al interior | Motivación directa para botaderos altos |
| Indraratna, B., Wijewardena, L. S. S., y Balasubramaniam, A. S. (1993). Large-scale triaxial testing of greywacke rockfill. *Géotechnique, 43*(1), 37–51. https://doi.org/10.1680/geot.1993.43.1.37 | D, L | Triaxiales grandes en grauvaca; dependencia de φ con σ3 normalizada por la UCS | Normalización por la UCS como covariable |
| Cylwik, S. D., Arrieta, M., Cunning, J. C., y Hawley, P. M. (2025). Update to the Leps strength envelopes for rockfill based on 900 large-scale triaxial tests. *International Journal of Geomechanics, 25*(12), 04025285. https://doi.org/10.1061/IJGNAI.GMENG-12050 | V, L | Criterio de potencia con un parámetro (φ′1) y modelo φ′1(e, calidad); D50 > 2 mm, finos < 25 % | Línea base; misma base de datos |
| Cylwik, S. D., Arrieta, M., Cunning, J. C., y Hawley, P. M. (2025). Leps 2.0: Updated strength envelopes for rockfill based on 900 large-scale triaxial tests. En *SSIM 2025* (pp. 1–17). ACG. https://doi.org/10.36487/ACG_repo/2535_0.02 | V, D | Versión de congreso | Citar junto con el artículo |
| Arrieta, M. (2025). *Rockfill test database* [Conjunto de datos]. Zenodo. https://doi.org/10.5281/zenodo.14665504 | L | 938 ensayos de 40 publicaciones; σ′n máximo de 7.86 MPa; 90 ensayos sobre 3 MPa (8 publicaciones) | Base de calibración |
| Ovalle, C., Linero, S., Dano, C., Bard, E., Hicher, P.-Y., y Osses, R. (2020). Data compilation from large drained compression triaxial tests on coarse crushable rockfill materials. *Journal of Geotechnical and Geoenvironmental Engineering, 146*(9), 06020013. https://doi.org/10.1061/(ASCE)GT.1943-5606.0002314 | V, L | 158 CD en 33 enrocados (~1 m); φ′máx > 45° con σ′3 < 0.2 MPa y 30–40° a alta presión | Base complementaria; verificar solapamiento con Arrieta |
| **Contreras, L.-F., y Linero-Molina, S. (2025). Hierarchical Bayesian inference of rockfill strength parameters from large-scale triaxial test data. *Australian Geomechanics, 60*(2), 91–106. https://doi.org/10.56295/AGJ6024** | **L** | B-K (φb, R, S) inferido por MCMC (PyMC, NUTS) con previas uniformes vagas. Usa 32 triaxiales grandes de **un proyecto** (4 grupos de mezcla, 5 tipos de roca) y 195 ensayos de φb. La jerarquía es entre grupos del mismo sitio. Error en φ homocedástico. No hay evaluación fuera de muestra ni análisis de extrapolación. Usa bandas del 95 % HDI (de la media) y PI de 5–95 % (de φ), y recomienda el límite inferior del PI para estructuras críticas (p. 11) | **Antecedente directo: la idea de un modelo bayesiano jerárquico con bandas para enrocados ya existe y hay que reconocer su prioridad.** Leps-P se diferencia por la previa poblacional mundial calibrada (36 publicaciones) y evaluada fuera de muestra, la incertidumbre que depende del esfuerzo y de la forma al extrapolar, el nivel de laboratorio y la aplicación a estabilidad con Pf |
| Contreras, L.-F., Linero-Molina, S., y Dixon, J. (2022). Bayesian approach to improve the confidence of the estimation of the shear strength of coarse mine waste using Barton's empirical criterion. *Australian Geomechanics, 57*(2), 163–174 | S (DOI por buscar) | Bayes no jerárquico con B-K en desmonte grueso | Antecedente; citar |
| Linero-Molina, S., Contreras, L.-F., y Dixon, J. (2022). Shear strength estimation of very coarse mine waste using Barton's empirical criterion and a Bayesian analysis. En *Proc. 20th ICSMGE* (pp. 4369–4374) | S | Ídem, en congreso | Antecedente; citar |
| Williams, H., y Ledesma, O. N. (2022). Use of Bayesian hierarchical models to estimate geotechnical parameters for tailings. *GeoCalgary 2022* | S | Modelos jerárquicos en relaves | Antecedente metodológico en minería |

### 1.2 Alta presión, estado crítico y rotura

| Referencia (APA 7) | Nivel | Hallazgo clave | Relevancia |
|---|---|---|---|
| Marsal, R. J. (1967). Large scale testing of rockfill materials. *Journal of the Soil Mechanics and Foundations Division, 93*(2), 27–43. https://doi.org/10.1061/JSFEAQ.0000958 | D | Índice de rotura Bg; ensayos a alta presión | Bg en la base y en el sitio |
| Marsal, R. J. (1973). Mechanical properties of rockfill. En R. C. Hirschfeld y S. J. Poulos (Eds.), *Embankment-dam engineering: Casagrande volume* (pp. 109–200). Wiley | S | Síntesis de ensayos de Marsal a alta presión | Parte de los ensayos de > 3 MPa de la base |
| Marachi, N. D., Chan, C. K., y Seed, H. B. (1972). Evaluation of properties of rockfill materials. *Journal of the Soil Mechanics and Foundations Division, 98*(1), 95–114. https://doi.org/10.1061/JSFEAQ.0001735 | D | Triaxiales hasta ~4.5 MPa; efecto de escala | Parte de los ensayos a alta presión de la base; residuos extremos en el modo B |
| Varadarajan, A., Sharma, K. G., Venkatachalam, K., y Gupta, A. K. (2003). Testing and modeling two rockfill materials. *Journal of Geotechnical and Geoenvironmental Engineering, 129*(3), 206–218. https://doi.org/10.1061/(ASCE)1090-0241(2003)129:3(206) | D, L | El signo del efecto de escala depende del origen (redondeado o anguloso) | Término de escala por tipo de material |
| Xiao, Y., Liu, H., Chen, Y., y Jiang, J. (2014). Strength and deformation of rockfill material based on large-scale triaxial compression tests. I. *Journal of Geotechnical and Geoenvironmental Engineering, 140*(12), 04014070. https://doi.org/10.1061/(ASCE)GT.1943-5606.0001176 | D, L | Influencia de la densidad y la presión | Densidad × esfuerzo (curvatura) |
| Xiao, Y., et al. (2014). Strength and deformation … II. *JGGE, 140*(12), 04014071. https://doi.org/10.1061/(ASCE)GT.1943-5606.0001177 | D, L | Rotura y dilatancia | Ídem |
| Ventini, R., Lirer, S., Mancuso, C., y Flora, A. (2021). Simplified procedure to identify the critical state line of crushable rockfills. *JGGE, 147*(12), 04021150. https://doi.org/10.1061/(ASCE)GT.1943-5606.0002668 | V, D, L | La CSL no es intrínseca: se desplaza con la rotura; propone un procedimiento para ubicarla | Base física para un piso de estado crítico dependiente de la rotura en la extrapolación |
| Bard, E., Anabalón, M. E., y Campaña, J. (2011). Waste rock behavior at high pressures. En *Multiscale geomechanics* (cap. 4). Wiley. https://doi.org/10.1002/9781118601433.ch4 | D (posible copia local: R011) | Comportamiento del desmonte a alta presión | Precedente directo |
| Coop, M. R., Sørensen, K. K., Bodas Freitas, T., y Georgoutsos, G. (2004). Particle breakage during shearing of a carbonate sand. *Géotechnique, 54*(3), 157–163. https://doi.org/10.1680/geot.2004.54.3.157 | D | Rotura continua hasta grandes deformaciones en material carbonatado | Pertinente para el mármol |
| Yamamuro, J. A., y Lade, P. V. (1996). Drained sand behavior in axisymmetric tests at high pressures. *Journal of Geotechnical Engineering, 122*(2), 109–119. https://doi.org/10.1061/(ASCE)0733-9410(1996)122:2(109) | D | Comportamiento a muy alta presión | Rango de esfuerzos |

### 1.3 Rotura de partículas, escala y resistencia de partícula

| Referencia (APA 7) | Nivel | Hallazgo clave | Relevancia |
|---|---|---|---|
| Hardin, B. O. (1985). Crushing of soil particles. *Journal of Geotechnical Engineering, 111*(10), 1177–1192. https://doi.org/10.1061/(ASCE)0733-9410(1985)111:10(1177) | D, L | Rotura relativa Br | Índice alternativo a Bg |
| Einav, I. (2007). Breakage mechanics—Part I: Theory. *Journal of the Mechanics and Physics of Solids, 55*(6), 1274–1297. https://doi.org/10.1016/j.jmps.2006.11.003 | D, L | Rotura como variable de estado | Marco teórico |
| Frossard, E., Hu, W., Dano, C., y Hicher, P.-Y. (2012). Rockfill shear strength evaluation: A rational method based on size effects. *Géotechnique, 62*(5), 415–427. https://doi.org/10.1680/geot.10.P.079 | V, D, L | Escala de Weibull de envolventes a partir de material fino de la misma mineralogía | Paso de la probeta al tamaño de campo |
| Ovalle, C., Frossard, E., Dano, C., Hu, W., Maiolino, S., y Hicher, P.-Y. (2014). The effect of size on the strength of coarse rock aggregates and large rockfill samples through experimental data. *Acta Mechanica, 225*(8), 2199–2216. https://doi.org/10.1007/s00707-014-1127-z | V, D, L | A mayor tamaño, más rotura y menos resistencia (probetas de 250 frente a 1000 mm) | Término de escala |
| Alonso, E. E., Tapias, M., y Gili, J. (2012). Scale effects in rockfill behaviour. *Géotechnique Letters, 2*(3), 155–160. https://doi.org/10.1680/geolett.12.00025 | D, L | Escala y tiempo | Ídem |
| Girumugisha, G., Ovalle, C., y Ouellet, S. (2024). Grading scalping and sample size effects on critical shear strength of mine waste rock through laboratory and in-situ testing. *International Journal of Rock Mechanics and Mining Sciences, 183*, 105915. https://doi.org/10.1016/j.ijrmms.2024.105915 | V, D, L | Escalpado y tamaño de probeta en desmonte, con ensayos in situ | Desmonte de mina específicamente |
| Oldecop, L. A., y Alonso, E. E. (2001). A model for rockfill compressibility. *Géotechnique, 51*(2), 127–139. https://doi.org/10.1680/geot.2001.51.2.127 | D | Humedad y fisuración subcrítica | Durabilidad y colapso |

### 1.4 Caracterización de desmonte y botaderos altos

| Referencia (APA 7) | Nivel | Hallazgo clave | Relevancia |
|---|---|---|---|
| Hawley, M., y Cunning, J. (Eds.). (2017). *Guidelines for mine waste dump and stockpile design*. CSIRO Publishing | S (copia local R001) | Marco de diseño y criterios de aceptación | Formato de diseño |
| Linero, S., Palma, C., y Apablaza, R. (2007). Geotechnical characterisation of waste material in very high dumps with large scale triaxial testing. En Y. Potvin (Ed.), *Slope Stability 2007* (pp. 59–75). ACG. https://doi.org/10.36487/ACG_repo/708_2 | V, D | Triaxiales grandes que reproducen las cargas de botaderos de cientos de metros | Precedente directo |
| Valenzuela, L., Bard, E., Campaña, J., y Anabalón, M. E. (2008). High waste rock dumps: Challenges and developments. En *Rock Dumps 2008* (pp. 65–78). ACG. https://doi.org/10.36487/ACG_repo/802_6 | V, D | Equipo IDIEM de 1 m (σ′3 ≤ 2.5 MPa); la envolvente se curva sobre ~2 MPa; contractivo sobre 0.2 MPa; Su/σ′30 = 0.28–0.29 (CIU) | Precedente y valor de tamizaje no drenado |
| McLemore, V. T., Fakhimi, A., van Zyl, D., Ayakwah, G. F., et al. (2009). *Literature review of other rock piles: Characterization, weathering, and stability*. NMBGMR, OFR-517. https://doi.org/10.58799/OFR-517 | D | Meteorización y estabilidad de pilas de desmonte | Durabilidad y degradación |
| Dawson, R. F., Morgenstern, N. R., y Stokes, A. W. (1998). Liquefaction flowslides in Rocky Mountain coal mine waste dumps. *Canadian Geotechnical Journal, 35*(2), 328–343. https://doi.org/10.1139/t98-009 | D | Licuación estática en botaderos | Mecanismo no drenado |
| Hungr, O., Dawson, R. F., Kent, A., Campbell, D., y Morgenstern, N. R. (2002). Rapid flow slides of coal-mine waste in British Columbia, Canada. En S. G. Evans y J. V. DeGraff (Eds.), *Catastrophic landslides* (pp. 191–208). GSA. https://doi.org/10.1130/REG15-p191 | D | Flujos rápidos | Ídem |
| BC Mine Waste Rock Pile Research Committee (1991). *Mined rock and overburden piles: Investigation and design manual (interim guidelines)* | S | Clasificación de estabilidad de botaderos | Contexto histórico |

### 1.5 Probabilidad, Bayes, variabilidad espacial y diseño

| Referencia (APA 7) | Nivel | Hallazgo clave | Relevancia |
|---|---|---|---|
| Ching, J., y Phoon, K.-K. (2019). Constructing site-specific multivariate probability distribution model using Bayesian machine learning. *Journal of Engineering Mechanics, 145*(1), 04018126. https://doi.org/10.1061/(ASCE)EM.1943-7889.0001537 | D, L | Distribución específica del sitio a partir de bases genéricas | Marco equivalente: base mundial → sitio |
| Ching, J., Wu, S., y Phoon, K.-K. (2021). Constructing quasi-site-specific multivariate probability distribution using hierarchical Bayesian model. *Journal of Engineering Mechanics, 147*(10), 04021069. https://doi.org/10.1061/(ASCE)EM.1943-7889.0001964 | D, L | Modelo bayesiano jerárquico casi específico del sitio | Antecedente metodológico directo |
| Phoon, K.-K., y Kulhawy, F. H. (1999). Characterization of geotechnical variability. *Canadian Geotechnical Journal, 36*(4), 612–624. https://doi.org/10.1139/t99-038 | D | Componentes de la incertidumbre | Separación entre material y laboratorio |
| Vanmarcke, E. H. (1977). Probabilistic modeling of soil profiles. *Journal of the Geotechnical Engineering Division, 103*(11), 1227–1246. https://doi.org/10.1061/AJGEB6.0000517 | D | Promedio espacial | Diferencia entre variabilidad espacial y epistémica |
| Christian, J. T., Ladd, C. C., y Baecher, G. B. (1994). Reliability applied to slope stability analysis. *Journal of Geotechnical Engineering, 120*(12), 2180–2207. https://doi.org/10.1061/(ASCE)0733-9410(1994)120:12(2180) | D, L | Confiabilidad de taludes; incertidumbre sistemática frente a espacial | Correlación entre litologías |
| Prästings, A., Spross, J., y Larsson, S. (2019). Characteristic values of geotechnical parameters in Eurocode 7. *Proceedings of the ICE – Geotechnical Engineering, 172*(4), 301–311. https://doi.org/10.1680/jgeen.18.00057 | D, L | Valor característico del EC7 por enfoque bayesiano | Formato de diseño |
| Laird, N. M., y Ware, J. H. (1982). Random-effects models for longitudinal data. *Biometrics, 38*(4), 963–974. https://doi.org/10.2307/2529876 | D | Modelo mixto | Método |
| Gneiting, T., y Raftery, A. E. (2007). Strictly proper scoring rules, prediction, and estimation. *JASA, 102*(477), 359–378. https://doi.org/10.1198/016214506000001437 | D | CRPS | Método |
| Baecher, G. B., y Christian, J. T. (2003). *Reliability and statistics in geotechnical engineering*. Wiley | S | Texto de referencia | Método |
| Read, J., y Stacey, P. (Eds.). (2009). *Guidelines for open pit slope design*. CSIRO Publishing | S | Criterios de aceptación por FS y Pf | Criterio de aceptación |

### 1.6 Presión de poros, consolidación y resistencia no drenada

| Referencia (APA 7) | Nivel | Hallazgo clave | Relevancia |
|---|---|---|---|
| Gibson, R. E. (1958). The progress of consolidation in a clay layer increasing in thickness with time. *Géotechnique, 8*(4), 171–182. https://doi.org/10.1680/geot.1958.8.4.171 | D, L | Consolidación con carga creciente | Base de la sección de presión de poros |
| Olson, S. M., y Stark, T. D. (2002). Liquefied strength ratio from liquefaction flow failure case histories. *Canadian Geotechnical Journal, 39*(3), 629–647. https://doi.org/10.1139/t02-001 | D, L | Su(liq)/σ′v a partir de casos de falla | Resistencia licuada para la base no drenada |

### 1.7 Co-disposición de relaves y desmonte

La búsqueda no encontró fuentes verificadas. Hay que hacer una búsqueda dirigida, por ejemplo con los términos *co-disposal*, *paste rock*, *GeoWaste*, Wickland y Wilson, y Bareither.

## 2. Afirmaciones refutadas (no usar)

- Que Leps 2.0 recomiende calibrar solo entre 60 y 600 kPa e implique que no vale a 10–15 MPa (0-3). **Nota:** nuestro manuscrito cita «la guía 60-600»; hay que revisar en Cylwik et al. (2025) qué dice exactamente antes de mantenerlo.
- Que Leps 2.0 simplifique Leps en «cinco categorías» (1-2).
- Valores de R y S que reproducen Leps según Barton (1-2).
- Que Frossard et al. (2012) excluyan el escalpado (0-3).

## 3. Brechas y tratamiento propuesto

Categorías:

- **Cerrar:** con nuestros datos y métodos.
- **Acotar:** cuantificar el efecto en el diseño de lo que no se puede resolver.
- **Protocolo:** especificar los ensayos y cómo se incorporan al criterio.

| # | Brecha | Evidencia de la brecha | Tratamiento en Leps-P | Categoría |
|---|---|---|---|---|
| B1 | No hay un criterio de resistencia de enrocado y desmonte con incertidumbre calibrada fuera de muestra, que crezca con el esfuerzo y se actualice con ensayos del sitio | Leps 2.0 es determinista con dispersión de φ′1. Contreras y Linero-Molina (2025) es bayesiano jerárquico (**hay que leerlo para delimitar**) | Modelo de 3 niveles con validación cruzada por publicación y por tipo de roca, bootstrap, PIT y pérdida de cuantil | Cerrar (delimitando frente a Contreras y Linero-Molina) |
| B2 | La variabilidad del material se confunde con la del laboratorio o procedimiento | Phoon y Kulhawy (1999); los revisores encontraron que la publicación explica el 36–54 % | Nivel de publicación explícito; varianza del sitio sin sesgo de laboratorio | Cerrar |
| B3 | No hay datos sobre 7.9 MPa; la forma de la envolvente a 10–15 MPa no está identificada | Toda la literatura verificada queda bajo 3–5 MPa; la CSL depende de la rotura (Ventini et al., 2021) | Banda de incertidumbre de forma: potencia, Barton-Kjærnsli (piso φb) y piso de estado crítico; promedio de modelos; FS en cada caso | Acotar y protocolo |
| B4 | Escala de la probeta (dmax ≤ 200 mm) al campo, combinada con el efecto de presión | Frossard et al. (2012) y Ovalle et al. (2014) tratan la escala sin presión ni incertidumbre | Término de escala en el modelo (D/dmax o dmax) estimado con la base y el sitio; sensibilidad | Acotar (cerrar si la base lo identifica) |
| B5 | Resistencia de partícula (UCS) como predictor, en lugar de la «calidad» subjetiva | Barton y Kjærnsli (1981), Indraratna et al. (1993); la clase de Cylwik se asignó con la resistencia medida (fuga) | Probar la UCS como covariable continua con los datos de la base que la tienen; prueba dejando fuera cada tipo de roca | Cerrar o acotar según los datos |
| B6 | Litologías calcáreas y argiláceas sin ensayos a alta presión | Los ensayos de > 3 MPa son de basalto, grava, argilita, diorita y conglomerado | Previa mezcla sobre clases y sensibilidad; programa de ensayos | Acotar y protocolo |
| B7 | Resistencia no drenada y licuada del desmonte triturado a alta presión | Valenzuela et al. (2008): Su/σ′3c = 0.28–0.29 en CIU; Olson y Stark (2002) para la resistencia licuada; sin datos a alta presión | Escenarios de base no drenada (fluencia y licuada) con normalización correcta; efecto en el FS y la Pf | Acotar y protocolo |
| B8 | Presión de poros por avance del frente y por fundación poco permeable | Gibson (1958); la consolidación global sola es favorable | Gibson con carga por frente de volteo y k de fundación; efecto de ru en el FS | Acotar |
| B9 | Correlación y disposición espacial de litologías en la estabilidad de un botadero mixto | Christian et al. (1994) y Vanmarcke (1977) separan lo sistemático de lo espacial; no hay aplicación a botaderos mixtos | Correlación ρ entre 0 y 1, zonificación y litología más débil | Acotar |
| B10 | No hay un formato de diseño que conecte la envolvente probabilística con criterios de aceptación de minería | Read y Stacey (2009), Hawley y Cunning (2017), EC7 (Prästings et al., 2019) | Formato: percentil más FS objetivo frente a Pf por Monte Carlo; tabla de equivalencias | Cerrar |
| B11 | Efecto de la co-disposición de relaves en la resistencia drenada y no drenada | Sin fuentes verificadas; datos propios débiles (1 set de control) | Acotar con los datos del sitio y especificar ensayos | Acotar y protocolo |
| B12 | Degradación por durabilidad y desleimiento a largo plazo (margas y limolitas) | Oldecop y Alonso (2001), McLemore et al. (2009) | Escenario de degradación (cambio de clase o de e); ensayos de durabilidad | Protocolo y acotar |
| B13 | Validación de cualquier criterio sobre 8 MPa | Ninguna base llega | Programa mínimo de ensayos (σ′3 de 5–10 MPa, litologías y escalas) y regla para incorporarlos al criterio | Protocolo |

## 4. Para descargar (el usuario tiene acceso a ASCE y ScienceDirect)

Prioridad 1:

- Contreras y Linero-Molina (2025), Australian Geomechanics.
- Ventini et al. (2021), ASCE.
- Ching et al. (2021), ASCE.
- Ching y Phoon (2019), ASCE.
- Marachi et al. (1972), ASCE.
- Xiao et al. (2014) I y II, ASCE.
- Charles y Watts (1980), ICE.
- De Mello (1977), ICE.
- Frossard et al. (2012), ICE.
- Indraratna et al. (1993), ICE.

Prioridad 2:

- Varadarajan et al. (2003), ASCE.
- Hardin (1985), ASCE.
- Christian et al. (1994), ASCE.
- Einav (2007), ScienceDirect.
- Olson y Stark (2002), CSP.
- Gibson (1958), ICE.
- Alonso et al. (2012), ICE.
- Ovalle et al. (2014), Springer.
- Prästings et al. (2019), ICE.
- Bard et al. (2011), Wiley (verificar si R011 es este capítulo).

Sin DOI:

- Marsal (1973);
- Baecher y Christian (2003);
- Read y Stacey (2009);
- BC Mine Waste Rock Pile Research Committee (1991).

Guardarlos en `Aporte_alto_confinamiento/literatura/pdf/`.

**Estado (2026-10-06):**
- Se recibieron y leyeron 21 PDF.
- Faltan De Mello (1977), Marachi et al. (1972), Marsal (1967) y Bard et al. (2011).
- De Marachi se leyó la discusión de Al-Hussaini (1972), *JSMFD 98*(12), 1409–1411.
- Einav (2007b), Parte II: *J. Mech. Phys. Solids, 55*, 1298–1320. https://doi.org/10.1016/j.jmps.2006.11.004

## 5. Síntesis de la lectura: qué cambia en Leps-P

Hay tres lecturas paralelas y la nuestra de Contreras y Linero-Molina. Los números marcados como «cálculo» son derivaciones de los lectores y deben verificarse antes de citarse.

### 5.1 Novedad reclamable

**No se puede reclamar:**
- el modelo jerárquico sobre una base genérica;
- la predictiva de un material nuevo;
- la actualización gaussiana conjugada con pocos datos del sitio;
- la propagación de la incertidumbre de los hiperparámetros.

Todo esto ya lo hacen Ching y Phoon (2019) y Ching et al. (2021) en arcillas. Contreras y Linero-Molina (2025) hacen Bayes jerárquico con B-K en enrocado de un solo sitio.

**Sí se puede reclamar:**
1. una envolvente dependiente del esfuerzo con θ y m aleatorios y covariables físicas;
2. una previa poblacional mundial para enrocado y desmonte (767 ensayos y 36 publicaciones);
3. una evaluación fuera de muestra sistemática, dejando fuera cada publicación;
4. un nivel de laboratorio o publicación, que Ching et al. dejan abierto;
5. un diagnóstico de conflicto entre la previa y el sitio;
6. la incertidumbre de forma y de escala al extrapolar;
7. el enlace con el formato de diseño (EC7, Pf).

**Debilidad que hay que corregir:** el REML no propaga la incertidumbre de los hiperparámetros. Hay que usar un bootstrap paramétrico o Bayes completo.

### 5.2 Forma de la envolvente y extrapolación

**La pendiente log–log local aumenta con el esfuerzo:**

| Fuente | Pendiente | Rango |
|---|---|---|
| Charles y Watts (1980) | b de 0.67 a 0.81 | ≤ 0.4 MPa |
| De Mello, según Charles y Watts | 0.81 a 0.88 | ≤ 5 MPa |
| Marachi, según Indraratna et al. (1993) | 0.87 a 0.90 | ≤ 4.5 MPa |

- Indraratna et al. (1993) dicen que la pendiente tiende a 1 sobre 1–1.5 MPa y que φ′ se acerca a unos 30°.
- **Acción:** comprobar si los residuos de Leps-P muestran una curvatura sistemática en log–log. Si la hay, m dependería del esfuerzo, y una ley de potencia con m < 1 sería **conservadora** al extrapolar.

**Barton-Kjærnsli:**
- Con R ≈ 7.5, su pendiente local es 0.87–0.89 (cálculo), casi idéntica a la ley de potencia en el rango con datos. Solo la extrapolación las separa.
- Indraratna et al. (1993) advierten no extrapolar B-K sobre 1 MPa: φ cae más rápido de lo que predice.

**Piso de estado crítico:**
- No es identificable como constante.
- El «φcs» de Xiao et al. (2014a) baja unos 7° por década de esfuerzo; extrapolado da unos 33° a 10 MPa (cálculo).
- φcs también baja con la rotura (Xiao et al., 2014b).
- La CSL no es intrínseca (Ventini et al., 2021), y la literatura discrepa sobre si M baja con la rotura.
- Ovalle et al. (2014) y Einav (2007b) sostienen que φcs no depende de la rotura.
- **Decisión propuesta:** sin piso duro. El piso entra en la banda de forma como escenario de sensibilidad dependiente de la rotura, no como un φcs fijo.

**Datos a alta presión:**
- Ninguna fuente tiene datos a 10–15 MPa. Los máximos son 4.5 MPa (Marachi), 3.45 (Al-Hussaini), 2.5 (IDIEM), 1.6 (Xiao) y < 1 (Ventini).
- Nuestra base llega a 7.9 MPa, entre las más altas disponibles.

### 5.3 Efecto de escala de la probeta al campo

- **Forma:** con la homotecia de Weibull de Frossard et al. (2012), la corrección en log–log es Δθ = −κ (1 − m) ln(D_campo/D_lab), con m sin cambio.
- **Previa propuesta (cálculo, con 12 valores publicados):** κ ~ LogNormal con mediana 0.41 y IC 95 % de 0.22 a 0.75.
- **Magnitud (cálculo):** con dmax de 150 mm, campo de 0.5–1.5 m, m = 0.87 y φ′ = 35°, Δφ′ ≈ −2.4° (intervalo de 90 %: −1.4° a −4.3°).
- **Validación experimental:** Ovalle et al. (2014) midieron −2° a −3° con un factor de tamaño de 4.
- **Límites:**
  - El signo depende del material: aluvial redondeado gana φ y tronadura débil lo pierde (Varadarajan et al., 2003).
  - Debe tratarse como incertidumbre, no como una corrección fija.
  - Factor de tamaño ≤ 15 (Frossard et al., 2012).
- **Consecuencia:** el campo a 10–15 MPa equivale al laboratorio a unos 23–35 MPa. La extrapolación efectiva es mayor que la nominal.

### 5.4 Covariables

- **Resistencia de partícula:**
  - Indraratna et al. (1993) normalizan por σc.
  - Barton usa S con corrección por tamaño, (50/d50)^0.2.
  - Ventini et al. (2021) usan pf.
  - El efecto esperado sobre θ es pequeño: el coeficiente de ln σc sería 1 − b ≈ 0.10–0.14 (cálculo).
  - Advertencia: la UCS de la grauvaca aparece como 13.5 o 136 MPa en el mismo artículo; las fuentes de UCS son frágiles.
- **Densidad:** módula la curvatura. Recalculado con Xiao et al. (2014a), m sube de 0.77 a 0.91 cuando e0 va de 0.189 a 0.317 (cálculo). Esto respalda incluir una interacción e × x (efecto de e sobre m).
- **Índice de rotura:**
  - Br de Hardin o B de Einav, mejor que Bg (que depende del tamiz y la granulometría).
  - La rotura es resultado del ensayo, no una variable explicativa. Para explicar m hay que usar covariables previas al ensayo: dureza o UCS, forma, e0 y Cu.
- **Uniformidad:** Cu pesa más que el tamaño en la rotura (Ventini et al., 2021).

### 5.5 Diseño, Pf y presión de poros

- **Componentes de la incertidumbre (Christian et al., 1994; Prästings et al., 2019):**
  - Sistemática, que no se promedia: efectos fijos, material, laboratorio, forma y escala.
  - Espacial: supuesta, reducida con R = 2r₀/L.
  - El residuo de laboratorio es error de ensayo y **no** variabilidad del botadero.
  - Christian et al. (1994): «the systematic error propagates almost unchanged through an analysis and can have a much greater influence on the predictive uncertainty than does the spatial variability».
- **Valor característico para la falla global:** θk = μ − 1.645 σ_sistemático (EC7, estimación prudente de la media).
- **Verificación:** Pf y β por Monte Carlo, más una tabla de FS consistente por consecuencia, al estilo de la Tabla 8 de Christian et al. (1994).
- **Correlación entre litologías:** Cov(θA, θB) = x_A′V_β x_B + σ²_publicación·1[mismo laboratorio] (derivación del lector).
- **Presión de poros (Gibson, 1958):**
  - Para un crecimiento a ritmo constante (h = m t), el resultado depende de T = m²t/cv.
  - La cota sin drenaje es ru = B̄.
  - cv y B̄ dependen de la colocación, y la presión de poros hay que medirla.
- **Resistencia licuada (Olson y Stark, 2002):**
  - Su(liq)/σ′v está entre 0.05 y 0.12, con media 0.09 (±0.03, una desviación estándar).
  - Viene de arenas y relaves con σ′v ≤ 350 kPa, así que aplicarla a desmonte a varios MPa es una extrapolación.
  - Exige que la línea de consolidación sea paralela a la de estado estacionario.

### 5.6 Cambios a la tabla de brechas (sección 3)

- **B1:** cerrar, pero solo en lo reclamable (5.1). Citar a Ching et al. (2021) y a Contreras y Linero-Molina (2025) como antecedentes.
- **B3:** acotar con una banda de forma de tres miembros (potencia, B-K, piso dependiente de la rotura) y verificar la curvatura de los residuos.
- **B4:** acotar con la homotecia de Frossard con κ aleatorio y signo incierto según el origen del material. Puede pasar a «cerrar» si la base tiene sets con varios dmax del mismo material.
- **B5:** probar ln UCS (efecto pequeño esperado) y la interacción e × x.
- **B7:** acotar con Su(liq)/σ′v de 0.05–0.12 como escenario. El protocolo exige CIU a alta presión que verifique el paralelismo de las líneas de consolidación y de estado estacionario.
- **B10:** cerrar con el formato de 5.5.
