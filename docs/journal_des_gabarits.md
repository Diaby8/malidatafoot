# Gabarits MaliDataFoot

## La règle de travail

1. Pour chaque nouvelle visualisation, on regarde d'abord les gabarits possibles (les deux styles ci-dessous).
2. Une fois le gabarit choisi, on sort toujours deux versions : TikTok et Twitter/X.
3. Chaque image est livrée avec son audit : sens des chiffres, termes, lisibilité.

## Le jeu de variantes (validé le 7 octobre 2026)

Règle permanente : pour chaque traitement de données, chaque data viz et chaque post, on sort la grille numérotée
des variantes (une colonne par plan, une ligne par variante, cases 1A, 1B…) avant de finaliser quoi que ce soit.

Ordre de travail : d'abord la visualisation dans la nouvelle DA (cadre blanc), ensuite seulement le jeu de variantes,
puis les versions X et TikTok de ce que Diaby retient. Le jeu de quatre mises en scène :

1. Cadre blanc : fond jaune, cadre blanc, radar et tableau.
2. Nuit : fond vert foncé, jaune et blanc, barres face à face.
3. Encre : tout sur le jaune, sans cadre, une seule encre verte, ronds plein et vide reliés.
4. Blanc : bandeau jaune, fond blanc, une barre d'écart par ligne.

## Ce qui est commun à tous les styles

- Signature : logo rond + « MaliDataFoot » en Barlow Condensed penché, fin, « Data » en demi-gras. Pas de capitales, pas de rouge, pas de @.
- Comptes : logos X et TikTok + @MaliDataFoot, toujours présents.
- Couleurs : or #F6C41C, verts #0B7A3B / #064A25, rouge #D4252A.
- Pas de slogan sur les visuels (il va dans la bio, la bannière, la fin des vidéos).
- Pas de chiffres posés sur les graphiques quand un tableau peut les porter.

## Style « vidéo »

Fond jaune avec trame de points, grand titre en capitales penchées sur deux lignes (vert puis rouge),
grand chiffre fantôme, données posées directement sur le fond, signature en bas à gauche.
Fichiers : `vitv.tpl.html` (vertical animé, six formats : tirs, but, fil du match, réseau de passes, fiche, duel, classement).

## Style « fiche »

Fond jaune uni, signature en haut à gauche, grand titre penché, cadre blanc avec graphique sans chiffres
et tableaux, comptes en bas à droite. Texte courant en Inter.
Fichiers : `da.py` (cadre commun), `fiche_pro.py` (fiche joueur), `tirs_pro.py` (carte des tirs).

## Formats de sortie

| Version | Taille | Contraintes |
|---|---|---|
| TikTok | 1080 x 1920 | rien d'important au-dessus de 150 px ni dans les 340 px du bas ; à droite, rester sous x = 946 en dessous de y = 880 |
| Twitter/X | 1080 x 1350 | marges de 56 px ; le plus petit texte reste lisible sur téléphone |

## État des gabarits

Décision du 7 octobre 2026 : la fiche joueur, le duel et le classement restent dans la nouvelle DA (l'ancienne version
de ces trois-là « fait IA »). Pour qu'ils ne se ressemblent pas tous, on propose plusieurs mises en scène par format :
duel = cadre blanc et radar (`duel_pro.py`), nuit, encre, blanc (`duel_variantes.py ... B|C|D`). Le style « vidéo » reste pour les autres.

| Visualisation | Style « vidéo » | Style « fiche » |
|---|---|---|
| Carte des tirs | X et TikTok | X seulement (`tirs_pro.py`), en réserve |
| But décortiqué | X et TikTok | pas fait |
| Fil du match | X et TikTok | pas fait |
| Réseau de passes | X et TikTok | pas fait |
| Fiche joueur | abandonné | X et TikTok (`fiche_pro.py fiche.json sortie.html x` ou `tiktok`) |
| Duel | abandonné | X et TikTok (`duel_pro.py A.json B.json sortie.html x` ou `tiktok`) |
| Classement | abandonné | fait (`classement_pro.py`), mais rangé : voir l'audit |

Style « vidéo » : la version TikTok est une image du gabarit `vitv.tpl.html` (`shotv.mjs`), la version X la même scène
réduite et recentrée (`stillx.mjs vitv.html <secondes> sortie.png`). Scènes : tirs 7,6 s ; but 12,6 s ; fil du match 17,5 s ; réseau 21,9 s.

## Audit de la note (7 octobre 2026)

Test : les matchs de chaque joueur coupés en deux paquets, la note calculée sur chacun, puis comparée (corrélation de rang).
Latéraux 0,40 ; milieux 0,25 ; défenseurs centraux 0,11 ; milieux défensifs 0,09 ; milieux offensifs et ailiers -0,03 ; avants-centres -0,10.
Sur un tournoi de cinq matchs, la note est donc surtout du bruit hors latéraux. Conséquences :

