"""HiBER manuscript, round 6 (ASCE Int. J. Geomech., Technical Paper). Cleaned database (σ′3 reported, duplicates
removed), extended model (ln Dmax, decay rate by class, censoring at large strain, truncation of the database), validation
leaving out one laboratory at a time, a single design procedure, and foundation and seepage mechanisms in Slide2. All numbers are
read from result files; formatting in asce_docx.py (LaTeX with the official ascelike-new class)."""
import json, math
from pathlib import Path
import numpy as np
from scipy.stats import chi2 as _chi2, norm as _norm
import asce_docx as A
from asce_docx import doc, P, Hd, EQ, tabla

AQ = Path(__file__).parent; R = AQ.parent; AN = R / "analisis"; AA = R / "analisis_antamina"
J = lambda p: json.load(open(p, encoding="utf-8"))
PAR = J(R / "hiber" / "hiber_parameters.json"); FA = PAR["formas"]["acotada"]; N = PAR["n"]; ESCP = PAR["escala"]
M6 = J(AN / "lepsp_mcmc6.json"); PR = J(AN / "lepsp_perfil6.json"); CV = J(AN / "lepsp_cv6_metricas.json"); CC = J(AN / "lepsp_cv6_censura.json")
ES = J(AN / "lepsp_escala6.json"); E1 = J(AN / "lepsp_e1_estructura.json"); DG = J(AN / "lepsp_diag_alta6.json"); VAR = J(AN / "lepsp_varianza6.json")
DPL = J(AN / "lepsp_desplegada6.json"); TD = J(AN / "lepsp_tabla_diseno.json"); EST = J(AN / "lepsp_estabilidad6.json")
SIT = J(AA / "lepsp_sitio6.json"); SITQ = J(AA / "lepsp_sitio6_x2.json"); SITL = J(AA / "lepsp_sitio6_labindep.json"); SITB = J(AA / "lepsp_sitio6_bdindep.json")
SITM = J(AA / "lepsp_sitio6_muestra.json"); SITW = J(AA / "lepsp_sitio6_weibull.json"); CF = J(AA / "a7_criterio_falla.json")
A.SYM[:0] = [("τ_D", r"\tau_D"), ("t∞", r"t_\infty"), ("*a*0", r"a_0"), ("*a*1", r"a_1"), ("φ′∞", r"\phi'_\infty"), ("ζ0", r"\zeta_0"),
             ("u_η", r"u_\eta"), ("u_ζ", r"u_\zeta"), ("η_t", r"\eta_t"), ("ε_a", r"\varepsilon_a"), ("δ_c", r"\delta_c"), ("*D*r", r"D_r")]

# ------------------------------------------------------------------ numbers
CL = ["good", "moderate", "low"]; b = dict(zip(FA["nombres"], FA["beta"])); SE = dict(zip(FA["nombres"], np.sqrt(np.diag(FA["cov_beta"]))))
HP = FA["hiper"]; deg = lambda th: math.degrees(math.atan(math.exp(th))); phi1 = {c: deg(b[c]) for c in CL}
pc = lambda v: f"{100 * v:.0f}%"; pc1 = lambda v: f"{100 * v:.1f}%"; f2 = lambda v: f"{v:.2f}"; f3 = lambda v: f"{v:.3f}"; f4 = lambda v: f"{v:.4f}"
neg = lambda s: s.replace("-", "−"); sg = lambda v, dd=3: neg(f"{v:+.{dd}f}")
# profile likelihood of φ′∞ (observed-data likelihood with censoring and truncation)
pp = sorted(PR["perfil"], key=lambda r: r["phi"]); MLX = PR["ml_max"]; ph_ = np.array([r["phi"] for r in pp]); dm_ = np.array([r["ml"] - MLX for r in pp])
dML0 = -dm_[ph_ == 0.0][0]; p_LR = float(1 - _chi2.cdf(2 * dML0, 1))
def cruce(nivel):
    i0 = int(np.argmax(dm_)); xs = np.linspace(ph_.min(), ph_.max(), 3601); ys = np.interp(xs, ph_, dm_); ok = xs[ys >= -nivel]
    return ok.min(), ok.max()
ci_lo, ci_hi = cruce(1.92)
b3_lo, b3_hi = min(r['phi'] for r in pp if r['ml'] >= MLX - 3), max(r['phi'] for r in pp if r['ml'] >= MLX - 3)   # puntos de la grilla, como en lepsp6_envolventes_alto.py
cresta = [r["phi"] for r in pp if r["ml"] >= MLX - 6]
PHM, ZEM, PHT = M6["cresta"]["phi_media"], M6["cresta"]["zeta_media"], M6["cresta"]["phi_media_tan"]
z0 = {"good": FA["zeta"], "moderate": FA["zeta"] + b["dz_moderate"], "low": FA["zeta"] + b["dz_low"]}
sh = [math.exp(2 * s["psi"][0]) / (math.exp(2 * s["psi"][0]) + math.exp(2 * s["psi"][3])) for s in FA["muestras"]]
SHARE = (np.median(sh), np.percentile(sh, 5), np.percentile(sh, 95))
# structural study (Laplace and crossed fits; data without censoring)
MD = E1["modelos"]; DEC = E1["descomposicion"]; LO = E1["lopo"]["total"]
lap_opt = max(v["ll_laplace"] for v in E1["laplace_en_FO"]); lap_phi = [v["phi"] for v in E1["laplace_en_FO"] if v["ll_laplace"] == lap_opt][0]
fo_lap = {v["phi"]: v["fo_menos_laplace"] for v in E1["laplace_en_FO"]}
top_pub = max(E1["por_publicacion"]["M1-M3"]["por_pub"].values())
# validation by laboratory
A_, A2, Al, A3 = CV["A|todo"], CV["A|sn>=2"], CV["A|sn<0.5"], CV["A|sn>3"]
BN, BP, BJ, BS, BD, B90, BTR, BNn = (CV[f"B|{k}"] for k in ("nivel", "previa", "conjunta", "sitio", "descarte", "ingenuo_m090", "ingenuo_mtr", "n"))
SV = CV["S"]
holm_min = min((v["p_signflip_holm"], k) for k, v in A_.items() if "|" in k)
holm_pond = min((v["p_signflip_pond_holm"], k) for k, v in A2.items() if "|" in k)
C2, C3 = CC["sn>=2"], CC["sn>=3"]
cb = lambda o, q="P05": f"{pc1(o[q][0])}–{pc1(o[q][1])}" if abs(o[q][0] - o[q][1]) > 1e-9 else pc1(o[q][0])
# Mode B: bias by laboratory, and the rule "lower of updated and prior above the tested range"
import pandas as pd  # noqa: E402
BB = pd.read_csv(AN / "lepsp_cv6_B.csv"); BB["z"] = (BB.y - BB.mu) / BB.sd
bn_ = BB[BB.variante == "nivel"]; zl = bn_.groupby("lab").z.agg(["size", "mean"]).sort_values("size"); labmax = zl.index[-1]
mm = bn_.merge(BB[BB.variante == "previa"], on=["lab", "pub", "Set", "x", "y"], suffixes=("", "_p"))
q05n, q05p = mm.mu - 1.645 * mm.sd, mm.mu_p - 1.645 * mm.sd_p; q10n, q10p = mm.mu - 1.2816 * mm.sd, mm.mu_p - 1.2816 * mm.sd_p
REGLA = dict(b05=float((mm.y < np.minimum(q05n, q05p)).mean()), b10=float((mm.y < np.minimum(q10n, q10p)).mean()), mas_alto=float((q05n > q05p).mean()))
sin_lab = bn_[bn_.lab != labmax]
# size effect
EL, EP, EX = ES["laboratorios R ≥ 2"], ES["publicaciones R ≥ 2"], ES["interaccion laboratorios R ≥ 2"]
EG = ESCP["general"]
# variance decomposition
V1, V3, V10 = (VAR[f"low e=0.65 σ′n={s} D=100 mm"] for s in (1, 3, 10)); V3r = VAR["low e=0.65 σ′n=3 D=178 mm"]
vs = lambda V, k: 100 * V["comp"][k] / V["total"]
sdφ = lambda V: math.degrees(math.sqrt(V["total"]) * math.sin(math.radians(V["phi_mediana"])) * math.cos(math.radians(V["phi_mediana"])))
# site
SNs = np.array(SIT["sn"]); isn = lambda s: int(np.argmin(np.abs(SNs - s)))
ST = {s["lit"] + ("2" if s["lit"] in "BC" and any(t["lit"] == s["lit"] and t is not s and SIT["sets"].index(t) < SIT["sets"].index(s) for t in SIT["sets"]) else ""): s for s in SIT["sets"]}
flag = [s for s in SIT["sets"] if s["marcado"]]; usados = [s for s in SIT["sets"] if s["usado"]]
fb = SIT["escenarios"]["e=0.65|general"]["botadero"]; fbn = SIT["escenarios"]["e=0.65|ninguno"]["botadero"]; lbn = SIT["escenarios"]["e=lab|ninguno"]["botadero"]
weak = lambda dct, t: [v for k, v in dct.items() if k.startswith(t)][0]
bot = lambda S_, k="model", q="P05", s=1: S_["escenarios"]["e=0.65|general"]["botadero"][k][q][isn(s)]
# stability
D_ = lambda caso, esc, H, q: (EST["det"][f"{caso}|{esc}|{H}|{q}"] if f"{caso}|{esc}|{H}|{q}" in EST["det"]
                              else [v for k, v in EST["det"].items() if k.startswith(f"{caso}|{esc}") and k.endswith(f"|{H}|{q}")][0])
