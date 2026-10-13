"""Supplemental Materials of the HiBER manuscript (round 6, LaTeX with the official ascelike-new class): Figs. S1–S5,
Tables S1–S4, and a worked example of the update with the published matrices. Numbers read from result files."""
import json, re, shutil
from pathlib import Path
import numpy as np
import asce_docx as A
from asce_docx import tex

AQ = Path(__file__).parent; AN = AQ.parent / "analisis"; FIG = AQ.parent / "figuras" / "lepsp6"; LX = AQ / "latex"
J = lambda p: json.load(open(p, encoding="utf-8"))
CV = J(AN / "lepsp_cv6_metricas.json"); CC = J(AN / "lepsp_cv6_censura.json"); ES = J(AN / "lepsp_escala6.json"); DG = J(AN / "lepsp_diag_alta6.json")
PR = J(AN / "lepsp_perfil6.json"); E1 = J(AN / "lepsp_e1_estructura.json"); EJ = J(AN / "lepsp_ejemplo6.json"); S2 = J(AQ / "tabla_S2_r6.json")
A.SYM[:0] = [("φ′∞", r"\phi'_\infty"), ("ζ0", r"\zeta_0"), ("τ_D", r"\tau_D"), ("β_D", r"\beta_D"), ("q_0", r"q_0"), ("g_0", r"g_0"), ("ε_a", r"\varepsilon_a")]
neg = lambda s: s.replace("-", "−"); sg = lambda v, d=3: neg(f"{v:+.{d}f}"); pc = lambda v: f"{100 * v:.0f}%"; pc1 = lambda v: f"{100 * v:.1f}%"
EL = ES["laboratorios R ≥ 2"]
for f in FIG.glob("*.png"):
    shutil.copy2(f, LX / "figs" / f.name)

FIGS = [("FigS1_stress_coverage.png", 6.0, "Distribution of effective normal stress on the failure plane in the calibration database (741 tests)."),
        ("FigS2_volumetric_breakage.png", 6.0, "Net volumetric strain at the maximum deviator (negative: contraction) and breakage index of Marsal (1973) versus σ′n in the "
         f"calibration database. Reported breakage indices above 100%, impossible by definition, were excluded ({DG['bg_excluidos_mayor_100']} tests). Above 1.5 MPa the "
         f"residuals of HiBER increased with the volumetric compression (Spearman ρ = {DG['res_vs_evol_alta']['spearman']:.2f}, n = {DG['res_vs_evol_alta']['n']}) and, "
         f"above 2.75 MPa, with the breakage index (ρ = {DG['res_vs_bg_alta']['spearman']:.2f}, n = {DG['res_vs_bg_alta']['n']})."),
        ("FigS3_profile_likelihood.png", 4.0, f"Profile of the observed-data log-likelihood (censoring and truncation included) of the asymptotic angle φ′∞ relative to its "
         f"maximum ({PR['ml_max']:.2f}); at each angle ζ0, the fixed effects, and the variance parameters were refitted. φ′∞ = 0 is the form without an asymptote "
         "(approximate: maximum over two values of ζ0). Dashed: 1.92 units (approximate 95% interval); dotted: 3 units. First-order approximation; see Table S3."),
        ("FigS4_size_effect.png", 5.6, f"Within-material specimen-size coefficient β_D by laboratory (bars: 95% confidence intervals; set intercepts adjusted for void ratio). "
         f"Hatched band: Knapp–Hartung 95% confidence interval of the random-effects mean across {EL['k']} laboratories with size ratio ≥ 2 "
         f"({sg(EL['b'][0])}; {sg(EL['ci'][0][0])} to {sg(EL['ci'][0][1])}); between-laboratory standard deviation τ_D = {EL['tau']:.3f}."),
        ("FigS5_variance.png", 3.5, "Shares of the variance of the mean-envelope ln τ for an untested material of low rock quality placed at e = 0.65, scaled from 100 mm "
         "to 1 m maximum particle size, at three normal stresses.")]

