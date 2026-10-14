# HiBER: hierarchical bounded shear-strength envelopes for rockfill and mine waste rock

`hiber.py` is the reference implementation of HiBER, a probabilistic criterion for the drained shear strength of
rockfill and mine waste rock. It returns the full distribution of the secant friction angle φ′s as a function of
normal stress σ′n, not a single curve.

The model has three levels (laboratory → material set → test) and is calibrated on a compiled database of
large-scale drained triaxial tests. The central form is a bounded envelope:

    tan φ′s = tan φ′∞ + (tan φ′1 − tan φ′∞) · exp(−ζ · ln(σ′n/σ0)),   σ0 = 10 pa = 1.013 MPa
    ln tan φ′1 = β[class] + βe · e + κ · ln(Dmax / 100 mm)  (+ laboratory and set random effects)
    ζ = ζ0 + δ[class]  (+ laboratory and set random effects)

It is calibrated with tests stopped at large axial strain (≥ 19%) treated as censored and with the truncation of the
database (φ′1 ≥ 31°) in the likelihood.

φ′1 is the secant angle at σ′n = σ0. φ′∞ is the asymptotic angle of the decay law: it is a fitted decay parameter,
**not** a critical-state friction angle. Uncertainty is carried by samples: hyperparameters, fixed effects and random
effects. The library can:

- give the prior envelope for a rock-quality class (`good` / `moderate` / `low`) and void ratio e;
- update it with drained triaxial tests from the site, with a prior–data conflict check;
- shift it from specimen density to placement density (Δe) and from specimen size to field size (Dmax);
- report percentiles of the **mean** envelope (the quantity used for global stability) and export (σ′n, τ) pairs
  for limit-equilibrium software.

Units: MPa and degrees (Slide2 export in kPa by default). Function names, arguments and warning messages are in
Spanish; `design_envelope` is an English alias of `envolvente_diseno`, and class names are accepted in English or
Spanish (`buena`/`moderada`/`baja`).

## Installation

Python 3 (tested with 3.14). Keep `hiber.py` and `hiber_parameters.json` in the same folder.

```
pip install -r requirements.txt     # numpy, scipy, pandas
pytest -q                           # optional: runs test_hiber.py (needs pytest)
```

## Worked example

A `low`-quality waste rock. The laboratory specimens were compacted to e = 0.35 with Dmax = 150 mm. The dump will be
placed at e = 0.65 with Dmax ≈ 1000 mm. Four drained triaxial tests are available, run on one sample (one set) by
one laboratory. The test values below are synthetic, consistent with φ′1 ≈ 42° and a log–log slope of 0.86:

| σ′3 (MPa) | σ′1 (MPa) |
|---|---|
| 0.3 | 1.71 |
| 0.7 | 3.42 |
| 1.2 | 5.34 |
| 2.0 | 8.17 |

```python
import hiber

tests = dict(s3=[0.3, 0.7, 1.2, 2.0],      # σ′3 at failure, MPa
             s1=[1.71, 3.42, 5.34, 8.17])  # σ′1 at failure, MPa

r = hiber.design_envelope("low", e_lab=0.35, e_campo=0.65, D_lab=150, D_campo=1000,
                          ensayos=tests, representa="tipo")

print(f"p (prior-data conflict check) = {r.p_conflicto:.2f}")
print(r.tabla.round(2).to_string(index=False))
for w in r.avisos:
    print("WARNING:", w)
```

Actual output (default `n=40000`, `seed=0`):

```
p (prior-data conflict check) = 0.98
 sn_MPa  phi_P50  phi_P05  tau_P50  tau_P05
   0.05    47.59    36.04     0.05     0.04
   0.10    44.66    34.54     0.10     0.07
   0.20    42.05    33.09     0.18     0.13
   0.50    39.10    31.28     0.41     0.30
   1.00    37.24    30.03     0.76     0.58
   2.00    35.67    28.87     1.44     1.10
   3.00    34.87    28.26     2.09     1.61
   5.00    33.87    27.27     3.36     2.58
   8.00    33.19    26.76     5.23     4.03
WARNING: e = 0.650 > 0.55 con σ′n > 3 MPa: la base no tiene ensayos de material suelto a esa tensión; extrapolación.
```

`phi_*` are in degrees and `tau_*` in MPa. P50 and P05 are percentiles of the mean envelope of the material. A
conflict p-value well above 0.05 means the tests are consistent with the `low` class. The warning is expected: the
calibration database has no loose material (e > 0.55) above σ′n = 3 MPa, so that part of the table is an
extrapolation.

What `design_envelope` did, in this order:

1. Prior of the `low` class at the **laboratory** void ratio e_lab = 0.35 and specimen size D_lab = 150 mm.
2. Conflict check and update with the four tests (`actualizar_sitio`, one set at e_lab).
3. Density shift Δe = e_campo − e_lab = +0.30.
4. Size shift from Dmax 150 mm to 1000 mm.
5. P50 and P05 of the mean envelope at the requested σ′n (default 0.05–8 MPa; pass `sn=[...]` to change).
6. Above the largest σ′n of the site tests (here 3.36 MPa), the lower of the updated and prior percentiles. In the
   validation by laboratory, updating with tests at low stress left 14% of the tests at higher stress below the
   5th percentile; with this rule, 4%. In the example the prior governs at 5 and 8 MPa (`r.diagnostico["previa_gobierna"]`).

