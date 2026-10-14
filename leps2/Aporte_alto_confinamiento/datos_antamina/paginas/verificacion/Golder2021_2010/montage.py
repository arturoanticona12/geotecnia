# uso: montage.py <pdf> <salida.png> <dpi> <cols> <paginas> <clip x0,y0,x1,y1>
import fitz, sys, os
pdf,outn,dpi,cols,pages,clip=sys.argv[1],sys.argv[2],int(sys.argv[3]),int(sys.argv[4]),sys.argv[5],[float(x) for x in sys.argv[6].split(',')]
doc=fitz.open(pdf); ps=[]
for t in pages.split(','):
    if '-' in t:
        a,b=map(int,t.split('-')); ps+=range(a,b+1)
    else: ps.append(int(t))
pix=[]
for p in ps:
    pg=doc[p-1]; r=pg.rect
    c=fitz.Rect(r.x0+clip[0]*r.width,r.y0+clip[1]*r.height,r.x0+clip[2]*r.width,r.y0+clip[3]*r.height)
    pix.append((p,pg.get_pixmap(dpi=dpi,clip=c)))
w=max(x.width for _,x in pix); h=max(x.height for _,x in pix)+18
rows=(len(pix)+cols-1)//cols
out=fitz.Pixmap(fitz.csRGB,fitz.IRect(0,0,w*cols,h*rows),False); out.clear_with(255)
for i,(p,x) in enumerate(pix):
    if x.n!=3 or x.alpha: x=fitz.Pixmap(fitz.csRGB,x,0)
    x.set_origin((i%cols)*w,(i//cols)*h+18); out.copy(x,x.irect)
out.save(os.path.join(os.path.dirname(os.path.abspath(__file__)),outn))
# etiqueta de pagina: escribir con fitz en un pdf temporal
d=fitz.open(); pg=d.new_page(width=w*cols,height=h*rows)
pg.insert_image(pg.rect,filename=os.path.join(os.path.dirname(os.path.abspath(__file__)),outn))
for i,(p,x) in enumerate(pix):
    pg.insert_text(((i%cols)*w+5,(i//cols)*h+14),f'PDF p.{p}',fontsize=13,color=(1,0,0))
pg.get_pixmap(dpi=72).save(os.path.join(os.path.dirname(os.path.abspath(__file__)),outn))
print(outn,w*cols,h*rows)
