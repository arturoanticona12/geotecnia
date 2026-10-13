"""Leps-P manuscript for the ASCE International Journal of Geomechanics (Technical Paper).
ASCE format: double spacing, continuous line numbers, unnumbered word headings, equations as Word equation objects,
figure captions listed at the end followed by tables, ASCE author–date references. All numbers are read from results."""
import json, math, re
from pathlib import Path
import numpy as np
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_COLOR_INDEX, WD_BREAK
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn
from docx.shared import Pt, Inches
from lxml import etree
import latex2mathml.converter as l2m

AQ = Path(__file__).parent; R = AQ.parent; AN = R / "analisis"; AA = R / "analisis_antamina"
RES = Path(r"H:\Mi unidad\slide2-bench-intercambio\resultados")
PAR = json.load(open(R / "leps3" / "lepsp_parametros.json")); FX = PAR["formas"]["x2"]
MET = json.load(open(AN / "lepsp_cv_metricas.json", encoding="utf-8"))
ESC = json.load(open(AN / "lepsp_escala.json")); SIT = json.load(open(AA / "lepsp_sitio.json", encoding="utf-8"))
EST = json.load(open(AN / "lepsp_estabilidad.json", encoding="utf-8")); CON = json.load(open(AN / "consol_frente.json", encoding="utf-8"))
S60 = json.load(open(RES / "60-lepsp-estabilidad" / "fs_por_escenario.json", encoding="utf-8"))["lepsp_estabilidad"]["fs"]
S61 = {k.split(" / ")[-1]: v for k, v in json.load(open(RES / "61-lepsp-nodrenado" / "fs_por_escenario.json", encoding="utf-8"))["lepsp_nodrenado"]["fs"].items()}
XSL = etree.XSLT(etree.parse(r"C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL"))

# ------------------------------------------------------------------ numbers
b = dict(zip(FX["nombres"], FX["beta"])); se = np.sqrt(np.diag(FX["cov_beta"]))
SE = dict(zip(FX["nombres"], se))
psi = np.array(FX["psi"]); H = []
for s in FX["muestras"]:
    p = np.array(s["psi"]); H.append([math.exp(p[0]), math.exp(p[1]), math.tanh(p[2]), math.exp(p[3]), math.exp(p[4]), math.tanh(p[5]), math.exp(p[6]), p[7]])
H = np.array(H); HP = lambda i: (np.median(H[:, i]), np.percentile(H[:, i], 5), np.percentile(H[:, i], 95))
pt = [math.exp(psi[0]), math.exp(psi[1]), math.tanh(psi[2]), math.exp(psi[3]), math.exp(psi[4]), math.tanh(psi[5]), math.exp(psi[6]), psi[7]]
deg = lambda th: math.degrees(math.atan(math.exp(th)))
phi_e0 = {c: deg(b[c]) for c in ("good", "moderate", "low")}
omega = -b["e"] * math.sin(math.radians(41)) * math.cos(math.radians(41)) * 180 / math.pi
var_b = pt[0] ** 2 + pt[3] ** 2; frac_between = var_b / (var_b + pt[6] ** 2); frac_lab = pt[0] ** 2 / var_b
N = PAR["n"]
A_all = MET["pub|M2|todo"]; A_hi = MET["pub|M2|σ′n>2.75"]; A0 = MET["pub|M0|todo"]; ALR = MET["Material Type|M0|todo"]; AU = MET["pub|M5|todo"]
BB = MET["B|M2|solo_theta_si_conflicto"]; BF = MET["B|M2|completo"]
pc = lambda v: f"{100 * v:.0f}%"
f2 = lambda v: f"{v:.2f}"; f3 = lambda v: f"{v:.3f}"
neg = lambda s: s.replace("-", "−")
SL = lambda g, e, met="gle/morgenstern-price": S60[f"{g} / {e}"][met]
ES = ESC["similares"]; EA = ESC["todos"]; EN = ESC["no_similares"]
dphi_scale = deg(math.log(math.tan(math.radians(40)))) - 40
LIT = SIT["litologias"]; KM, KH, KI, KS = list(LIT)
DIAG = SIT["diag"]
BOT = SIT["botadero"]; KB = list(BOT)
sn_i = {s: i for i, s in enumerate(SIT["sn"])}
pf7 = EST["pf"]["700"]
cr = {(c["caso"], c["Hs"], c["k"]): c["ru"] for c in CON}

# ------------------------------------------------------------------ document setup
doc = Document()
st = doc.styles["Normal"]; st.font.name = "Times New Roman"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Times New Roman")
st.paragraph_format.line_spacing = 2.0; st.paragraph_format.space_after = Pt(0)
sec = doc.sections[0]
for m in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
    setattr(sec, m, Inches(1))
ln = OxmlElement("w:lnNumType"); ln.set(qn("w:countBy"), "1"); ln.set(qn("w:restart"), "continuous"); sec._sectPr.append(ln)
fp = sec.footer.paragraphs[0]; fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
for tag, txt in (("begin", None), (None, " PAGE "), ("end", None)):
    r = fp.add_run()
    if tag:
        e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), tag); r._r.append(e)
    else:
        e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)


def omml(latex):
    mml = l2m.convert(latex)
    return XSL(etree.fromstring(mml.encode())).getroot()


SYM = [("b^(p)", r"\mathbf{b}^{(p)}"), ("b^(s)", r"\mathbf{b}^{(s)}"), ("C_β", r"\mathbf{C}_\beta"), ("β̂", r"\hat{\boldsymbol{\beta}}"),
       ("β_c", r"\beta_c"), ("β_e", r"\beta_e"), ("β_x", r"\beta_x"), ("β_D", r"\beta_D"), ("G_p", r"\mathbf{G}_p"), ("G_s", r"\mathbf{G}_s"),
       ("σε²(*x*i)", r"\sigma_\varepsilon^2(x_i)"), ("σε²", r"\sigma_\varepsilon^2"), ("σε", r"\sigma_\varepsilon"), ("φ′e=0", r"\phi'_{e=0}"),
       ("φ′1", r"\phi'_1"), ("φ′s", r"\phi'_s"), ("σ′n", r"\sigma'_n"), ("σ′3", r"\sigma'_3"), ("σ′v", r"\sigma'_v"), ("Δu/σv", r"\Delta u/\sigma_v"),
       ("σv", r"\sigma_v"), ("σ0", r"\sigma_0"), ("p_a", r"p_a"), ("*D*max", r"D_{max}"), ("*D*f", r"D_f"), ("*D*l", r"D_l"),
       ("*x*i", r"x_i"), ("*y*i", r"y_i"), ("*x̄*", r"\bar{x}"), ("x̃", r"\tilde{\mathbf{x}}"), ("**z**", r"\mathbf{z}"),
       ("Su = ", r"S_u="), ("K0", r"K_0"), ("c2", r"c_2"), ("a0, a1", r"a_0, a_1"), ("a1", r"a_1"), ("D_f, D_l", r"D_f, D_l")]


def simbolos(text):
    parts = re.split(r"(\$[^$]+\$|https?://\S+)", text); out = []
    for s in parts:
        if s.startswith("$") or s.startswith("http"):
            out.append(s); continue
        for a, l in SYM:
            s = s.replace(a, f"${l}$")
        out.append(s)
    return "".join(out)


def runs(p, text, _sym=True):
    if _sym:
        text = simbolos(text)
    for tok in re.split(r"(\$[^$]+\$|\*[^*]+\*|\[\[[^\]]+\]\])", text):
        if not tok:
            continue
        if tok.startswith("$"):
            p._p.append(parse_xml(etree.tostring(omml(tok[1:-1]))))
        elif tok.startswith("*") and "$" in tok:
            runs(p, tok[1:-1], False)
        elif tok.startswith("*"):
            p.add_run(tok[1:-1]).italic = True
        elif tok.startswith("[["):
            r = p.add_run(tok[2:-2]); r.font.highlight_color = WD_COLOR_INDEX.YELLOW
        else:
            p.add_run(tok)
    return p