`representa="tipo"` (default) treats the tests as information about the rock **type**. It returns the envelope of a
new set from the same laboratory: the laboratory effect is updated, and the between-set variance is restored.
`representa="muestra"` returns the posterior of the tested set only. That is narrower, and is valid only if the
design material is the sample that was tested. In this example, `representa="muestra"` gives P05 = 31.35° at 1 MPa
instead of 30.03°.

The returned object also carries `r.material` (the final `Material`, at e_campo and D_campo) and `r.diagnostico`
(conflict-check details, including the `m` used to convert σ′3, σ′1 to σ′n, τ).

## Domain of validity

| Item | Range | What the code does outside it |
|---|---|---|
| σ′n | ≤ 8 MPa (database maximum 7.9 MPa) | `ValueError`, unless `permitir_extrapolacion=True`; then a visible warning |
| e at σ′n > 3 MPa | ≤ 0.55 | warning |
| e (and e_lab + Δe) | 0.15–0.89 (database range) | warning |
| σ′n low end | ≥ 0.05–0.1 MPa | warning below 0.05 MPa unless a cap is given (`tope_reposo`) |
| Size ratio D_campo/D_lab | ≤ 15 | warning |
| σ′n vs. site tests | ≤ 3 × the largest σ′n tested | warning |

**Low-stress cap.** The secant angle keeps rising as σ′n → 0. `tope_reposo=38` (degrees) limits φ′s to that value for
σ′n < 0.1 MPa, in `design_envelope` and in `tabla_slide2`. The default is `None`, which applies no cap and leaves the
results unchanged. Choose the cap from the angle of repose or from shallow-slip back-analysis, not from this library.

## Usage warnings

- **Order of operations.** Update with the laboratory tests at the **laboratory** void ratio, then shift to the
  placement density and field size. Shifting first and updating afterwards pulls the envelope back to
  laboratory-specimen strength. In the example above, the reversed order gives P05 = 40.0° at 1 MPa instead of
  30.03°, about 10° on the unsafe side. `design_envelope` enforces the correct order. If you chain the low-level
  functions yourself, `actualizar` warns when it receives a material that has already been shifted.
- **At least 2 sets per rock type.** One set (one sample, one laboratory) cannot separate the rock type from the
  sample. Use `representa="tipo"` unless the design material is the tested sample itself.
- **At least 3 tests per set.** With fewer than 2 tests the library warns. One test cannot be separated from test
  scatter.
- **Test up to the design stress.** Choose σ′3 so that the σ′n at failure reaches the normal stress on the critical
  surface. Above 3 × the largest tested σ′n, the site update has not been verified, and the code warns.
- **Degradable waste rock is out of scope.** Material that weathers or breaks down with time (slaking, clay-forming
  lithologies) is not represented in the calibration database.
- Percentiles default to the **mean** envelope (`puntual=False`). Use `puntual=True` only for the strength of a
  single test point, not for a failure surface.

## Exporting the envelope to Slide2

Use a "Shear/Normal Function" (non-linear) material. `r.a_slide2(p=5)` returns the P05 (σ′n, τ) pairs in kPa,
starting with (0, 0) and spanning 0.05–8 MPa on a log scale (30 points). It applies the same `tope_reposo` as the
design call.

```python
import csv
pairs = r.a_slide2(p=5)                    # or hiber.tabla_slide2(r.material, p=5, tope_reposo=38)
with open("envelope_P05.csv", "w", newline="") as f:
    csv.writer(f).writerows([("normal_stress_kPa", "shear_stress_kPa"), *pairs])
```

The first rows of the file produced by the example are:

```
normal_stress_kPa,shear_stress_kPa
0.0,0.0
50.0,36.382
59.563,42.758
```

Paste the two columns into the Slide2 shear/normal function table. Use P50 for best-estimate or back-analysis runs
and P05 (characteristic mean-envelope value) for design, following your project's acceptance criteria.

## Low-level API

| Function | Purpose |
|---|---|
| `previa(clase, e)` | prior envelope of a class at void ratio e (new material, new laboratory) |
| `actualizar(mat, s3, s1)` | update with tests of the same material (posterior of the tested sample) |
| `actualizar_sitio(sets, nuevos)` | joint update of several sets from one laboratory; `nuevos` = new sets of a type |
| `densidad(mat, de)` | void-ratio shift Δe |
| `escala(mat, d_lab, d_campo)` | size shift between Dmax values |
| `percentiles(sn, mat, ps)` | percentiles of φ′s (mean envelope by default) |
| `tabla_slide2(mat, p)` | (σ′n, τ) pairs for limit-equilibrium software |
