---
name: malidatafoot-donnees-et-audit
description: Règles de fond de MaliDataFoot : sources de données, pipeline, définitions des indicateurs et audit des chiffres. À lire avant toute analyse, tout chiffre publié ou tout ajout de source.
---

# MaliDataFoot : données, chiffres et audit (le fond)

**Règle d'or : uniquement des faits vérifiés.** Une page data se juge sur sa crédibilité. Un chiffre faux publié coûte plus
cher que dix posts réussis. Il faut être strict, vouloir réussir, et donc vérifier plus que ce qui paraît nécessaire.

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

- **StatsBomb Open Data.** C'est la seule source gratuite d'événements récents pour l'Afrique : la CAN 2023 (et la Ligue 1 jusqu'en 2022/23). Leur logo est obligatoire et l'exploitation commerciale est interdite (clause 1.2.2).
- **API-Football.** Gratuit à 100 requêtes par jour, puis 19, 29 ou 39 $ par mois. La clé reste dans la variable d'environnement `API_FOOTBALL_KEY`, jamais dans la conversation ni dans un fichier suivi par git. Diaby lance lui-même `outils/test_api_football.py` et transmet `rapport_api_football.json`.
- **Sportmonks.** Environ 29 € par mois pour 5 championnats, plus une option xG à 24–29 € (Ligue 1 et phases finales de la CAN, pas les éliminatoires).
- **Understat.** Gratuit : top 5 + Russie, avec le xG de chaque tir.
- **FBref.** A perdu les données avancées Opta le 20 janvier 2026.
- **FotMob.** Interdit l'extraction automatique : ne pas l'utiliser.
- **Wyscout.** Environ 299 € par an en licence personnelle.

**Scraping et collecte automatique** : ils sont prévus, mais seulement sur des sources dont les conditions le permettent. Il
faut lire les conditions d'utilisation et noter la décision dans `docs/sources_de_donnees.md`, respecter les limites de
débit, mettre en cache, et ne jamais dépendre d'une source dont on n'a pas le droit de se servir (leçon FBref).

**Piste propre à la page** : relever nous-mêmes les tirs des Aigles à la vidéo, et leur donner un xG avec un modèle entraîné sur les tirs StatsBomb ouverts.

**Bibliothèques possibles** : soccerdata, worldfootballR, ScraperFC, statsbombpy, mplsoccer.

## 5. Chiffres de référence (CAN 2023, après audit)

- **Mali** : 64 tirs, 5 buts + 1 contre son camp.
- **Hamari Traoré** : 480 minutes, note 60, 11e sur 49 latéraux (ex aequo).
- **Sinayoko** : 398 minutes, 3 buts sur 9 tirs, 1,53 but attendu.
- **Osimhen** : 646 minutes, 1 but sur 24 tirs.
- **Mali 1-2 Côte d'Ivoire** :
  - 1,32 but attendu, dont 0,78 sur le penalty arrêté, contre 0,84 ;
  - possession de 68 % après le carton rouge, contre 47 % avant ;
  - réseau de passes du onze jusqu'à la 62e : 27 passes entre Niakaté et Kouyaté.

## 6. Contexte à revérifier avant chaque post

- **Éliminatoires CAN 2027.** Groupe : Rwanda, Cap-Vert, Liberia. Résultats : Mali 3-1 Cap-Vert, victoire au Liberia le 29 septembre 2026. Prochaine étape : double confrontation avec le Rwanda en novembre 2026. Fin : mars 2027.
- **Sinayoko** au Paris FC : 4 buts et 1 passe décisive en 5 matchs de Ligue 1 début octobre 2026 (à mettre à jour).
- **Registre des joueurs maliens** : `registre/joueurs.csv`, avec la source de chaque club et un champ « à confirmer ».
