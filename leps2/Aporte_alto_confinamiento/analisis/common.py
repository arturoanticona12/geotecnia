import numpy as np, pandas as pd
from scipy.optimize import least_squares
PA = 0.1013
SP = str(__import__("pathlib").Path(__file__).parent)
P = r"H:\Mi unidad\00_WORKSPACE\20_PROYECTOS_CONSULTORÍA\Antamina\2026_Gate3\Revisión de literatura\Leps 2.0"


def load_db():
    df = pd.read_excel(P + r"\Rockfill_Test_Database_v1.xlsx", sheet_name="Data", header=0)
    df.columns = [str(c).replace("\n", " ").strip() for c in df.columns]
    ren = {"σ3 (MPa)": "s3", "σ1 (MPa)": "s1", "σn (MPa)": "sn", "τ (MPa)": "tau", "ei": "e", "UCS (MPa)": "UCS",
           "Bg (%)": "Bg", "evol (%)": "evol", "eaxial (%)": "eax", "Fines-BT (%)": "fines", "D50-BT (mm)": "D50",
           "Dmax (mm)": "Dmax", "sat (%)": "sat"}
    df = df.rename(columns=ren)
    for c in ren.values():
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df = df[df["sn"] > 0].copy()
    # clave única de set: los ID "A" y "C" se repiten entre publicaciones
    df["Set"] = df["Reference"].astype(str) + " | " + df["Set"].astype(str)
    df["phis"] = np.degrees(np.arctan(df.tau / df.sn))
    df["phi1_test"] = np.degrees(np.arctan(df.tau / ((10 * PA) ** 0.1 * df.sn ** 0.9)))
    return df


def tau_leps(sn, phi1, m):
    return np.tan(np.radians(phi1)) * (10 * PA) ** (1 - m) * np.asarray(sn) ** m


def fit_set(sn, tau, m=None):
    if m is None:
        f = lambda x: np.log(tau_leps(sn, x[0], x[1])) - np.log(tau)
        return least_squares(f, [41, 0.9], bounds=([15, 0.5], [70, 1.0])).x
    f = lambda x: np.log(tau_leps(sn, x[0], m)) - np.log(tau)
    return np.array([least_squares(f, [41], bounds=([15], [70])).x[0], m])


def within_set(df, lo=0.3, hi=1.5):
    rows = []
    for s, g in df.groupby("Set"):
        ref = g[(g.sn >= lo) & (g.sn <= hi)]
        if len(ref) < 1 or len(g) < 3:
            continue
        phi1_ref = fit_set(ref.sn.values, ref.tau.values, m=0.9)[0]
        for _, r in g.iterrows():
            rows.append(dict(Set=s, sn=r.sn, s3=r.s3, dphi1=r.phi1_test - phi1_ref, phi1_ref=phi1_ref, UCS=r.UCS,
                             Bg=r.Bg, e=r.e, mat=r["Material Type"], ref=r.Reference))
    return pd.DataFrame(rows)


df = load_db()