# ---- Table S1: every Mode B procedure
NOM = {"previa": "Prior, no site tests", "ingenuo_m090": "Least-squares fit of φ′1, m = 0.90", "ingenuo_mtr": "Least-squares fit of φ′1, m from training data",
       "conjunta": "Joint update of both random effects", "nivel": "Level update of each set (Eq. 8)", "descarte": "Level update, flagged sets discarded",
       "sitio": "Flagged sets discarded, shared laboratory effect"}
S1h = ["Procedure", "80% coverage", "Below P05", "Below P10", "Mean z", "CRPS", "Δ CRPS", "Holm p"]
S1f = []
for k, nm in NOM.items():
    o = CV[f"B|{k}"]; c = o.get("vs_nivel")
    S1f.append([nm, pc(o["cob80"]), pc(o["bajo05"]), pc(o["bajo10"]), f"{o['z_medio']:+.2f}".replace("-", "−"), f"{o['crps']:.4f}",
                sg(c["media"], 4) if c else "—", f"{c['p_signflip_holm']:.2f}" if c else "—"])
BN = CV["B|n"]
NOTA_S1 = (f"{BN['ensayos']} held-out tests at σ′n ≥ 2 MPa on {BN['sets']} sets from {BN['labs']} laboratories ({BN['pubs']} publications), predicted from tests at "
           "σ′n ≤ 1.5 MPa of the same set. Mean z: mean standardized residual (negative: strength overpredicted). The procedures were developed while examining "
           "earlier versions of the model on related held-out sets, so the comparisons are exploratory. p-values from exact sign-flip tests on laboratory means, "
           "Holm-adjusted within Mode B. CRPS in units of ln τ; Δ CRPS relative to the level update. In the design procedure, the lower of the level-updated and prior percentiles is used above the "
           "largest σ′n of the site tests.")

# ---- Table S3: structural comparison (uncensored likelihood)
MD = E1["modelos"]; LO = E1["lopo"]["total"]
NM3 = [("M1", "Bounded", "Stress-decreasing (gradient of the mean)"), ("M2", "Bounded", "Additive (level and slope)"),
       ("M4b", "Quadratic by class", "Stress-decreasing (from M1)"), ("M3b", "Quadratic by class", "Additive"),
       ("M4", "Quadratic", "Stress-decreasing (from M1)"), ("M3", "Quadratic", "Additive")]
S3f = [[k, mean, cov, str(MD[k]["k"]), f"{MD[k]['ll']:.1f}", f"{LO[k]:.1f}"] for k, mean, cov in NM3]
lap = E1["laplace_en_FO"]
NOTA_S3 = ("741 tests without censoring or truncation; all models include rock quality class, void ratio, and ln Dmax. Log-likelihood: maximum likelihood with the "
           "exact Gaussian marginal for each publication, given the covariance structure; for M1 and M2, maximum over φ′∞ from 20° to 28°. Out-of-sample: joint "
           "log score leaving out one publication at a time with the variance parameters fixed. First-order minus Laplace log-likelihood of M1: "
           + ", ".join(f"{v['fo_menos_laplace']:.1f} at {v['phi']:.0f}°" for v in lap) +
           f"; the Laplace maximum was {max(v['ll_laplace'] for v in lap):.1f}. Largest single-publication contribution to M1 − M3: "
           f"{max(E1['por_publicacion']['M1-M3']['por_pub'].values()):.1f} of {E1['descomposicion']['total_M1_M3']:.1f}.")

# ---- Table S4: scores with censored tests, by band
FORMS = [("acotada", "HiBER, bounded"), ("cuadratica", "HiBER, quadratic"), ("potencia", "HiBER, power"), ("leps2_jer", "Leps 2.0, hierarchical dispersion"),
         ("leps2_ref", "Leps 2.0, constant dispersion")]
