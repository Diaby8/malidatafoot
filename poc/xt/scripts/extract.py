"""Extrait passes, conduites et tirs (format compact) des fichiers d'événements StatsBomb -> parquet."""
import gzip, json, sys, glob, os
from multiprocessing import Pool
import pandas as pd

KEEP = {"Pass", "Carry", "Shot"}

def ts_s(t):
    h, m, s = t.split(":"); return int(h) * 3600 + int(m) * 60 + float(s)

def rows_of(mid, events):
    out = []
    for e in events:
        t = e["type"]["name"]
        if t not in KEEP or e["period"] > 4 or "location" not in e: continue
        r = {"match_id": mid, "idx": e["index"], "period": e["period"], "ts": ts_s(e["timestamp"]),
             "minute": e["minute"], "second": e["second"], "type": t,
             "team": e["team"]["name"], "player_id": e.get("player", {}).get("id"), "player": e.get("player", {}).get("name"),
             "position": e.get("position", {}).get("name"),
             "possession": e["possession"], "possession_team": e["possession_team"]["name"],
             "play_pattern": e["play_pattern"]["name"], "x": e["location"][0], "y": e["location"][1],
             "ex": None, "ey": None, "sub_type": None, "outcome": None, "xg": None}
        if t == "Pass":
            p = e["pass"]; r["ex"], r["ey"] = p["end_location"][:2]
            r["sub_type"] = p.get("type", {}).get("name"); r["outcome"] = p.get("outcome", {}).get("name")
        elif t == "Carry":
            r["ex"], r["ey"] = e["carry"]["end_location"][:2]
        else:
            s = e["shot"]; r["sub_type"] = s.get("type", {}).get("name"); r["outcome"] = s.get("outcome", {}).get("name")
            r["xg"] = s.get("statsbomb_xg")
        out.append(r)
    return out

CATS = ["type", "team", "player", "position", "possession_team", "play_pattern", "sub_type", "outcome"]

def work(path):
    mid = int(os.path.basename(path).split(".")[0])
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rb") as f: ev = json.load(f)
    df = pd.DataFrame(rows_of(mid, ev))
    df["player_id"] = df["player_id"].astype("Int64")
    for c in ("ex", "ey", "xg"): df[c] = df[c].astype(float)
    for c in ("idx", "period", "minute", "second", "possession"): df[c] = df[c].astype("int32")
    for c in CATS: df[c] = df[c].astype("string")
    return df

if __name__ == "__main__":
    src, dst = sys.argv[1], sys.argv[2]
    files = sorted(glob.glob(os.path.join(src, "*.json*")))
    parts = []
    with Pool(2) as p:
        for k, df in enumerate(p.imap_unordered(work, files, chunksize=8)):
            for c in CATS: df[c] = df[c].astype("category")
            parts.append(df)
            if (k + 1) % 250 == 0: print(k + 1, "files", flush=True)
    for c in CATS:
        cats = sorted(set().union(*[set(d[c].cat.categories) for d in parts]))
        for d in parts: d[c] = d[c].cat.set_categories(cats)
    df = pd.concat(parts, ignore_index=True)
    df.to_parquet(dst, index=False)
    print("rows", len(df), "matches", df.match_id.nunique(), "files", len(files))
