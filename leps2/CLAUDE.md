# Proyecto: Leps 2.0 a alto confinamiento (Antamina, Gate 3)

## Objetivo
Resistencia al corte drenada del desmonte de mina a grandes confinamientos. Dos líneas:
1. **Memo EoR Antamina**: curva Leps 2.0 ajustada a los ensayos de Antamina (LaTeX, en revisión con WA).
2. **Artículo HiBER** (antes Leps-P / Leps 3.0): criterio probabilístico jerárquico, manuscrito ASCE IJGM (ronda r6).

## Estructura (dentro de `Aporte_alto_confinamiento/`)
- `eor_antamina/`: memo `curva_leps2_antamina.tex` (+ `build_curva_leps2.py`, planilla `_calculos.xlsx`, `flac/`, `figs/`).
  Las versiones `*_revN_respaldo.py` son históricas.
- `analisis_antamina/`: scripts `aNN_*.py` del sitio (a1 → a34). a12 = ajuste vigente; a28 = planilla; a30 = ajuste en dos pasos.
- `analisis/`: scripts del artículo (`lepsp_*`, `leps3_*`); `modelos.py` (sigma1, tau_leps2); `lepsp_r6.py` (base mundial).
- `hiber/hiber.py`: implementación de referencia de HiBER (README en inglés). `leps3/lepsp.py`: versión anterior.
- `manuscrito/`: `build_*` generan el docx/PDF; `PLAN_RONDA6.md` = brechas de la última revisión; `NORMAS_ASCE_IJGM.md`.
- `datos_antamina/`: `base/` (CSV limpios; `ensayos.csv` principal), `extraido/` (CSV por informe), `DECISIONES.md`.
- `slide2/`: generadores de YAML/.slmd por lote; `resultados_Slide2/` (los .s01 no están en git).
- `literatura/`: `MATRIZ_LITERATURA.md` y PDF. `docs/`: diseños y planes fechados.
- Raíz de `leps2/`: material original de Drive (paper de Cylwik et al. 2025, guía de usuario, base Rockfill).

## Cómo correr
- Dependencias: `pip install numpy scipy pandas matplotlib openpyxl pytest`.
- Pruebas: `cd Aporte_alto_confinamiento/hiber && python -m pytest -q` (21) y en `leps3/` (30).
- Los scripts se corren desde su carpeta (rutas relativas).
- En la nube **no** hay Slide2, Word ni FLAC; tampoco pdflatex salvo que se instale (`apt-get install texlive-...`).
  Los lotes de Slide2 y la exportación a PDF con Word se hacen en el PC.

## Convenciones
- Unidades: MPa y grados (Slide2 en kPa). σ0 = 10 pa = 1.013 MPa. e = relación de vacíos inicial de la probeta.
- Textos en español, sin modismos de IA; el artículo en inglés. Revisiones con `revN` / `_rN` en el nombre.
- Antes de cambiar a12, la planilla o el memo con números nuevos: informar al usuario y esperar aprobación.

## Trampas conocidas
- Clave de set = publicación + set (los códigos "A", "C" se repiten entre publicaciones).
- La unidad independiente es el laboratorio, no la publicación.
- m ≤ 1 truncado exacto; truncamiento de la base en φ′1 ≥ 31°; máximos censurados con εa ≥ 19 %.
- `LEEME.md` describe el estado al 2026-10-07 (Leps-P); lo vigente está en `ESTADO.md`.
- Datos de Antamina confidenciales: en el artículo el sitio se anonimiza («yacimiento de skarn polimetálico en los Andes»).
