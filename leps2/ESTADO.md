# Estado: Leps 2.0 a alto confinamiento   (actualizado: 2026-10-13)

Reconstruido al migrar el proyecto de Drive al repo; revisar y corregir lo que no coincida con tu memoria.

## Pendiente (en orden)
1. Memo EoR, pendientes que esperan al usuario: rótulo de confidencialidad de Antamina; nota de cambio de revisión
   (46.53° → 48.47°).
2. Incorporar los comentarios de WA (`eor_antamina/curva_leps2_antamina_rev3_comentarios_WA.pdf`, `_1210wa.pdf`).
3. **Artículo HiBER r6:** cerrar las brechas de `manuscrito/PLAN_RONDA6.md` que sigan abiertas; revisión visual final.
4. Pendientes del artículo sin resolver: autores y afiliaciones, DOI del repositorio, año de la versión de Slide2,
   autorización del propietario de los datos.

## En curso
- Nada corriendo en la nube. Lotes de Slide2 se corren en el PC.

## Decisiones tomadas (no volver a discutir)
- Modelo renombrado **HiBER** (antes Leps-P), 2026-10-07.
- Memo: no mencionar los 42 triaxiales CD de mezclas con relave (usuario y WA, 2026-10-13).
- Memo: m común para los sets de Antamina (pedido de WA), en vez de una m por set como Cylwik.
- Regla de diseño del Modo B: sobre la σ′n máxima del sitio, el menor entre el percentil actualizado y el de la previa.
- Curva vigente del memo: φ′e=0 = 48.47° (media de 13 sets, 37 ensayos), ω = 20°, m = 0.85, e base 0.45, **tope de 42°** en φ′s (`analisis_antamina/tope.py`, fuente única),
  verificación del diseño con e = 0.55. Es la curva media, no característica (decisión del usuario, 2026-10-13).

## Datos y valores clave
- a30 (con e0 adoptado): paso 1 m = 0.93 (50 % mundo), 1.00 con Antamina sola; paso 2 ω = −17.7°, IC 90 % [−38°, +30°]
  → **no adoptable**; base mundial ω = 7.6°. El memo lo presenta como control (sec. 4.1) y mantiene ω = 20°.
- Curva vigente: φ′s = 39.5° (1 MPa), 33.3° (4.6 MPa), 30.3° (10 MPa), 28.8° (15 MPa); tope 42° gobierna bajo 0.56 MPa (0.35 con e = 0.55).
- Banda (m P10–P90 entre materiales 0.787–0.923 + nivel P5–P95): 37.4–42.2° a 1 MPa, 25.1–36.1° a 10 MPa.
- Niveles: mármol 45.81°, intrusivo 48.05°, hornfels 51.62°; DDE 48.42°; LE2 (MR2024 ≥2035, caliza y margas = mármol) 47.09°.
- HiBER r6: MC 0/600 fallas (β_LN 3.2); Pf integrada sobre τ_D 4.6e-3 (β 2.6); manuscrito 30 p., suplemento 8 p.

## Preguntas abiertas
- ¿Se mantiene ω = 20° en el memo, dado que el ajuste propio de Antamina no identifica ω? (para WA)

## Hecho (reciente)
- 2026-10-13 (5): tope 40° → 42° (decisión del usuario). En el memo solo cambia el valor del tope y los números que dependen
  de él; las figuras siguen siendo las de Python (a11, a16, a34) sin otros cambios. Planilla (para que los autores de Leps 2.0
  validen los cálculos): hoja «Figuras» con las seis figuras del memo como gráficos nativos (a28_figuras_excel.py; datos con
  fórmulas en «Datos_figuras», verificados contra matplotlib). Regla del usuario: no alterar el memo cuando se pide trabajar en
  el Excel. Memo final: justificación del tope frente a la base mundial (sec. 6) y cierre
  del riesgo de bajo confinamiento con cortes directos de gran escala; el Excel reproduce las figuras del memo, no al revés.
- 2026-10-13 (4): revisión del memo completo (autor de Leps 2.0, Stantec, Piteau, Antamina). Aplicado: curva media 48.47°
  declarada como no característica; tope de 40°; verificación con e = 0.55; banda con m P10–P90; sensibilidades de nivel por
  litología y LE2; Indraratna con dos lecturas; ajuste en dos pasos en la sec. 4.1; riesgos actualizados; planilla (a28) con
  tope, banda nueva y control LE2 (verificada con LibreOffice contra Python). Memo 52 p., anexos 12 p., sin errores.
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
