import re, json, pathlib
out = pathlib.Path(__file__).parent
txt = open(out/"texto_todo.txt",encoding="utf8").read()
pages = {}
for blk in txt.split("\n===== ")[1:]:
    head, body = blk.split("\n",1)
    pages[head.split(" | ")[0]] = body.split("\n")
num = re.compile(r"^-?\d+\.\d+$|^-?\d+$")
res = {}
for k in ["M","H","I","P1","P2"]:
    for p in (3,4,5):
        L=[re.sub(r"^(-?\d+),(\d+)$",r"\1.\2",x.strip()) for x in pages[f"TX_{k}_p{p}"]]
        s3=[x for x in L if re.fullmatch(r"\d+ kPa",x)]
        g=[x for x in L if x in ("2.70","2,70")]
        def after(lbl, n):
            i=[j for j,x in enumerate(L) if x.startswith(lbl)][0]
            vals=[]; j=i+1
            while len(vals)<n:
                if num.match(L[j]): vals.append(float(L[j]))
                j+=1
            return vals
        H=after("Altura",2); D=after("Diámetro",2); B=after('Parámetro "B"',1); V=after("Velocidad",1)
        W=after("(%)",2) ; C=after("Presión de celda",1); R=after("(g/cm3)",2); BP=after("Contra presión",1)
        # rows
        i=max(j for j,x in enumerate(L) if x=="(kPa)")+1
        nums=[]
        while i<len(L) and (num.match(L[i]) or L[i]==""):
            if L[i]: nums.append(float(L[i]))
            i+=1
        rows=[nums[r:r+9] for r in range(0,len(nums)//9*9,9)]
        res[f"{k}_{s3[0]}"]=dict(set=k,page=p,s3=s3,hidden=g,H=H,D=D,B=B,v=V,w=W,cell=C,rho=R,bp=BP,nrows=len(rows),leftover=len(nums)%9,rows=rows)
        print(k,p,s3,g,H,D,B,V,W,C,R,BP,len(rows),len(nums)%9, rows[-1])
json.dump(res,open(out/"tx_verif.json","w"),indent=0)

