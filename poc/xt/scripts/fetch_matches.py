import json, os, sys, time, urllib.request
BASE="https://raw.githubusercontent.com/statsbomb/open-data/master/data/"
root=sys.argv[1]
comps=json.load(open(f"{root}/cache/raw/competitions.json"))
def get(url, path, tries=5):
    if os.path.exists(path) and os.path.getsize(path)>0: return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=60) as r: data=r.read()
            open(path+".part","wb").write(data); os.replace(path+".part", path); return
        except Exception as e:
            print("retry",url,e, file=sys.stderr); time.sleep(2**i)
    raise RuntimeError(url)
rows=[]
for c in comps:
    if c["competition_gender"]!="male": continue
    p=f"{root}/cache/raw/matches/{c['competition_id']}/{c['season_id']}.json"
    get(BASE+f"matches/{c['competition_id']}/{c['season_id']}.json", p)
    ms=json.load(open(p))
    rows.append((c['competition_name'],c['season_name'],len(ms)))
    time.sleep(0.2)
tot=0
for r in rows: print(*r); tot+=r[2]
print("total",tot)
