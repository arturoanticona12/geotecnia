import json,sys
d=json.load(open(sys.argv[1]))
for p,rows in d.items():
    print('p',p)
    for r in rows: print('  eps=%5.2f q=%8.2f u=%7.2f s3=%7.2f s1=%8.2f obl=%5.2f calc=%6.3f'%(r[0],r[1],r[2],r[3],r[4],r[8],r[4]/r[3]))
