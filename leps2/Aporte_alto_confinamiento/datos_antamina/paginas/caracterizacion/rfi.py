import sys; sys.stdout.reconfigure(encoding="utf-8")
import sys, fitz, os
d=fitz.open(sys.argv[1]); out=sys.argv[2]
print("pages", d.page_count, d.metadata)
for i,p in enumerate(d):
    t=p.get_text()
    print(f"\n=== PAGE {i+1} === chars={len(t)} imgs={len(p.get_images())}")
    print(t)
    p.get_pixmap(dpi=130).save(os.path.join(out, f"RFI_p{i+1:02d}.png"))
