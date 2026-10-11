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

## Test API-Football du 11 octobre 2026 (compte gratuit, 35 appels)

- **Couverture des championnats** : bonne. Ligue 1, Ligue 2, Premier League, Serie A, Liga, Bundesliga, Eredivisie et Süper Lig existent, avec les saisons 2024, 2025 et 2026 (en cours). La CAN existe (édition 2025). L'API connaît un championnat du Mali.
- **Joueurs** : les 8 joueurs témoins sont retrouvés, 7 avec la même date de naissance que notre registre (Alimami Gory reste à vérifier).
- **Blocage** : l'offre gratuite ne donne les stats que pour les saisons 2022 à 2024. Les saisons 2025 et 2026 sont refusées (« Free plans do not have access to this season »). Le test du détail d'un match (partie 4) n'a rien renvoyé pour la même raison.
- **Conclusion** : le compte gratuit ne sert à rien pour la saison en cours. Il faut une offre payante (à vérifier sur leur page de tarifs) ou une autre source. Décision à prendre par Diaby.

## Recherche du 11 octobre 2026 : toutes les sources possibles pour la saison en cours

| Source | Ce qu'on obtient | Prix | Droit de s'en servir | Verdict |
|---|---|---|---|---|
| StatsBomb Open Data | Événements complets : CAN 2023, Euro 2024, Copa América 2024, Ligue 1 2021-23, Bundesliga 2023-24… Pas la saison en cours | Gratuit | Oui, en citant Hudl StatsBomb, sans usage commercial | Garder : rétro et entraînement du modèle xG |
| Understat | xG de chaque tir, top 5 européen + Russie, saison en cours (Sinayoko au Paris FC) | Gratuit | Pas d'interdiction trouvée ; à relire (robots.txt) avant de brancher ; débit très lent | À brancher en premier |
| FBref | Stats de base (minutes, buts, passes déc.) ; plus de stats avancées depuis le 20 janvier 2026 | Gratuit | Robots limités à 10 requêtes/minute, sinon blocage d'un jour ; pas de téléchargement autorisé par leurs accords | Vérification ponctuelle seulement |
| API-Football Pro | Tous les championnats (y compris Golfe, Russie, Afrique, éliminatoires), stats par joueur et par match, saison en cours | 19 $/mois, 7 500 requêtes/jour | Oui, c'est une API faite pour ça | Meilleur rapport couverture/prix |
| Sportmonks Starter | 5 championnats au choix ; xG en option | 29 €/mois + 29 €/mois pour le xG | Oui | Plus cher pour moins de championnats |
| FotMob | — | — | Interdit noir sur blanc (« Data Usage & Scraping ») | Non |
| Sofascore | — | — | Pas d'API, données sous accords fournisseurs | Non |
| WhoScored | Données Opta | — | Données sous licence | Non |
| Transfermarkt | Transferts, contrats, valeurs (pas de stats de jeu) | — | Conditions non lues | Non tant qu'on ne les a pas lues |
| Fait maison | Tirs des Aigles relevés à la vidéo (FIFA+, YouTube) + notre modèle xG | Gratuit | Oui (nos propres données) | À construire : personne d'autre ne l'a |

Proposition : Understat (gratuit) pour le xG des Maliens du top 5, plus un mois d'API-Football Pro pour juger la richesse des stats par match sur la saison en cours. Décision à Diaby.
