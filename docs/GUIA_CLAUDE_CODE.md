# Guía de trabajo con Claude Code: más precisión con menos tokens

Versión 1.0 · 2026-10-13
Para proyectos de ingeniería geotécnica (Python, LaTeX, Excel, FLAC) en Windows y en la nube.

---

## Índice

0. Idea central
1. Configuración única (para todos los proyectos)
2. Proyectos activos: cómo migrar sesiones largas
3. Proyectos nuevos: cómo arrancar ordenado
4. Proyectos grandes con varios componentes
5. El ciclo diario
6. Cómo pedir para gastar menos
7. Modelo y esfuerzo según la tarea
8. Límites de uso y créditos
9. Qué esperar y dónde puede fallar
10. Checklist rápido
Anexo: plantillas

---

## 0. Idea central

**La memoria del proyecto vive en archivos, no en la conversación.**

Cada mensaje que envías hace que Claude vuelva a procesar todo el contexto acumulado de la sesión. En una sesión de 800 mil tokens, cada mensaje procesa esos 800 mil. Si limpias el contexto y el estado del proyecto vive en un archivo de unos 2 mil tokens, el mismo mensaje parte de unos 20–40 mil.

Además, con contexto limpio Claude trabaja mejor:
- No se distrae con versiones viejas de scripts, errores ya corregidos ni ideas descartadas.
- Un error de hace 200 mensajes ya no influye.
- Las decisiones quedan escritas una vez y en limpio, sin enterrarse en la conversación.

**Regla de oro:**
> Lo que no quieres repetir va en `CLAUDE.md`. Lo que cambia va en `ESTADO.md`.
> Al terminar cada tarea: `/cerrar` y luego `/clear`.

---

## 1. Configuración única (para todos los proyectos)

### 1.1 Tres niveles de archivos

| Archivo | Dónde | Contiene | Cambia… |
|---|---|---|---|
| CLAUDE.md global | `C:\Users\<usuario>\.claude\CLAUDE.md` | Tu perfil, el estilo de respuesta, las reglas de ahorro de tokens | Casi nunca |
| CLAUDE.md del proyecto | Raíz de cada proyecto | Qué es el proyecto, la estructura y cómo correr o compilar | Rara vez |
| ESTADO.md | Raíz de cada proyecto | Hecho, pendiente, decisiones tomadas, lo que está en curso | Al cerrar cada tarea |

Claude Code lee estos archivos automáticamente al iniciar la sesión, sin que tengas que pedírselo:
- el `CLAUDE.md` global;
- el `CLAUDE.md` de la carpeta donde abres la sesión;
- los `CLAUDE.md` de las carpetas superiores a esa.

Los `CLAUDE.md` de las subcarpetas los lee solo cuando trabaja con archivos de ellas.

### 1.2 Skills de atajo: /retomar y /cerrar

Crea dos skills en `C:\Users\<usuario>\.claude\skills\`. Así basta con escribir `/retomar` o `/cerrar` en vez de un prompt largo. El contenido está en el Anexo (A.4 y A.5).

### 1.3 Skills para procedimientos repetidos

Todo procedimiento que pides con frecuencia conviene convertirlo en skill: compilar el memo, verificar la planilla en Excel, el formato de un informe, el QC de una base de ensayos. Así Claude no gasta tokens redescubriendo cómo se hace cada vez.

Para usarlas también en la nube, guárdalas dentro del repo, en `.claude/skills/`.

---

## 2. Proyectos activos: cómo migrar sesiones largas

**Objetivo:** pasar el conocimiento de la conversación larga a archivos **una sola vez**, y desde ahí trabajar con sesiones limpias.

### Paso A1: Extraer la memoria (un mensaje, dentro de la sesión larga)

La sesión larga tiene todo el contexto, así que es la que mejor puede escribir los archivos. Es el último turno caro.

```
Vamos a migrar este proyecto a sesiones cortas. Con todo lo que sabes de esta
conversación, crea dos archivos en la raíz del proyecto:

1. CLAUDE.md (máximo 60 líneas): qué es el proyecto y su objetivo; estructura de
   carpetas con el rol de cada una; scripts principales en orden de ejecución y cómo
   correrlos; cómo compilar o generar los entregables; convenciones (nombres,
   revisiones, unidades); trampas conocidas (qué falló y por qué).