SNd = EST["sn_det"]["e065|model|700|P05"]; SN150 = EST["sn_det"]["e065|model|150|P05"]
MCm, MCe, SUS = EST["mc"]["modelo"], EST["mc"]["E"], EST["sustituto"]
def sci(v):                                                           # 1.1 × 10⁻³ en modo matemático (LaTeX y OMML)
    e = int(np.floor(np.log10(v))); return f"${v / 10 ** e:.1f}\\times 10^{{{e}}}$"
cpi = lambda m: f"{100 * m['pf_ic95'][0]:.1f}–{100 * m['pf_ic95'][1]:.1f}%"
AL, SNA = EST["alto"], EST["sn_alto"]
al = lambda t, H, env: AL[f"{t}|{H}|{env}"]
MECS = [("comp", 700, "Competent level foundation"), ("debil25", 400, "Weak layer, 25°"), ("debil25", 700, "Weak layer, 25°"),
        ("debil30", 700, "Weak layer, 30°"), ("inc10", 400, "Foundation inclined 10°"), ("inc10", 700, "Foundation inclined 10°"),
        ("inc20", 700, "Foundation inclined 20°"), ("agua100", 700, "Basal water table, 100 m")]
MECS = [m for m in MECS if f"{m[0]}|{m[1]}|B P05" in AL]
snA = lambda t, H: SNA.get(f"{t}|{H}|B P05", {}).get("max", float("nan"))
SECOS = [m for m in MECS if m[0] != "agua100"]
SNX = max(snA(t, H) for t, H, _ in SECOS)
DMEC = max(al("comp", 700, "B P05") - al(t, H, "B P05") for t, H, _ in SECOS if H == 700)
DFORM = max(abs(al(t, H, "B P05") - al(t, H, "Q P05")) for t, H, _ in SECOS)
DPHI = max(abs(al(t, H, "Fhi P05") - al(t, H, "Flo P05")) for t, H, _ in SECOS)
assert all(al(t, H, "B P05") < al(t, H, "L2 P50") < al(t, H, "B P50") for t, H, _ in SECOS)   # texto: Leps 2.0 entre P05 y P50
BLQ = J(AN / "lepsp_bloques6.json")                                # lote 72: capas débiles con SA y búsqueda por bloques
WK = [("debil20", "Weak layer, 20°"), ("debil15", "Weak layer, 15°"), ("incdeb", "Weak layer 20°, inclined 10°")]
def bq(t, env, que="fs"):
    o = min((BLQ[f"{t}|{s}|{env}"] for s in ("SA", "bloques") if f"{t}|{s}|{env}" in BLQ), key=lambda v: v["fs"]); return o[que]
FSW = (min(bq(t, "B P05") for t, _ in WK), max(bq(t, "B P05") for t, _ in WK)); FRW = (min(bq(t, "B P05", "frac_capa") for t, _ in WK), max(bq(t, "B P05", "frac_capa") for t, _ in WK))
SNW = max(bq(t, e, "sn_max_desmonte") for t, _ in WK for e in ("B P05", "Q P05"))
DFORMT = max(DFORM, max(abs(bq(t, "B P05") - bq(t, "Q P05")) for t, _ in WK))
assert all(bq(t, "B P05") < bq(t, "L2 P50") < bq(t, "B P50") for t, _ in WK)
DOMINIO = ("The validity domain is drained, global mechanisms with σ′n ≤ 8 MPa and, above 3 MPa, *e* ≤ 0.55, the range of the "
           "calibration tests")

# ================================================================== TITLE, ABSTRACT
A.titulo("HiBER: Hierarchical Bounded Strength Envelopes for Rockfill and Mine Waste Rock")
A.autores("Wilson A. Anticona", "[[ASCE grade, affiliation, and corresponding author e-mail to be completed; add any coauthors.]]")
Hd("Abstract")
P("Reliability-based design of high waste dumps needs the drained strength of rockfill and mine waste rock as a "
  "distribution that combines published experience with site tests. HiBER (hierarchical bounded envelopes for rockfill), an extension of the Leps charts, is a three-level hierarchical model "
  f"of the secant friction angle, calibrated on {N['ensayos']} large-scale triaxial tests from {N['labs']} laboratories, with rock "
  "quality, void ratio, and particle size as covariates, censoring of tests stopped at large strain, and truncation of the "
  "database. The dilatant part of strength decays with stress toward an asymptote "
  "of about 28 degrees, which bounds extrapolation; the likelihood strongly preferred this form to a power law but only "
  "weakly to an equally flexible quadratic form. Leaving out one laboratory at a time, the bounded, quadratic, power, and "
  "Leps 2.0 envelopes predicted new materials with indistinguishable accuracy; the hierarchical intervals had nominal "
  "coverage at low stress, and at high stress the bounded median was nearly unbiased but its lower tail slightly "
  "optimistic. Updating with site tests at low stress was optimistic above the tested stress unless the prior governed "
  "there. At field scale, the between-laboratory heterogeneity of the particle-size effect contributed about three "
  "quarters of the variance of untested waste rock. In 700 m dumps, also on weak foundation layers, the waste rock along "
  f"critical surfaces mobilized at most about {SNW:.0f} MPa, where the envelope forms agreed within {DFORMT:.2f} in factor of "
  "safety: weak layers and the cautious strength, not the envelope form, controlled stability.", indent=False)
Hd("Practical Applications")
P("Designers of high waste dumps often have few large-scale shear tests and rely on published charts of rockfill strength. "
  "HiBER gives a best estimate and a cautious design value of strength for any rock quality, density, and particle size, "
  "up to 8 MPa on the failure plane. Site tests sharpen the estimate within their range of pressure, with a warning when they "
  "disagree with published experience. For untested waste rock most of the uncertainty comes "
  "from the effect of particle size, so large-scale tests at two particle sizes are the most valuable investigation. Even "
  "for 700 m dumps on weak foundation layers the waste rock along failure surfaces stayed below about 3 MPa, so the "
  "strength of the weak layer and the cautious strength of the waste rock, not the shape of the envelope, govern design.", indent=False)
P("*Author keywords:* Rockfill; Mine waste rock; Shear strength; Nonlinear failure envelope; Dilatancy; Hierarchical model; "
  "Reliability-based design; High waste dumps.", indent=False)

# ================================================================== INTRODUCTION
Hd("Introduction")
P("Leps (1970) compiled 109 large-scale triaxial tests and proposed nonlinear envelopes for rockfill that have been used "
  "whenever site-specific tests were unavailable. Cylwik et al. (2025) updated them with a public database of 938 tests "
  "(Arrieta 2025), adopting the power criterion of De Mello (1977) and Charles and Watts (1980) with the secant friction "
  "angle at σ′n = 10p_a related to rock quality and void ratio (Leps 2.0).")
P("Reliability-based design (Read and Stacey 2009; Hawley and Cunning 2017) requires a strength distribution and a rule to "
  "combine published experience with site tests. Waste dumps now reach 500–700 m (Valenzuela et al. 2008; Bard et al. "
  "2011), and at high normal stress waste rock crushes and loses "
  "dilatancy (Marsal 1973; Hardin 1985; Indraratna et al. 1993; Linero et al. 2007; Xiao et al. 2014a, "
  "2014b; Ovalle et al. 2020; Ventini et al. 2021). Beyond the data a power law keeps curving downward, whereas the "
  "contribution of dilatancy is suppressed by confinement (Bolton 1986; Jefferies and Been 2016).")
P("Hierarchical models that borrow strength from generic databases exist for soil and rock properties (Ching and Phoon 2019, "
  "2020; Bozorgzadeh et al. 2019; Ching et al. 2021), and a hierarchical Bayesian analysis of the Barton and Kjærnsli (1981) "
  "parameters has been applied to the rockfill of one project (Contreras et al. 2022; Contreras and Linero-Molina 2025). "
  "HiBER (hierarchical bounded envelopes for rockfill) extends the Leps charts: it pools 23 laboratories, bounds extrapolation with an asymptote, accounts for tests stopped before failure, and is "
  "evaluated out of sample by laboratory; it also gives a design procedure with a prior–data conflict check, a "
  "decomposition of the uncertainty of untested waste rock, and the mechanisms for which the envelope form matters.")

