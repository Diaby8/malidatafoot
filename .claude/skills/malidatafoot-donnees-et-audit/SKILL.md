---
name: malidatafoot-donnees-et-audit
description: Règles de fond de MaliDataFoot : sources de données, pipeline, définitions des indicateurs et audit des chiffres. À lire avant toute analyse, tout chiffre publié ou tout ajout de source.
---

# MaliDataFoot : données, chiffres et audit (le fond)

**Règle d'or : uniquement des faits vérifiés.** Une page data se juge sur sa crédibilité. Un chiffre faux publié coûte plus
cher que dix posts réussis. Il faut être strict, vouloir réussir, et donc vérifier plus que ce qui paraît nécessaire.

**Relire avant de proposer (Diaby, 14 octobre 2026 : « faut pas jeter des trucs comme ça en pâture, c'est un projet pro »).**
À chaque nouvelle idée de visuel, de data visualisation ou de sujet, et avant toute proposition de source, relire d'abord :
- `docs/sources_de_donnees.md` : quelles sources on a déjà trouvées, testées, autorisées ou écartées (ex. martj42 = scores sans compos ; API-Football gratuit = 2022-2024 seulement ; FotMob = accord écrit à archiver) ;
- `docs/boite_a_idees.md` et `docs/banque_idees.md` : ce qui est déjà fait, en cours ou rejeté ;
- `docs/journal_des_gabarits.md` : les décisions de forme et de fond déjà prises ;
- les sections utiles des trois skills (DA, données, production).
Puis proposer en s'appuyant dessus : dire ce qu'on a déjà, ce qui manque, et d'où viendrait le manque, vérifié. Ne jamais proposer une solution (surtout payante) qu'on n'a pas vérifiée.

## 1. Avant de publier un chiffre

1. **Le recompter** depuis les fichiers bruts (pas depuis un résumé, pas de mémoire).
2. **Le recouper** avec une source externe s'il surprend : score officiel, minutes, buts.
3. **Pour un visuel important**, le faire recompter par un contrôle indépendant qui n'a pas vu le code de calcul. Le recomptage du 7 octobre a trouvé un rang faux (12e au lieu de 11e) que tout le reste avait laissé passer.
4. **Pour tout ce qui décrit le présent** (club actuel, buts de la saison, sélection, calendrier des Aigles), revérifier sur le web à la date du post et citer la source. Aucune anecdote inventée.

## 2. Les quatre angles de l'audit (aussi sévère que Diaby)

1. **Données.** Chaque chiffre affiché est recompté.
2. **Logique.** Volume ou réussite ? Rang ou vraie valeur ? Poids d'un penalty, sens d'une passe ? Le titre ou la phrase ne doit pas faire dire au chiffre plus qu'il ne dit. On n'écrit pas une conclusion qui dépend d'un seuil choisi par nous : « aucune passe vers l'avant » était faux sans notre seuil de 10 yards.
3. **Sémantique.** Les mots, les unités, les définitions. Les termes sont en français : buts attendus, passes décisives attendues, conduites progressives, possession.
4. **Visuel.** Voir le skill `malidatafoot-direction-artistique`.

**Pièges déjà rencontrés** :
- **« Top 60 » doit vouloir dire top 60 FIFA** (13 octobre 2026). Notre rang Elo classe aussi des sélections non membres de la FIFA et ne colle pas au rang FIFA : l'Afrique du Sud était 86e chez nous mais 66e FIFA avant la CAN 2023, la Côte d'Ivoire 72e contre 49e. Diaby l'a relevé (« l'Afrique du Sud, c'est du top »). Quand on parle de niveau ou de rang à des supporters, c'est le rang FIFA du dernier classement avant le match (`fifa.rang_le_jour`) ; l'Elo sert seulement au calcul « à adversaires égaux ».
- **Une médiane peut cacher une moyenne qui bouge** : le rang Elo médian des adversaires était stable (122e, 125e) mais leur Elo moyen a baissé (1565 → 1522) et le rang FIFA médian aussi (91e → 106e). Vérifier plusieurs mesures avant d'écrire « même niveau ».
- un arrondi machine qui change un rang (59,999… contre 60,0) ;
- des tirs colorés différemment sans légende ;
- une étiquette plus près de la pastille d'un autre joueur ;
- des minutes en temps réel au lieu du chrono du match ;
- des « ballons reçus » qui comptaient les ballons ratés ;
- un bassin de poste qui mélangeait les rôles.

## 3. Le pipeline (`malidata/`)

Les étapes : bronze (JSON bruts, jamais modifiés) → silver (DuckDB / Parquet) → gold (modèles SQL dans `sql/`) → profils →
contrôles qualité → export (`outputs/`). L'entrepôt est `data/warehouse.duckdb`. Les commandes sont `python taches.py donnees`
puis `python taches.py tests`. Le pipeline s'arrête au premier contrôle en échec. On ne publie rien tant qu'un test est
rouge.

**Règles de calcul (testées)**

- **Minutes** : au chrono du match (un match = 90 ou 120). `minutes_reelles` garde le temps réel à part.
- **Ballons reçus dans la surface** : seulement les ballons vraiment reçus.
- **Poste** : un joueur n'entre dans un poste que s'il y fait au moins 50 % de ses actions (`PART_MIN`) et qu'il a joué au moins 180 minutes. Résultat : 49 latéraux, 22 avants-centres.
- **Centile** : la part des autres joueurs du bassin strictement dépassés.
- **Note** : la moyenne des centiles sur les critères du poste (`config.yaml`, `roles`), arrondie à 6 décimales avant le classement. Des ex aequo ont le même rang.
- **Affichage** : arrondi « comme à l'école » (`da.fr` : 2,25 donne 2,3). Les fiches gardent 4 décimales.
- **Stabilité de la note.** Sur un tournoi de 5 matchs, la note est surtout du bruit hors latéraux (corrélation de rang entre deux moitiés : latéraux 0,40, avants-centres −0,10). On la présente donc comme « son tournoi », sans décimale. Le classement reste rangé jusqu'à disposer d'une saison complète.
- **Seuils** : ils sont écrits en bas des visuels (180 minutes, nombre de joueurs du poste).

**Ajouter une source** : un module d'ingestion dépose ses fichiers bruts dans `data/bronze/<source>/`, avec un manifeste (taille, empreinte, date). Une fonction les ramène au schéma silver. Ensuite viennent les contrôles. Les modèles gold ne changent pas.

## 4. Sources (état au 7 octobre 2026, détail dans `docs/sources_de_donnees.md`)

- **Toujours chercher les meilleures sources** (Diaby, 14 octobre 2026) : refaire régulièrement le tour des sources (open data sur GitHub, API, accords avec les sites, licences), regarder d'où viennent les données des grosses pages, et proposer à Diaby les sources qui débloquent de nouveaux sujets. Le statut de chaque source (autorisée, à confirmer, interdite) est dans `docs/sources_de_donnees.md` ; une source ne passe « autorisée » qu'avec une trace écrite (mail, conditions lues), archivée dans le dépôt.
- **StatsBomb Open Data.** C'est la seule source gratuite d'événements récents pour l'Afrique : la CAN 2023 (et la Ligue 1 jusqu'en 2022/23). Leur logo est obligatoire et l'exploitation commerciale est interdite (clause 1.2.2).
- **API-Football.** Gratuit à 100 requêtes par jour, puis 19, 29 ou 39 $ par mois. La clé reste dans la variable d'environnement `API_FOOTBALL_KEY`, jamais dans la conversation ni dans un fichier suivi par git. Diaby lance lui-même `outils/test_api_football.py` et transmet `rapport_api_football.json`.
- **Sportmonks.** Environ 29 € par mois pour 5 championnats, plus une option xG à 24–29 € (Ligue 1 et phases finales de la CAN, pas les éliminatoires).
- **Understat.** Gratuit : top 5 + Russie, avec le xG de chaque tir.
- **martj42/international_results** (GitHub, CC0) : tous les matchs internationaux depuis 1872, dont 572 du Mali, à jour (octobre 2026). **Branché dans le pipeline** (étape `aigles`, tables `gold.aigles_matchs` et `gold.aigles_bilan_annuel`), recoupé avec StatsBomb. Buteurs incomplets : recouper avec RSSSF.
- **RSSSF** : archives des sélections (capes, buteurs), copie libre en citant l'auteur.
- **Opta** : objectif d'obtenir un accès légal (par FotMob, ou une licence Stats Perform) ; voir `docs/feuille_de_route.md`. Opta est derrière presque tout le grand public (FotMob, WhoScored, Flashscore…) : on ne prend jamais ces données sans accord écrit. Cartographie complète dans `docs/sources_de_donnees.md`.
- **FBref.** A perdu les données avancées Opta le 20 janvier 2026.
- **FotMob.** Interdit l'extraction automatique : ne pas l'utiliser.
- **Wyscout.** Environ 299 € par an en licence personnelle.

