# Le pipeline de données (détail technique)

Un pipeline complet, de la donnée brute au graphique, sur des données de match réelles :
les 52 matchs de la Coupe d'Afrique des Nations 2023, événement par événement
(162 903 passes, tirs, duels, pressions… avec leur position sur le terrain).

Il produit des tables d'analyse, un score par joueur (le **Mali Player Score**),
cinq graphiques sur les Aigles et un fichier de résultats qui alimente les visuels de la page.

## Lancer

```bash
python taches.py donnees      # environ une minute, téléchargement compris
python taches.py tests        # 28 tests
```

Options : `--only gold charts` pour ne relancer que certaines étapes, `--force` pour
retélécharger les fichiers bruts. Tout se règle dans `config.yaml` (compétition, équipe
suivie, temps de jeu minimal, poids du score).

## Comment c'est construit

```
StatsBomb Open Data (GitHub)
        │  ingest.py   téléchargement repris, écriture atomique, manifeste (taille, empreinte, date)
        ▼
BRONZE  data/bronze/        106 fichiers JSON bruts, jamais modifiés
        │  silver.py   aplatissement des événements, typage, temps de jeu reconstruit
        ▼
SILVER  data/silver/        matches, events, players, starting_xi, player_match_minutes
        │  sql/*.sql + gold.py   indicateurs, comparaisons par poste, score
        ▼
GOLD    data/gold/          player_match_stats, player_tournament, team_match_stats, shots, player_scores
        │  quality.py  11 contrôles, le pipeline s'arrête au premier échec
        ▼
SORTIES outputs/            resultats.json, graphiques/*.png, quality_report.json
```

Tout est aussi chargé dans une base DuckDB (`data/warehouse.duckdb`) : on peut interroger
les tables en SQL directement. Les tables silver et gold existent aussi en Parquet, et les
tables gold en CSV.

| Fichier | Rôle |
|---|---|
| `malidata/ingest.py` | Collecte des fichiers bruts |
| `malidata/silver.py` | Nettoyage et temps de jeu |
| `sql/10…40_*.sql` | Modèles d'indicateurs, en SQL |
| `malidata/gold.py` | Exécution des modèles, centiles, score |
| `malidata/quality.py` | Contrôles de qualité |
| `malidata/export.py` | Résumé JSON pour les visuels |
| `malidata/charts.py` | Graphiques |
| `tests/` | Tests unitaires |

## Deux choix d'ingénierie à connaître

**Le temps de jeu est recalculé depuis les événements.** Le fichier des compositions
contient 23 plages horaires incohérentes réparties sur 4 matchs (une fin de plage située
dans une période antérieure à son début). Le pipeline repart donc des
titularisations, des remplacements et des expulsions, et mesure le temps réellement joué,
arrêts de jeu compris. Un contrôle vérifie que la somme des minutes d'une équipe vaut bien
11 joueurs × la durée du match.

**Les buts sont recoupés avec le score officiel.** Pour chacune des 104 équipes-matchs, les
buts recomptés depuis les événements (tirs marqués + buts contre son camp adverses) doivent
redonner le score officiel. C'est le cas partout.

## Définitions

Le terrain StatsBomb mesure 120 × 80 et chaque équipe attaque vers x = 120.

- **Buts attendus (xG)** : probabilité qu'un tir finisse en but, fournie par StatsBomb. `npxg` exclut les penalties.
- **Passes décisives attendues (xA)** : xG du tir que la passe a amené.
- **Passe progressive** : passe réussie dans le jeu, partie hors des 40 % défensifs, qui rapproche le ballon du but d'au moins 10 yards ou qui entre dans la surface.
- **Conduite progressive** : même critère pour une course balle au pied finissant dans la moitié adverse.
- **PPDA** : passes adverses dans leurs 60 % défensifs, divisées par nos tacles, interceptions et fautes dans cette zone. Plus c'est bas, plus le pressing est intense.
- **Occupation du dernier tiers** (`field_tilt_pct`) : part des passes jouées dans le dernier tiers adverse, sur le total des deux équipes.
- **Possession** : part des passes du match. C'est une approximation, pas un temps de possession.

## Mali Player Score

Une note sur 100, calculée parmi les joueurs de champ du tournoi ayant joué au moins
180 minutes (263 joueurs), comparés à leur groupe de postes (défenseurs, milieux, attaquants).

1. Chaque indicateur par 90 minutes est transformé en rang centile dans le groupe de postes.
2. Chaque pilier est la moyenne des centiles de ses indicateurs.
3. Le score est la moyenne des piliers, pondérée selon le poste.

| Pilier | Indicateurs (par 90 min) | ATT | MIL | DEF |
|---|---|---|---|---|
| Production | xG hors penalty, buts hors penalty, tirs | 40 | 15 | 5 |
| Création | xA, passes clés, passes dans la surface | 25 | 25 | 10 |
| Progression | passes progressives, conduites progressives, dribbles réussis | 20 | 30 | 25 |
| Défense | tacles + interceptions, pressions, récupérations, duels aériens gagnés | 5 | 20 | 50 |
| Temps de jeu | rang des minutes jouées | 10 | 10 | 10 |

Les poids sont une proposition de départ, à ajuster dans `config.yaml`.

## Limites

- **L'échantillon est court** : 3 à 7 matchs par équipe. Un score sur 300 minutes décrit un tournoi, pas le niveau d'un joueur.
- **Les données datent de janvier-février 2024.** StatsBomb ne publie pas en libre accès les saisons en cours ; pour les suivre, il faut une source payante ou une collecte autorisée.
- **Les postes sont regroupés en trois familles** : un latéral et un défenseur central sont comparés ensemble, ce qui avantage les latéraux sur la création.
- **Le score ne note pas les gardiens.**
- Les données StatsBomb Open Data sont publiées pour un usage non commercial, avec mention de la source.

## Pour aller plus loin

- Ajouter une source : écrire un module d'ingestion qui dépose ses fichiers dans `data/bronze/`, puis une fonction qui les ramène au schéma de `silver.events`. Les modèles SQL ne changent pas.
- Passer sur BigQuery : les modèles `sql/` sont du SQL standard, à l'exception de `count(*) filter (...)` (à remplacer par `countif`) et de `exclude` (`except`).
- Planifier : `python -m malidata run` est rejouable sans effet de bord, donc directement planifiable (cron, Cloud Run, Airflow).

## Profils par rôle (étape `profils`)

`python -m malidata run --only profils` lit `gold.player_tournament` et produit `gold.player_profiles`
ainsi qu'un fichier par joueur de l'équipe suivie dans `outputs/fiches/` (c'est ce que lit la fiche joueur).

Trois règles, codées dans `malidata/profils.py` et testées :

- **Bassin** : un joueur est comparé aux joueurs du même rôle ayant joué au moins `min_minutes`
  (un latéral aux latéraux). Le bassin « ligne » (tous les défenseurs) est aussi exporté pour comparer.
- **Centile** : part des autres joueurs du bassin strictement dépassés. Zéro dribble = centile 0.
- **Note** : moyenne des centiles sur les critères du rôle, listés dans `config.yaml` (`roles`).
  Un rôle sans liste de critères n'est pas encore profilé.

L'ancien « Mali Player Score » (`gold.player_scores`, cinq piliers pondérés) reste en place : la vidéo vitrine
et le graphique 5 s'en servent encore. À remplacer quand les critères de tous les rôles seront validés.