# ================================================================== MODEL
Hd("Database and Model Formulation")
Hd("Calibration Database", 2)
P(f"The public database (Arrieta 2025) was filtered to tests with reported σ′3 ≥ 60 kPa and initial void ratio and at least "
  "two tests per set; points digitized from published curves without a reported confining stress and tests duplicated "
  f"between publications were removed. This gave {N['ensayos']} tests on {N['sets']} sets from {N['pub']} publications and "
  f"{N['labs']} laboratories (publications of one testing program form one laboratory; Fig. S1). A set is a material with a "
  "given gradation, density, and rock type tested in one program; failure is the maximum deviator stress, and rock quality "
  "classes follow Table 5 of Cylwik et al. (2025). Tests with σ′n > 3 MPa (90) come from five laboratories, mostly from "
  "1963–1983 (e.g., Marachi et al. 1972; Marsal 1973), and sets with φ′1 < 31° were excluded by Cylwik et al. (2025), which "
  f"truncates the population. In {N['censurados']} tests the maximum deviator was reached at an axial strain ε_a ≥ 19%, near "
  "the stroke limit of large cells, while the specimens were still compressing, so it is a lower bound of strength. The "
  f"volumetric strain at the maximum deviator was compressive, with a median of {DG['bandas'][-1]['evol_mediana']:.1f}% and a "
  f"median breakage index of {DG['bandas'][-1]['bg_mediana']:.0f}% above 3 MPa (Fig. S2), and above 1.5 MPa the residuals of "
  f"the model increased with it (Spearman ρ = {DG['res_vs_evol_alta']['spearman']:.2f}). The void ratio ranges from 0.15 to "
  "0.89, and most tests above 3 MPa have *e* ≤ 0.55.")
Hd("Envelope", 2)
P("The Leps 2.0 criterion is the power law")
EQ(r"\tau=\tan\phi'_1\,\sigma_0^{1-m}\,\sigma_n'^{\,m}")
P("where σ0 = 10p_a, p_a = 0.1013 MPa, φ′1 is the secant friction angle at σ′n = σ0, and *m* is a constant exponent; the secant "
  "friction angle is φ′s = arctan(τ/σ′n). In granular materials the excess of strength over the critical state is governed by "
  "dilatancy, which is suppressed by confinement (Bolton 1986; Jefferies and Been 2016, p. 43); particle crushing reinforces "
  "this trend (Hardin 1985; Einav 2007). A minimal form with this property is", indent=False)
EQ(r"\tan\phi'_s=t_\infty+\left(\tan\phi'_1-t_\infty\right)\exp(-\zeta x),\qquad x=\ln(\sigma'_n/\sigma_0),\quad t_\infty=\tan\phi'_\infty")
P("in which the dilatant part decays at rate ζ toward the asymptotic angle φ′∞. For φ′∞ = 0 it reduces to a power law with "
  "*m* = 1 − ζ. Because many specimens at high stress were still compressing at the maximum deviator, φ′∞ is a population "
  "decay parameter of the maximum-deviator envelope and not a critical-state angle (Been and Jefferies 1985).", indent=False)
Hd("Hierarchical Model", 2)
P("With *y* = ln(τ/σ0), the strength of test *i* of set *j* of laboratory *k* is")
EQ(r"y_{ijk}=x_{ijk}+\ln\!\left[t_\infty+\left(\exp\eta_{jk}-t_\infty\right)\exp\!\left(-\zeta_{jk}x_{ijk}\right)\right]+\varepsilon_{ijk}")
EQ(r"\eta_{jk}=\beta_{c}+\beta_e e_{jk}+\kappa\ln\!\left(D_{max,jk}/D_r\right)+u_{\eta,jk},\quad \zeta_{jk}=\zeta_0+\delta_{c}+u_{\zeta,jk},\quad \mathbf{u}_{jk}=\mathbf{u}^{(p)}_k+\mathbf{u}^{(s)}_{jk}")
EQ(r"\mathbf{u}^{(p)}\sim N(\mathbf{0},\mathbf{G}_p),\quad \mathbf{u}^{(s)}\sim N(\mathbf{0},\mathbf{G}_s),\quad \ln\sigma_\varepsilon(x)=a_0+a_1x")
P("where η = ln tan φ′1 is the dilatant level of the material, β_c the coefficient of its rock quality class *c*, β_e the "
  "effect of the initial void ratio *e*, κ the between-set effect of the maximum particle size *D*max relative to *D*r = 100 mm, "
  "ζ0 the decay rate of the good class and δ_c the offset of class *c*, $\\mathbf{u}$ = (u_η, u_ζ) the laboratory and set "
  "random effects with covariance matrices G_p and G_s, and ε the test-to-test deviation with standard deviation σε; "
  "*D*max, missing for 49 sets, was imputed from the gradation or the median. The common asymptote makes "
  "between-material differences shrink with stress; the between-set standard deviation of the mean residual of ln τ fell "
  f"from {DG['sd_entre_sets']['0-1.0']['sd']:.3f} below 1 MPa to {DG['sd_entre_sets']['3.0-99']['sd']:.3f} above 3 MPa. The "
  "laboratory effect (equipment, procedure, era, and material selection) is treated as uncertainty of strength. A quadratic "
  "log–log form, *y* = θ + *m*·*x* + *c*₂*x*², and a power form (*c*₂ = 0), with the same covariates and random effects on θ "
  "and *m*, were fitted for comparison.", indent=False)
P("A test with ε_a ≥ 19% contributes to the likelihood the probability that its strength exceeds the measured value, "
  "conditional on the uncensored tests of its block, and each set is divided by the probability that its level exceeds "
  "η_t = ln tan 31°, the truncation of the database. The asymptote is weakly identified, so its profile likelihood was "
  "computed from 0° to 36° (Fig. S3), and predictions average over the values within 6 log-likelihood units of the maximum "
  "with weights proportional to the likelihood (flat prior in degrees; uniform in tan φ′∞ as a sensitivity).")
Hd("Predictive Distribution and Design Values", 2)
P("For a new material of class *c*, void ratio *e*, and size *D*max tested by a new laboratory, *y* is approximately normal "
  "with mean *f*(*x*) given by Eq. (3) with $\\mathbf{u}$ = 0 and variance")
EQ(r"\mathrm{Var}[y]=\mathbf{z}^T(\mathbf{G}_p+\mathbf{G}_s)\mathbf{z}+\mathbf{j}^T\mathbf{C}_\beta\mathbf{j}+\sigma_\varepsilon^2(x)")
P(r"where $\mathbf{z}$ and $\mathbf{j}$ are the gradients of *f* with respect to (η, ζ) and to the fixed effects and C_β is the "
  "covariance of the fixed effects, evaluated at zero random effects (first-order method; Lindstrom and Bates 1990). The "
  "first two terms describe the uncertainty of the mean envelope of the material, which does not average out along a failure "
  "surface within that material (Christian et al. 1994); the last describes test-to-test scatter, which does (Vanmarcke "
  "1977). Design values are percentiles of the mean envelope; Fig. 1 shows the median and 5th percentile for untested "
  "materials at a specimen size of 100 mm.", indent=False)
Hd("Updating with Site Tests", 2)
P("Site triaxial tests are reduced with the maximum-deviator criterion of the database and converted to (σ′n, τ) with Eqs. "
  "(13), (14), and (16) of Cylwik et al. (2025). Consistency with the prior is checked with the prior predictive Mahalanobis distance")
EQ(r"D^2=\mathbf{r}^T\mathbf{V}^{-1}\mathbf{r}\sim\chi^2_n,\qquad \mathbf{V}=\mathbf{Z}(\mathbf{G}_p+\mathbf{G}_s)\mathbf{Z}^T+\mathbf{J}\mathbf{C}_\beta\mathbf{J}^T+\mathbf{S}")
P(r"where $\mathbf{r}$ holds the residuals *r*i of the *n* site tests from the prior mean, $\mathbf{Z}$ and $\mathbf{J}$ have rows "
  r"$\mathbf{z}_i^T$ and $\mathbf{j}_i^T$, and $\mathbf{S}=\mathrm{diag}\,\sigma_\varepsilon^2(x_i)$. When several sets of a site "
  "are checked, their *p*-values are adjusted with the Holm (1979) procedure. The update treats the residuals as measurements "
  r"of the level of the envelope at the centroid *x̄* of the tests. With $\mathbf{v}$ the random effects of the material and "
  r"the deviation of the fixed effects, $\mathbf{P}$ their prior covariance, $\mathbf{a}$ the gradient at *x̄*, and g_0 = "
  r"$\mathbf{a}^T\mathbf{P}\mathbf{a}$, the level q_0 = $\mathbf{a}^T\mathbf{v}$ has the posterior", indent=False)