def P(text, indent=True):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.LEFT
    if indent:
        p.paragraph_format.first_line_indent = Inches(0.5)
    return runs(p, text)


def Hd(text, level=1):
    p = doc.add_paragraph(); r = p.add_run(text); r.bold = level == 1; r.italic = level == 2
    p.paragraph_format.keep_with_next = True
    return p


NEQ = [0]


def EQ(latex):
    NEQ[0] += 1
    p = doc.add_paragraph(); pf = p.paragraph_format
    pf.tab_stops.add_tab_stop(Inches(3.25), alignment=1); pf.tab_stops.add_tab_stop(Inches(6.5), alignment=2)
    p.add_run("\t"); p._p.append(parse_xml(etree.tostring(omml(latex)))); p.add_run(f"\t({NEQ[0]})")


def br():
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)


# ================================================================== TITLE PAGE
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Leps-P: A Probabilistic and Updatable Extension of the Leps Shear Strength Envelopes for Rockfill and Mine Waste Rock"); r.bold = True
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, "[[Author names, ASCE grade and affiliations to be confirmed. Corresponding author e-mail.]]")
Hd("Abstract")
P("The Leps envelopes, recently updated with a database of more than 900 large-scale triaxial tests (Leps 2.0), are the "
  "standard empirical estimate of the drained shear strength of rockfill and coarse mine waste rock. Waste dumps 500–700 m "
  "high and reliability-based design require more than a central envelope: they need a strength distribution that depends "
  "on stress, can be updated with site tests, and states how much uncertainty is added when extrapolating beyond the data. "
  "This paper presents Leps-P, a three-level hierarchical model of the Leps power envelope in which the reference secant "
  "friction angle and the curvature exponent vary randomly between laboratories and between materials, the within-material "
  "dispersion depends on stress, and hyperparameter uncertainty is propagated by Markov chain Monte Carlo sampling. The model "
  f"was calibrated with {N['ensayos']} tests on {N['sets']} materials from {N['pub']} publications and evaluated by leaving out one "
  f"publication at a time. Without site tests, the 80% predictive interval contained {pc(A_all['m']['cob80'])} of the "
  f"held-out tests, with {pc(A_all['m']['bajo10'])} below the 10th percentile; its accuracy was equivalent to that of the "
  "deterministic envelope with constant dispersion. With site tests at low stress and an updating rule that guards against "
  "prior–data conflict, the continuous ranked probability score at high stress improved significantly "
  f"({f3(BB['sin']['crps'])} to {f3(BB['sitio']['crps'])}). Between-laboratory differences accounted for {pc(frac_lab)} of "
  "the between-material variance of the reference angle. Within-material comparisons showed a specimen-size effect "
  f"consistent with Weibull scaling but about 60% of its usual magnitude (κ = {f2(ES['kappa'])} ± {f2(ES['se'] / 0.14)}). "
  "Applied to waste rock from a polymetallic skarn deposit, the strength uncertainty alone gave negligible probabilities of "
  "failure for dumps up to 700 m, whereas a saturated, contractive base controlled stability. Leps-P, its code, and its "
  "parameters can be recalibrated as high-pressure tests become available.", indent=False)
Hd("Practical Applications")
P("Engineers who design high waste dumps and rockfill dams often have few or no large-scale shear tests of their own and rely "
  "on published charts. This paper turns the most widely used chart into a tool that gives not only a best estimate of "
  "strength but also its range, how that range grows at the very high stresses found at the base of tall dumps, and how much "
  "it shrinks when a few laboratory tests of the site material are added. The method also warns the user when site tests "
  "disagree with the published experience, and when strength is being extrapolated beyond the stresses that have ever been "
  "tested. An example for a 700 m waste dump shows that, once the strength of the waste rock is characterized, the safety of "
  "a very high dump depends mostly on keeping its base drained: a saturated base that cannot drain during construction can "
  "reduce the factor of safety below one even when the drained strength is well known. The free software that accompanies "
  "the paper can be used to obtain design strength envelopes and to update them as new tests become available.", indent=False)
P("*Author keywords:* Rockfill; Mine waste rock; Shear strength; Nonlinear failure envelope; Hierarchical Bayesian model; "
  "Reliability-based design; High waste dumps; Specimen-size effect.", indent=False)

# ================================================================== INTRODUCTION
Hd("Introduction")
P("Leps (1970) compiled 109 large-scale triaxial tests and proposed three nonlinear envelopes for rockfill. For five decades "
  "those curves were used for dams and waste dumps whenever site-specific tests were unavailable. Cylwik et al. (2025) "
  "updated them with a public database of 938 tests (Arrieta 2025), adopted the power criterion of De Mello (1977) and "
  "Charles and Watts (1980) with a single fitting parameter, the secant friction angle at σ′n = 10p_a, and related that "
  "angle to rock quality and void ratio. That update is referred to as Leps 2.0.")
P("Two developments in mining practice call for a further step. First, waste dumps now reach 500–700 m (Valenzuela et al. "
  "2008), so effective normal stresses at their base reach 10–15 MPa in a material that crushes, loses dilatancy and "
  "permeability, and may respond contractively (Linero et al. 2007; Ovalle et al. 2020), whereas the largest normal stress in "
  "the database is 7.9 MPa. Second, design is moving toward reliability-based criteria (Read and Stacey 2009; Hawley and Cunning "
  "2017), which require a strength distribution, its dependence on stress, and a rule to combine published experience with "
  "site tests.")
P("Bayesian and hierarchical models have been used to characterize geotechnical properties from generic databases and few "
  "site data (Ching and Phoon 2019; Ching et al. 2021) and, for rockfill, to infer the parameters of the Barton and Kjærnsli (1981) criterion for material "
  "groups of a single project (Contreras et al. 2022; Contreras and Linero-Molina 2025). The present work builds on both lines "
  "and contributes: (1) a hierarchical model of the stress-dependent envelope itself, with random reference angle and "
  "curvature and physical covariates, calibrated on the worldwide database; (2) separation of laboratory (publication) "
  "and material variability; (3) systematic out-of-sample evaluation by leaving out entire publications; (4) an updating rule "
  "with a prior–data conflict diagnostic, validated out of sample; (5) quantification of shape and specimen-size uncertainty "
  "in extrapolation; and (6) a design format linked to characteristic values and probability of failure. The approach is "
  "illustrated with waste rock from a polymetallic skarn deposit in the Andes and with waste dumps 150–700 m high.")

# ================================================================== FORMULATION
Hd("Database and Model Formulation")
Hd("Calibration Database", 2)
P(f"The public database of Leps 2.0 (Arrieta 2025) was used. Tests with σ′3 ≥ 60 kPa, reported initial void ratio, and at "
  f"least two tests per set were retained: {N['ensayos']} tests on {N['sets']} sets from {N['pub']} publications. A set is a "
  "material with a given gradation, density, and lithology tested in one program. Rock quality was assigned following Table 5 "
  "of Cylwik et al. (2025), and failure was taken at maximum deviator stress, as in the database. Fig. 1 shows that the "
  "data are concentrated between 0.1 and 3 MPa; 90 tests exceed 3 MPa and come from eight publications.")
Hd("Hierarchical Envelope", 2)
P("The Leps 2.0 criterion is the power law")
EQ(r"\tau = \tan\phi'_1\,\sigma_0^{1-m}\,\sigma_n'^{\,m}")
P("where σ0 = 10p_a, p_a = 0.1013 MPa is atmospheric pressure, and φ′1 is the secant friction angle at σ′n = σ0. In logarithmic variables "
  "*x* = ln(σ′n/σ0) and *y* = ln(τ/σ0), Eq. (1) is a straight line with intercept θ = ln tan φ′1 and slope *m*. Leps-P "
  "treats every set *j* tested in publication *k* as a realization of a population:", indent=False)
