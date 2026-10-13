import numpy as np, sys
from PIL import Image
from scipy import ndimage
a = np.asarray(Image.open(sys.argv[1]).convert("RGB")).astype(int)[::-1]
colored = (a[:,:,2]-a[:,:,0] > 40) | (a.sum(2)<250)
er = ndimage.binary_erosion(colored, iterations=3)
lab, n = ndimage.label(er)
x0,dx = 108.5, (1079-108.5)/5
y100,y0 = 21.0, 583.5
pts=[]
for k in range(1,n+1):
    ys,xs = np.where(lab==k)
    cx,cy = xs.mean(), ys.mean()
    D = 10**(-2 + (cx-x0)/dx); P = (y0-cy)/(y0-y100)*100
    pts.append((D,P,len(ys)))
for D,P,s in sorted(pts): print(f"D={D:9.3f} mm  pasa={P:6.1f} %  npx={s}")