EQ(r"\hat q_0=\frac{\sum_i r_i/\sigma_{\varepsilon,i}^2}{1/g_0+\sum_i 1/\sigma_{\varepsilon,i}^2},\qquad \mathrm{Var}(q_0)=\left(\frac{1}{g_0}+\sum_i\frac{1}{\sigma_{\varepsilon,i}^2}\right)^{-1}")
P(r"and $\mathbf{v}$ is shifted by $\mathbf{P}\,\mathbf{a}\,\hat q_0/g_0$. Eq. (8) is a cut update that can be applied in a "
  "spreadsheet with the published matrices (worked example in the supplemental materials). A tested sample does not "
  "represent a rock type, so a rock type is represented by a new set from the same laboratory: the updated laboratory "
  "effect is kept and the set effect is drawn again from G_s.", indent=False)
Hd("Placement Density and Specimen Size", 2)
P("A change of void ratio Δ*e* from the specimens to the placed material enters through η, so its effect fades with stress; "
  "because β_e was estimated between sets, applying it to a change of state of one material is an assumption. The "
  "between-set coefficient κ mixes size with gradation and source, so the change of size from the specimens to the field "
  "enters as a separate shift of level")
EQ(r"\Delta y=\beta_D\ln\left(D_f/D_l\right)")
P("where *D*f and *D*l are the maximum particle sizes in the field and in the laboratory and β_D is the within-material size "
  "coefficient estimated below; Weibull scaling of homothetic gradations predicts β_D < 0 (Frossard et al. 2012; Ovalle et al. "
  "2014; Alonso et al. 2012), and the trend depends on the scaling technique (Ovalle and Dano 2020; Girumugisha et al. 2026).", indent=False)

# ================================================================== ESTIMATION & EVALUATION
Hd("Estimation and Out-of-Sample Evaluation")
P("Fixed effects were estimated by Gauss–Newton iteration on the linearized mean, with restricted maximum likelihood "
  "for the variance parameters and expectation–maximization steps for the censored tests. Variance parameters were sampled "
  "with an adaptive Metropolis algorithm under weakly informative priors (half-normal with scale 0.25 on standard "
  "deviations), with four chains, conditionally on the fixed effects (an empirical Bayes scheme); convergence was checked "
  "as in Vehtari et al. (2021). The bounded and quadratic means were also fitted with each other's covariance structure, "
  "and the bounded model with the Laplace approximation (Pinheiro and Bates 2000), on the uncensored likelihood.")
P("Each laboratory was left out in turn (23 folds), with (φ′∞, ζ0) selected on the training data on a grid (18–32°, "
  "0.20–0.50). In Mode A every held-out test was predicted with the bounded, quadratic, and power forms and with the Leps 2.0 "
  "envelope (*m* = 0.9, constants fitted to the whole database, which favors it) with a constant or a hierarchical "
  "dispersion; censored tests were scored with bounds. In Mode B each held-out set with at least two tests at σ′n ≤ 1.5 MPa "
  "and one at σ′n ≥ 2 MPa was updated with the former to predict the latter (Table S1). Scores were the 80% coverage, the "
  "fractions below the 5th and 10th percentiles, and the continuous ranked probability score (CRPS) of ln τ (Gneiting and "
  "Raftery 2007); laboratory means were compared with exact sign-flip tests, unweighted and weighted, with Holm (1979) "
  f"adjustment. The folds used plug-in predictive distributions, which differed from those of the implementation by at most "
  f"{DPL['dmed_abs_max']:.3f} in median ln τ and {100 * (DPL['ratio_sd_max'] - 1):.0f}% in standard deviation.")

# ================================================================== RESULTS
Hd("Results")
Hd("Parameters and Evidence for Stress-Decaying Curvature", 2)
P(f"Table 1 lists the parameters. The potential scale reduction factor was at most {max(M6['acotada']['rhat']):.3f} and the "
  f"effective sample sizes at least {min(M6['acotada']['ess_bulk']):.0f}; the "
  f"between-laboratory standard deviation of η was {M6['previa_0.1']['hiper'][0][0]:.3f}–{M6['previa_0.5']['hiper'][0][0]:.3f} for prior "
  f"scales of 0.1–0.5. Laboratory effects account for {pc(SHARE[0])} (90% credible interval "
  f"{pc(SHARE[1])}–{pc(SHARE[2])}) of the between-material variance of η at σ0. The size coefficient κ = {f3(b['lnD'])} "
  f"(standard error {f3(SE['lnD'])}) is positive: between sets, coarser materials were slightly stronger, a mixture of size, "
  f"gradation, and source. The decay rate was {z0['good']:.2f}, {z0['moderate']:.2f}, and {z0['low']:.2f} for good, moderate, and "
  "low rock quality, so weaker rock loses less of its dilatant strength per unit of log stress.")
P(f"The profile likelihood peaked at φ′∞ = {ph_[np.argmax(dm_)]:.0f}° (likelihood-ratio 95% interval {ci_lo:.0f}–{ci_hi:.0f}°; "
  f"Fig. S3); the weighted mean over the ridge was {PHM:.1f}° ({PHT:.1f}° with a prior uniform in tan φ′∞) with ζ0 = {ZEM:.2f}. "
  f"The power form (φ′∞ = 0) was {dML0:.0f} units lower, but under the first-order approximation, which on the uncensored "
  f"data overstated the likelihood of the bounded model by {fo_lap[22.0]:.1f}–{fo_lap[25.0]:.1f} units near the maximum and "
  f"by {fo_lap[28.0]:.0f} at 28° (Table S3); under the Laplace approximation the maximum moved to about {lap_phi:.0f}°, within "
  "the ridge. With the covariance structures crossed, the bounded mean exceeded the plain quadratic mean by "
  f"{DEC['media_con_cov_aditiva_M2_M3']:.0f} units but a quadratic with class-specific curvature and the same number of "
  f"parameters by only {DEC['media_clase_cov_adit_M2_M3b']:.1f}, and one publication contributed {top_pub:.0f} of the "
  f"{DEC['total_M1_M3']:.0f} units separating the bounded and plain quadratic models. Out of sample by publication, the joint "
  f"log score of the bounded model was {LO['M1'] - LO['M4b']:.0f} units higher than that of the best quadratic. The evidence "
  "for the bounded form is therefore moderate; its justification is a bounded extrapolation consistent with the suppression "
  "of dilatancy rather than a better fit.")
Hd("Mode A: No Site Tests", 2)
P(f"Across all {A_['n']} uncensored held-out tests (Table 2, Fig. 2a), the CRPS ranged from {f4(A_['leps2_ref']['crps'])} "
  f"(Leps 2.0, constant dispersion) to {f4(A_['leps2_jer']['crps'])} (Leps 2.0, hierarchical dispersion), with "
  f"{f4(A_['acotada']['crps'])} for the bounded form, and no difference was significant after adjustment. Below 0.5 MPa the "
  f"constant-dispersion interval covered {pc(Al['leps2_ref']['cob80'])} of tests, with the median biased low (mean "
  f"standardized residual {sg(Al['leps2_ref']['z_medio'], 2)}), whereas the bounded form covered {pc(Al['acotada']['cob80'])}.")
P(f"At σ′n ≥ 2 MPa ({A2['n']} uncensored tests, {A2['n_lab']} laboratories) the bounded form was nearly unbiased (mean "
  f"standardized residual {sg(A2['acotada']['z_medio'], 2)}, against {sg(A2['cuadratica']['z_medio'], 2)} for the quadratic form and "
  f"{sg(A2['leps2_ref']['z_medio'], 2)} for Leps 2.0), but its intervals were too narrow (standard deviation of standardized "
  f"residuals {f2(A2['acotada']['sd_z'])}) and its CRPS higher. Including the {C2['censurados']} censored tests through their "
  f"bounds, {cb(C2['acotada'])} of the tests fell below the bounded 5th percentile, against {cb(C2['cuadratica'])} for the "
  f"quadratic form (Table S4); with tests weighted, the lower quantile losses favored the hierarchical Leps 2.0 envelope "
  f"(Holm-adjusted *p* = {holm_pond[0]:.2f}). The lower tail of the bounded form is thus slightly optimistic above 2 MPa. "
  f"At the set level, {pc1(SV['acotada']['bajo05'])} of {SV['acotada']['n_sets']} held-out set means fell below the 5th "
  f"percentile of the mean envelope. The conflict check gave *p* < 0.05 for {pc1(SV['conflicto']['frac_p05'])} of the sets, more often than its nominal 5%.")
