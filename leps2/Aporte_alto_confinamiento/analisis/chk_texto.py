import sys; from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent)); sys.stdout.reconfigure(encoding="utf-8")
import numpy as np
from common import load_db, PA
df = load_db()
print("ensayos con σn > 4.48:", (df.sn > 4.48).sum(), f"({100*(df.sn>4.48).mean():.1f} %)")
# conversión: lineal vs almacenada (primer ensayo de Holtz & Gibbs)
r = df.iloc[0]; s1, s3 = r.s1, r.s3
phi = np.arcsin((s1 - s3) / (s1 + s3)); snl = (s1 + s3)/2 - (s1 - s3)/2*np.sin(phi); tl = (s1 - s3)/2*np.cos(phi)
print(f"lineal σn={snl:.4f} τ={tl:.4f} | base σn={r.sn:.4f} τ={r.tau:.4f}")
d = df.dropna(subset=["s1","s3"]); ph = np.arcsin((d.s1-d.s3)/(d.s1+d.s3)); snl = (d.s1+d.s3)/2-(d.s1-d.s3)/2*np.sin(ph)
print("fracción de ensayos con σn base > σn lineal:", np.mean(d.sn > snl*1.001).round(3))
# σ3 equivalente a σn en la envolvente (Ecs. 10-12 de Cylwik et al. 2025)
for p1 in (38, 41):
    for m in (0.9, 0.87):
        for sn in (3.0, 6.0):
            K = np.tan(np.radians(p1))*10**(1-m); tau = K*PA*(sn/PA)**m; tphi = K*m*(sn/PA)**(m-1)
            beta = 0.5*np.arctan(tphi) + np.pi/4; s3 = sn - tau/np.tan(beta)
            print(f"φ1={p1} m={m} σn={sn}: σ3={s3:.2f} MPa")
