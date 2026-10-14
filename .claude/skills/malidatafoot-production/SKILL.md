---
name: malidatafoot-production
description: Comment produire un post ou une vidéo MaliDataFoot avec Diaby : façon de travailler, règles de texte, motion design, sons, workflow et publication. À lire au début de toute session sur la page.
---

# MaliDataFoot : production des posts et des vidéos

## 1. Travailler avec Diaby

- En français, court, simple, peu de listes.
- Discuter et vérifier l'objectif avant de produire quand la demande est ambiguë. Quand il dit « génère plein, on va choisir », produire un lot numéroté.
- Être aussi critique que lui sur le fond et la forme : « c'est un projet pro ». Auditer soi-même avant d'envoyer, sans attendre qu'il trouve les défauts.
- **Ça vaut pour tous les contenus, textes des posts compris** (rappel du 13 octobre 2026). Avant de proposer ou de valider une légende : répétitions (« nouvelle page, le nouveau compte »), ton trop froid (un point sec après une accroche), oubli d'une partie du public (les Maliens en club, pas seulement les Aigles), promesse qui enferme la page, longueur (X : 280 caractères, emojis comptés double ; TikTok : 5 hashtags au plus, bio 80 caractères), hashtags inutiles ou ambigus (#CAN = « can » en anglais : préférer #AFCON). Proposer de vraies alternatives, pas seulement corriger ses brouillons.
- Ne jamais changer un texte, un chiffre ou un son d'un visuel validé sans le lui montrer d'abord.
- Si une commande ou un rendu est refusé, s'arrêter et attendre son instruction.
- Ne jamais saisir de mot de passe ou de clé, ne jamais créer de compte ni accepter de cookies à sa place.
- C'est un vrai projet de data engineering, d'analyse et de data science. Il se travaille dans le dépôt `malidatafoot` (VS Code + git), pas dans un espace temporaire. Ce qui est fait dans une session doit finir dans le dépôt : code, docs, décisions.

## 2. Règles de texte (visuels, vidéos, posts)

- **Un chiffre, une phrase.** Concis.
- **Pas d'abréviation** que tout le monde ne connaît pas (« A.P. » refusé).
- **« Possession »** (calculée sur les passes), et pas « part des passes ».
- **« Performances proches »**, et pas « Profils proches » : on compare le tournoi, pas le joueur en général.
- **Pas de conclusion qui dépend d'un seuil choisi par nous.**
- **Notes de bas de fiche validées** :
  - « Rang : sa place parmi les 49 latéraux ayant joué au moins 180 minutes. »
  - « Note : la part des autres latéraux qu'il dépasse, en moyenne sur les dix critères. »
  - « Données » + logo StatsBomb.
- **Accroche** : « Les Aigles jouent. La data parle. »
- **Bio X** : « Comprendre le football malien par la data 📊🇲🇱 / Aigles • Maliens & binationaux en club / Data viz • Page indépendante ».
- **Bio TikTok** : « Le football malien par la data 📊🇲🇱 / Aigles • Maliens & binationaux en club • Page indépendante ».
- **Nom affiché sur X** : à passer de « MLdata » à « MaliDataFoot ».

## 3. Workflow d'un post

1. **L'idée.** Quelle question de foot on éclaire. Il y a plein de phénomènes à comprendre avec la data, et le but est d'apporter quelque chose de nouveau sur les réseaux.
2. **Les données.** Source autorisée, pipeline à jour, tests verts (`python taches.py donnees`, puis `tests`).
3. **L'analyse.** Calcul dans le pipeline (SQL / Python versionné), pas « à la main ».
4. **Le visuel.** D'abord en nouvelle DA, puis la grille de variantes numérotée, et Diaby choisit.
5. **Les versions finales.** X et TikTok du choix.
6. **L'audit.** Données, logique, sémantique, visuel (skill `malidatafoot-donnees-et-audit`). Pour un post important, un recomptage indépendant.
7. **Le texte du post.** Diaby explique l'analyse par écrit sur X.
8. **Le dépôt.** Le code et la décision sont enregistrés (commit + une ligne dans `docs/journal_des_gabarits.md`).

## 4. Motion design et vidéo

