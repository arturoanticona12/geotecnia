# Douglas (2002), capítulo 4 «The Shear Strength of Rockfill»: resumen

**Fuentes:** `2002_Douglas_The Shear Strength of Rock Masses_Cap4.pdf` (64 páginas, pp. 4.1–4.64) y `..._Index.pdf` (portada, resumen e índices).
Douglas, K. J. (2002). *The shear strength of rock masses* [Tesis de doctorado]. School of Civil and Environmental Engineering, The University of New South Wales, Sídney. https://doi.org/10.26190/unsworks/21014 (el DOI viene de la hoja Info de la base de Cylwik).

**Qué no está en los PDF entregados:**
- La lista de referencias de la tesis.
- El Apéndice F («Shear strength of rockfill database»), que iba en CD-ROM según el índice (Index, p. viii).

Por eso, las referencias completas de abajo vienen de la base de Cylwik (columna `Reference.1`) o de la lista de referencias de Ovalle et al. (2020), según se indica en cada caso.

**Páginas verificadas en imagen** (`paginas\Douglas2002\`): 4.13, 4.20–4.26, 4.28, 4.40–4.42, 4.55, 4.58 y 4.62.

## Base de datos de Douglas (sección 4.4, pp. 4.26–4.28)

- **Tamaño:** más de 989 triaxiales de 307 sets. Vienen de publicaciones y de informes no publicados de organizaciones que ensayaron para presas.
- **Ensayos descartados:** los de velocidad de deformación muy alta y aquellos en que se alcanzó el límite de deformación del equipo antes del máximo.
- **Rangos (Tabla 4.7):**
  - diámetro de probeta: 50.8–1130.3 mm (promedio 332 mm);
  - dmax: 4.8–200 mm (promedio 59 mm);
  - finos: 0–45 % (40 % de los ensayos sin finos; 80 % con ≤ 5 %);
  - Cu: 1.3–3243;
  - UCS: 25–761 MPa (promedio 153 MPa).
- **Litologías:** 18.7 % basalto, 14.9 % granito, 8.2 % arenisca y 3.9 % caliza.
- **Angularidad:** 49 % de las muestras son angulares (rating 8).
- **Rango de esfuerzos:** según las Figs. 4.42 y 4.43 (p. 4.55), **σ′3 va de ≈ 0 a ≈ 4.5 MPa** y σ′1 llega a ≈ 22 MPa. Hay grupos de datos en σ′3 ≈ 2.0–2.1, 2.4–2.5, 2.8–2.9, 3.1, 3.45, 3.8 y 4.48 MPa. En la Fig. 4.21, σn llega a unos 7–10 MPa.
- **Coincide con la base de Cylwik:** los parámetros registrados (Tabla 4.6: Case, Reference, Set, Test, Site, Origin, Type, UCS, Ang, Ang rat, Ds, Hs, Fines, dmin, d10…d90, dmax, cu, cc, Grav, rd, γd, emin, emax, ei, n, Bg, Gs, w, S, σ′3, σ′1, εaf, εvf, Brit) son prácticamente las columnas de Cylwik, y la hoja Info de Cylwik dice que se construyó sobre Douglas (2002) y Ovalle (2020). **Lo más probable es que la base de Douglas ya esté incorporada en Cylwik** (938 filas frente a 989).
- **Supuestos para completar datos (p. 4.29–4.30):**
  - UCS estimado en grupos de 40, 100 y 200 MPa;
  - dmin estimado cuando venía como «menor que»;
  - e calculado con e = n/(1 − n), con Dr o con e = Gs·γw/γd − 1, usando Gs = 2.7 si faltaba.

## Modelo de resistencia propuesto

### 1. φsec–σn (sección 4.5.2.2, p. 4.40). Ajuste pobre, el autor no lo recomienda

φ′ = a + b·σ′n^c  (4.20)

- a = 36.43 − 0.267·ANG − 0.172·FINES + 0.756·(cc − 2) + 0.0459·(UCS − 150)  (4.21)
- b = 69.51 + 10.27·ANG + 0.549·FINES − 5.105·(cc − 2) − 0.408·(UCS − 150)  (4.22). En la imagen aparece un «-0.408» suelto al final de la ecuación; parece un error tipográfico.
- c = −0.3974  (4.23)

Las variables son:
- ANG = rating de angularidad − 5 si el rating es > 5.5; si no, 0;
- FINES = % que pasa 0.075 mm;
- cc = coeficiente de curvatura;
- UCS en MPa.

El ajuste explica el 61.7 % de la varianza. Añadir cu, dmax o dmin no mejoró el ajuste.

### 2. σ′1–σ′3 («RFI», sección 4.5.3, p. 4.41). Es el criterio recomendado

σ′1 = RFI · σ′3^α  (4.24), con esfuerzos en MPa.

- **Base completa (988 datos):** RFI = 4.7002 y α = 0.8972 (varianza explicada 97.13 %).
- **Modelo con parámetros (869 datos, varianza explicada 98.82 %):** α = 0.8726 y
  RFI = 6.3491·RFI_e + 0.48763·RFI_ANG − 0.0027·RFI_dmax − 1.1568·RFI_FINES + 0.30598·RFI_UCS  (4.25)
  - RFI_e = 1/(1 + e_i)  (4.26)
  - RFI_ANG = 1 si es angular (rating 8); si no, 0  (4.27)
  - RFI_dmax = dmax en mm  (4.28). El coeficiente es negativo, así que la resistencia baja con dmax. El texto de p. 4.42 dice «proporcional», pero la Fig. 4.40 y la Tabla 4.8 muestran que disminuye.
  - RFI_FINES = e^(F−20)/(1 + e^(F−20)), F en %  (4.29): es un escalón suave en 20 % de finos.
  - RFI_UCS = e^(UCS−110)/(1 + e^(UCS−110)), UCS en MPa  (4.30): es un escalón suave en 110 MPa.
- **Bandas aproximadas (p. 4.45, Fig. 4.42):** RFI = 7 (superior), 4.7 (mejor estimación) y 3 (inferior).
- **Conversión a φsec y σn (p. 4.58):**
  - φsec = sin⁻¹[(RFI·σ′3^α − σ′3)/(RFI·σ′3^α + σ′3)]  (4.31)
  - σn = cos φsec · √(RFI·σ′3^(α+1))  (4.32)
- **Sensibilidad (Tabla 4.8, p. 4.58):** caso base con UCS 100 MPa, ANG 7, 0 % de finos, dmax 60 mm y e 0.4. Cambio de φsec a σn = 0.1 / 0.5 / 1 MPa:
  - UCS de 50 a 200 MPa: +1.3 / +1.4 / +1.5°;
  - angularidad 8: +2.1 / +2.2 / +2.3°;
  - 20 % de finos: −2.8 / −3.1 / −3.4°;
  - dmax de 50 a 200 mm: −2.2 / −2.1 / −2.1°;
  - e de 0.2 a 0.6: −6.4 / −9.1 / −9.5°.
- **Diámetro de probeta:** los residuos no muestran tendencia con el diámetro hasta unos 1.2 m (Fig. 4.36). El autor concluye que la gradación paralela es válida, salvo que el escalamiento aumente los finos.

### 3. Hoek-Brown con s = 0 (sección 4.5.4, pp. 4.61–4.62, Tabla 4.9)

| Forma | Datos | mb | a | Var. expl. |
|---|---|---|---|---|
| σ′1 = σ′3 + σc(mb σ′3/σc)^0.6 | 405 (σci conocido) | 0.42929 | 0.6 (fijo) | 88.95 % |
| σ′1 = σ′3 + σc(mb σ′3/σc)^a | 405 | 2.40706 | 0.89999 | 97.40 % |
| σ′1/σc = σ′3/σc + (mb σ′3/σc)^0.6 | 405 | 0.75486 | 0.6 (fijo) | 90.93 % |
| σ′1/σc = σ′3/σc + (mb σ′3/σc)^a | 405 | 2.71833 | 0.94877 | 98.73 % |
| σ′1 = σ′3 + σc(mb σ′3/σc)^a | 988 (σci estimado si falta) | 2.39551 | 0.8954 | 97.42 % |

**Conclusión del autor:** para el enrocado, a ≈ 0.90–0.95. Con a = 0.6 se sobrestima σ′1 a σ′3 bajo y se subestima a σ′3 alto.

## Otros criterios revisados (Tabla 4.5, pp. 4.19–4.25)

- **De Mello (1977) / Charles y Watts (1980):** τ = A·σn^B. Charles (1991) da A y B para grava arenosa y enrocado blando (Tabla 4.4).
- **Indraratna et al. (1993) e Indraratna (1994):**
  - forma τ/σc = a(σn/σc)^b, con a,b = 0.25/0.83 (inferior) y 0.71/0.84 (superior) para σn = 0.1–1 MPa, y **0.75/0.98 y 1.80/0.99 para σn = 1–7 MPa**;
  - forma σ′1/σc = α(σ′3/σc)^β, con α,β = 0.4/0.62 y 0.78/0.65 para 0.1–1 MPa, y **2.71/0.96 y 3.58/0.90 para 1–7 MPa**.
- **Sarac y Popovic (1985):** τmax = A(σn/σ0)^B, con σ0 = 1 MPa, A ≈ 0.7–1.5 y B ≈ 0.419–0.911. Sale de corte directo de gran escala, con σn hasta 2 MPa.
- **Indraratna et al. (1998), para balasto:** σ′1/σ′3 = a·σ′3^b.
- **Doruk (1991):** Hoek-Brown con s = 0.
- **Barton y Kjærnsli (1981):** φ′ = R·log(S/σn) + φb.
- **Charles (1991):** φ′ = C1·log(C2/σ′3) + φb.
- **González (1985):** φ′ = φ0 − j·log10(σnf/σc0), con NR función de Cu, rotura y e (Fig. 4.16).

## Fuentes de datos de alta presión que menciona el capítulo

Criterio: σ′3 ≥ 2 MPa, o σn alto cuando solo se da σn.

| Fuente citada en Douglas | Qué dice Douglas | Página | ¿En Cylwik? | Referencia completa (origen) |
|---|---|---|---|---|
| Marachi et al. (1969) | Triaxiales de gran escala en argilita, basalto chancado y anfibolita redondeada; φ no baja mucho más allá de σn = 4.5 MPa; σ3 hasta 4.5 MPa | 4.4, 4.10–4.11 | Sí, como Marachi et al. (1972): 36 ensayos con σ3 hasta 4.48 MPa, 18 con ≥ 2 MPa | Marachi, N. D., Chan, C. K., Seed, H. B. y Duncan, J. M. (1969). *Strength and deformation characteristics of rockfill materials* (Rep. No. TE-69-5). Dept. of Civil Engineering, Univ. of California, Berkeley. (lista de Ovalle 2020) |
| Marsal (1973) | Basalto con σn = 0.8 / 1.6 / 3.9 MPa (Tabla 4.1); conglomerado silicificado y gneis granítico con σn = 3.92 MPa (Tabla 4.2) | 4.13 | Sí: 68 ensayos con σ3 hasta 2.46 MPa | Marsal, R. J. (1973). Mechanical properties of rockfill. En *Embankment-dam engineering: Casagrande volume* (pp. 109–200). Wiley. (Cylwik) |
| Marsal (1967) | Citado por el efecto de cu (vía Chiu 1994) y de la humedad | 4.8, 4.17 | **No** como referencia. El basalto de Infiernillo de Marsal (1967) tampoco está (sí está en Ovalle 2020, con σ3 hasta 2.55 MPa) | Marsal, R. (1967). Large-scale testing of rockfill materials. *J. Soil Mech. Found. Div.*, 93(2), 27–43. (lista de Ovalle 2020) |
| Indraratna et al. (1993) e Indraratna (1994) | Bandas para σn = 1–7 MPa (Tabla 4.5); envolvente casi lineal por encima de 1.5 MPa | 4.4, 4.20 | Indraratna et al. (1993) sí, pero solo 12 ensayos con σ3 ≤ 0.6 MPa. Las bandas de 1–7 MPa salen de datos que no están en Cylwik con esa referencia. **Indraratna (1994) no está** | Indraratna, B., Wijewardena, L. y Balasubramaniam, A. (1993). Large-scale triaxial testing of greywacke rockfill. *Géotechnique*, 43(1), 539–543, https://doi.org/10.1680/geot.1994.44.3.539 (tal como aparece en Cylwik y en Ovalle 2020; el volumen y el DOI no son coherentes entre sí, hay que verificarlo). **Indraratna (1994): referencia completa no disponible en los PDF** |
| Al-Hussaini (1983) | Basalto chancado denso y medio denso, triaxial y deformación plana (Fig. 4.2) | 4.5, 4.10, 4.17 | Sí: 40 ensayos con σ3 hasta 3.1 MPa, 20 con ≥ 2 MPa, D ≤ 305 mm | Al-Hussaini, M. (1983). Effect of particle size and strain conditions on the strength of crushed basalt. *Can. Geotech. J.*, 20(4), 706–717. (Cylwik) |
| Base propia de Douglas (Apéndice F, CD-ROM) | 989 ensayos con σ′3 hasta ≈ 4.5 MPa (Fig. 4.42) | 4.26, 4.55 | Probablemente sí, porque Cylwik declara que se basa en ella | No disponible: el CD-ROM no está en los PDF |
| Sarac y Popovic (1985); Anagnosti y Popovic (1982) | Corte directo de gran escala, σn hasta 2 MPa (no es triaxial) | 4.5, 4.7, 4.19–4.24 | No | **Referencias completas no disponibles en los PDF** |

En el capítulo, Becker et al. (1972) (arenisca Venato) aparece solo en la leyenda de la Fig. 4.12 de Thiers y Donovan (1981), p. 4.13. Sus 4 ensayos, con σ3 hasta 4.48 MPa, no están en Cylwik, pero sí en el xlsx de Ovalle 2020.

## ¿Hay tablas con datos de σ3 ≥ 2 MPa que no estén en Cylwik?

**No.** Las únicas tablas numéricas del capítulo son:
- Tabla 4.1 y Tabla 4.2: diferencias porcentuales de φ derivadas de Marsal (1973), no son ensayos;
- Tabla 4.4: parámetros de De Mello según Charles (1991);
- Tablas 4.5, 4.8 y 4.9: criterios y ajustes.

Los ensayos individuales están en el Apéndice F (CD-ROM), que no se entregó. Por eso **no se creó un CSV por ensayo para Douglas**.

## Dudas

1. **Bandas de Indraratna para σn = 1–7 MPa:** la Tabla 4.5 las cita, pero Cylwik solo tiene ensayos de Indraratna hasta σ3 = 0.6 MPa. Hay que revisar en Indraratna et al. (1993) y en Indraratna (1994) de qué datos de alta presión salen (probablemente de una compilación de literatura).
2. **Referencias completas:** la lista de referencias de la tesis no está en los PDF entregados. Para Indraratna (1994), Sarac y Popovic (1985) y Anagnosti y Popovic (1982) hace falta el capítulo de referencias.
3. **Apéndice F:** conviene conseguirlo (UNSWorks, DOI 10.26190/unsworks/21014) para confirmar que Cylwik lo contiene completo. La diferencia es de 989 frente a 938 filas, y Cylwik además incluye fuentes posteriores a 2002.
4. **p. 4.13:** el texto habla de un aumento de φ de «3–4 %» y de «0.3°», mientras que la Tabla 4.1 está en %. La inconsistencia es del original.
