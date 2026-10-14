# Cuarta ronda de revisores (2026-10-07): respuestas

Recomendaciones:
- **Revisión menor:** editor ASCE, estabilidad y confiabilidad.
- **Menor cercana a mayor:** mecánica de enrocados.
- **Mayor de alcance acotado:** estadística.

## Decisiones del usuario
- Reestructurar el modelo para que cada material tenga su envolvente acotada.
- τ del efecto de escala conservador: 0.063.
- Estabilidad **solo en Slide2 y solo con Morgenstern–Price**.
- Autorización para avanzar con criterio propio durante la noche.

## Respuestas

| Revisor | Pedido | Respuesta | Archivo |
|---|---|---|---|
| Mecánica | La asíntota no es φ′cs; cada envolvente individual seguía como ley de potencia | Efectos aleatorios en (η, ζ) de cada material; asíntota renombrada φ′∞ y descrita como parámetro de decaimiento. ML +3.8 frente al modelo de la ronda 3 y +9.8 frente a la cuadrática; sin asíntota, −44.7; φ′∞ = 24.6° (25° en el óptimo) | `lepsp_acotada2.py`, `lepsp_mcmc4.py` |
| Mecánica | Ensayos a alta tensión limitados por deformación; Bg como covariable | Deformación volumétrica en la falla: −6.9 % sobre 3 MPa, 99 % contractivas. Bg sin relación con los residuos (ρ = 0.00). Se excluyen 4 Bg > 100 % (imposibles). Fig. S2 | `lepsp_diag_alta.py` |
| Mecánica | Extrapolación en e; dominio de validez | Dominio declarado: σ′n ≤ 8 MPa; e ≤ 0.55 sobre 3 MPa. Celdas extrapoladas marcadas en la Tabla 3 | manuscrito |
| Mecánica | Transferir βe a la densidad de colocación | Declarado como supuesto | manuscrito |
| Estadística | «Prespecified» falso | Eliminado; el modo B se presenta como exploratorio. **Error propio reconocido** | manuscrito |
| Estadística | Multiplicidad; bootstrap con pocos grupos | Prueba exacta de signo invertido y ajuste de Holm. Ninguna diferencia es significativa en los modos A ni B | `lepsp_cv4_metricas.py` |
| Estadística | Procedimiento validado ≠ recomendado | Validado el procedimiento recomendado (descarte + laboratorio común): «sitio» | `lepsp_cv4.py` |
| Estadística | Sobredispersión del modo B por un error de código | Corregido: la actualización también reduce la incertidumbre de los efectos fijos. Cobertura 83 % (nominal 80 %), sd(z) 0.91 | `lepsp_cv4.py`, `leps3/lepsp.py` |
| Estadística | Previa de la cresta | Sensibilidad con previa uniforme en tan φ′∞: 24.6°, igual | `lepsp_mcmc4.py` |
| Estadística | Predictiva desplegada ≠ validada | Diferencia de la mediana ≤ 0.005; DE 1.03–1.09×; la librería usa la misma regla que el modo B | `lepsp_desplegada.py` |
| Estadística / confiabilidad | τ del efecto de escala | τ = 0.063 (IC Q-profile 0.042–0.107; corregido en la ronda 5, decía 0.043); 0.049 como sensibilidad; la media sigue sin efecto | `lepsp_escala3.py` |
| Confiabilidad | Laboratorio heredado por D y E | Sensibilidad con laboratorio independiente: 0.2–0.3° | `a8 --lab-indep` |
| Confiabilidad | Agregación por tipo de roca | Un material por tipo de roca | `a8_lepsp_sitio.py` |
| Confiabilidad / estabilidad | Separar densidad y escala | Escenarios con solo densidad, solo escala, ambos y ninguno (también en Slide2) | `a8`, `generar_yaml_lepsp4.py` |
| Estabilidad | Motivación frente al ejemplo; formato EC7 sin FS objetivo | Introducción y diseño reescritos; doble conteo «parcial»; sin FS objetivo | manuscrito |
| Estabilidad | Solo Slide2 con M–P (usuario) | Lote 64: determinístico. Lote 66: Monte Carlo de 600 realizaciones por caso, cada una con búsqueda propia | `slide2/` |
| Editor | Extensión, figuras, notación, orden de citas | 4 figuras en el cuerpo y 4 en el suplemento; notación completa; Tabla 2 por bloques; título nuevo; anonimización por clase | `build_lepsp_asce4.py`, `figuras_lepsp4.py` |

## Resultados que cambian el mensaje del artículo
- **Fuera de muestra, las formas no se distinguen.** La evidencia a favor de la forma acotada es por verosimilitud y por coherencia mecánica.
- **Ensayos del sitio:** la actualización da predicciones calibradas, pero su ventaja frente a ajustes simples no es significativa con 13 publicaciones.
- **Escala de campo:** el efecto de tamaño domina la incertidumbre (≈ 60 % de la varianza) bajo el modelo adoptado.
