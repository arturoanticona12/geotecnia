"""Estadística de carga puntual Is50 por litología (IDIEM 1.914.482-F, pp. 356, 358, 360, 362)."""
import statistics as st
# (página, fragmento, litología, Is50 MPa, válido)
d = """356 A T 5.9 1|356 B C 5.5 1|356 C T 4.3 1|356 D C 5.3 1|356 E T 7.2 1|356 F T 1.1 1|356 G T 4.7 1|356 H T 6.7 1|356 I T 7.5 1|356 J T 6.7 1|
358 A T 8.8 1|358 B T 4.6 1|358 C T 0.6 0|358 D T 6.5 1|358 E C 4.3 1|358 F C 4.3 1|358 G T 3.7 1|358 H T 2.1 1|
360 A T 3.3 1|360 B T 1.8 1|360 C T 3.4 0|360 D T 4.7 1|360 E T 2.1 1|360 F T 4.6 1|360 G C 5.1 1|360 H T 9.9 0|360 I T 1.3 1|360 J T 5.1 0|
362 A C 5.8 1|362 B T 6.5 1|362 C T 6.1 1|362 D T 5.2 1|362 E T 7.1 1|362 F T 8.2 1|362 G C 6.6 1|362 H T 6.5 0|362 I T 4.3 1|362 J T 5.3 1"""
rows = [r.split() for r in d.replace("\n", "").split("|") if r.strip()]
print("fragmentos:", len(rows))
for lit in "TC":
    a = [float(r[3]) for r in rows if r[2] == lit]
    v = [float(r[3]) for r in rows if r[2] == lit and r[4] == "1"]
    print(lit, "n=", len(a), "válidos=", len(v), "media válidos=%.2f mediana=%.2f min=%.1f max=%.1f" % (st.mean(v), st.median(v), min(v), max(v)))
for pg in ("356", "358", "360", "362"):
    v = [float(r[3]) for r in rows if r[0] == pg and r[4] == "1"]
    a = [float(r[3]) for r in rows if r[0] == pg]
    print(pg, "media válidos %.2f  media todos %.2f" % (st.mean(v), st.mean(a)))