EQ(r"y_{ijk}=\theta_{jk}+m_{jk}x_{ijk}+c_2x_{ijk}^2+\varepsilon_{ijk}")
EQ(r"\theta_{jk}=\beta_{c(jk)}+\beta_e e_{jk}+b_{0k}^{(p)}+b_{0jk}^{(s)},\quad m_{jk}=\beta_x+b_{1k}^{(p)}+b_{1jk}^{(s)}")
EQ(r"\mathbf{b}^{(p)}\sim N(\mathbf{0},\mathbf{G}_p),\quad \mathbf{b}^{(s)}\sim N(\mathbf{0},\mathbf{G}_s),\quad \ln\sigma_\varepsilon(x)=a_0+a_1x")
P("where β_c is the intercept of rock-quality class *c* (good, moderate, or low), β_e is the effect of initial void ratio *e*, "
  "β_x is the mean curvature, *c*2 is a population term that lets the local slope change with stress, b^(p) and b^(s) are "
  "the publication (laboratory and procedure) and set (material) random effects on (θ, *m*) with covariance matrices G_p "
  "and G_s, and ε is the dispersion between specimens of the same material. Eqs. (2)–(4) form a linear mixed model "
  "(Laird and Ware 1982) with heteroscedastic residuals. With β_e and β_c, the median of φ′1 approximates the relation "
  "φ′1 = φ′e=0 − ωe of Leps 2.0; with G_p = G_s = 0, σε = 0 and c2 = 0, Eq. (2) reduces to Eq. (1).", indent=False)
Hd("Predictive Distribution and Shape Constraint", 2)
P("For a new material of class *c* and void ratio *e* tested by a new laboratory, *y* at stress *x* is normal with")
EQ(r"E[y]=\beta_c+\beta_e e+\beta_x x+c_2x^2,\quad \mathrm{Var}[y]=\mathbf{z}^T(\mathbf{G}_p+\mathbf{G}_s)\mathbf{z}+\tilde{\mathbf{x}}^T\mathbf{C}_\beta\tilde{\mathbf{x}}+\sigma_\varepsilon^2(x)")
P("with **z** = (1, *x*)ᵀ, x̃ the covariate vector, and C_β the covariance of the fixed effects. The first term is the "
  "uncertainty of the mean envelope of the material; the last is the scatter of a single test about it. The distinction "
  "matters in design: a long failure surface averages the second term but not the first (Vanmarcke 1977; Christian et al. "
  "1994). Hyperparameter uncertainty is propagated by sampling (G_p, G_s, a0, a1) from their posterior and, for each "
  "sample, the fixed effects from N(β̂, C_β). A power envelope whose local slope exceeds one is convex and its secant angle "
  "grows without bound, which has no physical support in granular materials; samples whose local slope *m* + 2c2*x* exceeds "
  "one for σ′n ≤ 20 MPa are therefore discarded.", indent=False)
Hd("Updating with Site Tests and Prior–Data Conflict", 2)
P(r"Given *n* site tests (*x*i, *y*i) of one material, the random effects $\mathbf{b}=\mathbf{b}^{(p)}+\mathbf{b}^{(s)}$ are updated with the exact "
  "Gaussian posterior")
EQ(r"\mathbf{C}_{post}=\left(\mathbf{G}^{-1}+\mathbf{Z}^T\mathbf{R}^{-1}\mathbf{Z}\right)^{-1},\quad \boldsymbol{\mu}_{post}=\mathbf{C}_{post}\mathbf{Z}^T\mathbf{R}^{-1}\mathbf{r}")
P(r"where $\mathbf{G}=\mathbf{G}_p+\mathbf{G}_s$, $\mathbf{Z}$ has rows (1, *x*i), $\mathbf{R}=\mathrm{diag}\,\sigma_\varepsilon^2(x_i)$, and $\mathbf{r}$ is the vector of residuals with respect to the "
  "prior mean. Triaxial results are converted to (σ′n, τ) with Eqs. (13), (14), and (16) of Cylwik et al. (2025). Before "
  "updating, consistency between site tests and prior is checked with the prior predictive Mahalanobis distance", indent=False)
EQ(r"D^2=\mathbf{r}^T\left(\mathbf{Z}\mathbf{G}\mathbf{Z}^T+\tilde{\mathbf{X}}\mathbf{C}_\beta\tilde{\mathbf{X}}^T+\mathbf{R}\right)^{-1}\mathbf{r}\sim\chi^2_n")
P("Updating both θ and *m* requires tests that span a range of stresses. The rule adopted, and validated below, is: update "
  "(θ, *m*) jointly only if the site tests span a ratio of normal stresses of at least three and the conflict test is "
  "passed (*p* ≥ 0.05); otherwise update only the level of the envelope at the centroid of the site data, "
  "*x̄*, and keep the prior conditional distribution of the slope. In the second case the envelope pivots about the tested "
  "range instead of about σ0, which avoids spurious extrapolation toward low stress.")
Hd("Specimen Size", 2)
P("Following the Weibull scaling of Frossard et al. (2012) and Ovalle et al. (2014), the envelope of a material with "
  "maximum particle size *D*f is obtained from tests at size *D*l by a shift in θ with *m* unchanged:")
EQ(r"\Delta\theta=\beta_D\ln\left(D_f/D_l\right),\quad \beta_D=-\kappa\left(1-m\right)")
P("where κ is the ratio of a size exponent to the Weibull modulus. Rather than adopting κ from particle-crushing tests, "
  "β_D was estimated within materials of the database tested at several sizes (see Results), and it enters Leps-P as a "
  "random variable with the between-material dispersion found there.", indent=False)

# ================================================================== ESTIMATION & EVALUATION
Hd("Estimation and Out-of-Sample Evaluation")
P("The fixed effects and random effects were integrated analytically and the variance parameters were estimated by "
  "restricted maximum likelihood with publication blocks. The posterior of the eight variance parameters was sampled with "
  "an adaptive Metropolis algorithm on the restricted likelihood (two chains; potential scale reduction ≤ 1.04). Two "
  "forms were fitted: the quadratic form of Eq. (2) and a pure power form (c2 = 0).")
P("The model was refitted leaving out each publication and its tests were predicted, so every prediction refers to a "
  "laboratory, material, and procedure not used in calibration. To check that the class assignment, which Cylwik et al. "
  "(2025) based on measured strength, does not leak information, the evaluation was repeated leaving out each material "
  "type. Two uses were evaluated. In Mode A (no site tests) the predictive distribution of Eq. (5) was scored. In Mode B, "
  "each held-out set with at least two tests at σ′n ≤ 1.5 MPa and one at σ′n ≥ 2 MPa was updated with the former, and the "
  "latter were predicted. Metrics were the coverage of the central 80% interval, the fraction of tests below the 10th "
  "percentile (which should be close to 10% for a design envelope at that percentile to mean what it says), the mean width "
  "of the 80% interval, the continuous ranked probability score (CRPS; Gneiting and Raftery 2007), and the quantile "
  "(pinball) loss at 10%. Confidence intervals were obtained by bootstrapping whole publications. The reference was the "
  "Leps 2.0 envelope (*m* = 0.9) with a constant dispersion in ln τ estimated in the same training fold.")

# ================================================================== RESULTS
Hd("Results")
Hd("Parameters", 2)
P(f"Table 1 lists the parameters. The mean curvature is β_x = {f3(b['x'])} and the quadratic term is "
  f"c2 = {f3(b['x2'])} ± {f3(SE['x2'])}, so the local slope rises with stress, from about 0.84 at 0.2 MPa to about 0.89 at "
  "15 MPa. This agrees with the increase of the power exponent with stress range reported by Charles and Watts (1980) and "
  f"Indraratna et al. (1993). The reference angles at *e* = 0 are {f2(phi_e0['good'])}°, {f2(phi_e0['moderate'])}°, and "
  f"{f2(phi_e0['low'])}° for good, moderate, and low rock quality, and the void-ratio effect is about {omega:.0f}° per unit "
  "of *e* at φ′1 ≈ 41°, compared with 20° in Leps 2.0. The median φ′1 of a new material reproduces the Leps 2.0 table within "
  "1.8° for 0.3 ≤ *e* ≤ 0.6; because Leps-P estimates the curvature (0.86) instead of fixing it at 0.9, its median envelope "
  "is lower than the Leps 2.0 envelope away from the anchor, by about 2° at 10 MPa for moderate rock quality.")