Hd("Mode B: Site Tests at Low Stress", 2)
P(f"Mode B comprised {BNn['ensayos']} tests on {BNn['sets']} sets from {BNn['labs']} laboratories (Table 2, Fig. 2b). With the level "
  f"update of each set, {pc(BN['cob80'])} of the tests fell within the 80% interval, but {pc(BN['bajo05'])} fell below the 5th "
  f"percentile and the median was biased high (mean standardized residual {sg(BN['z_medio'], 2)}). The bias came mostly from "
  f"one laboratory ({int(zl.loc[labmax, 'size'])} tests, mean standardized residual {sg(zl.loc[labmax, 'mean'], 2)}), whose materials "
  f"curved more than the population between the update range and 2 MPa; without it, {pc(float((sin_lab.z < -1.645).mean()))} of "
  f"the remaining tests fell below the 5th percentile, against {pc(BP['bajo05'])} with the prior alone. Using the lower of the "
  f"updated and prior percentiles, as in the design procedure, gave {pc(REGLA['b05'])} below the 5th and {pc(REGLA['b10'])} below "
  "the 10th percentile. No difference between procedures was significant after adjustment (Table S1).")
Hd("Specimen Size", 2)
P(f"Sixteen materials from {EL['k']} laboratories were tested at maximum particle sizes differing by a factor of "
  f"{ES['rango_razon_tamanos'][0]:.1f}–{ES['rango_razon_tamanos'][1]:.0f}. With set intercepts adjusted for void ratio and "
  "materials combined within laboratories, the random-effects mean of β_D was "
  f"{sg(EL['b'][0])} (Knapp–Hartung 95% CI {sg(EL['ci'][0][0])} to {sg(EL['ci'][0][1])}; Knapp and Hartung 2003) with a "
  f"between-laboratory standard deviation τ_D = {f3(EL['tau'])} (Q-profile 95% CI {f3(EL['tau_ci'][0])}–{f3(EL['tau_ci'][1])}; "
  f"Viechtbauer 2007) and a 95% prediction interval for a new laboratory of {sg(EL['prediccion95'][0], 2)} to "
  f"{sg(EL['prediccion95'][1], 2)} (Higgins et al. 2009; Fig. S4); grouped by publication the mean was {sg(EP['b'][0])} "
  f"({sg(EP['ci'][0][0])} to {sg(EP['ci'][0][1])}), and no interaction with stress was detected. The database mixes scalped and "
  "parallel gradations and rounded and angular particles, with opposite reported trends (Varadarajan et al. 2003; Ovalle and "
  "Dano 2020). For design, HiBER uses a zero mean with τ_D and the standard error of the mean as uncertainty (effective "
  f"standard deviation {float(np.hypot(EG['se_hk'], EG['tau'])):.3f} per unit ln(*D*f/*D*l)); β_D = {sg(ESCP['weibull']['b'], 2)} "
  "(Weibull) is a sensitivity.")
Hd("Sources of Uncertainty at Field Scale", 2)
P(f"For an untested material of low rock quality placed at *e* = 0.65 and scaled from 100 mm to 1 m particles, the standard "
  f"deviation of the mean-envelope ln τ at 3 MPa corresponds to about {sdφ(V3):.1f}° in φ′s. Specimen size contributed "
  f"{vs(V1, 'escala_campo'):.0f}%, {vs(V3, 'escala_campo'):.0f}%, and {vs(V10, 'escala_campo'):.0f}% of the variance at 1, 3, and "
  f"10 MPa ({vs(V3r, 'escala_campo'):.0f}% at 3 MPa from 178 mm specimens), between-set variability {vs(V3, 'material'):.0f}%, "
  f"laboratory {vs(V3, 'publicacion'):.0f}%, and the fixed effects and the ridge of (φ′∞, ζ0) {vs(V3, 'efectos_fijos') + vs(V3, 'cresta'):.0f}% "
  "(Fig. S5). Because κ now carries the between-set size effect, the between-set variance no longer absorbs it and the size "
  "term is not counted twice. The size shift is a level term, so at field scale it does not decrease with stress.")
Hd("Design Values", 2)
P("Table 3 gives the median and 5th percentile of the mean envelope of untested materials at a specimen size of 100 mm and "
  "the 5th percentile at a field size of 1 m, by rock quality and void ratio. " + DOMINIO + "; the values do not represent "
  "degradable, argillaceous, or fines-rich waste, and because the database is truncated at φ′1 = 31°, 5th percentiles below "
  "about 33° rest on the model of the tail.")

# ================================================================== APPLICATION
Hd("Application: Waste Rock from a Large Open-Pit Mine")
Hd("Site Data and Conflict Check", 2)
pA = [s for s in SIT["sets"] if s["lit"] == "A"][0]
mB = [CF[c][k]["m_libre"] for c in CF for k in CF[c] if "HF" in k]
P(f"The waste rock of a large open-pit mine comprises five rock types, A to E. Drained triaxial tests on large specimens of "
  f"scalped gradation by one laboratory were available for A, B, and C ({len(SIT['sets'])} sets of three to five tests); D and E "
  "were untested, and E is prone to degradation. Rock quality was taken as low for A, C, D, and E and moderate for B; "
  "illustrative mass fractions of 35%, 25%, 20%, 10%, and 10% were used. For rock type A the conflict check gave "
  f"*p* = {TD['clase_A']['baja']:.2f} with the low class and {TD['clase_A']['buena']:.3f} with the good class; the class is assigned "
  "from the rock description and only checked with the tests. After Holm adjustment over the five sets, the check flagged "
  f"both sets of B (adjusted *p* ≤ {max(s['p_holm'] for s in flag):.4f}; Fig. 3a), which were stronger than the prior (mean "
  f"residuals {sg(min(s['residuo_medio'] for s in flag), 2)} and {sg(max(s['residuo_medio'] for s in flag), 2)} in ln τ); their "
  "secant angle increased with stress, also with the deviator taken at 10% or 15% strain. Being stronger, they were excluded; "
  f"the remaining {len(usados)} sets were updated jointly with a common laboratory effect, and each rock type is represented "
  "by a new set from that laboratory.")
Hd("Placement Density, Specimen Size, and Dump-Average Envelope", 2)
lE = weak(fb, "weakest (")
P(f"Laboratory specimens had void ratios of {min(s['e'] for s in SIT['sets']):.2f}–{max(s['e'] for s in SIT['sets']):.2f} and "
  "maximum particle sizes of 102–178 mm; a placement void ratio of 0.65 and a field size of 1 m were adopted for end-dumped "
  "waste rock (0.80 for the degradable E). The dump-average envelope weights the rock types by mass, which assumes mixing "
  "along the failure surface; the weakest-rock-type case bounds segregation. At σ′n = 1 MPa the median and 5th percentile "
  "of the dump-average φ′s "
  f"were {lbn['model']['P50'][isn(1)]:.1f}° and {lbn['model']['P05'][isn(1)]:.1f}° at laboratory density and size, "
  f"{fbn['model']['P50'][isn(1)]:.1f}° and {fbn['model']['P05'][isn(1)]:.1f}° at placement density without size shift, and "
  f"{fb['model']['P50'][isn(1)]:.1f}° and {fb['model']['P05'][isn(1)]:.1f}° with both (Table S2; Fig. 3b). The 5th percentile "
  f"was {bot(SITM):.1f}° with the tested samples taken as representative, {bot(SITL):.1f}° with an independent laboratory effect "
  f"for D and E, {bot(SITB):.1f}° with independent size shifts per rock type, and {bot(SITW):.1f}° with Weibull scaling; a surface "
  f"confined to E lowered it by {fb['model']['P05'][isn(1)] - lE['P05'][isn(1)]:.1f}°.")
Hd("Stability of a High Dump on a Competent Foundation", 2)
P("Dumps 150–700 m high with an overall slope of 2H:1V on a competent, drained, level rock foundation (*c*′ = 1 MPa, "
  "φ′ = 40°) were analyzed in Slide2 (Rocscience [[year]]) with the Morgenstern and Price (1965) method (half-sine interslice "
  "function) and a noncircular search by simulated annealing, with the envelopes tabulated from 0.05 to 8 MPa (Table S6). "
  "The section is a uniform dry face without benches (unit weight 17.2 kN/m³ at *e* = 0.65). The critical surfaces ran "
  "from the toe to the crest, "
  f"{SNd['prof_max']:.0f} m deep at 700 m, and mobilized σ′n averaging {SNd['media']:.1f} MPa and at most {SNd['max']:.1f} MPa "
  "(γ·h·cos²α). For 700 m, the factor of safety was "
  f"{f2(D_('e065', 'model', 700, 'P50'))} with the median and {f2(D_('e065', 'model', 700, 'P05'))} with the 5th-percentile "
  f"dump-average envelope, and {f2(D_('lab sin escala', 'model', 700, 'P50'))} and {f2(D_('lab sin escala', 'model', 700, 'P05'))} "
  f"at laboratory density and size; the quadratic form gave {f2(D_('x2 e065', 'model', 700, 'P05'))} with the 5th percentile, and "
  f"a circular search gave {f3(EST['conv']['P05'])} against {f3(D_('e065', 'model', 700, 'P05'))}. Analyzing "
  f"{MCm['n']} envelope samples, each with its own search, the model correlation gave {MCm['fallas']} "
  f"failure{'s' if MCm['fallas'] != 1 else ''} (one-sided 95% upper bound of the probability of failure "
  f"{100 * MCm['pf_unilateral95']:.1f}%; Clopper and Pearson 1934), and a surface confined to E gave {MCe['fallas']} of {MCe['n']} (lognormal reliability index {MCe['beta_ln']:.1f}). "
  f"Because ln FS was linear in ln τ at σ′rep = {SUS['sigma_rep']:.1f} MPa (correlation {SUS['r']:.4f}), the probability of failure "
  f"was also computed from all envelope samples: {sci(SUS['pf'])} (reliability index {-_norm.ppf(max(SUS['pf'], 1e-15)):.1f}) at "
  f"τ_D = {f3(EG['tau'])}, {sci(SUS['pf_integrada'])} (index {SUS['beta_integrado']:.1f}) integrated over the uncertainty of τ_D, and "
  f"{sci(SUS['pf_t4'])} with Student *t* tails on the size shift. The 5th percentile of the factor of safety equals the factor of "
  "safety of the 5th-percentile envelope only because of this monotone relation for a single governing material.")