rng_ = lambda o: pc1(o[0]) if abs(o[0] - o[1]) < 1e-9 else f"{pc1(o[0])}–{pc1(o[1])}"
S4f = []
for band, nm in (("todo", "All stresses"), ("sn>=2", "σ′n ≥ 2 MPa"), ("sn>=3", "σ′n ≥ 3 MPa")):
    o = CC[band]; S4f.append([f"{nm} ({o['n']} tests, {o['censurados']} censored, {o['n_lab']} laboratories)", "", "", ""])
    for k, nmf in FORMS:
        S4f.append(["   " + nmf, rng_(o[k]["P05"]), rng_(o[k]["P10"]), f"{o[k]['z_no_cens']:+.2f}".replace("-", "−")])
NOTA_S4 = ("Censored tests (axial strain at the maximum deviator ≥ 19%) are lower bounds of strength. Ranges: lower value counts a censored test as below a "
           "percentile only if its lower bound is; upper value counts it always. Mean z: mean standardized residual of the uncensored tests. Nominal: 5% and 10%.")


def tabla_tex(titulo, enc, filas, nota, cols, size=r"\footnotesize"):
    L = [r"\begin{table}[htbp]", r"\caption{" + tex(titulo) + "}", r"\centering" + size, r"\renewcommand{\arraystretch}{1.2}", r"\setlength{\tabcolsep}{3.5pt}",
         r"\begin{tabular}{" + cols + "}", r"\hline", " & ".join(tex(h) for h in enc) + r" \\", r"\hline"]
    L += [" & ".join(tex(str(v)) for v in f) + r" \\" for f in filas]
    L += [r"\hline", r"\end{tabular}", r"\par\vspace{4pt}\parbox{\linewidth}{\footnotesize Note: " + tex(nota) + "}", r"\end{table}"]
    return "\n".join(L)


def mat_tex(M, nombres, esc=1.0, fmt="{:.3f}"):
    L = [r"\begin{tabular}{l" + "r" * len(nombres) + "}", r"\hline", " & " + " & ".join(tex(n) for n in nombres) + r" \\", r"\hline"]
    for n, fila in zip(nombres, M):
        L.append(tex(n) + " & " + " & ".join(tex(neg(fmt.format(v * esc))) for v in fila) + r" \\")
    return "\n".join(L + [r"\hline", r"\end{tabular}"])