P(f"Heteroscedasticity was strongly supported: the within-material dispersion decreases from about 0.056 at 0.2 MPa to "
  f"{f3(pt[6])} at σ0 and 0.020 at 7.5 MPa (Table 1). The publication level was also strongly supported: laboratories and "
  f"procedures account for {pc(frac_lab)} of the between-material variance of θ and for most of that of *m*. At σ0, "
  f"between-material and between-laboratory differences make up {pc(frac_between)} of the predictive variance. Within-material "
  "dispersion, which is mostly specimen-to-specimen and testing error, is a small part of the total.")
Hd("Calibration without Site Tests", 2)
P(f"Leaving out each publication, the 80% interval contained {pc(A_all['m']['cob80'])} of the tests "
  f"(95% CI {pc(A_all['ci']['cob80'][0])}–{pc(A_all['ci']['cob80'][1])}) and {pc(A_all['m']['bajo10'])} fell below the 10th "
  f"percentile (Fig. 3, Table 2). Leaving out each material type gave {pc(ALR['m']['cob80'])} and {pc(ALR['m']['bajo10'])}, "
  "so the class assignment does not inflate the scores. Replacing the class by the uniaxial compressive strength of the "
  f"rock degraded all metrics (CRPS {f3(AU['m']['crps'])} versus {f3(A_all['m']['crps'])}). The CRPS of Leps-P and of the "
  f"reference were statistically indistinguishable (difference {neg(f'{A_all[chr(100)+chr(99)+chr(114)+chr(112)+chr(115)][0]:+.4f}')}, "
  f"95% CI {neg(f'{A_all[chr(100)+chr(99)+chr(114)+chr(112)+chr(115)][1]:+.4f}')} to {neg(f'{A_all[chr(100)+chr(99)+chr(114)+chr(112)+chr(115)][2]:+.4f}')}). "
  "Without site tests, therefore, Leps-P does not predict the strength of a new material better than Leps 2.0 with a constant "
  "dispersion; its contribution in that case is a calibrated and stress-dependent description of the uncertainty.")
P(f"Above 2.75 MPa the Leps-P intervals were wider than necessary: coverage was {pc(A_hi['m']['cob80'])}, only "
  f"{pc(A_hi['m']['bajo10'])} of the tests fell below the 10th percentile, and the 10% quantile loss favored the reference. "
  "Materials converge at high stress (Indraratna et al. 1993) faster than the random-slope model assumes. Leps-P is thus "
  "conservative at high stress, and the extra width is the price of not assuming the convergence beyond the data.")
Hd("Value of Site Tests", 2)
P(f"In Mode B ({BB['sets']} sets, {BB['sitio']['n']} tests at σ′n ≥ 2 MPa from 13 publications), the prior intervals were "
  f"too wide for these materials (coverage {pc(BB['sin']['cob80'])}). Updating θ and *m* jointly narrowed the interval but "
  f"made it overconfident (standard deviation of standardized residuals {f2(BF['sitio']['sdz'])}) and did not improve the "
  f"CRPS significantly. With the updating rule, the CRPS improved from {f3(BB['sin']['crps'])} to {f3(BB['sitio']['crps'])} "
  f"(difference {neg(f'{BB[chr(100)+chr(99)+chr(114)+chr(112)+chr(115)][0]:+.4f}')}, 95% CI "
  f"{neg(f'{BB[chr(100)+chr(99)+chr(114)+chr(112)+chr(115)][1]:+.4f}')} to {neg(f'{BB[chr(100)+chr(99)+chr(114)+chr(112)+chr(115)][2]:+.4f}')}), "
  f"the mean width of the 80% interval fell from {f3(BB['sin']['ancho80'])} to {f3(BB['sitio']['ancho80'])} in ln τ, coverage "
  f"was {pc(BB['sitio']['cob80'])}, and {pc(BB['sitio']['bajo10'])} of the tests fell below the 10th percentile (Fig. 4). A "
  "few conventional tests at low stress thus improve both the accuracy and the sharpness of the strength predicted at high "
  f"stress. The conflict test flagged {pc(BB['conflicto'])} of the sets.")
Hd("Form of the Envelope in Extrapolation", 2)
P("The quadratic and power forms are indistinguishable within the data (Fig. 2) but diverge beyond them: for moderate rock "
  "quality and *e* = 0.45, the median secant angle at 15 MPa is 31.6° with the quadratic form and 30.5° with the power form, "
  "and the 10th percentiles are 27.2° and 26.0°. The power form is the conservative choice when extrapolating. A floor at a "
  "critical-state angle was not imposed because the critical-state line of crushable rockfill moves with breakage (Ventini "
  "et al. 2021) and the critical-state angle itself decreases with stress and breakage in large triaxial tests (Xiao et al. "
  "2014a, b); such a floor cannot be identified as a material constant with the present data.")
Hd("Specimen-Size Effect", 2)
P(f"Eighteen materials of the database were tested at more than one maximum particle size (Fig. 5). Across all of them the "
  f"mean β_D was {neg(f'{EA[chr(98)]:+.3f}')} ± {f3(EA['se'])} with a large between-material dispersion "
  f"({f3(EA['tau'])}), and the sign of the effect varied. In most groups with a positive β_D the gradation became wider or "
  "the density increased as *D*max increased, so gradation and packing, not size alone, controlled the result (see also "
  "Alonso et al. 2012). In the five groups with parallel gradation and similar density, "
  f"β_D = {neg(f'{ES[chr(98)]:+.3f}')} ± {f3(ES['se'])} (κ = {f2(ES['kappa'])} ± {f2(ES['se'] / 0.14)}), "
  "consistent in sign with Weibull scaling (Frossard et al. 2012) but about 60% of the magnitude implied by κ ≈ 0.4, in line "
  "with the observation of Ovalle et al. (2014) that the method is conservative. For a material tested with *D*max = 178 mm "
  "and placed with *D*max ≈ 1 m, the median reduction in φ′s is about 2° with a standard deviation of about 1.5°. The "
  "scale shift is therefore a source of uncertainty of the same order as the between-material variability, and it is reduced "
  "only by large-scale tests of the site material.")

# ================================================================== APPLICATION
Hd("Application: Waste Rock from a Polymetallic Skarn Deposit")
Hd("Site Data", 2)
P(f"The deposit is a polymetallic skarn in the Andes whose waste rock is composed of metamorphic carbonate rock (marble), "
  "hornfels, intrusive rock, and sedimentary carbonate rocks (limestone and marl). Drained triaxial tests on specimens 0.6–1.0 m "
  f"in diameter without tailings were used: 17 tests in five sets, *D*max = {SIT['d_lab']:.0f} mm, σ′3 = 0.5–2.5 MPa, and "
  "failure at maximum deviator stress. Replicates of one material were grouped, and single tests on smaller specimens were "
  "excluded. Rock quality was assigned as low for the metamorphic carbonate, intrusive, and sedimentary carbonate rocks, and as "
  "moderate for hornfels. The sedimentary carbonate rocks have no tests and keep the prior. Illustrative mass fractions of "
  "40%, 20%, 15%, and 25% were used for the dump.")