**Scraping et collecte automatique** : ils sont prévus, mais seulement sur des sources dont les conditions le permettent. Il
faut lire les conditions d'utilisation et noter la décision dans `docs/sources_de_donnees.md`, respecter les limites de
débit, mettre en cache, et ne jamais dépendre d'une source dont on n'a pas le droit de se servir (leçon FBref).

**Piste propre à la page** : relever nous-mêmes les tirs des Aigles à la vidéo, et leur donner un xG avec un modèle entraîné sur les tirs StatsBomb ouverts.

**Bibliothèques possibles** : soccerdata, worldfootballR, ScraperFC, statsbombpy, mplsoccer.

**Règle (Diaby, 14 octobre 2026) : jamais proposer une source payante sans preuve.** Avant de suggérer de payer quoi que ce soit, vérifier sur un échantillon de nos propres matchs (ex. 5 matchs du Mali, dont éliminatoires et amicaux) que la source les couvre, avec des données justes (comparées à une autre source) et mises à jour après chaque match, et savoir d'où viennent ses données. Toujours épuiser d'abord les sources gratuites (FotMob, FBref, Transfermarkt, Wikipédia, FEMAFOOT), copiées à la main par Diaby si besoin.

## 5. Chiffres de référence (CAN 2023, après audit)

- **Mali** : 64 tirs, 5 buts + 1 contre son camp.
- **Hamari Traoré** : 480 minutes, note 60, 11e sur 49 latéraux (ex aequo).
- **Sinayoko** : 398 minutes, 3 buts sur 9 tirs, 1,53 but attendu.
- **Osimhen** : 646 minutes, 1 but sur 24 tirs.
- **Mali 1-2 Côte d'Ivoire** :
  - 1,32 but attendu, dont 0,78 sur le penalty arrêté, contre 0,84 ;
  - possession de 68 % après le carton rouge, contre 47 % avant ;
  - réseau de passes du onze jusqu'à la 62e : 27 passes entre Niakaté et Kouyaté.