# ---- worked example
m = EJ["matrices"]; en = EJ["ensayos"]; pv = EJ["previa_en_ensayos"]; co = EJ["corte"]; SNe = EJ["sn"]
A1S = neg(f"{m['a1']:+.3f}")
NB = ["β good", "β moderate", "β low", "β_e", "κ", "δ moderate", "δ low"]
fila = lambda k: [f"{a:.1f} / {b:.1f}" for a, b in zip(EJ[k]["P50"], EJ[k]["P05"])]
EX = [r"\section*{Worked Example of the Update}",
      tex(f"The example follows Eqs. (3)–(9) of the paper at the maximum-likelihood point of the ridge (φ′∞ = {m['phi_inf']:.0f}°, ζ0 = {m['zeta0']:.3f}), "
          "with the published parameters, and is checked against the implementation, which also averages over the ridge and the posterior of the variance "
          f"parameters. Material: low rock quality, specimen void ratio {EJ['material']['e_lab']}, maximum particle size {EJ['material']['D_lab_mm']:.0f} mm; "
          f"placement void ratio {EJ['material']['e_campo']} and field size {EJ['material']['D_campo_mm'] / 1000:.0f} m."),
      "", r"\paragraph{Step 1: Site tests.}",
      tex(f"Three drained tests at σ′3 = {', '.join(f'{v:g}' for v in en['s3'])} MPa failed at σ′1 = {', '.join(f'{v:.2f}' for v in en['s1'])} MPa. With the "
          f"conversion of Cylwik et al. (2025) and m = {en['m_conversion']:.3f} (the local slope of the prior at 1 MPa), they give σ′n = "
          f"{', '.join(f'{v:.3f}' for v in en['sn'])} MPa and τ = {', '.join(f'{v:.3f}' for v in en['tau'])} MPa, that is, x = "
          f"{', '.join(f'{v:.3f}' for v in en['x'])} and y = {', '.join(f'{v:.3f}' for v in en['y'])}."),
      "", r"\paragraph{Step 2: Conflict check.}",
      tex(f"The prior mean at the tests is f = {', '.join(f'{v:.3f}' for v in pv['f'])}, the residuals are r = {', '.join(f'{v:.3f}' for v in pv['r'])}, and "
          f"σε = {', '.join(f'{v:.3f}' for v in pv['sigma_eps'])}. With V from Eq. (7) built with the matrices below, D² = {pv['D2']:.2f} with 3 degrees of freedom "
          f"(p = {pv['p']:.3f}): no conflict."),
      "", r"\paragraph{Step 3: Cut update.}",
      tex(f"At the centroid x̄ = {co['x_bar']:.3f}, the gradient a stacks the gradient of the envelope with respect to (η, ζ) for the laboratory and the set "
          f"effects and with respect to the fixed effects; $g_0=\\mathbf{{a}}^T\\mathbf{{P}}\\mathbf{{a}}$ = {co['g0']:.4f}. Eq. (8) gives $\\hat q_0$ = {co['q0']:.4f} with variance {co['var_q0']:.5f}. "
          f"The shift $\\mathbf{{P}}\\mathbf{{a}}\\hat q_0/g_0$ raises η by {co['desplaz_eta_lab']:.4f} through the laboratory effect and by {co['desplaz_eta_set']:.4f} through the set effect, "
          "and moves the fixed effects slightly."),
      "", r"\paragraph{Step 4: Rock type, density, and size.}",
      tex("The rock type is represented by a new set from the same laboratory: the updated laboratory and fixed effects are kept, and the set effect is "
          "drawn again from G_s. The void ratio is then changed to the placement value through η, and the size shift adds a variance of "
          "(ln(D_f/D_l))²(SE² + τ_D²) with zero mean. Above the largest σ′n of the tests "
          f"({EJ['sn_max_ensayos']:.2f} MPa), the lower of the updated and prior percentiles is used."),
      tabla_tex("Worked example: secant friction angle φ′s (°), median / 5th percentile of the mean envelope",
                ["Stage"] + [f"{s:g} MPa" for s in SNe],
                [["Prior, laboratory"] + fila("previa_lab"), ["Updated (rock type), laboratory"] + fila("actualizada_lab"),
                 ["Prior, placed and field size"] + fila("previa_campo"), ["Updated (rock type), placed and field size"] + fila("actualizada_campo"),
                 ["Design 5th percentile"] + [f"{v:.1f}" for v in EJ["diseno_P05"]],
                 ["Implementation (envolvente_diseno)"] + [f"{a:.1f} / {b:.1f}" for a, b in zip(EJ["biblioteca"]["P50"], EJ["biblioteca"]["P05"])]],
                "Plug-in values at the maximum-likelihood point; the implementation averages over the ridge of (φ′∞, ζ0) and the posterior of the variance parameters "
                f"(conflict p = {EJ['biblioteca']['p']:.3f}).", "l" + "c" * len(SNe)),
      r"\paragraph{Published matrices.}",
      tex(f"Fixed effects β = ({', '.join(neg(f'{v:.4f}') for v in m['beta'])}) in the order of Table 1 (β_c good, moderate, low; β_e; κ; δ_c moderate, low). "
          f"Dispersion: ln σε = {m['a0']:.3f} {A1S}x."),
      r"\begin{center}\footnotesize", r"\textbf{Covariance of the fixed effects, $\mathbf{C}_\beta \times 10^4$}\\[2pt]", mat_tex(m["C_beta"], NB, 1e4, "{:.2f}"),
      r"\\[8pt]\textbf{$\mathbf{G}_p$ and $\mathbf{G}_s$ (rows and columns $\eta$, $\zeta$), $\times 10^4$}\\[2pt]",
      r"\begin{tabular}{lrrrr}", r"\hline", r" & $\eta$ (laboratory) & $\zeta$ (laboratory) & $\eta$ (set) & $\zeta$ (set) \\", r"\hline"]
