# La menace attendue (xT) : comment on la calcule

Données : Hudl StatsBomb Open Data (usage non commercial, logo et mention « Hudl StatsBomb » obligatoires).

## L'idée en une phrase

On découpe le terrain en 192 cases (16 dans la longueur, 12 dans la largeur). Pour chaque case, on se demande :
« si mon équipe a le ballon ici, quelle est la chance que ça finisse en but dans les actions qui suivent ? ».
C'est la menace attendue de la case (xT, pour *expected threat*, méthode de Karun Singh, 2019).

Une passe ou une conduite de balle qui amène le ballon d'une case à 0,01 vers une case à 0,10 ajoute 0,09 de menace.
On crédite ce gain au joueur qui a fait l'action. Une passe en retrait donne un chiffre négatif.

## Comment la grille est apprise

On a regardé 2 564 matchs masculins (de 2003/04 à 2024) : La Liga, Premier League, Serie A, Ligue 1, Bundesliga,
Coupes du monde, Euros, Copa América, Ligue des champions, Indian Super League, MLS. Les matchs féminins sont laissés
de côté pour comparer ce qui est comparable. Les 52 matchs de la CAN 2023 ne servent pas à apprendre : on les garde pour
appliquer et tester le modèle.

Pour chaque case, on compte ce que font les joueurs qui ont le ballon :

- ils tirent (part de tirs, et chance qu'un tir de cette case finisse en but, mesurée par le xG StatsBomb des tirs,
  plus stable que le simple taux de buts) ;
- ou ils déplacent le ballon (passe ou conduite) et on note la case où il arrive, si l'action réussit.

La valeur d'une case = (chance de tirer × chance de marquer) + (chance de déplacer le ballon × valeur moyenne des cases
où il arrive). On répète ce calcul jusqu'à ce que plus rien ne bouge (55 tours, écart final inférieur à 0,0000001).

On ne prend que le jeu courant : les touches, corners, coups francs, six mètres et engagements ne servent pas de point
de départ (les actions qui les suivent, si). Les penaltys et coups francs directs sont exclus. Une conduite doit faire
au moins 3 unités StatsBomb (environ 2,7 m). Au total : 3,35 millions de passes et conduites et 60 101 tirs.

## Ce que donne la grille

Les valeurs montent vers le but adverse, et la case la plus forte est en plein centre, juste devant le but :
0,28 (28 % de chance de but dans la suite). Dans son propre camp, aucune case ne dépasse 0,01. La grille est
symétrique entre la gauche et la droite. C'est l'ordre de grandeur des grilles publiées.

## Est-ce que ça marche ?

- **Sur des matchs jamais vus.** On a refait la grille sur 80 % des matchs et testé sur les 20 % restants
  (82 496 possessions). Le xT ajouté pendant une possession sépare bien celles qui finissent par un tir :
  AUC 0,85 (0,5 = hasard, 1 = parfait), contre 0,68 pour les mètres gagnés vers le but. Pour les buts : 0,91.
  Sur la CAN 2023 : 0,86 pour les tirs, 0,89 pour les buts.
- **Au niveau d'un match.** Le xT d'une équipe dans un match suit son xG hors penalty (corrélation 0,69).
- **La grille est stable.** Deux moitiés de matchs tirées au hasard donnent la même grille (corrélation 0,9996).
  La grille de La Liga seule ressemble au reste (0,9993), même si sa case la plus forte est plus haute (0,32 contre 0,27).
- **Contrôle indépendant.** Un second programme, écrit à part, a tout recompté depuis les fichiers bruts : même
  grille, mêmes chiffres pour le Mali (écarts dus aux arrondis).

## Ce qu'il faut garder en tête

- **Cinq matchs, c'est peu.** Le modèle est solide, mais le classement des joueurs sur un seul tournoi est fragile :
  quand on coupe les matchs de chaque joueur en deux, les deux moitiés se ressemblent peu (corrélation de rang 0,29).
  Pour l'équipe, en tirant au hasard ses matchs, le rang du Mali varie entre 14e et 22e.
- **Le xT ne voit que le ballon.** Pas de valeur pour la défense, les appels sans ballon, le pressing. Une passe ratée
  ne retire rien. Un attaquant qui joue en remise vers l'arrière (comme Sinayoko) a un xT de passe négatif sans mal
  jouer.
- **Une case ne connaît pas le contexte.** Pas de position des adversaires, pas de vitesse de l'action.
- **Biais des données ouvertes.** Beaucoup de matchs du Barça de Messi et de grands championnats européens ;
  peu de football africain. La grille reste quasi identique sans La Liga ou avec les seuls matchs de sélections.
- **Deux façons de compter l'équipe.** En comptant les retours en arrière (xT net), le Mali est 21e sur 24 ;
  en ne gardant que les gains (xT positif), il est 13e. Le Mali fait beaucoup circuler le ballon vers l'arrière.

## Définitions des fichiers

- `xt_grid.json` : la grille 16 × 12 (valeurs[ligne y][colonne x], le but attaqué est en x = 120), ses
  composantes, l'intervalle à 95 % (bootstrap sur 200 tirages) et les contrôles.
- `mali_players.json` : xT ajouté par joueur malien, par 90 minutes (chrono du match), passes et conduites séparées,
  rang parmi les 243 joueurs de champ de la CAN avec au moins 180 minutes, et rang dans son poste.
- `teams.json` : xT généré et concédé par 90 minutes pour les 24 équipes.
- `top_possession.json` : la possession la plus menaçante du Mali, événement par événement (coordonnées, horodatage),
  pour l'animation.
- `validation.json` : tous les tests ci-dessus, chiffres complets.
