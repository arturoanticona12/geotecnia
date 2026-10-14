# Base de datos de desmonte de Antamina: diseño para análisis estadístico

**Objetivo:** reunir en una base sólida y trazable los ensayos geotécnicos del desmonte de Antamina, para analizar en profundidad la resistencia al corte por litología y clase de desmonte, y para integrarla a Leps 3.0.

## 1. Estructura relacional

Se arman tablas enlazadas por identificadores en lugar de una planilla plana: una misma muestra tiene granulometría, índices y varios ensayos de resistencia.

| Tabla | Una fila por | Claves y contenido principal |
|---|---|---|
| `fuentes` | informe o publicación | `fuente_id`, autor, año, laboratorio, código, tipo (primaria, secundaria o histórica), observaciones |
| `materiales` | material o muestra ensayada (set) | `material_id`, `fuente_id`, clase (ROM, Chancado, Enrocado o mezcla), litología normalizada, subtipo, proporciones, alteración, % relave, origen (tajo, banco, fase, calicata) |
| `granulometrias` | curva antes o después del ensayo | `material_id`, estado (antes o después), escalamiento, tamices y % pasante, más D10–Dmax, Cu, Cc, % grava, arena y finos |
| `indices_roca` | determinación de propiedad de roca | `material_id` o litología, propiedad (UCS, carga puntual, Los Ángeles, durabilidad, absorción, Gs), valor, unidad, n |
| `probetas` | probeta ensayada | `probeta_id`, `material_id`, tipo de ensayo, drenaje, saturación, dimensiones, Dmax, γd, e0 (y su origen), Dr, w |
| `resultados` | probeta en la falla | σ′3, σ′1, q, p′, u, Su, σn y τ (corte directo), criterio de falla, εa, εv, Bg, finos después del ensayo, página de origen, verificado |
| `curvas` | punto de una curva (opcional) | `probeta_id`, εa, q, εv, u: para ajustar dilatancia y estado crítico |
| `edometros` | escalón de carga | `probeta_id`, σv, εv o e |

## 2. Reglas de homogeneización

- **Unidades:** kPa, mm, kN/m³ y %. Los grados de las envolventes solo como dato informado.
- **Desviador:** siempre q = σ1 − σ3, aunque el informe use la notación MIT (q/2).
- **Deformación volumétrica:** compresión negativa, como en la base de Cylwik et al. (2025).
- **Relación de vacíos:** si no viene, e0 = Gs·γw/γd − 1. Se marca si es calculada y con qué Gs (de la probeta, de la litología o supuesto).
- **Litología y clase:** listas controladas (ver `DECISIONES.md`). El nombre original se conserva.

## 3. Calidad y trazabilidad

Cada resultado lleva:

- la página de origen;
- si se verificó en la imagen;
- si es un valor leído de gráfico;
- una marca de calidad:
  - **A:** tabla verificada;
  - **B:** leído de gráfico;
  - **C:** dato incompleto o dudoso.

Además se registran:

- **Duplicados.** Se detectan entre informes (el mismo ensayo citado en dos documentos) y frente a la base de Cylwik y la de Ovalle. Se conserva el registro primario y los demás se marcan.
- **Fuentes históricas.** Las láminas Stantec 2023 quedan como contexto, sin entrar en el análisis.

## 4. Análisis estadístico previsto

1. **Estadística descriptiva por litología y clase:** granulometría, densidad, índices de roca y cobertura de esfuerzos (cuánto hay sobre 1, 2 y 3 MPa).
2. **Resistencia por litología y clase:** ajuste de φ′1 y m por material en ln q, con la misma metodología que la base mundial.
3. **Modelo jerárquico** con efectos de litología y clase anidados en Antamina, comparado con la base mundial: ¿el desmonte de Antamina se comporta como la población, o tiene sesgo?
4. **Actualización de Leps 3.0 con los datos de Antamina** (posterior por litología y clase), con intervalos predictivos y validación dejando fuera cada informe.
5. **Variables explicativas:** e0, finos, Cu, Dmax, UCS, Bg y % de relave en las mezclas de co-disposición.
6. **Rotura y volumen:** Bg y εv frente al esfuerzo por litología, como base del criterio de drenaje.
7. **Cobertura frente a la necesidad de diseño:** esfuerzos ensayados frente a los de un botadero de 700 m, por litología, para definir el programa de ensayos que falta.

## 5. Entregables

- `antamina_base.xlsx`: una hoja por tabla y un diccionario de datos.
- Los mismos datos en CSV, para análisis reproducible.
- Ficha por litología y clase.
- Informe de calidad: cobertura, duplicados, vacíos y dudas por resolver con el usuario.
