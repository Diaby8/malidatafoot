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

## 3. POC faits (maquettes X et TikTok + textes des threads et voix off dans `poc/textes.md`, images dans `livrables/poc/` ; à améliorer au cas par cas)
| # | Sujet | Ce que ça fait comprendre | Données | Fichiers |
|---|---|---|---|---|
| 2 | **Points FIFA contre le Rwanda** | ce que rapporte une victoire, un nul, une défaite ; « il faut gagner deux fois » | formule FIFA, registre | `outputs/analyses/fifa_rwanda.json` |
| 3 | **On a joué le groupe 100 000 fois** | un modèle testé honnêtement ; 98 % de qualif, la vraie bataille est la 1re place ; Kigali est le danger | martj42 + Elo, modèle Dixon-Coles (recompté) | `malidata/simulation.py`, `livrables/video-simulation/voix-off.txt` |
| 4 | **Vidéo A : ce que le 1-1 ne dit pas** (présente la page) | un score remis dans son contexte : force, terrain, attendu | Elo, modèle, FIFA (recompté) | `livrables/video-A/voix-off.txt` |
| 5 | **Vidéo B : trois questions, trois réponses** | défense, avantage du terrain, génération la plus forte (pic 2024) | analyses + Elo | `poc/maquettes/poc.py` |
| 6 | **Vidéo C : la boîte à outils** | la force (Elo), la qualité d'une occasion (xG), la simulation | Elo, StatsBomb, simulation | `poc/maquettes/poc.py` |
| 7 | **L'avantage du terrain pèse presque double en Afrique** | 317 points d'Elo en Afrique contre 169 en Europe | martj42 + Elo (recompté) | `outputs/analyses/avantage_terrain.json` |
| 8 | **Mali - Côte d'Ivoire décodé** (en pause : « pas Mali-Côte d'Ivoire », Diaby, 14/10) | le ballon, pas les occasions : 90 passes dans le dernier tiers, 8 dans la surface | StatsBomb | `poc/maquettes/poc.py` |
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

## 6. Toutes les autres idées dont on a parlé (statut : idée)
Reprises des échanges d'août, septembre et octobre 2026 et de `docs/banque_idees.md`. Chacune deviendra un sujet numéroté quand on la lance.

**Séries et rendez-vous**
- « La data dit quoi ? » : un joueur, une analyse de 45 secondes (« on parle de ses buts, mais est-ce son meilleur atout ? »).
- « Mali Next Gen » : les jeunes Maliens à suivre, série numérotée.
- « Qui est le meilleur ? » : duels entre Maliens du même poste.
- « La Data sélection » : le XI que la data choisirait, à chaque rassemblement.
- Le classement hebdo des Maliens d'Europe (Mali Data Ranking, avec un score maison transparent sur sa méthode).
- Les Maliens du week-end ; le joueur malien de la semaine ; l'analyse d'avant-match et d'après-match des Aigles.
- Les joueurs proposés par les abonnés (« analyse mon joueur »).
- Binationaux et joueurs à suivre : ce que dit la data sur un joueur éligible, comparé aux titulaires du poste (sensible : seulement des origines publiques et sourcées).
- Carrousels TikTok (plusieurs images à faire défiler) pour les fiches et les classements.
- Storytelling de parcours (format à la MARA) : Sinayoko, de la CAN 2024 au triplé au Vélodrome (septembre 2026), avec des faits vérifiés.

**Aigles : actu et rassemblements**
- La liste de septembre en data : où jouent les appelés, âge, nouveaux, rescapés de la CAN 2023.
- Les débuts d'Ange Martial Tia (but de la victoire au Liberia).
- Maroc 1-1 Mali : l'égalisation de Gaoussou Diarra (déjà dans la vidéo A).
- Hier et aujourd'hui : le groupe de septembre comparé à celui d'Abidjan.
- Avant le Rwanda, qui est en forme ; le Mali du nouveau coach, match après match (jeu, nouveaux appelés, âge du groupe, ce qui coince aussi).
- Le classement FIFA : ce qui fait monter ou descendre une équipe (fait : sujet 2).

**Phénomènes et analyses**
- Pourquoi le Mali bute sur les quarts ? (éliminations récentes une par une).
- Le Mali domine souvent, pourquoi marque-t-il si peu ?
- La dépendance à un joueur (lié au sujet 13).
- Quand le Mali encaisse-t-il ? Première ou deuxième mi-temps ?
- Qui fait avancer le ballon ; les sorties de balle ; les coups de pied arrêtés.
- Notre propre xG des éliminatoires (« comment on calcule »), si les matchs complets sont disponibles en vidéo.
- Le quart contre la Côte d'Ivoire rejoué 10 000 fois (simulation à partir des occasions).
- Valeur marchande contre performance réelle.
- « Il ne marque pas beaucoup, mais regardez où il joue » (carte de chaleur d'un joueur).

**Histoire et curiosités**
- L'historique complet des Aigles : matchs, compos, buteurs, sélectionneurs ; rétrospectives et records.
- Hamari Traoré, le latéral qui créait comme un attaquant (à vérifier).
- D'où viennent les Aigles : carte des clubs, kilomètres jusqu'à Bamako.
- La génération des Mondiaux jeunes (U17, U20), dix ans après.
- Seydou Dembélé à Reims, de la CAN U17 aux équipes de Reims.
- Les Aigles Dames et les U20 (élargir aux autres sélections).

**Outils et grands projets**
- La base de tous les joueurs maliens et binationaux dans le monde, mise à jour automatiquement ; alertes (but, transfert, blessure).
- Un tableau de bord des sélectionnables (minutes, blessures, forme), utile aussi pour la FEMAFOOT.
- Le championnat malien reconstitué à partir de sources publiques.
- Profils de jeu (regroupement de joueurs), joueurs semblables (« le prochain Seydou Keita »), repérage des jeunes à fort potentiel.
- Prédictions des matchs des Aigles (la simulation du groupe K en est le premier pas).
- Brouillons de visuels générés automatiquement après chaque match ; un chatbot sur le foot malien ; des contenus en bambara, soninké et anglais.
- Formats légers : devine le joueur à partir de son radar, quiz, le onze de la CAN 2023 selon la data.
