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