EX += [tex(n) + " & " + " & ".join(tex(neg(f"{v * 1e4:.2f}")) for v in list(gp) + list(gs)) + r" \\" for n, gp, gs in zip(["η", "ζ"], m["G_p"], m["G_s"])]
EX += [r"\hline", r"\end{tabular}", r"\end{center}"]

T = [r"\documentclass[Journal,letterpaper,InsideFigs,NoLists,NoLineNumbers]{ascelike-new}", r"\WarningFilter{caption}{Unknown document class}",
     r"\usepackage[utf8]{inputenc}", r"\usepackage[T1]{fontenc}", r"\usepackage{lmodern}", r"\usepackage{graphicx}",
     r"\usepackage[style=base,figurename=Fig.,labelfont=bf,labelsep=period]{caption}", r"\usepackage{amsmath}",
     r"\usepackage{newtxtext,newtxmath}", r"\usepackage[colorlinks=true,citecolor=red,linkcolor=black]{hyperref}",
     r"\usepackage{bm,textcomp,url}", r"\urlstyle{same}", r"\graphicspath{{figs/}}", r"\NameTag{Anticona, \today}",
     r"\renewcommand{\thefigure}{S\arabic{figure}}", r"\renewcommand{\thetable}{S\arabic{table}}", r"\begin{document}",
     r"\title{Supplemental Materials\\[0.5ex] HiBER: Hierarchical Bounded Strength Envelopes for Rockfill and Mine Waste Rock}",
     r"\author[1]{Wilson A. Anticona}", r"\affil[1]{\textbf{[ASCE grade, affiliation, and e-mail to be completed]}}", r"\maketitle",
     r"\noindent This file contains Figs.~S1--S5, Tables~S1--S6, and a worked example of the update, cited in the paper. Equation and table numbers "
     r"without the prefix S refer to the paper.", ""]
for f, w, cap in FIGS:
    T += [r"\begin{figure}[htbp]", r"\centering\includegraphics[width=" + f"{min(w, 6.5):.1f}" + r"in]{" + f + "}", r"\caption{" + tex(cap) + "}", r"\end{figure}"]
T.append(r"\clearpage")
T.append(tabla_tex("Mode B: every procedure evaluated (held-out tests at σ′n ≥ 2 MPa predicted from tests at σ′n ≤ 1.5 MPa of the same set)",
                   S1h, S1f, NOTA_S1, r"p{1.7in}ccccccc"))
T.append(tabla_tex(S2["titulo"], S2["enc"], S2["filas"], S2["nota"], "lccc", r"\small"))
T.append(tabla_tex("Structural comparison of mean and covariance forms (data without censoring)", ["Model", "Mean", "Random-effect covariance", "Parameters",
                   "Log-likelihood", "Out-of-sample log score"], S3f, NOTA_S3, "llp{1.6in}ccc"))
T.append(tabla_tex("Mode A with censored tests: fractions below the 5th and 10th percentiles", ["Band and form", "Below P05", "Below P10", "Mean z"], S4f, NOTA_S4, "lccc"))
S6 = J(AQ / "tabla_S6_r6.json")                                  # escrita por build_hiber_asce6.py (antes Tabla 4 del artículo)
T += EX
T.append(r"\setcounter{table}{5}")
T.append(tabla_tex(S6["titulo"], S6["enc"], S6["filas"], S6["nota"], "lccc", r"\small"))
T += [r"\end{document}", ""]
txt = "\n".join(T)
txt = re.sub(r"\(Cylwik et al\. 2025\)|Cylwik et al\. \(2025\)", "Cylwik et al. (2025)", txt)
(LX / "HiBER_IJGM_supplement_r6.tex").write_text(txt, encoding="utf-8"); print("written latex/HiBER_IJGM_supplement_r6.tex")