- **Règle des formats (13 octobre 2026)** : chaque sujet se décline en **motion design pour TikTok** et en **thread pour X**, à partir des mêmes visuels (gabarit `visuels/posts_video.py`, DA section 0). Le thread : un tweet d'accroche avec la première image, puis un tweet et une image par idée. Le motion design : les mêmes images animées, dans la mécanique de la vidéo de lancement (GSAP, `window.seek`).

- **Format.** Vertical 1080 × 1920, 60 images/s. Pages HTML + GSAP en timelines arrêtées (`window.seek(t)`, `window.READY`), capturées par Chromium (Playwright) en quatre lots, puis assemblées par ffmpeg : libx264 crf 20, preset slow, AAC 192k. Commande : `python taches.py video` ; `--controle` donne quelques images pour vérifier.
- **Vidéo de lancement.** 37,45 s, finale du 8 octobre 2026 : `MaliDataFoot-video-de-lancement-tiktok-essai-4.mp4` (« sons de terrain »). Elle n'est pas encore postée : Diaby prépare d'abord de vrais posts, pour ne pas la publier puis attendre une semaine.
- **Avant de poster** : écouter au téléphone avec le son, tester la zone du bas de TikTok en brouillon privé, revérifier le « club actuel ».

## 5. Sons

- Synthèse procédurale (`visuels/sfx_md2.py`), sans mélodie : Diaby ajoute lui-même la musique.
- **Version validée le 8 octobre 2026, les « sons de terrain »** : djembés, impacts, souffles de transition, clameur, **frappes de balle** sur les passes, les conduites et le tir de l'anatomie du but, une **touche de balle** par joueur du réseau de passes, des **coups mats sans note** (lignes de la fiche, barres du duel), et un souffle qui monte à la place des roulements de tics.
- **Retirés à sa demande** : les cloches (« ting ting, ça fait trop »), les bulles (gardées seulement sur les buts de la carte des tirs), le scintillement du but, les coups de bois en série qui montent (« xylophone »), les tics et cliquetis.
- Ce réglage est celui par défaut. `SFX_SANS_DING=0` redonne les anciens sons, pour comparer.
- **Règle** : rien qui fasse une note qui tinte (cloche, xylophone, bulle aiguë, scintillement), rien qui sonne jouet ou dessin animé. Préférer des sons de foot (ballon, filet, stade) et des sons secs et sobres.
- **Contrôle** : chercher par la mesure les sons aigus et tenus (le script d'audit du 8 octobre en trouvait 28 avant, contre 4 souffles seulement après). Faire écouter Diaby au téléphone avant de valider.
- **Piste** : remplacer un jour les frappes de synthèse par de vrais enregistrements libres de droits (CC0), que Diaby télécharge et dont on vérifie la licence.

## 6. Idées de contenus

- **Toujours être à jour** : avant de proposer des idées, vérifier sur le web la dernière actu des Aigles (matchs joués, listes, résultats, prochains rendez-vous). Une idée qui ignore le dernier match fait perdre toute crédibilité.

- Chaque fois qu'on cherche des idées : en proposer dans **plusieurs catégories** (actu des Aigles, Maliens en club, rétro, lien hier / aujourd'hui, phénomènes, sujets poussés et curieux, formats légers). Pas de stats « bateau » : des sujets qui font comprendre un phénomène.
- **Le suivi de tous les sujets (statut, données, formats) est dans `docs/boite_a_idees.md`** : le mettre à jour à chaque idée nouvelle, POC ou publication. La banque d'exemples est dans `docs/banque_idees.md`. Ce sont des exemples, pas une liste fermée : on continue d'en proposer de nouveaux au même niveau, et on y ajoute ceux qui plaisent.
- Formats : posts, threads sur X, TikTok en motion design avec voix off (scripts écrits avec les règles de texte ci-dessus).

## 7. Prochains contenus (proposition du 7 octobre, à décider avec lui)

- le début de saison de Sinayoko ;
- les Aigles avant la double confrontation contre le Rwanda (novembre 2026) ;
- une série « rétro » sur la CAN 2023 ;
- d'autres types de visualisations au fil des idées, chacune avec sa grille de variantes.

Tout ça vient après le choix de la source de données pour la saison en cours.
