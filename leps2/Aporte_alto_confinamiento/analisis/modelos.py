"""Envolventes candidatas, conversión envolvente → σ1(σ3) y clasificación de calidad de roca (Tabla 5 de Cylwik et al., 2025)."""
import numpy as np

PA = 0.1013
S0 = 10 * PA  # esfuerzo de anclaje

# Tabla 5 de Cylwik et al. (2025) aplicada a los rótulos de la base. Mezclas y rótulos ambiguos: ver CALIDAD_NOTA.
CALIDAD = {
    "good": ["Basalt", "basalt", "Latite basalt", "dolomitic basalt", "Granite", "granite", "Calcareous quarried",
             "Crushed Colluvial BIF"],
    "moderate": ["phyllite", "weathered phyllite", "Slate", "slate", "andesite", "argillite", "quartzite",
                 "Quartzite shale rock", "gravel, quartz (crushed)", "Diorite", "diorite", "Conglomerate", "conglomerate",
                 "Silicified conglomerate", "silicified conglomerate", "amphibolite", "granitic gneiss", "granite-gneiss",
                 "granite-gneiss + 30% schist", "rhyolite", "rhyolite (MW)", "rhyolite (SW-MW)", "limestone & basalt"],
    "low": ["Gravel", "gravel", "King River Gravels", "alluvial", "gravel, quartz", "sand and gravel", "sandy gravel",
            "silty gravel", "sandy clayey gravel", "clayey gravel", "clayey gravelly sand", "gravel/sand/silt",
            "gravel + clay mix", "gneiss/granite/schist", "Limestone", "limestone", "Sandstone", "sandstone",
            "sandstone/siltstone", "sandstone & siltstone", "shale & siltstone", "Schist", "schist", "Sedimentary",
            "greywacke", "tuff", "porphyritic quartz monzonite", "weathered argillaceous chert", "chert 43%"],
}
CALIDAD_NOTA = ("«limestone & basalt» se asignó a calidad moderada (mezcla de baja y buena); «Sedimentary» corresponde a "
                "grauvaca según la propia base; «gneiss/granite/schist» es grava de río (baja).")
CLASE = {mt: c for c, lst in CALIDAD.items() for mt in lst}


# ---------------------------------------------------------------- envolventes τ(σn) vectorizadas
def tau_leps2(sn, phi1, m):
    return np.tan(np.radians(phi1)) * S0 ** (1 - m) * sn ** m


def tau_leps3(sn, phi1, phics, scr):
    """φs = φcs + (φ1 − φcs)·ln(1 + σcr/σn)/ln(1 + σcr/σ0)."""
    phis = phics + (phi1 - phics) * np.log1p(scr / sn) / np.log1p(scr / S0)
    return sn * np.tan(np.radians(phis))


def sigma1(tau_fn, s3, *par, it=70):
    """σ1 de falla para cada σ3: círculo que pasa por σ3 y es tangente a τ(σn) (Ecs. 10–12 de Cylwik et al., 2025,
    generalizadas a cualquier envolvente). Bisección en ln σn del punto de tangencia, vectorizada."""
    s3 = np.asarray(s3, float)
    lo, hi = np.log(s3 * 1.0001 + 1e-6), np.log(s3 * 40 + 0.5)

    def g(lsn):
        sn = np.exp(lsn); h = sn * 1e-4
        t = tau_fn(sn, *par); dt = (tau_fn(sn + h, *par) - tau_fn(sn - h, *par)) / (2 * h)
        b = np.arctan(dt) / 2 + np.pi / 4
        return sn - t / np.tan(b) - s3, sn, t, b
    for _ in range(it):
        mid = 0.5 * (lo + hi); v = g(mid)[0]
        hi = np.where(v > 0, mid, hi); lo = np.where(v > 0, lo, mid)
    _, sn, t, b = g(0.5 * (lo + hi))
    return sn + t * np.tan(b), sn, t
