#!/usr/bin/env python3
"""Test de la source API-Football pour MaliDataFoot.

But : savoir, avec le compte gratuit, ce qu'on obtient VRAIMENT pour les joueurs du registre :
quelles saisons, quels championnats, quelles stats par joueur et par match.

Utilisation (aucune installation, Python 3.9+ suffit) :
    Mac / Linux :  export API_FOOTBALL_KEY="ta_clé"  &&  python3 test_api_football.py
    Windows (PowerShell, terminal de VS Code) :  $env:API_FOOTBALL_KEY="ta_clé"  puis  python outils/test_api_football.py
    Windows (invite cmd) :  set API_FOOTBALL_KEY=ta_clé  puis  python outils\test_api_football.py

Mets joueurs.csv dans le même dossier que ce script.
Le script fait environ 35 appels (le compte gratuit en autorise 100 par jour), attend entre
deux appels pour respecter la limite par minute, n'affiche jamais la clé, et écrit
rapport_api_football.json à côté de lui. C'est ce fichier qu'il faut renvoyer.
"""
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

BASE = os.environ.get("API_FOOTBALL_BASE", "https://v3.football.api-sports.io")   # la variable ne sert qu'aux essais
ICI = Path(__file__).resolve().parent
REGISTRE = (ICI / "joueurs.csv") if (ICI / "joueurs.csv").exists() else ICI.parent / "registre" / "joueurs.csv"   # à côté du script, ou dans le projet
RAPPORT = ICI / "rapport_api_football.json"
PAUSE = float(os.environ.get("API_FOOTBALL_PAUSE", "7"))   # secondes entre deux appels (limite gratuite : 10 par minute)
MAX_APPELS = 45      # garde-fou : on ne brûle pas le quota de la journée
SAISONS = [2026, 2025, 2024]   # 2026 = saison 2026-27 en cours

# Championnats à vérifier. Les numéros viennent de la doc API-Football ; le rapport affiche le nom
# renvoyé par l'API, donc une erreur de numéro se verra tout de suite.
CHAMPIONNATS = {61: "Ligue 1", 62: "Ligue 2", 39: "Premier League", 135: "Serie A", 140: "La Liga",
                78: "Bundesliga", 88: "Eredivisie", 203: "Süper Lig", 6: "Coupe d'Afrique des Nations"}

# Joueurs témoins : un par situation (grand championnat, Ligue 2, Afrique, Golfe, Russie).
TEMOINS = ["Lassine Sinayoko", "Kamory Doumbia", "Nene Dorgeles", "Mamadou Sangaré",
           "Djigui Diarra", "Issa Djiguiba", "Alimami Gory", "Nathan Gassama"]

appels = 0


def appel(chemin, **params):
    """Un appel GET. Renvoie le JSON complet, ou {'erreur_http': ...} si ça casse."""
    global appels
    if appels >= MAX_APPELS:
        return {"erreur_http": "garde-fou atteint, appel non fait", "response": [], "errors": []}
    if appels:
        time.sleep(PAUSE)
    appels += 1
    url = f"{BASE}/{chemin}"
    if params:
        url += "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"x-apisports-key": CLE})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        data = {"erreur_http": f"HTTP {e.code}", "response": [], "errors": []}
    except Exception as e:  # réseau, délai, JSON illisible
        data = {"erreur_http": f"{type(e).__name__}: {e}", "response": [], "errors": []}
    err = data.get("errors") or data.get("erreur_http")
    print(f"  [{appels:02d}] {chemin} {params or ''} -> {data.get('results', '?')} résultat(s)" + (f"  ERREUR : {err}" if err else ""))
    return data


def erreurs(d):
    e = d.get("errors")
    return d.get("erreur_http") or (e if e else None)


def lire_registre():
    with open(REGISTRE, encoding="utf-8") as f:
        return {r["nom"]: r for r in csv.DictReader(f)}


def sans_accent(s):
    import unicodedata
    return unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode().lower()