Hd("Envelopes by Lithology", 2)
P(f"Table 3 and Fig. 6 give the field-scale envelopes, after the size shift from {SIT['d_lab']:.0f} mm to 1,000 mm. The "
  "metamorphic carbonate and intrusive sets spanned stress ratios of about four and passed the conflict test, so θ and *m* "
  "were updated. The hornfels tests spanned a ratio of 2.6 and failed the conflict test (*p* < 0.001): their secant angle "
  "increased from 41.7° to 45.1° as σ′n rose from 1.6 to 4.2 MPa, which the population model regards as implausible. The "
  "level of the hornfels envelope was updated at the centroid of the tests, and its slope kept the prior. The likely cause is "
  "the failure definition: the specimens were still contracting and hardening at 11–20% axial strain, so the maximum deviator "
  "reflects the strain limit of the test. The diagnostic thus identifies data that should be reviewed before they are trusted "
  "in extrapolation. The metamorphic carbonate, which dominates the dump, loses strength with stress faster than the "
  "intrusive rock, while the untested sedimentary rocks have the widest band and are the largest source of uncertainty.")
Hd("Dump-Average Envelope and Correlation between Lithologies", 2)
P("A failure surface through a mixed dump mobilizes the mass-weighted strength of the lithologies it crosses. The "
  "lithology envelopes were sampled jointly, sharing hyperparameters, fixed effects, and size shift (systematic "
  "uncertainty), with independent material effects. Three assumptions bound the result at 15 MPa (Table 3): the model "
  f"correlation gives a P05 of {BOT[KB[0]]['P05'][-1]:.1f}°, full correlation between lithologies gives "
  f"{BOT[KB[1]]['P05'][-1]:.1f}°, and a surface that crosses only the weakest lithology gives "
  f"{BOT[KB[2]]['P05'][-1]:.1f}°. The difference between the last two values, about 6°, is larger than any other source "
  "of uncertainty considered and depends on how the lithologies are placed in the dump, which is a design decision.")
Hd("Stability of Dumps 150–700 m High", 2)
P("Dumps with an overall slope of 2H:1V, unit weight 21 kN/m³, and a competent level foundation were analyzed with the "
  "envelopes as tabulated functions, using Bishop's (1955) method with a circular search in a purpose-written code and the "
  "Morgenstern and Price (1965) and Spencer (1967) methods in Slide2 9.043 (Rocscience [[year]]). The two programs agreed "
  "within 0.010; the purpose-written code was slightly higher. Table 4 summarizes the results. For the 700 m dump, "
  f"the factor of safety is {f2(SL('H700 fundacion horizontal', 'Sitio P50'))} with the median envelope of the site waste rock, "
  f"{f2(SL('H700 fundacion horizontal', 'Sitio P05'))} with its characteristic (P05) envelope, "
  f"{f2(SL('H700 fundacion horizontal', 'Segregacion P05'))} if the surface crosses only the weakest lithology, and "
  f"{f2(SL('H700 fundacion horizontal', 'Generico P05'))} for a generic material of moderate quality without tests. Even for "
  f"700 m, the critical circle reached σ′n ≈ {EST['det']['700|Desmonte del sitio, P50']['snmax']:.1f} MPa, within the "
  "calibration range: on a competent level foundation the global factor of safety of a high dump is controlled by stresses "
  "of 1–3 MPa, not by the extrapolated part of the envelope.")
P(f"A Monte Carlo analysis with 400 joint samples of the dump-average envelope gave, for the 700 m dump, a median factor "
  f"of safety of {f2(pf7['FS_P50'])}, a 10th percentile of {f2(pf7['FS_P10'])}, a minimum of {f2(pf7['FS_min'])}, and a "
  f"coefficient of variation of {f3(pf7['cov'])}, with no failures. The factor of safety computed with the P10 envelope "
  "approximated the 10th percentile of the factor of safety. The uncertainty of the drained strength alone, once quantified, "
  "does not control the reliability of a high dump on a competent, drained foundation.")
Hd("Base Saturation and Undrained Response", 2)
p50ru = S60["H700 ladera 10 basal ru 0.2 / Sitio P50"]["gle/morgenstern-price"]; p05ru = S60["H700 ladera 10 basal ru 0.2 / Sitio P05"]["gle/morgenstern-price"]
P("The 700 m dump was also analyzed on a 10° foundation slope with a 30 m basal layer, using a nonlinear search optimized "
  "by simulated annealing and the Morgenstern–Price method (Table 5). Dry, the critical surface remained nearly circular "
  f"within the waste rock (factor of safety {f2(SL('H700 ladera 10 seco', 'Sitio P50'))} and "
  f"{f2(SL('H700 ladera 10 seco', 'Sitio P05'))} with the P50 and P05 envelopes). With a saturated basal layer and an excess "
  f"pore-pressure ratio of 0.2, it dropped to {f2(p50ru)} and {f2(p05ru)}. With an undrained basal layer whose strength is "
  "proportional to the vertical effective stress, Su = 0.17σ′v (the isotropic triaxial ratio of 0.28 reported by Valenzuela "
  "et al. (2008) referred to σ′v under K0 ≈ 0.4) and Su = 0.09σ′v (the mean liquefied strength ratio of Olson and Stark "
  f"(2002), extrapolated from much lower stresses), the factor of safety was {f2(S61['r 0.17 (fluencia)']['gle/morgenstern-price'])} "
  f"and {f2(S61['r 0.09 (licuada)']['gle/morgenstern-price'])}.")
P("Excess pore pressure from consolidation was estimated with one-dimensional consolidation under time-dependent loading "
  "(Olson 1977) for a constrained modulus of 50 MPa and a drained top. For the slow overall growth of the dump it is negligible "
  f"unless *k* ≤ 10⁻⁸ m/s, but a dumping front that adds 150 m in three months produces Δu/σv = "
  f"{f2(cr[('frente 150 m en 3 meses', 30.0, 1e-7)])} in a 30 m basal layer with *k* = 10⁻⁷ m/s and "
  f"{f2(cr[('frente 150 m en 3 meses', 100.0, 1e-7)])} in a 100 m layer. The rate of advance of the dumping front and the "
  "permeability of the crushed or degraded base are therefore first-order design variables, as in the liquefaction "
  "flowslides of coal-mine waste dumps (Dawson et al. 1998; Hungr et al. 2002).")

# ================================================================== DISCUSSION
Hd("Discussion")
Hd("What Leps-P Adds", 2)
P("Leps-P does not predict the central strength of an untested material better than Leps 2.0; its value lies in "
  "uncertainty that is calibrated and stress dependent, and in making site tests count. Because most of the predictive "
  "variance lies between materials and laboratories, it is not reduced by averaging along a failure surface within one "
  "material, but by testing that material at large scale over a stress range wide enough to update the curvature.")
Hd("Design Format", 2)
P("Following Eurocode 7 as interpreted by Prästings et al. (2019), the characteristic value for a global failure mechanism "
  "is a cautious estimate of the mean strength along the surface. In Leps-P it is the 5th percentile of the mean envelope "
  "(excluding within-material scatter), with the systematic components (fixed effects, laboratory, material, shape, and "
  "size) retained. Reliability is then checked with the probability of failure computed by sampling the envelope, with "
  "correlations between lithologies stated explicitly. Applying a global factor of safety to a P05 envelope counts the "
  "strength uncertainty twice; the target factor of safety should be calibrated to the consequence class and to the "
  "remaining sources of uncertainty, chiefly pore pressure and foundation conditions (Christian et al. 1994; Read and "
  "Stacey 2009).")
Hd("Limitations", 2)
P("The calibration database contains no tests above σ′n = 7.9 MPa, and its high-stress tests come from eight publications "
  "on basalt, gravel, argillite, diorite, and conglomerate; carbonate and argillaceous waste rock are not represented at "
  "high stress. Above 7.9 MPa the band is an extrapolation of the model. The class assignment for lithologies not listed by "
  "Cylwik et al. (2025) is a judgment. Specimens were scalped or of parallel gradation with *D*max ≤ 200 mm, and the "
  "relation with field material depends on gradation as well as size (Girumugisha et al. 2024). The within-material "
  "residual is laboratory scatter and does not represent spatial variability in the dump, which was not modeled. Leps-P "
  "describes drained strength; undrained and liquefied strengths of crushed waste rock at high stress were taken from "
  "lower-stress studies and must be measured. Leps-P is defined by its population parameters and by the procedure to "
  "estimate and evaluate them, so these gaps can be closed by re-estimation as data appear: drained large-scale tests at "
  "σ′3 of 5–10 MPa on carbonate and argillaceous waste rock, undrained tests at high pressure on crushed gradations, and "
  "tests of one material at two specimen sizes with parallel gradation and equal density would most reduce the "
  "uncertainty of high dumps.")

