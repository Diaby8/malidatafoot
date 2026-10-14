"""Télécharge les événements StatsBomb du jeu d'entraînement (hommes, saisons >= 2003, hors CAN 2023).
Cache gzip, 3 connexions max, reprises exponentielles."""
import gzip, json, os, re, sys, time, urllib.request
from concurrent.futures import ThreadPoolExecutor
BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data/"
root = sys.argv[1]
comps = json.load(open(f"{root}/cache/raw/competitions.json"))

def start_year(s):
    return int(re.match(r"(\d{4})", s).group(1))

pool = []
for c in comps:
    if c["competition_gender"] != "male": continue
    if (c["competition_id"], c["season_id"]) == (1267, 107): continue
    if start_year(c["season_name"]) < 2003: continue
    for m in json.load(open(f"{root}/cache/raw/matches/{c['competition_id']}/{c['season_id']}.json")):
        pool.append({"match_id": m["match_id"], "competition": c["competition_name"], "season": c["season_name"],
                     "competition_id": c["competition_id"], "season_id": c["season_id"], "match_date": m["match_date"],
                     "home": m["home_team"]["home_team_name"], "away": m["away_team"]["away_team_name"]})
json.dump(pool, open(f"{root}/cache/training_pool.json", "w"))
print("matches in pool:", len(pool), flush=True)
os.makedirs(f"{root}/cache/raw/events", exist_ok=True)

def fetch(mid):
    path = f"{root}/cache/raw/events/{mid}.json.gz"
    if os.path.exists(path): return 0
    for i in range(6):
        try:
            with urllib.request.urlopen(BASE + f"events/{mid}.json", timeout=120) as r:
                data = r.read()
            json.loads(data)  # validation : JSON complet
            with gzip.open(path + ".part", "wb", compresslevel=6) as f: f.write(data)
            os.replace(path + ".part", path); time.sleep(0.1); return 1
        except Exception as e:
            print("retry", mid, repr(e)[:120], file=sys.stderr, flush=True); time.sleep(2 ** i)
    print("FAILED", mid, file=sys.stderr, flush=True); return -1

done = 0
with ThreadPoolExecutor(max_workers=3) as ex:
    for k, r in enumerate(ex.map(fetch, [p["match_id"] for p in pool])):
        if (k + 1) % 100 == 0: print(k + 1, "processed", flush=True)
print("done", flush=True)
