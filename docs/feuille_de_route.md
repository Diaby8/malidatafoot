# Feuille de route (proposition du 8 octobre 2026, à discuter avec Diaby avant de construire)

Objectif : passer d'un pipeline qui tourne sur la CAN 2023 à une plateforme qui suit **les Aigles et les Maliens en club,
saison en cours, automatiquement**, avec des données dont on a le droit de se servir, et qui sort des brouillons de
visuels après chaque match.

## Étape 1 : la base (tout de suite)

- Le dépôt sur l'ordinateur de Diaby et sur GitHub (privé). VS Code + Claude Code.
- Intégration continue GitHub Actions : les tests à chaque envoi.
- Le registre des joueurs maliens (`registre/joueurs.csv`) devient la table de référence. On y relie, pour chaque joueur, les identifiants de chaque source (API-Football, Understat…).

## Étape 2 : la saison en cours

- Le module `ingest_api_football`, qui dépose ses fichiers bruts dans `data/bronze/api_football/` avec un manifeste. La clé est dans un secret, jamais dans le code.
- Les fonctions qui ramènent ces données au schéma silver. Les modèles gold existants restent les mêmes.
- La collecte planifiée : chaque nuit pour les clubs, et après chaque match des Aigles. Au début avec GitHub Actions (cron) ou le planificateur de l'ordinateur.
- Les contrôles qualité étendus : fraîcheur des données, joueurs du registre introuvables, écarts entre sources.

## Étape 3 : ce que personne n'a

- **Les tirs des Aigles en éliminatoires.** Un petit outil de saisie à partir de la vidéo (position, partie du corps, situation), puis un **modèle xG** entraîné sur les tirs de StatsBomb Open Data. Le modèle est évalué honnêtement (log loss, calibration) et documenté. C'est la partie data science.
- **Le scraping**, seulement là où c'est permis (Understat pour le xG des clubs, par exemple), avec un cache, une limite de débit et la décision notée dans `docs/sources_de_donnees.md`.

## Étape 4 : passer à l'échelle

- Un entrepôt partagé : BigQuery (Diaby connaît GCP) ou Postgres. Les modèles SQL sont déjà presque compatibles (voir `docs/pipeline.md`).
- Un orchestrateur (Prefect, Dagster ou Airflow) quand il y aura plusieurs sources et plusieurs fréquences.
- La génération automatique des brouillons de visuels (fiche, duel, carte des tirs) après chaque match, à valider avant publication.
- D'autres analyses :
  - profils de jeu (regroupement de joueurs) ;
  - joueurs semblables ;
  - évolution sur la saison ;
  - phénomènes de jeu des Aigles (pressing, sorties de balle, coups de pied arrêtés).

## Ce qu'il faut décider ensemble

1. La source payante, ou pas, pour la saison en cours : le test API-Football est à lancer.
2. Où tourne la collecte planifiée : sur l'ordinateur ou sur GitHub Actions.
3. Le premier phénomène à étudier et le premier post de la saison.
