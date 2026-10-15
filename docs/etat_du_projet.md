# MaliDataFoot : l'état du projet, en clair (14 octobre 2026)

Ce document remplace la lecture de tout le reste. Si tu ne lis qu'un fichier, c'est celui-là.
Il se met à jour à chaque post publié et à chaque décision.

## 1. Le projet en une phrase

On prend des données de football (matchs, actions, résultats), on les range dans une base, on les analyse avec du code,
et on en tire des visuels et des vidéos qui font comprendre le foot malien : @MaliDataFoot sur X, @malidatafoot sur TikTok.

## 2. Où est quoi

| Dossier | Ce qu'il contient | Tu y touches ? |
|---|---|---|
| `malidata/` | **Le pipeline** : le code qui télécharge, nettoie, calcule (un fichier par étape) | non |
| `sql/` | Les calculs d'indicateurs, écrits en SQL (stats par joueur, par match, tirs) | non |
| `data/` | **La base de données** (`warehouse.duckdb`) et les fichiers bruts téléchargés | non |
| `registre/` | Nos fichiers tenus à la main : joueurs maliens (56), calendrier du groupe K, classement FIFA | oui, quand un club change |
| `tests/` | Les 34 contrôles automatiques : si un seul est rouge, on ne publie rien | non |
| `visuels/` | Les gabarits des images et vidéos (fiche joueur, duel, posts, vidéo de lancement), logos, photos | non |
| `poc/` | Les essais : analyses et maquettes pas encore rangées dans le pipeline | non |
| `livrables/` | Les images et vidéos finies, prêtes à poster | oui, c'est là que tu prends les fichiers |
| `docs/` | Ce document, les sources, les idées, le journal des décisions | oui, pour relire |
| `.claude/skills/` | Les règles du projet que je dois suivre (DA, données, production) | non |

## 3. La base de données (ce qu'on a vraiment)

Tout est dans un seul fichier, `data/warehouse.duckdb`, qu'on interroge en SQL.

| Ce qu'il y a | Combien | D'où ça vient | Ce que ça permet |
|---|---|---|---|
| Chaque action de la CAN 2023 (passes, tirs, duels…), avec la position sur le terrain | 52 matchs, 162 903 actions | StatsBomb Open Data (gratuit, logo obligatoire) | fiches joueurs, cartes de tirs, réseaux de passes, rayons X d'une action |
| Les compos de départ de la CAN 2023 | 1 144 lignes | StatsBomb | onze type de Chelle (période CAN) |
| Tous les matchs internationaux depuis 1872 (tapis verts listés dans `registre/forfaits.csv`, comptés au score officiel) | 49 945 matchs, dont 572 du Mali | martj42 (GitHub, domaine public, mis à jour en continu) | historique, bilans par année, séries |
| Notre classement Elo de toutes les sélections | 337 équipes | calculé par nous à partir des 49 945 matchs | force des adversaires, « à adversaires égaux » |
| Le classement FIFA | historique + octobre 2026 | fichiers FIFA + `registre/classement_fifa.csv` | rang affiché aux supporters (jamais notre Elo) |
| Notre modèle de menace (xT) | 1 grille de 192 cases | appris sur 2 564 matchs StatsBomb | « +0,25 de menace », menace créée et concédée |
| Notre simulation du groupe K | 100 000 tirages | notre modèle de scores | « On a joué le groupe 100 000 fois » |
| Les profils par poste | 233 joueurs de la CAN 2023 | calculés par nous | les fiches joueurs |

**Ce qui manque**
- **Les compos des Aigles hors CAN 2023** (pour le onze type par coach) : 29 matchs. **Tu copies les pages, je saisis** dans un fichier avec la source de chaque ligne, et je recoupe.
- **La saison en cours des Maliens en club** : pas encore de source branchée (Understat pour le top 5, à brancher).

## 4. Le pipeline expliqué simplement

Une commande, `python taches.py donnees`, fait tout dans l'ordre :