2. ESTADO.md (máximo 80 líneas) con estas secciones:
   - Hecho (lo relevante, no todo el historial)
   - Pendiente (ordenado; el #1 es lo próximo)
   - Decisiones tomadas: cada criterio, parámetro o método que ya acordamos, con su
     justificación en una línea. Es la sección más importante: incluye todo lo que
     no quiero volver a discutir.
   - Datos y valores clave (parámetros adoptados, resultados de referencia)
   - Preguntas abiertas
   - En curso (corridas o procesos lanzados)
   - Archivos clave

No incluyas nada que se pueda deducir leyendo el código. Prioriza lo que solo está
en esta conversación.
```

**Si la sesión está bloqueada** (por ejemplo, porque llegaste al límite semanal):
- Opción 1: desde una sesión en la nube, pide que lea el historial de esa sesión y redacte los archivos.
- Opción 2: desde una sesión nueva, reconstruye los archivos a partir del proyecto:

```
Reconstruye CLAUDE.md y ESTADO.md de este proyecto a partir de los archivos.
Usa un subagente Explore para revisar scripts, CSV y documentos, y tráeme solo la
conclusión. Marca con [VERIFICAR] lo que no puedas confirmar.
```

La opción 2 recupera menos de "Decisiones tomadas", porque esas viven en la conversación y no en los archivos.

### Paso A2: Revisar tú mismo (5–10 minutos). Es el paso más importante.

Lee el ESTADO.md y corrígelo o complétalo:
- ¿Están **todas** las decisiones de criterio? Por ejemplo: qué e0 se adoptó, qué curva, qué factor y de dónde salió.
- ¿Están los **valores de referencia** (parámetros adoptados, resultados clave)?
- ¿El pendiente #1 es realmente lo próximo?
- ¿Lo marcado con [VERIFICAR] es correcto?

Un error en ESTADO.md se propaga a todas las sesiones futuras.

### Paso A3: Cerrar la sesión vieja y abrir una nueva

1. Archiva la sesión larga (no la borres; sirve como consulta).
2. Abre una sesión nueva en la carpeta del proyecto y escribe `/retomar`.
3. Si a Claude le falta algo, agrégalo a ESTADO.md. No se lo expliques en el chat, porque ahí se pierde.

### Casos particulares

| Situación | Cómo manejarla |
|---|---|
| Corridas FLAC o lotes en curso | Anótalas en "En curso": lote, carpeta y qué revisar al terminar. Cuando acaben, abre sesión y di "terminó el lote X, revisa resultados". Nadie vigila en bucle. |
| Preguntas abiertas (ej. "¿de dónde salió el 0.6?") | Sección "Preguntas abiertas". Cuando haya respuesta, pásala a "Decisiones tomadas". |
| Varios subproyectos en una carpeta | Un CLAUDE.md y un ESTADO.md por subproyecto. Abre la sesión en la subcarpeta. Ver sección 4. |
| Verificaciones repetitivas (Excel, QC) | Conviértelas en skill. |

---

## 3. Proyectos nuevos: cómo arrancar ordenado

### Paso B1: Estructura estándar

Usa siempre la misma estructura. Así Claude no necesita explorar para entender el proyecto.

```
<proyecto>/
├── CLAUDE.md          ← qué es, estructura, cómo correr
├── ESTADO.md          ← memoria de trabajo
├── fuentes/           ← informes del cliente, ensayos de laboratorio, papers
├── datos/             ← datos limpios (CSV) derivados de fuentes/
├── analisis/          ← scripts aNN_*.py numerados en orden de ejecución
├── modelos/           ← FLAC, Slide, etc.
├── resultados/        ← salidas (figuras, tablas)
└── entregables/       ← memo o informe (.tex/.docx) y PDFs
```

### Paso B2: Sesión de arranque (alcance)

Para esta sesión usa el modelo más capaz y esfuerzo High, porque aquí se definen las decisiones grandes.

```
Proyecto nuevo: <cliente, estructura, objetivo, entregable, plazo, en 3-5 líneas>.
En fuentes/ están <lista de documentos>.

1. Revisa fuentes/ con un subagente y resúmeme lo relevante (máximo 15 líneas).
2. Hazme las preguntas de alcance y criterio que necesites ANTES de proponer nada
   (normativa, sismo de diseño, FS mínimos, método, etc.).
3. Con mis respuestas, crea CLAUDE.md y ESTADO.md. El pendiente debe ser un plan
   por fases, donde cada fase quepa en 1-3 sesiones cortas.
```

### Paso B3: Plan por fases (ejemplo: estabilidad sísmica de un depósito)

```
1. Fase 1: Base de datos de ensayos (fuentes/ → datos/ensayos.csv) + QC
2. Fase 2: Parámetros de resistencia por material (envolventes, φ′ vs σ′)
3. Fase 3: Peligro sísmico: Sa(1.3Ts), Mw desagregada, interfase vs intraslab
4. Fase 4: Estabilidad estática y pseudoestática (k compatible con Da)
5. Fase 5: Desplazamientos (Newmark / BMT18 / Macedo et al. 2023) y FLAC si aplica
6. Fase 6: Memo técnico + anexos
```

Cada fase se trabaja en una o varias sesiones independientes. **Nunca hagas todo en una sola ventana.**

---

## 4. Proyectos grandes con varios componentes

### 4.1 Estructura de dos niveles

```
proyecto/
├── CLAUDE.md            ← común a TODO (cliente, normativa, convenciones, lista de componentes)
├── ESTADO.md            ← TABLERO: una fila por componente + dependencias (corto)
├── comun/
│   ├── DECISIONES.md    ← criterios compartidos (sismo, FS mínimos, materiales)
│   └── parametros/      ← valores adoptados que usan varios componentes (CSV)
├── componente_1/
│   ├── CLAUDE.md        ← solo lo específico del componente
│   ├── ESTADO.md        ← memoria detallada del componente
│   └── analisis/ datos/ entregables/ ...
├── componente_2/
├── componente_3/
└── informe_final/       ← integración
```

### 4.2 Qué va en cada archivo

| Archivo | Contenido | Tamaño |
|---|---|---|
| CLAUDE.md raíz | Cliente, objetivo, normativa, convenciones, componentes con una línea cada uno | ~40 líneas |
| ESTADO.md raíz (tablero) | Estado y bloqueos por componente; dependencias | ~30 líneas |
| comun/DECISIONES.md | Decisiones que afectan a **más de un** componente, con justificación | Lo necesario |
| componente/CLAUDE.md | Scripts, cómo correr y compilar, trampas propias | ~40 líneas |
| componente/ESTADO.md | Hecho, pendiente, decisiones locales, en curso | ~60–80 líneas |

### 4.3 Regla clave: cada dato vive en un solo lugar

El mayor riesgo en proyectos grandes es la **inconsistencia entre componentes**: que uno use un φ′ y otro uno distinto, o sismos de diseño diferentes.

- Lo que usa **un solo** componente va en su propio ESTADO.md.
- Lo que usan **dos o más** va en `comun/`: los criterios en DECISIONES.md y los valores en `parametros/`, como CSV que los scripts leen directamente.
- Si un componente produce algo que otros usan, lo publica en un archivo de salida fijo y se anota en "Dependencias" del tablero.
- Todo cambio en `comun/` se anota con su impacto:
  ```
  ## 2026-10-13: φ′ enrocado actualizado (curva rev10)
  Impacto: revisar componente_2 y componente_3 (usan comun/parametros/phi_enrocado.csv)
  ```

### 4.4 Dónde abrir la sesión

| Tarea | Dónde | Qué lee Claude |
|---|---|---|
| Trabajo en un componente (lo más común) | En la subcarpeta del componente | CLAUDE.md raíz y del componente, ESTADO del componente |
| Cambiar un criterio común | En la raíz | comun/DECISIONES.md y el tablero; anota el impacto |
| Integrar o revisar coherencia | En la raíz, con subagentes | Solo los resúmenes que devuelve cada subagente |
| Ver el panorama | En la raíz | Solo el tablero |

**Prompt de integración (no llena el contexto):**
```
Lee el tablero. Lanza un subagente por componente que lea su ESTADO.md y sus
resultados principales y me devuelva, en máximo 15 líneas: parámetros adoptados,
resultados clave e inconsistencias con comun/DECISIONES.md. Con esos resúmenes,
arma la estructura del informe final.
```

### 4.5 Sesiones en paralelo

Puedes tener una sesión abierta por componente al mismo tiempo, porque cada una edita sus propios archivos. Evita que dos sesiones editen **a la vez** el tablero o `comun/`. Esos archivos se tocan al cerrar, de a uno.

---

## 5. El ciclo diario

```
/retomar  →  [UNA tarea]  →  /cerrar  →  /clear  →  /retomar  →  ...
```

### Comandos clave

| Comando | Para qué |
|---|---|
| `/clear` | Borra el contexto pero mantiene la ventana. Úsalo al terminar cada tarea. Es el que más ahorra. |
| `/compact <foco>` | Resume el contexto a mitad de una tarea larga, por ejemplo: `/compact conserva solo lo necesario para la Tabla 2` |
| `/context` | Muestra cuánto contexto llevas usado |
| `/model` | Cambia el modelo |
| Selector de esfuerzo | Low / Medium / High |

### Cuándo limpiar

| Señal | Acción |
|---|---|
| Terminaste la tarea | `/cerrar` y luego `/clear` |
| Cambias de tema | `/cerrar` y luego `/clear`, aunque no hayas terminado |
| `/context` marca más de 150–200 mil tokens a mitad de una tarea | `/compact <foco>` |
| Claude repite errores u olvida instrucciones | El contexto está contaminado: `/cerrar`, `/clear`, `/retomar` |
| Fin del día | Siempre `/cerrar` |

---

## 6. Cómo pedir para gastar menos

| En vez de… | Haz… |
|---|---|
| 5 mensajes con un cambio cada uno y una compilación tras cada uno | 1 mensaje con los 5 cambios numerados y "compila una sola vez al final" |
| "Revisa el proyecto y dime qué falta" | "Revisa solo `archivo.py`, la parte de X, y dime Y" |
| Explicar contexto en el chat | Escribirlo en ESTADO.md (se lee una vez y sirve siempre) |
| "¿Ya terminó FLAC?" cada 10 minutos | Esperar y luego decir "terminó, revisa" |
| Un cambio grande sin plan | "Plan de máximo 5 pasos, no edites hasta mi ok" |
| Pedir que lea carpetas enteras | Pedir un subagente Explore que devuelva solo la conclusión |

### Prompts útiles

**Empezar o retomar:**
```
/retomar
```
o, sin skill:
```
Lee ESTADO.md. Haz el pendiente #1. Al terminar, actualiza ESTADO.md y resúmeme en 3 líneas.
```

**Cerrar:**
```
/cerrar
```

**Cambio grande:**
```
Quiero <cambio>. Primero dame un plan de máximo 5 pasos con los archivos que vas a
tocar. No edites nada hasta que te diga "ok".
```

**Varios cambios juntos:**
```
En build_memo.py: (1) Tabla 2 a [H], (2) título de la Fig. 4 "…", (3) unidades kPa
en el eje x. Luego compila una sola vez.
```

---

## 7. Modelo y esfuerzo según la tarea

| Tipo de tarea | Modelo / esfuerzo |
|---|---|
| Arranque de proyecto, definir metodología, revisar un criterio técnico difícil | El más capaz disponible, **High** |
| Programar un análisis nuevo, depurar un resultado raro | Opus, **Medium** o **High** |
| Editar el memo, compilar, figuras, tablas, reorganizar archivos | Opus, **Medium** |
| Renombrar, mover, cambios mecánicos | Opus, **Low** |

Por defecto usa Opus con esfuerzo Medium. Sube el modelo o el esfuerzo solo cuando la tarea lo justifique.

---

## 8. Límites de uso y créditos

- **Max 20x** es el plan individual más alto. Tiene un límite por ventana de 5 horas y un **límite semanal** común a Claude Code, el chat y la app de escritorio.
- **Uso extra:** en Settings → Usage puedes activar créditos a tarifa de API con un **tope mensual** que tú defines. Sirve para no quedarte parado a mitad de semana. Empieza con un tope bajo y ajústalo.
- **Créditos de sesiones en la nube:** si los tienes, se aplican solo a sesiones en la nube (claude.ai/code), no a las locales de VS Code. Revisa la fecha de vencimiento.
- **Trabajo para clientes:** consulta si tu empleador puede darte un asiento Team o Enterprise, o cubrir el uso extra.
- **Medir:** compara tu porcentaje de uso semanal antes y después de aplicar esta guía.

### Qué funciona en la nube y qué solo en la laptop

| Funciona en la nube (Linux) | Solo en la laptop (Windows) |
|---|---|
| Python, LaTeX (pdflatex), git, análisis de datos, figuras, memos | Excel por COM, FLAC, software con licencia, rutas `H:/...` |

Para trabajar un proyecto en la nube, súbelo a un repo **privado** de GitHub (datos de cliente = siempre privado).

---

## 9. Qué esperar y dónde puede fallar

**Beneficios esperados:**
- Respuestas más precisas, porque el contexto es limpio y enfocado.
- Menos costo por mensaje, normalmente un orden de magnitud menos que en sesiones de cientos de miles de tokens.
- Continuidad: cualquier sesión, local o en la nube, retoma el proyecto con `/retomar`.

**Riesgos:**
1. **Un ESTADO.md mal hecho.** Si falta una decisión, Claude la redescubre o toma otra. Revísalo siempre (paso A2).
2. **Falta de disciplina.** Saltarse `/cerrar` y `/clear` te devuelve al problema de antes.
3. **Tareas que sí necesitan mucho contexto** (coherencia global de un informe). Usa una sesión dedicada con subagentes. Es la excepción, no la regla.
4. **Matices no escritos.** Lo que no queda en ESTADO.md se pierde con `/clear`. Para eso existe `/cerrar`.

---

## 10. Checklist rápido

**Una sola vez:**
- [ ] CLAUDE.md global con perfil y reglas de economía
- [ ] Skills `/retomar` y `/cerrar`
- [ ] Skills para procedimientos repetidos
- [ ] Uso extra con tope mensual (opcional)

**Por proyecto activo:**
- [ ] Extraer CLAUDE.md y ESTADO.md desde la sesión larga
- [ ] Revisar y corregir ESTADO.md personalmente
- [ ] Archivar la sesión larga y abrir una nueva con `/retomar`

**Por proyecto nuevo:**
- [ ] Estructura estándar de carpetas
- [ ] Sesión de arranque: preguntas de alcance, CLAUDE.md, ESTADO.md con fases
- [ ] Si hay varios componentes: tablero raíz + `comun/` + ESTADO por componente

**Cada día:**
- [ ] `/retomar` → una tarea → `/cerrar` → `/clear`
- [ ] Cambios agrupados en un solo mensaje
- [ ] Corridas largas sin vigilancia en bucle
- [ ] Modelo y esfuerzo acordes a la tarea

---

# Anexo: plantillas

## A.1 CLAUDE.md global

`C:\Users\<usuario>\.claude\CLAUDE.md`

```markdown
# Perfil
Ingeniero civil geotécnico (Perú). Español, respuestas breves y técnicas.
Windows + PowerShell, Python vía `uv run`, LaTeX con MiKTeX, FLAC2D 9, Excel.

# Economía de tokens (aplica siempre)
- Ubica con Grep antes de leer; lee solo el rango necesario de archivos grandes.
- No releas archivos que ya leíste en la sesión salvo que hayan cambiado.
- Salidas largas: muestra solo el final o un resumen (`| Select-Object -Last 5`).
- Los scripts imprimen un resumen corto y guardan el detalle en archivos.
- Corridas largas (FLAC, lotes): lánzalas y NO consultes en bucle si terminaron.
  Dime que la lanzaste y espera a que yo diga "terminó".
- Búsquedas amplias en muchas carpetas: usa un subagente Explore y tráeme solo la conclusión.
- Agrupa cambios relacionados en una sola edición; compila o corre una sola vez al final.
- No narres lo que vas a hacer; hazlo y resume el resultado en 2-4 líneas.

# Memoria entre sesiones
- Al empezar: lee CLAUDE.md y ESTADO.md del proyecto o componente.
- "Decisiones tomadas" de ESTADO.md (y comun/DECISIONES.md) son definitivas:
  no las vuelvas a investigar salvo que yo lo pida.
- Si descubres algo que una sesión futura necesitaría saber, avísame para
  registrarlo en ESTADO.md.
```

## A.2 CLAUDE.md de proyecto

```markdown
# Proyecto: <nombre>

## Objetivo
<2-3 líneas: cliente, estructura, entregable>

## Estructura
- fuentes/: documentos originales (no editar)
- datos/: CSV limpios; ensayos.csv es la base principal
- analisis/: scripts aNN_*.py en orden (a01 → aNN)
- resultados/: figuras y tablas generadas
- entregables/: memo .tex y PDF

## Cómo correr
- Análisis: `uv run --with numpy --with pandas python analisis/aNN_x.py`
- Memo: `uv run python entregables/build.py` y luego `pdflatex` ×2

## Convenciones
- Unidades: kPa, kN/m³, grados. Revisiones: revNN en el nombre y en el encabezado.

## Trampas conocidas
- <ej.: los nombres de set difieren entre fuentes; emparejar por prefijo "Pila 01">
```

## A.3 ESTADO.md

```markdown
# Estado: <proyecto/componente>   (actualizado: AAAA-MM-DD)

## Pendiente (en orden)
1. <lo próximo>
2. ...

## En curso
- <corrida/lote, carpeta, qué revisar al terminar>

## Decisiones tomadas (no volver a discutir)
- <decisión>: <justificación en una línea>

## Datos y valores clave
- <parámetro = valor (fuente)>

## Preguntas abiertas
- <pregunta> (¿a quién? ¿desde cuándo?)

## Hecho (reciente)
- <ítem: archivo y resultado clave>

## Archivos clave
- <ruta>: <rol>

## Histórico
- <lo hecho que ya no es relevante para el trabajo inmediato>
```

## A.4 Skill /retomar

`C:\Users\<usuario>\.claude\skills\retomar\SKILL.md`

```markdown
---
name: retomar
description: Retomar el trabajo del proyecto leyendo ESTADO.md. Usar al iniciar una sesión.
---
1. Lee CLAUDE.md y ESTADO.md de la carpeta actual (no explores más carpetas todavía).
2. Si hay un ESTADO.md raíz (tablero), lee solo la fila de este componente y sus
   dependencias; revisa si algo de lo que usa cambió en comun/DECISIONES.md.
3. Dime en máximo 5 líneas: dónde quedamos, el pendiente #1, qué archivos vas a tocar
   y si hay cambios en dependencias.
4. Espera mi "ok" o una instrucción distinta antes de editar.
```

## A.5 Skill /cerrar

`C:\Users\<usuario>\.claude\skills\cerrar\SKILL.md`

```markdown
---
name: cerrar
description: Cerrar la tarea actual actualizando ESTADO.md. Usar antes de /clear o al terminar el día.
---
Actualiza ESTADO.md (máximo ~80 líneas en total):
- Hecho: añade lo completado en esta sesión (1 línea por ítem, con archivo y resultado clave).
- Pendiente: reordena; el #1 es lo próximo a hacer.
- Decisiones tomadas: añade las nuevas con su justificación en una línea.
- Datos y valores clave: actualiza si cambió algún valor adoptado.
- En curso: corridas o procesos lanzados que siguen corriendo.
- Archivos clave: actualiza si se crearon o renombraron.
- Mueve a "Histórico" lo hecho que ya no sea relevante.

Si este es un componente de un proyecto mayor:
- Actualiza su fila en el tablero raíz (estado, pendiente #1, bloqueos).
- Si se tocó un criterio o parámetro compartido, regístralo en comun/DECISIONES.md
  con la fecha y el "Impacto" sobre los otros componentes.

Luego dime "listo para /clear".
```

## A.6 Tablero raíz (proyectos con componentes)

```markdown
# Tablero: <proyecto>   (AAAA-MM-DD)

| Componente | Estado | Pendiente #1 | Bloqueado por |
|---|---|---|---|
| componente_1 | ... | ... | — |
| componente_2 | ... | ... | ... |
| informe_final | no iniciado | — | componente_1, componente_2 |

## Dependencias (quién usa qué)
- comun/parametros/<archivo>.csv → componente_1, componente_2
- componente_1: <resultado> → componente_2

## Cambios recientes en comun/ (últimos 5)
- AAAA-MM-DD: <cambio> → Impacto: <componentes>
```

## A.7 comun/DECISIONES.md

```markdown
# Decisiones compartidas: <proyecto>

## Sismo de diseño
- <criterio, periodo de retorno, fuente>  (AAAA-MM-DD)

## Factores de seguridad mínimos
- Estático ≥ 1.5; pseudoestático ≥ 1.0 con k compatible con Da = <x> cm, ε = <0 o σ>

## Materiales
- <material>: <parámetros> → comun/parametros/<archivo>.csv

## Registro de cambios
- AAAA-MM-DD: <cambio>. Impacto: <componentes a revisar>
```
