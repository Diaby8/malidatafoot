# Boîte à idées MaliDataFoot (le suivi de tout ce qu'on fait)

Créée le 14 octobre 2026 à la demande de Diaby. Une ligne par sujet, avec son statut. Chaque sujet sort en **thread X** et en
**motion design TikTok avec voix off**, avec les mêmes visuels (DA : `visuels/posts_video.py`, skill de DA section 0).
Les idées d'inspiration plus anciennes restent dans `docs/banque_idees.md` ; quand l'une d'elles devient un vrai sujet, elle passe ici.

Statuts : **publié** · **prêt** (vérifié, à poster) · **POC** (calcul fait + maquettes, à améliorer et auditer) · **à faire** · **bloqué** (il manque une source).

## 1. Déjà publié
| Sujet | Où | Date |
|---|---|---|
| Vidéo de lancement (teaser) | TikTok et X | 13/10/2026 |
| Bannière 2A (barres des décennies, logos X et TikTok) | X | 13/10/2026 |

## 2. Prêt à publier
| # | Sujet | Ce que ça fait comprendre | X | TikTok |
|---|---|---|---|---|
| 1 | **La défense des Aigles depuis 2020** | 2e défense d'Afrique, et même face aux mêmes adversaires le Mali encaisse deux fois moins | prêt (2 images + 4 tweets, `livrables/post1-defense`) | à faire |

## 3. POC faits (maquettes + calculs, à améliorer au cas par cas)
| # | Sujet | Ce que ça fait comprendre | Données | Fichiers |
|---|---|---|---|---|
| 2 | **Points FIFA contre le Rwanda** | ce que rapporte une victoire, un nul, une défaite ; « il faut gagner deux fois » | formule FIFA, registre | `outputs/analyses/fifa_rwanda.json` |
| 3 | **On a joué le groupe 100 000 fois** | un modèle testé honnêtement ; 98 % de qualif, la vraie bataille est la 1re place ; Kigali est le danger | martj42 + Elo, modèle Dixon-Coles (recompté) | `malidata/simulation.py`, `livrables/video-simulation/voix-off.txt` |
| 4 | **Vidéo A : ce que le 1-1 ne dit pas** (présente la page) | un score remis dans son contexte : force, terrain, attendu | Elo, modèle, FIFA (recompté) | `livrables/video-A/voix-off.txt` |
| 5 | **Vidéo B : trois questions, trois réponses** | défense, avantage du terrain, génération la plus forte (pic 2024) | analyses + Elo | `poc/maquettes/poc.py` |
| 6 | **Vidéo C : la boîte à outils** | la force (Elo), la qualité d'une occasion (xG), la simulation | Elo, StatsBomb, simulation | `poc/maquettes/poc.py` |
| 7 | **L'avantage du terrain pèse presque double en Afrique** | 317 points d'Elo en Afrique contre 169 en Europe | martj42 + Elo (recompté) | `outputs/analyses/avantage_terrain.json` |
| 8 | **Mali - Côte d'Ivoire décodé** | le ballon, pas les occasions : 90 passes dans le dernier tiers, 8 dans la surface | StatsBomb | `poc/maquettes/poc.py` |
| 9 | **Récupérer haut, mais en tirer peu** | 1er pour la hauteur de récupération, 2e pressing, 5 tirs pour 6,7 attendus | StatsBomb | `poc/jeu_can2023/` |
| 10 | **Les styles de jeu vus par la machine** | le Mali a le ballon mais ne va pas vers l'avant (23e sur 24) | StatsBomb, ACP | `poc/jeu_can2023/` |
| 11 | **Le Mali est-il maudit à la CAN ?** | pas maudit, pas encore assez fort : 62 % de chances de n'avoir aucun titre | martj42 + modèle | `poc/maudit/` |
| 12 | **Le Mali, roi du nul ?** | 21 nuls en poules pour environ 14 attendus, sans perte de points | martj42 + modèle | `poc/maudit/` |
| 13 | **Tout passe par Sinayoko (en sélection)** | 6 des 9 buts du Mali sur les deux dernières CAN, les 3 de 2025 | martj42 (à recouper) | `poc/maquettes/poc_joueurs.py` |

## 4. À faire (données disponibles)
| # | Sujet | Ce que ça fait comprendre | Données |
|---|---|---|---|
| 14 | **Sinayoko, le premier défenseur** | son pressing comparé à tous les attaquants de la CAN 2023 | StatsBomb |
| 15 | **Sinayoko, le buteur d'une équipe qui ne crée pas** | la qualité des occasions qu'il reçoit | StatsBomb + martj42 |
| 16 | **Jouer à 11 contre 10, un vrai avantage ?** | ce que change une expulsion, sur tous les cartons rouges de la CAN 2023 | StatsBomb |
| 17 | **Par où attaque le Mali ?** | réseau de passes et zones du terrain | StatsBomb |
| 18 | **Tirer beaucoup ne suffit pas** | 64 tirs contre la qualité des occasions | StatsBomb |
| 19 | **Le rassemblement de septembre en data** | la liste, les nouveaux (Ange Tia), Cap-Vert, Liberia, Maroc | registre + martj42 |
| 20 | **Le Mali, usine à milieux ?** | pourquoi tant de grands milieux et si peu de buteurs | à rassembler |

## 5. Bloqué (il manque une source)
| # | Sujet | Ce que ça fait comprendre | Il manque |
|---|---|---|---|
| 21 | **Sinayoko, talent ou réussite ?** | buts contre qualité des occasions, saison par saison depuis Auxerre | pages Understat enregistrées par Diaby |
| 22 | **Mamadou Sangaré, le milieu invisible** | sa part dans les actions qui finissent en tir, parmi les milieux de Premier League | pages Understat |
| 23 | **Ils percent (Kamissoko en porte d'entrée)** | les minutes des jeunes Maliens en Europe depuis 2014 | pages Understat + liste des jeunes Maliens |
| 24 | **Qui mérite sa place ?** | temps de jeu et forme en club des appelés, avant la liste de novembre | pages Understat (et une autre source hors grands championnats) |
| 25 | **Les Maliens du week-end** (rendez-vous) | qui a joué, marqué, brillé | source de la saison en cours |

## 6. Plus tard (réserve)
Seydou Dembélé à Reims ; les Aigles Dames et les U20 ; Hamari Traoré, le latéral créateur ; le Mali du nouveau coach match après match ;
le meilleur XI selon la data ; le prochain Seydou Keita (profils semblables) ; contenus en bambara, soninké, anglais ; et tout le reste de `docs/banque_idees.md`.
