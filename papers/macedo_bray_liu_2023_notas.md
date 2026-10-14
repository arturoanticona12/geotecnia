# Macedo, Bray & Liu (2023): notas de lectura

**Referencia:** Macedo, J., Bray, J. D., y Liu, C. (2023). *Seismic Slope Displacement Procedure for Interface and Intraslab Subduction Zone Earthquakes*. J. Geotech. Geoenviron. Eng., 149(11): 04023104. DOI: [10.1061/JGGEFK.GTENG-11445](https://doi.org/10.1061/JGGEFK.GTENG-11445)

> El PDF original tiene copyright de ASCE, por eso no se incluye en este repositorio público. Aquí solo van notas propias.

## Idea general

- Son modelos semiempíricos de desplazamiento sísmico de taludes (D) para sismos de subducción **interfase** e **intraplaca (intraslab)**. Se basan en la base de datos NGA-Sub (6 240 registros de interfase y 8 299 de intraslab).
- El bloque deslizante es el modelo acoplado, no lineal y deformable de Rathje y Bray (2000), con las mejoras de Bray et al. (2018) (BMT18).
- La forma es de variable aleatoria mixta, como en Bray y Travasarou (2007):
  f_D(d) = P · δ(d − 0.5) + (1 − P) · f_D(d > 0.5 cm)
- BMT18 se desarrolló solo con sismos de interfase y **no debe usarse para intraslab**.

## Ecuaciones

1. **P(D = 0)**, con D ≤ 0.5 cm (regresión logística, Ec. 2):
   ln[P/(1−P)] = c1 + c2·ln ky + c3·(ln ky)² + c4·Ts·ln ky + c5·Ts + c6·ln Sa(1.3Ts)
   (Tabla 1, con coeficientes separados para Ts ≤ 0.6 s y Ts > 0.6 s)
2. **D > 0.5 cm**:
   - Escalar (Ec. 3a): usa ky, Sa(1.3Ts), Ts y Mw.
   - Vectorial (Ec. 3b): agrega a9·ln(PGV). El escalar "underestimates D significantly" cuando PGV > 40 cm/s (interfase) o PGV > 20 cm/s (intraslab), y el vectorial elimina ese sesgo (p. PDF 8). a9 = 0.73 si PGV ≥ 10 cm/s (interfase) y 0.72 si PGV ≥ 30 cm/s (intraslab) (nota de la Tabla 3).
   - ε es normal con media 0 y desviación estándar σ (en unidades de ln).

| Modelo | σ interfase | σ intraslab |
|---|---|---|
| Escalar (Tabla 2) | 0.75 | 0.62 |
| Vectorial (Tabla 3) | 0.65 | 0.53 |
| BMT18 (referencia) | 0.73 | — |

3. **Coeficiente pseudoestático compatible con desplazamiento** (Ec. 4a–4d):
   k = exp[(−a + √b) / (−2·a2)], con a = −a1 − a3·ln Sa(1.3Ts)
   b = a² − 4·a2·(a0 + a4·lnSa + a5·(lnSa)² + a6·Ts + a7·Ts² + a8·Mw [+ a9·lnPGV] − ln Da)
   - Se desprecia P(D = 0). Esto es conservador cuando la mediana de D supera unos 5 cm.
   - El talud es aceptable si FS ≥ 1.0 con ese k (FS mínimo = 1.0).

## Dispersión: ¿mediana o una σ?

- El paper indica usar la **mediana (ε = 0)** o el percentil con **16 % de excedencia (ε = +σ)**, es decir, el percentil 84 de D, según el proyecto y las consecuencias.
- Al calcular k con ε = +σ, en la Ec. 4c/4d se reemplaza ln Da por (ln Da − σ). El resultado es un k mayor, más conservador.
- En la validación con casos históricos (Tabla 4), los rangos de D se reportan entre el 16 % y el 84 % (mediana ± 1σ).
- Mediana·e^σ ≈ 2.1× (escalar, interfase), 1.9× (escalar, intraslab), 1.9× (vectorial, interfase), 1.7× (vectorial, intraslab).

## Uso práctico

1. Mw: magnitud desagregada del PSHA para el periodo de retorno de diseño.
2. Sa(1.3Ts): del espectro de peligro uniforme (o de los GMM) para la fuente que controla.
3. PGV: condicionada a Sa(1.3Ts), por ejemplo con Liu y Macedo (2022).
4. ky y Ts: de análisis de estabilidad y ensayos geofísicos (Ts ≈ 4H/Vs).
5. Hay que usar el modelo que corresponde a cada fuente: interfase o intraslab. En el Perú andino el peligro suele estar dominado por sismos intraslab (Fig. 1).
