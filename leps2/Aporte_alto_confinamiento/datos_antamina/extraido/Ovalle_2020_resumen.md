# Ovalle et al. (2020): resumen de extracción

**Fuente:** `2020_Ovalle_Data Compilation from Large ICDTx on Coarse Crushable Rockfill Materials.pdf` (8 páginas, la primera es la portada de ResearchGate).
Ovalle, C., Linero, S., Dano, C., Bard, E., Hicher, P.-Y. y Osses, R. (2020). Data compilation from large drained compression triaxial tests on coarse crushable rockfill materials. *Journal of Geotechnical and Geoenvironmental Engineering*, 146(9), 06020013. https://doi.org/10.1061/(ASCE)GT.1943-5606.0002314

**Repositorio de datos (p. 6, «Data Availability Statement»):** https://doi.org/10.5281/zenodo.3625778. Es el registro Zenodo «Database rockfills», v1 del 23-01-2020, con licencia CC BY 4.0 y un único archivo, `Ovalle et al. 2020 - Database rockfills.xlsx` (26.7 kB). Lo descargué el 2026-10-06 en `..\fuentes_externas\Zenodo_3625778\`.

## Qué trae el artículo y qué trae el repositorio

- **El artículo no tiene tabla de ensayos.** Solo incluye la lista de los 33 materiales con su litología, dmax y referencia original (leyenda de la Fig. 2a, p. 4, verificada en la imagen), la Tabla 1 con arenas y balastos (no son enrocados, por eso no se extrajo) y figuras: φmax–σ′n (Fig. 2b), Bg–σ′3 y φmax–Bg (Fig. 3), E50 (Fig. 4) y K50 (Fig. 5). Las figuras no se digitalizaron.
- **El xlsx de Zenodo trae los 158 ensayos.** Cada uno tiene material, descripción, dmax, referencia, diámetro de probeta, e0, σ3, σ1 máximo, φmax, E50, Bg y Cu inicial. **El CSV `Ovalle_2020.csv` sale de este archivo** (una fila por ensayo, `ensayo_id` = N° del xlsx). Los valores numéricos no están en el PDF, por eso `verificado_imagen` = «no». Lo que sí verifiqué contra la imagen de la p. 4 es el nombre, la litología y el dmax de cada material.
- No hay granulometrías por ensayo (solo Cu), ni Gs, γd, w, deformaciones ni UCS.
- **Columnas de litología (según el esquema actualizado):**
  - `litologia_informe` es la descripción del xlsx sin cambios;
  - `litologia` es el tipo de roca de la fuente, traducido (Granodiorita, Pórfido, Basalto, Mármol…);
  - dos materiales son mezclas sin proporción («Felsic and andesite» y «Schist and mica-schist»): van como «Mezcla», con `litologia_proporcion` = «no indicada»;
  - Oroville solo trae su mineralogía, así que va como «Otra: no indicada». No adopté la «anfibolita» de Cylwik porque no está en esta fuente;
  - `alteracion` se llenó solo cuando la fuente lo dice: «Altered granite», los materiales «Leached» (lixiviados) y Pilbara (meteorizado, p. 3).
- **Columna `tipo_material`:**
  - solo se asignó ROM, Chancado o Enrocado cuando el nombre de la fuente lo dice (ROM, Crushed o Rockfill);
  - en el resto quedó vacía, con el nombre original en `notas`.

## Laboratorios y materiales (p. 3)

- **Reparto por laboratorio:** 14 materiales en IDIEM (Chile; cámara de 1000 × 1800 mm, σ3 hasta 3 MPa), 3 en ECN (Francia; 1000 × 1500 mm, σ3 hasta 1.5 MPa), 4 en UC Berkeley y 12 en CFE (México).
- **Asignación de cada material a su laboratorio:** la inferí yo a partir de esos totales y de las referencias. Así lo dice la columna `laboratorio`.
- **Materiales nuevos de este trabajo:**
  - Pilbara: desmonte minero chancado de Australia Occidental, ensayado en IDIEM.
  - ANR Pedra: granito chancado lavado.
  - Ste. Cécile d'Andorge: esquisto y micaesquisto subangular.
- **Condición de humedad:** hay muestras saturadas y secadas al aire, pero el xlsx solo marca «(dry)» en los materiales de CFE. En el resto, `saturado` = «no indicado».

## Envolventes y ajustes que da el artículo

| Ec. | Expresión | Página |
|---|---|---|
| (1) Leps (1970) / Indraratna et al. (1993) | φmax = −2.8 ln σ′n + φ1 (σ′n en MPa). φ1 = 36° (bajo), 41° (medio) y 46° (alto) según Leps; 33° es el límite bajo de Indraratna | p. 3 |
| (2) Nuevo límite inferior | φmax = −5.6 ln σ′n + 32 si σ′n ≤ 0.7 MPa; φmax = −2.8 ln σ′n + 33 si σ′n > 0.7 MPa | p. 5 |
| (3) Módulo | E50 = K50 · pa · (σ′3/pa)^n, con pa = 0.1 MPa. Para enrocados, K50 = 100–200, el rango de las arenas sueltas (Fig. 5) | p. 5–6 |

