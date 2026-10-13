"""Consulta Crossref (y DataCite para Zenodo) por cada DOI citado y guarda los metadatos para armar las referencias."""
import json, sys, urllib.request, urllib.parse
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
DOIS = [
    "10.1139/t83-077", "10.1680/geot.1955.5.1.7", "10.1680/geot.2004.54.3.157", "10.1061/IJGNAI.GMENG-12050",
    "10.1139/t98-009", "10.1130/REG15-p191", "10.1061/(ASCE)0733-9410(1996)122:4(309)", "10.1061/JSFEAQ.0001433",
    "10.36487/ACG_repo/708_2", "10.1061/JSFEAQ.0001735", "10.1680/geot.51.2.127.40283",
    "10.1061/(ASCE)GT.1943-5606.0002314", "10.1139/cgj-2014-0079", "10.36487/ACG_repo/802_6",
    "10.1061/(ASCE)GT.1943-5606.0001176", "10.1061/(ASCE)0733-9410(1996)122:2(109)", "10.25080/Majora-92bf1922-011",
    "10.1680/geot.1967.17.1.11", "10.1139/t04-065", "10.36487/ACG_repo/802_1", "10.26190/unsworks/21014",
    "10.1007/s10035-024-01428-0", "10.1016/j.ijrmms.2024.105915",
    # Leps 3.0 probabilístico
    "10.2307/2529876", "10.1198/016214506000001437", "10.1139/t99-038", "10.1061/AJGEB6.0000517",
    "10.1061/JSFEAQ.0000958", "10.1680/geot.1986.36.1.65", "10.1061/AJGEB6.0001167",
]
out = {}
for d in DOIS:
    try:
        url = "https://api.crossref.org/works/" + urllib.parse.quote(d, safe="")
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "doi-check/1.0"}), timeout=30) as r:
            m = json.load(r)["message"]
        au = "; ".join(f"{a.get('family','')}, {a.get('given','')}" for a in m.get("author", []))
        yr = (m.get("published-print") or m.get("published-online") or m.get("issued"))["date-parts"][0][0]
        rec = dict(autores=au, anio=yr, titulo=(m.get("title") or [""])[0], revista=(m.get("container-title") or [""])[0],
                   vol=m.get("volume", ""), num=m.get("issue", ""), pag=m.get("page", "") or m.get("article-number", ""), tipo=m.get("type"))
    except Exception as e:
        rec = dict(error=str(e)[:80])
    out[d] = rec
    print(d, "|", rec)
# Zenodo (DataCite)
for d in ["10.5281/zenodo.14665504"]:
    try:
        with urllib.request.urlopen("https://api.datacite.org/dois/" + d, timeout=30) as r:
            a = json.load(r)["data"]["attributes"]
        rec = dict(autores="; ".join(c.get("name", "") for c in a["creators"]), anio=a["publicationYear"], titulo=a["titles"][0]["title"],
                   editor=a.get("publisher"), version=a.get("version"))
    except Exception as e:
        rec = dict(error=str(e)[:80])
    out[d] = rec; print(d, "|", rec)
json.dump(out, open(Path(__file__).with_name("dois_crossref.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