def main():
    rapport = {"date": time.strftime("%Y-%m-%d %H:%M"), "saisons_testees": SAISONS}

    print("1. Compte")
    d = appel("status")
    rep = d.get("response") or {}
    rep = rep[0] if isinstance(rep, list) and rep else rep
    rapport["compte"] = {"offre": (rep.get("subscription") or {}).get("plan"), "quota": rep.get("requests"), "erreurs": erreurs(d)}
    if not rapport["compte"]["offre"]:
        print("\nLa clé n'est pas reconnue. Vérifie qu'elle est bien copiée, puis relance.")
        RAPPORT.write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")
        return

    print("2. Championnats : quelles saisons, quel niveau de détail")
    rapport["championnats"] = []
    for num, attendu in CHAMPIONNATS.items():
        d = appel("leagues", id=num)
        r = (d.get("response") or [{}])[0]
        rapport["championnats"].append({"numero": num, "attendu": attendu, "nom_api": (r.get("league") or {}).get("name"),
                                        "pays": (r.get("country") or {}).get("name"), "erreurs": erreurs(d),
                                        "saisons": [{"annee": s.get("year"), "en_cours": s.get("current"), "detail": s.get("coverage")}
                                                    for s in (r.get("seasons") or []) if s.get("year") in SAISONS]})
    d = appel("leagues", country="Mali")
    rapport["championnats_mali"] = {"erreurs": erreurs(d), "liste": [{"numero": (x.get("league") or {}).get("id"), "nom": (x.get("league") or {}).get("name"),
                                                                     "saisons": [s.get("year") for s in (x.get("seasons") or [])][-4:]} for x in (d.get("response") or [])]}

    print("3. Joueurs témoins : les retrouve-t-on, et avec quelles stats")
    reg = lire_registre()
    rapport["joueurs"] = []
    match_a_tester = None
    for nom in TEMOINS:
        fiche = reg.get(nom, {})
        cherche = sans_accent(nom.split()[-1])
        d = appel("players/profiles", search=cherche)
        cands = [(x.get("player") or {}) for x in (d.get("response") or [])]
        bons = [p for p in cands if (p.get("nationality") == "Mali") or (fiche.get("date_naissance") and (p.get("birth") or {}).get("date") == fiche["date_naissance"])]
        exact = [p for p in bons if fiche.get("date_naissance") and (p.get("birth") or {}).get("date") == fiche["date_naissance"]]
        choisi = (exact or bons or [None])[0]
        ligne = {"nom": nom, "recherche": cherche, "erreurs": erreurs(d), "candidats": len(cands),
                 "trouve": bool(choisi), "sur": bool(exact), "id": (choisi or {}).get("id"), "nom_api": (choisi or {}).get("name"),
                 "naissance_api": ((choisi or {}).get("birth") or {}).get("date"), "saisons": []}
        if choisi:
            for an in SAISONS[:2]:
                s = appel("players", id=choisi["id"], season=an)
                stats = ((s.get("response") or [{}])[0].get("statistics")) or []
                ligne["saisons"].append({"annee": an, "erreurs": erreurs(s),
                                         "lignes": [{"equipe": (t.get("team") or {}).get("name"), "equipe_id": (t.get("team") or {}).get("id"),
                                                     "competition": (t.get("league") or {}).get("name"),
                                                     "matchs": (t.get("games") or {}).get("appearences"), "minutes": (t.get("games") or {}).get("minutes"),
                                                     "note": (t.get("games") or {}).get("rating"), "buts": (t.get("goals") or {}).get("total"),
                                                     "passes_dec": (t.get("goals") or {}).get("assists"), "tirs": (t.get("shots") or {}).get("total"),
                                                     "passes_cles": (t.get("passes") or {}).get("key"), "duels": (t.get("duels") or {}).get("total"),
                                                     "rubriques_presentes": sorted(k for k, v in t.items() if isinstance(v, dict) and any(x is not None for x in v.values()))}
                                                    for t in stats]})
                if match_a_tester is None and not erreurs(s):
                    for t in stats:
                        if (t.get("games") or {}).get("minutes") and (t.get("team") or {}).get("id"):
                            match_a_tester = {"equipe_id": t["team"]["id"], "equipe": t["team"].get("name"), "saison": an, "joueur": nom}
                            break
        rapport["joueurs"].append(ligne)

    print("4. Un match au détail : stats d'équipe et stats de chaque joueur")
    rapport["match"] = {"cible": match_a_tester}
    if match_a_tester:
        d = appel("fixtures", team=match_a_tester["equipe_id"], season=match_a_tester["saison"])
        finis = [x for x in (d.get("response") or []) if ((x.get("fixture") or {}).get("status") or {}).get("short") in ("FT", "AET", "PEN")]
        finis.sort(key=lambda x: (x.get("fixture") or {}).get("date") or "")
        rapport["match"]["matchs_listes"] = len(d.get("response") or [])
        rapport["match"]["erreurs_liste"] = erreurs(d)
        if finis:
            m = finis[-1]
            fid = m["fixture"]["id"]
            rapport["match"]["choisi"] = {"id": fid, "date": m["fixture"].get("date"), "affiche": f"{m['teams']['home']['name']} - {m['teams']['away']['name']}",
                                          "competition": (m.get("league") or {}).get("name")}
            s = appel("fixtures/statistics", fixture=fid)
            rapport["match"]["stats_equipe"] = {"erreurs": erreurs(s), "types": sorted({st.get("type") for eq in (s.get("response") or []) for st in (eq.get("statistics") or []) if st.get("value") is not None})}
            p = appel("fixtures/players", fixture=fid)
            joueurs = [j for eq in (p.get("response") or []) for j in (eq.get("players") or [])]
            ex = (joueurs[0].get("statistics") or [{}])[0] if joueurs else {}
            rapport["match"]["stats_joueurs"] = {"erreurs": erreurs(p), "joueurs": len(joueurs),
                                                 "rubriques": {k: sorted(v.keys()) for k, v in ex.items() if isinstance(v, dict)}}
            e = appel("fixtures/events", fixture=fid)
            rapport["match"]["evenements"] = {"erreurs": erreurs(e), "nombre": len(e.get("response") or []),
                                              "types": sorted({x.get("type") for x in (e.get("response") or []) if x.get("type")})}

    rapport["appels_faits"] = appels
    RAPPORT.write_text(json.dumps(rapport, ensure_ascii=False, indent=1), encoding="utf-8")

    print("\n===== RÉSUMÉ =====")
    c = rapport["compte"]
    print(f"Offre : {c['offre']} | quota : {c['quota']}")
    for ch in rapport["championnats"]:
        ans = ", ".join(f"{s['annee']}{' (en cours)' if s['en_cours'] else ''}" for s in ch["saisons"]) or "aucune des saisons testées"
        print(f"  {ch['attendu']:<28} vu par l'API comme « {ch['nom_api']} » : {ans}")
    print(f"  Championnats du Mali connus de l'API : {len(rapport['championnats_mali']['liste'])}")
    for j in rapport["joueurs"]:
        etat = "introuvable" if not j["trouve"] else ("trouvé (date de naissance identique)" if j["sur"] else "trouvé (à vérifier)")
        det = " ; ".join(f"{s['annee']} : " + (f"REFUSÉ ({s['erreurs']})" if s["erreurs"] else f"{sum((l['minutes'] or 0) for l in s['lignes'])} min") for s in j["saisons"])
        print(f"  {j['nom']:<18} {etat}  {det}")
    m = rapport["match"]
    if m.get("choisi"):
        print(f"  Match testé : {m['choisi']['affiche']} ({m['choisi']['date'][:10]}) | stats d'équipe : {len(m['stats_equipe']['types'])} types | joueurs détaillés : {m['stats_joueurs']['joueurs']}")
    print(f"\n{appels} appels faits. Rapport écrit : {RAPPORT}")
    print("Renvoie-moi ce fichier rapport_api_football.json.")


if __name__ == "__main__":
    CLE = os.environ.get("API_FOOTBALL_KEY", "").strip()
    if not CLE:
        sys.exit("Il manque la clé. Mets-la dans la variable API_FOOTBALL_KEY puis relance (voir en haut du fichier).")
    main()