Hd("Foundation and Seepage Mechanisms", 2)
P("The 700 m dump was also analyzed on a 10 m weak foundation layer (*c*′ = 0), horizontal or under a foundation inclined "
  "10°, on competent foundations inclined 10° or 20°, and with a basal water table 100 m above the toe (Hu = 1), with the "
  "bounded, quadratic, and published Leps 2.0 envelopes and the bounded 5th percentile at the ends of the asymptote ridge "
  f"({b3_lo:.0f}° and {b3_hi:.0f}°) (Table 4); weak layers were searched by annealing and by blocks along the layer. With a 25° or 30° layer or a "
  f"competent foundation the critical surfaces stayed in the waste rock, at σ′n ≤ {SNX:.1f} MPa, and the 5th-percentile factor "
  f"of safety changed by at most {DMEC:.2f}. Horizontal or inclined layers of 15° and 20° carried {100 * FRW[0]:.0f}–{100 * FRW[1]:.0f}% of the critical "
  f"surface and lowered it to {FSW[0]:.2f}–{FSW[1]:.2f}, while the waste rock along these surfaces reached {SNW:.1f} MPa. In all "
  f"dry cases the bounded and quadratic 5th percentiles differed by at most {DFORMT:.2f}, the ends of the asymptote ridge by at "
  f"most {DPHI:.2f}, and the published Leps 2.0 envelope gave factors of safety between the HiBER median and 5th percentile. "
  "With the basal water table, seepage exiting the face caused a shallow failure at the toe (factor of safety "
  f"{f2(al('agua100', 700, 'B P50'))} with the median envelope), which calls for a toe drain. Stability was thus controlled by "
  "the strength of weak layers and the cautious strength of the waste rock at 1–3 MPa, not by the envelope form.")

# ================================================================== DISCUSSION
Hd("Discussion")
Hd("What HiBER Adds", 2)
P("HiBER does not predict the central strength of an untested material better than Leps 2.0. Its contributions are a "
  "bounded extrapolation consistent with the suppression of dilatancy; intervals with nominal coverage at low stress; a "
  "likelihood that uses tests stopped at large strain and corrects the truncation of the database; a design procedure whose "
  "lower tail was checked out of sample; and the finding that particle size and laboratory dominate the uncertainty of an "
  "untested waste rock. The envelope form matters only above about 3 MPa, which the waste rock barely reached in the "
  "mechanisms analyzed; there the asymptote is the least constrained parameter.")
Hd("Design Procedure", 2)
P("The procedure is: (1) assign rock quality from the rock description, placement void ratio, and field particle size "
  "(the maximum size of 90–95% of the mass) to each rock type, and reduce any site tests with the maximum-deviator criterion; "
  "(2) check each set with Eq. (7) and Holm adjustment, review flagged sets, and exclude them only if they are stronger than "
  "the prior; (3) update the laboratory and set effects (Eq. 8), jointly when one laboratory tested several materials, and "
  "represent each rock type by a new set from that laboratory; (4) above the largest σ′n of the site tests, use the lower of "
  "the updated and prior percentiles; (5) shift the envelopes to placement density and field size; (6) adopt as "
  "characteristic value for a global mechanism the 5th percentile of the mean envelope, a Bayesian cautious estimate of the "
  "mean (Prästings et al. 2019) in the spirit of Eurocode 7 (CEN 2024); and (7) check the probability of failure by "
  "sampling the envelopes with stated correlations between rock types, including the weakest-rock-type case. "
  f"{DOMINIO}. The open implementation enforces this order and domain.")
P("The factor of safety computed with the characteristic envelope already contains the strength uncertainty, so mining "
  "acceptance criteria calibrated for best-estimate strength (Read and Stacey 2009; Hawley and Cunning 2017) double count it "
  f"unless recalibrated. The example gives a lognormal reliability index of about {MCm['beta_ln']:.1f}, or "
  f"{SUS['beta_integrado']:.1f} with the uncertainty of τ_D integrated, against 3.8 targeted by EN 1990 (CEN 2002) for 50 years "
  "in its medium consequence class; yet with a partial factor of 1.25 on tan φ′ (Eurocode 7) the characteristic factor of "
  f"safety of {f2(D_('e065', 'model', 700, 'P05'))} would fail. No target values are proposed here.")
Hd("Limitations and Testing Needs", 2)
P("Tests above 3 MPa come from five laboratories, mostly from 1963–1983; the asymptote is weakly identified; class labels "
  "may carry information from measured strength; the within-material residual is laboratory scatter, not spatial "
  f"variability; and the size-effect heterogeneity rests on {EL['k']} laboratories. Pore pressure in saturated basal layers, "
  "wetting collapse (Oldecop and Alonso 2001), seismic loading, three-dimensional geometry, and static liquefaction are "
  "outside the scope. The most useful new data are drained tests at σ′3 of 5–10 MPa on loose specimens carried to 25% axial "
  "strain, tests of one material at two sizes with parallel gradation, in situ density of dumped waste rock, durability "
  "tests of degradable rock types, and programs published after the database for external validation.")

# ================================================================== CONCLUSIONS
Hd("Conclusions")
for t in [
    "A dilatant part of tan φ′s that decays with stress toward an asymptote of about 28° bounds extrapolation consistently "
    "with the suppression of dilatancy; its in-sample advantage over an equally flexible quadratic form is small.",
    "Out of sample by laboratory, the bounded, quadratic, power, and Leps 2.0 envelopes are equally accurate; the hierarchical "
    "intervals have nominal coverage at low stress, and above 2 MPa the bounded 5th percentile is exceeded downward by about "
    "7% of tests.",
    "Site tests at low stress should update the envelope only within their stress range; above it the prior governs if lower.",
    "The between-laboratory heterogeneity of the size effect contributes about three quarters of the variance of an untested "
    "waste rock at field scale.",
    "In 2H:1V dumps up to 700 m high the waste rock along critical surfaces, also through weak foundation layers, mobilizes "
    "about 3 MPa or less, where the envelope forms agree; weak layers and the cautious strength, not the envelope form, "
    "control stability.",
]:
    A.item(t)

# ================================================================== BACK MATTER
Hd("Data Availability Statement")
P("Some or all data, models, or code generated or used during the study are available in a repository or online in accordance "
  "with funder data retention policies (HiBER code, parameters, covariance matrices, and evaluation scripts: [[repository DOI]]; "
  "calibration database: Arrieta 2025). Some or all data, models, or code generated or used during the study are proprietary or "
  "confidential in nature and may only be provided with restrictions (the site test results, which may be provided in "
  "anonymized form with the permission of their owner).", indent=False)
Hd("Acknowledgments")
P("[[Acknowledgments, funding, and the permission of the owner of the site test data to be completed.]] [[Declaration of the "
  "use of AI tools, as required by ASCE policy: tool, purpose, and confirmation that the authors reviewed and take "
  "responsibility for the content.]]", indent=False)
