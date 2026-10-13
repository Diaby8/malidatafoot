"""Le calcul du classement FIFA masculin (méthode « SUM », en vigueur depuis août 2018), écrit en clair.

P après = P avant + I × (W − We)
- We = 1 / (10^(−dr/600) + 1), dr = écart de points entre les deux équipes AVANT le match (pas d'avantage du terrain) ;
- W = 1 victoire, 0,5 nul, 0 défaite ; aux tirs au but : 0,75 pour le vainqueur, 0,5 pour le perdant ;
- I selon le match : 5 amical hors fenêtre, 10 amical dans une fenêtre, 15 Ligue des nations (poules), 25 Ligue des nations
  (barrages et phase finale) et éliminatoires (CAN, Coupe du monde), 35 phase finale continentale avant les quarts,
  40 phase finale continentale à partir des quarts, 50 Coupe du monde avant les quarts, 60 Coupe du monde à partir des quarts ;
- en phase à élimination directe d'une phase finale, une défaite ne fait pas perdre de points.
Source : FIFA, « Revision of the FIFA/Coca-Cola World Ranking » (juin 2018).
"""
from __future__ import annotations

IMPORTANCE = {"amical_hors_fenetre": 5, "amical": 10, "ligue_des_nations": 15, "ligue_des_nations_finale": 25,
              "eliminatoires": 25, "phase_finale_poules": 35, "phase_finale_quarts": 40,
              "coupe_du_monde_poules": 50, "coupe_du_monde_quarts": 60}
RESULTAT = {"V": 1.0, "N": 0.5, "D": 0.0, "TAB_V": 0.75, "TAB_D": 0.5}


def attendu(points: float, points_adverse: float) -> float:
    return 1 / (10 ** (-(points - points_adverse) / 600) + 1)


def match(points: float, points_adverse: float, resultat: str, importance: int, elimination_directe: bool = False) -> tuple[float, float]:
    """Renvoie (points après, points de l'adversaire après). Ce que l'un gagne, l'autre le perd, sauf la règle
    « pas de points perdus en élimination directe » qui protège le perdant."""
    w = RESULTAT[resultat]
    d = importance * (w - attendu(points, points_adverse))
    da = -d
    if elimination_directe:
        d, da = max(d, 0.0), max(da, 0.0)
    return points + d, points_adverse + da


def scenarios(points: float, points_adverse: float, importance: int, n_matchs: int = 2) -> list[dict]:
    """Tous les enchaînements de résultats sur n matchs contre le même adversaire (les points des deux équipes bougent
    après chaque match, comme dans le vrai calcul)."""
    sortie = [{"resultats": "", "points": points, "points_adverse": points_adverse}]
    for _ in range(n_matchs):
        sortie = [{"resultats": s["resultats"] + r, **dict(zip(("points", "points_adverse"),
                                                                 match(s["points"], s["points_adverse"], r, importance)))}
                  for s in sortie for r in "VND"]
    for s in sortie:
        s["ecart"] = s["points"] - points
    return sortie


# ---------------------------------------------------------------------------------------------------------------
# Les rangs FIFA publiés, pour savoir où en était chaque adversaire le jour du match (ce que les supporters connaissent).
# Deux compilations publiques du site de la FIFA : Dato-Futbol (1992-2024) et World Football Rankings (2025-2026).
# Trou connu : octobre 2024 à août 2025 ; on prend alors le classement le plus proche et on le marque « approché ».
CODES = {"Ivory Coast": "CIV", "Cape Verde": "CPV", "DR Congo": "COD", "Gambia": "GAM", "Eswatini": "SWZ", "United States": "USA",
         "Guinea-Bissau": "GNB", "Central African Republic": "CTA", "Equatorial Guinea": "EQG", "South Sudan": "SSD", "Congo": "CGO",
         "Mauritania": "MTN", "Comoros": "COM", "Chad": "CHA", "Liberia": "LBR", "Madagascar": "MAD", "Zambia": "ZAM", "Morocco": "MAR",
         "Senegal": "SEN", "Tunisia": "TUN", "Ghana": "GHA", "Mozambique": "MOZ", "Burkina Faso": "BFA", "South Africa": "RSA",
         "Namibia": "NAM", "Uganda": "UGA", "Kenya": "KEN", "Rwanda": "RWA", "Guinea": "GUI", "Mali": "MLI"}


def bronze_rangs(cfg) -> dict:
    """Télécharge les deux compilations (une fois par jour) avec un manifeste, comme les autres sources."""
    import hashlib, json, urllib.request
    from datetime import datetime, timezone
    dossier = cfg.path("bronze") / "classement_fifa"
    dossier.mkdir(parents=True, exist_ok=True)
    chemin = dossier / "_manifest.json"
    man = json.loads(chemin.read_text(encoding="utf-8")) if chemin.exists() else {}
    jour = datetime.now(timezone.utc).date().isoformat()
    for s in cfg.raw["classement_fifa_historique"]["sources"]:
        dest = dossier / s["fichier"]
        if man.get(s["fichier"], {}).get("fetched_at", "")[:10] == jour and dest.exists():
            continue
        with urllib.request.urlopen(s["url"], timeout=60) as r:
            data = r.read()
        dest.write_bytes(data)
        man[s["fichier"]] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "source": s["url"],
                             "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    chemin.write_text(json.dumps(man, indent=1, sort_keys=True), encoding="utf-8")
    return man


def rangs_publies(cfg):
    """Table (code, date, rang) de tous les classements publiés disponibles."""
    import json
    import pandas as pd
    dossier = cfg.path("bronze") / "classement_fifa"
    d = pd.read_csv(dossier / "ranking_fifa_historical.csv", encoding="utf-8").dropna(subset=["total_points"])
    d["date"] = pd.to_datetime(d["date"])
    d["rang"] = d.groupby("date")["total_points"].rank(ascending=False, method="min").astype(int)
    h = json.loads((dossier / "wfr_history.json").read_text(encoding="utf-8"))
    autres = [(c, pd.Timestamp(j), int(rk)) for c, l in h["ranks"].items() for j, rk, _ in l if rk is not None]
    t = pd.concat([d[["team_short", "date", "rang"]].set_axis(["code", "date", "rang"], axis=1),
                   pd.DataFrame(autres, columns=["code", "date", "rang"])], ignore_index=True)
    noms = dict(zip(d["team"], d["team_short"]))
    return t, noms


def rang_le_jour(t, noms, adversaire: str, jour, ecart_max_jours: int = 100):
    """Rang FIFA publié avant le match (le plus récent) ; s'il date de plus de ecart_max_jours, le plus proche, marqué « approché »."""
    import pandas as pd
    code = CODES.get(adversaire, noms.get(adversaire))
    x = t[t.code == code]
    if x.empty:
        return None, None, "absent"
    jour = pd.Timestamp(jour); avant = x[x.date < jour]
    if len(avant) and (jour - avant.date.max()).days <= ecart_max_jours:
        r = avant[avant.date == avant.date.max()].iloc[0]
        return int(r.rang), r.date.date().isoformat(), "exact"
    r = x.loc[(x.date - jour).abs().idxmin()]
    return int(r.rang), r.date.date().isoformat(), "approché"