- fiche et duel : présentés comme « son tournoi », note sans décimale ;
- classement : rangé jusqu'à disposer d'une saison complète ;
- à corriger avec les données de saison : doublons de critères (xA / passes clés, passes progressives / vers le dernier tiers),
  effet de la possession de l'équipe (centraux, milieux défensifs), petits temps de jeu en tête de classement.

Les critères des six rôles sont dans `config.yaml` (`roles`). Seuls ceux des latéraux ont été discutés ; les autres sont une proposition à valider.

## Motion design, version 2 (7 octobre 2026)

37,45 s, vertical 1080 x 1920, 60 images par seconde. Page maître `md2.html` : elle superpose l'ancien gabarit (`vitv.html`,
accroche jouée 1,26 fois plus vite puis tirs, but, fil du match, réseau) et deux scènes animées de la nouvelle DA
(`scenes_md2.py` : fiche joueur cadre blanc, duel « nuit »), reliées par un volet rouge. Le classement n'y est plus.
Rendu : `render2.mjs` (quatre lots en parallèle), effets sonores `sfx_md2.py`, puis ffmpeg.

## Grille des variantes par plan (7 octobre 2026)

`variantes.py <plan> <A|B|C|D> sortie.html` : accroche, tirs, but, fil, reseau, fiche, fin, chacun dans les quatre mises en scène.
Le duel a ses propres scripts (`duel_pro.py` pour A, `duel_variantes.py` pour B, C, D). Les 32 cases sont numérotées de 1A à 8D
(plan 1 à 8 dans l'ordre de la vidéo, variante A à D). Format X pour l'instant ; la version TikTok se fait après le choix.

## Audit : ce qu'il couvre (règle du 7 octobre 2026)

Projet pro : l'audit est aussi sévère que celui de Diaby, sur le fond comme sur la forme. Il couvre toujours quatre choses.

1. Les données : chaque chiffre affiché est recompté depuis les fichiers bruts, et recoupé avec une source externe quand il surprend.
2. La logique : ce que le chiffre veut dire vraiment (volume ou réussite, rang ou vraie valeur, sens d'une passe, poids d'un penalty),
   et si le titre ou la phrase ne lui fait pas dire plus.
3. La sémantique : les mots, les unités, les définitions.
4. Le visuel : collisions, doublons, lisibilité sur téléphone.

Corrections de fond du 7 octobre : duel en vraies valeurs pour 90 minutes + bloc « réussite » avec le nombre de tentatives (`duel_v2.py`) ;
réseau de passes avec la colonne « en avant » et le contexte du carton rouge ; fil du match avec les buts attendus hors penalty ;
carte des tirs classée hors penalty ; but décortiqué : la séquence part du milieu et repasse par le gardien.
Pays : toujours avec leur drapeau, dans un petit rond comme dans les applis de foot (`da.drapeau`). Clubs : écusson seulement si Diaby dépose le fichier.
Le petit dessin à trois barres devant la ligne d'info du style « vidéo » est jugé « bof » : à retirer ou remplacer (choix en attente).


## Corrections après l'audit indépendant (7 octobre 2026, soir)

Données (pipeline) :
- minutes jouées au chrono du match (un match = 90 ou 120), plus au temps réel ; `minutes_reelles` garde l'ancien décompte ;
- « ballons reçus dans la surface » : seulement les ballons vraiment reçus ;
- un joueur n'entre dans un poste que s'il y a fait au moins la moitié de ses actions (`PART_MIN` dans `profils.py`) : 49 latéraux au lieu de 54 ;
- l'export donne la minute affichée (`minute_aff` : 120+2), la minute du premier changement (`until_clock`), la part des passes avant / après le rouge (`part_passes`).

Textes, règles retenues avec Diaby :
- être court : un chiffre, une phrase. Pas d'abréviation que tout le monde ne connaît pas (« A.P. » refusé) ;
- écrire « possession » (calculée sur les passes), pas « part des passes » ;
- ne pas écrire une conclusion qui dépend d'un seuil choisi par nous (« aucune vers l'avant » était faux sans le seuil de 9 m) ;
- « Performances proches » remplace « Profils proches » (on compare le tournoi, pas le joueur en général) ;
- termes en français : buts attendus, passes décisives attendues, conduites progressives ;
- le seuil de 180 minutes est écrit en bas de la fiche et du duel.

Visuel : le grain (effet craie) est retiré du style « vidéo », la trame de points reste. Le petit dessin à trois barres devant la ligne d'info est retiré.

