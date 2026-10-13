---
name: malidatafoot-direction-artistique
description: Direction artistique de MaliDataFoot (football malien par la data) : à lire avant tout visuel, post, bannière, photo de profil, motion design ou vidéo pour la page.
---

# MaliDataFoot : direction artistique (la forme)

MaliDataFoot (@MaliDataFoot sur X, @malidatafoot sur TikTok) est la page de Diaby : le football malien expliqué par la data.
C'est un projet pro. Chaque visuel doit avoir l'air d'une vraie interface de data foot (référence de niveau : Data'Scout,
les applis et institutions du foot), jamais « IA », « débutant » ou « enfantin ». Viser la réussite et la crédibilité :
mieux vaut un visuel de moins qu'un visuel approximatif.

## 1. Deux styles à ne jamais confondre

**La nouvelle DA = le style « fiche »** (validé le 7 octobre 2026, c'est celui de la grille des variantes) :
- fond jaune uni #F6C41C ;
- signature en haut à gauche ;
- grand titre en capitales penchées ;
- cadre blanc arrondi (rayon 20 px, ombre douce) qui porte le graphique et les tableaux ;
- texte courant et libellés en Inter ;
- comptes X et TikTok en bas à droite.

Quatre mises en scène : **A cadre blanc** ; **B nuit** (fond #04331A, jaune et blanc) ; **C encre** (tout sur le jaune,
sans cadre, une seule encre verte) ; **D blanc** (bandeau jaune en haut, fond blanc).
La fiche joueur, le duel et le classement n'existent qu'en nouvelle DA.

**Le style « vidéo »** (ancien gabarit, encore utilisé pour les tirs, le but, le fil du match et le réseau dans la vidéo
de lancement) :
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
  - Inter pour tout le reste.
  - Polices locales via npm (`@fontsource`). Une capture qui affiche une police de secours (à empattements) est un défaut bloquant ; les scripts de capture s'arrêtent si une police manque.
- **Signature.** Logo rond + « MaliDataFoot » écrit Mali*Data*Foot (fin, « Data » en demi-gras). Pas de capitales, pas de rouge, pas de @ dans la signature.
- **Comptes.** Logos X et TikTok + @MaliDataFoot, toujours présents sur un visuel publié.
- **Logo de la page** (`logo-verte.png`) : ne jamais le modifier (ni recolorer, ni recadrer, ni retoucher). On le redimensionne seulement. Photo de profil HD : 2048 px, depuis l'original.
- **Logo StatsBomb** sur chaque visuel de données, exigé par leur licence. Il n'est jamais recoloré ; sur fond sombre, il est posé sur une pastille blanche (`da.credit()`). Texte : « Données » + logo.
- **Trame de points.** Oui, Diaby l'aime : des points en quinconce qui grossissent vers un coin. **Grain : non.**
- **Pays.** Drapeau dans un petit rond, comme dans les applis de foot (`da.drapeau`).
- **Clubs.** Écusson seulement si Diaby fournit le fichier.
- **Photos de joueurs.** Photos officielles des clubs, non libres. La provenance est notée dans `visuels/photos/SOURCES.md`.
- **Chiffres.** Pas de chiffres posés sur un graphique quand un tableau peut les porter. Pas de gros chiffres décoratifs.
- **Slogan.** « Les Aigles jouent. La data parle. » sert d'accroche (vidéo, fin de vidéo, bio). Jamais sur un visuel de données. Phrase de fin : « La data du foot malien ».

## 2 bis. Logo : pistes alternatives (leçon du 13 octobre 2026)

Diaby a demandé d'autres idées de logo « au cas où ». Mes esquisses en formes plates géométriques (barres, hexagone, carte en points, silhouette) ont été jugées « hors DA, ça fait IA de ouf ». Ce qu'il avait déjà dit pour le logo, et qui reste la règle :
- minimaliste et pro, mais **illustré**, au niveau du logo actuel (dégradés, volumes, traits nets), jamais des aplats géométriques (« trop moche ») ni un style dessin animé ;
- on doit voir la data dans le logo ;
- le fond reste dans la DA des vidéos, pas un jaune à plat ;
- le **petit dessin à trois barres** fait partie de l'ancien style à ne plus refaire.

Un logo à ce niveau ne se bricole pas en SVG : discuter d'abord le symbole avec Diaby, puis rédiger un brief précis pour un illustrateur ou un outil de génération d'images, et auditer le résultat contre cette section. Le logo actuel (`logo-verte.png`) reste le logo de la page et ne se modifie pas.

## 3. Formats

| Sortie | Taille | Contraintes |
|---|---|---|
| X | 1080 × 1350 (capture ×2) | marges 56 px ; le plus petit texte reste lisible sur téléphone |
| TikTok | 1080 × 1920 (capture ×2) | rien d'important au-dessus de 150 px ni dans les 340 px du bas ; à droite, rester sous x = 946 en dessous de y = 880 |
| Bannière X | 1500 × 500 (exporter en 3000 × 1000) | la photo de profil couvre environ x 40–395, y 287–500 sur ordinateur ; sur téléphone, X pose des boutons en haut ; texte éventuel à partir de x = 432 |

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
| `da.py` | cadre commun, `fr()` (arrondi « comme à l'école »), `credit()`, `drapeau()` |
| `variantes.py <plan> <A\|B\|C\|D> <sortie.html> [x\|tiktok]` | plans accroche, tirs, but, fil, reseau, fiche, fin ; historique des Aigles : histoire, scores, decennies, competitions (pensés pour la bannière : le bas de la version X reste à remplir avant d'en faire un post) |
| `duel_v2.py`, `duel_mises.py`, `duel_commun.py` | le duel |
| `grille.py` | la grille des variantes |
| `vitv.tpl.html`, `md2.html`, `scenes_md2.py`, `render2.mjs` | la vidéo |
| `shotu.mjs` | la capture d'une page |

Toutes les commandes passent par `python taches.py …`. Si ces fichiers ne sont pas dans l'espace de travail, demander à Diaby le dépôt à jour.