Hd("Notation")
P("*The following symbols are used in this paper:*", indent=False)
NOT = [(r"$\mathbf{C}_\beta$", "covariance matrix of the fixed effects"), ("*D*f, *D*l", "maximum particle size in the field and in the laboratory"),
       (r"$D^2$", "prior predictive Mahalanobis distance of the site tests"), (r"$\mathbf{G}_p$, $\mathbf{G}_s$", "covariances of laboratory and set effects"),
       (r"$\mathbf{J}$, $\mathbf{Z}$", "gradients of the envelope with respect to fixed and random effects"),
       (r"$\mathbf{P}$", r"prior covariance of $\mathbf{v}$"), (r"$\mathbf{S}$", "diagonal matrix of test-to-test variances"),
       (r"$\mathbf{V}$", "prior predictive covariance of the site tests"), ("*D*max, *D*r", "maximum particle size; reference size, 100 mm"),
       (r"$\mathbf{a}$", "gradient of the envelope at *x̄*"), ("*a*0, *a*1", "parameters of the test-to-test dispersion"),
       ("*c*, *c*₂", "rock quality class; quadratic coefficient"), ("*e*", "initial void ratio"),
       ("*f*", "mean envelope of a new material in terms of *y*"), ("g_0", "prior variance of q_0"), (r"$\mathbf{j}$, $\mathbf{z}$", "gradients of *f* (fixed and random effects)"),
       ("*m*", "exponent of the power envelope"), ("*n*", "number of site tests"), ("p_a", "atmospheric pressure (0.1013 MPa)"),
       ("q_0", "level of the envelope at *x̄*"), (r"$\mathbf{r}$, *r*i", "residuals of the site tests from the prior mean"),
       (r"$\mathbf{u}$, $\mathbf{u}^{(p)}$, $\mathbf{u}^{(s)}$", "random effects on (η, ζ): total, laboratory, set"), (r"$\mathbf{v}$", "random effects and fixed-effect deviations of a material"),
       ("*x*", "ln(σ′n/σ0)"), ("*x̄*", "mean of *x* over the site tests of a set"), ("*y*", "ln(τ/σ0)"),
       ("β_c", "coefficient of rock quality class *c*"), ("β_D", "within-material specimen-size coefficient"), ("β_e", "effect of void ratio on η"),
       ("Δ*e*, Δ*y*", "change of void ratio; shift of *y* for specimen size"), ("δ_c", "offset of the decay rate of class *c*"), ("ε", "test-to-test deviation"),
       ("ε_a", "axial strain at the maximum deviator stress"), ("ζ, ζ0", "decay rate of a material and of the good class"),
       ("η, η_t", "dilatant level, ln tan φ′1; truncation level"), ("θ", "level of the comparison forms"),
       ("κ", "between-set coefficient of ln(*D*max/*D*r)"), ("σ0", "reference stress, 10p_a"),
       ("σ′3", "effective confining stress"), ("σ′n", "effective normal stress on the failure plane"), ("σε", "standard deviation of test-to-test scatter"),
       ("τ", "shear strength"), ("τ_D", "between-laboratory standard deviation of β_D"), ("t∞", "tan φ′∞"), ("φ′1", "secant friction angle at σ′n = σ0"),
       ("φ′∞", "asymptotic secant friction angle"), ("φ′e=0", "φ′1 extrapolated to *e* = 0 in Leps 2.0"), ("φ′s", "secant friction angle")]
A.notacion(NOT)
Hd("Supplemental Materials")
P("Figs. S1–S5 and Tables S1–S6, including a worked example of the update with the published matrices, are available "
  "online in the ASCE Library (www.ascelibrary.org).", indent=False)

Hd("References")
REFS = [
    "Alonso, E. E., M. Tapias, and J. Gili. 2012. \"Scale effects in rockfill behaviour.\" *Géotech. Lett.* 2 (3): 155–160. https://doi.org/10.1680/geolett.12.00025.",
    "Arrieta, M. 2025. \"Rockfill test database. Version 1.\" Zenodo. Accessed October 6, 2026. https://doi.org/10.5281/zenodo.14665504.",
]
for r_ in REFS:
    A.ref(r_)       # the LaTeX version takes the reference list from lepsp.bib (BibTeX); the Word copy is a draft only

Hd("Figure Captions List")
for n_, f_, c_ in [
    (1, "Fig01_design_envelopes.png", "Design envelopes of HiBER for a new material tested by a new laboratory, at a specimen size of 100 mm, by rock quality and void ratio: median (thick lines) and 5th percentile (thin lines) of the mean envelope, up to the limit of use (8 MPa)."),
    (2, "Fig02_validation.png", "Out-of-sample evaluation, leaving out each laboratory: (a) coverage of the 80% interval by range of normal stress without site tests; and (b) mean CRPS of ln τ for held-out tests at σ′n ≥ 2 MPa with site tests at σ′n ≤ 1.5 MPa (bars: 95% bootstrap intervals over laboratories; filled: level update of the design procedure)."),
    (3, "Fig03_site_envelopes.png", "Waste rock of the example: (a) laboratory-scale envelopes by rock type with the site tests (open symbols: sets flagged by the conflict check and excluded); and (b) envelopes of placed waste rock (void ratio 0.65, rock type E 0.80; maximum particle size 1 m) by rock type and dump-average envelope. Dotted vertical lines mark the largest normal stress of the site tests."),
]:
    A.figura(n_, f_, c_)

rg = lambda i, d=3: f"{HP[i][1]:.{d}f}–{HP[i][2]:.{d}f}"
tabla(1, "Parameters of HiBER", ["Parameter", "Estimate", "Standard error or 90% credible interval"],
      [["β_c, good rock quality", f3(b["good"]), f3(SE["good"])], ["β_c, moderate rock quality", f3(b["moderate"]), f3(SE["moderate"])],
       ["β_c, low rock quality", f3(b["low"]), f3(SE["low"])], ["β_e", neg(f3(b["e"])), f3(SE["e"])], ["κ", f3(b["lnD"]), f3(SE["lnD"])],
       ["δ_c, moderate rock quality", neg(f3(b["dz_moderate"])), f3(SE["dz_moderate"])], ["δ_c, low rock quality", neg(f3(b["dz_low"])), f3(SE["dz_low"])],
       ["φ′∞ (°), weighted mean over the ridge", f"{PHM:.1f}", f"{ci_lo:.0f}–{ci_hi:.0f} (likelihood-ratio 95% interval)"], ["ζ0, weighted mean over the ridge", f2(ZEM), "—"],
       ["SD of η, laboratory", f3(HP[0][0]), rg(0)], ["SD of ζ, laboratory", f3(HP[1][0]), rg(1)],
       ["Correlation of η and ζ, laboratory", neg(f2(HP[2][0])), neg(f"{HP[2][1]:.2f} to {HP[2][2]:.2f}")],
       ["SD of η, set", f3(HP[3][0]), rg(3)], ["SD of ζ, set", f3(HP[4][0]), rg(4)],
       ["Correlation of η and ζ, set", neg(f2(HP[5][0])), neg(f"{HP[5][1]:.2f} to {HP[5][2]:.2f}")],
       ["σε at σ′n = σ0", f3(HP[6][0]), rg(6)], ["*a*1", neg(f3(HP[7][0])), neg(f"{HP[7][1]:.3f} to {HP[7][2]:.3f}")]],
      f"{N['ensayos']} tests ({N['censurados']} censored), {N['sets']} sets, {N['labs']} laboratories. Fixed effects at the maximum-likelihood point "
      f"of the ridge (φ′∞ = {FA['phi_cs']:.0f}°, ζ0 = {FA['zeta']:.2f}); variance parameters: posterior median and 90% credible interval. "
      f"Median φ′1 at e = 0 and Dmax = 100 mm: {phi1['good']:.1f}°, {phi1['moderate']:.1f}°, and {phi1['low']:.1f}° for good, moderate, and "
      "low rock quality. The covariance matrices are published with the code.")
r_ = lambda o: [pc(o["cob80"]), pc(o["bajo05"]), neg(f2(o["z_medio"])), f4(o["crps"])]
tabla(2, "Out-of-sample evaluation (leave one laboratory out)", ["Procedure", "80% coverage", "Below P05", "Mean z", "CRPS"],
      [[f"Mode A, all stresses ({A_['n']} tests)", "", "", "", ""], ["   HiBER, bounded form"] + r_(A_["acotada"]), ["   HiBER, quadratic form"] + r_(A_["cuadratica"]),
       ["   HiBER, power form"] + r_(A_["potencia"]), ["   Leps 2.0, hierarchical dispersion"] + r_(A_["leps2_jer"]),
       ["   Leps 2.0, constant dispersion"] + r_(A_["leps2_ref"]), [f"Mode A, σ′n ≥ 2 MPa ({A2['n']} tests)", "", "", "", ""],
       ["   HiBER, bounded form"] + r_(A2["acotada"]), ["   HiBER, quadratic form"] + r_(A2["cuadratica"]), ["   HiBER, power form"] + r_(A2["potencia"]),
       ["   Leps 2.0, hierarchical dispersion"] + r_(A2["leps2_jer"]), ["   Leps 2.0, constant dispersion"] + r_(A2["leps2_ref"]),
       [f"Mode B, site tests at σ′n ≤ 1.5 MPa ({BNn['ensayos']} tests)", "", "", "", ""], ["   Prior, no site tests"] + r_(BP),
       ["   Fit of φ′1, m = 0.90"] + r_(B90), ["   Fit of φ′1, m from training data"] + r_(BTR), ["   Joint update of both random effects"] + r_(BJ),
       ["   Level update of each set"] + r_(BN)],
      f"Uncensored tests. Mode A: {A_['n_lab']} laboratories; σ′n ≥ 2 MPa, {A2['n_lab']} laboratories. Mode B: {BNn['sets']} sets, {BNn['labs']} laboratories. "
      "Mean z: mean standardized residual (positive: strength underpredicted). Nominal values: 80% coverage and 5% below P05. "
      f"In Mode B the lower of the updated and prior percentiles placed {pc(REGLA['b05'])} below P05. CRPS in units of ln τ. "
      "No difference in CRPS was significant after Holm adjustment.")