1. **Télécharger** les fichiers bruts (StatsBomb, martj42, FIFA). On ne les modifie jamais.
2. **Nettoyer** : remettre les actions en tableau, recalculer le temps de jeu de chaque joueur.
3. **Calculer** : stats par joueur et par match (SQL), Elo, analyses, simulation, profils par poste.
4. **Contrôler** : 11 contrôles qualité (les buts recomptés collent-ils au score officiel ? les minutes ?). Le pipeline s'arrête à la première erreur.
5. **Sortir** les résultats pour les visuels (`outputs/`).

Puis `python taches.py tests` : 34 contrôles, tous verts aujourd'hui.

**À ranger** (calculs faits dans `poc/`, pas encore dans le pipeline) : le modèle de menace (xT), les données de la vidéo explicative,
les analyses de jeu des sujets 14 à 18, la malédiction à la CAN. Je les ramène dans le pipeline, avec des tests, au fil des posts qui les utilisent.

## 5. Les sources, une fois pour toutes

| Statut | Sources |
|---|---|
| **On s'en sert** | StatsBomb Open Data, martj42, classement FIFA, nos modèles (Elo, xT, simulation), notre registre |
| **Tu copies les pages, je saisis et je recoupe** | FotMob, Transfermarkt, Wikipédia, FEMAFOOT, presse (décision de Diaby du 14/10/2026 : pas d'aspiration automatique) |
| **À brancher** | Understat (xG des Maliens du top 5, saison en cours) |
| **Écarté pour l'instant** | toute source payante tant qu'on n'a pas vérifié qu'elle couvre nos matchs (API-Football, Sportmonks, Wyscout) |

Détail et historique : `docs/sources_de_donnees.md`.

## 6. Le workflow d'un post (toujours le même)

1. **Relire** ce document et la liste des contenus : ne pas refaire, ne pas se contredire.
2. **Calculer** dans le pipeline, sur les vraies données.
3. **Planche numérotée** des visuels (en DA : jaune, vert ou panneau blanc).
4. **Tu choisis.**
5. **Audit** : chaque chiffre recompté, la phrase ne dit pas plus que le chiffre, visuel vérifié en taille téléphone.
6. **Publication** : thread X + TikTok (carrousel, ou vidéo si le mouvement apporte quelque chose). Une ligne dans le journal.

## 7. Les contenus

**Publiés** : la vidéo de lancement (TikTok et X, 13/10/2026), la bannière X.

**Les 4 premiers posts (choisis le 14/10/2026), dans cet ordre**

| # | Post | Format | État | Ce qu'il reste |
|---|---|---|---|---|
| 1 | La défense des Aigles depuis 2020 | thread X (6 tweets) + carrousel TikTok (2 images) | fini le 15/10 (livrables/post1-defense), posté par Diaby | — |
| 2 | Le compte expliqué : « Namibie-Mali aux rayons X » | vidéo TikTok 51 s + version X | prêt le 15/10 (livrables/video-explique/v3e-voix.mp4 + description-TikTok.txt), à poster par Diaby ; sons gardés tels quels | ranger les calculs dans le pipeline |
| 3 | On a joué le groupe 100 000 fois | vidéo ou carrousel + thread | POC | à sortir avant les matchs contre le Rwanda (novembre) ; visuels à refaire au niveau de la vidéo explicative |
| 4 | Le onze type de chaque coach (Chelle, Saintfiet, Da Silva) | carrousel + thread | données en cours | 29 compos à copier (liste dans `poc/onze_type/`) |

**En réserve** (idées et POC à reprendre plus tard, sans les ressortir tels quels) : voir `docs/boite_a_idees.md`.
Constat honnête du 14/10/2026 : beaucoup de ces idées sont des stats sans vraie profondeur. On ne les publie pas en l'état.

## 8. Ménage à faire

- `visuels/` contient 274 fichiers de rendu temporaires (`_*.html`) : à supprimer.
- Les textes des posts sont dans deux endroits (`poc/textes.md` et `livrables/vrais/`) : à regrouper par post dans `livrables/<post>/`.
