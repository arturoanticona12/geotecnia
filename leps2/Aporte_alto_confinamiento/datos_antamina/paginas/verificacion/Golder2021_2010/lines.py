import fitz, sys, re
doc=fitz.open(sys.argv[1])
for p in range(int(sys.argv[2]), int(sys.argv[3])+1):
    pg=doc[p-1]
    words=pg.get_text('words')
    # group by line (block,line)
    lines={}
    for w in words:
        k=(round(w[1]/3),)
        lines.setdefault(k,[]).append(w)
    out=[]
    for k in sorted(lines):
        ws=sorted(lines[k],key=lambda w:w[0])
        out.append(' '.join(w[4] for w in ws))
    txt='\n'.join(out)
    pat=sys.argv[4] if len(sys.argv)>4 else None
    print(f'=== p{p} ===')
    for l in out:
        if pat is None or re.search(pat,l): print(l)