fil = []
for cal, nom in (("buena", "Good"), ("moderada", "Moderate"), ("baja", "Low")):
    for e in (0.3, 0.45, 0.65):
        v = TD["tabla"][f"{cal}|{e}"]; w = TD["tabla_campo"][f"{cal}|{e}"]
        fil.append([nom if e == 0.3 else "", f"{e:.2f}"] + [f"{a:.1f} / {c:.1f} / {d:.1f}" + ("ᵃ" if (e == 0.65 and s_ > 3) else "")
                                                             for a, c, d, s_ in zip(v["P50"], v["P05"], w["P05"], TD["sn"])])
tabla(3, "Design values of the secant friction angle φ′s (°) for an untested material: median and 5th percentile of the mean envelope at a specimen size of 100 mm / 5th percentile at a field size of 1 m",
      ["Rock quality", "*e*"] + [f"{s:g} MPa" for s in TD["sn"]], fil,
      "New laboratory, no site tests, drained, maximum-deviator criterion; for global mechanisms. Field: size shift with zero mean "
      "and between-laboratory heterogeneity (the field median is within 0.3° of the laboratory median). Not applicable to degradable, "
      "argillaceous, or fines-rich waste. Values below about 33° rest on the model of the truncated tail (φ′1 ≥ 31° in the database). "
      "ᵃOutside the validity domain (e ≤ 0.55 above 3 MPa).")
fil = []; lab = SIT["escenarios"]["e=lab|ninguno"]["litologias"]; fld = SIT["escenarios"]["e=0.65|general"]["litologias"]
for k in "ABCDE":
    a_ = lab[k]; f_ = fld[k]
    fil.append([f"Rock type {k}{' (untested)' if k in 'DE' else ''}", f"{a_['P50'][isn(1)]:.1f} / {a_['P05'][isn(1)]:.1f}",
                f"{f_['P50'][isn(1)]:.1f} / {f_['P05'][isn(1)]:.1f}", f"{f_['P50'][isn(2)]:.1f} / {f_['P05'][isn(2)]:.1f}"])
for nm, k in (("Dump average, model correlation", "model"), ("Dump average, full correlation", "comonotonic")):
    a_ = lbn[k]; f_ = fb[k]
    fil.append([nm, f"{a_['P50'][isn(1)]:.1f} / {a_['P05'][isn(1)]:.1f}", f"{f_['P50'][isn(1)]:.1f} / {f_['P05'][isn(1)]:.1f}", f"{f_['P50'][isn(2)]:.1f} / {f_['P05'][isn(2)]:.1f}"])
json.dump(dict(titulo="Secant friction angle φ′s (°) of the waste rock of the example, median / 5th percentile of the mean envelope",
               enc=["Material", "Laboratory, 1 MPa", "Placed, 1 MPa", "Placed, 2 MPa"], filas=fil, nota=
               "Laboratory: specimen void ratio and size. Placed: void ratio 0.65 (rock type E, 0.80), maximum particle size 1 m, size effect "
               "with zero mean. Each rock type is represented by a new set from the site laboratory. The full-correlation case sorts the samples "
               "of each rock type at every stress, an upper bound on dependence."),
          open(AQ / "tabla_S2_r6.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
fil = []
for esc, nm in (("model", "Dump average, model correlation"), ("comonotonic", "Dump average, full correlation"), ("weakest tested", "Weakest tested rock type only"), ("weakest E", "Untested, degraded rock type E only")):
    fil.append([nm] + [f"{f2(D_('e065', esc, h, 'P50'))} / {f2(D_('e065', esc, h, 'P05'))}" for h in (150, 400, 700)])
_s6 = ("Factor of safety of dumps on a competent level foundation (Morgenstern–Price, Slide2), placed waste rock: median / 5th-percentile envelope",
      ["Envelope", "150 m", "400 m", "700 m"], fil,
      f"Uniform dry face without benches; unit weight 17.2 kN/m³ (rock type E only: 15.7 kN/m³). Monte Carlo at 700 m with {MCm['n']} envelope samples, each with its own search: "
      f"model correlation {MCm['fallas']} failure{'s' if MCm['fallas'] != 1 else ''} (lognormal reliability index {MCm['beta_ln']:.1f}); rock type E only {MCe['fallas']} "
      f"(index {MCe['beta_ln']:.1f}). 700 m, model correlation: without size shift {f2(D_('e065 sin escala', 'model', 700, 'P50'))} / {f2(D_('e065 sin escala', 'model', 700, 'P05'))}; "
      f"laboratory density with size shift (21 kN/m³) {f2(D_('lab escala', 'model', 700, 'P50'))} / {f2(D_('lab escala', 'model', 700, 'P05'))}; "
      f"laboratory density and size {f2(D_('lab sin escala', 'model', 700, 'P50'))} / {f2(D_('lab sin escala', 'model', 700, 'P05'))}; "
      f"size effect at its estimated mean {f2(D_('e065 escala datos', 'model', 700, 'P50'))} / {f2(D_('e065 escala datos', 'model', 700, 'P05'))}; "
      f"Weibull scaling {f2(D_('e065 weibull', 'model', 700, 'P50'))} / {f2(D_('e065 weibull', 'model', 700, 'P05'))}; "
      f"independent size shifts per rock type {f2(D_('e065 bD indep', 'model', 700, 'P50'))} / {f2(D_('e065 bD indep', 'model', 700, 'P05'))}; "
      f"tested samples taken as representative {f2(D_('e065 muestra', 'model', 700, 'P50'))} / {f2(D_('e065 muestra', 'model', 700, 'P05'))}; "
      f"quadratic form {f2(D_('x2 e065', 'model', 700, 'P50'))} / {f2(D_('x2 e065', 'model', 700, 'P05'))}.")
json.dump(dict(titulo=_s6[0], enc=_s6[1], filas=_s6[2], nota=_s6[3]), open(AQ / "tabla_S6_r6.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
fil = []
for t, H, nm in MECS:
    fil.append([f"{nm}, {H} m", f"{snA(t, H):.1f}", f"{f2(al(t, H, 'B P50'))} / {f2(al(t, H, 'B P05'))}", f"{f2(al(t, H, 'Q P50'))} / {f2(al(t, H, 'Q P05'))}",
                f"{f2(al(t, H, 'Flo P05'))} / {f2(al(t, H, 'Fhi P05'))}", f2(al(t, H, "L2 P50"))])
pos = len(fil) - (1 if MECS[-1][0] == "agua100" else 0)            # capas débiles (lote 72) antes de la fila del freático
fil[pos:pos] = [[f"{nm}, 700 m", f"{max(bq(t, 'B P05', 'sn_max_desmonte'), bq(t, 'Q P05', 'sn_max_desmonte')):.1f}",
                 f"{f2(bq(t, 'B P50'))} / {f2(bq(t, 'B P05'))}", f"— / {f2(bq(t, 'Q P05'))}", "—", f2(bq(t, "L2 P50"))] for t, nm in WK]
tabla(4, "Factor of safety of foundation and seepage mechanisms, dump-average envelope of placed waste rock",
      ["Mechanism", "σ′n max. (MPa)", "Bounded", "Quadratic", f"φ′∞ = {b3_lo:.0f}° / {b3_hi:.0f}°", "Leps 2.0"],
      fil, "Slope 2H:1V; unit weight 17.2 kN/m³; foundation layer 10 m thick with c′ = 0 under the whole dump; inclined foundations dip toward the toe. "
           "Weak layers of 15° and 20°: lower factor of safety of the annealing and block searches; σ′n max. in the waste rock. "
           "Bounded and quadratic: median / 5th-percentile envelope; φ′∞: bounded 5th percentile restricted to samples at the ends of the ridge. "
           "σ′n max.: largest effective normal stress at the base of the slices of the critical surface with the bounded 5th percentile (γ·h·cos²α less pore pressure). "
           "Basal water table: shallow failure at the toe where seepage exits the face. "
           "Leps 2.0: published envelope (φ′e=0 − 20e, m = 0.9) at placement void ratio, without size shift.")
out = AQ / "HiBER_IJGM_manuscript_r6.docx"; doc.save(str(out)); print("written", out, "| equations:", A.NEQ[0])
(AQ / "latex").mkdir(exist_ok=True); usadas = A.escribir_tex(str(AQ / "latex" / "HiBER_IJGM_manuscript_r6.tex"), "figs/", nametag="Anticona", bib="hiber")
print("citas LaTeX:", len(usadas), "claves distintas de", len(A.CITAS), "| sin citar:", sorted(set(A.CITAS.values()) - set(usadas)) or "ninguna")
print("written", AQ / "latex" / "HiBER_IJGM_manuscript_r6.tex")
