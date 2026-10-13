"""Supplemental Materials of the Leps-P manuscript (round 5): Figs. S1–S5 and Table S1 (every Mode B procedure).
Numbers read from result files."""
import json
from pathlib import Path
from docx import Document
from docx.shared import Pt, Inches
from docx.oxml.ns import qn

AQ = Path(__file__).parent; AN = AQ.parent / "analisis"; FIG = AQ.parent / "figuras" / "lepsp5"
J = lambda p: json.load(open(p, encoding="utf-8"))
CV = J(AN / "lepsp_cv4_metricas.json"); E3 = J(AN / "lepsp_escala3.json")["publicaciones R ≥ 2"]; DG = J(AN / "lepsp_diag_alta.json"); PR = J(AN / "lepsp_perfil.json")
doc = Document(); st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12); st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
doc.add_paragraph().add_run("Supplemental Materials — Leps-P: Probabilistic Strength Envelopes with Stress-Decaying Curvature for Rockfill and Mine Waste Rock").bold = True
neg = lambda s: s.replace("-", "−")
NBG = DG["bg_excluidos_mayor_100"]; RHO = "0.00" if abs(DG["res_vs_bg_alta"]["spearman"]) < 0.005 else neg(f"{DG['res_vs_bg_alta']['spearman']:+.2f}"); NRB = DG["res_vs_bg_alta"]["n"]
EB, EL, EH = (neg(f"{v:+.3f}") for v in (E3["b"][0], E3["ci"][0][0], E3["ci"][0][1]))
FIGS = [("FigS1_stress_coverage.png", 6.0, "Fig. S1. Distribution of effective normal stress on the failure plane in the calibration database."),
        ("FigS2_volumetric_breakage.png", 6.0, f"Fig. S2. Net volumetric strain at the maximum deviator (negative: contraction) and breakage index of Marsal (1973) versus σ′n in the calibration database; shaded: σ′n > 2.75 MPa. Reported breakage indices above 100%, which are impossible by definition, were excluded ({NBG} tests). Above 2.75 MPa the residuals of Leps-P were unrelated to the breakage index (Spearman ρ = {RHO}, n = {NRB})."),
        ("FigS3_profile_likelihood.png", 4.0, f"Fig. S3. Profile log-likelihood of the asymptotic angle φ′∞ relative to its maximum ({PR['ml_max']:.2f}); at each angle the population decay rate ζ0 and the variance parameters were re-estimated by maximum likelihood. φ′∞ = 0 corresponds to the form without an asymptote. Dashed: 3 log-likelihood units below the maximum."),
        ("FigS4_size_effect.png", 5.6, f"Fig. S4. Within-material specimen-size coefficient β_D (bars: 95% confidence intervals; set intercepts adjusted for void ratio). Hatched band: Knapp–Hartung 95% confidence interval of the random-effects mean across {E3['k']} publications with size ratio ≥ 2 ({EB}; {EL} to {EH}). One value outside the axis is annotated."),
        ("FigS5_variance.png", 3.5, "Fig. S5. Shares of the variance of the mean-envelope ln τ for an untested material of low rock quality placed at e = 0.65, scaled from 0.18 m to 1 m maximum particle size.")]
for f, w, cap in FIGS:
    doc.add_picture(str(FIG / f), width=Inches(w)); doc.add_paragraph(cap)
doc.add_paragraph().add_run("Table S1. Mode B: every procedure evaluated (held-out tests at σ′n ≥ 2 MPa predicted from tests at σ′n ≤ 1.5 MPa of the same set)").bold = True
NOM = {"previa": "Prior, no site tests", "ingenuo_m090": "Least-squares fit of φ′1, m = 0.90", "ingenuo_mtr": "Least-squares fit of φ′1, m = median within-set slope of training data",
       "conjunta": "Joint update of both random effects", "nivel": "Level update of each set (Eq. 8)", "descarte": "Level update after discarding flagged sets",
       "sitio": "Recommended procedure: discard flagged sets, joint update with shared laboratory effect"}
t = doc.add_table(rows=1 + len(NOM), cols=7)
for j, h in enumerate(["Procedure", "80% coverage", "Below P10", "SD of z", "CRPS", "Δ vs level update (95% CI)", "Holm-adjusted p"]):
    t.rows[0].cells[j].text = h
for i, (k, nm) in enumerate(NOM.items(), 1):
    o = CV[f"B|{k}"]; c = o.get("vs_nivel")
    vals = [nm, f"{100 * o['cob80']:.0f}%", f"{100 * o['bajo10']:.0f}%", f"{o['sd_z']:.2f}", f"{o['crps']:.4f}",
            neg(f"{c['media']:+.4f} ({c['ic95'][0]:+.4f} to {c['ic95'][1]:+.4f})") if c else "—", f"{c['p_holm']:.2f}" if c else "—"]
    for j, v in enumerate(vals):
        t.rows[i].cells[j].text = v
for row in t.rows:
    for c in row.cells:
        for pp in c.paragraphs:
            for r_ in pp.runs:
                r_.font.size = Pt(9)
doc.add_paragraph("Note: 64 tests, 46 sets, 13 publications. The procedures were developed while examining earlier versions of the model on the "
                  "same held-out sets; the comparisons are exploratory. p-values from exact sign-flip tests on publication means, Holm-adjusted within "
                  "Mode B. CRPS in units of ln τ.")
