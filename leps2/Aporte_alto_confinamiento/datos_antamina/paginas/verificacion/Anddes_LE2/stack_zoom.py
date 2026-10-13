from PIL import Image
import pathlib
out=pathlib.Path(__file__).parent
fs=sorted(out.glob("zoom_PR_linea_*.png"))
ims=[Image.open(f).rotate(-0,expand=True) for f in fs]
ims=[i.resize((i.width*2//3,i.height*2//3)) for i in ims]
W=sum(i.width for i in ims); H=max(i.height for i in ims)
c=Image.new("RGB",(W,H),"white"); x=0
for i in ims: c.paste(i,(x,0)); x+=i.width
c.save(out/"zoom_PR_lineas_todas.png"); print([f.name for f in fs])