Vidéo de lancement : `scenes_md2.py` construit la fiche (`variantes.py fiche A … tiktok`) et le duel (`duel_v2.py … tiktok`) puis les anime ;
`render2.mjs` en quatre lots, `sfx_md2.py`, ffmpeg. La fiche et le duel existent en X et en TikTok.

La grille des variantes est refaite avec ces corrections (`grille.py <dossier>` régénère les 32 cases et la grille ; le duel de la ligne 7 a quatre mises en scène différentes : A radar + tableau, C ronds reliés, D barres d'écart dans `duel_mises.py`, B barres face à face dans `duel_v2.py` ; les chiffres communs sont dans `duel_commun.py`). À recevoir de Diaby : le logo StatsBomb (demandé par leur licence), les écussons de clubs, un portrait d'Osimhen plus grand.

Règle rappelée par Diaby le 7 octobre : les variantes d'un plan ne doivent pas être le même dessin en quatre couleurs. Quand c'est possible, chaque ligne propose une mise en scène différente.

Accroche (7 octobre 2026, choisie par Diaby) : « Les Aigles jouent. La data parle. » remplace « Les Aigles. Les joueurs. Les matchs. Tout en chiffres. », dans la vidéo et dans les quatre variantes du plan 1.

## Recomptage indépendant du fichier final (7 octobre 2026, soir)

Tous les chiffres de la vidéo ont été recomptés depuis les fichiers bruts par un contrôle qui n'a pas vu le code. Résultat : tout est confirmé sauf un rang.
- Corrigé : Hamari Traoré était « 12e sur 49 » à cause d'un arrondi machine (59,999… contre 60,0) ; il est 11e ex aequo. La note est arrondie avant le classement (`profils.py`), avec un test.
- Corrigé : arrondi « comme à l'école » partout (`da.fr` : 2,25 donne 2,3) ; les fiches gardent 4 décimales et n'arrondissent qu'à l'affichage.
- Corrigé : la note de bas de fiche dit ce qu'est la note (part des autres joueurs dépassés, en moyenne sur dix critères), plus « moyenne de ses dix rangs ».
- Corrigé : sur le but, un nom n'est jamais plus près d'une autre pastille que de la sienne ; même joueur au même endroit = un seul nom.
- Corrigé : sur la carte des tirs, tous les tirs non marqués ont la même teinte (plus de tirs de Sinayoko en foncé sans légende).
- Réglé : la licence StatsBomb exige leur logo sur toute publication. Il vient de leur dépôt officiel (voir `SOURCES.md`) et il est posé sur chaque visuel de données par `da.credit()` : directement sur fond clair, sur une pastille blanche sur fond sombre, jamais recoloré. La licence interdit aussi l'exploitation commerciale des analyses.
La vidéo de lancement est re-rendue avec toutes ces corrections et le logo.

## Bruitages : cloches retirées (8 octobre 2026)

Diaby : les cloches (« ting ting ») font trop. Les 19 cloches de la vidéo de lancement sont retirées (`sfx_md2_sans_cloches.py`) :
3,35 / 3,38 / 3,50 / 4,28 / 4,58 / 5,30 / 5,42 / 5,54 / 11,24 / 14,47 / 19,82 / 23,02 / 28,79 / 33,60 à 34,32 s.
L'image n'a pas bougé (même flux vidéo, même empreinte) ; le reste de la piste est identique à 0,3 % près (compresseur).
Les « bulles » (pop) restent pour l'instant ; à revoir s'il les trouve aussi enfantines.

## Dépôt du projet (8 octobre 2026)

Le projet sort de l'espace de travail temporaire : dépôt `malidatafoot` (git), à ouvrir dans VS Code sur l'ordinateur de Diaby.
Toutes les commandes passent par `taches.py`. Vérifié sur une copie neuve : données, fiche, duel, grille, bannières et vidéo
ressortent identiques aux livrables. Les règles sont dans trois skills (`.claude/skills/`) : forme, fond, production.
Bannière : leçon retenue, les cartes se font depuis les vrais gabarits allégés (`reel_cartes.py`), pas redessinées.

## 8 octobre 2026 : les sons de la vidéo de lancement

Diaby entendait encore des « ding » après le retrait des cloches : c'étaient les bulles, le scintillement du but, les coups de
bois en série (« xylophone ») et les tics. Quatre essais. Validé : les « sons de terrain » (frappes de balle sur les passes et le tir,
touches de balle sur le réseau de passes, coups mats sans note sur la fiche et le duel, bulles seulement sur les buts de la carte
des tirs). C'est le réglage par défaut de `sfx_md2.py`. Fichier final : `MaliDataFoot-video-de-lancement-tiktok-essai-4.mp4`.
- 11 octobre 2026 : deuxième source branchée, l'historique des Aigles (résultats internationaux CC0), recoupée avec StatsBomb. Objectif : obtenir Opta légalement.