# ================================================================== CONCLUSIONS
Hd("Conclusions")
P("A three-level hierarchical extension of the Leps power envelope, Leps-P, was calibrated with the Leps 2.0 database and "
  "evaluated out of sample. The main conclusions are:")
for t in [
    f"Without site tests, the Leps-P 80% interval covered {pc(A_all['m']['cob80'])} of held-out tests and its accuracy equaled "
    "that of Leps 2.0 with constant dispersion; the intervals were conservative above 2.75 MPa.",
    f"With a few site tests at low stress and the proposed updating rule, the CRPS at high stress improved significantly, from "
    f"{f3(BB['sin']['crps'])} to {f3(BB['sitio']['crps'])}, while calibration was retained.",
    f"Laboratories and procedures explained {pc(frac_lab)} of the between-material variance of the reference angle; "
    "within-material scatter was a small part of the predictive variance.",
    f"Within materials of parallel gradation, the specimen-size effect agreed in sign with Weibull scaling but had about 60% of "
    f"its magnitude (κ = {f2(ES['kappa'])}); size enters design as an uncertainty of about 2° ± 1.5° from laboratory to field.",
    "For dumps up to 700 m on a competent drained foundation, the drained strength uncertainty gave negligible probability of "
    "failure; segregation of the weakest lithology, base saturation, and undrained response controlled stability.",
]:
    p = doc.add_paragraph(style="List Number"); runs(p, t)

# ================================================================== BACK MATTER
Hd("Data Availability Statement")
P("Some or all data, models, or code generated or used during the study are available in a repository online in "
  "accordance with funder data retention policies (the Leps-P code, calibrated parameters, and evaluation scripts: "
  "[[repository DOI to be assigned]]; calibration database: Arrieta 2025). Some or all data, models, or code generated or "
  "used during the study are proprietary or confidential in nature and may only be provided with restrictions (the test "
  "results of the skarn deposit, which belong to a third party and are published in anonymized and aggregated form with "
  "its consent [[to be confirmed]]).", indent=False)
Hd("Acknowledgments")
P("[[Acknowledgments and funding to be completed. The owner of the site test data is thanked for permission to publish them "
  "in anonymized form.]]", indent=False)

# ------------------------------------------------------------------ references (ASCE)
br(); Hd("References")
REFS = [
    "Alonso, E. E., M. Tapias, and J. Gili. 2012. \"Scale effects in rockfill behaviour.\" *Géotech. Lett.* 2 (3): 155–160. https://doi.org/10.1680/geolett.12.00025.",
    "Arrieta, M. 2025. \"Rockfill test database.\" Zenodo. Accessed October 6, 2026. https://doi.org/10.5281/zenodo.14665504.",
    "Barton, N., and B. Kjærnsli. 1981. \"Shear strength of rockfill.\" *J. Geotech. Eng. Div.* 107 (7): 873–891. https://doi.org/10.1061/AJGEB6.0001167.",
    "Bishop, A. W. 1955. \"The use of the slip circle in the stability analysis of slopes.\" *Géotechnique* 5 (1): 7–17. https://doi.org/10.1680/geot.1955.5.1.7.",
    "Charles, J. A., and K. S. Watts. 1980. \"The influence of confining pressure on the shear strength of compacted rockfill.\" *Géotechnique* 30 (4): 353–367. https://doi.org/10.1680/geot.1980.30.4.353.",
    "Ching, J., and K.-K. Phoon. 2019. \"Constructing site-specific multivariate probability distribution model using Bayesian machine learning.\" *J. Eng. Mech.* 145 (1): 04018126. https://doi.org/10.1061/(ASCE)EM.1943-7889.0001537.",
    "Ching, J., S. Wu, and K.-K. Phoon. 2021. \"Constructing quasi-site-specific multivariate probability distribution using hierarchical Bayesian model.\" *J. Eng. Mech.* 147 (10): 04021069. https://doi.org/10.1061/(ASCE)EM.1943-7889.0001964.",
    "Christian, J. T., C. C. Ladd, and G. B. Baecher. 1994. \"Reliability applied to slope stability analysis.\" *J. Geotech. Eng.* 120 (12): 2180–2207. https://doi.org/10.1061/(ASCE)0733-9410(1994)120:12(2180).",
    "Contreras, L.-F., and S. Linero-Molina. 2025. \"Hierarchical Bayesian inference of rockfill strength parameters from large-scale triaxial test data.\" *Aust. Geomech.* 60 (2): 91–106. https://doi.org/10.56295/AGJ6024.",
    "Contreras, L.-F., S. Linero-Molina, and J. Dixon. 2022. \"Bayesian approach to improve the confidence of the estimation of the shear strength of coarse mine waste using Barton's empirical criterion.\" *Aust. Geomech.* 57 (2): 163–174. https://doi.org/10.56295/AGJ5728.",
    "Cylwik, S. D., M. Arrieta, J. C. Cunning, and P. M. Hawley. 2025. \"Update to the Leps strength envelopes for rockfill based on 900 large-scale triaxial tests.\" *Int. J. Geomech.* 25 (12): 04025285. https://doi.org/10.1061/IJGNAI.GMENG-12050.",
    "Dawson, R. F., N. R. Morgenstern, and A. W. Stokes. 1998. \"Liquefaction flowslides in Rocky Mountain coal mine waste dumps.\" *Can. Geotech. J.* 35 (2): 328–343. https://doi.org/10.1139/t98-009.",
    "De Mello, V. F. B. 1977. \"Reflections on design decisions of practical significance to embankment dams.\" *Géotechnique* 27 (3): 281–355. https://doi.org/10.1680/geot.1977.27.3.281.",
    "Frossard, E., W. Hu, C. Dano, and P.-Y. Hicher. 2012. \"Rockfill shear strength evaluation: A rational method based on size effects.\" *Géotechnique* 62 (5): 415–427. https://doi.org/10.1680/geot.10.P.079.",
    "Girumugisha, G., C. Ovalle, and S. Ouellet. 2024. \"Grading scalping and sample size effects on critical shear strength of mine waste rock through laboratory and in-situ testing.\" *Int. J. Rock Mech. Min. Sci.* 183: 105915. https://doi.org/10.1016/j.ijrmms.2024.105915.",
    "Gneiting, T., and A. E. Raftery. 2007. \"Strictly proper scoring rules, prediction, and estimation.\" *J. Am. Stat. Assoc.* 102 (477): 359–378. https://doi.org/10.1198/016214506000001437.",
    "Hawley, M., and J. Cunning, eds. 2017. *Guidelines for mine waste dump and stockpile design.* Clayton, Australia: CSIRO Publishing.",
    "Hungr, O., R. F. Dawson, A. Kent, D. Campbell, and N. R. Morgenstern. 2002. \"Rapid flow slides of coal-mine waste in British Columbia, Canada.\" In *Catastrophic landslides: Effects, occurrence, and mechanisms*, edited by S. G. Evans and J. V. DeGraff, 191–208. Boulder, CO: Geological Society of America. https://doi.org/10.1130/REG15-p191.",
    "Indraratna, B., L. S. S. Wijewardena, and A. S. Balasubramaniam. 1993. \"Large-scale triaxial testing of greywacke rockfill.\" *Géotechnique* 43 (1): 37–51. https://doi.org/10.1680/geot.1993.43.1.37.",
    "Laird, N. M., and J. H. Ware. 1982. \"Random-effects models for longitudinal data.\" *Biometrics* 38 (4): 963–974. https://doi.org/10.2307/2529876.",
    "Leps, T. M. 1970. \"Review of shearing strength of rockfill.\" *J. Soil Mech. Found. Div.* 96 (4): 1159–1170. https://doi.org/10.1061/JSFEAQ.0001433.",
    "Linero, S., C. Palma, and R. Apablaza. 2007. \"Geotechnical characterisation of waste material in very high dumps with large scale triaxial testing.\" In *Proc., Int. Symp. on Rock Slope Stability in Open Pit Mining and Civil Engineering*, edited by Y. Potvin, 59–75. Perth, Australia: Australian Centre for Geomechanics. https://doi.org/10.36487/ACG_repo/708_2.",
    "Morgenstern, N. R., and V. E. Price. 1965. \"The analysis of the stability of general slip surfaces.\" *Géotechnique* 15 (1): 79–93. https://doi.org/10.1680/geot.1965.15.1.79.",
    "Olson, R. E. 1977. \"Consolidation under time dependent loading.\" *J. Geotech. Eng. Div.* 103 (1): 55–60. https://doi.org/10.1061/AJGEB6.0000369.",
    "Olson, S. M., and T. D. Stark. 2002. \"Liquefied strength ratio from liquefaction flow failure case histories.\" *Can. Geotech. J.* 39 (3): 629–647. https://doi.org/10.1139/t02-001.",
    "Ovalle, C., E. Frossard, C. Dano, W. Hu, S. Maiolino, and P.-Y. Hicher. 2014. \"The effect of size on the strength of coarse rock aggregates and large rockfill samples through experimental data.\" *Acta Mech.* 225 (8): 2199–2216. https://doi.org/10.1007/s00707-014-1127-z.",
    "Ovalle, C., S. Linero, C. Dano, E. Bard, P.-Y. Hicher, and R. Osses. 2020. \"Data compilation from large drained compression triaxial tests on coarse crushable rockfill materials.\" *J. Geotech. Geoenviron. Eng.* 146 (9): 06020013. https://doi.org/10.1061/(ASCE)GT.1943-5606.0002314.",
    "Prästings, A., J. Spross, and S. Larsson. 2019. \"Characteristic values of geotechnical parameters in Eurocode 7.\" *Proc. Inst. Civ. Eng. Geotech. Eng.* 172 (4): 301–311. https://doi.org/10.1680/jgeen.18.00057.",
    "Read, J., and P. Stacey, eds. 2009. *Guidelines for open pit slope design.* Collingwood, Australia: CSIRO Publishing.",
    "Rocscience. [[year]]. *Slide2.* Version 9.043. Toronto: Rocscience.",
    "Spencer, E. 1967. \"A method of analysis of the stability of embankments assuming parallel inter-slice forces.\" *Géotechnique* 17 (1): 11–26. https://doi.org/10.1680/geot.1967.17.1.11.",
    "Valenzuela, L., E. Bard, J. Campaña, and M. E. Anabalón. 2008. \"High waste rock dumps: Challenges and developments.\" In *Proc., 1st Int. Seminar on the Management of Rock Dumps, Stockpiles and Heap Leach Pads*, 65–78. Perth, Australia: Australian Centre for Geomechanics. https://doi.org/10.36487/ACG_repo/802_6.",
    "Vanmarcke, E. H. 1977. \"Probabilistic modeling of soil profiles.\" *J. Geotech. Eng. Div.* 103 (11): 1227–1246. https://doi.org/10.1061/AJGEB6.0000517.",
    "Ventini, R., S. Lirer, C. Mancuso, and A. Flora. 2021. \"Simplified procedure to identify the critical state line of crushable rockfills.\" *J. Geotech. Geoenviron. Eng.* 147 (12): 04021150. https://doi.org/10.1061/(ASCE)GT.1943-5606.0002668.",
    "Xiao, Y., H. Liu, Y. Chen, and J. Jiang. 2014a. \"Strength and deformation of rockfill material based on large-scale triaxial compression tests. I: Influences of density and pressure.\" *J. Geotech. Geoenviron. Eng.* 140 (12): 04014070. https://doi.org/10.1061/(ASCE)GT.1943-5606.0001176.",
    "Xiao, Y., H. Liu, Y. Chen, and J. Jiang. 2014b. \"Strength and deformation of rockfill material based on large-scale triaxial compression tests. II: Influence of particle breakage.\" *J. Geotech. Geoenviron. Eng.* 140 (12): 04014071. https://doi.org/10.1061/(ASCE)GT.1943-5606.0001177.",
]
for ref in REFS:
    p = doc.add_paragraph(); p.paragraph_format.left_indent = Inches(0.5); p.paragraph_format.first_line_indent = Inches(-0.5); runs(p, ref)

