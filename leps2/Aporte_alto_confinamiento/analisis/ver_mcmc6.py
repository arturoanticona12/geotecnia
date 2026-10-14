import json, sys
sys.stdout.reconfigure(encoding="utf-8")
M = json.load(open("lepsp_mcmc6.json", encoding="utf-8"))
nom = ["sd_eta_pub", "sd_zeta_pub", "rho_pub", "sd_eta_set", "sd_zeta_set", "rho_set", "sig_eps0", "a1"]
a = M["acotada"]
for i, n in enumerate(nom):
    print(f"{n:12s} rhat {a['rhat'][i]:.3f}  ess_bulk {a['ess_bulk'][i]:6.0f}  ess_tail {a['ess_tail'][i]:6.0f}")
for k in ("previa_0.1", "previa_0.25", "previa_0.5"):
    print(k, "medianas", [round(h[0], 3) for h in M[k]["hiper"]], "| R̂", M[k].get("rhat_max"))
    print("   IC90", [[round(h[1], 3), round(h[2], 3)] for h in M[k]["hiper"]])
print("beta", {k: round(v, 4) for k, v in M["beta"].items()})
print("se  ", {k: round(v, 4) for k, v in M["se"].items()})
print("cresta", M["cresta"])