S2 = J(AQ / "tabla_S2.json")                                  # escrita por build_lepsp_asce5.py (antes Tabla 4 del artículo)
doc.add_paragraph().add_run("Table S2. " + S2["titulo"]).bold = True
t = doc.add_table(rows=1 + len(S2["filas"]), cols=len(S2["enc"]))
for j, h in enumerate(S2["enc"]):
    t.rows[0].cells[j].text = h
for i, f in enumerate(S2["filas"], 1):
    for j, v in enumerate(f):
        t.rows[i].cells[j].text = v
for row in t.rows:
    for c in row.cells:
        for pp in c.paragraphs:
            for r_ in pp.runs:
                r_.font.size = Pt(9)
doc.add_paragraph("Note: " + S2["nota"])
cp = doc.core_properties; cp.author = ""; cp.last_modified_by = ""; cp.title = "Leps-P supplemental materials"
doc.save(str(AQ / "LepsP_IJGM_supplement_r5.docx")); print("written supplement r5")

# ------------------------------------------------------------------ versión LaTeX (clase oficial ascelike-new)
import re  # noqa: E402
import asce_docx as A  # noqa: E402
from asce_docx import tex  # noqa: E402
A.SYM[:0] = [("φ′∞", r"\phi'_\infty"), ("ζ0", r"\zeta_0"), ("τ_D", r"\tau_D")]
S1h = ["Procedure", "80% coverage", "Below P10", "SD of z", "CRPS", "Δ vs level update (95% CI)", "Holm-adjusted p"]
S1f = []
for k, nm in NOM.items():
    o = CV[f"B|{k}"]; c = o.get("vs_nivel")
    S1f.append([nm, f"{100 * o['cob80']:.0f}%", f"{100 * o['bajo10']:.0f}%", f"{o['sd_z']:.2f}", f"{o['crps']:.4f}",
                neg(f"{c['media']:+.4f} ({c['ic95'][0]:+.4f} to {c['ic95'][1]:+.4f})") if c else "—", f"{c['p_holm']:.2f}" if c else "—"])
NOTA_S1 = ("64 tests, 46 sets, 13 publications. The procedures were developed while examining earlier versions of the model on the "
           "same held-out sets; the comparisons are exploratory. p-values from exact sign-flip tests on publication means, Holm-adjusted "
           "within Mode B. CRPS in units of ln τ.")


def tabla_tex(titulo, enc, filas, nota, cols):
    L = [r"\begin{table}[htbp]", r"\caption{" + tex(titulo) + "}", r"\centering\footnotesize", r"\renewcommand{\arraystretch}{1.2}", r"\setlength{\tabcolsep}{3.5pt}",
         r"\begin{tabular}{" + cols + "}", r"\hline\hline", " & ".join(tex(h) for h in enc) + r" \\", r"\hline"]
    L += [" & ".join(tex(str(v)) for v in f) + r" \\" for f in filas]
    L += [r"\hline\hline", r"\end{tabular}", r"\par\vspace{4pt}\parbox{\linewidth}{\footnotesize Note: " + tex(nota) + "}", r"\end{table}"]
    return "\n".join(L)


T = [r"\documentclass[Journal,letterpaper,InsideFigs,NoLists,NoLineNumbers]{ascelike-new}", r"\WarningFilter{caption}{Unknown document class}",
     r"\usepackage[utf8]{inputenc}", r"\usepackage[T1]{fontenc}", r"\usepackage{lmodern}", r"\usepackage{graphicx}",
     r"\usepackage[style=base,figurename=Fig.,labelfont=bf,labelsep=period]{caption}", r"\usepackage{amsmath}",
     r"\usepackage{newtxtext,newtxmath}", r"\usepackage[colorlinks=true,citecolor=red,linkcolor=black]{hyperref}",
     r"\usepackage{bm,textcomp,url}", r"\urlstyle{same}", r"\graphicspath{{figs/}}", r"\NameTag{Anticona, \today}",
     r"\renewcommand{\thefigure}{S\arabic{figure}}", r"\renewcommand{\thetable}{S\arabic{table}}", r"\begin{document}",
     r"\title{Supplemental Materials\\[0.5ex] Leps-P: Probabilistic Strength Envelopes with Stress-Decaying Curvature for Rockfill and Mine Waste Rock}",
     r"\author[1]{Wilson A. Anticona}", r"\affil[1]{\textbf{[ASCE grade, affiliation, and e-mail to be completed]}}", r"\maketitle",
     r"\noindent This file contains Figs.~S1--S5 and Tables~S1--S2, cited in the paper. Equation and table numbers without the prefix S refer to the paper.", ""]
for f, w, cap in FIGS:
    T += [r"\begin{figure}[htbp]", r"\centering\includegraphics[width=" + f"{min(w, 6.5):.1f}" + r"in]{" + f + "}",
          r"\caption{" + tex(re.sub(r"^Fig\. S\d\. ", "", cap)) + "}", r"\end{figure}", r"\clearpage"]
T.append(tabla_tex("Mode B: every procedure evaluated (held-out tests at σ′n ≥ 2 MPa predicted from tests at σ′n ≤ 1.5 MPa of the same set)",
                   S1h, S1f, NOTA_S1, r"p{1.75in}ccccp{1.2in}p{0.55in}"))
T.append(tabla_tex(S2["titulo"], S2["enc"], S2["filas"], S2["nota"], "lccc"))
T += [r"\end{document}", ""]
(AQ / "latex" / "LepsP_IJGM_supplement_r5.tex").write_text("\n".join(T), encoding="utf-8"); print("written latex/LepsP_IJGM_supplement_r5.tex")
