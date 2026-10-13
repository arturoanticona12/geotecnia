# Estado: Leps 2.0 a alto confinamiento   (actualizado: 2026-10-13)

Reconstruido al migrar el proyecto de Drive al repo; revisar y corregir lo que no coincida con tu memoria.

## Pendiente (en orden)
1. **Memo EoR, ajuste en dos pasos (pedido de WA):** a30 ya corrió; falta decidir con el usuario si se adopta antes de
   tocar a12, la planilla (a28) y el memo. Ver «Datos y valores clave».
2. Incorporar los comentarios de WA (`eor_antamina/curva_leps2_antamina_rev3_comentarios_WA.pdf`, `_1210wa.pdf`).
3. **Artículo HiBER r6:** cerrar las brechas de `manuscrito/PLAN_RONDA6.md` que sigan abiertas; revisión visual final.
4. Pendientes del artículo sin resolver: autores y afiliaciones, DOI del repositorio, año de la versión de Slide2,
   autorización del propietario de los datos.

## En curso
- Nada corriendo en la nube. Lotes de Slide2 se corren en el PC.

## Decisiones tomadas (no volver a discutir)
- Modelo renombrado **HiBER** (antes Leps-P), 2026-10-07.
- Memo: m común para los sets de Antamina (pedido de WA), en vez de una m por set como Cylwik.
- Regla de diseño del Modo B: sobre la σ′n máxima del sitio, el menor entre el percentil actualizado y el de la previa.
- Curva vigente del memo: φ′e=0 = 48.10°, ω = 20°, m = 0.859, e base 0.45.

## Datos y valores clave
- a30 (`analisis_antamina/a30_dos_pasos.json`): paso 1 con w = 0 da m = 1.00 (límite); bootstrap m 0.89–0.97.
  Paso 2: ω = −4.2°, IC 90 % [−23°, +39°] → **no adoptable** por el criterio (15–25°, ±10°).
  Con la base mundial (217 sets, 50/50): ω = 9.3°, φ′e=0 Antamina = 44.6°.
- Curva vigente: φ′s = 39.2° (1 MPa), 33.3° (4.6 MPa), 30.5° (10 MPa), 29.0° (15 MPa).
- HiBER r6: MC 0/600 fallas (β_LN 3.2); Pf integrada sobre τ_D 4.6e-3 (β 2.6); manuscrito 30 p., suplemento 8 p.

## Preguntas abiertas
- ¿Se mantiene ω = 20° en el memo, dado que el ajuste propio de Antamina no identifica ω? (para WA)

## Hecho (reciente)
- 2026-10-13 (3): revisión por tres revisores senior (Stantec, Piteau, Antamina) de la sec. 2.2 y el Anexo B. Aplicado:
  matriz de cobertura ensayo × litología con n y fracción en masa LE2 (Tabla 2 nueva); REG 41061 = mármol; Los Ángeles
  individuales de WSP 2022 y Golder 2012; mármol M-001 de terreno; modelo de bloques = LOM25 (LE1+LE2) con columna LE2
  (≥2035); n de LE2 = 23 860 con cortes; P35 XDP recalculado 70.8 MPa; unidad de n en Tabla 3; citas internas completadas.
  Pendiente para el usuario: rótulo de confidencialidad de Antamina; ponderación por litología de la sec. 5 (DDE) frente a
  MR2024 (caliza y margas 30 % sin ensayos de desmonte).
- 2026-10-13 (2): memo con todo lo disponible por tipo de desmonte. Tabla 2 ampliada (fases A y B de Golder 2010, carga en
  plataforma, LE2 por RMU, Waste-C/Fine/Hard, modelo de bloques MR24, fragmentación) y Anexo B (Tablas B1–B11) con los valores
  por litología, clase o RMU y por muestra, cada uno con su tabla/página de origen. Referencias nuevas: Antamina 2025b (LE2),
  2025c (WSC) y 2024 (MR2024). Memo de 49 p., sin errores ni desbordes. Pendiente menor previo: la última página del Anexo A
  tiene una sola fila.
- 2026-10-13: memo EoR con tabla nueva de ensayos de caracterización (sección 2.2, Tabla 2: granulometría, Gs, absorción,
  densidades, Proctor, edómetros, permeabilidad, Los Ángeles, durabilidad, UCS, carga puntual y LE2). Cada valor se verificó en la
  página del informe original. Diferencias de los informes anotadas en la tabla: UCS de WSP 2024 (Tabla 6: 61.1–143.1; texto:
  64.0–143.1), k de Golder 2021 Alt. 1 1:1 (Tabla 9 frente a la hoja), Gs grueso de Golder 2010 (Tabla 2 frente a las hojas C127).
  `analisis/common.py` ahora cae a la ruta del repo si no existe H:\ (el generador corre en la nube; PDF de 41 p.).
- 2026-10-13: proyecto migrado de Drive a `leps2/` en el repo (sin .npz, PDF de ensayos, páginas escaneadas ni .s01).
  Pruebas de `hiber` (21) y `leps3` (30) pasan en la nube.
- 2026-10-12: diseño y plan del ajuste en dos pasos (`docs/`); `a30_dos_pasos.py` y `Fig_phi1_e.png`.
- 2026-10-07: manuscrito y suplemento r6 de HiBER con lotes 69–72 de Slide2.

## Archivos clave
- `Aporte_alto_confinamiento/eor_antamina/curva_leps2_antamina.tex`: memo EoR.
- `Aporte_alto_confinamiento/analisis_antamina/a30_dos_pasos.py`: ajuste en dos pasos.
- `Aporte_alto_confinamiento/hiber/hiber.py`: librería HiBER.
- `Aporte_alto_confinamiento/manuscrito/PLAN_RONDA6.md`: brechas de la revisión.

## Histórico
- `LEEME.md`: estado al 2026-10-07 (Leps-P, Leps 3.0 probabilístico, artículo corto con m = 0.87).
