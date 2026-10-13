import json,sys
d=json.load(open(sys.argv[1]))
for p,v in d.items():
    h=v['h']; print(p,h['B'],h['celda'],h['contra'],h['s3c'],h['final_consol'],h['final_corte'],h['obs'])