**Conclusiones (p. 6):**
- Con σ′n < 0.2 MPa, φmax supera los 45°.
- A presión alta, φmax baja a 30–40°.
- A los niveles de esfuerzo más altos no se observa un φ crítico constante.

**Otros ensayos:** el artículo no trae ensayos índice (UCS, Los Ángeles), permeabilidad, edómetros ni ensayos no drenados.

## Comparación con la base de Cylwik et al. (2025) / Arrieta (2025)

**Cómo se compararon:**
- En la base de Cylwik, la referencia «Ovalle et al. (2020)» tiene solo **10 ensayos**: los de los tres materiales nuevos (ANR Pedra 3, Ste. Cécile 3 y Pilbara 4).
- Los ensayos de CFE y UCB entran en Cylwik por sus fuentes originales: Marsal et al. (1965), Marsal (1973), Marachi et al. (1972) y Ovalle et al. (2014).
- Busqué cada ensayo del xlsx en Cylwik por σ3 y σ1 (tolerancias de 3 % y 4 %, diámetro ≥ 800 mm) dentro de la referencia original. En los casos dudosos revisé el set a mano. El resultado por ensayo está en la columna `notas` del CSV.

| Material (dmax mm) | Ref. original | n | σ3 (MPa) | ¿En Cylwik? |
|---|---|---|---|---|
| Infiernillo Rockfill, conglomerado silicificado (200) | Marsal et al. 1965 | 16 | 0.035–2.54 | Sí (sets a, b, d) |
| Infiernillo Cantera 5, diorita (200) | Marsal et al. 1965 | 7 | 0.041–2.54 | Sí (sets c, e) |
| Malpaso, conglomerado (200) | Marsal et al. 1965 | 11 | 0.041–2.54 | Sí (sets f, g) |
| San Francisco grad. 1 y 2, basalto (80 / 180) | Marsal 1973 | 3 + 3 | 0.46–2.42 | Sí (M5, M6) |
| Mica X e Y, gneis granítico (200) | Marsal 1973 | 4 + 3 | 0.45–2.42 | Sí (M11, M12) |
| El Granero A/B, densa/suelta, pizarra (200) | Marsal 1973 | 22 | 0.04–1.66 | Sí (M7–M10), **excepto el N° 128** (A densa, σ3 = 0.09) |
| **Infiernillo (dry), basalto (200)** | **Marsal 1967** | **5** | **0.041–2.55** | **No** |
| Crushed Basalt, Oroville, Pyramid (152) | Marachi et al. 1969 | 12 | 0.207–4.48 | Sí (BL, OL, PL de Marachi 1972) |
| STV, lutita (160) | Ovalle et al. 2014 | 4 | 0.2–0.4 | 3 sí (STV2); **N° 117 no** |
| **Venato, arenisca (152)** | **Becker et al. 1972** | **4** | **0.207–4.48** | **No** |
| ANR Pedra, Ste. Cécile, Pilbara | este trabajo | 10 | 0.1–2.0 | Sí |
| **13 materiales chilenos de IDIEM** (detalle abajo) | Linero 2007; Palma 2009; Dorador 2010; Contreras 2011; Bard 2012; Besio 2012 | **54** | 0.098–2.5 | **No** (ninguna de esas referencias está en Cylwik) |

### Ensayos de Ovalle que no están en Cylwik

Son **65 ensayos en total**: 37 con σ3 ≥ 1.0 MPa y 16 con σ3 ≥ 2.0 MPa.

