# Verificación independiente: Golder (2021) commingling y Golder (2010) ROM IPCC

Fecha: 2026-10-06. Verificador distinto del extractor. Cada número se leyó en la imagen renderizada de la página (PNG en `paginas/verificacion/Golder2021_2010/`, prefijos `G10_` y `G21_`; montajes `G10_m_*.png`, `G21_m_*.png`). Las páginas citadas son las del PDF. Los scripts que generan los entregables están en la misma carpeta (`datos_transcritos_2010.py`, `build_2010_cu.py`, `build_2021.py`, `build_indices_2010.py`, `build_condiciones.py`; registro completo de cambios del CSV 2010 en `log_cambios_2010.csv`).

Entregables en `verificado/`: `condiciones_Golder2010.csv` (19 sets), `condiciones_Golder2021.csv` (10 sets), `Golder_2010_ROM_verificado.csv` (57 filas, ninguna borrada), `Golder_2021_commingling_verificado.csv` (36 filas, ninguna borrada), `indices_roca_Golder2010.csv` (238 filas) y este archivo.

## 1. Resumen

| Fuente | Discrepancias en el CSV extraído | Discrepancias en el resumen extraído | Errores o contradicciones internas del informe |
|---|---|---|---|
| Golder 2010 | 57 filas con esfuerzos mezclados (todas las CU) y 16 filas con q y Δu desviados 1 kPa | 6 | 14 |
| Golder 2021 | 0 valores numéricos erróneos (30 triaxiales y 6 permeabilidades confirmados) | 2 | 8 |

**Nota sobre el «72 filas».** El CSV extraído de 2010 tiene 57 filas, no 72. Las 57 (45 de Golder y 12 de Vector) tenían `q_kPa ≠ sigma1_kPa − sigma3_kPa`, porque `sigma3_kPa` era σ′3 de consolidación y `sigma1_kPa` era σ′1 en la falla.

## 2. Golder 2010: corrección de los triaxiales CU

### 2.1 Qué se cambió (todas las filas)

| Columna | Antes | Ahora | Página | Razón |
|---|---|---|---|---|
| `sigma3_kPa` | σ′3 de consolidación | σ′3 en la falla (impreso en la hoja Golder; tabla Vector en el pico) | 82-152, 161-181 | Para que `q = sigma1 − sigma3` sea coherente |
| `sigma3c_kPa` (nueva) | — | σ′3 de consolidación | idem | Separar consolidación y falla |
| `sigma3f_kPa`, `sigma1f_kPa` (nuevas) | — | σ′3 y σ′1 en la falla | idem | Pedido explícito |
| `q_kPa`, `q_falla_und_kPa` | σ1−σ3 total de la hoja | σ′1f − σ′3f con los valores impresos | idem | En 16 hojas Golder σ1−σ3 total y σ′1−σ′3 difieren 1 kPa por redondeo; se adopta el efectivo |
| `u_falla_kPa` | σ′3c − σ′3f «derivado» | σ3 − σ′3 impresos (Golder) o «P. poros» (Vector) | idem | El extractor dedujo σ′3f = σ′1 − q y no copió el σ′3 impreso |
| `p_falla_kPa` | (σ′1+2σ′3)/3 con σ′3f derivado | recalculado con σ′3f impreso | idem | — |
| `maxdev_*`, `maxobl_*` (nuevas) | — | Estados de máximo desviador y máxima oblicuidad | idem | Golder no tabula la curva: la máxima oblicuidad es «no informado»; Vector sí la tabula |
| `B_valor`, `contrapresion_kPa`, `velocidad_pct_min`, `gamma_d_post_consol_kNm3`, `e_post_consol`, `S_final_pct`, `e0_Gs_usado` (nuevas) | — | De las hojas | idem | Condiciones por probeta |

Todo lo demás de esas filas (γd, e0, Gs, w, Ø, H, εa en la falla, σ′1f) coincidió con las imágenes: el script verificó cada valor con tolerancia de 0.05 y no hubo cambios.

### 2.2 Tabla de corrección por probeta