# ------------------------------------------------------------------ figure captions
br(); Hd("Figure Captions List")
CAP = [
    "Fig. 1. Distribution of effective normal stress on the failure plane in the calibration database, compared with the stresses in a 700 m waste dump.",
    "Fig. 2. Predictive distribution of the secant friction angle of a new material of moderate rock quality with e = 0.45 tested by a new laboratory: 80% interval, median, and 10th percentile for the quadratic and power forms. The shaded zone exceeds the largest normal stress in the database.",
    "Fig. 3. Out-of-sample calibration without site tests, leaving out each publication: (a) coverage of the 80% interval; and (b) fraction of tests below the 10th percentile, by range of normal stress. Dashed lines are the nominal values.",
    "Fig. 4. Mean continuous ranked probability score of ln τ for held-out tests at σ′n ≥ 2 MPa, without and with updating from site tests at σ′n ≤ 1.5 MPa. Thin lines are publications; the thick line is the mean of the 64 tests.",
    "Fig. 5. Within-material specimen-size coefficient β_D for materials tested at more than one maximum particle size (error bars: 95% confidence intervals). The shaded band is the 95% confidence interval of the mean for parallel gradation and equal density; the dotted line is Weibull scaling with κ = 0.41.",
    "Fig. 6. Field-scale envelopes of the waste rock of the skarn deposit by lithology (median and 10th percentile) and dump-average envelope. The shaded zone is beyond the stresses tested at the site.",
]
for c in CAP:
    P(c, indent=False)


# ------------------------------------------------------------------ tables (ASCE: after references)
def tabla(n, titulo, enc, filas, nota=None):
    if n == 1:
        br()
    else:
        doc.add_paragraph()
    p = doc.add_paragraph(); r = p.add_run(f"Table {n}. "); r.bold = True; p.add_run(titulo); p.paragraph_format.keep_with_next = True
    t = doc.add_table(rows=1 + len(filas), cols=len(enc))
    for j, h in enumerate(enc):
        c = t.rows[0].cells[j]; c.text = ""; runs(c.paragraphs[0], h)
    for i, f in enumerate(filas, 1):
        for j, v in enumerate(f):
            c = t.rows[i].cells[j]; c.text = ""; pp = c.paragraphs[0]; runs(pp, str(v))
            if not any(r_.text.strip() for r_ in pp.runs):          # solo ecuación: alinear a la izquierda
                M = "http://schemas.openxmlformats.org/officeDocument/2006/math"
                for om in pp._p.findall(f"{{{M}}}oMath"):
                    para = etree.SubElement(pp._p, f"{{{M}}}oMathPara"); ppr = etree.SubElement(para, f"{{{M}}}oMathParaPr")
                    jc = etree.SubElement(ppr, f"{{{M}}}jc"); jc.set(f"{{{M}}}val", "left"); pp._p.remove(om); para.append(om)
    for row in t.rows:
        for c in row.cells:
            for pp in c.paragraphs:
                pp.paragraph_format.line_spacing = 1.0
                for rr in pp.runs:
                    rr.font.size = Pt(10)
    tblPr = t._tbl.tblPr; bd = OxmlElement("w:tblBorders")
    for side in ("top", "bottom", "insideH"):
        e = OxmlElement(f"w:{side}"); e.set(qn("w:val"), "single"); e.set(qn("w:sz"), "4"); bd.append(e)
    tblPr.append(bd)
    if nota:
        p = doc.add_paragraph(); runs(p, "Note: " + nota)