| Material | Litología | Lab. | n | σ3 (MPa) | n con σ3 ≥ 1 MPa | φmax (°) | e0 | Cu |
|---|---|---|---|---|---|---|---|---|
| CAD waste Truncated GSD (Linero 2007) | granodiorita | IDIEM | 3 | 1.0–2.5 | 3 | 36–40 | 0.36–0.44 | 9 |
| CAD waste Parallel PSD (Linero 2007) | granodiorita | IDIEM | 5 | 0.1–2.0 | 2 | 32–51 | 0.34–0.45 | 16 |
| Andina waste rock 1 (Palma 2009) | granodiorita | IDIEM | 4 | 0.8–2.5 | 3 | 37–40 | 0.33–0.39 | 30 |
| Andina waste rock 2 (Palma 2009) | pórfido | IDIEM | 4 | 1.0–2.5 | 4 | 42–46 | 0.32–0.37 | 8 |
| Rancagua rockfill (Dorador 2010) | andesita | IDIEM | 3 | 0.39–1.57 | 1 | 36–36.8 | 0.414 | 4.4 |
| Leached rockfill (Dorador 2010) | granito alterado | IDIEM | 3 | 0.785–2.45 | 2 | 41.9–42 | 0.486 | 91 |
| Natural waste rock (Contreras 2011) | félsico y andesita | IDIEM | 5 | 0.098–1.96 | 1 | 36–51.7 | 0.50 | 17.4 |
| Leached waste rock (Contreras 2011) | félsico y andesita | IDIEM | 4 | 0.196–2.45 | 2 | 35.5–41.8 | 0.45 | 17.5 |
| Crushed waste rock (Contreras 2011) | félsico y andesita | IDIEM | 3 | 0.981–2.45 | 2 (+1 a 0.981) | 37–41.6 | 0.45 | 9.1 |
| ROM waste rock (Bard 2012) | pórfido | IDIEM | 5 | 0.1–2.0 | 2 | 32.4–51.3 | 0.459 | 9.3 |
| Leached waste rock (Bard 2012) | pórfido | IDIEM | 6 | 0.2–2.5 | 5 | 35.5–41.2 | 0.462 | 16 y 123 |
| Crushed waste rock (Bard 2012) | pórfido | IDIEM | 4 | 1.0–2.5 | 4 | 36.8–41.9 | 0.33–0.46 | 9.06 |
| **Black marble (Besio 2012)** | **mármol** | IDIEM | 5 | 0.49–1.96 | 2 | 35.7–39.7 | 0.293 | 34.4 |
| Venato (Becker et al. 1972) | arenisca | UCB | 4 | 0.207–4.48 | 2 | 36–40.2 | 0.46–0.54 | 7 |
| Infiernillo (dry) (Marsal 1967) | basalto | CFE | 5 | 0.041–2.55 | 2 | 31–60.1 | 0.30 | 19 |
| STV, N° 117 (Ovalle 2014) | lutita | ECN | 1 | 0.3 | 0 | 41.1 | 0.59 | 3.8 |
| El Granero A densa, N° 128 (Marsal 1973) | pizarra | CFE | 1 | 0.09 | 0 | 50.5 | 0.49 | 10 |

**Por qué importan para Antamina:**
- **Aportan a alto confinamiento:** los desmontes chilenos de IDIEM (ROM, lixiviados y chancados de pórfido, granodiorita y andesita, en probetas de 1 m con dmax de 150–200 mm y σ3 hasta 2.5 MPa) y Venato (σ3 hasta 4.48 MPa).
- **Black marble (Besio 2012) es el único mármol de toda la compilación.** Tiene dmax de 178 mm y σ3 de 0.49–1.96 MPa, y es directamente relevante para los desmontes de mármol de Antamina.

## Dudas y observaciones

1. **Posible duplicación entre fuentes chilenas.** «CAD waste Parallel PSD» (Linero 2007) y «ROM waste rock» (Bard 2012) tienen σ3, σ1 y Bg prácticamente iguales: 0.1/0.73 frente a 0.1/0.81; 2.0/6.6 frente a 2.0/6.61; Bg 6.4/7.7/9.4/13.6/15 frente a 6.3/7.6/9.4/13.6/15. «CAD waste Truncated» (Linero 2007) y «Crushed waste rock» (Bard 2012) se parecen mucho (σ1 de 4.5/8.0/10.0 frente a 4.55/8.0/9.99). Los dos conjuntos de Contreras (2011) también se parecen a los de Bard (2012). Podrían ser los mismos ensayos reportados en dos publicaciones. Hay que revisarlo antes de sumarlos a la base, para no contar dos veces el mismo dato.
2. **Pyramid Dam con σ3 = 0.965 MPa:** Zenodo da σ1 = 4.415 MPa (φ = 39.9°, consistente con ese σ1), pero Cylwik (Marachi 1972, PL, case 381) da 3.46 MPa. Uno de los dos tiene un error de transcripción. Hay que verificarlo en Marachi et al. (1969/1972).
3. **Venato N° 120:** el xlsx da un diámetro de 130 mm, distinto de los 914.4 mm del resto. Probablemente es un error del xlsx.
4. **Leached waste rock (Bard 2012):** los ensayos N° 108–109 tienen Cu = 123 y el resto Cu = 16. Parece otra granulometría dentro del mismo «material».
5. **Diferencias de cobertura entre los sets de Marsal 1973:** Cylwik tiene un ensayo a σ3 ≈ 2.4 MPa en M7 (El Granero) y en M12 (Mica Y) que el xlsx de Ovalle no incluye. Al revés, el xlsx tiene σ3 = 0.09 MPa en El Granero A densa, que Cylwik no tiene.
6. **El país y el yacimiento de los materiales chilenos no se indican.** No se completó el origen.
7. **σ3 = 0.981 MPa (1 kgf/cm²)** no se contó como ≥ 1 MPa.
8. **φmax** es el ángulo secante máximo informado en el xlsx, sin cohesión. **q** está calculado como σ1 − σ3.
