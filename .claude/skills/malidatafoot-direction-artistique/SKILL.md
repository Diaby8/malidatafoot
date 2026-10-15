---
name: malidatafoot-direction-artistique
description: Direction artistique de MaliDataFoot (football malien par la data) : à lire avant tout visuel, post, bannière, photo de profil, motion design ou vidéo pour la page.
---

# MaliDataFoot : direction artistique (la forme)

MaliDataFoot (@MaliDataFoot sur X, @malidatafoot sur TikTok) est la page de Diaby : le football malien expliqué par la data.
C'est un projet pro. Chaque visuel doit avoir l'air d'une vraie interface de data foot (référence de niveau : Data'Scout,
les applis et institutions du foot), jamais « IA », « débutant » ou « enfantin ». Viser la réussite et la crédibilité :
mieux vaut un visuel de moins qu'un visuel approximatif.

**Relire avant de proposer (Diaby, 14 octobre 2026 : « faut pas jeter des trucs comme ça en pâture, c'est un projet pro »).**
À chaque nouvelle idée de visuel, de data visualisation ou de sujet, et avant toute proposition de source, relire d'abord :
- `docs/sources_de_donnees.md` : quelles sources on a déjà trouvées, testées, autorisées ou écartées (ex. martj42 = scores sans compos ; API-Football gratuit = 2022-2024 seulement ; FotMob = accord écrit à archiver) ;
- `docs/boite_a_idees.md` et `docs/banque_idees.md` : ce qui est déjà fait, en cours ou rejeté ;
- `docs/journal_des_gabarits.md` : les décisions de forme et de fond déjà prises ;
- les sections utiles des trois skills (DA, données, production).
Puis proposer en s'appuyant dessus : dire ce qu'on a déjà, ce qui manque, et d'où viendrait le manque, vérifié. Ne jamais proposer une solution (surtout payante) qu'on n'a pas vérifiée.

## 0. LA DA DES POSTS : le style de la vidéo (validé le 13 octobre 2026, « la DA, elle est parfaite, c'est ça que je veux »)

C'est la référence pour **tout post** (X, TikTok) et tout nouveau visuel de données. Gabarit : `visuels/posts_video.py`
(trois exemples validés : classement des défenses africaines, courbe depuis 2000, points FIFA). Partir de ce fichier,
ne jamais redessiner « dans l'esprit ».
- Fond jaune dégradé `linear-gradient(180deg,#FBD134 0%,#F6C41C 45%,#EFA40A 100%)` + trame de points #FDEBA6 (opacité .85) qui grossissent vers le coin haut droit.
- En haut : ligne d'info en Barlow Semi Condensed 600 capitales (la fin en 800), puis le titre sur deux lignes, Barlow Condensed 900 italique vert #064A25, puis 800 italique rouge #D4252A.
- Le grand chiffre fantôme du message, en contour crème (#FFF6D0, trait 4 px, opacité .6), en haut à droite.
- Les données **posées directement sur le jaune** : barres vert #0B7A3B pour le Mali, crème #FFF3C4 pour les autres ; courbe Mali verte pleine, comparaison rouge en pointillés ; axes #064A25 4 px ; grands chiffres en Barlow Condensed 900 italique, vert si bon, rouge si mauvais.
- En bas du graphique : le chiffre clé en très gros + deux lignes de texte en capitales (un mot en rouge au plus).
- Pied : logo, Mali*Data*Foot, logos X et TikTok + @MaliDataFoot, puis la ligne de source en petit.
- **Aucun effet** : ni grain, ni craie, ni ombre, ni lueur, ni cadre ou carte blanche arrondie, ni dégradé sur les barres.
- **Être créatif dans la DA** (Diaby, 14 octobre 2026) : des mises en scène inventives, mais avec nos couleurs, nos polices et sans effet. Exemple validé (« j'aime bien ») : le terrain vu en perspective (vert, lignes crème, posé sur le jaune) qui **penche** proportionnellement à l'avantage du terrain, et des **flèches sur le terrain** dont l'épaisseur suit les buts attendus. Inspiration acceptée : les visuels de terrain avec données posées dessus, mais sans photo réaliste et sans fausses actions : tout ce qui est dessiné correspond à une vraie donnée.
- **Une idée, deux formats** : sur X, un **thread** (une image par tweet, chaque image porte un message) ; sur TikTok, par défaut un **carrousel de photos** (les mêmes visuels en 1080 × 1920). Le **motion design** seulement quand l'animation apporte vraiment quelque chose (Diaby, 14 octobre 2026), et alors travaillé scène par scène.
- **Les trois couleurs, d'après la vidéo de lancement** (Diaby, 14 octobre 2026) : **jaune** = données posées sur le fond jaune (carte des tirs, fil du match) ; **blanc** = la scène « Hamari Traoré » : fond jaune et trame gardés, données dans un grand panneau blanc à coins arrondis, sans ombre, entre le titre et le pied de page (c'est la seule carte blanche autorisée) ; **vert** = la scène du duel Sinayoko-Osimhen (vert nuit #04331A, jaune et blanc), ou le vert dégradé de l'accroche. Fonction `teinte()` dans `poc/maquettes/formats.py` ; le panneau blanc se cale plan par plan.
- **Versions de couleurs** : Diaby est d'accord pour en proposer (autres fonds), mais la mise en page et les éléments ci-dessus ne bougent pas.

Pourquoi cette section : jusqu'au 13 octobre, ce skill présentait la « fiche » à cadre blanc comme la nouvelle DA et le
style vidéo comme un ancien gabarit. Les posts faits sur la fiche ont été jugés « trop IA, pas pro ». Le cadre blanc ne
sert plus que pour la fiche joueur et le duel déjà validés (à reconfirmer avant de les réutiliser).

## 1. Deux styles à ne jamais confondre (historique ; la section 0 prime)

**Le style « fiche »** (validé le 7 octobre 2026 pour la fiche joueur et le duel, rejeté le 13 octobre pour les posts) :
- fond jaune uni #F6C41C ;
- signature en haut à gauche ;
- grand titre en capitales penchées ;
- cadre blanc arrondi (rayon 20 px, ombre douce) qui porte le graphique et les tableaux ;
- texte courant et libellés en Inter ;
- comptes X et TikTok en bas à droite.

Quatre mises en scène : **A cadre blanc** ; **B nuit** (fond #04331A, jaune et blanc) ; **C encre** (tout sur le jaune,
sans cadre, une seule encre verte) ; **D blanc** (bandeau jaune en haut, fond blanc).
La fiche joueur, le duel et le classement n'existent qu'en nouvelle DA.

**Le style « vidéo »** (celui de la vidéo de lancement, devenu la DA des posts, voir section 0) :
- fond jaune dégradé (#FBD134 → #F6C41C → #EFA40A) avec la trame de points ;
- titre sur deux lignes, vert foncé puis rouge ;
- grand chiffre fantôme en contour ;
- données posées directement sur le fond.

**L'ancien style, à ne plus refaire** : cartes crème, roue en parts colorée par pilier, en-tête vert et noir avec une
pastille « VS », police Montserrat, « player score », grain ou effet craie, grands anneaux, bande de motifs façon bogolan,
volets diagonaux, encadrés verts, petit dessin à trois barres devant la ligne d'info.

**Leçon du 8 octobre 2026.** Quand Diaby dit « pas dans la DA », repartir des vrais gabarits (`visuels/variantes.py`,
`duel_v2.py`, `duel_mises.py`) et n'enlever ou ajouter que ce qu'il demande. Ne pas redessiner un graphique « dans
l'esprit » de la DA avec ses propres choix : c'est ce qui l'a fait retomber dans l'ancien style.

## 2. Éléments communs

- **Couleurs.** Or #F6C41C. Verts #0B7A3B, #064A25, #04331A (nuit), #19A552. Rouge #D4252A. Encre #0E1A13.
  Gris #5E6B62. Trait #E3E8E3.
- **Code des niveaux.** Au-dessus #0B7A3B, dans la moyenne #E3A600, en dessous #D4252A.
- **Polices.**
  - Barlow Condensed 900 italique en capitales, pour les titres et les grands chiffres.
  - Barlow Condensed italique pour la signature.
  - Inter pour le reste dans la fiche ; Barlow Semi Condensed (capitales) pour le reste dans les posts (section 0).
  - Polices locales via npm (`@fontsource`). Une capture qui affiche une police de secours (à empattements) est un défaut bloquant ; les scripts de capture s'arrêtent si une police manque.
- **Signature.** Logo rond + « MaliDataFoot » écrit Mali*Data*Foot (fin, « Data » en demi-gras). Pas de capitales, pas de rouge, pas de @ dans la signature.
- **Comptes.** Logos X et TikTok + @MaliDataFoot, toujours présents sur un visuel publié.
- **Logo de la page** (`logo-verte.png`) : ne jamais le modifier (ni recolorer, ni recadrer, ni retoucher). On le redimensionne seulement. Photo de profil HD : 2048 px, depuis l'original.
- **Logo StatsBomb** sur chaque visuel de données, exigé par leur licence. Il n'est jamais recoloré ; sur fond sombre, il est posé sur une pastille blanche (`da.credit()`). Texte : « Données » + logo.
- **Trame de points.** Oui, Diaby l'aime : des points en quinconce qui grossissent vers un coin. **Grain : non.**
- **Pays.** Drapeau dans un petit rond, comme dans les applis de foot (`da.drapeau`).
- **Clubs.** Écusson seulement si Diaby fournit le fichier.
- **Photos de joueurs.** Photos officielles des clubs, non libres. La provenance est notée dans `visuels/photos/SOURCES.md`.
- **Chiffres.** Pas de chiffres posés sur un graphique quand un tableau peut les porter. Pas de gros chiffres décoratifs, sauf le chiffre fantôme et le chiffre clé du gabarit des posts (section 0), qui portent le message.
- **Slogan.** « Les Aigles jouent. La data parle. » sert d'accroche (vidéo, fin de vidéo, bio). Jamais sur un visuel de données. Phrase de fin : « La data du foot malien ».

## 2 bis. Logo : pistes alternatives (leçon du 13 octobre 2026)

Diaby a demandé d'autres idées de logo « au cas où ». Mes esquisses en formes plates géométriques (barres, hexagone, carte en points, silhouette) ont été jugées « hors DA, ça fait IA de ouf ». Ce qu'il avait déjà dit pour le logo, et qui reste la règle :
- minimaliste et pro, mais **illustré**, au niveau du logo actuel (dégradés, volumes, traits nets), jamais des aplats géométriques (« trop moche ») ni un style dessin animé ;
- on doit voir la data dans le logo ;
- le fond reste dans la DA des vidéos, pas un jaune à plat ;
- le **petit dessin à trois barres** fait partie de l'ancien style à ne plus refaire.

Un logo à ce niveau ne se bricole pas en SVG : discuter d'abord le symbole avec Diaby, puis rédiger un brief précis pour un illustrateur ou un outil de génération d'images, et auditer le résultat contre cette section. Le logo actuel (`logo-verte.png`) reste le logo de la page et ne se modifie pas.

## 2 ter. Une image, un message (leçon du 13 octobre 2026)

Critique faite à Diaby, et qu'il a validée (« améliore tout ») : nos visuels faisaient « tableau de bord générique », pas Data'Scout.
- **Un seul graphique par image, en grand**, qui remplit le cadre. Pas de cadre à moitié vide.
- **Pas de triple répétition** : un graphique + un tableau + un paragraphe « À lire » qui redit le tweet, c'est trop. Le détail chiffré va dans le texte du post.
- **Le message est écrit sur le graphique** (une annotation courte : « Deux fois moins »), et seulement les deux ou trois chiffres qui portent le message.
- **Pas le même bloc partout** : un tableau « Le bilan » répété en bas de chaque variante rend tout pareil.
- **Couleurs franches** : pas de dégradés pastel (« mise en forme Excel »). Le code des niveaux de la DA (vert, jaune, rouge, rouge foncé) en classes nettes.
- **Étiquettes courtes** et placées de la même façon pour toutes les barres.
- **Le type de graphique ne doit pas tromper l'œil** (Diaby, 14/10/2026 : « faut pas se tromper sur les data, même sur le choix de la visualisation »). Pas de moyenne glissante courte qui fait de fausses grosses chutes, pas de cumul qui donne l'impression que ça empire, pas deux façons de compter sur la même image. Écrire en une phrase ce que l'œil retient en 2 secondes et vérifier que c'est vrai. Détail : skill données, angle 6.
- **Le ton** : un chiffre qui peut se lire comme négatif pour le Mali se cadre sur ce qu'il faut faire (« il faut gagner deux fois »), pas sur la peur (« plus à perdre qu'à gagner »).

## 3. Formats

| Sortie | Taille | Contraintes |
|---|---|---|
| X | 1080 × 1350 (capture ×2) | marges 56 px ; le plus petit texte reste lisible sur téléphone |
| TikTok | 1080 × 1920 (capture ×2) | rien d'important au-dessus de 150 px ni dans les 340 px du bas ; à droite, rester sous x = 946 en dessous de y = 880 |
| TikTok **carrousel de photos** | 1080 × 1920, mais l'appli n'affiche que la bande centrale **y 240–1680** (format 3:4, mesuré le 15/10/2026 sur l'iPhone de Diaby avec le post défense : le haut du surtitre était rogné) | dans cette bande : rien d'important avant **y ≈ 400** (nom du compte, date, flèche retour et « 1/2 » couvrent le haut) ; colonne d'icônes à droite (photo, cœur, commentaires) au-delà de **x ≈ 940** dès y ≈ 1000 ; les points du carrousel vers y ≈ 1640. Le plus simple : composer le carrousel directement en 1080 × 1440 avec ces marges. Contrôle : simuler l'écran avant livraison |
| Bannière X | 1500 × 500 (exporter en 3000 × 1000) | **zone sûre x 560–1230, y 210–448** (mesurée le 13 octobre sur l'iPhone de Diaby : l'appli ne montre que x 338–1393, y 79–500, l'heure couvre le haut, les boutons retour et recherche sont à mi-hauteur sur les côtés, la photo couvre x 360–575 dès y = 455 ; sur ordinateur, la photo couvre x 40–395, y 287–500). Contrôle : `apercu_iphone.py` et `apercu_profil.py` |

Toujours livrer la version X **et** la version TikTok d'un visuel retenu.

## 4. Variantes et choix

- Pour chaque data viz ou post : d'abord la version en nouvelle DA, puis la **grille numérotée des variantes** (une colonne par plan, une ligne par variante : 1A, 1B…), puis les versions X et TikTok de ce que Diaby retient (`python taches.py grille`).
- Les variantes sont de **vraies mises en scène différentes**, pas le même dessin recoloré. Exemple validé : le duel en quatre mises en scène (radar + tableau, barres face à face, ronds reliés, barres d'écart).
- Diaby aime choisir. Proposer des options numérotées, puis donner un avis franc (deux ou trois préférées, et pourquoi).
- Ne jamais changer un texte, un chiffre ou un son d'une vidéo déjà validée sans lui montrer d'abord les plans modifiés.

## 5. Bannière X (état au 13 octobre 2026)

- Ce qu'il a aimé : la composition « terrain derrière, cartes penchées ».
- Ses retours :
  - pas de noms de joueurs ;
  - pas de contenu trop exact repris de la vidéo ;
  - plusieurs types de dataviz ;
  - rester dans la nouvelle DA ;
  - pas de cartes vides.
- Les cartes se font depuis les vrais gabarits allégés (`reel_cartes.py`, `banniere_reel.py`, `python taches.py bannieres`). Les essais redessinés sont rangés dans `visuels/archives/`.
- Il avait aussi dit (6–7 octobre) « pas besoin d'écriture sur la bannière, on écrira dans la bio » : reconfirmer avant d'y mettre l'accroche.
- **13 octobre 2026** : la bannière en place « fait trop copier l'ancienne DA ». Retour au « terrain derrière » dans la nouvelle DA, petits points autorisés. Série `banniere_terrain.py` (données : `banniere_donnees.py`) :
  - la trame de points peut porter la donnée (points en quinconce qui grossissent selon la densité des actions du Mali, sur un vrai terrain à l'échelle) : c'est notre motif et une vraie data viz à la fois ; points pleins, sans transparence (des points à moitié transparents virent à l'olive sale) ;
  - les traits de passes en masse font « grain » : ne pas les utiliser en fond ;
  - sur un fond nuit, mettre les cartes jaunes (cadre blanc) : les cartes nuit s'y perdent ;
  - sur téléphone, X pose ses boutons en haut à gauche et à droite : aucun titre de carte sous ces zones (environ x 30–155 et x 1170–1450, y 40–160) ;
  - le crédit StatsBomb reste en bas à droite dès qu'il y a de la donnée ;
  - aperçus de contrôle : `apercu_profil.py` (photo de profil posée dessus) et `apercu_tel.py` (taille téléphone avec les boutons).
- **13 octobre 2026, suite** : dans la bannière, ni les dataviz de la vidéo ni la CAN 2023 (« on est trop butés là-dessus »). Varier les sources et les sujets. Série actuelle : l'historique des Aigles depuis 1960 (gabarits `histoire`, `scores`, `decennies`, `competitions` de `variantes.py`, cartes par `reel_histoire.py`, données par `aigles_export.py`).
- **Retenue le 13 octobre 2026 : la 2A** (`banniere_mini.py 2 … signature`), en place sur X.
- **13 octobre 2026, fin** : un décor dessiné en code (stade 3D, projecteurs, lumières) fait « dessin animé, pas pro » ; le vert drapeau en fond a été écarté (« je veux la DA de la vidéo »). Pour la bannière : minimaliste, style vidéo (fond jaune dégradé, trame, terrain crème, données posées sur le fond), une seule data viz, MaliDataFoot + logo en bas juste à droite de la photo de profil (`banniere_mini.py`). Pour du réaliste, seulement une vraie photo libre de droits ou générée (Higgsfield, crédits de Diaby).

## 6. Audit visuel (toujours, avant d'envoyer)

Regarder soi-même le rendu (capture à taille réelle et réduite, comme sur un téléphone) et vérifier :
- collisions et textes coupés ;
- doublons ;
- un nom plus près d'une autre pastille que de la sienne ;
- légende manquante pour une couleur ;
- zones de sécurité (TikTok, photo de profil X) ;
- polices bien chargées ;
- cohérence avec les gabarits validés.

## 7. Où sont les gabarits

Dans le dépôt `malidatafoot`, dossier `visuels/`.

| Fichier | Rôle |
|---|---|
| `posts_video.py` | **le gabarit des posts** (section 0) : `_pv_1.html` défenses africaines, `_pv_2.html` courbe depuis 2000, `_pv_3.html` points FIFA |
| `da.py` | cadre commun, `fr()` (arrondi « comme à l'école »), `credit()`, `drapeau()` |
| `variantes.py <plan> <A\|B\|C\|D> <sortie.html> [x\|tiktok]` | plans accroche, tirs, but, fil, reseau, fiche, fin ; historique des Aigles : histoire, scores, decennies, competitions (pensés pour la bannière : le bas de la version X reste à remplir avant d'en faire un post) |
| `duel_v2.py`, `duel_mises.py`, `duel_commun.py` | le duel |
| `grille.py` | la grille des variantes |
| `vitv.tpl.html`, `md2.html`, `scenes_md2.py`, `render2.mjs` | la vidéo |
| `shotu.mjs` | la capture d'une page |

Toutes les commandes passent par `python taches.py …`. Si ces fichiers ne sont pas dans l'espace de travail, demander à Diaby le dépôt à jour.
