import json, glob, sys
import numpy as np
sys.stdout.reconfigure(encoding="utf-8")
P = json.load(open("lepsp_parametros.json", encoding="utf-8"))["formas"]["acotada"]
p = np.array(P["psi"])
print("psi óptimo REML: sd_eta_pub %.3f sd_zeta_pub %.3f rho_pub %.2f | sd_eta_set %.3f sd_zeta_set %.3f rho_set %.2f | sig %.3f a1 %.3f"
      % (np.exp(p[0]), np.exp(p[1]), np.tanh(p[2]), np.exp(p[3]), np.exp(p[4]), np.tanh(p[5]), np.exp(p[6]), p[7]))
for f in sorted(glob.glob("lepsp_perfil6_*.json")):
    for r in json.load(open(f, encoding="utf-8"))["perfil"]:
        if r["psi"]:
            q = np.array(r["psi"]); print(f"  perfil φ′∞ {r['phi']:4.0f}: sd_eta_pub {np.exp(q[0]):.3f}  sd_eta_set {np.exp(q[3]):.3f}")
