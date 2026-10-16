---
name: malidatafoot-production
description: Comment produire un post ou une vidéo MaliDataFoot avec Diaby : façon de travailler, règles de texte, motion design, sons, workflow et publication. À lire au début de toute session sur la page.
---

# MaliDataFoot : production des posts et des vidéos

**Relire avant de proposer (Diaby, 14 octobre 2026 : « faut pas jeter des trucs comme ça en pâture, c'est un projet pro »).**
À chaque nouvelle idée de visuel, de data visualisation ou de sujet, et avant toute proposition de source, relire d'abord :
- `docs/sources_de_donnees.md` : quelles sources on a déjà trouvées, testées, autorisées ou écartées (ex. martj42 = scores sans compos ; API-Football gratuit = 2022-2024 seulement ; FotMob = accord écrit à archiver) ;
- `docs/boite_a_idees.md` et `docs/banque_idees.md` : ce qui est déjà fait, en cours ou rejeté ;
- `docs/journal_des_gabarits.md` : les décisions de forme et de fond déjà prises ;
- les sections utiles des trois skills (DA, données, production).
Puis proposer en s'appuyant dessus : dire ce qu'on a déjà, ce qui manque, et d'où viendrait le manque, vérifié. Ne jamais proposer une solution (surtout payante) qu'on n'a pas vérifiée.

## 1. Travailler avec Diaby

- En français, court, simple, peu de listes.
- Discuter et vérifier l'objectif avant de produire quand la demande est ambiguë. Quand il dit « génère plein, on va choisir », produire un lot numéroté.
- Être aussi critique que lui sur le fond et la forme : « c'est un projet pro ». Auditer soi-même avant d'envoyer, sans attendre qu'il trouve les défauts.
- **Ça vaut pour tous les contenus, textes des posts compris** (rappel du 13 octobre 2026). Avant de proposer ou de valider une légende : répétitions (« nouvelle page, le nouveau compte »), ton trop froid (un point sec après une accroche), oubli d'une partie du public (les Maliens en club, pas seulement les Aigles), promesse qui enferme la page, longueur (X : 280 caractères, emojis comptés double ; TikTok : 5 hashtags au plus, bio 80 caractères), hashtags inutiles ou ambigus (#CAN = « can » en anglais : préférer #AFCON). Proposer de vraies alternatives, pas seulement corriger ses brouillons.
- Ne jamais changer un texte, un chiffre ou un son d'un visuel validé sans le lui montrer d'abord.
- Si une commande ou un rendu est refusé, s'arrêter et attendre son instruction.
- Ne jamais saisir de mot de passe ou de clé, ne jamais créer de compte ni accepter de cookies à sa place.
- **Être force de proposition, sans attendre qu'il demande** (Diaby, 14 octobre 2026) : à chaque session, suggérer de soi-même des sujets, des améliorations, des sources, des formats. Ne pas seulement exécuter.
- **Être exigeant et critique sur tout** : la qualité visuelle, le respect de la DA, la pertinence du sujet, la profondeur de l'analyse. « On est une page data, pas une simple page stats » : un classement ou un pourcentage seul ne suffit pas. Il faut au moins une partie des contenus avec de la vraie profondeur (modèle, attendu contre réel, simulation, analyse de jeu, comparaison au bon groupe de référence).
- **Ne pas se bloquer sur un seul sujet ou une seule source** (reproche du 14 octobre : « trop bloqué sur la CAN 2023 »). Varier : actu, joueurs en club, histoire, phénomènes.
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

- **Pas de texte qui sonne « IA »** (Diaby, 16 octobre 2026, sur le thread du onze type). Les tweets et descriptions doivent se lire comme écrits par un fan qui connaît le foot, et rester courts. À éviter :
  - les phrases à deux-points en série (« Le plus régulier : … », « Les limites : … », « Ceux qui restent : … ») ;
  - les formules en miroir (« deux sélectionneurs, deux onzes types ») et les accroches de pub ;
  - un tweet par idée quand deux idées tiennent dans un seul ; le 🧵 et les emojis en décoration.
  Exemple. Avant : « Le plus régulier : Hamari Traoré, titulaire 12 fois sur 15. » Après : « Sous Chelle, Hamari Traoré est le plus régulier avec 12 titularisations sur 15. »
  Garder la fin qui marche : les limites dites simplement, puis une question au lecteur.
- **Toujours dire les limites** (Diaby, 14 octobre 2026 : « les points de faiblesse, faut toujours en parler, pour pas qu'un petit malin essaie de debunk, et ça rend le truc encore plus crédible »). Chaque post d'analyse finit par ses limites, en clair : taille de l'échantillon, choix qu'on a faits (année de départ, compétitions retenues), là où le modèle force, ce qui va contre notre conclusion. Et à chaque fois, dire si la conclusion tient quand même (tester l'autre choix, enlever le match qui pose problème).

## 3. Workflow d'un post

0. **Le POC d'abord** (14 octobre 2026) : pour un nouveau sujet, d'abord le calcul sur les vraies données et 2 ou 3 plans clés en maquette (les visuels avant les voix off), montrés à Diaby. On améliore ensuite au cas par cas.
1. **L'idée.** Quelle question de foot on éclaire. Il y a plein de phénomènes à comprendre avec la data, et le but est d'apporter quelque chose de nouveau sur les réseaux.
2. **Les données.** Source autorisée, pipeline à jour, tests verts (`python taches.py donnees`, puis `tests`).
3. **L'analyse.** Calcul dans le pipeline (SQL / Python versionné), pas « à la main ».
4. **Le visuel.** D'abord en nouvelle DA, puis la grille de variantes numérotée, et Diaby choisit.
5. **Les versions finales.** X et TikTok du choix.
6. **L'audit.** Données, logique, sémantique, visuel (skill `malidatafoot-donnees-et-audit`). Pour un post important, un recomptage indépendant.
7. **Le texte du post.** Diaby explique l'analyse par écrit sur X.
8. **Le dépôt.** Le code et la décision sont enregistrés (commit + une ligne dans `docs/journal_des_gabarits.md`).

## 4. Motion design et vidéo

- **Règle des formats (mise à jour du 14 octobre 2026)** : chaque sujet se décline en **thread pour X** et, sur TikTok, en **carrousel de photos** par défaut ; le **motion design** seulement quand on le juge utile (une histoire qui se raconte en mouvement, une simulation, un terrain qui bouge). Mêmes visuels pour les deux (gabarit `visuels/posts_video.py`, DA section 0). Le thread : un tweet d'accroche avec la première image, puis un tweet et une image par idée. Le motion design : les mêmes images animées, dans la mécanique de la vidéo de lancement (GSAP, `window.seek`).

- **Qualité avant quantité** (Diaby, 14 octobre 2026, sur 18 vidéos produites d'un coup avec des animations génériques : « des trucs bateau, pas recherchés ») : une vidéo se travaille une par une, au niveau de la vidéo de lancement. Chaque scène a son animation propre, qui raconte la donnée (les tirs qui tombent, le terrain qui penche vraiment, les simulations qui remplissent des cases), un rythme calé sur la voix, des sons. Les fondus et montées génériques de `animer.py` ne servent qu'aux brouillons, jamais à une version à publier.
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
- **Veille régulière des pages maliennes** : regarder l'actu et les derniers posts de @equipesdumali, @AiglesDuMali_, @malicomps et @femafoot (X), pour être à la page et ne pas refaire ce qu'elles viennent de poster. Si on ne peut pas les lire directement, demander à Diaby une capture ou chercher les reprises dans la presse.
- **Veille des grosses pages data** (Data'Scout, DataFoot et les autres) : ce qu'elles publient, leurs formats, et surtout **leurs sources de données** (étude de marché à refaire régulièrement, résultats dans `docs/sources_de_donnees.md`). Objectif : faire mieux, avec plus de contexte et de profondeur, pas les copier.
- **Poster souvent** : plusieurs publications variées par semaine. Proposer un planning à Diaby et tenir un stock d'avance (les sujets « prêts » de la boîte à idées).

- Chaque fois qu'on cherche des idées : en proposer dans **plusieurs catégories** (actu des Aigles, Maliens en club, rétro, lien hier / aujourd'hui, phénomènes, sujets poussés et curieux, formats légers). Pas de stats « bateau » : des sujets qui font comprendre un phénomène.
- **Le suivi de tous les sujets (statut, données, formats) est dans `docs/boite_a_idees.md`** : le mettre à jour à chaque idée nouvelle, POC ou publication. La banque d'exemples est dans `docs/banque_idees.md`. Ce sont des exemples, pas une liste fermée : on continue d'en proposer de nouveaux au même niveau, et on y ajoute ceux qui plaisent.
- Formats : posts, threads sur X, TikTok en motion design avec voix off (scripts écrits avec les règles de texte ci-dessus).

## 7. Prochains contenus

Voir `docs/boite_a_idees.md` (statut de chaque sujet : publié, prêt, POC, à faire, en attente de source). À relire en début de session pour proposer la suite.

## 8. Planifier les publications (Diaby, 15 octobre 2026 : « faut mettre dans les skills de m'aider à planifier »)

- **Dès qu'un post est prêt, dire sans attendre qu'on le demande** : dans quel ordre poster, quel jour, à quelle heure (heure de Paris et heure de Bamako : 2 h d'écart en été, 1 h en hiver), sur quelle plateforme, quels fichiers prendre (dans l'ordre du carrousel) et le texte à coller. Diaby ne doit jamais se demander « je poste quoi en premier ».
- **Un sujet par jour au maximum.** Le thread X et le TikTok d'un même sujet sortent le même jour ; le sujet suivant, le lendemain ou plus tard.
- **Ordre** : celui validé dans `docs/etat_du_projet.md`. Un post lié à l'actu passe avant l'événement (ex. la simulation du groupe K avant Mali-Rwanda de novembre).
- **Heure** : on n'invente pas de « meilleure heure ». Tant qu'on n'a pas nos propres chiffres, on poste en soirée, et on note les vues 48 h après dans le calendrier pour apprendre ce qui marche.
- **Programmer** : si Diaby n'est pas disponible, lui proposer de programmer la publication (X et TikTok le permettent depuis l'ordinateur).
- **Avant de poster** : rappeler les vérifications du brouillon (corrections convenues faites, bonne version du fichier, images dans l'ordre, description, son au téléphone).
- **Le calendrier est tenu dans `docs/calendrier_publications.md`** : ce qui est publié, ce qui est programmé, ce qui est prêt. Le mettre à jour à chaque publication et à chaque post prêt.

## 9. Toujours montrer des exemples (Diaby, 15 octobre 2026 : « à chaque fois, il faut que tu montres des exemples pour que je comprenne »)

Quand j'explique un plan, un thread, une correction ou une idée : montrer l'exemple concret tout de suite (le texte exact du tweet, l'image, le chiffre réel, le match précis), pas une description abstraite. Et vérifier que l'angle colle à la réalité du foot que Diaby connaît (ex. le Rwanda est faible en Afrique : ne pas le présenter comme un gros danger, expliquer d'où vient le danger, ici jouer chez lui).