hp = [HP(i) for i in range(8)]
tabla(1, "Parameters of Leps-P (quadratic form)",
      ["Parameter", "Estimate", "Standard error or 90% credible interval"],
      [["β_c, good rock quality", f3(b["good"]), f"{f3(SE['good'])} (φ′e=0 = {phi_e0['good']:.1f}°)"],
       ["β_c, moderate rock quality", f3(b["moderate"]), f"{f3(SE['moderate'])} (φ′e=0 = {phi_e0['moderate']:.1f}°)"],
       ["β_c, low rock quality", f3(b["low"]), f"{f3(SE['low'])} (φ′e=0 = {phi_e0['low']:.1f}°)"],
       ["β_e", neg(f3(b["e"])), f3(SE["e"])], ["β_x", f3(b["x"]), f3(SE["x"])], ["c2", f3(b["x2"]), f3(SE["x2"])],
       ["SD of θ, publication", f3(hp[0][0]), f"{f3(hp[0][1])}–{f3(hp[0][2])}"],
       ["SD of m, publication", f3(hp[1][0]), f"{f3(hp[1][1])}–{f3(hp[1][2])}"],
       ["Correlation of θ and m, publication", neg(f2(hp[2][0])), neg(f"{f2(hp[2][1])} to {f2(hp[2][2])}")],
       ["SD of θ, set", f3(hp[3][0]), f"{f3(hp[3][1])}–{f3(hp[3][2])}"],
       ["SD of m, set", f3(hp[4][0]), f"{f3(hp[4][1])}–{f3(hp[4][2])}"],
       ["Correlation of θ and m, set", neg(f2(hp[5][0])), neg(f"{f2(hp[5][1])} to {f2(hp[5][2])}")],
       ["σε at σ′n = σ0", f3(hp[6][0]), f"{f3(hp[6][1])}–{f3(hp[6][2])}"],
       ["a1", neg(f3(hp[7][0])), neg(f"{f3(hp[7][1])} to {f3(hp[7][2])}")]],
      f"{N['ensayos']} tests, {N['sets']} sets, {N['pub']} publications. Fixed effects: restricted maximum likelihood estimate and standard error; variance parameters: posterior median and 90% credible interval.")
row = lambda nm, m: [nm, m["m"]["n"] if "m" in m else m["sitio"]["n"]]
tabla(2, "Out-of-sample evaluation",
      ["Evaluation", "Tests", "80% coverage", "Below P10", "CRPS (Leps-P)", "CRPS (reference)"],
      [["Mode A, leave one publication out, all", A_all["m"]["n"], pc(A_all["m"]["cob80"]), pc(A_all["m"]["bajo10"]), f"{A_all['m']['crps']:.4f}", f"{A_all['m0']['crps']:.4f}"],
       ["Mode A, leave one publication out, σ′n > 2.75 MPa", A_hi["m"]["n"], pc(A_hi["m"]["cob80"]), pc(A_hi["m"]["bajo10"]), f"{A_hi['m']['crps']:.4f}", f"{A_hi['m0']['crps']:.4f}"],
       ["Mode A, leave one material type out, all", ALR["m"]["n"], pc(ALR["m"]["cob80"]), pc(ALR["m"]["bajo10"]), f"{ALR['m']['crps']:.4f}", f"{ALR['m0']['crps']:.4f}"],
       ["Mode B, without site tests", BB["sin"]["n"], pc(BB["sin"]["cob80"]), pc(BB["sin"]["bajo10"]), f"{BB['sin']['crps']:.4f}", "—"],
       ["Mode B, joint update of θ and m", BF["sitio"]["n"], pc(BF["sitio"]["cob80"]), pc(BF["sitio"]["bajo10"]), f"{BF['sitio']['crps']:.4f}", "—"],
       ["Mode B, updating rule", BB["sitio"]["n"], pc(BB["sitio"]["cob80"]), pc(BB["sitio"]["bajo10"]), f"{BB['sitio']['crps']:.4f}", "—"]],
      "Nominal values: 80% coverage and 10% below P10. Reference: Leps 2.0 (m = 0.9) with constant dispersion. Mode A rows for leave one material type out use the power form.")
EN_LIT = {KM: "Metamorphic carbonate", KH: "Hornfels", KI: "Intrusive", KS: "Sedimentary carbonate (untested)"}
filas = []
for k, nm in EN_LIT.items():
    r_ = LIT[k]; dg = DIAG.get(k)
    upd = ("θ and m" if dg["modo"].startswith("θ y") else "level only") if dg else "prior"
    pv = (f"{dg['p_conflicto']:.3f}" if dg["p_conflicto"] >= 0.001 else "<0.001") if dg else "—"
    filas.append([nm, f"{r_['phi1']:.1f}° / {r_['m']:.2f}", upd, pv] + [f"{r_['campo_P50'][sn_i[s]]:.1f} / {r_['campo_P10'][sn_i[s]]:.1f}" for s in (1, 3, 10, 15)])
for kb, nm in zip(KB, ["Dump average, model correlation", "Dump average, full correlation", "Weakest lithology only"]):
    filas.append([nm, "", "", ""] + [f"{BOT[kb]['P50'][sn_i[s]]:.1f} / {BOT[kb]['P05'][sn_i[s]]:.1f}" for s in (1, 3, 10, 15)])
tabla(3, "Field-scale secant friction angle (°) of the skarn waste rock by lithology and for the dump",
      ["Material", "φ′1 / m (lab)", "Update", "Conflict p", "1 MPa", "3 MPa", "10 MPa", "15 MPa"], filas,
      "Lithology rows give P50 / P10 of the mean envelope; dump rows give P50 / P05. Size shift from 178 to 1,000 mm. No site tests above σ′n ≈ 4.3 MPa.")
G = {150: "H150 fundacion horizontal", 400: "H400 fundacion horizontal", 700: "H700 fundacion horizontal"}
filas = []
for k, nm in [("Sitio P50", "Site waste rock, P50"), ("Sitio P05", "Site waste rock, P05"), ("Segregacion P05", "Weakest lithology, P05"),
              ("Generico P50", "Generic material, P50"), ("Generico P05", "Generic material, P05")]:
    filas.append([nm] + [f"{SL(G[h], k):.2f}" for h in (150, 400, 700)])
tabla(4, "Factor of safety of dumps on a competent level foundation (Morgenstern–Price method)",
      ["Envelope", "150 m", "400 m", "700 m"], filas,
      f"Slide2 9.043 with circular search; purpose-written Bishop code within 0.010. Monte Carlo for 700 m (400 samples of the dump-average envelope): median {f2(pf7['FS_P50'])}, P10 {f2(pf7['FS_P10'])}, minimum {f2(pf7['FS_min'])}. Generic material: moderate rock quality, e = 0.45, size shift from 150 to 1,000 mm.")
tabla(5, "Factor of safety of a 700 m dump on a 10° foundation slope with a 30 m basal layer (Morgenstern–Price method)",
      ["Basal layer condition", "P50 envelope", "P05 envelope"],
      [["Drained, dry", f2(SL("H700 ladera 10 seco", "Sitio P50")), f2(SL("H700 ladera 10 seco", "Sitio P05"))],
       ["Drained, saturated, excess pore-pressure ratio 0.2", f2(p50ru), f2(p05ru)],
       ["Undrained, Su = 0.17σ′v", f2(S61["r 0.17 (fluencia)"]["gle/morgenstern-price"]), "—"],
       ["Undrained, Su = 0.09σ′v (liquefied)", f2(S61["r 0.09 (licuada)"]["gle/morgenstern-price"]), "—"]],
      "Nonlinear search optimized by simulated annealing in Slide2 9.043. For undrained cases the search was restricted to global mechanisms; the critical surface entered at the limit of the entry range, so the values are upper bounds for that family.")
out = AQ / "LepsP_IJGM_manuscript.docx"; doc.save(out); print("written", out, "| equations:", NEQ[0])
