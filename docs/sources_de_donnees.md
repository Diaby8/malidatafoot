# Sources de données : état des lieux (7 octobre 2026)

Deux besoins : (A) les Maliens en club cette saison ; (B) les matchs des Aigles (éliminatoires CAN 2027 : Mali, Rwanda, Cap-Vert, Liberia ;
Mali 3-1 Cap-Vert, victoire au Liberia le 29 septembre ; Rwanda en novembre 2026, fin en mars 2027).

| Source | Prix | Ce qu'elle donne | Couvre A (clubs) | Couvre B (Aigles) | Droit de publier | Vérifié |
|---|---|---|---|---|---|---|
| StatsBomb Open Data | gratuit | tout le match, action par action, avec positions et xG | non (Ligue 1 jusqu'en 2022/23) | CAN 2023 seulement | oui, avec leur logo ; pas d'usage commercial | liste des compétitions lue le 7/10/2026 |
| API-Football | 0 $ (100 requêtes/jour, saisons limitées), puis 19, 29 ou 39 $/mois | calendrier, compos, buts, cartons, stats par match et par joueur | oui, toutes compétitions | à tester (script `test_api_football.py`) | conditions à lire | page des prix lue |
| Sportmonks | 29 €/mois pour 5 championnats + option xG (24 à 29 €/mois) | stats par match et joueur, xG par tir | Ligue 1 oui | CAN (phase finale) oui, éliminatoires africaines non pour le xG | conditions à lire | pages prix et couverture xG lues |
| Understat | gratuit | tirs un par un avec xG, depuis 2014/15 | 5 grands championnats + Russie | non | pas de licence affichée ; récupération par script tolérée, pas autorisée par écrit | article de référence 2026 |
| FBref | gratuit | depuis janvier 2026 : stats de base seulement (plus de données Opta) | oui, de base | oui, de base | site de référence, citer la source | annonce officielle du 20/01/2026 |
| Sofascore, FotMob, WhoScored | gratuit à consulter | notes, stats de match, tirs ; WhoScored : flux Opta | très large | Sofascore a une page éliminatoires CAN | FotMob interdit toute extraction automatique et toute réutilisation sans accord écrit ; les autres à vérifier | conditions FotMob lues |
| Hudl Wyscout (licence perso) | environ 299 €/an | vidéo + stats, très large catalogue | oui | probable, à vérifier | à vérifier | article de référence 2026 |
| StatsBomb payant, Opta, SkillCorner | prix club (milliers d'euros/an) | le niveau pro | oui | oui | selon contrat | article de référence 2026 |

Bibliothèques (ce sont des outils, pas des droits) : `soccerdata` (Python : ClubElo, ESPN, FBref, Football-Data.co.uk, Sofascore, SoFIFA, Understat, WhoScored),
`worldfootballR` (R : FBref, Transfermarkt, Understat), `ScraperFC`, `statsbombpy`, `mplsoccer` (terrains, radars).
Leur FAQ rappelle que le statut légal de la récupération automatique est flou et qu'il faut respecter les conditions des sites.

Leçon de l'année : FBref a perdu toutes ses données avancées du jour au lendemain sur un désaccord de licence avec son fournisseur.
Une page pro ne doit pas dépendre d'une source dont elle n'a pas le droit de se servir.

Piste propre à MaliDataFoot pour les matchs des Aigles : relever nous-mêmes les tirs à la vidéo (20 à 30 par match) et leur donner
un xG avec un modèle entraîné sur les tirs de StatsBomb Open Data. Personne n'a ces données pour les éliminatoires africaines.

À faire : lancer `test_api_football.py` (clé dans l'environnement, jamais dans le chat), lire les conditions d'API-Football, vérifier Wyscout.
