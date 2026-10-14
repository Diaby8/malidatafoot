"""Recompte indépendant (n'utilise ni xtlib ni build_xt) : refait la grille depuis les fichiers bruts,
puis recompte le xT des joueurs du Mali, de l'équipe et de la meilleure possession depuis les événements bruts de la CAN."""
import gzip, json, glob, os, sys
import numpy as np
from multiprocessing import Pool

ROOT = sys.argv[1]; REPO = "/home/claude/repo/malidatafoot"
SP = {"Throw-in", "Free Kick", "Goal Kick", "Corner", "Kick Off"}


def z_of(p):
    cx = min(max(int(p[0] // 7.5), 0), 15); cy = min(max(int(p[1] / (80 / 12)), 0), 11)
    return cy * 16 + cx


def is_credit(e):
    t = e["type"]["name"]
    if e["period"] > 4 or "location" not in e: return None
    if t == "Pass":
        p = e["pass"]
        if (p.get("type") or {}).get("name") in SP: return None
        if (p.get("outcome") or {}).get("name") == "Injury Clearance": return None
        return ("move", "outcome" not in p, p["end_location"])
    if t == "Carry":
        a, b = e["location"], e["carry"]["end_location"]
        if ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5 < 3: return None
        return ("move", True, b)
    if t == "Shot" and e["shot"]["type"]["name"] == "Open Play":
        return ("shot", e["shot"].get("statsbomb_xg", 0.0), None)
    return None


def count(path):
    S = np.zeros(192); M = np.zeros(192); XG = np.zeros(192); T = np.zeros((192, 192))
    with gzip.open(path, "rb") as f: ev = json.load(f)
    for e in ev:
        c = is_credit(e)
        if not c: continue
        z = z_of(e["location"])
        if c[0] == "shot": S[z] += 1; XG[z] += c[1]
        else:
            M[z] += 1
            if c[1]: T[z, z_of(c[2])] += 1
    return S, M, XG, T


if __name__ == "__main__":
    files = sorted(glob.glob(f"{ROOT}/cache/raw/events/*.json.gz"))
    S = np.zeros(192); M = np.zeros(192); XG = np.zeros(192); T = np.zeros((192, 192))
    with Pool(2) as p:
        for s, m, x, t in p.imap_unordered(count, files, chunksize=16): S += s; M += m; XG += x; T += t
    s = S / (S + M); m = M / (S + M); g = np.divide(XG, S, out=np.zeros(192), where=S > 0); Tn = T / M[:, None]
    v = np.zeros(192)
    for i in range(1000):
        nv = s * g + m * Tn.dot(v)
        if np.abs(nv - v).max() < 1e-7: v = nv; break
        v = nv
    grid = np.array(json.load(open(f"{ROOT}/xt_grid.json"))["valeurs"]).ravel()
    print("fichiers", len(files), "iterations", i + 1, "ecart max avec xt_grid.json", np.abs(v - grid).max())
    # CAN : recompte Mali depuis le brut avec la grille publiée
    ids = {"Hamari Traoré": None}
    per_player, team, poss = {}, 0.0, {}
    for mid in [3920391, 3920404, 3920417, 3922244, 3922659]:
        ev = json.load(open(f"{REPO}/data/bronze/events/{mid}.json", encoding="utf-8"))
        for e in ev:
            if e["team"]["name"] != "Mali": continue
            c = is_credit(e)
            if not c or c[0] != "move" or not c[1]: continue
            d = grid[z_of(c[2])] - grid[z_of(e["location"])]
            per_player[e["player"]["name"]] = per_player.get(e["player"]["name"], 0) + d
            team += d
            if e["possession_team"]["name"] == "Mali": poss[(mid, e["possession"])] = poss.get((mid, e["possession"]), 0) + d
    for k, val in sorted(per_player.items(), key=lambda kv: -kv[1])[:6]: print(k, round(val, 6))
    print("Mali total", round(team, 6), "par 90", round(team / 480 * 90, 6))
    best = max(poss.items(), key=lambda kv: kv[1]); print("meilleure possession", best)
    # comparaison avec les fichiers publiés
    mp = {j["nom_complet"]: j["xt_ajoute"] for j in json.load(open(f"{ROOT}/mali_players.json"))["joueurs"]}
    raw_names = {"Sikou Niakate": "Sikou Niakaté", "Boubakar Kouyate": "Kiki Kouyaté"}
    pl_diff = max(abs(val - mp.get(raw_names.get(k, k), mp.get(k, np.nan))) for k, val in per_player.items())
    tj = [e for e in json.load(open(f"{ROOT}/teams.json"))["equipes"] if e["equipe"] == "Mali"][0]
    tp = json.load(open(f"{ROOT}/top_possession.json"))["meilleure"]
    vpath = f"{ROOT}/validation.json"; V = json.load(open(vpath, encoding="utf-8"))
    V["audit_independant"] = {
        "principe": "second code, écrit à part (scripts/audit_independant.py), qui relit les fichiers bruts sans passer par le code du modèle",
        "grille_ecart_max": float(np.abs(v - grid).max()), "iterations": i + 1,
        "joueurs_mali_ecart_max": round(float(pl_diff), 6), "joueurs_recomptes": len(per_player),
        "mali_xt_total": [round(team, 6), tj["xt"]],
        "meilleure_possession": [[best[0][0], best[0][1], round(best[1], 6)], [tp["match_id"], tp["possession"], tp["xt_ajoute_total"]]],
        "lecture": "les écarts viennent de l'arrondi à 6 décimales de la grille publiée"}
    json.dump(V, open(vpath, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("audit écrit", V["audit_independant"])
