# MaliDataFoot

Le football malien expliqué par la data : @MaliDataFoot sur X, @malidatafoot sur TikTok.

Ce dépôt contient tout le projet, de la donnée brute au post publié :

- le **pipeline de données** : collecte, nettoyage, base DuckDB, indicateurs en SQL, profils par poste, contrôles qualité ;
- les **gabarits visuels** : fiche joueur, duel, carte des tirs, but décortiqué, fil du match, réseau de passes, bannières ;
- le **motion design** de la vidéo de lancement, avec ses bruitages ;
- les **règles du projet** (direction artistique, données, production), écrites sous forme de skills dans `.claude/skills/`.

## Installer (une fois)

Il faut **Python 3.11 ou plus**, **Node.js 20 ou plus**, **git**, et **ffmpeg** (seulement pour la vidéo).

```bash
python -m venv .venv
# Windows : .venv\Scripts\activate      macOS / Linux : source .venv/bin/activate
python taches.py installer
```

`installer` installe les bibliothèques Python, les polices et GSAP (`visuels/package.json`) et le navigateur de rendu Chromium.

## Commandes

Toutes les commandes passent par `taches.py`. Elles fonctionnent sur Windows, macOS et Linux, et sont aussi dans le menu
« Exécuter la tâche » de VS Code.

| Commande | Ce qu'elle fait |
|---|---|
| `python taches.py donnees` | pipeline complet (StatsBomb Open Data, CAN 2023), puis exports pour les visuels ; environ 1 min |
| `python taches.py tests` | les 28 tests du pipeline ; on ne publie rien si un test est rouge |
| `python taches.py fiche` | fiche joueur, X et TikTok, dans `livrables/` |
| `python taches.py duel` | duel, X et TikTok |
| `python taches.py grille` | grille numérotée des variantes (32 cases) |
| `python taches.py bannieres` | les 16 bannières X + deux planches de choix |
| `python taches.py video --controle` | quelques images de la vidéo, pour vérifier vite |
| `python taches.py video` | vidéo de lancement complète (≈ 5 min) |
| `python taches.py tout` | données, tests, fiche, duel, grille, bannières |

`data/`, `outputs/` et `livrables/` ne sont pas suivis par git : tout se régénère avec ces commandes.
Vérifié le 8 octobre 2026 sur une copie neuve : les données, la fiche, le duel, la grille, les bannières et la vidéo
ressortent identiques aux fichiers livrés.

## Organisation

```
malidata/          le pipeline (ingest → silver → gold → profils → quality → export → charts)
sql/               les modèles d'indicateurs (gold), en SQL
tests/             les tests du pipeline
config.yaml        compétition, équipe suivie, postes et critères, seuils
registre/          le registre des joueurs maliens (club, source, à confirmer)
outils/            test de l'API-Football (la clé reste dans la variable d'environnement API_FOOTBALL_KEY)
visuels/           les gabarits (pages HTML capturées par Chromium), logos, photos, sons
visuels/archives/  essais de bannières non retenus, gardés pour mémoire (non maintenus)
docs/              pipeline, sources de données, workflow, feuille de route, journal des décisions
.claude/skills/    les règles du projet, lues automatiquement par Claude (forme, fond, production)
CLAUDE.md          l'essentiel pour travailler avec Claude Code dans ce dépôt
```

## Les règles du projet

Elles sont écrites une seule fois, dans les skills, et valent pour tout le monde (Diaby, Claude, un futur collaborateur) :

- `.claude/skills/malidatafoot-direction-artistique/SKILL.md` : la forme (nouvelle DA, formats, variantes, audit visuel) ;
- `.claude/skills/malidatafoot-donnees-et-audit/SKILL.md` : le fond (sources, calculs, audit des chiffres) ;
- `.claude/skills/malidatafoot-production/SKILL.md` : la façon de produire (textes, workflow d'un post, vidéo, sons).

Le workflow (git, contrôles avant publication) est dans `docs/workflow.md`. La suite (collecte automatique, scraping
autorisé, planification, data science) est proposée dans `docs/feuille_de_route.md`.

## Données et licences

Les données de la CAN 2023 viennent de **StatsBomb Open Data**. Leur licence demande leur logo sur chaque publication
(c'est fait par `visuels/da.py`) et interdit l'exploitation commerciale des analyses.

Les photos de joueurs sont des photos officielles de clubs, non libres : leur provenance est dans `visuels/photos/SOURCES.md`.
Le logo de la page (`visuels/logo-verte.png`) ne se modifie pas.