## 6. Toujours être à jour

**Avant de proposer un sujet ou d'en parler**, vérifier sur le web la dernière actu des Aigles : derniers matchs, dernière liste, résultats, prochains rendez-vous. Ne jamais présenter comme « à venir » quelque chose qui a déjà eu lieu. C'est une exigence de Diaby, rappelée le 8 octobre 2026.

**Où regarder** :
- le web (presse sportive, femafoot.online pour le calendrier) ;
- les pages X suivantes : @femafoot (officielle), @AiglesDuMali_, @Equipesdumali, @malicomps. On les lit avec le navigateur intégré de l'ordinateur de Diaby : sans connexion, X n'affiche que les 5 derniers posts environ, et la page @femafoot non connectée montre surtout des posts anciens.

Ces pages sont des pistes, pas des preuves : un chiffre ou un fait qu'on y lit se recoupe à la source officielle avant d'être repris. Et la source officielle se lit en entier, après chargement complet de la page. Le 8 octobre 2026, j'ai lu trop vite la page FIFA du Mali (l'encadré « records » disait 53e) et j'ai contredit à tort @AiglesDuMali_ : le tableau du haut affiche bien 47e.

**État au 8 octobre 2026** (à revérifier, ça bouge) :
- **CAN 2025** (Maroc) : élimination en quart contre le Sénégal (0-1), le 9 janvier 2026 à Tanger.
- **Sélectionneur** : Anthony Da Silva. Sa première liste date du 10 septembre 2026.
- **Éliminatoires CAN 2027, groupe K** (Mali, Rwanda, Cap-Vert, Liberia) :
  - Mali 3-1 Cap-Vert le 25 septembre 2026 ;
  - Liberia 0-1 Mali le 29 septembre 2026, avec le but d'Ange Martial Tia à la 79e (première convocation) ;
  - le Mali a 6 points, à égalité avec le Rwanda.
- **Amical Maroc 1-1 Mali**, le 4 octobre 2026 à Tanger : but marocain d'Ezzalzouli à la 35e, égalisation de Gaoussou Diarra à la 77e. Ce match a remplacé l'amical contre la Tunisie, annulé.
- **Prochains matchs** : contre le Rwanda en novembre, à Bamako puis à Kigali (dates à confirmer, voir plus bas). Ensuite le Cap-Vert et le Liberia, les 23 et 27 mars 2027 selon femafoot.online (lu le 13 octobre).
- **Classement FIFA** : 47e (+6, 1474,14 points) au classement **officiel du 7 octobre 2026** (article FIFA du 7 octobre ; le précédent, du 20 juillet, le donnait 53e). Rwanda 119e (1156,16 points, à confirmer sur fifa.com). Le prochain classement sort le 18 novembre 2026, après les deux matchs contre le Rwanda. Le calcul FIFA est dans `malidata/fifa.py` (il retrouve les points d'octobre du Mali à 0,14 près) ; les points de départ dans `registre/classement_fifa.csv`.
- **Dates contre le Rwanda à confirmer** : femafoot.online annonce le 13 novembre à Bamako et le 17 à Kigali (lu le 13 octobre) ; Africa Top Sports (13 octobre) dit le 11 et le 15.
- **Elo maison** (`malidata/elo.py`, méthode eloratings.net, 49 945 matchs) : le Mali est 54e des sélections actives (1747 points) au 6 octobre 2026.
- **Aigles Dames** : 2e tour des éliminatoires des JO 2028, en double confrontation contre le Bénin. Le premier match se joue à Lomé, vers le 8 octobre.
- **U20** : tournoi UFOA-A à domicile, qualificatif pour la CAN U20. Le Mali n'y est plus allé depuis son titre de 2019.
- **Seydou Dembélé** (Reims, arrivé en septembre 2026, révélation de la CAN U17 2025) : 8 buts dans 3 catégories selon @AiglesDuMali_, à recompter.
- **Sinayoko** au Paris FC : 4 buts et 1 passe décisive en 5 matchs de Ligue 1 début octobre 2026 (à mettre à jour).
- **Registre des joueurs maliens** : `registre/joueurs.csv`, avec la source de chaque club et un champ « à confirmer ».
