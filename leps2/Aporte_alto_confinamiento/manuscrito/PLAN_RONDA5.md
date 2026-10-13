# Ronda 5: respuesta a los revisores (los cinco: revisión menor)

Manuscrito: `build_lepsp_asce5.py` → `LepsP_IJGM_manuscript_r5.docx`; suplemento: `build_suplemento5.py` → `LepsP_IJGM_supplement_r5.docx`.

## Correcciones de fondo (cálculo)

| Observación | Qué se hizo | Resultado | Archivo |
|---|---|---|---|
| ΔML de la forma acotada sesgado (grilla, ψ fija) | Verosimilitud perfilada real: en cada φ′∞ se reestiman ζ0 y ψ por ML completa | Máximo en φ′∞ = 25° (ML 1685.51). ΔML frente a la cuadrática 9.7 y frente a la potencia 12.2. Con φ′∞ = 0 se reproduce exactamente la potencia (control). Banda de 3 unidades: 19–28° (en la grilla de 1°) | `analisis/lepsp_perfil.py`, `lepsp_perfil.json` |
| R̂ alto en las cadenas | 4 cadenas de 12 000 + 3 000; previas 0.1 y 0.5 con 6 000 + 2 000 | R̂ máx 1.005, ESS bulk mín 967, tail 2121; previas: R̂ 1.009 y 1.015, hiperparámetros cambian ≤ 0.02 | `lepsp_mcmc5.py`, `lepsp_mcmc5.json` |
| Cresta | 16 puntos con ΔML > −6 (14–29°), pesos ∝ exp(ML) | φ′∞ medio 24.4° (24.5° con previa uniforme en tan φ′∞); ζ0 medio 0.29 | ídem |
| Doble conteo de la varianza de efectos fijos en `actualizar_sitio` | P0g solo para la ganancia | Corregido; 24 pruebas pasan | `leps3/lepsp.py` |
| ¿La superficie crítica sale del dominio de validez? | σ′n ≈ γ·h·cos²α en la base de las dovelas | 700 m: media 1.4 MPa, máx 2.0 MPa, profundidad 137–147 m; 150 m: máx 0.5 MPa. Dentro del dominio | `lepsp_sn_movilizada.py` |
| Sensibilidades de escala en Slide2 | Casos nuevos `e065 bD indep` y `e065 tau r3` (τ_D = 0.049, el de la ronda 3, más bajo) | FS 700 m P50/P05: base 1.47/1.21; bD independiente 1.48/1.32 (compartir es conservador); τ_D 0.049 1.47/1.25; escala con media estimada 1.58/1.30; laboratorio con escala 1.69/1.39; laboratorio sin escala 1.69/1.60; cuadrática 1.46/1.20 | lote 67, `lepsp_estabilidad_slide2.json` |
| Convergencia de la búsqueda | Control circular Auto Refine del caso que gobierna | 1.475/1.209 frente a SA no circular 1.470/1.205 | lote 67 |
| Monte Carlo | 600 realizaciones por caso, cada una con su búsqueda | Modelo: 0/600 fallas (Pf < 0.61 %, Clopper–Pearson), FS P50/P05 1.478/1.215, β_LN 3.28. Solo E: 11/600 (0.92–3.26 %), 1.352/1.069, β_LN 2.11. El P05 del FS (1.215) coincide con el FS de la envolvente P05 (1.205) | `slide2/mc5`, lote 68 |

## Correcciones de redacción

- Orden de citas: tres figuras principales (Fig. 2 del perfil pasa a Fig. S3); S1–S5 secuenciales; Table S1 citada.
- Notación: t∞ (antes *T*), τ_D, *D*max, *a*0 y *a*1 en cursiva.
- Conclusiones en presente; «intervalos consistentes con la cobertura nominal» en vez de «calibrados».
- p del conflicto del tipo de roca A desde `lepsp_sitio3.json` (0.17).
- Referencias nuevas: Been y Jefferies (1985), Russell y Khalili (2004).
- Aplicación: Tabla 4 a 1 y 2 MPa; σ′n movilizada; supuestos (sin bancos, seco, e y γ constantes); comprobación tipo EC7 M2; base del índice β; cota superior de Pf; sensibilidades.
- Discusión: la curvatura que decae importa solo en mecanismos profundos (fundación débil, capa basal), no analizados; procedimiento: actualizar con todos los sets y descartar solo con causa o si es conservador.

## Extensión y formato

- Versión principal en LaTeX con la clase oficial `ascelike-new` (`latex/LepsP_IJGM_manuscript_r5.tex/.pdf`): 30 páginas con texto, listas, 4 tablas y 3 figuras; 0 errores y 0 líneas desbordadas. El .docx se genera desde la misma fuente como respaldo (28 páginas más 3 figuras).
- Recortes para llegar a 30 páginas: resumen de 290 a 250 palabras (límite de ASCE); frases repetidas en otra sección; lista de procedimientos del modo B remitida a la Tabla S1; sensibilidades de Slide2 pasadas a la nota de la Tabla 4; la tabla de φ′s del ejemplo pasa al suplemento (Tabla S2) y la antigua Tabla 5 pasa a ser la Tabla 4.
- Verificado: 45 referencias, todas citadas, y todas las citas con su referencia; orden alfabético correcto; anonimización limpia (sin nombres, sitio ni años del proyecto; metadatos sin autor).
- Corregido de paso: la nota de la Tabla 3 decía «about 3°» y el texto «2–4°». Además, **u** va en negrita, *e* en cursiva y la comparación de búsquedas lleva 3 decimales (1.209 frente a 1.205).

## Errores propios corregidos en esta ronda

- El perfil tenía φ′∞ = 24° duplicado (archivo de prueba); se deduplicó en `unir` y se relanzó el MCMC (φ′∞ medio 24.3° → 24.4°).
- El docstring de `generar_yaml_lepsp5.py` decía τ_D = 0.084 para `tau r3`; el valor es 0.049.
- PLAN_RONDA4: IC de τ 0.042–0.107 (decía 0.043).

## Pendiente del usuario

Autores y afiliaciones, año de Slide2, DOI del repositorio, agradecimientos y declaración de uso de IA, y el consentimiento escrito del dueño de los datos.
